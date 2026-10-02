#!/bin/bash

# Ship Framework — plugin project bootstrap
# Plugin installs have no setup.sh step, so this gives a project the files a Ship
# project needs. Run from the project root. Safe to re-run; never overwrites your files.
#
#   CLAUDE.md                      created, or Ship section appended to yours (backup kept)
#   TASKS/DECISIONS/CONTEXT/LEARNINGS.md   created if missing, never overwritten
#   .claude/team-rules.md          Ship's managed copy (the plugin keeps it current)
#
# Codex: the plugin route is Claude-only. For Codex, use the setup.sh project install
# (it adds AGENTS.md and the references Codex reads). See CAPABILITIES.md.

set -e

PLUGIN="$(cd "$(dirname "$0")/.." && pwd)"
TEMPLATES="$PLUGIN/templates"
PROJECT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT"

[ -f "$TEMPLATES/CLAUDE.md" ] || { echo "bootstrap: templates not found at $TEMPLATES" >&2; exit 1; }
STAMP="$(date +%Y%m%d-%H%M%S)"

if [ ! -f CLAUDE.md ]; then
  cp "$TEMPLATES/CLAUDE.md" CLAUDE.md
  echo "✓ Created CLAUDE.md"
elif ! grep -q "## /team\|## Ship Framework\|Ship Framework team definitions" CLAUDE.md 2>/dev/null; then
  mkdir -p ".ship/backups/$STAMP" && cp CLAUDE.md ".ship/backups/$STAMP/CLAUDE.md"
  { printf '\n\n---\n\n<!-- Ship Framework team definitions below -->\n\n'; cat "$TEMPLATES/CLAUDE.md"; } >> CLAUDE.md
  echo "✓ Appended Ship Framework to your existing CLAUDE.md (your content above it is unchanged; copy in .ship/backups/$STAMP/)"
fi

for f in TASKS.md DECISIONS.md CONTEXT.md LEARNINGS.md; do
  if [ ! -f "$f" ]; then
    cp "$TEMPLATES/$f" "$f"
    echo "✓ Created $f"
  fi
done

mkdir -p .claude
if [ -d .claude/skills/ship ]; then
  echo "  This project also has a setup.sh install; it keeps its own .claude/team-rules.md."
elif ! cmp -s "$TEMPLATES/team-rules.md" .claude/team-rules.md 2>/dev/null; then
  if [ -f .claude/team-rules.md ]; then
    mkdir -p ".ship/backups/$STAMP/.claude" && cp .claude/team-rules.md ".ship/backups/$STAMP/.claude/team-rules.md"
  fi
  cp "$TEMPLATES/team-rules.md" .claude/team-rules.md
  echo "✓ Synced .claude/team-rules.md (managed by Ship — don't edit)"
fi

# What's reduced without optional tools/skills — never blocks setup.
KNOW="$PLUGIN/skills/ship-knowledge/bin/knowledge.py"
if [ -f "$KNOW" ] && command -v python3 >/dev/null 2>&1; then
  OUT="$(python3 "$KNOW" doctor --root "$PROJECT" --brief 2>&1)" \
    && [ -n "$OUT" ] && echo "$OUT" | sed 's/^/  /' \
    || { [ -n "$OUT" ] && echo "  Knowledge check didn't finish; Ship works without it."; }
fi
exit 0
