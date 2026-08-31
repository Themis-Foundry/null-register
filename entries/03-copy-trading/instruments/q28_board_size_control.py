"""
Q28 side-study — does the copy-trade leaderboard rank SKILL, or account size?

Registered Q28 asks whether leaderboard position persists. Its honest read is
2026-09-20 at +30 days. This is NOT that test and does not answer it: three
snapshots exist (2026-08-21, 08-23, 08-30), so a NINE-day read is possible now,
and the nine-day read turns out to be interesting for a reason that has nothing
to do with persistence.

THE CONTROL IS THE POINT. Rank wallets by last week's dollar PnL and the top
decile is 88.6% profitable in the following period against a 52.8% base rate,
which reads as strong persistence. Then rank by ACCOUNT SIZE — a quantity
containing no performance information whatsoever — and the same test gives
83.8%. A ranking that cannot possibly know anything reproduces almost the whole
effect, so almost the whole effect is size.

Also measured, because the number a reader is given should not depend on which
defensible method the analyst happened to pick: the same "does last period
predict this one" question, on one snapshot, answered eight ways.

Output: strategies/_data/q28_board_size_control.json + per-wallet rows via
register_emit. Reads only the gzipped snapshots collected on Helios.

    python3 q28_board_size_control.py
"""

import gzip
import json
import os
import statistics

import register_emit

_D = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategies", "_data")
SNAPS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", "copytrade")
OUT = os.path.join(_D, "q28_board_size_control.json")
EARLY, LATE = "2026-08-21", "2026-08-30"


def load(day):
    p = os.path.join(SNAPS, f"hl_leaderboard_{day}.json.gz")
    with gzip.open(p) as fh:
        d = json.load(fh)
    return d, {r["addr"]: r for r in d["rows"]}


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    dx = sum((a - mx) ** 2 for a in x) ** 0.5
    dy = sum((b - my) ** 2 for b in y) ** 0.5
    if dx == 0 or dy == 0:
        return 0.0
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / (dx * dy)


def spearman(x, y):
    return pearson(ranks(x), ranks(y))


def main():
    meta_e, early = load(EARLY)
    meta_l, late = load(LATE)
    common = sorted(set(early) & set(late))
    gone = set(early) - set(late)
    fresh = set(late) - set(early)

    def g(d, a, w, k):
        return float(d[a]["perf"][w][k])

    # ── the eight defensible answers to one question, on the early snapshot ──
    rows_e = list(early.values())
    def col(w, k):
        return [float(r["perf"][w][k]) for r in rows_e]
    methods = {}
    for unit, k in (("dollars", "pnl"), ("percent", "roi")):
        w, m = col("week", k), col("month", k)
        prior = [x - y for x, y in zip(m, w)]
        for stat, fn in (("ranked", spearman), ("raw", pearson)):
            methods[f"{unit}, {stat}"] = {"nested_month_vs_week": round(fn(m, w), 3),
                                          "subtracted_prior_vs_week": round(fn(prior, w), 3)}

    # ── the control: three sorts, one of which cannot know anything ──
    def decile(keyfn):
        top = sorted(common, key=keyfn)[:len(common) // 10]
        nxt = [g(late, a, "week", "pnl") for a in top]
        roi = [g(late, a, "week", "roi") for a in top]
        return {"n": len(top),
                "pct_positive_next": round(sum(1 for v in nxt if v > 0) / len(top) * 100, 1),
                "median_roi_next_pct": round(statistics.median(roi) * 100, 2),
                "median_account_usd": round(statistics.median(
                    [float(early[a]["acct"]) for a in top]), 2)}

    base_n = [g(late, a, "week", "pnl") for a in common]
    base_r = [g(late, a, "week", "roi") for a in common]
    sorts = {
        "by_dollar_pnl_last_week": decile(lambda a: -g(early, a, "week", "pnl")),
        "by_percent_roi_last_week": decile(lambda a: -g(early, a, "week", "roi")),
        "by_account_size_ONLY": decile(lambda a: -float(early[a]["acct"])),
    }
    baseline = {"n": len(common),
                "pct_positive_next": round(sum(1 for v in base_n if v > 0) / len(common) * 100, 1),
                "median_roi_next_pct": round(statistics.median(base_r) * 100, 2),
                "median_account_usd": round(statistics.median(
                    [float(early[a]["acct"]) for a in common]), 2)}

    top_d = set(sorted(common, key=lambda a: -g(early, a, "week", "pnl"))[:len(common) // 10])
    top_s = set(sorted(common, key=lambda a: -float(early[a]["acct"]))[:len(common) // 10])

    at = [float(r["perf"]["allTime"]["pnl"]) for r in rows_e]
    idle = sum(1 for r in rows_e if float(r["perf"]["month"]["vlm"]) == 0)

    out = {
        "question": "Q28-side", "run_on": __import__("datetime").date.today().isoformat(),
        "NOT_the_registered_test": "Q28 registered a +30d read, first honest on 2026-09-20. "
                                   "This is a 9-day read across two snapshots and answers a "
                                   "different question: what does the ranking actually rank?",
        "snapshots": {"early": {"day": EARLY, "fetched_at": meta_e.get("fetched_at"),
                                "rows": len(early)},
                      "late": {"day": LATE, "fetched_at": meta_l.get("fetched_at"),
                               "rows": len(late)}},
        "board": {"rows": len(rows_e), "unique_addresses": len({r["addr"] for r in rows_e}),
                  "alltime_positive": sum(1 for x in at if x > 0),
                  "alltime_negative": sum(1 for x in at if x < 0),
                  "above_100k": sum(1 for x in at if x > 100_000),
                  "no_volume_that_month": idle},
        "churn_9d": {"survived": len(common), "left": len(gone), "new": len(fresh),
                     "leavers_pct_profitable": round(sum(
                         1 for a in gone if float(early[a]["perf"]["allTime"]["pnl"]) > 0)
                         / len(gone) * 100, 1) if gone else None,
                     "stayers_pct_profitable": round(sum(
                         1 for a in common if float(early[a]["perf"]["allTime"]["pnl"]) > 0)
                         / len(common) * 100, 1)},
        "one_question_eight_answers": methods,
        "baseline_next_period": baseline,
        "decile_sorts": sorts,
        "size_overlap_pct": round(len(top_d & top_s) / len(top_d) * 100, 1),
    }
    with open(OUT, "w") as fh:
        json.dump(out, fh, indent=2)

    ev = []
    for a in common:
        # ⚠ NOT ROUNDED, and that is deliberate. The first version rounded PnL to
        # two decimals, which turned thousands of tiny positive results into
        # exactly 0.0 and moved the published base rate by 2.4 points. A row is
        # evidence; rounding it is editing it. The verifier caught this.
        ev.append({"addr": a,
                   "acct_usd_early": float(early[a]["acct"]),
                   "week_pnl_early": g(early, a, "week", "pnl"),
                   "week_roi_early": g(early, a, "week", "roi"),
                   "month_pnl_early": g(early, a, "month", "pnl"),
                   "month_roi_early": g(early, a, "month", "roi"),
                   "month_vlm_early": g(early, a, "month", "vlm"),
                   "alltime_pnl_early": g(early, a, "allTime", "pnl"),
                   "week_pnl_late": g(late, a, "week", "pnl"),
                   "week_roi_late": g(late, a, "week", "roi"),
                   "in_top_decile_by_dollars": a in top_d,
                   "in_top_decile_by_account_size": a in top_s})
    p = register_emit.emit("Q28S", ev, {"survived_both_snapshots": len(common),
                                        "left_the_board": len(gone),
                                        "new_to_the_board": len(fresh),
                                        "early_rows": len(early), "late_rows": len(late)})

    print("=" * 74)
    print("  Q28 side-study — what does the leaderboard actually rank?")
    print("=" * 74)
    print(f"  board {len(rows_e):,} wallets, {idle:,} with no volume that month")
    print(f"  baseline next period: {baseline['pct_positive_next']}% positive\n")
    for k, v in sorts.items():
        print(f"  {k:32s} {v['pct_positive_next']:5.1f}% positive   "
              f"median acct ${v['median_account_usd']:>13,.0f}")
    print(f"\n  overlap, best-dollar-week vs biggest-account: {out['size_overlap_pct']}%")
    print("\n  one question, eight answers:")
    for k, v in methods.items():
        print(f"    {k:18s} nested {v['nested_month_vs_week']:+.3f}   "
              f"subtracted {v['subtracted_prior_vs_week']:+.3f}")
    print(f"\n  -> {OUT}\n  -> {p}")


if __name__ == "__main__":
    main()
