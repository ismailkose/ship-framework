---
description: "Activate full safety: destructive command warnings + directory-scoped edit restriction."
disable-model-invocation: true
---

Activate full safety: destructive command warnings + directory-scoped edit restriction.

Read `.claude/skills/ship/guard/SKILL.md` to load the combined PreToolUse hooks.

Parse $ARGUMENTS for the directory path. If no path provided, ask: "Which directory should I lock edits to?"

Write the freeze path to `.claude/.freeze-path`:
```bash
echo "$ARGUMENTS" > .claude/.freeze-path
```

Once active:
1. Destructive Bash commands (rm -rf, DROP TABLE, etc.) trigger a warning
2. Any Edit or Write outside the specified directory is hard-blocked

Confirm activation: "Guard active. Destructive commands need approval. Edits locked to [path]/. Use /ship-unfreeze to unlock edits."

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [directory path]

User's request: $ARGUMENTS
