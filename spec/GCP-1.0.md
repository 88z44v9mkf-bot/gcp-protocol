# GCP 1.0 — Automotive & Mobility Commerce Protocol

Status: public draft for paper and industry review.
Scope: personal agents (PA) acting for a user in automotive and mobility commerce: parts and accessories, branded merchandise, after-sales maintenance and repair, insurance and mobility services, vehicle reservation/test-drive, and vehicle ordering.
Design goals: open, capability-based, safety-aware, payment-agnostic, interoperable with Poppy (identity/session), UCP (universal commerce), and ACP (agentic checkout/payment).

## 1. Design principles

1. **Principal-first.** Every action is bound to a human principal through a verifiable delegation credential. The agent never holds the user's long-term payment credential.
2. **Capability, not endpoint.** Merchants expose capabilities (discover, quote, cart, checkout, book, bind, aftercare) with explicit schemas; agents negotiate what they can use.
3. **Safety before commerce.** Vehicle-safety rules (safety-critical parts, recalls, compatibility, insurance eligibility) are evaluated before an order is placed; a safe block cannot be overridden by a prompt.
4. **Authorize once, constrain always.** Users grant scopes with budget, time, merchant, and item constraints; every transaction is checked against the grant at execution time.
5. **Payment-agnostic.** GCP defines payment *intent* and *evidence*; the actual rail (card, wallet, Alipay, WeChat Pay, UCP/ACP payment, bank transfer, OEM finance) is a pluggable adapter.
6. **Auditable by default.** Every decision, consent, exception, and settlement emits a signed evidence record; logs are exportable to the user and the OEM.
7. **Compatible by translation.** GCP is a superset with explicit profile mappings: `profile=ucp`, `profile=acp`, `profile=poppy`; unsupported fields degrade with declared loss.
8. **Fail closed, recover gracefully.** Unknown actions are rejected; exceptions have typed recovery paths (retry, re-auth, substitute, escalate, refund).

## 2. Layered architecture

```
+-------------------------------------------------------------+
|  PA runtime (mobile, PC, cockpit, third-party assistant)    |
+-------------------------------------------------------------+
|  GCP client: intent -> authorization -> plan -> execute     |
+-------------------------------------------------------------+
|  GCP core: discovery | catalog | cart/order | booking       |
|            payment intent | fulfillment | aftercare         |
+-------------------------------------------------------------+
|  Safety & compliance engine | evidence ledger | error bus   |
+-------------------------------------------------------------+
|  Transport bindings: HTTPS/JSON, MCP tools, A2A messages     |
+-------------------------------------------------------------+
|  Adapters: UCP | ACP | Poppy | OEM DMS/ERP | PSPs           |
+-------------------------------------------------------------+
```

## 3. Identity and delegation

### 3.1 Principals and agents
- `principal`: the human user (OEM account, mobility account, or guest with verified phone).
- `agent`: a PA instance with a key pair and a stable `agent_id`.
- `delegate`: an optional sub-agent (e.g., a cockpit assistant delegating to a service agent).

### 3.2 Delegation credential (Poppy-compatible)

```json
{
  "gcp_version": "1.0",
  "credential_id": "cred_01H...",
  "principal": {"id": "user_123", "id_type": "oem_account", "verified": true},
  "agent": {"agent_id": "pa_doubao_xxx", "public_key": "ed25519:..."},
  "scopes": ["catalog.read", "cart.write", "checkout.execute", "service.book", "insurance.bind"],
  "constraints": {
    "budget": {"currency": "CNY", "per_tx_max": 2000, "period_max": 8000, "period": "P30D"},
    "merchants": {"allow": ["oem_store", "dealer_*"], "deny": ["unauthorized_marketplace"]},
    "items": {"safety_critical": "requires_oem_approval", "vehicle_id": "VIN_..."},
    "time": {"not_before": "2026-11-18T00:00:00Z", "not_after": "2026-12-18T00:00:00Z"},
    "human_step_up": {"amount_over": 1000, "new_merchant": true, "safety_critical": true}
  },
  "signature": "base64..."
}
```

Rules:
- The credential is short-lived (default 30 days) and revocable; revocation propagates to merchants within one heartbeat.
- Each transaction carries a `consent_receipt` referencing the credential and the exact intent hash.
- Sub-delegation is allowed only if `scopes` include `delegate` and constraints are narrowed (never widened).

### 3.3 Authorization ladder
| Level | Scope | Example | Human involvement |
|---|---|---|---|
| L0 | read-only | browse parts, compare insurance | none |
| L1 | cart/quote | add to cart, hold slot | none, notify |
| L2 | bounded pay | pay <= per-tx limit, allowed merchants | biometric/PIN at first use |
| L3 | high-value pay | vehicle deposit, insurance bind | explicit step-up (biometric + confirmation) |
| L4 | irreversible | registration, contract signature | human-only, agent prepares |

## 4. Discovery

`GET /.well-known/gcp` returns a manifest:

