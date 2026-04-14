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

# ─── Ensure git repo exists ──────────────────────────────────────────────────
# Claude Code requires a git repo to discover .claude/commands/

if [ ! -d "$TARGET_DIR/.git" ]; then
  (cd "$TARGET_DIR" && git init --quiet)
  echo -e "${GREEN}✓${RESET} Initialized git repo (required for Claude Code to detect commands)"
fi

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

# ─── Copy slash commands as skills ───────────────────────────────────────────
# Claude Code v2.1.88+ has a bug where .claude/commands/ aren't discovered.
# Skills format (.claude/skills/<name>/SKILL.md) works reliably across all versions.

COMMAND_COUNT=0
for cmd_file in "$TEMPLATE_DIR/.claude/commands/ship-"*.md; do
  [ -e "$cmd_file" ] || continue
  cmd_name=$(basename "$cmd_file" .md)
  mkdir -p "$TARGET_DIR/.claude/skills/$cmd_name"
  cp "$cmd_file" "$TARGET_DIR/.claude/skills/$cmd_name/SKILL.md"
  COMMAND_COUNT=$((COMMAND_COUNT + 1))
done
echo -e "${GREEN}✓${RESET} Created .claude/skills/ ($COMMAND_COUNT slash commands)"

# Also keep .claude/commands/ for backward compatibility with older Claude Code versions
mkdir -p "$TARGET_DIR/.claude/commands"
cp "$TEMPLATE_DIR/.claude/commands/"*.md "$TARGET_DIR/.claude/commands/"

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

# ─── Register hooks in settings.json ─────────────────────────────────────────
# SKILL.md frontmatter defines hook intent, but Claude Code only executes hooks
# registered in .claude/settings.json. This writes the hook config.

SETTINGS_FILE="$TARGET_DIR/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
  # settings.json exists — merge hooks if not already present
  if ! grep -q '"PreToolUse"' "$SETTINGS_FILE" 2>/dev/null; then
    # No hooks yet — add them. Use python for safe JSON merge.
    python3 -c "
import json, sys
with open('$SETTINGS_FILE') as f:
    data = json.load(f)
hooks = data.setdefault('hooks', {})
hooks['SessionStart'] = [{'hooks': [{'type': 'command', 'command': 'bash .claude/skills/ship/sessionstart/bin/session-start.sh', 'timeout': 5000}]}]
hooks['PreToolUse'] = [
    {'matcher': 'Edit', 'hooks': [{'type': 'command', 'command': 'bash .claude/skills/ship/refgate/bin/check-refgate.sh'}]},
    {'matcher': 'Write', 'hooks': [{'type': 'command', 'command': 'bash .claude/skills/ship/refgate/bin/check-refgate.sh'}]}
]
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" 2>/dev/null && echo -e "${GREEN}✓${RESET} Registered hooks in .claude/settings.json (refgate)" || {
      echo -e "${YELLOW}⚠${RESET} Could not merge hooks into existing settings.json — add manually"
    }
  else
    echo -e "${DIM}  Hooks already registered in settings.json${RESET}"
  fi
else
  # No settings.json — create it with hooks
  cat > "$SETTINGS_FILE" << 'HOOKS_EOF'
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/ship/sessionstart/bin/session-start.sh",
            "timeout": 5000
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/ship/refgate/bin/check-refgate.sh"
          }
        ]
      },
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "bash .claude/skills/ship/refgate/bin/check-refgate.sh"
          }
        ]
      }
    ]
  }
}
HOOKS_EOF
  echo -e "${GREEN}✓${RESET} Created .claude/settings.json (hooks: refgate)"
fi

# ─── References ──────────────────────────────────────────────────────────────
# Framework references now live inside skill directories (.claude/skills/ship/*/references/)
# and are already copied by the cp -r above. The root references/ directory is for user content.

mkdir -p "$TARGET_DIR/references"
if [ -f "$TEMPLATE_DIR/references/README.md" ]; then
  cp "$TEMPLATE_DIR/references/README.md" "$TARGET_DIR/references/README.md"
fi

REF_COUNT=$(find "$TARGET_DIR/.claude/skills/ship" -path "*/references/*.md" -type f 2>/dev/null | wc -l | xargs)
echo -e "${GREEN}✓${RESET} References loaded ($REF_COUNT files across skill directories)"

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

if [ -f "$TEMPLATE_DIR/LEARNINGS.md" ] && [ ! -f "$TARGET_DIR/LEARNINGS.md" ]; then
  cp "$TEMPLATE_DIR/LEARNINGS.md" "$TARGET_DIR/LEARNINGS.md"
  echo -e "${GREEN}✓${RESET} Created LEARNINGS.md (team memory across sessions)"
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
