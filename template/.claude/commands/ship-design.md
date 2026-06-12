---
description: "Create or evolve a design system — competitor research, complete proposal, preview mockups, documented tokens."
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
- **Design-model schema** (`.claude/skills/ship/design/references/design-model-schema.md`) — required before writing or reading `design-model.yaml` / `design/components.yaml`
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
- `--tokens` — Generate or update `design-model.yaml` (the machine token registry). Print notice: "`--tokens` now manages design-model.yaml."
- `--research` — Competitor research phase only
- `--mockup` — AI mockup generation via GPT Image API (requires OPENAI_API_KEY)
- `--init` — Scaffold DESIGN.md + design-model.yaml + design/components.yaml + PDC.md (+ optional TASTE.md). If DESIGN.md already exists, generate the registry + PDC.md from it.
- `--preview` — Generate or open design system preview (HTML + native). See Preview section below.
- `split <section>` — Extract a section from DESIGN.md into `design/<section>.md`, update PDC.md pointer.

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

### Phase 6a: Documentation — DESIGN.md (prose layer)

Write `DESIGN.md` as the prose design file: rationale, voice & tone, do/don't, SAFE/RISK decisions. Values (hex, scales, spacing) live in `design-model.yaml` (Phase 6b) — prose explains *why*, the YAML holds *what*. Never duplicate values across the two.

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

### Phase 6b: design-model.yaml (machine layer)

Write the token registry. This is the file `/ship-build`, previews, and platform emitters read — the single source of truth for design values.

1. Load `design-model-schema.md` + `design-model-template.yaml` from `.claude/skills/ship/design/references/`
2. Fill the template from Phase 3 decisions: primitives (color ramps, type scale, radius, spacing, motion springs), then semantic + semantic_dark layers
3. Dark mode is required by default (`modes: [light, dark]`). Light-only needs explicit `modes: [light]` + a documented "Dark mode exception" in DESIGN.md
4. Motion is platform-neutral: springs named by character (gentle/snappy) with response/damping. Never write platform-specific motion values
5. Run the schema's validation rules (semantic paths resolve, no hex outside primitives, required keys in both modes)
6. Write `design-model.yaml` to project root and print a token receipt:

```
✓ design-model.yaml — 3 ramps · 4 type sizes · 2 radii · 2 springs · 6+2 semantic (light+dark)
```

### Phase 6c: Seed design/components.yaml

Register the starting primitives — the components the validated scope clearly demands:

1. From the Phase 3 component decisions, identify reusable primitives (test: *would a second screen plausibly want this?*)
2. Register what the scope demands — no numeric cap, but **speculative registration is banned** (no component without a planned screen that needs it)
3. Each entry references **semantic tokens only** (no hex, no primitive paths)
4. If design runs before any code exists, set the planned source path + `planned: true`; the first build session realizes it
5. Write `design/components.yaml` (create `design/` if needed)

### Phase 6d: PDC Generation (v2)

After the registry is written, generate `PDC.md` — the Project Design Contract manifest:

1. Parse the headings in the just-written DESIGN.md
2. For each heading matching a known section (overview, colors, typography, components, motion, voice-tone, do-dont), add a `sections:` entry pointing to `DESIGN.md#<anchor>`
3. Read CLAUDE.md for the `Stack:` field to set `platform:`
4. If TASTE.md does not exist, set `taste: missing`
5. Write PDC.md to the project root
6. Create dimension-specific refgate markers for all sections just written:
   ```bash
   touch .claude/.refgate-dim-ui .claude/.refgate-dim-motion .claude/.refgate-dim-copy
   ```

**PDC.md format:**
```yaml
# PDC.md — Project Design Contract
schema_version: 2
platform: <from CLAUDE.md Stack>

design_model: design-model.yaml        # the token registry (machine layer)
components:   design/components.yaml   # the component manifest

sections:                              # prose pointers (unchanged from v1)
  overview:    DESIGN.md#overview
  colors:      DESIGN.md#colors
  typography:  DESIGN.md#typography
  components:  DESIGN.md#components
  donts:       DESIGN.md#dos-and-donts

taste: TASTE.md   # or "missing"
```

**Backward compatibility:** PDC v1 files (no `design_model:` key) keep working exactly as before — no forced migration. `--init` offers the upgrade.

### --init Behavior

