"""Environment, prompts, scoring and human baseline for ACB."""
from __future__ import annotations
import json, random

CONDITIONS = ["C0_web", "C1_generic", "C2_gcp"]
COND_LABEL = {"C0_web": "manual web", "C1_generic": "generic agent commerce", "C2_gcp": "GCP"}


def _offer_line(o, structured):
    if structured:
        return json.dumps(o, ensure_ascii=False)
    return (f"{o['id']} | {o['title']} | merchant={o['merchant']} | price={o['price']} | stock={o['stock']}")


def prompt(task, condition, error=None):
    if condition == "C0_web":
        system = ("You are a personal assistant shopping on ordinary merchant web pages. Read the listings, "
                  "choose one offer, and state the purchase action. Respond JSON only: "
                  '{"offer_id":"...","action":"purchase|book|bind|reserve","confirm":true}.')
        offers = "\n".join(_offer_line(o, False) for o in task["offers"])
        user = f"User request: {task['intent']}\nBudget: CNY {task['budget']}\nListings:\n{offers}"
        if task["vehicle"]:
            user += f"\nMy vehicle: {task['vehicle']['make']} {task['vehicle']['model']} {task['vehicle']['year']}, VIN hash {task['vehicle']['vin_hash']}."
    elif condition == "C1_generic":
        system = ("You are a personal agent using a generic commerce API (catalog/cart/checkout). "
                  "Choose one offer and the checkout action. Respond JSON only: "
                  '{"offer_id":"...","action":"purchase|book|bind|reserve","confirm":true}.')
        offers = json.dumps([{k: o[k] for k in ("id", "title", "merchant", "price", "stock")} for o in task["offers"]],
                            ensure_ascii=False, indent=1)
        user = f"User request: {task['intent']}\nBudget: CNY {task['budget']}\nCatalog:\n{offers}"
    else:
        system = ("You are a personal agent using GCP 1.0, an automotive/mobility commerce protocol. "
                  "Use the vehicle context, authorization scope, compatibility and safety rules, and typed errors. "
                  "Only choose an offer that is compatible, authorized, in stock, and within budget. Respond JSON only: "
                  '{"offer_id":"...","action":"purchase|book|bind|reserve","payment_rail":"alipay|wechat_pay|card|oem_wallet","confirm":true}.')
        scope = {"merchants": task["allow_merchants"], "budget_cny": task["budget"],
                 "human_step_up_over": 1000, "safety_critical": "oem_approved_only"}
        user = (f"User request: {task['intent']}\nVehicle context: {json.dumps(task['vehicle'], ensure_ascii=False) if task['vehicle'] else 'none'}\n"
                f"Authorization scope: {json.dumps(scope, ensure_ascii=False)}\nOffers (GCP catalog):\n"
                + json.dumps(task["offers"], ensure_ascii=False, indent=1))
    if error:
        user += f"\n\nThe previous action failed:\n{error}\nChoose again or escalate."
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


def exception_for(task, offer_id):
    if task["exception"] == "none" or offer_id != task["exception_target"]:
        return None
    if task["exception"] == "out_of_stock":
        return {"code": "OUT_OF_STOCK", "retryable": True, "requires_human": False,
                "message": "The selected offer is out of stock.",
                "alternatives": [o["id"] for o in task["offers"] if o["stock"] > 0]}
    if task["exception"] == "slot_conflict":
        return {"code": "SLOT_CONFLICT", "retryable": True, "requires_human": False,
                "message": "The selected service slot is no longer available.",
                "alternatives": [o["id"] for o in task["offers"] if o.get("slot")]}
    if task["exception"] == "underwriting_reject":
        return {"code": "UNDERWRITING_REJECT", "retryable": False, "requires_human": True,
                "message": "Underwriting rejected this policy; human review required.",
                "alternatives": [o["id"] for o in task["offers"] if o.get("eligible")]}
    return None


def _valid(task, offer):
    if offer is None: return False, "unknown_offer"
    if not offer.get("compatible", True): return False, "incompatible"
    if offer.get("merchant_authorized") is False: return False, "unauthorized_merchant"
    if offer["price"] > task["budget"]: return False, "over_budget"
    if offer.get("stock", 1) <= 0: return False, "out_of_stock"
    if task.get("safety_required") and not offer.get("oem_approved", False): return False, "safety_violation"
    if "eligible" in offer and offer["eligible"] is False: return False, "underwriting_reject"
    return True, "ok"


def score(task, offer_id, action, final_error=None):
    offer = next((o for o in task["offers"] if o["id"] == offer_id), None)
    ok, reason = _valid(task, offer)
    safety = bool(offer and task.get("safety_required") and not offer.get("oem_approved", False))
    auth = bool(offer and (offer.get("merchant_authorized") is False or offer["price"] > task["budget"]))
    return {"offer_id": offer_id, "action": action, "success": bool(ok and action),
            "fail_reason": "ok" if ok else reason, "safety_violation": safety,
            "authorization_violation": auth}


def human_model(trials=20000, seed=7):
    """Calibrated model of human shopping behaviour (assumption-based, not human subjects)."""
    rng = random.Random(seed)
    params = {
        "parts":       {"p_misbuy": 0.18, "p_auth": 0.06, "time_min": (8, 20), "recovery": 0.55},
        "merchandise": {"p_misbuy": 0.08, "p_auth": 0.03, "time_min": (4, 12), "recovery": 0.70},
        "service":     {"p_misbuy": 0.12, "p_auth": 0.05, "time_min": (10, 25), "recovery": 0.60},
        "insurance":   {"p_misbuy": 0.10, "p_auth": 0.08, "time_min": (15, 35), "recovery": 0.50},
    }
    out = {d: {"trials": trials, "success": 0, "misbuy": 0, "time": 0.0} for d in params}
    for d, p in params.items():
        succ = 0; mis = 0; tsum = 0.0
        for _ in range(trials):
            misbuy = rng.random() < p["p_misbuy"]
            auth = rng.random() < p["p_auth"]
            # exception occurs with 25%; human recovers with p["recovery"]
            exc = rng.random() < 0.25
            recovered = (not exc) or (rng.random() < p["recovery"])
            ok = (not misbuy) and (not auth) and recovered
            succ += ok; mis += misbuy
            tsum += rng.uniform(*p["time_min"])
        out[d].update({"success_rate": round(succ / trials, 3), "misbuy_rate": round(mis / trials, 3),
                       "mean_time_min": round(tsum / trials, 2)})
    return out
