<!-- ship-reference
id: taste-schema
kind: ship-default
sources: Ship (original)
reviewed: 2026-09-23
-->
# Taste store schema

Two files, same shape. `taste.py` is the only writer Ship uses; hand edits are fine if they keep
this shape (comments other than the file header are not preserved on the next write).

| Scope | File | Holds | Why there |
|---|---|---|---|
| product | `design/taste.yaml` (project) | `decision`, `inference`, `expert` | Beside `design/components.yaml`: user-owned, never shipped in `template/`, so `ship-update.sh` never writes it; `.ship/` is Ship-managed and refreshed. Plain file, so Claude and Codex read the same thing; committed with the product. |
| founder | `$SHIP_HOME/taste.yaml` (default `~/.ship/taste.yaml`) | `preference`, `expert` | Follows the founder across products. Only written with `confirmed_by_founder`. |

## File

```yaml
schema: 1
scope: product              # or founder — must match the file
product:                    # product scope only; optional
  name: CoachEva
  platform: [ios]           # query fills platform/product_type from here when not given
  product_type: [fitness]
entries:
  - id: t-2026-09-23-001    # product t-DATE-NNN · founder tf-DATE-NNN · never reused
    kind: decision          # decision | inference | expert (product) · preference | expert (founder)
    status: active          # active | superseded | confirmed (inference → decision) | rejected
    source: correction      # approval | rejection | correction | example | inference
    topic: card-elevation   # slug; same topic = same question → conflicts are detected per topic
    statement: "Cards never have shadows; separate with hairlines."
    rationale: "Shadows read as generic next to the calm palette."
    context:                # omitted field = applies to any value
      platform: [ios]
      surface: [home]       # screen / flow
      component: [card]     # component or role
      domain: [layout]      # layout | color | type | motion | copy | iconography | interaction | ...
      product_type: [fitness]
    evidence:               # at least one item; first item is the one shown in queries
      - date: "2026-09-23"
        quote: "no shadows on cards, ever"    # founder's words, verbatim
        file: App/Views/StatCard.swift
        commit: abc1234
        screenshot: design/shots/home-v3.png
        url: https://example.com/a-reference   # a reference the founder showed
    recorded: "2026-09-23"
    # optional
    expert: {ref, stance}   # kind expert: reference path#section + accept | override (block form)
    confirmed_by_founder: {quote, date}   # required on every active founder entry
    overrides: tf-…         # a product decision that deliberately departs from a founder preference
    supersedes / superseded_by / derived_from   # history links (ids in the same file)
    promoted_to: founder:tf-…   /   promoted_from: "<product>:t-…"
    imported_from: LEARNINGS.md#<hash>   # import-learnings idempotency
    status_note: "founder rejected 2026-09-24: \"…\""
```

YAML subset: block mappings and lists, `[a, b]` scalar lists, `{}`, quoted or plain scalars,
`#` comments. No anchors, block scalars (`|`, `>`), or multi-document files — these are errors
with a line number, as is any schema violation. A missing file is an empty store; an empty or
malformed one is an error (exit 2), never an empty result.

## Kinds

| Kind | Who it comes from | Scope | Applies |
|---|---|---|---|
| decision | Founder approved, rejected, corrected, or showed an example — for this product | product | Yes (rank 1) |
| preference | Founder said it holds across products (`promote`, or `add --confirmed-by-founder`) | founder | Where context matches (rank 2) |
| expert | Founder accepted or overrode a specific expert default; points at the reference | either | At its scope's rank |
| inference | An agent's own reading of signals | product | Never — surfaced for confirmation (rank 4) |

Expert defaults themselves are not stored: they live in the skill references (rank 3 — "see
reference").

## Precedence and conflicts

`query` returns active, context-matched entries in this order: product decision → founder
preference → (expert references, not stored) → inference. Platform requirements and
accessibility sit above all of it (MODERNIZATION-MAP precedence 1).

- Per topic, the highest rank applies; lower-ranked entries are shown as *not applied* with the
  reason, and listed under CONFLICTS when they say something different.
- Two active entries at the same rank on the same topic that disagree → `UNRESOLVED`
  (`query --strict` exits 3). Resolve by asking the founder and superseding one.
- A founder preference promoted from this product's decision is shown as the *same judgment*,
  not a conflict.
- `overrides: tf-…` on a product decision marks a deliberate local departure.

## Context matching

A query field filters only if both the query and the entry name it: an entry with no `surface`
matches every surface; a query without `--domain` returns all domains. Values are lowercased,
spaces become `-`, and `colour→color`, `animation→motion`, `typography→type` are folded. `*`,
`any`, `all` in an entry mean any.

## Lifecycle (nothing is deleted)

| Event | Command | Effect |
|---|---|---|
| Founder corrects/approves/rejects/shows | `add --kind decision --source … --quote` | new active decision |
| Agent notices a pattern | `add --kind inference --source inference` | tentative; never applied |
| Founder confirms an inference | `confirm ID --quote` | new decision `derived_from` it; inference → `confirmed` |
| Founder says no | `reject ID --quote` | inference → `rejected` (kept so it isn't re-proposed) |
| Founder changes their mind | `supersede ID --rationale --quote` | new entry; old → `superseded` + pointer |
| Founder says "everywhere" | `promote ID --confirmed-by-founder` | founder copy; product entry gets `promoted_to` |

Superseding a founder entry also needs `--confirmed-by-founder`: it changes every product.
