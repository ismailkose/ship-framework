#!/bin/bash

# Ship Framework — plugin project bootstrap
# Plugin installs have no setup.sh step, so this gives a project the files a
# Ship project needs. Run from the project root. Safe to re-run.
#
#   CLAUDE.md                      created, or Ship section appended to yours
#   TASKS/DECISIONS/CONTEXT/LEARNINGS.md   created if missing, never overwritten
#   .claude/team-rules.md          managed copy, refreshed every run
#
# Codex support (AGENTS.md) needs the setup.sh install — see README.

set -e

TEMPLATES="$(cd "$(dirname "$0")/../templates" && pwd)"
PROJECT="${CLAUDE_PROJECT_DIR:-$(pwd)}"
cd "$PROJECT"

[ -f "$TEMPLATES/CLAUDE.md" ] || { echo "bootstrap: templates not found at $TEMPLATES" >&2; exit 1; }

if [ ! -f CLAUDE.md ]; then
  cp "$TEMPLATES/CLAUDE.md" CLAUDE.md
  echo "✓ Created CLAUDE.md"
elif ! grep -q "## /team\|## Ship Framework\|ship-framework" CLAUDE.md 2>/dev/null; then
  # Same append format as setup.sh
  { printf '\n\n---\n\n<!-- Ship Framework team definitions below -->\n\n'; cat "$TEMPLATES/CLAUDE.md"; } >> CLAUDE.md
  echo "✓ Appended Ship Framework to your existing CLAUDE.md"
fi

for f in TASKS.md DECISIONS.md CONTEXT.md LEARNINGS.md; do
  if [ ! -f "$f" ]; then
    cp "$TEMPLATES/$f" "$f"
    echo "✓ Created $f"
  fi
done

mkdir -p .claude
cp "$TEMPLATES/team-rules.md" .claude/team-rules.md
echo "✓ Synced .claude/team-rules.md (managed by Ship — don't edit)"
