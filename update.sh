#!/bin/bash

# Ship Framework — Update
# Zero-prompt update. Syncs the full template structure to your project.
# Does NOT overwrite user-customized files (CLAUDE.md content, TASKS.md, design-system.md).
#
# Usage:
#   bash ship-framework/update.sh              # updates current directory
#   bash ship-framework/update.sh ./my-project  # updates specified directory
#   bash ship-framework/update.sh ./my-project --add-framework healthkit,storekit

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/template"

# Colors
BOLD='\033[1m'
DIM='\033[2m'
ORANGE='\033[38;5;208m'
GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

# ─── Protected files ────────────────────────────────────────────────────────
# These are NEVER overwritten — they contain user customizations.
# New template files ARE added if they don't exist yet in the project.

PROTECTED_FILES=(
  "CLAUDE.md"          # User's product rules, design system, agent customizations
  "TASKS.md"           # User's task board
  "references/design-system.md"  # User's design tokens
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

# ─── Pull latest version ────────────────────────────────────────────────────

echo ""
echo -e "${DIM}Checking for updates...${RESET}"

if [ -d "$SCRIPT_DIR/.git" ]; then
  (cd "$SCRIPT_DIR" && git pull --quiet 2>/dev/null) && \
  echo -e "${GREEN}✓${RESET} Pulled latest from GitHub" || \
  echo -e "${YELLOW}⚠${RESET} Could not pull latest — continuing with local version"
fi

VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

echo ""
echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Update"
echo ""

# ─── Step 1: Find project directory ──────────────────────────────────────────

if [ -n "$1" ] && [ "${1:0:2}" != "--" ]; then
  TARGET_DIR="$1"
else
  TARGET_DIR="."
fi

TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
  echo "Error: Directory not found: $TARGET_DIR"
  exit 1
}

# ─── Step 2: Check for existing install ──────────────────────────────────────

if [ ! -f "$TARGET_DIR/CLAUDE.md" ]; then
  echo ""
  echo -e "${YELLOW}⚠${RESET} No CLAUDE.md found in $TARGET_DIR"
  echo "  Run setup.sh first to create a new project."
  exit 1
fi

if [ ! -d "$TARGET_DIR/.claude/commands" ]; then
  echo ""
  echo -e "${YELLOW}⚠${RESET} No .claude/commands/ found in $TARGET_DIR"
  echo "  Run setup.sh first to create a new project."
  exit 1
fi

# ─── Step 3: Detect current version ─────────────────────────────────────────

CURRENT_VERSION=$(grep -oP 'Ship Framework.*?v\K[0-9.]+' "$TARGET_DIR/CLAUDE.md" 2>/dev/null || echo "unknown")

echo ""
echo -e "  Project:          ${BOLD}$TARGET_DIR${RESET}"
echo -e "  Installed version: ${BOLD}$CURRENT_VERSION${RESET}"
echo -e "  Latest version:    ${BOLD}$VERSION${RESET}"
echo ""

if [ "$CURRENT_VERSION" = "$VERSION" ]; then
  echo -e "${GREEN}✓${RESET} Already up to date."
  echo ""
  exit 0
fi

# ─── Step 4: Show what changed ───────────────────────────────────────────────

if [ -f "$SCRIPT_DIR/CHANGELOG.md" ]; then
  echo -e "${BOLD}What's new in v${VERSION}:${RESET}"
  echo ""
  sed -n '/^## '"$VERSION"'/,/^## [0-9]/{ /^## [0-9]/!p; }' "$SCRIPT_DIR/CHANGELOG.md"
  echo ""
fi

# ─── Step 5: Show what will be updated ───────────────────────────────────────

echo -e "${BOLD}This will sync from template:${RESET}"
echo "  • .claude/commands/  — slash commands (new + updated)"
echo "  • references/        — all reference files (new + updated)"
echo "  • CHEATSHEET.md      — quick reference card"
echo "  • Any new template files added in this version"
echo ""
echo -e "${DIM}This will NOT touch:${RESET}"
echo "  • CLAUDE.md content  — your product rules, design system, agent customizations"
echo "  • TASKS.md           — your task board"
echo "  • references/design-system.md — your design tokens"
echo ""
echo ""

# ─── Step 6: Generic template sync ──────────────────────────────────────────
# Walks the entire template/ directory and syncs to the project.
# - New files: created
# - Existing files: updated (unless protected)
# - New directories: created
# - Protected files: never touched if they exist

