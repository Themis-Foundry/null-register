#!/usr/bin/env python3
"""Generate index.json — the register's stable contract with anything that reads it.

A consumer that hardcodes `data/oddlot_census_119.json` breaks the day this repo
is reorganised, and it was: Entry 01 sat at the root until a second entry arrived
and everything moved under entries/. Nothing outside the repo had wired itself to
those paths yet, which was luck rather than design.

So the paths are published instead. Read index.json, follow `path`, and a future
restructure is a manifest change rather than a broken fetch. Every file carries
its size and SHA-256, so a consumer can tell "moved" from "changed" and cache
against the hash.

    python3 make_index.py            write index.json
    python3 make_index.py --check    verify it matches the tree, exit 1 if not
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).parent
SCHEMA = 1


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def title_of(readme):
    for line in readme.read_text().splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return readme.parent.name


def summary_of(readme):
    """The bold one-liner each entry opens with, which is its own summary."""
    m = re.search(r"^\*\*(.+?)\*\*", readme.read_text(), re.S | re.M)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else None


def build():
    entries = []
    for d in sorted((ROOT / "entries").iterdir()):
        if not d.is_dir():
            continue
        readme = d / "README.md"
        files = []
        for f in sorted((d / "data").rglob("*")) if (d / "data").is_dir() else []:
            if f.is_file():
                files.append({"name": f.name,
                              "path": str(f.relative_to(ROOT)),
                              "bytes": f.stat().st_size,
                              "sha256": sha(f)})
        e = {"id": d.name,
             "title": title_of(readme),
             "summary": summary_of(readme),
             "path": str(d.relative_to(ROOT)) + "/",
             "readme": str(readme.relative_to(ROOT)),
             "verify": str((d / "verify.py").relative_to(ROOT)),
             "data": files}
        for extra in ("diagram.svg", "reproduce.sh", "make_diagram.py"):
            if (d / extra).exists():
                e[extra.split(".")[0]] = str((d / extra).relative_to(ROOT))
        entries.append(e)

    corrections = re.findall(r"^## (\d+)\.\s*(.+)$",
                             (ROOT / "CORRECTIONS.md").read_text(), re.M)
    return {
        "schema": SCHEMA,
        "register": "The Null Register",
        "description": "Research that did not work, published with the same care "
                       "as research that did.",
        "repository": "https://github.com/kylemillerbuilds/null-register",
        "license": "See LICENSE. Sources are public filings and public APIs.",
        "note": "Paths are published here so consumers never hardcode them. "
                "Follow `path`; a restructure changes this file, not your code.",
        "verify_all": "reproduce.sh",
        "entries": entries,
        "corrections": {"count": len(corrections),
                        "path": "CORRECTIONS.md",
                        "titles": [t.strip() for _, t in
                                   sorted(corrections, key=lambda c: int(c[0]))]},
    }


def main():
    idx = build()
    out = ROOT / "index.json"
    text = json.dumps(idx, indent=2) + "\n"
    if "--check" in sys.argv:
        cur = out.read_text() if out.exists() else ""
        if cur != text:
            print("  FAIL  index.json does not match the tree. Run make_index.py.")
            sys.exit(1)
        n = sum(len(e["data"]) for e in idx["entries"])
        print(f"  PASS  index.json matches the tree: {len(idx['entries'])} entries, "
              f"{n} data files, every path and hash current")
        return
    out.write_text(text)
    print(f"wrote {out.name}: {len(idx['entries'])} entries, "
          f"{sum(len(e['data']) for e in idx['entries'])} data files")


if __name__ == "__main__":
    main()
