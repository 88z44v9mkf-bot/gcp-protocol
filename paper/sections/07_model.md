## 7. Human and Agent Commerce: A Quantitative Model

### 7.1 Why the comparison is not obvious

It is tempting to say that agents are faster and humans are more trustworthy. Both claims are incomplete. An agent is faster at search and execution but can make errors at machine speed; a human is slower but can notice that a brake pad does not fit. The right comparison is not speed versus trust; it is the <i>information</i> available at decision time and the <i>cost of errors</i> when the decision is wrong.

We model a commerce task by a set of constraints $K$ (vehicle compatibility, budget, merchant authorization, stock, safety eligibility, service capacity). A decision is successful if the chosen offer satisfies all constraints and the fulfillment succeeds. Let $p$ be the probability that the decision violates at least one constraint, $E$ the expected direct loss from a wrong purchase (return, repair, reschedule), $R$ the expected relationship loss (trust, support cost), $t$ the time spent, and $c_t$ the user's time cost. The expected cost is
<div class="eq"><i>C</i> = <i>P</i> + <i>p</i>(<i>E</i> + <i>R</i>) + <i>t c</i><sub>t</sub> + <i>a c</i><sub>a</sub>, &nbsp;&nbsp;(2)</div>
where $a$ is the number of authorization interactions and $c_a$ their cost. A protocol improves the comparison only if it reduces $p$ or $a$ without increasing $P$ or $t$ more than the gain.

### 7.2 What GCP changes

GCP does not make the model smarter. It changes the information and the action space:
<ul>
<li><b>Information.</b> Compatibility, safety, stock, and authorization become machine-checkable fields instead of prose; hidden constraints become visible before checkout.</li>
<li><b>Action.</b> Checkout is gated by the delegation and safety engine; an invalid action is rejected with a typed error and alternatives.</li>
<li><b>Recovery.</b> Typed errors carry recovery paths; the agent does not need to guess why a purchase failed.</li>
</ul>

This yields three testable predictions:
<ol>
<li><b>P1 (constraint effect).</b> The error reduction from GCP is increasing in the number and heterogeneity of constraints. It should be largest for parts (compatibility and safety) and service (authorization and capacity), smaller for simple merchandise.</li>
<li><b>P2 (recovery effect).</b> Typed errors with alternatives improve recovery relative to plain error messages, especially for out-of-stock and slot-conflict failures.</li>
<li><b>P3 (authorization effect).</b> A bounded delegation with step-up thresholds reduces unauthorized transactions relative to an unbounded mandate, at a measurable friction cost in authorization interactions.</li>
</ol>

### 7.3 Human baseline

Human error and time are not measured in this paper with human subjects. We use a calibrated model with domain-specific parameters drawn from plausible ranges (parts: 18% misbuy, 6% authorization error, 8–20 min; merchandise: 8%, 3%, 4–12 min; service: 12%, 5%, 10–25 min; insurance: 10%, 8%, 15–35 min; exception recovery 50–70%). The model runs 20,000 Monte Carlo trials per domain and reports expected success, misbuy, and time. We label it explicitly as a model, not as human-subject data, and we report sensitivity in Appendix C. The comparison is therefore a <i>conditional</i> statement: given these human parameters, how does the agent compare?

### 7.4 Propositions

<b>Proposition 1 (information effect).</b> If GCP converts a fraction $\phi$ of hidden constraints into machine-checkable signals, the agent's constraint-violation probability falls from $p_0$ to $p_1\le p_0(1-\phi)$, and the reduction is increasing in the number of constraints that were previously hidden.

<b>Proposition 2 (recovery effect).</b> If a typed error includes a correct alternative with probability $\rho$, and the agent selects it with probability $\sigma>\sigma_0$ (where $\sigma_0$ is the probability under a plain error message), the expected success rate increases by $\rho(\sigma-\sigma_0)$ per exception.

<b>Proposition 3 (authorization threshold).</b> Under the friction-risk model of Section 4.3, the optimal step-up threshold is decreasing in item value, safety criticality, and dispute cost, and increasing in the quality of the agent's verification. A single global threshold is dominated by a value- and safety-dependent ladder.

The propositions are deliberately directional; Section 9 measures their empirical counterparts.


### 7.5 Interaction cost across horizons

The comparison in Sections 7.1–7.4 is about a single task. The near-term question (12–24 months) is about the <i>interaction cost per unit of commerce</i>: how many human touches, how much waiting, and how much oversight are needed as the agent takes on more work.

Let a task have $s$ interaction steps, of which $s_h$ require the human, and let $w$ be the waiting time per step. The interaction cost is
<div class="eq"><i>I</i> = <i>s</i><sub><i>h</i></sub> <i>c</i><sub><i>h</i></sub> + (<i>s</i> − <i>s</i><sub><i>h</i></sub>) <i>w</i> + <i>a c</i><sub><i>a</i></sub>, &nbsp;&nbsp;(3)</div>
where $c_h$ is the cost of a human step and $c_a$ the cost of an approval. Table 4 gives a scenario analysis for the four commerce families, combining the measured agent behavior in Section 9 with the calibrated human baseline and the horizon assumptions in Section 3.6 (0–6, 6–18, and 18–36 months). The numbers are scenario estimates, not forecasts; their purpose is to show which protocol properties dominate as authority moves from the human to the agent.

<div class="tblwrap"><table><caption>Table 4. Interaction cost per task by horizon (scenario estimates; human steps and minutes).</caption>
<thead><tr><th>Family</th><th>H1 human</th><th>H1 agent</th><th>H2 agent</th><th>H3 agent</th></tr></thead>
<tbody>
<tr><td>Parts purchase</td><td>8–12 steps, 14 min</td><td>1.5 steps, 1 approval, seconds</td><td>0.2 touches, auto-reorder</td><td>agent-to-agent, policy audit</td></tr>
<tr><td>Merchandise</td><td>5–8 steps, 8 min</td><td>1.5 steps, 1 approval, seconds</td><td>0.1 touches, budgeted</td><td>agent-to-agent, gifting</td></tr>
<tr><td>Service booking</td><td>10–15 steps, 18 min</td><td>1.5 steps, 1 approval</td><td>proactive reminder, 0.3 touches</td><td>fleet scheduling</td></tr>
<tr><td>Insurance / test drive</td><td>12–20 steps, 25 min</td><td>1.5 steps, step-up</td><td>renewal proposal, 0.5 touches</td><td>agent-to-agent underwriting</td></tr>
</tbody></table></div>

Three implications follow. First, the dominant cost shifts from <i>search and form-filling</i> (human) to <i>authorization and exception review</i> (agent). A protocol that does not reduce authorization friction will not deliver the H2 benefit. Second, the number of human touches falls faster than the number of agent steps; the binding constraint becomes trust and liability, not latency. Third, the protocol must remain useful when the human is absent for long periods: expiry, revocation, anomaly detection, and evidence export become more important than the checkout call itself.


The frequency of interaction amplifies the authorization problem. If a user buys a part twice a year, one approval per purchase is tolerable. If an agent reorders consumables monthly, books service twice a year, and renews insurance annually, the oversight load is the product of tasks and exception rate, not the cost of a single task. GCP's evidence ledger and typed exceptions are designed to make oversight <i>batchable</i>: the user reviews exceptions and anomalies, not every transaction, and the protocol records enough context to make that review fast.
