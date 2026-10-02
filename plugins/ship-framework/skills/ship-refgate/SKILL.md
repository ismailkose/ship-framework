---
name: ship-refgate
description: |
  Design gate. (ship) In a Ship project without a design contract (PDC.md), creating a
  new UI/motion/copy file is blocked with the on-ramp to /shipmate design. Edits to existing
  files, logic, tests, and design files are never blocked. Activated automatically.
user-invocable: false
hooks:
  PreToolUse:
    - matcher: "Edit"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-refgate.sh"
          statusMessage: "Checking design gate..."
    - matcher: "Write"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-refgate.sh"
          statusMessage: "Checking design gate..."
  PostToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "bash ${CLAUDE_SKILL_DIR}/bin/check-after-shell.sh"
---

# Design Gate

A PreToolUse hook on Edit and Write. One job: new UI shouldn't be invented before the
product has a design contract — `PDC.md`, which indexes `DESIGN.md`, `design-model.yaml`,
and `design/components.yaml`. Once the contract exists, the registry loop in /shipmate build
does the rest; the gate steps aside.

| The edit | No PDC.md | PDC.md exists |
|---|---|---|
| Creates a new UI / motion / copy file | **deny** — on-ramp to `/shipmate design` (adopt an existing app's system, or plant a seed) | allow |
| Changes an existing file | allow — a fix in an existing app is never locked out | allow |
| Logic, tests, config, design files, Ship memory | allow | allow |
| Not a Ship project | allow | allow |

**Two checks, honestly labelled.** The table above is *preventive*: it runs before Edit and Write
and can refuse them. A shell command (`sed -i`, a script, a heredoc) writes without passing through
it, so `check-after-shell.sh` runs *after* each Bash call and reports what the gate would have
refused: a generated file that differs from what `design-model.yaml` emits (re-emitted to a temp file
and compared — works without configured outputs), or a
new UI file created without the contract (a file that matches the emitter is the model's output and
is never flagged). That's *detection* — it can't undo the write. Limits: git projects only; it compares
against the last commit — staged, unstaged and untracked changes — so ignored files, files outside the
project, a write reverted or committed within the same command aren't seen; each file version is
reported once. The
generated-file rule applies in any project — the header marks the file — while the new-UI rule
applies only to Ship projects.

Classification uses the path inside the project, so a project folder named `motion` or
`components` doesn't change the verdict. No reading receipts or marker files: references are
loaded on demand (`${CLAUDE_PLUGIN_ROOT}/templates/team-rules.md` › References on demand) and review judges outcomes. The gate fails open on anything it
can't parse, and writes nothing in the project (the after-shell check keeps a small "already
reported" list in the system temp folder).

Works alongside the careful and freeze hooks; never touches Read, Grep, Glob, or Bash.
