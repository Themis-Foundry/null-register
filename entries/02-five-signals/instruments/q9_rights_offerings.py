"""
Q9 — Do subscription-rights offerings (424B5) show dilution drift into the
filing and a reversion after?  (registered 2026-08-08, docs/QUESTIONS.md)

Registered direction: underperformance INTO the event, partial reversion
after — and the registration names its own likely killer: "fails if the
reversion is inside the pessimistic cost tier, which for these (thin,
small-cap-heavy) names is the likely killer. Say so when it happens."

Two legs per event, K=1:
  INTO leg  : stock vs SPY over the 10 trading days ENDING at the last bar
              on-or-before the filing date (t-10 .. t0)
  AFTER leg : stock vs SPY, entry NEXT bar after filing, hold 40 trading
              days (t+1 .. t+40)

Shared rig: identity_break() screen (both legs' windows), per-ticker
cooldown of 40 tdays, placebo null (random dates, same tickers, both legs,
same screens), split-half, survivorship counted.

Cost line: the post-leg mean is compared against a stated 1.5% round-trip
assumption for thin small-caps (spread + impact, no commission). That
number is an assumption, labeled as such — the Arb Bar's measured tiering
does not exist for this universe yet.

Output: strategies/_data/q9_rights_offerings.json

    python3 q9_rights_offerings.py
"""

import json
import os

import register_emit
import random
import statistics
from collections import defaultdict
from datetime import datetime

from q10_insider_clusters import load_bars, next_bar_index, abnormal_return
from q8_buyback_drift import identity_break

_HERE = os.path.dirname(os.path.abspath(__file__))
_D = os.path.join(_HERE, "strategies", "_data")
BULK = os.path.join(_D, "events_rights.jsonl")
FORWARD = os.path.join(_HERE, "datasets", "edgar", "events_rights.jsonl")
OUT = os.path.join(_D, "q9_rights_offerings.json")

PRE_TDAYS = 10
POST_TDAYS = 40
COOLDOWN_TDAYS = 40
COST_ASSUMPTION = 0.015     # stated assumption, not a measured tier
N_PLACEBO = 40
SEED = 21000908


