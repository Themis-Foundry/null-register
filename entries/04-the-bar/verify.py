#!/usr/bin/env python3
"""
Regenerate and check every number published in The Null Register, Entry 04.

    python3 verify.py      recompute every published figure from the shipped rows.
                           Offline, no key, instant.

Every figure on the page is rebuilt from data/batches/<batch>/results.jsonl and
manifest.json. The batch runner's own verdict.md files are shipped as the record of
what it said at the time, but nothing here trusts them: one of their counts is wrong
(see the page), and a checker that reads the report instead of the rows would have
passed it.

Grading is strict, the way the manifests say it should be: a null counts only if it
finished, and only if its trade count reached the batch's declared minimum. Rows that
crashed or came up thin are shipped and are not graded.

A negative control runs at the end. It corrupts the rows on purpose and requires every
check to go red. If the checker cannot be made to fail, it is not checking anything,
and this script exits non-zero rather than reporting a pass it has not earned.
"""

import json
import pathlib
import statistics
import sys

DATA = pathlib.Path(__file__).parent / "data" / "batches"
LEAD = "league-check-momentum"
BATCHES = ["league-check-momentum", "pilot-q16-momentum", "q16-momentum-deep",
           "q16-mean-reversion", "q16-mean-reversion-deep"]

GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = OFF = ""

fails = []


def load(batch, _cache={}):
    if batch not in _cache:
        rows = [json.loads(l) for l in open(DATA / batch / "results.jsonl") if l.strip()]
        man = json.load(open(DATA / batch / "manifest.json"))
        _cache[batch] = (rows, man)
    rows, man = _cache[batch]
    return [dict(r) for r in rows], dict(man)


def graded_nulls(rows, man):
    return [r for r in rows if r.get("kind") == "null" and "expectancy_R" in r
            and r.get("n", 0) >= man["required_n"]]


def graded_reals(rows, man):
    return [r for r in rows if r.get("kind") == "real" and "expectancy_R" in r
            and r.get("n", 0) >= man["required_n"]]


def check(label, got, want):
    ok = got == want
    mark = f"{GREEN}PASS{OFF}" if ok else f"{RED}FAIL{OFF}"
    print(f"  {mark}  {label:<52} {str(got):>12}   published {want}")
    if not ok:
        fails.append(f"{label}: got {got}, published {want}")
    return ok


# ── the lead batch, exactly as the page states it ────────────────────────────

def lead(rows=None, man=None):
    if rows is None:
        rows, man = load(LEAD)
    bar = man["promote_bar_R"]
    nulls = graded_nulls(rows, man)
    e = [r["expectancy_R"] for r in nulls]
    real = [r for r in rows if r["kind"] == "real"]
    print(f"\nTHE LEAD BATCH {DIM}({LEAD}, seed {man['seed']}, "
          f"null generator {man['null_generator']}){OFF}")
    check("declared: real candidates (K)", man["K"], 1)
    check("declared: nulls", man["n_nulls"], 40)
    check("declared: promotion bar, R", bar, 0.07)
    check("signal-free strategies graded", len(nulls), 40)
    check("cleared the bar", sum(1 for x in e if x >= bar), 39)
    check("cleared the bar, %", round(100 * sum(1 for x in e if x >= bar) / len(e)), 98)
    check("their mean profit per trade, R", round(statistics.mean(e), 3), 0.169)
    check("their best, R", round(max(e), 3), 0.304)
    check("the real strategy, R", round(real[0]["expectancy_R"], 3), 0.196)
    check("the real strategy, trades", real[0]["n"], 627)
    check("the real strategy's verdict", real[0]["verdict"], "PROMOTE")
    check("signal-free strategies that beat the real one",
          sum(1 for x in e if x >= real[0]["expectancy_R"]), 12)
    check("signal-free strategies the grader marked PROMOTE",
          sum(1 for r in nulls if r.get("verdict") == "PROMOTE"), 11)
    check("real strategies clearing the empirical bar (best null)",
          sum(1 for r in graded_reals(rows, man) if r["expectancy_R"] >= max(e)), 0)


