## 9. Experiments

### 9.1 Setup

We ran ACB on the full 60-task set with three models and three conditions, giving 540 trajectories (539 analyzed; one run failed). Temperature was 0; the same prompt template was used within a condition. An exception triggered one recovery turn. All raw records are released.

### 9.2 Main results

<div class="tblwrap"><table><caption>Table 6. ACB results by condition and model (percent unless noted; n=59–60 per cell).</caption><thead><tr><th>Condition</th><th>Model</th><th>Success</th><th>Misbuy</th><th>Recovery</th><th>Steps</th><th>Latency (s)</th></tr></thead><tbody><tr><td>Manual web</td><td>deepseek-v4.1-flash-1017</td><td>65</td><td>35</td><td>59</td><td>1.27</td><td>2.2</td></tr><tr><td>Manual web</td><td>kimi-k3.1-pro</td><td>62</td><td>38</td><td>56</td><td>1.28</td><td>9.0</td></tr><tr><td>Manual web</td><td>qwen3.8-flash</td><td>67</td><td>33</td><td>59</td><td>1.32</td><td>7.8</td></tr><tr><td>Generic agent</td><td>deepseek-v4.1-flash-1017</td><td>63</td><td>37</td><td>59</td><td>1.28</td><td>2.1</td></tr><tr><td>Generic agent</td><td>kimi-k3.1-pro</td><td>70</td><td>30</td><td>59</td><td>1.38</td><td>17.1</td></tr><tr><td>Generic agent</td><td>qwen3.8-flash</td><td>75</td><td>25</td><td>59</td><td>1.43</td><td>10.6</td></tr><tr><td>GCP</td><td>deepseek-v4.1-flash-1017</td><td>83</td><td>17</td><td>78</td><td>1.48</td><td>6.2</td></tr><tr><td>GCP</td><td>kimi-k3.1-pro</td><td>93</td><td>7</td><td>91</td><td>1.50</td><td>23.1</td></tr><tr><td>GCP</td><td>qwen3.8-flash</td><td>100</td><td>0</td><td>100</td><td>1.53</td><td>25.8</td></tr></tbody></table></div>

[[FIG:figures/fig_results.svg|Figure 2. Success and misbuy by condition, averaged over the three models. GCP moves success above 90% and misbuy below 10%; structure without automotive semantics (C1) is close to the manual baseline (C0).]]

GCP raises aggregate success from 64.5% (manual web) and 69.4% (generic agent commerce) to 92.2%, and cuts misbuy from 35.5% and 30.6% to 7.8%. The gain is consistent across models: C2 success is 83% for DeepSeek, 93% for Kimi, and 100% for Qwen-Flash. The protocol adds steps (1.29 → 1.50) and latency, but the additional interaction is a validation step, not a human confirmation. C0 and C1 are almost indistinguishable: structure without automotive semantics does not prevent the error.

### 9.3 Domain heterogeneity

<div class="tblwrap"><table><caption>Table 7. Success by domain and condition (percent; n=45 per cell).</caption><thead><tr><th>Condition</th><th>Domain</th><th>Success</th></tr></thead><tbody><tr><td>Manual web</td><td>parts</td><td>100</td></tr><tr><td>Manual web</td><td>merchandise</td><td>100</td></tr><tr><td>Manual web</td><td>service</td><td>44</td></tr><tr><td>Manual web</td><td>insurance</td><td>13</td></tr><tr><td>Generic agent</td><td>parts</td><td>100</td></tr><tr><td>Generic agent</td><td>merchandise</td><td>100</td></tr><tr><td>Generic agent</td><td>service</td><td>53</td></tr><tr><td>Generic agent</td><td>insurance</td><td>24</td></tr><tr><td>GCP</td><td>parts</td><td>100</td></tr><tr><td>GCP</td><td>merchandise</td><td>100</td></tr><tr><td>GCP</td><td>service</td><td>86</td></tr><tr><td>GCP</td><td>insurance</td><td>82</td></tr></tbody></table></div>

The aggregate hides where the protocol matters. Parts and merchandise are already at 100% in all conditions: the traps (aftermarket part, reseller) are salient enough that the models avoid them without GCP fields. Service and insurance are different. Service success rises from 44% (C0) and 53% (C1) to 86% (C2); insurance rises from 13% and 24% to 82%. These are the domains where authorization, capacity, and underwriting constraints are hidden in ordinary pages and cannot be inferred from price or title. This is the empirical form of P1: the value of the protocol is concentrated in constraint-rich domains.

### 9.4 Exceptions and recovery

Exception recovery shows the value of typed errors. Across all exception tasks, recovery is 58.3% in C0 and 59.4% in C1, but 89.6% in C2 (78% DeepSeek, 91% Kimi, 100% Qwen-Flash). The difference is not model capability; it is the error surface. A plain error message tells the agent that something failed. A GCP error tells it the code, whether it is retryable, whether a human is required, and which alternatives remain. This supports P2.

