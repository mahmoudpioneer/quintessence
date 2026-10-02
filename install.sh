#!/usr/bin/env bash
# Build Quintessence and install it as a global Claude Code skill (+ impeccable's subagents).
set -euo pipefail
cd "$(dirname "$0")"
export INSTALL_DIR=${INSTALL_DIR:-$HOME/.claude/skills/quintessence}
AGENTS_DIR=${AGENTS_DIR:-$HOME/.claude/agents}

./build.sh
mkdir -p "$INSTALL_DIR" "$AGENTS_DIR"
rsync -a --delete dist/quintessence/ "$INSTALL_DIR/"
for a in dist/agents/*.md; do
  dest="$AGENTS_DIR/$(basename "$a")"
  if [ -f "$dest" ] && ! grep -q "$INSTALL_DIR" "$dest"; then
    echo "skipping $(basename "$a"): $dest exists and wasn't installed by Quintessence" >&2; continue
  fi
  cp "$a" "$dest"
done
ls dist/agents > "$INSTALL_DIR/.installed-agents"
echo "installed → $INSTALL_DIR (+ agents in $AGENTS_DIR)"

# Remove the install from before the rename, if present.
if [ -d "$HOME/.claude/skills/design-max" ]; then rm -rf "$HOME/.claude/skills/design-max"; echo "removed old design-max install"; fi

# Pre-fetch impeccable's detector engine (sha256-verified by its launcher) into ~/.impeccable/bin.
if "$INSTALL_DIR/modules/impeccable/scripts/impeccable" engine-probe; then
  echo "impeccable engine ready"
else
  echo "warning: impeccable engine unavailable — Quintessence still works, minus the deterministic detector" >&2
fi

python3 "$INSTALL_DIR/modules/ui-ux-pro-max/scripts/search.py" "saas dashboard" --domain style -n 1 >/dev/null && echo "ui-ux-pro-max search OK"
python3 "$INSTALL_DIR/modules/forever/scripts/forever_search.py" loader --perf cheap -n 1 >/dev/null && echo "forever search OK"
echo "Done. Start a new Claude Code session and run /quintessence"
