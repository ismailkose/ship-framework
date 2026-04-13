---
name: ship-refgate
description: |
  Reference Gate — blocks first Edit/Write until references are loaded. (ship)
  Hard block on first edit, no-op after refs are confirmed.
  Activated automatically. No user command needed.
user-invocable: false
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-refgate.sh"
          statusMessage: "Checking reference gate..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-refgate.sh"
          statusMessage: "Checking reference gate..."
---

# Reference Gate — First-Edit Protection

This skill enforces Rule 25 (Reference Gate) as a real PreToolUse hook. It blocks the first Edit or Write operation in a session if references haven't been loaded yet.

## How It Works

Hard block on the first edit, no-op after that.

1. Session starts — no state files exist
2. Agent tries first Edit/Write → hook checks for `.claude/.refgate-loaded`
3. If missing → **hard block** with message to load references first
4. Agent loads references → command prints `REFERENCES LOADED` receipt → creates `.claude/.refgate-loaded`
5. Agent tries edit again → hook sees `.refgate-loaded`, creates `.refgate-passed`, allows edit
6. All subsequent edits → hook sees `.refgate-passed` → instant allow (no-op)

## State Files

| File | Created by | Meaning |
|---|---|---|
| `.claude/.refgate-loaded` | Ship commands (after printing REFERENCES LOADED receipt) | References have been read this session |
| `.claude/.refgate-passed` | This hook (after first allowed edit) | Gate passed, no more checks needed |

## How References Get Marked as Loaded

Ship commands already print a `REFERENCES LOADED:` receipt. To wire this into the hook, commands should also create the state file:

```bash
touch .claude/.refgate-loaded
```

This happens inside the command workflow — after the agent reads the relevant reference files and prints the receipt.

## Session Cleanup

Both state files are cleaned automatically at session start by the `ship-sessionstart` hook. If they persist between sessions (e.g., on older versions without the session start hook), the gate won't fire — but that's acceptable since a new session means a new context window where references need re-reading anyway.

## Compatibility

- Works alongside freeze and careful hooks — they all run independently on PreToolUse
- Does NOT interfere with Read, Grep, Glob, Bash — only blocks Edit and Write
- Fails open: if the state check errors, the script exits before reaching the deny block
