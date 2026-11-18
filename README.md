# GCP: A Safety-Aware Commerce Protocol for Automotive and Mobility Agents

Jipu Su — Chief AI-Native Scientist, Geely Automobile Group; Professor, City University of Hong Kong.

This repository contains the GCP 1.0 specification, the AutomotiveCommerce-Bench (ACB), a real-LLM evaluation harness, a calibrated human baseline, and the paper.

## Why GCP

Poppy, UCP, and ACP solve identity, generic commerce, and agentic checkout. Automotive and mobility commerce adds constraints those protocols do not encode: vehicle compatibility, safety-critical parts, authorized service networks, insurance underwriting, vehicle deposits, after-sales, and region-specific payment rails. GCP makes those constraints first-class and auditable.

## Contents

```
spec/GCP-1.0.md          protocol specification (objects, flows, auth, payments, safety, errors, compatibility)
paper/                   manuscript sources and compiled PDF
experiments/bench/       tasks, environment, scorer, LLM runner, human model, analysis
experiments/results/     raw runs, summary, figures
```

## Core design

- Vehicle context and safety gates before checkout.
- Revocable delegation ladder (L0 browse → L4 human-only) with budget, merchant, time, and step-up constraints.
- Payment intent abstraction over card/PSP, Alipay, WeChat Pay, UnionPay, OEM finance, UCP/ACP tokens.
- Typed errors with retryable/requires_human/alternatives.
- Profiles for Poppy (identity), UCP (catalog/cart/checkout), ACP (agentic payment), with explicit lossy conversion.

## Benchmark

ACB has 60 tasks across parts, merchandise, after-sales service, and insurance/reservation, each with a valid offer, a near-miss trap, and an over-budget/unauthorized option. Conditions: C0 manual web, C1 generic agent commerce, C2 GCP.

Run:

```bash
export DASHSCOPE_API_KEY=...
python3 experiments/bench/runner.py --out experiments/results/acb.jsonl --tasks 60 --workers 18
python3 experiments/bench/analyze.py
```

## Results

| Condition | Success | Misbuy | Recovery |
|---|---|---|---|
| Manual web (C0) | 64.5% | 35.5% | 58.3% |
| Generic agent (C1) | 69.4% | 30.6% | 59.4% |
| GCP (C2) | **92.2%** | **7.8%** | **89.6%** |

The gain is concentrated in service (44%→86%) and insurance (13%→82%), where constraints are hidden in ordinary web pages. A calibrated human model gives 68.5–82.7% success and 8–25 minutes per task; it is a model, not human-subject data.

A Stripe test-mode authorization study (180 charges, 180/180 reconciled, USD 71,808 of test money) shows that bounded delegation cuts human approvals by 70% relative to per-transaction approval with no loss of success. A semi-field study on 30 real catalog tasks shows no degradation (100% success in both C1 and C2); it is a non-degradation check, not a discriminating test.

## Paper

`paper/main.pdf` (14 pages). The manuscript is built from `paper/sections/*.md` with `paper/build/build.py`.

## License

Code: MIT. Paper and results: CC BY 4.0.
