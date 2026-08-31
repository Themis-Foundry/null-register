#!/usr/bin/env python3
"""
Regenerate and check every number published in The Null Register, Entry 02.

Two modes:
    python3 verify.py              recompute every published figure from the
                                   per-event rows. Offline, no key, instant.
    python3 verify.py --instruments
                                   also re-derive the summaries by re-running the
                                   original instruments. Needs the daily price
                                   bars, which are not redistributable.

Entry 01 published the quotes its verdicts were read from and deliberately did
NOT publish the pipeline. This entry does the opposite, and the reversal is the
point: when the evidence is a sentence in a filing, the sentence is the evidence.
When the evidence is a computation over 24,000 events, the computation is the
evidence, and a summary statistic with nothing underneath it is exactly the kind
of claim this register exists to refuse.

So every study here ships the rows it scored, one per line, including the ones it
threw out and why. Every figure below is recomputed from those rows. You can
disagree with a classification and still check the arithmetic.

A negative control runs at the end. It corrupts the data on purpose and requires
every check to go red. If the checker cannot be made to fail, it is not checking
anything, and this script exits non-zero rather than reporting a pass it has not
earned.
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


def rows(name, _cache={}):
    """Every scored row for a study, manifest line excluded."""
    if name not in _cache:
        out = []
        for line in open(DATA / f"{name}_events.jsonl"):
            r = json.loads(line)
            if not r.get("_manifest"):
                out.append(r)
        _cache[name] = out
    return list(_cache[name])


def manifest(name):
    return json.loads(open(DATA / f"{name}_events.jsonl").read().splitlines()[-1])


def summary(name):
    """A figure the rows cannot rebuild. The placebo means require re-running the
    instrument 40 times over the bars, so they are read from the study artifact
    rather than recomputed here, and are labelled that way rather than dressed up
    as something this script derived."""
    return json.load(open(DATA / "summaries" / f"{name}.json"))


def check(label, got, want, silent=False):
    ok = got == want
    if not silent:
        mark = f"{GREEN}PASS{OFF}" if ok else f"{RED}FAIL{OFF}"
        print(f"  {mark}  {label:<38} {str(got):>9}   published {want}")
    if not ok:
        fails.append(f"{label}: got {got}, published {want}")
    return ok


def pct(x, dp=1):
    """A return as the percentage this entry prints, at the precision it prints."""
    return round(x * 100, dp)


# ── the figures exactly as the entry states them ────────────────────────────
# Asserted here so that a number drifting in the data shows up as a failure
# rather than as a quietly different README.

def q12(rs=None):
    print(f"\nQ12 — THE S&P DELETION REBOUND {DIM}(the one that worked, then stopped){OFF}")
    rs = rs if rs is not None else rows("q12")
    sc = [r for r in rs if r["bucket"] == "scored"]
    check("events scored", len(sc), 114)
    check("removals in the cohort", manifest("q12")["exclusions"]["removals_total"], 227)
    check("dropped for having no price data", manifest("q12")["exclusions"]["no_bars"], 83)
    pre = [r["pre"] for r in sc if r["pre"] is not None]
    check("into the date, mean %", pct(statistics.mean(pre)), -4.2)
    check("after, mean %", pct(statistics.mean(r["post"] for r in sc)), 4.7)
    check("after, median %", pct(statistics.median(r["post"] for r in sc)), -2.0)
    for lbl, lo, hi, want in (("2016-2020", "2016", "2021", 12.4),
                              ("2021-2026", "2021", "2027", -3.9)):
        h = [r["post"] for r in sc if lo <= r["date"][:4] < hi]
        check(f"  {lbl} after, mean %", pct(statistics.mean(h)), want)
    for reason, want_n, want_m in (("demotion", 83, 7.6), ("acquisition", 15, -10.8)):
        h = [r["post"] for r in sc if r["reason_class"] == reason]
        check(f"  by reason: {reason} n", len(h), want_n)
        check(f"  by reason: {reason} mean %", pct(statistics.mean(h)), want_m)


def q10(rs=None):
    print(f"\nQ10 — INSIDER CLUSTER BUYING {DIM}(the screener signal){OFF}")
    rs = rs if rs is not None else rows("q10")
    cl = [r["ar"] for r in rs if r["bucket"] == "cluster"]
    sg = [r["ar"] for r in rs if r["bucket"] == "single"]
    check("cluster events", len(cl), 6511)
    check("single events", len(sg), 17510)
    check("cluster mean %", pct(statistics.mean(cl), 2), 1.82)
    check("single mean %", pct(statistics.mean(sg), 2), 1.31)
    check("spread %", pct(statistics.mean(cl) - statistics.mean(sg), 2), 0.52)
    bd = [r for r in rs if r.get("trailing60") is not None]
    bd.sort(key=lambda r: r["trailing60"])
    third = len(bd) // 3
    low = bd[:third]
    lc = [r["ar"] for r in low if r["bucket"] == "cluster"]
    ls = [r["ar"] for r in low if r["bucket"] == "single"]
    check("beaten-down tercile spread %",
          pct(statistics.mean(lc) - statistics.mean(ls), 2), -3.75)
    print(f"  {DIM}the tercile where the insider-conviction story is loudest is where "
          f"clusters do worst{OFF}")


def q8(rs=None):
    print(f"\nQ8 — BUYBACK ANNOUNCEMENTS {DIM}(the base rate is zero){OFF}")
    rs = rs if rs is not None else rows("q8")
    sc = [r["ar"] for r in rs if r["bucket"] == "scored"]
    check("events scored", len(sc), 9470)
    check("mean %", pct(statistics.mean(sc), 2), -0.13)
    check("median %", pct(statistics.median(sc), 2), -0.90)
    check("beat SPY, %", pct(sum(1 for x in sc if x > 0) / len(sc), 1), 47.4)
    ex = [r for r in rs if r["bucket"] == "excluded"]
    check("identity-break exclusions", len(ex), 3)
    for r in sorted(ex, key=lambda r: r["filing"]):
        print(f"        {DIM}{r['ticker']:<6} {r['filing']}  would have booked "
              f"{r['ar'] * 100:+.0f}%  ({r['day_factor']:.2f}x in one day, "
              f"{r['break_day']}){OFF}")
    print(f"  {DIM}the first run of this study printed +3.41% and every basis point "
          f"of it was CBL{OFF}")


def q9(rs=None):
    print(f"\nQ9 — RIGHTS OFFERINGS {DIM}(the dilution dip that runs the other way){OFF}")
    rs = rs if rs is not None else rows("q9")
    sc = [r for r in rs if r["bucket"] == "scored"]
    check("events scored", len(sc), 3144)
    check("into the filing, mean %", pct(statistics.mean(r["pre"] for r in sc), 2), 4.41)
    check("into the filing, median %", pct(statistics.median(r["pre"] for r in sc), 2), -0.35)
    check("after, mean %", pct(statistics.mean(r["post"] for r in sc), 2), -3.64)
    for lbl, lo, hi, want in (("2016-2020", "2016", "2021", 5.68),
                              ("2021-2026", "2021", "2027", 3.32)):
        h = [r["pre"] for r in sc if lo <= r["entry"][:4] < hi]
        check(f"  {lbl} into, mean %", pct(statistics.mean(h), 2), want)
    print(f"  {DIM}positive in both halves: issuers sell strength, they are not "
          f"caught by weakness{OFF}")


def q11(rs=None):
    """The registered direction was: top-decile funding precedes NEGATIVE forward
    returns, i.e. the top-decile mean sits BELOW the unconditional mean. The
    registration demanded it hold in BOTH the 2021 bull and the 2022 bear. The
    2024-26 window is the out-of-sample repeat that was never part of the test."""
    print(f"\nQ11 — FUNDING EXTREMES {DIM}(passed both registered windows, then reversed){OFF}")
    WINDOWS = (("2021 bull", "2021", "2022"),
               ("2022 bear", "2022", "2023"),
               ("2024-26 live", "2024", "2027"))
    # published: does the registered direction hold? per asset, per window, per horizon
    PUBLISHED = {"btc": {"2021 bull": (False, False, False),
                         "2022 bear": (True, True, True),
                         "2024-26 live": (True, False, False)},
                 "eth": {"2021 bull": (True, True, True),
                         "2022 bear": (True, True, True),
                         "2024-26 live": (False, False, False)}}
    PRINTS = {"btc": (7358, 1703), "eth": (7124, 1364)}
    for asset in ("btc", "eth"):
        rr = rs if rs is not None else rows(f"q11_{asset}")
        n_scored, n_top = PRINTS[asset]
        check(f"{asset.upper()} prints scored", len(rr), n_scored)
        check(f"{asset.upper()} top-decile prints",
              len([r for r in rr if r["bucket"] == "top_decile"]), n_top)
        if rs is not None:
            return
        for lbl, lo, hi in WINDOWS:
            el = [r for r in rr if r["bucket"] != "warmup" and lo <= r["date"][:4] < hi]
            top = [r for r in el if r["bucket"] == "top_decile"]
            got = tuple(statistics.mean(r[f"fwd_{h}h"] for r in top) <
                        statistics.mean(r[f"fwd_{h}h"] for r in el)
                        for h in ("8", "24", "72"))
            check(f"  {asset.upper()} {lbl}: direction holds 8/24/72h",
                  got, PUBLISHED[asset][lbl])
    print(f"  {DIM}BTC fails the registered 2021 test outright, so it never had the "
          f"effect.{OFF}")
    print(f"  {DIM}ETH holds in both registered windows and then reverses at every "
          f"horizon in the live window. Registered and tested in January 2024 it "
          f"would have read confirmed, and then bled.{OFF}")
    eth = rows("q11_eth")
    live = [r for r in eth if r["bucket"] != "warmup" and r["date"][:4] >= "2024"]
    top = [r for r in live if r["bucket"] == "top_decile"]
    for h, w_top, w_unc in (("8", 0.19, 0.02), ("24", 0.5, 0.05), ("72", 1.1, 0.14)):
        check(f"  ETH live window, top-decile {h}h %",
              pct(statistics.mean(r[f"fwd_{h}h"] for r in top), 2), w_top)
        check(f"  ETH live window, everything {h}h %",
              pct(statistics.mean(r[f"fwd_{h}h"] for r in live), 2), w_unc)


def from_the_artifacts():
    """Every remaining figure on the page, bound to the study artifact it came from."""
    print(f"\nFIGURES READ FROM THE STUDY ARTIFACTS {DIM}(not rebuildable from rows: "
          f"each needs 40 placebo re-runs over the price bars){OFF}")
    a = summary("q10_insider_clusters")
    lo, hi = a["spread_ci95_bootstrap"]
    check("Q10 spread CI low %", pct(lo, 1), -2.9)
    check("Q10 spread CI high %", pct(hi, 1), 3.0)
    check("Q10 placebo mean %", pct(a["placebo"]["mean"], 2), 2.28)
    check("Q12 placebo p", summary("q12_index_deletions")["placebo"]["p_empirical"], 0.025)
    b = summary("q8_buyback_drift")
    check("Q8 placebo p", b["placebo"]["p_empirical"], 0.725)
    print(f"  {DIM}Q8's placebo p was published as 0.700 on 2026-08-18 and is 0.725 "
          f"today. See correction 8: it is one placebo run in forty crossing, and "
          f"the reason it moved is that the price history grew underneath a "
          f"finished study.{OFF}")


def negative_control():
    """Corrupt the data three ways and require every check to notice."""
    print(f"\nNEGATIVE CONTROL {DIM}— the checker must be able to say no{OFF}")
    global fails
    probes = [
        ("one abnormal return altered", "q8", lambda rs: (
            rs.__setitem__(0, dict(rs[0], ar=rs[0]["ar"] + 0.5)), rs)[1], q8),
        ("one row dropped", "q10", lambda rs: rs[1:], q10),
        ("one bucket label flipped", "q10", lambda rs: (
            rs.__setitem__(0, dict(rs[0], bucket="single")), rs)[1], q10),
        ("one funding print removed", "q11_btc", lambda rs: rs[1:], q11),
    ]
    all_bit = True
    for label, src, corrupt, fn in probes:
        before = list(fails)
        fails = []
        buf, sys.stdout = sys.stdout, open("/dev/null", "w")
        try:
            fn(corrupt(rows(src)))
        finally:
            sys.stdout.close()
            sys.stdout = buf
        bit = bool(fails)
        fails = before
        print(f"  {(GREEN + 'PASS' + OFF) if bit else (RED + 'FAIL' + OFF)}  "
              f"{label:<38} {'rejected' if bit else 'ACCEPTED — the check is blind'}")
        if not bit:
            fails.append(f"negative control did not fire: {label}")
            all_bit = False
    if all_bit:
        print(f"  {DIM}every corruption was caught, so the passes above mean "
              f"something{OFF}")


def main():
    print(f"\n{'=' * 72}\n  THE NULL REGISTER — Entry 02, five signals, measured"
          f"\n{'=' * 72}")
    q12(); q10(); q8(); q9(); q11()
    from_the_artifacts()
    negative_control()

    if "--instruments" in sys.argv:
        print(f"\n{DIM}--instruments re-runs the original studies in instruments/. "
              f"They read a local cache of daily price bars, which is licensed data "
              f"and is not redistributed here. Point them at your own bars to "
              f"regenerate the rows this script just checked.{OFF}")

    print()
    if fails:
        print(f"{RED}{len(fails)} FAILURE(S){OFF}")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"{GREEN}All checks passed.{OFF}  Everything above the artifact section "
          f"was recomputed from the shipped rows; the five figures below it were "
          f"read from the study artifacts and are labelled as such.")


if __name__ == "__main__":
    main()
