#!/bin/bash

# Ship Framework — Self-Contained Update
# Lives inside your project. No external clone needed.
# Pulls the latest from GitHub into a temp directory, syncs, cleans up.
#
# Handles v3→v4 migration automatically:
#   - Removes old command files (plan.md → ship-plan.md)
#   - Moves references to platform subdirectories
#   - Creates skills directory
#   - Adds The Founder section placeholder to CLAUDE.md
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

# ─── Cross-platform sed -i (macOS BSD sed vs GNU sed) ────────────────────────
sedi() {
  if sed --version >/dev/null 2>&1; then
    # GNU sed
    sed -i "$@"
  else
    # BSD sed (macOS) — requires '' after -i
    sed -i '' "$@"
  fi
}

# ─── Step 1: Verify this is a Ship Framework project ─────────────────────────

if [ ! -f "$PROJECT_DIR/CLAUDE.md" ] || [ ! -d "$PROJECT_DIR/.claude/commands" ]; then
  echo ""
  echo -e "${RED}✗${RESET} This doesn't look like a Ship Framework project."
  echo "  Expected CLAUDE.md and .claude/commands/ in: $PROJECT_DIR"
  exit 1
fi

# macOS-compatible: BSD grep doesn't support -P (Perl regex), use sed instead
CURRENT_VERSION=$(sed -n 's/.*Ship Framework.*v\([0-9.]*\).*/\1/p' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null | head -1)
CURRENT_VERSION="${CURRENT_VERSION:-unknown}"

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

# ─── Self-heal: update this script first, then re-exec if changed ───────────
# Prevents "old script can't parse new features" failures.
if [ -f "$TEMPLATE_DIR/ship-update.sh" ] && [ "${SHIP_UPDATE_REEXEC:-}" != "1" ]; then
  if ! diff -q "$PROJECT_DIR/ship-update.sh" "$TEMPLATE_DIR/ship-update.sh" > /dev/null 2>&1; then
    cp "$TEMPLATE_DIR/ship-update.sh" "$PROJECT_DIR/ship-update.sh"
    chmod +x "$PROJECT_DIR/ship-update.sh"
    echo -e "${DIM}Script updated — restarting...${RESET}"
    SHIP_UPDATE_REEXEC=1 exec bash "$PROJECT_DIR/ship-update.sh" "$@"
  fi
fi

echo ""
echo -e "${BOLD}${ORANGE}Ship Framework${RESET} v${VERSION} — Update"
echo ""
echo -e "  Project:           ${BOLD}$PROJECT_DIR${RESET}"
echo -e "  Installed version: ${BOLD}$CURRENT_VERSION${RESET}"
echo -e "  Latest version:    ${BOLD}$VERSION${RESET}"
echo ""

if [ "$CURRENT_VERSION" = "$VERSION" ]; then
  # Still mirror commands as skills even if version matches (fixes Claude Code v2.1.88+ bug)
  SKILLS_SYNCED=0
  for cmd_file in "$PROJECT_DIR/.claude/commands/"*.md; do
    [ -e "$cmd_file" ] || continue
    cmd_name=$(basename "$cmd_file" .md)
    mkdir -p "$PROJECT_DIR/.claude/skills/$cmd_name"
    cp "$cmd_file" "$PROJECT_DIR/.claude/skills/$cmd_name/SKILL.md"
    SKILLS_SYNCED=$((SKILLS_SYNCED + 1))
  done
  if [ $SKILLS_SYNCED -gt 0 ]; then
    echo -e "${GREEN}✓${RESET} Verified $SKILLS_SYNCED commands mirrored as skills"
  fi
  echo -e "${GREEN}✓${RESET} Already up to date."
  echo ""
  exit 0
fi

# ─── Step 3: Show what changed ────────────────────────────────────────────────

if [ -f "$FRAMEWORK_DIR/CHANGELOG.md" ]; then
  echo -e "${BOLD}What's new in v${VERSION}:${RESET}"
  echo ""
  sed -n '/^## '"$VERSION"'/,/^## [0-9]/{ /^## [0-9]/!p; }' "$FRAMEWORK_DIR/CHANGELOG.md" | head -30
  echo ""
fi

# ─── Protected files ─────────────────────────────────────────────────────────
# These are NEVER overwritten — they contain user customizations.

PROTECTED_FILES=(
  "CLAUDE.md"
  "TASKS.md"
  "DECISIONS.md"
  "CONTEXT.md"
  "LEARNINGS.md"
  "DESIGN.md"
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

# ─── Step 4: Detect v3 install and migrate ────────────────────────────────────
# v3 had commands without ship- prefix and flat reference structure.
# v4 has ship- prefixed commands, skills/, and platform-organized references.

V3_MIGRATION=false

# Check for old v3 command files (without ship- prefix)
OLD_V3_COMMANDS=(
  "plan.md" "build.md" "review.md" "qa.md" "ship.md"
  "fix.md" "money.md" "browse.md" "team.md" "retro.md" "update.md"
  "visionary.md" "architect.md" "critic.md" "polish.md"
  "health.md" "status.md"
)

for old_cmd in "${OLD_V3_COMMANDS[@]}"; do
  if [ -f "$PROJECT_DIR/.claude/commands/$old_cmd" ]; then
    V3_MIGRATION=true
    break
  fi
done

if [ "$V3_MIGRATION" = true ]; then
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}Migrating from v3 → v4${RESET}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""

  # ── Remove old v3 command files ──
  REMOVED_COMMANDS=0
  for old_cmd in "${OLD_V3_COMMANDS[@]}"; do
    if [ -f "$PROJECT_DIR/.claude/commands/$old_cmd" ]; then
      rm "$PROJECT_DIR/.claude/commands/$old_cmd"
      REMOVED_COMMANDS=$((REMOVED_COMMANDS + 1))
    fi
  done
  if [ $REMOVED_COMMANDS -gt 0 ]; then
    echo -e "${GREEN}✓${RESET} Removed $REMOVED_COMMANDS old v3 commands (replaced by /ship-* versions)"
  fi

  # ── Move root-level references to shared/ ──
  OLD_SHARED_REFS=(
    "animation.md" "animation-css.md" "animation-framer-motion.md"
    "animation-performance.md" "components.md" "ux-principles.md"
  )
  MOVED_REFS=0
  if [ -d "$PROJECT_DIR/references" ]; then
    mkdir -p "$PROJECT_DIR/references/shared"
    for ref in "${OLD_SHARED_REFS[@]}"; do
      if [ -f "$PROJECT_DIR/references/$ref" ] && [ ! -f "$PROJECT_DIR/references/shared/$ref" ]; then
        mv "$PROJECT_DIR/references/$ref" "$PROJECT_DIR/references/shared/$ref"
        MOVED_REFS=$((MOVED_REFS + 1))
      elif [ -f "$PROJECT_DIR/references/$ref" ] && [ -f "$PROJECT_DIR/references/shared/$ref" ]; then
        # New version already exists, just remove old
        rm "$PROJECT_DIR/references/$ref"
        MOVED_REFS=$((MOVED_REFS + 1))
      fi
    done
  fi
  if [ $MOVED_REFS -gt 0 ]; then
    echo -e "${GREEN}✓${RESET} Moved $MOVED_REFS reference files to references/shared/"
  fi

  # ── Move root-level iOS references ──
  OLD_IOS_ROOT_REFS=("hig-ios.md" "swiftui-core.md" "swift-essentials.md")
  MOVED_IOS=0
  if [ -d "$PROJECT_DIR/references" ]; then
    mkdir -p "$PROJECT_DIR/references/ios"
    for ref in "${OLD_IOS_ROOT_REFS[@]}"; do
      if [ -f "$PROJECT_DIR/references/$ref" ] && [ ! -f "$PROJECT_DIR/references/ios/$ref" ]; then
        mv "$PROJECT_DIR/references/$ref" "$PROJECT_DIR/references/ios/$ref"
        MOVED_IOS=$((MOVED_IOS + 1))
      elif [ -f "$PROJECT_DIR/references/$ref" ]; then
        rm "$PROJECT_DIR/references/$ref"
        MOVED_IOS=$((MOVED_IOS + 1))
      fi
    done
  fi

  # ── Clean up any remaining root-level .md files that now live in subdirs ──
  CLEANED_ROOT=0
  for old_file in "$PROJECT_DIR/references/"*.md; do
    [ -f "$old_file" ] || continue
    fname=$(basename "$old_file")
    # If the file exists in ios/ or shared/, the root copy is stale
    if [ -f "$PROJECT_DIR/references/ios/$fname" ] || [ -f "$PROJECT_DIR/references/shared/$fname" ]; then
      rm "$old_file"
      CLEANED_ROOT=$((CLEANED_ROOT + 1))
    fi
  done
  if [ $CLEANED_ROOT -gt 0 ]; then
    echo -e "${GREEN}✓${RESET} Removed $CLEANED_ROOT stale root-level reference files (moved to subdirs)"
  fi

  # ── Move frameworks/ to ios/frameworks/ ──
  if [ -d "$PROJECT_DIR/references/frameworks" ] && [ ! -d "$PROJECT_DIR/references/ios/frameworks" ]; then
    mkdir -p "$PROJECT_DIR/references/ios"
    mv "$PROJECT_DIR/references/frameworks" "$PROJECT_DIR/references/ios/frameworks"
    echo -e "${GREEN}✓${RESET} Moved references/frameworks/ → references/ios/frameworks/"
  elif [ -d "$PROJECT_DIR/references/frameworks" ] && [ -d "$PROJECT_DIR/references/ios/frameworks" ]; then
    # Both exist — remove old, keep new
    rm -rf "$PROJECT_DIR/references/frameworks"
    echo -e "${GREEN}✓${RESET} Cleaned up old references/frameworks/ (now at references/ios/frameworks/)"
  fi

  # ── Create references directory for user content ──
  mkdir -p "$PROJECT_DIR/references"

  # ── Create skills directory structure ──
  if [ ! -d "$PROJECT_DIR/.claude/skills" ]; then
    echo -e "${GREEN}✓${RESET} Created .claude/skills/ (new in v4)"
  fi

  # ── Add The Founder section to CLAUDE.md if missing ──
  if ! grep -q "## The Founder" "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
    # Find where to insert — after ## The Product or after the first ---
    python3 << 'PYEOF' - "$PROJECT_DIR/CLAUDE.md"
