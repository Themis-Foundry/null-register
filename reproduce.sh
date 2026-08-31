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
exit $rc