If `--init` flag is given:
- **DESIGN.md does not exist:** Run the full process above (Phases 1-5, then 6a-6d).
- **DESIGN.md exists, design-model.yaml doesn't:** Offer: "Extract design-model.yaml from your DESIGN.md? (~2 min)" — on yes, run Phases 6b-6d from the existing prose; on no, generate PDC v1 from headings only (legacy behavior).
- **PDC.md already exists:** Show current PDC state (note v1 vs v2), ask what to update.
- After PDC generation, prompt: "Run `/ship-variants --taste` to capture your design preferences?"
- Then prompt: "Run `/ship-design --preview` to generate a visual preview of your design system?"

### split <section> Behavior

If `split <section>` is given (e.g., `/ship-design split motion`):
1. Find the section heading in DESIGN.md matching `<section>` (case-insensitive)
2. Extract all content from that heading to the next heading of same or higher level
3. Create `design/` directory if it doesn't exist
4. Write extracted content to `design/<section>.md`
5. Replace the section in DESIGN.md with: `## Motion\n\nSee [motion.md](design/motion.md)`
6. Update PDC.md to point to the new file: `motion: design/motion.md`

### --preview Behavior

Generates a visual preview of the design system from DESIGN.md. Two artifacts, always both:
1. HTML preview at `design/preview/index.html` (cross-platform, browser)
2. Native preview (platform-specific, real fidelity)

If preview files already exist, check what changed in DESIGN.md since last generation. Update only affected sections, or regenerate fully if asked.

**Quality bar:** Study Tailwind docs, Radix UI, Vercel Geist, Apple HIG documentation sites. The preview should look like a world-class design system documentation page — not a token dump.

---

**Step 1: HTML preview — `design/preview/index.html`**

Single-file, no build, self-contained. Create `design/preview/` directory if needed.

**Registry sourcing:** if PDC.md has a `design_model:` key, ALL token values (CSS custom properties, swatches, scales, springs) come from `design-model.yaml` — never re-derived from DESIGN.md prose. The preview is the registry's mirror: add footer line "This page mirrors design-model.yaml + design/components.yaml — regenerate after registry changes."

**Layout:**
- Sticky left sidebar with section navigation (anchored links, highlights active section on scroll)
- Main content area with generous whitespace (max-width ~720px content, centered)
- Dark mode toggle in top-right corner (instant, CSS-only via `[data-theme]`)
- Page title: `Design System — [Product Name]` with generation date

**Sections (in this exact order):**

1. **Overview** — product name, emotional keywords from DESIGN.md, signature token called out. One hero composition showing a card + button + text using real tokens — demonstrates the system working together.

