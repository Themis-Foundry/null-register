# Corrections

Every entry here is an error this project made about its own data. They are published because a
research record with no corrections in it is not a research record.

## 8. A finished number moved, because the data underneath it kept growing

Entry 02's buyback study was run on 2026-08-18 and reported a placebo p of **0.700**.
Re-run on 2026-08-31 against the same code and the same seed, it reports **0.725**.

The p is an empirical count: of forty placebo runs, how many produced a mean at or
above the real one. 0.700 is 28 of 40. 0.725 is 29 of 40. **One placebo run crossed.**

The cause was found by experiment rather than assumed. The placebo moves each event to
a random date in its own stock's history, so the set of dates available to draw from
depends on how much history that stock has. Sixteen price files had been refreshed in
the meantime for unrelated work, gaining 33 trading days each. Truncating those files
back to their earlier state and re-running reproduces 0.700 exactly. Truncating only
the market benchmark does not, so the benchmark was ruled out.

The conclusion is untouched: both numbers say the same thing, which is that buyback
announcement dates are indistinguishable from random dates. **What moved is a
published figure, and a published figure that moves is a correction whether or not it
changes the answer.**

A second, smaller movement in the same study is *not* explained by that experiment.
The median return shifted in the fifth decimal and truncating the price files did not
restore it. The event corpus itself grew from 13,645 filings to 13,694 over the same
period. That is the likely cause and it has not been isolated, so it is stated here as
measured rather than as understood.

**The general point, which is why this correction is worth more than the number in
it:** a study is not finished when it is written up. Adjusted price history is
rewritten by every split and dividend, event corpora keep accruing, and a figure
computed against them has a date attached whether anyone wrote one down or not. The
five studies in Entry 02 were re-run before publication for exactly this reason, and
four of the five came back bit-identical.

## 7. The word "complete"

Earlier drafts of this README and of the register page said this was *a complete count* and that
it covered *every operating-company odd-lot tender offer* in the window. **Both were false.** The
sweep found 372 such filings, 210 carry the preference, and this census covers 119.

The 119 are the offers whose filer could be matched to a ticker with confidence, and 75 of the 91
left out failed exactly that check. The correct description is a **verified-identity subset**, and
the selection it introduces plausibly favours larger companies.

It was caught before publication by someone reading the claim and asking whether a decade of full
coverage was really in hand. It was not. **A project whose entire argument is that unverified
figures should not be trusted had an unverified figure in its opening sentence.**

## 6. Two offers were on the wrong side

**Alliance Data was published as a failure and is a success.** The census recorded 99,724 shares
tendered. The filing says **12,099,724**. The stored figure was parsed from a quote whose opening
had clipped the leading digits, and the same filing states a proration factor of 91.72%. Holders
were cut back.

**Cannae Holdings was published as a success and is a failure.** Its filing says *"there is no
proration factor"* and that all tendered shares were accepted.

The headline counts did not move, because the two errors ran in opposite directions. **The summary
statistic was correct the whole time while two of the rows underneath it were wrong**, and nothing
but row-level evidence could have shown it. Every other resolved offer was tested for the same
truncation defect. Alliance Data was the only one.

## 5. Seven offers had no share count to begin with

The census originally carried a shares-sought figure for every offer. For dollar-denominated
auctions that figure was a derived convenience, not something the filing states: Qualcomm's offer
commits to $10bn, Altice's to $2.5bn, Valvoline's to $1bn, and the share count follows from
wherever the price lands. Those rows now record the dollar amount and leave the share count empty.
No classification changed.

## 4. The percentage column

An earlier version expressed each result as a percentage of shares sought. **The denominator is not
sound.** In a Dutch auction the company states how many shares it would buy at a reference price
and settles elsewhere, and SEC rules let a company purchase an additional 2% of its outstanding
stock without amending the offer. Recomputed at its settled price, Valvoline reads as 102%
subscribed, which would have flipped it out of the failure list. Its own filing says there is no
proration factor. **The filing outranks the arithmetic.** The column was removed.

## 3. The Robin Energy arithmetic

An internal audit flagged one row as impossible: shares sought exactly equalled shares tendered.
The audit was wrong. That field holds shares *accepted*, and sought equalling accepted is exactly
what a heavily prorated offer looks like. **The audit ran an arithmetic test on a mislabelled
quantity while auditing for that exact mistake.**

## 2. The survivorship explanation

A block of 28 offers had no recorded outcome, and the working hypothesis was survivorship bias.
Accounting for all 28 individually refuted it: thirteen were funds, three were share exchanges,
three had no odd-lot preference, five resolved on re-examination, two were too recent and two
remain open. Nineteen had never been candidates. **A cohort error wearing a survivorship costume.**

## 1. The 60% base rate

An earlier pass reported that roughly 60% of resolved odd-lot tenders were oversubscribed. That
figure was measured across three instruments, only one of which carries an odd-lot premium at all.
Restricted to the real instrument the honest answer became a 44-point band. **The original number
was not biased. Its denominator was the wrong population.**
