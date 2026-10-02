#!/bin/bash

# Ship Framework — Setup (project install route; works for Claude Code and Codex)
#
# One command for all three cases:
#   • empty folder        → fresh install
#   • existing project    → adoption: Ship adds its files, never overwrites yours
#   • existing Ship project → update (same engine ship-update.sh uses)
#
# Usage:
#   bash ship-framework/setup.sh                    # current directory
#   bash ship-framework/setup.sh ./my-project       # a specific directory
#   bash ship-framework/setup.sh --dry-run [dir]    # show what would change, write nothing
#   bash ship-framework/setup.sh --no-playwright    # skip the optional Playwright install
#
# What Ship owns vs what you own: CAPABILITIES.md › "What updates touch".
# Bash 3.2 compatible. Needs python3 (preinstalled on macOS with the Command Line Tools).

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

BOLD='\033[1m'; DIM='\033[2m'; ORANGE='\033[38;5;208m'; GREEN='\033[32m'; YELLOW='\033[33m'; RESET='\033[0m'

DRY_RUN=""
PLAYWRIGHT="auto"
TARGET_DIR=""
UPDATE_MODE=""
for arg in "$@"; do
  case "$arg" in
    --dry-run)       DRY_RUN="--dry-run" ;;
    --no-playwright) PLAYWRIGHT="no" ;;
    --update)        UPDATE_MODE="1" ;;       # called by ship-update.sh
    -h|--help)       sed -n '3,17p' "$0"; exit 0 ;;
    -*)              echo "setup.sh: unknown option $arg" >&2; exit 2 ;;
    *)               TARGET_DIR="$arg" ;;
  esac
done
[ "${SHIP_SKIP_PLAYWRIGHT:-}" = "1" ] && PLAYWRIGHT="no"

TARGET_DIR="$(cd "${TARGET_DIR:-.}" 2>/dev/null && pwd)" || {
  echo "Error: Directory not found: ${TARGET_DIR:-.}"; exit 1; }

command -v python3 >/dev/null 2>&1 || {
  echo "Ship needs python3 to install. On macOS: xcode-select --install"; exit 1; }

echo ""
if [ -n "$UPDATE_MODE" ]; then
  echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Update"
else
  echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Setup"
fi
echo -e "${DIM}  Project: $TARGET_DIR${RESET}"

# Was this already a Ship project? (decides Playwright + the closing message)
WAS_SHIP=""
if [ -f "$TARGET_DIR/.ship/manifest.json" ] || [ -d "$TARGET_DIR/.claude/skills/ship" ] || \
   { [ -f "$TARGET_DIR/CLAUDE.md" ] && grep -q "## Ship Framework\|## /team\|Ship Framework team definitions" "$TARGET_DIR/CLAUDE.md" 2>/dev/null; }; then
  WAS_SHIP="1"
fi
PROJECT_WAS_EMPTY=""
[ -z "$(ls -A "$TARGET_DIR" 2>/dev/null | grep -v '^\.git$' | grep -v '^\.DS_Store$')" ] && PROJECT_WAS_EMPTY="1"

# Claude Code discovers project .claude/ from the git root.
if [ -z "$DRY_RUN" ] && [ ! -d "$TARGET_DIR/.git" ] && ! git -C "$TARGET_DIR" rev-parse --git-dir >/dev/null 2>&1; then
  git -C "$TARGET_DIR" init --quiet && echo -e "${GREEN}✓${RESET} Initialized git repo (Claude Code finds project commands from the git root)"
fi

python3 "$SCRIPT_DIR/scripts/ship-install.py" apply --source "$SCRIPT_DIR" --target "$TARGET_DIR" $DRY_RUN

[ -n "$DRY_RUN" ] && { echo ""; exit 0; }

# ─── Optional: Playwright for visual QA ──────────────────────────────────────
# Only for fresh, empty projects or projects that already use npm. Never creates a
# package.json inside an existing non-JS project (e.g. an Xcode app). Never fails setup.
if [ "$PLAYWRIGHT" = "auto" ] && [ -z "$WAS_SHIP" ]; then
  if [ -f "$TARGET_DIR/package.json" ] || [ -n "$PROJECT_WAS_EMPTY" ]; then
    if command -v npm >/dev/null 2>&1; then
      echo ""
      echo -e "${DIM}Installing Playwright for visual QA (optional)...${RESET}"
      [ -f "$TARGET_DIR/package.json" ] || echo '{ "name": "my-project", "private": true }' > "$TARGET_DIR/package.json"
      if (cd "$TARGET_DIR" && npm install -D @playwright/test >/dev/null 2>&1) && \
         (cd "$TARGET_DIR" && npx playwright install chromium >/dev/null 2>&1); then
        echo -e "${GREEN}✓${RESET} Installed Playwright — visual QA can take screenshots"
      else
        echo -e "${YELLOW}-${RESET} Playwright install skipped (network or npm issue). Visual QA falls back to reading code."
        echo -e "${DIM}  Add later: npm install -D @playwright/test && npx playwright install chromium${RESET}"
      fi
    else
      echo -e "${YELLOW}-${RESET} Node.js not found: visual QA screenshots unavailable. Add later: install Node.js, then"
      echo -e "${DIM}  npm install -D @playwright/test && npx playwright install chromium${RESET}"
    fi
  else
    echo -e "${DIM}  Playwright not installed (existing non-npm project). For web visual QA: npm install -D @playwright/test${RESET}"
  fi
fi

# ─── Summary ─────────────────────────────────────────────────────────────────
echo ""
if [ -n "$WAS_SHIP" ]; then
  echo -e "${BOLD}${ORANGE}Updated.${RESET} Your CLAUDE.md content, memory files, design files, and settings are untouched."
  echo -e "${DIM}  Restart Claude Code (or /reload-plugins) so new commands and agents load.${RESET}"
else
  echo -e "${BOLD}${ORANGE}Done!${RESET} Your team is ready."
  echo ""
  echo -e "  ${BOLD}1.${RESET} Fill in CLAUDE.md: The Product, The Founder, Stack."
  echo -e "  ${BOLD}2.${RESET} Start:"
  echo -e "     ${BOLD}Claude Code:${RESET} /shipmate I want to build [your idea]"
  echo -e "     ${BOLD}Codex:${RESET}       open the project and describe the task (AGENTS.md routes it)"
fi
echo ""
echo -e "${DIM}Update anytime: /shipmate update in Claude Code, or bash ship-update.sh. What each runtime can do: github.com/ismailkose/ship-framework/blob/main/CAPABILITIES.md${RESET}"
echo ""
