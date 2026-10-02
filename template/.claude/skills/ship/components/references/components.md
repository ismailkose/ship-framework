<!-- ship-reference
id: components-architecture
kind: ship-default
sources: .claude/skills/ship/design/references/design-model-schema.md (Ship contract: design/components.yaml); https://www.w3.org/WAI/ARIA/apg/ (2026-09-23); https://developer.apple.com/documentation/swiftui/buttonstyle (2026-09-23); https://m3.material.io/components (2026-09-23); books-and-sites (Adham Dannaway, Practical UI — component property axes, button weights); vercel-agent-skills@063bee9 composition-patterns (one idea, in Ship's words: a look is a variant, a behaviour is its own component; 2026-09-29)
reviewed: 2026-09-23
-->

# Component Architecture

Labels: REQ / PLATFORM / EXPERT / SHIP (see `.claude/skills/ship/ux/references/accessibility.md`).
Web stacks on shadcn/ui: also read `shadcn.md` (same folder).

## 0. The registry decides first

`design/components.yaml` is the list of what exists. Before building any UI element:

1. **Registered?** Reuse it (its `file`, `variants`, `rule`). Don't fork a lookalike.
2. **Reusable primitive** (a second screen would plausibly want it)? Build it on Layer 1/2 below
   and register it on first use: `name`, `file`, semantic `tokens`, `variants`, `doc`, `added`.
3. **One-off composition?** Compose it locally from registered parts; don't register it.
4. **Third local copy of the same composition?** Propose promotion (rule of three) — the only
   component question the build loop asks the founder.

Components reference **semantic tokens only** (`action`, `surface`, `radius.control`) — never hex
or primitives (`design_model.py validate` enforces it). Registry decisions beat everything in this
file except accessibility requirements.

---

## 1. The three layers

| Layer | What it is | Web (React) | iOS (SwiftUI) | Android (Compose) |
|---|---|---|---|---|
| **1 Primitives** | Behaviour + accessibility, no look: focus, keyboard, ARIA/traits, dismissal, positioning | Base UI, Radix, React Aria (headless) | Built-in controls and modifiers (`Button`, `Toggle`, `Menu`, `.sheet`, `.contextMenu`) | Material 3 components / foundation |
| **2 Styled** | Primitives + the registry's tokens and variants | shadcn/ui on one of those bases (`shadcn.md`), or your own | `ButtonStyle`, `LabelStyle`, `ToggleStyle`, view modifiers fed by the emitted `Theme.swift` | M3 components under your `MaterialTheme` |
| **3 Product** | Styled components + data + business logic | `CheckInCard`, `PricingTable` | same | same |

**The layering rule:** the registry's styled components (2) win where they exist; primitives (1)
fill the gaps, styled to match the tokens; build from scratch only when neither covers the
behaviour.

**What primitives handle, so you don't:** focus trapping and restore, arrow-key navigation,
roles/states/properties, live announcements, outside-click and Esc dismissal, collision-aware
positioning, scroll locking (including iOS Safari quirks), RTL. If you're writing any of these by
hand, stop — pick the primitive (REQ 4.1.2 is easy to fail by hand).

**Build custom only when** the interaction doesn't exist in any primitive set, or the primitive's
*behaviour* (not its look) conflicts with the need. "I don't like its API" isn't a reason.

**Anti-patterns**
- Fighting a primitive (`!important` on internals, patched event handlers) → wrong primitive or wrong layer.
- Two primitive libraries in one app → inconsistent keyboard/focus behaviour, double bundle.
- Skipping Layer 2 (styling primitives inside product components) → every feature re-styles; extract a styled component and register it.
- Re-implementing platform controls on native (custom toggles, fake navigation bars) → loses
  Dynamic Type, VoiceOver traits and future OS styling for free.

## 2. Variation axes (SHIP)

When a component varies, it varies along these independent axes — not through one-off props
(`isSpecial`, `variant="blue-large"`):

| Axis | Controls | Example values |
|---|---|---|
| **Type** | structure | card horizontal/vertical; alert inline/banner |
| **Tone** | semantic intent | brand, neutral, destructive, inverse, success, warning, info |
| **State** | interaction state | default, hover, focus, pressed, disabled (+ loading, selected, error) — `.claude/skills/ship/ux/references/interaction-design.md` §1 |
| **Size** | density | small, medium, large — tied to spacing/type tokens |
| **Content** | optional slots | icon, subtitle, avatar, badge, trailing action |

Register the axes a component actually exposes as `variants` in `design/components.yaml`.
A different look is a variant on one of these axes; a different behaviour (a button that asks to
confirm first, a list that reorders) is its own component that reuses the look (SHIP).

## 3. Composition checks

**Block shipping** — these break a contract or cause defects:

| Signal | Action |
|---|---|
| Hand-written focus trap, roving tabindex, ARIA wiring | Use the Layer 1 primitive |
| Literal color/size/spacing/shadow in a component | Semantic token from the registry |
| Two components for the same pattern | Consolidate into one registered component with variants |

**Signals, not blockers** — raise them when they're causing a problem (conflicting states, a
variant that's hard to add, repeated bugs), not because a count was reached:

| Signal | Usual fix |
|---|---|
| Several boolean props that combine into looks | A variant axis or a compound component (`Tabs`/`Tabs.List`/`Tabs.Panel`) |
| The same prop threaded through many levels | Context/environment (`@Environment`, React context, `CompositionLocal`) |

React composition details: `.claude/skills/ship/web/references/react-patterns.md`.

## 4. Buttons — weight, tone, friction

**Three weights (EXPERT: Practical UI; SHIP default):**
- **Primary** — filled with the action color. **One per view**: the single most likely next step;
  none when no action leads.
- **Secondary** — outlined or tonal. Alternatives of equal or lesser importance; several allowed.
  Equal choices get equal weight.
- **Tertiary** — text only. Least important actions, Cancel on web forms, low-emphasis destructive actions.
- **The decline beside a primary** (a paywall, a consent or upgrade prompt) may be quieter but
  keeps text contrast and a full-size target; a tiny or faint "No thanks" is a trick
  (`.claude/skills/ship/ux/references/psychology.md` §7).

Platform mapping: SwiftUI `.borderedProminent` / `.bordered` / `.borderless` (or registry
`ButtonStyle`s); Material 3 filled / outlined or tonal / text; shadcn `default` / `outline` or
`secondary` / `ghost` or `link`.

**Tone is independent of weight.** A destructive action can be primary (filled red in a
delete-confirmation) or tertiary (a quiet "Delete" at the bottom of a settings page). Destructive
tone means the friction rules in `.claude/skills/ship/ux/references/copy-clarity.md` §2 apply;
on iOS use `role: .destructive` so the system styles and orders it.

**Order and alignment** follow the platform in native dialogs and Ship's web default elsewhere
(`copy-clarity.md` §2).

## 5. Review checklist (Pol, Eye, Crit, Test)

- [ ] Every reusable UI element is in `design/components.yaml`, with a real `file` (or `planned: true` only before first build).
- [ ] No component uses literal colors, sizes or spacing; tokens are semantic.
- [ ] No hand-rolled focus/keyboard/ARIA where a primitive exists; one primitive library.
- [ ] Variants follow the axes in §2; no boolean pile-ups (§3).
- [ ] Exactly one primary button per view; destructive tone carries the right friction.
- [ ] State coverage complete for each registered component (focus visible in both modes).
- [ ] Keyboard and screen-reader pass on each interactive component: name, role, state, order.
- [ ] Same component looks and behaves the same on every screen.
