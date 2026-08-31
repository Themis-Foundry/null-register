"""
Q10 — Does a CLUSTER of insider open-market buying predict forward return
better than a single buy?  (registered 2026-08-08, docs/QUESTIONS.md)

Runs the registered condition EXACTLY, K=1 — no parameter shopping:
  cluster : >=3 DISTINCT insiders at one issuer filing open-market purchases
            (code P, acquired) within a trailing 10-TRADING-DAY window
  single  : exactly 1 purchase filing in the same trailing window
  outcome : stock cumulative return minus SPY, entry close t+1 after the
            filing that completes the condition, exit close t+60 after entry
            (NEXT-bar law, docs/S3_TEMPLATES.md — same-bar = auto-REJECT)
  cohort  : every row of strategies/_data/form4_purchases.jsonl, unselected

Registered direction: clusters outperform singles.

Discipline carried from the registration + LAW E2 (hand-built, since
worker.py refuses event-family batches until null generators exist):
  - survivorship is COUNTED: issuers without a bars file, and events whose
    outcome window has no bar coverage, are excluded LOUDLY, never silently
  - placebo null: N_PLACEBO re-runs with each event moved to a random
    trading date in its own ticker's bar history — same tickers, same event
    counts, no information. The real spread must sit outside that
    distribution or the timing signal is not a signal.
  - beaten-down check: the spread re-reported inside trailing-60d-return
    terciles, because insider clusters concentrate in beaten-down names and
    that is a beta story, not an edge
  - split-half repeat: 2016-2020 vs 2021-2024

Overlap rule (methods choice, applied IDENTICALLY to both buckets, stated
here rather than hidden): after an issuer fires an event in either bucket,
that issuer is ineligible for another event until 60 trading days pass —
overlapping outcome windows are not independent observations.

Output: strategies/_data/q10_insider_clusters.json (regenerable artifact)
and a printed report. The committed findings doc quotes this artifact.

    python3 q10_insider_clusters.py
"""

import json
import os

import register_emit
import random
import statistics
from collections import defaultdict
from datetime import datetime

_HERE = os.path.dirname(os.path.abspath(__file__))
_D = os.path.join(_HERE, "strategies", "_data")
FORM4 = os.path.join(_D, "form4_purchases.jsonl")
BARS = os.path.join(_D, "bars")
OUT = os.path.join(_D, "q10_insider_clusters.json")

WINDOW_TDAYS = 10          # registered
CLUSTER_MIN = 3            # registered: >=3 distinct insiders
HOLD_TDAYS = 60            # registered outcome horizon
COOLDOWN_TDAYS = 60        # methods: non-overlapping outcomes per issuer
N_PLACEBO = 40             # LAW E2 spirit: enough for an empirical p
SEED = 21001008            # Q10, registered 2026-08-08 — fixed, not tuned


def parse_date(s):
    return datetime.strptime(s, "%d-%b-%Y").date()


def load_bars(ticker):
    try:
        with open(os.path.join(BARS, f"{ticker}_ohlc.json")) as fh:
            d = json.load(fh)
    except (OSError, ValueError):
        return None
    bars = d.get("bars") or []
    if len(bars) < HOLD_TDAYS + 2:
        return None
    dates = [b[0] for b in bars]
    closes = [b[4] for b in bars]
    return {"dates": dates, "closes": closes,
            "idx": {dt: i for i, dt in enumerate(dates)}}


def next_bar_index(b, iso_date):
    """Index of the first bar STRICTLY AFTER iso_date (NEXT-bar entry)."""
    import bisect
    return bisect.bisect_right(b["dates"], iso_date)


def abnormal_return(b, spy, entry_i):
    """Stock close[entry_i] -> close[entry_i+HOLD], minus SPY over the SAME
    calendar span. None when either leg lacks coverage (counted upstream)."""
    exit_i = entry_i + HOLD_TDAYS
    if exit_i >= len(b["closes"]):
        return None
    e_date, x_date = b["dates"][entry_i], b["dates"][exit_i]
    si = spy["idx"].get(e_date)
    sx = spy["idx"].get(x_date)
    if si is None or sx is None:
        # SPY calendar mismatch: fall back to nearest SPY bars inside the span
        import bisect
        si = bisect.bisect_left(spy["dates"], e_date)
        sx = bisect.bisect_left(spy["dates"], x_date)
        if si >= len(spy["closes"]) or sx >= len(spy["closes"]) or si == sx:
            return None
    r_stock = b["closes"][exit_i] / b["closes"][entry_i] - 1.0
    r_spy = spy["closes"][sx] / spy["closes"][si] - 1.0
    return r_stock - r_spy


