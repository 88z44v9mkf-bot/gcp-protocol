# GCP 1.0 — General Commerce Protocol for Automotive and Mobility

**Status:** Public draft for industry review (v1.0-draft, November 2026)
**Editors:** Jipu Su
**License:** This specification is released under CC BY 4.0. Implementations may use it royalty-free.
**Scope:** Personal agents (PA) acting for a human principal in automotive and mobility commerce: parts and accessories, branded merchandise, after-sales maintenance and repair, insurance and mobility services, vehicle reservation/test-drive, and vehicle ordering.
**Relationship to other protocols:** GCP is a vertical commerce profile that composes with Poppy (identity and delegation), UCP (universal commerce), and ACP (agentic checkout/payment). It does not replace them.

## 0. Normative language

The key words MUST, MUST NOT, REQUIRED, SHALL, SHALL NOT, SHOULD, SHOULD NOT, RECOMMENDED, MAY, and OPTIONAL are to be interpreted as described in RFC 2119 and RFC 8174.

A **conforming implementation** is one that satisfies at least one conformance level in Section 13 and passes the corresponding tests in the public conformance suite.

## 1. Design principles

1. **Principal-first.** Every action MUST be bound to a human principal through a verifiable delegation credential. An agent MUST NOT hold a user's long-term payment credential.
2. **Capability, not endpoint.** Merchants MUST expose capabilities with explicit schemas; agents MUST negotiate capabilities before use.
3. **Safety before commerce.** Safety eligibility MUST be evaluated before checkout. A safety block MUST NOT be overridable by a prompt, a client flag, or a merchant request.
4. **Authorize once, constrain always.** Delegation MUST carry scopes and constraints (budget, merchants, items, time, step-up). Every mutating call MUST re-check the credential at execution time.
5. **Payment-agnostic.** GCP defines payment *intent* and *evidence*; the actual rail (card/PSP, wallet, Alipay, WeChat Pay, UnionPay, OEM finance, UCP/ACP token) is an adapter.
6. **Auditable by default.** Every consent, check, error, and settlement MUST emit an evidence record that is exportable to the user and the OEM.
7. **Compatible by translation.** GCP MUST declare profiles for Poppy, UCP, and ACP, and MUST mark any lossy conversion.
8. **Fail closed, recover explicitly.** Unknown actions MUST be rejected. Errors MUST be typed and carry a recovery path.

## 2. Roles and trust boundaries

| Role | Responsibility |
|---|---|
| Principal | Human user; grants/revokes delegation; performs step-up. |
| PA runtime | Mobile, PC, cockpit, or third-party assistant; renders consent and evidence UI. |
| GCP client | Turns intent into an authorized plan; enforces client-side checks. |
| Merchant / provider | Dealer, OEM store, aftermarket merchant, service center, insurer. |
| OEM authorization vault | Issues/revokes credentials, enforces policy, stores evidence (MAY be operated by an OEM or a neutral trust provider). |
| Payment service provider | Executes payment intents; tokenizes credentials. |
| Fitment service | Resolves VIN/vehicle attributes to compatible parts and services. |
| Auditor | User, OEM, regulator, or independent conformance body. |

Trust boundaries: the PA runtime and GCP client are **untrusted** from the merchant's perspective; the merchant and payment adapter are **untrusted** from the principal's perspective. Every cross-boundary action MUST be authenticated, authorized, and evidenced.

## 3. Identity and delegation

### 3.1 Delegation credential

A delegation credential MUST be a signed object with:

```json
{
  "gcp_version": "1.0",
  "credential_id": "cred_...",
  "principal": {"id": "user_123", "id_type": "oem_account", "verified": true},
  "agent": {"agent_id": "pa_xxx", "public_key": "ed25519:..."},
  "scopes": ["catalog.read", "cart.write", "checkout.execute"],
  "constraints": {
    "budget": {"currency": "CNY", "per_tx_max": 2000, "period_max": 8000, "period": "P30D"},
    "merchants": {"allow": ["oem_store", "dealer_*"], "deny": []},
    "items": {"vehicle_id": "veh_...", "safety_critical": "requires_oem_approval"},
    "time": {"not_before": "...", "not_after": "..."},
    "human_step_up": {"amount_over": 1000, "new_merchant": true, "safety_critical": true}
  },
  "signature": "base64..."
}
```

