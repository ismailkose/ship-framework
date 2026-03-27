#!/bin/bash

# Ship Framework — Self-Contained Update
# Lives inside your project. No external clone needed.
# Pulls the latest from GitHub into a temp directory, syncs, cleans up.
#
# Usage:
#   bash ship-update.sh                          # updates current project
#   bash ship-update.sh --add-framework healthkit,storekit

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_URL="https://github.com/ismailkose/ship-framework.git"
TMP_DIR=$(mktemp -d)

# Cleanup on exit (success or failure)
cleanup() {
  rm -rf "$TMP_DIR"
}
trap cleanup EXIT

# Colors
BOLD='\033[1m'
DIM='\033[2m'
ORANGE='\033[38;5;208m'
GREEN='\033[32m'
YELLOW='\033[33m'
RED='\033[31m'
RESET='\033[0m'

# ─── Step 1: Verify this is a Ship Framework project ─────────────────────────

if [ ! -f "$PROJECT_DIR/CLAUDE.md" ] || [ ! -d "$PROJECT_DIR/.claude/commands" ]; then
  echo ""
  echo -e "${RED}✗${RESET} This doesn't look like a Ship Framework project."
  echo "  Expected CLAUDE.md and .claude/commands/ in: $PROJECT_DIR"
  exit 1
fi

CURRENT_VERSION=$(grep -oP 'Ship Framework.*?v\K[0-9.]+' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null || echo "unknown")

echo ""
echo -e "${DIM}Fetching latest Ship Framework...${RESET}"

# ─── Step 2: Shallow clone into temp directory ────────────────────────────────

if ! git clone --depth 1 --quiet "$REPO_URL" "$TMP_DIR/ship-framework" 2>/dev/null; then
  echo ""
  echo -e "${RED}✗${RESET} Could not reach GitHub. Check your internet connection."
  echo "  Tried: $REPO_URL"
  exit 1
fi

FRAMEWORK_DIR="$TMP_DIR/ship-framework"
TEMPLATE_DIR="$FRAMEWORK_DIR/template"
VERSION=$(cat "$FRAMEWORK_DIR/VERSION" 2>/dev/null || echo "unknown")

echo ""
echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Update"
echo ""
echo -e "  Project:           ${BOLD}$PROJECT_DIR${RESET}"
echo -e "  Installed version: ${BOLD}$CURRENT_VERSION${RESET}"
echo -e "  Latest version:    ${BOLD}$VERSION${RESET}"
echo ""

if [ "$CURRENT_VERSION" = "$VERSION" ]; then
  echo -e "${GREEN}✓${RESET} Already up to date."
  echo ""
  exit 0
fi

# ─── Step 3: Show what changed ────────────────────────────────────────────────

if [ -f "$FRAMEWORK_DIR/CHANGELOG.md" ]; then
  echo -e "${BOLD}What's new in v${VERSION}:${RESET}"
  echo ""
  sed -n '/^## '"$VERSION"'/,/^## [0-9]/{ /^## [0-9]/!p; }' "$FRAMEWORK_DIR/CHANGELOG.md"
  echo ""
fi

# ─── Protected files ─────────────────────────────────────────────────────────
# These are NEVER overwritten — they contain user customizations.

PROTECTED_FILES=(
  "CLAUDE.md"
  "TASKS.md"
  "references/design-system.md"
)

is_protected() {
  local relpath="$1"
  for pf in "${PROTECTED_FILES[@]}"; do
    if [ "$relpath" = "$pf" ]; then
      return 0
    fi
  done
  return 1
}

# ─── Step 4: Sync template ───────────────────────────────────────────────────

echo -e "${BOLD}Syncing:${RESET}"
echo "  • .claude/commands/  — slash commands (new + updated)"
echo "  • .claude/team-rules.md — agent definitions + rules"
echo "  • references/        — all reference files (new + updated)"
echo "  • CHEATSHEET.md      — quick reference card"
echo ""

TOTAL_UPDATED=0
TOTAL_NEW=0
TOTAL_SKIPPED=0