```json
{
  "gcp_version": "1.0",
  "merchant": {"id": "dealer_001", "name": "Example Dealer", "country": "CN"},
  "capabilities": ["catalog.read", "cart.write", "checkout.execute", "service.book", "aftercare.claim"],
  "catalogs": [{"id": "parts", "url": "https://.../gcp/catalog/parts", "vehicle_filter": true}],
  "payments": [{"rail": "alipay", "mode": "redirect"}, {"rail": "wechat_pay", "mode": "jsapi"}, {"rail": "ucp_payment", "mode": "token"}],
  "service_areas": ["310000", "330100"],
  "profiles": {"ucp": "https://.../ucp", "acp": "https://.../acp", "poppy": "https://.../poppy"},
  "safety": {"recall_feed": "https://.../recalls", "certified_parts_only": true}
}
```

Agents MUST negotiate capabilities before use; unknown capability => `CAPABILITY_UNSUPPORTED`, not a silent failure.

## 5. Catalog and vehicle context

Offer object:

```json
{
  "offer_id": "part_brake_pad_001",
  "type": "part",
  "title": "Front brake pad set",
  "sku": "BP-1234",
  "price": {"amount": 680, "currency": "CNY", "tax_included": true},
  "compatibility": {"make": "OEM_A", "model": "X", "year": [2022, 2026], "vin_pattern": "L6T..."},
  "safety": {"critical": true, "oem_approved": true, "certifications": ["ECE-R90"], "recall_status": "clear"},
  "warranty": {"months": 24, "scope": "parts_and_labor"},
  "inventory": {"qty": 4, "location": "dealer_001"},
  "fulfillment": ["pickup", "install"],
  "evidence": {"source": "DMS", "updated_at": "2026-11-18T..."}
}
```

Vehicle context is a first-class object (`vehicle_id`, VIN hash, model/year, mileage, service history, open recalls). Agents MUST pass it to compatibility checks; merchants MUST reject incompatible offers with `VEHICLE_INCOMPATIBLE`.

## 6. Commerce flow

1. `intent.create` — user intent, budget, preferences, vehicle context, authorization reference.
2. `catalog.search` / `catalog.get` — offers filtered by compatibility, availability, safety.
3. `cart.add` / `cart.update` — holds inventory for a TTL.
4. `checkout.quote` — price, tax, delivery/installation, insurance, final constraints.
5. `checkout.execute` — requires execution-time authorization check; idempotent `order_id`.
6. `payment.intent` — PSP-specific authorization; human step-up if needed.
7. `fulfillment.create` — delivery, installation appointment, or service slot.
8. `aftercare.register` — warranty, returns, claims.

Every mutating call carries `Idempotency-Key` and `consent_receipt`. Duplicate keys return the original result.

## 7. Payment abstraction

Payment intent (rail-neutral):

```json
{
  "payment_intent_id": "pi_...",
  "amount": {"value": 680, "currency": "CNY"},
  "rail": "alipay",
  "capture": "on_fulfillment",
  "risk": {"user_present": true, "sca": "biometric", "device": "cockpit"},
  "split": [{"party": "dealer", "amount": 600}, {"party": "oem", "amount": 80}],
  "refund_policy": "7d",
  "evidence": {"consent_receipt": "...", "authorization_hash": "..."}
}
```

Rails:
- **Domestic CN**: Alipay (page/JSAPI/mini-program), WeChat Pay (JSAPI/Native), UnionPay, OEM wallet, finance/lease.
- **International**: card/PSP (Stripe/Adyen), Apple/Google Pay, SEPA, local wallets.
- **Agent-native**: UCP payment token, ACP checkout token.
- **High-value**: escrow/hold, deposit, split settlement, invoice.

The agent never sees PANs; PSP tokens are scoped to one intent and one merchant.

## 8. Service, insurance, vehicle reservation

- `service.book`: service catalog, bay capacity, parts availability, loaner, pickup; conflict resolution with typed alternatives.
- `insurance.quote`/`bind`: underwriting fields, eligibility, consent, cooling-off; binding is L3+.
- `vehicle.reserve`: test-drive slot or vehicle order deposit; identity and license verification; deposit refund rules.
- `aftercare.claim`: warranty claim, recall scheduling, return/refund; evidence chain links to original order and service record.

## 9. Safety and compliance engine

Rules evaluated before checkout:
1. Safety-critical part must be OEM-approved or certified (ECE-R90, etc.); otherwise `SAFETY_BLOCK`.
2. Open recall on the vehicle blocks non-recall service purchases until acknowledged.
3. Insurance eligibility and consent rules (age, license, region).
4. Vehicle order/deposit: cooling-off, identity, license, payment limits.
5. Data minimization: VIN and personal data are hashed/tokenized; merchants receive only what the scope allows.
6. Regional rules: UN R155/R156 (cybersecurity/software update) evidence for connected services; local consumer protection; cross-border data.

