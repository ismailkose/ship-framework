Generate theory-backed design variants — each justified against UX principles. Compare, rate, learn your taste.

Read CLAUDE.md for product context and DECISIONS.md for direction. If a design registry exists (`design-model.yaml`, `design/components.yaml`, `DESIGN.md`), variants explore *inside* it — registered tokens and components first. Query the founder's taste for the surface you're exploring:

```bash
python3 .claude/skills/ship/taste/bin/taste.py query --surface <screen> --domain layout,color,type,motion
```

## Load References

References these variants may need:
- `.claude/skills/ship/ux/references/ux-principles.md` (Hick's Law, Fitts's Law, Peak-End, Goal Gradient)
- `.claude/skills/ship/ux/references/typography.md` (type scale, hierarchy, pairing)
- `.claude/skills/ship/ux/references/color.md` (palette, semantic roles, contrast)
- `.claude/skills/ship/ux/references/layout-responsive.md` (grid, breakpoints, spacing, density)
- `.claude/skills/ship/ux/references/interaction-design.md` (state coverage, micro-interactions)
- `.claude/skills/ship/motion/references/animation.md` (motion budget, easing)
- `.claude/skills/ship/ux/references/design-quality.md` (first impression, AI slop detection)
- `.claude/skills/ship/ux/references/navigation.md` (navigation patterns)
- `.claude/skills/ship/components/references/components.md` (component architecture)

Load the references above that these variants touch (on demand, core rules › References) and name them in one line.

## Flag Handling

### Smart Flag Resolution

If an explicit flag is passed, use it. If no flag is given, auto-detect based on:
- **Brief scope:** Single component → `--quick` (2 variants inline). Full page/screen → full run (3 variants + board).
- **Prior feedback:** Recent variant-feedback.json → `--refine`. Old or missing → full run.
- **Taste maturity:** decisions in the taste query for this surface → weight toward them. None → diverse variants.
- **Mockup availability:** OPENAI_API_KEY present + full page → auto-add `--mockup`. Components → HTML only.

### Available Flags

- No flag → Smart resolution (see above), defaults to 3 variants + HTML comparison board
- `--quick` → 2 variants, show inline (no comparison board)
- `--refine` → Read previous variant-feedback.json, generate refined options
- `--taste` → Show the founder's recorded taste (`taste.py list`, readable view: `taste.py export-md`)
- `--mockup` → Generate AI mockup images via GPT Image API (requires OPENAI_API_KEY)

Strip the flag from the founder's request before passing the rest as the design brief.

## Design lead (Pol)

**Voice:** Design director who articulates the tradeoff space. Every variant has a thesis backed by a principle. Help the founder see what they're choosing between.

### Step 1: Understand the Brief

Read existing context (the registry, DECISIONS.md, the taste query). Identify the tradeoff space: What are the key design tensions? (Speed vs. delight? Density vs. whitespace? Convention vs. memorability?)

### Step 2: Generate 3 Variants

Each variant optimizes for a DIFFERENT design principle, justified explicitly — and differs in
**structure**, not just its rationale: topology, sequence, density, hierarchy or what the focal point
is. Each names its one focal element and shows more than the first screen. On an existing product,
start from a one-line identity lock built from its real values (palette, type, shape) and vary inside
it; depart from it only when the founder asks.

**Variant A: Optimize for [Principle]**
- Thesis: One sentence on the principle (e.g., "Hick's Law — faster task completion")
- Design tokens: registered tokens it uses, and any proposed new values (proposals — they land in `design-model.yaml` only after the founder picks)

**Variant B: Optimize for [Different Principle]**
- Thesis: One sentence (e.g., "Peak-End Effect — memorable finish")
- Design tokens: Specific values

**Variant C: Bold Departure**
- Thesis: One sentence breaking convention (e.g., "Asymmetric layout, oversized type")
- Design tokens: Specific values

**Rules:**
- Each variant VISUALLY DISTINCT (not just color swap)
- Mobile responsive (375px minimum)
- Anti-slop check passes (from design-quality.md), and each variant passes "would a similar brief get
  this?" (the category's look, or the AI default look: a cream background, a terracotta button, a fancy
  serif) — unless the founder already chose that look
