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

<b>Simulated commerce.</b> The benchmark uses synthetic offers and a simulator, not live merchant systems. The payment rails are specified but not exercised with real money in this paper; a real-money sandbox is the natural next step.

<b>Human baseline.</b> Human error and time are modeled, not measured with human subjects. The parameters are plausible but not universal; Appendix C reports sensitivity. A controlled human study is future work.

<b>Single OEM context.</b> The protocol is designed to be industry-wide, but the benchmark reflects one OEM's catalog structure. Cross-OEM and cross-border catalogs may require additional fields (homologation, tax, language).

<b>Model coverage.</b> Three models from one endpoint are tested; results may differ with other model families or agent scaffolds.

### 10.6 Adoption path

A practical rollout is staged: (1) L1/L2 for parts and merchandise in one OEM app and one dealer group; (2) L3 for service and insurance with step-up; (3) L4 for vehicle reservation and deposit; (4) third-party PA integration via MCP/A2A; (5) cross-OEM standardization through an open foundation. Each stage has measurable success, misbuy, authorization, and recovery metrics, so adoption can be evidence-driven rather than all-or-nothing.