TOTAL_UPDATED=0
TOTAL_NEW=0
TOTAL_SKIPPED=0

sync_template_dir() {
  local src_dir="$1"
  local dst_dir="$2"
  local rel_prefix="$3"  # relative path prefix for display and protection check

  mkdir -p "$dst_dir"

  # Sync files
  for src_file in "$src_dir"/*; do
    [ -e "$src_file" ] || continue
    local filename=$(basename "$src_file")
    local relpath="${rel_prefix}${filename}"

    if [ -d "$src_file" ]; then
      # Directory — recurse
      if [ -d "$dst_dir/$filename" ]; then
        sync_template_dir "$src_file" "$dst_dir/$filename" "${relpath}/"
      else
        # New directory — create and copy everything
        mkdir -p "$dst_dir/$filename"
        sync_template_dir "$src_file" "$dst_dir/$filename" "${relpath}/"
      fi
    elif [ -f "$src_file" ]; then
      # File — check protection
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

# Sync template/ → project root
echo -e "${DIM}Syncing template...${RESET}"
sync_template_dir "$TEMPLATE_DIR" "$TARGET_DIR" ""

if [ $TOTAL_NEW -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Template synced ($TOTAL_UPDATED updated, ${BOLD}$TOTAL_NEW new${RESET}, $TOTAL_SKIPPED protected)"
else
  echo -e "${GREEN}✓${RESET} Template synced ($TOTAL_UPDATED updated, $TOTAL_SKIPPED protected)"
fi

# ─── Step 7: Update cheatsheet ───────────────────────────────────────────────

cp "$SCRIPT_DIR/CHEATSHEET.md" "$TARGET_DIR/CHEATSHEET.md"
echo -e "${GREEN}✓${RESET} Updated CHEATSHEET.md"

# ─── Step 8: Create root-level template files if missing ─────────────────────
# Files that live at project root (not inside template/) but ship with the framework.

for root_file in DECISIONS.md CONTEXT.md; do
  if [ ! -f "$TARGET_DIR/$root_file" ] && [ -f "$TEMPLATE_DIR/$root_file" ]; then
    cp "$TEMPLATE_DIR/$root_file" "$TARGET_DIR/$root_file"
    echo -e "${GREEN}✓${RESET} Created $root_file (new in this version)"
  fi
done

# ─── Step 9: Update version stamp in CLAUDE.md ──────────────────────────────

if grep -q "Ship Framework" "$TARGET_DIR/CLAUDE.md"; then
  sed -i "s|Ship Framework.*v[0-9.]*|Ship Framework](https://github.com/ismailkose/ship-framework) v${VERSION}|g" "$TARGET_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Updated version stamp in CLAUDE.md footer"
else
  echo "" >> "$TARGET_DIR/CLAUDE.md"
  echo "---" >> "$TARGET_DIR/CLAUDE.md"
  echo "" >> "$TARGET_DIR/CLAUDE.md"
  echo "_Generated by [Ship Framework](https://github.com/ismailkose/ship-framework) v${VERSION}_" >> "$TARGET_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Added version stamp to CLAUDE.md"
fi

# ─── Handle --add-framework flag ─────────────────────────────────────────────

# Check all args for --add-framework
for i in "$@"; do
  if [ "$prev_arg" = "--add-framework" ]; then
    mkdir -p "$TARGET_DIR/references/frameworks"
    IFS=',' read -ra NEW_FW <<< "$i"
    for fw in "${NEW_FW[@]}"; do
      fw=$(echo "$fw" | xargs)
      if [ -f "$TEMPLATE_DIR/references/frameworks/${fw}.md" ]; then
        cp "$TEMPLATE_DIR/references/frameworks/${fw}.md" "$TARGET_DIR/references/frameworks/"
        echo -e "${GREEN}✓${RESET} Added framework reference: ${fw}"
      else
        echo -e "${YELLOW}⚠${RESET}  Framework reference not found: ${fw}"
        echo -e "${DIM}  Available: $(ls "$TEMPLATE_DIR/references/frameworks/" 2>/dev/null | sed 's/\.md//g' | tr '\n' ', ' | sed 's/,$//')${RESET}"
      fi
    done
  fi
  prev_arg="$i"
done

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${ORANGE}Updated!${RESET} v${CURRENT_VERSION} → v${VERSION}"
echo ""
echo -e "${DIM}Your CLAUDE.md content, TASKS.md, and design-system.md are untouched.${RESET}"
echo -e "${DIM}All template files (commands, references, frameworks) are synced.${RESET}"
echo ""
