# Ship Framework

`v2026.04.11` · 61 framework references · 10 personas · 21 commands

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

Ship has 21 commands. You don't need to learn them all — `/ship-team` handles routing. But when you want to call a specific specialist directly, here's how they're organized:

### 🔄 The Core Loop — every feature goes through this

| Command | Who | What happens |
|:---|:---|:---|
| **ship-think** | Vi | Validate the idea. Six forcing questions kill bad ideas before you invest time. |
| **ship-plan** | Vi + Pol + Arc | Product brief + design readiness score + technical plan. They argue, you decide. |
| **ship-build** | Dev | Builds one feature at a time. Scope enforcement, atomic commits. |
| **ship-review** | Crit + Pol + Eye + Test | The quality gate. UX, design, visual QA, tests. Health score 0-100. |
| **ship-launch** | Cap | Readiness check, deploy, measurement plan. |

### 🎨 Design Tools

| Command | Who | What happens |
|:---|:---|:---|
| **ship-design** | Pol + Eye | Create a design system from scratch. Research competitors, propose tokens, preview mockups (AI or HTML), write DESIGN.md. |
| **ship-variants** | Pol | Generate 3 theory-backed design options. HTML comparison board + AI mockups. Learns your taste over time. |
| **ship-html** | Dev + Pol | Production-quality responsive HTML. No framework, proper text reflow. |

### 🔧 When You Need It

| Command | Who | What happens |
|:---|:---|:---|
| **ship-fix** | Bug | Paste the error. Checks known patterns first, then systematic investigation. |
| **ship-browse** | Eye | Visual QA with browser power. Headed mode, cookie import, perf snapshots. |
| **ship-perf** | Eye + Test | Core Web Vitals benchmark. Before/after comparison. CI assertions. |
| **ship-money** | Biz | Pricing strategy starting from willingness-to-pay. |
| **ship-retro** | Retro | Reads git history. What actually happened, not what you think. |

### 🛡️ Safety Net — set once, runs in the background

| Command | What it does |
|:---|:---|
| **ship-careful** | Warns before destructive commands (rm -rf, DROP TABLE, force push). |
| **ship-freeze** | Locks edits to one directory. Nothing else gets touched. |
| **ship-guard** | Both at once. |
| **ship-unfreeze** | Removes the lock. |

### 🔒 Automatic Hooks — no commands needed

| Hook | When | What it does |
|:---|:---|:---|
| **Reference Gate** | First Edit/Write | Blocks coding until references are loaded. Passes after first successful edit. |
| **Session Start** | Session opens | Loads your Stack, product name, version, task count. Cleans stale state. |

### ⚡ Optional

| Command | What it does |
|:---|:---|
| **ship-codex** | Second opinion from OpenAI Codex. Review, challenge, or consult. |
| **ship-update** | Updates Ship Framework to latest version. |

---

## Smart Flags — No Flags Needed

Every command auto-detects the right mode from context. The team reads your diff size, file types, project state, and prior outputs — then picks the appropriate flag automatically. You'll see what it chose. Explicit flags always override.

**AI Mockups:** Set `OPENAI_API_KEY` and `/ship-variants` and `/ship-design` auto-generate high-fidelity AI mockups via GPT Image API alongside the HTML comparison boards.

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

Web project? You get web references. iOS project? You get Apple HIG, SwiftUI patterns, and 61 framework guides. Android? Material 3 and Compose patterns. No irrelevant context cluttering your sessions.

Platform skills also auto-activate by file type — touch a `.swift` file and iOS knowledge loads, edit a `.tsx` and web patterns activate. The Stack declaration and file detection work together so nothing gets missed.

---

## Skills Route, References Teach

Ship splits design intelligence into two layers:

**Skills** are thin routing tables (~60-80 lines). They tell each persona WHEN to read WHICH reference, for WHICH command. They also carry priority enforcement gates — the things that block shipping (contrast ratios, tap targets, reduced motion).

**References** are the brain (200-700+ lines). They teach Claude HOW to think about a domain — with reasoning, correct vs incorrect examples, and anti-patterns. Different personas read different sections of the same reference at different times.

Example flow: you run `/ship-build` → Dev loads the UX skill → skill says "read `.claude/skills/ship/ux/references/forms-feedback.md` Section 1 for form implementation" → Dev reads the reference and applies the reasoning to the specific form being built.

Each skill owns its references — the UX skill has 12 reference files, motion has 4, iOS has 64 (including 61 framework guides), web has 3. Total: 85 deep reference files covering UX, typography, color, forms, navigation, layout, touch, dark mode, animation, components, design quality, hardening, and platform-specific patterns. All auto-loaded based on your declared stack. The team also learns your patterns over time — bug fixes write to LEARNINGS.md, design reviews record your taste preferences, and every session starts by reading what past sessions discovered.

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

Pol:       Design readiness score: 62/70. Information Architecture 9/10,
           Interaction States 7/10 — we need to plan the toggle states.
           AI Slop Risk 8/10 — the color strategy is intentional.

Arc:       Two approaches. Minimal: CSS variables + system preference
           detection, 2 hours. Clean: full theme engine with custom
           palettes, 2 days. I'd go Minimal — ship it, see if users
           want custom palettes.

