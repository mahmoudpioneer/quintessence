#!/bin/sh
# Mac/Linux wrapper. All logic lives in quintessence.py (works on Windows too: uninstall.cmd).
cd "$(dirname "$0")" || exit 1
if command -v python3 >/dev/null 2>&1; then exec python3 quintessence.py uninstall "$@"; fi
exec python quintessence.py uninstall "$@"
