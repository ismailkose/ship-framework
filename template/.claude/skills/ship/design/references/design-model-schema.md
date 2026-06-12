# design-model-schema.md — The Design Registry Schema

**Authoritative reference for Ship's machine-checkable design registry.** Load this file
before writing or reading `design-model.yaml` or `design/components.yaml`.

The registry is two files with different write cadences:

| File | Holds | Changes |
|------|-------|---------|
| `design-model.yaml` (project root) | tokens — the design decisions as data | rarely (design sessions) |
| `design/components.yaml` | the component manifest — what exists in the system | every build session |

**The layering rule (what makes the registry machine-checkable):**

```
hex / raw values  →  live ONLY in primitives
semantic tokens   →  reference primitives by dot-path
components        →  reference semantic tokens ONLY
```

Each layer validates against the one below. A hex value in a component is a refgate
violation; a component referencing `primitives.color.brand.500` directly (skipping
semantic) is too.

`DESIGN.md` remains the prose layer — rationale, voice & tone, do/don't, SAFE/RISK
decisions. The YAML holds *values*, the prose holds *why*. They never duplicate content.
`PDC.md` (schema v2) indexes both.

---

## File 1: `design-model.yaml`

```yaml
schema_version: 1

modes: [light, dark]            # default. Light-only requires explicit `modes: [light]`
                                # PLUS a documented reason in DESIGN.md. Dark mode is
                                # the default expectation, not an add-on.

brand:
  name: string                  # required (working names fine)
  feel: [calm, precise, ...]    # required, 3-5 adjectives — Eye validates previews
                                # against these words
  references: [strings]         # optional — e.g. "Cash App (roundness)",
                                # "Stripe (precision)". Name WHAT is borrowed.

primitives:                     # ── LAYER 1: raw values. Hex/numbers ONLY here. ──
  color:
    <ramp-name>:                # free-form ramp names (paper, ink, slate, gain...)
      <stop>: "#HEX"            # free-form stops; 50..900 convention recommended
    # Minimum: one neutral-ish ramp + one accent ramp.
  type:
    family: string              # one family; a second requires a documented reason
    scale:
      <name>: <px>              # required: `body` + at least one display size
  radius:
    control: <px>               # required
    card: <px>                  # required
    <name>: <px>                # free extension
  spacing:
    unit: <px>                  # everything derives from unit multiples
  motion:                       # platform-NEUTRAL physics. The one canonical source.
    springs:
      <name>:                   # named by CHARACTER (gentle, snappy), never platform
        response: <seconds>
        damping: <0..1>
    durations:
      <name>: <ms>              # for non-spring transitions
    # Emitters translate per platform — the YAML never contains platform-specific
    # motion values:
    #   SwiftUI  → Animation.spring(response:dampingFraction:)  (direct)
    #   Compose  → spring(dampingRatio:stiffness:)              (converted)
    #   CSS      → duration + cubic-bezier/linear() approximation

semantic:                       # ── LAYER 2: meaning. Values are dot-paths into
                                #    primitives (e.g. `paper.50` = primitives.color.paper.50,
                                #    shorthand allowed within color). ──
  background: <path>            # ┐
  surface:    <path>            # │
  text:       <path>            # │ REQUIRED keys
  muted:      <path>            # │
  hairline:   <path>            # │
  action:     <path>            # ┘
  <custom>:   <path>            # free extension (e.g. pnl.gain, pnl.loss)

semantic_dark:                  # REQUIRED when `dark` ∈ modes (the default).
  <key>: <path>                 # Same key set as `semantic`. Seed generates both
                                # modes; Eye validates contrast in both.
```

### Validation rules (check before every write)

1. Every `semantic` / `semantic_dark` value resolves to an existing `primitives` path.
2. No hex value appears outside `primitives`.
3. `brand.feel` has 3-5 entries.
4. All six required semantic keys present — in both modes unless `modes: [light]`.
5. `modes: [light]` requires a "Dark mode exception" note in DESIGN.md.
6. Warn (don't block) on primitives referenced by zero semantic tokens.

---

## File 2: `design/components.yaml`

```yaml
schema_version: 1
components:
  - name: PrimaryButton            # PascalCase, unique
    file: <path to source file>    # must exist — or `planned: true` if design ran
                                   # before code; first build session realizes it
    tokens: [action, radius.control]   # SEMANTIC tokens only — no hex, no primitives
    doc: >
      One-line usage note (rendered in the component-library view).
    rule: optional taste constraint    # e.g. "color on numeral only"
    added: YYYY-MM-DD
```

### Registration contract

A component enters this file **only if it is a reusable primitive** — the test:
*would a second screen plausibly want this?* Page-specific compositions never appear
here; they stay local to their screen.

- **Seed** (`/ship-design`): register what the validated scope demands — no numeric
  cap, but speculative registration (components no planned screen needs) is banned.
- **Build loop** (`/ship-build`, Slice 2): silent registry check per UI element;
  hit → reuse, miss → primitive registers on first use, one-off composes locally,
  rule-of-three promotion is the only user prompt.

---

## Worked example (abridged) — "Tempo", a calm workout tracker

```yaml
schema_version: 1
modes: [light, dark]
brand:
  name: Tempo
  feel: [calm, warm, precise]
primitives:
  color:
    paper: { 50: "#FAF9F6", 100: "#F3F1EC", 200: "#E8E5DF" }
    ink:   { 900: "#1C1A17", 600: "#5C5950", 400: "#8A867C" }
    night: { 900: "#161512", 800: "#211F1B", 300: "#B5B0A6" }
    brand: { 500: "#E0633C", 300: "#EE9A7E" }
  type:   { family: Inter, scale: { caption: 13, body: 17, title: 22, display: 28 } }
  radius: { control: 10, card: 18 }
  spacing: { unit: 4 }
  motion:
    springs:
      gentle: { response: 0.5, damping: 0.9 }
      snappy: { response: 0.3, damping: 0.8 }
semantic:
  background: paper.50
  surface:    paper.100
  text:       ink.900
  muted:      ink.400
  hairline:   paper.200
  action:     brand.500
semantic_dark:
  background: night.900
  surface:    night.800
  text:       paper.50
  muted:      night.300
  hairline:   night.800
  action:     brand.300
```

```yaml
# design/components.yaml
schema_version: 1
components:
  - name: PrimaryButton
    file: UI/PrimaryButton.swift
    tokens: [action, radius.control, type.body]
    doc: The one loud element per screen. Never more than one per view.
    added: 2026-06-11
```
