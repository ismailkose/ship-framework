<!-- ship-reference
id: ux-interaction
kind: mixed
sources: https://www.w3.org/TR/WCAG22/ (2.5.1, 2.5.2, 2.5.7, 2.5.8, 2.4.7; 2026-09-23); https://developer.apple.com/design/human-interface-guidelines/gestures (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/playing-haptics (2026-09-23); https://m3.material.io/foundations/interaction/states (2026-09-23); books-and-sites (Dan Saffer, Microinteractions; Jakob Nielsen, response-time limits); impeccable@e0881d2 (historical idea credit only, pbakaus/impeccable, Apache-2.0)
reviewed: 2026-09-23
-->

# Interaction Design — states, feedback, touch, gestures

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** `design/components.yaml` lists each component's `variants`; its states are
designed once in the component, not per screen. Motion values (durations, curves, springs) belong
to the motion skill and `design-model.yaml` → `primitives.motion` — this file says *when*
feedback happens, not how it animates.

---

## 1. State coverage (SHIP default)

Every interactive component designs the states it can actually be in:

| State | Applies to | Must communicate |
|---|---|---|
| Default | all | that it's interactive (shape, color, affordance) |
| Hover | pointer devices only (`@media (hover: hover)`, iPad pointer) | "you can act here" — a hint, never essential info |
| Focus | all (keyboard, switch, TV remote) | where focus is — REQ 2.4.7, indicator 3:1 (1.4.11) |
| Pressed | all | the press registered, before the result |
| Disabled | controls that can be unavailable | unavailable *and why* (nearby text or tooltip) |
| Selected / checked | toggles, tabs, list selection | current value — not by color alone (REQ 1.4.1) |
| Loading | anything that triggers async work | work in progress; blocks repeat submits |
| Error | inputs, submit actions, async components | what failed and how to fix it (REQ 3.3.1/3.3.3) |
| Success | actions whose result isn't otherwise visible | it worked — quietly |
| Dragging / drop target | draggable items | what's moving and where it can land |

This table is Ship's own default, drawn from Material's state guidance and common practice.

Coverage audit — mark each cell for the component set in `design/components.yaml`:

| | Button | Input | Card (tappable) | Toggle | Link | List row |
|---|---|---|---|---|---|---|
| Default/Hover/Focus/Pressed | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Disabled | ✓ | ✓ | — | ✓ | — | ✓ |
| Selected/checked | — | — | opt. | ✓ | — | opt. |
| Loading | ✓ | opt. (async validation) | opt. | — | — | — |
| Error / Success | ✓ | ✓ | opt. | — | — | — |

```css
.button { transition: background 150ms ease, transform 160ms cubic-bezier(0.23, 1, 0.32, 1); }
@media (hover: hover) { .button:hover:not(:disabled) { background: var(--action-hover); } }
.button:focus-visible { outline: 2px solid var(--focus); outline-offset: 2px; }
.button:active:not(:disabled) { transform: scale(0.97); background: var(--action-pressed); }
.button:disabled { opacity: .38; cursor: not-allowed; }
.button[aria-busy="true"] { pointer-events: none; }          /* keep label width; show spinner */
.input[aria-invalid="true"] { border-color: var(--error); }  /* + text message, not color alone */
```

## 2. Feedback timing (when, not how)

- **Response limits (EXPERT, Nielsen):** ~0.1 s feels instant, ~1 s keeps flow, ~10 s is the
  limit of attention. So: pressed state on touch-down (SHIP: visible within 100 ms, ideally the
  next frame); a skeleton or inline progress past ~1 s; a determinate progress + estimate and a
  way to leave past ~10 s.
- **Local first:** never wait for the network to show the press. Optimistic updates for safe,
  reversible actions; roll back visibly on failure.
- **Actions fire on release** (REQ 2.5.2) so a finger can slide off to cancel.
- **No double submits:** the loading state blocks re-entry (and the server stays idempotent).

## 3. Micro-interactions (EXPERT: Saffer)

Trigger → rules → feedback → loops/modes. Design all four: what starts it, what it does, what
the user perceives, and what happens on the second, tenth and hundredth time (does it get quieter?).
Animate the result of an action, not every frame of a continuous one (typing, scrolling).
Don't animate layout the system changed on its own.

Timing (EXPERT, the motion authority: full table and SwiftUI values in
`.claude/skills/ship/motion/references/animation.md`): enter **and exit** ease-out, never
ease-in; exits never slower than entrances.

| Interaction | Duration | Easing |
|---|---|---|
| Button press / release | 100–160 ms | ease-out (scale 0.97) |
| Toggle thumb | 150 ms | ease-out, or a spring with no bounce |
| Color change | 150–200 ms | ease |
| Toast enter / exit | 200–400 ms, exit ≤ enter | ease-out (Sonner-style toasts: `ease` 400 ms) |
| Modal open / close | 200–250 ms / ≤ open | ease-out |
| Skeleton shimmer | 1500 ms loop | linear (pause under Reduce Motion) |

