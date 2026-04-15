---
name: ship-refgate
description: |
  Reference Gate — dimension-aware design gate. (ship)
  Classifies edits by dimension (ui/motion/copy/logic), hard-blocks
  when PDC.md is missing, and gates per-dimension until the relevant
  design section has been read. No gate for logic/test files.
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

# Reference Gate — Dimension-Aware Design Protection

This skill enforces Rule 25 (Reference Gate) as a real PreToolUse hook. It classifies edits by design dimension and ensures the relevant design context has been loaded before allowing changes.

## How It Works

1. **Classify** — extract file path from the pending edit, classify into a dimension:
   - `ui` — views, screens, components, pages, styles
   - `motion` — animation, transition, motion files
   - `copy` — localization, i18n, string resources
   - `logic` — models, services, utils, API (no design gate)
   - `none` — tests (no design gate)
2. **Check PDC** — for design dimensions (`ui`, `motion`, `copy`):
   - PDC.md missing → **hard block** with message to run `/ship-design init`
   - PDC.md exists → check if the relevant section has been read this session
3. **Per-dimension gating** — each dimension has its own lifecycle marker. Reading the motion section doesn't satisfy the UI gate, and vice versa.
4. **Backward compat** — framework references (`.refgate-loaded`) must still be loaded before any edit.

## Dimension Classification

| Signal | Dimension | Gate? |
|---|---|---|
| `*/views/*`, `*/components/*`, `*/pages/*`, `*.css` | `ui` | Yes |
| `*animation*`, `*motion*`, `*transition*` | `motion` | Yes |
| `*/Localizable*`, `*/i18n/*`, `*/locales/*` | `copy` | Yes |
| `*/models/*`, `*/services/*`, `*/utils/*`, `*/lib/*` | `logic` | No |
| `*/test*`, `*.test.*`, `*.spec.*` | `none` | No |
| Unknown paths | `ui` (safe default) | Yes |

## The Forcing Function

When PDC.md does not exist and an edit touches a design dimension, the gate **hard-blocks** with a message to run `/ship-design init`. This creates natural adoption pressure — the system degrades visibly without a design contract. Logic-only edits still work, so a project without PDC.md functions for non-UI work.

## State Files

| File | Created by | Meaning |
|---|---|---|
| `.claude/.refgate-loaded` | Ship commands (after REFERENCES LOADED receipt) | Framework references loaded this session |
| `.claude/.refgate-dim-ui` | Ship commands (after reading UI design section) | UI design section read this session |
| `.claude/.refgate-dim-motion` | Ship commands (after reading motion section) | Motion section read this session |
| `.claude/.refgate-dim-copy` | Ship commands (after reading copy section) | Copy section read this session |

## How Design Sections Get Marked as Read

When Ship commands read a design section (e.g., `/ship-build` reads the motion section from PDC.md), they create the dimension marker:

```bash
touch .claude/.refgate-dim-motion
```

This mirrors how `touch .claude/.refgate-loaded` works for framework references.

## Session Cleanup

All state files (`.refgate-loaded` and `.refgate-dim-*`) are cleaned at session start by `ship-sessionstart`. Each new session starts with a clean gate — design sections must be re-read.

## Compatibility

- Works alongside freeze and careful hooks — they all run independently on PreToolUse
- Does NOT interfere with Read, Grep, Glob, Bash — only blocks Edit and Write
- Fails open: if path extraction fails or the script errors, the edit is allowed
- Path-based classification is intentionally heuristic — false positives cost one design doc read (never harmful)
