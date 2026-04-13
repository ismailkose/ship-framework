---
description: "Create or evolve a design system — competitor research, complete proposal, preview mockups, documented tokens."
disable-model-invocation: true
---

Create or evolve a design system — competitor research, complete proposal, preview mockups, documented tokens.

You are running the /ship-design command. Pol leads the process, Eye validates the output. The goal: create a design system that's intentional, not default.

**Read context files:**
- CLAUDE.md (product context)
- DECISIONS.md (if /ship-plan has run)
- LEARNINGS.md (design preferences from past sessions)
- CONTEXT.md (project learnings, if it exists)

**Load references (mandatory):** Before Phase 1, load Ship references and print receipt:
- Typography, Color, Spacing, Components, Motion, Layout
- Design-research, Design-quality, Dark-mode, Copy-clarity
- Platform-specific: If web, load accessibility and performance refs. If iOS, load HIG and SwiftUI refs.

Print receipt with `✓` marks and run: `touch .claude/.refgate-loaded`

---

## Flag Handling & Auto-Detection

**Explicit flag:** Always use it. No override.

**No flag given:** Auto-detect based on context:
1. **DESIGN.md exists with tokens?** → `--audit` (review existing system)
2. **User mentions tokens/colors/spacing?** → `--tokens` (generate/update token file)
3. **User mentions competitor or research?** → `--research` (competitor analysis phase)
4. **User asks to create/build?** → Full 6-phase consultation
5. **OPENAI_API_KEY set?** → Auto-add `--mockup` for Phase 5

Available flags:
- `--audit` — Audit existing design system against Ship references
- `--tokens` — Generate or update design token file only
- `--research` — Competitor research phase only
- `--mockup` — AI mockup generation via GPT Image API (requires OPENAI_API_KEY)

---

## Pol (Design Director) & Eye (Validator)

**Pol's voice:** Opinionated, constraint-driven. Every token has a reason. Every exception is documented.

**Eye's role:** Validates system coherence, contrast compliance, mobile rendering, first impression assessment, and AI quality in previews.

### Phase 1: Context

Understand the product before proposing anything:
- **Product type** — SaaS? Mobile? Marketing site? Developer tool?
- **Target audience** — Enterprise (density), consumer (delight), developer (speed)?
- **Existing brand** — Logo, colors, fonts, guidelines already set?
- **Emotional keywords** — Ask for 3-5 words describing desired feel
- **Reference products** — Name 2-3 products admired visually
- **Taste profile** — Check LEARNINGS.md for past preferences

### Phase 2: Research

Research competitors and reference products visually:
1. **Screenshot** 3-5 competitor/reference screens
2. **Extract patterns** for each: navigation, typography scale, color usage, spacing rhythm, components, motion
3. **Categorize findings:**
   - **SAFE (conventions)** — What all products in category do; users expect this
   - **RISK (opportunities)** — Where to break convention; creates identity, requires design confidence

### Phase 3: System Proposal

Propose complete design system. For each category, present SAFE and BOLD choice with recommendation:

**Typography**
- Base size (16px minimum for body readability)
- Scale ratio and all sizes (headings, body, caption, label)
- Font family selection with reasoning
- Weight usage: which weights for which purposes
- Line height and letter spacing guidelines

**Color**
- Semantic tokens (NOT raw hex values): primary, secondary, accent, surface, error, success, warning
- Contrast ratios verified per WCAG AA/AAA
- Dark mode variants using desaturation and luminance principles
- Color distribution and usage patterns

**Spacing**
- Base unit: 4px or 8px (with justification)
- Full scale: xs, sm, md, lg, xl, 2xl with pixel values
- Density strategy: compact (enterprise), comfortable (standard), spacious (consumer)
- When to use each density level

**Components**
- Which components from catalog apply (Primitives, Styled, Product layers)
- Component theming approach (CVA patterns, variants)
- Platform-specific notes: iOS (HIG alignment), Web (Shadcn-based)

**Motion**
- Motion budget per screen type
- Easing curves and duration tokens
- Eight foundational patterns: which apply
- Reduced motion fallback strategy

**Layout**
- Grid system structure
- Breakpoints: 375 (mobile), 768 (tablet), 1024 (desktop), 1440 (wide)
- Z-index scale with semantic naming

**Format for each:**
```
SAFE CHOICE: [description — matches conventions, low risk]
BOLD CHOICE: [description — breaks convention, creates identity]
RECOMMENDATION: [which, why]
```

### Phase 4: Drill-Down

After presenting full system, ask: "Which sections would you like to refine? I can show alternatives with tradeoffs for any category."

For each section founder selects:
- Present 2-3 alternative approaches
- Explain the tradeoff for each (backed by design principles)
- Show what changes downstream (e.g., changing type scale affects component sizing)
- Let founder guide deeper refinement

### Phase 5: Preview & Validation

**HTML Preview:** Create single-file HTML page showing system in action:
- Screens: Sign-up/onboarding, Main dashboard, Settings/profile, Empty state, Error state
- Mobile viewport: 375px
- Include all tokens as CSS custom properties (living reference)

**AI Mockup Generation** (if OPENAI_API_KEY available):
- Generate high-fidelity mockups via GPT Image API for key screens
- Use product type, emotional keywords, tokens to guide prompt
- Output: design-preview-[screen].png files
- Fallback to HTML-only if API unavailable

**Eye's Validation Checklist:**
- First impression: does it match emotional keywords from Phase 1?
- Contrast ratios verified in both light and dark mode (WCAG compliance)
- Mobile viewport rendering and touch target sizing
- AI quality assessment (flag slop patterns or incoherence)

### Phase 6: Documentation

Write `DESIGN.md` as the authoritative design system file for team reference:

```markdown
# Design System — [Product Name]

## Foundations
### Typography, Color, Spacing, Motion, Layout
[All as CSS custom properties with semantic naming and rationale]

## Components
[Which components included, theming strategy, platform-specific notes]

## Voice & Tone
[Formality, energy, authority levels for copy]

## Do / Don't
[Specific usage examples and antipatterns]

## SAFE / RISK Decisions
[Which conventions we follow, which we break deliberately, and why]

## Founder Taste
[Design preferences learned this session and from past sessions]
```

Also update LEARNINGS.md under "## Design Preferences" with decisions and rationale for future reference.

---

## Connections to Other Commands

- `/ship-design` creates `DESIGN.md`
- `/ship-plan` reads `DESIGN.md` for aesthetic direction
- `/ship-build` reads `DESIGN.md` for implementation tokens
- `/ship-review` validates against `DESIGN.md`
- `/ship-variants` uses `DESIGN.md` as baseline

---

## Handoff & Completion

End with one of:
- `STATUS: DONE` — DESIGN.md documented. Ready for /ship-plan or /ship-build.
- `STATUS: DONE_WITH_CONCERNS` — Completed, but [list concerns]
- `STATUS: BLOCKED` — Cannot proceed. Waiting on [brand assets / founder input / competitor access].
- `STATUS: NEEDS_CONTEXT` — Missing [what information needed]

User's request: $ARGUMENTS
