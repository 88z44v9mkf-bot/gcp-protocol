#!/usr/bin/env python3
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
FIG = ROOT / "paper" / "figures"; FIG.mkdir(exist_ok=True)
FONT = "Times New Roman, Times, serif"; INK = "#222"; MUTED = "#555"


def box(x, y, w, h, lines, fill="#fff", fs=11.5, bold=False):
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="6" fill="{fill}" stroke="{INK}" stroke-width="1.2"/>']
    n = len(lines)
    for i, line in enumerate(lines):
        yy = y + h / 2 + (i - (n - 1) / 2) * (fs + 4) + fs * .35
        wt = "bold" if bold and i == 0 else "normal"
        s.append(f'<text x="{x+w/2}" y="{yy:.1f}" text-anchor="middle" font-family="{FONT}" font-size="{fs}" font-weight="{wt}" fill="{INK}">{line}</text>')
    return "".join(s)


def arrow(x1, y1, x2, y2):
    return f'<path d="M{x1},{y1} L{x2},{y2}" stroke="{MUTED}" stroke-width="1.2" marker-end="url(#a)"/>'


def arch():
    W, H = 900, 470
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 z" fill="{MUTED}"/></marker></defs>',
         f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(box(40, 20, 820, 54, ["PA runtime: mobile app  ·  PC  ·  cockpit  ·  third-party assistant (Doubao, Qwen, ChatGPT, Claude, ...)"], fs=11.5, bold=True))
    p.append(box(40, 100, 820, 66, ["GCP client: intent  →  authorization check  →  plan  →  execute  →  evidence"], fs=11.5, bold=True))
    p.append(box(40, 192, 820, 74, ["GCP core: discovery | catalog + vehicle context | cart/order | booking | payment intent | fulfillment | aftercare"], fs=11, bold=True))
    p.append(box(40, 292, 260, 64, ["Safety & compliance", "compatibility · recall · insurance", "no prompt override"], fs=10.5))
    p.append(box(320, 292, 260, 64, ["Evidence ledger", "consent · checks · settlement", "hash-chained"], fs=10.5))
    p.append(box(600, 292, 260, 64, ["Error bus", "typed errors + alternatives", "recovery paths"], fs=10.5))
    p.append(box(40, 386, 400, 62, ["Adapters: Poppy | UCP | ACP | OEM DMS/ERP | PSPs"], fs=11))
    p.append(box(460, 386, 400, 62, ["Merchants · dealers · insurers · payment rails"], fs=11))
    for x in (450,):
        p.append(arrow(x, 74, x, 100)); p.append(arrow(x, 166, x, 192)); p.append(arrow(x, 266, x, 292)); p.append(arrow(x, 356, x, 386))
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
    W, H = 760, 330; left, bottom, top = 70, 60, 40
    pw, ph = W - left - 30, H - bottom - top; ymax = 1.0
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', f'<rect width="{W}" height="{H}" fill="#fff"/>']
    p.append(f'<line x1="{left}" y1="{H-bottom}" x2="{W-30}" y2="{H-bottom}" stroke="{INK}"/>')
    p.append(f'<line x1="{left}" y1="{top}" x2="{left}" y2="{H-bottom}" stroke="{INK}"/>')
    for v in range(0, 101, 20):
        y = H - bottom - v/100*ph
        p.append(f'<line x1="{left}" y1="{y:.1f}" x2="{W-30}" y2="{y:.1f}" stroke="#eee"/>')
        p.append(f'<text x="{left-8}" y="{y+4:.1f}" text-anchor="end" font-family="{FONT}" font-size="10" fill="{MUTED}">{v}%</text>')
    gw = pw/3; bw = gw*0.25
    colors = ["#3d5a80", "#c26a3a"]
    for gi, cond in enumerate(conds):
        cx = left + gw*(gi+0.5)
        p.append(f'<text x="{cx:.1f}" y="{H-bottom+20}" text-anchor="middle" font-family="{FONT}" font-size="11">{labels[gi]}</text>')
        for mi, (key, lab) in enumerate([("success", "Success"), ("misbuy", "Misbuy")]):
            val = agg(cond, key)
            x = cx - bw + mi*(bw+3); y = H - bottom - val*ph
            p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{bw:.1f}" height="{H-bottom-y:.1f}" fill="{colors[mi]}" opacity=".9"/>')
    for mi, lab in enumerate(["Success", "Misbuy"]):
        lx = left + 10 + mi*100
        p.append(f'<rect x="{lx}" y="{top-22}" width="12" height="9" fill="{colors[mi]}"/>')
        p.append(f'<text x="{lx+18}" y="{top-14}" font-family="{FONT}" font-size="10.5">{lab}</text>')
    p.append("</svg>")
    (FIG / "fig_results.svg").write_text("".join(p), encoding="utf-8")


if __name__ == "__main__":
    arch(); results(); print("figs ok")
