# BATCH pilot-q16-momentum — verdict

`scored 2026-08-08T14:06:14 · question: Q16 — does the funnel tax hold in practice? (docs/QUESTIONS.md) · family: momentum`

## The gate that was applied

- **K (declared before grading): 9** real candidates, 20 nulls (block_bootstrap)
- LAW E1 min-n: **136 trades** (family-wise alpha 0.05 over K -> 5.56e-03 each)
- League promote bar: +0.07R
- **Empirical bar actually used: +0.1961R** (the strictest of: league bar, parametric null quantile +0.1961R, observed null max +0.1828R)
  - ⚠ the 0.99444 quantile needs ~180 nulls to observe directly; we ran 17, so the parametric figure stands in and it ASSUMES the null expectancies are roughly normal. **That assumption is known OPTIMISTIC**: batch q16-momentum-deep measured the real tail at +0.2255R where parametric predicted +0.1743R. The assumption-free observed max is included in the bar for exactly this reason — but a batch this thin should be read as a could-not-look on calibration, not a measurement.

## LAW E2 — what the worthless candidates scored

- nulls run: 20; **graded: 17** (3 were thinner than the 136-trade min-n and are could-not-look, the same rule the real candidates get)
- null expectancy: mean **+0.0938R**, sd 0.0403, max **+0.1828R**
- nulls clearing the +0.07R league bar: **12/17 (71%)**

### ⛔ BATCH VOID — the absolute bar is not a bar here

More than one null in five cleared +0.07R, so every 'survivor' below is reported against the EMPIRICAL bar only and none may be quoted against +0.07R.

**Measured cause: DRIFT CAPTURE — the null cohort's CENTRE sits above the league bar, so a signal-free rule on this family earns the bar just by holding a market that went up. The bar is measuring 'did you beat zero' when it should measure 'did you beat being long'.**

This is a finding about the bar, not a failure of the batch — and it is exactly what LAW E2 was built to catch.

## Results

| bucket | count |
|---|---|
| **SURVIVORS** (n>=136 and expectancy >= +0.1961R) | **0** |
| INSUFFICIENT (n < 136 — could-not-look, NOT a rejection) | 2 |
| below the empirical bar | 7 |
| errored | 0 |

### No survivors.

This is a result, not a failure. The batch bought a real answer: on this family, universe and cost model, nothing beat a signal-free strategy once the funnel tax was paid. Record it and move to the next question.

## Honest limits of this batch

- Every candidate searched the SAME price history. K controls error within this batch; it does not undo the fact that earlier batches already searched this data. Project-lifetime K is the number that actually governs, and it only goes up.
- `bars/` holds what the data source serves today, so delisted names are absent. Any equity result here is optimistic by an amount nobody has measured.
