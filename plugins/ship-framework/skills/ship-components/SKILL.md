---
name: ship-components
description: |
  Component architecture routing — three-layer model, composition, tokens. (ship)
  Use when deciding how to structure or reuse a component; knowledge routing names the reference to open.
user-invocable: false
---

# Components — routing and road signs

## 1. Registry first

`design/components.yaml` is the source of truth for what exists; `design-model.yaml` for the
tokens components may use. Before building any UI element:

1. **Registered?** → reuse it (file, variants, rule). Never fork a lookalike.
2. **Reusable primitive?** (a second screen would plausibly want it) → build on Layer 1/2, then
   register it on first use (`name`, `file`, semantic `tokens`, `variants`, `doc`, `added`).
3. **One-off?** → compose locally from registered parts; don't register.
4. **Third local copy?** → propose promotion (rule of three) — the only component question for the founder.

Components use **semantic tokens only** — no hex, no primitives
(`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py validate`). Registry decisions beat
generic guidance; accessibility requirements beat the registry.
Precedence and labels (REQ / PLATFORM / EXPERT / SHIP): `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/SKILL.md` §2.

## 2. Which reference for which decision

| Deciding… | Open |
|---|---|
| Layers, what primitives handle, when to build custom, variation axes, composition gates, button weights/tones | `${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/components.md` |
| Web on shadcn/ui: which base (Base UI / Radix / React Aria), token mapping, where edits go, upgrades, review | `${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/shadcn.md` |
| shadcn component APIs, install commands, examples | shadcn's own CLI, called by Ship: `npx shadcn@latest docs <component>`, `view`, `add --dry-run` (`shadcn.md`) |
| React composition (compound components, context), React 19 APIs | `${CLAUDE_PLUGIN_ROOT}/skills/ship-web/references/react-patterns.md` |
| Component states, gestures, feedback | `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/interaction-design.md` |
| Registry schema (`components.yaml` fields, registration contract) | `${CLAUDE_PLUGIN_ROOT}/skills/ship-design/references/design-model-schema.md` |

## 3. The three layers (always enforce)

| Layer | Role | Web | iOS | Android |
|---|---|---|---|---|
| 1 Primitives | Behaviour + accessibility, no look | Base UI, Radix, React Aria | Built-in SwiftUI controls/modifiers | Material 3 Compose |
| 2 Styled | Primitives + registry tokens + variants | shadcn/ui or your own | `ButtonStyle`/`LabelStyle`/modifiers on the emitted theme | M3 under your theme |
| 3 Product | Styled + data + logic | features | features | features |

Check 1 → 2 → 3 in order; never rebuild what a lower layer handles. One primitive library per app.

## 4. Composition gates — block shipping

Boolean pile-ups and deep prop threading are **signals, not gates** — raise them when they cause a
real problem (conflicting states, a hard-to-add variant), not at a count (components.md §3).

| Gate | Signal | Action |
|---|---|---|
| Layer violation | Hand-rolled focus trap, keyboard nav, ARIA/traits | Layer 1 primitive |
| Token violation | Literal color, size, spacing, font, shadow in a component | Semantic token from the registry |
| Registry drift | Reusable component not in `design/components.yaml`, or a lookalike of a registered one | Register / consolidate |
| Button hierarchy | Two filled primaries in one view | Demote one (components.md §4) |

## 5. By phase

**Plan (Arc):** list registered components the feature needs; name new reusable primitives to
register; plan compound structure for complex widgets (tabs, menus, pickers); missing tokens go
into `design-model.yaml` before build.

**Build (Dev):** registry check (§1) → layer check (§3) → tokens only → register new primitives
in the same change. Web shadcn projects: `shadcn.md` §3.

**Review (Pol, Eye, Crit, Test):** `components.md` §5 checklist (+ `shadcn.md` §4 on shadcn
projects): registry coverage, token use, one primitive library, state coverage, keyboard and
screen-reader pass, same component = same everywhere.

## See also

- UX skill — accessibility requirements, states, forms, copy
- Web skill — React 19 patterns, web accessibility implementation
- Motion skill — motion tokens and component transitions
