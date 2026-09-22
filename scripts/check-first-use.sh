#!/bin/bash

# Ship Framework — First-use checks
# Behavior tests for the hooks, installer, and plugin build: the things that
# break a fresh install. Runs in temp dirs; never touches your projects.
# Bash 3.2 compatible (macOS default).
#
# Usage: bash scripts/check-first-use.sh

set -u

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILLS="$ROOT/template/.claude/skills/ship"
REFGATE="$SKILLS/refgate/bin/check-refgate.sh"
CAREFUL="$SKILLS/careful/bin/check-careful.sh"
FREEZE="$SKILLS/freeze/bin/check-freeze.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

PASS=0
FAIL=0
ok()   { PASS=$((PASS+1)); echo "  ✓ $1"; }
bad()  { FAIL=$((FAIL+1)); echo "  ✗ $1"; [ -n "${2:-}" ] && echo "      got: $2"; }

# expect <name> <expected: allow|deny|ask> <output> <exit code>
expect() {
  local name="$1" want="$2" out="$3" code="$4"
  if [ "$code" != "0" ]; then bad "$name (exit $code)" "$out"; return; fi
  case "$want" in
    allow) [ "$out" = "{}" ] && ok "$name" || bad "$name" "$out" ;;
    *)     echo "$out" | grep -q "\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"$want\",\"permissionDecisionReason\":" \
             && ok "$name" || bad "$name" "$out" ;;
  esac
}

# run_hook <script> <cwd> <stdin json>  → sets OUT, CODE
run_hook() {
  OUT="$(cd "$2" && printf '%s' "$3" | CLAUDE_PROJECT_DIR= bash "$1" 2>/dev/null)"
  CODE=$?
}

# ── Refgate: fresh /ship-design seed flow ────────────────────────────────
echo "Refgate"
ship_project() { mkdir -p "$1/.claude" && printf '# App\n\n## Ship Framework\n' > "$1/CLAUDE.md"; }
P="$TMP/seed"; ship_project "$P" && touch "$P/DESIGN.md"   # Phase 6a done, no PDC.md yet
for f in design-model.yaml design/components.yaml design/components.yml PDC.md; do
  run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/$f\"}}"
  expect "seed file allowed before PDC.md: $f" allow "$OUT" "$CODE"
done
run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/views/Home.swift\"}}"
expect "UI edit denied without PDC.md" deny "$OUT" "$CODE"
run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/services/api.ts\"}}"
expect "logic edit allowed without PDC.md" allow "$OUT" "$CODE"
run_hook "$REFGATE" "$P" '{}'
expect "missing file_path fails open" allow "$OUT" "$CODE"
P="$TMP/not-ship"; mkdir -p "$P" && printf '# Some other project\n' > "$P/CLAUDE.md"
run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/views/Home.tsx\"}}"
expect "non-Ship project is never gated" allow "$OUT" "$CODE"
OUT="$(cd "$P" && CLAUDE_PROJECT_DIR= bash "$SKILLS/sessionstart/bin/session-start.sh" 2>&1)"
[ -z "$OUT" ] && ok "session-start silent in non-Ship project" || bad "session-start silent in non-Ship project" "$OUT"

# ── Careful ──────────────────────────────────────────────────────────────
echo "Careful"
run_hook "$CAREFUL" "$TMP" '{"tool_input":{"command":"rm -rf /var/data"}}'
expect "rm -rf asks" ask "$OUT" "$CODE"
run_hook "$CAREFUL" "$TMP" '{"tool_input":{"command":"git push --force origin main"}}'
expect "force push asks" ask "$OUT" "$CODE"
run_hook "$CAREFUL" "$TMP" '{"tool_input":{"command":"rm -rf node_modules"}}'
expect "rm -rf node_modules allowed" allow "$OUT" "$CODE"
run_hook "$CAREFUL" "$TMP" '{"tool_input":{"command":"ls -la"}}'
expect "safe command allowed" allow "$OUT" "$CODE"

# ── Freeze ───────────────────────────────────────────────────────────────
echo "Freeze"
P="$TMP/frozen"; mkdir -p "$P/.claude" "$P/src/ui" && echo "src/ui" > "$P/.claude/.freeze-path"
run_hook "$FREEZE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/ui/Button.tsx\"}}"
expect "inside boundary allowed" allow "$OUT" "$CODE"
run_hook "$FREEZE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/api/client.ts\"}}"
expect "outside boundary denied" deny "$OUT" "$CODE"

# ── Installer: hooks merge alongside existing ones ───────────────────────
echo "Installer"
STUB="$TMP/stub-bin"; mkdir -p "$STUB"
printf '#!/bin/sh\nexit 1\n' > "$STUB/npm"; cp "$STUB/npm" "$STUB/npx"; chmod +x "$STUB/npm" "$STUB/npx"

count_hook() {  # count_hook <settings> <event> <command substring>
  python3 -c "
import json,sys
d=json.load(open(sys.argv[1]))
print(sum(sys.argv[3] in h.get('command','') for e in d.get('hooks',{}).get(sys.argv[2],[]) for h in e.get('hooks',[])))
" "$1" "$2" "$3"
}

