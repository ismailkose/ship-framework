# Ship Framework — Cheatsheet

---

## Commands

| Command | When to use |
|---------|-------------|
| `/team [task]` | Default for everything. Routes to the right commands. |
| `/team continue` | Start of day. Picks up from TASKS.md. |
| `/team Take over` | Existing codebase. Assess → audit → strategy → roadmap. |
| `/plan [idea]` | Product + technical planning. Vi (product brief, JTBD, PMF, growth) + Arc (RICE build order, dual-approach plan) + Adversarial (stress test). Flags: `vi-only`, `arc-only`, `with-monetization`. |
| `/build` | Code one feature at a time. Scope enforcement before every edit, atomic commits. |
| `/review` | Quality review. Crit (HEART) + Pol (anti-slop check) + Eye (screen walkthrough) + Adversarial (challenge). Confidence scoring 0-100. Flags: `crit-only`, `pol-only`, `eye-only`. |
| `/qa` | Test + fix — 8 phases: scope, run tests, explore like a user, document issues, write tests, health score, fix loop, report. |
| `/ship` | Deploy — plan completion audit, test failure triage, coverage gate, pre-landing safety net, deploy, verify, measurement plan, TASKS.md auto-completion. |
| `/fix [error]` | Debug systematically — scope lock, investigate, pattern analysis, hypothesize with 3-strike tracking, sanitized external search, debug report. |
| `/money` | Pricing strategy — 9 steps: WTP, model, free line, price, free-tier, self-serve ceiling, implementation, iteration, disagreements. |
| `/browse` | Visual QA — alias for `/review eye-only` with screenshot mode. |
| `/retro` | Weekly retro — 10 steps: data, metrics, streak, time patterns, hotspots, task health, decision + measurement review, narrative, trends, update CONTEXT.md. |
| `/ship-update` | Update Ship Framework to latest version — pulls, compares, updates commands + references. |

---

## JTBD

Two levels — product and feature:

```
"When I [situation], I want to [motivation], so I can [expected outcome]."
```

Vi writes the product-level JTBD in /plan. Arc writes one per feature in the build order.
No JTBD = don't build it.

---

## HEART

Crit picks 2-3 per review:

| H | Happiness | Does the user feel good using this? |
|---|-----------|-------------------------------------|
| E | Engagement | How deeply do they interact? |
| A | Adoption | Can new users figure it out? |
| R | Retention | Do they come back? |
| T | Task success | Can they complete the core flow? |

Vi picks one HEART dimension as the success metric for each feature.

---

## RICE

Arc scores every item in the build order. /team uses it to break priority ties.

```
Score = (Reach × Impact × Confidence) / Effort
```

| Reach | Users affected per week | number |
|-------|------------------------|--------|
| Impact | How much it moves the needle | 3 / 2 / 1 / 0.5 / 0.25 |
| Confidence | How sure are we | 100% / 80% / 50% |
| Effort | Person-weeks to build | number |

Magic moment feature always goes first regardless of score.

---

## QA Health Score

/qa computes a health score after testing:

```
Start at 100. Critical: -25, High: -15, Medium: -8, Low: -3
```

| 90-100 | Ship it |
| 70-89 | Fix criticals and highs first |
| 50-69 | Needs work |
| Below 50 | Don't ship |

---

## Motion Budget

Arc defines, Crit checks. Limit competing patterns per screen, not element count.

| Level | Motion | Example |
|-------|--------|---------|
| Magic moment | Most expressive | Check-in completion reveal |
| Primary actions | Clear, purposeful | Navigation slide, submit confirmation |
| Secondary UI | Functional, quick | Tooltip, dropdown, toast |
| Background | Subtle | Loading skeleton, pulse |
| Repeated (50x/day) | Minimal or none | Button tap, list scroll |

**1-2 simultaneous motion patterns per screen.** A staggered group counts as one.

9 animation principles: anticipation, staging, follow-through, secondary action, squash & stretch, exaggeration, arcs, solid drawing, appeal.

8 pattern foundations: reveal on hover, stacking, staggered reveal, shared element transition, dynamic resize, directional navigation, inline expansion, element-to-view expansion.

Deep-dives (loaded only when needed): `animation-css.md` (universal, includes View Transitions API), `animation-framer-motion.md` (React, includes advanced AnimatePresence), `animation-performance.md` (universal).

Checked across pipeline: Arc specs the budget in /plan → Dev builds in /build → Pol + Eye + Crit audit in /review → Test checks accessibility in /qa

---

## Component Architecture

Three layers: **Primitives** (headless — behavior + accessibility) → **Styled** (your design tokens applied) → **Product** (your features + business logic).

**The layering rule:** Your design system overrides where it has opinions. Primitives fill the gaps.

For React web: Base UI (primitives) + shadcn/ui (styled). Native stacks use platform primitives.

Never rebuild accessibility (focus trapping, keyboard nav, ARIA) — use a primitive. Check `references/components.md`.

**Extend:** Add `references/design-system.md` with your tokens and component rules. See `references/README.md` for the template.

Checked across pipeline: Arc specs architecture in /plan → Dev builds from primitives in /build → Pol + Eye + Crit audit in /review → Test checks keyboard + screen reader in /qa

**shadcn/ui Practical Guide (Section 3, React web stacks):**

46 components in 7 categories. Install bundles:
```bash
# Forms:    form input label button select checkbox radio-group switch textarea
# Data:     table badge avatar progress skeleton calendar
# Overlays: dialog sheet popover tooltip alert-dialog drawer
# Nav:      navigation-menu breadcrumb pagination command dropdown-menu
# Layout:   card accordion tabs separator sidebar
```

Theming: HSL CSS variables in `globals.css` — `--primary`, `--secondary`, `--muted`, `--destructive`, `--accent`, `--border`, `--ring`, `--radius`. Each has a `-foreground` pair. Dark mode via `.dark` class.

Key patterns: `cn()` for class merging, CVA for variants, react-hook-form + zod for forms, wrapper components for behavior (don't modify `components/ui/`).

Review checklist (Section 3.9): theming consistency, no hardcoded hex, `cn()` usage, form validation, focus indicators.

---

## UX Principles

35 principles in 5 groups. `references/ux-principles.md`.

**Making Decisions Easy:** Hick's Law (fewer choices), Miller's Law (chunk data ~7 items), Cognitive Load (remove noise), Progressive Disclosure (basics first), Tesler's Law (system absorbs complexity), Pareto (optimize the 20%).

**Making Interactions Work:** Fitts's Law (44px targets, expand hit areas), Doherty Threshold (<400ms or fake it), Postel's Law (accept messy input), Goal Gradient (show progress).

**Making Layout Communicate:** Proximity (spacing = grouping), Similarity (same function = same look), Common Region (boundaries group), Uniform Connectedness (lines link), Von Restorff (different = remembered), Prägnanz (simplify), Serial Position (key items first/last).

**Making Experiences Stick:** Peak-End Rule (invest in endings), Zeigarnik (show incomplete), Jakob's Law (use familiar patterns), Aesthetic-Usability (polish = trust).

**Platform-Aware Design:** Control Hierarchy (primary visible, secondary discoverable), Thumb Zone (CTAs in bottom third), Respect System Preferences (dark mode, reduced motion, text size), Use Device Capabilities (camera, location, biometrics over manual input), Onboarding (value before sign-in), Smart Data Entry (pickers over text, inline validation), Feedback Hierarchy (match weight to significance), Loading & Launching (skeleton screens, restore state), Modality (only when clear benefit), Settings (smart defaults, in-context options), Charts (simple, accessible, consistent), UX Writing (voice + tone, action-oriented labels, clear errors, empty states), Accessibility (4.5:1 contrast, 44pt targets, keyboard nav, reduced motion), Inclusion (plain language, gender-neutral, people-first, no jargon), Branding (defers to content, accent color, standard patterns first).

Used across pipeline: Arc + Vi read during /plan (screen planning, magic moment, onboarding) → Dev reads during /build (patterns, Section 5) → Pol + Crit read during /review (layout, HEART, accessibility, inclusion)

---

## Apple HIG — iOS/SwiftUI (when stack includes iOS)

`references/hig-ios.md`. Only loaded for iOS/SwiftUI projects.

**Navigation:** Tab bar (max 5, 49pt), NavigationStack (push/pop, large titles), sheets (half/full, swipe dismiss). Don't mix at the same level.

**Layout:** Safe areas always respected. Status bar 59pt (Dynamic Island), nav bar 44pt, tab bar 49pt, home indicator 34pt. Margins 16pt iPhone, 20pt Pro Max.

**Typography:** Dynamic Type scale — Large Title 34pt, Title 28pt, Body 17pt, Caption 12pt. Always use `.font(.body)`, never hardcode sizes.

**Colors:** Semantic system colors (`.background`, `.primary`, `.secondary`) — auto dark mode. One tint color for the app. 4.5:1 contrast ratio.

**Touch:** 44×44pt minimum. 8pt between targets. Never disable swipe-back. Use system haptics.

**Motion:** Spring animations (response: 0.35, damping: 0.85), not CSS easing. Under 0.4s. `matchedGeometryEffect` for hero transitions.

**Components:** System first (`List`, `Form`, `NavigationStack`, `TabView`, `.sheet`, `.alert`, `.searchable`). SF Symbols for icons.

**App Lifecycle:** Onboarding (TipKit for discovery, delay sign-in), Accounts (Sign in with Apple, passkeys, deletion required), Notifications (4 levels: passive/active/time-sensitive/critical), Multitasking (save/restore state, handle audio interruptions), Settings (smart defaults, ⌘-Comma, task-specific in-context), Haptics (9 patterns: 5 impact weights + success/warning/error/selection), Swift Charts (BarMark/LineMark/PointMark, accessibility labels, consistent types).

**Foundations:** Extended Typography (min sizes, avoid light weights, custom font scaling with UIFontMetrics), Extended Color (system vs grouped backgrounds, Liquid Glass color, foreground color table), Dark Mode (base vs elevated, no app-specific toggle, test with Increase Contrast), Materials (Liquid Glass regular/clear variants, standard material thicknesses), Images (@2x/@3x, SVG/PDF for icons, color profiles), Layout (size classes compact/regular, iPad NavigationSplitView, convertible tab bar, backgroundExtensionEffect).

**Design Review Checklists (Section 10):** Navigation, Typography, Color, Touch, Materials/Liquid Glass, Accessibility, App Lifecycle — Eye uses during `/review`.

---

## SwiftUI Core Implementation (when stack includes iOS)

`references/swiftui-core.md`. Always loaded for iOS/SwiftUI projects.

**Navigation Implementation:** NavigationStack + NavigationPath (programmatic push/pop/pop-to-root), route enum pattern, router pattern (@Observable @MainActor, per-tab stacks), NavigationSplitView (iPad), sheet routing (.sheet(item:), enum-driven, .presentationSizing), deep links (.onOpenURL, universal links, AASA).

**Swift 6.2 Concurrency:** Default MainActor isolation (SE-0466), @concurrent for background work, nonisolated(nonsending) default, Task.immediate (SE-0472), actor isolation rules, Sendable rules, structured concurrency (async let, TaskGroup), synchronization primitives (Mutex, OSAllocatedUnfairLock, Atomic), actor reentrancy.

**Liquid Glass Implementation:** .glassEffect() API (regular/clear/tint/interactive), GlassEffectContainer (grouping, spacing, blending), morphing transitions (glassEffectID + @Namespace), glassEffectUnion, button styles (.glass/.glassProminent), scroll edge effects, backgroundExtensionEffect, ToolbarSpacer.

**Animation:** Spring animations (preferred), transitions, matchedGeometryEffect, PhaseAnimator, KeyframeAnimator, Reduce Motion support.

**Gestures:** Tap, long press, drag, MagnifyGesture, RotateGesture, gesture composition (simultaneous/sequenced/exclusive).

**Layout:** layoutPriority, ViewThatFits, Grid, custom Layout protocol, ContentUnavailableView, ScrollView enhancements.

**Architecture:** @Observable + @State ownership, Environment for DI, Observations (SE-0475).

**UIKit Interop:** UIViewRepresentable, UIViewControllerRepresentable, UIHostingController.

**Review Checklists (Section 9):** Navigation, Concurrency, Liquid Glass, Animation, Architecture — Eye + Dev self-check.

---

## Swift Essentials (when stack includes iOS)

`references/swift-essentials.md`.

**Swift Language:** Result builders, property wrappers, macros, opaque types (some/any), pattern matching, typed throws, key protocols (Hashable, Identifiable, Codable, Sendable).

**Codable:** JSONDecoder/JSONEncoder setup, custom CodingKeys, custom init(from:)/encode(to:), nested containers, null/missing key handling.

**Swift Testing:** @Test macro, #expect/#require, @Suite, parameterized tests, traits, async support, XCTest migration.

---

## iOS Framework References (conditional)

`references/frameworks/`. 40 framework-specific references. Only read when building features that use that framework. Each has: triage, core API, code examples, common mistakes, review checklist.

**Data & Storage:** swiftdata, cloudkit, contacts, eventkit
**App Experience:** storekit, app-intents, live-activities, widgetkit, app-clips, alarmkit
**Auth & Notifications:** authentication, push-notifications, permissionkit
**AI & ML:** coreml, vision-framework, speech
**Media:** photos-camera, musickit, passkit
**Hardware:** core-bluetooth, core-motion, core-nfc, pencilkit, realitykit
**Platform:** callkit, energykit, homekit, shareplay, weatherkit
**Engineering:** networking, security, accessibility, localization, background-processing, debugging, device-integrity, metrickit, app-store-review

Add more later: `bash update.sh ~/MyApp --add-framework healthkit,storekit`

---

## Disagreements

1. State what the previous agent decided
2. State why you disagree
3. Offer the alternative
4. Minor → /team decides, explains in one sentence
5. Significant → /team stops, asks you
6. Priority tie → RICE score wins, show the math

---

## TDD (Test-Driven Development)

Dev's default for new functions, bug fixes, and behavior changes:

```
RED:    Write failing test → run → verify fails for the right reason
GREEN:  Write minimal code → run → verify passes
REFACTOR: Clean up → keep tests green → commit
```

Skip for: config files, pure layout, generated code, or when founder says "skip tests."
Iron rule: wrote code before the test? Delete it. Start with the test.

---

## Verification Rule

Rule #12: Never claim something works without running the command and showing the output.

No "should work." No "looks correct." Run it. Show it. Then claim it.

For changes under 10 lines: manual check with explanation is OK.

---

## Skill Conflict Detection

Rule #13: Team agents own their domains. If external skills overlap, team warns once and overrides.

/team checks at session start for skills that overlap with Vi, Arc, Dev, Bug, Crit, Pol, Test, Cap, or Eye.

---

## Decision Log

Rule #14: Every significant decision gets logged to DECISIONS.md automatically.

Format: date, decision, type (one-way door / two-way door), reasoning, who called it.

One-way door = irreversible, spend more time. Two-way door = reversible, decide fast.

/team reads at session start. Retro reviews weekly.

---

## Scope Guard

Rule #15: No unplanned work without an explicit override.

/team checks tasks against Arc's build order. Not in the plan → backlog, swap, or override.
Arc sets appetite per item. Exceeding appetite → "cut scope or extend?"
Override = one word. Logged to DECISIONS.md.

---

## Post-Launch Loop

Cap writes a measurement plan after every ship (Phase 9):
- Feature, metric, how to measure, when to check, success/failure thresholds
- Filed to DECISIONS.md + CONTEXT.md

Retro enforces: surfaces due measurements every weekly retro. Never drops them.

---

## Context File

CONTEXT.md = institutional memory. Agents write, /team reads at session start.

- Bug writes after fixes (Tech Learnings)
- Arc writes after planning (Tech Learnings)
- Retro writes after retros (Product Learnings, Patterns)
- Cap writes after shipping (Active Experiments)

---

## PMF + North Star + Growth

Vi's brief now includes:
- Item 9: PMF Signal — "Would 40%+ be very disappointed without this?"
- Item 10: Growth Mechanism — viral, content, product-led, or paid
- Item 7: North Star metric — value delivered, not captured

Cap checks growth basics at ship time: sharing, invite flow, SEO, attribution.

---

## Pricing Strategy

Biz expanded from 5 to 9 steps:
1. WTP first (ask before guessing)
2-4. Model, free line, price point
5. Free-tier: sample premium in free
6. Self-serve ceiling (~$10K)
7. Implementation (Stripe)
8. Iterate every 6 months
9. Disagreements

---

## Rules

1. No code before /plan is done
2. One feature at a time (unless /team dispatches 3+ independent tasks in parallel)
3. Commit before starting the next thing
4. Takes more than a day → break it down
5. Working > pretty
6. Real users > hypothetical users
7. Agents disagree → you decide
8. Every agent references what came before
9. Every feature needs a JTBD + HEART metric before building
10. Always flag cost implications
11. Team orchestrates — external skills supplement, not replace
12. Verify before claiming done — evidence, not hope
13. Team agents own their domains — external skills don't override
14. Log every significant decision to DECISIONS.md — one-way/two-way door
15. No unplanned work without override — scope guard enforces the plan
16. 3-attempt retry limit — after 3 failures, escalate
17. Screenshot evidence required — Eye defaults to NEEDS WORK without proof
18. Mid-build status — progress update after each completed task
19. Apple API first — no custom builds when a system API exists
20. Completeness is cheap — finish the last 10%, DONE or BLOCKED
21. Search before building — codebase → references → vendor docs
22. Atomic commits — one concern per commit
23. One decision per question — no compound questions
24. Anti-sycophancy — no validation without substance, banned AI vocabulary
