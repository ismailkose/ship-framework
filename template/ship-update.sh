#!/bin/bash

# Ship Framework — project update (setup.sh installs)
# Lives in your project. Fetches the latest Ship, then runs the same install engine as
# setup.sh. The engine updates Ship's own files, backs up any you edited first, removes
# files Ship retired, and never overwrites yours (CLAUDE.md content, TASKS/DECISIONS/
# CONTEXT/LEARNINGS, DESIGN/PDC, design-model.yaml, design/, references/, your-skills/).
#
# Usage:
#   bash ship-update.sh                 # update from GitHub (latest main)
#   bash ship-update.sh --dry-run       # show what would change, write nothing
#   bash ship-update.sh --from <dir>    # update from a local Ship checkout (offline)
#   SHIP_REF=v2026.10.01 bash ship-update.sh   # a specific tag or branch
#
# Plugin installs update through Claude Code instead: /plugin marketplace update ship-framework

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_URL="${SHIP_REPO_URL:-https://github.com/ismailkose/ship-framework.git}"
SOURCE="${SHIP_SOURCE:-}"
PASS=()

while [ $# -gt 0 ]; do
  case "$1" in
    --from)          SOURCE="$2"; shift 2 ;;
    --dry-run)       PASS+=("--dry-run"); shift ;;
    --add-framework)
      # Retired: iOS framework references now come from dependency skills.
      echo "Note: --add-framework is retired. Ship routes iOS frameworks to installed expert skills;"
      echo "      after the update, run: python3 .claude/skills/ship/knowledge/bin/knowledge.py doctor"
      shift 2 ;;
    -h|--help)       sed -n '3,15p' "$0"; exit 0 ;;
    *)               echo "ship-update.sh: unknown option $1" >&2; exit 2 ;;
  esac
done

if [ ! -f "$PROJECT_DIR/.ship/manifest.json" ] && [ ! -d "$PROJECT_DIR/.claude/skills/ship" ] && \
   ! grep -q "## Ship Framework\|## /team" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
  echo "✗ This doesn't look like a Ship Framework project: $PROJECT_DIR"
  echo "  To install Ship here, run setup.sh from a Ship checkout."
  exit 1
fi

TMP_DIR=""
cleanup() { [ -n "$TMP_DIR" ] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT

if [ -z "$SOURCE" ]; then
  TMP_DIR="$(mktemp -d)"
  echo "Fetching latest Ship Framework..."
  REF_ARGS=""
  [ -n "${SHIP_REF:-}" ] && REF_ARGS="--branch $SHIP_REF"
  if ! git clone --depth 1 --quiet $REF_ARGS "$REPO_URL" "$TMP_DIR/ship-framework" 2>/dev/null; then
    echo "✗ Could not reach $REPO_URL. Check your connection, or update offline:"
    echo "  bash ship-update.sh --from /path/to/ship-framework"
    exit 1
  fi
  SOURCE="$TMP_DIR/ship-framework"
fi
SOURCE="$(cd "$SOURCE" && pwd)"
[ -f "$SOURCE/setup.sh" ] && [ -f "$SOURCE/scripts/ship-install.py" ] || {
  echo "✗ $SOURCE isn't a Ship Framework checkout this script can update from."; exit 1; }

INSTALLED="$(sed -n 's/^> Ship Framework v\([0-9A-Za-z.]*\).*/\1/p' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | head -1)"
LATEST="$(cat "$SOURCE/VERSION" 2>/dev/null || echo unknown)"
if [ -n "$INSTALLED" ] && [ "$INSTALLED" != "$LATEST" ] && [ -f "$SOURCE/CHANGELOG.md" ]; then
  echo ""
  echo "What's new since v$INSTALLED (v$LATEST):"
  sed -n '/^## '"$LATEST"'/,/^## [0-9]/{ /^## [0-9]/!p; }' "$SOURCE/CHANGELOG.md" | head -30
fi

bash "$SOURCE/setup.sh" --update ${PASS[@]+"${PASS[@]}"} "$PROJECT_DIR"
