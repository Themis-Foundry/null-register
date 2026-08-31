# The Null Register — Entry 01: the odd-lot census

**119 SEC tender offers read one filing at a time, published with the 14 cases where the
strategy did not work, and with the 91 qualifying offers this census does not reach.**

---

### If you have never heard of any of this, start here

**What is it?** When a company wants to buy back its own shares, it sometimes makes a public
offer: we will purchase this many shares, at this price, for the next few weeks. If more people
say yes than the company asked for, everybody gets cut back proportionally. You offer 1,000
shares, they buy 400, and you are stuck holding the rest.

**Except for very small holders.** Most of these offers carry a clause: if you own fewer than
100 shares, you get bought out in full, ahead of everyone else. That clause is real, it is
written into the filings linked throughout this repo, and most investors have never heard of it.

**So is there money in it?** Only when the offer is oversubscribed, which is the one thing that
makes the clause worth anything. **This repo is a count of how often that actually happened, and
the honest answer is a range so wide you should not trade on it.** If you came for a strategy,
that is your answer. If you came to see what a count looks like when nobody is selling you
anything, keep reading.

**Why publish it at all?** Because the failures normally vanish. Everyone writes up the times a
thing worked, so the record everyone reads is a highlight reel, and the same idea gets retried
because nobody published the last five times it did not pay. Here the failures get the same
space, the same evidence and the same links as the wins.

---

Almost every published figure on this strategy is a success rate quoted without a denominator.
This is a denominator, stated honestly:

- The EDGAR sweep found **372** tender offers carrying odd-lot language, 2016 to 2026.
- **210** of those are operating-company offers that actually carry the preference. The rest
  are closed-end funds tendering at net asset value, or offers with no odd-lot provision.
- **This census covers 119 of the 210**, spanning 2016-01-13 to 2025-07-10.

⚠ **It is not a complete count and the gap is not random.** The census was restricted to offers
whose filer could be matched to a ticker with confidence, and **75 of the 91 left out
failed exactly that check.** Identity is easier to establish for larger, more heavily traded
companies, so this set probably skews toward bigger offers. Nothing here corrects for that.

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

Seven, in [CORRECTIONS.md](CORRECTIONS.md). Every one is an error this project made about its own
data, including two rows published on the wrong side of a headline that was right, and the word
"complete" appearing in an earlier draft of this file.

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
