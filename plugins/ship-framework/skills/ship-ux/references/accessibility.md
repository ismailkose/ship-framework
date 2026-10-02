<!-- ship-reference
id: ux-accessibility
kind: platform
sources: https://www.w3.org/TR/WCAG22/ (W3C Recommendation, 12 Dec 2024; checked 2026-09-23); https://www.w3.org/WAI/WCAG22/Understanding/ (2026-09-23); https://www.w3.org/WAI/ARIA/apg/ (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/accessibility (2026-09-23); https://m3.material.io/foundations/designing/structure (2026-09-23)
reviewed: 2026-09-23
-->

# Accessibility — what's required, what's recommended

Labels used in every Ship UX reference:
**REQ** = requirement (WCAG 2.2 AA or a platform/App Review rule) — blocks shipping ·
**PLATFORM** = HIG / Material guidance · **EXPERT** = named expert source ·
**SHIP** = Ship default (a registry or product decision overrides it).

Precedence: accessibility requirements > the project registry (`design-model.yaml`,
`design/components.yaml`, `DECISIONS.md`) > founder taste > HIG/Material > experts > Ship defaults.
A registry value that fails a REQ row is a bug in the registry — flag it, don't ship it.

Ship's target is **WCAG 2.2 Level AA** on every stack. Native apps apply the same criteria
(W3C's WCAG2ICT note maps them to non-web software). Laws and procurement rules often cite
WCAG 2.1 AA (e.g. EN 301 549 behind the EU Accessibility Act); 2.2 AA is a superset except
for 4.1.1 Parsing, which 2.2 made obsolete.

Implementation details live with the stack: web → `${CLAUDE_PLUGIN_ROOT}/skills/ship-web/references/web-accessibility.md`
(and the ARIA Authoring Practices Guide for widget patterns); iOS → the ios skill;
motion → `${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/` (Reduce Motion is a REQ there).

---

## 1. Requirement map (WCAG 2.2 A + AA)

What each criterion means for the screens Ship builds. Level in brackets.

### Perceivable

| SC | Practical rule |
|---|---|
| 1.1.1 Non-text content [A] | Every meaningful image/icon has a text alternative; decorative ones are hidden from AT. Icon-only buttons need an accessible name. |
| 1.3.1 Info & relationships [A] | Structure is in the markup/semantics, not just the visuals: headings, lists, labels tied to inputs, table headers, grouped radios. |
| 1.3.4 Orientation [AA] | Don't lock to portrait/landscape unless essential. |
| 1.3.5 Identify input purpose [AA] | Personal-data fields declare their purpose (`autocomplete` on web, `textContentType` on iOS). |
| 1.4.1 Use of color [A] | Color never carries meaning alone — add text, icon, shape or position. |
| 1.4.3 Contrast (minimum) [AA] | Text ≥ **4.5:1**; large text ≥ **3:1**. Large = ≥ 18pt (24 CSS px) regular or ≥ 14pt (≈18.7 CSS px) bold. Disabled controls and logos are exempt. |
| 1.4.4 Resize text [AA] | Text scales to 200% without loss of content or function. |
| 1.4.10 Reflow [AA] | Content works at 320 CSS px wide (400% zoom) without two-direction scrolling (data tables, maps, toolbars excepted). |
| 1.4.11 Non-text contrast [AA] | **3:1** for the parts needed to identify a control and its state (input borders, toggle track vs thumb, checkbox box, focus indicator) and for meaningful graphics (chart lines, status icons). |
| 1.4.12 Text spacing [AA] | Nothing breaks when users set line-height 1.5, paragraph spacing 2×, letter spacing 0.12em, word spacing 0.16em. No fixed-height text boxes. |
| 1.4.13 Content on hover/focus [AA] | Tooltips/popovers are dismissible (Esc), hoverable, and persistent until dismissed. |

### Operable

| SC | Practical rule |
|---|---|
| 2.1.1 Keyboard [A] · 2.1.2 No trap [A] | Everything works from a keyboard (web, iPad/Mac with keyboard, Full Keyboard Access); focus can always leave a component. |
| 2.2.1 Timing adjustable [A] | No time limit the user can't turn off/extend. A toast that carries an action (Undo, Retry) must not vanish before the user can reach it — keep it until dismissed, or put the action somewhere persistent too. |
| 2.2.2 Pause, stop, hide [A] | Anything that auto-moves, blinks or scrolls for > 5 s, or auto-updates, can be paused. |
| 2.3.1 Three flashes [A] | Nothing flashes more than 3 times per second. |
| 2.4.3 Focus order [A] | Focus follows the reading/visual order. Modals move focus in and return it on close. |
| 2.4.4 Link purpose (in context) [A] | A link's text, with its sentence or list item, says where it goes; a bare "Learn more" or "Click here" fails when nothing around it does. |
| 2.4.6 Headings and labels [AA] | Headings and labels describe their topic or purpose and make sense read alone. |
| 2.4.7 Focus visible [AA] | A keyboard focus indicator is always visible. Never remove outlines without a replacement. |
| 2.4.11 Focus not obscured (min) [AA] | The focused element isn't fully hidden by sticky headers/footers, cookie banners, bottom sheets or chat bubbles (use `scroll-padding` / inset-aware scrolling). |
| 2.5.1 Pointer gestures [A] | Path-based or multi-finger gestures (swipe, pinch, two-finger) have a single-pointer alternative (a button, a menu item). |
| 2.5.2 Pointer cancellation [A] | Actions fire on up/release, not on down, so a user can slide off to cancel. |
| 2.5.3 Label in name [A] | The accessible name contains the visible label text (voice control users say what they see). |
| 2.5.7 Dragging movements [AA] | Every drag (reorder, slider, map pan, swipe-to-dismiss sheet, kanban move) can be done with a **single pointer without dragging**: buttons, a menu "Move to…", tap-to-place, tapping the track. Arrow keys are the separate keyboard requirement (2.1.1) — they don't satisfy 2.5.7 on their own (a touch user may have no keyboard). |
| 2.5.8 Target size (min) [AA] | Pointer targets ≥ **24×24 CSS px**, or undersized targets spaced so a 24 px circle centered on each doesn't overlap another target. Exceptions: an equivalent control elsewhere meets it, inline links in text, user-agent-controlled, or size is essential. |

### Understandable

| SC | Practical rule |
|---|---|
| 3.2.6 Consistent help [A] | If help/contact exists on several screens, it's in the same relative place each time. |
| 3.3.1 Error identification [A] · 3.3.3 Error suggestion [AA] | Errors are described in text next to the field and say how to fix them. |
| 3.3.2 Labels or instructions [A] | Every input has a visible label (placeholder isn't a label). |
| 3.3.7 Redundant entry [A] | Don't make people re-type what they gave earlier in the same flow — prefill or offer "same as shipping". |
| 3.3.8 Accessible authentication (min) [AA] | No cognitive test to log in (memorising, transcribing, puzzles) unless an alternative exists. Allow paste and password managers, support passkeys / Sign in with Apple / magic links; never block paste in password or OTP fields; OTP fields accept autofill (`autocomplete="one-time-code"`, iOS `.oneTimeCode`). |

### Robust

| SC | Practical rule |
|---|---|
| 4.1.2 Name, role, value [A] | Custom controls expose name, role, state (and state changes) — use platform controls or headless primitives rather than hand-rolled ARIA. |
| 4.1.3 Status messages [AA] | Toasts, "Saved", result counts and inline async errors are announced without moving focus (`role="status"`/`aria-live` on web, `AccessibilityNotification.Announcement` on iOS). |

**Worth knowing, not required (AAA):** 1.4.6 enhanced contrast 7:1 · 2.4.13 focus appearance
(indicator ≥ a 2 CSS px perimeter, 3:1 between focused and unfocused states) · 2.5.5 target
size 44×44 CSS px · 3.3.9 no cognitive test even with help · 1.4.8 visual presentation (reading
text not justified, about 80 characters a line at most). Ship uses some of these as defaults (§3).

---

## 2. Platform guidance (PLATFORM — not WCAG, but reviewers and users expect it)

| Topic | Apple HIG | Material 3 / Android |
|---|---|---|
| Hit targets | iOS/iPadOS default 44×44 pt (min 28×28); visionOS 60×60 pt; macOS 28×28 pt | 48×48 dp touch target, ≥ 8 dp between targets |
| Text size | Support ≥ 200% enlargement (watchOS 140%); adopt Dynamic Type incl. accessibility sizes | Honour font scale (nonlinear up to 200% since Android 14); size text in `sp` |
| Contrast | 4.5:1 up to 17 pt, 3:1 at 18 pt+ or bold; for custom colors strive for 7:1 in small text; provide Increase Contrast variants | Tonal palettes are built to meet 4.5:1 / 3:1 when roles are used as intended |
| Settings to honour | Reduce Motion, Reduce Transparency, Increase Contrast, Bold Text, Differentiate Without Color, Smart Invert, Button Shapes | Remove animations, High-contrast text, Color correction, Bold text |
| Screen reader | VoiceOver: labels, traits, grouped elements, custom actions for swipe actions, rotor headings | TalkBack: `contentDescription`, merged semantics, custom actions |

- **App Store accessibility labels (iOS):** App Store Connect lets you declare which accessibility
  features the app supports (VoiceOver, Voice Control, Larger Text, Sufficient Contrast, Dark
  Interface, Differentiate Without Color, Reduced Motion, captions, audio descriptions). Only claim
  what the /shipmate review evidence shows — check the current App Store Connect form before launch.
- HIG's contrast table treats bold text of any size as 3:1; WCAG only relaxes bold at ≥ 14 pt.
  Where they differ, **WCAG wins** (precedence 1 over 4).

---

## 3. Ship defaults (SHIP — stricter than AA where it's cheap)

| Default | Why | Override |
|---|---|---|
| Touch targets **44×44** (pt on iOS, CSS px on touch web), **48×48 dp** on Android; 24 px is the floor for dense desktop UIs only | Platform sizes beat the AA floor on touch; the AA floor still applies everywhere | Registry `components.yaml` may shrink visuals — never the hit area |
| Focus ring: 2 px solid, 2 px offset, ≥ 3:1 against both the control and the background; `:focus-visible` on web | Meets 2.4.7 + 1.4.11 and approximates 2.4.13 | The `focus` role in `design-model.yaml` › semantic (recommended in the template) |
| Body text contrast aim **7:1**, never below 4.5:1; secondary text ≥ 4.5:1 | Matches HIG's advice for custom colors; small/thin text reads worse than its ratio says | Brand muted tones must still pass 4.5:1 |
| Every drag and swipe ships with a visible alternative (menu item, button, arrow keys) | 2.5.1 + 2.5.7, and discoverability | — |
| Toasts: text-only confirmations may auto-dismiss (≥ 4 s, pause on hover/focus); toasts with actions persist until dismissed | 2.2.1 + 4.1.3 | — |
| Never `disabled` a submit button to signal "form incomplete" — validate on submit | Disabled buttons drop out of focus order and explain nothing | Type-to-confirm destructive actions may disable (see forms-feedback.md) |
| Screens tested at the largest accessibility text size and at 320 px / 200% zoom | 1.4.4 / 1.4.10 fail silently otherwise | — |

---

## 4. Contrast — how to judge it

- **The requirement is the WCAG 2 ratio** (relative luminance). Compute it; don't eyeball it, and
  don't infer it from OKLCH/HSL lightness. Ship's validator (`design_model.py validate`) and
  `npx @google/design.md lint` check registry pairs; check the rendered UI too.
- Check **every mode**: light, dark, Increase Contrast, and every state (hover, pressed,
  selected, error). A pair that passes in light often fails in dark.
- Text on images/gradients/glass: measure against the worst region, or add a scrim/solid layer.
  With translucent materials (e.g. Liquid Glass), prefer system text styles and vibrancy.
- Placeholder text that conveys information needs 4.5:1; decorative placeholder can be lighter,
  which is one more reason not to use placeholders as labels.
- **APCA is not a requirement.** It isn't part of any W3C Recommendation (WCAG 3 is a Working
  Draft). Use it at most as a second opinion on readability — never to justify failing a WCAG 2 ratio.

---

## 5. Build-time road signs

- Use the platform control or the stack's headless primitive before any custom widget
  (components skill, Layer 1). Custom widgets follow the ARIA APG pattern for their role.
- Every input: visible label, `autocomplete`/`textContentType`, hint and error text linked to the
  field (`aria-describedby`, the hint's id too), `aria-invalid` on error, and the required state
  exposed (`required` / `aria-required`; on iOS, say it in the label).
- Icon-only buttons: accessible name that starts with the visible meaning ("Close", not "X icon").
- Group related elements for VoiceOver/TalkBack so a card reads as one element with custom actions.
- Headings in order; one `h1`/large title per screen; landmarks on web.
- Announce async results (4.1.3); move focus only when the user's context changes (dialog, new page).
- Sticky/fixed UI: reserve space (`scroll-padding`, safe-area insets) so focus isn't obscured (2.4.11).
- Respect Reduce Motion / `prefers-reduced-motion` — values and fallbacks live in the motion skill.

---

## 6. Verification (Test, Eye, /shipmate review evidence)

- **Keyboard walk** (web, iPad keyboard): Tab through the whole flow — order, visible focus, no traps, Esc closes overlays, focus returns.
- **Screen reader pass** on the primary flow: VoiceOver (iOS/macOS), TalkBack (Android), VoiceOver or NVDA (web). Every control announces name + role + state.
- **Text size:** iOS largest accessibility size (`xcrun simctl ui booted content_size accessibility-extra-extra-extra-large`); Android font scale 200%; web 200% zoom and 320 px width.
- **Contrast** in every mode and state (see §4). `xcrun simctl ui booted appearance dark` for native dark captures.
- **Targets:** measure hit areas, not glyphs (Accessibility Inspector, Layout Inspector, DevTools).
- **Alternatives:** every drag/swipe/multi-finger action has a visible alternative (2.5.1, 2.5.7).
- **Automated scans** catch only part of the issues: Xcode Accessibility Inspector audit, axe/Lighthouse on web (web skill owns tool setup). Automated green ≠ accessible.

Record results in the review evidence; a failed REQ row is a blocker, a failed SHIP row is a finding.
