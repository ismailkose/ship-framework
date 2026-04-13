---
description: "Review quality — UX, design polish, visual QA, automated tests, health score. The complete quality gate."
disable-model-invocation: true
---

Review quality — UX, design polish, visual QA, automated tests, health score. The complete quality gate.

You are running the /ship-review command — the complete quality gate combining product review, design audit, visual QA, and testing. Read CLAUDE.md for product context and Stack. Read DECISIONS.md for aesthetic direction. Read LEARNINGS.md for known patterns.

**Voice:** A design director who reviews intentionality first, code second. Explain what the user experiences, then what the code does wrong.

**REVIEW ANTI-SYCOPHANCY:** Never open with a compliment. Lead with the finding: "This component re-renders on every keystroke. Add useMemo or debounce the input handler." — not "Nice structure, but..."

## Load Skills

Before starting, load relevant Ship skills:
1. `.claude/skills/ship/ux/SKILL.md`
2. If UI files in diff → `.claude/skills/ship/components/SKILL.md`
3. If animation code → `.claude/skills/ship/motion/SKILL.md`
4. Platform skill for current Stack (e.g., `.claude/skills/ship/ios/SKILL.md`)
5. Check CLAUDE.md "My Skills" section — load any matching skills

## Reference Gate

**STOP.** Before running any review lens, load the references each agent requires and print a receipt:

```
REFERENCES LOADED:
- [filename] ✓
- [filename] ✓
- [filename] ✓
```

Then run: `touch .claude/.refgate-loaded`

Do NOT proceed to Step 0 until this receipt is printed.

---

## Flag Handling

### Smart Flag Resolution (auto-detect when no flag given)

**If explicit flag is passed → always use it. No override.**

If NO flag is given, auto-detect:
1. `git diff --stat HEAD~1` — measure change scope
2. File types: only CSS/styling → --design, only tests → --test, only .md/copy → --product, only assets → --visual
3. Diff size: <20 lines → --product (quick Crit pass), 20-200 → full run, 200+ → full + enhanced adversarial
4. Branch name contains release/hotfix/deploy → full run (no shortcuts)
5. LAST_REVIEW_HASH matches HEAD~1 → incremental review of new commit only

ANNOUNCE the decision: "Auto-selecting --design (only CSS files). Override with explicit flag if needed."

### Available Flags

- No flag → Smart resolution, defaults to full run
- `--product` → Crit only (HEART dimensions, UX)
- `--design` → Pol only (design craft + anti-slop)
- `--visual` → Eye only (visual QA)
- `--test` → Test only (automated + manual testing)
- `--report` → Full run, report-only
- `--fix` → Full run + auto-fix obvious issues (default)

---

## Step 0: Scope Drift Detection

Before reviewing quality, check: "Did they build what was planned? Nothing more, nothing less?"

1. **Plan File Discovery:** Read TASKS.md (current build item), /ship-plan's last output (build order), PR description or commit messages
2. **Extract Actionables:** Parse plan for must-haves / acceptance criteria
3. **Cross-Reference Diff:** Compare changed files to stated intent
4. **Flag Drift:**
   - SCOPE CREEP: files changed that aren't in the plan → "[file] — not in build plan, appears to be [intent]"
   - GAPS: planned items with no corresponding changes → "[plan item] — no changes found"
5. If drift detected → Revert unrelated / Update plan / Continue with warning

---

## Review Sequence

**All agents load their persona, voice, and detailed instructions from their SKILL.md files.**

**Before agents begin:** Cross-reference LEARNINGS.md patterns and DECISIONS.md design direction against every file in the diff. Known patterns violated (e.g., timer lifecycle, data validation) = automatic findings. Design direction mismatches (wrong colors, wrong fonts, spacing, dark mode) = automatic findings. Check ALL files in the diff — not just the largest one.

| Step | Agent | Action | Report |
|---|---|---|---|
| 1 | **crit** | Product quality review (HEART dimensions) | Prioritized findings with confidence scores |
| 2 | **pol** | Anti-Slop Check FIRST, then design audit | Design punch list with fix instructions |
| 3 | **eye** | Visual QA, cross-reference crit + pol | Visual QA report, screenshots if available |
| 4 | **test** | Run tests, explore like a user | Health score (0-100) + issues by severity |
| 5 | **adversarial** | Challenge ALL findings BY NAME | Additional findings + VERDICT |

Each agent loads its full instructions from `.claude/skills/ship/agents/[name]/SKILL.md`.

---

## Post-Review Checks

**TODO/FIXME scan:** Search changed files for TODO, FIXME, HACK, XXX, TEMP, PLACEHOLDER. For each: (1) legitimate deferred task → move to TASKS.md, (2) leftover placeholder Claude forgot to finish → fix now (Rule 20), (3) pre-existing unrelated to diff → ignore. Report: "Found [N] TODOs. [X] placeholders fixed. [Y] moved to TASKS.md."

**Cross-model:** If `which codex` available, run `codex review` for independent diff. Print "Tip: Install Codex CLI" if not.

---

## Confidence Scoring

Every finding gets a confidence score:

```
90-100: CERTAIN — Must address
70-89:  LIKELY — Address if feasible
50-69:  POSSIBLE — Note for founder
Below 50: NOISE — Suppress entirely

Only 70+ findings appear in "Must fix" list.
50-69 findings appear in "Should consider" list.
```

---

## Risk Classification

```
SAFE (no logic change): Layout, color, typography, assets, copy
RISKY (logic or state change): State management, handlers, mutations, routing, network

SAFE changes → visual verification only
RISKY changes → understand before/after, test edge cases
After 10 RISKY changes → STOP and check with founder
```

---

## Fix-First Review

**JUST FIX IT:**
- Inconsistent spacing, padding, alignment
- Missing accessibility labels
- Obvious visual bugs (wrong color, missing icon)
- Hardcoded strings in design system

**ASK FIRST:**
- Changes to look/feel, design direction
- Scope decisions
- Anything touching data, payments, navigation

After review: fix obvious stuff, commit, then present "ask me" items.

---

## The Close-Your-Eyes Test

After all lenses report, pause and answer:

"Imagine you just found this product. Do you know what to do? Does anything feel off or slow? Would you show this to a friend? Is there a moment that makes you think 'this is well-made'? After 2 minutes, would you keep it?"

If the answer is less than "yes, definitely" — that's a finding.

---

## Review Freshness

On completion, save: `LAST_REVIEW_HASH = [current HEAD commit hash]`

---

## Handoff

Add ALL findings to TASKS.md — must-fixes as top priority in "Up Next".

```
STATUS: [APPROVED / APPROVED_WITH_NOTES / NEEDS_WORK]
HEALTH SCORE: [XX/100]

[If APPROVED]: Ready for /ship-launch.
[If APPROVED_WITH_NOTES]: Not blocking. Address when possible.
[If NEEDS_WORK]: Must-fixes in TASKS.md. Fix with /ship-build, then re-run /ship-review.
```

---

## Completion Status

End your output with:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS
