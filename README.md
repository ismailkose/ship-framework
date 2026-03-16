# Ship Framework

**An AI product team for one-person teams.**

You're one person. You handle product, design, business, and decisions. You need engineering — that's what Claude Code is for. But raw Claude Code is like having a brilliant engineer with no product sense, no design eye, and no business context. It builds what you say, not what you need.

This framework gives Claude Code structure. It turns one AI into a team of 8 opinionated specialists who challenge each other, catch problems early, and keep you shipping. You're the CEO. They report to you.

---

## Setup (2 minutes)

```bash
git clone https://github.com/ismailkose/ship-framework.git
bash ship-framework/setup.sh
```

The script asks 4 questions — product name, description, tech stack, and project stage — then generates everything:

```
Ship Framework — Setup

What's your product called? > Trackwise
Describe it in one sentence: > A habit tracker for runners

Pick a tech stack, or type your own:

  1) Web App          — Next.js 15, React 19, Tailwind CSS 4, shadcn/ui, Supabase
  2) Mobile App       — React Native (Expo 52), TypeScript, Supabase
  3) iOS App          — SwiftUI, Swift 6, CloudKit
  4) Full-Stack Python — FastAPI, Python 3.13, PostgreSQL, HTMX, Tailwind CSS 4
  5) Static Site      — Astro 5, Tailwind CSS 4, Markdown, Vercel
  6) Custom           — Type your own stack

> 1

What stage? > 1 (Starting fresh)

✓ Created CLAUDE.md
✓ Created .claude/commands/ (13 slash commands)
✓ Created TASKS.md
✓ Created CHEATSHEET.md

Done! Open Claude Code and type:
  /team I want to build Trackwise
```

That's it. Your team is running.

---

## The Team

| Command | Name | Role | What they do |
|---------|------|------|-------------|
| `/team` | — | **Orchestrator** | Give it any instruction. It delegates to the right agents. |
| `/visionary` | Vi | Product Strategist | Rips ideas apart. Kills feature creep. Finds the magic moment. |
| `/architect` | Arc | Technical Lead | Turns briefs into buildable plans. Chooses boring tech. |
| `/build` | Dev | Builder | Writes code, one feature at a time. Commits and explains. |
| `/critic` | Crit | Product Reviewer | Uses it like a real user. Finds every rough edge. |
| `/polish` | Pol | Design Director | Your design voice. Typography, spacing, transitions, copy. |
| `/ship` | Cap | Release Manager | Gets it live. Hates "almost done." |
| `/money` | Biz | Business Brain | Simplest path to revenue. Pricing, Stripe, conversion. |
| `/browse` | Eye | Visual QA | Screenshots the app. Compares to designs. Catches visual bugs. |
| `/qa` | Test | Tester | Runs tests, writes missing ones. Proves things work. |
| `/fix` | Bug | Debugger | Fixes errors. Explains in plain English. Teaches you one thing. |
| `/retro` | Retro | Retrospective | Weekly review. Git stats, velocity, wins, drags, next focus. |
| `/status` | — | Status check | Quick snapshot of progress from TASKS.md. |

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
/browse -> Visual QA (screenshots + design comparison)
    |
/qa -> Run tests, write missing tests
    |
/critic -> HEART review (may send back to /build)
    |
/polish -> Design refinement (may send back to /build)
    |
/ship -> Launch checklist + deploy
    |
/money -> Payments
```

You don't run all 8 every time. `/team` figures out which agents are needed.

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

### The Task Board

`TASKS.md` is the team's memory across sessions. After every task, `/team` updates it. Next session, `/team` reads it first. Nothing gets lost.

---

## Why This Exists

When you're a one-person team, you're not "a designer" or "a PM" or "a founder" — you're everything. You need product thinking AND technical rigor AND design craft AND business sense AND the discipline to ship.

Claude Code gives you engineering. But without structure, it just builds whatever you describe — no pushback, no quality checks, no "have you thought about this?" This framework adds that structure through agents that are specifically designed to challenge each other:

- Vi asks "why would anyone care?" before anything gets built
- Arc asks "will this still work at 3am?" before the architecture is set
- Crit asks "but what if I do THIS?" after every feature
- Pol asks "does this feel right on a phone?" before shipping
- Cap asks "why aren't we live yet?" when polish goes too long
- Biz asks "how does this make money?" before it's too late

One AI, eight perspectives, one you making the calls.

---

## Tips from Production Use

**Use `/team` for almost everything.** It handles routing. You don't need to remember which agent does what.

**Let the disagreements play out.** When Vi wants something and Arc pushes back, that's the system working. Listen to both sides.

**TASKS.md is your source of truth.** Start every session with `/team continue` or `/status`. The task board keeps you on track across days and weeks.

**One feature at a time.** Dev builds, tests, and commits one thing before moving on. Resist the urge to batch.

**Don't skip /critic.** It's tempting to go straight from build to ship. Crit finds the things your users would find first.

**Customize CLAUDE.md aggressively.** Add your color tokens, component library rules, copy guidelines, API constraints. The more specific, the better every agent performs.

**The takeover sequence works.** Existing codebase? `/team Take over this project` runs Arc (assess) → Crit (audit) → presents options. Fastest way to orient.

---

## What This Is (and Isn't)

**This is:** A structured workflow for one-person teams to ship real products using Claude Code.

**This is not:** Multiple AI agents running in parallel. It's one AI wearing different hats. But the structure — forced disagreements, handoffs, checklists, persistent task tracking — catches problems that unstructured conversations miss.

---

## File Structure

```
your-project/                    (generated by setup.sh)
  CLAUDE.md                      # Team framework + product rules
  TASKS.md                       # Persistent task board
  .claude/commands/              # 13 slash commands
    team.md
    visionary.md
    architect.md
    build.md
    browse.md
    qa.md
    critic.md
    polish.md
    ship.md
    money.md
    fix.md
    retro.md
    status.md
```

---

## Customization

**Adding agents** — Create `.claude/commands/yourcommand.md`, add the definition to CLAUDE.md. Follow the pattern: name, personality, checklist, handoff.

**Design system rules** — Add a "Design System" section to CLAUDE.md with color tokens, typography, spacing. Pol enforces them.

**Domain rules** — Building a health app? Add medical terminology rules. Finance tool? Add number formatting rules. The more context, the better.

---

## Credits

- Inspired by [gstack](https://github.com/garrytan/gstack) by Garry Tan
- Built by [Ismael Kose](https://github.com/ismailkose) from the experience of shipping a production health app as a one-person team

---

## Contributing

PRs welcome. Ideas: new agents for specific workflows, setup script improvements, integrations with design tools or deployment platforms.

## License

MIT
