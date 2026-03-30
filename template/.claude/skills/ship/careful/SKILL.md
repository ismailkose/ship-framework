---
name: ship-careful
description: |
  Destructive command guardrails. Warns before rm -rf, DROP TABLE, (ship)
  git push --force, and other dangerous operations.
  Activate with /ship-careful or /ship-guard.
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-careful.sh"
          statusMessage: "Checking for destructive commands..."
---

# Careful — Destructive Command Guardrails

This skill uses a PreToolUse hook to intercept Bash commands before they run. When a destructive pattern is detected, the user is warned and must approve before it executes.

## What It Catches

| Pattern | Example | Risk |
|---|---|---|
| `rm -rf` / `rm -r` | `rm -rf /var/data` | Recursive delete |
| `DROP TABLE` / `DROP DATABASE` | `DROP TABLE users;` | Data loss |
| `TRUNCATE` | `TRUNCATE orders;` | Data loss |
| `git push --force` / `-f` | `git push -f origin main` | History rewrite |
| `git reset --hard` | `git reset --hard HEAD~3` | Uncommitted work loss |
| `git checkout .` / `git restore .` | `git checkout .` | Uncommitted work loss |
| `git clean -f` | `git clean -fd` | Untracked file loss |
| `kubectl delete` | `kubectl delete pod` | Production impact |
| `docker rm -f` / `docker system prune` | `docker system prune -a` | Container/image loss |

## Safe Exceptions

These directories are safe to `rm -rf` without warning:
`node_modules`, `.next`, `dist`, `__pycache__`, `.cache`, `build`, `.turbo`, `coverage`, `.parcel-cache`, `.nuxt`, `.output`, `tmp`

## How It Works

The `check-careful.sh` script reads the Bash tool input from stdin (JSON), extracts the command, pattern-matches against the destructive list, and returns:
- `{}` — allow (safe command or safe exception)
- `{"permissionDecision": "ask", "message": "⚠️ Destructive: [pattern]. Approve?"}` — warn user
