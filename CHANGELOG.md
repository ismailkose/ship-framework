# Changelog

All notable changes to Ship Framework are documented here. Versions use date-based format (`YYYY.MM.DD`).

To update an existing project, run `bash ship-update.sh` from your project root, or type `/ship-update` in Claude Code.

---

## 2026.04.12 — Plugin-Native Architecture, Auto-Routing, E2E Quality Validation

### Plugin Distribution
- **Ship Framework is now a plugin.** Install via `.plugin` file in Cowork or Claude Code. No more `setup.sh` copy-paste into every project — one install, works everywhere.
- **134 files, 532KB compressed** — 21 commands, 20 skills, 85 reference files, 6 project templates, all in one package.
- **Portable paths** — All internal references use `${CLAUDE_PLUGIN_ROOT}` so the plugin works from any install location.

### Auto-Routing
- **No commands required.** The `ship-router` skill detects intent from natural language and engages the right command automatically. "Build me a login screen" triggers Dev. "Something broke" triggers Bug. "Ship it" triggers Cap.
- **Intent map covers all 21 commands** — planning, building, reviewing, fixing, launching, design, monetization, safety, and project management intents all route correctly.
- **Direct commands still work.** `/ship-plan`, `/ship-build`, etc. are available when you want explicit control. Auto-routing and direct commands work side by side.

### Command Refinements
- **ship-plan** — Reference Gate receipt format made explicit (REFERENCES LOADED with filename list).
- **ship-review** — Added cross-reference instruction: checks LEARNINGS.md patterns and DECISIONS.md design direction against every file in the diff before agents begin.

---

## 2026.04.11b — Agent Architecture, Command Slimming, Test Bench

### Agent Architecture
- **5 independent review agents** — Crit, Pol, Eye, Test, and Adversarial each have their own SKILL.md with model assignments. Crit and Adversarial run on opus, Pol and Test on sonnet, Eye on haiku. Each agent loads its full persona, voice, and instructions from `.claude/skills/ship/agents/[name]/SKILL.md`.
- **Roles vs Agents split** — Vi, Arc, Dev, and Cap remain as roles (shared conversation context, can argue/debate). Crit, Pol, Eye, Test, and Adversarial become agents (separate context windows, independent findings). This preserves the Vi/Arc debate in `/ship-plan` while giving reviewers isolation.
- **Agent container SKILL.md** — Root `agents/SKILL.md` documents the full roster with model assignments and which commands call which agents.

### Command Slimming
- **38% total line reduction** — Commands went from 4,170 to 2,594 total lines. All 8 target commands are now under 200 lines.
- **ship-review** (626→190): Full Crit/Pol/Eye/Test/Adversarial persona definitions replaced with agent call table. Kept workflow script, scoring, and output format.
- **ship-plan** (560→167): Vi and Arc sections condensed, Pol and Adversarial replaced with agent calls.
- **ship-launch** (389→181): Cap's voice trimmed, all 9 phases kept but condensed.
- **ship-design** (322→193): 6-phase structure kept, verbose examples removed.
- **ship-variants** (327→140): 5-step workflow kept, HTML code blocks and examples removed.
- **ship-team** (304→188): Orchestration and routing kept, persona re-definitions removed.
- **ship-fix** (258→153): 5-step debug process kept, verbose examples trimmed.
- **ship-html** (215→181): Reference Gate block removed (hook handles it), Smart Flag collapsed.
- **team-rules.md** (738→520): Per-command persona summaries replaced with compact Team Roster table, Per-Persona Strengths replaced with pointer to agent SKILL.md files.

### Test Bench
- **3-layer validation system** — Layer 1: structural integrity (automated, 142 tests). Layer 2: quality scanning (semi-automated, checks saved command output against rubrics). Layer 3: scenario rubrics (manual comparison, 66-point plan rubric, 82-point review rubric).
- **Mock project fixture** — FocusFlow iOS app with 16 intentional bugs across code crashes, design slop, accessibility gaps, and process violations. Used for benchmarking review quality.
- **All 142 structural tests pass** — Command frontmatter, skill files, reference paths, hook scripts, size budgets, team-rules structure, cross-references, agent readiness, duplicate content detection.

---

## 2026.04.11 — Smarter Commands, Auto-Detection, Reference Gate, Session Awareness, Reference Restructure

### Smarter Commands
- **All 21 commands now have descriptions** — Each `/ship-*` command declares what it does in its metadata. This powers Claude Code's skill picker and prevents Claude from auto-triggering commands without you explicitly invoking them.
- **ship-browse is now read-only** — Restricted to Read, Grep, Glob, and Bash tools so the browse command can't accidentally edit your files.

### Platform Auto-Detection
- **Skills activate by file type** — iOS, Web, and Android skills now trigger automatically when Claude touches matching files. Edit a `.swift` file and iOS knowledge loads. Touch a `.tsx` and web patterns activate. No manual Stack declaration needed as a fallback.
  - **iOS**: `*.swift, *.xib, *.storyboard, *.xcodeproj, *.plist, *.entitlements, Package.swift`
  - **Web**: `*.tsx, *.jsx, *.css, *.scss, *.html, *.vue, *.svelte, *.astro, next.config.*, vite.config.*`
  - **Android**: `*.kt, *.kts, *.java, *.xml, build.gradle, build.gradle.kts, AndroidManifest.xml`

### Reference Gate Hook
- **First-edit protection** — The first edit in a session is hard-blocked unless references have been loaded. After the first successful edit, the hook steps aside for the rest of the session. This enforces the "read before you code" rule automatically instead of relying on the agent to follow prompt instructions.
- **How it works** — Commands create a `.claude/.refgate-loaded` marker after printing the `REFERENCES LOADED` receipt. The hook checks for this marker before allowing any Edit or Write. Pure bash, under 1 second.
- **Works alongside freeze and careful** — All hooks run independently.

### Session Awareness
- **Automatic project context** — When a Claude Code session starts, Ship reads your CLAUDE.md and gives Claude immediate awareness: your Stack, product name, version, open task count, decisions, and learnings. No manual setup needed.
- **Environment variables** — Sets `SHIP_STACK`, `SHIP_VERSION`, `SHIP_PRODUCT` so hooks and scripts can use them throughout the session.
- **Fresh gate every session** — Cleans stale reference gate state from previous sessions so the "read before you code" check fires fresh.
- **Setup hints** — Gently reminds you if product name or Stack aren't configured yet.

### Reference Restructure
- **References moved into skill directories** — All 85 reference files now live inside their owning skill at `.claude/skills/ship/*/references/`. This enables Claude Code's progressive disclosure: skill metadata loads first, skill body loads on trigger, references load on demand. No more relying on prompt instructions to get Claude to read the right files.
- **Ownership mapping** — UX skill owns 12 references (ux-principles, typography-color, design-quality, forms, layout, navigation, touch, spatial, copy, dark-mode, interaction-design, design-research). Motion skill owns 4 (animation, animation-css, animation-framer-motion, animation-performance). Components owns 1 (components). New hardening skill owns 1 (hardening-guide). iOS owns 64 (3 core + 61 frameworks). Web owns 3.
- **New hardening skill** — Pre-launch hardening reference now has its own skill with priority enforcement table.
- **Automatic migration** — Running `/ship-update` moves your references from the old locations and cleans up empty directories. All path references in commands, skills, and team-rules updated.
- **User references stay at root** — The `references/` directory is now for your custom references. A README explains where framework references moved.

---

## 2026.04.08 — Stale v3 Command Cleanup + Setup Fixes

### Bug Fixes
- **Always-on v3 cleanup** — Old non-prefixed commands (plan.md, build.md, ship.md, architect.md, etc.) are now removed on every update, not just during initial v3→v4 migration. Fixes projects that updated from intermediate versions before the migration logic existed.
- **Skills mirror scoped to ship-* only** — The command→skill mirror in both `setup.sh` and `ship-update.sh` now only copies `ship-*` prefixed files, preventing stale v3 commands from being duplicated as skills.
- **Stale skill cleanup** — If a v3 command was previously mirrored as a skill, the orphaned skill folder is also removed.
- **Web references now copied on fresh install** — `setup.sh` was creating `references/web/` as an empty directory without copying the actual reference files (react-patterns.md, web-accessibility.md, web-performance.md). Fixed.

---

## 2026.04.07b — Reference Gate + AI Mockups + Smart Flags

### New Features
- **Reference Gate (Rule 25)** — Every command now enforces mandatory reference reading before any work begins. Agents must print a `REFERENCES LOADED` receipt before proceeding. Reviews flag `REF_SKIP` when issues were preventable by reading references. No exceptions for speed, small changes, or "I already know this."
- **AI Mockup Generation** — `/ship-variants` and `/ship-design` now support `--mockup` flag for GPT Image API integration. Generates high-fidelity AI mockup images alongside HTML comparison boards. Auto-detected when `OPENAI_API_KEY` is set and the brief is a full page/screen. Falls back to HTML-only when unavailable. Uses `gpt-image-1` with portrait (1024x1536) for mobile and landscape (1536x1024) for web.
- **Smart Flag Resolution** — All 5 design/review commands (ship-review, ship-variants, ship-design, ship-plan, ship-html) now auto-detect the right flag based on context. The team reads the diff size, file types, project state, and prior outputs to choose the appropriate mode. Explicit flags always override. Each command announces its decision so you know what happened.

### How Smart Flags Work
- **ship-review**: Auto-selects `--design` for CSS-only changes, `--product` for small diffs, full suite near releases
- **ship-plan**: Auto-selects `vi-only` for vague ideas, `arc-only` for technical requests, inherits scope mode from /ship-think
- **ship-variants**: Auto-selects `--quick` for single components, `--refine` when recent feedback exists, `--mockup` when API key available
- **ship-design**: Auto-selects `--audit` when DESIGN.md exists, `--mockup` when API key available for full consultations
- **ship-html**: Auto-adds `--dark` when DESIGN.md has dark tokens, `--form` when brief mentions forms

---

## 2026.04.07a — Hotfix: Dotglob + Version Stamp + Cleanup

### Critical Fix
- **ship-update.sh: dotglob bug** — `sync_template_dir` used `"$src_dir"/*` which doesn't match dotfiles in bash. The `.claude/` directory was completely skipped during updates, so new command files (ship-think, ship-design, ship-variants, ship-html, ship-perf) never landed on existing installs. Fixed by enabling `shopt -s dotglob` inside the sync function, with `.git`/`.gitignore`/`.github` exclusions.

### Bug Fixes
- **Version stamp corruption** — The sed pattern for updating the CLAUDE.md footer could mangle the markdown link syntax, producing `> Ship Framework](https://...` (missing opening `[`). Replaced with a full-line replacement anchored on `^>.*Ship Framework`.
- **Stale reference path** — `swiftui-core.md` header pointed to `references/frameworks/` instead of `references/ios/frameworks/`.

### Migration Improvements
- **Root-level reference cleanup** — Added catch-all migration step: any `.md` file at `references/` root that also exists in `references/ios/` or `references/shared/` is automatically removed. Handles edge cases the named-file migration missed.

---

## 2026.04.07 — iOS Muscle: Deep Framework Enrichment

### Core Reference Enrichment
- **swiftui-core.md** — Added ~800 lines: NavigationSplitView, sheet detents, iOS 26 tabs, deep linking, PhaseAnimator, KeyframeAnimator, @Animatable macro, gesture composition, @GestureState, grid layouts, iOS 26 layout APIs, MV pattern, @Observable ownership rules, Coordinator pattern, UIHostingController. NEW Section 10: Performance Diagnostics (Instruments workflow, Self._printChanges, identity/lifetime, lazy loading). Common Mistakes added to every section.
- **swift-essentials.md** — Added ~700 lines: if/switch expressions, typed throws, Never type, Regex builders, FormatStyle API, modern collection APIs. Swift 6.3 concurrency (SE-0466 default MainActor, SE-0493 async defer, SE-0473 clock epochs), concurrency error triage, Sendable rules table, synchronization primitives (Mutex, Atomic). NEW sections: Codable Patterns, Swift Testing framework.

### Framework Reference Enrichment
- **All 47 existing framework references** now include Common Mistakes (5-8 anti-patterns each) and Review Checklists (5-8 verification items each). Crit and Eye use these during /ship-review.
- **swiftdata.md** — Major enrichment: schema versioning, @ModelActor for background ops, type-safe #Predicate, PersistentIdentifier patterns.
- **storekit.md** — Added Family Sharing, subscription grace periods, SubscriptionStoreView.
- **authentication.md** — Added credential state lifecycle, identity token validation.
- **healthkit.md** — Added HKSampleQueryDescriptor async/await, empty-results-on-denial pattern.
- **cloudkit.md** — Added CKSyncEngine (iOS 17+) as recommended sync approach.
- **coreml.md** — Added async loading, MLTensor (iOS 18+), MLState stateful prediction.
- **debugging.md** — Added Memory Graph Debugger workflow, 250ms hang threshold, os_signpost.
- **networking.md** — Added token refresh pattern, exponential backoff, middleware architecture.
- **accessibility.md** — Added VoiceOver reading order, focus restoration, custom rotors.

### 14 New Framework References
- **Common:** avkit.md, pdfkit.md, cryptokit.md, financekit.md
- **Gaming:** gamekit.md, spritekit.md, scenekit.md (with deprecation note), tabletopkit.md
- **Specialized:** accessorysetupkit.md, dockkit.md, sensorkit.md, browserenginekit.md, appmigrationkit.md, cryptotokenkit.md

### Routing Updates
- **ship-team.md** — Added Gaming Stack routing (items 22-25), framework Review Checklist routing for Crit
- **ship-review.md** — Crit now reads framework Review Checklists during review
- **ship-build.md** — Dev reads framework Common Mistakes before building
- **team-rules.md** — Added swiftui-core.md Section 10 routing for Dev and Crit

### Cross-Reference Notes
5 overlap quality fixes: swiftui-core.md ↔ ux-principles.md (performance), swift-essentials.md ↔ swiftui-core.md (concurrency), webkit.md ↔ swiftui-core.md, accessibility.md ↔ ux-principles.md, debugging.md ↔ swiftui-core.md

---

## 2026.04.06 — Depth Evolution: New Commands, Session Memory, QA Consolidation

### New Commands
- **ship-think** — Pre-planning idea validation. 6 forcing questions (Real Pain, Status Quo, Specificity, Narrowest Wedge, Surprise, Taste Test). Scope modes: `--dream`, `--focus`, `--strip`. Writes idea brief to DECISIONS.md, feeds into /ship-plan.
- **ship-design** — 6-phase design system consultation: Context → Research → System Proposal → Drill-down → Preview → Documentation. SAFE/RISK breakdown per category. Creates DESIGN.md as authoritative design system file.
- **ship-variants** — 3 theory-backed variant generation, each optimizing for a different UX principle (Hick's Law, Peak-End, etc). HTML comparison board with star ratings and priority selector. Taste memory writes to LEARNINGS.md and DESIGN.md. Flags: `--quick`, `--refine`, `--taste`.
- **ship-html** — Production-quality responsive HTML prototyping. Design tokens as CSS custom properties. Semantic HTML, responsive by flow not breakpoint. Pol quality check (anti-slop, token consistency, responsive, states). Flags: `--quick`, `--dark`, `--form`.
- **ship-perf** — Core Web Vitals measurement (LCP, CLS, INP) with real Chromium. 3 runs averaged, Fast 3G throttled pass. Anti-pattern scan from web-performance.md. PERF-REPORT.md with before/after. CI assertion generation with `--ci` flag.

### Improved Commands
- **ship-plan** — Added ship-think integration (reads IDEA BRIEF from DECISIONS.md). Added LEARNINGS.md reading at session start. New Pol Design Director Plan Scoring: 7 dimensions (Information Architecture, Interaction State Coverage, User Journey, AI Slop Risk, Design System Alignment, Responsive & Accessibility, Unresolved Decisions) scored 0-10, must average ≥7. Search-before-recommending for Arc. Flags: `--pol-only`, `--dream`, `--focus`, `--strip`.
- **ship-fix** — Added LEARNINGS.md reading. Phase 0.5: Known Pattern Check (searches LEARNINGS.md bug patterns and framework docs before investigating). Architecture Assessment at strike 3 (tactical fix vs structural refactor). Bug pattern writing to LEARNINGS.md after each fix.
- **ship-review** — QA consolidated into review. New flags: `--product`, `--design`, `--visual`, `--test`, `--report`, `--fix` (legacy `crit-only`/`pol-only`/`eye-only` still supported). Full Test persona merged from ship-qa: test runner check, scope/tiers, run existing tests, explore like user, write missing tests, health score. Search-before-recommending for Crit and Pol. LEARNINGS.md writes for code patterns and design preferences.
- **ship-browse** — Complete rewrite from 47-line alias to 170-line full command. Headed browser mode (`--watch`), cookie import from installed browsers (`--auth`), Core Web Vitals snapshot (`--perf`), enhanced Eye workflow with 6 phases, persistent session support.

### Session Memory
- **LEARNINGS.md** — New persistent team memory file. Sections: Bug Patterns, Design Preferences, Code Patterns, Deployment Notes, Architecture Decisions. Multiple personas read at session start and write during their work. Created by setup.sh and ship-update.sh.

### QA Consolidation
- **ship-qa** — Deprecated. Now shows 28-line notice redirecting to `/ship-review --test`. Migration table maps old → new commands.

### Migration & Backward Compatibility
- **ship-update.sh** — Auto-fixes `/ship-qa` references in CLAUDE.md and TASKS.md. Backs up ship-team.md before overwriting (`.backup` file). Shows migration notice with diff command if routing table changed. LEARNINGS.md and DESIGN.md added to protected files.

### Documentation
- **CHEATSHEET.md** — Complete rewrite: 5 sections (Core Loop, Design Tools, When You Need It, Safety, Optional), flag reference tables, key files table, Design Readiness framework.
- **README.md** — Updated badge (v2026.04.06 · 19 deep references · 10 personas · 21 commands), new Design Tools section, expanded file structure listing all 21 commands.
- **team-rules.md** — Updated core loop (ship-think → ship-plan with Pol → ship-build → ship-review with Test), new command sections, updated flow diagram.
- **ship-team.md** — Updated routing table: "New idea" routes through ship-think first, added routes for ship-design/variants/html/perf, ship-qa replaced with ship-review --test.

---

## 2026.03.31 — Phase 3: Spatial Design, Research Depth, Overlap Fixes

### New Reference
- **spatial-design.md** — Spacing systems (4px/8px base, semantic tokens), density strategy (high/medium/low matched to product type, density modes via CSS custom properties), whitespace as design tool (active vs passive, hierarchy through space, content-to-chrome ratio).

### Enhanced References
- **design-research.md** — Added Section 4: Design Audit Methodology (inventory → extract → cluster → consolidate → document workflow), competitive analysis depth framework (flow comparison, design system extraction, 2x2 differentiation map). Updated Quick Start with deeper analysis steps.

### Overlap Quality Fixes
5 cross-reference notes added to clarify boundaries between overlapping references:
1. **typography-color.md** Section 3 → design-quality.md (type/color style vs visual consistency)
2. **layout-responsive.md** Section 2 → spatial-design.md + ux-principles.md (implementation vs philosophy vs psychology)
3. **forms-feedback.md** Section 2 → copy-clarity.md (structure/placement vs words)
4. **touch-interaction.md** → interaction-design.md (physical layer vs behavioral layer)
5. **design-quality.md** Section 2 → copy-clarity.md Section 3 (visual slop vs written slop)

### Routing Updates
- **ship-team.md** — Added item 18: spatial-design.md routing for Arc, Dev, Pol
- **ship-build.md** — Added spatial-design.md for layout builds
- **ship-plan.md** — Added spatial-design.md Sections 1-2 for spacing/density planning
- **ship-review.md** — Pol: spatial-design audit (spacing consistency, density, chrome ratio)
- **ux-principles.md** — Added spatial-design.md to deep-dive reference map
- **README.md** — Updated file tree (19 shared references)
- **CHEATSHEET.md** — Added spatial-design to reference list

---

## 2026.03.31 — Phase 2: Hardening, UX Copy, Motion Tokens

### New References
- **hardening-guide.md** — Error boundaries, network error patterns, optimistic UI recovery, edge case tables (text, numeric, timing, file upload, auth), environmental hardening (browser matrix, performance, security, accessibility), pre-launch checklist.
- **copy-clarity.md** — Voice & tone framework (3 dimensions, tone map by context), copy patterns (button labels, error messages, empty states, confirmation dialogs, loading copy), AI copy slop detection (exclamation inflation, vague value props, synonym cycling, emoji seasoning, "we" overuse).

### Enhanced References
- **animation.md** — Added motion token system (duration, easing, spring, stagger, distance tokens with CSS custom properties), full reduced motion implementation (3 levels: CSS override, JS detection hook, in-app toggle), what to keep vs remove with reduced motion.

### Routing Updates
- **ship-team.md** — Added items 16-17: hardening-guide and copy-clarity routing
- **ship-build.md** — Added copy-clarity Section 2 for copy implementation, hardening-guide for error handling
- **ship-review.md** — Crit: copy clarity + edge case review. Pol: copy-clarity Sections 1-3 for voice + AI slop
- **ship-launch.md** — Added production hardening check before tests (references hardening-guide Section 3)
- **ux-principles.md** — Added copy-clarity to deep-dive reference map
- **README.md** — Updated file tree (18 shared references)
- **CHEATSHEET.md** — Added copy-clarity and hardening-guide to reference list

---

## 2026.03.31 — Phase 1: Interaction Design, OKLCH Color, AI Slop Expansion

### New Reference
- **interaction-design.md** — 8 interactive states model (default, hover, focus, active, disabled, loading, error, success), micro-interaction timing guide, gesture design patterns with keyboard parity. 460 lines.

### Enhanced References
- **typography-color.md** — Added fluid type scales with `clamp()`, OKLCH perceptually uniform color (palette generation, browser support, HSL comparison), font alternatives beyond Google Fonts (system stacks, self-hosted, variable fonts), recommended font stacks by product type. +160 lines.
- **design-quality.md** — Expanded AI slop detection from 10 to 18 patterns. New patterns: Contrast Theater, Single-Breakpoint Responsiveness, Orphaned Interactive States, Icon-Label Mismatch, Uniform Border Radius, Stock Illustration Syndrome, Navigation Overload, Premature Dark Mode. +180 lines.

### Routing Updates
- **ship-team.md** — Added item 15: interaction-design.md routing for Dev, Pol, Eye, Crit
- **ship-build.md** — Added interaction-design.md Sections 1-2 for interactive component builds
- **ship-review.md** — Crit: interaction states audit. Pol: 18 slop patterns + state coverage audit
- **ship-plan.md** — Added interaction-design.md Section 1 for component state planning
- **ux-principles.md** — Added interaction-design.md to deep-dive reference map
- **README.md** — Updated file tree (16 shared references), updated descriptions
- **CHEATSHEET.md** — Added interaction-design to reference list

### Sources
- 8-state model: impeccable by Paul Bakaus
- Micro-interactions: Dan Saffer's Microinteractions
- OKLCH: CSS Color Level 4 spec, oklch.com
- Fluid type: Utopia type scale methodology

---

## 2026.03.30 — Design Enrichment: Skills Route, References Teach

Major design intelligence overhaul. Skills slimmed from heavy inline rules to thin routing tables (~60-80 lines each). Deep knowledge moved into 18 reference files (7,500+ lines total) that teach Claude how to think about design domains. Filled gaps identified by analyzing gstack design skills, ui-ux-pro-max-skill, and Vercel agent-skills.

### Architecture — Skills as Routers
- **UX skill** slimmed from 350+ lines to 88 lines. Routes to 9 reference files.
- **Web skill** built from placeholder to 94 lines. Routes to 3 web references + shared references.
- **Motion skill** slimmed from 180 lines to 79 lines. Quick timing table kept inline. Routes to 4 animation references.
- **Components skill** slimmed from 150 lines to 71 lines. Three-layer model kept inline. Routes to 2 references.
- All skills now have per-command routing sections (Plan, Build, Review, QA) and priority enforcement gates.
- Cross-references ("See Also") added to all 4 design skills to prevent duplication.

### Added — New Shared References
- **`typography-color.md`** (695 lines) — Type scale reasoning, font pairing, semantic color tokens, dark mode color strategy, style selection
- **`forms-feedback.md`** (265 lines) — Form architecture, validation patterns, empty states, toasts, progressive disclosure
- **`navigation.md`** (175 lines) — Nav architecture, back behavior, deep linking, adaptive patterns, URL state
- **`layout-responsive.md`** (165 lines) — Mobile-first philosophy, breakpoint reasoning, spacing scale, z-index
- **`touch-interaction.md`** (254 lines) — Tap target design (44pt/48dp reasoning), gestures, press feedback, haptics
- **`dark-mode.md`** (188 lines) — Desaturation, elevation via luminance, semantic tokens, platform implementations
- **`design-quality.md`** (644 lines) — First impression assessment, AI slop detection (10 patterns), cross-page consistency, visual coherence
- **`design-research.md`** (287 lines) — Competitive research, design direction decisions, design system creation (DESIGN.md workflow)

### Added — New Web References
- **`react-patterns.md`** (359 lines) — Server vs Client components, data fetching, composition, hydration safety
- **`web-accessibility.md`** (381 lines) — Semantic HTML, ARIA, focus management, screen reader patterns
- **`web-performance.md`** (169 lines) — Core Web Vitals, image/font optimization, anti-patterns

### Added — Reference README
- **`references/shared/README.md`** — Full listing of all reference files, "How Skills and References Work Together" section, design system template shortcut

### Fixed — Overlap Quality
- Accessibility rules deduplicated between UX and web skills (web adds web-specific only, defers to UX for core)
- Form rules deduplicated similarly
- Reduced motion priority aligned to MANDATORY everywhere (was MEDIUM in UX skill)
- Component patterns deduplicated between web and components skills

### Changed — Documentation
- README.md: File structure expanded to show all 18 reference files. New "Skills Route, References Teach" section.
- CHEATSHEET.md: Skills section replaced with "Skills + References" section including priority gates table.

### Sources
- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) — 161 color palettes, 57 font pairings, 99 UX guidelines, style selection
- [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) — React best practices, web design guidelines, composition patterns
- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) — Accessibility, forms, animation, typography, performance
- [gstack design skills](https://github.com/garrytan/gstack) — Gap analysis for AI slop detection, first impression, coherence, competitive research

---

## 2026.03.29 — v4: Skills, Safety, and Founder-Aware Teams

Complete architectural overhaul. Ship Framework v4 introduces a skills system, safety hooks, stack-aware context routing, and a Founder section that makes every persona adapt to how YOU work. 16 commands (up from 11), 10 framework skills, and a coaching system that turns AI personas into world-class teammates who speak up when it matters.

### Architecture — Phase 1: Command Namespacing
- All commands renamed with `/ship-` prefix: `/plan` → `/ship-plan`, `/build` → `/ship-build`, etc.
- `/ship` (old release command) → `/ship-launch` to avoid `/ship-ship`
- CLAUDE.md becomes thin orchestrator (~95 lines). All rules moved to `.claude/team-rules.md`

### Architecture — Phase 2: Stack-Aware Context Routing
- CLAUDE.md declares `Stack: web | ios | android | cross-platform`
- References restructured: `shared/` (always loaded), `ios/`, `web/`, `android/` (per stack)
- Commands detect declared stack and only load relevant platform references
- If no stack declared, Ship asks on first `/ship-plan` or `/ship-build`

### Architecture — Phase 3: Skills System
- New `.claude/skills/` directory with framework skills and user skills
- **Framework skills** (`ship/`): ux, components, motion, ios, web, android, careful, freeze, guard, unfreeze
- **User skills** (`your-skills/`): add your own skills with YAML frontmatter SKILL.md files
- Skills are active (knowledge + instructions + when to apply). References remain passive data.
- Commands explicitly declare which skills they load

### Architecture — Phase 4: Completion Status Protocol
- Every command ends with `STATUS: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT`
- Added to all 16 command files

### Architecture — Phase 5: Decision Classification
- Every decision categorized: **mechanical** (auto-decide), **taste** (surface at gate), **user-challenge** (always ask)
- Integrated into `/ship-plan`, `/ship-build`, `/ship-review`

### Architecture — Phase 6: User Sovereignty
- "No amount of model confidence overrides a direct founder instruction"
- Protocol for single persona disagreement, multi-persona disagreement, and cross-model disagreement
- The founder always decides — the team informs

### Architecture — Phase 7: Cross-Model Verification (Codex)
- New `/ship-codex` command with three modes: review, challenge, consult
- Prompt injection boundary mandatory for every Codex invocation
- Graceful degradation when Codex not installed
- Optional integration in `/ship-plan` (challenge) and `/ship-review` (review)

### Architecture — Phase 8: Safety Hooks
- **`/ship-careful`** — PreToolUse hook on Bash. Warns before destructive commands (rm -rf, DROP TABLE, git push --force, git reset --hard, kubectl delete, docker prune, etc.). Safe exceptions for node_modules, .next, dist.
- **`/ship-freeze`** — PreToolUse hook on Edit and Write. Reads `.claude/.freeze-path` state file. Blocks edits outside frozen directory.
- **`/ship-guard`** — Combined: both careful + freeze hooks active.
- **`/ship-unfreeze`** — Removes freeze restriction.
- All hooks use shell scripts with JSON stdin/stdout per Claude Code hook protocol.
- 28 automated tests in `test/test-safety.sh` (all passing).

### Architecture — Phase 10: Anti-Slop Vocabulary
- Rule 24 expanded with full banned vocabulary list
- Anti-sycophancy enforcement across all personas

### Architecture — Phase 11: Test Cases
- Full test matrix in `test/TEST-MATRIX.md` covering all phases
- 28/28 automated safety hook tests passing

### Added — The Founder Section
- New `## The Founder` section in CLAUDE.md template
- 7 fields: Background, Technical comfort, Decision style, Communication, Taste, Context need, Focus awareness
- Every persona reads and adapts to founder's profile on command load
- "Adapting to The Founder" rules added to team-rules.md

### Added — Coaching the Founder
- New section in team-rules.md: personas are world-class talent, not just executors
- **Detail trap pattern**: when founder goes deep on shippable details while core flows are incomplete, personas surface it respectfully
- **Per-persona agentic strengths**: each persona's human expertise + what they can do that humans can't (scan codebases, run edge case matrices, measure pixels, read git history, do live research)
- Handles founders who are learning — designers, PMs, aspiring founders who need coaching not just execution

### Added — Talent Framing
- Team intro rewritten: personas are the best in their field, top-tier talent a solo founder could never hire
- Combined deep expertise with agentic capabilities

### Added — Post-v4 from gstack v0.13.7-v0.13.9
- **Skill discoverability**: `(ship)` tag added to all 10 skill descriptions for command palette search
- **Content Trust Boundary**: `--- BEGIN/END UNTRUSTED EXTERNAL CONTENT ---` markers in `/ship-browse`
- **Proactive Skill Routing**: auto-detect new user skills in `your-skills/`, offer CLAUDE.md wiring, ask once per skill

### Changed
- CLAUDE.md Design Principles: removed hardcoded animation timing ("150-250ms, ease-out") — motion skill handles this with more nuance
- All reference paths updated to platform subdirectories (`references/ux-principles.md` → `references/shared/ux-principles.md`)
- Rule 19 renamed to "Platform API first" (was iOS-specific)
- Rule 21 now stack-aware with graceful degradation

### Phase 9 (Build System) — Skipped
- Deferred until commands grow past 25+. Current duplication manageable at 16 commands.

---

## 2026.03.27 — Adversarial Autoplan: Named Personas Inside Simple Commands

The team collapsed from 15 commands to 11. Five standalone agents (Vi, Arc, Crit, Pol, Eye) now live inside two power commands: `/plan` and `/review`. Each persona keeps its name, voice, and explicit disagreements, but you invoke one command instead of five. Every command now ends with a STATUS signal. New rules 20-24 enforce completeness, atomic commits, anti-sycophancy, and search-before-building.

### Architecture Change
- **`/plan`** = Vi (product strategist) + Arc (technical lead) + Adversarial (stress test). Produces product brief, dual-approach technical plan, and adversarial attack in one pass
- **`/review`** = Crit (product reviewer) + Pol (design director) + Eye (visual QA) + Adversarial (challenge). Produces HEART review, anti-slop check, screen walkthrough, confidence scoring, and adversarial challenge in one pass
- **`/browse`** rewritten as thin alias for `/review eye-only`
- Old standalone commands deleted: `/visionary`, `/architect`, `/critic`, `/polish`, `/health`, `/status`

### Added — New Command Files
- **plan.md** — Full /plan command with Vi + Arc + Adversarial voices, flag handling (vi-only, arc-only, with-monetization), dual-approach planning with guardrail, Safe/Bold design proposals, STATUS signal
- **review.md** — Full /review command with Crit + Pol + Eye + Adversarial voices, flag handling (crit-only, pol-only, eye-only), anti-slop check (22 universal + platform-specific items), confidence scoring (0-100), Close-Your-Eyes test, review freshness hash, STATUS signal

### Changed — Existing Commands
- **build.md** — Added Build Scope declaration, Scope Enforcement (mandatory check before every file edit, MINOR vs STRUCTURAL classification), atomic commits (Rule 22), review staleness note, STATUS signal
- **fix.md** — Added Phase 0 Scope Lock, Pattern Analysis Table, 3-Strike Tracking with attempt format and BLOCKED escalation, Sanitized External Search (strip sensitive data before web searching), Debug Report format, STATUS signal
- **ship.md** — Added Plan Completion Audit, Test Failure Triage (IN-BRANCH vs PRE-EXISTING), Coverage Gate (platform-aware: iOS xcodebuild, Web Jest, Android jacoco), Pre-Landing Safety Net (LAST_REVIEW_HASH comparison), TASKS.md Auto-Completion, Documentation Sync check, STATUS signal
- **qa.md** — Updated Vi reference to point to /plan
- **money.md** — Updated Vi reference to point to /plan
- **browse.md** — Rewritten as thin alias for `/review eye-only`
- **team.md** — Task routing rewritten for /plan and /review, agent count updated

### Changed — Team Rules (`team-rules.md`)
- "How the Team Thinks" rewritten: 6 questions collapsed to 5+1 using /plan and /review
- Removed 5 old agent definitions (/visionary, /architect, /critic, /polish, /browse)
- Added 2 new definitions (/plan and /review) with persona descriptions
- Workflow diagram updated: `/plan -> /build -> /review -> /qa -> /ship`
- Rule 1 updated: "Never start coding before /plan" (was "/visionary and /architect")
- **Rule 20: Completeness is cheap** — finish the last 10%, no TODO comments, DONE or BLOCKED
- **Rule 21: Search before building** — three layers (codebase, references, vendor docs) with graceful degradation for missing platform references
- **Rule 22: Atomic commits** — one concern per commit, enables git bisect
- **Rule 23: One decision per question** — no compound questions to the founder
- **Rule 24: Anti-sycophancy** — banned phrases, banned AI vocabulary (delve, robust, nuanced, etc.), lead with concern not compliment

### Deleted
- `visionary.md`, `architect.md`, `critic.md`, `polish.md`, `health.md`, `status.md`

### Design Philosophy
- **Anti-slop typography flag** — catches lazy defaults (everything `.body` at `.regular` weight) not intentional platform-native choices
- **Platform detection** — Arc auto-detects platform from project files (*.swift, package.json, build.gradle)
- **Platform-conditional checklists** — universal items apply everywhere, platform-specific items conditionally
- **Confidence scoring** — 0-100 on review findings, below 50 filtered out
- **3-strike escalation** — stop after 3 failed debug hypotheses
- **Review staleness tracking** — hash comparison between /review and /ship

---

## 2026.03.26 — Community Skill Audit + Security Reference + Quality Improvements

Cross-referenced 10+ community agent skills and Apple's Xcode 26 system prompts to identify gaps, fix quality issues, and add missing coverage. New iOS Security reference file. No-Hack API expanded from 10 to 18 patterns.

### Sources Analyzed
- [twostraws/SwiftUI-Agent-Skill](https://github.com/twostraws/SwiftUI-Agent-Skill) — SwiftUI Pro (9 reference files)
- [twostraws/SwiftData-Agent-Skill](https://github.com/twostraws/SwiftData-Agent-Skill) — Predicate safety, actor boundaries, relationship traps
- [twostraws/Swift-Concurrency-Agent-Skill](https://github.com/twostraws/Swift-Concurrency-Agent-Skill) — Actor reentrancy (#1 LLM bug), 10 bug patterns
- [twostraws/Swift-Testing-Agent-Skill](https://github.com/twostraws/Swift-Testing-Agent-Skill) — .serialized gotchas, confirmation() traps
- [artemnovichkov/xcode-26-system-prompts](https://github.com/artemnovichkov/xcode-26-system-prompts) — Apple's Xcode 26 AI instructions
- [ivan-magda/swift-security-skill](https://github.com/ivan-magda/swift-security-skill) — Keychain, biometrics, CryptoKit
- [arjitj2/swiftui-design-principles](https://github.com/arjitj2/swiftui-design-principles) — Spacing grid, typography hierarchy, semantic colors
- [Dimillian/Skills](https://github.com/Dimillian/Skills) — View composition fix, performance audit, concurrency patterns
- [dadederk/iOS-Accessibility-Agent-Skill](https://github.com/dadederk/iOS-Accessibility-Agent-Skill) — VoiceOver, Switch Control, Voice Control
- [AvdLee/Swift-Testing-Agent-Skill](https://github.com/AvdLee/Swift-Testing-Agent-Skill) — Testing best practices (partial)

### Added — New Framework Reference
- **ios-security.md** — Keychain add-or-update pattern, OSStatus error table, accessibility tiers, LAContext boolean gate vulnerability (Frida-bypassable), correct Secure Enclave pattern, access control flags, 7 anti-patterns, CryptoKit essentials (symmetric + public key + post-quantum iOS 26+), Secure Enclave constraints, keychain lifecycle, testing patterns

### Changed — SwiftUI Core Reference (`swiftui-core.md`)
- **Section 1 Navigation:** Sheet presentation shortcuts, alert single-OK shorthand, navigationDestination once-per-type rule, confirmationDialog Liquid Glass placement, toolbar enhancements (toolbar(id:), searchToolbarBehavior, matchedTransitionSource, .largeSubtitle, sharedBackgroundVisibility), Tab selection binding (enum not integer)
- **Section 6 Layout:** ContentUnavailableView.search shorthand, **NEW Design Rules subsection** (44pt tap targets, typography with bold(), .caption2 avoidance, semantic styling, Label over HStack, LabeledContent for Form, TextField(axis:), spacing grid 4/8/12/16/20/24/32/40/48, design constants enum)
- **Section 6.5 No-Hack API:** Expanded from 10 to 18 patterns — added overlay() trailing closure, topBarLeading/topBarTrailing, scrollIndicators(.hidden), @Entry macro, fill+stroke chaining, Text interpolation, grammar agreement, ForEach enumerated
- **NEW Section 6.7 Accessibility Quick Reference:** Dynamic Type rules, VoiceOver (button labels, Menu labels, onTapGesture rules, accessibilityInputLabels), Color & Motion (differentiateWithoutColor, reduceMotion), Tap Targets (44pt), Input Methods (Voice Control, Keyboard, Switch Control)
- **Section 7 Architecture:** Data Flow Rules (@State private, @AppStorage in @Observable trap, Binding rules, numeric TextField, onChange variant rules, import Combine requirement, SwiftData+CloudKit constraints, MV-first default)
- **Section 8.5 Performance:** Ternary vs if/else for modifier toggling, view initializers must be minimal, scrollContentBackground(.visible), @ViewBuilder closure storage anti-pattern, avoid inline transforms
- **Section 8.6 View Composition QUALITY FIX:** Replaced computed property guidance with separate View struct preference (contradicted community best practices), added view file ordering convention, MV-first rules
- **Section 9 Checklists:** Added Accessibility checklist, added 8 new No-Hack API checklist items

### Changed — Swift Essentials Reference (`swift-essentials.md`)
- **NEW Section 1 Modern Swift Idioms:** 15 rules — replacing(), URL.documentsDirectory, FormatStyle, static member lookup, localizedStandardContains, Double over CGFloat, count(where:), Date.now, PersonNameComponents, Comparable for sorts, "y" not "yyyy", Date strategy, flag swallowed errors, if/switch expressions, import SwiftUI includes UIKit
- **Section 2 Concurrency:** Actor reentrancy with deduplication pattern, 10 bug patterns list, structured concurrency (async let vs task groups with limiting), AsyncStream patterns (makeStream, buffer policy), cancellation patterns, bridging legacy code table, diagnostics quick reference table, Swift 6.3 updates
- **Section 3 Testing:** Testing gotchas (.serialized only parameterized, confirmation must complete, .minutes not .seconds, don't negate with !, tests without expectations pass, no float tolerance), best practices (parallel-safe default, #expect vs #require, traits over naming, XCTest carve-outs), range-based confirmations, exit testing, Swift 6.3 testing updates (Issue.record severity, Test.cancel(), image attachments)

### Changed — Framework Reference Updates
- **swiftdata.md** — Major expansion: Predicate safety (safe ops vs runtime crash ops like isEmpty), Core Rules (autosaving, actor boundaries, @Relationship one-side, inverse relationships, "description" reserved, property observers ignored, @Transient defaults, migration schemas, delete rules, @Query view-only, fetchCount limitations, #Unique one-per-model, enum associated values), Indexing (iOS 18+), Class Inheritance (iOS 26+), SwiftData+CloudKit constraints
- **storekit.md** — iOS 26+ updates (appTransactionID, originalPlatform, currentEntitlements, expirationReason, SubscriptionOfferView, visibleRelationship)
- **app-intents.md** — iOS 26+ updates (IntentModes, continueInForeground, requestChoice, @ComputedProperty, @DeferredProperty, IndexedEntity, Swift Package support)
- **swift-charts.md** — 3D Charts (Chart3D, SurfacePlot, Chart3DPose, projections, surface coloring)
- **accessibility.md** — Assistive Access (iOS 26+), Advanced Accessibility Patterns (Switch Control, Voice Control, Full Keyboard Access, announcement timing, Smart Invert)
- **apple-on-device-ai.md** — Guided Generation (@Generable macro, snapshot streaming, tool calling, 4096 token limit)
- **widgetkit.md** — visionOS Widgets, Widget Performance (memory budget, timeline refresh strategy)

### Changed — Architecture Routing (v2, from efremidze/swift-architecture-skill)
- **Section 7:** Architecture detection table (8 patterns with codebase signals), isolation rules (8 "never mix" constraints), intentional simplification rule (simpler patterns OK inside complex architectures, never reverse), architecture decision tree for new projects and reviews, over/under-engineered detection, "when to justify a view model" conditions
- **Section 8.5:** Performance triage ordering (invalidation → identity churn → main-thread → image → layout), formatter anti-pattern (static cached singletons, FormatStyle preferred)

### Changed — Async Patterns (from efremidze/swift-architecture-skill)
- **swift-essentials.md Section 2:** Request ID gating pattern (UUID-based stale response prevention), distinction from Task cancellation (both needed), cancellation-first checklist for every async entry point
- **swift-essentials.md Section 3:** Deterministic async testing with CheckedContinuation (no sleeps), TCA TestClock pattern, architecture-specific test target table (what to test per pattern)

### Stats
- Framework reference count: 46 → 47
- No-Hack API patterns: 10 → 18
- Community sources analyzed: 12+ repos
- Quality fix: View composition guidance corrected (separate View structs > computed properties)
- New: Architecture routing with pattern detection + isolation rules
- New: Request ID gating pattern for stale response prevention

---

## 2026.03.25 — iOS Reference Deep-Dive + 5 New Frameworks + Modern API Modernization

Comprehensive reference update informed by [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills). All 41 existing framework files updated, 5 new frameworks added, both core reference files substantially expanded.

### Added — 5 New Framework References (`references/frameworks/`)
- **apple-on-device-ai.md** — Foundation Models framework, on-device inference, tool calling, guided generation, streaming
- **swift-charts.md** — Swift Charts: BarMark, LineMark, AreaMark, PointMark, SectorMark, axes, selection, scrolling
- **tipkit.md** — TipKit: inline/popover tips, parameter and event rules, eligibility, TipGroup
- **natural-language.md** — NLTagger, NLEmbedding, sentiment analysis, tokenization, NER, language detection
- **webkit.md** — WKWebView in SwiftUI, JavaScript bridging, navigation policies, cookie management

### Changed — SwiftUI Core Reference (`swiftui-core.md`, +1110 lines)
- **Section 1 Navigation:** iOS 26 Tab APIs (`Tab(role: .search)`, `.tabBarMinimizeBehavior()`, `.tabViewBottomAccessory {}`, `TabSection`), `.presentationSizing` fine-tuning, `.dismissalConfirmationDialog()`, 7 additional common mistakes
- **Section 4 Animation:** All 10 symbol effects with rendering modes, `@Animatable` macro, `withAnimation` completion callbacks, `ContentTransition`, Navigation Zoom Transition, PhaseAnimator per-phase curves, 7 common mistakes (was 0)
- **Section 5 Gestures:** `MagnifyGesture`/`RotateGesture` (iOS 17+), `@GestureState` reset behavior, gesture composition patterns, `GestureMask` control, parent/child conflict resolution
- **Section 6 Layout:** `LazyVStack`/`LazyHStack` guidance, `.scrollContentBackground(.hidden)`, `ScrollViewReader`, `.searchable` with scopes + debouncing, `.safeAreaInset(edge:)`
- **Section 8 UIKit Interop:** Lifecycle table, guard-against-redundancy pattern, `.sizeThatFits()`, `UIHostingConfiguration`, `UIHostingController.sizingOptions`
- **NEW Section 8.5 Performance:** Instruments profiling, view body evaluation analysis, `Self._printChanges()`, lazy loading decision guide, observation scope pollution
- **NEW Section 8.6 Patterns:** `@Observable` ownership rules, view composition, `@ViewBuilder`, custom `ViewModifier`

### Changed — Swift Essentials Reference (`swift-essentials.md`, +791 lines)
- **Language:** if/switch expressions, modern collection APIs, `FormatStyle`, string interpolation extensions
- **NEW Concurrency section:** Triage workflow, `AsyncSequence`/`AsyncStream`, `Mutex` vs `OSAllocatedUnfairLock` vs `Atomic` decision guide, GCD prohibition, 8 additional common mistakes
- **Codable:** Lossy array decoding, single value containers, `decodeIfPresent` defaults, Codable with SwiftData, `keyDecodingStrategy` trade-offs
- **Testing:** `confirmation()`, parameterized tests with `zip()`, custom test argument generators, `TestScoping` traits, `withKnownIssue()`, exit testing

### Changed — Tier 1 Framework Updates (12 files, major API modernization)
- **healthkit.md** — Async/await `HKSampleQueryDescriptor` replacing callbacks, `HKUnit` reference table, privacy-by-silence, 6+ new mistakes
- **storekit.md** — `StoreView`/`ProductView`, `AppStore.sync()`, `.currentEntitlementTask(for:)`, purchase options, subscription renewal states, 5+ new mistakes
- **coreml.md** — `MLTensor` (iOS 18+), `MLState`, `CoreMLRequest`, `MLComputePlan`, async model loading, batch predictions, actor-based caching
- **cloudkit.md** — `CKSyncEngine` (iOS 17+), `CKError` handling table, three-way merge, iCloud Drive sync, `NSUbiquitousKeyValueStore`
- **swiftdata.md** — `#Unique`, model inheritance (iOS 26+), `@Attribute` options, `modelContext.transaction {}`, bulk delete, `@ModelActor`
- **mapkit.md** — `CLServiceSession` (iOS 18+), `CLLocationUpdate.liveUpdates()`, `PlaceDescriptor` (iOS 26+), `MKGeocodingRequest`, search debouncing
- **live-activities.md** — Push-to-start (iOS 17.2+), scheduled activities (iOS 26+), `ActivityStyle`, channel-based push, APNs payload format
- **app-intents.md** — `IndexedEntity` (iOS 26+), `SnippetIntent`, `IntentValueQuery`, `ControlConfigurationIntent`, deprecated macro warnings
- **networking.md** — `RequestMiddleware` protocol, `withRetry()`, `APIClient` architecture, `AsyncStream` pagination, `NWPathMonitor`
- **speech.md** — `SpeechAnalyzer` (iOS 26+), `SpeechTranscriber`, comparison table vs `SFSpeechRecognizer`
- **alarmkit.md** — `AlarmManager` API, `Alarm.Schedule` types, `CountdownDuration`, state machine, `AlarmButton`
- **vision-framework.md** — Modern iOS 18+ struct-based requests, `RecognizeDocumentsRequest`, person instance masks, hand/animal pose detection

### Changed — Tier 2 Framework Updates (13 files, moderate improvements)
- **widgetkit.md** — `AppIntentTimelineProvider`, `WidgetPushHandler`, `WidgetAccentedRenderingMode`, CarPlay widgets
- **push-notifications.md** — Async/await delegates, `@Observable` DeepLinkRouter, provisional/critical alerts
- **background-processing.md** — `BGContinuedProcessingTask` (iOS 26+), resource requirements, Swift 6 concurrency
- **accessibility.md** — `@AccessibilityFocusState`, `.isModal` trait, custom rotors, Assistive Access (iOS 18+)
- **localization.md** — `LocalizedStringResource`, grammar agreement inflection, `@ScaledMetric`, pseudolocalization
- **security.md** — `SecAccessControl` flags, `.biometryCurrentSet` vs `.biometryAny`, Secure Enclave persistence
- **debugging.md** — `mxSignpost()`, `OSSignposter` actor, `xctrace` CLI, Thread Sanitizer patterns
- **metrickit.md** — `MXCallStackTree` symbolication, `MXSignpostIntervalData`, app exit metrics, `pastPayloads`
- **core-bluetooth.md** — RSSI filtering, peripheral reference management, background BLE, state restoration
- **realitykit.md** — `RealityView` SwiftUI-first, spatial gesture targeting, `SceneEvents.Update`, visionOS callout
- **shareplay.md** — `GroupSessionMessenger` delivery modes, `GroupSessionJournal`, late-joiner handling
- **energykit.md** — `ElectricityGuidance.Query`, `EnergyVenue`, `ElectricalMeasurement`, `ElectricityInsightQuery`
- **callkit.md** — Async/await VoIP push, E.164 formatting, outgoing call flow, `@unchecked Sendable`

### Changed — Tier 3 Framework Updates (14 files, minor additions)
- **contacts.md** — `.limited` authorization, composite key descriptors, change observer
- **eventkit.md** — Write-only access, `EKStructuredLocation`, async reminders
- **musickit.md** — Subscription observation, player type contrast, offer modifier
- **weatherkit.md** — `WeatherAvailability`, selective queries, SF Symbol names, caching actor
- **photos-camera.md** — `Transferable`, composite filters, downsampling, concurrent loading
- **core-motion.md** — `CMBatchedSensorManager`, polling vs callback, confidence checking
- **core-nfc.md** — Tag status checking, type switch pattern, error filtering
- **authentication.md** — `.transferred` state, revocation observer, SwiftUI OAuth, JWT validation
- **app-store-review.md** — Phased release table, expedited review, video specs, ATT timing
- **passkit.md** — Button type table, `PaymentConfig` enum, shipping update delegate
- **homekit.md** — `DeviceCriteria`, Matter handler signatures, characteristic metadata
- **device-integrity.md** — Actor-based `AppAttestManager`, retry backoff, `DCError` handling
- **pencilkit.md** — PaperKit comparison, stroke interpolation, programmatic construction
- **permissionkit.md** — `AskCenter`, all 9 communication actions, `PermissionButton`

### Stats
- Framework reference count: 41 → 46
- `swiftui-core.md`: ~1,371 → 2,481 lines (+81%)
- `swift-essentials.md`: ~680 → 1,471 lines (+116%)
- Source: [dpearson2699/swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) (57 skills, iOS 26+ / Swift 6.2)

---

## 2026.03.23 — Production Chat UI Reference + Quality Loop + Prompt Sharpening + No-Hack APIs

### Added — Rule 19: Apple API First (`team-rules.md`)
- No custom builds when a system API exists — check Apple documentation before building anything custom
- Eye rejects any PR that custom-builds something Apple already provides natively
- Applies to: UI effects, layout, presentation, navigation, accessibility, data flow

### Added — No-Hack API Reference (`references/swiftui-core.md` Section 6.5)
- 9 common patterns where agents try hacky workarounds instead of using the real SwiftUI API
- Each entry shows the WRONG approach (so agents recognize what not to do) and the CORRECT one-liner
- Progressive blur / scroll edge effects: `.scrollEdgeEffectStyle(.soft)` — not custom blur overlays
- safeAreaBar (iOS 26): `.safeAreaBar(edge:)` — extends scroll edge effects into custom bars
- Haptic feedback: `.sensoryFeedback()` — not `UIImpactFeedbackGenerator` bridge code
- containerRelativeFrame: percentage sizing without `GeometryReader`
- symbolEffect: animated SF Symbols without manual rotation/opacity
- scrollDismissesKeyboard: `.scrollDismissesKeyboard(.interactively)` — not tap gesture hacks
- presentationDetents: native half-sheets — not custom `DragGesture` bottom sheets
- FocusState: `@FocusState` + `.focused()` — not `UITextField` wrapping
- toolbarVisibility: `.toolbarVisibility(.hidden, for:)` — not `UINavigationBar.appearance()`
- MeshGradient (iOS 18): native mesh gradients — not stacked `LinearGradient` hacks
- Review checklist added to Section 9 for Eye to catch these during review
- Scroll Edge Effects section expanded with full SwiftUI + UIKit API, styles table, safeAreaBar
- chat-ui.md floating composer section updated with progressive blur implementation guidance

### Added — Chat UI Reference (`references/frameworks/chat-ui.md`)
- Part 1: Universal principles — architecture philosophy, message animation sequencing, the blank size problem (4 failed approaches + what works), keyboard management (6 behaviors + edge cases), floating composer cascade, streaming text with animation pool pattern, markdown rendering, performance principles, shared API architecture
- Part 2: SwiftUI full code examples — @Observable state, PhaseAnimator, .contentMargins(), KeyboardObserver, GlassEffectContainer, actor-based animation pool, AttributedString markdown, native menus/sheets
- Part 3: React Native full code examples — context providers, Reanimated shared values, contentInset blank size, react-native-keyboard-controller, Liquid Glass, createUsePool fade system, TextInput native patch, initial scroll-to-end
- Part 4: Platform comparison table (SwiftUI vs React Native vs Web/Other)
- Part 5: Review checklist for Eye — animation, blank size, keyboard, composer, streaming, performance
- Source: Vercel v0 iOS engineering blog + krispuckett/V0Swift SwiftUI translation
- Conditional framework: add with `--add-framework chat-ui`

### Changed — Rule 0: Global Prompt Sharpening
- Added Rule 0 to team-rules.md — restate the founder's request in one clear sentence before doing anything
- Applies to ALL interactions (slash commands, direct typing, everything)
- Ask ONE clarifying question if vague, or assume and move on

### Added — Quality Loop Rules (team-rules.md Rules 16-18)
- Rule 16: 3-attempt retry limit — Dev tries 3 different approaches, then escalates to Arc or founder. No spinning on the same problem.
- Rule 17: Screenshot evidence required — Eye defaults to "NEEDS WORK" on UI changes unless there's actual screenshot proof. No "looks correct based on the code."
- Rule 18: Mid-build status reporting — progress update after each completed task during multi-task builds. Founder never has to ask "where are we?"

### Changed — Agent Routing (team.md)
- Items 19-21: Chat UI reference routing for Dev, Arc, Eye
- Dev reads Part 1 + platform-specific part when building chat interfaces
- Arc reads architecture + blank size + API sections when planning chat
- Eye reads Part 5 review checklist when reviewing chat UI

---

## 2026.03.21 — SwiftUI Deep-Dive + shadcn/ui Practical Guide + Prompt Sharpening + Design Discovery

### Added — shadcn/ui Practical Guide (components.md Section 3)
- Full component catalog: 46 components in 7 categories (form, layout, overlay, nav, feedback, data, utility) with install commands and "when to use"
- Install bundles: pre-grouped commands for forms, data display, overlays, navigation, layout, feedback
- Theming system: HSL CSS variable roles, dark mode setup with next-themes, `--radius`, color role mapping
- `cn()` utility: tailwind-merge + clsx for intelligent class merging, incorrect/correct examples
- CVA variant pattern: adding custom variants and sizes to existing components, TypeScript interfaces
- Composite component pattern: wrapper components for behavior changes, file structure convention
- Form integration: react-hook-form + zod + shadcn Form — the #1 pattern Dev builds, now fully documented
- Blocks overview: pre-built page sections (dashboard, auth, sidebar, calendar)
- Review checklist (Section 3.9): theming consistency, component quality, form validation, accessibility — for Eye and Test

### Added — Prompt Sharpening (Vi + Arc)
- Vi Step 0: restate the idea in one sentence, ask ONE clarifying question if vague, or assume and move on
- Arc Step 0: same pattern for direct build requests when Vi is skipped
- Both entry points now catch ambiguity before planning against it
- team.md routing updated: "New idea" → Vi (sharpen → brief), "Build this" → Arc (sharpen → plan)

### Added — Design System Auto-Discovery (Eye Phase 0)
- Eye checks for `references/design-system.md` before running visual QA
- If missing/empty: discovers tokens from globals.css, tailwind.config, and component files
- For shadcn projects: reads CSS variables and components.json for structured token data
- Compiles "Discovered Design Tokens" section at top of report
- Suggests creating design-system.md at end of report — observation only, founder decides
- Solves the common case where founders build for weeks without documenting design tokens

### Added — SwiftUI Implementation Deep-Dive + 40 Conditional Framework References

### Added — SwiftUI Core Implementation (swiftui-core.md)
- New always-included reference for iOS projects (9 sections)
- Navigation implementation: NavigationStack, NavigationPath, router pattern, NavigationSplitView, sheet routing, deep links
- Swift 6.2 concurrency: default MainActor isolation (SE-0466), @concurrent, nonisolated(nonsending), Task.immediate, actor isolation, Sendable, structured concurrency, synchronization primitives
- Liquid Glass implementation: .glassEffect() API, GlassEffectContainer, morphing transitions, glass union, button styles, scroll edge effects
- Animation: spring animations, transitions, matchedGeometryEffect, PhaseAnimator, KeyframeAnimator, Reduce Motion
- Gestures: tap, drag, magnify, rotate, gesture composition
- Layout: ViewThatFits, Grid, custom Layout, ContentUnavailableView, ScrollView enhancements
- Architecture: @Observable, Environment DI, Observations (SE-0475)
- UIKit interop: UIViewRepresentable, UIViewControllerRepresentable, UIHostingController
- Review checklists for all sections

### Added — Swift Essentials (swift-essentials.md)
- Swift 6.2 language features, Codable patterns, Swift Testing (@Test, #expect, @Suite)

### Added — 40 Conditional Framework References (references/frameworks/)
- Data & Storage: swiftdata, cloudkit, contacts, eventkit
- App Experience: storekit, app-intents, live-activities, widgetkit, app-clips, alarmkit
- Auth & Notifications: authentication, push-notifications, permissionkit
- AI & ML: coreml, vision-framework, speech
- Media: photos-camera, musickit, passkit
- Hardware: core-bluetooth, core-motion, core-nfc, pencilkit, realitykit
- Platform: callkit, energykit, homekit, shareplay, weatherkit
- Engineering: networking, security, accessibility, localization, background-processing, debugging, device-integrity, metrickit, app-store-review
- Each file: triage workflow, core API, code examples, common mistakes, review checklist
- Conditional loading: all copied by default, `SHIP_FRAMEWORKS` env var for selective install
- Add later: `bash update.sh ~/MyApp --add-framework healthkit,storekit`

### Added — Design Review Checklists (hig-ios.md Section 10)
- Navigation, Typography, Color, Touch, Materials/Liquid Glass, Accessibility, App Lifecycle checklists
- Eye agent reads during `/review`

### Changed — Agent Routing (team.md)
- Items 9-15: SwiftUI core, Swift essentials, conditional frameworks, design checklists, implementation checklists
- Dev reads `swiftui-core.md` for all SwiftUI features, `swift-essentials.md` for Swift code, relevant `frameworks/` files
- Arc reads `swiftui-core.md` Section 1 for navigation planning
- Eye reads `hig-ios.md` Section 10 + `swiftui-core.md` Section 9 for reviews

### Changed — CLAUDE.md Split (Two-File Architecture)
- CLAUDE.md now contains ONLY user content: product name, description, stack, design principles, key files, custom references
- All framework content (agent definitions, product frameworks, rules, workflows) moved to `.claude/team-rules.md`
- `team-rules.md` is managed by Ship Framework and synced on every update — users never edit it
- CLAUDE.md is protected and never overwritten — users customize it freely
- All 12 slash commands updated to read both files: CLAUDE.md for product context, `.claude/team-rules.md` for agent definitions and rules
- Solves the update gap: framework improvements (new agents, rule changes, routing updates) now reach existing projects automatically

### Changed — Generic Template Sync (update.sh rewrite)
- Replaced piecemeal hardcoded sync blocks with recursive `sync_template_dir` function
- Walks entire `template/` directory: creates new dirs, copies new files, updates existing files, skips protected files
- Protected files: CLAUDE.md, TASKS.md, `references/design-system.md` — never overwritten
- Reports counts: "Template synced (X updated, Y new, Z protected)"
- Any new files/directories added to `template/` in future versions automatically sync to existing projects
- `setup.sh` existing-install path now delegates to `update.sh` (single source of truth)
- `/ship-update` command rewritten to use `update.sh` — no duplicate sync logic

### Changed — Setup & Update
- `setup.sh`: copies SwiftUI core + Swift essentials automatically for iOS projects, copies all framework refs (or selective via `SHIP_FRAMEWORKS` env var)
- `update.sh`: generic recursive sync, `--add-framework` flag for selective framework addition

### Previous in this version — Apple HIG Deep Integration: 24 Patterns + Foundations + UX Writing & Accessibility

### Added — Platform-Aware Design (ux-principles.md Section 5)
- 15 new universal principles distilled from 24 Apple HIG pages
- Control Hierarchy, Thumb Zone, System Preferences, Device Capabilities
- Onboarding, Smart Data Entry, Feedback Hierarchy, Loading & Launching
- Modality, Settings, Charts & Data
- UX Writing: voice/tone, action-oriented labels, clear errors, empty states, language patterns
- Accessibility: contrast ratios, tap targets, keyboard nav, reduced motion, color-independence
- Inclusion: plain language, gender-neutral copy, people-first disability language, avoid stereotypes
- Branding: defers to content, accent color, standard patterns first, no logo spam
- All with incorrect/correct code examples matching existing ux-principles style

### Added — App Lifecycle Patterns (hig-ios.md Section 8)
- Onboarding with TipKit (popover, annotation, hint styles) + code example
- Account management: Sign in with Apple, passkeys, account deletion requirement
- Notifications: 4 interruption levels table (passive/active/time-sensitive/critical) with rules
- Multitasking: save/restore state, audio interruption handling, background task completion
- Settings: zero-settings goal, ⌘-Comma keyboard shortcut, respect systemwide settings
- Haptics expanded: 9 pattern types with weights and use cases (impact×5 + notification×3 + selection)
- Swift Charts: mark types, accessibility labels, consistent chart types, interactive overlay

### Added — iOS Foundations (hig-ios.md Section 9)
- Extended Typography: min sizes per platform, avoid light weights, UIFontMetrics for custom fonts, emphasized weights
- Extended Color: system vs grouped background hierarchy, Liquid Glass color rules (iOS 26+), foreground color table
- Dark Mode: base vs elevated backgrounds, no app-specific toggle, test with Increase Contrast + Reduce Transparency
- Materials: Liquid Glass (regular/clear variants, don't use in content layer), standard material thicknesses
- Images: @2x/@3x scale factors, SVG/PDF for icons, color profiles, prefer SF Symbols
- Layout: size classes (compact/regular per device), iPad NavigationSplitView, convertible tab bar, backgroundExtensionEffect

### Changed — Agent Routing Updated
- team.md: Arc reads ux-principles.md Section 5 for writing, accessibility, inclusion
- team.md: Dev reads hig-ios.md Sections 2-6 + 8-9 (includes foundations)
- team.md: Pol now reads Section 5 for writing and branding rules
- CHEATSHEET.md: UX Principles count updated to 35, HIG sections expanded with Foundations

---

## 2026.03.20b — Zero-Prompt Setup, Apple HIG, Product Intelligence, Institutional Memory

### Added — Apple HIG Reference for iOS/SwiftUI
- New `references/hig-ios.md` — concrete specs from Apple's Human Interface Guidelines
- Navigation patterns (tab bar, NavigationStack, sheets) with when-to-use rules
- Layout & safe areas (device dimensions, margins, safe area rules)
- Dynamic Type scale (all 11 text styles with sizes, weights, usage)
- Semantic color system (backgrounds, labels, accents) with dark mode support
- Touch & interaction (44pt targets, standard gestures, haptic feedback patterns)
- Spring animations (response/damping parameters, not CSS easing)
- System components (List, Form, NavigationStack, SF Symbols) with "use this, not that" table
- App Store rejection common causes checklist
- Only loaded when tech stack includes SwiftUI/iOS — web projects skip it

### Changed — Zero-Prompt Setup + Default Mode
- `setup.sh` is now fully zero-prompt — no interactive questions at all
- Product name, description, and tech stack all gathered by `/team` on first run inside Claude Code
- Eliminates terminal multiline paste issues entirely — all context gathering happens in conversation
- `/team` detects `SHIP_SETUP` comment markers in CLAUDE.md and asks all missing items in one message
- Every conversation now defaults to `/team` mode — no need to invoke it explicitly
- `update.sh` also zero-prompt — accepts directory as argument

### Added — /health Command
- Dedicated slash command for project health checks
- Runs Vi → Arc → Crit → Biz → Eye health check flow
- Shows up in autocomplete instead of requiring `/team health check`

### Added — /ship-update Command
- Update Ship Framework from inside Claude Code — no terminal needed
- Pulls latest, compares versions, shows changelog, updates commands + references
- Replaces `bash update.sh` as the primary update method (15 total commands)

---

## 2026.03.20 — Product Intelligence, Institutional Memory, Engineering Hardening, View Transitions

### Added — Decision Log (Rule #14)
- New `DECISIONS.md` template — agents write automatically after every significant decision
- One-way door (irreversible, think carefully) vs two-way door (reversible, decide fast) classification
- /team reads at session start, logs after founder decisions and agent disagreements
- Arc logs architecture decisions, Retro reviews weekly
- Disagreement rule updated: classify door type before deciding

### Added — Context File (Institutional Memory)
- New `CONTEXT.md` template — persistent project knowledge across sessions
- Sections: Tech Learnings, Product Learnings, Patterns, Active Experiments
- Bug writes after fixes, Arc writes after planning, Retro writes after retros
- /team reads at session start — session 10 is as informed as session 1
- "Taking Over" flow now starts by reading CONTEXT.md and DECISIONS.md

### Added — Post-Launch Loop (Measurement Plans)
- Cap writes Phase 9: Measurement Plan after every ship
- Records: feature, metric, how to measure, when to check, success/failure thresholds
- Filed to DECISIONS.md and CONTEXT.md Active Experiments
- Retro enforces: surfaces due measurements every weekly retro, never drops them
- Vi's success metric now includes how to verify, when to check, what failure looks like

### Added — Scope Guard (Rule #15)
- /team checks every task against Arc's approved build order before dispatching Dev
- Unplanned work gets flagged: backlog it, swap a planned item, or override
- Overrides logged to DECISIONS.md — intentional, not accidental creep
- Arc adds time appetite per build order item — fixed time, variable scope
- If item exceeds appetite: "Cut scope or extend?" — no silent extensions

### Added — Vi Upgrade: PMF + North Star + Growth
- Item 9: PMF Signal — Sean Ellis "very disappointed" survey for existing products, reference customer targets for new products
- Item 10: Growth Mechanism — viral, content, product-led, or paid. Pick the primary loop
- Item 7 upgraded: Success Metric becomes North Star approach — measure value delivered, not captured
- Brief stays under 300 words — items 9-10 are one sentence each

### Added — Biz Upgrade: Pricing Strategy
- Expanded from 5 steps to 9 — Biz becomes a business strategist, not just a payment integrator
- Step 1: Willingness-to-pay conversations before suggesting a price
- Free-tier strategy: sample premium features in the free experience
- Self-serve ceiling: flags when pricing suggests sales-led motion (~$10K)
- Pricing iteration: revisit every 6 months, grandfather existing users

### Added — Growth Threading (Vi + Cap)
- Vi defines growth mechanism upfront (item 10 in product brief)
- Cap checks growth basics at ship time: sharing, invite flow, SEO, attribution
- No new agent — growth is a thread through existing team, not a separate role

### Added — View Transitions API Reference
- CSS-native shared element transitions added to `animation-css.md`
- `view-transition-name`, `::view-transition-group()`, `::view-transition-old/new()` with code examples
- When to use (lightbox, page transitions, state changes) and when not to (high-frequency, Framer Motion available)
- Connects to Pattern 4 (shared element transition) in `animation.md`

### Updated
- `template/CLAUDE.md` — Rules #14-15, Vi items 9-10, Biz 5→8 steps, Cap 7→9 phases, disagreement rule, workflow mentions
- `template/DECISIONS.md` — New template file
- `template/CONTEXT.md` — New template file
- `template/.claude/commands/team.md` — Reads DECISIONS.md + CONTEXT.md at start, scope guard, decision logging
- `template/.claude/commands/architect.md` — Logs to DECISIONS.md + CONTEXT.md, appetite per item
- `template/.claude/commands/visionary.md` — PMF, North Star, growth mechanism, measurement timing
- `template/.claude/commands/money.md` — Expanded to 9-step pricing strategy
- `template/.claude/commands/ship.md` — Phase 9 (measurement plan), growth checks in Phase 4
- `template/.claude/commands/retro.md` — Reads DECISIONS.md, checks measurement plans, writes CONTEXT.md
- `template/.claude/commands/fix.md` — Writes to CONTEXT.md after fixes

---

## 2026.03.20a — Engineering Hardening: TDD, Verification, Systematic Debugging, Plan Expansion, Parallel Dispatch, Worktrees, Branch Finishing, Skill Conflict Detection

### Added — Verification Before Completion (Rule #12)
- Universal rule: never claim something works without running the verification command and showing output
- Reinforced in Dev (build.md), Test (qa.md), and Cap (ship.md)
- For changes under 10 lines, manual check is acceptable; full suite for anything larger

### Added — Skill Conflict Detection (Rule #13)
- /team checks for installed external skills that overlap with team agents at session start
- Covers all agents: Vi, Arc, Dev, Bug, Crit, Pol, Test, Cap, Eye
- Warns once, then team agents take priority over external skills in their domains
- Prevents skills like Superpowers' brainstorming from hijacking Vi's product thinking role

### Added — TDD Enforcement
- Dev (build.md): test-first is the default for new functions, bug fixes, behavior changes
- Red-green-refactor cycle with iron rule: code before test = delete and start over
- Skip TDD for config, pure layout, generated code, or when founder says "skip tests"
- Test (qa.md): TDD verification check — flags when Dev wrote tests after code

### Added — Plan Expansion
- Arc's plan stays under 500 words (overview for the founder)
- After founder approves, /team auto-runs a Plan Expansion pass for `[COMPLEX]` items
- Expands into bite-sized steps: file map, test-first steps, exact paths, verification commands
- Founder doesn't see expansion unless they ask — it's Arc briefing Dev

### Added — Systematic Debugging (/fix rewrite)
- Bug keeps patient teacher personality, gains 4-phase methodology
- Phase 1: Investigate (translate, reproduce, check changes, trace data flow)
- Phase 2: Find the pattern (compare working vs broken code)
- Phase 3: Hypothesis (one change at a time, no stacking fixes)
- Phase 4: Fix and verify (failing test, fix root cause, show evidence, teach one thing)
- 3-strikes rule: 3+ failed fixes = architectural problem, route to Arc

### Added — Git Worktrees
- Arc recommends worktrees for features touching 3+ files across different directories
- Dev (build.md): worktree workflow with baseline verification
- Cap (ship.md): worktree cleanup in Phase 0

### Added — Branch Finishing (Phase 0 in /ship)
- New Phase 0 before deployment: resolve branch state
- Options: merge to main, create PR, keep branch
- Auto-merges when unambiguous; presents options when multiple branches exist
- Verifies tests on merged result before proceeding

### Added — Parallel Dispatch
- /team can dispatch 3+ independent tasks in parallel (fresh subagent per task)
- Each subagent gets full task text, context, constraints, expected output
- Verified after each: run tests, check conflicts, mark complete
- Auto-selects: defaults to sequential, switches to parallel for independent tasks
- Rule #2 updated: "one feature at a time" becomes default-with-exception

### Updated
- `template/CLAUDE.md` — Rules #12-13, updated Bug/Dev/Arc/Team sections
- `template/.claude/commands/fix.md` — Complete rewrite (was 16 lines, now ~80)
- `template/.claude/commands/build.md` — TDD rules, verification, worktree workflow
- `template/.claude/commands/architect.md` — Plan expansion markers, isolation recommendation
- `template/.claude/commands/team.md` — Skill conflict detection, plan expansion, parallel dispatch
- `template/.claude/commands/qa.md` — TDD verification check, verification rule
- `template/.claude/commands/ship.md` — Phase 0 (branch finishing), verification rule
- `CHEATSHEET.md` — TDD, verification, conflict detection sections

### How to update
```bash
bash ship-framework/update.sh
```
This updates your slash commands, references/, cheatsheet, and version stamp. Your CLAUDE.md content and TASKS.md are untouched.

---

## 2026.03.19 — UX Principles + Spring Decision Framework + Interaction State Checks

### Added — UX Principles
- `references/ux-principles.md` — 20 UX principles in 4 groups with incorrect/correct code examples
- **Making Decisions Easy:** Hick's Law, Miller's Law, Cognitive Load, Progressive Disclosure, Tesler's Law, Pareto Principle
- **Making Interactions Work:** Fitts's Law (hit area expansion), Doherty Threshold (<400ms), Postel's Law (flexible input), Goal Gradient (show progress)
- **Making Layout Communicate:** Proximity, Similarity, Common Region, Uniform Connectedness, Von Restorff, Prägnanz, Serial Position
- **Making Experiences Stick:** Peak-End Rule, Zeigarnik Effect, Jakob's Law, Aesthetic-Usability Effect
- Based on [Jon Yablonski's Laws of UX](https://lawsofux.com/) and [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/)

### Added — Spring Decision Framework
- "Springs vs Easing: When to Use Which" added to `animation.md` — user-driven → spring, system-driven → easing, time-based → linear, high-frequency → none
- "If it feels slow, shorten duration first" debugging tip
- Based on Raphael Salaja's "To Spring or Not To Spring"

### Added — Interaction State Checks
- Eye (browse.md) Phase 4: 6 interaction state checks between steps — focus ring leaking, hover persistence, scroll reset, back button state, double-click, mobile touch
- QA (qa.md) Phase 3: state transition testing for multi-step flows — focus leaking, back button, refresh mid-flow, loading state clearing, animation interruption, mobile touch

### Added — Agent Collaboration
- All review agents (Crit, Pol, Eye, QA) reference previous agents first, then read TASKS.md, and stay in their lane (only Dev writes code)
- Universal rule: any agent that produces action items saves them to TASKS.md before handoff
- Reordered flow: build → crit → polish → browse → qa → ship (fix UX first, polish second, verify last)
- Scaffolding rule restored in build.md (move SF files out, scaffold, move back)

### Updated
- `template/.claude/commands/architect.md` — reads ux-principles for screen planning
- `template/.claude/commands/build.md` — reads ux-principles for UI interactions, scaffolding rule
- `template/.claude/commands/critic.md` — reads ux-principles for HEART psychology
- `template/.claude/commands/polish.md` — reads ux-principles for layout craft
- `template/.claude/commands/visionary.md` — reads Peak-End Rule for magic moment
- `template/.claude/commands/team.md` — ux-principles in CRITICAL section, updated flow order
- `template/.claude/commands/browse.md` — interaction state checks, stays in lane
- `template/.claude/commands/qa.md` — state transition testing, stays in lane
- CHEATSHEET.md: UX Principles section
- README.md: UX Principles section, updated file structure

### How to update
```bash
bash ship-framework/update.sh
```
This updates your slash commands, references/, cheatsheet, and version stamp. Your CLAUDE.md content and TASKS.md are untouched.

---

## 2026.03.18 — Component Architecture + Animation Gaps + Setup Improvements

### Added — Animation Principles & Gap Fixes
- 9 animation principles added to `animation.md` Section 1: anticipation, staging, follow-through, secondary action, squash & stretch, exaggeration, arcs, solid drawing, appeal — based on Disney's 12 Principles adapted for UI, with technique foundations from [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/)
- 3 new "When NOT to Animate" rules: context menus (no entrance), keyboard navigation (always instant), high-frequency interactions (zero animation)
- Exit-matches-initial golden rule: exit animation properties should mirror enter
- Stagger max tightened to 30-50ms per item (was 50-100ms)
- Spring velocity preservation for drag gestures
- Pattern 5 (Dynamic Resize) strengthened with container gotchas: guard initial zero, callback ref, two-div loop warning, transition delay for natural feel, overflow hidden
- Advanced AnimatePresence patterns added to `animation-framer-motion.md`: useIsPresent, usePresence + safeToRemove, nested exit coordination with propagate prop
- AnimatePresence mode "wait" duration warning added

### Added — Component Architecture
- `references/components.md` — headless component architecture reference
- Three-layer model: primitives (Base UI) → styled components (shadcn) → product components (yours)
- Layering rule: design system overrides where it has opinions, headless primitives fill gaps
- Stack-agnostic Section 1 (composition thinking) + React-specific Section 2 (Base UI + shadcn)
- Anti-patterns: don't fight primitives, don't mix layers, don't rebuild accessibility
- Web App stack default updated to shadcn/ui (Base UI)

### Added — Extensible References
- `references/README.md` — guide for adding custom references (design system, API patterns, domain rules)
- Design system template inline — tokens, typography, spacing, component rules, patterns
- Custom References section in CLAUDE.md template — routing notes tell agents when to read what
- Framework references are always loaded; user references override where they have opinions

### Added — Setup Improvements
- `/team` first-run detection: checks for existing code, routes to Vi (fresh) or asks about assessing (existing)
- `setup.sh` simplified: 3 questions (name, description, stack) — stage, directory, Playwright questions removed
- Playwright installs automatically (graceful fail if no Node.js)
- CLAUDE.md conflict handling: previous Ship Framework install → updates safely; existing CLAUDE.md → appends, never overwrites
- Directory passed as argument: `bash setup.sh ./my-project`
- Without-terminal setup guide in README

### Updated
- `template/.claude/commands/architect.md` — component architecture spec
- `template/.claude/commands/build.md` — component architecture reference
- `template/.claude/commands/critic.md` — adoption + accessibility checks
- `template/.claude/commands/browse.md` — visual component consistency
- `template/.claude/commands/polish.md` — keyboard nav, focus states
- `template/.claude/commands/qa.md` — keyboard + screen reader testing
- `template/.claude/commands/team.md` — first-run project state detection
- `template/CLAUDE.md` — Custom References section, design system comment, Base UI stack
- `setup.sh` — simplified to 3 questions, auto Playwright, conflict handling
- `update.sh` — protects user's design-system.md during updates
- CHEATSHEET.md: Component Architecture section
- README.md: Updated setup, component architecture section, without-terminal guide

### How to update
```bash
bash ship-framework/update.sh
```
This updates your slash commands, references/, cheatsheet, and version stamp. Your CLAUDE.md content and TASKS.md are untouched.

---

## 2026.03.17 — Animation Reference

### Added
- `references/animation.md` — stack-agnostic animation reference with 4 sections
- **Section 1: Design Principles** — motion budget (limit competing patterns per screen, not element count), easing table, golden rules, spring configs, motion hierarchy
- **Section 2: Audit Checklist** — timing, easing, performance, accessibility, balance, and feel checks
- **Section 3: Build Rules** — CSS-first foundations (universal, works in any stack) + Framer Motion patterns (React). Data-attribute triggers, CSS custom properties for dynamic values, keyframe animations
- **Section 4: Pattern Library** — 8 reusable foundations based on Emil Kowalski's "Animations on the Web": reveal on hover, stacking & positioning, staggered reveal, shared element transition, dynamic resize, directional navigation, inline expansion, element-to-view expansion
- Motion budget concept: 1-2 simultaneous motion patterns per screen. A staggered group counts as one pattern
- 3 deep-dive reference files (loaded conditionally to keep context lean):
  - `animation-css.md` — transforms, transitions, keyframes, clip-path, data-attribute patterns (universal)
  - `animation-framer-motion.md` — full API: components, AnimatePresence, variants, layout, gestures, drag, hooks (useScroll, useInView, useMotionValue, useSpring), MotionConfig (React only)
  - `animation-performance.md` — 60fps target, GPU properties, will-change, DevTools monitoring, reduced motion testing on each OS, focus management, accessible animation guidelines (universal)
- Crit added as 6th agent checking animation balance
- Arc's motion system now emphasizes restraint alongside spec
- Dev references pattern library as learning material (adapt, don't copy)
- CHEATSHEET.md: Motion Budget quick reference with hierarchy table
- README.md: Animation Reference section, updated Arc and Crit descriptions

### Updated
- `template/.claude/commands/architect.md` — motion system includes budget + pattern awareness
- `template/.claude/commands/build.md` — references Section 4 patterns + deep-dives when needed
- `template/.claude/commands/critic.md` — animation balance check + performance deep-dive
- `template/.claude/commands/browse.md` — animation audit checklist + performance deep-dive
- `template/.claude/commands/polish.md` — motion feel audit + CSS and Framer Motion deep-dives
- `template/.claude/commands/qa.md` — reduced motion testing + performance deep-dive
- `template/references/animation.md` — Section 3B trimmed to pointer (no duplication)
- `setup.sh` — copies references/ directory during project setup
- `update.sh` — copies references/ during updates

### How to update
```bash
bash ship-framework/update.sh
```
This updates your slash commands, references/, cheatsheet, and version stamp. Your CLAUDE.md content and TASKS.md are untouched.

---

## 2026.03.16 — Initial Release

### Added
- 11 agents: Vi, Arc, Dev, Crit, Pol, Cap, Eye, Test, Bug, Retro, Biz
- 13 slash commands including `/team` orchestrator and `/status`
- `setup.sh` interactive setup (3 questions → full project scaffold)
- Built-in product frameworks: JTBD, HEART, RICE
- Multi-phase workflows for Eye (6 phases), Test (8 phases), Cap (7 phases), Retro (9 steps)
- QA health score system (0-100 with severity-based deductions)
- QA tiers: Quick, Standard, Exhaustive
- Retro data analysis: shipping streak, session detection, time patterns, hotspot analysis, trend comparison
- Optional Playwright browser support for Eye and Cap (real screenshots at desktop + mobile viewports)
- Graceful degradation: screenshot mode when Playwright is installed, code mode when it's not
- Takeover route: Arc → Crit → Vi → Biz → roadmap
- Health check route: Vi → Arc → Crit → Biz → Eye → prioritized roadmap
- Date-based versioning (`YYYY.MM.DD`) with VERSION file
- Version stamped into generated CLAUDE.md footer via setup.sh
- `update.sh` for updating existing projects (updates commands + cheatsheet, never touches CLAUDE.md content or TASKS.md)
- CHEATSHEET.md quick reference card with QA health score reference
- TASKS.md persistent task board with stage-specific starter tasks
- README with detailed agent descriptions, setup + update instructions, browser support docs, file structure

### Files
```
setup.sh
update.sh
VERSION
CHANGELOG.md
CHEATSHEET.md
README.md
template/CLAUDE.md
template/.claude/commands/ (13 files)
template/references/animation.md
```
