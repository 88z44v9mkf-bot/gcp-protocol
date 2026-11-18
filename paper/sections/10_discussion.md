## 10. Discussion

### 10.1 What GCP changes

The results support the protocol's central claim: the value of a commerce protocol is not that it lets an agent pay, but that it makes the constraints of a domain machine-checkable before the agent pays. In automotive commerce, the three constraints that matter most—vehicle compatibility, safety eligibility, and merchant authorization—are exactly the ones that generic protocols leave in prose or omit. GCP turns them into fields, gates, and typed errors.

### 10.2 Why compatibility matters

The protocol is designed to be adopted, not to replace the ecosystem. A PA vendor that already supports Poppy, UCP, or ACP can translate to GCP and keep its existing checkout; a merchant can start at L2 and add safety and aftercare later. The lossy flag makes the trade-off explicit: a transaction that loses vehicle or safety fields is not silently treated as equivalent.

### 10.3 Payments and regions

Separating payment intent from rail is what makes a single protocol usable in China (Alipay/WeChat/UnionPay), Europe (PSD2/SCA/SEPA), and the US (cards/wallets). The agent never holds a long-term credential; the PSP token is scoped to one intent and one merchant. This is both a security property and a precondition for OEM finance and insurance products.

### 10.4 Human-in-the-loop

The authorization ladder is a practical answer to the trust problem. A user can grant a small budget for parts and merchandise, require step-up for safety-critical parts and insurance, and keep vehicle deposits human-only. Revocation and expiry are protocol-level, not UI-level. This is more usable than asking for approval on every action and safer than an unbounded mandate.

### 10.5 Limitations

<b>Simulated commerce.</b> The benchmark uses synthetic offers and a simulator, not live merchant systems. Payments were exercised in Stripe test mode (180 charges, no live money); a live-money field pilot is the natural next step.

<b>Human baseline.</b> Human error and time are modeled, not measured with human subjects. The parameters are plausible but not universal; Appendix C reports sensitivity. A controlled human study is future work.

<b>OEM and category coverage.</b> The benchmark uses three anonymized OEM profiles, and the semi-field check covers a real merchandise catalog rather than a multi-OEM automotive catalog. Cross-OEM and cross-border catalogs may require additional fields (homologation, tax, language); a multi-OEM field study is future work.

<b>Model coverage.</b> Three models from one endpoint are tested; results may differ with other model families or agent scaffolds.

### 10.6 Adoption path

A practical rollout is staged: (1) L1/L2 for parts and merchandise in one OEM app and one dealer group; (2) L3 for service and insurance with step-up; (3) L4 for vehicle reservation and deposit; (4) third-party PA integration via MCP/A2A; (5) cross-OEM standardization through an open foundation. Each stage has measurable success, misbuy, authorization, and recovery metrics, so adoption can be evidence-driven rather than all-or-nothing.


### 10.7 From protocol to product and business

GCP is designed to be shippable in stages, with a business model at each stage.

<b>Product surface.</b> (1) A <b>merchant gateway</b> that exposes the manifest, catalog, checkout, service booking, and aftercare endpoints; (2) an <b>OEM authorization vault</b> that issues and revokes delegation credentials, enforces step-up, and stores evidence; (3) a <b>PA SDK</b> (mobile, PC, cockpit) that imports the GCP tool schema and renders delegation, step-up, and exception UI; (4) a <b>conformance suite</b> that certifies merchant and PA implementations at L1–L5.

<b>Business models.</b> The protocol itself should be open and royalty-free. Value accrues to the participants: merchants gain qualified agent traffic and lower return/repair costs; OEMs gain service retention, insurance attachment, and accessory sales; PA vendors gain a safe commerce capability without building automotive integrations; payment providers and insurers gain distribution. Revenue can come from gateway SaaS, certification, transaction facilitation, and service/insurance lead generation, not from charging for the specification.

<b>KPIs.</b> Success rate, misbuy/return rate, authorization touches per task, exception recovery, safety-block rate, time-to-first-purchase, merchant onboarding time, and conformance pass rate. These map directly to the metrics in this paper, so pilots can be evaluated with the same instrument.

### 10.8 Open governance

If GCP is to become an industry protocol rather than one OEM's interface, governance matters as much as the schema. We recommend: an open, versioned specification with a public change process; a conformance test suite with independent certification; a steering group with OEMs, dealers, insurers, payment providers, and PA vendors; a security response process for vulnerabilities; and a commitment that the core protocol remains royalty-free. The specification in this paper is a draft intended to start that process, not a finished standard.
