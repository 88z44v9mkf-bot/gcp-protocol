"""Analyze ACB results and produce tables/figures data."""
from __future__ import annotations
import json, os, random
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))


def load(path):
    return [json.loads(l) for l in open(path) if l.strip()]


def rate(rows, key):
    return sum(1 for r in rows if r.get(key)) / len(rows) if rows else 0.0


def boot(rows, key, reps=1500, seed=5):
    rng = random.Random(seed)
    by = defaultdict(list)
    for r in rows:
        by[r["task_id"]].append(r)
    tids = list(by)
    vals = []
    for _ in range(reps):
        sample = [r for t in (rng.choice(tids) for _ in tids) for r in by[t]]
        vals.append(rate(sample, key))
    vals.sort()
    return vals[int(.025 * reps)], vals[int(.975 * reps)]


def main():
    rows = load(os.path.join(ROOT, "experiments/results/acb.jsonl"))
    cells = defaultdict(list)
    for r in rows:
        cells[(r["condition"], r["model"])].append(r)
    out = {"n": len(rows), "cells": [], "by_domain": []}
    for (cond, model), rs in sorted(cells.items()):
        d = {"condition": cond, "model": model, "n": len(rs),
             "success": round(rate(rs, "success"), 3),
             "misbuy": round(rate(rs, "misbuy"), 3) if "misbuy" in rs[0] else round(1 - rate(rs, "success"), 3),
             "safety_violation": round(rate(rs, "safety_violation"), 3),
             "authorization_violation": round(rate(rs, "authorization_violation"), 3),
             "steps": round(sum(r["steps"] for r in rs) / len(rs), 2),
             "latency_s": round(sum(r["latency_s"] for r in rs) / len(rs), 2)}
        exc = [r for r in rs if r.get("exception") and r["exception"] != "none"]
        d["recovery"] = round(rate(exc, "success"), 3) if exc else None
        d["n_exception"] = len(exc)
        lo, hi = boot(rs, "success")
        d["success_ci"] = [round(lo, 3), round(hi, 3)]
        out["cells"].append(d)
    for cond in ["C0_web", "C1_generic", "C2_gcp"]:
        for dom in ["parts", "merchandise", "service", "insurance"]:
            rs = [r for r in rows if r["condition"] == cond and r["domain"] == dom]
            out["by_domain"].append({"condition": cond, "domain": dom, "n": len(rs),
                                     "success": round(rate(rs, "success"), 3)})
    from env import human_model
    out["human"] = human_model()
    json.dump(out, open(os.path.join(ROOT, "experiments/results/summary.json"), "w"), indent=1)
    print(json.dumps(out, indent=1)[:4000])


if __name__ == "__main__":
    main()
