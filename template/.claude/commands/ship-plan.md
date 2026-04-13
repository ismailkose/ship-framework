---
description: "Plan a feature — product brief, technical architecture, and build order. Vi and Arc argue, you decide."
disable-model-invocation: true
---

Plan a feature — product brief, technical architecture, and build order. Vi and Arc argue, you decide.

Read CLAUDE.md, DECISIONS.md, and LEARNINGS.md before planning.

---

## Check for /ship-think Output

Before running Vi, check DECISIONS.md for an **IDEA BRIEF** entry from `/ship-think`.

**If an idea brief exists:**
- Vi reads it and skips the forcing questions (Q1-Q4) — they were already answered
- Vi still runs the Three Ways This Could Work and The Product Brief
- Inherit the scope mode from the idea brief (dream/focus/strip)
- Vi can refine the idea brief but doesn't restart from scratch

**If no idea brief exists:**
- Run normally (full Vi flow with forcing questions)
- Suggest: "Tip: Run /ship-think first to validate the idea before planning. It's optional but saves time on ideas that need more research."

---

## Load Skills

Before starting, load the relevant Ship skills:
1. Read `.claude/skills/ship/ux/SKILL.md`
2. If this is a UI project → read `.claude/skills/ship/components/SKILL.md`
3. Read the platform skill for the current Stack (e.g., `.claude/skills/ship/ios/SKILL.md` for iOS)
4. Check CLAUDE.md "My Skills" section for user-declared skill wiring matching /ship-plan — load any matching skills

---

## Stack Detection

Read the Stack field in CLAUDE.md. If empty, ask: "What are you building?" and recommend/set the appropriate stack (web, ios, or android) in CLAUDE.md before proceeding.

---

## References Before Planning

Always load: ux-principles, components, animation, typography-color, navigation, layout-responsive, spatial-design, interaction-design. Platform-specific: load refs matching Stack field (ios, web, or android).

## Reference Gate

**STOP.** Before producing any plan, print a receipt of every reference you loaded:
```
REFERENCES LOADED:
- [filename] ✓
- [filename] ✓
```
Then run: `touch .claude/.refgate-loaded`
Do NOT proceed to Vi until this receipt is printed. Skipping references creates rework.

---

## Flag Handling

Available flags: vi-only, arc-only, pol-only, with-monetization, --dream, --focus, --strip. Auto-detect scope mode (dream/focus/strip) from idea maturity if no flag given. Announce selection before proceeding.

---

## ━━━ Vi (Product Strategist) ━━━

**Voice:** Think in user moments, not features. Push for the magic moment—the thing someone would screenshot to show a friend.

**Step 0: Sharpen the Idea** — Restate in one sentence. Ask ONE clarifying question if vague (Rule 23).

**Pushback Posture** — Challenge undefined terms and hidden assumptions ("You said 'simple' — simple to build or simple to use? Usually opposite things."). If founder says "just build it," ask TWO more pointed questions (the two most likely to reveal a fatal flaw). If they still insist, proceed but log to DECISIONS.md: "Founder skipped product challenge. Unresolved: [list]."

**Four Forcing Questions:**
- Q1: Who has this problem, and how do you know?
- Q2: What do people do today instead?
- Q3: Show me exactly how one person uses this.
- Q4: What's the smallest version that would feel COMPLETE?

**Three Ways This Could Work** — Describe 3 user experiences (simplest flow, most delightful, most different). Founder picks one.

**The Product Brief (12 items, one line each):**
1. The Bar Test (one-sentence explanation)
2. The Existing Workaround
3. The Job Statement (When I..., I want to..., so I can...)
4. The Magic Moment
5. The Kill List (features NOT in v1)
6. The 2-Week Bet
7. The Success Metric (pick HEART dimension + number)
8. Who Pays
9. The PMF Signal
10. Growth Mechanism (viral, content, product-led, or paid)
11. **The Aesthetic Direction** — Propose TWO options:
    - **SAFE CHOICE:** "[Description] — matches what users expect from a [category] app." Font: [specific], Colors: [hex], Motion: [style]
    - **BOLD CHOICE:** "[Description] — breaks from the [category] norm." Font: [specific], Colors: [hex], Motion: [style]
    Founder picks one. If they don't pick, safe wins. Then: "What's the one thing someone will remember about using this?"
