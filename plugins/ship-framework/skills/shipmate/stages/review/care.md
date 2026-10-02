The care pass — `review --care` (preview). Read instead of `review.md`; it's self-contained.

For when the founder asks what's missing, what feels generic or how to make it feel cared for, and
for a promise's core journey. The lens is `${CLAUDE_PLUGIN_ROOT}/skills/ship-review/references/care-lens.md`.
It's report-first: nothing gets fixed until the founder picks. You orchestrate; you don't review.

1. **Journey files.** Pick the screens the task passes through, then run
   `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-review/bin/review.py scope --care --journey "<the task>" --paths <files>
   --commitment <ship.py state's commitment, or promise for the core journey; omit if neither>`.
2. **Point of view.** Read `DESIGN.md › ## Point of view`. If it's missing or incomplete, draft it
   (care-lens §1) into the run folder as `point-of-view.md`, with every drafted field marked
   proposed. Reviewers read it from there. DESIGN.md changes only when the founder confirms.
3. **Earlier rejections.** Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py query --domain care`,
   so gaps the founder rejected before aren't raised again.
4. **Blind look, then reviewers.** First capture the journey's first screen, garble it
   (`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/gibberish.py <shot>`, or `gibberish.js` in the page) and run
   `ship-eye` twice with only that image, the word `blind` and nothing about the product. Give both guesses to
   Pol with the image; nothing to capture or scramble → it goes under "Not checked". Then launch product review, design review and the visual check — subagents `ship-crit`,
   `ship-pol`, `ship-eye` (plugin: `ship-framework:<name>`) — in one message, one Agent call each,
   with the run folder, `${CLAUDE_PLUGIN_ROOT}/skills/ship-review/references/review-protocol.md`, the snapshot,
   depth `care`, the task, and "Reply with the JSON object only"; then say so in one line and stop
   until all have returned (each reports on its own). Each uses its care-lens §2 lens:
   - outputs carry `"mode": "care"`, the fingerprint from `scope.json`, and one dimension each
     (`journey`, `expression`, `task walk`);
   - map each gap onto the output: the moment and its evidence go in `why_it_matters` and
     `evidence`; the fix and how to check it go in `suggested_fix`; what already shows care goes in
     `notes`;
   - Pol also gets `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py sameness`;
   - Eye walks the task in the running build. If it can't run the build, it returns `skipped` with
     the reason, and the walk is listed under "Not checked": a code read isn't a task walk.
5. **Collect.** Save each reply verbatim to `<run>/<reviewer>.json` and run `review.py validate` on
   it; send errors back once, never edit a reviewer's findings. Without subagents, run the three
   lenses one after another yourself (`.claude/agents/ship-<name>.md`) and label the report
   **SINGLE-CONTEXT — NOT INDEPENDENT**.
6. **Consolidate, then report.** `review.py consolidate <run> --draft`, then `consolidate <run>`
   (add `--mode single-context` without subagents). Report in care-lens §4 form and ask which gap
   to fix first; after the founder picks, follow §5. The change review's extras (TODO scan,
   REF_SKIP, the reference check) don't apply.

A care record is kept apart from change reviews: it never satisfies launch's review gate. In a
project without `.ship/`, it uses a temporary folder.
