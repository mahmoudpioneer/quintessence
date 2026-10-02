#!/usr/bin/env bash
# Assemble dist/quintessence (the skill) and dist/agents (impeccable's subagents) from vendor/ + src/.
set -euo pipefail
cd "$(dirname "$0")"
ROOT=$PWD
V=$ROOT/vendor
OUT=$ROOT/dist/quintessence
AGENTS_OUT=$ROOT/dist/agents
INSTALL_DIR=${INSTALL_DIR:-$HOME/.claude/skills/quintessence}

UUPM=$V/nextlevelbuilder_ui-ux-pro-max-skill
IMPECCABLE=$V/pbakaus_impeccable
EMIL=$V/emilkowalski_skills
FOREVER=$V/isas1_forever-ai-components
TASTE=$V/leonxlnx_taste-skill

EMIL_SKILLS="emil-design-eng animate review-animations improve-animations find-animation-opportunities animation-vocabulary apple-design mobile-native pick-ui-library prototype ask-sonner"
TASTE_SKILLS="taste-skill minimalist-skill soft-skill brutalist-skill redesign-skill stitch-skill output-skill"
UUPM_EXTRAS="design-system ui-styling brand banner-design slides design"

for d in "$UUPM" "$IMPECCABLE" "$EMIL" "$FOREVER" "$TASTE"; do
  [ -d "$d/.git" ] || { echo "missing $d — run ./update.sh first" >&2; exit 1; }
done

copy() { mkdir -p "$2"; rsync -a --exclude '.git' --exclude 'tests' --exclude '__pycache__' --exclude '.DS_Store' "$1/" "$2/"; }

rm -rf "$OUT" "$AGENTS_OUT"
mkdir -p "$OUT/modules" "$OUT/LICENSES" "$OUT/scripts" "$AGENTS_OUT"
cp src/SKILL.md "$OUT/SKILL.md"
cp src/scripts/* "$OUT/scripts/"
chmod +x "$OUT/scripts/"*

# ui-ux-pro-max + extras
copy "$UUPM/.claude/skills/ui-ux-pro-max" "$OUT/modules/ui-ux-pro-max"
for s in $UUPM_EXTRAS; do copy "$UUPM/.claude/skills/$s" "$OUT/modules/uupm-$s"; done
# Point plugin-root paths at the installed location; macOS has python3, not python.
find "$OUT/modules" -path '*uupm*/SKILL.md' -o -path '*ui-ux-pro-max/SKILL.md' | while read -r f; do
  sed -i '' \
    -e "s#\${CLAUDE_PLUGIN_ROOT}/.claude/skills/ui-ux-pro-max#$INSTALL_DIR/modules/ui-ux-pro-max#g" \
    -e 's#^python "#python3 "#' -e 's#^python scripts/#python3 scripts/#' "$f"
done

# impeccable (Apache-2.0). Patch the launcher: no telemetry ping, no update check (update.sh handles updates),
# and an opt-in fully offline mode for concept-seed.
copy "$IMPECCABLE/.claude/skills/impeccable" "$OUT/modules/impeccable"
L="$OUT/modules/impeccable/scripts/impeccable"
grep -q '^set -eu$' "$L" || { echo "impeccable launcher changed upstream; update the patch in build.sh" >&2; exit 1; }
awk '{print} /^set -eu$/ && !done {
  print "# --- Quintessence patch: privacy defaults ---"
  print "export IMPECCABLE_NO_TELEMETRY=\"${IMPECCABLE_NO_TELEMETRY:-1}\" DO_NOT_TRACK=\"${DO_NOT_TRACK:-1}\" IMPECCABLE_NO_UPDATE_CHECK=\"${IMPECCABLE_NO_UPDATE_CHECK:-1}\""
  print "if [ \"${QUINTESSENCE_OFFLINE:-0}\" = 1 ]; then export IMPECCABLE_API_URL=\"http://127.0.0.1:9/api\"; fi"
  print "# --- end patch ---"
  done=1 }' "$L" > "$L.tmp" && mv "$L.tmp" "$L" && chmod +x "$L"

# impeccable's subagents, pointed at the installed launcher
for a in "$IMPECCABLE"/.claude/agents/impeccable-*.md; do
  sed -e "s#\.claude/skills/impeccable/#$INSTALL_DIR/modules/impeccable/#g" "$a" > "$AGENTS_OUT/$(basename "$a")"
done

# emil + taste
for s in $EMIL_SKILLS; do copy "$EMIL/skills/$s" "$OUT/modules/emil/$s"; done
cp "$EMIL/performance-cheatsheet.md" "$OUT/modules/emil/"
for s in $TASTE_SKILLS; do copy "$TASTE/skills/$s" "$OUT/modules/taste/$s"; done

# forever: our wrapper + the upstream component library
copy src/modules/forever "$OUT/modules/forever"
copy "$FOREVER/infinite" "$OUT/modules/forever/infinite"
chmod +x "$OUT/modules/forever/scripts/forever_search.py"

# Licenses + provenance
cp "$UUPM/LICENSE" "$OUT/LICENSES/ui-ux-pro-max.MIT.txt"
cp "$IMPECCABLE/LICENSE" "$OUT/LICENSES/impeccable.Apache-2.0.txt"
cp "$IMPECCABLE/NOTICE.md" "$OUT/LICENSES/impeccable.NOTICE.md"
cp "$EMIL/LICENSE" "$OUT/LICENSES/emilkowalski-skills.MIT.txt"
cp "$FOREVER/LICENSE" "$OUT/LICENSES/forever-ai-components.MIT.txt"
cp "$FOREVER/NOTICE.md" "$OUT/LICENSES/forever-ai-components.NOTICE.md"
cp "$TASTE/LICENSE" "$OUT/LICENSES/taste-skill.MIT.txt"

{
  echo "# Upstream sources"
  echo
  echo "Built $(date -u +%Y-%m-%dT%H:%MZ). Modules are copied unmodified except:"
  echo "- ui-ux-pro-max SKILL.md paths rewritten to the install dir and \`python\` → \`python3\`."
  echo "- impeccable's launcher (\`modules/impeccable/scripts/impeccable\`) gets a privacy patch: telemetry and update check off, \`QUINTESSENCE_OFFLINE=1\` for an offline concept roll."
  echo "- impeccable's agents (installed to ~/.claude/agents/) point at this install's launcher."
  echo
  echo "| Module | Repo | Commit |"
  echo "|---|---|---|"
  for pair in "ui-ux-pro-max (+uupm-*):$UUPM" "impeccable:$IMPECCABLE" "emil:$EMIL" "forever:$FOREVER" "taste:$TASTE"; do
    name=${pair%%:*}; dir=${pair#*:}
    echo "| $name | $(git -C "$dir" remote get-url origin) | $(git -C "$dir" rev-parse --short HEAD) |"
  done
} > "$OUT/SOURCES.md"

echo "built $OUT ($(du -sh "$OUT" | cut -f1)) + $(ls "$AGENTS_OUT" | wc -l | tr -d ' ') agents"
