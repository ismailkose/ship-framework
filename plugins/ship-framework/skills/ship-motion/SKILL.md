---
name: ship-motion
description: |
  Animation and motion design routing: Ship's motion authority for web and
  SwiftUI. (ship) Loaded by /shipmate build, /shipmate review, /shipmate plan, /shipmate design when something
  animates, transitions, springs, or responds to a gesture.
user-invocable: false
---

# Motion

Routing plus the road signs that must be in view when a motion decision is made. The detail —
values, recipes, review tables — lives in the references; open the one the decision needs.
The motion authority's rules are these references (sources and license notices: each file's footer
and the Ship repository's `maintainers/upstreams.yaml`).

## Precedence — who wins

1. **Platform & accessibility** — SDK facts, HIG accessibility, WCAG, Reduce Motion. Always.
2. **Product decisions** — `design-model.yaml › primitives.motion` tokens (or, with no registry,
   the motion values in the project's own hand-written theme), `DECISIONS.md`,
   `design/components.yaml`, product taste entries. A token that differs from the authority's default is a
   decision: use it; don't "fix" it.
3. **Founder preferences** (taste store).
4. **Platform design guidance** — HIG, Material; on iOS the system components' own motion.
5. **The motion authority** (expert): the references below.
6. **Ship defaults** — motion budget, named primitives, the defaults in the design-model template.

## Road signs — apply without opening anything

- **Should it animate?** Keyboard-initiated or 100+/day → **no animation**. Name the purpose
  (feedback, spatial consistency, state, preventing a jarring change, explanation, delight-if-rare)
  or don't build it.
- **Easing:** enter **and exit** → ease-out `cubic-bezier(0.23, 1, 0.32, 1)`; moving on screen →
  ease-in-out `cubic-bezier(0.77, 0, 0.175, 1)`; hover/color → ease; progress → linear.
  **Never ease-in on UI.**
- **Duration:** press 100–160ms · tooltip 125–200 · dropdown 150–250 · modal/drawer 200–500 ·
  UI under 300ms · exits never slower than entrances.
- **Springs:** default critically damped — `.spring(duration: 0.35, bounce: 0)` ≡
  `.spring(response: 0.35, dampingFraction: 1.0)`. Bounce ≈0.2 (damping 0.8) **only after a
  flick / drag release** or at the rare delight tier. SwiftUI's `.snappy` (0.15) and `.bouncy`
  (0.3) presets overshoot — not for taps. (A project token that happens to be named "snappy" is
  whatever the project set.)
- **Never from `scale(0)`** — 0.95 + opacity. Popovers grow from their trigger; modals stay
  centered.
- **Interruptible:** transitions / state-driven animation, not restarting keyframes; springs for
  anything the finger drives; never lock input during a transition.
- **Reduced motion = gentler, not zero** — movement becomes a short crossfade; opacity and color
  stay. Ships with the animation.
- **iOS:** system sheets, navigation, menus, alerts already move correctly — don't re-animate them.
- **Web:** `transform`/`opacity` only; no `transition: all`; hover motion inside
  `@media (hover: hover) and (pointer: fine)`.

## Which reference for which decision

| Decision | Open |
| --- | --- |
| Gate, purpose, tool, properties, easing, duration, springs (both SwiftUI forms), interruption, stagger, cohesion, Ship contracts, never-ship list | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/animation.md` |
| Building a component on the web — press, dropdown, tooltip, modal, drawer, toast, accordion, stagger, hold-to-confirm, tabs, scroll reveal, blur mask, WAAPI, view transitions | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/recipes-web.md` |
| The same in SwiftUI (type-checked), and which system component to use instead | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/recipes-swiftui.md` |
| Drag, swipe, flick, sheets with snap points, velocity handoff, projection, rubber-banding, interruption | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/fluid-interfaces.md` |
| Reduced motion / transparency / contrast, WCAG, testing per OS | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/reduced-motion.md` |
| Frame drops, `will-change`, Motion shorthands, SwiftUI per-frame state, debugging feel | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/performance.md` |
| Materials & glass, haptics + sound with motion, Apple type details, Apple's eight principles | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/apple-design.md` |
| Reviewing motion in a diff (Pol, Crit, Eye) — detection table, severities, report format | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/review-standards.md` |
| "Improve / audit the animations" across a codebase → findings + self-contained plans | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/audit-and-plans.md` |
| "What could animate here?" — opportunities, with the rejections | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/opportunities.md` |
| "What's it called when…" — naming an effect; SwiftUI names | `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/references/vocabulary.md` |

## Named primitives (when a design contract exists)

If `PDC.md` / `design-model.yaml` defines motion tokens:
- Use the token (`Theme.Motion.<name>` in Swift, the CSS variable on the web) and tag the call
  site `// motion: <name>` (CSS: `/* motion: <name> */`). Untagged raw values are flagged.
- A new motion needs a motion token (`/shipmate design --tokens`), not an inline value; tune existing
  ones by eye with `/shipmate design --motion-tune`.
- Run `python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py validate` — its motion warnings
  (ease-in, overshoot on press tokens, long UI durations) are prompts to confirm, not to rewrite.

Without a contract, use the values above and in `animation.md` (the design gate only stops
*new* UI files before a contract exists; fixing existing motion is never blocked).

## /shipmate build

1. Gate + purpose (`animation.md` §1–2). Rejected → say so and ship the non-motion version.
2. Tool: system component first on iOS; cheapest CSS tool on the web (`animation.md` §3).
3. Start from the recipe (`recipes-web.md` / `recipes-swiftui.md`); gestures from
   `fluid-interfaces.md`.
4. Reduced motion and hover gating in the same change (`reduced-motion.md`).
5. Report in three lines: gate result, ingredients, what to feel-check (slow motion, real device).

## /shipmate review

Pol owns motion taste and values, Crit flags motion that breaks the task (input locked,
animation on a high-frequency action, missing Reduce Motion), Eye checks rendered motion in slow
motion. All three use `review-standards.md` (detection table → JSON findings; `motion`
dimension). A value that matches a project token isn't a finding.

## Test (/shipmate review --test)

- Reduce Motion on (OS or DevTools emulation): movement gone, fades and state feedback present.
- Tap / click rapidly mid-animation: it retargets, never restarts or locks up.
- Interrupt a drag or sheet mid-flight: it follows the finger.
- Frame rate: no hitches in gestures (Instruments Animation Hitches / DevTools Performance).
Steps and OS paths: `reduced-motion.md` › Testing and `performance.md` › Measuring.

## Not ported (undecided upstream skills)

`write-swift`, `prototype`, `mobile-native`, `animate-expo`, `pick-ui-library`, `ask-sonner` are
awaiting a founder decision — don't cite them as Ship guidance.
