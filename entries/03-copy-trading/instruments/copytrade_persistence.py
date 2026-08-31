"""
Plutus — Q28: does a leaderboard leader's performance PERSIST?
==============================================================

**Why this does not use the leaderboard.** The board's four windows NEST — month contains
week contains day — so every single-snapshot shortcut is an artifact, and both were measured
on 2026-08-21 before this file existed: nested (month vs week) `+0.831` because the shared
component is added, subtracted ((month−week) vs week) `−0.480` because it is removed. They
disagree in SIGN. The subtracted form is the more dangerous, because sorting by `month−week`
literally selects for accounts that had a big week; its "bottom decile" showed 88.6% positive
and a $202,005 median, produced entirely by its own construction.

**So this measures from FILLS instead.** `userFillsByTime` pages past the 2000-fill cap, so a
per-wallet realized-PnL series can be rebuilt over genuinely disjoint calendar days. Realized
PnL is `closedPnl` on closing fills; `fee` is subtracted on every fill, opens included,
because a copier pays it either way.

**The test:** fix ONE calendar window, split it in half, and rank-correlate each wallet's
early-half PnL against its late-half PnL across wallets. Disjoint periods, no shared
component, no subtraction. This is the thing the board cannot do.

⚠ **A COMMON WINDOW IS MANDATORY, and it is the trap in this data.** The 2000-fill cap bites
hardest on the most active accounts — measured coverage ran from **0.11 days to 185 days**,
inversely related to activity. Comparing wallets over different real durations would compare
a day of one trader against a month of another and call the difference skill. Wallets without
fills in BOTH halves are EXCLUDED AND COUNTED, never silently dropped.

⛔ Public endpoints only. No key, no account, no order.

    python3 copytrade_persistence.py --days 14
"""
import argparse
import datetime
import json
import os
import statistics
import sys
import time
import urllib.request

API = "https://api.hyperliquid.xyz/info"
UA = {"User-Agent": "Plutus research kmiller3104@gmail.com",
      "Content-Type": "application/json"}
CHUNK_MS = 2 * 86_400_000          # walk back in 2-day chunks; the cap is per response
MAX_HOPS = 14


def post(body, retry=2):
    for i in range(retry + 1):
        try:
            req = urllib.request.Request(API, data=json.dumps(body).encode(), headers=UA)
            return json.loads(urllib.request.urlopen(req, timeout=45).read())
        except Exception as e:                                   # noqa: BLE001
            if i == retry:
                return {"_err": str(e)[:80]}
            time.sleep(1.5)


def fills_window(addr, start_ms, end_ms):
    """Every fill in [start, end], walking back so the 2000-cap cannot truncate the window."""
    out, cur, hops = [], end_ms, 0
    while cur > start_ms and hops < MAX_HOPS:
        lo = max(start_ms, cur - CHUNK_MS)
        r = post({"type": "userFillsByTime", "user": addr,
                  "startTime": int(lo), "endTime": int(cur)})
        time.sleep(0.3)
        if not isinstance(r, list):
            return None                                          # could-not-look, not "no fills"
        out.extend(r)
        if len(r) >= 2000:
            # the chunk itself hit the cap: this window is not fully observed
            cur = min(x["time"] for x in r) - 1
        else:
            cur = lo - 1
        hops += 1
    seen, uniq = set(), []
    for f in out:
        k = (f.get("tid"), f.get("time"), f.get("hash"))
        if k not in seen:
            seen.add(k)
            uniq.append(f)
    return uniq


def net_pnl(fs):
    """Realized PnL net of fees. Opens contribute their fee only — a copier pays it too."""
    return sum(float(f.get("closedPnl") or 0) - float(f.get("fee") or 0) for f in fs)


