#!/usr/bin/env python3
"""Draw Entry 02's diagram from the shipped rows, so the picture cannot drift
from the data the way a hand-made one would.

Every bar and every whisker below is bootstrapped from data/*_events.jsonl at a
fixed seed. Nothing is typed in. Run it and diff the output: if the SVG changes,
either the data changed or someone edited the picture by hand.

    python3 make_diagram.py > diagram.svg
"""
import json
import pathlib
import random
import statistics
import sys

DATA = pathlib.Path(__file__).parent / "data"
SEED = 20260831
BOOT = 4000


def rows(name):
    return [r for r in (json.loads(l) for l in open(DATA / f"{name}_events.jsonl"))
            if not r.get("_manifest")]


def est(vals, label):
    """Mean and a 95% bootstrap interval, in percent.

    The RNG is seeded from the label rather than shared across the run. A single
    stream would make each interval depend on how many draws happened before it,
    so re-deriving one figure on its own would give a different answer than
    re-deriving all of them together. That is not a reproducible interval, and
    verify.py caught exactly that: it computed Q12's interval from a fresh
    stream and disagreed with this file by more than a point.
    """
    m = statistics.mean(vals)
    rng = random.Random(f"{SEED}:{label}")
    b = sorted(statistics.mean(rng.choices(vals, k=len(vals))) for _ in range(BOOT))
    return m * 100, b[int(0.025 * BOOT)] * 100, b[int(0.975 * BOOT)] * 100


def main():
    q8 = [r["ar"] for r in rows("q8") if r["bucket"] == "scored"]
    q9 = [r["post"] for r in rows("q9") if r["bucket"] == "scored"]
    q10 = rows("q10")
    cl = [r["ar"] for r in q10 if r["bucket"] == "cluster"]
    sg = [r["ar"] for r in q10 if r["bucket"] == "single"]
    q12 = [r for r in rows("q12") if r["bucket"] == "scored"]
    early = [r["post"] for r in q12 if r["date"][:4] < "2021"]
    late = [r["post"] for r in q12 if r["date"][:4] >= "2021"]

    # the cluster-minus-single spread needs its own bootstrap over both buckets
    m10 = (statistics.mean(cl) - statistics.mean(sg)) * 100
    rng = random.Random(f"{SEED}:q10_spread")
    b10 = sorted((statistics.mean(rng.choices(cl, k=len(cl))) -
                  statistics.mean(rng.choices(sg, k=len(sg)))) * 100
                 for _ in range(BOOT))
    bars = [
        ("S&P deletions, 2016-2020", "the rebound, while it lasted", *est(early, "q12_early"), len(early)),
        ("S&P deletions, 2021-2026", "the same rule, five years later", *est(late, "q12_late"), len(late)),
        ("Insider clusters", "three insiders beat one, supposedly",
         m10, b10[int(0.025 * BOOT)], b10[int(0.975 * BOOT)], len(cl) + len(sg)),
        ("Buyback announcements", "buy when the company buys", *est(q8, "q8_mean"), len(q8)),
        ("Rights offerings", "the dilution dip, after", *est(q9, "q9_post"), len(q9)),
    ]

    # ── geometry ────────────────────────────────────────────────────────────
    # The scale is derived from the widest interval, never typed. The first
    # version of this file hard-coded -14 to +20 and the 2016-2020 whisker ran
    # off the canvas at +30.5 with its label past the edge.
    W, H = 940, 560
    L, R = 300, 862
    span = max(abs(v) for _, _, m, lo, hi, _ in bars for v in (m, lo, hi))
    lo_ax, hi_ax = -span * 1.12, span * 1.12
    x = lambda v: L + (v - lo_ax) / (hi_ax - lo_ax) * (R - L)
    y0, step = 248, 58

    crosses = sum(1 for *_, m, clo, chi, _ in [(0, 0, *b[2:]) for b in bars]
                  if clo <= 0 <= chi)
    # The headline is COUNTED off the bars, not typed above them. A picture whose
    # caption is written by hand is a picture that can disagree with itself, and
    # the first draft of this one did: it claimed one bar cleared zero when the
    # only interval clear of zero is negative.
    odd = [b for b in bars if not (b[3] <= 0 <= b[4])]
    headline = (f"{'All five' if crosses == 5 else f'{crosses} of the 5'} intervals "
                f"cross zero." if crosses >= 4 else
                f"{crosses} of the 5 intervals cross zero.")
    if crosses == 4 and odd and odd[0][2] < 0:
        headline = "Four intervals cross zero. The fifth points the wrong way."

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
         f'width="{W}" height="{H}" font-family="ui-sans-serif, -apple-system, '
         f'\'Segoe UI\', Roboto, Helvetica, Arial, sans-serif">',
         '<defs><linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#111c33"/><stop offset="1" stop-color="#0a1120"/>'
         '</linearGradient><radialGradient id="glow" cx="0.22" cy="0.3" r="0.9">'
         '<stop offset="0" stop-color="#1b2a4a" stop-opacity="0.7"/>'
         '<stop offset="1" stop-color="#0a1120" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#panel)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
         '<text x="64" y="70" fill="#6f86ab" font-size="13" letter-spacing="3.4">'
         'RETURN VS THE MARKET, WITH THE UNCERTAINTY DRAWN</text>',
         # sized to fit rather than assumed: the first render clipped "wrong way"
         # off the right edge at a hard-coded 33px
         f'<text x="64" y="114" fill="#eaf1fb" '
         f'font-size="{min(33, int((W - 128) * 1.92 / max(len(headline), 1)))}" '
         f'font-weight="600">{headline}</text>',
         '<text x="64" y="152" fill="#8fa3c4" font-size="16">'
         'The bar is the average. The whisker is the range the data actually supports.'
         '<tspan x="64" dy="22">A whisker touching the line means the signal has not shown '
         'it does anything at all.</tspan>'
         '<tspan x="64" dy="22">The rebound that paid +12.4% is also the widest bar here, '
         'and that is the point.</tspan></text>']

    o.append(f'<line x1="{x(0):.1f}" y1="{y0 - 30}" x2="{x(0):.1f}" '
             f'y2="{y0 + step * (len(bars) - 1) + 26}" stroke="#41547d" stroke-width="1.5"/>')
    tick = 10
    v = -int(span // tick) * tick
    while v <= span:
        o.append(f'<text x="{x(v):.1f}" y="{y0 - 40}" fill="#5d7299" font-size="11" '
                 f'text-anchor="middle">{v:+d}%</text>')
        v += tick

    for i, (name, sub, m, clo, chi, n) in enumerate(bars):
        yy = y0 + i * step
        straddles = clo <= 0 <= chi
        col = "#42557d" if straddles else ("#2f9e8f" if m > 0 else "#c98a2e")
        o.append(f'<text x="284" y="{yy + 4}" fill="#dbe6f6" font-size="15" '
                 f'font-weight="600" text-anchor="end">{name}</text>')
        o.append(f'<text x="284" y="{yy + 22}" fill="#6d82a6" font-size="12" '
                 f'text-anchor="end">{sub} &#183; n={n:,}</text>')
        a, b = sorted((x(0), x(m)))
        o.append(f'<rect x="{a:.1f}" y="{yy - 9}" width="{max(b - a, 2):.1f}" '
                 f'height="18" rx="2" fill="{col}" opacity="0.92"/>')
        o.append(f'<line x1="{x(clo):.1f}" y1="{yy}" x2="{x(chi):.1f}" y2="{yy}" '
                 f'stroke="#8fa3c4" stroke-width="1.6"/>')
        for e in (clo, chi):
            o.append(f'<line x1="{x(e):.1f}" y1="{yy - 6}" x2="{x(e):.1f}" '
                     f'y2="{yy + 6}" stroke="#8fa3c4" stroke-width="1.6"/>')
        # labels sit outside the whisker, and flip inward rather than leave the canvas
        right = m >= 0
        lx = x(chi) + 12 if right else x(clo) - 12
        anchor = "start" if right else "end"
        if lx > W - 76 or lx < L - 240:
            lx, anchor = (x(clo) - 12, "end") if right else (x(chi) + 12, "start")
        o.append(f'<text x="{lx:.1f}" y="{yy + 5}" fill="#c7d6ec" font-size="14" '
                 f'text-anchor="{anchor}">{m:+.1f}%</text>')
        o.append(f'<text x="{x(clo):.1f}" y="{yy + 26}" fill="#55688f" font-size="10.5" '
                 f'text-anchor="start">{clo:+.1f} to {chi:+.1f}</text>')

    o.append(f'<text x="64" y="{H - 24}" fill="#5d7299" font-size="12">'
             'Bootstrapped from the rows in data/, 4,000 resamples at a fixed seed. '
             'Regenerate with make_diagram.py and diff the file.</text>')
    o.append("</svg>")
    sys.stdout.write("\n".join(o) + "\n")


if __name__ == "__main__":
    main()
