<!-- ship-reference
id: review-protocol
kind: ship-default
sources: Ship-only (C-06/C-07/C-08, docs/REVIEW-RECONCILIATION.md #2); Claude Code subagents docs (code.claude.com/docs/en/sub-agents, read 2026-09-23)
reviewed: 2026-09-23
-->

# Review protocol — shared by Crit, Pol, Eye, Test, Adversarial

Every reviewer reads this once. Your agent file says *what* to look at; this says *how* to report.

## What you receive

The orchestrator (/shipmate review) gives you a run folder `.ship/reviews/runs/<run>/` containing:

- `scope.json` — `fingerprint.tree` (the exact snapshot under review), `base`, `reviewed_paths`,
  `signals` (UI / risk / size), `depth`.
- `diff.patch` — base → snapshot. Includes staged, unstaged, and new untracked files. Review
  this, not `git diff` (which misses untracked files and may be taken after someone edits).
- `shots/` — screenshots or recordings (Eye writes here; others may read).
- Your focus inputs in the prompt (plan item, reported symptom, screens to check, …).

First-wave reviewers (Crit, Pol, Eye, Test) do **not** see each other's findings. Don't go looking
for them. Adversarial runs second and sees `merged.json` (all first-wave findings, deduplicated).

## Rules

1. **Evidence or it isn't a finding.** Each finding cites something checkable: `file`+`line`,
   a `screenshot`, a `command` with its `output`, or an exact `quote` from a plan/decision file.
   A hunch without evidence goes in `notes` as a question. **One finding per root cause:** the
   same problem in several places is one finding, every place in `evidence.locations`
   (`[{file, line}]`) — fixed once, at the token or component. Say how you know: *source read*,
   *rendered* (which engine / viewport), *synthesized input*, or *device*. A screenshot shows
   layout; it doesn't verify a gesture or a screen-reader announcement.
2. **No scores.** No 0–100 health, no /70 readiness, no confidence percentages. Use severity,
   evidence, and `confidence_reason` (what you checked; what you couldn't).
3. **Severity by consequence:**
   - `blocker` — breaks the core task, loses or leaks data, crashes, security hole, App Review /
     store rejection, or an accessibility failure that blocks use.
   - `major` — noticeably degrades a primary flow, or contradicts an explicit product decision
     (`DECISIONS.md`, `design-model.yaml`, `design/components.yaml`, a confirmed `DESIGN.md`
     direction, an approved screen in `design/approved/`).
   - `minor` — real but contained; secondary flow or polish users would notice.
   - `nit` — taste or tidiness; fine to skip.
4. **Precedence when sources disagree:** platform requirements & accessibility → explicit product
   decisions → founder preferences (taste store) → platform design guidance (HIG, Material) →
   expert sources → Ship defaults → your own inference. Never flag a product decision as wrong
   because a lower tier disagrees — note the tension instead.
5. **Judge against the bar, not the effort.** The bar is the product's own contract and approved
   screens, the platform, and the best work of its kind. A fix is an instruction ("set the body to
   the 17 pt text style"), not "consider…"; don't soften a finding because the work shows care.
   Say what already works and must be kept, so a fix doesn't undo it.
6. **Stay in your lane.** Report what your role covers; one line in `notes` for anything else.
7. **Read, don't write.** You have no Edit/Write tools. Bash can still write — that's not a
   boundary, it's your instruction: don't change tracked files, don't commit, don't install
   packages. Scratch output goes under the run folder. If a command you ran changed tracked
   files (snapshots, lockfiles), say so in `notes`. The orchestrator re-fingerprints after you.
8. **Say which snapshot you reviewed** (`fingerprint`) and **your model** (`model`: the exact
   model ID from your environment section, or null).
9. **Dimensions** — never a number: `pass` / `concerns` (you checked it), `not-applicable` (the
   change can't affect it — say why in `note`), or `not-checked` (it applies but you couldn't
   verify it). Report every dimension your role lists. A review counts as complete only when
   something was checked and nothing applicable is unverified or unreported — otherwise it's
   partial, and the launch gate says INCOMPLETE until it's finished or the founder accepts it.

## Output — reply with one JSON object, nothing else

Shape: `reviewer-output.schema.json` next to this file. Check it with
`python3 .claude/skills/ship/review/bin/review.py validate <file>` if you save a copy.

```json
{
  "reviewer": "crit",
  "status": "completed",
  "fingerprint": "3f1c2a9e0b7d4c6e8a1f2b3c4d5e6f708192a3b4",
  "model": "claude-opus-4-7",
  "findings": [
    {
      "id": "crit-1",
      "severity": "major",
      "claim": "Saving an empty title silently discards the draft",
      "evidence": {"file": "src/editor/save.ts", "line": "41-47"},
      "why_it_matters": "A user who taps Save before typing a title loses everything they wrote, with no message.",
      "suggested_fix": "Keep the draft and show an inline 'Add a title' hint instead of returning early.",
      "confidence_reason": "Read the early return on line 43 and traced both callers; did not run the app."
    }
  ],
  "dimensions": [
    {"name": "task success", "result": "concerns", "note": "empty-title path loses data"},
    {"name": "states", "result": "pass", "note": "loading, error, empty covered"}
  ],
  "notes": "References used: ux/references/interaction-design.md §1."
}
```

**Citations:** `evidence.line` is one line or one range (`"41-47"`); every other place goes in
`evidence.locations` as `{file, line, note}`, and a label for the main range in `line_note`. (A
list like `"9, 112-133"` is split that way for you and the change is recorded — write it
correctly to keep your report exactly as you sent it.)

**Required by role** — missing these makes the report invalid, and you'll be asked again:
- **Test:** `"commands_run": [{"command": "...", "exit_code": 0, "summary": "..."}]` — every
  command you ran, as data, not only in `notes`.
- **Eye:** `"artifacts": ["shots/01-main.png", …]` — every screenshot or recording you looked at.

Status: `completed`, `partial` (say what you didn't get to in `notes`), or `skipped` with
`skipped_reason` (e.g. Eye had no way to render the app). A skipped reviewer is reported as
such — never as a pass.
Your file name, `reviewer` field, and echoed `fingerprint` must match the run: output under another
reviewer's name, or for another snapshot, doesn't count. The record tracks completion (did every
selected reviewer finish on this snapshot?) separately from findings and freshness; anything short
of complete is verdict `incomplete`, and `/shipmate launch`'s `review.py gate` won't pass it.
