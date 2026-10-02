#!/usr/bin/env bash
# Ship Framework — SessionStart hook
# Runs once when a Claude Code session begins in a Ship project.
# Sets environment variables and prints project context.
#
# Output: printed text becomes part of Claude's initial context.
# Env: writes to $CLAUDE_ENV_FILE to persist vars across the session.

set -euo pipefail

cd "${CLAUDE_PROJECT_DIR:-.}"

CLAUDE_MD="CLAUDE.md"

# Stay silent outside Ship projects — the plugin registers this hook in every
# project. Same detection as setup.sh.
if ! grep -q "## /team\|## Ship Framework\|ship-framework" "$CLAUDE_MD" 2>/dev/null; then
  exit 0
fi

# ── Read project metadata from CLAUDE.md ──────────────────────────────────────

# Stack (e.g., "web", "ios", "android", "cross-platform")
STACK=$(grep -m1 "^Stack:" "$CLAUDE_MD" 2>/dev/null | sed 's/^Stack:[[:space:]]*//' | xargs 2>/dev/null || true)

# Product name from first heading
PRODUCT=$(head -1 "$CLAUDE_MD" 2>/dev/null | sed 's/^#[[:space:]]*//' | xargs 2>/dev/null || true)

# Ship version from footer
VERSION=$(grep -o 'Ship Framework v[^ ]*' "$CLAUDE_MD" 2>/dev/null | head -1 | sed 's/Ship Framework //' || true)

# ── Count project state ───────────────────────────────────────────────────────

OPEN_TASKS=0
if [ -f "TASKS.md" ]; then
  OPEN_TASKS=$(grep -c '^\- \[ \]' "TASKS.md" 2>/dev/null | head -1 || true)
  OPEN_TASKS=${OPEN_TASKS:-0}
fi

DECISIONS=0
if [ -f "DECISIONS.md" ]; then
  DECISIONS=$(grep -c '^## [0-9]\{4\}-' "DECISIONS.md" 2>/dev/null | head -1 || true)
  DECISIONS=${DECISIONS:-0}
fi

LEARNINGS=0
if [ -f "LEARNINGS.md" ]; then
  LEARNINGS=$(grep -c '^- ' "LEARNINGS.md" 2>/dev/null | head -1 || true)
  LEARNINGS=${LEARNINGS:-0}
fi

# ── Clean stale refgate state from previous sessions ──────────────────────────

rm -f .claude/.refgate-loaded .claude/.refgate-passed .claude/.refgate-dim-* 2>/dev/null || true

# ── Set environment variables for the session ─────────────────────────────────

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  [ -n "$STACK" ] && echo "export SHIP_STACK=\"$STACK\"" >> "$CLAUDE_ENV_FILE"
  [ -n "$VERSION" ] && echo "export SHIP_VERSION=\"$VERSION\"" >> "$CLAUDE_ENV_FILE"
  [ -n "$PRODUCT" ] && echo "export SHIP_PRODUCT=\"$PRODUCT\"" >> "$CLAUDE_ENV_FILE"
fi

# ── Print session context: one line, then only what needs attention ─────────────

SHIP_SKILLS_DIR="$(cd "$(dirname "$0")/../.." && pwd)"
# Plugin installs namespace the command (/ship-framework:shipmate); this script's path says which install ran it.
case "$0" in */skills/ship-sessionstart/*) C="/ship-framework:shipmate" ;; *) C="/shipmate" ;; esac

LINE="Ship ${VERSION:-}"
if [ -n "$PRODUCT" ] && [ "$PRODUCT" != "[Your Product Name]" ]; then LINE="$LINE · $PRODUCT"; fi
[ -n "$STACK" ] && LINE="$LINE · $STACK"
[ "$OPEN_TASKS" -gt 0 ] && LINE="$LINE · $OPEN_TASKS open task(s)"
echo "$LINE · say what you need, or $C."

# Warnings
if [ "$PRODUCT" = "[Your Product Name]" ] || [ -z "$PRODUCT" ]; then
  echo "⚠ Product name not set: the first heading in CLAUDE.md."
fi
if [ -z "$STACK" ]; then
  echo "⚠ Stack not set: add a Stack: line to CLAUDE.md (e.g. Stack: web) so platform guidance loads."
fi
if [ -f PDC.md ]; then
  :
elif [ -f DESIGN.md ]; then
  echo "⚠ DESIGN.md has no PDC.md yet: $C design --init writes it. Until then, creating a new UI, motion, or copy file needs PDC.md first. Editing existing files is allowed."
else
  echo "Design gate: creating a new UI, motion, or copy file needs PDC.md first ($C design). Editing existing files is allowed."
fi

# Knowledge: an installed skill that changed since last session, or a missing tool — printed only when something needs attention
for K in "$SHIP_SKILLS_DIR/knowledge/bin/knowledge.py" "$SHIP_SKILLS_DIR/ship-knowledge/bin/knowledge.py"; do
  if [ -f "$K" ] && command -v python3 >/dev/null 2>&1; then
    KOUT="$(python3 "$K" doctor --brief --record --root . 2>/dev/null || true)"
    [ -n "$KOUT" ] && echo "$KOUT"
    break
  fi
done

# Taste: one line when something is recorded (product decisions, founder preferences) or needs attention
for TP in "$SHIP_SKILLS_DIR/taste/bin/taste.py" "$SHIP_SKILLS_DIR/ship-taste/bin/taste.py"; do
  if [ -f "$TP" ] && command -v python3 >/dev/null 2>&1; then
    TOUT="$(python3 "$TP" summary --root . 2>/dev/null || true)"
    case "$TOUT" in ""|"Taste: nothing recorded yet"*) ;; *) echo "$TOUT" ;; esac
    break
  fi
done
