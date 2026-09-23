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
printf 'design_model: design-model.yaml\n' > "$P/PDC.md"
run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/views/Home.swift\"}}"
expect "UI edit allowed once PDC.md exists — no reference receipt/marker needed" allow "$OUT" "$CODE"
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

# ── Design registry ──────────────────────────────────────────────────────
echo "Design registry"
DM="$SKILLS/design/bin/design_model.py"
P="$TMP/tempo"; mkdir -p "$P/design" "$P/UI" && touch "$P/UI/PrimaryButton.swift"
cat > "$P/design-model.yaml" <<'YAML'
schema_version: 1
modes: [light, dark]
brand:
  name: Tempo
  feel: [calm, warm, precise]
primitives:
  color:
    paper: { 50: "#FAF9F6", 100: "#F3F1EC", 200: "#E8E5DF" }   # comment after flow map
    ink:   { 900: "#1C1A17", 400: "#8A867C" }
    night: { 900: "#161512", 800: "#211F1B", 300: "#B5B0A6" }
    brand: { 500: "#E0633C", 300: "#EE9A7E" }
  type:   { family: Inter, scale: { caption: 13, body: 17, title: 22, display: 28 } }
  radius: { control: 10, card: 18 }
  spacing: { unit: 4 }
  motion:
    springs:
      gentle: { response: 0.5, damping: 0.9 }
    durations: { fade: 200 }
semantic:
  background: paper.50
  surface:    paper.100
  text:       ink.900
  muted:      ink.400
  hairline:   paper.200
  action:     brand.500
semantic_dark:
  background: night.900
  surface:    night.800
  text:       paper.50
  muted:      night.300
  hairline:   night.800
  action:     brand.300
YAML
cat > "$P/design/components.yaml" <<'YAML'
schema_version: 1
components:
  - name: PrimaryButton
    file: UI/PrimaryButton.swift
    tokens: [action, radius.control, type.body]
    doc: >
      The one loud element per screen.
    added: 2026-06-11
YAML
python3 "$DM" validate --root "$P" >/dev/null 2>&1 && ok "valid registry passes" || bad "valid registry passes" "$(python3 "$DM" validate --root "$P" 2>&1)"
python3 "$DM" emit-swiftui --root "$P" --out UI/Theme.swift >/dev/null 2>&1 && [ -f "$P/UI/Theme.swift" ] \
  && ok "emit-swiftui writes Theme.swift" || bad "emit-swiftui writes Theme.swift"
if xcrun -sdk iphonesimulator --show-sdk-path >/dev/null 2>&1; then
  xcrun -sdk iphonesimulator swiftc -typecheck -target arm64-apple-ios17.0-simulator "$P/UI/Theme.swift" >/dev/null 2>&1 \
    && ok "Theme.swift type-checks against the iOS SDK" || bad "Theme.swift type-checks against the iOS SDK"
else
  echo "  - skipped Swift type-check (no iOS SDK)"
fi
printf '  - name: StatCard\n    file: UI/StatCard.swift\n    tokens: [brand.500]\n' >> "$P/design/components.yaml"
OUT="$(python3 "$DM" validate --root "$P" 2>&1)"
[ $? -ne 0 ] && echo "$OUT" | grep -q "color primitive" && echo "$OUT" | grep -q "not found" \
  && ok "component using a raw primitive / missing file is rejected" || bad "component using a raw primitive / missing file is rejected" "$OUT"
sed -i '' '/name: StatCard/,$d' "$P/design/components.yaml"
printf '    variants: [content, grouped]\n' >> "$P/design/components.yaml"
python3 "$DM" validate --root "$P" >/dev/null 2>&1 && ok "component variants accepted" || bad "component variants accepted" "$(python3 "$DM" validate --root "$P" 2>&1)"
printf '  - name: Badge\n    planned: true\n    tokens: [action]\n    variants: Big\n' >> "$P/design/components.yaml"
python3 "$DM" validate --root "$P" 2>&1 | grep -q "variants must be" && ok "malformed variants rejected" || bad "malformed variants rejected"
P="$TMP/unfilled"; mkdir -p "$P" && cp "$SKILLS/design/references/design-model-template.yaml" "$P/design-model.yaml"
python3 "$DM" validate --root "$P" >/dev/null 2>&1 && bad "unfilled template is rejected" || ok "unfilled template is rejected"

P="$TMP/real-app"; mkdir -p "$P"
cat > "$P/design-model.yaml" <<'YAML'
schema_version: 1
modes: [light, dark]
brand: { name: Real, feel: [warm, sharp, grounded] }
primitives:
  color:
    paper: { 0: "#FFFFFF", 50: "#F9F9F5" }
    night: { 900: "#262524", 850: "#2E2D2B" }
    veil:  { sand50: "#DFDED180", white06: "#FFFFFF0F" }
    ember: { 500: "#D4692C", 400: "#E0844A" }
  type:
    families: { display: Gelasio, text: Geist }
    dynamic_type: false
    styles:
      heroTitle: { family: display, weight: Bold, size: 34 }
      body:      { family: text, weight: Regular, size: 17 }
  radius: { md: 12 }
  spacing: { unit: 4, scale: { sm: 8, md: 16 } }
  motion:
    springs: { default: { response: 0.35, damping: 0.85 } }
    durations: { fade: { ms: 200, curve: easeOut } }
semantic:
  background: paper.50
  surface: paper.0
  text: system.primary
  muted: system.secondary
  hairline: system.separator
  action: ember.500
  bubble: { border: veil.sand50 }
semantic_dark:
  background: night.900
  surface: night.850
  text: system.primary
  muted: system.secondary
  hairline: system.separator
  action: ember.400
  bubble: { border: veil.white06 }
emit:
  swiftui:
    namespaces: { colors: Brand, typography: Typo }
    rename: { action: accent }
YAML
if python3 "$DM" emit-swiftui --root "$P" --out Theme.swift >/dev/null 2>&1; then
  G="$P/Theme.swift"
  grep -q "^enum Brand {" "$G" && grep -q "static let accent = Color(light: 0xD4692C, dark: 0xE0844A)" "$G" \
    && grep -q "enum Bubble {" "$G" && grep -q 'static let text = Color.primary' "$G" \
    && grep -q 'static let heroTitle: Font = .custom("Gelasio-Bold", size: 34)$' "$G" \
    && grep -q 'static let `default` = Animation.spring' "$G" && grep -q 'Animation.easeOut(duration: 0.2)' "$G" \
    && ok "real-app model emits existing names (namespaces, rename, groups, system colors, styles)" \
    || bad "real-app model emits existing names" "$(cat "$G")"
  if xcrun -sdk iphonesimulator --show-sdk-path >/dev/null 2>&1; then
    xcrun -sdk iphonesimulator swiftc -typecheck -target arm64-apple-ios17.0-simulator "$G" >/dev/null 2>&1 \
      && ok "real-app Theme.swift type-checks" || bad "real-app Theme.swift type-checks"
  fi
else
  bad "real-app model validates" "$(python3 "$DM" validate --root "$P" 2>&1)"
fi
sed -i '' 's/text: system.primary/text: system.notAColor/' "$P/design-model.yaml"
python3 "$DM" validate --root "$P" 2>&1 | grep -q "unknown system color" && ok "unknown system color is rejected" || bad "unknown system color is rejected"

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
  grep -rq "refgate-loaded\|REFERENCES LOADED" "$X/commands" "$X/templates" && bad "plugin still asks for reference receipts/markers" || ok "no reference receipts/markers left in commands or templates"
  MISSING=""
  for ref in $(grep -oh '${CLAUDE_PLUGIN_ROOT}/[A-Za-z0-9_./-]*\.\(py\|sh\)' "$X"/commands/*.md "$X"/skills/*/SKILL.md | sort -u); do
    rel="${ref#\$\{CLAUDE_PLUGIN_ROOT\}/}"
    [ -f "$X/$rel" ] || MISSING="$MISSING $rel"
  done
  [ -z "$MISSING" ] && ok "scripts referenced by plugin commands exist" || bad "missing scripts:$MISSING"
  grep -q "__VERSION__" "$X/templates/CLAUDE.md" && bad "plugin CLAUDE.md template has version filled in" || ok "plugin CLAUDE.md template has version filled in"

  # First-run bootstrap (plugin installs have no setup.sh)
  BOOT="$X/bin/bootstrap-project.sh"
  P="$TMP/plugin-empty"; mkdir -p "$P"
  (cd "$P" && CLAUDE_PROJECT_DIR= bash "$BOOT" >/dev/null 2>&1)
  if [ -f "$P/CLAUDE.md" ] && [ -f "$P/TASKS.md" ] && [ -f "$P/LEARNINGS.md" ] && [ -f "$P/.claude/team-rules.md" ]; then
    ok "bootstrap sets up an empty project"
  else
    bad "bootstrap sets up an empty project" "$(ls -A "$P")"
  fi
  run_hook "$REFGATE" "$P" "{\"tool_input\":{\"file_path\":\"$P/src/views/Home.tsx\"}}"
  expect "bootstrapped project is gated as a Ship project" deny "$OUT" "$CODE"

  P="$TMP/plugin-own"; mkdir -p "$P" && printf '# My app\n\nMy own rules.\n' > "$P/CLAUDE.md" && echo "- [ ] my task" > "$P/TASKS.md"
  (cd "$P" && CLAUDE_PROJECT_DIR= bash "$BOOT" >/dev/null 2>&1)
  head -3 "$P/CLAUDE.md" | grep -q "My own rules." && grep -q "## Ship Framework" "$P/CLAUDE.md" \
    && ok "bootstrap appends to an existing CLAUDE.md" || bad "bootstrap appends to an existing CLAUDE.md"
  [ "$(cat "$P/TASKS.md")" = "- [ ] my task" ] && ok "bootstrap never overwrites memory files" || bad "bootstrap never overwrites memory files"
  BEFORE="$(cat "$P/CLAUDE.md")"
  (cd "$P" && CLAUDE_PROJECT_DIR= bash "$BOOT" >/dev/null 2>&1)
  [ "$(cat "$P/CLAUDE.md")" = "$BEFORE" ] && ok "re-running bootstrap leaves CLAUDE.md alone" || bad "re-running bootstrap leaves CLAUDE.md alone"
else
  bad "plugin builds"
fi

echo ""
echo "$PASS passed, $FAIL failed"
[ "$FAIL" = "0" ]
