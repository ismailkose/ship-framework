#!/bin/bash

# Ship Framework — Interactive Setup
# Generates a customized CLAUDE.md, TASKS.md, and slash commands for your project.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE_DIR="$SCRIPT_DIR/template"

# Colors
BOLD='\033[1m'
DIM='\033[2m'
ORANGE='\033[38;5;208m'
GREEN='\033[32m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}${ORANGE}Ship Framework${RESET} — Setup"
echo -e "${DIM}Let's set up your AI product team.${RESET}"
echo ""

# ─── Step 1: Project info ───────────────────────────────────────────────────

read -p "What's your product called? > " PRODUCT_NAME
echo ""

read -p "Describe it in one sentence: > " PRODUCT_DESC
echo ""

echo -e "${DIM}Pick a tech stack, or type your own:${RESET}"
echo -e "${DIM}(Don't worry about versions — Arc will use the latest stable when building.)${RESET}"
echo ""
echo -e "  1) ${BOLD}Web App${RESET}         — Next.js, React, Tailwind CSS, shadcn/ui, Supabase"
echo -e "  2) ${BOLD}Mobile App${RESET}      — React Native (Expo), TypeScript, Supabase"
echo -e "  3) ${BOLD}iOS App${RESET}         — SwiftUI, Swift, CloudKit"
echo -e "  4) ${BOLD}Full-Stack Python${RESET} — FastAPI, Python, PostgreSQL, HTMX, Tailwind CSS"
echo -e "  5) ${BOLD}Static Site${RESET}     — Astro, Tailwind CSS, Markdown, Vercel"
echo -e "  6) ${BOLD}Custom${RESET}          — Type your own stack"
echo ""
read -p "> " STACK_CHOICE

case $STACK_CHOICE in
  1)
    TECH_STACK="Next.js, React, TypeScript, Tailwind CSS, shadcn/ui, Supabase, Vercel"
    ;;
  2)
    TECH_STACK="React Native (Expo), TypeScript, Supabase, EAS Build"
    ;;
  3)
    TECH_STACK="SwiftUI, Swift, CloudKit, Xcode"
    ;;
  4)
    TECH_STACK="FastAPI, Python, PostgreSQL, HTMX, Tailwind CSS, Uvicorn"
    ;;
  5)
    TECH_STACK="Astro, Tailwind CSS, Markdown, Vercel"
    ;;
  6|*)
    if [ "$STACK_CHOICE" != "6" ] && [ -n "$STACK_CHOICE" ]; then
      # They typed their stack directly instead of picking a number
      TECH_STACK="$STACK_CHOICE"
    else
      echo ""
      echo -e "${DIM}Type your stack (comma-separated):${RESET}"
      read -p "> " TECH_STACK
    fi
    ;;
esac
echo ""

echo -e "${DIM}What stage is the project at?${RESET}"
echo "  1) Starting fresh — no code yet"
echo "  2) In progress — some code exists"
echo "  3) Launched — live product, needs iteration"
read -p "> " STAGE_CHOICE
echo ""

# ─── Step 2: Target directory ───────────────────────────────────────────────

echo -e "${DIM}Where is your project? (path to project root)${RESET}"
echo -e "${DIM}Press Enter for current directory.${RESET}"
read -p "> " TARGET_DIR

if [ -z "$TARGET_DIR" ]; then
  TARGET_DIR="."
fi

# Resolve to absolute path
TARGET_DIR="$(cd "$TARGET_DIR" 2>/dev/null && pwd)" || {
  echo "Error: Directory not found: $TARGET_DIR"
  exit 1
}

echo ""

# ─── Generate CLAUDE.md ─────────────────────────────────────────────────────

# Parse tech stack into bullet points
IFS=',' read -ra STACK_ITEMS <<< "$TECH_STACK"
STACK_BULLETS=""
for item in "${STACK_ITEMS[@]}"; do
  trimmed="$(echo "$item" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
  STACK_BULLETS="${STACK_BULLETS}- ${trimmed}\n"
done

# Use python3 for safe template replacement (handles quotes, special chars)
python3 << 'PYEOF' - "$TEMPLATE_DIR/CLAUDE.md" "$TARGET_DIR/CLAUDE.md" "$PRODUCT_NAME" "$PRODUCT_DESC" "$STACK_BULLETS"
import sys

