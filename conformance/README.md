# GCP Conformance Suite

This directory contains a reference mock merchant and an executable conformance suite for GCP 1.0.

## What it tests

| Level | Tests |
|---|---|
| L1 Catalog | manifest, catalog, vehicle filter |
| L2 Cart/checkout | cart, quote, idempotent checkout, replay |
| L3 Payment | payment intent, scope denial |
| L4 Service | slot conflict and alternatives |
| L5 Safety | safety block, incompatible part |
| X Cross-cutting | consent expiry, evidence lookup |

## Run

```bash
python3 conformance/run.py
```

Expected:

```text
PASS GCP-L1-01 200
...
13/13 passed -> conformance/report.json
```

The runner starts `mock_merchant.py` on `127.0.0.1:8099`, executes the cases in `cases.json`, and writes a machine-readable report to `conformance/report.json`.

## Current result

13/13 passing (November 2026).

## Extending

Add a case to `cases.json` with `id`, `level`, `method`, `path`, `auth`, optional `body`/`headers`, `expect_status`, and `expect_code`/`expect_json`/`expect_header`. The runner supports `{{cart_id}}`-style substitution and response capture. Merchants should run the suite in CI; a public directory of conforming implementations is a next step.