import sys

filepath = sys.argv[1]
with open(filepath, 'r') as f:
    content = f.read()

founder_section = """
## The Founder

<!-- NEW in v4: This tells the team how to work with YOU.
     Every persona reads this and adapts their communication style.
     Fill in each field — delete the examples in brackets. -->

Background: [e.g., "Product designer" / "Design engineer" / "PM who thinks in flows"]
Technical comfort: [e.g., "Can read code and review diffs" / "Full-stack" / "Non-technical"]
Decision style: [e.g., "One strong recommendation" / "Show me options"]
Communication: [e.g., "Short and direct" / "Walk me through it"]
Taste: [e.g., "Craft-obsessed" / "Ship fast, polish later"]
Context need: [e.g., "I need the why before I commit" / "Just tell me what to do"]
Focus awareness: [e.g., "I can get deep into details" / "I stay high-level"]
"""

# Insert after ## The Product section or at the top after the first heading
if '## The Product' in content:
    # Find the next ## after ## The Product
    idx = content.index('## The Product')
    rest = content[idx + len('## The Product'):]
    next_section = rest.find('\n## ')
    if next_section != -1:
        insert_point = idx + len('## The Product') + next_section
        content = content[:insert_point] + '\n' + founder_section + content[insert_point:]
    else:
        content = content + '\n' + founder_section
elif '## Stack' in content:
    idx = content.index('## Stack')
    content = content[:idx] + founder_section + '\n' + content[idx:]
else:
    # Append at end
    content = content + '\n' + founder_section

with open(filepath, 'w') as f:
    f.write(content)
