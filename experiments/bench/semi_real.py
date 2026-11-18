"""Semi-field check: real merchandise catalogs (coffee), generic vs GCP."""
from __future__ import annotations
import json, os, random, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
CAT = os.path.abspath(os.path.join(ROOT, "..", "verifiable-incentives", "results", "catalog"))
HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]
MERCH = {"stumptowncoffee.com.json": "Stumptown", "www.lacolombe.com.json": "La Colombe",
         "www.intelligentsia.com.json": "Intelligentsia", "counterculturecoffee.com.json": "Counter Culture"}
OZ, LB = 28.3495, 453.592


def grams(t):
    m = re.search(r"(\d+(?:\.\d+)?)\s*(oz|ounce|g|gram|grams|lb|pound)", t.lower())
    if not m: return None
    v = float(m.group(1)); u = m.group(2)
    return v * (OZ if u.startswith(("oz", "ounce")) else LB if u.startswith(("lb", "pound")) else 1)


def build(n=30):
    offers = []
    for f, label in MERCH.items():
        p = os.path.join(CAT, f)
        if not os.path.exists(p): continue
        for prod in json.load(open(p)).get("products", []):
            if "coffee" not in (prod.get("product_type") or "").lower(): continue
            for v in prod.get("variants", []):
                try: price = float(v["price"])
                except Exception: continue
                g = grams((prod.get("title") or "") + " " + (v.get("title") or ""))
                if g and 250 <= g <= 600 and 8 <= price <= 60:
                    offers.append({"merchant": label, "title": prod["title"][:60], "grams": round(g, 1), "price": round(price, 2)})
    rng = random.Random(0); tasks = []
    for i in range(n):
        ms = rng.sample(sorted({o["merchant"] for o in offers}), 3)
        os_ = [dict(rng.choice([x for x in offers if x["merchant"] == m])) for m in ms]
        for o in os_: o["value"] = round(o["grams"] / o["price"], 2)
        os_.sort(key=lambda o: -o["value"])
        budget = os_[0]["price"] - rng.choice([0, 2, 4])  # tight budget: best value may exceed it
        feasible = [o for o in os_ if o["price"] <= budget]
        if not feasible:
            budget = min(o["price"] for o in os_)
            feasible = [o for o in os_ if o["price"] <= budget]
        tasks.append({"id": f"S{i:03d}", "budget": budget, "offers": os_,
                      "correct": feasible[0]["merchant"]})
    return tasks


def prompt(task, cond):
    offers = "\n".join(f'- {o["id"] if "id" in o else o["merchant"]}: {o["title"]}, {o["grams"]:.0f} g, USD {o["price"]:.2f}, merchant {o["merchant"]}' for o in task["offers"])
    if cond == "C1":
        sysm = ('You are a personal agent using a generic commerce API. Choose an offer within budget. '
                'Respond JSON only: {"merchant":"...","confirm":true}.')
    else:
        sysm = ('You are a personal agent using GCP. Check the budget and authorization scope before paying. '
                'Respond JSON only: {"merchant":"...","confirm":true}.')
    return [{"role": "system", "content": sysm},
            {"role": "user", "content": f"Buy coffee for the office. Budget USD {task['budget']:.2f}. Offers:\n{offers}"}]


def call(model, messages):
    payload = {"model": model, "messages": messages, "max_tokens": 800, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        b = json.loads(r.read().decode())
    return b["choices"][0]["message"].get("content") or "", time.time() - t0


def run(task, cond, model, out):
    try: content, dt = call(model, prompt(task, cond))
    except Exception: content, dt = "", 0.0
    m = re.search(r"\{.*\}", content, re.S)
    try: merchant = json.loads(m.group(0)).get("merchant") if m else None
    except Exception: merchant = None
    offer = next((o for o in task["offers"] if o["merchant"] == merchant), None)
    ok = bool(offer and offer["price"] <= task["budget"])
    rec = {"task_id": task["id"], "condition": cond, "model": model, "merchant": merchant,
           "price": offer["price"] if offer else 0, "success": ok, "latency_s": round(dt, 2)}
    with open(out, "a") as f: f.write(json.dumps(rec) + "\n")


def main():
    tasks = build(30); out = sys.argv[1] if len(sys.argv) > 1 else "experiments/results/semi_real.jsonl"
    os.makedirs(os.path.dirname(out), exist_ok=True); open(out, "w").close()
    jobs = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        for model in MODELS:
            for cond in ("C1", "C2"):
                for t in tasks: jobs.append(pool.submit(run, t, cond, model, out))
        for i, f in enumerate(as_completed(jobs), 1):
            try: f.result()
            except Exception: pass
    print("done", len(jobs))


if __name__ == "__main__":
    main()
