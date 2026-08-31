"""
Q8 — Do share-repurchase announcements produce abnormal returns?
(registered 2026-08-08, docs/QUESTIONS.md — DESCRIPTIVE: base rate and
dispersion first; no direction registered, none is verdict-ed here)

Cohort: every row of strategies/_data/buyback_events.jsonl (2016-2024 bulk)
plus datasets/edgar/events_buyback.jsonl (the forward tail), unselected.
Outcome: stock cumulative return minus SPY, entry close NEXT bar after
filing_date (S3 law), exit t+60 trading days.

⚠ The registration's second half — "does announcement SIZE condition it" —
is COULD-NOT-LOOK on this corpus: neither feed carries an announced amount
(rows are {ticker, cik, filing_date} only). Stated, not fudged with a proxy.
A size-capturing harvester is the unblock, same shape as Q17's tag fix.

Discipline (shared rig with q10_insider_clusters.py):
  - survivorship COUNTED: tickers without bars, events without outcome
    coverage — loud, never silent
  - placebo null: N_PLACEBO re-runs, every event moved to a random trading
    date in its own ticker's history — the "abnormal" in abnormal return
    must mean abnormal vs these same tickers' ordinary drift, or it means
    nothing
  - per-ticker 60-tday cooldown so outcome windows never overlap (serial
    announcers), disclosed methods choice
  - split-half repeat 2016-2020 / 2021-2026

Output: strategies/_data/q8_buyback_drift.json + printed report.

    python3 q8_buyback_drift.py
"""

import json
import os

import register_emit
import random
import statistics
from collections import defaultdict
from datetime import datetime

from q10_insider_clusters import (load_bars, next_bar_index, abnormal_return)


def identity_break(b, entry_i, hold=60, up=4.0, down=0.25):
    """A single close-to-close day factor outside [down, up] inside the outcome
    window is an identity break (ticker re-listing, unadjusted reverse split,
    spinoff misadjustment), not a return anybody earned. Calibrated on this
    corpus: CBL's bankruptcy re-listing prints 335x in one day and CNX's
    spinoff prints 0.10x, while the worst REAL single days (biotech failures,
    squeezes) stay inside the band. Symmetric on purpose — it may not know the
    outcome's sign. Returns the offending (date, factor) or None."""
    exit_i = min(entry_i + hold, len(b["closes"]) - 1)
    for i in range(entry_i + 1, exit_i + 1):
        prev = b["closes"][i - 1]
        if not prev:
            continue
        f = b["closes"][i] / prev
        if f > up or f < down:
            return (b["dates"][i], f)
    return None

_HERE = os.path.dirname(os.path.abspath(__file__))
_D = os.path.join(_HERE, "strategies", "_data")
BULK = os.path.join(_D, "buyback_events.jsonl")
FORWARD = os.path.join(_HERE, "datasets", "edgar", "events_buyback.jsonl")
OUT = os.path.join(_D, "q8_buyback_drift.json")

HOLD_TDAYS = 60
COOLDOWN_TDAYS = 60
N_PLACEBO = 40
SEED = 21000808            # Q8, registered 2026-08-08 — fixed, not tuned


