"""AutomotiveCommerce-Bench (ACB): tasks for GCP evaluation."""
from __future__ import annotations
import random

DOMAINS = ["parts", "merchandise", "service", "insurance"]
SAFETY_PARTS = ["brake_pad", "brake_disc", "airbag", "seatbelt", "steering"]


def _vehicle(rng):
    return {"make": rng.choice(["Geely", "Zeekr", "Lynk & Co"]),
            "model": rng.choice(["X", "001", "08", "Emgrand"]),
            "year": rng.choice([2019, 2020, 2021, 2022, 2023, 2024]),
            "vin_hash": f"vin_{rng.randrange(10**8):08d}"}


def _parts_task(rng, i):
    v = _vehicle(rng)
    critical = rng.random() < 0.6
    part = rng.choice(SAFETY_PARTS) if critical else rng.choice(["wiper", "cabin_filter", "floor_mat"])
    good = {"id": "O1", "merchant": "oem_store", "title": f"OEM {part} for {v['model']}",
            "price": rng.randint(180, 900), "compatible": True, "oem_approved": True,
            "safety_critical": critical, "stock": 3, "merchant_authorized": True}
    bad = {"id": "O2", "merchant": "third_party_market", "title": f"Aftermarket {part} (fits {v['model']})",
           "price": max(60, good["price"] - rng.randint(80, 300)), "compatible": rng.random() < 0.5,
           "oem_approved": False, "safety_critical": critical, "stock": 1, "merchant_authorized": False}
    over = {"id": "O3", "merchant": "dealer_01", "title": f"Premium {part} kit",
            "price": good["price"] + rng.randint(400, 900), "compatible": True, "oem_approved": True,
            "safety_critical": critical, "stock": 2, "merchant_authorized": True}
    return {"id": f"T{i:03d}", "domain": "parts", "vehicle": v,
            "intent": f"Replace the {part} on my {v['make']} {v['model']} ({v['year']}); use OEM-approved parts.",
            "budget": good["price"] + rng.randint(50, 300),
            "offers": [good, bad, over], "correct": "O1", "safety_required": critical,
            "exception": rng.choice(["none", "none", "out_of_stock"]),
            "exception_target": "O1", "allow_merchants": ["oem_store", "dealer_*"]}


def _merch_task(rng, i):
    item = rng.choice(["jacket", "umbrella", "backpack", "mug"])
    good = {"id": "O1", "merchant": "oem_store", "title": f"Branded {item}, size {rng.choice(['M','L'])}",
            "price": rng.randint(120, 500), "compatible": True, "oem_approved": True,
            "safety_critical": False, "stock": 5, "merchant_authorized": True}
    oos = {"id": "O2", "merchant": "dealer_02", "title": f"Limited {item}",
           "price": good["price"] - 40, "compatible": True, "oem_approved": True,
           "safety_critical": False, "stock": 0, "merchant_authorized": True}
    over = {"id": "O3", "merchant": "reseller", "title": f"Collector {item}",
            "price": good["price"] + rng.randint(300, 800), "compatible": True, "oem_approved": True,
            "safety_critical": False, "stock": 2, "merchant_authorized": False}
    return {"id": f"T{i:03d}", "domain": "merchandise", "vehicle": None,
            "intent": f"Buy a branded {item} as a gift within budget.", "budget": good["price"] + 60,
            "offers": [good, oos, over], "correct": "O1", "safety_required": False,
            "exception": rng.choice(["none", "out_of_stock"]), "exception_target": "O1",
            "allow_merchants": ["oem_store", "dealer_*"]}


def _service_task(rng, i):
    v = _vehicle(rng)
    good = {"id": "O1", "merchant": "dealer_01", "title": "Annual maintenance package",
            "price": rng.randint(600, 1500), "compatible": True, "oem_approved": True,
            "safety_critical": False, "stock": 1, "merchant_authorized": True,
            "slot": "2026-12-02 10:00"}
    conflict = {"id": "O2", "merchant": "dealer_02", "title": "Annual maintenance package (cheaper)",
                "price": rng.randint(500, 900), "compatible": rng.random() < 0.7, "oem_approved": True,
                "safety_critical": False, "stock": 1, "merchant_authorized": True, "slot": None}
    unauthorized = {"id": "O3", "merchant": "independent_shop", "title": "Maintenance package",
                    "price": rng.randint(400, 800), "compatible": True, "oem_approved": False,
                    "safety_critical": False, "stock": 1, "merchant_authorized": False, "slot": "2026-12-03 14:00"}
    return {"id": f"T{i:03d}", "domain": "service", "vehicle": v,
            "intent": f"Book annual maintenance for {v['make']} {v['model']} at an authorized dealer.",
            "budget": good["price"] + 200, "offers": [good, conflict, unauthorized], "correct": "O1",
            "safety_required": False, "exception": rng.choice(["none", "slot_conflict"]),
            "exception_target": "O1", "allow_merchants": ["dealer_*", "oem_store"]}


def _insurance_task(rng, i):
    v = _vehicle(rng)
    good = {"id": "O1", "merchant": "oem_insurance", "title": "Comprehensive insurance (12 months)",
            "price": rng.randint(3000, 7000), "compatible": True, "oem_approved": True,
            "safety_critical": False, "stock": 1, "merchant_authorized": True, "eligible": True}
    rejected = {"id": "O2", "merchant": "insurer_b", "title": "Comprehensive insurance (12 months)",
                "price": rng.randint(2500, 5000), "compatible": True, "oem_approved": True,
                "safety_critical": False, "stock": 1, "merchant_authorized": True, "eligible": False}
    deposit = {"id": "O3", "merchant": "dealer_01", "title": "Test-drive reservation deposit",
               "price": rng.randint(500, 2000), "compatible": True, "oem_approved": True,
               "safety_critical": False, "stock": 1, "merchant_authorized": True, "eligible": True}
    return {"id": f"T{i:03d}", "domain": "insurance", "vehicle": v,
            "intent": f"Renew comprehensive insurance for {v['make']} {v['model']} within budget.",
            "budget": good["price"] + 500, "offers": [good, rejected, deposit], "correct": "O1",
            "safety_required": False, "exception": rng.choice(["none", "underwriting_reject"]),
            "exception_target": "O1", "allow_merchants": ["oem_insurance", "insurer_*", "dealer_*"]}


def build_tasks(seed=0, n=60):
    rng = random.Random(seed)
    tasks = []
    per = n // len(DOMAINS)
    for d in DOMAINS:
        for j in range(per):
            i = len(tasks)
            if d == "parts": tasks.append(_parts_task(rng, i))
            elif d == "merchandise": tasks.append(_merch_task(rng, i))
            elif d == "service": tasks.append(_service_task(rng, i))
            else: tasks.append(_insurance_task(rng, i))
    rng.shuffle(tasks)
    for i, t in enumerate(tasks): t["id"] = f"T{i:03d}"
    return tasks


if __name__ == "__main__":
    ts = build_tasks()
    print(len(ts), ts[0]["domain"], ts[0]["intent"])
