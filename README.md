# GCP: A Safety-Aware Commerce Protocol for Automotive and Mobility Agents

Jipu Su — Chief AI-Native Scientist, Geely Automobile Group; Professor, City University of Hong Kong.

This repository contains the GCP 1.0 specification, the AutomotiveCommerce-Bench (ACB), a real-LLM evaluation harness, a calibrated human baseline, and the paper.

## Why GCP

Poppy, UCP, and ACP solve identity, generic commerce, and agentic checkout. Automotive and mobility commerce adds constraints those protocols do not encode: vehicle compatibility, safety-critical parts, authorized service networks, insurance underwriting, vehicle deposits, after-sales, and region-specific payment rails. GCP makes those constraints first-class and auditable.

## Contents

```
spec/GCP-1.0.md          public GCP 1.0 draft (normative language, objects, flows, auth, payments, safety, errors, profiles, conformance)
paper/                   manuscript sources and compiled PDF
experiments/bench/       tasks, environment, scorer, LLM runner, human model, analysis
conformance/             executable conformance suite (13/13 passing) and mock merchant
fitment/                 VIN -> vehicle -> fitment design, mock service, tests
experiments/results/     raw runs, summary, figures
```

## Specification and conformance

The public draft is `spec/GCP-1.0.md` (RFC 2119 language, conformance levels L1–L5, scopes, error model, profile mappings, governance). The executable suite in `conformance/` starts a mock merchant and runs 13 cases across L1–L5 plus cross-cutting tests; it currently passes 13/13. The runner is intended for merchant CI.

## Fitment

`fitment/README.md` specifies VIN resolution and part/service fitment: data sources and licensing (OEM DMS, ACES/PIES, TecDoc, merchant feeds), tokenized vehicle model, resolution order and confidence, privacy, evaluation metrics, and GCP integration. `fitment/mock_fitment.py` implements the reference API and `fitment/test_fitment.py` covers resolution, unknown VIN, compatible/incompatible parts, and universal accessories.

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

A Stripe test-mode authorization study (180 charges, 180/180 reconciled, USD 71,808 of test money) shows that bounded delegation cuts human approvals by 70% relative to per-transaction approval with no loss of success. A cockpit experiment (24 tasks x 2 states x 2 conditions x 2 models = 192 trajectories) shows that GCP reduces unsafe driving-time purchase attempts from 47.9% to 0% (deferral rises to 81.2%), at the cost of some over-caution when parked (77.1% vs 87.5%). A real aftermarket parts/service-kit catalog (30 tasks, real prices, synthetic compatibility flags) raises success from 26.7% (generic) to 100% (GCP).

## Paper

`paper/main.pdf` (19 pages, 12 tables, 5 figures).

**Preprint:** Research Square, DOI [10.21203/rs.3.rs-11787193/v1](https://doi.org/10.21203/rs.3.rs-11787193/v1) (submitted 18 November 2026; QA/QC check). The manuscript is built from `paper/sections/*.md` with `paper/build/build.py`.

## License

Code: MIT. Paper and results: CC BY 4.0.