def main():
    rng = random.Random(SEED)
    spy = load_bars("SPY")
    assert spy, "SPY bars missing"

    per_ticker = defaultdict(set)
    rows = 0
    for path in (BULK, FORWARD):
        with open(path) as fh:
            for line in fh:
                rows += 1
                try:
                    r = json.loads(line)
                    t = (r.get("ticker") or "").strip().upper()
                    d = r.get("filing_date")
                    if t and d:
                        per_ticker[t].add(d)
                except ValueError:
                    pass

    tally = {"rows_total": rows, "tickers_total": len(per_ticker),
             "tickers_no_bars": 0, "events_no_outcome_coverage": 0,
             "events_cooldown_skipped": 0}
    events = []
    suspects = []          # identity-break exclusions — each one listed by name
    for ticker, dates in per_ticker.items():
        b = load_bars(ticker)
        if b is None:
            tally["tickers_no_bars"] += 1
            continue
        cooldown_until = -1
        for fdate in sorted(dates):
            entry_i = next_bar_index(b, fdate)
            if entry_i >= len(b["closes"]):
                tally["events_no_outcome_coverage"] += 1
                continue
            if entry_i <= cooldown_until:
                tally["events_cooldown_skipped"] += 1
                continue
            ar = abnormal_return(b, spy, entry_i)
            if ar is None:
                tally["events_no_outcome_coverage"] += 1
                continue
            brk = identity_break(b, entry_i, HOLD_TDAYS)
            if brk:
                suspects.append({"ticker": ticker, "filing": fdate, "ar": ar,
                                 "break_day": brk[0], "day_factor": brk[1]})
                cooldown_until = entry_i + COOLDOWN_TDAYS
                continue
            events.append({"ticker": ticker, "filing": fdate,
                           "entry": b["dates"][entry_i], "ar": ar})
            cooldown_until = entry_i + COOLDOWN_TDAYS

    ars = [e["ar"] for e in events]
    ars_sorted = sorted(ars)
    def pct(p):
        return ars_sorted[min(len(ars_sorted) - 1, int(p * len(ars_sorted)))]
    mean_ar = statistics.mean(ars)
    win = sum(1 for a in ars if a > 0) / len(ars)

    # bootstrap CI on the mean
    boots = sorted(statistics.mean(rng.choices(ars, k=len(ars)))
                   for _ in range(2000))
    ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))])

    # placebo: same tickers, same event counts, random dates
    bars_cache = {}
    def cached(t):
        if t not in bars_cache:
            bars_cache[t] = load_bars(t)
        return bars_cache[t]
    placebo_means = []
    for _ in range(N_PLACEBO):
        vals = []
        for e in events:
            b = cached(e["ticker"])
            hi = len(b["closes"]) - HOLD_TDAYS - 1
            if hi <= 61:
                continue
            j = rng.randint(61, hi)
            if identity_break(b, j, HOLD_TDAYS):     # same screen, same rule
                continue
            ar = abnormal_return(b, spy, j)
            if ar is not None:
                vals.append(ar)
        placebo_means.append(statistics.mean(vals))
    excess = mean_ar - statistics.mean(placebo_means)
    p_emp = sum(1 for m in placebo_means if m >= mean_ar) / N_PLACEBO

    halves = {}
    for label, lo, hi in (("2016-2020", "2016", "2021"), ("2021-2026", "2021", "2027")):
        h = [e["ar"] for e in events if lo <= e["entry"][:4] < hi]
        halves[label] = {"n": len(h), "mean_ar": statistics.mean(h) if h else None}

    out = {
        "question": "Q8", "run_on": datetime.now().date().isoformat(),
        "K_declared": 1, "descriptive": True, "direction_registered": None,
        "size_conditioning": "COULD-NOT-LOOK — neither feed records announced "
                             "amount; rows are {ticker, cik, filing_date} only",
        "n_events": len(ars), "mean_ar": mean_ar,
        "median_ar": statistics.median(ars), "sd": statistics.pstdev(ars),
        "win_rate_vs_spy": win,
        "pct": {"p10": pct(0.10), "p25": pct(0.25), "p75": pct(0.75), "p90": pct(0.90)},
        "mean_ci95_bootstrap": ci,
        "placebo": {"n_runs": N_PLACEBO, "mean": statistics.mean(placebo_means),
                    "max": max(placebo_means), "min": min(placebo_means),
                    "excess_vs_placebo": excess, "p_empirical": p_emp, "seed": SEED},
        "split_half": halves,
        "survivorship_and_exclusions": tally,
        "identity_break_exclusions": suspects,
    }
    rows_ev = [dict(e, bucket="scored") for e in events] + \
              [dict(s, bucket="excluded", excluded_reason="identity_break") for s in suspects]
    ev_path = register_emit.emit("Q8", rows_ev, tally)
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print("=" * 72)
    print("  Q8 — buyback-announcement drift, DESCRIPTIVE (registered 2026-08-08)")
    print("=" * 72)
    print(f"  n={len(ars)}   mean AR {mean_ar:+.4f}  CI95 [{ci[0]:+.4f},{ci[1]:+.4f}]"
          f"   median {statistics.median(ars):+.4f}   sd {statistics.pstdev(ars):.4f}")
    print(f"  win vs SPY {win:.1%}   p10 {pct(0.10):+.3f}  p25 {pct(0.25):+.3f}"
          f"  p75 {pct(0.75):+.3f}  p90 {pct(0.90):+.3f}")
    print(f"  placebo ({N_PLACEBO} runs): mean {statistics.mean(placebo_means):+.4f}"
          f"  [{min(placebo_means):+.4f},{max(placebo_means):+.4f}]"
          f"   excess {excess:+.4f}   p = {p_emp:.3f}")
    for label, h in halves.items():
        print(f"  {label}: n={h['n']}  mean AR {h['mean_ar']:+.4f}")
    print(f"  size conditioning: COULD-NOT-LOOK (no amount field in either feed)")
    print(f"  identity-break exclusions ({len(suspects)}), each auditable:")
    for s in suspects:
        print(f"    {s['ticker']:6} {s['filing']}  AR {s['ar']:+9.2f}  "
              f"break {s['break_day']} ({s['day_factor']:.2f}x/day)")
    print(f"  exclusions: {tally}")
    print(f"  -> {OUT}")
    print(f"  -> {ev_path}")


if __name__ == "__main__":
    main()
