# BATCH league-check-momentum — verdict

`scored 2026-08-08T14:06:14 · question: Q16 — is the league momentum PROMOTE distinguishable from a signal-free strategy? · family: momentum`

## The gate that was applied

- **K (declared before grading): 1** real candidates, 40 nulls (block_bootstrap)
- LAW E1 min-n: **57 trades** (family-wise alpha 0.05 over K -> 5.00e-02 each)
- League promote bar: +0.07R
- **Empirical bar actually used: +0.3040R** (the strictest of: league bar, parametric null quantile +0.2525R, observed null max +0.3040R)
  - the 0.95000 quantile was **OBSERVED directly** at +0.2769R from 40 graded nulls — no normality assumption used.

## LAW E2 — what the worthless candidates scored

- nulls run: 40; **graded: 40** (0 were thinner than the 57-trade min-n and are could-not-look, the same rule the real candidates get)
- null expectancy: mean **+0.1686R**, sd 0.0510, max **+0.3040R**
- nulls clearing the +0.07R league bar: **39/40 (98%)**

### ⛔ BATCH VOID — the absolute bar is not a bar here

More than one null in five cleared +0.07R, so every 'survivor' below is reported against the EMPIRICAL bar only and none may be quoted against +0.07R.

**Measured cause: DRIFT CAPTURE — the null cohort's CENTRE sits above the league bar, so a signal-free rule on this family earns the bar just by holding a market that went up. The bar is measuring 'did you beat zero' when it should measure 'did you beat being long'.**

This is a finding about the bar, not a failure of the batch — and it is exactly what LAW E2 was built to catch.

## Results

| bucket | count |
|---|---|
| **SURVIVORS** (n>=57 and expectancy >= +0.3040R) | **0** |
| INSUFFICIENT (n < 57 — could-not-look, NOT a rejection) | 0 |
| below the empirical bar | 1 |
| errored | 0 |

### No survivors.

This is a result, not a failure. The batch bought a real answer: on this family, universe and cost model, nothing beat a signal-free strategy once the funnel tax was paid. Record it and move to the next question.

## Honest limits of this batch

- Every candidate searched the SAME price history. K controls error within this batch; it does not undo the fact that earlier batches already searched this data. Project-lifetime K is the number that actually governs, and it only goes up.
- `bars/` holds what the data source serves today, so delisted names are absent. Any equity result here is optimistic by an amount nobody has measured.
