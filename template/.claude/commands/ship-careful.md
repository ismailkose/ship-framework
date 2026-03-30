Activate destructive command guardrails for this session.

Read `.claude/skills/ship/careful/SKILL.md` to load the PreToolUse hook.

Once active, any destructive Bash command (rm -rf, DROP TABLE, git push --force, git reset --hard, kubectl delete, docker prune, etc.) will trigger a warning before executing. You must approve each one.

Safe exceptions (no warning): rm -rf on node_modules, .next, dist, build, coverage, and other common build artifacts.

Confirm activation: "Careful mode active. Destructive commands will require your approval."

To also restrict edits to a directory, use `/ship-guard [path]` instead.

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: BLOCKED` — cannot proceed: [what's needed]

User's request: $ARGUMENTS
