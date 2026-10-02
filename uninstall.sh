#!/usr/bin/env bash
# Remove the Quintessence skill and the impeccable agents it installed. Leaves vendor/ and ~/.impeccable alone.
set -euo pipefail
INSTALL_DIR=${INSTALL_DIR:-$HOME/.claude/skills/quintessence}
AGENTS_DIR=${AGENTS_DIR:-$HOME/.claude/agents}
if [ -f "$INSTALL_DIR/.installed-agents" ]; then
  while read -r a; do
    f="$AGENTS_DIR/$a"
    [ -f "$f" ] && grep -q "$INSTALL_DIR" "$f" && rm "$f" && echo "removed agent $a"
  done < "$INSTALL_DIR/.installed-agents"
fi
rm -rf "$INSTALL_DIR" && echo "removed $INSTALL_DIR"
echo "The impeccable engine cache in ~/.impeccable was left in place; delete it yourself if you no longer need it."
