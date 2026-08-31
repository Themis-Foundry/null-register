"""
Plutus — Q29: the gap between a LEADER's fill and a COPIER's fill
=================================================================

**The question that decides whether copy-trading is income or trivia.** A leaderboard
reports the leader's fills. A copier enters *after* the leader, into a price the leader's
own flow just moved, and pays fees on top. **A strategy can be genuinely profitable for the
leader and negative for every copier**, and no leaderboard anywhere reports that gap.

**Method.** For each leader fill at time T and price P on coin C, read the 1-minute candles
around T and take the price a copier would realistically have paid at a lag of +1m and +5m.
The gap is signed AGAINST the copier: for a buy, paying more is a loss; for a sell,
receiving less is a loss. Reported in basis points of the fill price.

    gap_bps = 10_000 * (P_lag - P) / P * (+1 if side is BUY else -1)

**Three states, never two.** A fill whose candle window cannot be read is `could_not_look`
and is counted separately — never folded into the median as a zero.

⚠ **What this measures and what it does not.** It measures the price move over the copier's
latency, which is the dominant term and the one nobody publishes. It does NOT model order
book depth, so a copier moving size into a thin book does strictly worse than this. **This
is therefore a LOWER BOUND on the gap.** Fees are reported separately rather than assumed,
because they depend on the copier's own tier.

⚠ **Selection.** Run against wallets that are actually live — carrying open positions and
recent fills. Measured 2026-08-21: **14 of the top 20 leaderboard wallets return ZERO fills
and their live `accountValue` is 0 while the board advertises hundreds of millions**, so the
head of the board is not a copyable population and cannot be sampled here.

⛔ Public endpoints only. No key, no account, no order.

    python3 copytrade_slippage.py --wallets 8 --fills 40
"""
import argparse
import json
import statistics
import sys
import time
import urllib.request

API = "https://api.hyperliquid.xyz/info"
UA = {"User-Agent": "Plutus research kmiller3104@gmail.com",
      "Content-Type": "application/json"}
LAGS_MS = {"+1m": 60_000, "+5m": 300_000}


def post(body, retry=2):
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=45).read())
        except Exception as e:                                   # noqa: BLE001
            if i == retry:
                return {"_err": str(e)[:80]}
            time.sleep(1.5)


def candles(coin, start_ms, end_ms):
    r = post({"type": "candleSnapshot",
              "req": {"coin": coin, "interval": "1m",
                      "startTime": int(start_ms), "endTime": int(end_ms)}})
    return r if isinstance(r, list) else []


def price_at(cs, t_ms):
    """Close of the last 1m candle that has CLOSED at or before t_ms.

    A copier cannot trade at a price that has not printed yet, so this deliberately
    looks BACKWARD. Using the containing candle's close would let the copier trade on
    information from the future of their own fill.
    """
    best = None
    for c in cs:
        if c["T"] <= t_ms:
            if best is None or c["T"] > best["T"]:
                best = c
    return float(best["c"]) if best else None


def measure_wallet(addr, max_fills):
    fills = post({"type": "userFills", "user": addr})
    if not isinstance(fills, list) or not fills:
        return None
    # Entries only: a copier mirrors opens. Closes carry the leader's own exit timing.
    ent = [f for f in fills if str(f.get("dir", "")).lower().startswith("open")][:max_fills]
    if not ent:
        ent = fills[:max_fills]
    by_coin = {}
    for f in ent:
        by_coin.setdefault(f["coin"], []).append(f)
    out = {"addr": addr, "gaps": {k: [] for k in LAGS_MS}, "n_fills": 0, "could_not_look": 0}
    for coin, fs in by_coin.items():
        lo = min(f["time"] for f in fs) - 120_000
        hi = max(f["time"] for f in fs) + max(LAGS_MS.values()) + 120_000
        cs = candles(coin, lo, hi)
        time.sleep(0.25)
        if not cs:
            out["could_not_look"] += len(fs)
            continue
        for f in fs:
            p = float(f["px"])
            sign = 1.0 if f.get("side") == "B" else -1.0
            got = False
            for lab, lag in LAGS_MS.items():
                q = price_at(cs, f["time"] + lag)
                if q is None or p <= 0:
                    continue
                out["gaps"][lab].append(10_000.0 * (q - p) / p * sign)
                got = True
            out["n_fills"] += 1 if got else 0
            out["could_not_look"] += 0 if got else 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description="Q29 leader-vs-copier slippage")
    ap.add_argument("--wallets", type=int, default=8)
    ap.add_argument("--fills", type=int, default=40)
    ap.add_argument("--snapshot", default="datasets/copytrade/hl_leaderboard_2026-08-21.json.gz")
    ap.add_argument("--out", default="strategies/_data/q29_slippage.json")
    args = ap.parse_args(argv)

    import gzip, os
    here = os.path.dirname(os.path.abspath(__file__))
    snap = json.load(gzip.open(os.path.join(here, args.snapshot), "rt"))
    rows = [r for r in snap["rows"] if r["perf"].get("month")]
    rows.sort(key=lambda r: -float(r["perf"]["month"]["pnl"]))

    picked, results = [], []
    for r in rows:
        if len(picked) >= args.wallets:
            break
        cs = post({"type": "clearinghouseState", "user": r["addr"]})
        time.sleep(0.25)
        live = (isinstance(cs, dict) and cs.get("assetPositions")
                and float(cs["marginSummary"]["accountValue"]) > 1000)
        if not live:
            continue
        m = measure_wallet(r["addr"], args.fills)
        if m and m["n_fills"] >= 5:
            m["month_pnl"] = float(r["perf"]["month"]["pnl"])
            m["rank"] = rows.index(r) + 1
            picked.append(r["addr"])
            results.append(m)
            print(f"  wallet {len(picked)}/{args.wallets} rank {m['rank']} "
                  f"month ${m['month_pnl']:,.0f} — {m['n_fills']} fills", flush=True)

    if not results:
        print("COULD-NOT-LOOK: no live wallet yielded enough fills", file=sys.stderr)
        return 1
    print("\n" + "=" * 72)
    summary = {"wallets": len(results), "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    for lab in LAGS_MS:
        allg = [g for m in results for g in m["gaps"][lab]]
        if not allg:
            continue
        allg.sort()
        summary[lab] = {"n": len(allg), "median_bps": round(statistics.median(allg), 2),
                        "mean_bps": round(statistics.fmean(allg), 2),
                        "pct_against_copier": round(100 * sum(1 for g in allg if g > 0) / len(allg), 1),
                        "p90_bps": round(allg[int(0.9 * len(allg)) - 1], 2)}
        s = summary[lab]
        print(f"  lag {lab}: n={s['n']:5d}  median {s['median_bps']:+7.2f} bps  "
              f"mean {s['mean_bps']:+7.2f}  worse-for-copier {s['pct_against_copier']:5.1f}%  "
              f"p90 {s['p90_bps']:+7.2f}")
    summary["could_not_look"] = sum(m["could_not_look"] for m in results)
    print(f"\n  could-not-look fills (candle window unreadable): {summary['could_not_look']}")
    print("  ⚠ LOWER BOUND — no book depth modelled, and fees are on top.")
    op = os.path.join(here, args.out)
    with open(op, "w") as fh:
        json.dump({"summary": summary, "wallets": results}, fh, indent=2)
    print(f"  → {op}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
