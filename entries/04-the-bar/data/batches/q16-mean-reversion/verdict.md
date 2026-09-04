# BATCH q16-mean-reversion — verdict

`scored 2026-08-08T14:06:14 · question: Q16 — does the drift-capture finding generalise to a SECOND family? (docs/QUESTIONS.md) · family: mean_reversion`

## The gate that was applied

- **K (declared before grading): 6** real candidates, 30 nulls (block_bootstrap)
- LAW E1 min-n: **121 trades** (family-wise alpha 0.05 over K -> 8.33e-03 each)
- League promote bar: +0.07R
- **Empirical bar actually used: +0.5026R** (the strictest of: league bar, parametric null quantile +0.5026R, observed null max +0.3556R)
  - ⚠ the 0.99167 quantile needs ~120 nulls to observe directly; we ran 30, so the parametric figure stands in and it ASSUMES the null expectancies are roughly normal. **That assumption is known OPTIMISTIC**: batch q16-momentum-deep measured the real tail at +0.2255R where parametric predicted +0.1743R. The assumption-free observed max is included in the bar for exactly this reason — but a batch this thin should be read as a could-not-look on calibration, not a measurement.

## LAW E2 — what the worthless candidates scored

- nulls run: 30; **graded: 30** (24 were thinner than the 121-trade min-n and are could-not-look, the same rule the real candidates get)
- ⚠ **only 6 nulls cleared min-n, so the figures below fall back to ALL 30 nulls and the calibration is UNRELIABLE.** Treat this batch's empirical bar as could-not-look, not as a measurement.
- null expectancy: mean **-0.0176R**, sd 0.2173, max **+0.3556R**
- nulls clearing the +0.07R league bar: **8/30 (27%)**

### ⛔ BATCH VOID — the absolute bar is not a bar here

More than one null in five cleared +0.07R, so every 'survivor' below is reported against the EMPIRICAL bar only and none may be quoted against +0.07R.

**Measured cause: THIN-SAMPLE NOISE — the null cohort centres near zero (-0.0176R), so there is no drift story here; the passes come from DISPERSION (sd 0.2173). Candidates in this family trade rarely, and a handful of trades can clear any per-trade bar by luck. The cure is sample size, not a higher threshold.**

This is a finding about the bar, not a failure of the batch — and it is exactly what LAW E2 was built to catch.

## Results

| bucket | count |
|---|---|
| **SURVIVORS** (n>=121 and expectancy >= +0.5026R) | **0** |
| INSUFFICIENT (n < 121 — could-not-look, NOT a rejection) | 5 |
| below the empirical bar | 1 |
| errored | 0 |

### No survivors.

This is a result, not a failure. The batch bought a real answer: on this family, universe and cost model, nothing beat a signal-free strategy once the funnel tax was paid. Record it and move to the next question.

## Honest limits of this batch

- Every candidate searched the SAME price history. K controls error within this batch; it does not undo the fact that earlier batches already searched this data. Project-lifetime K is the number that actually governs, and it only goes up.
- `bars/` holds what the data source serves today, so delisted names are absent. Any equity result here is optimistic by an amount nobody has measured.
