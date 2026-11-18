## 8. AutomotiveCommerce-Bench

### 8.1 Tasks

ACB contains 60 tasks across four domains: parts (15), merchandise (15), after-sales service (15), and insurance/vehicle reservation (15). Each task specifies a user intent, a budget, a vehicle context where relevant, and three offers. The offers are constructed so that one is valid, one is a near-miss (cheaper but incompatible, unauthorized, out of stock, or safety-critical without OEM approval), and one is over budget or from an unauthorized merchant. Some tasks include an exception: out-of-stock, service-slot conflict, or underwriting rejection.

Table 3 shows the structure. The traps are hidden in C0/C1 and visible in C2 because GCP exposes compatibility, safety, authorization, and inventory fields.

<div class="tblwrap"><table><caption>Table 3. ACB domains and hidden traps.</caption>
<thead><tr><th>Domain</th><th>Example intent</th><th>Hidden traps</th></tr></thead>
<tbody>
<tr><td>Parts</td><td>replace brake pads for a 2021 model</td><td>VIN/year mismatch, non-OEM safety part, unauthorized marketplace</td></tr>
<tr><td>Merchandise</td><td>buy a branded jacket within budget</td><td>out of stock, reseller above budget</td></tr>
<tr><td>Service</td><td>book annual maintenance at an authorized dealer</td><td>unauthorized independent shop, slot conflict</td></tr>
<tr><td>Insurance/reservation</td><td>renew comprehensive insurance</td><td>underwriting rejection, deposit product confusion</td></tr>
</tbody></table></div>

### 8.2 Conditions

We compare three conditions on the same task stream:
<ul>
<li><b>C0 (manual web).</b> The agent reads unstructured listings, with no compatibility, safety, authorization, or typed-error fields. This approximates an assistant using ordinary web pages.</li>
<li><b>C1 (generic agent commerce).</b> The agent uses structured catalog/cart/checkout objects (UCP/ACP-like), but without vehicle context, safety rules, or the GCP authorization ladder.</li>
<li><b>C2 (GCP).</b> The agent uses the GCP manifest, vehicle context, delegation scope, safety fields, typed errors, and alternatives.</li>
</ul>

All conditions use the same model, temperature 0, and the same scoring. The only difference is the protocol surface.

### 8.3 Scoring and metrics

A decision is successful if the final offer satisfies compatibility, authorization, budget, stock, safety eligibility, and underwriting eligibility, and the action matches the domain. We record success, misbuy (any constraint violation), safety violation (safety-critical part without OEM approval), authorization violation (unauthorized merchant or over budget), steps, latency, and recovery after an exception.

### 8.4 Models and protocol

We run three production models through an OpenAI-compatible endpoint: deepseek-v4.1-flash-1017, kimi-k3.1-pro, and qwen3.8-flash. Each task–condition–model cell is one trajectory; an exception triggers one recovery turn. This gives 60 × 3 × 3 = 540 trajectories. The full prompts, tasks, and scorer are released.
