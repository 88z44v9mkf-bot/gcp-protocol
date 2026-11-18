## 6. Compatibility with Poppy, UCP, and ACP

### 6.1 Profiles and negotiation

GCP is a superset with explicit profiles. The client sends `Accept-Profile: gcp=1.0, ucp=<version>, acp=<version>, poppy=<version>`; the merchant selects the highest mutually supported profile and returns `profile_used` and a `lossy` flag. Required capabilities that cannot be met fail closed; optional capabilities are dropped with an explicit loss report.

### 6.2 Poppy

Poppy supplies the principal identity, delegation, and session. GCP consumes the Poppy credential as `principal` and `delegate`, maps the Poppy session to `session_id`, and adds commerce scopes, budget constraints, and evidence requirements. Identity conversion is lossless; commerce constraints remain GCP fields.

### 6.3 UCP

UCP supplies generic discovery, catalog, cart, and checkout. GCP maps manifest→discovery, offer→product/variant, cart→cart, checkout→checkout, and payment intent→payment handler. Vehicle compatibility, safety, and authorization travel as extension namespaces (`gcp.vehicle`, `gcp.safety`, `gcp.auth`). If the UCP endpoint cannot carry them, GCP validates locally and marks the transaction `lossy=true`.

### 6.4 ACP

ACP supplies the agentic checkout and payment handshake. GCP maps `checkout.execute`→ACP checkout session and `payment.intent`→ACP payment token, while retaining the GCP authorization and safety gates. ACP may complete the PSP flow; GCP remains the authority for principal scope and safety.

### 6.5 Integration patterns

<b>Third-party PA products.</b> A PA vendor imports the GCP tool schema via MCP or A2A; the tools expose discover, catalog, cart, checkout, book, and aftercare. For assistants that already support Poppy/UCP/ACP, the GCP adapter translates and adds the automotive extensions.

<b>Ecosystem of PA products.</b> A third-party assistant such as Doubao, Tongyi Qianwen/Lingguang, DeepSeek, ChatGPT, Claude/Claude Code, WorkBuddy, QwenWork, or a Xiaohongshu-style shopping assistant can expose GCP tools through its existing MCP/A2A tool layer: the tools are discover, catalog, cart, checkout, book, and aftercare; the host app supplies the step-up UI and the Poppy/OAuth session. The same tool schema is used by an OEM's own mobile/PC assistant and by the cockpit, so a merchant integrates once and reaches every PA channel that supports the protocol. A PA that already speaks UCP or ACP keeps its checkout and calls the GCP adapter only for vehicle/safety/authorization fields; a PA that speaks only Poppy uses GCP for all commerce objects.

<b>OEM apps and cockpit.</b> The OEM mobile/PC app and the cockpit use the same client SDK and authorization vault; the cockpit adds the parked/step-up rules. Dealers and service centers connect through a DMS/ERP adapter; insurers through quote/bind adapters; payment providers through PSP adapters.

### 6.6 Loading GCP in practice

A merchant becomes GCP-capable in four steps: publish `/.well-known/gcp`; implement catalog and checkout endpoints; add a PSP adapter; run the conformance suite. An OEM deploys the authorization vault and vehicle-context service, registers merchants, and publishes safety rules. A PA vendor imports the tool schema, requests delegation scopes, and implements the step-up UI. A pilot starts at L1/L2 (parts and merchandise), then L3 (service and insurance), then L4 (vehicle order). The specification, conformance tests, and reference client are released with this paper.