Safety decisions are emitted as signed evidence; an agent prompt cannot override a block.

## 10. Exception and recovery taxonomy

| Code | Meaning | Default recovery |
|---|---|---|
| `VEHICLE_INCOMPATIBLE` | part/service not valid for VIN | suggest compatible alternatives |
| `SAFETY_BLOCK` | safety rule violated | escalate to human/OEM; no auto-override |
| `OUT_OF_STOCK` | inventory gone | substitute/backorder/nearest dealer |
| `PRICE_CHANGED` | quote expired | re-quote, require consent if increase > threshold |
| `PAYMENT_DECLINED` | PSP decline | alternate rail, retry policy, human step-up |
| `SCA_REQUIRED` | strong customer auth | biometric/PIN challenge |
| `SLOT_CONFLICT` | service bay unavailable | nearest slots, loaner, reschedule |
| `UNDERWRITING_REJECT` | insurance ineligible | explain, alternatives, human review |
| `RECALL_BLOCK` | open recall | book recall service first |
| `DUPLICATE_ORDER` | idempotency conflict | return original order |
| `TIMEOUT` | network/merchant timeout | retry with backoff, then escalate |
| `CONSENT_EXPIRED` | delegation expired/revoked | re-authorize |
| `POLICY_BLOCK` | merchant/region policy | explain, no retry |

Each error carries `retryable`, `requires_human`, `alternatives`, and `evidence_id`.

## 11. Compatibility with Poppy, UCP, ACP

### 11.1 Poppy (identity/session)
GCP consumes Poppy credentials as `principal` + `delegate`; Poppy session tokens map to GCP `session_id`. GCP adds commerce scopes, budget constraints, and evidence requirements. Translation is lossless for identity; commerce-specific constraints remain in GCP.

### 11.2 UCP (universal commerce)
Mapping:
| GCP | UCP |
|---|---|
| manifest | discovery document |
| catalog.offer | product/variant |
| cart | cart |
| checkout.quote/execute | checkout |
| payment.intent | payment handler |
| fulfillment | fulfillment options |
GCP-specific fields (vehicle compatibility, safety, aftercare, authorization) are carried as extension namespaces `gcp.vehicle`, `gcp.safety`, `gcp.auth`. If UCP endpoint lacks them, GCP falls back to local validation and marks `lossy=true`.

### 11.3 ACP (agentic commerce/checkout)
GCP maps `checkout.execute` to ACP checkout session, `payment.intent` to ACP payment token, and adds GCP authorization/evidence. ACP handles the PSP handshake; GCP enforces the principal/delegation and safety layers.

### 11.4 Capability negotiation
The agent sends `Accept-Profile: gcp=1.0, ucp=..., acp=..., poppy=...`; the merchant selects the highest mutually supported profile and returns `profile_used` + `lossy` flags. Unsupported required capabilities fail closed.

## 12. Integration patterns

- **Third-party PA products** (Doubao, Qwen, Lingguang, DeepSeek, ChatGPT, Claude, WorkBuddy, etc.): integrate via MCP tools or A2A; GCP exposes discover/catalog/cart/checkout/book tools; auth via Poppy-style delegation or OAuth.
- **OEM mobile/PC apps**: native SDK or HTTPS client; shared authorization vault.
- **Cockpit**: voice-first, short confirmation, driver-distraction constraints; no high-value purchase while driving (L3+ blocked unless parked).
- **Dealers/merchants**: DMS/ERP adapter; catalog sync; service capacity; aftercare.
- **Insurers**: quote/bind adapter; consent and cooling-off.
- **Payment providers**: PSP adapters; tokenization; reconciliation.

## 13. Security and privacy

- mTLS + signed requests; replay protection (nonce/timestamp).
- Short-lived tokens; revocation list; per-merchant keys.
- PII minimization; VIN hashing; consent receipts; data residency.
- Prompt-injection defense: untrusted catalog text is data, never instructions; tool outputs are schema-validated; allowlists.
- Fraud: velocity limits, device binding, step-up.
- Evidence ledger: append-only hash chain; user-exportable.

## 14. Versioning and conformance

- Semantic versioning; capability negotiation; deprecation policy (12 months).
- Conformance levels: L1 catalog, L2 cart/checkout, L3 payment, L4 service/insurance, L5 aftercare + safety.
- Test suite: schema validation, compatibility rejection, authorization checks, exception recovery, idempotency, evidence chain.

## 15. Loading and adoption

1. Merchant: implement `/.well-known/gcp`, catalog/checkout endpoints, PSP adapter, conformance L2+.
2. OEM: deploy authorization vault + vehicle context service; register merchants; publish safety rules.
3. PA vendor: import GCP tool schema (MCP/A2A) or SDK; request delegation scopes; implement step-up UI.
4. Pilot: start L1/L2 (parts/merchandise), then L3 (service/insurance), then L4 (vehicle order).
5. Measure: success, misbuy, authorization load, exception recovery, safety blocks; publish conformance results.
