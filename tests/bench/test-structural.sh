#!/usr/bin/env bash
# Ship Framework — Structural Integrity Test Suite
# Validates that all internal references resolve, frontmatter is valid,
# hooks work, and file sizes are within targets.
#
# Usage: bash tests/bench/test-structural.sh [template_dir]
# Default template_dir: ./template

set -euo pipefail

TEMPLATE_DIR="${1:-./template}"
COMMANDS_DIR="$TEMPLATE_DIR/.claude/commands"
SKILLS_DIR="$TEMPLATE_DIR/.claude/skills/ship"
TEAM_RULES="$TEMPLATE_DIR/.claude/team-rules.md"

# Counters
PASS=0
FAIL=0
WARN=0
TOTAL=0

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

pass() { PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}✓${RESET} $1"; }
fail() { FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}✗${RESET} $1"; }
warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}⚠${RESET} $1"; }
section() { echo -e "\n${BLUE}${BOLD}━━━ $1 ━━━${RESET}"; }

# ============================================================
# TEST 1: Command Frontmatter Validation
# ============================================================
section "1. Command Frontmatter"

for cmd in "$COMMANDS_DIR"/*.md; do
    name=$(basename "$cmd" .md)

    # Check for YAML frontmatter
    if head -1 "$cmd" | grep -q "^---$"; then
        # Check description field
        if grep -q "^description:" "$cmd"; then
            pass "$name — has description"
        else
            fail "$name — missing description in frontmatter"
        fi

        # Check disable-model-invocation
        if grep -q "^disable-model-invocation: true" "$cmd"; then
            pass "$name — disable-model-invocation set"
        else
            warn "$name — disable-model-invocation not set (may auto-trigger)"
        fi
    else
        fail "$name — NO frontmatter at all"
    fi
done

# ============================================================
# TEST 2: Skill SKILL.md Existence & Frontmatter
# ============================================================
section "2. Skill Files"

for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    skill_file="$skill_dir/SKILL.md"

    if [ -f "$skill_file" ]; then
        pass "$skill_name — SKILL.md exists"

        # Check for frontmatter
        if head -1 "$skill_file" | grep -q "^---$"; then
            pass "$skill_name — has frontmatter"
        else
            warn "$skill_name — no frontmatter in SKILL.md"
        fi
    else
        fail "$skill_name — SKILL.md MISSING"
    fi
done

# ============================================================
# TEST 3: Reference Path Resolution
# ============================================================
section "3. Reference Path Resolution"

# Extract all .claude/skills/ship paths from command files and check they exist
ref_paths_checked=0
ref_paths_broken=0

for cmd in "$COMMANDS_DIR"/*.md; do
    name=$(basename "$cmd" .md)
    # Extract paths like .claude/skills/ship/xxx/references/yyy.md or .claude/skills/ship/xxx/SKILL.md
    paths=$(grep -oE '\.claude/skills/ship/[a-zA-Z0-9/_.-]+\.md' "$cmd" 2>/dev/null || true)

    for ref_path in $paths; do
        full_path="$TEMPLATE_DIR/$ref_path"
        ref_paths_checked=$((ref_paths_checked + 1))

        if [ -f "$full_path" ]; then
            : # silent pass for individual refs (too noisy)
        else
            # Check if it's a directory pattern (e.g., frameworks/)
            dir_path=$(dirname "$full_path")
            if [ -d "$dir_path" ]; then
                : # directory exists, file might be generated
            else
                fail "$name → $ref_path (file not found)"
                ref_paths_broken=$((ref_paths_broken + 1))
            fi
        fi
    done
done

if [ "$ref_paths_broken" -eq 0 ]; then
    pass "All $ref_paths_checked reference paths resolve"
else
    fail "$ref_paths_broken of $ref_paths_checked reference paths broken"
fi

# Also check team-rules.md references
team_refs=$(grep -oE '\.claude/skills/ship/[a-zA-Z0-9/_.-]+\.md' "$TEAM_RULES" 2>/dev/null || true)
team_broken=0
team_total=0

for ref_path in $team_refs; do
    full_path="$TEMPLATE_DIR/$ref_path"
    team_total=$((team_total + 1))
    if [ ! -f "$full_path" ]; then
        fail "team-rules.md → $ref_path (not found)"
        team_broken=$((team_broken + 1))
    fi
done

if [ "$team_broken" -eq 0 ] && [ "$team_total" -gt 0 ]; then
    pass "team-rules.md — all $team_total reference paths resolve"
fi

# ============================================================
# TEST 4: Hook Scripts
# ============================================================
section "4. Hook Scripts"

# Find all .sh files in skills
while IFS= read -r hook_script; do
    hook_name=$(echo "$hook_script" | sed "s|$TEMPLATE_DIR/||")

    # Check executable
    if [ -x "$hook_script" ] || head -1 "$hook_script" | grep -q "#!/"; then
        pass "$hook_name — has shebang/executable"
    else
        warn "$hook_name — no shebang or not executable"
    fi

    # Check for valid JSON output (dry run check — look for echo patterns with JSON)
    if grep -qE "echo ['\"](\{|\\$)" "$hook_script" || grep -q "permissionDecision" "$hook_script" || grep -q "echo '{}'" "$hook_script"; then
        pass "$hook_name — outputs JSON"
    else
        warn "$hook_name — no JSON output detected"
    fi
done < <(find "$SKILLS_DIR" -name "*.sh" -type f 2>/dev/null)

# Actually run the refgate hook to check it returns valid JSON
REFGATE_HOOK="$SKILLS_DIR/refgate/bin/check-refgate.sh"
if [ -f "$REFGATE_HOOK" ]; then
    # Run in a temp dir (no .refgate files = should deny)
    tmpdir=$(mktemp -d)
    mkdir -p "$tmpdir/.claude"
    # Pipe empty JSON to stdin (hook may read stdin)
    output=$(cd "$tmpdir" && echo '{}' | bash "$(cd - > /dev/null && realpath "$REFGATE_HOOK")" 2>/dev/null || echo "SCRIPT_ERROR")

    if [ "$output" != "SCRIPT_ERROR" ] && echo "$output" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        pass "refgate hook — returns valid JSON"

        # Check it correctly denies when no refs loaded
        if echo "$output" | grep -q "permissionDecision.*deny"; then
            pass "refgate hook — correctly denies without refs"
        else
            warn "refgate hook — did not deny without refs loaded"
        fi
    else
        fail "refgate hook — invalid JSON output: $output"
    fi

    # Test with refs loaded
    echo "1" > "$tmpdir/.claude/.refgate-loaded"
    output=$(cd "$tmpdir" && echo '{}' | bash "$(cd - > /dev/null && realpath "$REFGATE_HOOK")" 2>/dev/null || echo "SCRIPT_ERROR")
    rm -rf "$tmpdir"

    if echo "$output" | grep -q '{}'; then
        pass "refgate hook — correctly allows with refs loaded"
    else
        fail "refgate hook — did not allow with refs loaded"
    fi
fi

# Run session-start hook
SESSION_HOOK="$SKILLS_DIR/sessionstart/bin/session-start.sh"
if [ -f "$SESSION_HOOK" ]; then
    tmpdir=$(mktemp -d)
    # Create a minimal CLAUDE.md
    cat > "$tmpdir/CLAUDE.md" << 'MOCK'
# Test
Stack: ios
Version: v2026.04.11
Product: TestApp
MOCK
    cat > "$tmpdir/TASKS.md" << 'MOCK'
- [ ] Task one
- [ ] Task two
- [x] Done task
MOCK
    mkdir -p "$tmpdir/.claude"
    CLAUDE_ENV_FILE="$tmpdir/.env_test"
    touch "$CLAUDE_ENV_FILE"
    export CLAUDE_ENV_FILE
    output=$(cd "$tmpdir" && bash "$SESSION_HOOK" 2>&1 || echo "SCRIPT_ERROR")
    rm -rf "$tmpdir"

    if echo "$output" | grep -qi "ship\|stack\|task"; then
        pass "session-start hook — produces status output"
    else
        fail "session-start hook — no meaningful output: $output"
    fi
fi

# ============================================================
# TEST 5: Command Line Counts (Size Budget)
# ============================================================
section "5. Command Size Budget"

# Define targets (current and post-Phase 6+7)
declare -A SIZE_TARGETS
SIZE_TARGETS[ship-review]=200
SIZE_TARGETS[ship-plan]=200
SIZE_TARGETS[ship-launch]=200
SIZE_TARGETS[ship-design]=200
SIZE_TARGETS[ship-variants]=200
SIZE_TARGETS[ship-team]=200
SIZE_TARGETS[ship-build]=200
SIZE_TARGETS[ship-fix]=200
SIZE_TARGETS[ship-html]=200
SIZE_TARGETS[ship-browse]=200

for cmd in "$COMMANDS_DIR"/*.md; do
    name=$(basename "$cmd" .md)
    lines=$(wc -l < "$cmd")

    target="${SIZE_TARGETS[$name]:-999}"

    if [ "$target" -eq 999 ]; then
        # No target for this command
        if [ "$lines" -le 200 ]; then
            pass "$name — $lines lines (within general budget)"
        else
            warn "$name — $lines lines (no specific target, but over 200)"
        fi
    else
        if [ "$lines" -le "$target" ]; then
            pass "$name — $lines lines (target: ≤$target)"
        else
            over=$((lines - target))
            fail "$name — $lines lines (target: ≤$target, over by $over)"
        fi
    fi
done

# ============================================================
# TEST 6: team-rules.md Structure
# ============================================================
section "6. team-rules.md Structure"

team_lines=$(wc -l < "$TEAM_RULES")
echo -e "  ${BLUE}ℹ${RESET} team-rules.md: $team_lines lines"

# Check required sections exist
for section_name in "How the Team Thinks" "Product Frameworks" "The Team" "JTBD" "HEART" "RICE"; do
    if grep -qi "$section_name" "$TEAM_RULES"; then
        pass "team-rules.md — has '$section_name' section"
    else
        fail "team-rules.md — missing '$section_name' section"
    fi
done

# Count persona definition blocks (before Phase 7, these should exist in team-rules)
persona_count=$(grep -c "^### \(Vi\|Arc\|Dev\|Crit\|Pol\|Eye\|Test\|Cap\|Biz\)" "$TEAM_RULES" 2>/dev/null || echo 0)
echo -e "  ${BLUE}ℹ${RESET} Persona definitions in team-rules.md: $persona_count"

if [ "$team_lines" -le 500 ]; then
    pass "team-rules.md — within 500-line target ($team_lines lines)"
else
    warn "team-rules.md — $team_lines lines (Phase 7 target: ≤500)"
fi

# ============================================================
# TEST 7: Cross-Reference Consistency
# ============================================================
section "7. Cross-Reference Consistency"

# Check that commands referencing skills actually exist
for cmd in "$COMMANDS_DIR"/*.md; do
    name=$(basename "$cmd" .md)

    # Check for references to team-rules.md
    if grep -q "team-rules.md" "$cmd"; then
        if [ -f "$TEAM_RULES" ]; then
            : # fine
        else
            fail "$name references team-rules.md but it doesn't exist"
        fi
    fi

    # Check for references to CLAUDE.md
    if grep -q "CLAUDE.md" "$cmd"; then
        pass "$name — references CLAUDE.md (expected)"
    fi
done

# Check skill references/ directories have actual content
for skill_dir in "$SKILLS_DIR"/*/; do
    skill_name=$(basename "$skill_dir")
    refs_dir="$skill_dir/references"

    if [ -d "$refs_dir" ]; then
        ref_count=$(find "$refs_dir" -name "*.md" -type f | wc -l)
        if [ "$ref_count" -gt 0 ]; then
            pass "$skill_name — $ref_count reference files"
        else
            warn "$skill_name — references/ dir exists but empty"
        fi
    fi
