# The Null Register — Entry 01: the odd-lot census

**A complete count of one small stock-market strategy, published with the 14 cases where
it did not work.**

Almost every published figure on this strategy is a success rate quoted without a denominator.
This is the denominator: every operating-company odd-lot tender offer filed with the SEC between
2016-01-13 and 2025-07-10, and what the filings actually establish about each one.

| | |
|---|---:|
| Offers in the census | **119** |
| Reached a final, filed outcome | **62** |
| Confirmed oversubscribed | **21** |
| Confirmed **not** oversubscribed | **14** |
| Resolved but undetermined | **27** |
| No final filing found | **49** |
| Excluded (share exchange) | **7** |
| Could not be checked | **1** |

**Oversubscription rate: 33.9% to 77.4%, n=62.** A range, not a number, because
27 outcomes are genuinely undetermined. The lower bound assumes all of them were
not oversubscribed; the upper bound assumes all of them were. **A 43.5-point band cannot
size a position and is not offered as one.**

## Proration, which is the condition that actually pays

The odd-lot preference is worth something exactly when other holders are cut back and you are not.
That is proration, and it is not the same event as oversubscription: a company facing excess demand
can simply buy the extra shares, in which case nobody is prorated and the preference pays nothing.

Measured across the 62 resolved offers, from filing language and never from arithmetic:
**25 state that proration occurred, 11 state that it did not, 26 do not
say.** A band of **40.3% to 82.3%** on the condition that pays.

## Why the failures are here

A dataset that can only report successes is not evidence. It has no mechanism for being wrong.
The 14 confirmed failures are the negative control, and they are what make the
21 successes worth anything.

They are also harder to establish, which is a finding in itself. A company that prorates is
required to publish the factor, so oversubscription announces itself. A company that did not
prorate often just reports what it bought. **Absence has to be established; presence declares
itself.** That is a large part of why the failures in this strategy are underpublished.

## How to check this without trusting me

Every classified row carries the sentence it was read from and the URL of the document containing
it. 35 of 35 do. You can check any row against its own SEC filing
without running a line of my code.

```bash
./reproduce.sh            # regenerates every published figure. Offline, instant.
./reproduce.sh --claims   # also fetches each cited filing and proves the quote is in it.
```

Set your contact address at the top of `verify.py` before the network run. The SEC requires one.

**The script is built to fail.** It runs negative controls in both modes: a real quote must match,
a one-character change must be rejected, another filing's quote must be rejected. If the checker
cannot be made to say no, it exits non-zero rather than reporting a pass it has not earned.

## What is deliberately not here

The harvester and classifier that produced the dataset are not published. **They do not need to
be, and that is the point.** You are not being asked to run my pipeline and believe its output.
You are being handed the evidence each row was built from, which is a stronger claim than a
reproducible script: it lets you disagree with my classification while still checking my sources.

## Corrections

Six, in [CORRECTIONS.md](CORRECTIONS.md). Every one is an error this project made about its own
data, including two rows that were published on the wrong side of a headline that was right.

## Files

```
data/oddlot_census_119.json    every row, with evidence quotes and source URLs
data/oddlot_census_119.csv     the same, flattened
data/edgar_oddlot_offers_2016_2026.jsonl
                               the underlying index of odd-lot tender offers on EDGAR,
                               useful on its own to anyone studying tender offers
verify.py / reproduce.sh       regenerate and check every published figure
```

## Corrections are welcome and are the most useful thing you can send

If you find an error in a row, that is worth more to this project than a star. Open an issue with
the ticker and the filing. Corrections are published in `CORRECTIONS.md` with the original claim
left standing next to the reversal.

MIT licensed. Sources are SEC EDGAR filings, retrieved under the SEC fair-access policy.