### 9.5 Human comparison

The calibrated human model gives the following expected outcomes (model, not human subjects):

<div class="tblwrap"><table><caption>Table 8. Calibrated human baseline (model, not human subjects; 20,000 trials per domain).</caption><thead><tr><th>Domain</th><th>Success</th><th>Misbuy</th><th>Time (min)</th></tr></thead><tbody><tr><td>parts</td><td>68.5</td><td>18.1</td><td>14.0</td></tr><tr><td>merchandise</td><td>82.7</td><td>8.0</td><td>8.0</td></tr><tr><td>service</td><td>75.1</td><td>12.2</td><td>17.5</td></tr><tr><td>insurance</td><td>71.8</td><td>10.3</td><td>25.0</td></tr></tbody></table></div>

The calibrated human model gives expected success of 68.5% (parts), 82.7% (merchandise), 75.1% (service), and 71.8% (insurance), with 8–25 minutes per task. C2 agents reach 92.2% aggregate success in 1.5 steps and seconds of latency. The comparison is conditional on the model parameters (Appendix C), but the direction is robust: the protocol closes most of the human error gap in constraint-rich domains, while the human retains an advantage in tasks whose constraints are not encoded.

### 9.6 Interpretation

Three conclusions follow. First, structure alone (C1) is not enough; the automotive semantics—vehicle context, safety, authorization, typed recovery—are what change outcomes. Second, the protocols benefit is domain-specific: it is large where constraints are hidden and small where they are salient. Third, the cost is additional protocol steps and latency, which is the right trade when the expected error cost is high; for low-value merchandise, a lighter profile may be preferable. P3 (authorization friction) is not directly tested here because the benchmark did not vary the authorization ladder; we leave that to a follow-up with the real-money sandbox.


### 9.7 Authorization friction with a test-mode payment sandbox

To measure the friction side of the authorization ladder, we connected GCP to a Stripe test-mode payment sandbox. We selected 30 purchase tasks (parts and merchandise), ran two models, and compared three authorization modes: per-transaction approval (every payment asks the human), bounded delegation (auto-approve under USD 500, step-up above), and unbounded delegation (auto-approve everything). Each successful decision created a real PaymentIntent in Stripe test mode; no live money moved. This produced 180 test charges.

<div class="tblwrap"><table><caption>Table 9. Authorization friction in a Stripe test-mode sandbox (180 charges; n=60 per mode).</caption>
<thead><tr><th>Mode</th><th>Success</th><th>Auth. steps/task</th><th>Auth. violations</th><th>Charges</th></tr></thead>
<tbody>
<tr><td>Per-transaction approval</td><td>100%</td><td>1.00</td><td>0</td><td>60</td></tr>
<tr><td>Bounded delegation</td><td>100%</td><td>0.30</td><td>0</td><td>60</td></tr>
<tr><td>Unbounded delegation</td><td>100%</td><td>0.00</td><td>0</td><td>60</td></tr>
</tbody></table></div>

Bounded delegation cuts human approvals by 70% relative to per-transaction approval, with no loss of success. All 180 PaymentIntents were reconciled against the Stripe API (180/180 matched; USD 71,808 of test money). Unbounded delegation also had zero violations on this task set, which is a caution rather than a vindication: the benchmark does not contain adversarial prompts or ambiguous mandates, so the risk of an unbounded mandate is not exercised here. The result should be read as evidence that bounded delegation removes most of the friction without changing outcomes on well-specified tasks, not as evidence that unbounded delegation is safe.

### 9.8 Semi-field check on real catalogs

The benchmark uses synthetic offers. To check that the protocol does not depend on synthetic prices, we built 30 additional tasks from real public coffee-merchant catalogs (four merchants, real product titles, real prices, real bag weights), with a tight budget and a correct feasible offer. Two models ran under C1 (generic) and C2 (GCP), giving 120 trajectories.

<div class="tblwrap"><table><caption>Table 10. Semi-field check on real merchandise catalogs (30 tasks; n=30 per cell).</caption>
<thead><tr><th>Condition</th><th>Model</th><th>Success</th></tr></thead>
<tbody>
<tr><td>C1 generic</td><td>DeepSeek</td><td>100%</td></tr>
<tr><td>C1 generic</td><td>Kimi</td><td>100%</td></tr>
<tr><td>C2 GCP</td><td>DeepSeek</td><td>100%</td></tr>
<tr><td>C2 GCP</td><td>Kimi</td><td>100%</td></tr>
</tbody></table></div>

Both conditions succeed on this task set: with real prices and an explicit budget, the models choose a feasible offer. The semi-field check is therefore a non-degradation result, not a discriminating experiment; the tasks lack the hidden compatibility and safety constraints that drive the main benchmark. It confirms that GCP does not add failure modes on real catalog data, and it motivates a larger multi-OEM, multi-category field study.
