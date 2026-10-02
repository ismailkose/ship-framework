---
name: ship-router
description: >
  Picks the matching Ship workflow for product work in a Ship project when the user didn't type
  /shipmate: a bug, error, broken screen, or a TASKS.md item to take care of → /shipmate fix or
  /shipmate build; a new feature, screen, or UI/motion change → /shipmate build; "review this" / "is this
  ready" → /shipmate review; "it feels generic", "what's missing", "make it feel cared for", "watch people
  use it" → /shipmate review --care; "is this worth building", a new idea → /shipmate think; design
  direction or tokens → /shipmate design; pricing or payments → /shipmate money; planning, launch,
  retro, "continue" → the matching stage. Skip it for trivial edits (typo, rename) and for
  conversation that isn't product work.
user-invocable: false
---

# Ship Framework — Auto-Router

The user asked for product work without typing `/shipmate`. Run it for them: read
`${CLAUDE_PLUGIN_ROOT}/skills/shipmate/SKILL.md` and follow it, with the user's message as the
request. That file is the one routing source — its stage table and rules pick the stage; then read
the stage file it names and follow it fully. Never ask "which command do you want?" — pick the right
stage and run it.

Plugin folder: `${CLAUDE_PLUGIN_ROOT}`. The entry and its stage files are read as plain files, so
where they write this folder's token (CLAUDE_PLUGIN_ROOT in braces), read it as this folder.

Start with `python3 "${CLAUDE_PLUGIN_ROOT}/skills/ship-knowledge/bin/knowledge.py" project` — it reports the stack and the project's own instructions without writing anything; every stage works from that. Only when the founder wants Ship's files in the project (no CLAUDE.md, or one without a `## Ship Framework` section) run `bash "${CLAUDE_PLUGIN_ROOT}/bin/bootstrap-project.sh"` from the project root — ask first when the project has its own instructions (`AGENTS.md`, its own `CLAUDE.md`). It creates or appends CLAUDE.md, adds TASKS/DECISIONS/CONTEXT/LEARNINGS.md if missing, and syncs `.claude/team-rules.md`; it never overwrites your files. Then run the `team` stage's first-run setup before routing.

## What This Skill Does NOT Handle

- General conversation unrelated to building products ("what's the weather", "tell me a joke")
- Questions about Claude itself or how to use Claude
- Tasks that have nothing to do with software development, product design, or shipping

For those, respond normally without invoking Ship Framework.
