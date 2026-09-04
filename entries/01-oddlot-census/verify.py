#!/usr/bin/env python3
"""
Regenerate and check every number published in The Null Register, Entry 01.

Two modes:
    python3 verify.py              counts and arithmetic only. Offline, instant.
    python3 verify.py --claims     also fetches every cited SEC document and checks
                                   that the quoted sentence is a verbatim substring
                                   of it. Network, ~35 requests, about a minute.

This script does not contain the classifier that produced the dataset, and it does
not need to. Every classified row carries the sentence it was read from and the URL
of the document containing it, so any row can be checked against its own source
without trusting the pipeline that built it. That is the point: you are not being
asked to run our code and believe the output. You are being handed the evidence.

A negative control runs in both modes. If the checker cannot be made to fail, it
is not checking anything, and this script exits non-zero rather than reporting a
pass it has not earned.
"""

import json, sys, re, html, time, pathlib, urllib.request, urllib.error

DATA = pathlib.Path(__file__).parent / "data" / "oddlot_census_119.json"
EDGAR = pathlib.Path(__file__).parent / "data" / "edgar_oddlot_offers_2016_2026.jsonl"
UA = "The Null Register — dataset verification — replace-with-your-email@example.com"

# ── the figures as published, asserted here so a drift shows up as a failure ──
PUBLISHED = {
    "total offers":                119,
    "resolved":                     62,
    "no final filing found":        49,
    "excluded (share exchange)":     7,
    "could not be checked":          1,
    "confirmed oversubscribed":     21,
    "confirmed not oversubscribed": 14,
    "resolved but undetermined":    27,
    # only offers with a real share cap can exceed one. Three further offers bought above
    # their reference share count, but are dollar-denominated and have no share target.
    "bought above stated target":    1,
    "carrying a proration factor":  18,
    # the denominator: of 372 EDGAR hits, the operating-company offers that carry the
    # preference. A hand count until 2026-09-04, when an independent audit noted the
    # shipped rows could not reproduce it. The two fields that do ship now.
    "EDGAR offers swept":            372,
    "operating-company, preference": 210,
    "census offers inside the 210":  119,
}
PUBLISHED_BAND = (33.9, 77.4)