Dev:       Built it. CSS variables, prefers-color-scheme, toggle in
           settings. 47 minutes. Atomic commit done.

Crit:      Contrast ratios pass. Toggle is discoverable. One issue —
           the chart colors don't adapt. Not blocking but worth fixing.

Test:      12 tests written. All passing. Edge case covered: system
           preference changes while app is open. Health score: 88/100.

Cap:       ✓ DONE — Dark mode is live. Measuring: daily active users
           after 6pm (baseline: 340). Check in one week.
```

One idea → planned, scored, built, reviewed, tested, shipped, measured. That's Ship.

---

## File Structure

```
your-project/
  CLAUDE.md                    # Yours — product, founder, stack, principles
  CHEATSHEET.md                # Quick reference
  LEARNINGS.md                 # Team memory — bug patterns, design preferences, code patterns
  DESIGN.md                    # Design system tokens (created by /ship-design)
  PERF-REPORT.md               # Performance benchmarks (created by /ship-perf)
  .claude/
    team-rules.md              # Framework — personas, rules, coaching
    commands/                  # 21 slash commands
      ship-think.md            #   Pre-planning idea validation
      ship-plan.md             #   Product + design scoring + architecture
      ship-build.md            #   Build one feature with TDD
      ship-review.md           #   Quality gate (Crit + Pol + Eye + Test)
      ship-launch.md           #   Deploy + measurement
      ship-design.md           #   Design system creation
      ship-variants.md         #   Theory-backed design exploration
      ship-html.md             #   Responsive HTML prototyping
      ship-fix.md              #   Systematic debugging
      ship-browse.md           #   Visual QA with browser power
      ship-perf.md             #   Performance benchmarking
      ship-money.md            #   Monetization strategy
      ship-retro.md            #   Weekly retrospective
      ship-team.md             #   Orchestrator — routes everything
      ship-codex.md            #   Cross-model verification
      ship-careful.md          #   Destructive command warnings
      ship-freeze.md           #   Directory edit lock
      ship-guard.md            #   Combined safety
      ship-unfreeze.md         #   Remove lock
      ship-update.md           #   Framework update
      ship-qa.md               #   (deprecated → /ship-review --test)
    skills/
      ship/                    # Framework skills — each owns its references
        ux/                    #   12 references: UX principles, typography, forms, layout, etc.
        motion/                #   4 references: animation system, CSS, Framer Motion, performance
        components/            #   1 reference: component catalog, three-layer model
        hardening/             #   1 reference: error handling, edge cases, pre-launch checklist
        ios/                   #   64 references: SwiftUI, HIG, Swift essentials, 61 framework guides
        web/                   #   3 references: React patterns, accessibility, performance
        android/               #   (planned: Compose, Material 3, Kotlin, platform APIs)
        refgate/               #   Reference Gate hook — blocks first edit until refs loaded
        sessionstart/          #   Session Start hook — loads project context automatically
        freeze/                #   Directory lock hook
        careful/               #   Destructive command hook
        guard/                 #   Combined: careful + freeze
        unfreeze/              #   Remove directory lock
      your-skills/             # Your skills (design system, API patterns, etc.)
  references/                  # Your custom references (framework refs are in skills above)
```

**CLAUDE.md** is yours — edit freely, never overwritten. **LEARNINGS.md** and **DESIGN.md** are yours too — the team writes to them but updates never overwrite your content. **team-rules.md** is the framework's — auto-synced on update.

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

- [impeccable](https://github.com/pbakaus/impeccable) by Paul Bakaus — 8-state interaction model, AI slop patterns, design hardening
- [stitch-skills](https://github.com/nicholasgriffintn/stitch-skills) by Google Labs — design system patterns, component architecture
- [ui-ux-pro-max-skill](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill) by NextLevelBuilder — design intelligence, 161 color palettes, 57 font pairings, 99 UX guidelines, style selection
- [Animations on the Web](https://animations.dev) by Emil Kowalski — motion design principles and timing
- [userinterface.wiki](https://userinterface.wiki) by Raphael Salaja — UI component patterns and interaction design
- [Laws of UX](https://lawsofux.com) by Jon Yablonski — UX heuristics and design psychology
- [Microinteractions](https://www.oreilly.com/library/view/microinteractions/9781491945957/) by Dan Saffer — micro-interaction design patterns
- [Butterick's Practical Typography](https://practicaltypography.com) — typographic standards, type scale reasoning
- [Interaction of Color](https://yalebooks.yale.edu/book/9780300179354/interaction-of-color/) by Josef Albers — color theory foundations
- [Space in Design Systems](https://medium.com/eightshapes-llc/space-in-design-systems-188bcbae0d62) by Nathan Curtis — spacing system methodology

**Web & React references:**

- [Vercel agent-skills](https://github.com/vercel-labs/agent-skills) — React best practices (65 rules), web design guidelines (100+ rules), composition patterns
- [Web Interface Guidelines](https://github.com/vercel-labs/web-interface-guidelines) by Vercel — accessibility, forms, animation, typography, performance, dark mode, i18n
- [Vercel v0 iOS engineering blog](https://v0.dev/blog) — chat UI patterns and interface architecture

Built by [Ismael Kose](https://github.com/ismailkose).

## Contributing

PRs welcome. Ideas: new platform skills, reference files, design tool integrations.

## License

MIT