def spearman(a, b):
    ra = sorted(range(len(a)), key=lambda i: a[i])
    rb = sorted(range(len(b)), key=lambda i: b[i])
    x = [0] * len(a); y = [0] * len(a)
    for i, v in enumerate(ra): x[v] = i
    for i, v in enumerate(rb): y[v] = i
    mx, my = statistics.mean(x), statistics.mean(y)
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    den = (sum((xi - mx) ** 2 for xi in x) * sum((yi - my) ** 2 for yi in y)) ** 0.5
    return num / den if den else None


def main(argv=None):
    ap = argparse.ArgumentParser(description="Q28 persistence from fills")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--wallets", default="strategies/_data/q29_slippage_n32.json")
    ap.add_argument("--out", default="strategies/_data/q28_persistence.json")
    args = ap.parse_args(argv)

    here = os.path.dirname(os.path.abspath(__file__))
    src = json.load(open(os.path.join(here, args.wallets)))
    addrs = [w["addr"] for w in src["wallets"]]

    now = int(time.time() * 1000)
    start = now - args.days * 86_400_000
    mid = start + (now - start) // 2
    rows, excluded = [], {"could_not_look": 0, "no_fills_both_halves": 0}

    for i, a in enumerate(addrs, 1):
        fs = fills_window(a, start, now)
        if fs is None:
            excluded["could_not_look"] += 1
            continue
        early = [f for f in fs if start <= f["time"] < mid]
        late = [f for f in fs if mid <= f["time"] <= now]
        if not early or not late:
            excluded["no_fills_both_halves"] += 1
            continue
        rows.append({"addr": a, "n_early": len(early), "n_late": len(late),
                     "pnl_early": net_pnl(early), "pnl_late": net_pnl(late)})
        print(f"  {i}/{len(addrs)} {a[:12]}… early ${net_pnl(early):>14,.0f} "
              f"late ${net_pnl(late):>14,.0f}", flush=True)

    if len(rows) < 5:
        print(f"COULD-NOT-LOOK: only {len(rows)} wallets covered both halves "
              f"({excluded}) — not a persistence result", file=sys.stderr)
        return 1

    e = [r["pnl_early"] for r in rows]
    l = [r["pnl_late"] for r in rows]
    rho = spearman(e, l)
    n = len(rows)
    med_e = statistics.median(e)
    top = [r for r in rows if r["pnl_early"] > med_e]
    bot = [r for r in rows if r["pnl_early"] <= med_e]
    top_pos = sum(1 for r in top if r["pnl_late"] > 0)
    bot_pos = sum(1 for r in bot if r["pnl_late"] > 0)

    win = f"{datetime.datetime.utcfromtimestamp(start/1000):%Y-%m-%d} → {datetime.datetime.utcfromtimestamp(now/1000):%Y-%m-%d}"
    summary = {"window": win, "days": args.days, "wallets_in": len(addrs),
               "wallets_measured": n, "excluded": excluded,
               "spearman_early_vs_late": round(rho, 3) if rho is not None else None,
               "top_half_positive_late": f"{top_pos}/{len(top)}",
               "bottom_half_positive_late": f"{bot_pos}/{len(bot)}",
               "median_late_pnl_top_half": round(statistics.median([r["pnl_late"] for r in top]), 2),
               "median_late_pnl_bottom_half": round(statistics.median([r["pnl_late"] for r in bot]), 2)}
    print("\n" + "=" * 72)
    print(f"  window {win}  (two DISJOINT halves of {args.days/2:.1f} days each)")
    print(f"  wallets measured {n} of {len(addrs)}   excluded {excluded}")
    print(f"  rank correlation early-half vs late-half PnL: {summary['spearman_early_vs_late']}")
    print(f"  top half by early PnL   → positive late: {top_pos}/{len(top)}  "
          f"median ${summary['median_late_pnl_top_half']:,.0f}")
    print(f"  bottom half by early PnL→ positive late: {bot_pos}/{len(bot)}  "
          f"median ${summary['median_late_pnl_bottom_half']:,.0f}")
    with open(os.path.join(here, args.out), "w") as fh:
        json.dump({"summary": summary, "rows": rows}, fh, indent=2)
    print(f"  → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
