#!/bin/bash

# Ship Framework — Setup
# Zero-prompt install. Copies files, installs Playwright. That's it.
# All product context is gathered when you fill in CLAUDE.md.
#
# Usage:
#   bash ship-framework/setup.sh              # sets up in current directory
#   bash ship-framework/setup.sh ./my-project  # sets up in specified directory

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/template"
VERSION=$(cat "$SCRIPT_DIR/VERSION" 2>/dev/null || echo "unknown")

# Colors
BOLD='\033[1m'
DIM='\033[2m'
ORANGE='\033[38;5;208m'
GREEN='\033[32m'
YELLOW='\033[33m'
RESET='\033[0m'

# Cross-platform sed -i (macOS BSD sed vs GNU sed)
sedi() {
  if sed --version >/dev/null 2>&1; then
    sed -i "$@"
  else
    sed -i '' "$@"
  fi
}

echo ""
echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Setup"
echo ""

# ─── Target directory ─────────────────────────────────────────────────────
# Accept as argument or default to current directory

if [ -n "$1" ]; then
  TARGET_DIR="$1"
else
  TARGET_DIR="."
fi

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
  echo "Error: Directory not found: $TARGET_DIR"
  exit 1
}

# ─── Check for existing Ship Framework install ───────────────────────────────
# Detect v3 (## /team) or v4 (## Ship Framework) installs

if [ -f "$TARGET_DIR/CLAUDE.md" ]; then
  if grep -q "## /team\|## Ship Framework\|ship-framework" "$TARGET_DIR/CLAUDE.md" 2>/dev/null; then
    # Previous Ship Framework install — copy fresh update script and run it
    echo -e "${DIM}Found existing Ship Framework install. Running update...${RESET}"
    echo ""
    cp "$TEMPLATE_DIR/ship-update.sh" "$TARGET_DIR/ship-update.sh"
    chmod +x "$TARGET_DIR/ship-update.sh"
    bash "$TARGET_DIR/ship-update.sh"
    exit $?
  else
    # Their own CLAUDE.md — append mode
    echo -e "${YELLOW}⚠${RESET}  Found existing CLAUDE.md (not from Ship Framework)."
    echo -e "${DIM}Ship Framework will append to your existing file, not replace it.${RESET}"
    echo ""
  fi
fi

# ─── Generate CLAUDE.md ──────────────────────────────────────────────────────

if [ -f "$TARGET_DIR/CLAUDE.md" ]; then
  # Append Ship Framework to existing CLAUDE.md
  python3 << 'PYEOF' - "$TEMPLATE_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md" "$VERSION"
import sys

template_path = sys.argv[1]
output_path = sys.argv[2]
version = sys.argv[3]

with open(template_path, 'r') as f:
    template = f.read()

template = template.replace('__VERSION__', version)

with open(output_path, 'r') as f:
    existing = f.read()

merged = existing.rstrip() + '\n\n---\n\n'
merged += '<!-- Ship Framework team definitions below -->\n\n'
merged += template

with open(output_path, 'w') as f:
    f.write(merged)
PYEOF
  echo -e "${GREEN}✓${RESET} Appended Ship Framework to existing CLAUDE.md"
else
  # Fresh CLAUDE.md
  cp "$TEMPLATE_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md"
  sedi "s|__VERSION__|${VERSION}|g" "$TARGET_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Created CLAUDE.md"
fi

# ─── Copy team rules ─────────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/.claude"
cp "$TEMPLATE_DIR/.claude/team-rules.md" "$TARGET_DIR/.claude/team-rules.md"
echo -e "${GREEN}✓${RESET} Created .claude/team-rules.md (agent definitions + rules)"

# ─── Copy slash commands ──────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/.claude/commands"
cp "$TEMPLATE_DIR/.claude/commands/"*.md "$TARGET_DIR/.claude/commands/"
COMMAND_COUNT=$(ls "$TEMPLATE_DIR/.claude/commands/"*.md 2>/dev/null | wc -l | xargs)
echo -e "${GREEN}✓${RESET} Created .claude/commands/ ($COMMAND_COUNT slash commands)"

# ─── Copy skills ──────────────────────────────────────────────────────────────

# Framework skills
if [ -d "$TEMPLATE_DIR/.claude/skills/ship" ]; then
  mkdir -p "$TARGET_DIR/.claude/skills"
  cp -r "$TEMPLATE_DIR/.claude/skills/ship" "$TARGET_DIR/.claude/skills/ship"
  SKILL_COUNT=$(find "$TEMPLATE_DIR/.claude/skills/ship" -name "SKILL.md" 2>/dev/null | wc -l | xargs)
  echo -e "${GREEN}✓${RESET} Created .claude/skills/ship/ ($SKILL_COUNT framework skills)"
fi

# User skills directory (with README)
if [ -d "$TEMPLATE_DIR/.claude/skills/your-skills" ]; then
  mkdir -p "$TARGET_DIR/.claude/skills/your-skills"
  cp "$TEMPLATE_DIR/.claude/skills/your-skills/README.md" "$TARGET_DIR/.claude/skills/your-skills/README.md" 2>/dev/null
  echo -e "${GREEN}✓${RESET} Created .claude/skills/your-skills/ (add your own skills here)"
fi

# Skills README
if [ -f "$TEMPLATE_DIR/.claude/skills/README.md" ]; then
  cp "$TEMPLATE_DIR/.claude/skills/README.md" "$TARGET_DIR/.claude/skills/README.md"
fi

# ─── Copy references (platform-organized) ─────────────────────────────────────

