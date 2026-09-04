# Corrections

Every entry here is an error this project made about its own data. They are published because a
research record with no corrections in it is not a research record.

## The flip log

Ten reversals, newest first. Each one leaves the original claim standing next to what replaced it.
`reproduce.sh` counts these headings and fails if the front page says a different number.

| # | entry | what was published | what stands now |
|---|---|---|---|
| 10 | 02 | the S&P deletion rebound *worked, then stopped* | neither era clears zero; the eras differ (+16.4%, interval +0.4% to +35.4%, the thinnest result here) |
| 9 | 02 | one 95% interval, two different values | each figure now seeds its own generator, so any one can be re-derived alone |
| 8 | 02 | buyback placebo p = 0.700 | 0.725; one placebo run crossed because the price history grew under a finished study |
| 7 | 01 | *a complete count* of every qualifying offer | a verified-identity subset: 372 filings, 210 with the preference, 119 reached |
| 6 | 01 | Alliance Data a failure, Cannae a success | the reverse of both; the headline count never moved while two rows under it were wrong |
| 5 | 01 | a shares-sought figure on every offer | seven dollar-denominated auctions state no share count; the column is empty for them |
| 4 | 01 | each result as a percentage of shares sought | column removed; the denominator is not sound and the filing outranks the arithmetic |
| 3 | 01 | an audit called one row impossible | the audit was wrong; it tested a mislabelled quantity while auditing for that mistake |
| 2 | 01 | 28 missing outcomes explained as survivorship | accounted for one by one: nineteen were never candidates |
| 1 | 01 | ~60% of resolved odd-lot tenders oversubscribed | a 44-point band; the denominator was the wrong population |

## 10. "It worked" was a claim the data did not support

Entry 02 called the S&P deletion rebound **the one that worked, and then stopped**, on a mean of
+12.4% from 2016 to 2020 against −3.9% from 2021 to 2026. The page disclosed that the first era's
interval runs from −1.7% to +30.5% and contains zero, and then went on calling it a win anyway.

**An external audit caught it.** Its argument was simple and correct: a mean whose interval
contains zero is not distinguishable from zero, so "it worked" is not available, and what was left
looked like a story told over noise.

Half right, and the other half needed a number neither side had computed. **The gap between the
eras is +16.4%, with a 95% interval of +0.4% to +35.4% that excludes zero**, and 97.7% of
resamples put the earlier era ahead. So the eras do differ. What cannot be claimed is that either
one was profitable.

The entry now makes a difference claim instead of a level claim, which is what the pre-registered
test was measuring in the first place: whether the effect repeats out of sample. It did not.

⚠ **That interval clears zero by 0.4 points**, which is the thinnest result in this register and
is labelled as such on the page. One more quiet year either way moves it.

**The auditor's other headline finding was wrong**, and it is recorded here because a correction
file that only carries our own errors would be a strange kind of record. It reported that Q10's
"the placebo beats the real dates" is inverted, having read `mean_ar_single` (+1.31%) as the
placebo. The placebo is a separate 40-run computation whose mean spread is +2.28% against the real
spread of +0.52%. The claim stands.

## 9. A confidence interval that depended on the order the code ran

Entry 02's diagram and its verifier both bootstrap the same intervals from the same
rows at the same fixed seed, and they disagreed. The era that worked read −2.0% to
+30.5% in one and −1.7% to +29.3% in the other.

Neither was corrupt. Both drew from **one** random number generator seeded once at the
start of the run, so each interval depended on how many draws had already happened
before it. The diagram computes four other quantities first. The verifier computes
this one first. Same seed, same data, different position in the stream, different
answer.

**An interval that changes depending on what the program did beforehand is not
reproducible, and calling it a 95% interval is a stronger claim than the code was
making.** Both now seed a separate generator per quantity, keyed to that quantity's
own name, so any figure can be re-derived alone and matches the full run exactly.

Caught before publication, by the verifier disagreeing with the picture. **Neither
would have caught it alone**, which is the argument for having a checker that is not
the thing it checks.

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
