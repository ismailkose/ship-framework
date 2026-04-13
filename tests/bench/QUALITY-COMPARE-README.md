# Ship Framework Quality Comparison Tool

## Overview

This interactive HTML tool compares the quality output of Ship Framework commands **before slimming** (~600 lines per command) vs **after slimming** (~190 lines + agents).

**File:** `E2E-QUALITY-COMPARE.html`

## What It Does

### Two Scenarios

1. **Scenario 1: /ship-plan**
   - Input: "Build a focus timer that helps remote workers protect deep work time..."
   - Project: FocusFlow iOS app (SwiftUI, SwiftData, dark-first amber accent)
   - Verifies 22 quality markers (forcing questions, brief items, design readiness, adversarial challenge, etc.)

2. **Scenario 2: /ship-review**
   - Input: Review FocusTimerView.swift (intentionally buggy with 16 planted issues)
   - Project: Same FocusFlow
   - Verifies 25 quality markers (scope drift, HEART dimensions, anti-slop, visual QA, health score, bug detection, etc.)

### Quality Markers Checked

#### /ship-plan markers:
- REFERENCES LOADED receipt
- Four Forcing Questions (Q1-Q4)
- Three Ways / Experiences (A/B/C)
- Product Brief items (bar test, JTBD, magic moment, kill list, etc.)
- Aesthetic Direction (Safe + Bold choices)
- Experience Walk-Through
- Build Order with RICE scoring
- Dual-Approach (Minimal vs Clean)
- Dependency Analysis
- Security Check (iOS-specific)
- Pol Design Readiness Score (7 dimensions)
- Adversarial Challenge
- Anti-patterns: No sycophantic opening, no web patterns in iOS

#### /ship-review markers:
- Scope Drift Detection
- HEART dimensions (Task success, Adoption, Happiness, Engagement, Retention)
- Anti-Slop Check (typography, color, layout, components, motion)
- Eye Visual QA (layout, typography, spacing, color, states)
- Test Health Score (numeric 0-100)
- Adversarial challenges (by name: Crit, Pol, Eye, Test)
- Confidence Scoring
- Risk Classification (SAFE/RISKY)
- Close-Your-Eyes Test
- TODO/FIXME scan
- 16 specific bugs: timer invalidation, console print, no completion handling, system blue not amber, no type hierarchy, magic padding, no dark mode, display too small, no accessibility labels, no Dynamic Type, no reduced motion, empty/completion states, negative duration, learnings pattern violations
- Anti-patterns: No compliments opening, health score appropriate

## How to Use

### 1. Open the Tool

```bash
open /sessions/stoic-serene-keller/mnt/designer-ship-framework/tests/bench/E2E-QUALITY-COMPARE.html
```

Or drag the file into your browser.

### 2. Select Scenario

Click the tab: **"Scenario 1: /ship-plan"** or **"Scenario 2: /ship-review"**

### 3. Copy Prompts

For each panel (BEFORE/AFTER):
- Click **"Copy Prompt"** button
- Paste the prompt into Claude (or your AI tool)
- Run the command and get the output

The prompts are **fully embedded** in the HTML — they include:
- The full command text (before or after version)
- All fixture files (CLAUDE.md, DECISIONS.md, LEARNINGS.md, TASKS.md, CONTEXT.md)
- For /ship-review: code files (FocusTimerView.swift, FocusSession.swift)
- For after: agent SKILL.md files (pol, crit, eye, test, adversarial)

### 4. Paste Outputs

In each panel's textarea, paste the complete output from the AI tool.

### 5. Score Both

Click **"Score Both {scenario} Outputs"** button.

The tool will:
- Scan both outputs for each quality marker using regex patterns
- Build a comparison table
- Show BEFORE/AFTER status for each marker
- Calculate summary stats (passes, improvements, regressions, failures)
- Display a verdict: ✅ EQUIVALENT, 📈 IMPROVEMENT, or ⚠️ NEEDS REVIEW

### 6. Interpretation

**Status column meanings:**

- **PASS** — Both versions detected the marker (✓ on both sides)
- **IMPROVED** — Only after version detected it (✗→✓)
- **FAIL** — Neither version detected it (✗ on both sides)
- **REGRESSED** — Only before version detected it (✓→✗) ⚠️

**Summary verdict:**

- **✅ EQUIVALENT** — After maintains all markers. No regressions. Safe to deploy.
- **📈 IMPROVEMENT** — After improves on some markers. Strong signal.
- **⚠️ NEEDS REVIEW** — After regressed on some markers. Investigate why.

### 7. Export Report

After scoring both scenarios, click **"Generate Markdown Report"** to download a markdown summary with:
- Executive summary
- Both scenarios' input/context
- Comparison results
- Key findings
- Recommendations

## Embedded Content