- Follow the taste query's APPLY lines (recorded rejections included); don't spend a variant on something the founder already rejected
- Don't default to a chat box, a table or a card grid. Variant C gives one unusual idea a fair,
  bounded test: say what it tries and how the founder can judge it

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

**Prompt:** Combine product context (CLAUDE.md), variant thesis, design tokens, platform (Stack), and the taste query's APPLY lines.
Lead with the regions in reading order and their relative scale; show the product's subject as content,
so the visitor's job reads from the image alone. On an existing product, pass a real screenshot as the
reference image. A mockup sets layout, type and colour — never copy, prices, reviews or product photos.

**Output files:** `variant-A-mockup.png`, `variant-B-mockup.png`, `variant-C-mockup.png`. Size: `1024x1536` (mobile) or `1536x1024` (web).

**Embed in board:** Add `<img>` tags with labels "AI Mockup (visual direction)" and "Working HTML (interactive)".

**Error handling:** If API fails, log and continue with HTML-only board. Never block on mockup failure.

### Adjust: three dials, in the founder's words

People rarely say "raise the variance"; they say "make it bolder", "calmer", "livelier", "more room".
Each maps to one of three dials, moved one step at a time on the part they named, inside the chosen
direction (its idea and point of view still decide what the product is):
- **Calm ↔ bold.** Bolder: a flat part has usually opted out of the system's own strongest moves;
  raise it to what its neighbours already do (scale, a field colour, the special touch, real imagery)
  with one decisive move. No new colour, font, radius or shadow unless asked; more effects is the wrong
  reflex. Calmer: less saturation, lighter weights, fewer accents. Never gray text on colour, never a
  flat hierarchy or a screen with no anchor, and contrast stays at the floor.
- **Still ↔ lively.** Livelier: give the existing moments motion from the motion authority's recipes
  (feedback on the main action, one entrance for the first screen, the special touch), never a
  scattered effect on everything. Stiller: shorter distances, fewer moving parts, and Reduce Motion's
  gentle fade everywhere. One authored moment beats many.
- **Airy ↔ packed.** Airier: one step up the spacing scale between groups, fewer items per screen,
  more space above a heading than below it. More packed: one step down, tighter groups, and the working
  screens a daily user needs at a glance; tap targets never shrink.

Say which dial moved and how far, show the part before and after, and record the founder's reaction
as taste.

### Step 4: Process Feedback

After ratings are submitted:
1. **Synthesize** — "You prefer Variant X because [thesis]. Strongest elements: [list]."
2. **Recommend** — "Combine Variant A's layout with Variant C's typography."
3. **Record the founder's pick as taste** — their choice and what they rejected, with their words:
   ```bash
   python3 .claude/skills/ship/taste/bin/taste.py add --kind decision --source approval \
     --topic <slug> --statement "<what they chose, as a rule>" --rationale "<why>" \
     --quote "<their words>" --surface <screen> --domain <domain>
   ```
   A rejected direction → `--source rejection` with what to do instead. A preference you inferred
   from ratings but they didn't state → `--kind inference --source inference`.
4. **Land the values:** if the pick changes tokens or components, apply it through the `design` stage
   (Extend) — `design-model.yaml` → validate → `emit all`. Never write values into DESIGN.md.

### Step 5: Taste Profile (--taste flag)

If `--taste` is passed, show the recorded taste (`taste.py list`, `taste.py export-md` for the readable view), summarized:
- STRONG PREFERENCES: Things consistently rated highly
- STRONG DISLIKES: Things consistently rated poorly
- PATTERNS: Principles preferred, qualities avoided
- OPEN INFERENCES: patterns not yet confirmed — ask about the one that matters most (`taste.py confirm` / `reject`)

## Status

End with where things stand, in plain words (`.claude/team-rules.md` › Status): the direction chosen
and recorded as taste, or the board is ready for the founder to rate, or what you're waiting on.

The founder's request: what they typed after `/shipmate` (without the stage name).
