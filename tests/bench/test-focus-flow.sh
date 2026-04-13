#!/usr/bin/env bash
# Ship Framework — Focus Flow Comparison Test
# Compares before-slimming vs after-slimming command files to verify
# output-shaping instructions are preserved.
#
# This test doesn't run actual AI — it checks that the command files
# contain the quality markers that SHAPE AI output. If a marker is in
# the before version but missing from the after version, that's a
# quality regression.
#
# Usage: bash tests/bench/test-focus-flow.sh [template_dir]
# Default template_dir: ./template

set -euo pipefail

TEMPLATE_DIR="${1:-./template}"
COMMANDS_DIR="$TEMPLATE_DIR/.claude/commands"
AGENTS_DIR="$TEMPLATE_DIR/.claude/skills/ship/agents"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

PASS=0
FAIL=0
WARN=0
TOTAL=0

pass() { PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}✓${RESET} $1"; }
fail() { FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}✗${RESET} $1"; }
warn() { WARN=$((WARN + 1)); echo -e "  ${YELLOW}⚠${RESET} $1"; }
section() { echo -e "\n${BLUE}${BOLD}━━━ $1 ━━━${RESET}"; }
subsection() { echo -e "\n  ${CYAN}${BOLD}▸ $1${RESET}"; }

# Check if pattern exists in file (case-insensitive)
has() { grep -qi "$2" "$1" 2>/dev/null; }

# Check if pattern exists in any of several files (for relocated content)
has_any() {
    local pattern="$1"
    shift
    for file in "$@"; do
        if [ -f "$file" ] && grep -qi "$pattern" "$file" 2>/dev/null; then
            return 0
        fi
    done
    return 1
}

echo -e "${BOLD}Focus Flow Quality Comparison Test${RESET}"
echo -e "Verifying output-shaping instructions are preserved after slimming."
echo -e "Template: $COMMANDS_DIR"
echo ""

# ============================================================
# TEST 1: /ship-plan — Output-Shaping Markers
# ============================================================
section "1. /ship-plan — Output Quality Markers"
PLAN="$COMMANDS_DIR/ship-plan.md"

subsection "Vi's Product Brief"
# These are the specific output templates that shape AI behavior

# Aesthetic Direction — must have Safe/Bold template
if has "$PLAN" "safe choice" && has "$PLAN" "bold choice"; then
    if has "$PLAN" "font:.*color" || (has "$PLAN" "Font:" && has "$PLAN" "Colors:"); then
        pass "Aesthetic Direction: Safe/Bold format with font + color specs"
    else
        fail "Aesthetic Direction: Has Safe/Bold but missing font/color template"
    fi
else
    fail "Aesthetic Direction: Missing Safe/Bold two-option structure"
fi

# Experience Walk-Through — must have the output format
if has "$PLAN" "you open the app" || has "$PLAN" "first thing you see"; then
    pass "Experience Walk-Through: Has second-person narrative format"
else
    if has "$PLAN" "walk.through" && has "$PLAN" "first launch.*magic.*return"; then
        warn "Experience Walk-Through: Has requirements but missing narrative template"
    else
        fail "Experience Walk-Through: Missing output format"
    fi
fi

# Forcing Questions — must have all 4
if has "$PLAN" "Q1.*who" || has "$PLAN" "who.*needs\|who has this problem"; then
    pass "Forcing Question Q1 (Who) present"
else
    fail "Forcing Question Q1 (Who) missing"
fi

if has "$PLAN" "Q2.*status quo\|what do people do today"; then
    pass "Forcing Question Q2 (Status Quo) present"
else
    fail "Forcing Question Q2 (Status Quo) missing"
fi

if has "$PLAN" "Q3.*walk.*through\|show me exactly"; then
    pass "Forcing Question Q3 (Walk Through) present"
else
    fail "Forcing Question Q3 (Walk Through) missing"
fi

if has "$PLAN" "Q4.*smallest.*complete\|smallest version"; then
    pass "Forcing Question Q4 (Smallest Complete) present"
else
    fail "Forcing Question Q4 (Smallest Complete) missing"
fi

# Three Ways — must generate 3 options
if has "$PLAN" "experience [abc]\|three ways\|3.*ways\|simplest.*delightful.*different"; then
    pass "Three Ways This Could Work present"
