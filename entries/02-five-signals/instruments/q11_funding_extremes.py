"""
Q11 — Does funding-rate extremity predict forward return on BTC/ETH?
(registered 2026-08-08, docs/QUESTIONS.md)

Registered condition: funding in the top/bottom decile of a TRAILING 90-day
window (trailing, not full-sample — full-sample deciles are look-ahead).
Registered direction: extreme positive funding precedes negative forward
return (crowded longs pay to be long). Outcomes: forward 8h / 24h / 72h
returns from klines.

⚠ VERDICT CEILING, stated up front: the registration names the cohort
"every 8h funding print ... 2019→now" and demands the effect hold in BOTH
the 2021 bull and 2022 bear sub-samples. The funding file on disk holds
2024-01 → 2026-06 ONLY (fetched once, 2026-06-26). Neither registered
sub-sample exists in the data — the day's FOURTH
registered-against-unverified-data case (Q17 category, Q8 size, Q12 cohort,
now Q11 span). Everything below is therefore PARTIAL by construction; the
unblock is a bounded 2019-2023 funding backfill (Binance serves it free).

Method: per asset, trailing decile edges over the prior 270 prints (90d x
3/day), strictly excluding the current print. Condition fires on top/bottom
decile. Forward returns from 1h klines at the print timestamp (NEXT hour
onward — no same-bar). Comparison: conditional mean vs the unconditional
mean of ALL prints (the mundane null), plus a 40-run placebo drawing the
same number of random prints. Overlapping 72h windows are reported as-is
and flagged — at PARTIAL status no claim hardens anyway.

Output: strategies/_data/q11_funding_extremes.json

    python3 q11_funding_extremes.py
"""

import bisect
import json
import os

import register_emit
import random
import statistics
from datetime import datetime, timezone

_HERE = os.path.dirname(os.path.abspath(__file__))
_D = os.path.join(_HERE, "strategies", "_data")
OUT = os.path.join(_D, "q11_funding_extremes.json")

TRAIL = 270                 # 90 days x 3 prints/day, registered
HORIZONS_H = (8, 24, 72)
N_PLACEBO = 40
SEED = 21001108


def load_klines(symbol):
    """1h bars: {"bars": [[iso_ts, o, h, l, c], ...]} — ISO timestamps, no
    volume. Converted to epoch-ms so funding prints (epoch-ms) join directly."""
    with open(os.path.join(_D, f"binance_klines_{symbol}_1h.json")) as fh:
        k = json.load(fh)
    rows = k["bars"]
    ts = [int(datetime.fromisoformat(r[0]).timestamp() * 1000) for r in rows]
    close = [float(r[4]) for r in rows]
    return ts, close


def forward_return(ts, close, t_ms, hours):
    i = bisect.bisect_right(ts, t_ms)          # first kline AFTER the print
    j = i + hours
    if i >= len(close) or j >= len(close):
        return None
    return close[j] / close[i] - 1.0


