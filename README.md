 # Ship Framework

**v2026.03.18** · **An AI product team for one-person teams.**

You're one person. You handle product, design, business, and decisions. You need engineering — that's what Claude Code is for. But raw Claude Code is like having a brilliant engineer with no product sense, no design eye, and no business context. It builds what you say, not what you need.

This framework gives Claude Code structure. It turns one AI into a team of 11 opinionated specialists who challenge each other, catch problems early, and keep you shipping. You're the CEO. They report to you.

---

## Setup (2 minutes)

```bash
git clone https://github.com/ismailkose/ship-framework.git
bash ship-framework/setup.sh
```

The script asks 3 questions — product name, description, and tech stack — then generates everything and installs Playwright for visual QA:

```
Ship Framework — Setup

What's your product called? > Trackwise
Describe it in one sentence: > A habit tracker for runners

Pick a tech stack, or type your own:

  1) Web App          — Next.js, React, Tailwind CSS, shadcn/ui (Base UI), Supabase
  2) Mobile App       — React Native (Expo), TypeScript, Supabase
  3) iOS App          — SwiftUI, Swift, CloudKit
  4) Full-Stack Python — FastAPI, Python, PostgreSQL, HTMX, Tailwind CSS
  5) Static Site      — Astro, Tailwind CSS, Markdown, Vercel
  6) Custom           — Type your own stack

> 1

✓ Created CLAUDE.md
✓ Created .claude/commands/ (13 slash commands)
✓ Created references/ (animation + component architecture)
✓ Created CHEATSHEET.md
✓ Created TASKS.md
✓ Installed Playwright

Copy the command below and paste it right here to start building:

claude "/team I want to build Trackwise"
```

That's it. Your team is running.

**Already have a CLAUDE.md?** Setup detects it. If it's from a previous Ship Framework install, it updates commands and references. If it's your own, it appends Ship Framework below your existing content.

**Specifying a directory:** `bash ship-framework/setup.sh ./my-project`

**Without terminal:** Download the ZIP from GitHub, copy `template/.claude/commands/` to your project's `.claude/commands/`, copy `template/references/` to `references/`, copy `CHEATSHEET.md`, and edit `template/CLAUDE.md` manually. Then open Claude Code and type `/team`.

---

## Updating

```bash
bash ship-framework/update.sh
```

That's it. The update script pulls the latest version automatically, then:
- Shows your current version vs latest
- Shows what changed (from the [changelog](CHANGELOG.md))
- Updates your slash commands and cheatsheet
- Stamps the new version in your CLAUDE.md footer
- **Never touches** your CLAUDE.md content, TASKS.md, or project files

**Checking your version:** Look at the bottom of your CLAUDE.md — it shows the Ship Framework version.

