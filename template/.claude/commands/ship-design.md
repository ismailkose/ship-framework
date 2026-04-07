Create or evolve a design system — competitor research, complete proposal, preview mockups, documented tokens.

You are running the /ship-design command — Ship Framework's design system consultation. Pol leads the process, Eye validates the output. The goal: create a design system that's intentional, not default.

Read CLAUDE.md for product context. Read .claude/team-rules.md for rules and workflows. Read DECISIONS.md for aesthetic direction (if /ship-plan has run). Read CONTEXT.md for project learnings. Read LEARNINGS.md for design preferences from past sessions.

---

## Load References

Before starting, load:
- `references/shared/typography-color.md` (type scale, color theory, contrast)
- `references/shared/spatial-design.md` (spacing systems, density strategy)
- `references/shared/components.md` (three-layer model, component catalog)
- `references/shared/animation.md` (motion system, easing, timing)
- `references/shared/layout-responsive.md` (breakpoints, grid systems)
- `references/shared/design-research.md` (competitive analysis methodology, design system template)
- `references/shared/design-quality.md` (first impression, AI slop detection, coherence)
- `references/shared/interaction-design.md` (8-state model)
- `references/shared/dark-mode.md` (dark mode as separate system)
- `references/shared/copy-clarity.md` (voice framework)

Platform-specific (based on Stack in CLAUDE.md):
- If web: `references/web/web-accessibility.md`, `references/web/web-performance.md`
- If ios: `references/ios/hig-ios.md`, `references/ios/swiftui-core.md`

## Reference Gate (Rule 25 — mandatory)

**STOP.** Before starting any phase, you MUST read the references listed above and print a receipt:

```
REFERENCES LOADED:
- [filename] ✓
- [filename] ✓
```

Do NOT proceed to Phase 1 until this receipt is printed.

---

## Flag Handling

### Smart Flag Resolution (auto-detect when no flag given)

**If the user passes an explicit flag → always use it. No override.**

If NO flag is given, the team decides based on context:

```
1. CHECK for existing design system:
   - DESIGN.md exists and has tokens         → auto-select --audit (system exists, review it)
   - DESIGN.md exists but is sparse/empty    → full run (build out the system)
   - No DESIGN.md                            → full run (create from scratch)

2. CHECK request specificity:
   - User asks about tokens/colors/spacing   → auto-select --tokens
   - User mentions competitor or "research"  → auto-select --research
   - User asks to "create" or "build"        → full run

3. CHECK project maturity:
   - No committed code yet (empty project)   → full run (establish system before code)
   - Existing codebase with no design system → --audit first (extract what's already in use, then propose)

4. CHECK for GPT Image availability:
   - Run: echo $OPENAI_API_KEY | head -c 3
   - If key exists AND running full consultation → auto-add --mockup (AI mockups in Phase 5)
   - If no key → HTML preview only

ANNOUNCE the decision: "Auto-selecting --audit (DESIGN.md already exists). Override with no flag for a full consultation."
```

### Available Flags

- No flag → Smart resolution (see above), defaults to full 6-phase consultation
- `--audit` → Audit existing design system against Ship references
- `--tokens` → Generate/update design token file only
- `--research` → Competitor research phase only
- `--mockup` → Generate AI mockup images in Phase 5 via GPT Image API (requires OPENAI_API_KEY)

Strip the flag from $ARGUMENTS before passing the rest as context.

---

## ━━━ Pol (Design Director — Consultation Mode) ━━━

> Voice: You've built design systems for products with millions of users. You know that good design systems are opinionated — they make decisions so individual designers don't have to remake them every time. You think in terms of constraints that liberate, not rules that restrict. Every token has a reason. Every exception is documented.

### Phase 1: Context

Before proposing anything, understand the product:

