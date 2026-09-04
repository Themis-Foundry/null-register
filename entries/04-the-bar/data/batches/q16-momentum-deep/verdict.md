# BATCH q16-momentum-deep — verdict

`scored 2026-08-08T14:06:19 · question: Q16 — the null quantile, MEASURED instead of assumed (docs/QUESTIONS.md) · family: momentum`

## The gate that was applied

- **K (declared before grading): 6** real candidates, 300 nulls (block_bootstrap)
- LAW E1 min-n: **121 trades** (family-wise alpha 0.05 over K -> 8.33e-03 each)
- League promote bar: +0.07R
- **Empirical bar actually used: +0.2309R** (the strictest of: league bar, parametric null quantile +0.1743R, observed null max +0.2309R)
  - the 0.99167 quantile was **OBSERVED directly** at +0.2255R from 258 graded nulls — no normality assumption used.

## LAW E2 — what the worthless candidates scored

- nulls run: 300; **graded: 258** (42 were thinner than the 121-trade min-n and are could-not-look, the same rule the real candidates get)
- null expectancy: mean **+0.0693R**, sd 0.0438, max **+0.2309R**
- nulls clearing the +0.07R league bar: **102/258 (40%)**

### ⛔ BATCH VOID — the absolute bar is not a bar here

More than one null in five cleared +0.07R, so every 'survivor' below is reported against the EMPIRICAL bar only and none may be quoted against +0.07R.

**Measured cause: MIXED — neither the null centre nor its spread alone explains the pass rate; read the numbers above directly rather than taking a one-line cause from this report.**

This is a finding about the bar, not a failure of the batch — and it is exactly what LAW E2 was built to catch.

## Results

| bucket | count |
|---|---|
| **SURVIVORS** (n>=121 and expectancy >= +0.2309R) | **0** |
| INSUFFICIENT (n < 121 — could-not-look, NOT a rejection) | 1 |
| below the empirical bar | 5 |
| errored | 0 |

### No survivors.

This is a result, not a failure. The batch bought a real answer: on this family, universe and cost model, nothing beat a signal-free strategy once the funnel tax was paid. Record it and move to the next question.

## Honest limits of this batch

- Every candidate searched the SAME price history. K controls error within this batch; it does not undo the fact that earlier batches already searched this data. Project-lifetime K is the number that actually governs, and it only goes up.
- `bars/` holds what the data source serves today, so delisted names are absent. Any equity result here is optimistic by an amount nobody has measured.
