Upgrade Ship Framework to the latest version. Run this from inside Claude Code — no terminal needed.

## Steps

1. **Find the Ship Framework repo** — Look for the `ship-framework` or `designer-ship-framework` directory. Check common locations:
   - `../ship-framework/`
   - `~/ship-framework/`
   - `~/designer-ship-framework/`
   - Check if there's a path in the CLAUDE.md footer (look for the GitHub URL)
   - If not found, ask: "Where is your ship-framework directory?"

2. **Run update.sh** — This is the single source of truth for all sync logic. Run:
   ```
   bash <framework-dir>/update.sh <project-dir>
   ```
   Where `<project-dir>` is the current working directory (`.` or the absolute path).

   `update.sh` handles everything:
   - Pulls latest from git
   - Compares versions and shows changelog
   - Syncs the entire `template/` directory (commands, references, frameworks, any new files/directories)
   - Protects user-customized files (CLAUDE.md content, TASKS.md, design-system.md)
   - Updates CHEATSHEET.md
   - Creates new template files (DECISIONS.md, CONTEXT.md) if missing
   - Stamps the version in CLAUDE.md footer

3. **Report** — Show the output from update.sh. If it succeeded, confirm the version change.

## Rules
- ALWAYS use update.sh — never duplicate its logic here
- If update.sh doesn't exist (very old framework version), tell the user to `git pull` the framework repo first
- NEVER overwrite CLAUDE.md content, TASKS.md, or design-system.md manually

User's request: $ARGUMENTS