P="$TMP/fresh"; mkdir -p "$P"
PATH="$STUB:$PATH" bash "$ROOT/setup.sh" "$P" >/dev/null 2>&1
S="$P/.claude/settings.json"
[ "$(count_hook "$S" PreToolUse check-refgate.sh)" = "2" ] && ok "fresh install registers refgate" || bad "fresh install registers refgate"

P="$TMP/existing"; mkdir -p "$P/.claude"
cat > "$P/.claude/settings.json" <<'EOF'
{"hooks": {
  "PreToolUse": [{"matcher": "Bash", "hooks": [{"type": "command", "command": "my-lint.sh"}]}],
  "SessionStart": [{"hooks": [{"type": "command", "command": "my-start.sh"}]}]
}}
EOF
S="$P/.claude/settings.json"
PATH="$STUB:$PATH" bash "$ROOT/setup.sh" "$P" >/dev/null 2>&1
[ "$(count_hook "$S" PreToolUse check-refgate.sh)" = "2" ] && ok "refgate added alongside existing PreToolUse hook" || bad "refgate added alongside existing PreToolUse hook" "$(cat "$S")"
[ "$(count_hook "$S" PreToolUse my-lint.sh)" = "1" ] && ok "existing PreToolUse hook kept" || bad "existing PreToolUse hook kept"
[ "$(count_hook "$S" SessionStart my-start.sh)" = "1" ] && ok "existing SessionStart hook kept" || bad "existing SessionStart hook kept"
PATH="$STUB:$PATH" bash "$ROOT/setup.sh" "$P" >/dev/null 2>&1
[ "$(count_hook "$S" PreToolUse check-refgate.sh)" = "2" ] && ok "re-running setup does not duplicate hooks" || bad "re-running setup does not duplicate hooks"

# ── Codex bridge ─────────────────────────────────────────────────────────
echo "Codex bridge"
python3 "$ROOT/scripts/render_ship_core.py" --check >/dev/null 2>&1 \
  && ok "generated Ship core blocks in sync with framework.yaml" \
  || bad "generated blocks drifted — run: python3 scripts/render_ship_core.py --write"
P="$TMP/fresh"
if [ -f "$P/AGENTS.md" ] && grep -q "Managed by Ship Framework" "$P/AGENTS.md" && ! grep -q "__VERSION__" "$P/AGENTS.md"; then
  ok "fresh install creates AGENTS.md with version filled in"
else
  bad "fresh install creates AGENTS.md with version filled in"
fi
[ -f "$P/.ship/framework.yaml" ] && ok "fresh install creates .ship/framework.yaml" || bad "fresh install creates .ship/framework.yaml"
P="$TMP/own-agents"; mkdir -p "$P" && echo "# My own agent rules" > "$P/AGENTS.md"
PATH="$STUB:$PATH" bash "$ROOT/setup.sh" "$P" >/dev/null 2>&1
[ "$(cat "$P/AGENTS.md")" = "# My own agent rules" ] && ok "user's own AGENTS.md left untouched" || bad "user's own AGENTS.md left untouched"

# ── Plugin build ─────────────────────────────────────────────────────────
echo "Plugin build"
B="$TMP/build"; mkdir -p "$B"
cp -R "$ROOT/template" "$ROOT/scripts" "$ROOT/VERSION" "$B/"
if bash "$B/scripts/build-plugin.sh" >/dev/null 2>&1 && [ -f "$B/ship-framework.plugin" ]; then
  ok "plugin builds"
  X="$B/unzipped"; mkdir -p "$X" && (cd "$X" && unzip -q "$B/ship-framework.plugin")
  DUPES=0
  for f in "$X"/commands/*.md; do
    n=$(sed -n '2,/^---$/p' "$f" | grep -c '^disable-model-invocation:')
    [ "$n" = "1" ] || DUPES=$((DUPES+1))
  done
  [ "$DUPES" = "0" ] && ok "every command has exactly one disable-model-invocation" || bad "$DUPES commands with missing/duplicate disable-model-invocation"
  BROKEN=""
  for ref in $(grep -oh '${CLAUDE_SKILL_DIR}/\.\./[a-z-]*/bin/[a-z-]*\.sh' "$X"/skills/*/SKILL.md | sort -u); do
    rel="${ref#\$\{CLAUDE_SKILL_DIR\}/../}"
    [ -f "$X/skills/$rel" ] || BROKEN="$BROKEN $rel"
  done
  [ -z "$BROKEN" ] && ok "sibling-skill hook scripts resolve in plugin layout" || bad "unresolved hook scripts:$BROKEN"
  MISSING=$(python3 -c "
import json,os,re,sys
root=sys.argv[1]
d=json.load(open(os.path.join(root,'hooks/hooks.json')))
for entries in d['hooks'].values():
    for e in entries:
        for h in e['hooks']:
            for p in re.findall(r'\\$\\{CLAUDE_PLUGIN_ROOT\\}/([^\" ]+)', h['command']):
                if not os.path.isfile(os.path.join(root,p)): print(p)
" "$X" 2>&1)
  [ -f "$X/hooks/hooks.json" ] && [ -z "$MISSING" ] && ok "plugin hooks.json registers existing scripts" || bad "plugin hooks.json" "${MISSING:-missing}"
else
  bad "plugin builds"
fi

echo ""
echo "$PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
