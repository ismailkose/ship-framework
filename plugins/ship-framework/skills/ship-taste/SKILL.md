---
name: ship-taste
description: |
  The founder's taste, recorded and reused. (ship)
  Record right away when the founder approves, rejects, corrects, or shows an example of a
  design choice. Look up before UI, design, copy, or motion work and in Pol's review.
  Loaded by /shipmate build, /shipmate review, /shipmate variants, /shipmate design, /shipmate retro.
user-invocable: false
---

# Taste — the founder's judgments, kept

The registry (`design-model.yaml`, `design/components.yaml`) holds **what exists**: tokens and
components. Taste holds **judgments** about how to use them, with context and the founder's own
words: "cards never have shadows", "copy is terse", "prefer system sheets over custom drawers
on iOS". When the two disagree, the registry is the realized fact and taste is the reason:
flag the mismatch and don't change either on your own.

Tool (stdlib Python, same for Claude and Codex):
`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py <command>`. Schema, kinds and lifecycle are in
`${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/references/taste-schema.md`.

| Scope | File | Contains |
|---|---|---|
| product | `design/taste.yaml` | decisions for this product, your inferences, expert stances |
| founder | `~/.ship/taste.yaml` (`$SHIP_HOME`) | preferences the founder confirmed hold across products |

## Precedence

Platform requirements and accessibility → **product decision** → **founder preference** (only
where the context matches) → expert references (not stored: follow the loaded reference) →
**inference** (never applied; ask first). A dependency or Ship update never rewrites taste.

`query` applies this order for you and lists conflicts. Report conflicts to the founder and
don't pick a winner quietly. An `UNRESOLVED` conflict means two entries at the same level
disagree: ask the founder, then `supersede` one.

## Look up (before you design or build)

Before UI, design, copy, or motion work, query with the context you're about to touch:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py query --surface workout-picker --component sheet --domain motion,layout
```

`platform` and `product_type` come from the product's `design/taste.yaml` header unless you pass
them. Follow the **APPLY** lines. Don't apply **ASK FIRST** lines. If one of them would change
what you build, ask about it (see below). In your handoff, name the ids you followed or
departed from, e.g. `Taste: followed t-2026-09-23-001, tf-2026-09-20-002`.

**Pol's review:** run the same query for the surfaces in the diff. A violated APPLY line is a
finding and cites the id and the founder's quote. An inference is never a finding.

## Record (the moment it happens)

**The founder said it → record it now, as a decision, with their words.** Approval, rejection,
correction, or "like this" all count. So does picking a variant on the board, and so does
an edit they make to your UI.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py add --kind decision --source correction \
  --topic card-elevation --statement "Cards never have shadows; separate with hairlines." \
  --rationale "Shadows read as generic next to the calm palette." \
  --quote "no shadows on cards, ever" --component card --domain layout --file App/Views/StatCard.swift
```

- `--source`: `approval` | `rejection` (record what to do instead, e.g. "no gradient headers") |
  `correction` | `example` (point `--file`/`--screenshot`/`--url` at it — a site the founder admires is
  an example too: record what it lends, in their words).
- `--rationale` is the founder's reason if they gave one. If they didn't, write your one-line
  reading and keep `--quote` verbatim. Never invent a quote.
- `--topic`: a short slug for the question being answered. Reuse an existing one
  (`list --topics`). Topics are how conflicts are found.
- Context: add each field only when the judgment is actually scoped by it. Leave `--surface`
  out if it holds for every screen.
- If the topic already has a decision, the tool refuses: the founder changed their mind, so
  `supersede ID` and keep the history.
- A departure from an expert default ("no scale-down on press"): `--kind expert --ref
  <reference path#section> --stance override` (or `accept`).

**You noticed it → record an inference, never a decision.** For example: they picked the denser
variant three times, or they keep shortening labels.

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-taste/bin/taste.py add --kind inference --source inference \
  --topic copy-length --statement "Button labels are one or two words." \
  --rationale "Founder shortened 4 labels in this build." --commit abc1234 --domain copy
```

**Never widen scope yourself.** A product decision becomes a founder preference only through
`promote ID --confirmed-by-founder "<their words>"`, after the founder says it applies
beyond this product ("do that in all my iOS apps"). Suggest it when the same judgment
shows up in a second product. Promote with the narrowest context they agreed to.

## Ask (one question, only when it matters)

Ask about an inference when it would change what you are about to build or ship. Ask once,
at the approval gate and not mid-build. Put the inference, the evidence, and a default in
one line:

> I've noticed you shorten button labels (4 edits this week). Keep labels to one or two words
> in this app? **Yes** / **No** / **Only on this screen**

Then run `confirm ID --quote "<answer>"` (narrow context with flags if they scoped it) or
`reject ID --quote "<answer>"`. If they don't answer, leave the inference tentative. Don't ask
again this session.

## Correct and inspect

- `list` (active), `show --all` (with superseded, confirmed, rejected), `show ID` (full entry +
  where it went).
- `supersede ID --statement … --rationale … --quote …`: replaces an entry and keeps the old one
  with a pointer. Nothing is deleted.
- `export-md`: a readable view for the founder. It's generated, so don't edit it.
- `check`: validates both files. A malformed store fails with the file and line. Fix it; don't
  work around it.

## Retro

Walk the open inferences (`list --kind inference`). Ask about the ones with repeated evidence,
using the one-question form, and leave the rest. Name decisions that came up in more than one
product as promotion candidates. Show `export-md` so the founder sees their taste get
sharper.

## Migration

`LEARNINGS.md › ## Design Preferences` was agent-written. `import-learnings` copies those bullets
in as inferences to confirm and leaves LEARNINGS.md untouched. New taste goes here, not to
LEARNINGS.md.