else
    fail "Three Ways This Could Work missing"
fi

# Product Brief items
for item_pattern in "bar test" "JTBD\|job statement\|when I.*want to" "magic moment" "kill list" "2.week bet\|two.week" "success metric\|HEART" "who pays" "PMF\|product.market fit" "growth mechanism\|viral.*content.*product.led"; do
    item_name=$(echo "$item_pattern" | sed 's/\\|/ or /g' | head -c 30)
    if has "$PLAN" "$item_pattern"; then
        pass "Brief: $item_name"
    else
        fail "Brief: $item_name missing"
    fi
done

# Pushback Posture — must have gated escape hatch
if has "$PLAN" "pushback\|challenge.*assumption"; then
    if has "$PLAN" "two.*question\|TWO.*question\|2.*pointed\|just build it"; then
        pass "Pushback Posture: Gated escape hatch present"
    else
        warn "Pushback Posture: Basic presence but missing escape hatch detail"
    fi
else
    fail "Pushback Posture: Missing entirely"
fi

subsection "Arc's Technical Plan"

# Build Order with RICE
if has "$PLAN" "RICE" && has "$PLAN" "build order"; then
    pass "Build Order with RICE scoring"
else
    fail "Build Order with RICE scoring missing"
fi

# Dual-Approach
if has "$PLAN" "approach a\|approach b\|minimal.*clean\|dual.approach"; then
    pass "Dual-Approach Planning present"
else
    fail "Dual-Approach Planning missing"
fi

# Dependency Analysis
if has "$PLAN" "dependency\|depends on\|can start after\|parallel.safe\|sequential"; then
    pass "Dependency Analysis present"
else
    fail "Dependency Analysis missing"
fi

# Security Check — platform-specific
if has "$PLAN" "keychain\|userdefaults" || has "$PLAN" "httponly\|httpOnly\|localStorage"; then
    pass "Security Check: Platform-specific items present"
else
    if has "$PLAN" "security check"; then
        warn "Security Check: Header present but no platform-specific items"
    else
        fail "Security Check: Missing entirely"
    fi
fi

# State Diagrams
if has "$PLAN" "state diagram\|state machine\|\[idle\].*\[loading\]"; then
    pass "State Diagrams for complex features"
else
    warn "State Diagrams not mentioned (may be in team-rules)"
fi

subsection "Pol & Adversarial (Agent Delegation)"

POL_SKILL="$AGENTS_DIR/pol/SKILL.md"
ADV_SKILL="$AGENTS_DIR/adversarial/SKILL.md"

# Pol Design Readiness — 7 dimensions
if has "$PLAN" "design readiness\|7 dimension\|all.*≥.*5\|average.*≥.*7"; then
    if has_any "information architecture" "$PLAN" "$POL_SKILL"; then
        pass "Pol: Design Readiness with 7 dimensions (in command or agent)"
    else
        warn "Pol: Mentioned but dimensions not listed anywhere"
    fi
else
    fail "Pol: Design Readiness Score missing from plan flow"
fi

# Adversarial — must reference agent and require APPROVED
if has "$PLAN" "adversarial" && has "$PLAN" "APPROVED"; then
    if has_any "attack vector\|missing states\|race condition\|edge case\|contradiction\|scope creep\|security\|design slop" "$PLAN" "$ADV_SKILL"; then
        pass "Adversarial: Attack vectors defined (in command or agent)"
    else
        warn "Adversarial: Referenced but no attack vectors found anywhere"
    fi
else
    fail "Adversarial: Missing from plan graduation flow"
fi

# ============================================================
# TEST 2: /ship-review — Output Quality Markers
# ============================================================
section "2. /ship-review — Output Quality Markers"
REVIEW="$COMMANDS_DIR/ship-review.md"
CRIT_SKILL="$AGENTS_DIR/crit/SKILL.md"
EYE_SKILL="$AGENTS_DIR/eye/SKILL.md"
TEST_SKILL="$AGENTS_DIR/test/SKILL.md"

subsection "Scope Drift Detection"
if has "$REVIEW" "scope drift\|scope creep"; then
    if has "$REVIEW" "plan.*discovery\|extract.*actionable\|cross.reference.*diff\|compare.*changed.*files"; then
        pass "Scope Drift: Multi-step algorithm present"
    else
        warn "Scope Drift: Mentioned but algorithm steps missing"
    fi