**Watching for updates:** Star or watch the [repo](https://github.com/ismailkose/ship-framework) to get notified when new versions drop.

Ship Framework uses date-based versioning (`YYYY.MM.DD`). Each release is tagged with the date it shipped.

---

## The Team

| Command | Name | Role |
|---------|------|------|
| `/team` | — | **Orchestrator** — give it any instruction, it delegates to the right agents |
| `/visionary` | Vi | **Product Strategist** — rips ideas apart, writes JTBD, finds the magic moment, picks HEART metric |
| `/architect` | Arc | **Technical Lead** — turns briefs into buildable plans, RICE-scores the build order, defines motion system, estimates cost |
| `/build` | Dev | **Builder** — writes code one feature at a time, commits and explains every decision |
| `/critic` | Crit | **Product Reviewer** — uses it like a real user, reviews against HEART dimensions, checks animation balance, finds rough edges |
| `/polish` | Pol | **Design Director** — your design voice: typography, spacing, transitions, copy, mobile feel |
| `/ship` | Cap | **Release Manager** — 7-phase deploy: pre-flight → tests → quality gate → readiness → deploy → verify → report |
| `/money` | Biz | **Business Brain** — simplest path to revenue: pricing model, cost math, Stripe implementation |
| `/browse` | Eye | **Visual QA** — 6-phase review: setup → screen map → mobile viewport → interaction walkthrough → bug checklist → report |
| `/qa` | Test | **Tester** — 8-phase QA: scope → tests → explore like a user → document issues → write tests → health score → fix loop → report |
| `/fix` | Bug | **Debugger** — translates errors to plain English, fixes them, teaches you one thing |
| `/retro` | Retro | **Retrospective** — 9-step weekly review: git data, metrics, shipping streak, time patterns, hotspots, task health, narrative, trends |
| `/status` | — | **Status check** — quick snapshot of progress from TASKS.md |

**They disagree with each other.** Vi might want a feature that Arc thinks is over-engineered. Dev might build something that Crit finds confusing. Pol might want polish that Cap thinks delays launch. When they disagree, they present both sides — you make the call.

That tension is the whole point.

---

## Built-In Frameworks

The team uses three product frameworks so decisions are structured, not gut-feel:

- **Jobs To Be Done (JTBD)** — Vi writes a job statement for every feature: *"When I [situation], I want to [motivation], so I can [expected outcome]."* No vague personas.
- **HEART Framework** — Crit reviews against Google's UX quality dimensions: Happiness, Engagement, Adoption, Retention, Task success. Picks the 2-3 most relevant per review.
- **RICE Scoring** — Arc scores every item in the build order: (Reach × Impact × Confidence) / Effort. When agents disagree on priority, RICE is the tiebreaker.

These frameworks are woven into the agents — you don't need to invoke them manually.

---

## How It Works

### The Flow

```
/team (orchestrator — delegates automatically)
    |
/visionary -> Product brief + JTBD + HEART metric + who pays
    |
/architect -> RICE-scored build order + cost estimate
    |
/build -> Code, one feature at a time
    |
/critic -> HEART review (must-fixes go back to /build, rest to TASKS.md)
    |
/polish -> Design refinement (may send back to /build)
    |
/browse -> Visual QA (screenshots + design comparison)
    |
/qa -> Run tests, write missing tests
    |
/ship -> Launch checklist + deploy
    |
/money -> Payments
```

You don't run all 11 every time. `/team` figures out which agents are needed.

### Daily Workflow

```bash
# Start of day — pick up where you left off
/team continue

# New feature idea
/team I want to build a weekly email digest

# Something broke
/team [paste error]

# Quick check
/status
```

**Once `/team` is running, just talk naturally.** You don't need to type `/team` again within the same session. Say "go ahead", "build it", "looks good, next feature", "the dashboard feels off, review it" — the team stays active and routes to the right agents automatically. You only need `/team` again when you start a new Claude Code session.

### The Task Board

`TASKS.md` is the team's memory across sessions. After every task, `/team` updates it. Next session, `/team` reads it first. Nothing gets lost.

---

## Why This Exists

When you're a one-person team, you're not "a designer" or "a PM" or "a founder" — you're everything. You need product thinking AND technical rigor AND design craft AND business sense AND the discipline to ship.

Claude Code gives you engineering. But without structure, it just builds whatever you describe — no pushback, no quality checks, no "have you thought about this?" This framework adds that structure through agents that are specifically designed to challenge each other:

- Vi asks "why would anyone care?" before anything gets built
- Arc asks "will this still work at 3am?" before the architecture is set
- Eye screenshots the actual UI and compares it to the design
- Test proves things work — or proves they don't
- Crit asks "but what if I do THIS?" after every feature
- Pol asks "does this feel right on a phone?" before shipping
- Cap asks "why aren't we live yet?" when polish goes too long
- Biz asks "how does this make money?" before it's too late
- Retro asks "what actually happened this week?" to keep you honest

One AI, eleven perspectives, one you making the calls.

---

## Tips from Production Use

**Use `/team` for almost everything.** It handles routing. You don't need to remember which agent does what.

**Let the disagreements play out.** When Vi wants something and Arc pushes back, that's the system working. Listen to both sides.

**TASKS.md is your source of truth.** Start every session with `/team continue` or `/status`. The task board keeps you on track across days and weeks.

**One feature at a time.** Dev builds, tests, and commits one thing before moving on. Resist the urge to batch.

**Don't skip /critic.** It's tempting to go straight from build to ship. Crit finds the things your users would find first.

**Customize CLAUDE.md aggressively.** Add your color tokens, component library rules, copy guidelines, API constraints. The more specific, the better every agent performs.

**The takeover sequence works.** Existing codebase? `/team Take over this project` runs Arc (assess) → Crit (HEART audit) → Vi (product JTBD) → Biz (who pays) → presents options. Fastest way to orient.

**Run a health check.** Already building? `/team Health check` runs Vi → Arc → Crit → Biz → Eye for a full strategic review — product fit, tech debt, UX gaps, monetization, and visual QA in one pass.

---

## What This Is (and Isn't)

**This is:** A structured workflow for one-person teams to ship real products using Claude Code.

**This is not:** Multiple AI agents running in parallel. It's one AI wearing different hats. But the structure — forced disagreements, handoffs, multi-phase workflows, health scores, persistent task tracking — catches problems that unstructured conversations miss.

---

## File Structure

```
your-project/                    (generated by setup.sh)
  CLAUDE.md                      # Team framework + product rules
  TASKS.md                       # Persistent task board
  CHEATSHEET.md                  # Quick reference card
  .claude/commands/              # 13 slash commands
  references/                    # Agent reference files (auto-read when relevant)
    README.md                    # Extension guide + design system template
    animation.md                 # Motion budget, build rules, 8 patterns
    animation-css.md             # Deep-dive: transforms, transitions, keyframes
    animation-framer-motion.md   # Deep-dive: Framer Motion API (React only)
    animation-performance.md     # Deep-dive: 60fps, DevTools, reduced motion
    components.md                # Headless architecture, three-layer model
    design-system.md             # (you create) Your tokens, rules, patterns

ship-framework/                  (the repo itself)
  setup.sh                       # Interactive setup (3 questions)
  update.sh                      # Update existing projects
  VERSION                        # Current version (YYYY.MM.DD)
  CHANGELOG.md                   # What changed in each version
  README.md                      # This file
  CHEATSHEET.md                  # Template for quick reference
  template/                      # Source templates
    CLAUDE.md                    # Team framework template
    references/                  # Reference files copied to projects
    .claude/commands/            # 13 slash command files
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

**The layering rule:** Your design system overrides where it has opinions. Headless primitives fill the gaps. If your design system has Button and Card but not Dialog, agents use yours for Button/Card and reach for a headless Dialog primitive, styled to match your existing tokens.

**Extending with your design system:** Add `references/design-system.md` with your tokens, component rules, and patterns. Agents use your rules first, fall back to framework defaults where you're silent. See `references/README.md` for the template and extension guide.

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

## Customization

**Adding agents** — Create `.claude/commands/yourcommand.md`, add the definition to CLAUDE.md. Follow the pattern: name, personality, checklist, handoff.

**Design system rules** — Add a "Design System" section to CLAUDE.md with color tokens, typography, spacing. Pol enforces them.

**Domain rules** — Building a health app? Add medical terminology rules. Finance tool? Add number formatting rules. The more context, the better.

---

## Credits

- Inspired by [gstack](https://github.com/garrytan/gstack) by Garry Tan
- Built by [Ismael Kose](https://github.com/ismailkose) from the experience of shipping production apps as a one-person team

---

## Contributing

PRs welcome. Ideas: new agents for specific workflows, setup script improvements, integrations with design tools or deployment platforms.

## License

MIT
