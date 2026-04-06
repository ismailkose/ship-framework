# Ship Framework Evolution Plan

> GStack competitive analysis → actionable roadmap for Ship v2026.04
> Each section: what exists today, what we're adding, why, and how it fits Ship's architecture.

---

## 1. `/ship-think` (NEW) — Pre-Planning Idea Validation

### What exists today
Ship jumps straight to `/ship-plan` which assumes the idea is worth building. Vi asks one clarifying question max and runs four forcing questions, but these are inside the planning flow — by the time you're in `/ship-plan`, you're already committed to building something.

### What GStack does
`/office-hours` is a separate pre-planning stage — YC-style mentorship that challenges your idea before any planning begins. Six forcing questions designed to kill bad ideas early:
- Demand reality — is there a real human with real pain?
- Status quo — what's broken today?
- Desperate specificity — concrete examples, not vague aspirations
- Narrowest wedge — smallest defensible initial market
- Observation & surprise — unexpected insight from research
- Future-fit — will this remain relevant?

Two modes: startup mode (interrogative, validates market demand) and builder mode (generative design thinking for side projects).

### What Ship adds
**`/ship-think`** — a standalone idea validation command that runs BEFORE `/ship-plan`.

**Personas involved:** Vi (Product Strategist) in interrogation mode.

**Workflow:**
1. **Context Gathering** — What are you trying to build? Who is it for? Why now?
2. **Six Forcing Questions** — Adapted for designer-builders:
   - **Real Pain Test** — Can you name a specific person who has this problem today?
   - **Status Quo Test** — What do they currently do? Why is that broken?
   - **Specificity Test** — Describe the exact moment the user feels the pain.
   - **Narrowest Wedge** — What's the smallest version that solves the core pain?
   - **Surprise Test** — What did you learn from users/research that surprised you?
   - **Taste Test** (Ship-unique) — What does the 10/10 version feel like? What's the aesthetic vision?
3. **Verdict:**
   - `VALIDATED` — Proceed to `/ship-plan`
   - `PIVOT_SUGGESTED` — The core idea has potential but the framing needs work. Here's an alternative angle.
   - `PAUSE` — The problem isn't clear enough. Go talk to 3 users first.
