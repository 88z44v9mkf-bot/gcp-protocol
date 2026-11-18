## 1. Introduction

A personal agent used to answer questions; it is now expected to buy. The first generation of agent-commerce protocols is arriving: identity and session protocols let an assistant prove which user it represents (Poppy [@poppy2026]), universal commerce protocols define catalog, cart, and checkout (UCP [@ucp2026]), and agentic checkout protocols define how an agent completes a payment (ACP [@acp2026]). These protocols solve the general problem: an agent can find a merchant, select a product, and pay.

The automotive and mobility problem is not general. A user does not simply buy a product; the user buys <i>a part that must fit a specific vehicle</i>, <i>a service that must be performed by an authorized dealer</i>, <i>an insurance policy that must satisfy underwriting rules</i>, or <i>a vehicle reservation that carries a deposit and a cooling-off period</i>. The catalog is multi-sided (OEM, dealer, aftermarket, insurer), the constraints are safety-critical, the payment rails differ across regions, and the after-sales relationship continues for years. A generic shopping protocol that treats a brake pad as a SKU with a price will produce exactly the errors that make users distrust agents: the wrong part, the unauthorized repair, the insurance that cannot be bound, the deposit that cannot be refunded.

This paper asks a practical question: <b>what must a commerce protocol contain so that a personal agent can act for a human in automotive and mobility commerce, safely, accountably, and across the existing agent ecosystem?</b> We answer with GCP 1.0.

<b>Contributions.</b>
<ul>
<li><b>A protocol for constrained commerce.</b> GCP makes vehicle context, compatibility, safety eligibility, authorization scope, payment intent, fulfillment, and aftercare first-class objects. A safety gate is evaluated before checkout and cannot be overridden by a prompt.</li>
<li><b>An authorization ladder.</b> Users grant bounded, revocable delegation (scopes, budget, merchants, time, human step-up thresholds). We formalize the trade-off between friction and risk and show how the threshold should depend on item value, safety criticality, and dispute cost.</li>
<li><b>Payment and regional abstraction.</b> GCP separates payment <i>intent</i> from payment <i>rail</i>: card/PSP, wallet, Alipay, WeChat Pay, UnionPay, OEM finance, and agent-native tokens are adapters; the agent never holds the user's long-term credential.</li>
<li><b>Compatibility by translation.</b> GCP consumes Poppy credentials, maps catalog/cart/checkout to UCP and ACP, and carries GCP-specific fields as extension namespaces. Capability negotiation makes lossy conversions explicit.</li>
<li><b>Benchmark and evidence.</b> AutomotiveCommerce-Bench (ACB) covers 60 tasks with hidden compatibility, safety, authorization, and exception traps; a real-LLM study with three models compares manual web shopping, generic agent commerce, and GCP. We also quantify the human baseline with a calibrated model and release the protocol, implementation, and raw results.</li>
</ul>

The rest of the paper is organized as follows. Section 2 positions the work. Section 3 specifies GCP. Sections 4 and 5 detail authorization/payments and safety/compliance. Section 6 defines compatibility with Poppy, UCP, and ACP. Section 7 develops the human-versus-agent analysis. Section 8 describes the benchmark, Section 9 the experiments, Section 10 discusses implications and limitations, and Section 11 concludes.
