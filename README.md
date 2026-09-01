# The Null Register

**A public record of research that did not work, published with the same care as
research that did.**

---

I kept noticing the same thing. Someone writes up a trading idea, the write-up is
always about the version that worked, and six months later somebody else tries the
same idea from scratch because nobody published the five times it did not pay. The
record everyone reads is a highlight reel, and a highlight reel is not a record.

So this is the other half. Every entry here is something I measured and mostly could
not make work, published with the failures given the same space, the same evidence and
the same links as the parts that held.

**Nothing here is a recommendation, and a few entries exist specifically to talk you
out of something.**

---

## The entries

### [01 — The odd-lot census](entries/01-oddlot-census/)

*119 SEC tender offers, read one filing at a time.*

There is a clause in most corporate buyback offers that buys out holders of fewer than
100 shares in full, ahead of everyone else. It is real and most investors have never
heard of it. **It is only worth something when the offer is oversubscribed, and this
is a count of how often that actually happened.**

The answer is a range so wide you should not trade on it: **33.9% to 77.4%**, because
27 of the 62 resolved offers genuinely cannot be determined from their own filings.
Twenty-one worked. Fourteen did not, and those fourteen are in the data.

Every classified row carries the sentence it was read from and a link to the filing,
so you can check any row against its own SEC document without running my code.

### [02 — Five signals everyone repeats, measured](entries/02-five-signals/)

*Five rules of thumb, each measured against a placebo on the whole cohort.*

Buy when insiders buy. Buy the buyback announcement. Buy the stock that just got
dropped from the S&P 500. Fade extreme funding rates. Sell into a rights offering.

**Four of the five were never there.** The insider-cluster signal at 24,021 events has
a spread whose confidence interval straddles zero, and moving every event to a random
date in the same stocks produces a *larger* edge than the real dates do.

**One changed its behaviour.** Buying S&P 500 deletions returned **+12.4%** a trade from
2016 to 2020 and **−3.9%** from 2021 to 2026. Neither era clears zero on its own, and the
**gap between them does**, which is a different and more careful claim than the one this
page made first.

Every study ships the rows it scored, including the ones it threw out and why.

### [03 — The leaderboard ranks account size](entries/03-copy-trading/)

*43,141 crypto traders ranked in public, and a control that shows the ranking is mostly
wallet size.*

Take the top tenth of a public trading leaderboard by last week's profit and **88.6% are
profitable again nine days later**, against a **52.8%** base rate. That is the number a
copy-trading product would advertise.

**Then rank by account size alone, which contains no performance information at all, and
you get 83.8%.** The two rankings pick 72.9% of the same wallets, and the median account
in the "best traders" decile is $870,640 against $1,018 for the board.

Also here: the same question answered eight defensible ways, giving everything from
**+0.83 to −0.89**, disagreeing about the sign.

---

## How this is checked

Each entry has a `verify.py` that recomputes every figure the entry claims and prints
it beside what the page says.

```bash
cd entries/02-five-signals && ./reproduce.sh
```

**The checkers are built to fail.** Each one corrupts its own data on purpose at the
end of the run and requires every check to go red. If a checker cannot be made to say
no, it exits non-zero rather than reporting a pass it has not earned. A gate that has
never gone red is not a gate, it is a decoration.

Two entries verify in two different ways, and the difference is deliberate:

| | Entry 01 | Entry 02 |
|---|---|---|
| what the evidence is | a sentence in a filing | a computation over thousands of events |
| so what ships | the quote and its source URL | the per-event rows, and the code |
| what is withheld | the harvester and classifier | the licensed price bars |

Entry 03 follows Entry 02: the rows ship, and so does the code.

**When the evidence is a sentence, hand over the sentence. When the evidence is a
computation, the computation is the evidence.** A summary statistic with nothing
underneath it is the exact kind of claim this register exists to refuse.

## Reading this from a program

`index.json` at the root lists every entry and every data file with its path, size
and SHA-256. **Read that rather than hardcoding a path.** Entry 01 sat at the repo
root until a second entry arrived and everything moved under `entries/`; anything
wired to the old locations would have broken, and the next reorganisation should be
a manifest change instead.

```bash
curl -s https://raw.githubusercontent.com/Themis-Foundry/null-register/main/index.json
```

The hashes let a consumer tell a file that moved from a file that changed, and cache
against the content rather than the URL. `reproduce.sh` regenerates the manifest and
fails if it has drifted from the tree, so it cannot go stale quietly.

## Corrections

**[CORRECTIONS.md](CORRECTIONS.md) — ten of them, numbered across the whole
register.**

They are the most important file here. Two published rows sat on the wrong side of a
headline that was right the whole time, and only row-level evidence could have shown
it. A figure moved after publication because the price history underneath it kept
growing. The word "complete" appeared in a draft of Entry 01 and was false.

Each correction leaves the original claim standing next to the reversal.

**If you find an error in a row, that is worth more to this project than a star.** Open
an issue with the ticker and the filing.

---

Sources are public: SEC EDGAR filings, S&P index change announcements, and public
exchange APIs. Entry 01 is MIT licensed. Corrections and disagreement are welcome, and
disagreeing with a classification while checking its source is exactly the use this is
built for.
