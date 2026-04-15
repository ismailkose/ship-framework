# Ship Framework — Design Foundation Plan

**Goal:** Make design a first-class foundation in Ship Framework — with the same rigor Vi brings to product scoping and Arc brings to architecture. Build a strong base that works for any project (new or mid-flight), captures taste, eliminates drift, and is easy to extend later.

**Author:** Drafted with Ismael, April 2026.

---

## 1. The Problem

Ship today is **product-first and build-first**. Vi asks product questions. Arc asks engineering questions. `/ship-plan` elaborates features. `/ship-build` writes code. `/ship-review` checks quality after the fact.

Design is assumed, inferred, or pasted mid-conversation — never *elicited*, never *persisted*, never *enforced*.

Concretely, the gaps are:

- **`ship-ux`, `ship-motion`, `ship-components`** exist as routing layers, but they route to nothing project-specific. They'd behave identically in any Ship project.
- **`ship-refgate`** blocks the first edit until "references loaded," but has no opinion about *which* references and no enforcement by dimension (motion vs. layout vs. copy).
- **No convention** for where design truth lives. Every project improvises.
- **No taste extraction ritual**. The designer's eye — the thing that makes output feel right — is never captured.
- **No visual loop during build.** Screenshots happen in QA, after commit. Motion mismatches are only visible at runtime, by which point they're already committed.
- **No drift detection.** Off-system colors, hardcoded spacing, inline animations accumulate invisibly.

**Net effect:** every UI decision is generated fresh each session. References are pasted and forgotten. Taste stays in the designer's head. The skills look powerful but route to empty rooms.

---

## 2. The Thesis

Design should have the same first-class treatment in Ship as product and engineering. That means five things, as a system:

1. **A canonical project-local structure** all design-touching skills read from — the *Project Design Contract* (PDC).
2. **A ritual for extracting taste** and persisting it on disk — `/ship-taste`, producing `TASTE.md`.
3. **Commands to scaffold, audit, and evolve** the design system over a project's life — `/ship-design init`, `audit`, `evolve`.
4. **A visual-first build loop** that defaults to variants-as-previews before any commit — change `ship-build` and `ship-variants` defaults.
5. **Drift as a first-class citizen** — ongoing design lint that flags off-system usage, feeds into `ship-review`.

Order of implementation doesn't matter; the five reinforce each other. But they must exist as a system, not as scattered upgrades.

---

## 2.5 Audit of Existing Ship Commands (before proposing new)

Reading the actual command files for `/ship-design`, `/ship-variants`, and `/ship-html` reveals significant existing coverage. This plan is **revised to upgrade existing commands, not duplicate them**.

### 2.5.1 `/ship-design` — already does a lot

Pol-led 6-phase design system creation. Produces `DESIGN.md` with Foundations (Typography, Color, Spacing, Components, Motion, Layout), Voice & Tone, Do/Don't, SAFE/RISK, and a **Founder Taste** section. Has `--audit` (review existing), `--tokens` (token-only), `--research` (competitor scan), `--mockup` (AI mockup generation). Phase 5 already produces an HTML preview page with tokens as CSS custom properties.

### 2.5.2 `/ship-variants` — already captures taste

