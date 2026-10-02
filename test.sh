#!/usr/bin/env bash
# Smoke-test the installed Quintessence skill. Prints PASS/FAIL per check.
set -uo pipefail
DM=${INSTALL_DIR:-$HOME/.claude/skills/quintessence}
AGENTS=${AGENTS_DIR:-$HOME/.claude/agents}
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
pass=0; fail=0

check() { # name, command...
  local name=$1; shift
  if out=$("$@" 2>&1); then
    echo "PASS  $name"; pass=$((pass+1))
  else
    echo "FAIL  $name"; echo "$out" | sed 's/^/      /' | tail -5; fail=$((fail+1))
  fi
}
contains() { grep -q -- "$1"; }

echo "== Install structure ($DM)"
check "router SKILL.md has name: quintessence" grep -q '^name: quintessence' "$DM/SKILL.md"
check "old design-max install removed" test ! -e "$HOME/.claude/skills/design-max"
for a in impeccable-finish-reviewer impeccable-documenter impeccable-asset-producer impeccable-manual-edit-applier; do
  check "agent $a installed" grep -q '^name: '$a "$AGENTS/$a.md"
done
check "agents point at this install's launcher" sh -c "! grep -l '\.claude/skills/impeccable/' '$AGENTS'/impeccable-*.md"
for m in ui-ux-pro-max uupm-design-system uupm-ui-styling uupm-brand uupm-banner-design uupm-slides uupm-design impeccable forever \
         emil/emil-design-eng emil/animate emil/review-animations emil/improve-animations emil/find-animation-opportunities \
         emil/animation-vocabulary emil/apple-design emil/mobile-native emil/pick-ui-library emil/prototype emil/ask-sonner \
         taste/taste-skill taste/minimalist-skill taste/soft-skill taste/brutalist-skill taste/redesign-skill taste/stitch-skill taste/output-skill; do
  check "module $m has SKILL.md" test -s "$DM/modules/$m/SKILL.md"
done
check "no unresolved \${CLAUDE_PLUGIN_ROOT} in module docs" sh -c "! grep -rl 'CLAUDE_PLUGIN_ROOT' '$DM/modules' --include=SKILL.md"
check "forever library has 600+ components" sh -c "[ \$(find '$DM/modules/forever/infinite' -name '*.html' | wc -l) -ge 600 ]"
check "licenses bundled (7 files)" sh -c "[ \$(ls '$DM/LICENSES' | wc -l) -ge 7 ]"

echo "== ui-ux-pro-max"
UU="python3 $DM/modules/ui-ux-pro-max/scripts/search.py"
check "design-system generator" sh -c "$UU 'fintech dashboard dark' --design-system -p Test | grep -q 'TYPOGRAPHY'"
check "style domain search"     sh -c "$UU 'glassmorphism' --domain style -n 2 | grep -qi 'glass'"
check "ux domain search"        sh -c "$UU 'keyboard focus modal' --domain ux -n 2 | grep -qi 'focus'"
check "stack search (nextjs)"   sh -c "$UU 'suspense streaming' --stack nextjs -n 2 | grep -qi 'suspense'"
check "json output parses"      sh -c "$UU 'saas' --domain color --json | python3 -c 'import json,sys; json.load(sys.stdin)'"

echo "== forever"
FS="python3 $DM/modules/forever/scripts/forever_search.py"
check "keyword + filter search"    sh -c "$FS loader --perf cheap --label mobile-ready -n 3 | grep -q '•'"
check "role/technique filter"      sh -c "$FS --role button --technique css-only --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d and all(c[\"role\"]==\"button\" for c in d)'"
check "--show returns agent meta"  sh -c "$FS --show navigation/10-command-palette.html | grep -q useWhen"
check "--facets lists filters"     sh -c "$FS --facets | grep -q perfTier"
check "nonsense query → no matches" sh -c "$FS zzqqxx | grep -q 'No matches'"

