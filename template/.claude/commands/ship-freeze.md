---
description: "Lock edits to a specific directory for this session."
disable-model-invocation: true
---

Lock edits to a specific directory for this session.

Read `.claude/skills/ship/freeze/SKILL.md` to load the PreToolUse hook.

Parse $ARGUMENTS for the directory path. If no path provided, ask: "Which directory should I lock edits to?"

Write the path to `.claude/.freeze-path`:
```bash
echo "$ARGUMENTS" > .claude/.freeze-path
```

Once active, any Edit or Write to a file OUTSIDE the specified directory is hard-blocked. Edits inside the directory work normally.

Confirm activation: "Freeze active. Edits locked to [path]/. Use /ship-unfreeze to remove."

To also get destructive command warnings, use `/ship-guard [path]` instead.

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [directory path]

User's request: $ARGUMENTS