def run_asset(asset, symbol):
    with open(os.path.join(_D, f"binance_funding_{asset}.json")) as fh:
        prints = json.load(fh)
    # 2019-2023 backfill (PLU-D1 rerouted to Helios after Binance geo-blocked
    # the US harvest, fetched 2026-08-18) — union on t, the registered cohort
    # "2019→now" finally exists on disk.
    backfill = os.path.join(_D, f"binance_funding_{asset}_2019_2023.json")
    if os.path.exists(backfill):
        with open(backfill) as fh:
            prints.extend(json.load(fh))
    seen = set()
    prints = [p for p in prints if not (p["t"] in seen or seen.add(p["t"]))]
    prints.sort(key=lambda r: r["t"])
    ts, close = load_klines(symbol)
    rng = random.Random(SEED)

    rows = []                # (t, rate, {h: fwd})
    skipped_no_kline = 0
    for p in prints:
        fwd = {}
        ok = True
        for h in HORIZONS_H:
            r = forward_return(ts, close, p["t"], h)
            if r is None:
                ok = False
                break
            fwd[h] = r
        if ok:
            rows.append((p["t"], p["r"], fwd))
        else:
            skipped_no_kline += 1

    def year_of(t_ms):
        return datetime.fromtimestamp(t_ms / 1000, tz=timezone.utc).year

    top, bottom = [], []
    top_by_year, elig_by_year = {}, {}
    for i in range(TRAIL, len(rows)):
        window = sorted(r for _, r, _ in rows[i - TRAIL:i])
        lo = window[int(0.10 * TRAIL)]
        hi = window[int(0.90 * TRAIL)]
        t, r, fwd = rows[i]
        y = year_of(t)
        elig_by_year.setdefault(y, []).append(fwd)
        if r >= hi:
            top.append(fwd)
            top_by_year.setdefault(y, []).append(fwd)
        elif r <= lo:
            bottom.append(fwd)
    eligible = rows[TRAIL:]

    # THE REGISTERED SURVIVAL TEST: the direction (top-decile funding ->
    # NEGATIVE forward return, i.e. top mean BELOW that year's unconditional)
    # must hold in BOTH the 2021 bull and the 2022 bear.
    sub_samples = {}
    for y in (2021, 2022):
        te, ee = top_by_year.get(y, []), elig_by_year.get(y, [])
        sub_samples[str(y)] = {
            "n_top": len(te), "n_eligible": len(ee),
            "top_mean": {h: statistics.mean(f[h] for f in te) if te else None
                         for h in HORIZONS_H},
            "uncond_mean": {h: statistics.mean(f[h] for f in ee) if ee else None
                            for h in HORIZONS_H},
            "direction_holds": {h: (statistics.mean(f[h] for f in te) <
                                    statistics.mean(f[h] for f in ee))
                                if te and ee else None
                                for h in HORIZONS_H}}

    def mean_by_h(bucket):
        return {h: statistics.mean(f[h] for f in bucket) if bucket else None
                for h in HORIZONS_H}

    uncond = mean_by_h([f for _, _, f in eligible])
    placebo = {h: [] for h in HORIZONS_H}
    for _ in range(N_PLACEBO):
        sample = [f for _, _, f in rng.sample(eligible, len(top))]
        for h in HORIZONS_H:
            placebo[h].append(statistics.mean(f[h] for f in sample))

    span = (datetime.fromtimestamp(rows[0][0] / 1000, tz=timezone.utc).date().isoformat(),
            datetime.fromtimestamp(rows[-1][0] / 1000, tz=timezone.utc).date().isoformat())
    res = {"asset": asset.upper(), "span_on_disk": span,
           "prints_total": len(prints), "prints_scored": len(rows),
           "skipped_no_kline_coverage": skipped_no_kline,
           "n_eligible_after_trailing_warmup": len(eligible),
           "n_top_decile": len(top), "n_bottom_decile": len(bottom),
           "unconditional_mean": uncond,
           "top_decile_mean": mean_by_h(top),
           "bottom_decile_mean": mean_by_h(bottom),
           "registered_sub_samples": sub_samples,
           "placebo_top_size": {h: {"mean": statistics.mean(placebo[h]),
                                    "min": min(placebo[h]), "max": max(placebo[h]),
                                    "p_lower": sum(1 for m in placebo[h]
                                                   if m <= mean_by_h(top)[h]) / N_PLACEBO}
                                for h in HORIZONS_H}}
    top_ids, bot_ids = {id(f) for f in top}, {id(f) for f in bottom}
    warm = set(id(f) for _, _, f in rows[:TRAIL])
    ev = []
    for t, r, fwd in rows:
        ev.append({"asset": asset.upper(),
                   "ts_ms": t,
                   "date": datetime.fromtimestamp(t / 1000, tz=timezone.utc)
                                   .isoformat(),
                   "funding_rate": r,
                   "bucket": ("warmup" if id(fwd) in warm else
                              "top_decile" if id(fwd) in top_ids else
                              "bottom_decile" if id(fwd) in bot_ids else
                              "eligible_mid"),
                   **{f"fwd_{h}h": fwd[h] for h in HORIZONS_H}})
    register_emit.emit(f"Q11_{asset.upper()}", ev,
                       {"prints_total": len(prints),
                        "prints_scored": len(rows),
                        "skipped_no_kline_coverage": skipped_no_kline,
                        "trailing_warmup_prints": TRAIL,
                        "n_eligible": len(eligible),
                        "n_top_decile": len(top),
                        "n_bottom_decile": len(bottom)})
    return res


def main():
    results = [run_asset("btc", "BTCUSDT"), run_asset("eth", "ETHUSDT")]
    out = {"question": "Q11", "run_on": datetime.now().date().isoformat(),
           "K_declared": 1,
           "verdict_ceiling": "FULL — the registered cohort exists on disk since "
                              "the 2026-08-18 Helios backfill (Binance geo-blocks "
                              "the US; the box in Nuremberg is not blocked)",
           "direction_registered": "extreme positive funding precedes negative "
                                   "forward return",
           "trailing_window_prints": TRAIL, "seed": SEED,
           "assets": results}
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print("=" * 74)
    print("  Q11 — funding extremity vs forward return (full registered cohort)")
    print("=" * 74)
    for a in results:
        print(f"  {a['asset']}  span {a['span_on_disk'][0]}..{a['span_on_disk'][1]}"
              f"   eligible {a['n_eligible_after_trailing_warmup']}"
              f"   top-decile n={a['n_top_decile']}  bottom n={a['n_bottom_decile']}")
        for h in HORIZONS_H:
            u = a["unconditional_mean"][h]
            t = a["top_decile_mean"][h]
            b = a["bottom_decile_mean"][h]
            pl = a["placebo_top_size"][h]
            print(f"    {h:>3}h: uncond {u:+.4f} | top-decile {t:+.4f} "
                  f"(placebo p_lower={pl['p_lower']:.3f}) | bottom {b:+.4f}")
        for y, s in a.get("registered_sub_samples", {}).items():
            holds = s["direction_holds"]
            print(f"    {y}: n_top={s['n_top']}  direction holds: "
                  + "  ".join(f"{h}h={'YES' if holds[h] else 'no' if holds[h] is not None else '—'}"
                              for h in HORIZONS_H))
    print("  registered survival test: direction must hold in BOTH 2021 and 2022;")
    print("  the 2024-26 window is the out-of-sample repeat (THE BAR, item 4).")
    print(f"  -> {OUT}")


if __name__ == "__main__":
    main()