## 4. Touch and pointer

- **Targets:** sizes and spacing in `accessibility.md` §1–3 (REQ 24 px floor; Ship 44 pt / 48 dp).
  Measure the hit area, not the glyph; extend with padding or `contentShape`.
- **Hover is an enhancement.** Nothing essential (delete, price, close) is hover-only; design for
  `(hover: none)` first. On iPad, pointer hover effects come free with system controls.
- **Haptics (PLATFORM):** system controls already play them. Add your own only for meaningful
  moments — success/failure of a significant action, a selection change in a custom picker, a
  snap point — using semantic feedback (SwiftUI `.sensoryFeedback(.success, trigger:)`, Android
  `HapticFeedbackConstants`). Never on every tap or while scrolling. The web Vibration API isn't
  available in Safari on iOS — don't design web feedback around it.
- **Sound (EXPERT, Saffer):** only as a backup to something visible, never the only signal; off by
  default for routine actions. On iOS, play it through an audio session the silent switch mutes
  (`.ambient`).
- **Web touch hygiene:** `touch-action: manipulation` on controls (no double-tap-zoom on buttons);
  `overscroll-behavior: contain` on modals and sheets; `-webkit-tap-highlight-color: transparent`
  only when you provide your own pressed state.
- **Custom drag surfaces on the web** (sliders, carousels, swipe rows): say which axis the page
  keeps — `touch-action: pan-y` on a horizontal drag surface (`pan-x` on a vertical one) — capture
  the pointer, and handle `pointercancel` (the browser takes over when a touch turns into a
  scroll). Size for the input actually present: `@media (pointer: coarse)` / `(any-pointer: coarse)`
  catches touch on a laptop too.

## 5. Gestures

- **Prefer the platform's gestures** (swipe actions on list rows, pull to refresh, context menu
  on long press, swipe-back) over custom ones, and use system recognizers — they carry the
  platform's timing and accessibility (VoiceOver custom actions, Voice Control).
- **REQ alternatives:** every path-based or multi-finger gesture has a single-pointer
  alternative (2.5.1); every drag has a single-pointer, non-drag alternative (2.5.7) — a menu
  item, move buttons, "Move to…", tap-to-place — **and** a keyboard path (2.1.1). Keyboard alone
  fails 2.5.7: a reorderable list with drag + arrow keys but nothing to click still fails.
- **Swipe actions (convention in Apple's own apps, e.g. Mail):** leading-edge actions are
  toggles (read/unread, pin); trailing-edge actions hold destructive ones (delete) and a full
  swipe performs the first action. Destructive full-swipe needs undo.
- **Drag:** show a handle or other affordance; lift + shadow on pickup; show valid drop targets.
- **System edge gestures win:** iOS back swipe from the left edge, home/app switcher from the
  bottom, Notification/Control Center from the top; Android back from both side edges and home
  from the bottom. Don't start custom horizontal drags at a screen edge.
- **Discoverability:** gestures are shortcuts, never the only path. Teach with a visible control
  first; a one-time hint at most.
- **Keyboard parity (web, iPad keyboard):**

| Gesture | Keyboard equivalent |
|---|---|
| Tap | Enter / Space |
| Long press / context menu | Shift+F10 or Menu key; ⌃-click on Mac |
| Swipe to delete | Delete/Backspace on the focused row, plus a visible menu item |
| Drag to reorder | Focus the handle, arrow keys to move, Enter to drop |
| Pinch zoom | ⌘/Ctrl + and − (and visible zoom buttons) |

## 6. QA (Test, Eye)

- [ ] Every component in `design/components.yaml` has its applicable states designed and visible.
- [ ] Focus is visible on every control, in every mode.
- [ ] Rapid taps (5–10×) fire a submit once; slow network doesn't re-enable too early. A toggle ends in
      the state of the last tap: send only the final state (or queue the requests) and ignore stale
      responses; reload to check it stuck.
- [ ] Press feedback appears before any network result (record at 60 fps if unsure).
- [ ] Every gesture/drag has a visible single-pointer alternative (a tap/click path) and a keyboard
      path, and both work with VoiceOver/TalkBack.
- [ ] Each custom drag control, on touch: the drag completes, and a swipe along the page's scroll axis
      scrolls the page instead of moving the control. Needs a phone or tablet (or iOS Simulator) —
      a resized desktop browser doesn't test this; say which you used.
- [ ] Back-swipe, home and notification gestures work on every screen; nothing custom hijacks an edge.
- [ ] Hover-less devices can reach everything.
