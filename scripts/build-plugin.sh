#!/bin/bash

# Ship Framework — Plugin Builder
# Builds ship-framework.plugin from template/ + scripts/plugin-assets/.
# Single source of truth: template/ is canonical; the plugin is a mechanical
# transform of it. Never edit plugin contents by hand.
#
# Transform spec (reverse-engineered from the v5.0.0 plugin, 2026-06-11):
#   1. commands/   ← template/.claude/commands/*.md
#        + inject `disable-model-invocation: true` into frontmatter
#        + path rewrite (see below)
#   2. skills/ship-<name>/ ← template/.claude/skills/ship/<name>/
#        + same path rewrite in all .md files
#   3. skills/ship-router/ ← scripts/plugin-assets/skills/ship-router/ (plugin-only)
#   4. templates/  ← template/{CLAUDE,TASKS,DECISIONS,CONTEXT,LEARNINGS}.md
#                    + template/.claude/team-rules.md
#   5. .claude-plugin/plugin.json + README.md ← scripts/plugin-assets/
#
# Path rewrites (project-relative → plugin-root-relative):
#   .claude/skills/ship/<name>/  →  ${CLAUDE_PLUGIN_ROOT}/skills/ship-<name>/
#   .claude/team-rules.md        →  ${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md
#   (all other .claude/ paths — refgate markers, your-skills — stay project-local)
#
# Usage: bash scripts/build-plugin.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
T="$ROOT/template"
ASSETS="$ROOT/scripts/plugin-assets"
OUT="$ROOT/ship-framework.plugin"
STAGE="$(mktemp -d)"
trap 'rm -rf "$STAGE"' EXIT

fail() { echo "build-plugin: $1" >&2; exit 1; }

# ── Preflight ────────────────────────────────────────────────────────────
[ -d "$T/.claude/commands" ]      || fail "missing $T/.claude/commands"
[ -d "$T/.claude/skills/ship" ]   || fail "missing $T/.claude/skills/ship"
[ -f "$ASSETS/plugin.json" ]      || fail "missing $ASSETS/plugin.json"
[ -f "$ASSETS/README.md" ]        || fail "missing $ASSETS/README.md"
[ -f "$ASSETS/skills/ship-router/SKILL.md" ] || fail "missing router skill asset"
for f in CLAUDE.md TASKS.md DECISIONS.md CONTEXT.md LEARNINGS.md; do
  [ -f "$T/$f" ] || fail "missing $T/$f"
done
[ -f "$T/.claude/team-rules.md" ] || fail "missing team-rules.md"

# Portable in-place rewrite (BSD + GNU)
rewrite() {
  perl -pi -e 's#\.claude/skills/ship/([a-z][a-z-]*)/#\${CLAUDE_PLUGIN_ROOT}/skills/ship-$1/#g; s#\.claude/skills/ship/#\${CLAUDE_PLUGIN_ROOT}/skills/#g; s#\.claude/team-rules\.md#\${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md#g' "$1"
}

# ── 1. Static assets ─────────────────────────────────────────────────────
mkdir -p "$STAGE/.claude-plugin"
cp "$ASSETS/plugin.json" "$STAGE/.claude-plugin/plugin.json"
cp "$ASSETS/README.md" "$STAGE/README.md"

# ── 2. Commands ──────────────────────────────────────────────────────────
mkdir -p "$STAGE/commands"
CMD_COUNT=0
for f in "$T/.claude/commands/ship-"*.md; do
  name="$(basename "$f")"
  head -1 "$f" | grep -q '^---$' || fail "$name: expected frontmatter on line 1"
  { head -1 "$f"; echo "disable-model-invocation: true"; tail -n +2 "$f"; } \
    > "$STAGE/commands/$name"
  rewrite "$STAGE/commands/$name"
  CMD_COUNT=$((CMD_COUNT+1))
done

# ── 3. Skills (template → flat ship-<name> layout) ───────────────────────
mkdir -p "$STAGE/skills"
SKILL_COUNT=0
for d in "$T/.claude/skills/ship/"*/; do
  name="$(basename "$d")"
  cp -R "$d" "$STAGE/skills/ship-$name"
  find "$STAGE/skills/ship-$name" -type f \( -name "*.md" -o -name "*.yaml" -o -name "*.yml" \) | while read -r md; do
    rewrite "$md"
  done
  SKILL_COUNT=$((SKILL_COUNT+1))
done
# Plugin-only skills
cp -R "$ASSETS/skills/ship-router" "$STAGE/skills/ship-router"
SKILL_COUNT=$((SKILL_COUNT+1))

# ── 4. Project templates ─────────────────────────────────────────────────
mkdir -p "$STAGE/templates"
for f in CLAUDE.md TASKS.md DECISIONS.md CONTEXT.md LEARNINGS.md; do
  cp "$T/$f" "$STAGE/templates/$f"
done
cp "$T/.claude/team-rules.md" "$STAGE/templates/team-rules.md"

# ── 5. Zip ───────────────────────────────────────────────────────────────
# Build to temp, then overwrite in place (works even where unlink is restricted)
( cd "$STAGE" && zip -qr "$STAGE/out.plugin" . -x "*.DS_Store" -x "out.plugin" )
cat "$STAGE/out.plugin" > "$OUT"

# ── Receipt ──────────────────────────────────────────────────────────────
VERSION="$(cat "$ROOT/VERSION" 2>/dev/null || echo unknown)"
PLUGIN_VERSION="$(grep -o '"version": *"[^"]*"' "$ASSETS/plugin.json" | head -1 | sed 's/.*: *"//;s/"//')"
REFS="$(find "$STAGE/skills" -name "*.md" -path "*references*" | wc -l | xargs)"
SIZE="$(du -h "$OUT" | cut -f1 | xargs)"

echo ""
echo "✓ ship-framework.plugin built"
echo "  framework VERSION: $VERSION · plugin.json version: $PLUGIN_VERSION"
echo "  commands: $CMD_COUNT · skills: $(ls "$STAGE/skills" | wc -l | xargs) · reference files: $REFS · size: $SIZE"
echo ""
echo "  Reminder: bump scripts/plugin-assets/plugin.json version + CHANGELOG before a release."