sync_template_dir() {
  local src_dir="$1"
  local dst_dir="$2"
  local rel_prefix="$3"

  mkdir -p "$dst_dir"

  for src_file in "$src_dir"/*; do
    [ -e "$src_file" ] || continue
    local filename=$(basename "$src_file")
    local relpath="${rel_prefix}${filename}"

    if [ -d "$src_file" ]; then
      sync_template_dir "$src_file" "$dst_dir/$filename" "${relpath}/"
    elif [ -f "$src_file" ]; then
      if is_protected "$relpath" && [ -f "$dst_dir/$filename" ]; then
        TOTAL_SKIPPED=$((TOTAL_SKIPPED + 1))
        continue
      fi

      if [ -f "$dst_dir/$filename" ]; then
        TOTAL_UPDATED=$((TOTAL_UPDATED + 1))
      else
        TOTAL_NEW=$((TOTAL_NEW + 1))
      fi
      cp "$src_file" "$dst_dir/$filename"
    fi
  done
}

echo -e "${DIM}Syncing template...${RESET}"
sync_template_dir "$TEMPLATE_DIR" "$PROJECT_DIR" ""

if [ $TOTAL_NEW -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Template synced ($TOTAL_UPDATED updated, ${BOLD}$TOTAL_NEW new${RESET}, $TOTAL_SKIPPED protected)"
else
  echo -e "${GREEN}✓${RESET} Template synced ($TOTAL_UPDATED updated, $TOTAL_SKIPPED protected)"
fi

# ─── Step 5: Update cheatsheet ────────────────────────────────────────────────

cp "$FRAMEWORK_DIR/CHEATSHEET.md" "$PROJECT_DIR/CHEATSHEET.md"
echo -e "${GREEN}✓${RESET} Updated CHEATSHEET.md"

# ─── Step 6: Create root-level template files if missing ─────────────────────

for root_file in DECISIONS.md CONTEXT.md; do
  if [ ! -f "$PROJECT_DIR/$root_file" ] && [ -f "$TEMPLATE_DIR/$root_file" ]; then
    cp "$TEMPLATE_DIR/$root_file" "$PROJECT_DIR/$root_file"
    echo -e "${GREEN}✓${RESET} Created $root_file (new in this version)"
  fi
done

# ─── Step 7: Update version stamp in CLAUDE.md ───────────────────────────────

if grep -q "Ship Framework" "$PROJECT_DIR/CLAUDE.md"; then
  sed -i "s|Ship Framework.*v[0-9.]*|Ship Framework](https://github.com/ismailkose/ship-framework) v${VERSION}|g" "$PROJECT_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Updated version stamp in CLAUDE.md footer"
else
  echo "" >> "$PROJECT_DIR/CLAUDE.md"
  echo "---" >> "$PROJECT_DIR/CLAUDE.md"
  echo "" >> "$PROJECT_DIR/CLAUDE.md"
  echo "_Generated by [Ship Framework](https://github.com/ismailkose/ship-framework) v${VERSION}_" >> "$PROJECT_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Added version stamp to CLAUDE.md"
fi

# ─── Step 8: Update self (this script) ────────────────────────────────────────
# Keep the update script itself current

if [ -f "$TEMPLATE_DIR/ship-update.sh" ]; then
  cp "$TEMPLATE_DIR/ship-update.sh" "$PROJECT_DIR/ship-update.sh"
  chmod +x "$PROJECT_DIR/ship-update.sh"
  echo -e "${GREEN}✓${RESET} Updated ship-update.sh (self-update)"
fi

# ─── Handle --add-framework flag ──────────────────────────────────────────────

prev_arg=""
for i in "$@"; do
  if [ "$prev_arg" = "--add-framework" ]; then
    mkdir -p "$PROJECT_DIR/references/frameworks"
    IFS=',' read -ra NEW_FW <<< "$i"
    for fw in "${NEW_FW[@]}"; do
      fw=$(echo "$fw" | xargs)
      if [ -f "$TEMPLATE_DIR/references/frameworks/${fw}.md" ]; then
        cp "$TEMPLATE_DIR/references/frameworks/${fw}.md" "$PROJECT_DIR/references/frameworks/"
        echo -e "${GREEN}✓${RESET} Added framework reference: ${fw}"
      else
        echo -e "${YELLOW}⚠${RESET}  Framework reference not found: ${fw}"
        echo -e "${DIM}  Available: $(ls "$TEMPLATE_DIR/references/frameworks/" 2>/dev/null | sed 's/\.md//g' | tr '\n' ', ' | sed 's/,$//')${RESET}"
      fi
    done
  fi
  prev_arg="$i"
done

# ─── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${ORANGE}Updated!${RESET} v${CURRENT_VERSION} → v${VERSION}"
echo ""
echo -e "${DIM}Your CLAUDE.md content, TASKS.md, and design-system.md are untouched.${RESET}"
echo -e "${DIM}All template files (commands, references, frameworks) are synced.${RESET}"
echo ""
