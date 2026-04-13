# Ship Framework — Test Bench

Quality benchmarking system for validating Ship Framework changes.

## Quick Start

```bash
# Run structural tests (automated, no setup needed)
bash tests/bench/run-bench.sh

# Run everything including quality tests
bash tests/bench/run-bench.sh --with-quality
```

## Three Test Layers

### Layer 1: Structural Integrity (automated)
Tests that all internal references resolve, frontmatter is valid, hooks return correct JSON, and file sizes are within targets.

```bash
bash tests/bench/test-structural.sh ./template
```

### Layer 2: Quality Scenarios (semi-automated)
Tests that command outputs contain the right sections, catch planted bugs, and avoid anti-patterns.

**Setup:**
1. Copy `fixtures/` into a test project that has Ship Framework installed
2. Run `/ship-plan` or `/ship-review` in that project
3. Copy the full output to `outputs/plan-output.txt` or `outputs/review-output.txt`
4. Run the scanner:

```bash
bash tests/bench/test-quality.sh plan outputs/plan-output.txt
bash tests/bench/test-quality.sh review outputs/review-output.txt
```

### Layer 3: Before/After Comparison

```bash
# Before making changes: save baseline
bash tests/bench/run-bench.sh --baseline

# After making changes: compare
bash tests/bench/run-bench.sh --compare
```

## Test Fixtures

The `fixtures/` directory contains a complete mock project:

- **FocusFlow** — a minimalist iOS focus timer app
- **CLAUDE.md** — iOS/SwiftUI stack, dark-first amber accent design
- **FocusTimerView.swift** — 16 planted bugs for /ship-review to find
- **FocusSession.swift** — mostly clean data model with 2 bugs
- **TASKS.md, DECISIONS.md, LEARNINGS.md, CONTEXT.md** — project memory

## Planted Bugs

FocusTimerView.swift has intentional issues across all review categories:

| Category | Count | Examples |
|---|---|---|
| Code/Crash | 2 | Timer not invalidated, console print |
| Design/Slop | 4 | System blue, no hierarchy, magic numbers |
| Design/Direction | 2 | No dark mode, time too small |
| Accessibility | 3 | No labels, no Dynamic Type, no reduced motion |
| UX/States | 1 | No empty/completion/error states |
| Process | 1 | LEARNINGS.md pattern violated |
| Validation | 1 | Negative duration possible |
| Testing | 1 | No preview states |
| **Total** | **16** | |

## Scenarios

- `scenarios/scenario-plan.md` — rubric for /ship-plan output quality
- `scenarios/scenario-review.md` — rubric for /ship-review output quality (with bug detection scoring)

## Interpreting Results

**Structural tests:** All should pass. Any failure means a broken reference or missing file.

**Quality tests:** Percentage score:
- 80%+ = Good quality, changes are safe
- 60-79% = Acceptable, review what's missing
- Below 60% = Quality regression, investigate before shipping

**Bug detection rate (review only):**
- 14-16 / 16 = Excellent
- 10-13 / 16 = Good
- Below 10 / 16 = Review quality degraded