The HTML includes:

1. **Full command text** (before and after versions)
2. **All fixture files** for the FocusFlow test project:
   - CLAUDE.md (product context)
   - DECISIONS.md (architecture & design direction)
   - LEARNINGS.md (patterns, preferences, decisions)
   - TASKS.md (build queue)
   - CONTEXT.md (project learnings)
   - FocusTimerView.swift (intentionally buggy code)
   - FocusSession.swift (clean model file)
3. **Agent SKILL.md files** (for "after" version):
   - pol (design director)
   - crit (product reviewer)
   - eye (visual QA)
   - test (QA tester)
   - adversarial (stress tester)

Everything is **self-contained in one HTML file** — no external dependencies except Tailwind CSS (via CDN).

## Design

- **Dark theme** optimized for long review sessions
- **Two-column layout** for easy side-by-side comparison
- **Tabbed interface** for switching between scenarios
- **Real-time scoring** with visual status indicators (✓, ✗, colors)
- **Responsive** (works on desktop, tablet, mobile)
- **Clipboard integration** for easy prompt copying

## Quality Markers Regex Patterns

Each marker uses a regex pattern to detect presence in the output:

```javascript
// Example: detect "REFERENCES LOADED"
pattern: /REFERENCES LOADED/i

// Example: detect forcing questions
pattern: /Q1.*WHO NEEDS|who needs this/i

// Example: detect security checks
pattern: /security|keychain|ATS|hardcoded|api key|user data/i
```

**Note:** Patterns are tuned for real command output. If a scenario produces unexpected scores, review the output text to see if the pattern needs refinement.

## Workflow

1. **Run BEFORE prompt** → Copy, run in Claude, paste output
2. **Run AFTER prompt** → Copy, run in Claude, paste output
3. **Score both** → View comparison table and verdict
4. **Investigate any regressions** → Check the output text to understand why a marker was missed
5. **Repeat for second scenario** → Same workflow for /ship-review
6. **Export report** → Share findings with team

## Expected Results

### Success Criteria

**BEFORE vs AFTER should be equivalent** (or AFTER should improve):

- Both versions detect the same quality markers
- No significant regressions
- Slimmed version maintains same rigor with ~70% less context per command
- Evidence that agents provide the same structured output as the inline instructions

### What to Watch For

**If AFTER regresses on a marker:**
1. Check the agent's SKILL.md file — is the instruction missing?
2. Check the AI output — did it skip the step? (e.g., Crit didn't run health score?)
3. Verify the regex pattern — does it need adjustment for the actual output format?
4. Consider if the slimming accidentally removed a critical instruction

## Files Modified

- ✅ Created: `/sessions/stoic-serene-keller/mnt/designer-ship-framework/tests/bench/E2E-QUALITY-COMPARE.html` (50KB, 1267 lines)

## Prompts Included (Embedded)

### BEFORE Prompts
- ship-plan-before.md (~600 lines) — Full verbose command
- ship-review-before.md (~600 lines) — Full verbose command

### AFTER Prompts
- ship-plan.md (~190 lines) — Slimmed command
- ship-review.md (~190 lines) — Slimmed command

### Agent SKILLs (used in AFTER prompts)
- pol/SKILL.md
- crit/SKILL.md
- eye/SKILL.md
- test/SKILL.md
- adversarial/SKILL.md

### Fixtures (used in both)
- CLAUDE.md — Product context
- DECISIONS.md — Architecture & design decisions
- LEARNINGS.md — Known patterns & preferences
- TASKS.md — Build queue
- CONTEXT.md — Project learnings
- FocusTimerView.swift — Buggy view with 16 planted issues
- FocusSession.swift — Clean data model

## Troubleshooting

**"Copy Prompt not working"**
- Prompts are embedded in the HTML. If the copy button doesn't work, select all text in the textarea and copy manually.

**"Scoring not detecting any markers"**
- Paste the full AI output in the textarea, not just a partial response.
- Check that the text includes the expected keywords for each marker.
- If markers are genuinely missing, investigate the prompt — the command may not be producing that section.

**"Only one scenario's buttons work"**
- Both scenarios should work independently. Reload the page if buttons become unresponsive.

**"Export button doesn't download"**
- Check your browser's download settings. The file will be named `ship-framework-quality-comparison-YYYY-MM-DD.md`.

## Next Steps

1. **Run both scenarios** against the embedded prompts
2. **Compare results** — Are before and after equivalent?
3. **Document any discrepancies** — If after regresses, note which markers and investigate
4. **Share findings** — Use the exported markdown report with the team
5. **Iterate** — If needed, refine agent SKILLs or command text and re-run

## Questions?

This tool is designed to be self-explanatory. Every aspect is embedded in the single HTML file for portability and version control. See the JavaScript console for any errors during scoring.
