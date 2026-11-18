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


### 3.6 Designed for the next twelve years

GCP is specified for the interaction pattern that is emerging, not only for today's app. Three horizons matter.

<b>H1 (2026–2029): assisted commerce.</b> The human initiates a task in a mobile or PC assistant; the agent searches, compares, and prepares a cart; the human approves payment. The interaction is still turn-taking, but the agent absorbs search and form-filling. GCP's job in H1 is to make constraints visible and approvals bounded.

<b>H2 (2029–2033): delegated commerce.</b> The human grants a mandate ("keep the car maintained; buy approved accessories under a monthly budget"); the agent acts proactively, books service, and reorders consumables. The human reviews exceptions, not every step. GCP's job in H2 is to make mandates revocable, auditable, and composable across merchants and OEMs.

<b>H3 (2033–2038): agent-native commerce.</b> Multiple agents negotiate on behalf of a household, a fleet, or a small business; agents transact with agents; the human sets policy and audits outcomes. GCP's job in H3 is to make agent-to-agent negotiation, evidence, liability, and settlement first-class, while preserving a human principal at the root of every delegation chain.

The protocol is deliberately layered so that H1 deployments are not throwaway: the same delegation credential, evidence record, and safety object used for a single purchase in H1 become the policy and audit layer for an autonomous fleet in H3. Table 1 summarizes the interaction shifts and the protocol requirement each shift creates.

<div class="tblwrap"><table><caption>Table 1. Interaction evolution and GCP requirements.</caption>
<thead><tr><th>Horizon</th><th>Who initiates</th><th>Human role</th><th>Protocol requirement</th></tr></thead>
<tbody>
<tr><td>H1 assisted</td><td>human</td><td>approves payment</td><td>discovery, compatibility, bounded step-up</td></tr>
<tr><td>H2 delegated</td><td>human sets policy; agent acts</td><td>reviews exceptions</td><td>revocable mandate, proactive triggers, audit</td></tr>
<tr><td>H3 agent-native</td><td>agents negotiate</td><td>sets policy, audits outcomes</td><td>agent-to-agent contracts, evidence, liability, settlement</td></tr>
</tbody></table></div>

The design implication is that GCP cannot be a thin checkout wrapper. It must carry the <i>policy</i> (who may act, for what, under which limits) and the <i>evidence</i> (what happened, why, and who is accountable) across all three horizons. That is why authorization, safety, and evidence are core objects rather than optional extensions.
