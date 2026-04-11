---
description: "Remove the directory-scoped edit restriction."
disable-model-invocation: true
---

Remove the directory-scoped edit restriction.

Delete the freeze state file:
```bash
rm -f .claude/.freeze-path
```

Confirm: "Freeze removed. Edits are no longer restricted to a directory."

If no freeze was active: "No freeze was active — edits were already unrestricted."

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully

User's request: $ARGUMENTS