Generates 3 theory-backed variants (each optimized for a different UX principle — Hick's Law, Peak-End, etc.), builds `variant-comparison.html` with 5-star ratings + comment fields, saves to `variant-feedback.json`, synthesizes preferences, writes to `LEARNINGS.md` and updates the "Founder Taste" section in `DESIGN.md`. Has `--taste` flag to show current profile, `--refine` to iterate. **This is essentially taste extraction by comparison.** My original `/ship-taste` proposal is ~80% redundant with this.

### 2.5.3 `/ship-html` — already does preview pages

Single-file HTML, production quality, tokens as CSS custom properties, reads DESIGN.md if present, handles dark mode, includes Pol quality check. Any preview page this plan proposes (motion.html, motion-tune.html, unified hub) is built using the `/ship-html` capability, not a new tool.

### 2.5.4 Revised distinction — upgrade vs. net new

**Upgrades to existing commands (not new commands):**
- `/ship-design` should write to split section files (motion.md, components.md, etc.) under a `design/` folder, not one monolithic DESIGN.md. Or: DESIGN.md remains the monolith but sections are addressable and parseable by skills.
- `/ship-design` should write a PDC.md manifest so other skills can introspect what exists.
- `/ship-variants` should add a **motion-dimension** mode (variants differ in motion primitive, not just layout/color) — this is the "motion taste playground" folded into an existing command.
- `/ship-motion` should enforce named primitives with backlinks.
- `ship-refgate` should gate by dimension, not generically.

**Net new (no existing coverage):**
- **PDC.md manifest** (§3.2)
- **Dynamic motion docs with adjustable sliders** (§4.10) — existing `/ship-design` Phase 5 HTML is static; the tuning loop is absent
- **MotionLab.swift native fidelity playground** (§4.10.4)
- **Common Pattern Library** (§4.11) — framework-level, shared across projects
- **Unified Documentation Hub** (new §4.12) — see below
- **Routing & discoverability fix** (new §4.13) — the real adoption gap

Everything else in the original §4 either already exists or is a thin upgrade of what exists.

### 2.5.5 Implication for the plan

Delete mental model of "new commands." Think in terms of:

1. **Commands already exist and mostly work** — they're underused, not underbuilt.
2. **Adoption is the real gap** — users don't know to run them, the router doesn't auto-invoke them. (§4.13)
3. **Output format is the secondary gap** — monolithic DESIGN.md is harder to consume than split files + manifest. (§3)
4. **The dynamic/interactive layer is missing** — static HTML previews exist, live-tuning surfaces don't. (§4.10)
5. **Cross-doc connection is missing** — each command writes its own file in isolation; no unified view. (§4.12)

---

## 3. The Foundation — Project Design Contract (PDC)

Every Ship project should have a small set of canonical design files. This is what all design-touching skills read from.

### 3.1 Initial structure (day one)

```
DESIGN.md       # Monolith (what /ship-design already produces)
TASTE.md        # The designer's eye (separate — different lifecycle, portable across projects)
PDC.md          # Manifest pointing to sections within DESIGN.md
```

Three files at the project root. That's it on day one.

PDC.md points to *sections within* DESIGN.md using anchors (e.g., `DESIGN.md#colors`) — not to separate files. When a section grows large enough that a founder wants to extract it, they run `/ship-design split <section>`, which:

1. Extracts the section from DESIGN.md into `design/<section>.md`
2. Replaces the section in DESIGN.md with a link: `See [motion.md](design/motion.md)`
3. Updates PDC.md to point to the new file instead of the anchor

The `design/` folder and split files emerge organically, not by scaffolding. A mature project *may* evolve into:

```
DESIGN.md              # Summary with links to split sections
TASTE.md               # Designer's eye
PDC.md                 # Manifest pointing to split files
design/
  motion.md            # Split from DESIGN.md when it grew
  components.md        # Split from DESIGN.md when it grew
  references/          # Added when founder imports references
  preview/             # Added when dynamic docs are generated
```

But this is not scaffolded up front — it grows from use.

**Platform contract principle:** Every platform-specific path in the PDC must state the contract ("every platform needs X"), then show examples across stacks. Never hardcode one stack's path as the only option.

| Contract | iOS | Web | Android |
|---|---|---|---|
| Token source | `Theme.swift` | `tokens.ts` / `tailwind.config` | `Theme.kt` |
| Native motion playground | `MotionLab.swift` | `motion-lab.tsx` | `MotionLab.kt` |
| Component preview | `#Preview` blocks | Storybook / HTML | `@Preview` composables |

PDC's `platform` field (auto-detected from CLAUDE.md `Stack:`) determines which paths apply.

**Three-doc audience principle (from Stitch §6.1.1):** the repo root should have `README.md` (for humans), `AGENTS.md` (for coding agents, how to build), and `DESIGN.md` (for design agents, how it should look and feel). Ship assumes `AGENTS.md` exists at repo root — `/ship-design init` offers to scaffold one if missing.

**Export-as-standalone principle (from Stitch §6.1.9):** every file in the design system must be self-sufficient markdown. No Ship-specific macros, no proprietary frontmatter required for a designer with no Ship installed to read and understand the system.

### 3.2 PDC.md — the manifest

A short machine-readable YAML file that tells Ship where design truth lives. Skills check this before doing design work. Intentionally flat — no nested maps, parseable by grep.

**Initial state (anchor-based, pointing into DESIGN.md monolith):**

```yaml
# PDC.md — Project Design Contract
schema_version: 1
platform: <auto-detected from CLAUDE.md Stack>

sections:
  overview:    DESIGN.md#overview
  colors:      DESIGN.md#colors
  typography:  DESIGN.md#typography
  components:  DESIGN.md#components
  donts:       DESIGN.md#dos-and-donts
  # Optional — add with /ship-design add-section or /ship-design split
  # motion:     DESIGN.md#motion
  # copy:       DESIGN.md#voice--tone

taste: TASTE.md   # or "missing" if not yet captured
```

**After organic splitting (what it looks like once sections are extracted):**

```yaml
# PDC.md — Project Design Contract
schema_version: 1
platform: ios

sections:
  overview:    DESIGN.md#overview
  colors:      DESIGN.md#colors
  typography:  DESIGN.md#typography
  components:  design/components.md
  donts:       DESIGN.md#dos-and-donts
  motion:      design/motion.md
  copy:        design/copy.md

taste: TASTE.md
```

Section values are either `<file>#<anchor>` or `<file-path>`. The refgate script handles both. No `status` field in v1 — status tracking (draft/missing/needs-review) is a Phase 2+ concern. In v1, the manifest's job is *where things are*, not *how complete they are*.

### 3.3 Section templates (brief)

Section templates define the skeleton for each design dimension. They are used in two places: (1) as sections within DESIGN.md when `/ship-design` first creates the monolith, and (2) as standalone files when `/ship-design split` extracts a section.

**Sections are optional but ordered (from Stitch §6.1.4).** Not every project needs every section. `/ship-design init` asks which sections apply; missing sections are omitted from the PDC but their *canonical order* is preserved across all Ship projects so reviewers know where to look.

**Lite mode is the default starter (from Stitch §6.1.5).** First-run produces 5 sections within DESIGN.md — Overview, Colors, Typography, Components, Don'ts — matching Stitch's ~20-line canonical example. Founders add sections as they need them via `/ship-design add-section <name>`. Linear's 367-line mature DESIGN.md ships as a reference for founders who want to see what depth looks like.

- **tokens.md** — Nine sections adopted from awesome-design-md (atmosphere, palette with semantic roles, typography, components, layout, depth/shadow, breakpoints, do/don't, agent prompts). Every token references its code source line. **Color naming uses Material roles with `on-*` pairs (from Stitch §6.1.6):** every color used as a background must declare its `on-*` counterpart (e.g., `primary` / `on-primary`, `surface` / `on-surface`). This removes ambiguity about text-on-color. The **Agent Prompt Guide** section is three sub-parts (Quick Color Reference + Example Component Prompts + Iteration Guide as enforceable rules) — the Iteration Guide is the highest-leverage part; see §4.5 for how refgate turns these into hard constraints.
- **motion.md** — 6–10 named primitives. Each has: name, values (Swift/CSS), character (snappy/gentle/etc.), use cases, anti-use cases. Anti-use cases matter most — they prevent drift. *This is Ship's Section 10 extension of the 9-section format — awesome-design-md does not include motion; Ship does, and can upstream the extension.*
- **components.md** — Inventory with states (default/hover/pressed/disabled/loading/error). Each links to the Swift/JSX file and the preview.
- **copy.md** — Voice sliders (formal↔casual, technical↔plain, warm↔neutral), banned words, signature phrasings, empty-state patterns, error patterns.
- **principles.md** — Hard rules ("Orange accent only — no color proliferation"). Each principle has an example of compliance and violation.
- **references/** — Every file or subfolder has a one-liner: what dimension, what to borrow, what *not* to borrow.
- **preview/index.html** — All tokens rendered. Color chips, type specimens, motion demos (CSS/JS approximations for iOS-origin projects), component gallery.

---

## 4. New Capabilities

### 4.1 Taste Extraction Ritual — as `/ship-variants` dimension mode (not a new command)

> **Revised after §2.5 audit.** `/ship-variants` already does variant rating → `variant-feedback.json` → taste synthesis → LEARNINGS.md → DESIGN.md "Founder Taste" update. A separate `/ship-taste` command would duplicate this. Instead: add **dimension flags** to `/ship-variants` — `--motion`, `--layout`, `--type`, `--copy`, `--color` — so variants can be dimension-focused (three motion primitives side-by-side, not three full UI variants). Everything below describes the motion-dimension mode of `/ship-variants`, not a new command.

The key insight: asking "what's your taste?" produces generic answers. Showing examples and asking people to react produces real taste. **Visual experience is nearly impossible to reflect in prose**, so every taste module that can be visual, must be.

**Two modes — ask the user which one:**

When taste extraction starts, ask: *"Two options for capturing your design taste: (1) Quick — ~5 minutes, 10 examples, enough to start building (recommended). (2) Comprehensive — ~30 minutes, 50 examples across all dimensions, produces a high-confidence taste profile. Which do you prefer?"*

#### Quick Taste (~5 minutes)

For founders who want to start building, not spend 30 minutes rating examples.

1. Show 3 reference products (auto-selected from pattern library based on product type). Ask: "Which feels closest to what you want?"
2. For the closest match, show 3 motion examples and 3 color palettes. Rate 1–5 each.
3. Synthesize a minimal TASTE.md with 3–5 preference signals, marked `confidence: low (quick-taste)`.
4. Print: "Quick taste captured. Run `/ship-variants --taste-deep` for the full session when you're ready."

#### Comprehensive Taste (~30–45 minutes)

A structured session across all dimensions. 50 examples total.

1. **Warmup (2 min).** Why we're doing this. Reassurance that taste evolves.
2. **Motion module (8 min).** 10 live animation examples in a browser playground. Rate 1–5, one-word reaction each. Claude surfaces patterns: "you favor quick enter, slow exit" / "you dislike bouncy springs."
3. **Layout module (8 min).** 10 rendered UI screens varying in density, hierarchy, alignment. Same rating pattern.
4. **Typography module (6 min).** 10 type pairings/scales, rendered live.
5. **Copy module (6 min).** 10 microcopy samples varying formality, warmth, verbosity.
6. **Color + atmosphere module (6 min).** 10 palettes rendered as mini-compositions (not flat chips).
7. **Synthesis (5 min).** Claude drafts TASTE.md with `confidence: high (deep-taste)`. User reviews and refines.

#### 4.1.1 The Motion Taste Playground — detailed spec

A **single-file HTML playground** at `design/preview/taste-motion.html`. Self-contained, no hosting, no build. Opens in any browser. This file is generated by `/ship-taste` from a template + pattern library (see §4.11).

**Card anatomy.** Each of the 10 motion examples is one card on the page:

- A trigger element in realistic UI context (a button, a sheet handle, a list row, a toast, a modal backdrop, etc. — not an abstract square)
- Hover or click plays the animation
- A "Replay" button (you'll want to watch twice)
- A 1–5 rating slider + a one-word text field ("why")
- **Underlying values are hidden during rating** — no `response: 0.35` visible. Judging feel, not reading numbers. Values reveal after submission.
- Optional "Compare with A/B" toggle — side-by-side with a contrast variant to sharpen the signal

**The 10 canonical motion categories** (covers the space for iOS + general UI):

1. Sheet enter (modal presentation)
2. Sheet dismiss (drag-to-dismiss release)
3. Button press (scale + timing)
4. List item insertion (single + stagger)
5. Toast / banner appear
6. Pull-to-refresh release
7. Tab switch / container transition
8. Modal backdrop fade
9. Loading breath / shimmer pulse
10. Typing indicator / dots cadence

**Deliberately-bad plants.** Each module seeds 2–3 examples that are obviously off — overbouncy springs, mushy damping, too-slow eases. If the rater *doesn't* filter them out, it's a signal that taste is still forming and TASTE.md should be marked `tentative`. awesome-design-md doesn't do this; it's a genuine addition.

**Output format.** On submission, the playground writes `design/TASTE.md` (motion section) plus a JSON blob like:

```json
{
  "motion_ratings": [
    {"id": "sheet_enter_v1", "rating": 5, "word": "snappy", "values": {"response": 0.32, "damping": 0.88}},
    {"id": "sheet_enter_v2", "rating": 2, "word": "sluggish", "values": {"response": 0.55, "damping": 0.75}}
  ],
  "derived_preferences": {
    "spring_response_preferred_range": [0.28, 0.38],
    "spring_damping_preferred_range": [0.82, 0.92],
    "anti_patterns": ["overbounce", "slow_enter"]
  }
}
```

Claude reads this and writes `motion.md` — named primitives whose values cluster around the preferred ranges.

**Why HTML even for iOS.** Taste is about preference, not implementation. CSS can approximate Swift springs with `cubic-bezier` close enough for taste capture. Once taste is captured, the native-fidelity twin (`MotionLab.swift`, see §4.10.4) becomes the implementation reference. Two artifacts, two jobs: HTML for taste, Swift for build.

#### 4.1.2 Other module playgrounds

- **Layout playground** — `design/preview/taste-layout.html`. 10 rendered cards (each a realistic UI fragment — a list, a settings screen, a dashboard tile), rating slider, same pattern.
- **Typography playground** — `design/preview/taste-type.html`. 10 type specimens showing actual content at real scale.
- **Copy playground** — `design/preview/taste-copy.html`. 10 microcopy samples in UI context (not isolated sentences). Empty states, error states, CTAs.
- **Color playground** — `design/preview/taste-color.html`. 10 mini-compositions (a card + button + text on each palette), not flat swatches.

All follow the same contract: single-file HTML, no build, rate-and-react, emit JSON + TASTE.md draft.

**Rerunnable.** Taste evolves. `/ship-taste --refresh` re-opens the playgrounds with new examples (drawn from the pattern library) and diffs new answers against old, proposing edits to TASTE.md.

**Portable.** TASTE.md lives in the project but can be exported to `~/.ship/taste/<profile>.md` so it follows the designer across projects.

### 4.2 `/ship-design init` — Scaffold

Creates the full `design/` folder. Works on new projects and mid-flight projects.

**Behavior for mid-flight projects:**

- Reads existing code to pre-populate tokens.md (e.g., parses Theme.swift → tokens.md with every Brand.* entry auto-extracted)
- Reads CLAUDE.md for informal design notes → seeds principles.md
- Scans for inline animations → seeds motion.md with current usage, flags un-named primitives
- Generates preview/index.html from what's found
- Marks sections as `auto-extracted, needs-review` in PDC.md

**Behavior for new projects:**

- Asks 5–8 targeted questions (platform, brand starting point, reference projects)
- **Uses the IDEA / THEME / CONTENT / IMAGE 4-slot formula (from Stitch §6.1.7)** as the structured starting prompt:
  - **IDEA** — what it is (one sentence: "A calm, minimal journal app for creative writers")
  - **THEME** — the idea for the core theme ("Warm paper, soft ink, generous spacing, zero chrome")
  - **CONTENT** — what screens or flows matter ("Today's entry, archive by month, prompt-of-the-day")
  - **IMAGE** — optional reference image or URL the founder already likes
- **Includes the "signature choice" question** (lesson from Linear's DESIGN.md): *"What is the one token that, if removed, collapses your system? (A weight? A radius? A spacing multiplier? A motion response? A palette bias?)"* The answer goes into TASTE.md as the north-star constraint and is echoed in PDC.md as `signature_token: <value> — <rationale>`.
- **Asks the palette-bias question** (lesson from Claude's DESIGN.md): *"What colors are forbidden? (cool grays? pure black? any blue?)"* — framed as anti-palette, not palette.
- **Asks which sections apply** (from Stitch §6.1.4 — sections are optional, order is preserved). Defaults to **Lite mode**: Overview, Colors, Typography, Components, Don'ts (5 sections). Founders can add Motion, Elevation, Responsive, Layout, Agent Prompt Guide later via `/ship-design add-section <name>`.
- Scaffolds empty-but-structured templates
- Prompts: "Run `/ship-variants --taste` now, or later?"

**New creation paths (from Stitch §6.1.3 — three paths, Ship was missing one):**

| Flag | Path | Behavior |
|---|---|---|
| *(default, mid-flight)* | Auto-extract from code | Parses Theme.swift → tokens.md; matches Stitch's "Let the agent generate it" |
| *(default, new project)* | Question-driven | 4-slot formula + signature/anti-palette questions; matches Stitch's "Write it by hand" with scaffolding help |
| `--from-brand <url\|image>` | **Derive from branding** | Reads a brand landing-page screenshot or logo image; Claude extracts palette, typography, and style patterns; drafts PDC. Fills Stitch's third creation path. Different from `/ship-design import <brand>` (§4.14), which imports *curated known* brands. `--from-brand` works for *any* brand a founder has a URL or image for. |

### 4.3 `/ship-design audit` — Gap + Drift Report

Runs on demand or as part of `ship-review`. Outputs a structured report:

- **PDC status** — which sections are missing, draft, or stale
- **Undocumented tokens** — tokens in code but not in tokens.md
- **Off-system usage** — hex values not in palette, font families not in type scale, spacing not using tokens
- **Un-named animations** — `.animation(...)` blocks not referencing a motion primitive
- **Outdated claims** — CLAUDE.md assertions that contradict current code (like "system fonts" when custom fonts are used)
- **Reference decay** — references folder with unlabeled items, dead links

Report severity: **block / warn / note**. Only `block`-level issues gate commits.

### 4.4 `/ship-design evolve` — Controlled expansion

For adding a new color, motion primitive, component, or copy pattern. Forces the question: *does this collapse into existing?* If not, requires a one-line justification. Updates PDC.md and the relevant section atomically, plus the preview page.

This is the mechanism that prevents the "20 shades of orange" problem.

### 4.5 Enhanced `ship-refgate` — Dimension-Aware Gating with Hard Block

The current refgate is a binary gate: loaded or not loaded. The upgrade makes it **dimension-aware** and adds a **hard forcing function** for PDC adoption.

#### 4.5.1 Dimension classification

The hook receives JSON on stdin with `{"tool_input": {"file_path": "..."}}`. Classification uses file path heuristics (not content — content parsing would be too slow for a PreToolUse hook):

| Signal | Dimension |
|---|---|
| `*/test*`, `*.test.*`, `*.spec.*` | `none` (no gate) |
| `*animation*`, `*motion*`, `*transition*` | `motion` |
| `*/Localizable*`, `*/i18n/*`, `*/locales/*` | `copy` |
| `*/views/*`, `*/screens/*`, `*/components/*`, `*/UI/*`, `*/pages/*`, `*.css` | `ui` |
| `*/models/*`, `*/services/*`, `*/utils/*`, `*/lib/*` | `logic` (no gate) |
| Default (unknown paths) | `ui` (safe default — worst case: user reads a design doc) |

#### 4.5.2 Gating behavior

1. Dimension is `none` or `logic` → **allow immediately**. No design gate for non-design files.
2. Dimension is `ui`, `motion`, or `copy` → check PDC.md exists:
   - **PDC.md missing → hard block:** `"Design contract missing. Run /ship-design init to create DESIGN.md + PDC.md. Without it, design consistency cannot be enforced."` This is the adoption forcing function — the system degrades visibly without PDC.md, creating natural pressure to set it up. Logic-only edits still work, so a project without PDC.md functions for non-UI work.
   - **PDC.md exists, section missing in manifest → allow** with advisory (no block for undefined sections)
   - **PDC.md exists, section present → check `.claude/.refgate-dim-<dimension>` marker:**
     - Marker exists → allow (section was read this session)
     - Marker missing → **block:** `"This edit touches <dimension>. Read <path> first."`

#### 4.5.3 State files

| File | Purpose |
|---|---|
| `.claude/.refgate-loaded` | Backward compat — framework refs loaded (existing behavior preserved) |
| `.claude/.refgate-dim-ui` | UI design section read this session |
| `.claude/.refgate-dim-motion` | Motion section read this session |
| `.claude/.refgate-dim-copy` | Copy section read this session |

`.refgate-passed` is removed — no single "gate passed" concept. Each dimension has its own lifecycle. Markers are cleaned at session start by `ship-sessionstart`.

When Ship commands read a design section (e.g., `/ship-build` reads the motion section), they create the dimension marker: `touch .claude/.refgate-dim-motion`. This mirrors how `touch .claude/.refgate-loaded` works today.

#### 4.5.4 Iteration Guide enforcement

(Lesson from Linear/Claude DESIGN.md 3-part Agent Prompt Guide.) At session start, refgate loads every *numbered rule* from each PDC section's Iteration Guide into a hard-constraints register. During `ship-review`, any violation of a numbered rule is a **block**, not a warn. Example rules:
  - *"Never use pure black — darkest background is #08090a"*
  - *"Always set `font-feature-settings: 'cv01', 'ss03'` on Inter text"*
  - *"Every `.animation(...)` must reference a named motion primitive by comment"*
  - *"No hover adds a new color — only adds white/black overlay at documented opacity"*

#### 4.5.5 Why this is not brittle

Path-based heuristics are wrong sometimes (a file in `components/` might be pure logic), but the cost of a false positive is *reading a design doc* — never harmful. The cost of a false negative (missing a design-touching edit) is the status quo — no worse than today. Projects can override the path classification in PDC.md with a `path_overrides:` section in a future version.

### 4.6 Enhanced `ship-motion`

- Reads `motion.md` as source of truth
- For any new animation, must either reference an existing primitive by name (a comment like `// motion: gentleEnter`) or propose a new primitive via `/ship-design evolve`
- Hard-blocks raw `.animation(.spring(response: X, damping: Y))` without a named primitive tag

### 4.7 Enhanced `ship-components`

- Reads `components.md`
- For any new UI pattern: check if it exists. If yes, reuse. If no, propose addition via `/ship-design evolve`
- Reports reuse rate in `ship-review`

### 4.8 Preview-First `ship-build` / `ship-variants`

**Default behavior change.** For any UI-touching work:

- Generate 2–3 variants as `#Preview` blocks (SwiftUI) or live HTML previews (web) before committing
- Variants span meaningful states: empty, loading, populated, error, dark mode
- User sees variants in Xcode Canvas or a browser, picks one
- The picked variant becomes the commit; others are discarded

This turns UI work from *writing code with Claude* into *directing Claude*. Rewrite tax drops dramatically, and motion mismatches become visible before commit.

### 4.9 Enhanced `ship-review`

Adds design-specific checks:

- Diff touches UI → runs `/ship-design audit` on the change
- Reports: new off-system tokens, new un-named animations, drift from TASTE.md patterns
- Design-specific issues surface in the same health score as functional issues
- **Always loads `anti-slop.md`** (surfaced from `design-quality.md` Section 2) before *every* review — not just design-specific ones. The same slop detectors that catch AI-generated HTML also catch AI-generated UI components, copy, and layouts everywhere else.
- **Iteration Guide violations are hard blocks** (see §4.5). If a numbered Iteration Guide rule from any PDC file was violated in the diff, the review fails with the specific rule quoted.

### 4.10 Dynamic Motion Documentation

Static `motion.md` is necessary but insufficient. Reading "gentleEnter: response 0.38, damping 0.85" tells you values, not feel. And when a new animation is needed, you don't want to read — you want to **dial**. So motion documentation is a *layered* asset: text for the canon, live preview for the feel, slider-based adjustment for the tuning, native playground for the fidelity.

#### 4.10.1 The four layers

1. **`motion.md`** — canonical text. Named primitives, values, when-to-use, anti-use. The source of truth that version-controls cleanly.
2. **`design/preview/motion.html`** — **dynamic reference preview**. Generated from `motion.md` on demand (or on save). Every primitive renders as a live card. Hover/click plays. Shows the values.
3. **`design/preview/motion-tune.html`** — **adjustment surface**. Same cards as the reference, but with sliders exposed. You can dial `response` and `damping` live and see what happens. Press "save" → writes a diff to `motion.md`. This is what makes the docs *dynamic and adjustable*, not just viewable.
4. **Native fidelity playground** (path is stack-dependent — `MotionLab.swift` for iOS, `motion-lab.tsx` for Web/React, `MotionLab.kt` for Android). A native file where every primitive runs as a real platform animation. Used as an implementation reference by Claude and as a visual QA surface by you.

Critical invariant: **`motion.md` is the single source of truth**. Layers 2, 3, 4 are derived — either generated on the fly or regenerated by `/ship-design rebuild-preview`. If you tune in layer 3 and save, layer 1 updates and layers 2 and 4 regenerate.

#### 4.10.2 What each preview card looks like

One card per primitive. Card elements:

- **Live trigger** — the primitive plays in realistic UI context, not on an abstract box
- **Name** — `gentleEnter`, `snapRelease`, `softLand`, etc.
- **Character tag** — one word: `snappy`, `gentle`, `brisk`, `soft`
- **Use cases** — 2–3 lines: "Sheet enter. Toast appear. Non-urgent confirmations."
- **Anti-use cases** — the dimension most systems skip: "Don't use for button press (too slow). Don't use for error shakes (too smooth)."
- **Values** (visible in reference preview, editable in tune preview)
- **Code snippet** — copy-pasteable Swift/CSS
- **Compare with** — dropdown of other primitives, plays side-by-side
- **Seen in** — backlinks to files in the codebase that currently use this primitive

The backlinks matter. If `gentleEnter` is used in 14 places, changing it is a big deal. The doc surfaces that cost before you tune.

#### 4.10.3 Slider-based adjustment (the "dynamic" part)

In `motion-tune.html`, every primitive card has sliders for its parameters:

- `response` slider (0.1 – 0.8)
- `damping` slider (0.5 – 1.0)
- `duration` slider where relevant
- For custom curves, four bezier handles

Moving a slider:
- Animation re-runs on every slider release
- A small indicator shows "value has changed from canonical" + a reset button
- A "save" button at top writes all pending changes back to `motion.md` as a diff
- Optional: "save as new primitive" — forks into a new named primitive rather than changing the existing one (important when 14 files reference the original)

This is the piece that closes the animation-mismatch loop directly. You feel the mismatch → open the tune preview → dial the exact primitive responsible → save → every file using that primitive updates on next build. No hunting through Swift files.

#### 4.10.4 MotionLab.swift — native fidelity

A permanent SwiftUI file that imports every primitive from `motion.md` (regenerated by `/ship-design rebuild-preview`). Each primitive is a separate `#Preview`. You open it in Xcode, scroll through Canvas, tap each preview, feel the real spring at 60/120fps on actual iOS.

This is the fidelity layer. HTML approximates; native code renders. For any iOS project, this is where you verify that taste captured in HTML translates correctly to Apple's spring physics. For web projects, this is a React/vanilla JS file running real CSS transitions at 60fps.

#### 4.10.5 Keeping layers in sync

A `.pdc-cache/` directory holds the generated artifacts. `motion.md` is watched:

- On save: trigger `/ship-design rebuild-preview` (regenerates HTML + MotionLab.swift)
- On `ship-sessionstart`: verify cache is fresh; rebuild if stale
- In `ship-review`: fail if any file in the codebase uses `.animation(.spring(...))` with raw values not matching any primitive in `motion.md`

No manual sync. Edit the canon, everything downstream updates.

### 4.11 Common Pattern Library

The taste playground in §4.1.1 and the dynamic docs in §4.10 both draw from a **Common Pattern Library** — a framework-level asset shipped with Ship itself (not per project).

#### 4.11.1 Why it's framework-level

Every project re-authoring motion examples from scratch is wasted work. Sheet dismissals, button presses, list insertions — these are *universal UI interactions* with a finite set of tasteful variations. Ship can ship a curated library of these, categorized and ready to drop into taste playgrounds or dynamic docs.

#### 4.11.2 Structure

Lives at `~/.ship/patterns/` or inside the Ship Framework plugin itself (`ship-framework/patterns/`):

```
patterns/
  motion/
    sheet-enter/
      variants.json     # 4 variants with values + character tags
      preview.html      # Renders all variants live
      notes.md          # When each variant fits
    sheet-dismiss/
    button-press/
    list-insertion/
    toast-appear/
    pull-to-refresh/
    tab-switch/
    modal-backdrop/
    loading-breath/
    typing-dots/
  layout/
    list-density/
    card-hierarchy/
    dashboard-tile/
    settings-row/
    empty-state/
    ...
  typography/
    display-body-pairing/
    scale-compact/
    scale-generous/
    ...
  copy/
    empty-state/
    error-message/
    success-confirmation/
    cta-urgent/
    cta-soft/
    ...
  color/
    warm-minimal/
    cool-technical/
    vivid-playful/
    ...
```

Each pattern has:

- `variants.json` — canonical values + character tag for each variant
- `preview.html` — live renderable demo (or `.swift` for native)
- `notes.md` — when-to-use, anti-use, origin/inspiration (acknowledges what taste tradition it draws from — Apple HIG, Material, Linear, Arc, etc.)

#### 4.11.3 How `/ship-taste` uses it

When you run `/ship-taste`, the motion module pulls 10 patterns from `patterns/motion/` (one from each category by default). It selects 2–3 variants per pattern to include, ensuring the 10-card spread exercises the full space of plausible tastes. A seed ensures different sessions get different variant subsets — avoiding test-fatigue on reruns.

#### 4.11.4 How dynamic docs use it

`motion-tune.html` uses the pattern library as the "known space." When you dial sliders outside the canonical ranges, the doc can say: "this is moving away from `Linear-standard` and toward `Apple-HIG-default`." You get educated while tuning.

#### 4.11.5 How projects extend it

A project can add project-local patterns to `design/patterns/` that override or supplement the framework library. Example: A fitness app might have an exercise-specific `breathing-prompt` pattern with its own canonical variants. These live alongside the project's `motion.md` and get picked up automatically.

#### 4.11.6 Community contribution path (later)

Once the pattern schema is stable, a `ship-framework-patterns` community repo can accept PRs. Each pattern is reviewed for: taste quality, anti-use correctness, schema compliance. Not open from day one — curate first, open later.

### 4.12 Unified Documentation Hub (future direction)

Currently, every Ship command writes its own markdown file in isolation. The vision is a single HTML page that indexes and renders every canonical project doc — but this is a Phase 3+ feature that should not block Slices 1–2.

**v1 (static-only):** A static index page built by `/ship-hub` using `/ship-html`. Renders a table of contents linking to each PDC section, TASTE.md, DECISIONS.md, LEARNINGS.md, and key project docs. No live zones, no JS interactivity, no search. Generated on demand.

**v2 (live zones, future):** Add interactive zones one at a time: motion primitives (hover-to-play), color palette (click-to-copy), type specimens. The motion tune surface (§4.10.3) stays standalone at `motion-tune.html` — it works fine as a separate file and doesn't need to be embedded in the hub.

**v3 (full vision, future):** Search, deep-linkable anchors, variant gallery, regeneration buttons, optional `--publish` for team sharing. **No existing design/product tool unifies product + design + engineering + taste + tasks + retros into one interactive hub that's always fresh from source.** That's the long-term unlock.

### 4.13 Routing & Discoverability

You named this directly: `/ship-design`, `/ship-variants`, `/ship-html` exist, but the user may not know to use them, and the router doesn't auto-invoke them often enough. The best commands in the world don't help if they never run. This section addresses the adoption gap explicitly.

#### 4.13.1 Diagnosis — why routing misses design work

`ship-router` triggers on product development phrases broadly. But design work often arrives as: "make this feel nicer," "tweak the animation," "the colors feel off," "this screen is empty." These don't reliably match the router's trigger set for design-specific commands. Even when they do, the router often picks `/ship-build` (the general-purpose command) over `/ship-design` or `/ship-variants`.

Result: design-specific commands are theoretically available but practically invisible.

#### 4.13.2 Upgrades to `ship-router`

Three concrete changes:

1. **Expand design trigger vocabulary.** Add phrases like "make this feel X," "tweak motion," "the timing is off," "colors feel Y," "make this more Z," "this doesn't match the vibe," "inspired by [product]," "I want it to feel like [adjective]." These are the real design asks, not "design a system."
2. **Dimension detection.** Classify the design ask by dimension — motion vs. layout vs. color vs. copy vs. type. Route to the most relevant specialist (ship-variants with `--motion` flag for motion-specific, ship-html for layout prototyping, ship-design --tokens for token changes).
3. **Default to variants-first for UI work.** When a UI change is requested, the router proposes `/ship-variants` first ("let me show you 3 options") rather than jumping to `/ship-build`. The user can always say "just build it" — but the default should be to offer choices.

#### 4.13.3 Proactive surfacing in session

At `ship-sessionstart`, print a small "design moves available" footer when the project has a `design/` folder:

```
Design:
  /ship-design   — create or evolve design system
  /ship-variants — explore options with comparison
  PDC: 5 sections defined
  Taste: captured (confidence: high)
```

Lightweight, non-naggy, but present. Only prints when design files exist. Users learn what's available by seeing it at the top of every session. If DESIGN.md exists but no PDC.md, prints: `Tip: DESIGN.md exists but no PDC.md. Run /ship-design init.`

#### 4.13.4 Metric to track

How often does a design-touching user message result in design-specific-command activation? Measure this. If below a target (say 70%), tune the router triggers. This is the adoption feedback loop.

### 4.14 `/ship-design import <brand>` — borrow structure, not content

Modeled on `npx getdesign@latest add <brand>`. Fetches a DESIGN.md from awesome-design-md (or a local pack under `~/.ship/packs/`), translates it into PDC schema, and writes it into `design/references/imported/<brand>/` — never into the project's own tokens.

**Behavior:**

- `/ship-design import linear` → fetches Linear's DESIGN.md, splits into 9-section + Motion (empty) layout under `design/references/imported/linear/`.
- Adds a `references/imported/linear/README.md` with a one-liner on what to borrow and what to avoid.
- Updates `PDC.md` `references:` array with the import and its intended use (*"borrow typography treatment only, do not adopt palette"*).
- **Translation, not copy.** The file isn't dropped in raw — it's parsed into the PDC's file structure so the agent treats it like any other reference. This is the key difference from getdesign's CLI: we normalize on ingest.

**Why this matters:**

- Turns the 66+ awesome-design-md files into a **composable taste registry** rather than a gallery.
- Lets `ship-review` compare project tokens against imported references and flag divergence: *"you imported Linear's type treatment but your body weight is 400, not 510 — did you mean to drop the signature?"*
- Keeps taste borrowing explicit. A project can say *"typography: per imported/linear/; palette: ours; motion: ours"* — and the PDC records it.

**Later:** `/ship-design export <name>` — dumps the project's PDC as an awesome-design-md-compatible DESIGN.md file. Ship becomes a producer in the ecosystem, not just a consumer.

### 4.15 `/ship-design sync` — keep markdown and tokens honest

Stitch's insight (§6.1.2): DESIGN.md has two faces — a human-readable markdown summary, and structured tokens underneath for enforcement. Edits to either should update both. Ship today has drift: `design/tokens/*.swift` is the real source, PDC prose gets stale.

**What sync does:**
1. Parses `design/DESIGN.md` (and all section files) for tokens stated in prose — hex values, font weights, radii, spacing.
2. Parses `design/tokens/*` code files (Theme.swift, tokens.ts, tokens.kt) for actual values.
3. Reports drift in a three-column table: *Token | Markdown says | Code says | Decision*.
4. For each drift, asks: keep markdown value, keep code value, or pick new? Writes the winner back to both sides.
5. Emits a sync signature to `PDC.md` manifest: `last_sync: <sha> <date>`. `ship-review` refuses to green-light if `last_sync` is older than the most recent commit touching either side.

**Authoring modes supported** (from Stitch §6.1.2):
- **Approximate mode** — founder writes "warm, rounded" in PDC; `/ship-design sync` asks Claude to propose exact tokens, founder approves, writes to code.
- **Exact mode** — founder changes `Theme.swift` directly; `/ship-design sync` updates PDC prose to match.

**Why this exists:** without sync, the PDC becomes aspirational and the code becomes the actual system. With sync, both stay true. The refgate already forces agents to *read* PDC; sync makes sure what they read is current.

---

## 5. The Loops

Three loops at three timescales:

### 5.1 The Learn Loop (project start, ~1 hour)

1. `/ship-design init` → scaffold folder, auto-extract from code
2. `/ship-taste` → produce TASTE.md
3. User adds 3–5 references per dimension with one-line labels
4. `/ship-design audit` → fix any `block`-level gaps
5. `ship-sessionstart` loads PDC into every future session

### 5.2 The Build Loop (daily, per-task)

1. User requests UI work
2. `ship-refgate` verifies relevant PDC sections are read
3. Claude proposes 2–3 variants as previews
4. User picks in < 60 seconds
5. Winning variant is committed with motion/component references tagged
6. If new pattern emerged worth keeping, `/ship-design evolve` promotes it to PDC

### 5.3 The Evolve Loop (weekly/bi-weekly)

1. `/ship-design audit` surfaces drift
2. Intentional additions → `/ship-design evolve`
3. Drift (unintentional) → either corrected in code or formally adopted
4. When taste has shifted, `/ship-taste --refresh`

### 5.4 The Motion Tune Loop (moment-to-moment)

This is the loop that directly addresses the "animations don't match what I expect" pain. It's fast and iterative:

1. You see an animation in the running app that feels off
2. Identify the primitive responsible (the diff or code tags it — e.g., `// motion: gentleEnter`)
3. Open `design/preview/motion-tune.html` in a browser
4. Find `gentleEnter`, dial `response` and `damping` sliders until the feel is right
5. Choose: "save" (updates the primitive, cascades to every user) *or* "save as new primitive" (forks into a new named one, leaves existing untouched)
6. `/ship-design rebuild-preview` regenerates `MotionLab.swift` and the reference HTML
7. Next build, the new feel shows up everywhere

Total loop time: ~2 minutes. Compare to: find the Swift file, guess new values, rebuild app, re-run, repeat. That's ~20 minutes per iteration.

---

## 6. Learning from External Sources — what I actually extracted

This section documents what I pulled from each source, what I almost missed, and what Ship can steal that isn't in the current plan above. I tried to treat these as primary research, not references.

### 6.1 Google Stitch (`stitch.withgoogle.com/docs/design-md/`)

**How I read it:** The docs are a client-rendered SPA behind a cross-origin iframe — WebFetch and JS eval both failed. I got full content via browser-MCP screenshots of four pages: *What is DESIGN.md?*, *The DESIGN.md format*, *View, edit, and export*, and *Everything you need to know to design with Stitch*. Reading the canonical spec firsthand changed what I took away.

**Principle for using Stitch's work:** learn the underlying moves, don't clone the product. Stitch is tuned for Gemini + a hosted SaaS canvas. Ship is tuned for Claude + a code-first framework. The ideas translate; the implementations shouldn't.

#### 6.1.1 The three-document audience model

Stitch's clearest contribution is a triad — one doc per audience:

| File | Audience | Defines |
|---|---|---|
| `README.md` | Humans | What the project is |
| `AGENTS.md` | Coding agents | How to build the project |
| `DESIGN.md` | Design agents | How the project should look and feel |

**Ship gap:** my plan has the PDC folder but no stated relationship to README/AGENTS.md. Ship should adopt this triad explicitly. Action: update §3.1 so `design/DESIGN.md` is positioned as the design peer to `AGENTS.md`, and assume a top-level `AGENTS.md` exists (generate one if not). This makes onboarding legible — a founder sees three files, three jobs.

#### 6.1.2 Dual representation — markdown + structured tokens

The single biggest idea I missed on first pass. Direct quote from the docs: *"A DESIGN.md has two faces. The markdown is what you read and edit, a human-friendly summary. Underneath, Stitch maintains structured tokens, the precise values it uses to enforce consistency during generation."*

Two modes of authoring coexist:
- **Approximate markdown** — "warm colors, rounded feel" → Stitch translates into precise tokens.
- **Exact markdown** — `#2665fd, 8px radius` → Stitch respects literally.

**Ship gap:** my plan treats PDC as markdown-only, with Theme.swift as the "real" code source. Stitch's model is bidirectional — edits to either representation update both. Ship today has one-way flow (Theme.swift → read into context; PDC prose drifts). Action: add new §4.15 command `/ship-design sync` that reconciles `DESIGN.md` prose with `design/tokens/*.swift` (or `.ts`, `.kt`) and flags drift. Markdown stays the humanist layer; tokens stay the enforcement layer; sync is the seam.

This rewrites Open Decision #7 — it's not "DESIGN.md vs code-canonical," it's **both-canonical with a sync contract**.

#### 6.1.3 Three creation paths — Ship is missing one

Stitch names three paths to a DESIGN.md:
1. **Let the agent generate it** — "Describe the vibe." Prompt → full system.
2. **Derive from branding** — "Provide a URL or image." Agent extracts palette, typography, style patterns from existing brand.
3. **Write it by hand** — advanced users author directly.

My plan's `/ship-design init` covers paths 1 and 3 (auto-extract from existing code = a variant of "agent generate"; questions-based = "write by hand"). **Path 2 is absent.** Action: add `/ship-design init --from-brand <url|image>` that reads a brand URL (landing page) or logo image and derives the starting PDC. Composes with §4.14 `/ship-design import <brand>` — import is for *known curated* brands (Linear, Claude); `--from-brand` is for *any* brand a founder already has a URL for.

#### 6.1.4 Sections are omittable, order is preserved

Direct from the format docs: *"Every DESIGN.md follows the same structure. Sections can be omitted if they're not relevant to your project, but the order should be preserved."*

My plan implicitly treats the 9 sections (+ motion = 10) as required. Too heavy for a new project. Action: update §3.3 — all sections optional-by-default but ordered. `/ship-design init` asks "which sections do you need?" and produces only those. A calm productivity app might genuinely not need §6 Depth & Elevation (Linear's file essentially doesn't). A motion-forward app might skip §8 Responsive. **Lite mode** becomes the default starter — Overview, Colors, Typography, Components, Don'ts — five sections, matching Stitch's example. Founders can `/ship-design add-section motion` later.

#### 6.1.5 The minimal example — what "enough" looks like

Stitch's canonical example is strikingly short:

```markdown
# Design System
## Overview
A focused, minimal dark interface for a developer productivity tool.
Clean lines, low visual noise, high information density.
## Colors
- **Primary** (#2665fd): CTAs, active states, key interactive elements
- **Secondary** (#475569): Supporting UI, chips, secondary actions
- **Surface** (#0b1326): Page backgrounds
- **On-surface** (#dae2fd): Primary text on dark backgrounds
- **Error** (#ffb4ab): Validation errors, destructive actions
## Typography
- **Headlines**: Inter, semi-bold
- **Body**: Inter, regular, 14-16px
- **Labels**: Inter, medium, 12px, uppercase for section headers
## Components
- **Buttons**: Rounded (8px), primary uses brand blue fill
- **Inputs**: 1px border, subtle surface-variant background
- **Cards**: No elevation, relies on border and background contrast
## Do's and Don'ts
- Do use the primary color sparingly, only for the most important action
- Don't mix rounded and sharp corners in the same view
- Do maintain 4:1 contrast ratio for all text
```

~20 lines and fully functional. Awesome-design-md expands to hundreds with Motion, Elevation, Responsive, Agent Prompt Guide — right for mature products, overwhelming at init. Action: Ship ships *two* canonical examples — Stitch-minimal (above) as the init output, and Linear-full (367 lines) as the "here's what mature looks like" reference in `design/references/`.

#### 6.1.6 Named colors using Material roles

Stitch generates named colors like `surface`, `on-primary`, `error`, `outline` — Material 3 conventions. The `on-*` pattern (text color that sits *on* a background color) is a small but valuable convention. My plan's §3.3 token format doesn't require `on-*` pairs. Action: update the `tokens.md` section template to require `on-*` for every base color used as a background.

#### 6.1.7 The IDEA / THEME / CONTENT / IMAGE prompt formula

From the walkthrough page, Stitch teaches four slots for initial prompts:

- **IDEA**: What it is ("A landing page for a running podcast named 'The Pacing Project'")
- **THEME**: The idea for the core theme ("Modern, edgy, high contrast. Black and white with hard angles")
- **CONTENT**: The actual content ("Hero section with headline '…' and links to podcast platforms")
- **IMAGE**: Optional reference image

Ready-made schema for **what Ship's `/ship-plan` Phase 1 should ask.** My plan has Phase 1 Context questions but unstructured. Action: adopt the 4-slot IDEA/THEME/CONTENT/IMAGE structure as the explicit prompt scaffold in `/ship-plan` and `/ship-design init`. Short, complete, thirty seconds to fill.

#### 6.1.8 "Make one major change at a time"

Stitch's iteration rule echoes Ship's `/ship-build` scope enforcement verbatim. *"Pick one thing you want to change, just one. Select the Screen you want to change, click Edit, Add to Chat, and write a prompt. Be specific about what to change and how to change it."*

Not new for Ship, but **external validation** that scope atomicity is the correct iteration grain. Worth citing in `/ship-build` docs as industry-shared practice.

#### 6.1.9 Export-as-standalone

*"The exported DESIGN.md is a standalone document. It doesn't depend on Stitch to be useful."*

Ship's PDC must have the same property. A team should hand off `design/` to a designer with no Ship installed and have it make sense. Action: the `PDC.md` manifest and every section file must be self-sufficient markdown — no Ship-specific macros, no proprietary frontmatter required for readability. Make this an explicit design principle in §3.1.

#### 6.1.10 What Ship should *not* copy from Stitch

- Stitch's hosted Design System panel (GUI for editing tokens). Ship is code-first; tokens live in Theme.swift/tokens.ts as source of truth. No GUI.
- Stitch's device-type lock-in (App/Web toggle). Ship's platform detection lives in `ship-sessionstart`, not in PDC.
- Stitch's export-to-HTML pipeline with downstream translators to React/Flutter/SwiftUI. Ship assumes native stacks from day one.
- The "Add to Chat / Edit Theme" canvas metaphor. Ship's iteration surface is the terminal + file diffs, not a visual canvas.
- Stitch's curated 26-font starter list. Worth a nod, but Ship shouldn't prescribe type — founders pick via `/ship-design init` or import from brand.

#### 6.1.11 Concrete plan updates from Stitch (checklist)

| Insight | Plan section to update | New artifact |
|---|---|---|
| Three-doc triad (README/AGENTS/DESIGN) | §3.1 | Position `design/DESIGN.md` as design peer to `AGENTS.md` |
| Dual representation + sync | §4 (new §4.15) | `/ship-design sync` command + Open Decision #7 rewritten |
| "Derive from branding" path missing | §4.2 | `/ship-design init --from-brand <url\|image>` flag |
| Sections optional, order preserved | §3.3 | Lite mode default (5 sections); `/ship-design add-section` |
| Two canonical examples | §3.3 + `design/references/` | Ship Stitch-minimal + Linear-full |
| `on-*` color naming convention | §3.3 tokens template | Require `on-primary`, `on-surface`, etc. |
| IDEA/THEME/CONTENT/IMAGE prompt formula | §4.1 (`/ship-plan`) | 4-slot Phase 1 brief |
| Export-as-standalone principle | §3.1 | Written into PDC design principles |

**Credit in PDC.md manifest:** `format_lineage: google-stitch -> awesome-design-md -> ship-framework`. What Ship takes from Stitch is the *architecture* (triad, dual representation, creation paths, optional sections). What Ship adds is the *enforcement* (refgate, hard-constraint register, agent review loop) and the *code-first stance* (tokens as source, no hosted canvas).

### 6.2 awesome-design-md (VoltAgent, 48.2k⭐)

**How I used it:** Read the README in full. Then went deeper — the getdesign.md gallery (where awesome-design-md files are browsable) is also client-rendered, so I couldn't read files through it. I found the actual bundled files by downloading the `getdesign` npm package (0.6.2) via `curl | tar xz` and reading Linear's and Claude's DESIGN.md from `/tmp/getdesign-extract/package/templates/`. Real content, not a gallery preview.

**The 9-section format** (canonical in every file I read):

1. Visual Theme & Atmosphere
2. Color Palette & Roles
3. Typography Rules
4. Component Stylings
5. Layout Principles
6. Depth & Elevation
7. Do's and Don'ts
8. Responsive Behavior
9. Agent Prompt Guide

**Critical gap I hadn't flagged:** **Motion is not a section.** None of the 66+ curated files include a motion spec. Linear's file mentions transitions briefly inside Component Stylings (e.g., `transition: background 120ms`), but there's no motion section with named primitives, anti-patterns, or stiffness/damping values. This is a real opportunity — Ship already has `ship-motion` as a skill. Adding **Motion as Section 10** to the PDC is a differentiator on the format itself, not just on our process. Ship can publish the extended format and upstream it.

**The Agent Prompt Guide has 3 sub-parts** (I missed this on first read of the README; only spotted it in Linear's file):

1. **Quick Color Reference** — a flat list of hex codes with semantic names (e.g., "Brand Indigo #5e6ad2, Signature Weight 510"). Designed for prompt stuffing.
2. **Example Component Prompts** — actual copy-pastable prompts like *"Create a button with Brand Indigo background, 6px radius, Inter 510 weight, 14px, with the signature semi-transparent white border (rgba(255,255,255,0.08))"*. The DESIGN.md ships the prompts, not just the tokens.
3. **Iteration Guide** — a numbered list of **enforceable rules** (e.g., *"1. Always set font-feature-settings 'cv01', 'ss03' on Inter. 2. Never use pure black #000. 3. Button hover adds 8% white overlay, not a new color."*). These are hard non-negotiables the agent must obey.

**What Ship should do with this:**
- PDC adopts the 9-section format (+ Motion as Section 10), so `/ship-design import linear` works trivially.
- The **Iteration Guide becomes a refgate contract.** `ship-refgate` already blocks first edit until references load; extend it to load Iteration Guide rules into a "hard constraints" register that `ship-review` validates against. This turns written taste into enforced taste.
- Every PDC section ends with a starter prompts block, mirroring the Agent Prompt Guide — not as decoration, as the call-to-action.

### 6.3 Linear's DESIGN.md (read in full — 367 lines)

**Signature moves I extracted:**

- **Inter Variable at weight 510** (not 500 or 600). A custom midpoint weight — only possible with variable fonts. This single choice defines the Linear feel more than any color.
- **-1.584px letter-spacing at 72px** headings. Aggressive negative tracking, proportional to size. Encoded as a formula, not a constant.
- **Semi-transparent white borders on dark:** `rgba(255,255,255,0.05)` default, `0.08` hover, `0.12` active. Never solid borders, never gray. This is a *system-wide* rule, not component-specific.
- **No pure black.** Darkest background is `#08090a`. Listed as an Iteration Guide rule.
- **`font-feature-settings: "cv01", "ss03"`** set globally on body. Without these, Inter looks generic.
- **Motion: almost no section.** The only motion mentioned is `transition: 120ms` on interactive states. Linear's whole design identity comes from typography + border treatment, not motion. Confirms Ship's motion gap insight.

**What the plan should now say:** Linear's file is the strongest example of *one signature choice* (weight 510) carrying the entire identity. Ship's `/ship-design` should push founders to identify *their* signature choice — the one token that if removed, the whole system collapses. Add this to the §4.2 `/ship-design init` Phase 1 Context questions: *"What is the one token that makes this yours? (weight, color, radius, spacing multiplier, motion response)"*

### 6.4 Claude's DESIGN.md (read in full)

**Signature moves:**

- **Parchment as base** (`#f5f4ed`, warm off-white) instead of pure white. Every neutral is warm-biased — no cool grays.
- **Terracotta brand** (`#c96442`) — unusual choice for tech, intentionally anti-Silicon-Valley-blue.
- **Ring shadows, not border-only:** `box-shadow: 0px 0px 0px 1px rgba(...)`. Enables animating the "border" with no layout shift.
- **Single serif weight (500).** Resists the usual serif-regular-plus-bold pattern.
- **Three font families** (Serif / Sans / Mono), each with a specific role — no overlap.
- **No motion section either.** Same format gap as Linear.

**What the plan should now say:** Claude's file shows that **palette bias** (warm-only, cool-only, saturated-only) is itself a taste decision that deserves its own line item in TASTE.md. Not "what colors do you like" but "what colors do you forbid."

### 6.5 The getdesign CLI model (`npx getdesign@latest add <brand>`)

**How I used it:** Downloaded the package. The CLI just copies one of the bundled DESIGN.md files into the user's project. Brilliantly simple — it's a distribution mechanism for taste, not a tool.

**What Ship should do:** A matching `/ship-design import <brand>` command. Behavior:

- Fetches the awesome-design-md file for the chosen brand.
- **Translates** it into the PDC schema (9-section → PDC folders + Motion=empty by default).
- Writes it into `design/references/imported/<brand>/` — never overwrites the project's own tokens.
- The project's DESIGN.md can reference it (*"see references/imported/linear/ for the typography treatment we're borrowing"*) without being contaminated.
- `ship-review` can then compare project tokens against the imported reference and flag *"you imported Linear's type treatment but your body weight is 400, not 510 — did you mean to drop the signature?"*

This is how Ship turns awesome-design-md from a read-only gallery into a **composable taste registry**.

### 6.6 UX / design references (from the credits trail of awesome-design-md)

**What's in Ship's references (already loaded):** `ux-principles.md`, `typography-color.md`, `spatial-design.md`, `layout-responsive.md`, `interaction-design.md`, `design-quality.md`, `navigation.md`, `dark-mode.md`, `forms-feedback.md`, `animation.md`, `components.md`.

**What I didn't fully check that these references should cover (gap scan):**

- **Peak-End rule specifically applied to motion.** `animation.md` covers easing and duration but doesn't explicitly frame motion as an opportunity for the *end* of an interaction. A completion animation is a taste choice, not a filler. Add to `ship-motion`.
- **Fitts's Law applied to touch targets on iOS.** `interaction-design.md` covers hover/focus/active but touch target size rules live separately in the iOS HIG references. Should cross-link.
- **Anti-slop checklist as a first-class file.** `design-quality.md` has a "slop detection" section, but it's buried. Ship should surface an `anti-slop.md` reference that's auto-loaded by every Pol and Eye review — it's the most-used part of design-quality.
- **Copy clarity as a design reference, not just UX writing.** Button labels, empty states, error copy — these are type-set alongside the design system. Should be part of PDC's `copy.md` (already in the schema but worth reinforcing the cross-reference).

**Add to the plan:** §4.9's enhanced `ship-review` should load `anti-slop.md` before *every* review, not just design-specific ones. That's the payoff from taking design references seriously everywhere, not just in design commands.

### 6.7 Summary: what the plan now must absorb

| Source | What's in the plan already | What's been added after deep-dive |
|--------|----------------------------|-----------------------------------|
| Google Stitch | Preview-first build loop | DESIGN.md-as-canonical question (§10), format lineage credit |
| awesome-design-md | 9-section format, Agent prompts | 3-part Agent Prompt Guide (Quick Ref + Prompts + Iteration Guide), Motion as Section 10 (differentiator), `/ship-design import <brand>` |
| Linear DESIGN.md | "Named motion primitives" | Signature-choice question in `/ship-design init`; Iteration Guide → refgate hard constraints |
| Claude DESIGN.md | (not previously covered) | Palette bias as a TASTE.md line item; ring-shadow border pattern |
| getdesign CLI | (not previously covered) | Import command model; references/imported/ isolation |
| UX references | Loaded on command | `anti-slop.md` as always-loaded; Peak-End cross-link into motion |

---

## 7. What Makes This a Moat (Not Parity)

Several design plugins / tools exist. This design foundation differentiates on five axes:

1. **Taste-first, not token-first.** Every other system starts with documenting tokens. Ship starts with documenting the *eye* that chose the tokens. TASTE.md is the differentiator no one else ships.
2. **Visual-in-loop, not visual-after.** Preview variants during build turn design from writing to directing. Most tools generate, you review after.
3. **Drift as first-class.** Audit is ongoing, not a one-time exercise. The system actively fights entropy.
4. **Portable across projects.** TASTE.md follows the designer. A second iOS app inherits the first project's eye. No restart cost.
5. **Additive, not prescriptive.** awesome-design-md content becomes optional reference packs. You can import Linear's motion characteristics as a reference without adopting their tokens.

---

## 8. Extensibility Principles

The foundation must be easy to extend later. Constraints:

1. **Platform-specific layers are additive.** `ship-ios-design`, `ship-web-design`, `ship-android-design` each extend the PDC schema with platform-specific sections (HIG compliance for iOS, Material for Android) without breaking the core schema.
2. **Token-source is flexible.** `tokens.md` is the canonical doc, but token values live where the code lives — `Theme.swift`, CSS vars, Tailwind config. PDC's `token_source` field points to the source, not the other way around.
3. **Taste is portable.** `TASTE.md` can be exported to `~/.ship/taste/<profile>.md` and imported into new projects.
4. **Schema versioning.** `schema_version: 1` lets future upgrades add sections without breaking old projects. Old projects continue working; `/ship-design upgrade` migrates.
5. **Plugin-contributable primitives.** Third-party plugins can contribute motion primitives, component patterns, or reference packs. They land in `design/references/imported/<plugin-name>/` without polluting the project's own.
6. **Minimum viable PDC.** A project can have *only* TASTE.md and still benefit. Sections degrade gracefully.

---

## 9. Roadmap / Phasing

**Phase 0 — Schema & Convention (week 1)**
Define PDC.md schema v1. Document folder structure. Draft section templates. No code yet — just the contract and template files.

**Phase 1 — Scaffolding (week 2)**
`/ship-design init` command. Pre-populates tokens.md from code. Scaffolds empty templates. Produces first preview/index.html.

**Phase 2 — Audit (week 2–3)**
`/ship-design audit` command. Drift detector. Three-severity report.

**Phase 3 — Taste Extraction + Pattern Library seed (week 3–4)**
`/ship-taste` command. Curated example decks for each module. Synthesis to TASTE.md. Dogfooded on the author's first project first. Phase 3 also seeds the initial Common Pattern Library (§4.11) — starts with motion-only (10 categories, 3–4 variants each, ~40 total) because motion is the highest-pain dimension. Layout/type/copy/color patterns added in Phase 7.

**Phase 4 — Refgate + Motion + Components upgrades (week 4–5)**
`ship-refgate` reads PDC and gates by dimension. `ship-motion` enforces named primitives. `ship-components` enforces reuse.

**Phase 5 — Preview-First Build + Dynamic Motion Docs (week 5–6)**
`ship-build` and `ship-variants` default to variants-as-previews. Works for SwiftUI and React/HTML. Dynamic motion documentation (§4.10) ships here: `motion.html`, `motion-tune.html` with live sliders, `MotionLab.swift` generator, `/ship-design rebuild-preview` command. The Motion Tune Loop (§5.4) becomes real in this phase.

**Phase 6 — Review Integration (week 6–7)**
`ship-review` incorporates design drift into health score. `/ship-design evolve` for intentional expansion.

**Phase 7 — External Reference Packs + Pattern Library expansion (ongoing)**
Import awesome-design-md content as optional reference packs. Add a `/ship-design import` command to pull a named pack into `references/imported/`. Expand the Common Pattern Library to layout/type/copy/color dimensions (§4.11). Optionally open pattern library to community contribution once schema is stable.

Phases 0–6 are ~6–7 weeks of focused work; each phase is independently shippable. Phases can also parallelize — e.g., Phase 3 (taste) and Phase 5 (preview) don't depend on each other.

---

## 10. Decisions

### Resolved

1. **Is `TASTE.md` private or shared?** **Decided: committed by default.** Teams benefit from shared taste. Personal overlay at `~/.ship/taste/personal.md` for individual preferences on top.
2. **Do we dogfood first or design abstractly?** **Decided: dogfood.** Build on a real project; what works there generalizes.
3. **How visual are taste-extraction examples?** **Decided: HTML playgrounds.** Self-contained single-file HTML, no hosting. Text is too weak, video too heavy.
4. **Does drift detection block commits or just report?** **Decided: report for style, block for structural.** *note/warn* for stylistic drift. *block* only when PDC is missing or a core principle is violated. Never block for subjective drift — that's a velocity killer.
6. **Reference packs — first-party or community?** **Decided: first-party first.** A few curated packs from awesome-design-md content. Community opens later once schema is stable.
7. **Is DESIGN.md/PDC canonical, or is code canonical?** **Decided: both-canonical with a sync contract (§6.1.2, §4.15).** PDC prose is the humanist layer, code tokens are the enforcement layer, `/ship-design sync` is the seam.

### Still Open

5. **Cross-project taste — one `~/.ship/taste/default.md` for all projects, or per-project only?** Leaning: both. Personal taste at `~/.ship/taste/`, project-specific at `TASTE.md`, project overrides personal. Needs real usage to validate.
8. **Do we upstream the Motion = Section 10 extension to awesome-design-md?** Leaning: yes — after Phase 3, submit a well-documented PR. Needs the format to stabilize first.

---

## 11. Success Criteria

How to know this worked:

- **Before:** user feels "design references don't impact output." Animation mismatches are discovered post-build. Each session is a cold start on design.
- **After:** Claude refuses to start UI work before reading PDC. Animations always reference named primitives. UI work produces 2–3 previews the user picks from in under a minute. TASTE.md exists on disk and survives sessions. Drift is visible and manageable, not invisible and compounding.

Concrete measurable signals:

- Rewrite-after-commit rate on UI changes drops (tracked via git)
- % of animations using named motion primitives rises to ≥ 90%
- % of colors/fonts/spacing referencing tokens rises to ≥ 95%
- Time-to-first-commit on a new UI task drops (preview round-trip replaces iterate-in-simulator loop)
- Designer qualitative: "the output now feels like my eye on the first try"

---

## 12. What I'd Build First (revised after audit + review)

Given §2.5 — most "new commands" aren't needed. The minimum viable slice is smaller and more leveraged than originally scoped. Three files on day one (DESIGN.md monolith + TASTE.md + PDC.md), not eight.

**Slice 1 — PDC manifest + dimension-aware refgate + routing fix (~3–4 days)**

Five existing files to modify. No new files created — all changes are upgrades to Ship Framework plugin files.

| # | What | File | Change |
|---|---|---|---|
| 1 | Dimension-aware refgate script | `template/.claude/skills/ship/refgate/bin/check-refgate.sh` | Replace binary gate with dimension classifier → PDC check → per-dimension markers. Hard-block when PDC.md missing and edit touches UI. |
| 2 | Refgate skill docs | `template/.claude/skills/ship/refgate/SKILL.md` | Update description, state file table, "How It Works" to reflect dimension model. |
| 3 | Session start footer + cleanup | `template/.claude/skills/ship/sessionstart/bin/session-start.sh` | Clean `.refgate-dim-*` markers. Add design footer when DESIGN.md/PDC.md exists. |
| 4 | Router trigger expansion | `template/.claude/commands/ship-team.md` | Add design-feel vocabulary: "make this feel X", "timing is off", "colors feel Y" → route to design commands, not /ship-build. |
| 5 | PDC generation + init flag | `template/.claude/commands/ship-design.md` | Phase 6 also generates PDC.md from DESIGN.md headings. Add `--init` flag and `split <section>` sub-command. |

**Implementation order:** 1+2+3 in parallel → 5 (after PDC format settles) → 4 (independent).

**Value:** Discoverability and introspection without creating a single new command. The hard-block forcing function creates real adoption pressure for PDC.md.

**Slice 2 — Design preview (~4–5 days)**

`/ship-design --preview` generates two preview layers from DESIGN.md — one cross-platform, one native-fidelity:

6. **HTML preview** — `design/preview/index.html`. Single-file, no build. Covers all dimensions: color swatches, typography specimens, spacing scale, border radius, component examples, and CSS-approximated motion demos. If preview exists, opens it. If not, creates it first. Offered at end of `/ship-design init` and `/ship-design --audit`. Shown in session footer when present.
7. **Native preview** (platform-specific) — one consolidated file per stack:
   - iOS: `DesignPreview.swift` with `#Preview` sections:
     - `#Preview("Colors")` — all palette tokens as swatches
     - `#Preview("Typography")` — type scale with real fonts at real sizes
     - `#Preview("Spacing")` — spacing scale visualized
     - `#Preview("Components")` — key components in all states
     - `#Preview("Motion")` — every named primitive, tap to play real springs
   - Web: `design-preview.tsx` with equivalent sections
   - Android: `DesignPreview.kt` with `@Preview` composables
   One file, one place to scroll through. Not separate files per dimension.
8. **Motion tune surface** — `design/preview/motion-tune.html` with live sliders that write back to `motion.md` (or DESIGN.md#motion). This is the interactive tuning layer on top of the read-only previews.
9. Enforce named-primitive tagging in `ship-motion` skill (hard-block raw springs without a tag).

Session footer shows both layers: `Preview: design/preview/index.html | Xcode: DesignPreview.swift`

HTML preview is the approximation for reviewing the *system*. Native preview is the fidelity layer for reviewing the *feel*. Motion tune is the adjustment layer for changing values live.

**Slice 3 — Taste extraction + pattern library seed (~3–4 days)**

11. Taste extraction in `/ship-variants --taste` — asks user to choose Quick (~5 min, recommended) or Comprehensive (~30 min).
12. Comprehensive mode: 50 examples across all dimensions (motion, layout, type, copy, color).
13. Seed Common Pattern Library with motion-only (10 categories, 3–4 variants each, ~40 total).
14. TASTE.md generation with confidence marker.

**Open — needs iteration:**

- **Preview quality (Slice 2 follow-up):** HTML preview generates but output quality needs work. Spec is written (world-class layout, 10 sections, sidebar nav, Tailwind/Radix quality bar) but Claude's output doesn't match the spec yet. Native `DesignPreview.swift` generation also needs dogfooding — wasn't generated in first test (Stack field was missing). Iterate until preview output matches the spec.
- **Fix broken Ship hooks:** Freeze, careful, and guard hooks all have the old `permissionDecision` format (silently ignored by Claude Code) and aren't registered in settings.json. Need `hookSpecificOutput` wrapper + settings.json registration.

**Deferred (Phase 2+):**

- Unified Documentation Hub — static v1 only (§4.12)
- `/ship-design sync` — both-canonical enforcement (§4.15)
- `/ship-design import <brand>` — awesome-design-md composable registry (§4.14)
- Community pattern library contribution
- Dimension expansion beyond motion (layout-tune, color-tune, type-tune)

**Why this order**

Slice 1 fixes discoverability (adoption problem) and adds the forcing function before adding features. No point shipping new capabilities nobody triggers.

Slice 2 directly addresses animation mismatch pain. Highest leverage single slice.

Slice 3 captures taste — the differentiator no one else ships. Pattern library seeds the examples needed for taste extraction.

Total MVP: ~2 weeks for all three slices, dogfooded on the author's first project. Each slice is independently shippable.

---

## Next Steps

1. Build Slice 1: modify the five files listed above.
2. Dogfood Slice 1 on a real project (see below).
3. Iterate Slice 1 based on dogfood findings.
4. Build Slices 2 and 3.

### What dogfooding means here

Dogfooding is not testing that the code runs — it's testing that the **workflow** works. Take a real project that already has UI code, run `/ship-design init` on it, and then do a normal UI task ("tweak the button animation", "adjust the color palette"). The dogfood test answers these questions:

- **Did refgate fire on the right dimension?** Edit a file in `views/` — did it block for UI? Edit a file in `models/` — did it allow without a design gate?
- **Did the router pick the right command?** Say "make this feel smoother" — did it route to `/ship-variants`, or did it fall through to `/ship-build`?
- **Did the session footer help?** At session start, did the design tools footer surface what was available? Was it useful or noise?
- **Was PDC.md useful to the skills that read it?** When refgate blocked and pointed to a section, was the section content actually helpful for the task at hand?
- **Was the monolith + anchor approach sufficient?** Or did you immediately want split files? If so, when and why?
- **What was the forcing function experience?** When PDC.md didn't exist and refgate blocked, was the message clear? Was running `/ship-design init` fast enough that the block felt like a 2-minute setup, not a 20-minute obstacle?

The point is to surface whether the architecture holds before investing in Slices 2 and 3. If the dimension classifier is too coarse, or the PDC manifest format needs fields we didn't anticipate, or the router triggers produce false positives — those are cheaper to fix now than after building motion docs and taste extraction on top.
