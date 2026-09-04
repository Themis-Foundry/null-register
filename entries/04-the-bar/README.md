# Entry 04 — The bar that random strategies cleared

**Forty trend-following strategies with no signal in them were run against the bar this
project used to promote a strategy. Thirty-nine cleared it. So did the strategy it had
promoted, which twelve of the forty then beat.**

verdict: NEVER WORKED — a fixed per-trade profit bar tells you whether the market went up, not whether the rule works

---

![Forty signal-free strategies on one strip, each a dot at its profit per trade. The promotion bar sits at +0.07R near the left edge and thirty-nine dots are to the right of it. The one real strategy, promoted by the league, sits at +0.196R with twelve null dots beyond it. The rightmost null, +0.304R, is the empirical bar.](diagram.svg)

### If you have never backtested anything, start here

**What is a bar?** When you test a trading rule on past prices, you get a number: on
average, how much did each trade make after costs? Every backtesting setup has a
threshold. Above it the rule is "promoted," meaning it is allowed to trade real money or
at least to be taken seriously. This project's threshold was **+0.07R per trade**, where
R is the amount risked on the trade. Seven cents kept for every dollar put at risk.

**What is a signal-free strategy?** Take the exact same rule and run it on a version of
the price history that has been scrambled in one-week blocks. The market still goes up
over the years, still has its crashes and its calm stretches, still has the same
volatility. What it no longer has is any pattern longer than a week for the rule to
find. A trend rule on that history is guessing. **If guessing clears the bar, the bar
is not measuring the rule.**

**What happened.** Forty of those scrambled histories were built, seeded, and run
through the same rule with the same costs. Thirty-nine of the forty came out above
+0.07R. Their average was +0.169R, more than double the bar. The best of them made
+0.304R per trade.

The one real strategy, the one this project's own league had promoted on the real
history, made +0.196R. **Twelve of the forty guessing strategies made more than that.**

---

## The numbers, from the shipped rows

Batch `league-check-momentum`, scored 2026-08-08, seed 8080, 24 large ETFs, one
momentum rule with a 48-cell parameter grid, one real run and forty block-bootstrap
nulls. Every figure below is recomputed by `verify.py` from `data/batches/…/results.jsonl`.

| | value |
|---|---|
| signal-free strategies graded | 40 |
| cleared the +0.07R bar | **39 (98%)** |
| their mean profit per trade | +0.169R |
| their best | +0.304R |
| the real, promoted strategy | +0.196R over 627 trades |
| signal-free strategies that beat the real one | **12 of 40** |
| signal-free strategies the grader itself marked PROMOTE | 11 of 40 |

That last row is the one to sit with. The grading code that had promoted the real
strategy, handed forty strategies it had no way to tell apart from noise, promoted
eleven of them.

## Why: the bar measured the market, not the rule

The scrambled histories keep the drift of the real one, because they are built from the
real returns and equities went up over the window. A long-only trend rule on a rising
market makes money whether or not its signal means anything. The bar asked "did you
beat zero?" when the question that matters is "did you beat holding the market?"

That is a finding about the bar, not about the strategy. The strategy may or may not
have an edge. **The instrument that was supposed to tell us cannot.**

## Where it could work: the same bar on a second family

The same test was run four more times. Three on trend-following, one pair on mean
reversion, a family whose rules do not ride drift.

| batch | family | signal-free graded | cleared +0.07R | grader said PROMOTE |
|---|---|---:|---:|---:|
| `league-check-momentum` | momentum | 40 | **39 (98%)** | 11 |
| `pilot-q16-momentum` | momentum | 17 | **12 (71%)** | 13 |
| `q16-momentum-deep` | momentum | 258 | **102 (40%)** | 154 |
| `q16-mean-reversion` | mean reversion | 6 | 0 | 0 |
| `q16-mean-reversion-deep` | mean reversion | 150 | 0 | 9 |
| **all five** | | **471** | **153 (32%)** | 187 |

On trend-following, 153 of 315 signal-free strategies cleared the bar. On mean
reversion, none of 156 did, and their average sat near zero. **A fixed bar is a
usable bar exactly when guessing centres on zero, and it is not a bar at all when
guessing centres above it.** The cure is not a higher number. It is measuring what
guessing scores, every time, and demanding the real rule beat that.

Measured that way, with the bar set at the best of the signal-free runs in its own
batch: **one real candidate across the five batches cleared it, and it was not one of
the promoted ones.** Twenty-four were run and one crashed. Thirteen had been promoted
by the league beforehand; none of the thirteen beat its batch's best guess. The one
that did was a mean-reversion rule at +0.036R over 148 trades, ahead of the best of six
graded nulls in a batch where guessing centred on zero, and still below the +0.07R bar.
The batch had marked it WATCH.

## What is in the data and what is not

- `data/batches/<batch>/results.jsonl` is one row per run, real and null, including the
  rows that were too thin to grade and the rows that crashed. In `q16-mean-reversion-deep`,
  151 of 302 runs errored: the mean-reversion code failed on one universe, and those
  rows are shipped with their tracebacks rather than dropped.
- `data/batches/<batch>/manifest.json` is what was declared before grading: the
  question, the family, the number of real candidates, the null generator and its seed,
  the bar, and the minimum trade count.
- `data/batches/<batch>/verdict.md` is the report the batch runner wrote at the time.
  **One of its counts is wrong and is left as written.** For `q16-mean-reversion` it
  reports 8 of 30 signal-free strategies clearing the bar; 24 of those 30 were below the
  batch's own minimum trade count and should not have been counted. Graded strictly,
  it is 0 of 6. `verify.py` uses the strict count and says so.
- The daily price bars the strategies ran on are licensed and are not here. The null
  generator and the strategy code are not here either; this entry ships what was
  measured, not the instrument. That is the same choice Entry 02 made, for the same
  reason: the rows are the evidence.

## The honest limits

- Every candidate in every batch searched the same price history, and so did the
  batches before them. The count of things tried against this data only goes up, and it
  is larger than any one batch reports.
- The ETF universe holds what the data source serves today. Delisted names are absent,
  which flatters every equity result here by an amount nobody has measured.
- "Nothing beat the empirical bar" is a statement about these rules, these costs and
  this window. It is not a statement that trend-following does not work.

## How this is checked

```bash
python3 verify.py
```

Recomputes every figure on this page from the shipped rows, then corrupts the rows
three ways and requires each corruption to be caught. If the checker cannot be made to
say no, it exits non-zero.