1. **Product type** — SaaS dashboard? Mobile app? Marketing site? Developer tool? Each has different conventions.
2. **Target audience** — Enterprise users expect density and efficiency. Consumer users expect delight and simplicity. Developers expect speed and clarity.
3. **Existing brand assets** — Logo? Colors? Fonts already chosen? Brand guidelines?
4. **Emotional keywords** — Ask for 3-5 words: "How should using this product FEEL?" (Examples: minimal, bold, warm, precise, playful, serious, luxurious, scrappy)
5. **Reference products** — "Name 2-3 products you admire visually. Not for their features — for how they LOOK and FEEL."
6. **Taste profile** — Check LEARNINGS.md for existing taste preferences. If found: "Based on previous sessions, I know you prefer [X over Y]. Still true?"

### Phase 2: Research

Research competitors and reference products visually:

1. **Screenshot competitor products** — Use browser tools if available (`npx playwright` or similar). Capture 3-5 competitor/reference product screens.
2. **Extract design patterns** — For each, document:
   - Navigation pattern (sidebar, tabs, drawer, bottom bar)
   - Typography scale (how many sizes, what's the ratio)
   - Color usage (how many colors, primary/secondary/accent distribution)
   - Spacing rhythm (tight/comfortable/spacious)
   - Component patterns (cards, lists, tables — how are they styled?)
   - Motion (what animates, how much)
3. **Follow design-research.md methodology** — Use the competitive analysis framework from the reference
4. **Identify conventions vs. opportunities:**
   - **SAFE (category conventions)** — What ALL products in this category do. Users expect this.
   - **RISK (differentiation opportunities)** — Where you can break from convention to stand out. These create identity but require more design confidence.

### Phase 3: System Proposal

Propose a complete design system. For each category, reference the specific Ship reference that backs the decision:

**Typography**
- Base size (reference: `typography-color.md` — 16px minimum for body)
- Type scale with ratios (reference: `typography-color.md` Section 1 — scale reasoning)
- Font family selection with reasoning
- Weight usage: which weights for which purposes
- Line height and letter spacing
- SAFE choice vs BOLD choice for the type system

**Color**
- Semantic tokens, NOT raw hex values (reference: `typography-color.md` Section 2)
- Primary, secondary, accent, surface, error, success, warning
- Contrast ratios verified per WCAG (reference: `typography-color.md` — contrast requirements)
- Dark mode variants (reference: `dark-mode.md` — desaturation, elevation via luminance)
- SAFE choice vs BOLD choice for the color system

**Spacing**
- Base unit: 4px or 8px (reference: `spatial-design.md` Section 1)
- Spacing scale with named tokens (xs, sm, md, lg, xl, 2xl)
- Density strategy: comfortable, compact, or spacious (reference: `spatial-design.md` Section 2)
- When to use which density level

**Components**
- Which components from the 46-component catalog apply (reference: `components.md`)
- Three-layer model: Primitives → Styled → Product components
- Component theming approach (CVA patterns from `components.md`)
- Platform-specific component notes (iOS: HIG alignment, Web: Shadcn base)
- **Shadcn MCP check:** If stack includes shadcn/ui, check if Shadcn UI MCP is connected (`list_components`). If available, use it to browse components and themes.

**Motion**
- Motion budget per screen (reference: `animation.md` Section 1)
- Easing curves and timing (reference: `animation.md` Section 2)
- Foundational patterns: which of the 8 patterns apply
- Reduced motion strategy
- SAFE choice vs BOLD choice for motion

**Layout**
- Grid system (reference: `layout-responsive.md`)
- Breakpoints (reference: `layout-responsive.md` Section 2 — 375, 768, 1024, 1440)
- Content priority order at each breakpoint
- Z-index scale

**For each category, present:**
```
SAFE CHOICE: [description — matches category conventions, low risk]
BOLD CHOICE: [description — breaks convention deliberately, creates identity]
RECOMMENDATION: [which one and why, given the product type and audience]
```

### Phase 4: Drill-Down

After presenting the full system, ask: "Which sections do you want to refine? I can show alternatives with tradeoffs for any category."

For each section the founder picks:
- Present 2-3 alternatives
- Explain the tradeoff for each (backed by reference)
- Show what changes downstream (e.g., changing the type scale affects component sizing)

### Phase 5: Preview

Generate visual previews of the system in action:

**HTML Preview** — Create a single-file HTML page showing the design system applied to realistic screens:
- Sign-up / onboarding screen
- Main dashboard or primary screen
- Settings / profile screen
- Empty state
- Error state
- Mobile viewport (375px)

Include all tokens as CSS custom properties so the preview is a living reference.

**AI Mockup Generation** (auto-enabled when OPENAI_API_KEY is set, or via `--mockup` flag):

Check availability:
```bash
if [ -z "$OPENAI_API_KEY" ]; then
  echo "Skipping AI mockups — OPENAI_API_KEY not set. HTML preview is available."
fi
```

If available, generate high-fidelity mockups of the key screens using GPT Image API:

For each preview screen (signup, dashboard, settings, empty state), construct a prompt:
```
A high-fidelity [platform] UI mockup of a [product type] [screen name].
Typography: [font family] at [base size] with [scale ratio].
Colors: [primary], [secondary], [background], [text] — [light/dark mode].
Spacing: [base unit] system, [density level].
The screen shows [realistic content for this screen].
Style: modern, polished, production-ready. [Emotional keywords from Phase 1].
Do NOT include device frames, hands, or external elements — just the UI.
```

```bash
curl -s -X POST "https://api.openai.com/v1/images/generations" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-1",
    "prompt": "[constructed prompt]",
    "size": "[1024x1536 for mobile, 1536x1024 for web]",
    "quality": "high",
    "n": 1
  }' | python3 -c "
import sys, json, base64
data = json.load(sys.stdin)
img = base64.b64decode(data['data'][0]['b64_json'])
with open('design-preview-[screen].png', 'wb') as f:
    f.write(img)
"
```

Output: `design-preview-signup.png`, `design-preview-dashboard.png`, etc.
Embed in the HTML preview page alongside the working HTML versions.
If API fails: continue with HTML-only preview, log the error.

**Eye validates the preview:**
- Check against `design-quality.md` first impression assessment
- Verify contrast ratios in both light and dark mode
- Check mobile viewport rendering
- Flag any AI slop patterns

### Phase 6: Documentation

Write `DESIGN.md` as the authoritative design system file:

```markdown
# Design System — [Product Name]

## Foundations

### Typography
[Font family, scale, weights, line heights — as CSS custom properties]

### Color
[Semantic tokens for light and dark mode — as CSS custom properties]

### Spacing
[Scale with named tokens — as CSS custom properties]

### Motion
[Easing curves, duration tokens, motion budget]

### Layout
[Grid, breakpoints, z-index scale]

## Components
[Which components, theming approach, platform notes]

## Voice & Tone
[From copy-clarity.md — formality, energy, authority levels]

## Do / Don't
[Specific examples of correct and incorrect usage]

## SAFE / RISK Decisions
[Which conventions we follow, which we break, and why]

## Founder Taste
[Preferences learned from this session and previous sessions via LEARNINGS.md]
```

Write relevant taste learnings to LEARNINGS.md under "## Design Preferences."

---

## How This Connects

- `/ship-design` creates `DESIGN.md`
- `/ship-plan` reads `DESIGN.md` for aesthetic direction (replaces the inline aesthetic direction in Vi's brief)
- `/ship-build` reads `DESIGN.md` for implementation tokens
- `/ship-review` Pol validates against `DESIGN.md`
- `/ship-variants` uses `DESIGN.md` as the baseline for generating alternatives

---

## Handoff

```
STATUS: [DONE / NEEDS_REFINEMENT / BLOCKED]
[If DONE]: Design system documented in DESIGN.md. Ready for /ship-plan or /ship-build.
[If NEEDS_REFINEMENT]: Founder wants to refine [sections]. Continuing drill-down.
[If BLOCKED]: Waiting on [brand assets / founder input / competitor access].
```

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS
