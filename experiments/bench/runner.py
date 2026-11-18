"""Run ACB against real LLMs."""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from tasks import build_tasks
from env import prompt, exception_for, score

HOST = os.environ.get("DASHSCOPE_HOST", "https://ws-eafvwf0veluppvrv.cn-beijing.maas.aliyuncs.com/compatible-mode/v1")
KEY = os.environ.get("DASHSCOPE_API_KEY", "")
MODELS = ["deepseek-v4.1-flash-1017", "kimi-k3.1-pro", "qwen3.8-flash"]
CONDITIONS = ["C0_web", "C1_generic", "C2_gcp"]
MAXTOK = {"kimi-k3.1-pro": 1800, "deepseek-v4.1-flash-1017": 1400, "qwen3.8-flash": 1400}


def call(model, messages, max_tokens=1400, timeout=180):
    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.0}
    req = urllib.request.Request(HOST.rstrip("/") + "/chat/completions", data=json.dumps(payload).encode(),
                                 headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        body = json.loads(r.read().decode())
    return body["choices"][0]["message"].get("content") or "", time.time() - t0


def parse(content):
    m = re.search(r"\{.*\}", content, re.S)
    if not m: return None
    try:
        return json.loads(m.group(0))
    except Exception:
        return None


def run_one(task, condition, model, out_path):
    steps, lat, errs = 0, 0.0, []
    obj = None
    error_msg = None
    for attempt in range(2):
        msgs = prompt(task, condition, error_msg)
        try:
            content, dt = call(model, msgs, max_tokens=MAXTOK.get(model, 1400))
        except Exception as exc:
            content, dt = "", 0.0
            errs.append(f"{type(exc).__name__}: {exc}")
        steps += 1; lat += dt
        obj = parse(content) or {}
        offer_id = obj.get("offer_id")
        exc = exception_for(task, offer_id)
        if exc and attempt == 0:
            if condition == "C2_gcp":
                error_msg = json.dumps(exc, ensure_ascii=False)
            else:
                error_msg = f"{exc['code']}: {exc['message']}"
            continue
        break
    offer_id = (obj or {}).get("offer_id")
    action = (obj or {}).get("action", "")
    sc = score(task, offer_id, action)
    rec = {"task_id": task["id"], "domain": task["domain"], "condition": condition, "model": model,
           "offer_id": offer_id, "action": action, "steps": steps, "latency_s": round(lat, 2),
           "errors": errs, "exception": task["exception"], **sc}
    with open(out_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
    return rec


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--tasks", type=int, default=60)
    ap.add_argument("--workers", type=int, default=16)
    args = ap.parse_args(argv)
    if not KEY:
        print("DASHSCOPE_API_KEY missing", file=sys.stderr); return 2
    tasks = build_tasks(seed=0)[: args.tasks]
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    open(args.out, "w").close()
    jobs = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        for model in MODELS:
            for cond in CONDITIONS:
                for t in tasks:
                    jobs.append(pool.submit(run_one, t, cond, model, args.out))
        done = 0
        for fut in as_completed(jobs):
            done += 1
            try: fut.result()
            except Exception as exc: print("job error", exc, file=sys.stderr)
            if done % 60 == 0: print(f"{done}/{len(jobs)}", flush=True)
    print(f"done {len(jobs)} -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
