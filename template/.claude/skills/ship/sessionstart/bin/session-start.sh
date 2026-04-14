#!/usr/bin/env bash
# Ship Framework — SessionStart hook
# Runs once when a Claude Code session begins in a Ship project.
# Sets environment variables and prints project context.
#
# Output: printed text becomes part of Claude's initial context.
# Env: writes to $CLAUDE_ENV_FILE to persist vars across the session.

set -euo pipefail

# ── Read project metadata from CLAUDE.md ──────────────────────────────────────

CLAUDE_MD="CLAUDE.md"

if [ ! -f "$CLAUDE_MD" ]; then
  echo "Ship Framework: No CLAUDE.md found. Run setup.sh first."
  exit 0
fi

# Stack (e.g., "web", "ios", "android", "cross-platform")
STACK=$(grep -m1 "^Stack:" "$CLAUDE_MD" 2>/dev/null | sed 's/^Stack:[[:space:]]*//' | xargs 2>/dev/null || true)

# Product name from first heading
PRODUCT=$(head -1 "$CLAUDE_MD" 2>/dev/null | sed 's/^#[[:space:]]*//' | xargs 2>/dev/null || true)

# Ship version from footer
VERSION=$(grep -o 'Ship Framework v[^ ]*' "$CLAUDE_MD" 2>/dev/null | head -1 | sed 's/Ship Framework //' || true)

# ── Count project state ───────────────────────────────────────────────────────

OPEN_TASKS=0
if [ -f "TASKS.md" ]; then
  OPEN_TASKS=$(grep -c '^\- \[ \]' "TASKS.md" 2>/dev/null || echo 0)
fi

DECISIONS=0
if [ -f "DECISIONS.md" ]; then
  DECISIONS=$(grep -c '^## ' "DECISIONS.md" 2>/dev/null || echo 0)
fi

LEARNINGS=0
if [ -f "LEARNINGS.md" ]; then
  LEARNINGS=$(grep -c '^## \|^- ' "LEARNINGS.md" 2>/dev/null || echo 0)
fi

# ── Clean stale refgate state from previous sessions ──────────────────────────

rm -f .claude/.refgate-loaded .claude/.refgate-passed .claude/.refgate-dim-* 2>/dev/null || true

# ── Set environment variables for the session ─────────────────────────────────

if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
  [ -n "$STACK" ] && echo "export SHIP_STACK=\"$STACK\"" >> "$CLAUDE_ENV_FILE"
  [ -n "$VERSION" ] && echo "export SHIP_VERSION=\"$VERSION\"" >> "$CLAUDE_ENV_FILE"
  [ -n "$PRODUCT" ] && echo "export SHIP_PRODUCT=\"$PRODUCT\"" >> "$CLAUDE_ENV_FILE"
fi

# ── Print session context (becomes part of Claude's initial context) ──────────

echo "─── Ship Framework Session ───"
echo ""

# Version + Stack
STATUS_LINE="Ship Framework ${VERSION:-unknown}"
if [ -n "$STACK" ]; then
  STATUS_LINE="$STATUS_LINE | Stack: $STACK"
else
  STATUS_LINE="$STATUS_LINE | Stack: not set"
fi
echo "$STATUS_LINE"

# Product
if [ "$PRODUCT" = "[Your Product Name]" ] || [ -z "$PRODUCT" ]; then
  echo "⚠ Product name not configured — update the first heading in CLAUDE.md"
else
  echo "Product: $PRODUCT"
fi

# Project state
STATE_PARTS=""
[ "$OPEN_TASKS" -gt 0 ] && STATE_PARTS="$OPEN_TASKS open tasks"
[ "$DECISIONS" -gt 0 ] && STATE_PARTS="${STATE_PARTS:+$STATE_PARTS | }$DECISIONS decisions logged"
[ "$LEARNINGS" -gt 0 ] && STATE_PARTS="${STATE_PARTS:+$STATE_PARTS | }$LEARNINGS learnings"

if [ -n "$STATE_PARTS" ]; then
  echo "$STATE_PARTS"
fi

# Stack warning
if [ -z "$STACK" ]; then
  echo ""
  echo "Tip: Set your stack in CLAUDE.md (e.g., Stack: web) so platform skills load automatically."
fi

# ── Design state (if PDC or DESIGN.md exists) ────────────────────────────────

PDC_FILE="PDC.md"
DESIGN_FILE="DESIGN.md"
TASTE_FILE="TASTE.md"

if [ -f "$PDC_FILE" ] || [ -f "$DESIGN_FILE" ]; then
  echo ""
  echo "Design:"
  echo "  /ship-design   — create or evolve design system"
  echo "  /ship-variants — explore options with comparison"
  if [ -f "$PDC_FILE" ]; then
    SECTIONS=$(grep -c '^  [a-z]' "$PDC_FILE" 2>/dev/null || echo 0)
    echo "  PDC: $SECTIONS sections defined"
  elif [ -f "$DESIGN_FILE" ]; then
    echo "  Tip: DESIGN.md exists but no PDC.md. Run /ship-design init."
  fi
  if [ -f "$TASTE_FILE" ]; then
    echo "  Taste: captured"
  else
    echo "  Taste: not yet — /ship-variants --taste"
  fi
fi

echo ""
echo "Reference Gate is active. First edit requires references to be loaded."
echo "───────────────────────────────"
