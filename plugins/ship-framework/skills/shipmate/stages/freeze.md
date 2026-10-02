Lock edits to a specific directory for this session.

Invoke the `ship-freeze` skill with the Skill tool (plugin install: `ship-framework:ship-freeze`). Invoking it registers its PreToolUse hooks for the rest of the session — reading the file does not.

Parse the founder's request for the directory path. If no path provided, ask: "Which directory should I lock edits to?"

Write the path to `.claude/.freeze-path`:
```bash
echo "<directory path from the request>" > .claude/.freeze-path
```

Once active, any Edit or Write to a file OUTSIDE the specified directory is hard-blocked. Edits inside the directory work normally.

Confirm activation: "Freeze active. Edits locked to [path]/. Say `unfreeze` to remove it."

To also get destructive command warnings, use `guard [path]` instead.

## Status

End with where things stand, in plain words (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Status); no folder given means ask which one.

The founder's request: what they typed after `/shipmate` (without the stage name).
