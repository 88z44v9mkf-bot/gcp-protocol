# VIN → Vehicle → Fitment: data access design for GCP

This document specifies how GCP resolves a vehicle identity and a compatible part/service. It is the bridge between the protocol's `vehicle context` object and real catalogs.

## 1. Why fitment is the hard part

A VIN is not a catalog key. Two vehicles with the same make/model/year can differ by engine, trim, market, suspension, or production split. Aftermarket catalogs use application tables (ACES/PIES) with qualifiers; OEM catalogs use VIN-specific parts data. A protocol that treats a part as a SKU without fitment will produce exactly the wrong-part failures GCP is designed to prevent.

## 2. Data sources and rights

| Source | What it provides | Access model |
|---|---|---|
| OEM VIN decode / DMS | authoritative build data, OEM part numbers, service parts | OEM API / partner agreement; may be restricted |
| ACES/PIES | aftermarket application and product data | open specification; data licensed by data providers |
| TecDoc / commercial catalogs | broad aftermarket coverage | paid subscription |
| Merchant feeds | merchant-specific fitment, stock, price | merchant agreement |
| Recall feeds | open recalls by VIN/model | regulator/OEM feed |

The implementation MUST NOT assume one source is complete. It SHOULD combine an authoritative OEM decode with an aftermarket application table and mark provenance and confidence on every result.

## 3. Data model

```json
{
  "vehicle": {
    "vehicle_id": "veh_9f2c...",
    "vin_hash": "sha256:...",
    "make": "OEM_A", "model": "X", "year": 2022,
    "engine": "2.0T", "trim": "Premium", "market": "CN",
    "source": "oem_vault", "decoded_at": "2026-11-18T..."
  },
  "application": {
    "part_id": "P001",
    "make": "OEM_A", "model": "X", "year_from": 2022, "year_to": 2024,
    "engine": "2.0T", "position": "front", "qualifiers": ["vented"],
    "source": "ACES", "confidence": 0.98, "valid_from": "2025-01-01"
  },
  "result": {
    "compatible": true, "confidence": 0.98,
    "source": "oem_dms+aces", "evidence_id": "fit_...",
    "requires_human": false, "alternatives": []
  }
}
```

## 4. API

| Method | Path | Purpose |
|---|---|---|
| POST | `/fitment/resolve` | VIN → tokenized vehicle + attributes |
| GET | `/fitment/parts?vehicle_id=&category=` | compatible parts/services |
| POST | `/fitment/check` | check one part against a vehicle |
| GET | `/fitment/applications/{part_id}` | application table for a part |

Rules:
- Raw VINs MUST NOT be returned to merchants; return `vehicle_id` and `vin_hash`.
- Every result MUST carry `confidence`, `source`, and `requires_human`.
- A safety-critical part with confidence below a threshold (RECOMMENDED 0.95) MUST return `requires_human=true`; GCP MUST treat it as a safety block until confirmed.
- Unknown VIN MUST return `UNKNOWN_VIN` with no guessed vehicle.

## 5. Resolution order and fallback

1. Exact VIN decode (OEM) → application match on engine/trim/market.
2. VIN decode without OEM parts data → aftermarket application table.
3. No VIN → make/model/year/engine → application table (confidence capped).
4. No match → `UNKNOWN_VIN` / `NO_APPLICATION`; never guess.

The protocol's `compatibility.confidence` field carries the result; the agent MUST NOT treat low confidence as compatible.

## 6. Privacy and security

- VIN is personal data in many jurisdictions (it can identify a vehicle/owner). Store only a hash/token; restrict raw VIN to the decode step.
- Log fitment decisions as evidence, not raw VINs.
- Rate-limit VIN decode to prevent enumeration.
- Use mTLS and per-caller credentials; audit data access.

## 7. Evaluation plan

- **Coverage:** fraction of VINs resolved to a vehicle and to at least one application.
- **Precision/recall:** on a labeled fitment set (OEM + aftermarket), per category.
- **False-compatible rate:** the fraction of incompatible parts returned as compatible; this is the safety-critical metric and MUST be measured separately.
- **Latency:** p50/p95 resolve + check.
- **Freshness:** age of application data and recall feed.
- **Human escalation rate:** low-confidence results routed to a human.

A pilot should target: false-compatible rate below 0.1% for safety-critical parts, coverage above 95% for the OEM's own VINs, and p95 latency below 300 ms.

## 8. Integration with GCP

- `catalog.search` calls fitment and filters offers by `compatible=true`.
- `checkout.execute` re-checks fitment at execution time (catalog can be stale).
- `safety` block applies when a safety-critical part has low confidence or no OEM approval.
- `aftercare` links the fitment evidence id to warranty/claim records.

## 9. Roadmap

Phase 1: OEM VIN decode + OEM parts for one brand.
Phase 2: aftermarket ACES/PIES for consumables and accessories.
Phase 3: service menus, insurance eligibility, and cross-OEM coverage.
