#!/usr/bin/env bash
# Ship Framework — Quality Output Scanner
# Scans saved command output against scenario rubrics.
#
# Usage:
#   1. Run a Ship command, copy the full output to a file
#   2. bash tests/bench/test-quality.sh <scenario> <output-file>
#
# Examples:
#   bash tests/bench/test-quality.sh plan outputs/baseline-plan.txt
#   bash tests/bench/test-quality.sh review outputs/baseline-review.txt

set -euo pipefail

SCENARIO="${1:-}"
OUTPUT_FILE="${2:-}"

if [ -z "$SCENARIO" ] || [ -z "$OUTPUT_FILE" ]; then
    echo "Usage: bash tests/bench/test-quality.sh <plan|review> <output-file>"
    exit 1
fi

if [ ! -f "$OUTPUT_FILE" ]; then
    echo "Error: Output file not found: $OUTPUT_FILE"
    exit 1
fi

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

PASS=0
FAIL=0
TOTAL=0

pass() { PASS=$((PASS + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${GREEN}✓${RESET} $1"; }
fail() { FAIL=$((FAIL + 1)); TOTAL=$((TOTAL + 1)); echo -e "  ${RED}✗${RESET} $1"; }
section() { echo -e "\n${BLUE}${BOLD}━━━ $1 ━━━${RESET}"; }
check() {
    local label="$1"
    shift
    # All remaining args are patterns (OR logic — any match = pass)
    for pattern in "$@"; do
        if grep -qi "$pattern" "$OUTPUT_FILE" 2>/dev/null; then
            pass "$label"
            return
        fi
    done
    fail "$label"
}

# ============================================================
# PLAN SCENARIO
# ============================================================
if [ "$SCENARIO" = "plan" ]; then
    echo -e "${BOLD}Quality Scan: /ship-plan output${RESET}"
    echo -e "File: $OUTPUT_FILE"
    echo -e "Lines: $(wc -l < "$OUTPUT_FILE")"

    section "Section Presence"
    check "REFERENCES LOADED receipt" "REFERENCES LOADED" "references loaded"
    check "Forcing Questions (Q1-Q4)" "who needs this" "who has this problem" "Q1" "forcing question"
    check "Three Ways / Experiences A/B/C" "experience a" "three ways" "approach a"
    check "Bar Test" "bar test" "one sentence explanation"
    check "JTBD / Job Statement" "when I.*want to.*so I can" "JTBD" "job statement" "job to be done"
    check "Magic Moment" "magic moment"
    check "Kill List" "kill list" "NOT build" "won't build"
    check "Build Order" "build order" "RICE"
    check "Screen Map" "screen map"
    check "Dual Approach (Minimal vs Clean)" "approach a.*approach b\|minimal.*clean\|fastest to ship.*best architecture" "APPROACH A" "APPROACH B"
    check "Dependency Analysis" "depends on\|dependency\|can start after"
    check "Security Check (iOS)" "keychain\|userdefaults\|ATS\|data protection"
    check "Pol Design Readiness Score" "design readiness\|DESIGN READINESS\|/10\]" "information architecture.*10\|interaction state.*10"
    check "Adversarial Challenge" "adversarial\|attack vector\|challenge"
    check "Adversarial Verdict" "APPROVED\|NEEDS.REVISION\|verdict"
    check "Aesthetic Direction" "aesthetic direction\|font:.*color\|safe choice\|bold choice"

    section "Content Quality Signals"
    check "Vi pushes back / challenges" "but\|however\|challenge\|pushback\|actually\|disagree\|are you sure" "really need"
    check "iOS/SwiftUI-specific content" "swiftui\|swiftdata\|@observable\|@state\|@model"
    check "Amber accent referenced" "amber\|F59E0B\|#f59e0b\|warm"
    check "Dark-first referenced" "dark.first\|dark mode\|dark.theme"
    check "LEARNINGS.md referenced" "learnings\|timer invalidat"
    check "DECISIONS.md referenced" "decisions\|aesthetic"

    section "Anti-Pattern Check"
    # These are INVERTED — finding them is bad
    if grep -qi "great idea\|love this\|wonderful\|excellent idea\|that's a great" "$OUTPUT_FILE" 2>/dev/null; then
        fail "ANTI-PATTERN: Sycophantic opening detected"
    else
        pass "No sycophantic opening"
    fi

    if grep -qi "react\|next\.js\|tailwind\|html\|css\|jsx\|tsx" "$OUTPUT_FILE" 2>/dev/null; then
        if grep -qi "swiftui" "$OUTPUT_FILE" 2>/dev/null; then
            pass "Platform-correct (SwiftUI present, web terms may be in kill list)"
        else
            fail "ANTI-PATTERN: Web patterns in iOS plan"
        fi
    else
        pass "No web framework confusion"
    fi

# ============================================================
# REVIEW SCENARIO
# ============================================================
elif [ "$SCENARIO" = "review" ]; then
    echo -e "${BOLD}Quality Scan: /ship-review output${RESET}"
    echo -e "File: $OUTPUT_FILE"
    echo -e "Lines: $(wc -l < "$OUTPUT_FILE")"

    section "Section Presence"
    check "REFERENCES LOADED receipt" "REFERENCES LOADED" "references loaded"
    check "Scope Drift Detection" "scope drift\|SCOPE DRIFT\|scope creep"
    check "Crit review" "crit\|HEART\|task success\|adoption\|happiness"
    check "Anti-Slop Check" "anti.slop\|ANTI.SLOP\|slop check"
    check "Pol Design Audit" "typography audit\|color system\|spacing\|pol.*audit\|design director"
    check "Eye Visual QA" "visual qa\|eye\|screenshot\|design system discovery"
    check "Test section" "test.*runner\|health score\|explore like a user"
    check "Adversarial Challenge" "adversarial\|challenge.*by name\|contradiction check"
    check "Health Score (numeric)" "[0-9][0-9]*/100\|health score.*[0-9]"
    check "Confidence Scoring" "confidence.*[0-9]\|CERTAIN\|LIKELY\|POSSIBLE"
    check "Risk Classification" "SAFE\|RISKY\|risk classif"
    check "Close-Your-Eyes Test" "close.your.eyes\|would you keep"
    check "STATUS line" "STATUS:.*DONE\|STATUS:.*APPROVED\|STATUS:.*NEEDS"

    section "Bug Detection (planted issues)"
    check "B1: Timer not invalidated" "invalidat.*onDisappear\|onDisappear.*timer\|timer.*cleanup\|timer.*leak"
    check "B2: Console print in production" "print.*production\|console.*log\|print.*Timer done\|remove.*print"
    check "B3: No completion handling" "completion.*missing\|no.*completion\|haptic.*missing\|no.*haptic\|no notification"
    check "B4: System blue instead of amber" "system.*blue\|default.*blue\|amber\|F59E0B\|accent.*color"
    check "B5: No type hierarchy" "type.*hierarchy\|font.*hierarchy\|no.*hierarchy\|type scale\|generic.*font"
    check "B6: Magic number padding" "magic.*number\|hardcoded.*padding\|spacing.*scale\|inconsistent.*padding"
    check "B7: Same corner radius" "corner.*radius\|border.*radius\|same.*radius"
    check "B8: No dark mode" "dark.*mode\|dark.*first\|dark.*theme\|no.*dark"
    check "B9: Time display too small" "too.*small\|32.*small\|larger.*display\|wall.*clock\|display.*size"
    check "B10: No accessibility labels" "accessibility.*label\|no.*label\|missing.*label\|VoiceOver"
    check "B11: No Dynamic Type" "dynamic.*type\|text.*size\|font.*scaling"
    check "B12: No reduced motion" "reduced.*motion\|motion.*preference\|accessibility.*motion"
    check "B13: No states (empty/completion/error)" "empty.*state\|error.*state\|completion.*state\|missing.*state"
    check "B14: Negative duration" "negative.*duration\|validation\|invalid.*duration"
    check "B16: LEARNINGS pattern violated" "LEARNINGS\|REF_SKIP\|timer.*pattern\|known.*pattern"

    section "Content Quality Signals"
    check "Findings are SwiftUI-specific" "swiftui\|@state\|@observable\|.font\|.padding\|onDisappear"
    check "References DECISIONS.md aesthetic" "decisions\|aesthetic\|amber\|dark.first"
    check "Adversarial challenges by name" "crit.*did\|pol.*did\|eye.*did\|crit.*said\|pol.*said"
    check "Findings prioritized" "must.fix\|critical\|high\|medium\|low\|severity"

    section "Anti-Pattern Check"
    if grep -qi "nice.*structure\|good.*job\|well.*written\|clean.*code\|looks good overall" "$OUTPUT_FILE" 2>/dev/null; then
        fail "ANTI-PATTERN: Opens with compliment"
    else
        pass "No sycophantic opening"
    fi

    # Health score should be below 50 for this buggy code
    health=$(grep -oE '[0-9]+/100' "$OUTPUT_FILE" 2>/dev/null | head -1 | cut -d/ -f1)
    if [ -n "$health" ]; then
        if [ "$health" -le 50 ]; then
            pass "Health score realistic ($health/100 for buggy code)"
        else
            fail "ANTI-PATTERN: Health score too generous ($health/100 for code with 16 bugs)"
        fi
    else
        fail "No health score found in output"
    fi

else
    echo "Unknown scenario: $SCENARIO (use 'plan' or 'review')"
    exit 1
fi

# ============================================================
# SUMMARY
# ============================================================
section "SUMMARY"

echo -e "  ${GREEN}Passed:${RESET}  $PASS"
echo -e "  ${RED}Failed:${RESET}  $FAIL"
echo -e "  ${BOLD}Total:${RESET}   $TOTAL checks"

SCORE_PCT=$((PASS * 100 / TOTAL))
echo -e "\n  ${BOLD}Quality Score: ${SCORE_PCT}%${RESET} ($PASS / $TOTAL)"

if [ "$SCORE_PCT" -ge 80 ]; then
    echo -e "  ${GREEN}${BOLD}QUALITY: GOOD${RESET}"
elif [ "$SCORE_PCT" -ge 60 ]; then
    echo -e "  ${YELLOW}${BOLD}QUALITY: ACCEPTABLE${RESET}"
else
    echo -e "  ${RED}${BOLD}QUALITY: NEEDS IMPROVEMENT${RESET}"
fi