else
    fail "Scope Drift Detection missing entirely"
fi

subsection "Flag Detection"
if has "$REVIEW" "smart flag\|auto.detect"; then
    if has "$REVIEW" "file types\|diff size\|<.*20.*lines\|20.*200\|200+\|release.*proximity\|branch.*name"; then
        pass "Flag Detection: Concrete detection criteria present"
    else
        warn "Flag Detection: Header present but criteria missing"
    fi
else
    fail "Flag Detection missing"
fi

subsection "Review Agents (via SKILL.md)"

# Crit — HEART dimensions
if has_any "task success" "$REVIEW" "$CRIT_SKILL" && has_any "adoption" "$REVIEW" "$CRIT_SKILL"; then
    pass "Crit: HEART dimensions present"
else
    fail "Crit: HEART dimensions missing from both command and agent"
fi

# Pol — Anti-Slop Check
if has_any "anti.slop" "$REVIEW" "$POL_SKILL"; then
    if has_any "typography.*same font\|no weight variation\|default.*platform.*color\|same.*border.radius\|find.*replace.*logo" "$REVIEW" "$POL_SKILL"; then
        pass "Pol: Anti-Slop Check with specific patterns"
    else
        warn "Pol: Anti-Slop mentioned but specific patterns missing"
    fi
else
    fail "Pol: Anti-Slop Check missing from both command and agent"
fi

# Eye — Visual QA phases
if has_any "design system discovery\|phase 0.*design" "$REVIEW" "$EYE_SKILL"; then
    pass "Eye: Design System Discovery phase"
else
    warn "Eye: Design System Discovery not found"
fi

if has_any "screen map walkthrough\|phase 1.*screen" "$REVIEW" "$EYE_SKILL"; then
    pass "Eye: Screen Map Walkthrough phase"
else
    warn "Eye: Screen Map Walkthrough not found"
fi

if has_any "cross.reference.*crit.*pol\|challenge.*other.*reviewer\|crit.*said\|pol.*approved" "$REVIEW" "$EYE_SKILL"; then
    pass "Eye: Cross-reference with Crit + Pol"
else
    fail "Eye: Cross-reference behavior missing"
fi

# Test — Health Score
if has_any "health score" "$REVIEW" "$TEST_SKILL"; then
    if has_any "start at 100\|critical.*-25\|high.*-15\|medium.*-8\|90.100.*ship\|70.89.*fix\|below 50.*don.t ship" "$REVIEW" "$TEST_SKILL"; then
        pass "Test: Health Score calculation formula present"
    else
        warn "Test: Health Score mentioned but formula missing"
    fi
else
    fail "Test: Health Score missing from both command and agent"
fi

# Test — Explore Like a User
if has_any "explore like a user\|visit each.*page\|click every\|submit.*empty\|long text\|special char" "$REVIEW" "$TEST_SKILL"; then
    pass "Test: User exploration checklist present"
else
    fail "Test: User exploration checklist missing"
fi

# Adversarial — challenge BY NAME
if has_any "challenge.*by name\|crit.*did\|pol.*did\|eye.*did\|who.*right" "$REVIEW" "$ADV_SKILL"; then
    pass "Adversarial: Challenge-by-name behavior present"
else
    fail "Adversarial: Challenge-by-name missing from both command and agent"
fi

subsection "Post-Review Quality Controls"

# Confidence Scoring
if has "$REVIEW" "confidence.*scor\|90.*100.*certain\|70.*89.*likely\|50.*69.*possible"; then
    pass "Confidence Scoring system present"
else
    fail "Confidence Scoring missing"
fi

# Risk Classification
if has "$REVIEW" "risk classif\|SAFE.*no logic\|RISKY.*logic\|after 10.*risky.*stop"; then
    pass "Risk Classification (SAFE/RISKY) present"
else
    fail "Risk Classification missing"
fi

# Fix-First
if has "$REVIEW" "fix.first\|just fix it\|ask.*first"; then
    pass "Fix-First Review protocol present"
else
    fail "Fix-First Review protocol missing"
fi

# Close-Your-Eyes
if has "$REVIEW" "close.your.eyes\|would you keep\|would you show.*friend"; then
    pass "Close-Your-Eyes Test present"
