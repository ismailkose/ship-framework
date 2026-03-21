# Changelog

All notable changes to Ship Framework are documented here. Versions use date-based format (`YYYY.MM.DD`).

To update an existing project, run `bash update.sh` — it handles everything automatically.

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
