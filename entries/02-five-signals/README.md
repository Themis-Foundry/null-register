# Entry 02 — Five signals everyone repeats, measured

**Five things retail investors are told to trade, each measured against a placebo on
the whole cohort rather than a chosen slice. One of them worked and then stopped.
The other four were never there.**

---

![Return against the market for each signal, with a 95% interval drawn. Four of the five bars have an interval crossing zero. The S&P deletion rebound is far to the right for 2016 to 2020 and to the left of zero for 2021 to 2026](diagram.svg)

### If none of these terms mean anything to you, start here

Every one of these five is a rule of thumb you can find repeated in a thousand
places: buy when insiders buy, buy when a company announces a buyback, buy a stock
that just got kicked out of the S&P 500, and so on. They sound like they should
work, and each has a story attached explaining why.

**A story is not evidence, and neither is a backtest that only ever ran once.** The
question is whether the thing beats the same stocks on random dates. If a signal
does no better than throwing darts at the calendar, then what you measured was the
stocks, not the signal.

That comparison is called a placebo, and it is the whole method here. Every study
below moves each event to a random date in that same stock's own history, forty
times, and asks whether the real dates did anything the random ones did not.

**Four of the five did not.** The fifth did, for five years, and then stopped.

---

## The one whose behaviour changed

### Q12 — buying S&P 500 deletions

When a company is dropped from the S&P 500, index funds have to sell it whether they
want to or not. The stock gets pushed down by forced selling, and the trade is to buy
that push and wait for it to come back.

**The push is real.** Across 114 removals from 2016 to 2026, the stock falls 4.2% in
the twenty trading days into the deletion date, against the market.

**The rebound was real too, and then it went away.**

| era | mean return after, vs SPY, 120 trading days | 95% interval |
|---|---:|---:|
| 2016 to 2020 | **+12.4%** | −1.7% to +30.5% |
| 2021 to 2026 | **−3.9%** | −10.4% to +2.5% |

If you had run this from 2016 to 2020 you would have made about 12% a trade over the
market. If you read about it in 2021 and ran it since, you lost about 4%. Same rule,
same cohort construction, opposite answer, and nothing in the strategy changed.

**Read the intervals before the averages, because they change the claim.** Neither era
is distinguishable from zero on its own: 2016 to 2020 runs from −1.7% to +30.5%, and 2021
to 2026 from −10.4% to +2.5%. **So "it worked" is not a claim this data supports**, and an
earlier version of this page made it anyway.

**What the data does support is that the two eras differ.** The gap between them is
**+16.4%**, with a 95% interval of **+0.4% to +35.4%** that excludes zero, and 97.7% of
resamples put the earlier era ahead. That is the finding: not that the strategy paid, but
that whatever it was doing in the first era it stopped doing in the second.

⚠ **That interval clears zero by 0.4 points.** It is the thinnest result in this register
and one more quiet year either way would move it. Treated as suggestive, not settled.

Two things worth knowing before you take even that much:

- **It was only ever the demotions.** Companies dropped because they got too small
  returned +7.6%. Companies dropped because they were being acquired returned −10.8%.
  Lumping them together makes an average that describes neither.
- **The dead names are missing, and that flatters the era that worked.** 227 companies
  were removed. 83 of them have no usable price history, mostly because they were
  bought or wound up, and those are disproportionately the ones that never came back.

The pooled result across both eras is positive and clears a placebo at p=0.025. **Do
not read that as a live edge.** A signal that works in one half of the sample and
fails in the other has failed the only test that matters, which is whether it repeats
on data it has not seen.

---

## The four that were never there

### Q10 — the "three insiders are buying" screener

The idea: one executive buying stock might mean nothing, but three of them buying in
the same fortnight is a cluster, and a cluster means they know something.

Measured across 24,021 events, entry the day after the filing, held 60 trading days
against SPY:

| | events | mean return vs SPY |
|---|---:|---:|
| cluster, three or more insiders | 6,511 | +1.82% |
| single insider | 17,510 | +1.31% |

**A spread of 0.52%, and its confidence interval runs from −2.9% to +3.0%.** Zero sits
in the middle of it.

**The placebo is the finding.** Move every one of those events to a random date in the
same stock's own history and the "edge" comes out at **+2.28%**, which is larger than
the real one. What the cluster bucket measures is which companies end up in it, not
when their insiders bought.

And the story fails hardest exactly where it is told loudest. Among the stocks that
had fallen the most over the previous 60 days, the tercile where "insiders are buying
the dip" is the whole pitch, clusters underperform singles by **3.75%**.

### Q8 — buyback announcements

The idea: a company announcing it will buy its own shares is telling you the stock is
cheap, and you should buy alongside it.

9,470 announcements, 2016 to 2026:

| | |
|---|---:|
| mean return vs SPY, 60 trading days | **−0.13%** |
| median | **−0.90%** |
| share that beat SPY | **47.4%** |

Fewer than half beat the market, and the random-date placebo is statistically
indistinguishable from the real announcement dates.

This does not contradict the academic work on multi-year buyback drift. It says that
at the horizon a retail investor would actually trade, over this decade, the
announcement itself is worth nothing.

**The first version of this study printed +3.41%, and it was one stock.**