else
    fail "Close-Your-Eyes Test missing"
fi

# TODO/FIXME scanning
if has "$REVIEW" "todo.*fixme\|TODO.*FIXME\|HACK.*TEMP"; then
    if has "$REVIEW" "placeholder.*fix\|move.*TASKS\|pre.existing.*ignore"; then
        pass "TODO/FIXME scan with triage logic"
    else
        warn "TODO/FIXME scan mentioned but triage logic missing"
    fi
else
    fail "TODO/FIXME scanning missing"
fi

# ============================================================
# TEST 3: /ship-team — Orchestration Quality
# ============================================================
section "3. /ship-team — Orchestration Quality"
TEAM="$COMMANDS_DIR/ship-team.md"

# Task routing — should auto-detect intent
if has "$TEAM" "task routing\|never ask.*which agent\|read.*request.*decide"; then
    if has "$TEAM" "continue.*TASKS\|new idea.*ship.think\|build this.*ship.plan\|fix this.*ship.fix"; then
        pass "Task Routing: Intent-to-command mapping present"
    else
        warn "Task Routing: Header present but mapping missing"
    fi
else
    fail "Task Routing missing"
fi

# Parallel dispatch
if has "$TEAM" "parallel dispatch\|parallel.*independent.*tasks"; then
    if has "$TEAM" "when to use parallel\|when not to use"; then
        pass "Parallel Dispatch: When-to-use/when-not-to guidance"
    else
        warn "Parallel Dispatch: Mentioned but criteria missing"
    fi
else
    fail "Parallel Dispatch missing"
fi

# Scope Guard
if has "$TEAM" "scope guard\|appetite check\|scope creep prevention"; then
    pass "Scope Guard present"
else
    fail "Scope Guard missing"
fi

# Plan Expansion
if has "$TEAM" "plan expansion\|bite.sized\|expand.*complex"; then
    pass "Plan Expansion for complex items"
else
    fail "Plan Expansion missing"
fi

# Decision logging
if has "$TEAM" "decision.*log\|DECISIONS.md.*date.*what.*why\|one.way door\|two.way door"; then
    pass "Decision Logging protocol present"
else
    fail "Decision Logging protocol missing"
fi

# ============================================================
# TEST 4: /ship-fix — Debugging Quality
# ============================================================
section "4. /ship-fix — Debugging Quality"
FIX="$COMMANDS_DIR/ship-fix.md"

# Iron Law
if has "$FIX" "iron law\|no fixes without root cause"; then
    pass "Iron Law (no fixes without root cause)"
else
    fail "Iron Law missing"
fi

# Known Pattern Check
if has "$FIX" "known pattern\|LEARNINGS.md.*check\|match.*known"; then
    pass "Known Pattern Check (LEARNINGS.md)"
else
    fail "Known Pattern Check missing"
fi

# 3-Strike Rule
if has "$FIX" "3.strike\|three.*strike\|after 3.*rejection\|PATH A.*PATH B"; then
    pass "3-Strike Rule with escalation paths"
else
    fail "3-Strike Rule missing"
fi

# Blast Radius
if has "$FIX" "blast radius\|how many files.*touch\|6+.*stop\|one fix per commit"; then
    pass "Blast Radius Check present"
else
    fail "Blast Radius Check missing"
fi

# Debug Report format
if has "$FIX" "debug report\|root cause.*fix.*evidence\|pattern.*lesson"; then
    pass "Debug Report output format present"
else
    fail "Debug Report format missing"
fi

# ============================================================
# TEST 5: /ship-launch — Ship Quality
# ============================================================
section "5. /ship-launch — Ship Quality"
LAUNCH="$COMMANDS_DIR/ship-launch.md"

# Plan Completion Audit
if has "$LAUNCH" "plan completion audit\|compare.*ship.plan.*built"; then
    if has "$LAUNCH" "COMPLETE.*PARTIAL.*MISSING\|was it built.*was it tested"; then
        pass "Plan Completion Audit with COMPLETE/PARTIAL/MISSING"
    else
        warn "Plan Completion Audit mentioned but criteria missing"
    fi
else
    fail "Plan Completion Audit missing"
fi

# Test Classification
if has "$LAUNCH" "IN.BRANCH\|PRE.EXISTING"; then
    pass "Test failure classification (IN-BRANCH vs PRE-EXISTING)"