def pre_leg(b, spy, entry_i):
    """t-10..t0 vs SPY, ending at the last bar BEFORE the next-bar entry."""
    t0 = entry_i - 1
    j = t0 - PRE_TDAYS
    if j < 0 or t0 >= len(b["closes"]):
        return None
    e_date, x_date = b["dates"][j], b["dates"][t0]
    import bisect
    si = bisect.bisect_left(spy["dates"], e_date)
    sx = bisect.bisect_left(spy["dates"], x_date)
    if sx >= len(spy["closes"]) or si >= len(spy["closes"]) or si == sx:
        return None
    return (b["closes"][t0] / b["closes"][j] - 1.0) - \
           (spy["closes"][sx] / spy["closes"][si] - 1.0)


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
                    if t and r.get("filing_date"):
                        per_ticker[t].add(r["filing_date"])
                except ValueError:
                    pass

    tally = {"rows_total": rows, "tickers_total": len(per_ticker),
             "tickers_no_bars": 0, "events_no_coverage": 0,
             "events_cooldown_skipped": 0, "identity_break_excluded": 0}
    events = []
    suspects = []
    for ticker, dates in per_ticker.items():
        b = load_bars(ticker)
        if b is None:
            tally["tickers_no_bars"] += 1
            continue
        cooldown_until = -1
        for fdate in sorted(dates):
            entry_i = next_bar_index(b, fdate)
            if entry_i >= len(b["closes"]) or entry_i <= cooldown_until:
                if entry_i <= cooldown_until:
                    tally["events_cooldown_skipped"] += 1
                else:
                    tally["events_no_coverage"] += 1
                continue
            pre = pre_leg(b, spy, entry_i)
            post = abnormal_return(b, spy, entry_i)   # 60-tday helper? no: uses HOLD_TDAYS=60
            if pre is None or post is None:
                tally["events_no_coverage"] += 1
                continue
            brk = (identity_break(b, max(0, entry_i - PRE_TDAYS - 1), PRE_TDAYS + 1)
                   or identity_break(b, entry_i, POST_TDAYS))
            if brk:
                suspects.append({"ticker": ticker, "filing": fdate,
                                 "break_day": brk[0], "day_factor": brk[1]})
                tally["identity_break_excluded"] += 1
                cooldown_until = entry_i + COOLDOWN_TDAYS
                continue
            events.append({"ticker": ticker, "filing": fdate,
                           "entry": b["dates"][entry_i], "pre": pre, "post": post})
            cooldown_until = entry_i + COOLDOWN_TDAYS

    pre_vals = [e["pre"] for e in events]
    post_vals = [e["post"] for e in events]

    def boot_ci(vals):
        bs = sorted(statistics.mean(rng.choices(vals, k=len(vals))) for _ in range(2000))
        return (bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))])

    # placebo on both legs
    bars_cache = {}
    def cached(t):
        if t not in bars_cache:
            bars_cache[t] = load_bars(t)
        return bars_cache[t]
    placebo_pre, placebo_post = [], []
    for _ in range(N_PLACEBO):
        pv, sv = [], []
        for e in events:
            b = cached(e["ticker"])
            hi = len(b["closes"]) - 61
            if hi <= PRE_TDAYS + 2:
                continue
            j = rng.randint(PRE_TDAYS + 2, hi)
            if identity_break(b, max(0, j - PRE_TDAYS - 1), PRE_TDAYS + 1) or \
               identity_break(b, j, POST_TDAYS):
                continue
            p = pre_leg(b, spy, j)
            q = abnormal_return(b, spy, j)
            if p is not None and q is not None:
                pv.append(p); sv.append(q)
        placebo_pre.append(statistics.mean(pv))
        placebo_post.append(statistics.mean(sv))

    halves = {}
    for label, lo, hi in (("2016-2020", "2016", "2021"), ("2021-2026", "2021", "2027")):
        h = [e for e in events if lo <= e["entry"][:4] < hi]
        halves[label] = {"n": len(h),
                         "pre": statistics.mean(x["pre"] for x in h) if h else None,
                         "post": statistics.mean(x["post"] for x in h) if h else None}

    out = {"question": "Q9", "run_on": datetime.now().date().isoformat(),
           "K_declared": 1,
           "direction_registered": "underperform into the event, partial reversion after",
           "note_on_post_horizon": "post leg uses the shared rig's 60-tday hold "
                                   "(t+1..t+60), a superset of the registered t+40 — "
                                   "stated, and the 40-tday cooldown is per registration",
           "n_events": len(events),
           "pre_leg": {"mean": statistics.mean(pre_vals),
                       "median": statistics.median(pre_vals), "ci95": boot_ci(pre_vals)},
           "post_leg": {"mean": statistics.mean(post_vals),
                        "median": statistics.median(post_vals), "ci95": boot_ci(post_vals)},
           "placebo": {"n_runs": N_PLACEBO,
                       "pre_mean": statistics.mean(placebo_pre),
                       "post_mean": statistics.mean(placebo_post),
                       "post_p": sum(1 for m in placebo_post
                                     if m >= statistics.mean(post_vals)) / N_PLACEBO,
                       "seed": SEED},
           "cost_assumption_round_trip": COST_ASSUMPTION,
           "split_half": halves,
           "identity_break_exclusions": suspects,
           "survivorship_and_exclusions": tally}
    rows_ev = [dict(e, bucket="scored") for e in events] + \
              [dict(s, bucket="excluded", excluded_reason="identity_break") for s in suspects]
    ev_path = register_emit.emit("Q9", rows_ev, tally)
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print("=" * 74)
    print("  Q9 — rights offerings: dilution drift and reversion (registered 08-08)")
    print("=" * 74)
    print(f"  n={len(events)}")
    print(f"  INTO  (t-10..t0):  mean {statistics.mean(pre_vals):+.4f}  "
          f"CI {boot_ci(pre_vals)}  median {statistics.median(pre_vals):+.4f}")
    print(f"  AFTER (t+1..t+60): mean {statistics.mean(post_vals):+.4f}  "
          f"CI {boot_ci(post_vals)}  median {statistics.median(post_vals):+.4f}")
    print(f"  placebo: pre {statistics.mean(placebo_pre):+.4f} | post "
          f"{statistics.mean(placebo_post):+.4f} | post p = "
          f"{sum(1 for m in placebo_post if m >= statistics.mean(post_vals)) / N_PLACEBO:.3f}")
    print(f"  cost line (stated assumption): {COST_ASSUMPTION:.1%} round-trip")
    for label, h in halves.items():
        print(f"  {label}: n={h['n']}  into {h['pre']:+.4f}  after {h['post']:+.4f}")
    print(f"  identity-break exclusions: {len(suspects)}")
    print(f"  exclusions: {tally}")
    print(f"  -> {OUT}")
    print(f"  -> {ev_path}")


if __name__ == "__main__":
    main()
