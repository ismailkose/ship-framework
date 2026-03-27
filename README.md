 # Ship Framework

**v2026.03.27** · **An AI product team for one-person teams.**

You're one person. You handle product, design, business, and decisions. You need engineering — that's what Claude Code is for. But raw Claude Code is like having a brilliant engineer with no product sense, no design eye, and no business context. It builds what you say, not what you need.

This framework gives Claude Code structure. It turns one AI into a team of opinionated specialists who challenge each other, catch problems early, and keep you shipping. You're the CEO. They report to you.

---

## Setup (1 minute)

```bash
git clone https://github.com/ismailkose/ship-framework.git
bash ship-framework/setup.sh
```

Zero prompts. The script copies all files and installs Playwright — no questions asked:

```
Ship Framework v2026.03.27 — Setup

✓ Created CLAUDE.md (your product rules — never overwritten)
✓ Created .claude/team-rules.md (agent definitions — auto-synced on update)
✓ Created .claude/commands/ (11 slash commands)
✓ Created references/ (animation, components, UX principles)
✓ Created references/frameworks/ (conditional framework references)
✓ Created CHEATSHEET.md
✓ Created TASKS.md
✓ Created DECISIONS.md
✓ Created CONTEXT.md
✓ Installed Playwright

Next step: Open Claude Code in your project directory and type:

  /team I want to build [your idea]
```

Every conversation defaults to `/team` mode — no need to invoke it explicitly. On first run, it asks for your product name, description, and tech stack inside Claude Code where you can paste freely, no terminal limitations. That's where your product context lives.

That's it. Your team is running.

**Already have a CLAUDE.md?** Setup detects it. If it's from a previous Ship Framework install, it updates commands and references. If it's your own, it appends Ship Framework below your existing content.

**Specifying a directory:** `bash ship-framework/setup.sh ./my-project`

**Without terminal:** Download the ZIP from GitHub, copy `template/.claude/commands/` to your project's `.claude/commands/`, copy `template/references/` to `references/`, copy `template/ship-update.sh` to your project root, copy `CHEATSHEET.md`, and edit `template/CLAUDE.md` manually. Then open Claude Code and type `/team`.

---

## Updating

From inside Claude Code, just type:

```
/ship-update
```

That's it. No terminal needed, no external clone required. The update script fetches the latest from GitHub into a temp directory, syncs your commands, references, and cheatsheet, then cleans up. It never touches your CLAUDE.md content, TASKS.md, or project files.

**Prefer terminal?** Run `bash ship-update.sh` from your project root. Same result.

**Older installs (before v2026.03.27)?** If your project doesn't have `ship-update.sh` yet, `/ship-update` will download it for you automatically.

**Checking your version:** Look at the bottom of your CLAUDE.md — it shows the Ship Framework version.

