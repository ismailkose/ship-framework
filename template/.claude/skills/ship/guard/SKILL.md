---
name: ship-guard
description: |
  Hook holder for /shipmate guard: destructive-command warnings + directory-scoped edit (ship)
  restriction. Invoked by /shipmate guard (invoking it registers the hooks for the session); not a
  user command.
user-invocable: false
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../careful/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/../freeze/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---

# Guard — Combined Safety (Careful + Freeze)

Activates both destructive command warnings (careful) and directory-scoped edit restriction (freeze) in one command.

## Usage

`/shipmate guard src/auth/` — enables careful warnings AND locks edits to `src/auth/`

This is equivalent to running `/shipmate careful` and `/shipmate freeze src/auth/` together.

See `careful/SKILL.md` for what destructive commands are caught.
See `freeze/SKILL.md` for how directory restriction works.
