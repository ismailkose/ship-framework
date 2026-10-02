Activate full safety: destructive command warnings + directory-scoped edit restriction.

Invoke the `ship-guard` skill with the Skill tool (plugin install: `ship-framework:ship-guard`). Invoking it registers the combined PreToolUse hooks for the rest of the session — reading the file does not.

Parse the founder's request for the directory path. If no path provided, ask: "Which directory should I lock edits to?"

Write the freeze path to `.claude/.freeze-path`:
```bash
echo "<directory path from the request>" > .claude/.freeze-path
```

Once active:
1. Destructive Bash commands (rm -rf, DROP TABLE, etc.) trigger a warning
2. Any Edit or Write outside the specified directory is hard-blocked

Confirm activation: "Guard active. Destructive commands need approval. Edits locked to [path]/. Say `unfreeze` to unlock edits."

## Status

End with where things stand, in plain words (`.claude/team-rules.md` › Status); no folder given means ask which one.

The founder's request: what they typed after `/shipmate` (without the stage name).
