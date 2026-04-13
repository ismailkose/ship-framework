# Test Scenario: /ship-review

## Input
```
/ship-review
```
(No flags — Smart Flag Resolution should auto-detect and run full suite on FocusTimerView.swift)

## Mock Project
Uses `fixtures/` — FocusFlow with intentionally buggy FocusTimerView.swift and clean FocusSession.swift.

## Planted Bugs (must-finds)
The test file has these intentional issues. A quality review MUST catch them:

| # | Bug | Category | Severity |
|---|---|---|---|
| B1 | Timer not invalidated in onDisappear | Code/Crash | Critical |
| B2 | Console print("Timer done!") in production | Code | Medium |
| B3 | No completion handling (haptics, notification) | UX/Task Success | High |
| B4 | Default system blue instead of amber accent (#F59E0B) | Design/Slop | High |
| B5 | No type hierarchy (generic .system sizes) | Design/Slop | High |
| B6 | Magic number padding (16, 20) instead of spacing scale | Design/Slop | Medium |
| B7 | Same corner radius everywhere | Design/Slop | Medium |
| B8 | No dark mode despite "dark-first" design direction | Design/Direction | Critical |
| B9 | Time display too small (32pt) for "wall clock" preference | Design/Founder Pref | High |
| B10 | No accessibility labels | Accessibility | High |
| B11 | No Dynamic Type support | Accessibility | High |
| B12 | No reduced motion consideration | Accessibility | Medium |
| B13 | No empty/completion/error states | UX/States | High |
| B14 | Negative duration possible in FocusSession | Code/Validation | Medium |
| B15 | No preview with different states | Dev/Testing | Low |
| B16 | LEARNINGS.md timer pattern violated | Process/REF_SKIP | High |

## Quality Rubric

### Section Presence (must appear)

| # | Expected Section | Present? | Notes |
|---|---|---|---|
| 1 | REFERENCES LOADED receipt | | Specific filenames listed |
| 2 | Scope Drift Detection (Step 0) | | Check diff against TASKS.md |
| 3 | Crit review (HEART dimensions) | | At least 2-3 dimensions evaluated |
| 4 | Pol Anti-Slop Check | | Checklist with specific flags |
| 5 | Pol Design Audit (Steps 2-9) | | Typography, color, spacing, interaction |
| 6 | Eye Visual QA | | Design System Discovery + bug checklist |
| 7 | Test section | | Test runner check + explore like a user |
| 8 | Adversarial Challenge | | By-name challenges to Crit/Pol/Eye |
| 9 | Health Score | | Numeric score with breakdown |
| 10 | Confidence scores on findings | | 50-100 range per finding |
| 11 | Risk Classification | | SAFE vs RISKY per change |
| 12 | Fix-First categorization | | "Just fix" vs "Ask first" |
| 13 | Close-Your-Eyes Test | | Honest assessment |
| 14 | Handoff (TASKS.md update) | | Findings added to tasks |
| 15 | STATUS line | | APPROVED / NEEDS_WORK |
| 16 | REF_SKIP detection | | Timer invalidation pattern from LEARNINGS |

### Bug Detection Rate

| # | Bug | Found? | By Whom? | Confidence |
|---|---|---|---|---|
| B1 | Timer not invalidated in onDisappear | | | |
| B2 | Console print in production | | | |
| B3 | No completion handling | | | |
| B4 | System blue instead of amber | | | |
| B5 | No type hierarchy | | | |
| B6 | Magic number padding | | | |
| B7 | Same corner radius | | | |
| B8 | No dark mode | | | |
| B9 | Time display too small | | | |
| B10 | No accessibility labels | | | |
| B11 | No Dynamic Type | | | |
| B12 | No reduced motion | | | |
| B13 | No empty/completion states | | | |
| B14 | Negative duration possible | | | |
| B15 | No preview states | | | |
| B16 | LEARNINGS timer pattern violated | | | |

**Detection rate: ___ / 16 bugs found**

### Reviewer Attribution
Each finding should be attributed to the correct reviewer persona:

| Reviewer | Expected Findings | Correct Attribution? |
|---|---|---|
| Crit | B1, B2, B3, B10, B11, B13, B14, B16 | |
| Pol | B4, B5, B6, B7, B8, B9, B12 | |
| Eye | B4, B8, B9 (visual confirmation) | |
| Test | B1, B2, B14, B15 | |
| Adversarial | Challenges approvals, finds what others missed | |

### Content Quality (score 1-5 per item)

| # | Quality Check | Score | Notes |
|---|---|---|---|
| Q1 | Anti-slop check catches the "default app" look | | Should flag 5+ slop items |
| Q2 | Crit references LEARNINGS.md timer pattern | | REF_SKIP detection |
| Q3 | Pol references DECISIONS.md aesthetic direction | | Amber accent, dark-first |
| Q4 | Findings are specific (not "improve accessibility") | | Should say exactly what + where |
| Q5 | Fix suggestions are iOS/SwiftUI-specific | | Not generic web patterns |
| Q6 | Health score is realistic (should be <50) | | This code is pretty bad |
| Q7 | Adversarial challenges by name | | "Crit, did you check..." |
| Q8 | Confidence scores differentiate certain vs possible | | Not everything at 90 |
| Q9 | Findings prioritized (critical before low) | | Must-fix vs nice-to-have |
| Q10 | Close-your-eyes test is honest (not flattering) | | Should say "would not keep" |

### Anti-Patterns (should NOT appear)

| # | Anti-Pattern | Found? |
|---|---|---|
| A1 | Opening with a compliment ("Nice structure, but...") | |
| A2 | All findings at same severity (no prioritization) | |
| A3 | Generic accessibility advice (not SwiftUI-specific) | |
| A4 | Missing Cross-Reference between reviewers | |
| A5 | Health score above 50 (this code is seriously flawed) | |
| A6 | No mention of DECISIONS.md aesthetic direction | |

### Scoring

```
Section Presence:     ___ / 16
Bug Detection:        ___ / 16
Content Quality:      ___ / 50
Anti-Patterns:        ___ / 6  (each worth -5 if found)

TOTAL: ___ / 82 baseline + anti-pattern deductions
```

## Baseline Score (pre-Phase 6+7)
Run date: ___________
Score: ___ / 82
Bugs found: ___ / 16
Notes: ___________

## Post-Change Score (after Phase 6+7)
Run date: ___________
Score: ___ / 82
Bugs found: ___ / 16
Notes: ___________

## Regression?
[ ] No regression — post score ≥ baseline AND bug detection ≥ baseline
[ ] Minor regression — score 1-5 lower OR 1-2 fewer bugs (acceptable if explainable)
[ ] Major regression — score >5 lower OR 3+ fewer bugs (BLOCK the change)