Requirements:
- The credential MUST be short-lived (RECOMMENDED ≤ 30 days) and revocable.
- Scopes MUST be from the registry in Section 13.
- Sub-delegation MUST require the `delegate` scope and MUST narrow constraints; a child credential MUST NOT widen any parent constraint.
- Merchants MUST reject an expired, revoked, or out-of-scope credential with `CONSENT_EXPIRED` or `SCOPE_DENIED`.
- The client MUST send a `consent_receipt` with every mutating request; the receipt MUST bind the credential id, intent hash, and timestamp.

### 3.2 Authorization ladder

| Level | Scopes | Typical action | Human involvement |
|---|---|---|---|
| L0 | `catalog.read` | browse, compare | none |
| L1 | `cart.write`, `quote` | add to cart, hold slot | notify |
| L2 | `checkout.execute` within limit | bounded purchase, service booking | biometric at first use |
| L3 | `high_value.pay`, `insurance.bind` | insurance bind, vehicle deposit | explicit step-up |
| L4 | `contract.sign`, `registration` | contract/registration | human-only; agent prepares |

An implementation MUST enforce the level at execution time, not only at plan time.

## 4. Discovery

`GET /.well-known/gcp` MUST return a manifest:

```json
{
  "gcp_version": "1.0",
  "merchant": {"id": "dealer_001", "name": "Example Dealer", "country": "CN"},
  "capabilities": ["catalog.read", "cart.write", "checkout.execute", "service.book", "aftercare.claim"],
  "catalogs": [{"id": "parts", "url": "/gcp/catalog/parts", "vehicle_filter": true}],
  "payments": [{"rail": "alipay", "mode": "redirect"}, {"rail": "wechat_pay", "mode": "jsapi"}],
  "service_areas": ["310000"],
  "profiles": {"poppy": "/poppy", "ucp": "/ucp", "acp": "/acp"},
  "safety": {"recall_feed": "/gcp/recalls", "certified_parts_only": true}
}
```

Requirements:
- The manifest MUST declare every capability the merchant supports.
- The agent MUST NOT call an undeclared capability.
- The merchant SHOULD advertise profiles and any lossy mappings.

## 5. Catalog and vehicle context

### 5.1 Vehicle context

A vehicle context object MUST contain a tokenized `vehicle_id`, an optional VIN hash, make/model/year, and MAY contain mileage, service history, and open recalls:

```json
{"vehicle_id": "veh_...", "vin_hash": "sha256:...", "make": "OEM_A", "model": "X", "year": 2022,
 "mileage_km": 42000, "open_recalls": [], "service_history": ["..."], "source": "oem_vault"}
```

Raw VINs MUST NOT be stored by merchants beyond the transaction unless the user explicitly consents; a hash or token MUST be used for matching and audit.

### 5.2 Offer

```json
{"offer_id": "part_001", "type": "part", "title": "Front brake pad set",
 "price": {"amount": 680, "currency": "CNY", "tax_included": true},
 "compatibility": {"make": "OEM_A", "model": "X", "year": [2022, 2026], "confidence": 0.98},
 "safety": {"critical": true, "oem_approved": true, "certifications": ["ECE-R90"], "recall_status": "clear"},
 "warranty": {"months": 24}, "inventory": {"qty": 4}, "fulfillment": ["pickup", "install"],
 "merchant_authorized": true, "evidence": {"source": "DMS", "updated_at": "..."}}
```

Requirements:
- Compatibility and safety fields MUST be present for `type=part` and safety-critical services; absence MUST be treated as unknown, not as compatible.
- Inventory MUST be re-checked at checkout; stale inventory MUST produce `OUT_OF_STOCK`.

## 6. Commerce flow

Canonical methods (transport binding: HTTPS/JSON, MCP tools, or A2A messages):

| Method | Purpose |
|---|---|
| `intent.create` | Register intent, budget, preferences, vehicle, authorization. |
| `catalog.search` / `catalog.get` | Search/filter offers by compatibility and availability. |
| `cart.add` / `cart.update` | Hold inventory with TTL. |
| `checkout.quote` | Price, tax, delivery/installation, insurance, final constraints. |
| `checkout.execute` | Idempotent order creation; execution-time checks. |
| `payment.intent` | Create a rail-neutral payment intent. |
| `fulfillment.create` | Delivery, installation, service slot. |
| `aftercare.register` | Warranty, returns, claims. |