def trailing_return(b, entry_i, days=60):
    j = entry_i - days
    if j < 0:
        return None
    return b["closes"][entry_i] / b["closes"][j] - 1.0


def main():
    rng = random.Random(SEED)
    spy = load_bars("SPY")
    assert spy, "SPY bars missing — nothing can be market-adjusted"

    # ---- pass 1: purchases grouped per issuer ----------------------------
    per_issuer = defaultdict(list)   # ticker -> [(filing_iso, owner_cik)]
    rows = bad_rows = 0
    with open(FORM4) as fh:
        for line in fh:
            rows += 1
            try:
                r = json.loads(line)
                if r.get("code") != "P" or r.get("acq_disp") != "A":
                    continue
                t = (r.get("issuer_ticker") or "").strip().upper()
                if not t:
                    bad_rows += 1
                    continue
                per_issuer[t].append((parse_date(r["filing_date"]).isoformat(),
                                      r.get("owner_cik") or r.get("owner_name")))
            except (ValueError, KeyError):
                bad_rows += 1

    # ---- pass 2: events under the registered condition -------------------
    tally = {"issuers_total": len(per_issuer), "issuers_no_bars": 0,
             "events_no_outcome_coverage": 0, "events_mid_bucket_2insiders": 0,
             "events_cooldown_skipped": 0, "rows_total": rows,
             "rows_unparseable_or_no_ticker": bad_rows}
    events = {"cluster": [], "single": []}

    for ticker, filings in per_issuer.items():
        b = load_bars(ticker)
        if b is None:
            tally["issuers_no_bars"] += 1
            continue
        filings.sort()
        cooldown_until = -1
        for k, (fdate, owner) in enumerate(filings):
            entry_i = next_bar_index(b, fdate)
            if entry_i >= len(b["closes"]):
                tally["events_no_outcome_coverage"] += 1
                continue
            if entry_i <= cooldown_until:
                tally["events_cooldown_skipped"] += 1
                continue
            # trailing 10-TRADING-DAY window measured on this stock's calendar
            win_start_i = max(0, (entry_i - 1) - WINDOW_TDAYS + 1)
            win_start_date = b["dates"][win_start_i]
            in_win = [(d, o) for d, o in filings if win_start_date <= d <= fdate]
            distinct = len({o for _, o in in_win})
            n_filings = len(in_win)
            if distinct >= CLUSTER_MIN:
                bucket = "cluster"
            elif n_filings == 1:
                bucket = "single"
            else:
                tally["events_mid_bucket_2insiders"] += 1
                continue
            ar = abnormal_return(b, spy, entry_i)
            if ar is None:
                tally["events_no_outcome_coverage"] += 1
                continue
            tr = trailing_return(b, entry_i)
            events[bucket].append({"ticker": ticker, "filing": fdate,
                                   "entry": b["dates"][entry_i], "ar": ar,
                                   "trailing60": tr,
                                   "distinct_insiders": distinct})
            cooldown_until = entry_i + COOLDOWN_TDAYS

    cl = [e["ar"] for e in events["cluster"]]
    sg = [e["ar"] for e in events["single"]]
    spread = statistics.mean(cl) - statistics.mean(sg)

    # bootstrap CI on the spread
    boots = []
    for _ in range(2000):
        bc = [rng.choice(cl) for _ in range(len(cl))]
        bs = [rng.choice(sg) for _ in range(len(sg))]
        boots.append(statistics.mean(bc) - statistics.mean(bs))
    boots.sort()
    ci = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))])

    # ---- placebo null: same tickers, same counts, random dates -----------
    bars_cache = {}
    def cached(t):
        if t not in bars_cache:
            bars_cache[t] = load_bars(t)
        return bars_cache[t]

    placebo_spreads = []
    for _ in range(N_PLACEBO):
        means = {}
        for bucket in ("cluster", "single"):
            vals = []
            for e in events[bucket]:
                b = cached(e["ticker"])
                hi = len(b["closes"]) - HOLD_TDAYS - 1
                if hi <= 61:
                    continue
                ar = abnormal_return(b, spy, rng.randint(61, hi))
                if ar is not None:
                    vals.append(ar)
            means[bucket] = statistics.mean(vals)
        placebo_spreads.append(means["cluster"] - means["single"])
    p_emp = sum(1 for s in placebo_spreads if s >= spread) / N_PLACEBO

    # ---- beaten-down terciles (composition check) ------------------------
    both = [e for bucket in events.values() for e in bucket if e["trailing60"] is not None]
    both.sort(key=lambda e: e["trailing60"])
    cuts = [both[len(both) // 3]["trailing60"], both[2 * len(both) // 3]["trailing60"]]
    def tercile(e):
        if e["trailing60"] is None:
            return None
        return 0 if e["trailing60"] <= cuts[0] else (1 if e["trailing60"] <= cuts[1] else 2)
    terciles = {}
    for ti, label in enumerate(("beaten-down", "middle", "run-up")):
        c = [e["ar"] for e in events["cluster"] if tercile(e) == ti]
        s = [e["ar"] for e in events["single"] if tercile(e) == ti]
        terciles[label] = {"n_cluster": len(c), "n_single": len(s),
                           "spread": (statistics.mean(c) - statistics.mean(s))
                                     if c and s else None}

    # ---- split-half repeat ----------------------------------------------
    halves = {}
    for label, lo, hi in (("2016-2020", "2016", "2021"), ("2021-2024", "2021", "2025")):
        c = [e["ar"] for e in events["cluster"] if lo <= e["entry"][:4] < hi]
        s = [e["ar"] for e in events["single"] if lo <= e["entry"][:4] < hi]
        halves[label] = {"n_cluster": len(c), "n_single": len(s),
                         "spread": (statistics.mean(c) - statistics.mean(s))
                                   if c and s else None}

    out = {
        "question": "Q10", "run_on": datetime.now().date().isoformat(),
        "K_declared": 1,
        "condition": f">= {CLUSTER_MIN} distinct insiders / trailing {WINDOW_TDAYS} "
                     f"trading days; control = exactly 1 filing; entry NEXT bar "
                     f"after filing; hold {HOLD_TDAYS} tdays vs SPY; "
                     f"cooldown {COOLDOWN_TDAYS} tdays per issuer (both buckets)",
        "n_cluster": len(cl), "n_single": len(sg),
        "mean_ar_cluster": statistics.mean(cl), "median_ar_cluster": statistics.median(cl),
        "mean_ar_single": statistics.mean(sg), "median_ar_single": statistics.median(sg),
        "spread": spread, "spread_ci95_bootstrap": ci,
        "placebo": {"n_runs": N_PLACEBO, "mean": statistics.mean(placebo_spreads),
                    "max": max(placebo_spreads), "min": min(placebo_spreads),
                    "p_empirical": p_emp, "seed": SEED},
        "terciles_trailing60": terciles,
        "split_half": halves,
        "survivorship_and_exclusions": tally,
    }
    rows_ev = ([dict(e, bucket="cluster") for e in events["cluster"]] +
               [dict(e, bucket="single") for e in events["single"]])
    ev_path = register_emit.emit("Q10", rows_ev, tally)
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    print("=" * 72)
    print("  Q10 — insider CLUSTER buys vs SINGLE buys (registered 2026-08-08)")
    print("=" * 72)
    print(f"  cluster n={len(cl):>6}   mean AR {statistics.mean(cl):+.4f}   "
          f"median {statistics.median(cl):+.4f}")
    print(f"  single  n={len(sg):>6}   mean AR {statistics.mean(sg):+.4f}   "
          f"median {statistics.median(sg):+.4f}")
    print(f"  SPREAD (cluster - single): {spread:+.4f}   "
          f"bootstrap 95% CI [{ci[0]:+.4f}, {ci[1]:+.4f}]")
    print(f"  placebo null ({N_PLACEBO} runs): mean {statistics.mean(placebo_spreads):+.4f} "
          f"max {max(placebo_spreads):+.4f}  ->  empirical p = {p_emp:.3f}")
    for label, h in halves.items():
        print(f"  {label}: spread {h['spread']:+.4f} "
              f"(cluster n={h['n_cluster']}, single n={h['n_single']})")
    for label, t in terciles.items():
        sp = "n/a" if t["spread"] is None else f"{t['spread']:+.4f}"
        print(f"  trailing-60d {label:<12} spread {sp} "
              f"(c={t['n_cluster']}, s={t['n_single']})")
    print(f"  exclusions: {tally}")
    print(f"  -> {OUT}")
    print(f"  -> {ev_path}")


if __name__ == "__main__":
    main()