# ── the five batches ─────────────────────────────────────────────────────────

PUBLISHED = {
    "league-check-momentum":   ("momentum",       40,  39,  11),
    "pilot-q16-momentum":      ("momentum",       17,  12,  13),
    "q16-momentum-deep":       ("momentum",      258, 102, 154),
    "q16-mean-reversion":      ("mean_reversion",  6,   0,   0),
    "q16-mean-reversion-deep": ("mean_reversion", 150,  0,   9),
}


def five(loader=load):
    print(f"\nTHE FIVE BATCHES {DIM}(strict grading: finished, and at or above the "
          f"declared minimum trade count){OFF}")
    tot_g = tot_c = tot_p = reals = promoted = beat = 0
    fam = {"momentum": [0, 0], "mean_reversion": [0, 0]}
    for b in BATCHES:
        rows, man = loader(b)
        family, g_pub, c_pub, p_pub = PUBLISHED[b]
        nulls = graded_nulls(rows, man)
        e = [r["expectancy_R"] for r in nulls]
        c = sum(1 for x in e if x >= man["promote_bar_R"])
        p = sum(1 for r in nulls if r.get("verdict") == "PROMOTE")
        check(f"{b}: family", man["family"], family)
        check(f"{b}: graded", len(nulls), g_pub)
        check(f"{b}: cleared", c, c_pub)
        check(f"{b}: grader PROMOTE", p, p_pub)
        tot_g += len(nulls); tot_c += c; tot_p += p
        fam[man["family"]][0] += len(nulls); fam[man["family"]][1] += c
        rr = [r for r in rows if r["kind"] == "real"]
        reals += len(rr)  # every real candidate declared, including the one that crashed
        promoted += sum(1 for r in rr if r.get("verdict") == "PROMOTE")
        beat += sum(1 for r in graded_reals(rows, man) if r["expectancy_R"] >= max(e))
    check("all five: graded", tot_g, 471)
    check("all five: cleared", tot_c, 153)
    check("all five: cleared, %", round(100 * tot_c / tot_g), 32)
    check("all five: grader PROMOTE", tot_p, 187)
    check("momentum: graded / cleared", tuple(fam["momentum"]), (315, 153))
    check("mean reversion: graded / cleared", tuple(fam["mean_reversion"]), (156, 0))
    check("real candidates run", reals, 24)
    check("real candidates the league had promoted", promoted, 13)
    check("real candidates clearing their batch's best null", beat, 1)
    rows, man = loader("q16-mean-reversion")
    best = max(r["expectancy_R"] for r in graded_nulls(rows, man))
    winner = [r for r in graded_reals(rows, man) if r["expectancy_R"] >= best]
    check("the one that did: batch, R, trades, verdict",
          (len(winner), round(winner[0]["expectancy_R"], 3) if winner else None,
           winner[0]["n"] if winner else None, winner[0].get("verdict") if winner else None),
          (1, 0.036, 148, "WATCH"))
    check("the one that did: below the bar anyway", bool(winner) and winner[0]["expectancy_R"] < man["promote_bar_R"], True)
    rows, man = loader("q16-mean-reversion-deep")
    check("q16-mean-reversion-deep: rows that errored",
          sum(1 for r in rows if "error" in r), 151)
    check("q16-mean-reversion-deep: rows shipped", len(rows), 302)
    mr = [r["expectancy_R"] for r in graded_nulls(*loader("q16-mean-reversion-deep"))]
    check("mean reversion deep: null mean near zero (R, 2dp)", round(statistics.mean(mr), 2), 0.03)


