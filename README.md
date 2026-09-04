# The Null Register

**Things traders repeat, measured. Nothing here is a recommendation, and most of it is a
warning.**

8 beliefs tested · 6 never worked · 0 stopped working · 1 work only when · 1 could not tell · 10 corrections, all published

---

Every trading idea gets written up when it works. Nobody publishes the five times it did
not, so the next person tries it from scratch, and the record everyone reads is a highlight
reel. A highlight reel is not a record.

This is the other half. Each entry takes something people repeat as if it were known, runs
it against the whole cohort with a placebo, and files a verdict. The failures get the same
space, the same rows and the same links as the parts that held. **Every verdict comes with
the sentence or the computation it was read from, and a checker that must be able to go
red.**

## The verdicts

| verdict | meaning |
|---|---|
| **NEVER WORKED** | measured against a placebo on the whole cohort, the effect is not there |
| **STOPPED WORKING** | it was there, in a window that has closed. None has earned this label yet; the closest candidate lost it in correction 10 |
| **WORKS ONLY WHEN** | real, and conditional on something the belief leaves out |
| **COULD NOT TELL** | the honest methods disagree, and this register will not pick the one that flatters |

`reproduce.sh` counts the verdict lines in every entry and fails if the number at the top of
this page is not what they add up to.

## The entries

### [04 — The bar that random strategies cleared](entries/04-the-bar/)

**NEVER WORKED · "a backtest that averages +0.07R a trade has found an edge."**

Forty trend-following strategies with no signal in them, the same rule run on a market
scrambled in one-week blocks, were held to the bar this project used to promote a
strategy. **Thirty-nine cleared it.** Their average was more than double the bar. The one
real strategy the bar had promoted was beaten by twelve of the forty, and the grading code
that promoted it also promoted eleven of them.

The bar was measuring whether the market went up. Across five batches and 471 signal-free
strategies, 153 cleared it, every one of them a trend rule; on mean reversion, where
guessing centres on zero, none of 156 did. **The fix is not a higher number. It is measuring
what guessing scores, every time, and demanding the real rule beat that.** Held to that,
none of the thirteen strategies this project had promoted survived.

### [02 — Five signals everyone repeats, measured](entries/02-five-signals/)

**NEVER WORKED · five times.** Buy when insiders buy. Buy the buyback announcement. Buy the
stock that just got dropped from the S&P 500. Fade extreme funding rates. Sell into a rights
offering.

Each moved to random dates in the same stocks forty times. **The insider signal, at 24,021
events, lost to its own placebo:** random dates produced a larger edge than the real ones.
The S&P deletion rebound looked like the one that worked, +12.4% a trade from 2016 to 2020
and −3.9% after, and an audit took it away: neither era clears zero on its own. What
survives is that the eras differ, by an interval that clears zero by 0.4 points, and that is
the thinnest claim in this register.

### [03 — The leaderboard ranks account size](entries/03-copy-trading/)

**COULD NOT TELL · "copy the top traders."**

Take the top tenth of a public leaderboard of 43,141 crypto traders by last week's profit,
and **88.6% are profitable again nine days later**, against a 52.8% base rate. That is the
number a copy-trading product advertises. **Rank by account size alone, which contains no
performance information, and you get 83.8%.** The two rankings pick 72.9% of the same
wallets, and the median "best trader" holds $870,640 against $1,018 for the board. The same
question, answered eight defensible ways, gives everything from +0.83 to −0.89. It
disagrees about the sign, so no verdict is filed.

### [01 — The odd-lot census](entries/01-oddlot-census/)

**WORKS ONLY WHEN · "holders of under 100 shares get bought out in full, ahead of everyone."**

The clause is real and most investors have never heard of it. It pays only when the offer
is oversubscribed, and this is a count of how often that happened: **119 SEC tender offers
read one filing at a time.** Twenty-one paid. Fourteen did not, and those fourteen are in
the data. Twenty-seven cannot be determined from their own filings, so the honest rate is
a range too wide to trade on, 33.9% to 77.4%. Every row carries the sentence it was read
from and a link to the filing.

---

## How this is checked

Each entry has a `verify.py` that recomputes every figure the entry claims and prints it
beside what the page says.

```bash
./reproduce.sh
```

**The checkers are built to fail.** Each one corrupts its own data on purpose at the end of
the run and requires every check to go red. If a checker cannot be made to say no, it exits
non-zero rather than reporting a pass it has not earned. A gate that has never gone red is
not a gate, it is a decoration. Entry 04 exists because of one that had not.

Entries verify in two different ways, and the difference is deliberate:

| | when the evidence is a sentence | when the evidence is a computation |
|---|---|---|
| example | Entry 01, a clause in a filing | Entries 02, 03, 04, thousands of rows |
| what ships | the quote and its source URL | the per-row results, and the code where it is ours to give |
| what is withheld | the harvester and classifier | the licensed price bars |

**When the evidence is a sentence, hand over the sentence. When the evidence is a
computation, the computation is the evidence.** A summary statistic with nothing underneath
it is the exact kind of claim this register exists to refuse.

## The flip log

**[CORRECTIONS.md](CORRECTIONS.md) — ten of them, numbered across the whole register**, and
the most important file here. Two published rows sat on the wrong side of a headline that
was right the whole time. A finished number moved because the price history underneath it
kept growing. An entry called something "the one that worked" and the data did not support
it. Each correction leaves the original claim standing next to the reversal, and the table
at the top of that file is the register reversing itself in one screen.

**If you find an error in a row, that is worth more to this project than a star.** Open an
issue with the ticker and the filing, or the row and the batch.

## Reading this from a program

`index.json` at the root lists every entry and every data file with its path, size and
SHA-256. **Read that rather than hardcoding a path.** Entry 01 sat at the repo root until a
second entry arrived and everything moved under `entries/`; the next reorganisation should be
a manifest change instead.

```bash
curl -s https://raw.githubusercontent.com/Themis-Foundry/null-register/main/index.json
```

`reproduce.sh` regenerates the manifest and fails if it has drifted from the tree, so it
cannot go stale quietly.

---

Sources are public: SEC EDGAR filings, S&P index change announcements, public exchange
APIs, and this project's own batch runs. MIT licensed. Disagreeing with a classification
while checking its source is exactly the use this is built for.
