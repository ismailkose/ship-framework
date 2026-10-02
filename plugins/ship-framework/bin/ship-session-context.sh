#!/bin/bash

# Ship Framework — plugin session context (SessionStart hook, plugin installs only)
#
# In a Ship project, tells the session where the plugin lives so paths written as
# ${CLAUDE_PLUGIN_ROOT}/… in files read with the Read tool (references, team-rules)
# resolve — Claude Code only substitutes that variable inside skill/agent/command text.
# Also keeps the project's managed .claude/team-rules.md in step with the plugin after a
# plugin update (the project copy is Ship's, marked "managed by Ship Framework"; a copy
# that differs is saved to .ship/backups/ first). Skipped when the project has its own
# setup.sh install — that install owns team-rules.md.
#
# Silent in non-Ship projects. Never fails the session.

ROOT="${CLAUDE_PLUGIN_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
PROJECT="${CLAUDE_PROJECT_DIR:-$(pwd)}"

[ -f "$PROJECT/CLAUDE.md" ] && grep -q "## Ship Framework" "$PROJECT/CLAUDE.md" 2>/dev/null || exit 0

VERSION="$(sed -n 's/.*"version": *"\([^"]*\)".*/\1/p' "$ROOT/.claude-plugin/plugin.json" 2>/dev/null | head -1)"
echo "Ship plugin ${VERSION:+v$VERSION }is loaded from: $ROOT (read \${CLAUDE_PLUGIN_ROOT} in Ship's files as that folder)."

if [ ! -d "$PROJECT/.claude/skills/ship" ] && [ ! -f "$PROJECT/.ship/manifest.json" ] \
   && [ -f "$ROOT/templates/team-rules.md" ] && [ -f "$PROJECT/.claude/team-rules.md" ] \
   && grep -q "managed by Ship Framework" "$PROJECT/.claude/team-rules.md" 2>/dev/null \
   && ! cmp -s "$ROOT/templates/team-rules.md" "$PROJECT/.claude/team-rules.md"; then
  STAMP="$(date +%Y%m%d-%H%M%S)"
  mkdir -p "$PROJECT/.ship/backups/$STAMP/.claude" 2>/dev/null \
    && cp "$PROJECT/.claude/team-rules.md" "$PROJECT/.ship/backups/$STAMP/.claude/team-rules.md" 2>/dev/null \
    && cp "$ROOT/templates/team-rules.md" "$PROJECT/.claude/team-rules.md" 2>/dev/null \
    && echo "Ship refreshed .claude/team-rules.md from the plugin (previous copy: .ship/backups/$STAMP/)."
fi
exit 0