template_path = sys.argv[1]
output_path = sys.argv[2]
product_name = sys.argv[3]
product_desc = sys.argv[4]
stack_bullets = sys.argv[5].replace('\\n', '\n').strip()

with open(template_path, 'r') as f:
    template = f.read()

# Replace product name
template = template.replace('[Your Product Name]', product_name)

# Replace product description
template = template.replace(
    '<!-- Describe your product in 2-3 sentences. What does it do? Who is it for? -->',
    product_desc
)

# Replace tech stack placeholder
template = template.replace(
    '-\n-\n-',
    stack_bullets
)

with open(output_path, 'w') as f:
    f.write(template)
PYEOF

echo -e "${GREEN}✓${RESET} Created CLAUDE.md"

# ─── Copy slash commands ─────────────────────────────────────────────────────

mkdir -p "$TARGET_DIR/.claude/commands"
cp "$TEMPLATE_DIR/.claude/commands/"*.md "$TARGET_DIR/.claude/commands/"
echo -e "${GREEN}✓${RESET} Created .claude/commands/ (13 slash commands)"

# ─── Copy cheatsheet ─────────────────────────────────────────────────────────

cp "$SCRIPT_DIR/CHEATSHEET.md" "$TARGET_DIR/CHEATSHEET.md"
echo -e "${GREEN}✓${RESET} Created CHEATSHEET.md"

# ─── Create TASKS.md ─────────────────────────────────────────────────────────

# Set first tasks based on project stage
case $STAGE_CHOICE in
  1)
    FIRST_TASKS="1. [ ] Define product vision with /visionary
2. [ ] Create technical plan with /architect
3. [ ] Build the magic moment first"
    ;;
  2)
    FIRST_TASKS="1. [ ] Run /team Take over this project and tell me what needs work
2. [ ] Review the crit audit and decide priorities
3. [ ] Pick first task and /build it"
    ;;
  3)
    FIRST_TASKS="1. [ ] Run /critic for a full product audit
2. [ ] Run /polish for a design review
3. [ ] Prioritize and /build fixes"
    ;;
  *)
    FIRST_TASKS="1. [ ] First task
2. [ ] Second task"
    ;;
esac

cat > "$TARGET_DIR/TASKS.md" << TASKSEOF
# $PRODUCT_NAME — Team Task Board

> This is the team's persistent memory. /team reads this every session.
> When a task is done, move it to Completed with a date and one-line summary.
> When starting a task, mark it [IN PROGRESS] so the next session knows where we left off.

---

## Blocked (needs your decision)

<!-- Tasks that need a decision before work can continue -->

---

## Up Next (priority order)

$FIRST_TASKS

---

## In Progress

<!-- Tasks currently being worked on -->

---

## Completed

<!-- Format: [date] Task name — one-line summary of what was done -->

---

## Notes

<!-- Persistent notes the team needs across sessions.
     Examples: installed dependencies, design system info, API quirks, etc. -->

- Tech stack: $TECH_STACK
TASKSEOF

echo -e "${GREEN}✓${RESET} Created TASKS.md"

# ─── Summary ─────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${ORANGE}Done!${RESET} Your team is ready."
echo ""
echo "  Files created in: $TARGET_DIR"
echo "  • CLAUDE.md           — Your team framework"
echo "  • TASKS.md            — Persistent task board"
echo "  • CHEATSHEET.md       — Quick reference card"
echo "  • .claude/commands/   — 10 slash commands"
echo ""

# Show first step based on stage
case $STAGE_CHOICE in
  1)
    echo "  You're starting fresh. Open Claude Code and type:"
    echo ""
    echo -e "    ${BOLD}/team I want to build $PRODUCT_NAME${RESET}"
    ;;
  2)
    echo "  You have existing code. Open Claude Code and type:"
    echo ""
    echo -e "    ${BOLD}/team Take over this project and tell me what needs work${RESET}"
    ;;
  3)
    echo "  You're iterating on a live product. Open Claude Code and type:"
    echo ""
    echo -e "    ${BOLD}/team Review the product and give me a punch list${RESET}"
    ;;
  *)
    echo "  Open Claude Code and type:"
    echo ""
    echo -e "    ${BOLD}/team Take over this project and tell me what needs work${RESET}"
    ;;
esac

echo ""
