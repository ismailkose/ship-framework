`qa` is kept as a shortcut. It runs **`review --test`**: read the review stage
(`${CLAUDE_PLUGIN_ROOT}/skills/shipmate/stages/review.md`; plugin install: `${CLAUDE_PLUGIN_ROOT}/skills/shipmate/stages/review.md`)
and follow it exactly, with only the Test reviewer selected
(`review.py scope --only test`), and pass the founder's request through as the focus (a symptom to
reproduce, a test command, or acceptance criteria).

The Test reviewer runs the project's tests, reproduces the reported symptom, and checks the
changed behaviour for regressions. Every finding carries the command and its output; the result
is pass / concerns / blockers with that evidence — there is no numeric score. The run is recorded
like any review, so `launch`'s freshness check sees it.

Want more than tests? A full `review` sizes the reviewers to the change; `--report` gives findings
without fixes.

The founder's request: what they typed after `/shipmate` (without the stage name).
