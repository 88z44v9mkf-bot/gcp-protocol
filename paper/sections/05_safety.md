## 5. Safety, Compliance, and Exception Handling

### 5.1 Safety rules

GCP evaluates safety rules before checkout. The core rules are: safety-critical parts must be OEM-approved or certified (e.g., ECE-R90); an open recall blocks non-recall service purchases until acknowledged; insurance eligibility and consent rules are checked before binding; vehicle orders and deposits require identity, license, and cooling-off checks; and data minimization limits what a merchant receives. A block emits a signed evidence record and cannot be overridden by a prompt.

The protocol does not replace ISO 26262, UN R155/R156, or local consumer-protection law; it encodes their commerce-facing consequences as machine-checkable fields and requires the evidence to be retained.

### 5.2 Exception taxonomy and recovery

Real commerce fails in predictable ways. GCP defines a typed error with `retryable`, `requires_human`, `alternatives`, and `evidence_id` (Table 3). The client follows the declared recovery path rather than retrying blindly; a non-retryable error escalates to the human.

<div class="tblwrap"><table><caption>Table 3. Selected GCP error codes and default recovery.</caption>
<thead><tr><th>Code</th><th>Meaning</th><th>Recovery</th></tr></thead>
<tbody>
<tr><td>VEHICLE_INCOMPATIBLE</td><td>part/service not valid for VIN</td><td>suggest compatible alternatives</td></tr>
<tr><td>SAFETY_BLOCK</td><td>safety rule violated</td><td>escalate; no auto-override</td></tr>
<tr><td>OUT_OF_STOCK</td><td>inventory gone</td><td>substitute/backorder/nearest dealer</td></tr>
<tr><td>PRICE_CHANGED</td><td>quote expired</td><td>re-quote; consent if above threshold</td></tr>
<tr><td>PAYMENT_DECLINED</td><td>PSP decline</td><td>alternate rail, retry policy, step-up</td></tr>
<tr><td>SCA_REQUIRED</td><td>strong customer auth</td><td>biometric/PIN challenge</td></tr>
<tr><td>SLOT_CONFLICT</td><td>service bay unavailable</td><td>nearest slots, loaner, reschedule</td></tr>
<tr><td>UNDERWRITING_REJECT</td><td>insurance ineligible</td><td>explain, alternatives, human review</td></tr>
<tr><td>RECALL_BLOCK</td><td>open recall</td><td>book recall service first</td></tr>
<tr><td>DUPLICATE_ORDER</td><td>idempotency conflict</td><td>return original order</td></tr>
<tr><td>CONSENT_EXPIRED</td><td>delegation expired/revoked</td><td>re-authorize</td></tr>
</tbody></table></div>

### 5.3 Security and privacy

GCP uses mTLS and signed requests with replay protection, short-lived tokens, per-merchant keys, and revocation lists. Personal data is minimized: VINs are hashed, merchants receive only scoped fields, and evidence is exportable. Untrusted catalog text is treated as data, never as instructions; tool outputs are schema-validated; allowlists and step-up limits bound the blast radius of a compromised agent.

### 5.4 Safety in the cockpit

In-vehicle agents have an additional constraint: driver distraction. GCP blocks L3+ purchases while the vehicle is moving and requires parked status or voice-plus-biometric confirmation. Low-risk L1 actions (adding to cart, holding a slot) may be allowed with a short spoken confirmation. This is a protocol-level rule, not a UI preference.