def the_report_was_wrong():
    """The batch runner's own verdict.md for q16-mean-reversion says 8 of 30. The rows
    say 0 of 6 once the thin ones are excluded, as the manifest requires."""
    print(f"\nTHE REPORT THAT WAS WRONG {DIM}(left as written; the rows outrank it){OFF}")
    text = open(DATA / "q16-mean-reversion" / "verdict.md").read()
    check("verdict.md still claims 8/30", "**8/30 (27%)**" in text, True)
    rows, man = load("q16-mean-reversion")
    thin = [r for r in rows if r.get("kind") == "null" and "expectancy_R" in r
            and r.get("n", 0) < man["required_n"]]
    check("nulls below the declared minimum trade count", len(thin), 24)
    check("of those, clearing the bar (the 8 the report counted)",
          sum(1 for r in thin if r["expectancy_R"] >= man["promote_bar_R"]), 8)


# ── the checker must be able to say no ───────────────────────────────────────

def negative_control():
    print(f"\nNEGATIVE CONTROL {DIM}— the checker must be able to say no{OFF}")
    global fails

    def corrupt_flip(rows, man):
        # push the one null that missed the bar over it: 39 becomes 40
        for r in rows:
            if r.get("kind") == "null" and "expectancy_R" in r and r["expectancy_R"] < 0.07:
                r["expectancy_R"] = 0.08
        return rows, man

    def corrupt_drop(rows, man):
        idx = next(i for i, r in enumerate(rows) if r.get("kind") == "null" and "expectancy_R" in r)
        return rows[:idx] + rows[idx + 1:], man

    def corrupt_real(rows, man):
        for r in rows:
            if r.get("kind") == "real":
                r["expectancy_R"] = 0.4  # now beats every null
        return rows, man

    probes = [
        ("the one failing null nudged over the bar", corrupt_flip, lead),
        ("one null row dropped", corrupt_drop, lead),
        ("the real strategy inflated past the best null", corrupt_real, lead),
    ]
    all_bit = True
    for label, corrupt, fn in probes:
        before = list(fails)
        fails = []
        buf, sys.stdout = sys.stdout, open("/dev/null", "w")
        try:
            rows, man = load(LEAD)
            fn(*corrupt(rows, man))
        finally:
            sys.stdout.close()
            sys.stdout = buf
        bit = bool(fails)
        fails = before
        print(f"  {(GREEN + 'PASS' + OFF) if bit else (RED + 'FAIL' + OFF)}  "
              f"{label:<52} {'rejected' if bit else 'ACCEPTED — the check is blind'}")
        if not bit:
            fails.append(f"negative control did not fire: {label}")
            all_bit = False
    # a fourth probe on the five-batch pass: swap a family label
    before = list(fails)
    fails = []
    buf, sys.stdout = sys.stdout, open("/dev/null", "w")
    try:
        def swapped(b):
            rows, man = load(b)
            if b == "q16-mean-reversion-deep":
                man["family"] = "momentum"
            return rows, man
        five(loader=swapped)
    finally:
        sys.stdout.close()
        sys.stdout = buf
    bit = bool(fails)
    fails = before
    print(f"  {(GREEN + 'PASS' + OFF) if bit else (RED + 'FAIL' + OFF)}  "
          f"{'one batch relabelled to the other family':<52} {'rejected' if bit else 'ACCEPTED — the check is blind'}")
    if not bit:
        fails.append("negative control did not fire: family relabel")
        all_bit = False
    if all_bit:
        print(f"  {DIM}every corruption was caught, so the passes above mean something{OFF}")


def main():
    print(f"\n{'=' * 72}\n  THE NULL REGISTER — Entry 04, the bar that random strategies cleared"
          f"\n{'=' * 72}")
    lead()
    five()
    the_report_was_wrong()
    negative_control()
    print()
    if fails:
        print(f"{RED}{len(fails)} FAILURE(S){OFF}")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"{GREEN}All checks passed.{OFF}  Every figure on the page was rebuilt from the rows.")


if __name__ == "__main__":
    main()
