# Ship Framework

**An AI product team in your terminal.**

You're a designer who vibe codes. A PM who prototypes. Someone building toward founder — not there yet, but getting closer with every product you ship. You need engineering, and that's what Claude Code is for. But raw Claude Code is like having a brilliant engineer with no product sense, no design eye, and no business context. It builds what you say, not what you need.

This framework gives Claude Code structure. It turns one AI into a team of opinionated specialists who challenge each other, catch problems early, and keep you shipping. Not what you are today — what you can be tomorrow. You're the founder. They report to you.

```bash
/ship-team I want to build a habit tracker for creative professionals
```

That's it. The team takes over — plans the product, architects the code, builds it, reviews the quality, tests everything, and ships it. You make the calls. They do the work.

---

## Setup

```bash
git clone https://github.com/ismailkose/ship-framework.git
bash ship-framework/setup.sh
```

Open Claude Code in your project. Type `/ship-team`. You're running.

---

## The Only Command You Need to Remember

```
/ship-team
```

It routes everything. Say what you want in plain English:

```bash
/ship-team I want to build a weekly email digest
/ship-team continue                    # pick up where you left off
/ship-team Take over this project      # existing codebase
/ship-team something broke [paste error]
/ship-team status
```

That's the 80% workflow. One command. The team figures out the rest.

---

## When You Want More Control

Ship has 16 commands. You don't need to learn them all — `/ship-team` handles routing. But when you want to call a specific specialist directly, here's how they're organized:

### 🔄 The Core Loop — every feature goes through this

| Command | Who | What happens |
|:---|:---|:---|
| **ship-plan** | Vi + Arc | Product brief + technical plan. They argue, you get a battle-tested plan. |
| **ship-build** | Dev | Builds one feature at a time. Scope enforcement, atomic commits. |
| **ship-review** | Crit + Pol + Eye | UX quality, design polish, visual QA. Confidence score 0-100. |
| **ship-qa** | Test | Runs tests, writes missing ones, edge cases. Health score. |
| **ship-launch** | Cap | Readiness check, deploy, measurement plan. |

### 🔧 When You Need It

| Command | Who | What happens |
|:---|:---|:---|
| **ship-fix** | Bug | Paste the error. Systematic investigation, no guessing. |
| **ship-money** | Biz | Pricing strategy starting from willingness-to-pay. |
| **ship-browse** | Eye | Screenshots checked against your design system. |
| **ship-retro** | Retro | Reads git history. What actually happened, not what you think. |

### 🛡️ Safety Net — set once, runs in the background

| Command | What it does |
|:---|:---|
| **ship-careful** | Warns before destructive commands (rm -rf, DROP TABLE, force push). |
| **ship-freeze** | Locks edits to one directory. Nothing else gets touched. |
| **ship-guard** | Both at once. |
| **ship-unfreeze** | Removes the lock. |

### ⚡ Optional

| Command | What it does |
|:---|:---|
| **ship-codex** | Second opinion from OpenAI Codex. Review, challenge, or consult. |
| **ship-update** | Updates Ship Framework to latest version. |

---

## It Adapts to You

Ship doesn't treat every founder the same. The `## The Founder` section in your CLAUDE.md tells the team how YOU work:

```markdown
## The Founder

Background: Product designer
Technical comfort: Can read code and review diffs. Not architecting from scratch.
Decision style: One strong recommendation with clear reasoning.
Communication: Short and direct. Show, don't explain.
Taste: Craft-obsessed. If it feels off, it's not shipping.
Context need: I need the "why" before I commit.
Focus awareness: I can get deep into details that are already shippable.
```

Dev stops over-explaining code to a designer who can read it. Crit leads with design quality, not code quality. Vi presents one strong recommendation instead of three options if that's how you decide. The team shapes itself to you.

---

## They Push Back

These aren't assistants waiting for instructions. They're the best in their field and they act like it.

**Vi** asks "who told you they need this?" when you're building on taste alone. **Crit** says "this is shippable, move on" when you're perfecting something that's already good enough — and shows you the three core flows that don't exist yet. **Dev** shows the 80% version when the 100% version costs a week. **Arc** scans your entire codebase before recommending anything. **Cap** pushes to ship. **Retro** reads your actual git history and says "you spent three sessions on animation and zero on the payment flow."

They respect your authority — you always make the final call. But they make sure you're deciding *informed*, not guessing.

---

## Your Stack, Your References

Declare your stack once. Ship only loads what's relevant:

```markdown
## Stack
Stack: web (Next.js, Tailwind, Vercel)
```

Web project? You get web references. iOS project? You get Apple HIG, SwiftUI patterns, and 47 framework guides. Android? Material 3 and Compose patterns. No irrelevant context cluttering your sessions.

---

## Skills Route, References Teach

Ship splits design intelligence into two layers:

**Skills** are thin routing tables (~60-80 lines). They tell each persona WHEN to read WHICH reference, for WHICH command. They also carry priority enforcement gates — the things that block shipping (contrast ratios, tap targets, reduced motion).

**References** are the brain (200-700+ lines). They teach Claude HOW to think about a domain — with reasoning, correct vs incorrect examples, and anti-patterns. Different personas read different sections of the same reference at different times.

Example flow: you run `/ship-build` → Dev loads the UX skill → skill says "read `references/shared/forms-feedback.md` Section 1 for form implementation" → Dev reads the reference and applies the reasoning to the specific form being built.

Ship comes with 10 framework skills and 18 deep reference files covering UX, typography, color, forms, navigation, layout, touch, dark mode, animation, components, design quality, and platform-specific patterns. All auto-loaded based on your declared stack.

### Add Your Own

