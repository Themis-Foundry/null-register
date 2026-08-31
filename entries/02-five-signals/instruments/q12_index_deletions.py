"""
Q12 — Do S&P index deletions revert?  (registered 2026-08-08; runnable since
2026-08-18 when PLU-D1 delivered the membership-change corpus — the
originally-registered cohort file was a 4-ticker pilot cache,
docs/Q12_FINDINGS_2026-08-18.md)

Cohort: every `action: "removed"` row of
strategies/_data/sp500_membership_changes.jsonl (453 changes, 227 removals,
2016→today; known-answer control passed at audit). Unselected.
Condition: the deletion effective date.
Outcome: return vs SPY, entry NEXT bar after effective date, t+1..t+120.
Registered direction: deleted names underperform INTO the date and
outperform AFTER (forced selling, then relief).

THE REGISTRATION'S OWN TRAP, enforced: deletions skew distressed, so names
that vanish are OUTCOMES, never dropped —
  - no bars file at all           -> counted EXCLUDED_NO_BARS, bias stated
  - series ends inside t+1..t+120 -> DELISTED_IN_WINDOW: AR computed to the
    LAST AVAILABLE BAR and kept in the cohort (a stock that disappears
    mid-window contributed exactly what its holder got: the ride down to
    the last print). Reported both pooled and split by fate.
Reason slice (descriptive, from the corpus's verbatim reason field):
acquisitions leave the index at a premium and are not the forced-selling
story; demotions to MidCap are. Sliced, not selected on.

Shared rig: NEXT-bar entry · identity_break() over the window · placebo
null (40 runs, random dates, same tickers, same screens/truncation rule) ·
split-half · K=1.

Output: strategies/_data/q12_index_deletions.json

    python3 q12_index_deletions.py
"""

import bisect
import json
import os

import register_emit
import random
import statistics
from datetime import datetime

from q10_insider_clusters import load_bars, next_bar_index
from q8_buyback_drift import identity_break

_HERE = os.path.dirname(os.path.abspath(__file__))
_D = os.path.join(_HERE, "strategies", "_data")
CORPUS = os.path.join(_D, "sp500_membership_changes.jsonl")
OUT = os.path.join(_D, "q12_index_deletions.json")

PRE_TDAYS = 20
HOLD_TDAYS = 120
N_PLACEBO = 40
SEED = 21001208


def leg(b, spy, i0, i1):
    """Stock vs SPY between bar indices, truncating i1 to the series end.
    Returns (ar, truncated_bool) or None."""
    i1t = min(i1, len(b["closes"]) - 1)
    if i0 >= len(b["closes"]) or i1t <= i0:
        return None
    e_date, x_date = b["dates"][i0], b["dates"][i1t]
    si = bisect.bisect_left(spy["dates"], e_date)
    sx = bisect.bisect_left(spy["dates"], x_date)
    if si >= len(spy["closes"]) or sx >= len(spy["closes"]) or si == sx:
        return None
    ar = (b["closes"][i1t] / b["closes"][i0] - 1.0) - \
         (spy["closes"][sx] / spy["closes"][si] - 1.0)
    return ar, (i1t < i1)


def classify_reason(reason):
    r = (reason or "").lower()
    if "acquir" in r or "merger" in r or "purchas" in r or "bought" in r:
        return "acquisition"
    if "midcap" in r or "mid cap" in r or "smallcap" in r or "small cap" in r \
       or "market cap" in r or "representative" in r:
        return "demotion"
    return "other/unstated"


