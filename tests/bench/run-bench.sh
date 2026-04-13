#!/usr/bin/env bash
# Ship Framework — Test Bench Runner
# Runs all tests and generates a benchmark report.
#
# Usage:
#   bash tests/bench/run-bench.sh                    # structural tests only
#   bash tests/bench/run-bench.sh --with-quality     # structural + quality (needs output files)
#   bash tests/bench/run-bench.sh --baseline         # save results as baseline
#   bash tests/bench/run-bench.sh --compare          # compare against saved baseline
#
# Quality test workflow:
#   1. Set up a test project using fixtures/
#   2. Run /ship-plan or /ship-review, save output to tests/bench/outputs/
#   3. Run this script with --with-quality

set -euo pipefail

BENCH_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$BENCH_DIR/../.." && pwd)"
OUTPUTS_DIR="$BENCH_DIR/outputs"
BASELINE_FILE="$BENCH_DIR/baseline.json"

MODE="${1:-structural}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
RESET='\033[0m'

echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║   Ship Framework — Test Bench        ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo -e "  Date: $(date '+%Y-%m-%d %H:%M')"
echo -e "  Root: $ROOT_DIR"
echo ""

# ─────────────────────────────────────
# STRUCTURAL TESTS
# ─────────────────────────────────────
echo -e "${BOLD}▶ Running Structural Tests${RESET}"
echo ""

structural_result=0
bash "$BENCH_DIR/test-structural.sh" "$ROOT_DIR/template" || structural_result=$?

echo ""

# ─────────────────────────────────────
# QUALITY TESTS (if requested)
# ─────────────────────────────────────
if [ "$MODE" = "--with-quality" ] || [ "$MODE" = "--baseline" ] || [ "$MODE" = "--compare" ]; then
    mkdir -p "$OUTPUTS_DIR"

    echo -e "${BOLD}▶ Running Quality Tests${RESET}"
    echo ""

    quality_results=""

    if [ -f "$OUTPUTS_DIR/plan-output.txt" ]; then
        echo -e "${BLUE}Scanning /ship-plan output...${RESET}"
        bash "$BENCH_DIR/test-quality.sh" plan "$OUTPUTS_DIR/plan-output.txt" || true
        echo ""
    else
        echo -e "${YELLOW}⚠ No plan output found. Save /ship-plan output to:${RESET}"
        echo -e "  $OUTPUTS_DIR/plan-output.txt"
        echo ""
    fi

    if [ -f "$OUTPUTS_DIR/review-output.txt" ]; then
        echo -e "${BLUE}Scanning /ship-review output...${RESET}"
        bash "$BENCH_DIR/test-quality.sh" review "$OUTPUTS_DIR/review-output.txt" || true
        echo ""
    else
        echo -e "${YELLOW}⚠ No review output found. Save /ship-review output to:${RESET}"
        echo -e "  $OUTPUTS_DIR/review-output.txt"
        echo ""
    fi

    # Save baseline if requested
    if [ "$MODE" = "--baseline" ]; then
        echo -e "${BLUE}Saving baseline...${RESET}"
        cat > "$BASELINE_FILE" << BASELINE
{
  "date": "$(date '+%Y-%m-%d %H:%M')",
  "structural_exit": $structural_result,
  "plan_output_exists": $([ -f "$OUTPUTS_DIR/plan-output.txt" ] && echo "true" || echo "false"),
  "review_output_exists": $([ -f "$OUTPUTS_DIR/review-output.txt" ] && echo "true" || echo "false"),
  "notes": "Pre-Phase 6+7 baseline"
}
BASELINE
        echo -e "${GREEN}Baseline saved to $BASELINE_FILE${RESET}"
    fi

    # Compare if requested
    if [ "$MODE" = "--compare" ]; then
        if [ -f "$BASELINE_FILE" ]; then
            echo -e "${BLUE}Comparing against baseline...${RESET}"
            echo -e "  Baseline date: $(python3 -c "import json; print(json.load(open('$BASELINE_FILE'))['date'])" 2>/dev/null || echo "unknown")"
            echo -e "  Baseline structural: $(python3 -c "import json; d=json.load(open('$BASELINE_FILE')); print('PASS' if d['structural_exit']==0 else 'FAIL')" 2>/dev/null || echo "unknown")"
            echo ""
            echo -e "  ${YELLOW}Manual comparison needed:${RESET}"
            echo -e "  Compare the quality scores from this run against the baseline outputs."
            echo -e "  Baseline outputs should be in: $OUTPUTS_DIR/baseline-*.txt"
            echo -e "  Current outputs should be in:  $OUTPUTS_DIR/plan-output.txt, review-output.txt"
        else
            echo -e "${RED}No baseline found. Run with --baseline first.${RESET}"
        fi
    fi
fi

# ─────────────────────────────────────
# FINAL REPORT
# ─────────────────────────────────────
echo ""
echo -e "${BOLD}═══════════════════════════════════════${RESET}"
if [ "$structural_result" -eq 0 ]; then
    echo -e "${GREEN}${BOLD}  Structural: ALL PASSED${RESET}"
else
    echo -e "${RED}${BOLD}  Structural: FAILURES DETECTED${RESET}"
fi
echo -e "${BOLD}═══════════════════════════════════════${RESET}"
