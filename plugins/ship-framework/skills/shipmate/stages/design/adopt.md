## Adopt — an existing app · part of the design stage, read only on this path

The app's working system is the starting point. Nothing in the app is rewritten; views keep
compiling against the same names.

1. **Draft from the code:**
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py adopt --platform auto
   ```
   It writes `design-model.draft.yaml` + `design/components.draft.yaml` (origin: adopted), keeps
   existing names through `emit.swiftui.namespaces`/`rename` or `emit.css.prefix`/`rename`, and
   prints notes for what it couldn't read. It never touches `design-model.yaml`.
   It reads every source file under the project root. If the repo also holds fixtures, samples,
   solutions or a second app, scope it first: `--root <the app's folder>`, or `--exclude '<glob>'`
   (repeatable). If it's unclear which folder is the app, ask.
2. **Fill what the code couldn't say,** from the code itself where possible (a value adopt
   couldn't parse, a role no colour matched). Then see how consistently the app uses its own scale:
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py audit --model design-model.draft.yaml`
   — raw literals off the scale and repeated patterns: evidence for the founder, not a to-do list.
3. **Show the founder the draft** in plain terms: the palette and type as found, what looks
   accidental (three near-identical greys, one-off radii), and the components found. Ask only
   what the code can't answer: which near-duplicates are really one token, which inventory
   entries are screen compositions to drop. Draft the point of view (`DESIGN.md › ## Point of
   view`) from the app and mark it proposed; the founder confirms by picking between two concrete
   versions, never by naming adjectives. `brand.feel` stays empty unless they offer words. Record each answer as a taste
   decision (below). Don't "improve" values they didn't ask to change.
4. **Finish the component draft:** delete screen-specific compositions; give each kept entry
   `role`, `use_when`, `not_for`, and `api`.
5. **Accept the draft:** rename the two files to `design-model.yaml` and `design/components.yaml`,
   then `design_model.py validate` and fix every error. REQ warnings (colour contrast) describe the
   app as it is: list them for the founder with the fix, never change its colours silently.
6. **Prove nothing moved:** emit to scratch and diff every token against the old theme file.
   ```bash
   python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py emit swiftui --out /tmp/ship-adopt/Theme.swift   # web: emit css
   diff -u <old theme file> /tmp/ship-adopt/Theme.swift
   ```
   (Any scratch path outside the app's sources.) Every difference is either a formatting change or a decision the founder just made. Anything
   else: fix the model, re-emit, re-diff.
7. **Replace:** set `emit.<target>.out` to the old theme's path, `emit all --force` once (the old
   file is hand-written, so the emitter refuses without it), build the app, and screenshot the
   same screens before/after — they must match. Then `design_model.py docs`. A shadcn/ui project
   replaces nothing: the draft emits `tokens.css` beside the global stylesheet; add its import
   (`${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/shadcn.md` › Token mapping).
8. Write the short **DESIGN.md** (intent, voice, do/don't — the reasons behind what exists) and
   **PDC.md**. Proof: the before/after screenshots.