Requirements:
- Every mutating call MUST carry `Idempotency-Key`; duplicate keys MUST return the original result.
- `checkout.execute` MUST re-validate credential, budget, merchant allowlist, compatibility, and safety at execution time.
- The flow MUST be resumable: a failed step MUST return the last valid state and a typed error.

## 7. Payment abstraction

```json
{"payment_intent_id": "pi_...", "amount": {"value": 680, "currency": "CNY"},
 "rail": "alipay", "capture": "on_fulfillment",
 "risk": {"user_present": true, "sca": "biometric", "device": "cockpit"},
 "split": [{"party": "dealer", "amount": 600}, {"party": "oem", "amount": 80}],
 "refund_policy": "7d", "evidence": {"consent_receipt": "...", "authorization_hash": "..."}}
```

Requirements:
- The payment intent MUST be rail-neutral; the rail adapter MUST return a token, status, and settlement reference.
- The client MUST NOT receive or store a PAN.
- Tokens MUST be scoped to one intent and one merchant.
- Refunds and chargebacks MUST reconcile against the same intent id.
- Regional rules (e.g., PSD2 SCA, Chinese invoice requirements) MUST be declared as rail capabilities.

## 8. Service, insurance, and reservation

- `service.book`: service catalog, capacity, parts availability, loaner, pickup. A booking MUST declare cancellation and no-show rules.
- `insurance.quote` / `insurance.bind`: eligibility, consent, cooling-off. Binding is L3+.
- `vehicle.reserve`: test-drive slot or vehicle order deposit; identity/license verification; refund rules.
- `aftercare.claim`: warranty/recall/return; evidence MUST link to the original order and service record.

## 9. Safety and compliance

Before checkout the implementation MUST evaluate:

1. Safety-critical part is OEM-approved or certified (`SAFETY_BLOCK` otherwise).
2. Open recall blocks non-recall service purchases until acknowledged (`RECALL_BLOCK`).
3. Insurance eligibility and consent.
4. Vehicle order/deposit identity, license, cooling-off.
5. Data minimization: VIN hashing, scoped fields, regional data rules.
6. Cockpit: L3+ actions MUST be blocked while the vehicle is moving.

Safety decisions MUST be emitted as signed evidence records. A client or merchant MUST NOT override a block; only a human principal MAY resolve a `requires_human` error through the prescribed flow.

## 10. Error model

Errors MUST be JSON with `code`, `retryable`, `requires_human`, `message`, `alternatives`, `evidence_id`.

| Code | Meaning | Retryable | Human |
|---|---|---|---|
| `VEHICLE_INCOMPATIBLE` | part/service not valid | yes (alternatives) | no |
| `SAFETY_BLOCK` | safety rule violated | no | yes |
| `OUT_OF_STOCK` | inventory gone | yes | no |
| `PRICE_CHANGED` | quote expired | yes | if above threshold |
| `PAYMENT_DECLINED` | PSP decline | yes (alternate rail) | if repeated |
| `SCA_REQUIRED` | strong customer auth | yes | yes |
| `SLOT_CONFLICT` | service capacity conflict | yes | no |
| `UNDERWRITING_REJECT` | insurance ineligible | no | yes |
| `RECALL_BLOCK` | open recall | yes (book recall) | no |
| `DUPLICATE_ORDER` | idempotency conflict | no | no |
| `TIMEOUT` | network/merchant timeout | yes | if repeated |
| `CONSENT_EXPIRED` | credential expired/revoked | yes (re-auth) | yes |
| `SCOPE_DENIED` | action outside scope | no | yes |
| `CAPABILITY_UNSUPPORTED` | capability not declared | no | yes |

## 11. Compatibility profiles

### 11.1 Poppy
GCP MUST consume Poppy principal/delegation/session as `principal`, `delegate`, `session_id`. Poppy identity mapping is lossless; commerce constraints remain GCP.

### 11.2 UCP
| GCP | UCP |
|---|---|
| manifest | discovery document |
| offer | product/variant |
| cart | cart |
| checkout | checkout |
| payment intent | payment handler |
| fulfillment | fulfillment options |

