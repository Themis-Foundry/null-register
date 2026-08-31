#!/usr/bin/env python3
"""
Regenerate and check every number published in The Null Register, Entry 03.

    python3 verify.py     recompute every figure from the shipped rows. Offline.

Every figure on the entry page is recomputed here from data/q28s_events.jsonl,
one row per wallet present on the leaderboard in both snapshots. Board-level
counts that need the wallets who left are read from the study artifact and
labelled as such rather than dressed up as something these rows can rebuild.

The negative control at the end corrupts the data four ways and requires every
check to notice. The control is also the entry's whole argument, so it would be
absurd to ship without one: if a checker cannot be made to say no, it is not
checking anything.
"""

import json
import pathlib
import statistics
import sys

DATA = pathlib.Path(__file__).parent / "data"
GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = OFF = ""
fails = []


def rows(_c={}):
    if not _c:
        allr = [json.loads(l) for l in open(DATA / "q28s_events.jsonl")]
        _c["man"] = [r for r in allr if r.get("_manifest")][0]
        _c["rows"] = [r for r in allr if not r.get("_manifest")]
    return list(_c["rows"])


def manifest(_c={}):
    rows()
    return json.loads(open(DATA / "q28s_events.jsonl").read().splitlines()[-1])


def summary():
    return json.load(open(DATA / "summaries" / "q28_board_size_control.json"))


def check(label, got, want, silent=False):
    ok = got == want
    if not silent:
        print(f"  {GREEN + 'PASS' + OFF if ok else RED + 'FAIL' + OFF}  "
              f"{label:<44} {str(got):>10}   published {want}")
    if not ok:
        fails.append(f"{label}: got {got}, published {want}")
    return ok


def pct(x, dp=1):
    return round(x * 100, dp)


