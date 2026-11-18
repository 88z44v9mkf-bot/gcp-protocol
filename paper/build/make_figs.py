#!/usr/bin/env python3
"""Accurate, print-ready SVG figures for the GCP paper (no plotting libraries)."""
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "paper" / "figures"; FIG.mkdir(exist_ok=True)
FONT = "Times New Roman, Times, serif"; INK = "#222"; MUTED = "#555"


def box(x, y, w, h, lines, fs=11.5, bold=False, rx=6):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="#fff" stroke="{INK}" stroke-width="1.1"/>']
    n = len(lines)
    for i, line in enumerate(lines):
        yy = y + h / 2 + (i - (n - 1) / 2) * (fs + 4) + fs * .35
        wt = "bold" if bold and i == 0 else "normal"
        s.append(f'<text x="{x+w/2:.1f}" y="{yy:.1f}" text-anchor="middle" font-family="{FONT}" '
                 f'font-size="{fs}" font-weight="{wt}" fill="{INK}">{line}</text>')
    return "".join(s)


def arrow(x, y1, y2):
    return f'<path d="M{x},{y1} L{x},{y2}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#a)"/>'


def arch():
    W, H = 900, 590
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>']
    rows = [
        (20,  ["PA runtime: mobile app · PC · cockpit · third-party assistant (Doubao, Qwen, ChatGPT, Claude, ...)"], True),
        (100, ["GCP client: intent → authorization check → plan → execute → evidence"], True),
        (180, ["GCP core: discovery | catalog + vehicle context | cart/order | booking | payment intent | fulfillment | aftercare"], True),
        (260, ["Safety and compliance: compatibility · recall · insurance · cockpit rule · no prompt override"], False),
        (340, ["Evidence ledger: consent · checks · settlement · hash chain      Typed error bus: retryable · requires_human · alternatives"], False),
        (420, ["Adapters: Poppy | UCP | ACP | OEM DMS/ERP | payment providers"], False),
        (500, ["Merchants · dealers · service centers · insurers · payment rails"], False),
    ]
    for y, lines, bold in rows:
        p.append(box(50, y, 800, 55, lines, fs=10.5, bold=bold))
    for y in (75, 155, 235, 315, 395, 475):
        p.append(arrow(450, y, y + 25))
    p.append("</svg>")
    (FIG / "fig_gcp_arch.svg").write_text("".join(p), encoding="utf-8")


def results():
    s = json.loads((ROOT / "experiments/results/summary.json").read_text())
    conds = ["C0_web", "C1_generic", "C2_gcp"]; labels = ["Manual web", "Generic agent", "GCP"]
    cells = {(c["condition"], c["model"]): c for c in s["cells"]}
    models = sorted({c["model"] for c in s["cells"]})
    def agg(cond, key):
        vals = [cells[(cond, m)][key] for m in models if (cond, m) in cells]
        return sum(vals) / len(vals) if vals else 0
    W, H = 760, 340; left, bottom, top = 82, 66, 52
    pw, ph = W - left - 30, H - bottom - top
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H - bottom - v/100*ph
        p.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W-30}" y2="{y:.1f}" stroke="#ececec"/>')
        p.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}</text>')
    p.append(f'<text x="20" y="{top+ph/2}" transform="rotate(-90 20,{top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="10.5" fill="{MUTED}">Percent</text>')
    gw = pw/3; bw = gw*.26
    colors = ["#3d5a80", "#c26a3a"]
    for gi, cond in enumerate(conds):
        cx = left + gw*(gi+0.5)
        p.append(f'<text x="{cx:.1f}" y="{H-bottom+22}" text-anchor="middle" font-family="{FONT}" font-size="10.5">{labels[gi]}</text>')
        for mi, (key, lab) in enumerate([("success", "Success"), ("misbuy", "Misbuy")]):
            val = agg(cond, key)*100
            x = cx - bw + mi*(bw+4); y = H - bottom - val/100*ph
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{H-bottom-y:.1f}" fill="{colors[mi]}" opacity=".92"/>')
            p.append(f'<text x="{x+bw/2:.1f}" y="{y-5:.1f}" text-anchor="middle" font-family="{FONT}" font-size="9.5">{val:.1f}</text>')
    for mi, lab in enumerate(["Success", "Misbuy"]):
        lx = left + 10 + mi*100
        p.append(f'<rect x="{lx}" y="{top-24}" width="11" height="8" fill="{colors[mi]}"/>')
        p.append(f'<text x="{lx+16}" y="{top-17}" font-family="{FONT}" font-size="10.5">{lab}</text>')
    p.append("</svg>")
    (FIG / "fig_results.svg").write_text("".join(p), encoding="utf-8")


