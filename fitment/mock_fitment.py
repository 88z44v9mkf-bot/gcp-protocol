"""Reference fitment service for GCP (demo data)."""
from __future__ import annotations
import hashlib, json
from http.server import BaseHTTPRequestHandler, HTTPServer

VINS = {
    "L6TDEMO000000001": {"make": "OEM_A", "model": "X", "year": 2022, "engine": "2.0T", "trim": "Premium", "market": "CN"},
    "LVVDEMO000000002": {"make": "OEM_B", "model": "Y", "year": 2021, "engine": "1.5T", "trim": "Sport", "market": "CN"},
    "LSGDEMO000000003": {"make": "OEM_C", "model": "Z", "year": 2023, "engine": "EV", "trim": "Long Range", "market": "CN"},
}
PARTS = {
    "P001": {"part_id": "P001", "title": "Front brake pad set", "applications": [{"make": "OEM_A", "model": "X", "year_from": 2022, "year_to": 2024, "engine": "2.0T"}], "safety_critical": True},
    "P002": {"part_id": "P002", "title": "Cabin filter", "applications": [{"make": "OEM_A", "model": "X", "year_from": 2019, "year_to": 2024}, {"make": "OEM_B", "model": "Y", "year_from": 2020, "year_to": 2022}], "safety_critical": False},
    "P003": {"part_id": "P003", "title": "All-weather floor mat", "applications": [{"make": "*", "model": "*", "year_from": 2010, "year_to": 2030}], "safety_critical": False},
}


def vid(vin):
    return "veh_" + hashlib.sha256(("gcp:" + vin).encode()).hexdigest()[:12]


def resolve(vin):
    v = VINS.get(vin)
    if not v: return None
    return {**v, "vehicle_id": vid(vin), "vin_hash": "sha256:" + hashlib.sha256(vin.encode()).hexdigest()[:16]}


def check(vin, part_id):
    v = resolve(vin); p = PARTS.get(part_id)
    if not v: return {"code": "UNKNOWN_VIN", "compatible": False, "requires_human": True}
    if not p: return {"code": "UNKNOWN_PART", "compatible": False, "requires_human": True}
    ok = False; conf = 0.0
    for a in p["applications"]:
        if (a["make"] in ("*", v["make"]) and a["model"] in ("*", v["model"])
                and a["year_from"] <= v["year"] <= a["year_to"]
                and (a.get("engine") in (None, v["engine"]))):
            ok = True; conf = 0.98 if a["make"] != "*" else 0.85
    if not ok:
        return {"code": "VEHICLE_INCOMPATIBLE", "compatible": False, "confidence": 0.0,
                "requires_human": bool(p["safety_critical"]), "part_id": part_id}
    if p["safety_critical"] and conf < 0.95:
        return {"code": "LOW_CONFIDENCE", "compatible": True, "confidence": conf, "requires_human": True, "part_id": part_id}
    return {"code": "OK", "compatible": True, "confidence": conf,
            "requires_human": False, "part_id": part_id, "source": "mock_aces"}


class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass
    def _send(self, c, o):
        b = json.dumps(o).encode(); self.send_response(c); self.send_header("Content-Type", "application/json"); self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0)); body = json.loads(self.rfile.read(n) or b"{}")
        if self.path == "/fitment/resolve":
            v = resolve(body.get("vin", ""))
            return self._send(200 if v else 404, v or {"code": "UNKNOWN_VIN"})
        if self.path == "/fitment/check":
            return self._send(200, check(body.get("vin", ""), body.get("part_id", "")))
        self._send(404, {"code": "NOT_FOUND"})
    def do_GET(self):
        if self.path.startswith("/fitment/parts"):
            return self._send(200, {"parts": [{"part_id": k, **{kk: vv for kk, vv in v.items() if kk != "applications"}} for k, v in PARTS.items()]})
        self._send(404, {"code": "NOT_FOUND"})


if __name__ == "__main__":
    HTTPServer(("127.0.0.1", 8098), H).serve_forever()
