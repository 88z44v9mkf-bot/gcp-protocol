import json, subprocess, sys, time, urllib.request
proc = subprocess.Popen([sys.executable, "fitment/mock_fitment.py"]); time.sleep(0.6)
def post(path, body):
    req = urllib.request.Request("http://127.0.0.1:8098" + path, data=json.dumps(body).encode(), method="POST")
    req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as r: return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e: return e.code, json.loads(e.read())
try:
    s, v = post("/fitment/resolve", {"vin": "L6TDEMO000000001"})
    assert s == 200 and v["make"] == "OEM_A" and "vehicle_id" in v and "vin" not in v
    s, u = post("/fitment/resolve", {"vin": "UNKNOWN"})
    assert s == 404 and u["code"] == "UNKNOWN_VIN"
    s, c = post("/fitment/check", {"vin": "L6TDEMO000000001", "part_id": "P001"})
    assert c["compatible"] is True and c["confidence"] >= 0.95
    s, c = post("/fitment/check", {"vin": "LVVDEMO000000002", "part_id": "P001"})
    assert c["compatible"] is False and c["code"] == "VEHICLE_INCOMPATIBLE"
    s, c = post("/fitment/check", {"vin": "L6TDEMO000000001", "part_id": "P003"})
    assert c["compatible"] is True
    print("fitment tests passed: resolve, unknown VIN, compatible, incompatible, universal")
finally:
    proc.terminate()
