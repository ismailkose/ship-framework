#!/usr/bin/env bash
# Ship Framework — dimension-aware reference gate hook
# Classifies edits by design dimension (ui/motion/copy/logic/none),
# checks PDC.md for the relevant section, and blocks until it's been read.
# Hard-blocks all design-dimension edits when PDC.md is missing entirely.
#
# Returns JSON on stdout (single line):
#   Allow: {}
#   Deny:  {"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"..."}}
#
# Input: JSON on stdin with tool_input.file_path

set -euo pipefail

REFS_LOADED=".claude/.refgate-loaded"
PDC_FILE="PDC.md"
DEBUG_LOG="/tmp/refgate-debug.log"

# ── Helper: output deny JSON ─────────────────────────────────────────────────

deny() {
  local msg="$1"
  echo "RESULT: deny — $msg" >> "$DEBUG_LOG"
  echo "{\"hookSpecificOutput\":{\"hookEventName\":\"PreToolUse\",\"permissionDecision\":\"deny\",\"permissionDecisionReason\":\"$msg\"}}"
  exit 0
}

allow() {
  echo "RESULT: allow" >> "$DEBUG_LOG"
  echo '{}'
  exit 0
}

# ── Extract file path from stdin JSON ────────────────────────────────────────

INPUT=$(cat)
echo "--- $(date) ---" >> "$DEBUG_LOG"

FILE_PATH=$(echo "$INPUT" | grep -o '"file_path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/.*"file_path"[[:space:]]*:[[:space:]]*"//' | sed 's/"$//')
echo "FILE_PATH: $FILE_PATH" >> "$DEBUG_LOG"

# If we can't extract a file path, allow (fail open)
if [ -z "$FILE_PATH" ]; then
  allow
fi

# ── Whitelist: design system files are never blocked ─────────────────────────
# These are the files the gate enforces — don't block their creation.

case "$FILE_PATH" in
  */DESIGN.md|*/PDC.md|*/TASTE.md|*/design/*.md|*/.claude/*|*/LEARNINGS.md|*/DECISIONS.md|*/TASKS.md|*/CONTEXT.md|*/CLAUDE.md|*/AGENTS.md)
    allow
    ;;
esac

# ── Classify dimension by file path ──────────────────────────────────────────

classify_dimension() {
  local fp="$1"
  case "$fp" in
    */test/*|*/tests/*|*/__tests__/*|*_test.*|*.test.*|*.spec.*)
      echo "none" ;;
    *animation*|*Animation*|*motion*|*Motion*|*transition*|*Transition*|*/animations/*)
      echo "motion" ;;
    */Localizable*|*/i18n/*|*/locales/*|*/strings/*|*copy*|*Copy*|*/en.json|*/en.ts)
      echo "copy" ;;
    */models/*|*/Models/*|*/services/*|*/Services/*|*/utils/*|*/Utils/*|*/lib/*|*/helpers/*|*/api/*|*/API/*|*/store/*|*/Store/*|*/hooks/*|*/middleware/*)
      echo "logic" ;;
    */views/*|*/Views/*|*/screens/*|*/Screens/*|*/components/*|*/Components/*|*/UI/*|*/pages/*|*/Pages/*|*/layouts/*|*/Layouts/*|*.css|*.scss|*.less|*/styles/*|*/Styles/*|*.storyboard|*.xib)
      echo "ui" ;;
    *)
      echo "ui" ;;
  esac
}

DIMENSION=$(classify_dimension "$FILE_PATH")
echo "DIMENSION: $DIMENSION | CWD: $(pwd) | PDC: $([ -f "$PDC_FILE" ] && echo yes || echo no)" >> "$DEBUG_LOG"

# ── No gate for logic or test files ──────────────────────────────────────────

if [ "$DIMENSION" = "logic" ] || [ "$DIMENSION" = "none" ]; then
  allow
fi

# ── Design dimension: check PDC.md exists ────────────────────────────────────

if [ ! -f "$PDC_FILE" ]; then
  if [ -f "DESIGN.md" ]; then
    deny "Design Gate: DESIGN.md exists but no PDC.md manifest. Run /ship-design init to generate PDC.md from your existing design system."
  else
    deny "Design Gate: No design contract found. Run /ship-design init to scaffold DESIGN.md + PDC.md. Without it, design consistency cannot be enforced."
  fi
fi

# ── Backward compat: framework references must be loaded ─────────────────────

if [ ! -f "$REFS_LOADED" ]; then
  deny "Reference Gate: Load references before editing. Run your /ship-* command first, or read the relevant references/ files."
fi

# ── Check if the relevant design section has been read this session ───────────

DIM_MARKER=".claude/.refgate-dim-${DIMENSION}"

if [ -f "$DIM_MARKER" ]; then
  allow
fi

# Look up the section path in PDC.md
case "$DIMENSION" in
  ui)     SECTION_KEYS="overview colors typography components donts" ;;
  motion) SECTION_KEYS="motion" ;;
  copy)   SECTION_KEYS="copy" ;;
  *)      SECTION_KEYS="" ;;
esac

SECTION_PATH=""
for key in $SECTION_KEYS; do
  match=$(grep -m1 "^  ${key}:" "$PDC_FILE" 2>/dev/null | sed "s/^  ${key}:[[:space:]]*//" | xargs 2>/dev/null || true)
  if [ -n "$match" ]; then
    SECTION_PATH="$match"
    break
  fi
done

if [ -z "$SECTION_PATH" ]; then
  allow
fi

deny "Design Gate: This edit touches ${DIMENSION}. Read ${SECTION_PATH} first, or run the relevant /ship-* command to load design context."
