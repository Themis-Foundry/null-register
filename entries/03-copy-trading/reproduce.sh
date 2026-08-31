#!/usr/bin/env bash
# Regenerate and check every number published in The Null Register, Entry 03.
set -euo pipefail
cd "$(dirname "$0")"
command -v python3 >/dev/null || { echo "python3 not found"; exit 127; }
exec python3 verify.py "$@"
