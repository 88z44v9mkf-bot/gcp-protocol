"""Semi-field with a real aftermarket parts catalog (Urotuning) + service-kit tasks."""
from __future__ import annotations
import json, os, random, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]


def load_offers():
    j = json.load(open(os.path.join(ROOT, "experiments/results/urotuning_catalog.json")))
    out = []
    for p in j.get("products", []):
        for v in p.get("variants", []):
            try: price = float(v.get("price"))
            except Exception: continue
            if not (20 <= price <= 800): continue
            out.append({"title": p["title"][:70], "price": round(price, 2),
                        "type": (p.get("product_type") or "part").lower()})
    return out


def build(n_parts=20, n_service=10):
    offers = load_offers(); rng = random.Random(0); tasks = []
    parts = [o for o in offers if "service" not in o["title"].lower()][:n_parts]
    service = [o for o in offers if any(k in o["title"].lower() for k in ("kit", "service", "oil", "filter"))][:n_service]
    for i, base in enumerate(parts + service):
        kind = "service" if i >= len(parts) else "parts"
        chosen = [dict(rng.choice(offers)) for _ in range(3)]
        chosen[0]["compatible"] = True; chosen[1]["compatible"] = False; chosen[2]["compatible"] = True
        chosen[0]["authorized"] = True; chosen[1]["authorized"] = True; chosen[2]["authorized"] = False
        chosen[0]["price"] = base["price"]; chosen[1]["price"] = max(10, base["price"] - rng.randint(20, 60))
        chosen[2]["price"] = base["price"]
        budget = base["price"] + rng.choice([0, 20, 50])
        tasks.append({"id": f"RP{i:03d}", "domain": kind, "budget": budget,
                      "offers": [{"id": f"O{k+1}", **o} for k, o in enumerate(chosen)],
                      "correct": "O1"})
    return tasks


def prompt(task, cond):
    offers = "\n".join(f'- {o["id"]}: {o["title"]}, CNY {o["price"]}, stock 3' for o in task["offers"])
    if cond == "C1":
        sysm = ('You are a personal agent using a generic commerce API. Choose an offer within budget. '
                'Respond JSON only: {"offer_id":"..."}.')
    else:
        lines = "\n".join(f'- {o["id"]}: {o["title"]}, CNY {o["price"]}, compatible={o["compatible"]}, authorized={o["authorized"]}'
                          for o in task["offers"])
        sysm = ('You are a personal agent using GCP. Choose a compatible, authorized offer within budget. '
                'Respond JSON only: {"offer_id":"..."}.')
        offers = lines
    return [{"role": "system", "content": sysm},
            {"role": "user", "content": f"Request: buy {task['domain']} for my vehicle. Budget CNY {task['budget']}.\nOffers:\n{offers}"}]


def call(model, messages):
    payload = {"model": model, "messages": messages, "max_tokens": 500, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        b = json.loads(r.read().decode())
    return b["choices"][0]["message"].get("content") or "", time.time() - t0


def run(task, cond, model, out):
    try: content, dt = call(model, prompt(task, cond))
    except Exception: content, dt = "", 0.0
    m = re.search(r"\{.*\}", content, re.S)
    try: oid = json.loads(m.group(0)).get("offer_id") if m else None
    except Exception: oid = None
    offer = next((o for o in task["offers"] if o["id"] == oid), None)
    ok = bool(offer and offer["compatible"] and offer["authorized"] and offer["price"] <= task["budget"])
    rec = {"task_id": task["id"], "domain": task["domain"], "condition": cond, "model": model,
           "offer_id": oid, "success": ok, "latency_s": round(dt, 2)}
    with open(out, "a") as f: f.write(json.dumps(rec) + "\n")


def main():
    tasks = build(); out = sys.argv[1] if len(sys.argv) > 1 else "experiments/results/real_parts.jsonl"
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
