Upgrade Ship Framework to the latest version. Run this from inside Claude Code — no terminal needed.

## Steps

1. **Run the project-local update script** — Look for `ship-update.sh` in the project root:
   ```
   bash ship-update.sh
   ```
   It shallow-clones the latest from GitHub into a temp directory, syncs everything, and cleans up automatically.

2. **If `ship-update.sh` is missing** — The project was set up before self-contained updates existed. Create it:
   ```
   curl -fsSL https://raw.githubusercontent.com/ismailkose/ship-framework/main/template/ship-update.sh -o ship-update.sh && chmod +x ship-update.sh && bash ship-update.sh
   ```

3. **Report** — Show the output from the update script. If it succeeded, confirm the version change.

## What the update script handles
- Shallow-clones latest from GitHub (no persistent clone needed)
- Compares versions and shows changelog
- Syncs the entire `template/` directory (commands, references, frameworks, any new files/directories)
- Protects user-customized files (CLAUDE.md content, TASKS.md, design-system.md)
- Updates CHEATSHEET.md
- Creates new template files (DECISIONS.md, CONTEXT.md) if missing
- Stamps the version in CLAUDE.md footer
- Updates itself (ship-update.sh self-update)

## Rules
- ALWAYS use ship-update.sh — never duplicate its logic here
- NEVER overwrite CLAUDE.md content, TASKS.md, or design-system.md manually

---

## Completion Status

End your output with one of:
- `STATUS: DONE` — completed successfully
- `STATUS: DONE_WITH_CONCERNS` — completed, but [list concerns]
- `STATUS: BLOCKED` — cannot proceed: [what's needed]
- `STATUS: NEEDS_CONTEXT` — missing: [what information]

User's request: $ARGUMENTS
