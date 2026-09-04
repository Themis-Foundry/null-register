# Entry 03 — The leaderboard ranks account size

**A public leaderboard of 43,141 crypto traders, and a control that shows its top
performers are mostly just its biggest wallets.**

---

![Four rankings of the same 42,850 wallets over the same nine days. Ranked by last week's dollars, 88.6% are profitable again; ranked by account size alone, which contains no performance information, 83.8%; ranked by percent return, 64.5%; the whole board, 52.8%](diagram.svg)

### If you have never looked at one of these, start here

Several crypto exchanges publish a leaderboard: every trader ranked by how much money
they made, updated constantly, free to read. Whole products exist to let you copy the
people at the top, on the reasonable-sounding theory that whoever made the most last
week knows something.

**This is a check of what that ranking actually measures.** The data is one exchange's
full board, captured on two dates nine days apart, so every wallet can be scored on one
date and looked up again on the other.

The short answer: the top of the board is where the large accounts are, and once you
control for that, most of what looks like skill goes away.

---

## The finding, and it rests on a control

Take every wallet on the board on 21 August, rank them by how many dollars they made
that week, and take the top tenth. Nine days later, **88.6% of them are profitable
again**, against **52.8%** for the board as a whole. That looks like strong persistence,
and it is the number a copy-trading product would put on its landing page.

Now run the same test on a ranking that cannot possibly know anything about skill:

| ranked by | profitable next period | median account |
|---|---:|---:|
| last week's **dollars** | **88.6%** | $870,640 |
| last week's **percent return** | **64.5%** | $108,008 |
| **account size alone** | **83.8%** | $1,201,082 |
| everyone on the board | 52.8% | $1,018 |

**Sorting by how much money a wallet holds — a number containing no information about
performance at all — recovers 83.8 of the 88.6 points.** The two rankings pick 72.9% of
the same wallets. The median account in the "best traders of the week" decile is
$870,640, against $1,018 for the board.

The reason is not subtle once it is stated. A big account moves more dollars, so it
posts bigger dollar swings in both directions, and in a period when the market rose most
large accounts made money. Ranking by dollars ranks size wearing performance as a
costume.

**Switch to percent return, which is size-neutral, and the effect drops to 64.5%.**
Something may survive there. This entry does not claim it does: that is Q28's registered
question and its honest read is a thirty-day one due on 2026-09-20. **What is measured
here is nine days, and it is not that test.**

## The same question, answered eight ways

Before trusting any correlation from a board like this, it is worth knowing how much the
answer depends on choices nobody thinks of as choices. Here is one question — does an
earlier period predict a later one — computed eight defensible ways on the same wallets:

| | month vs week | prior month vs week |
|---|---:|---:|
| dollars, rank correlation | **+0.831** | **−0.511** |
| dollars, raw correlation | **+0.699** | **−0.885** |
| percent, rank correlation | **+0.810** | **−0.523** |
| percent, raw correlation | **−0.000** | **−0.002** |

Every cell is defensible. The left column compares the month against the week inside it,
so the two share data and the correlation is partly a number correlated with itself. The
right column removes the week from the month first, which fixes that and introduces the
opposite problem: subtracting a quantity from itself forces a negative relationship.

**The answers run from +0.83 to −0.89, and they disagree about the sign.** No sample size
repairs this. The number is a property of the method, and any single one of these
reported on its own would be believed.

The worst version is the one that looks most like a discovery. Sort by the subtracted
measure, take the bottom decile — the traders who did worst before that week — and 88.6%
of them are profitable that week with a median of $202,005. **That is not a comeback
effect. The sort selects for a big week directly, because a big week is what was
subtracted out.**

## Who leaves

Between the two snapshots, 291 wallets present on 21 August were gone by 30 August, and
1,531 new ones appeared.

**The ones that left were profitable 75.6% of the time. The ones that stayed, 49.5%.**

Whatever governs inclusion, it is not neutral with respect to performance, and it sits
above every figure on this page. The board's own rule for who appears is not published,
so this is a measured fact without an explanation attached, which is how it is left here.

## The other thing worth saying about "43,141 traders"

**26,511 of them, 61.9%, did no trading at all in the month measured.** Their volume is
zero. Across the whole board, 49.5% show an all-time profit, and 10,050 of those profits
exceed $100,000. That is profit, not account balance. A headcount that is mostly dormant
accounts is not a population of traders, and any base rate computed over it inherits that.

## How to check this without trusting me

```bash
./verify.py             # recompute every figure above. Offline, no key, instant.
```

Every wallet that appears in both snapshots ships as a row: its address, account size,
the week and month figures on the first date, and what happened by the second. Every
number on this page is recomputed from those rows.

**The checker is built to fail**, and this entry had to learn what that costs at scale.
It corrupts the data four ways on every run and requires each corruption to be caught.
An earlier version corrupted exactly one row, and at n=42,850 that moves nothing above
the precision these figures are published at, so **two of its four controls were silently
accepted and the suite reported a pass it had not earned.** They now corrupt a percent of
the board, which is still far smaller than any error worth finding.

## What is deliberately not here

**A claim that Q28 is answered.** It is not. The registered test is a thirty-day read
first honest on 2026-09-20, and only the feasibility question, Q30, is confirmed in this
project's durable ledger. The persistence and slippage studies ship here as interim
artifacts, labelled as such.

**Any recommendation.** Nothing here says copy-trading cannot work. It says this board's
default ranking is substantially a size ranking, and that a number taken off it depends
on a method choice that is usually invisible.

## Files

```
data/q28s_events.jsonl          42,850 wallets in both snapshots, unrounded
data/summaries/                 the study artifact, plus the interim persistence
                                and slippage studies
instruments/                    the collector and the exact code behind every row
verify.py                       recomputes every figure, and can be made to fail
make_diagram.py                 redraws diagram.svg from the rows above
```

Source is one exchange's public leaderboard endpoint, which needs no key and no account.
Addresses are the public identifiers the exchange itself publishes.

## Corrections

In [CORRECTIONS.md](../../CORRECTIONS.md) at the root, numbered across the whole register.