GCP fields (`gcp.vehicle`, `gcp.safety`, `gcp.auth`) MUST be carried as extension namespaces. If the peer cannot carry them, the client MUST mark `lossy=true` and apply local checks.

### 11.3 ACP
`checkout.execute` maps to ACP checkout session; `payment.intent` maps to ACP payment token. ACP MAY complete the PSP handshake; GCP MUST retain authorization and safety authority.

### 11.4 Negotiation
The client MUST send `Accept-Profile`; the merchant MUST return `profile_used` and `lossy`. Required unsupported capabilities MUST fail with `CAPABILITY_UNSUPPORTED`.

## 12. Security and privacy

- mTLS and signed requests; replay protection (nonce + timestamp).
- Short-lived tokens, revocation list, per-merchant keys.
- PII minimization; VIN hashing; data residency; consent receipts.
- Prompt-injection defense: untrusted catalog text is data, never instructions; tool outputs MUST be schema-validated; allowlists and step-up limit blast radius.
- Fraud controls: velocity limits, device binding, anomaly detection.
- Evidence ledger: append-only hash chain; user-exportable.

## 13. Conformance levels and scopes

| Level | Name | Requirements |
|---|---|---|
| L1 | Catalog | manifest, catalog, vehicle filter, offer schema |
| L2 | Cart/checkout | cart TTL, quote, idempotent execute, price/inventory errors |
| L3 | Payment | payment intent, step-up, capture, refund, reconciliation |
| L4 | Service/insurance | booking capacity, eligibility, cooling-off, evidence |
| L5 | Safety/aftercare | safety block, recall block, warranty/claim linkage |

**Scopes:** `catalog.read`, `cart.write`, `quote`, `checkout.execute`, `payment.intent`, `service.book`, `insurance.bind`, `vehicle.reserve`, `aftercare.claim`, `delegate`, `evidence.read`.

Conformance tests MUST cover: discovery, capability denial, compatibility rejection, safety block, budget/authorization, idempotency, duplicate order, out-of-stock, slot conflict, payment decline, consent expiry, evidence chain, lossy profile conversion.

## 14. Governance and change process

- The specification is versioned semantically; breaking changes require a major version.
- A public change process MUST allow implementers to propose changes; a steering group with OEMs, dealers, insurers, payment providers, and PA vendors SHOULD review.
- Conformance certification SHOULD be independent of any single OEM.
- Security vulnerabilities MUST have a private reporting channel and a coordinated disclosure timeline.
- The core protocol MUST remain royalty-free.

## 15. Changelog

| Version | Date | Change |
|---|---|---|
| 1.0-draft | 2026-11 | Initial public draft: objects, flows, authorization, payments, safety, errors, profiles, conformance. |

## Appendix A. Minimal JSON schemas

### A.1 Delegation credential
```json
{"type":"object","required":["gcp_version","credential_id","principal","agent","scopes","signature"],
 "properties":{"gcp_version":{"const":"1.0"},"scopes":{"type":"array","items":{"type":"string"}},
 "constraints":{"type":"object"},"signature":{"type":"string"}}}
```

### A.2 Typed error
```json
{"type":"object","required":["code","retryable","requires_human","message"],
 "properties":{"code":{"type":"string"},"retryable":{"type":"boolean"},"requires_human":{"type":"boolean"},
 "message":{"type":"string"},"alternatives":{"type":"array"},"evidence_id":{"type":"string"}}}
```

## Appendix B. Conformance test identifiers

| ID | Level | Test |
|---|---|---|
| GCP-L1-01 | L1 | manifest is valid and declares capabilities |
| GCP-L1-02 | L1 | catalog rejects incompatible vehicle |
| GCP-L2-01 | L2 | cart hold expires and releases inventory |
| GCP-L2-02 | L2 | checkout is idempotent |
| GCP-L3-01 | L3 | payment intent requires authorization |
| GCP-L3-02 | L3 | refund reconciles to intent |
| GCP-L4-01 | L4 | service slot conflict returns alternatives |
| GCP-L4-02 | L4 | insurance bind requires step-up |
| GCP-L5-01 | L5 | safety-critical non-OEM part is blocked |
| GCP-L5-02 | L5 | recall block prevents non-recall service |
| GCP-X-01 | all | consent expiry is rejected |
| GCP-X-02 | all | lossy profile is marked |