PYEOF
    echo -e "${GREEN}✓${RESET} Added The Founder section to CLAUDE.md (fill it in to personalize your team)"
  fi

  # ── Update old command references in CLAUDE.md ──
  # Replace /team with /ship-team, /plan with /ship-plan, etc.
  if grep -q '`/team' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null || \
     grep -q '`/plan' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
    # macOS-compatible: use sedi helper for cross-platform sed -i
    sedi 's|`/team`|`/ship-team`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/plan`|`/ship-plan`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/build`|`/ship-build`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/review`|`/ship-review`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/qa`|`/ship-qa`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/ship`|`/ship-launch`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/fix`|`/ship-fix`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/money`|`/ship-money`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/browse`|`/ship-browse`|g' "$PROJECT_DIR/CLAUDE.md"
    sedi 's|`/retro`|`/ship-retro`|g' "$PROJECT_DIR/CLAUDE.md"
    # Fix any double-prefix from /ship → /ship-launch
    sedi 's|`/ship-launch-|`/ship-|g' "$PROJECT_DIR/CLAUDE.md"
    echo -e "${GREEN}✓${RESET} Updated command references in CLAUDE.md (/plan → /ship-plan, etc.)"
  fi

  echo ""
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}v3 → v4 migration complete${RESET}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""
fi

# ─── Step 4a: v4 → v4.1 migration (ship-qa deprecation) ────────────────────
# Users on v4 (pre-2026.04.06) may have /ship-qa references in CLAUDE.md or TASKS.md

if grep -q '/ship-qa' "$PROJECT_DIR/CLAUDE.md" 2>/dev/null; then
  sedi 's|/ship-qa|/ship-review --test|g' "$PROJECT_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Updated /ship-qa → /ship-review --test in CLAUDE.md"
fi

if [ -f "$PROJECT_DIR/TASKS.md" ] && grep -q '/ship-qa' "$PROJECT_DIR/TASKS.md" 2>/dev/null; then
  sedi 's|/ship-qa|/ship-review --test|g' "$PROJECT_DIR/TASKS.md"
  echo -e "${GREEN}✓${RESET} Updated /ship-qa → /ship-review --test in TASKS.md"
fi

# ─── Step 4b: Migration helper — back up customizable routing files ──────────
# ship-team.md contains the Task Routing table that users often customize.
# Back it up before overwriting so they can see what changed and re-apply.

MIGRATION_WARNINGS=""

if [ -f "$PROJECT_DIR/.claude/commands/ship-team.md" ] && [ -f "$TEMPLATE_DIR/.claude/commands/ship-team.md" ]; then
  # Check if user's file differs from the NEW template (i.e., they'll lose changes)
  if ! diff -q "$PROJECT_DIR/.claude/commands/ship-team.md" "$TEMPLATE_DIR/.claude/commands/ship-team.md" > /dev/null 2>&1; then
    # Back up the current version
    cp "$PROJECT_DIR/.claude/commands/ship-team.md" "$PROJECT_DIR/.claude/commands/ship-team.md.backup"

    # Generate a human-readable diff summary
    DIFF_OUTPUT=$(diff --unified=3 "$PROJECT_DIR/.claude/commands/ship-team.md" "$TEMPLATE_DIR/.claude/commands/ship-team.md" 2>/dev/null | head -80)
    if [ -n "$DIFF_OUTPUT" ]; then
      MIGRATION_WARNINGS="ship-team"
    fi
  fi
fi

# ─── Step 5: Sync template ───────────────────────────────────────────────────

echo -e "${BOLD}Syncing files:${RESET}"

TOTAL_UPDATED=0
TOTAL_NEW=0
TOTAL_SKIPPED=0

