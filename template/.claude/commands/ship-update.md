Upgrade Ship Framework to the latest version. Run this from inside Claude Code — no terminal needed.

## Steps

1. **Find the Ship Framework repo** — Look for the `ship-framework` or `designer-ship-framework` directory. Check common locations:
   - `../ship-framework/`
   - `~/ship-framework/`
   - `~/designer-ship-framework/`
   - Check if there's a path in the CLAUDE.md footer (look for the GitHub URL)
   - If not found, ask: "Where is your ship-framework directory?"

2. **Pull latest** — Run `git -C <framework-dir> pull` to get the latest version.

3. **Read the new VERSION** — `cat <framework-dir>/VERSION`

4. **Compare versions** — Check the current version in CLAUDE.md footer vs the new VERSION. If already up to date, say so and stop.

5. **Show what changed** — Read the CHANGELOG.md from the framework repo. Show the entries between the current version and the new version.

6. **Update files** — Copy the following from `<framework-dir>/template/` to the current project:
   - `.claude/commands/*.md` — all slash commands (overwrite)
   - `references/*.md` — all reference files EXCEPT `design-system.md` (never overwrite user's design system)
   - Copy `<framework-dir>/CHEATSHEET.md` to `./CHEATSHEET.md`
   - Create `DECISIONS.md` from template if it doesn't exist
   - Create `CONTEXT.md` from template if it doesn't exist

7. **Stamp version** — Update the version number in the CLAUDE.md footer line (the line with "Ship Framework" and a version number).

8. **Report** — Show what was updated, what was added, and the version change. Mention that CLAUDE.md content, TASKS.md, and project files were NOT touched.

## Rules
- NEVER overwrite CLAUDE.md content (only the version stamp in the footer)
- NEVER overwrite TASKS.md
- NEVER overwrite `references/design-system.md` if it exists
- NEVER overwrite DECISIONS.md or CONTEXT.md if they exist

User's request: $ARGUMENTS
