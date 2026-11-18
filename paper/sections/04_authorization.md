## 4. Authorization, Payments, and the Human in the Loop

### 4.1 The authorization ladder

GCP defines five levels of authority (Table 1). The levels are scopes, not prompts: a merchant must reject an action whose scope is absent, and the client must obtain a fresh consent receipt for step-up actions.

<div class="tblwrap"><table><caption>Table 1. GCP authorization ladder.</caption>
<thead><tr><th>Level</th><th>Scope</th><th>Typical action</th><th>Human involvement</th></tr></thead>
<tbody>
<tr><td>L0</td><td>catalog.read</td><td>browse parts, compare insurance</td><td>none</td></tr>
<tr><td>L1</td><td>cart.write, quote</td><td>add to cart, hold a service slot</td><td>notify</td></tr>
<tr><td>L2</td><td>checkout.execute ≤ limit</td><td>bounded purchase, service booking</td><td>biometric at first use</td></tr>
<tr><td>L3</td><td>high-value pay, bind</td><td>insurance bind, vehicle deposit</td><td>explicit step-up</td></tr>
<tr><td>L4</td><td>irreversible</td><td>contract signature, registration</td><td>human-only; agent prepares</td></tr>
</tbody></table></div>

### 4.2 Delegation constraints

A credential constrains budget per transaction and per period, merchant allow/deny lists, item categories, vehicle binding, time window, and step-up thresholds. Sub-delegation is allowed only when the parent scope includes `delegate` and the child constraints are strictly narrower. Revocation propagates to merchants within one heartbeat; execution-time checks reject a revoked credential even if the plan was created earlier.

### 4.3 Friction versus risk

Let a transaction have value $v$, safety criticality $c\in\{0,1\}$, and dispute cost $d$. A step-up challenge costs the user $f$ in time and attention; an unauthorized transaction costs $L(v,c,d)$ in expected loss. The optimal policy is to require step-up when
<div class="eq"><i>p</i><sub>unauth</sub>(<i>v</i>,<i>c</i>,<i>d</i>) · <i>L</i> &gt; <i>f</i>, &nbsp;&nbsp;(1)</div>
where $p_{unauth}$ is the probability that the agent acts outside the intended scope. The threshold is decreasing in $v$, $c$, and $d$ and increasing in the quality of the agent's plan verification. This yields the practical rule used in GCP: small, low-risk purchases are L2; safety-critical parts, insurance binding, and vehicle deposits are L3 with biometric step-up.

### 4.4 Payment abstraction

GCP separates payment intent from rail. Domestic rails include Alipay (page/JSAPI/mini-program), WeChat Pay (JSAPI/Native), UnionPay, OEM wallet, and finance/lease. International rails include cards and PSPs, Apple/Google Pay, SEPA, and local wallets. Agent-native rails include UCP payment tokens and ACP checkout tokens. High-value transactions may use escrow, deposit, split settlement, or invoice.

The payment intent carries amount, capture mode (`immediate`, `on_fulfillment`), split settlement, risk signals (user present, SCA method, device), refund policy, and evidence. The rail adapter returns a token, a status, and a settlement reference; the client never stores long-term credentials. Refunds and chargebacks are reconciled against the same intent id.

### 4.5 Regional differences

The protocol does not assume a single payment culture. In China, QR/JSAPI and mini-program flows dominate, and invoices (发票) are expected; in Europe, PSD2 strong customer authentication and SEPA are required; in the US, card and wallet rails dominate. GCP encodes these as rail capabilities in the manifest, not as protocol variants. The same intent can be executed by different rails without changing the commerce flow.
