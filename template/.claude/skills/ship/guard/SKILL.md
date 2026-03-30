---
name: ship-guard
description: |
  Combined safety: destructive command warnings + directory-scoped edit restriction. (ship)
  Activate with /ship-guard [path].
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

`/ship-guard src/auth/` — enables careful warnings AND locks edits to `src/auth/`

This is equivalent to running `/ship-careful` and `/ship-freeze src/auth/` together.

See `careful/SKILL.md` for what destructive commands are caught.
See `freeze/SKILL.md` for how directory restriction works.
