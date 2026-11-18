## Appendix A. Protocol Objects

### A.1 Delegation credential

```json
{
  "gcp_version": "1.0",
  "principal": {"id": "user_123", "verified": true},
  "agent": {"agent_id": "pa_xxx", "public_key": "ed25519:..."},
  "scopes": ["catalog.read", "cart.write", "checkout.execute", "service.book"],
  "constraints": {"budget": {"currency": "CNY", "per_tx_max": 2000},
                  "merchants": {"allow": ["oem_store", "dealer_*"]},
                  "human_step_up": {"amount_over": 1000, "safety_critical": true}},
  "signature": "base64..."
}
```

### A.2 Offer with safety fields

```json
{
  "offer_id": "part_001",
  "type": "part",
  "price": {"amount": 680, "currency": "CNY"},
  "compatibility": {"make": "OEM_A", "model": "X", "year": [2022, 2026]},
  "safety": {"critical": true, "oem_approved": true, "certifications": ["ECE-R90"]},
  "inventory": {"qty": 4},
  "merchant_authorized": true
}
```

### A.3 Typed error

```json
{"code": "SLOT_CONFLICT", "retryable": true, "requires_human": false,
 "message": "The selected service slot is no longer available.",
 "alternatives": ["O1", "O3"], "evidence_id": "ev_..."}
```

## Appendix B. Conformance Suite

A GCP implementation is tested at five levels:
1. **L1 catalog:** manifest discovery, schema validation, vehicle filter.
2. **L2 commerce:** cart TTL, quote, idempotent checkout, price-change handling.
3. **L3 payment:** intent creation, step-up, capture, refund, reconciliation.
4. **L4 service/insurance:** booking capacity, eligibility, cooling-off, evidence.
5. **L5 safety/aftercare:** safety block, recall block, warranty/claim linkage.

The suite includes negative tests for incompatible offers, unauthorized merchants, expired consent, duplicate orders, payment decline, and slot conflict. A merchant that fails a required level cannot claim conformance.

## Appendix C. Human Baseline Parameters and Sensitivity

The human model is a Monte Carlo simulation, not human-subject data. Parameters:

| Domain | Misbuy | Authorization error | Time (min) | Recovery |
|---|---|---|---|---|
| Parts | 0.18 | 0.06 | 8–20 | 0.55 |
| Merchandise | 0.08 | 0.03 | 4–12 | 0.70 |
| Service | 0.12 | 0.05 | 10–25 | 0.60 |
| Insurance | 0.10 | 0.08 | 15–35 | 0.50 |

Sensitivity: varying the parts misbuy rate from 0.10 to 0.25 changes the human success rate by ±7 percentage points; varying merchandise from 0.04 to 0.12 changes it by ±4 points. The qualitative comparison in Section 9 is stable across these ranges.

## Appendix D. Integration Checklist

**Merchant:** publish manifest; implement catalog/checkout; add PSP adapter; run conformance; publish safety feeds.
**OEM:** deploy authorization vault and vehicle-context service; register merchants; publish safety rules; set step-up thresholds; monitor evidence.
**PA vendor:** import tool schema (MCP/A2A); request scopes; implement step-up and revocation UI; display evidence and alternatives.
**Cockpit:** enforce parked/step-up rules; voice-first confirmations; block L3+ while moving.

## Appendix E. Reproducibility

The repository contains `spec/GCP-1.0.md`, the benchmark (`experiments/bench/tasks.py`), the environment and scorer (`env.py`), the runner (`runner.py`), the human model, and all raw results. Commands:

```bash
export DASHSCOPE_API_KEY=...
python3 experiments/bench/runner.py --out experiments/results/acb.jsonl --tasks 60
python3 experiments/bench/analyze.py
```