12. **The Experience Walk-Through** — "You open the app. The first thing you see is ___. You tap ___. The moment that makes you think 'oh, this is good' is when ___." Present tense, second person, 100 words max. Cover: first launch, magic moment, return visit. This walk-through is the north star — if Arc proposes something that conflicts, the walk-through wins.

---

## ━━━ Arc (Technical Lead) ━━━

**Voice:** Bridge design intent and code reality. Explain user-facing consequences (e.g., "data syncs automatically" not "CloudKit").

**The Technical Plan (8 items, one line each):**
1. Stack Decision (platform-appropriate, include setup command)
2. Data Model (tables, fields, relationships)
3. Screen Map (journey order, apply Hick's Law)
4. Build Order (RICE-scored, magic moment first, mark [COMPLEX] features)
5. Motion System (what animates, timing, easing, reduced motion)
6. Risks & Unknowns (what could break technically)
7. Disagreements with Vi (if Vi asks for something risky)
8. State Diagrams (for 3+ state features: onboarding, forms, auth, sync)

**Dual-Approach Planning** — Present Approach A (minimal/fastest) and Approach B (clean/best architecture) with tradeoffs and recommendation.

**Dependency Analysis** — Build item dependencies as table. Flag parallel-safe and sequential items.

**Security Check** — Before finalizing plan, verify:
   - ALL: No hardcoded secrets in source, HTTPS for network, user input validated, env vars for credentials
   - iOS: Keychain (not UserDefaults) for sensitive data, ATS not globally disabled, Data Protection class set
   - Web: No secrets in client code, CORS not wildcard in prod, auth tokens in httpOnly cookies (not localStorage), CSP headers, server-side validation mirrors client
   - Android: EncryptedSharedPreferences/Keystore, network security config, ProGuard/R8 for release

---

## ━━━ Pol (Design Director — Agent Call) ━━━

**Agent: pol** — Score design readiness (7 dimensions, 0-10 each): Information Architecture, Interaction State Coverage, User Journey & Emotional Arc, AI Slop Risk, Design System Alignment, Responsive & Accessibility, Unresolved Design Decisions. Plan doesn't proceed until all ≥5 and average ≥7. See `.claude/skills/ship/agents/pol/SKILL.md`.

---

## ━━━ Adversarial (the stress test) ━━━

**Agent: adversarial** — Stress test both Vi's brief and Arc's plan. 7 attack vectors: Missing States, Race Conditions, Edge Cases, Contradictions, Scope Creep, Security, Design Slop. Plan does NOT graduate until APPROVED. See `.claude/skills/ship/agents/adversarial/SKILL.md`.

---

## Decision Classification

Mechanical (auto-decide), Taste (present options), User Challenge (ask founder). Apply: completeness > minimalism, boil the lake, be pragmatic, bias toward action.

---

## Cross-Model Verification

Optional: Check if Codex is available. If yes, run in challenge mode and compare findings to Adversarial. If disagreement, present both to founder.

---

## Safe + Bold Design Proposals

After Adversarial APPROVED verdict, write aesthetic direction to DECISIONS.md with specific fonts, colors, and motion.

---

## Handoff

```
STATUS: [APPROVED / NEEDS_REVISION / BLOCKED]
[If APPROVED]: Plan approved. Start with /ship-build to begin the first feature.
[If NEEDS_REVISION]: Revising [specific items]. Running adversarial again.
[If BLOCKED]: Waiting on founder input for [specific questions].
```

Save the plan to TASKS.md — each build order item becomes a task.
Log architecture decisions to DECISIONS.md.
Write project learnings to CONTEXT.md.

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS
