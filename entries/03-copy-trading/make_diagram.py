#!/usr/bin/env python3
"""Draw Entry 03's diagram from the shipped rows.

The entry's whole argument is a control, so the picture is the control: four
bars, one of which is a ranking that cannot know anything. Every value is
recomputed from data/q28s_events.jsonl at draw time. Nothing is typed in.

    python3 make_diagram.py > diagram.svg
"""
import json
import pathlib
import statistics
import sys

DATA = pathlib.Path(__file__).parent / "data"


def main():
    rows = [r for r in (json.loads(l) for l in open(DATA / "q28s_events.jsonl"))
            if not r.get("_manifest")]
    n10 = len(rows) // 10

    def decile(keyfn):
        top = sorted(rows, key=keyfn)[:n10]
        pos = sum(1 for r in top if r["week_pnl_late"] > 0) / len(top) * 100
        return pos, statistics.median([r["acct_usd_early"] for r in top])

    base = sum(1 for r in rows if r["week_pnl_late"] > 0) / len(rows) * 100
    base_acct = statistics.median([r["acct_usd_early"] for r in rows])
    bars = [
        ("Ranked by last week's dollars", "what a leaderboard shows you",
         *decile(lambda r: -r["week_pnl_early"]), False),
        ("Ranked by ACCOUNT SIZE alone", "contains no performance information",
         *decile(lambda r: -r["acct_usd_early"]), True),
        ("Ranked by last week's percent", "size-neutral",
         *decile(lambda r: -r["week_roi_early"]), False),
        ("Everyone on the board", "the base rate", base, base_acct, False),
    ]

    W, H = 940, 560
    L, R = 372, 812
    x = lambda v: L + (v / 100.0) * (R - L)
    y0, step = 250, 62
    gap = bars[0][2] - bars[1][2]
    head = (f"A ranking that knows nothing gets within "
            f"{gap:.1f} points of the real one.")

    o = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" '
         f'height="{H}" font-family="ui-sans-serif, -apple-system, \'Segoe UI\', Roboto, '
         f'Helvetica, Arial, sans-serif">',
         '<defs><linearGradient id="panel" x1="0" y1="0" x2="0" y2="1">'
         '<stop offset="0" stop-color="#111c33"/><stop offset="1" stop-color="#0a1120"/>'
         '</linearGradient><radialGradient id="glow" cx="0.22" cy="0.3" r="0.9">'
         '<stop offset="0" stop-color="#1b2a4a" stop-opacity="0.7"/>'
         '<stop offset="1" stop-color="#0a1120" stop-opacity="0"/></radialGradient></defs>',
         f'<rect width="{W}" height="{H}" fill="url(#panel)"/>',
         f'<rect width="{W}" height="{H}" fill="url(#glow)"/>',
         '<text x="64" y="70" fill="#6f86ab" font-size="13" letter-spacing="3.4">'
         'PROFITABLE NINE DAYS LATER &#183; TOP DECILE BY EACH RANKING</text>',
         f'<text x="64" y="114" fill="#eaf1fb" '
         f'font-size="{min(31, int((W - 128) * 1.92 / max(len(head), 1)))}" '
         f'font-weight="600">{head}</text>',
         '<text x="64" y="152" fill="#8fa3c4" font-size="16">'
         'The same wallets, the same nine days. Only the sort changes.'
         '<tspan x="64" dy="22">Sorting by how much money a wallet holds is not a '
         'skill measure, and it barely matters.</tspan></text>']

    o.append(f'<line x1="{x(base):.1f}" y1="{y0 - 34}" x2="{x(base):.1f}" '
             f'y2="{y0 + step * len(bars) - 30}" stroke="#41547d" stroke-width="1.5" '
             f'stroke-dasharray="4 4"/>')
    o.append(f'<text x="{x(base):.1f}" y="{y0 - 42}" fill="#5d7299" font-size="11" '
             f'text-anchor="middle">base rate {base:.1f}%</text>')

    for i, (name, sub, val, acct, control) in enumerate(bars):
        yy = y0 + i * step
        col = "#c98a2e" if control else ("#42557d" if val < base + 5 else "#2f9e8f")
        o.append(f'<text x="356" y="{yy + 4}" fill="#dbe6f6" font-size="15" '
                 f'font-weight="{"700" if control else "600"}" text-anchor="end">'
                 f'{name}</text>')
        o.append(f'<text x="356" y="{yy + 22}" fill="#6d82a6" font-size="12" '
                 f'text-anchor="end">{sub} &#183; median account '
                 f'${acct:,.0f}</text>')
        o.append(f'<rect x="{L}" y="{yy - 11}" width="{max(x(val) - L, 2):.1f}" '
                 f'height="22" rx="2" fill="{col}" opacity="0.92"/>')
        o.append(f'<text x="{x(val) + 12:.1f}" y="{yy + 5}" fill="#c7d6ec" '
                 f'font-size="14">{val:.1f}%</text>')

    o.append(f'<text x="64" y="{H - 24}" fill="#5d7299" font-size="12">'
             f'{len(rows):,} wallets present in both snapshots, 2026-08-21 and '
             f'2026-08-30. Recomputed from data/ by make_diagram.py.</text>')
    o.append("</svg>")
    sys.stdout.write("\n".join(o) + "\n")


if __name__ == "__main__":
    main()
