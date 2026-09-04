# BATCH q16-mean-reversion-deep — verdict

`scored 2026-08-08T14:32:15 · question: Q16 — can the mean_reversion family be calibrated AT ALL? (docs/QUESTIONS.md) · family: mean_reversion`

## The gate that was applied

- **K (declared before grading): 2** real candidates, 150 nulls (block_bootstrap)
- LAW E1 min-n: **81 trades** (family-wise alpha 0.05 over K -> 2.50e-02 each)
- League promote bar: +0.07R
- **Empirical bar actually used: +0.0700R** (the strictest of: league bar, parametric null quantile +0.0549R, observed null max +0.0619R)
  - the 0.97500 quantile was **OBSERVED directly** at +0.0535R from 150 graded nulls — no normality assumption used.

## LAW E2 — what the worthless candidates scored

- nulls run: 150; **graded: 150** (0 were thinner than the 81-trade min-n and are could-not-look, the same rule the real candidates get)
- null expectancy: mean **+0.0304R**, sd 0.0125, max **+0.0619R**
- nulls clearing the +0.07R league bar: **0/150 (0%)**
- predicted-vs-observed: nulls behaved consistently with a genuine ~zero-edge cohort at this bar.

## Results

| bucket | count |
|---|---|
| **SURVIVORS** (n>=81 and expectancy >= +0.0700R) | **0** |
| INSUFFICIENT (n < 81 — could-not-look, NOT a rejection) | 0 |
| below the empirical bar | 1 |
| errored | 151 |

### No survivors.

This is a result, not a failure. The batch bought a real answer: on this family, universe and cost model, nothing beat a signal-free strategy once the funnel tax was paid. Record it and move to the next question.

## Honest limits of this batch

- Every candidate searched the SAME price history. K controls error within this batch; it does not undo the fact that earlier batches already searched this data. Project-lifetime K is the number that actually governs, and it only goes up.
- `bars/` holds what the data source serves today, so delisted names are absent. Any equity result here is optimistic by an amount nobody has measured.
- 151 candidates errored and are excluded; an excluded candidate is could-not-look, and it still counted toward K.