CBL is a shopping-mall landlord that went through bankruptcy and re-listed. The price
series records a single day where the close goes from $0.06 to $20.88, a factor of
335.69, and that day sits inside one outcome window. One broken series out of 9,473
events manufactured the entire result.

The fix is a screen that rejects any event whose outcome window contains a single-day
move outside a factor of 0.25 to 4. It has to be symmetric, because it cannot be
allowed to know which direction it is protecting. It fired three times in 9,473, and
all three are in the data with their dates and factors:

| ticker | announcement | would have booked | the break |
|---|---|---:|---|
| TGNA | 2017-05-09 | −84% | 0.22× in a day, Cars.com spinoff |
| CNX | 2017-10-31 | −100% | 0.10× in a day, CONSOL spinoff |
| CBL | 2021-10-18 | **+33,707%** | 335.69× in a day, bankruptcy re-listing |

**Not one of those is a return anybody earned.** They are the same security changing
identity underneath a ticker that stayed the same.

### Q9 — the rights-offering dip

The idea, from the textbook: a company announcing a rights offering is diluting its
existing shareholders, the stock sells off into it, and part of that comes back
afterwards. Sell into it, buy the relief.

3,144 offerings. **Both halves of that shape are wrong.**

Stocks run **up** into the filing, +4.41% over the ten days before it, and they do it
in both halves of the sample: +5.68% from 2016 to 2020, +3.32% from 2021 to 2026.

The mean is +4.41% while the median is −0.35%, and that gap is the explanation. A
minority of small companies spike hard and then sell equity into the spike. **Issuers
time offerings after strength.** They are not getting caught by weakness.

The leg after the filing is negative, −3.64%, but it flips sign between the halves,
so there is no stable claim on that side either, long or short.

### Q11 — extreme funding rates in crypto

The idea: when the funding rate on perpetual futures gets extreme, the crowd is too
far on one side, and price is about to go the other way.

This one was registered properly in advance, with a survival condition set before
anything was measured: the effect had to hold in **both** the 2021 bull market and the
2022 bear market. 7,358 funding prints for Bitcoin and 7,124 for Ether, back to the
first day each contract existed.

**Bitcoin fails its own test immediately.** In 2021, extreme positive funding was
followed by *higher* returns than average, at every horizon. That is the opposite of
the registered direction.

**Ether is the one that should worry you.** It passed 2021. It passed 2022. It passed
at all three horizons in both. Then, in the 2024 to 2026 window that was never part of
the test:

| forward horizon | after extreme funding | everything |
|---|---:|---:|
| 8 hours | +0.19% | +0.02% |
| 24 hours | +0.50% | +0.05% |
| 72 hours | +1.10% | +0.14% |

Every horizon reversed. **Had this been registered and tested in January 2024, it
would have read as confirmed, and then it would have bled.** That is not a
hypothetical about overfitting. It is what the pre-registration caught, on this data,
by demanding a window the analyst did not choose.

---

## How to check this without trusting me

```bash
./verify.py             # recompute every figure above. Offline, no key, instant.
```

Every study here ships the rows it scored, one JSON object per line, including the
ones it threw out and why. `verify.py` recomputes each published number from those
rows and prints it beside what this page claims.

**Entry 01 of this register published the sentences its verdicts were read from and
deliberately withheld the pipeline. This entry does the opposite on purpose.** When
the evidence is a sentence in a filing, hand over the sentence. When the evidence is a
computation across 24,000 events, the computation *is* the evidence, and a summary
statistic with nothing underneath it is the exact kind of claim this register exists
to refuse.

**The checker is built to fail.** It corrupts the data four ways at the end of every
run: alters one return, drops one row, flips one bucket label, removes one funding
print. Each corruption must be caught. If the checker cannot be made to say no, it
exits non-zero rather than reporting a pass it has not earned.

## What is deliberately not here

**The daily price bars.** They come from a market-data vendor and are not mine to
redistribute. That is why verification is in two tiers rather than one: the rows are
the evidence and they are here, and `instruments/` holds the exact code that produced
them so you can point it at your own bars and regenerate.

**Anything about the crypto funding data beyond the analysed cohort.** The raw feed
came from a public exchange API. What ships here is the cohort as analysed, with the
forward returns computed.

## Files

```
data/q8_events.jsonl        9,470 scored events plus the 3 thrown out, with the reason
data/q9_events.jsonl        3,144 scored plus 25 thrown out
data/q10_events.jsonl       24,021 events, tagged cluster or single
data/q11_btc_events.jsonl   7,358 funding prints with forward returns and decile bucket
data/q11_eth_events.jsonl   7,124 the same
data/q12_events.jsonl       114 removals with both legs and the reason for the removal
data/summaries/             the study artifacts, which verify.py checks the rows against
data/cohorts/               the event lists these were built from, all public filings
instruments/                the exact code that produced every row above
verify.py                   recomputes every figure, and can be made to fail
make_diagram.py             redraws diagram.svg from the rows above, deterministically
```

Every study was registered with its direction and its bar stated in advance, and every
one carries a fixed seed set at registration rather than tuned afterwards.

## Corrections

In [CORRECTIONS.md](../../CORRECTIONS.md) at the root, numbered across the whole
register. Correction 8 belongs to this entry, and it is about a figure on this page
that moved after it was first measured.
