"""Run the GCP conformance cases against a merchant base URL."""
from __future__ import annotations
import argparse, json, subprocess, sys, time, urllib.error, urllib.request

TOKENS = {"token_full": "token_full", "token_read": "token_read", "token_expired": "token_expired"}


def call(base, case, ctx):
    url = base + case["path"]
    body = json.dumps(case.get("body", {})).encode() if case["method"] != "GET" else None
    # template substitution
    def sub(x):
        if isinstance(x, str):
            for k, v in ctx.items(): x = x.replace("{{" + k + "}}", str(v))
        return x
    body = sub(body.decode()).encode() if body else None
    req = urllib.request.Request(url, data=body, method=case["method"])
    req.add_header("Authorization", "Bearer " + case.get("auth", "token_read"))
    req.add_header("Content-Type", "application/json")
    for k, v in case.get("headers", {}).items(): req.add_header(k, v)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status, dict(r.headers), json.loads(r.read().decode() or "{}")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), json.loads(e.read().decode() or "{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8099")
    ap.add_argument("--cases", default="conformance/cases.json")
    ap.add_argument("--report", default="conformance/report.json")
    ap.add_argument("--no-server", action="store_true")
    args = ap.parse_args()
    proc = None
    if not args.no_server:
        proc = subprocess.Popen([sys.executable, "conformance/mock_merchant.py"])
        time.sleep(0.8)
    cases = json.load(open(args.cases)); results = []; ctx = {}
    try:
        for c in cases:
            status, headers, body = call(args.base, c, ctx)
            ok = status == c["expect_status"]
            if "expect_code" in c: ok = ok and body.get("code") == c["expect_code"]
            for k, v in c.get("expect_json", {}).items(): ok = ok and body.get(k) == v
            for k, v in c.get("expect_header", {}).items(): ok = ok and headers.get(k) == v
            for local, field in c.get("save", {}).items(): ctx[local] = body.get(field)
            results.append({"id": c["id"], "pass": ok, "status": status, "expect_status": c["expect_status"],
                            "code": body.get("code"), "body": body if not ok else None})
            print(("PASS" if ok else "FAIL"), c["id"], status, body.get("code", ""))
    finally:
        if proc: proc.terminate()
    report = {"total": len(results), "passed": sum(r["pass"] for r in results), "results": results}
    json.dump(report, open(args.report, "w"), indent=1)
    print(f"{report['passed']}/{report['total']} passed -> {args.report}")
    return 0 if report["passed"] == report["total"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
