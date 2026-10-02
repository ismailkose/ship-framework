Activate destructive command guardrails for this session.

Invoke the `ship-careful` skill with the Skill tool (plugin install: `ship-framework:ship-careful`). Invoking it registers its PreToolUse hook for the rest of the session — reading the file does not.

Once active, any destructive Bash command (rm -rf, DROP TABLE, git push --force, git reset --hard, kubectl delete, docker prune, etc.) will trigger a warning before executing. You must approve each one.

Safe exceptions (no warning): rm -rf on node_modules, .next, dist, build, coverage, and other common build artifacts.

Confirm activation: "Careful mode active. Destructive commands will require your approval."

To also restrict edits to a directory, use `guard [path]` instead.

## Status

End with where things stand, in plain words (`.claude/team-rules.md` › Status).

The founder's request: what they typed after `/shipmate` (without the stage name).
