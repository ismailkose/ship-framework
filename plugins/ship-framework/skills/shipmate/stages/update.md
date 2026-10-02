Upgrade Ship Framework to the latest version without touching the founder's own files.

## Which install is this?

- **Plugin install** (the project has no `.claude/skills/ship` folder; Ship's commands come from the
  `ship-framework` plugin): Ship updates through Claude Code, not a script. Tell the founder to run
  `claude plugin marketplace update ship-framework` then `claude plugin update ship-framework@ship-framework`
  in a terminal (or turn on auto-update in `/plugin` › Marketplaces), then restart or `/reload-plugins`.
  A plugin installed from a downloaded `.plugin` file updates by installing the newer file. Stop here.
- **Project install** (the project has a `.claude/skills/ship` folder — from `setup.sh`): continue.

## Steps

1. **Preview** — `bash ship-update.sh --dry-run`. Show the founder what would be created, updated,
   backed up, and removed. If `ship-update.sh` is missing, fetch it first:
   `curl -fsSL https://raw.githubusercontent.com/ismailkose/ship-framework/main/template/ship-update.sh -o ship-update.sh && chmod +x ship-update.sh`
2. **Update** — `bash ship-update.sh`. Offline, with a local Ship checkout: `bash ship-update.sh --from <path>`.
3. **Report** — the version change, anything backed up (`.ship/backups/<stamp>/` — files the founder had
   edited that Ship replaced or retired), anything left alone because it's the founder's, and the
   optional-capabilities lines. Suggest restarting Claude Code so new commands and agents load.

## What the update touches

- **Replaces** Ship's own files: `${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md`, everything under `.claude/skills/ship` and
  `.claude/skills/shipmate`, Ship's agents, a Ship-managed `AGENTS.md` and `.ship/framework.yaml`, and
  the `ship-generated` / `ship-managed` blocks plus the version line in `CLAUDE.md`. An older Ship
  section in `CLAUDE.md` gets the current wording only if it's exactly what Ship wrote. An edited copy
  is backed up first.
- **Removes** files Ship retired. Edited ones go to `.ship/backups/<stamp>/` instead of being lost.
- **Never touches** the founder's files: the rest of `CLAUDE.md`, `TASKS.md`, `DECISIONS.md`,
  `CONTEXT.md`, `LEARNINGS.md`, `DESIGN.md`, `PDC.md`, `design-model.yaml`, `design/`, taste stores,
  `references/`, `.claude/skills/your-skills/`, other agents/commands, and settings (Ship only adds
  its hooks next to existing ones).

## Rules
- ALWAYS use `ship-update.sh` — never copy Ship files by hand or re-implement its logic here.
- NEVER restore a backup over a Ship file without asking; a backup is the founder's edit to re-apply.

## Status

End with where things stand, in plain words (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › Status).

The founder's request: what they typed after `/shipmate` (without the stage name).