# Shared references (always copied)
if [ -d "$TEMPLATE_DIR/references/shared" ]; then
  mkdir -p "$TARGET_DIR/references/shared"
  cp "$TEMPLATE_DIR/references/shared/"*.md "$TARGET_DIR/references/shared/" 2>/dev/null
  echo -e "${GREEN}✓${RESET} Created references/shared/ (UX principles, components, animation)"
fi

# iOS references
if [ -d "$TEMPLATE_DIR/references/ios" ]; then
  mkdir -p "$TARGET_DIR/references/ios"
  cp "$TEMPLATE_DIR/references/ios/"*.md "$TARGET_DIR/references/ios/" 2>/dev/null

  # iOS framework references (conditional)
  if [ -d "$TEMPLATE_DIR/references/ios/frameworks" ]; then
    mkdir -p "$TARGET_DIR/references/ios/frameworks"

    if [ -n "$SHIP_FRAMEWORKS" ]; then
      # Selective copy: SHIP_FRAMEWORKS="swiftdata,healthkit,storekit"
      IFS=',' read -ra SELECTED <<< "$SHIP_FRAMEWORKS"
      COPIED=0
      for fw in "${SELECTED[@]}"; do
        fw=$(echo "$fw" | xargs)
        if [ -f "$TEMPLATE_DIR/references/ios/frameworks/${fw}.md" ]; then
          cp "$TEMPLATE_DIR/references/ios/frameworks/${fw}.md" "$TARGET_DIR/references/ios/frameworks/"
          COPIED=$((COPIED + 1))
        else
          echo -e "${YELLOW}⚠${RESET}  Framework reference not found: ${fw}"
        fi
      done
      echo -e "${GREEN}✓${RESET} Created references/ios/frameworks/ ($COPIED selected)"
    else
      cp "$TEMPLATE_DIR/references/ios/frameworks/"*.md "$TARGET_DIR/references/ios/frameworks/" 2>/dev/null
      TOTAL=$(ls "$TEMPLATE_DIR/references/ios/frameworks/"*.md 2>/dev/null | wc -l | xargs)
      echo -e "${GREEN}✓${RESET} Created references/ios/frameworks/ ($TOTAL framework references)"
    fi
  fi
fi

# Create empty platform directories for future content
mkdir -p "$TARGET_DIR/references/web"
mkdir -p "$TARGET_DIR/references/android"
mkdir -p "$TARGET_DIR/references/cross-platform"

# ─── Copy cheatsheet ─────────────────────────────────────────────────────────

cp "$SCRIPT_DIR/CHEATSHEET.md" "$TARGET_DIR/CHEATSHEET.md"
echo -e "${GREEN}✓${RESET} Created CHEATSHEET.md"

# ─── Create persistent files ─────────────────────────────────────────────────

if [ -f "$TEMPLATE_DIR/TASKS.md" ] && [ ! -f "$TARGET_DIR/TASKS.md" ]; then
  cp "$TEMPLATE_DIR/TASKS.md" "$TARGET_DIR/TASKS.md"
  echo -e "${GREEN}✓${RESET} Created TASKS.md"
fi

if [ -f "$TEMPLATE_DIR/DECISIONS.md" ] && [ ! -f "$TARGET_DIR/DECISIONS.md" ]; then
  cp "$TEMPLATE_DIR/DECISIONS.md" "$TARGET_DIR/DECISIONS.md"
  echo -e "${GREEN}✓${RESET} Created DECISIONS.md"
fi

if [ -f "$TEMPLATE_DIR/CONTEXT.md" ] && [ ! -f "$TARGET_DIR/CONTEXT.md" ]; then
  cp "$TEMPLATE_DIR/CONTEXT.md" "$TARGET_DIR/CONTEXT.md"
  echo -e "${GREEN}✓${RESET} Created CONTEXT.md"
fi

# ─── Copy self-contained update script ────────────────────────────────────────

if [ -f "$TEMPLATE_DIR/ship-update.sh" ]; then
  cp "$TEMPLATE_DIR/ship-update.sh" "$TARGET_DIR/ship-update.sh"
  chmod +x "$TARGET_DIR/ship-update.sh"
  echo -e "${GREEN}✓${RESET} Created ship-update.sh (run /ship-update in Claude Code to update)"
fi

# ─── Install Playwright ──────────────────────────────────────────────────────

echo ""
echo -e "${DIM}Installing Playwright for visual QA...${RESET}"

if [ ! -f "$TARGET_DIR/package.json" ]; then
  echo '{ "name": "my-project", "private": true }' > "$TARGET_DIR/package.json"
fi

if (cd "$TARGET_DIR" && npm install -D @playwright/test 2>/dev/null) && \
   (cd "$TARGET_DIR" && npx playwright install chromium 2>/dev/null); then
  echo -e "${GREEN}✓${RESET} Installed Playwright — visual QA can take screenshots"
else
  echo -e "${DIM}⚠ Playwright install skipped (no Node.js or network issue).${RESET}"
  echo -e "${DIM}  Add later: npm install -D @playwright/test && npx playwright install chromium${RESET}"
fi

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${ORANGE}Done!${RESET} Your team is ready."
echo ""
echo "  ${BOLD}Two things to do:${RESET}"
echo ""
echo "  1. Fill in CLAUDE.md:"
echo "     • The Product — what you're building (2-3 sentences)"
echo "     • The Founder — how you think and work (shapes how the team talks to you)"
echo "     • Stack — your tech stack (determines which references load)"
echo ""
echo "  2. Open Claude Code and type:"
echo ""
echo -e "     ${BOLD}/ship-team I want to build [your idea]${RESET}"
echo ""
echo -e "${DIM}Run /ship-update anytime to get the latest version.${RESET}"
echo ""
