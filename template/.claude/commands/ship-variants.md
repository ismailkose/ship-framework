---
description: "Generate theory-backed design variants — each justified against UX principles. Compare, rate, learn your taste."
disable-model-invocation: true
---

Generate theory-backed design variants — each justified against UX principles. Compare, rate, learn your taste.

Read CLAUDE.md for product context. Read DECISIONS.md for aesthetic direction. Read DESIGN.md for design system tokens. Read LEARNINGS.md for taste preferences from past sessions.

---

## Load References

Before generating variants, load:
- `.claude/skills/ship/ux/references/ux-principles.md` (Hick's Law, Fitts's Law, Peak-End, Goal Gradient)
- `.claude/skills/ship/ux/references/typography-color.md` (type and color theory)
- `.claude/skills/ship/ux/references/spatial-design.md` (spacing, density, whitespace)
- `.claude/skills/ship/ux/references/layout-responsive.md` (grid, breakpoints)
- `.claude/skills/ship/ux/references/interaction-design.md` (8-state model, micro-interactions)
- `.claude/skills/ship/motion/references/animation.md` (motion budget, easing)
- `.claude/skills/ship/ux/references/design-quality.md` (first impression, AI slop detection)
- `.claude/skills/ship/ux/references/navigation.md` (navigation patterns)
- `.claude/skills/ship/components/references/components.md` (component architecture)

## Reference Gate (Rule 25 — mandatory)

Before generating variants, read the references listed above and print a receipt confirming each file loaded. Then run: `touch .claude/.refgate-loaded`.

---

## Flag Handling

### Smart Flag Resolution

If an explicit flag is passed, use it. If no flag is given, auto-detect based on:
- **Brief scope:** Single component → `--quick` (2 variants inline). Full page/screen → full run (3 variants + board).
- **Prior feedback:** Recent variant-feedback.json → `--refine`. Old or missing → full run.
- **Taste maturity:** 5+ learnings → weight toward learned taste. 0 learnings → diverse variants.
- **Mockup availability:** OPENAI_API_KEY present + full page → auto-add `--mockup`. Components → HTML only.

### Available Flags

- No flag → Smart resolution (see above), defaults to 3 variants + HTML comparison board
- `--quick` → 2 variants, show inline (no comparison board)
- `--refine` → Read previous variant-feedback.json, generate refined options
- `--taste` → Show current taste profile from DESIGN.md and LEARNINGS.md
- `--mockup` → Generate AI mockup images via GPT Image API (requires OPENAI_API_KEY)

Strip the flag from $ARGUMENTS before passing the rest as the design brief.

---

## Pol (Design Director)

**Voice:** Design director who articulates the tradeoff space. Every variant has a thesis backed by a principle. Help the founder see what they're choosing between.

### Step 1: Understand the Brief

Read existing context (DESIGN.md, DECISIONS.md, LEARNINGS.md). Identify the tradeoff space: What are the key design tensions? (Speed vs. delight? Density vs. whitespace? Convention vs. memorability?)

### Step 2: Generate 3 Variants

Each variant optimizes for a DIFFERENT design principle, justified explicitly:

**Variant A: Optimize for [Principle]**
- Thesis: One sentence on the principle (e.g., "Hick's Law — faster task completion")
- Design tokens: Specific values (font size, spacing, colors)

**Variant B: Optimize for [Different Principle]**
- Thesis: One sentence (e.g., "Peak-End Effect — memorable finish")
- Design tokens: Specific values

**Variant C: Bold Departure**
- Thesis: One sentence breaking convention (e.g., "Asymmetric layout, oversized type")
- Design tokens: Specific values

**Rules:**
- Each variant VISUALLY DISTINCT (not just color swap)
- Mobile responsive (375px minimum)
- Anti-slop check passes (from design-quality.md)
- Respect learned dislikes; lean into learned preferences

### Step 3: Build Comparison Board

Generate `variant-comparison.html` with three columns (one per variant), each showing:
- Variant name and thesis (one sentence)
- Rendered HTML with design tokens
- 5-star rating input
- Comment textarea

Include a "What matters most?" selector (Speed / Delight / Memorability / Accessibility / Density) and submit button that saves feedback to `variant-feedback.json`.

**Board requirements:**
- Responsive (CSS Grid, mobile-friendly)
- Realistic content (not lorem ipsum)
- Self-contained (no external dependencies)
- Feedback saves via download or localStorage

**Quick mode:** Skip the board. Show variants inline with tokens and ask for preference directly.

### Step 3b: AI Mockup Generation (--mockup flag or auto-detected)

Skip this step if --mockup is not active.

**Check availability:** If OPENAI_API_KEY is set and brief is a full page/screen, generate AI mockups via GPT Image API.

**Prompt:** Combine product context (CLAUDE.md), variant thesis, design tokens, platform (Stack), and taste preferences (LEARNINGS.md).

**Output files:** `variant-A-mockup.png`, `variant-B-mockup.png`, `variant-C-mockup.png`. Size: `1024x1536` (mobile) or `1536x1024` (web).

**Embed in board:** Add `<img>` tags with labels "AI Mockup (visual direction)" and "Working HTML (interactive)".

**Error handling:** If API fails, log and continue with HTML-only board. Never block on mockup failure.

### Step 4: Process Feedback

After ratings are submitted:
1. **Synthesize** — "You prefer Variant X because [thesis]. Strongest elements: [list]."
2. **Recommend** — "Combine Variant A's layout with Variant C's typography."
3. **Record learnings** to LEARNINGS.md: `- **[date]** Prefers [thing] over [alternative] — context: [what]`
4. **Update DESIGN.md** (if exists): Add "## Founder Taste" section with cumulative preferences

### Step 5: Taste Profile (--taste flag)

If `--taste` is passed, display the current taste profile from DESIGN.md and LEARNINGS.md:
- STRONG PREFERENCES: Things consistently rated highly
- STRONG DISLIKES: Things consistently rated poorly
- PATTERNS: Principles preferred, qualities avoided
- CONFIDENCE: HIGH/MEDIUM/LOW based on data points

---

## Handoff

End with one of:
- `STATUS: DONE` — Variants explored. Taste recorded. Direction: [summary].
- `STATUS: AWAITING_FEEDBACK` — Board generated. Rate variants to continue.
- `STATUS: BLOCKED` — Waiting on: [what's needed]

User's request: $ARGUMENTS