**Watching for updates:** Star or watch the [repo](https://github.com/ismailkose/ship-framework) to get notified when new versions drop.

Ship Framework uses date-based versioning (`YYYY.MM.DD`). Each release is tagged with the date it shipped.

---

## The Team

| Command | Personas | Role |
|---------|----------|------|
| `/team` | — | **Orchestrator** — give it any instruction, it delegates to the right commands |
| `/plan` | Vi + Arc + Adversarial | **Product + Technical Planning** — Vi rips ideas apart (JTBD, magic moment, PMF, growth), Arc builds the technical plan (RICE, dual-approach, dependencies), Adversarial stress-tests both. Flags: `vi-only`, `arc-only`, `with-monetization` |
| `/build` | Dev | **Builder** — writes code one feature at a time, scope enforcement before every edit, atomic commits |
| `/review` | Crit + Pol + Eye + Adversarial | **Quality Review** — Crit reviews against HEART dimensions, Pol runs the anti-slop check, Eye walks every screen, Adversarial challenges everything. Confidence scoring 0-100. Flags: `crit-only`, `pol-only`, `eye-only` |
| `/qa` | Test | **Tester** — 8-phase QA: scope, tests, explore like a user, document issues, write tests, health score, fix loop, report |
| `/ship` | Cap | **Release Manager** — plan completion audit, test failure triage, coverage gate, pre-landing safety net, deploy, verify, measurement plan, TASKS.md auto-completion |
| `/fix` | Bug | **Debugger** — scope lock, investigate, pattern analysis, hypothesize with 3-strike tracking, sanitized external search, debug report |
| `/money` | Biz | **Business Brain** — 9-step pricing strategy: WTP, model, free line, price, free-tier, self-serve ceiling, implementation, iteration |
| `/browse` | Eye | **Visual QA** — alias for `/review eye-only` with screenshot mode |
| `/retro` | Retro | **Retrospective** — 10-step weekly review: git data, metrics, shipping streak, time patterns, hotspots, task health, decision + measurement review, narrative, trends, update CONTEXT.md |
| `/ship-update` | — | **Update framework** — pulls latest, updates commands + references from inside Claude Code |

**They disagree with each other.** Vi might want a feature that Arc thinks is over-engineered. Dev might build something that Crit finds confusing. Pol might want polish that Cap thinks delays launch. The Adversarial voice attacks everything. When they disagree, they present both sides — you make the call.

That tension is the whole point.

---

## Built-In Frameworks

The team uses three product frameworks so decisions are structured, not gut-feel:

- **Jobs To Be Done (JTBD)** — Vi writes a job statement for every feature: *"When I [situation], I want to [motivation], so I can [expected outcome]."* No vague personas.
- **HEART Framework** — Crit reviews against Google's UX quality dimensions: Happiness, Engagement, Adoption, Retention, Task success. Picks the 2-3 most relevant per review.
- **RICE Scoring** — Arc scores every item in the build order: (Reach × Impact × Confidence) / Effort. When agents disagree on priority, RICE is the tiebreaker.

These frameworks are woven into the agents — you don't need to invoke them manually.

---

## Product Intelligence

The team builds institutional memory and closes loops that most solo teams leave open:

- **Decision Log** (`DECISIONS.md`) — Every significant decision is logged automatically: what, why, who called it, and whether it's a one-way door (irreversible) or two-way door (reversible). Retro reviews weekly. Three weeks later you know exactly why Supabase was chosen over Firebase.
- **Context File** (`CONTEXT.md`) — Persistent knowledge across sessions. Bug writes after fixes, Arc writes after planning, Retro writes after reviews. Session 10 is as informed as session 1.
- **Post-Launch Loop** — Cap writes a measurement plan after every ship: what to measure, when to check, what success looks like. Retro enforces it weekly. No feature goes unmeasured.
- **Scope Guard** — /team checks every task against Arc's build order. Unplanned work gets flagged: backlog, swap, or override. No accidental scope creep.
- **PMF + Growth** — Vi checks for product-market fit signals and defines a growth mechanism before building. Cap verifies growth basics at ship time.
- **Pricing Strategy** — Biz starts with willingness-to-pay, not guessing. Includes free-tier strategy, self-serve ceiling, and 6-month iteration cadence.

---

## Engineering Rigor

The team enforces engineering discipline automatically — no extra commands needed:

- **TDD (Test-Driven Development)** — Dev writes failing tests first, then minimal code to pass. Code before test = delete and start over. Skip TDD for config, layout, or when you say "skip tests."
- **Verification Before Completion** — Every agent must run the verification command and show output before claiming success. No "should work" — evidence only.
- **Systematic Debugging** — Bug investigates root cause before fixing. Scope lock → investigate → pattern analysis → hypothesize with 3-strike tracking → fix. If 3 hypotheses fail, it escalates to `/plan arc-only`.
- **Dual-Approach Planning** — Arc produces Minimal and Clean approaches with explicit tradeoffs. Both must follow platform reference guardrails. "Minimal" means fewer features, not fewer best practices.
- **Parallel Dispatch** — When the plan has 3+ independent tasks, /team dispatches fresh agents per task for faster iteration. Each agent is verified before moving on.
- **Git Worktrees** — For complex features touching 3+ files, Arc recommends isolated worktrees with verified baselines.
- **Branch Finishing** — Cap resolves branch state before deploying: merge, PR, or keep. Verifies tests on merged result.
- **Skill Conflict Detection** — /team warns when external skills overlap with team agents. The team always takes priority in its domains.
- **Prompt Sharpening (Rule 0)** — Before doing anything, agents restate your request in one clear sentence. If it's vague, they ask ONE clarifying question. If it's clear enough, they assume and move on. Works on every interaction — slash commands and direct typing.
- **3-Attempt Retry Limit (Rule 16)** — When Dev can't get something working, retry up to 3 times with different approaches. After 3 failures, escalate to Arc for a new approach or to you for a decision. No spinning.
- **Screenshot Evidence Required (Rule 17)** — Eye defaults to "NEEDS WORK" on UI changes unless there's actual screenshot proof. No "looks correct based on the code."
- **Mid-Build Status (Rule 18)** — During multi-task builds, progress update after each completed task. You never have to ask "where are we?"
- **Apple API First (Rule 19)** — No custom builds when a system API exists. Before building any custom component, agents check Apple documentation first. If Apple provides it natively, use it. Eye rejects PRs that custom-build something Apple already provides.
- **No-Hack API Enforcement** — Section 6.5 of swiftui-core.md catches 18 patterns agents commonly get wrong (progressive blur, haptics, keyboard dismiss, sheet detents, focus state, toolbar visibility, containerRelativeFrame, symbolEffect, MeshGradient, overlay form, toolbar placement, scrollIndicators, @Entry macro, fill+stroke, Text concatenation, grammar agreement, ForEach enumerated, keyboard corners). Each shows the WRONG approach so agents recognize it and the CORRECT one-liner.
- **Completeness is Cheap (Rule 20)** — When a task is 90% done, finish the last 10%. No TODO comments, no "will fix later." A task is either DONE or BLOCKED.
- **Search Before Building (Rule 21)** — Three layers: codebase first, then references/, then platform vendor docs. Only build from scratch after all three come up empty. Graceful degradation when platform references don't exist yet.
- **Atomic Commits (Rule 22)** — One concern per commit. Enables git bisect. Adding a screen + its tests = one commit. Fixing two unrelated bugs = two commits.
- **One Decision Per Question (Rule 23)** — No compound questions to the founder. Each question requires exactly one decision.
- **Anti-Sycophancy (Rule 24)** — Banned phrases ("Great question!", "That's a really interesting idea!"), banned AI vocabulary (delve, robust, nuanced, etc.), lead with concern not compliment.
- **Scope Enforcement** — Before every file edit, Dev verifies the file is in the declared Build Scope. Out-of-scope edits classified as MINOR (proceed with note) or STRUCTURAL (stop and ask).
- **Review Staleness Tracking** — /review saves a hash; /ship compares HEAD against it to catch post-review changes.
- **Anti-Slop Design Check** — 22 universal items + platform-specific items (iOS 9, Web 9, Android 5) catching generic AI-generated aesthetics.
- **Confidence Scoring** — /review scores every finding 0-100. Below 50 gets filtered out. Findings classified as SAFE or RISKY.

---

## How It Works

### The Flow

```
/team (orchestrator — delegates automatically)
    |
/plan -> Vi: product brief + JTBD + North Star + PMF + growth
         Arc: RICE-scored build order + dual-approach plan
         Adversarial: stress test both
    |
/build -> Code, one feature at a time (scope enforcement + atomic commits)
    |
/review -> Crit: HEART review
           Pol: anti-slop check + design audit
           Eye: screen walkthrough + visual bugs
           Adversarial: challenge everything
           (must-fixes go back to /build, rest to TASKS.md)
    |
/qa -> Run tests, write missing tests
    |
/ship -> Plan audit + test triage + coverage gate + deploy + measurement plan
    |
/money -> Pricing strategy
```

You don't run all of them every time. `/team` figures out which commands are needed.

### Daily Workflow

```bash
# Start of day — pick up where you left off
/team continue

# New feature idea
/team I want to build a weekly email digest

# Something broke
/team [paste error]

# Quick check
/team status
```

**Once `/team` is running, just talk naturally.** You don't need to type `/team` again within the same session. Say "go ahead", "build it", "looks good, next feature", "the dashboard feels off, review it" — the team stays active and routes to the right agents automatically. You only need `/team` again when you start a new Claude Code session.

### The Task Board

`TASKS.md` is the team's memory across sessions. After every task, `/team` updates it. Next session, `/team` reads it first. Nothing gets lost.

---

## Why This Exists

When you're a one-person team, you're not "a designer" or "a PM" or "a founder" — you're everything. You need product thinking AND technical rigor AND design craft AND business sense AND the discipline to ship.

Claude Code gives you engineering. But without structure, it just builds whatever you describe — no pushback, no quality checks, no "have you thought about this?" This framework adds that structure through named personas that argue inside simple commands:

- `/plan` — Vi asks "why would anyone care?", Arc asks "will this still work at 3am?", and the Adversarial voice attacks both before a line of code is written
- `/build` — Dev codes one feature at a time with scope enforcement and atomic commits
- `/review` — Crit asks "but what if I do THIS?", Pol asks "does this feel right on a phone?", Eye screenshots the actual UI, and the Adversarial voice challenges everything
- `/ship` — Cap asks "why aren't we live yet?" and runs the safety net
- `/money` — Biz asks "how does this make money?" before it's too late
- `/retro` — Retro asks "what actually happened this week?" to keep you honest

One AI, named personas that disagree, one you making the calls.

---

## Tips from Production Use

**Use `/team` for almost everything.** It handles routing. You don't need to remember which agent does what.

**Let the disagreements play out.** When Vi wants something and Arc pushes back, that's the system working. Listen to both sides.

**TASKS.md is your source of truth.** Start every session with `/team continue`. The task board keeps you on track across days and weeks.

**One feature at a time.** Dev builds, tests, and commits one thing before moving on. Resist the urge to batch.

**Don't skip /review.** It's tempting to go straight from build to ship. Crit, Pol, and Eye find the things your users would find first.

**Customize CLAUDE.md aggressively.** Add your color tokens, component library rules, copy guidelines, API constraints. The more specific, the better every agent performs.

**The takeover sequence works.** Existing codebase? `/team Take over this project` runs `/plan arc-only` (assess) → `/review` (HEART + design + visual audit) → `/plan vi-only` (product JTBD) → `/money` (who pays) → presents options. Fastest way to orient.

**Run a health check.** Already building? `/team Health check` runs `/plan` → `/review` → `/money` for a full strategic review — product fit, tech debt, UX gaps, monetization, and visual QA in one pass.

---

## What This Is (and Isn't)

**This is:** A structured workflow for one-person teams to ship real products using Claude Code.

**This is not:** Multiple AI agents running in parallel. It's one AI wearing different hats. But the structure — forced disagreements, handoffs, multi-phase workflows, health scores, persistent task tracking — catches problems that unstructured conversations miss.

---

## File Structure

```
your-project/                    (generated by setup.sh)
  CLAUDE.md                      # Your product rules — never overwritten by updates
  TASKS.md                       # Persistent task board
  DECISIONS.md                   # Decision log (agents write automatically)
  CONTEXT.md                     # Institutional memory across sessions
  CHEATSHEET.md                  # Quick reference card
  ship-update.sh                 # Self-contained updater (no clone needed)
  .claude/
    team-rules.md                # Agent definitions + framework rules (auto-synced)
    commands/                    # 11 slash commands
  references/                    # Agent reference files (auto-read when relevant)
    README.md                    # Extension guide + design system template
    animation.md                 # Motion budget, build rules, 8 patterns
    animation-css.md             # Deep-dive: transforms, transitions, keyframes, View Transitions API
    animation-framer-motion.md   # Deep-dive: Framer Motion API (React only)
    animation-performance.md     # Deep-dive: 60fps, DevTools, reduced motion
    components.md                # Headless architecture + shadcn/ui practical guide
    ux-principles.md             # 20 UX principles with code examples
    hig-ios.md                   # Apple HIG for iOS/SwiftUI (iOS projects only)
    swiftui-core.md              # SwiftUI implementation reference (iOS projects only)
    swift-essentials.md          # Swift 6.2 language features (iOS projects only)
    design-system.md             # (you create) Your tokens, rules, patterns
    frameworks/                  # Conditional framework references
      chat-ui.md                 # Production chat UI patterns (SwiftUI + React Native + universal)
      healthkit.md               # HealthKit integration (iOS)
      storekit.md                # StoreKit / in-app purchases (iOS)
      ...                        # 46 conditional references (informed by swift-ios-skills)

ship-framework/                  (the repo itself)
  setup.sh                       # Zero-prompt setup
  VERSION                        # Current version (YYYY.MM.DD)
  CHANGELOG.md                   # What changed in each version
  README.md                      # This file
  CHEATSHEET.md                  # Template for quick reference
  template/                      # Source templates
    CLAUDE.md                    # User content template
    .claude/team-rules.md        # Framework content (synced on update)
    .claude/commands/            # 11 slash command files
    references/                  # Reference files copied to projects
    references/frameworks/       # Conditional framework references
```

---

## Animation Reference

The framework includes a stack-agnostic animation reference (`references/animation.md`) that 6 agents use automatically — no need to trigger anything.

**How it works:** Arc defines a motion system when planning (what animates, timing, easing, motion budget). Dev builds from Arc's spec using the build rules. Pol and Eye audit the feel and visuals. Test checks accessibility (`prefers-reduced-motion`). Crit checks whether animation is earning its place or just decorating.

**What's in it:** The main reference (`animation.md`) has design principles (including 9 from Disney's 12 Principles adapted for UI), motion budget, an audit checklist, CSS-first build rules, and 8 pattern foundations. Three deep-dive files provide API-level detail: `animation-css.md` (transforms, transitions, keyframes, clip-path — universal), `animation-framer-motion.md` (full Framer Motion API including advanced AnimatePresence patterns — React only), and `animation-performance.md` (60fps optimization, DevTools monitoring, reduced motion testing — universal). Agents load deep-dives only when building or reviewing animations, keeping context lean. Based on [Emil Kowalski's "Animations on the Web"](https://animations.dev/) and [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/).

**Motion budget:** The core restraint concept. Limit competing motion patterns per screen (not element count) — a staggered group of 6 cards is one pattern, that's fine. Four unrelated animations fighting for attention is four patterns, that's too much. Arc sets the budget, Crit checks it.

---

## Component Architecture

The framework includes a headless component architecture reference (`references/components.md`) that teaches agents how to think about UI components — from primitives to product features.

**The three-layer model:** Primitives (headless — behavior + accessibility, zero styling) → Styled components (your design tokens applied) → Product components (your features + business logic). For React web stacks, the recommended setup is Base UI (primitives) + shadcn/ui (styled). Native stacks use platform primitives with the same composition thinking.

**shadcn/ui practical guide (Section 3):** 46 components in 7 categories with install commands, theming system (HSL CSS variables, color roles, dark mode), the `cn()` utility, CVA variant patterns, form integration (react-hook-form + zod), composite component patterns, and a review checklist. Dev reads this when building React UI; Eye reads the checklist when reviewing.

**The layering rule:** Your design system overrides where it has opinions. Headless primitives fill the gaps. If your design system has Button and Card but not Dialog, agents use yours for Button/Card and reach for a headless Dialog primitive, styled to match your existing tokens.

**Extending with your design system:** Add `references/design-system.md` with your tokens, component rules, and patterns. Agents use your rules first, fall back to framework defaults where you're silent. See `references/README.md` for the template and extension guide.

---

## UX Principles

The framework includes 20 UX principles (`references/ux-principles.md`) — the psychological foundations behind every interface that feels right. These are the "why" behind design decisions.

**How agents use them:** Arc reads Hick's Law and Miller's Law when planning screen maps (how many options per screen, how to present data). Dev reads the code examples when building interactions (hit areas, response time, input handling). Crit reads them as the psychology behind HEART dimensions. Pol reads them when auditing spacing, hierarchy, and visual structure. Vi reads Peak-End Rule and Goal Gradient when defining the magic moment.

**What's in it:** 20 principles in 4 groups — Making Decisions Easy (Hick's, Miller's, Cognitive Load, Progressive Disclosure, Tesler's, Pareto), Making Interactions Work (Fitts's, Doherty, Postel's, Goal Gradient), Making Layout Communicate (Proximity, Similarity, Common Region, Uniform Connectedness, Von Restorff, Prägnanz, Serial Position), Making Experiences Stick (Peak-End, Zeigarnik, Jakob's, Aesthetic-Usability). Each principle has incorrect/correct code examples agents learn from. Based on [Jon Yablonski's Laws of UX](https://lawsofux.com/) and [Raphael Salaja's userinterface.wiki](https://www.userinterface.wiki/).

---

## Browser Support

Playwright is installed automatically during setup for visual QA. If it fails (no Node.js), setup continues without it.

**What it adds:** Real pixel-level screenshots at desktop and mobile viewports. Eye compares actual rendered pages against your design tokens. Cap screenshots your app before and after deploy.

**Without Playwright:** Eye and Cap still work — they review your CSS, Tailwind classes, and component code against the design system. It's a code-level audit instead of a pixel-level one.

**Adding it later:**
```bash
npm install -D @playwright/test
npx playwright install chromium
```

That's it. Eye and Cap auto-detect Playwright and switch to screenshot mode.

---

## iOS / SwiftUI References

For iOS projects, the framework includes deep references that agents read automatically when the tech stack includes SwiftUI:

**Apple HIG** (`references/hig-ios.md`) — Human Interface Guidelines foundations: typography (Dynamic Type, SF Pro, SF Mono), color (semantic system colors, accessibility contrast), layout (safe areas, readability widths), touch targets (44pt minimum), materials and Liquid Glass, accessibility, inclusion, branding, UX writing, and design review checklists.

**SwiftUI Core** (`references/swiftui-core.md`) — Implementation reference covering navigation (NavigationStack, router pattern, deep links, iOS 26 Tab APIs, toolbar enhancements, sheet/alert shorthand), Swift 6.2 concurrency (default MainActor isolation, @concurrent, structured concurrency), Liquid Glass API (.glassEffect, morphing, scroll edge effects with progressive blur), animation (spring, PhaseAnimator, KeyframeAnimator, all 10 symbol effects), gestures (MagnifyGesture, RotateGesture, composition patterns), layout (ViewThatFits, Grid, LazyVStack, .searchable with scopes), **Design Rules** (44pt tap targets, typography hierarchy, spacing grid, semantic colors, Label/LabeledContent patterns), **No-Hack API Reference** (Section 6.5 — 18 patterns agents get wrong: progressive blur, haptics, containerRelativeFrame, symbolEffect, keyboard dismiss, sheet detents, FocusState, toolbar visibility, MeshGradient, overlay trailing closure, topBarLeading/topBarTrailing, scrollIndicators, @Entry macro, fill+stroke chaining, Text interpolation, grammar agreement, ForEach enumerated), **Accessibility Quick Reference** (Dynamic Type, VoiceOver labels, color & motion, input methods), **Data Flow Rules** (@State private, @AppStorage traps, Binding rules, onChange variants), performance profiling (Instruments, `Self._printChanges()`, observation scope, ternary vs if/else, view initializer rules), architecture patterns (view composition with separate View structs, @Observable ownership, ViewModifier, @ViewBuilder, MV-first), and UIKit interop (lifecycle, UIHostingConfiguration, sizeThatFits).

**Swift Essentials** (`references/swift-essentials.md`) — Swift 6.2 language features (if/switch expressions, FormatStyle, modern collection APIs), **Modern Swift Idioms** (15 rules: replacing(), URL.documentsDirectory, static member lookup, localizedStandardContains, count(where:), Date.now, PersonNameComponents, Comparable for sorts, and more), concurrency (AsyncSequence, AsyncStream, Mutex vs Atomic decision guide, GCD prohibition, **actor reentrancy with deduplication pattern**, **10 bug patterns**, structured concurrency with async let vs task groups, cancellation patterns, bridging legacy code), Codable patterns (lossy arrays, single value containers, SwiftData integration), and Swift Testing (@Test, #expect, @Suite, confirmation, parameterized tests, exit testing, **testing gotchas**: .serialized only parameterized, confirmation must complete, .minutes not .seconds, parallel-safe defaults, **Swift 6.3 updates**: Issue.record severity, Test.cancel(), image attachments).

**47 Conditional Framework References** (`references/frameworks/`) — HealthKit, StoreKit, CloudKit, CoreML, Vision, CoreBluetooth, ARKit, Apple On-Device AI, Swift Charts, TipKit, Natural Language, WebKit, **iOS Security** (Keychain add-or-update, LAContext boolean gate vulnerability, Secure Enclave, CryptoKit, anti-patterns), and 34 more. Each file has a triage workflow, core API, code examples, common mistakes, and a review checklist. iOS framework references informed by [swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills). All copied by default; use `SHIP_FRAMEWORKS` env var for selective install or add later with `bash ship-update.sh --add-framework healthkit,storekit`.

---

## Chat UI Reference

For projects with a chat, messaging, or AI assistant interface (`references/frameworks/chat-ui.md`):

**Part 1 — Universal principles** that apply regardless of tech stack: message animation sequencing, the "blank size" problem (4 failed approaches + what works), keyboard management (6 behaviors + production edge cases), floating composer, streaming text with animation pool pattern, markdown rendering, performance principles, and shared API architecture. Based on Vercel's v0 iOS engineering blog.

**Part 2 — SwiftUI implementation** with full code examples: @Observable state, PhaseAnimator, .contentMargins(), KeyboardObserver, GlassEffectContainer, actor-based animation pool, AttributedString markdown, native menus and sheets.

**Part 3 — React Native implementation** with full code examples: Reanimated shared values, contentInset blank size, react-native-keyboard-controller, Liquid Glass, createUsePool fade system, TextInput native patch, initial scroll-to-end.

**Part 4 — Platform comparison table** mapping every pattern across SwiftUI, React Native, and Web/Other.

**Part 5 — Review checklist** for Eye: animation sequencing, blank size, keyboard edge cases, streaming, composer, performance.

---

## Two-File Architecture

Ship Framework uses a two-file split for configuration:

**CLAUDE.md** — Your content. Product name, description, tech stack, design principles, key files, custom references. This file is yours to customize and is **never overwritten** by updates. Edit it freely.

**.claude/team-rules.md** — Framework content. Agent definitions, product frameworks (JTBD, HEART, RICE), rules 0-24, workflow diagrams, and team routing. This file is **managed by Ship Framework** and synced automatically on every update. Don't edit it — your changes would be overwritten.

All 11 slash commands read both files. This way you can customize your product context without worrying about framework updates clobbering your changes.

---

## Customization

**Adding agents** — Create `.claude/commands/yourcommand.md`. Agents read both CLAUDE.md and .claude/team-rules.md automatically. Follow the pattern: name, personality, checklist, handoff.

**Design system rules** — Add a "Design System" section to CLAUDE.md with color tokens, typography, spacing. Pol enforces them.

**Domain rules** — Building a health app? Add medical terminology rules. Finance tool? Add number formatting rules. The more context, the better.

---

## Credits

- Inspired by [gstack](https://github.com/garrytan/gstack) by Garry Tan
- iOS framework references informed by [swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) by dpearson2699 — 57 agent skills for iOS 26+ / Swift 6.2 that shaped our modern API patterns, common mistakes sections, and framework coverage
- SwiftUI, SwiftData, Concurrency, and Testing quality improvements informed by [twostraws](https://github.com/twostraws) agent skills (SwiftUI Pro, SwiftData Pro, Swift Concurrency Pro, Swift Testing Pro)
- iOS 26 / Xcode 26 updates informed by [xcode-26-system-prompts](https://github.com/artemnovichkov/xcode-26-system-prompts) by artemnovichkov
- Security reference informed by [swift-security-skill](https://github.com/ivan-magda/swift-security-skill) by ivan-magda
- Design rules informed by [swiftui-design-principles](https://github.com/arjitj2/swiftui-design-principles) by arjitj2
- View composition, performance audit, and concurrency patterns informed by [Skills](https://github.com/Dimillian/Skills) by Thomas Ricouard (Dimillian)
- Accessibility patterns informed by [iOS-Accessibility-Agent-Skill](https://github.com/dadederk/iOS-Accessibility-Agent-Skill) by dadederk
- Architecture routing and cancellation-first patterns informed by [swift-architecture-skill](https://github.com/efremidze/swift-architecture-skill) by efremidze
- Built by [Ismael Kose](https://github.com/ismailkose) from the experience of shipping production apps as a one-person team

---

## Contributing

PRs welcome. Ideas: new agents for specific workflows, setup script improvements, integrations with design tools or deployment platforms.

## License

MIT