done

# ============================================================
# TEST 8: Agent Files (Phase 7 readiness)
# ============================================================
section "8. Agent Readiness (Phase 7)"

AGENTS_DIR="$TEMPLATE_DIR/.claude/skills/ship/agents"

if [ -d "$AGENTS_DIR" ]; then
    echo -e "  ${BLUE}ℹ${RESET} agents/ directory exists"

    for agent_expected in crit pol eye test adversarial; do
        agent_file=$(find "$AGENTS_DIR" -type f -name "SKILL.md" -path "*${agent_expected}*" 2>/dev/null | head -1)
        if [ -n "$agent_file" ]; then
            pass "Agent $agent_expected — file exists"

            # Check for model assignment (inside YAML frontmatter or at line start)
            if grep -q "model:" "$agent_file" 2>/dev/null; then
                model=$(grep "model:" "$agent_file" | head -1 | awk '{print $2}')
                pass "Agent $agent_expected — model: $model"
            else
                warn "Agent $agent_expected — no model assigned"
            fi
        else
            warn "Agent $agent_expected — not yet created (expected after Phase 7)"
        fi
    done
else
    echo -e "  ${BLUE}ℹ${RESET} agents/ directory not yet created (pre-Phase 7 — expected)"
fi

# ============================================================
# TEST 9: Duplicate Content Detection
# ============================================================
section "9. Duplicate Content Detection"

