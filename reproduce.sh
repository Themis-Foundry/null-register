#!/usr/bin/env bash
# Regenerate every number published in The Null Register, Entry 01.
#   ./reproduce.sh            counts and arithmetic. Offline, instant.
#   ./reproduce.sh --claims   also checks every quote against the live SEC filing.
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "python3 not found"; exit 127; }
exec python3 verify.py "$@"