def main():
    rng = random.Random(SEED)
    spy = load_bars("SPY")
    assert spy, "SPY bars missing"

    removals = []
    for line in open(CORPUS):
        r = json.loads(line)
        if r.get("action") == "removed" and r.get("ticker") and r.get("effective_date"):
            removals.append(r)

    tally = {"removals_total": len(removals), "no_bars": 0, "no_coverage": 0,
             "identity_break_excluded": 0, "delisted_in_window": 0}
    events, suspects = [], []
    for r in removals:
        b = load_bars(r["ticker"])
        if b is None:
            tally["no_bars"] += 1
            continue
        entry_i = next_bar_index(b, r["effective_date"])
        pre = leg(b, spy, max(0, entry_i - 1 - PRE_TDAYS), entry_i - 1) \
            if entry_i - 1 - PRE_TDAYS >= 0 else None
        post = leg(b, spy, entry_i, entry_i + HOLD_TDAYS)
        if post is None:
            tally["no_coverage"] += 1
            continue
        brk = identity_break(b, entry_i, HOLD_TDAYS)
        if brk:
            suspects.append({"ticker": r["ticker"], "date": r["effective_date"],
                             "break_day": brk[0], "day_factor": brk[1]})
            tally["identity_break_excluded"] += 1
            continue
        post_ar, truncated = post
        if truncated:
            tally["delisted_in_window"] += 1
        events.append({"ticker": r["ticker"], "date": r["effective_date"],
                       "reason_class": classify_reason(r.get("reason")),
                       "pre": pre[0] if pre else None,
                       "post": post_ar, "delisted_in_window": truncated})

    post_vals = [e["post"] for e in events]
    pre_vals = [e["pre"] for e in events if e["pre"] is not None]

    def boot_ci(vals):
        bs = sorted(statistics.mean(rng.choices(vals, k=len(vals))) for _ in range(2000))
        return (bs[int(0.025 * len(bs))], bs[int(0.975 * len(bs))])

    # placebo: same tickers, random dates, identical truncation + screen rules
    cache = {}
    def cached(t):
        if t not in cache:
            cache[t] = load_bars(t)
        return cache[t]
    placebo_post = []
    for _ in range(N_PLACEBO):
        vals = []
        for e in events:
            b = cached(e["ticker"])
            hi = len(b["closes"]) - 2
            if hi <= PRE_TDAYS + 2:
                continue
            j = rng.randint(PRE_TDAYS + 2, hi)
            if identity_break(b, j, HOLD_TDAYS):
                continue
            p = leg(b, spy, j, j + HOLD_TDAYS)
            if p is not None:
                vals.append(p[0])
        placebo_post.append(statistics.mean(vals))
    p_emp = sum(1 for m in placebo_post if m >= statistics.mean(post_vals)) / N_PLACEBO

    slices = {}
    for key in ("acquisition", "demotion", "other/unstated"):
        rows = [e["post"] for e in events if e["reason_class"] == key]
        slices[key] = {"n": len(rows),
                       "post_mean": statistics.mean(rows) if rows else None}
    fate = {}
    for label, flag in (("survived_window", False), ("delisted_in_window", True)):
        rows = [e["post"] for e in events if e["delisted_in_window"] == flag]
        fate[label] = {"n": len(rows),
                       "post_mean": statistics.mean(rows) if rows else None}
    halves = {}
    for label, lo, hi in (("2016-2020", "2016", "2021"), ("2021-2026", "2021", "2027")):
        rows = [e["post"] for e in events if lo <= e["date"][:4] < hi]
        halves[label] = {"n": len(rows),
                         "post_mean": statistics.mean(rows) if rows else None}

    out = {"question": "Q12", "run_on": datetime.now().date().isoformat(),
           "K_declared": 1,
           "direction_registered": "underperform into the date, outperform after",
           "n_events": len(events),
           "pre_leg": {"n": len(pre_vals), "mean": statistics.mean(pre_vals),
                       "median": statistics.median(pre_vals), "ci95": boot_ci(pre_vals)},
           "post_leg": {"mean": statistics.mean(post_vals),
                        "median": statistics.median(post_vals), "ci95": boot_ci(post_vals)},
           "placebo": {"n_runs": N_PLACEBO, "post_mean": statistics.mean(placebo_post),
                       "p_empirical": p_emp, "seed": SEED},
           "by_reason": slices, "by_fate": fate, "split_half": halves,
           "identity_break_exclusions": suspects,
           "survivorship_and_exclusions": tally,
           "bias_note": "no_bars exclusions skew to delistings/acquisitions "
                        "closed before the bars vendor's window; their absence, "
                        "if anything, flatters the post-leg (dead names cannot "
                        "revert). Count stated; direction of bias stated."}
    rows_ev = [dict(e, bucket="scored") for e in events] + \
              [dict(s, bucket="excluded", excluded_reason="identity_break") for s in suspects]
    ev_path = register_emit.emit("Q12", rows_ev, tally)
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print("=" * 74)
    print("  Q12 — S&P 500 deletions: puke and revert? (registered 2026-08-08)")
    print("=" * 74)
    print(f"  removals {len(removals)} -> scored {len(events)} "
          f"(no_bars {tally['no_bars']}, no_coverage {tally['no_coverage']}, "
          f"identity breaks {tally['identity_break_excluded']}, "
          f"delisted-in-window kept: {tally['delisted_in_window']})")
    print(f"  INTO (t-20..t0):   mean {statistics.mean(pre_vals):+.4f}  "
          f"median {statistics.median(pre_vals):+.4f}  n={len(pre_vals)}")
    print(f"  AFTER (t+1..t+120): mean {statistics.mean(post_vals):+.4f}  "
          f"median {statistics.median(post_vals):+.4f}  CI {boot_ci(post_vals)}")
    print(f"  placebo post: {statistics.mean(placebo_post):+.4f}  p = {p_emp:.3f}")
    for k, v in slices.items():
        print(f"  reason {k:16} n={v['n']:>3}  post {v['post_mean']:+.4f}" if v["n"] else
              f"  reason {k:16} n=0")
    for k, v in fate.items():
        print(f"  fate {k:20} n={v['n']:>3}  post {v['post_mean']:+.4f}" if v["n"] else
              f"  fate {k:20} n=0")
    for k, v in halves.items():
        print(f"  {k}: n={v['n']}  post {v['post_mean']:+.4f}")
    print(f"  -> {OUT}")
    print(f"  -> {ev_path}")


if __name__ == "__main__":
    main()
