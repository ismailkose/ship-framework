---
name: ship-sessionstart
description: |
  SessionStart hook — loads project context when a Claude Code session begins. (ship)
  Sets SHIP_STACK, SHIP_VERSION, SHIP_PRODUCT env vars.
  Cleans stale refgate state. Prints project status.
hooks:
  SessionStart:
    - matcher: "*"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/session-start.sh"
          timeout: 5000
          statusMessage: "Loading Ship Framework context..."
---

# SessionStart — Automatic Project Context

This skill fires once when a Claude Code session begins in a Ship Framework project. It gives Claude immediate awareness of the project without needing to read CLAUDE.md manually.

## What It Does

1. **Reads CLAUDE.md** — extracts Stack, product name, and framework version
2. **Counts project state** — open tasks (TASKS.md), decisions (DECISIONS.md), learnings (LEARNINGS.md)
3. **Cleans refgate state** — removes `.claude/.refgate-loaded` and `.claude/.refgate-passed` from previous sessions so the Reference Gate fires fresh
4. **Sets environment variables** — `SHIP_STACK`, `SHIP_VERSION`, `SHIP_PRODUCT` available to all subsequent hooks and scripts via `$CLAUDE_ENV_FILE`
5. **Prints context** — status line shown to Claude as initial session context

## Environment Variables Set

| Variable | Source | Example |
|---|---|---|
| `SHIP_STACK` | `Stack:` line in CLAUDE.md | `web`, `ios`, `android` |
| `SHIP_VERSION` | Footer in CLAUDE.md | `v2026.04.11` |
| `SHIP_PRODUCT` | First heading in CLAUDE.md | `CoachEva` |

## Gentle Warnings

The script warns (does not block) when:
- Product name is still `[Your Product Name]` (template default)
- Stack is not set (no platform skills will auto-activate)

## Timing

Runs once at session start. Under 1 second (file reads and grep only). Well within the 5-second timeout.