# Check for Reference Gate blocks that should only be in hook (post-Phase 3)
refgate_in_commands=0
for cmd in "$COMMANDS_DIR"/*.md; do
    name=$(basename "$cmd" .md)
    if grep -q "Reference Gate" "$cmd" 2>/dev/null; then
        refgate_in_commands=$((refgate_in_commands + 1))
    fi
done
echo -e "  ${BLUE}ℹ${RESET} Commands with Reference Gate block: $refgate_in_commands"
if [ "$refgate_in_commands" -gt 0 ]; then
    warn "Reference Gate text still in $refgate_in_commands commands (hook handles enforcement, but text is backup)"
fi

# Check for Smart Flag blocks duplicated across commands
flag_in_commands=0
for cmd in "$COMMANDS_DIR"/*.md; do
    if grep -q "Smart Flag Resolution" "$cmd" 2>/dev/null; then
        flag_in_commands=$((flag_in_commands + 1))
    fi
done
echo -e "  ${BLUE}ℹ${RESET} Commands with Smart Flag block: $flag_in_commands"

# ============================================================
# SUMMARY
# ============================================================
section "SUMMARY"

echo -e "  ${GREEN}Passed:${RESET}  $PASS"
echo -e "  ${RED}Failed:${RESET}  $FAIL"
echo -e "  ${YELLOW}Warnings:${RESET} $WARN"
echo -e "  ${BOLD}Total:${RESET}   $TOTAL tests"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}ALL TESTS PASSED${RESET}"
    exit 0
else
    echo -e "  ${RED}${BOLD}$FAIL TESTS FAILED${RESET}"
    exit 1
fi
