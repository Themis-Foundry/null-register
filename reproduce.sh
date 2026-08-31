#!/usr/bin/env bash
# Regenerate and check every number published in The Null Register, every entry.
#   ./reproduce.sh            counts and arithmetic. Offline, instant.
#   ./reproduce.sh --claims   Entry 01 also fetches each cited SEC filing and
#                             proves the quoted sentence is in it.
# A non-zero exit means a published figure no longer matches its own evidence.
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "python3 not found"; exit 127; }
rc=0
for entry in entries/*/; do
  echo
  echo "################ ${entry}"
  python3 "${entry}verify.py" "$@" || rc=$?
done

# The front page says how many corrections there are. Counted here rather than
# trusted, because a number typed next to the thing it counts stops being true
# the moment the thing changes.
echo
echo "################ the register itself"
python3 - <<'PY' || rc=$?
import re, sys
words = {1:"one",2:"two",3:"three",4:"four",5:"five",6:"six",7:"seven",8:"eight",
         9:"nine",10:"ten",11:"eleven",12:"twelve"}
n = len(re.findall(r"^## (\d+)\.", open("CORRECTIONS.md").read(), re.M))
readme = open("README.md").read()
claimed = re.search(r"CORRECTIONS\.md\) — (\w+) of them", readme)
ok = claimed and claimed.group(1).lower() == words.get(n)
print(f"  {'PASS' if ok else 'FAIL'}  corrections: {n} in the file, README says "
      f"{claimed.group(1) if claimed else 'nothing'}")
if not ok:
    sys.exit(1)
nums = sorted(int(m) for m in re.findall(r"^## (\d+)\.", open("CORRECTIONS.md").read(), re.M))
gap = nums != list(range(1, n + 1))
print(f"  {'FAIL' if gap else 'PASS'}  numbering is 1..{n} with no gaps or repeats")
sys.exit(1 if gap else 0)
PY
exit $rc
