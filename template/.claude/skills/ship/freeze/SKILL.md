---
name: ship-freeze
description: |
  Directory-scoped edit restriction. Locks edits to a specific directory. (ship)
  Files outside the frozen boundary are hard-blocked.
  Activate with /ship-freeze [path] or /ship-guard [path].
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-freeze.sh"
          statusMessage: "Checking freeze boundary..."
---

# Freeze — Directory-Scoped Edit Restriction

This skill uses PreToolUse hooks on Edit and Write to enforce a directory boundary. Once activated, any file edit OUTSIDE the frozen path is hard-blocked.

## How to Use

1. `/ship-freeze src/auth/` — locks edits to `src/auth/` and its subdirectories
2. Work freely inside the boundary — all edits within `src/auth/` are allowed
3. Any attempt to edit a file outside `src/auth/` is denied
4. `/ship-unfreeze` — removes the restriction

## Use Cases

- "I'm refactoring auth. Lock edits to `src/auth/` so nothing else changes."
- "Only touch the components directory until this feature is done."
- "Lock to `src/api/` while I fix the API layer."

## How It Works

The `check-freeze.sh` script:
1. Reads a state file (`.claude/.freeze-path`) for the active boundary
2. If no freeze is active, allows all edits
3. If frozen, resolves the target file path and checks if it's inside the boundary
4. Inside boundary → `{}` (allow)
5. Outside boundary → `{"permissionDecision": "deny", "message": "..."}` (hard block)

Path resolution is POSIX-portable (works on macOS and Linux). Symlinks are resolved.