Create skills in `.claude/skills/your-skills/` and wire them in CLAUDE.md:

```
tailwind-patterns: load during /ship-build and /ship-review when working on frontend files
```

Add references in `references/` and route them from CLAUDE.md under Custom References. Ship auto-detects new skills and offers to wire them for you.

---

## How It Actually Feels

```
You:       /ship-team I want to add dark mode

Vi:        Here's the job statement — users want to reduce eye strain
           during evening sessions. Magic moment: the first time the
           interface shifts and everything just feels right.

Arc:       Two approaches. Minimal: CSS variables + system preference
           detection, 2 hours. Clean: full theme engine with custom
           palettes, 2 days. I'd go Minimal — ship it, see if users
           want custom palettes.

Dev:       Built it. CSS variables, prefers-color-scheme, toggle in
           settings. 47 minutes. Atomic commit done.

Crit:      Contrast ratios pass. Toggle is discoverable. One issue —
           the chart colors don't adapt. Not blocking but worth fixing.

Test:      12 tests written. All passing. Edge case covered: system
           preference changes while app is open.

Cap:       ✓ DONE — Dark mode is live. Measuring: daily active users
           after 6pm (baseline: 340). Check in one week.
```

One idea → planned, built, reviewed, tested, shipped, measured. That's Ship.

---

## File Structure

```
your-project/
  CLAUDE.md                    # Yours — product, founder, stack, principles
  CHEATSHEET.md                # Quick reference
  .claude/
    team-rules.md              # Framework — personas, rules, coaching
    commands/                  # 16 slash commands
    skills/
      ship/                    # Routing skills (ux, web, motion, components, ios, android + safety)
      your-skills/             # Your skills (design system, API patterns, etc.)
  references/
    shared/                    # 19 deep references — the design brain
      ux-principles.md         #   Hick's, Miller's, Fitts's, Peak-End, HEART
      typography-color.md      #   Type scale, font pairing, OKLCH color, fluid type
      interaction-design.md    #   8 interactive states, micro-interactions, gestures
      spatial-design.md        #   Spacing tokens, density strategy, whitespace
      copy-clarity.md          #   UX writing, voice framework, AI copy slop patterns
      hardening-guide.md       #   Error boundaries, edge cases, pre-launch checklist
      forms-feedback.md        #   Input patterns, validation, empty states, toasts
      navigation.md            #   Nav architecture, back behavior, deep linking
      layout-responsive.md     #   Mobile-first, breakpoints, spacing scale
      touch-interaction.md     #   Tap targets, gestures, press feedback, haptics
      dark-mode.md             #   Theming strategy, semantic tokens, contrast
      design-quality.md        #   First impression, 18 AI slop patterns, coherence
      design-research.md       #   Competitive research, design system creation
      components.md            #   Three-layer model, 46 component catalog
      animation.md             #   Motion budget, tokens, 8 pattern foundations
      animation-css.md         #   CSS transforms, transitions, keyframes
      animation-framer-motion.md  Framer Motion API
      animation-performance.md #   60fps optimization, reduced motion
    web/                       # 3 web-specific references
      react-patterns.md        #   Server/Client components, composition, hydration
      web-accessibility.md     #   Semantic HTML, ARIA, focus, screen readers
      web-performance.md       #   Core Web Vitals, image/font optimization
    ios/                       # Apple HIG, SwiftUI, 47 framework guides
    android/                   # Material 3, Compose patterns
```

**CLAUDE.md** is yours — edit freely, never overwritten. **team-rules.md** is the framework's — auto-synced on update.

---

## Credits

**Framework inspiration:**

- [gstack](https://github.com/garrytan/gstack) by Garry Tan — the original AI team-in-terminal concept

**iOS references:**

- [swift-ios-skills](https://github.com/dpearson2699/swift-ios-skills) by dpearson2699 — SwiftUI patterns and iOS skill templates
- [twostraws](https://github.com/twostraws) agent skills — Swift/iOS agent skill foundations
- [xcode-26-system-prompts](https://github.com/artemnovichkov/xcode-26-system-prompts) by artemnovichkov — Xcode system prompt patterns
- [swift-security-skill](https://github.com/ivan-magda/swift-security-skill) by ivan-magda — iOS security patterns
- [swiftui-design-principles](https://github.com/arjitj2/swiftui-design-principles) by arjitj2 — SwiftUI design skill
- [Skills](https://github.com/Dimillian/Skills) by Dimillian (Thomas Ricouard) — iOS agent skills collection
- [iOS-Accessibility-Agent-Skill](https://github.com/dadederk/iOS-Accessibility-Agent-Skill) by dadederk — iOS accessibility patterns
- [swift-architecture-skill](https://github.com/efremidze/swift-architecture-skill) by efremidze — Swift architecture patterns

**UX & design references:**

- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) by NextLevelBuilder — design intelligence, 161 color palettes, 57 font pairings, 99 UX guidelines, style selection
- [Animations on the Web](https://animations.dev) by Emil Kowalski — motion design principles and timing
- [userinterface.wiki](https://userinterface.wiki) by Raphael Salaja — UI component patterns and interaction design
- [Laws of UX](https://lawsofux.com) by Jon Yablonski — UX heuristics and design psychology

**Web & React references:**

- [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) — React best practices (65 rules), web design guidelines (100+ rules), composition patterns
- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) by Vercel — accessibility, forms, animation, typography, performance, dark mode, i18n
- [Vercel v0 iOS engineering blog](https://v0.dev/blog) — chat UI patterns and interface architecture

Built by [Ismael Kose](https://github.com/ismailkose).

## Contributing

PRs welcome. Ideas: new platform skills, reference files, design tool integrations.

## License

MIT
