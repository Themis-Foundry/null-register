#!/usr/bin/env python3
"""Draw Entry 04's diagram from the shipped rows, so the picture cannot drift from
the data. Nothing is typed in: every dot is a null's profit per trade read from
data/batches/league-check-momentum/results.jsonl.

    python3 make_diagram.py > diagram.svg
"""
import json
import pathlib

HERE = pathlib.Path(__file__).parent
ROWS = HERE / "data" / "batches" / "league-check-momentum" / "results.jsonl"
MAN = HERE / "data" / "batches" / "league-check-momentum" / "manifest.json"

rows = [json.loads(l) for l in open(ROWS) if l.strip()]
man = json.load(open(MAN))
bar = man["promote_bar_R"]
nulls = sorted(r["expectancy_R"] for r in rows if r["kind"] == "null"
               and "expectancy_R" in r and r.get("n", 0) >= man["required_n"])
real = next(r["expectancy_R"] for r in rows if r["kind"] == "real")

W, H = 940, 400
L, R = 70, 900
x0, x1 = 0.0, 0.35


def X(v):
    return L + (v - x0) / (x1 - x0) * (R - L)


cleared = sum(1 for v in nulls if v >= bar)
beat = sum(1 for v in nulls if v >= real)

out = []
out.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
           f'font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">')
out.append('<defs><linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">'
           '<stop offset="0" stop-color="#0f172a"/><stop offset="1" stop-color="#111827"/>'
           '</linearGradient></defs>')
out.append(f'<rect width="{W}" height="{H}" fill="url(#bg)"/>')
out.append('<text x="60" y="52" fill="#94a3b8" font-size="13" letter-spacing="3">'
           'FORTY STRATEGIES WITH NO SIGNAL · ONE PROMOTION BAR · ONE REAL STRATEGY</text>')
out.append(f'<text x="60" y="98" fill="#f8fafc" font-size="30" font-weight="700">'
           f'{cleared} of {len(nulls)} guessed their way over the bar</text>')
out.append('<text x="60" y="126" fill="#cbd5e1" font-size="15">'
           'Each dot is the same trend rule run on a one-week-scrambled market. '
           'Profit per trade after costs, in units of the amount risked.</text>')

# axis
ay = 260
out.append(f'<line x1="{L}" y1="{ay}" x2="{R}" y2="{ay}" stroke="#334155" stroke-width="1.5"/>')
for t in [0.0, 0.07, 0.1, 0.2, 0.3]:
    x = X(t)
    out.append(f'<line x1="{x:.1f}" y1="{ay}" x2="{x:.1f}" y2="{ay + 6}" stroke="#475569"/>')
    lab = f"{t:+.2f}R" if t else "0"
    out.append(f'<text x="{x:.1f}" y="{ay + 24}" fill="#94a3b8" font-size="12" text-anchor="middle">{lab}</text>')

# the bar
xb = X(bar)
out.append(f'<line x1="{xb:.1f}" y1="150" x2="{xb:.1f}" y2="{ay}" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6 4"/>')
out.append(f'<text x="{xb + 8:.1f}" y="164" fill="#f59e0b" font-size="13" font-weight="600">the bar, +0.07R</text>')

# nulls, beeswarm by simple stacking
placed = []
for v in nulls:
    x = X(v)
    lane = 0
    while any(abs(x - px) < 14 and pl == lane for px, pl in placed):
        lane += 1
    placed.append((x, lane))
    y = ay - 18 - lane * 16
    col = "#34d399" if v >= bar else "#64748b"
    out.append(f'<circle cx="{x:.1f}" cy="{y}" r="6.5" fill="{col}" opacity="0.92"/>')

# the real strategy
xr = X(real)
out.append(f'<line x1="{xr:.1f}" y1="150" x2="{xr:.1f}" y2="{ay}" stroke="#f8fafc" stroke-width="2"/>')
out.append(f'<text x="{xr:.1f}" y="142" fill="#f8fafc" font-size="13" font-weight="600" text-anchor="middle">'
           f'the real strategy, +{real:.3f}R</text>')
out.append(f'<text x="{xr:.1f}" y="{ay + 46}" fill="#fca5a5" font-size="13" text-anchor="middle">'
           f'{beat} guessing strategies did better</text>')

# the best null
xm = X(max(nulls))
out.append(f'<text x="{xm:.1f}" y="{ay + 46}" fill="#34d399" font-size="13" text-anchor="middle">'
           f'best guess, +{max(nulls):.3f}R</text>')

# legend
out.append(f'<circle cx="72" cy="{H - 34}" r="6" fill="#34d399"/>'
           f'<text x="86" y="{H - 29}" fill="#cbd5e1" font-size="13">cleared the bar with no signal</text>')
out.append(f'<circle cx="330" cy="{H - 34}" r="6" fill="#64748b"/>'
           f'<text x="344" y="{H - 29}" fill="#cbd5e1" font-size="13">did not</text>')
out.append(f'<text x="{R}" y="{H - 29}" fill="#64748b" font-size="12" text-anchor="end">'
           f'batch league-check-momentum · seed {man["seed"]} · 2026-08-08</text>')
out.append('</svg>')
print("\n".join(out))