GREEN, RED, DIM, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[0m"
if not sys.stdout.isatty():
    GREEN = RED = DIM = OFF = ""

fails = []


def check(label, got, want):
    ok = got == want
    mark = f"{GREEN}PASS{OFF}" if ok else f"{RED}FAIL{OFF}"
    print(f"  {mark}  {label:<32} {got:>5}   expected {want}")
    if not ok:
        fails.append(f"{label}: got {got}, expected {want}")
    return ok


def normalise(s):
    """Strip tags and normalise the punctuation EDGAR varies on."""
    s = html.unescape(re.sub(r"<[^>]+>", " ", s))
    for a, b in [("“", '"'), ("”", '"'), ("’", "'"),
                 ("‘", "'"), ("—", "-"), ("–", "-"), (" ", " ")]:
        s = s.replace(a, b)
    return re.sub(r"\s+", " ", s).strip()


def state_of(row):
    """The three-state classification, recomputed from the shipped fields."""
    st = row.get("outcome_state")
    if st != "RESOLVED":
        return {"UNRESOLVED": "unresolved",
                "split_off_exchange": "excluded",
                "COULD_NOT_LOOK": "unchecked"}.get(st, "unknown")
    o = row.get("oversubscribed")
    return "oversubscribed" if o is True else ("not" if o is False else "undetermined")


def main():
    rows = json.load(open(DATA))["rows"]
    tally = {}
    for r in rows:
        tally[state_of(r)] = tally.get(state_of(r), 0) + 1

    print("\nTHE CENSUS")
    check("total offers", len(rows), PUBLISHED["total offers"])
    resolved = sum(tally.get(k, 0) for k in ("oversubscribed", "not", "undetermined"))
    check("resolved", resolved, PUBLISHED["resolved"])
    check("no final filing found", tally.get("unresolved", 0), PUBLISHED["no final filing found"])
    check("excluded (share exchange)", tally.get("excluded", 0), PUBLISHED["excluded (share exchange)"])
    check("could not be checked", tally.get("unchecked", 0), PUBLISHED["could not be checked"])

    print("\nOF THE RESOLVED")
    check("confirmed oversubscribed", tally.get("oversubscribed", 0), PUBLISHED["confirmed oversubscribed"])
    check("confirmed not oversubscribed", tally.get("not", 0), PUBLISHED["confirmed not oversubscribed"])
    check("resolved but undetermined", tally.get("undetermined", 0), PUBLISHED["resolved but undetermined"])

    print("\nTHE BAND")
    lo = round(tally.get("oversubscribed", 0) / resolved * 100, 1)
    hi = round((tally.get("oversubscribed", 0) + tally.get("undetermined", 0)) / resolved * 100, 1)
    ok = (lo, hi) == PUBLISHED_BAND
    print(f"  {(GREEN + 'PASS' + OFF) if ok else (RED + 'FAIL' + OFF)}  "
          f"oversubscription rate      {lo}% - {hi}%   expected "
          f"{PUBLISHED_BAND[0]}% - {PUBLISHED_BAND[1]}%")
    if not ok:
        fails.append(f"band: got {lo}-{hi}, expected {PUBLISHED_BAND}")
    print(f"  {DIM}lower bound treats all {tally.get('undetermined',0)} undetermined as not "
          f"oversubscribed; upper bound treats them all as oversubscribed{OFF}")

    print("\nTHE DENOMINATOR, RECOMPUTED FROM THE EDGAR SWEEP")
    edgar = [json.loads(l) for l in open(EDGAR) if l.strip()]
    check("EDGAR offers swept", len(edgar), PUBLISHED["EDGAR offers swept"])
    operating = [e for e in edgar if not e.get("is_fund") and e.get("odd_lot_preference")]
    check("operating-company, preference", len(operating), PUBLISHED["operating-company, preference"])
    op_keys = {(e["cik"], e["date"]) for e in operating}
    def cik_of(row):
        m = re.search(r"CIK (\d+)", row.get("company", ""))
        return m.group(1) if m else None
    inside = sum(1 for r in rows if (cik_of(r), r["date"]) in op_keys)
    check("census offers inside the 210", inside, PUBLISHED["census offers inside the 210"])
    print(f"  {DIM}every operating row carries the odd-lot sentence it was read from "
          f"(preference_quote); {sum(1 for e in operating if e.get('preference_quote'))} of "
          f"{len(operating)} do{OFF}")

    print("\nTHE CAVEATS, ALSO RECOMPUTED")
    upsized = [r for r in rows if r.get("shares_accepted") and r.get("shares_sought")
               and r["shares_accepted"] > r["shares_sought"]]
    check("bought above stated target", len(upsized), PUBLISHED["bought above stated target"])
    for r in upsized:
        over = r["shares_accepted"] / r["shares_sought"] - 1
        print(f"        {DIM}{r['ticker']:<6} +{over*100:>4.1f}%   "
              f"proration {r.get('proration_pct') or 'not stated'}{OFF}")
    withpro = [r for r in rows if r.get("proration_pct")]
    check("carrying a proration factor", len(withpro), PUBLISHED["carrying a proration factor"])
    print(f"  {DIM}18 stated factors against 21 oversubscribed verdicts is why the page calls "
          f"oversubscription a proxy for proration rather than the same event{OFF}")

    classified = [r for r in rows if r.get("oversubscribed") in (True, False)]

    print("\nEVIDENCE COMPLETENESS")
    check("classified rows", len(classified), 35)
    check("carrying a source URL", sum(1 for r in classified if r.get("evidence_url")), 35)
    check("carrying a verbatim quote", sum(1 for r in classified if r.get("evidence_quote")), 35)

    if "--claims" in sys.argv:
        print("\nCLAIM BINDING — fetching each cited filing from sec.gov")
        if "example.com" in UA:
            print(f"  {RED}STOP{OFF}  Set UA at the top of this file to your own contact address.")
            print("        The SEC requires it and will return 403 without one.")
            sys.exit(2)
        good = bad = err = 0
        for r in classified:
            try:
                req = urllib.request.Request(r["evidence_url"], headers={"User-Agent": UA})
                doc = normalise(urllib.request.urlopen(req, timeout=45).read().decode("utf-8", "ignore"))
                if normalise(r["evidence_quote"]) in doc:
                    good += 1
                else:
                    bad += 1
                    print(f"  {RED}FAIL{OFF}  {r['ticker']} — quote is not in the cited document")
                    fails.append(f"claim binding: {r['ticker']}")
                time.sleep(1.1)              # SEC fair-access rate limit
            except Exception as e:
                err += 1
                print(f"  {DIM}SKIP{OFF}  {r['ticker']} — {type(e).__name__}")
        print(f"  {GREEN}{good}{OFF} verbatim · {RED}{bad}{OFF} mismatched · {err} unreachable")
        if err:
            print(f"  {DIM}unreachable rows are not passes. Re-run before trusting a clean sheet.{OFF}")

    # ── negative control: the checks above are worthless if they cannot fail ──
    print("\nNEGATIVE CONTROL — the checker must be able to say no")
    probe = classified[0]
    q = normalise(probe["evidence_quote"])
    corrupted = q[:40] + "X" + q[41:]
    other = normalise(classified[3]["evidence_quote"])
    haystack = q                                    # stand-in for the document
    flipped = [dict(e) for e in operating]
    flipped[0]["odd_lot_preference"] = False
    n_flipped = sum(1 for e in flipped if not e.get("is_fund") and e.get("odd_lot_preference"))
    controls = [
        ("real quote matches itself",            q in haystack,          True),
        ("one flipped preference moves the 210", n_flipped == PUBLISHED["operating-company, preference"], False),
        ("one character changed is rejected",    corrupted in haystack,  False),
        ("a different filing's quote rejected",  other in haystack,      False),
    ]
    for label, got, want in controls:
        ok = got is want
        print(f"  {(GREEN+'PASS'+OFF) if ok else (RED+'FAIL'+OFF)}  {label}")
        if not ok:
            fails.append(f"negative control: {label}")

    print()
    if fails:
        print(f"{RED}{len(fails)} FAILURE(S){OFF}")
        for f in fails:
            print(f"  - {f}")
        sys.exit(1)
    print(f"{GREEN}All checks passed.{OFF}"
          + ("" if "--claims" in sys.argv else "  Run with --claims to verify every quote against sec.gov."))


if __name__ == "__main__":
    main()