2. **Color** — grouped by semantic role, NOT a flat list:
   - Core: background, surface, accent (with `on-*` pairs — text rendered ON TOP of each background color)
   - Text: on-background, on-surface, tertiary
   - State: error, success, warning
   - Custom palettes (e.g., SHMEC'D)
   - Each swatch: colored rectangle + CSS var name + hex value + contrast ratio against its paired background
   - Light and dark side-by-side in two columns (not toggled separately)

3. **Typography** — real sentences from the app (not lorem ipsum), every size/weight rendered at actual scale. Below each specimen: font name, weight, size, line-height, letter-spacing as a small metadata row. If using multiple font families (serif + sans), show them side-by-side with their roles.

4. **Spacing** — visual ruler with nested boxes at each scale step, labeled with token name + px value. Below: a real UI fragment (like a list row or card) annotated with spacing values pointing to the gaps.

5. **Radius** — shape specimens from sharp to pill on the same baseline. Below each: a real component (button or card) at that radius to show the feel, not just the shape.

6. **Elevation & Depth** — stacked cards at each shadow level. Light mode shows shadows, dark mode shows luminance differences. Side-by-side comparison.

7. **Motion** — each named primitive as an interactive card. Click/hover to play the CSS-approximated animation. Shows: name, character tag (snappy/gentle/etc.), duration, easing curve visualized as a bezier path. Note: "CSS approximation — open native preview for exact feel."

8. **Components** — key components in all states (default, hover, pressed, disabled, loading, error) using real tokens. Mobile viewport (375px frame). Include: buttons, inputs, cards, chat bubbles (if app has chat), list rows.

8b. **System components** (when `design/components.yaml` exists) — one card per registered component: name, doc line, semantic tokens consumed, source file, state badge (`planned` / realized). This section IS the living component library — it must mirror the manifest exactly, neither inventing nor omitting entries.

9. **Voice & Tone** — tone slider positions rendered visually (formal↔casual, etc.). Example copy for each register. Do/Don't copy pairs.

10. **Do / Don't** — side-by-side cards, green left border for do, red for don't. Visual examples where possible, not just text rules.

**Code quality:** All tokens as CSS custom properties in `:root`. Clean semantic HTML. No framework dependencies. Must render correctly at 375px (mobile) through 1440px (desktop).

---

**Step 2: Native preview — MUST generate alongside HTML**

This is not optional. For iOS projects, this is more valuable than the HTML.

Check CLAUDE.md `Stack:` field. Generate the appropriate file:

**iOS → `DesignPreview.swift`** (place in project's Swift source, e.g., alongside other Views)

```swift
import SwiftUI

// MARK: - Colors
#Preview("Colors") {
    ScrollView {
        LazyVGrid(columns: [GridItem(.flexible()), GridItem(.flexible())]) {
            // Every Brand.* color as a labeled rounded rectangle
            // Show color name + hex below each
            // Left column: light mode, Right column: dark mode
        }
    }
}

// MARK: - Typography
#Preview("Typography") {
    ScrollView {
        VStack(alignment: .leading, spacing: 24) {
            // Every type scale entry with REAL text from the app
            // Below each: font name, weight, size as caption
            // Show both serif (Gelasio) and sans (Geist) if both used
        }
    }
}

// MARK: - Spacing
#Preview("Spacing") {
    VStack(spacing: 0) {
        // Nested rectangles at each spacing scale step
        // Labeled: token name + value (e.g., "space-md: 16pt")
    }
}

// MARK: - Components
#Preview("Components") {
    ScrollView {
        VStack(spacing: 32) {
            // Buttons: primary, secondary, destructive — each in default + disabled
            // Chat bubbles: user vs Eva style
            // Cards: surface with shadow
            // List rows: with real content
        }
    }
}

// MARK: - Motion
#Preview("Motion") {
    ScrollView {
        VStack(spacing: 24) {
            // Each named primitive as a tappable card
            // Tap triggers the REAL SwiftUI animation
            // Shows: primitive name, response/damping values
            // Uses actual Animation.spring(response:damping:) — real 60/120fps
        }
    }
}
```

The file must **compile**. Use actual `Brand.*` colors, actual font names, actual spacing values from Theme.swift. Read Theme.swift to get the real token references — don't guess values.

**Web → `design/preview/design-preview.tsx`** (or `.html` if no React)
**Android → `design/preview/DesignPreview.kt`** with `@Preview` composables.

---

**After generation, print:**
```
Preview generated:
  HTML:   design/preview/index.html (open in browser)
  Native: DesignPreview.swift (open in Xcode Canvas)

Run `open design/preview/index.html` to view in browser.
```

### motion-tune Behavior

If `--preview --tune` or `--motion-tune` is given, generate `design/preview/motion-tune.html` — an interactive tuning surface for motion primitives:

- Every named motion primitive from DESIGN.md#motion rendered as a card
- Each card has sliders for its parameters (`response`, `damping`, `duration`)
- Moving a slider re-runs the animation live
- "Changed from canonical" indicator + reset button per primitive
- "Save" button writes all pending changes back to DESIGN.md (motion section) or `design/motion.md` if split
- "Save as new primitive" — forks into a new named primitive instead of overwriting

This is the interactive tuning layer on top of the read-only previews. The HTML approximates iOS springs with CSS — for exact fidelity, check the native preview.

---

## Connections to Other Commands

- `/ship-design` creates `DESIGN.md` + `design-model.yaml` + `design/components.yaml` + `PDC.md`
- `/ship-plan` reads `DESIGN.md` for aesthetic direction
- `/ship-build` consults `design-model.yaml` + `design/components.yaml` before every UI element — the silent system-first loop (reuse on hit; register primitives on miss; one-offs stay local)
- `/ship-review` validates against `DESIGN.md` and the registry
- `/ship-variants` uses `DESIGN.md` as baseline
- `ship-refgate` reads `PDC.md` to gate edits by design dimension

---

## Handoff & Completion

End with one of:
- `STATUS: DONE` — DESIGN.md documented. Ready for /ship-plan or /ship-build.
- `STATUS: DONE_WITH_CONCERNS` — Completed, but [list concerns]
- `STATUS: BLOCKED` — Cannot proceed. Waiting on [brand assets / founder input / competitor access].
- `STATUS: NEEDS_CONTEXT` — Missing [what information needed]

User's request: $ARGUMENTS