def _ranks(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    rk = [0.0] * len(v)
    i = 0
    while i < len(o):
        j = i
        while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            rk[o[k]] = (i + j) / 2 + 1
        i = j + 1
    return rk


def pearson(x, y):
    mx, my = statistics.mean(x), statistics.mean(y)
    dx = sum((a - mx) ** 2 for a in x) ** 0.5
    dy = sum((b - my) ** 2 for b in y) ** 0.5
    return 0.0 if dx == 0 or dy == 0 else \
        sum((a - mx) * (b - my) for a, b in zip(x, y)) / (dx * dy)


def spearman(x, y):
    return pearson(_ranks(x), _ranks(y))


def the_board(rs=None):
    print(f"\nWHAT IS ON THE BOARD {DIM}(wallets present in both snapshots){OFF}")
    rs = rs if rs is not None else rows()
    check("wallets tracked across both", len(rs), 42850)
    check("addresses unique", len({r['addr'] for r in rs}), 42850)
    idle = [r for r in rs if r["month_vlm_early"] == 0]
    check("did not trade at all that month", len(idle), 26511)
    check("  as a share of the board, %", pct(len(idle) / len(rs)), 61.9)
    at = [r["alltime_pnl_early"] for r in rs]
    check("all-time profitable, %", pct(sum(1 for x in at if x > 0) / len(at)), 49.5)
    check("all-time above $100k", sum(1 for x in at if x > 100_000), 10050)
    print(f"  {DIM}a leaderboard of 43,000 traders is mostly not traders{OFF}")


def the_control(rs=None):
    print(f"\nTHE CONTROL {DIM}(does the ranking rank skill, or account size?){OFF}")
    rs = rs if rs is not None else rows()
    nxt = [r["week_pnl_late"] for r in rs]
    check("baseline: profitable next period, %",
          pct(sum(1 for v in nxt if v > 0) / len(rs)), 52.8)
    n10 = len(rs) // 10
    for label, key, want_pos, want_acct in (
            ("ranked by last week's dollars", lambda r: -r["week_pnl_early"], 88.6, 870640),
            ("ranked by last week's percent", lambda r: -r["week_roi_early"], 64.5, 108008),
            ("ranked by ACCOUNT SIZE only", lambda r: -r["acct_usd_early"], 83.8, 1201082)):
        top = sorted(rs, key=key)[:n10]
        nx = [r["week_pnl_late"] for r in top]
        check(f"  {label}, %", pct(sum(1 for v in nx if v > 0) / len(top)), want_pos)
        check(f"    median account, $",
              round(statistics.median([r["acct_usd_early"] for r in top])), want_acct)
    if rs is rows() or len(rs) == 42850:
        d = {r["addr"] for r in rs if r["in_top_decile_by_dollars"]}
        s = {r["addr"] for r in rs if r["in_top_decile_by_account_size"]}
        check("overlap, best-week vs biggest-account, %",
              pct(len(d & s) / len(d)) if d else 0.0, 72.9)
    print(f"  {DIM}a sort that cannot know anything reproduces 83.8 of the 88.6, so "
          f"almost the whole effect is size{OFF}")


def one_question_eight_answers(rs=None):
    print(f"\nONE QUESTION, EIGHT ANSWERS {DIM}(identical wallets, defensible methods){OFF}")
    rs = rs if rs is not None else rows()
    PUB = {("dollars", "ranked"): (0.831, -0.511), ("dollars", "raw"): (0.699, -0.885),
           ("percent", "ranked"): (0.81, -0.523), ("percent", "raw"): (-0.0, -0.002)}
    for unit, wk, mo in (("dollars", "week_pnl_early", "month_pnl_early"),
                         ("percent", "week_roi_early", "month_roi_early")):
        w = [r[wk] for r in rs]
        # month ROI is a shipped field. An earlier draft derived it as
        # month_pnl/account when the field was missing, which is a DIFFERENT
        # quantity and disagreed by 0.06-0.19 on every percent row. A fallback
        # that silently computes something else is worse than a missing column.
        m = [r[mo] for r in rs]
        prior = [a - b for a, b in zip(m, w)]
        for stat, fn in (("ranked", spearman), ("raw", pearson)):
            wn, ws = PUB[(unit, stat)]
            check(f"  {unit}, {stat}: nested", round(fn(m, w), 3), wn)
            check(f"  {unit}, {stat}: subtracted", round(fn(prior, w), 3), ws)
    print(f"  {DIM}the sign of the answer is a property of the method, not of the traders{OFF}")


def from_the_artifact():
    print(f"\nREAD FROM THE STUDY ARTIFACT {DIM}(needs the wallets who left, which the "
          f"rows do not carry){OFF}")
    s = summary()
    check("full board, rows in the early snapshot", s["board"]["rows"], 43141)
    check("full board, unique addresses", s["board"]["unique_addresses"], 43141)
    check("left the board in 9 days", s["churn_9d"]["left"], 291)
    check("new to the board in 9 days", s["churn_9d"]["new"], 1531)
    check("leavers who were profitable, %", s["churn_9d"]["leavers_pct_profitable"], 75.6)
    check("stayers who were profitable, %", s["churn_9d"]["stayers_pct_profitable"], 49.5)
    print(f"  {DIM}the ones who left were far more profitable than the ones who stayed, "
          f"which is a survivorship channel sitting above everything here{OFF}")


def negative_control():
    print(f"\nNEGATIVE CONTROL {DIM}— the checker must be able to say no{OFF}")
    global fails
    # ⚠ A CONTROL MUST BE SCALED TO THE CLAIM IT GUARDS. The first version of
    # these probes corrupted exactly one row. At n=42,850 that moves a median
    # over 4,285 rows by nothing and a percentage by 0.002 points, which is
    # below the precision every figure here is published at, so two of the four
    # probes were silently ACCEPTED and the suite reported a pass it had not
    # earned. One-row corruption is the right size for a 119-row census and the
    # wrong size for this one. These corrupt a percent of the board, which is
    # still far smaller than any real error worth catching.
    def poison(rs, n, **fields):
        k = max(1, len(rs) * n // 100)
        return [dict(r, **fields) for r in rs[:k]] + rs[k:]

    probes = [
        ("1% of account sizes zeroed",
         lambda rs: poison(rs, 1, acct_usd_early=1.0), the_control),
        ("one row dropped", lambda rs: rs[1:], the_board),
        ("5% of next-period results flipped negative",
         lambda rs: poison(rs, 5, week_pnl_late=-1.0), the_control),
        ("1% of month figures altered",
         lambda rs: poison(rs, 1, month_pnl_early=1e9), one_question_eight_answers),
    ]
    ok_all = True
    for label, corrupt, fn in probes:
        before, fails = list(fails), []
        buf, sys.stdout = sys.stdout, open("/dev/null", "w")
        try:
            fn(corrupt(rows()))
        except Exception:
            fails.append("raised")
        finally:
            sys.stdout.close()
            sys.stdout = buf
        bit = bool(fails)
        fails = before
        print(f"  {GREEN + 'PASS' + OFF if bit else RED + 'FAIL' + OFF}  {label:<44} "
              f"{'rejected' if bit else 'ACCEPTED — the check is blind'}")
        if not bit:
            fails.append(f"negative control did not fire: {label}")
            ok_all = False
    if ok_all:
        print(f"  {DIM}every corruption was caught, so the passes above mean something{OFF}")


def main():
    print(f"\n{'=' * 74}\n  THE NULL REGISTER — Entry 03, the leaderboard ranks account size"
          f"\n{'=' * 74}")
    the_board(); the_control(); one_question_eight_answers(); from_the_artifact()
    negative_control()
    print()
    if fails:
        print(f"{RED}{len(fails)} FAILURE(S){OFF}")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"{GREEN}All checks passed.{OFF}  Everything above the artifact section was "
          f"recomputed from the shipped rows.")


if __name__ == "__main__":
    main()