4. **Scope Modes** (borrowed from GStack's plan-ceo-review, integrated here):
   - `--dream` — 10-star version, expand scope to find the magical version
   - `--focus` — Hold scope, execute exactly what's described
   - `--strip` — Minimum viable, fastest path to validation
   - Default: Vi picks the right mode based on the idea maturity

**Output:** Idea brief saved to `DECISIONS.md` as the first entry. Includes: problem statement, target user, scope mode, aesthetic direction seed, and Vi's verdict.

**How it connects:** `/ship-think` → feeds into → `/ship-plan` (Vi reads the idea brief and skips re-asking what to build).

---

## 2. `/ship-plan` (IMPROVED) — Planning with Scope Modes

### What exists today
Vi (product brief) → Arc (technical plan) → Adversarial (stress test). Strong 3-way debate. Four forcing questions, experience walk-through, technical architecture, RICE scoring.

### What we improve
1. **Scope mode inheritance** — If `/ship-think` was run, inherit the scope mode (dream/focus/strip). If not, ask.
2. **Vi reads `/ship-think` output** — No redundant questioning. Vi refines the validated idea, doesn't restart from scratch.
3. **Pre-implementation design scoring** (adapted from GStack's plan-design-review dimensions):

   After Arc's technical plan, before the Adversarial stress test, Pol (Design Director) scores the plan across 7 dimensions (0-10):
   - Information Architecture — content/feature organization clarity
   - Interaction State Coverage — all user states planned (empty, loading, error, success, edge)
   - User Journey & Emotional Arc — does the flow feel complete?
   - AI Slop Risk — are there generic, low-effort patterns in the plan?
   - Design System Alignment — does it fit existing patterns?
   - Responsive & Accessibility — mobile-first, inclusive design planned?
   - Unresolved Design Decisions — are there taste calls that need founder input?

   For each dimension below 8, Pol shows what 10/10 looks like using Ship's references (ux-principles.md, interaction-design.md, etc.). Plan doesn't graduate until all dimensions are ≥7.

4. **Search-before-recommending** — Arc checks that recommended patterns are current for the declared stack version before including them in the plan.

**Flags (updated):**
- No flag = Full run (Think check + Vi + Pol score + Arc + Adversarial)
- `vi-only` = Early brainstorming
- `arc-only` = Quick technical plan
- `pol-only` = Design dimension scoring only
- `with-monetization` = Add Biz voice

---

## 3. Consolidating Review + QA → Streamlined Quality Pipeline

### The problem today
Three overlapping commands confuse the workflow:
- `/ship-review` — Crit (product) + Pol (design) + Eye (visual) + Adversarial
- `/ship-qa` — Test (QA tester) with health score
- `/ship-browse` — Eye only (visual QA)

A user doesn't know when to run review vs qa vs browse. There's overlap between Crit checking UX and Test checking user flows.

### The consolidation

**Keep three commands but clarify their roles completely:**

#### `/ship-review` (IMPROVED) — The Quality Gate
**When:** After building, before shipping. This is the main quality command.

**Default run (no flags):** ALL quality checks in one pass:
1. **Crit** — Product quality (HEART dimensions, UX principles)
2. **Pol** — Design craft (anti-slop, typography, color, spacing)
3. **Eye** — Visual QA (screenshots, pixel-level checking)
4. **Test** — Automated tests + manual exploration (health score)
5. **Adversarial** — Challenge all of the above

This merges what was previously `/ship-review` + `/ship-qa` into one command. No more wondering which to run — you run `/ship-review` and get everything.

**New behavior — "search before recommending":**
Crit and Pol verify that suggested patterns/fixes are current best practice for the declared stack version before recommending them. No deprecated API suggestions.

**Flags for partial runs:**
- `--product` = Crit only (HEART dimensions, UX)
- `--design` = Pol only (design craft audit)
- `--visual` = Eye only (screenshots, same as current /ship-browse)
- `--test` = Test only (automated + manual testing, health score)
- `--report` = Full run but report-only, no fixes (this covers the qa-only use case)
- `--fix` = Full run + auto-fix obvious issues (current default behavior)

**Health Score (integrated from /ship-qa):**
Every `/ship-review` run produces a health score (0-100) combining all reviewer findings.
- 90-100: Ship it
- 70-89: Fix criticals first
- 50-69: Needs work
- Below 50: Don't ship

#### `/ship-browse` (ENHANCED) — Visual QA + Browser Power
**When:** Quick visual check, or when you need browser capabilities.

**Current:** Eye persona takes screenshots and checks design.

**Enhanced with:**
1. **Persistent browser daemon** — Keep browser session alive across commands (~100ms per action instead of cold start each time)
2. **Cookie/session import** — Import auth sessions from user's real browser so Eye can test authenticated pages without manual login
   - Auto-detect installed browsers (Chrome, Arc, Brave, Edge, Safari)
   - Import cookies for specified domains
   - Persist sessions across QA runs
3. **Headed mode option** — `--watch` flag opens a visible browser window so you can watch Eye navigate in real time. Useful for debugging visual issues together.
4. **Performance snapshot** — After visual QA, capture Core Web Vitals (LCP, CLS, INP) as part of the report. Eye already visits every page — measuring performance adds zero extra navigation.

**Flags:**
- No flag = Headless visual QA (current behavior, enhanced)
- `--watch` = Headed mode, visible browser
- `--auth` = Import cookies from real browser first
- `--perf` = Include performance metrics in report

#### `/ship-qa` → DEPRECATED (merged into `/ship-review --test`)
The Test persona and health scoring system move into `/ship-review`. Running `/ship-qa` shows a deprecation notice pointing to `/ship-review --test` or just `/ship-review` for the full suite.

### Why this is better
- **One command for quality** — `/ship-review` does everything. No confusion.
- **Flags for partial runs** — When you only need design or only need tests, use a flag.
- **Browse stays focused** — `/ship-browse` is specifically for visual/browser capabilities.
- **QA-only mode** via `--report` flag instead of a separate command.
- **Health score everywhere** — Every review produces a number, not just QA.

---

## 4. `/ship-fix` (IMPROVED) — Structured Hypothesis Framework

### What exists today
Bug persona with scope lock, investigation, pattern matching, hypothesis, fix & verify, debug report. Already has the "Iron Law: no fixes without root cause investigation first" and a 3-strike limit.

### What we improve
Ship-fix already has the 3-strike escalation! After reviewing the actual code, the hypothesis testing framework is largely there. The improvements:

1. **Search before guessing** — Before forming a hypothesis, search for the exact error message in framework issues and known bugs. Check if it's a known issue with a known fix. This prevents reinventing solutions that already exist.

2. **Pattern database** — After each successful fix, write the bug pattern to `LEARNINGS.md`:
   ```
   ## Bug Pattern: [category]
   - Symptom: [what the user saw]
   - Root cause: [what was actually wrong]
   - Fix pattern: [how to fix this class of bug]
   - Date: [when discovered]
   ```
   Before investigating new bugs, check `LEARNINGS.md` for matching patterns. The team gets smarter over time.

3. **Architecture questioning at strike 3** — Currently Ship says "escalate after 3 rejections." Make this more explicit: after 3 failed hypotheses, Bug persona must stop and write a brief architectural assessment. Is the bug a symptom of a deeper structural problem? Present two paths: tactical fix vs. structural refactor. Founder decides.

4. **Blast radius visualization** — Instead of just counting files (1-3, 4-5, 6+), show a simple dependency tree of affected files so the founder can see the actual impact.

---

## 5. `/ship-design` (NEW) — Design System Creation & Consultation

### What GStack does
`/design-consultation` runs a 6-phase workflow: context → competitor research → complete system proposal (with SAFE/RISK breakdown) → drill-downs → preview mockups → DESIGN.md documentation.

### What Ship adds
**`/ship-design`** — Create or evolve a design system, informed by Ship's deep references.

**Personas involved:** Pol (Design Director) + Eye (Visual QA for previews)

**Workflow:**
1. **Context Phase** — Pol asks about:
   - Product type (SaaS, mobile app, marketing site, tool)
   - Target audience and their expectations
   - Existing brand assets (colors, logo, fonts)
   - Emotional keywords (3-5 words: minimal, bold, warm, precise, etc.)
   - Reference products the founder admires

2. **Research Phase** — Pol + Eye research competitors:
   - Screenshot competitor products (via ship-browse capabilities)
   - Extract their design patterns: navigation, typography scale, color usage, spacing rhythm, component patterns
   - Reference Ship's `design-research.md` for structured extraction methodology
   - Identify industry conventions (SAFE) vs. differentiation opportunities (RISK)

3. **System Proposal** — Pol proposes a complete design system:
   - **Typography scale** — Using rules from `typography-color.md` (16px base, fluid scale, font pairing logic)
   - **Color tokens** — Semantic tokens (not raw hex), dark mode variants, contrast-verified per `typography-color.md`
   - **Spacing scale** — Based on `spatial-design.md` (4px/8px base unit, density strategy)
   - **Component patterns** — Mapped to `components.md` catalog (which of the 46 components apply)
   - **Motion system** — Based on `animation.md` (motion budget, easing curves, foundational patterns)
   - **Layout grid** — Based on `layout-responsive.md` (breakpoints, mobile-first, content priority)
   - **SAFE/RISK breakdown** — For each category, what's conventional vs. what's a deliberate departure that creates distinctive character

4. **Drill-down Phase** — Founder picks sections to refine. Pol presents alternatives with rationale grounded in references.

5. **Preview Phase** — Generate visual preview:
   - HTML preview page showing the system applied to realistic screens (signup, dashboard, settings, empty state)
   - If GPT Image API or similar is available: generate high-fidelity mockups
   - Eye validates the preview against design quality references

6. **Documentation** — Write `DESIGN.md` as the authoritative design system file:
   - Token values (CSS custom properties)
   - Component usage rules
   - Do/Don't examples
   - Platform-specific notes (if iOS: HIG alignment, if web: responsive breakpoints)

**Flags:**
- No flag = Full 6-phase consultation
- `--audit` = Audit existing design system against Ship references
- `--tokens` = Generate/update token file only
- `--research` = Competitor research phase only

**How it connects:** `/ship-design` creates `DESIGN.md` → `/ship-plan` references it for aesthetic direction → `/ship-build` uses it for implementation → `/ship-review` Pol validates against it.

---

## 6. `/ship-variants` (NEW) — Theory-Backed Design Variant Generation

### What GStack does
`/design-shotgun` generates 3 design variants in parallel using GPT Image API, serves them on a localhost HTML comparison board with star ratings and feedback capture, learns taste preferences over time.

### What Ship adds — and why it's better
GStack generates random visual variants. Ship generates **theory-backed variants** where each option is justified against design references.

**Personas involved:** Pol (Design Director) + Eye (Visual QA for rendering)

**Workflow:**
1. **Input** — Describe the screen/component/page to explore. Pol reads relevant references.

2. **Variant Generation** — Pol creates 3 distinct design directions, each with theoretical justification:
   - **Variant A: Optimize for [Principle X]** — e.g., "Optimizes for Hick's Law: fewer choices, larger targets, fastest task completion"
   - **Variant B: Optimize for [Principle Y]** — e.g., "Optimizes for emotional engagement: richer visuals, progressive disclosure, delight moments"
   - **Variant C: Bold departure** — e.g., "Breaks convention deliberately: unconventional layout that creates memorability (RISK move)"

   Each variant includes:
   - Which UX principle/reference it prioritizes
   - What it sacrifices (every design is a tradeoff)
   - Who it's best for (user type/scenario)

3. **Comparison Board** — Generate a self-contained HTML page:
   - Three columns showing each variant rendered as working HTML
   - Star rating (1-5) for each
   - Comment field per variant
   - "What matters most?" selector (speed, delight, memorability, accessibility)
   - Submit button → saves structured feedback to `variant-feedback.json`

4. **Feedback Loop** — Pol reads the feedback file and:
   - Synthesizes a recommended direction combining best elements
   - Updates `DESIGN.md` preference section with learned taste signals
   - Over multiple rounds, builds a taste profile: "Founder prefers minimal layouts, dislikes gradients, values whitespace over density"

5. **Taste Memory** — Preferences persist in `DESIGN.md` under a `## Founder Taste` section. Future variant generations and design reviews reference this. The team learns your aesthetic.

**Flags:**
- No flag = 3 variants + comparison board
- `--quick` = 2 variants, no comparison board, just show in terminal
- `--refine` = Take existing variant feedback and generate refined options
- `--taste` = Show current taste profile from DESIGN.md

**How it connects:** `/ship-variants` → informs → `DESIGN.md` taste section → `/ship-review` Pol references taste when evaluating design quality.

---

## 7. `/ship-perf` (NEW) — Performance Measurement & Benchmarking

### What GStack does
`/benchmark` uses real Chromium to measure LCP, CLS, INP, load time, resource counts, transfer size. Multiple runs averaged. Results persist for before/after comparison.

### What Ship adds
**`/ship-perf`** — Measure performance against the standards already defined in Ship's `web-performance.md` reference.

**Personas involved:** Eye (Visual QA, already has browser access) + Test (for test generation)

**Workflow:**
1. **Baseline Capture** — Eye navigates to each page of the app using browser daemon:
   - Core Web Vitals: LCP, CLS, INP
   - Load time (DOMContentLoaded, full load)
   - Resource count and total transfer size
   - JavaScript bundle size
   - Image optimization status (format, compression, lazy loading)
   - 3 runs per page, averaged for accuracy

2. **Reference Comparison** — Compare against Ship's `web-performance.md` targets:
   - LCP < 2.5s (good), < 4s (needs improvement), > 4s (poor)
   - CLS < 0.1 (good), < 0.25 (needs improvement), > 0.25 (poor)
   - INP < 200ms (good), < 500ms (needs improvement), > 500ms (poor)
   - Flag anti-patterns from the reference (layout thrashing, unoptimized images, render-blocking resources)

3. **Performance Report** — Saved to `PERF-REPORT.md`:
   - Per-page metrics table with pass/warn/fail indicators
   - Overall performance score (0-100)
   - Top 5 improvement opportunities ranked by impact
   - Specific code changes recommended (lazy load this image, code-split this route, etc.)

4. **Before/After Mode** — If a previous report exists:
   - Compare current vs. previous
   - Highlight regressions in red
   - Highlight improvements in green
   - Delta for each metric

5. **Performance Tests** — Test persona writes performance regression tests:
   - Lighthouse CI assertions for CI/CD
   - Bundle size limits
   - Image size limits

**Flags:**
- No flag = Full benchmark + report
- `--quick` = Single run, summary only
- `--compare` = Before/after comparison with previous report
- `--ci` = Generate performance test assertions for CI

**Platform note:** Web only for now. iOS performance measurement requires Xcode Instruments integration (future consideration).

**How it connects:** `/ship-perf` uses knowledge from `web-performance.md` → results feed into `/ship-review` → Eye includes perf snapshot in visual QA.

---

## 8. `/ship-html` (NEW) — Production-Quality HTML Prototyping

### What GStack does
`/design-html` uses Pretext (15KB library by Cheng Lou) for responsive HTML where text reflows naturally on resize instead of breaking at hardcoded heights. Solves the problem where AI-generated HTML looks right at one viewport but breaks at others.

### What Ship adds
**`/ship-html`** — Generate production-quality responsive HTML prototypes before committing to a framework.

**Personas involved:** Dev (Builder) + Pol (Design Director for quality)

**When to use:**
- Prototyping a design before building in React/SwiftUI
- Creating a marketing page or landing page
- Building a static site that doesn't need a framework
- Testing a layout idea quickly

**Workflow:**
1. **Input** — Describe the page/component. If `DESIGN.md` exists, Dev reads it for tokens.

2. **Build** — Dev generates single-file HTML with:
   - Semantic HTML structure
   - CSS using design tokens from `DESIGN.md` (or sensible defaults)
   - Responsive layout that flows (not snaps) across viewports
   - Proper text handling (no overflow, no hardcoded heights)
   - Following `layout-responsive.md` breakpoint strategy
   - Following `typography-color.md` type scale
   - Following `forms-feedback.md` for any form elements
   - Accessibility built in per `web-accessibility.md`
   - Pretext library integration for advanced text layout (multiline measurement, content-driven heights) when beneficial

3. **Quality Check** — Pol reviews against design references:
   - Anti-slop check (generic patterns, missing states, placeholder aesthetics)
   - Responsive verification (resize from 375px to 1440px)
   - Dark mode support if applicable

4. **Output** — Single HTML file, zero dependencies (or Pretext as only dependency), viewable by opening in any browser.

**Flags:**
- No flag = Full HTML prototype with quality check
- `--quick` = Dev builds fast, skip Pol review
- `--pretext` = Force Pretext integration for complex text layouts
- `--dark` = Include dark mode support

**How it connects:** `/ship-html` is a rapid prototyping tool. Output can be used as a reference for `/ship-build` when implementing in the actual framework.

---

## 9. Session Memory — `LEARNINGS.md` (IMPROVEMENT)

### What GStack does
`/learn` manages session memory — project-specific patterns, preferences, and lessons that persist across sessions.

### What Ship already has
Ship has `CONTEXT.md` (current session context), `DECISIONS.md` (design/technical decisions), and `TASKS.md` (task backlog). But none of these capture **lessons learned** that should inform future sessions.

### What Ship adds
**`LEARNINGS.md`** — A persistent file where the team writes patterns, mistakes, and preferences.

**Who writes to it:**
- **Crit** (during `/ship-review`) — Writes recurring quality issues: "This codebase tends to forget loading states on async operations"
- **Bug** (during `/ship-fix`) — Writes bug patterns: "State management race conditions happen when X"
- **Pol** (during `/ship-review` and `/ship-variants`) — Writes taste learnings: "Founder prefers X over Y"
- **Cap** (during `/ship-launch`) — Writes deployment learnings: "Remember to clear CDN cache after deploying"

**Who reads it:**
- **Every persona** reads `LEARNINGS.md` at session start (added to the reference loading step of each command)
- Crit checks new code against known patterns
- Bug checks new bugs against known patterns before investigating
- Pol applies learned taste preferences to design decisions

**Format:**
```markdown
# Ship Learnings

## Bug Patterns
- **[date]** Race condition in auth flow — symptom: intermittent 401 on refresh. Root cause: token refresh and API call racing. Fix: queue API calls during refresh.

## Design Preferences
- **[date]** Founder prefers 8px spacing minimum between interactive elements (above the 4px base)
- **[date]** No gradient backgrounds — founder finds them dated

## Code Patterns
- **[date]** Always use server components for data fetching in this project (Next.js 15 app router)

## Deployment Notes
- **[date]** Vercel preview deployments need env vars set manually for new branches
```

**Auto-cleanup:** If LEARNINGS.md exceeds 100 entries, Cap summarizes old entries into categories during `/ship-retro`.

---

## 10. Crit Protocol Update — Search Before Recommending

### What changes
Add to Crit's review protocol (in `/ship-review`):

**Before recommending any pattern, library, or API:**
1. Check the declared Stack version in CLAUDE.md
2. Search whether the recommended approach is current best practice for that version
3. Check if a newer/built-in solution exists in the declared version
4. Never suggest deprecated patterns
5. If unsure about version compatibility, flag it as "verify version compatibility" rather than confidently recommending

**Before forming fix suggestions:**
1. Search for the exact issue/pattern in framework documentation
2. Check if it's a known issue with a known solution
3. Reference `LEARNINGS.md` for project-specific patterns

This applies to Crit, Pol, and Arc — any persona that recommends technical patterns.

---

## Implementation Priority

### Phase 1 — High Impact, Low Effort (1-2 days)
1. **LEARNINGS.md** — Add the file, update all command prompts to read/write it
2. **Crit search-before-recommending** — Update review protocol in ship-review.md
3. **ship-fix hypothesis improvements** — Add search-first, pattern database writes, architecture questioning

### Phase 2 — Command Consolidation (1-2 days)
4. **Merge ship-qa into ship-review** — Add Test persona, health score, flag system
5. **ship-browse enhancement** — Persistent sessions, cookie import, headed mode, perf snapshot

### Phase 3 — New Planning Commands (2-3 days)
6. **ship-think** — New pre-planning validation command
7. **ship-plan improvements** — Scope modes, Pol dimension scoring, think integration

### Phase 4 — New Design Commands (3-4 days)
8. **ship-design** — Design system consultation (6-phase)
9. **ship-variants** — Theory-backed variant generation with comparison board
10. **ship-html** — Production-quality HTML prototyping

### Phase 5 — Performance & Polish (1-2 days)
11. **ship-perf** — Performance benchmarking command
12. **Documentation update** — README, CLAUDE.md template, version bump

---

## Command Count: Before vs After

### Before (14 commands)
ship-plan, ship-build, ship-review, ship-qa, ship-browse, ship-fix, ship-launch, ship-money, ship-retro, ship-codex, ship-careful, ship-freeze, ship-guard, ship-unfreeze

### After (16 commands, but cleaner)
**New:** ship-think, ship-design, ship-variants, ship-html, ship-perf
**Deprecated:** ship-qa (merged into ship-review)
**Improved:** ship-plan, ship-review, ship-browse, ship-fix
**Unchanged:** ship-build, ship-launch, ship-money, ship-retro, ship-codex, ship-careful, ship-freeze, ship-guard, ship-unfreeze

Net: +2 commands, but each one has a clear, non-overlapping purpose. The QA confusion is eliminated. The new commands fill genuine gaps (pre-planning, design systems, variants, performance, HTML prototyping) rather than adding bloat.

---

## Architecture Principle

Ship's advantage over GStack is **depth over width**. Every new command should leverage the 81+ reference documents. GStack's commands operate on Claude's general knowledge. Ship's commands operate on curated, opinionated design knowledge. That's the moat. Every new feature should deepen that advantage, not dilute it.
