# Test Scenario: /ship-plan

## Input
```
/ship-plan Build a focus timer that helps remote workers protect deep work time. 25-minute sessions with a visual countdown ring.
```

## Mock Project
Uses `fixtures/` — FocusFlow iOS app, SwiftUI, SwiftData, dark-first amber accent.

## Quality Rubric

### Section Presence (must appear in output)
Check each item — present or absent.

| # | Expected Section | Present? | Notes |
|---|---|---|---|
| 1 | REFERENCES LOADED receipt | | Must list specific filenames with ✓ |
| 2 | Vi's Four Forcing Questions (Q1-Q4) | | WHO, STATUS QUO, WALK THROUGH, SMALLEST |
| 3 | Three Ways This Could Work (A/B/C) | | Three distinct experience descriptions |
| 4 | The Product Brief (Bar Test, JTBD, Magic Moment, Kill List, etc.) | | All 12 items |
| 5 | Aesthetic Direction (Safe + Bold choices) | | Must include font, colors, motion |
| 6 | Experience Walk-Through | | First launch + magic moment + return visit |
| 7 | Arc's Technical Plan | | Stack, data model, screen map, build order |
| 8 | RICE-scored build order | | Each item with JTBD + RICE score |
| 9 | Dual-Approach (Minimal vs Clean) | | Two approaches side by side |
| 10 | Dependency Analysis table | | Items with depends-on relationships |
| 11 | Security Check | | iOS-specific (Keychain vs UserDefaults, ATS) |
| 12 | Pol's Design Readiness Score | | 7 dimensions, each scored 0-10 |
| 13 | Adversarial Challenge | | Numbered attacks, by-name challenges |
| 14 | Adversarial VERDICT | | APPROVED or NEEDS REVISION |
| 15 | DECISIONS.md update mention | | Aesthetic direction logged |
| 16 | TASKS.md update mention | | Build order items as tasks |

### Content Quality (score 1-5 per item)

| # | Quality Check | Score | Notes |
|---|---|---|---|
| Q1 | Vi challenges assumptions (not just agreeing) | | Should push back on at least one aspect |
| Q2 | Arc references are iOS-specific (SwiftUI, SwiftData) | | Not generic web/cross-platform |
| Q3 | JTBD is concrete (not "users want to focus") | | Should name a specific situation + outcome |
| Q4 | Magic moment is experiential (not technical) | | "The ring fills and you feel..." not "Timer fires completion handler" |
| Q5 | Kill list is opinionated (not empty) | | Should explicitly exclude features |
| Q6 | Build order puts magic moment first | | Timer ring experience before history/settings |
| Q7 | Pol scores reflect real gaps in the plan | | Not all 10/10 — that's sycophancy |
| Q8 | Adversarial finds real issues (not generic) | | Should reference FocusFlow specifics |
| Q9 | Vi and Arc disagree on at least one thing | | The tension that catches problems |
| Q10 | References actually influenced the output | | UX principles, HIG, SwiftUI patterns visible |

### Anti-Patterns (should NOT appear)

| # | Anti-Pattern | Found? | Notes |
|---|---|---|---|
| A1 | Generic plan that could be any app | | "Find-and-replace the name" test |
| A2 | No reference to LEARNINGS.md patterns | | Timer invalidation pattern should appear |
| A3 | No reference to DECISIONS.md aesthetic | | Amber accent, dark-first should carry through |
| A4 | Sycophantic "great idea!" opening | | Should sharpen, not praise |
| A5 | Web/React patterns in iOS plan | | Stack confusion |
| A6 | Missing iOS security checks | | Keychain, ATS, Data Protection |

### Scoring

```
Section Presence:  ___ / 16 (each worth 1 point)
Content Quality:   ___ / 50 (each worth 1-5)
Anti-Patterns:     ___ / 6  (each worth -3 if found)

TOTAL: ___ / 66 baseline + anti-pattern deductions
```

## Baseline Score (pre-Phase 6+7)
Run date: ___________
Score: ___ / 66
Notes: ___________

## Post-Change Score (after Phase 6+7)
Run date: ___________
Score: ___ / 66
Notes: ___________

## Regression?
[ ] No regression — post score ≥ baseline
[ ] Minor regression — post score 1-5 points lower (acceptable if architectural benefit)
[ ] Major regression — post score >5 points lower (BLOCK the change)