sync_template_dir() {
  local src_dir="$1"
  local dst_dir="$2"
  local rel_prefix="$3"

  mkdir -p "$dst_dir"

  # Enable dotglob so we sync hidden dirs like .claude/
  local _prev_dotglob=$(shopt -p dotglob 2>/dev/null)
  shopt -s dotglob

  for src_file in "$src_dir"/*; do
    [ -e "$src_file" ] || continue
    local filename=$(basename "$src_file")
    local relpath="${rel_prefix}${filename}"

    # Skip .git directories (dotglob matches them now)
    [ "$filename" = ".git" ] && continue
    [ "$filename" = ".gitignore" ] && continue
    [ "$filename" = ".github" ] && continue

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

  # Restore previous dotglob state
  eval "$_prev_dotglob"
}

sync_template_dir "$TEMPLATE_DIR" "$PROJECT_DIR" ""

# Also ensure your-skills directory has its README
if [ -d "$PROJECT_DIR/.claude/skills/your-skills" ] && [ ! -f "$PROJECT_DIR/.claude/skills/your-skills/README.md" ]; then
  if [ -f "$TEMPLATE_DIR/.claude/skills/your-skills/README.md" ]; then
    cp "$TEMPLATE_DIR/.claude/skills/your-skills/README.md" "$PROJECT_DIR/.claude/skills/your-skills/README.md"
  fi
fi

if [ $TOTAL_NEW -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Synced ($TOTAL_UPDATED updated, ${BOLD}$TOTAL_NEW new${RESET}, $TOTAL_SKIPPED protected)"
else
  echo -e "${GREEN}✓${RESET} Synced ($TOTAL_UPDATED updated, $TOTAL_SKIPPED protected)"
fi

# ─── Step 5a: Register hooks in settings.json ────────────────────────────────
# SKILL.md defines hook intent, but Claude Code only executes hooks from settings.json.

SETTINGS_FILE="$PROJECT_DIR/.claude/settings.json"
if [ -f "$SETTINGS_FILE" ]; then
  if ! grep -q '"PreToolUse"' "$SETTINGS_FILE" 2>/dev/null; then
    python3 -c "
import json
with open('$SETTINGS_FILE') as f:
    data = json.load(f)
data.setdefault('hooks', {})['PreToolUse'] = [
    {'matcher': 'Edit', 'hooks': [{'type': 'command', 'command': 'bash .claude/skills/ship/refgate/bin/check-refgate.sh'}]},
    {'matcher': 'Write', 'hooks': [{'type': 'command', 'command': 'bash .claude/skills/ship/refgate/bin/check-refgate.sh'}]}
]
with open('$SETTINGS_FILE', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
" 2>/dev/null && echo -e "${GREEN}✓${RESET} Registered hooks in settings.json (refgate)"
  fi
else
  cat > "$SETTINGS_FILE" << 'HOOKS_EOF'
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit",
        "hooks": [{"type": "command", "command": "bash .claude/skills/ship/refgate/bin/check-refgate.sh"}]
      },
      {
        "matcher": "Write",
        "hooks": [{"type": "command", "command": "bash .claude/skills/ship/refgate/bin/check-refgate.sh"}]
      }
    ]
  }
}
HOOKS_EOF
  echo -e "${GREEN}✓${RESET} Created .claude/settings.json (hooks: refgate)"
fi

# ─── Step 5b: Always clean stale v3 commands ────────────────────────────────
# Runs every update, not just during migration. Catches projects that updated
# from intermediate versions before the v3→v4 migration code existed.

STALE_V3_COMMANDS=(
  "plan.md" "build.md" "review.md" "qa.md" "ship.md"
  "fix.md" "money.md" "browse.md" "team.md" "retro.md" "update.md"
  "visionary.md" "architect.md" "critic.md" "polish.md"
  "health.md" "status.md"
)

STALE_REMOVED=0
for old_cmd in "${STALE_V3_COMMANDS[@]}"; do
  if [ -f "$PROJECT_DIR/.claude/commands/$old_cmd" ]; then
    rm "$PROJECT_DIR/.claude/commands/$old_cmd"
    STALE_REMOVED=$((STALE_REMOVED + 1))
    # Also remove the mirrored skill if it exists
    skill_name=$(basename "$old_cmd" .md)
    if [ -d "$PROJECT_DIR/.claude/skills/$skill_name" ]; then
      rm -rf "$PROJECT_DIR/.claude/skills/$skill_name"
    fi
  fi
done
if [ $STALE_REMOVED -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Removed $STALE_REMOVED stale v3 commands (non-prefixed duplicates)"
fi

# ─── Step 5b: Mirror commands as skills ──────────────────────────────────────
# Claude Code v2.1.88+ has a bug where .claude/commands/ aren't discovered.
# Skills format (.claude/skills/<name>/SKILL.md) works reliably across all versions.
# Only mirror ship-* prefixed commands — never non-framework commands.

SKILLS_SYNCED=0
for cmd_file in "$PROJECT_DIR/.claude/commands/ship-"*.md; do
  [ -e "$cmd_file" ] || continue
  cmd_name=$(basename "$cmd_file" .md)
  mkdir -p "$PROJECT_DIR/.claude/skills/$cmd_name"
  cp "$cmd_file" "$PROJECT_DIR/.claude/skills/$cmd_name/SKILL.md"
  SKILLS_SYNCED=$((SKILLS_SYNCED + 1))
done
if [ $SKILLS_SYNCED -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Mirrored $SKILLS_SYNCED commands as skills (Claude Code v2.1.88+ compatibility)"
fi

# ─── Step 5c: Migrate old-style references to skill directories ──────────────
# References moved from references/shared/, references/ios/, references/web/
# into .claude/skills/ship/*/references/ in v2026.04.11.
# sync_template_dir already copied the new files — this cleans up the old ones.

REF_MIGRATED=0

# Clean old shared/ references (now in ux/, motion/, components/, hardening/)
if [ -d "$PROJECT_DIR/references/shared" ]; then
  for f in "$PROJECT_DIR/references/shared/"*.md; do
    [ -e "$f" ] || continue
    fname=$(basename "$f")
    [ "$fname" = "README.md" ] && continue
    rm "$f"
    REF_MIGRATED=$((REF_MIGRATED + 1))
  done
  rmdir "$PROJECT_DIR/references/shared" 2>/dev/null || true
fi

# Clean old ios/ references (now in .claude/skills/ship/ios/references/)
if [ -d "$PROJECT_DIR/references/ios" ]; then
  for f in "$PROJECT_DIR/references/ios/"*.md; do
    [ -e "$f" ] || continue
    rm "$f"
    REF_MIGRATED=$((REF_MIGRATED + 1))
  done
  if [ -d "$PROJECT_DIR/references/ios/frameworks" ]; then
    for f in "$PROJECT_DIR/references/ios/frameworks/"*.md; do
      [ -e "$f" ] || continue
      rm "$f"
      REF_MIGRATED=$((REF_MIGRATED + 1))
    done
    rmdir "$PROJECT_DIR/references/ios/frameworks" 2>/dev/null || true
  fi
  rmdir "$PROJECT_DIR/references/ios" 2>/dev/null || true
fi

# Clean old web/ references (now in .claude/skills/ship/web/references/)
if [ -d "$PROJECT_DIR/references/web" ]; then
  for f in "$PROJECT_DIR/references/web/"*.md; do
    [ -e "$f" ] || continue
    rm "$f"
    REF_MIGRATED=$((REF_MIGRATED + 1))
  done
  rmdir "$PROJECT_DIR/references/web" 2>/dev/null || true
fi

# Clean empty android/ and cross-platform/ directories
rmdir "$PROJECT_DIR/references/android" 2>/dev/null || true
rmdir "$PROJECT_DIR/references/cross-platform" 2>/dev/null || true

# Add redirect README if missing
if [ ! -f "$PROJECT_DIR/references/README.md" ] && [ -f "$TEMPLATE_DIR/references/README.md" ]; then
  mkdir -p "$PROJECT_DIR/references"
  cp "$TEMPLATE_DIR/references/README.md" "$PROJECT_DIR/references/README.md"
fi

if [ $REF_MIGRATED -gt 0 ]; then
  echo -e "${GREEN}✓${RESET} Migrated references: removed $REF_MIGRATED old files (now in .claude/skills/ship/*/references/)"
fi

# ─── Step 6: Update cheatsheet ────────────────────────────────────────────────

cp "$FRAMEWORK_DIR/CHEATSHEET.md" "$PROJECT_DIR/CHEATSHEET.md"
echo -e "${GREEN}✓${RESET} Updated CHEATSHEET.md"

# ─── Step 7: Create root-level files if missing ──────────────────────────────

for root_file in DECISIONS.md CONTEXT.md TASKS.md LEARNINGS.md; do
  if [ ! -f "$PROJECT_DIR/$root_file" ] && [ -f "$TEMPLATE_DIR/$root_file" ]; then
    cp "$TEMPLATE_DIR/$root_file" "$PROJECT_DIR/$root_file"
    echo -e "${GREEN}✓${RESET} Created $root_file (new in this version)"
  fi
done

# ─── Step 8: Update version stamp in CLAUDE.md ───────────────────────────────

if grep -q "Ship Framework" "$PROJECT_DIR/CLAUDE.md"; then
  # Replace the entire footer line to avoid partial-match corruption
  sedi "s|^>.*Ship Framework.*|> Ship Framework v${VERSION} — [github.com/ismailkose/ship-framework](https://github.com/ismailkose/ship-framework)|" "$PROJECT_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Updated version stamp in CLAUDE.md"
else
  echo "" >> "$PROJECT_DIR/CLAUDE.md"
  echo "---" >> "$PROJECT_DIR/CLAUDE.md"
  echo "" >> "$PROJECT_DIR/CLAUDE.md"
  echo "> Ship Framework v${VERSION} — [github.com/ismailkose/ship-framework](https://github.com/ismailkose/ship-framework)" >> "$PROJECT_DIR/CLAUDE.md"
  echo -e "${GREEN}✓${RESET} Added version stamp to CLAUDE.md"
fi

# ─── Step 9: Update self (this script) ────────────────────────────────────────

if [ -f "$TEMPLATE_DIR/ship-update.sh" ]; then
  cp "$TEMPLATE_DIR/ship-update.sh" "$PROJECT_DIR/ship-update.sh"
  chmod +x "$PROJECT_DIR/ship-update.sh"
  echo -e "${GREEN}✓${RESET} Updated ship-update.sh"
fi

# ─── Handle --add-framework flag ──────────────────────────────────────────────

prev_arg=""
for i in "$@"; do
  if [ "$prev_arg" = "--add-framework" ]; then
    mkdir -p "$PROJECT_DIR/.claude/skills/ship/ios/references/frameworks"
    IFS=',' read -ra NEW_FW <<< "$i"
    for fw in "${NEW_FW[@]}"; do
      fw=$(echo "$fw" | xargs)
      if [ -f "$TEMPLATE_DIR/.claude/skills/ship/ios/references/frameworks/${fw}.md" ]; then
        cp "$TEMPLATE_DIR/.claude/skills/ship/ios/references/frameworks/${fw}.md" "$PROJECT_DIR/.claude/skills/ship/ios/references/frameworks/"
        echo -e "${GREEN}✓${RESET} Added framework reference: ${fw}"
      else
        echo -e "${YELLOW}⚠${RESET}  Framework reference not found: ${fw}"
        echo -e "${DIM}  Available: $(ls "$TEMPLATE_DIR/.claude/skills/ship/ios/references/frameworks/" 2>/dev/null | sed 's/\.md//g' | tr '\n' ', ' | sed 's/,$//')${RESET}"
      fi
    done
  fi
  prev_arg="$i"
done

# ─── Step 10: Show migration warnings ───────────────────────────────────────

if [ -n "$MIGRATION_WARNINGS" ]; then
  echo ""
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo -e "${BOLD}Migration Notice: Routing table changed${RESET}"
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
  echo ""
  echo -e "  ${BOLD}ship-team.md${RESET} has been updated with new routes and features."
  echo -e "  Your previous version was backed up to:"
  echo ""
  echo -e "    ${DIM}.claude/commands/ship-team.md.backup${RESET}"
  echo ""
  echo -e "  If you customized the Task Routing table, you can compare:"
  echo ""
  echo -e "    ${BOLD}diff .claude/commands/ship-team.md.backup .claude/commands/ship-team.md${RESET}"
  echo ""
  echo -e "  Then re-apply any custom routes you added."
  echo ""
  echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
fi

# ─── Summary ──────────────────────────────────────────────────────────────────

echo ""
echo -e "${BOLD}${ORANGE}Updated!${RESET} v${CURRENT_VERSION} → v${VERSION}"
echo ""
echo -e "${DIM}Your CLAUDE.md content, TASKS.md, DECISIONS.md, CONTEXT.md, and LEARNINGS.md are untouched.${RESET}"
if [ "$V3_MIGRATION" = true ]; then
  echo ""
  echo -e "${BOLD}v4 changes to know about:${RESET}"
  echo "  • Commands now use /ship- prefix: /ship-plan, /ship-build, /ship-review, etc."
  echo "  • New skills system in .claude/skills/ — add your own in your-skills/"
  echo "  • New safety commands: /ship-careful, /ship-freeze, /ship-guard"
  echo "  • Fill in The Founder section in CLAUDE.md — it shapes how the team talks to you"
  echo ""
  echo -e "${BOLD}Next step:${RESET} Open Claude Code and type:"
  echo ""
  echo -e "  ${BOLD}/ship-team continue${RESET}"
fi
echo ""