echo "== quintessence scripts"
BRIEF="python3 $DM/scripts/design_brief.py"
check "design brief runs"              sh -c "$BRIEF 'saas marketing tool landing' -p T | grep -q '## KEEP'"
check "brief rejects Inter (detector-flagged)" sh -c "$BRIEF 'saas marketing tool ad research performance marketers landing' -p T | grep -q 'Body font Inter: impeccable'"
check "brief resolves 'no transitions' clash"  sh -c "$BRIEF 'saas marketing tool ad research performance marketers landing' -p T | grep -q 'Emil'"
check "brief --json parses"            sh -c "$BRIEF 'fintech dashboard' --json | python3 -c 'import json,sys; d=json.load(sys.stdin); assert {\"keep\",\"review\",\"reject\"} <= d.keys()'"
mkdir -p "$TMP/site"; printf '<!doctype html><meta name=viewport content="width=device-width"><body style="margin:0"><div style="height:1500px;background:linear-gradient(#123,#456)">capture test</div>' > "$TMP/site/index.html"
check "capture writes desktop + mobile" sh -c "node '$DM/scripts/capture.mjs' 'file://$TMP/site/index.html' --out '$TMP/cap' >/dev/null && sips -g pixelWidth '$TMP/cap/mobile.png' | grep -q 'pixelWidth: 390' && sips -g pixelHeight '$TMP/cap/desktop.png' | grep -q 'pixelHeight: 1500'"

echo "== impeccable"
IMP="$DM/modules/impeccable/scripts/impeccable"
check "engine handshake" sh -c "'$IMP' engine-probe | grep -q impeccable-engine"
check "launcher privacy patch present" grep -q 'IMPECCABLE_NO_TELEMETRY="\${IMPECCABLE_NO_TELEMETRY:-1}"' "$IMP"
printf '# Product\n\n## Platform\n\nweb\n\n## Users\n\nTest users.\n' > "$TMP/PRODUCT.md"
check "offline mode gives an offline roll" sh -c "cd '$TMP' && QUINTESSENCE_OFFLINE=1 '$IMP' concept-seed --scope direction --mode persuade 2>&1 | grep -q 'source: degraded'"
cat > "$TMP/slop.html" <<'EOF'
<!doctype html><html><head><style>
body{font-family:Inter,sans-serif}
.hero{background:linear-gradient(135deg,#6366f1,#a855f7);padding:80px}
.hero p{color:#9ca3af}
.card{border-radius:16px;padding:24px;box-shadow:0 4px 6px rgba(0,0,0,.1);border:1px solid #e5e7eb}
</style></head><body>
<section class="hero"><h1>Supercharge Your Workflow</h1><p>Unlock AI-driven productivity</p></section>
<div class="card"><div class="card"><h3>Feature</h3><p>Sync every account automatically.</p></div></div>
</body></html>
EOF
cat > "$TMP/clean.html" <<'EOF'
<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Ledger</title><style>
body{font-family:"Source Serif 4",Georgia,serif;background:#ffffff;color:#14212b;font-size:18px;line-height:1.6}
h1{font-size:3rem;line-height:1.1} h2{font-size:1.75rem}
</style></head><body><main><h1>Monthly ledger</h1><h2>March totals</h2><p>Income and expenses for March, grouped by account.</p></main></body></html>
EOF
detect_out=$("$IMP" detect "$TMP/slop.html" 2>&1)
check "detector flags generic page" sh -c "echo \"\$0\" | grep -q 'anti-patterns found'" "$detect_out"
for rule in ai-color-palette overused-font gray-on-color nested-cards marketing-buzzword; do
  check "  catches $rule" sh -c "echo \"\$0\" | grep -q '\[$rule\]'" "$detect_out"
done
clean_out=$("$IMP" detect "$TMP/clean.html" 2>&1)
check "detector passes clean page" sh -c "! echo \"\$0\" | grep -q '\['" "$clean_out"
check "context loader runs" sh -c "cd '$TMP' && '$IMP' context --target slop.html | grep -q RESOLVED_CONTEXT"

echo
echo "== $pass passed, $fail failed"
[ "$fail" -eq 0 ]
