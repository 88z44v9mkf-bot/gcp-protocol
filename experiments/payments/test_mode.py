"""GCP authorization-friction experiment with Stripe test-mode payments.

Runs GCP purchase tasks under three authorization modes:
  per_tx   : every payment requires a human approval step
  bounded  : auto-approve under USD 500; step-up above
  unbounded: auto-approve everything
Stripe test mode is used; no real money moves.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time
from concurrent.futures import ThreadPoolExecutor, as_completed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "bench"))
from backend import StripeBackend
from ledger import Ledger
from tasks import build_tasks
from env import prompt, _valid

HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
STRIPE = os.environ.get("STRIPE_SECRET_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro"]
MODES = ["per_tx", "bounded", "unbounded"]
LIMIT = 500.0


def call(model, messages, max_tokens=1200):
    import urllib.request
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=180) as r:
        body = json.loads(r.read().decode())
    return body["choices"][0]["message"].get("content") or "", time.time() - t0


def run(task, mode, model, backend, out):
    lat = 0.0
    try:
        content, dt = call(model, prompt(task, "C2_gcp"))
        lat += dt
    except Exception as exc:
        content = ""
    m = re.search(r"\{.*\}", content, re.S)
    try:
        offer_id = json.loads(m.group(0)).get("offer_id") if m else None
    except Exception:
        offer_id = None
    offer = next((o for o in task["offers"] if o["id"] == offer_id), None)
    valid, reason = _valid(task, offer)
    price = offer["price"] if offer else 0
    if mode == "per_tx":
        approval_steps = 1
        approved = valid  # human oracle rejects invalid choices
    elif mode == "bounded":
        approval_steps = 1 if price > LIMIT else 0
        approved = valid
    else:
        approval_steps = 0
        approved = True  # auto-approve; over-budget/unauthorized not blocked
    charged = False
    charge_id, err = "", ""
    if offer and approved:
        try:
            res = backend.charge(price, "usd", f"{offer['title']} ({task['id']})", f"gcp:{task['id']}:{mode}:{model}:{time.time_ns()}", offer["merchant"])
            charged = res.ok
            charge_id = res.charge_id
            err = res.error
        except Exception as exc:
            err = str(exc)
    rec = {"task_id": task["id"], "domain": task["domain"], "mode": mode, "model": model,
           "offer_id": offer_id, "price": price, "valid": valid, "reason": reason,
           "approved": approved, "charged": charged, "charge_id": charge_id, "payment_error": err,
           "auth_steps": approval_steps, "latency_s": round(lat, 2),
           "authorization_violation": (not valid) if mode == "unbounded" else (not approved),
           "success": bool(valid and charged)}
    with open(out, "a") as f: f.write(json.dumps(rec) + "\n")
    return rec


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="experiments/results/payments.jsonl")
    ap.add_argument("--tasks", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()
    if not KEY or not STRIPE:
        print("DASHSCOPE_API_KEY and STRIPE_SECRET_KEY required", file=sys.stderr); return 2
    all_tasks = [t for t in build_tasks(seed=0) if t["domain"] in ("parts", "merchandise")][: args.tasks]
    backend = StripeBackend(STRIPE, live=False)
    os.makedirs(os.path.dirname(args.out), exist_ok=True); open(args.out, "w").close()
    jobs = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for model in MODELS:
            for mode in MODES:
                for t in all_tasks:
                    jobs.append(pool.submit(run, t, mode, model, backend, args.out))
        done = 0
        for fut in as_completed(jobs):
            done += 1
            try: fut.result()
            except Exception as exc: print("job error", exc, file=sys.stderr)
            if done % 20 == 0: print(f"{done}/{len(jobs)}", flush=True)
    print(f"done {len(jobs)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
