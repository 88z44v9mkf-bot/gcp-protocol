"""Reference mock merchant implementing the GCP 1.0 conformance surface."""
from __future__ import annotations
import hashlib, json, time, uuid
from http.server import BaseHTTPRequestHandler, HTTPServer

TOKENS = {
    "token_full": {"scopes": ["catalog.read", "cart.write", "quote", "checkout.execute", "payment.intent", "service.book", "aftercare.claim"], "expires": time.time() + 3600},
    "token_read": {"scopes": ["catalog.read"], "expires": time.time() + 3600},
    "token_expired": {"scopes": ["catalog.read", "checkout.execute"], "expires": time.time() - 10},
}
OFFERS = {
    "O1": {"offer_id": "O1", "title": "OEM brake pad set", "price": 680, "compatible": True, "oem_approved": True, "safety_critical": True, "stock": 4},
    "O2": {"offer_id": "O2", "title": "Aftermarket brake pad", "price": 420, "compatible": False, "oem_approved": False, "safety_critical": True, "stock": 2},
    "O3": {"offer_id": "O3", "title": "Non-OEM safety part", "price": 390, "compatible": True, "oem_approved": False, "safety_critical": True, "stock": 1},
    "O4": {"offer_id": "O4", "title": "OEM filter", "price": 120, "compatible": True, "oem_approved": True, "safety_critical": False, "stock": 0},
}
STATE = {"carts": {}, "orders": {}, "idem": {}, "evidence": {}, "bookings": {}}


def err(code, message, retryable=False, human=False, alternatives=None):
    return {"code": code, "retryable": retryable, "requires_human": human, "message": message,
            "alternatives": alternatives or [], "evidence_id": "ev_" + hashlib.sha256((code + message).encode()).hexdigest()[:12]}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a): pass

    def _send(self, code, obj, headers=None):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("X-GCP-Version", "1.0")
        for k, v in (headers or {}).items(): self.send_header(k, v)
        self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)

    def _auth(self):
        h = self.headers.get("Authorization", "")
        token = h.replace("Bearer ", "")
        info = TOKENS.get(token)
        if not info: return None, err("CONSENT_EXPIRED", "unknown or missing credential", True, True)
        if info["expires"] < time.time(): return None, err("CONSENT_EXPIRED", "credential expired", True, True)
        return token, None

    def _body(self):
        n = int(self.headers.get("Content-Length", 0)); raw = self.rfile.read(n).decode() if n else "{}"
        try: return json.loads(raw)
        except Exception: return {}

    def do_GET(self):
        if self.path == "/.well-known/gcp":
            return self._send(200, {
                "gcp_version": "1.0", "merchant": {"id": "dealer_001", "country": "CN"},
                "capabilities": ["catalog.read", "cart.write", "quote", "checkout.execute", "payment.intent", "service.book", "aftercare.claim"],
                "catalogs": [{"id": "parts", "url": "/gcp/catalog", "vehicle_filter": True}],
                "payments": [{"rail": "alipay", "mode": "redirect"}, {"rail": "card", "mode": "token"}],
                "profiles": {"poppy": "/poppy", "ucp": "/ucp", "acp": "/acp"},
                "safety": {"recall_feed": "/gcp/recalls", "certified_parts_only": True}})
        if self.path.startswith("/gcp/catalog"):
            return self._send(200, {"offers": [OFFERS["O1"], OFFERS["O4"]], "vehicle_id": "veh_001"})
        if self.path.startswith("/gcp/evidence/"):
            eid = self.path.rsplit("/", 1)[-1]
            return self._send(200, STATE["evidence"].get(eid, {"evidence_id": eid, "hash": "sha256:demo", "chain": []}))
        self._send(404, err("CAPABILITY_UNSUPPORTED", "unknown endpoint"))

    def do_POST(self):
        token, e = self._auth()
        if e: return self._send(401, e)
        scopes = TOKENS[token]["scopes"]
        body = self._body()
        if self.path == "/gcp/cart":
            if "cart.write" not in scopes: return self._send(403, err("SCOPE_DENIED", "cart.write required"))
            cid = "cart_" + uuid.uuid4().hex[:8]
            STATE["carts"][cid] = {"offer_id": body.get("offer_id", "O1"), "ttl": time.time() + 600}
            return self._send(200, {"cart_id": cid, "ttl": 600})
        if self.path == "/gcp/checkout/quote":
            if "quote" not in scopes: return self._send(403, err("SCOPE_DENIED", "quote required"))
            cart = STATE["carts"].get(body.get("cart_id"), {"offer_id": "O1"})
            offer = OFFERS.get(cart["offer_id"], OFFERS["O1"])
            return self._send(200, {"cart_id": body.get("cart_id"), "offer_id": offer["offer_id"], "amount": offer["price"], "currency": "CNY"})
        if self.path == "/gcp/checkout/execute":
            if "checkout.execute" not in scopes: return self._send(403, err("SCOPE_DENIED", "checkout.execute required"))
            idem = self.headers.get("Idempotency-Key", "")
            if idem and idem in STATE["idem"]:
                return self._send(200, STATE["idem"][idem], {"Idempotent-Replayed": "true"})
            offer = OFFERS.get(body.get("offer_id"), OFFERS["O1"])
            if not offer["compatible"]: return self._send(422, err("VEHICLE_INCOMPATIBLE", "offer is not compatible with vehicle", True, False, ["O1"]))
            if offer["safety_critical"] and not offer["oem_approved"]: return self._send(403, err("SAFETY_BLOCK", "safety-critical part requires OEM approval", False, True))
            if offer["stock"] <= 0: return self._send(409, err("OUT_OF_STOCK", "offer out of stock", True, False, ["O1"]))
            order = {"order_id": "ord_" + uuid.uuid4().hex[:8], "offer_id": offer["offer_id"], "amount": offer["price"], "status": "confirmed"}
            if idem: STATE["idem"][idem] = order
            STATE["orders"][order["order_id"]] = order
            return self._send(201, order)
        if self.path == "/gcp/payment/intent":
            if "payment.intent" not in scopes: return self._send(403, err("SCOPE_DENIED", "payment.intent required"))
            return self._send(200, {"payment_intent_id": "pi_" + uuid.uuid4().hex[:8], "status": "requires_confirmation", "rail": body.get("rail", "alipay")})
        if self.path == "/gcp/book":
            if "service.book" not in scopes: return self._send(403, err("SCOPE_DENIED", "service.book required"))
            return self._send(409, err("SLOT_CONFLICT", "requested slot unavailable", True, False, ["2026-12-03 10:00", "2026-12-04 14:00"]))
        if self.path == "/gcp/aftercare":
            return self._send(200, {"claim_id": "claim_" + uuid.uuid4().hex[:8], "status": "open"})
        self._send(404, err("CAPABILITY_UNSUPPORTED", "unknown endpoint"))

    def do_PUT(self):
        self._send(405, err("CAPABILITY_UNSUPPORTED", "method not allowed"))


def serve(port=8099):
    return HTTPServer(("127.0.0.1", port), Handler)


if __name__ == "__main__":
    serve().serve_forever()