def horizons():
    W, H = 900, 300
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="40" y1="45" x2="860" y2="45" stroke="{INK}" stroke-width="1.4"/>')
    cards = [
        (50,  "H1  0–6 months",  ["assisted commerce", "human initiates", "agent searches and prepares", "human approves payment", "GCP: bounded step-up"]),
        (330, "H2  6–18 months", ["delegated commerce", "human sets mandate", "agent acts proactively", "human reviews exceptions", "GCP: revocable policy"]),
        (610, "H3  18–36 months", ["agent-native commerce", "agents negotiate", "human sets policy", "human audits outcomes", "GCP: agent contracts"]),
    ]
    for x, title, lines in cards:
        p.append(f'<circle cx="{x+110}" cy="45" r="5" fill="#3d5a80"/>')
        p.append(f'<text x="{x+110}" y="30" text-anchor="middle" font-family="{FONT}" font-size="12" font-weight="bold">{title}</text>')
        p.append(f'<rect x="{x}" y="72" width="220" height="176" rx="6" fill="#fff" stroke="{INK}" stroke-width="1.1"/>')
        for i, line in enumerate(lines):
            wt = "bold" if i == 0 else "normal"
            p.append(f'<text x="{x+110}" y="{100+i*26}" text-anchor="middle" font-family="{FONT}" font-size="10.5" font-weight="{wt}">{line}</text>')
    p.append(f'<text x="450" y="278" text-anchor="middle" font-family="{FONT}" font-size="9.5" fill="{MUTED}">The three patterns may overlap within 12–24 months; GCP is layered so H1 deployments become the policy/evidence layer for H2 and H3.</text>')
    p.append("</svg>")
    (FIG / "fig_horizons.svg").write_text("".join(p), encoding="utf-8")


def cockpit():
    rows = [json.loads(l) for l in open(ROOT / "experiments/results/cockpit.jsonl")]
    keys = [("driving", "generic"), ("driving", "gcp"), ("parked", "generic"), ("parked", "gcp")]
    labels = ["Drive / generic", "Drive / GCP", "Parked / generic", "Parked / GCP"]
    data = []
    for st, c in keys:
        rs = [r for r in rows if r["state"] == st and r["condition"] == c]
        data.append({"unsafe": sum(r["unsafe"] for r in rs)/len(rs)*100,
                     "defer": sum(r["deferred"] for r in rs)/len(rs)*100,
                     "success": sum(r["success"] for r in rs)/len(rs)*100})
    W, H = 760, 340; left, bottom, top = 82, 66, 52; pw, ph = W-left-30, H-bottom-top
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H-bottom-v/100*ph
        p.append(f'<line x1="{left}" y1="{y}" x2="{W-30}" y2="{y}" stroke="#ececec"/>')
        p.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}</text>')
    p.append(f'<text x="20" y="{top+ph/2}" transform="rotate(-90 20,{top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="10.5" fill="{MUTED}">Percent</text>')
    colors = ["#c26a3a", "#3d5a80", "#5b8c5a"]; metrics = [("unsafe", "Unsafe"), ("defer", "Defer/cart"), ("success", "Success")]
    gw = pw/4; bw = gw*0.2
    for gi, d in enumerate(data):
        cx = left+gw*(gi+.5)
        p.append(f'<text x="{cx}" y="{H-bottom+22}" text-anchor="middle" font-family="{FONT}" font-size="9.5">{labels[gi]}</text>')
        for mi, (key, lab) in enumerate(metrics):
            val = d[key]; x = cx - bw*1.5 + mi*bw; y = H-bottom-val/100*ph
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw-2:.1f}" height="{H-bottom-y:.1f}" fill="{colors[mi]}" opacity=".92"/>')
            if val > 0:
                p.append(f'<text x="{x+(bw-2)/2:.1f}" y="{y-4:.1f}" text-anchor="middle" font-family="{FONT}" font-size="8.5">{val:.0f}</text>')
    for mi, (key, lab) in enumerate(metrics):
        lx = left + 10 + mi*120
        p.append(f'<rect x="{lx}" y="{top-24}" width="11" height="8" fill="{colors[mi]}"/>')
        p.append(f'<text x="{lx+16}" y="{top-17}" font-family="{FONT}" font-size="10.5">{lab}</text>')
    p.append("</svg>")
    (FIG / "fig_cockpit.svg").write_text("".join(p), encoding="utf-8")


def realfield():
    rows = [json.loads(l) for l in open(ROOT / "experiments/results/real_parts.jsonl")]
    conds = ["C1", "C2"]; labels = ["Generic", "GCP"]
    vals = [sum(r["success"] for r in rows if r["condition"] == c)/max(1, sum(1 for r in rows if r["condition"] == c))*100 for c in conds]
    W, H = 620, 320; left, bottom, top = 82, 66, 52; pw, ph = W-left-30, H-bottom-top
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H-bottom-v/100*ph
        p.append(f'<line x1="{left}" y1="{y}" x2="{W-30}" y2="{y}" stroke="#ececec"/>')
        p.append(f'<text x="{left-8}" y="{y+4}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}</text>')
    p.append(f'<text x="20" y="{top+ph/2}" transform="rotate(-90 20,{top+ph/2})" text-anchor="middle" font-family="{FONT}" font-size="10.5" fill="{MUTED}">Success (percent)</text>')
    gw = pw/2; bw = gw*0.4
    for gi, val in enumerate(vals):
        cx = left+gw*(gi+.5); x = cx-bw/2; y = H-bottom-val/100*ph
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{H-bottom-y:.1f}" fill="{"#3d5a80" if gi==1 else "#c26a3a"}" opacity=".92"/>')
        p.append(f'<text x="{cx:.1f}" y="{H-bottom+22}" text-anchor="middle" font-family="{FONT}" font-size="10.5">{labels[gi]}</text>')
        p.append(f'<text x="{cx:.1f}" y="{y-6}" text-anchor="middle" font-family="{FONT}" font-size="10">{val:.1f}%</text>')
    p.append("</svg>")
    (FIG / "fig_realfield.svg").write_text("".join(p), encoding="utf-8")


if __name__ == "__main__":
    arch(); results(); horizons(); cockpit(); realfield(); print("figs ok")
