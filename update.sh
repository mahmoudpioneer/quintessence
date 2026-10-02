#!/usr/bin/env bash
# Pull the latest upstream repos, then rebuild and reinstall Quintessence.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p vendor
for r in nextlevelbuilder/ui-ux-pro-max-skill pbakaus/impeccable emilkowalski/skills isas1/forever-ai-components leonxlnx/taste-skill; do
  d=vendor/$(echo "$r" | tr / _)
  if [ -d "$d/.git" ]; then git -C "$d" pull -q --ff-only; else git clone -q --depth 1 "https://github.com/$r.git" "$d"; fi
  echo "$r @ $(git -C "$d" rev-parse --short HEAD)"
done
./install.sh