else
    fail "Test failure classification missing"
fi

# Coverage thresholds
if has "$LAUNCH" "60%.*hard stop\|80%.*pass\|coverage.*check"; then
    pass "Coverage thresholds defined"
else
    warn "Coverage thresholds not found"
fi

# Measurement Plan
if has "$LAUNCH" "measurement plan\|when to check\|success looks like\|if it fails"; then
    pass "Measurement Plan present"
else
    fail "Measurement Plan missing"
fi

# ============================================================
# TEST 6: Cross-Command Flow Integrity
# ============================================================
section "6. Cross-Command Flow Integrity"

# /ship-think → /ship-plan handoff
THINK="$COMMANDS_DIR/ship-think.md"
if has "$PLAN" "ship.think\|idea brief" && has "$THINK" "ship.plan\|validated.*proceed"; then
    pass "Think → Plan handoff defined in both directions"
else
    warn "Think → Plan handoff may be incomplete"
fi

# /ship-plan → /ship-build handoff
BUILD="$COMMANDS_DIR/ship-build.md"
if has "$BUILD" "arc.*plan\|build order\|ship.plan"; then
    pass "Plan → Build handoff (Dev follows Arc's build order)"
else
    fail "Plan → Build handoff missing"
fi

# /ship-build → /ship-review handoff
if has "$BUILD" "ship.review\|review.*stale"; then
    pass "Build → Review handoff (review staleness tracking)"
else
    warn "Build → Review handoff may be incomplete"
fi

# /ship-review → /ship-launch handoff
if has "$REVIEW" "ship.launch\|ready for.*launch"; then
    pass "Review → Launch handoff defined"
else
    warn "Review → Launch handoff not explicit"
fi

# TASKS.md is the shared state
tasks_users=0
for cmd in "$COMMANDS_DIR"/*.md; do
    if has "$cmd" "TASKS.md"; then
        tasks_users=$((tasks_users + 1))
    fi
done
if [ "$tasks_users" -ge 5 ]; then
    pass "TASKS.md referenced in $tasks_users commands (shared state)"
else
    warn "TASKS.md only in $tasks_users commands (expected 5+)"
fi

# DECISIONS.md logging
decisions_users=0
for cmd in "$COMMANDS_DIR"/*.md; do
    if has "$cmd" "DECISIONS.md"; then
        decisions_users=$((decisions_users + 1))
    fi
done
if [ "$decisions_users" -ge 4 ]; then
    pass "DECISIONS.md referenced in $decisions_users commands"
else
    warn "DECISIONS.md only in $decisions_users commands"
fi

# LEARNINGS.md pattern accumulation
learnings_users=0
for cmd in "$COMMANDS_DIR"/*.md; do
    if has "$cmd" "LEARNINGS.md"; then
        learnings_users=$((learnings_users + 1))
    fi
done
if [ "$learnings_users" -ge 3 ]; then
    pass "LEARNINGS.md referenced in $learnings_users commands"
else
    warn "LEARNINGS.md only in $learnings_users commands"
fi

# ============================================================
# SUMMARY
# ============================================================
section "SUMMARY"

echo -e "  ${GREEN}Passed:${RESET}   $PASS"
echo -e "  ${RED}Failed:${RESET}   $FAIL"
echo -e "  ${YELLOW}Warnings:${RESET} $WARN"
echo -e "  ${BOLD}Total:${RESET}    $TOTAL checks"
echo ""

SCORE_PCT=$((PASS * 100 / TOTAL))
echo -e "  ${BOLD}Focus Flow Score: ${SCORE_PCT}%${RESET} ($PASS / $TOTAL)"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo -e "  ${GREEN}${BOLD}ALL QUALITY MARKERS PRESERVED${RESET}"
    echo -e "  No output-shaping regressions detected."
    exit 0
elif [ "$FAIL" -le 3 ]; then
    echo -e "  ${YELLOW}${BOLD}MINOR QUALITY GAPS ($FAIL)${RESET}"
    echo -e "  Review warnings — these may affect output consistency."
    exit 0
else
    echo -e "  ${RED}${BOLD}QUALITY REGRESSION DETECTED ($FAIL failures)${RESET}"
    echo -e "  Output-shaping instructions were lost during slimming."
    exit 1
fi
