"""
Plutus — copy-trade leaderboard collector (Q28 / Q29)
=====================================================

**Why a collector and not an analysis.** The Hyperliquid leaderboard reports four windows
per account — day, week, month, allTime — and they **NEST**: month contains week contains
day. Every shortcut for reading persistence out of ONE snapshot is therefore an artifact,
and both directions were measured on 2026-08-21 before this file was written:

    nested      month vs week            rank corr = **+0.831**   shared component ADDED
    subtracted  (month - week) vs week   rank corr = **-0.480**   shared component SUBTRACTED

They disagree in SIGN. The subtracted version is the more seductive because it looks
decontaminated, and it is worse: sorting by `month - week` literally selects for accounts
that had a large `week`, so its "bottom decile" showed an 88.6% positive rate and a
$202,005 median — a number produced entirely by its own construction. **Neither is
evidence. A single snapshot cannot answer this question at any sample size.**

Two snapshots at different times can, because they are genuinely independent measurements.
That is the entire reason this file exists.

**Kyle approved a WEEKLY cadence on Helios, 2026-08-21** (Rule 6: no timer without an
explicit yes). Weekly, not daily: the `week` window turns over in 7 days, so a faster
cadence re-reads the same number and buys resolution the source does not have.

**Identity is `ethAddress` and it is durable** — 43,141 unique addresses for 43,141 rows on
the t=0 snapshot; `displayName` is present on 3.3% and is ignored. That durability is what
makes an account followable across snapshots, and it is why Q30 came back SCRAPEABLE
against my registered prediction of OBSERVABLE-BUT-FRAGILE.

⚠ **The caveat this collector does NOT solve.** 43,141 is the size of the BOARD, not of
every Hyperliquid trader, and the board's inclusion rule is unmeasured. If accounts enter
on a volume or value threshold, the survivorship channel sits upstream of everything
collected here. Any result must say so.

⛔ Reads a public endpoint. No key, no account, no order — ever.

    python3 copytrade_collector.py            # one snapshot
    python3 copytrade_collector.py --check    # report what is on disk, fetch nothing
"""
import argparse
import datetime
import gzip
import json
import os
import sys
import urllib.request

_HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(_HERE, "datasets", "copytrade")
SRC = "https://stats-data.hyperliquid.xyz/Mainnet/leaderboard"
UA = "Plutus research kmiller3104@gmail.com"
MIN_ROWS = 1000          # a board this far below its observed 43k is a broken read, not a finding


def fetch():
    req = urllib.request.Request(SRC, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read()


def snapshot(out_dir=OUT_DIR):
    raw = fetch()
    blob = json.loads(raw)
    rows = blob.get("leaderboardRows") or []
    # THREE STATES. An empty or truncated board is COULD-NOT-LOOK — never a snapshot
    # recording that everyone left, which is what a silently-written short file would say.
    if len(rows) < MIN_ROWS:
        raise RuntimeError(f"could-not-look: leaderboard returned {len(rows)} rows "
                           f"(< {MIN_ROWS}); refusing to write a snapshot that would read "
                           f"as a real collapse")
    addrs = {r.get("ethAddress") for r in rows}
    if len(addrs) != len(rows):
        raise RuntimeError(f"could-not-look: {len(rows)} rows but {len(addrs)} distinct "
                           f"addresses — identity is the whole basis of following an account "
                           f"forward, so a duplicate address invalidates the snapshot")
    ts = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    out = {"fetched_at": ts, "source": SRC, "n_rows": len(rows),
           "note": "FULL board, not a top-N. ethAddress is the durable identity.",
           "rows": [{"addr": r["ethAddress"], "acct": r.get("accountValue"),
                     "perf": {k: v for k, v in r.get("windowPerformances", [])}}
                    for r in rows]}
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"hl_leaderboard_{ts[:10]}.json.gz")
    with gzip.open(path, "wt") as fh:
        json.dump(out, fh)
    return path, len(rows), os.path.getsize(path)


def on_disk(out_dir=OUT_DIR):
    if not os.path.isdir(out_dir):
        return []
    return sorted(f for f in os.listdir(out_dir) if f.endswith(".json.gz"))


def main(argv=None):
    ap = argparse.ArgumentParser(description="Hyperliquid leaderboard snapshot (Q28/Q29)")
    ap.add_argument("--check", action="store_true", help="report disk state, fetch nothing")
    ap.add_argument("--out", default=OUT_DIR)
    args = ap.parse_args(argv)

    have = on_disk(args.out)
    if args.check:
        print(f"snapshots on disk: {len(have)}")
        for f in have:
            print(f"  {f}")
        if len(have) < 2:
            print("\n  Only one snapshot. Q28 needs TWO at different times — a single one "
                  "cannot answer persistence, see this module's docstring.")
        return 0

    today = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    if f"hl_leaderboard_{today}.json.gz" in have:
        print(f"already have today's snapshot ({today}) — nothing to do")
        return 0
    try:
        path, n, size = snapshot(args.out)
    except Exception as e:                                       # noqa: BLE001
        print(f"COULD-NOT-LOOK: {e}", file=sys.stderr)
        return 1                                                 # loud: a missed week is a gap
    print(f"snapshot {os.path.basename(path)} — {n} rows, {size/1e6:.1f} MB gz "
          f"({len(have)+1} on disk)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
