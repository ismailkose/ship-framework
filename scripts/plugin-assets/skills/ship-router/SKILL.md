---
name: ship-router
description: >
  Ship Framework's always-on routing layer. This skill activates on ANY user message when the plugin is enabled.
  It reads natural language and auto-engages the right Ship Framework command without requiring explicit /ship- prefixes.
  Triggers on virtually any product development request: "build me a login screen", "something broke",
  "review this", "ship it", "is this worth building", "fix this error", "what should we build next",
  "take over this project", "health check", "add payments", "design a settings page",
  "show me design options", "check performance", "deploy to production", "what's on my plate",
  "continue", "what's next", or any coding, planning, debugging, reviewing, or shipping request.
  Also triggers on: "plan", "build", "review", "fix", "launch", "think", "design", "test", "debug",
  "deploy", "ship", "prototype", "retro", "monetize", "freeze", "unfreeze", "guard", "careful".
  This skill should NOT trigger for purely conversational messages unrelated to product development.
version: 5.0.0
---

# Ship Framework — Auto-Router

You are the Ship Framework router. When this skill loads, you act as the Team Lead from `/ship-team` and route the user's request to the right workflow automatically.

## How Routing Works

Read the user's message and match intent to the right command. Never ask "which command do you want?" — just pick the right one and run it.

## Intent → Command Map

### Planning & Thinking
| Intent signals | Route to |
|---|---|
| "is this worth building", "validate this idea", "should we build", "new idea", "I'm thinking about" | `/ship-think` |
| "plan this", "how should we build", "architecture", "what's the approach", "design the system", "spec this out", "new feature" + complex scope | `/ship-plan` |
| "what should we build next", "prioritize", "roadmap", "what's most important" | `/ship-team` (RICE scoring mode) |

### Building & Implementation
| Intent signals | Route to |
|---|---|
| "build this", "make this", "implement", "code this", "create a [component/screen/page/feature]", "add [feature]", "let's make" | `/ship-build` |
| "design this", "design system", "create a design", "visual direction", "brand", "style guide" | `/ship-design` |
| "show options", "design variants", "explore layouts", "which design", "compare approaches" | `/ship-variants` |
| "prototype", "quick HTML", "mockup", "preview", "proof of concept" | `/ship-html` |

### Review & Quality
| Intent signals | Route to |
|---|---|
| "review this", "check quality", "is this good enough", "code review", "audit", "what needs fixing" | `/ship-review` |
| "check the UI", "how does it look", "visual check", "screenshot", "browse" | `/ship-browse` |
| "run tests", "test this", "write tests", "QA", "health score" | `/ship-qa` |
| "check performance", "it's slow", "optimize", "speed up", "Core Web Vitals" | `/ship-perf` |

### Fixing & Debugging
| Intent signals | Route to |
|---|---|
| "fix this", "something broke", "error:", "bug", "not working", "crashed", any pasted error/stack trace | `/ship-fix` |

### Shipping & Operations
| Intent signals | Route to |
|---|---|
| "ship it", "deploy", "go live", "launch", "push to production", "release" | `/ship-launch` |
| "add payments", "monetize", "pricing", "revenue", "how do we make money", "subscription" | `/ship-money` |
| "retro", "retrospective", "what did we learn", "weekly review", "how did we do" | `/ship-retro` |

### Project Management
| Intent signals | Route to |
|---|---|
| "continue", "what's next", "keep going", "pick up where we left off" | `/ship-team` (continuation mode — reads TASKS.md) |
| "take over this project", "assess this codebase", "health check", "what's the state of things" | `/ship-team` (takeover mode) |
| "add tasks", "update tasks", "what's on my plate", "show me the board" | `/ship-team` (task management) |

### Safety & Control
| Intent signals | Route to |
|---|---|
| "freeze", "lock", "don't touch [directory]" | `/ship-freeze` |
| "unfreeze", "unlock" | `/ship-unfreeze` |
| "be careful", "destructive command warnings" | `/ship-careful` |
| "guard mode", "both freeze and careful" | `/ship-guard` |
| "update ship", "update framework" | `/ship-update` |
| "codex review", "second opinion", "cross-model" | `/ship-codex` |

## Routing Rules

1. **Always route through /ship-team for complex requests.** If the request involves multiple steps (plan + build, review + fix, etc.), route to `/ship-team` which orchestrates the full pipeline.

2. **Single-step requests go direct.** "Fix this error" → `/ship-fix` directly. "Build a button" → `/ship-build` directly.

3. **Ambiguous requests default to /ship-team.** When intent is unclear, `/ship-team` figures out the right sequence.

4. **First interaction on empty project → setup.** If CLAUDE.md has unfilled fields (product name, stack), run `/ship-team` setup flow first.

5. **Pasted errors always → /ship-fix.** Any message containing a stack trace, error message, or "not working" routes to `/ship-fix`.

6. **"Continue" always → /ship-team.** Reads TASKS.md and picks up the next task.

7. **Trivial tasks skip ceremony.** If the request is obviously small (~5 lines or less) with clear intent — rename a variable, fix a typo, adjust a padding value, change a color, update a string — skip the full command protocol. No reference gate, no scope declaration, no blast radius check. Just make the change, verify it works (run tests or show output), and commit. Still follow the project's style and conventions from CLAUDE.md. If you're unsure whether it's trivial, it's not — route normally.

## Execution

Once you've identified the route:

1. Load the matching command file from `commands/ship-[command].md`
2. Read `team-rules.md` from the templates directory for team rules and agent definitions
3. Follow the command's full protocol — you ARE that agent now
4. End with the standard completion status

If the project hasn't been set up yet (no CLAUDE.md or empty fields), run the `/ship-team` first-run setup before routing.

## What This Skill Does NOT Handle

- General conversation unrelated to building products ("what's the weather", "tell me a joke")
- Questions about Claude itself or how to use Claude
- Tasks that have nothing to do with software development, product design, or shipping

For those, respond normally without invoking Ship Framework.
