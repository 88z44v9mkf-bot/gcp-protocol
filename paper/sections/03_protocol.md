## 3. The GCP Protocol

### 3.1 Design principles

GCP is built on eight principles: principal-first delegation; capability-based discovery; safety before commerce; authorize once and constrain always; payment-agnostic intent; auditable evidence; compatibility by translation; and fail-closed recovery. The full specification is released with this paper; this section summarizes the objects and flows that matter for evaluation.

### 3.2 Architecture

GCP has five layers: (i) the <b>PA runtime</b> (mobile, PC, cockpit, or third-party assistant); (ii) the <b>GCP client</b>, which turns a user intent into an authorized plan; (iii) the <b>GCP core</b> (discovery, catalog, cart/order, booking, payment intent, fulfillment, aftercare); (iv) the <b>safety and evidence layer</b>; and (v) <b>transport and adapters</b> (HTTPS/JSON, MCP tools, A2A messages, Poppy/UCP/ACP profiles, OEM DMS/ERP, payment service providers). Figure 1 shows the architecture.

[[FIG:figures/fig_gcp_arch.svg|Figure 1. GCP architecture. The agent plan is authorized against a delegation credential; the safety engine can block a transaction before checkout; payment is an intent executed by a rail adapter; every step emits evidence.]]

### 3.3 Core objects

<b>Delegation credential.</b> A signed object binding principal, agent, scopes, constraints (budget, merchants, items, time), and step-up rules. It is short-lived and revocable. Poppy credentials can be consumed directly; when they lack commerce scopes, GCP wraps them with a commerce delegation.

<b>Manifest.</b> `/.well-known/gcp` declares merchant identity, capabilities, catalogs, payment rails, service areas, safety feeds, and profiles (UCP/ACP/Poppy). Capability negotiation precedes any transaction.

<b>Vehicle context.</b> A tokenized vehicle object (VIN hash, make/model/year, mileage, service history, open recalls). It is passed to compatibility checks and never stored by merchants beyond the transaction.

<b>Offer.</b> A product or service with price, compatibility, safety attributes (critical, OEM-approved, certifications, recall status), warranty, inventory, fulfillment, and evidence source.

<b>Order and booking.</b> Cart holds inventory with a TTL; checkout produces a quote (price, tax, delivery/installation, insurance) and an idempotent order; service and reservation produce a booking with capacity and cancellation rules.

<b>Payment intent.</b> A rail-neutral object with amount, capture mode, split settlement, risk signals, refund policy, and evidence. The rail adapter executes it; the agent never sees a PAN.

<b>Evidence record.</b> An append-only, hash-chained record of consent, checks, errors, and settlement, exportable to the user and the OEM.

### 3.4 Commerce flow

The canonical flow is: `intent.create` → `catalog.search`/`catalog.get` → `cart.add` → `checkout.quote` → `checkout.execute` → `payment.intent` → `fulfillment.create` → `aftercare.register`. Every mutating call carries an `Idempotency-Key` and a `consent_receipt`; duplicate keys return the original result. Execution-time checks re-validate the credential, budget, merchant allowlist, compatibility, and safety rules, so a stale plan cannot bypass a revocation.

### 3.5 What GCP adds beyond generic commerce

Three protocol objects are unique to GCP: (i) <b>vehicle context</b> as a required input to compatibility; (ii) <b>safety eligibility</b> as a pre-checkout gate with signed evidence; and (iii) <b>aftercare linkage</b>, where warranty, recall, and service records are attached to the original order. These objects are what turn a generic checkout into automotive commerce. A protocol that omits them can complete a transaction but cannot prevent a wrong or unsafe one.
