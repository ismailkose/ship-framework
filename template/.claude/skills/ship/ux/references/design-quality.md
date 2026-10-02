<!-- ship-reference
id: ux-design-quality
kind: ship-default
sources: impeccable@9d715cc (call: `npx impeccable detect`; ideas only: the parts nobody draws, the cream-palette tell, one focal move, imitation material, container in container, echo copy, web-shaped native, judging before the tools; pbakaus/impeccable, Apache-2.0); web-interface-guidelines@e3d624b (call; vercel-labs/web-interface-guidelines, MIT); gstack@636175d (idea credit: "first impression before audit" review phase; garrytan/gstack, MIT); taste-skill@ce26fc2 (ideas only: the second default look, invented proof; leonxlnx/taste-skill, MIT); Lindgaard et al., "Attention web designers: You have 50 milliseconds…", Behaviour & Information Technology, 2006; books-and-sites (Adham Dannaway, Practical UI)
reviewed: 2026-09-28
-->

# Design Quality — the reviewer's eye

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`). This file is Ship's taste
layer for Pol, Eye and Crit.
**Registry first:** judge against the project's own contract before generic taste —
`PDC.md` → `DESIGN.md` (point of view, intent, do/don't), `design-model.yaml` (tokens),
`design/components.yaml` (what exists), `DECISIONS.md`. A choice the registry made on purpose
is not slop; a value outside the registry is a finding even if it looks fine.

---

## 1. First impression (before any checklist)

- **Three seconds:** can a fresh viewer say what this is and what to do first? If they have to
  read to find the entry point, hierarchy is broken. Visual judgments form within a fraction of
  a second (Lindgaard et al. measured 50 ms exposures) — you can't argue someone into trust later.
- **Feeling vs intent:** name the feeling the screen gives, then compare it with `DESIGN.md › Point
  of view` (and `brand.feel` when the founder gave words). A mismatch with confirmed words is the
  finding ("reads corporate; they said warm"); against proposed ones it's a question for the founder.
- **Squint test:** shrink the screenshot to 25% — the primary action and the section hierarchy
  should still be obvious.
- **Density vs purpose:** dense for tools used for hours, spacious for consumer and first run.
  Suffocating and barren both fail.

## 2. Deterministic pre-pass (run before judging by eye)

- **Web:** the web scan, `python3 .claude/skills/ship/web/bin/scan.py <files|dev-server URL>`:
  deterministic anti-pattern rules; exit 0 clean, 2 findings, 1 a target couldn't be scanned (flags
  and fallbacks: web skill). Triage its findings; don't re-describe them by hand.
- **Web:** for web interface rules (focus, forms, touch, performance), apply the current web
  interface checklist at review time; the web skill owns that step.
- **Native:** capture light, dark and the largest Dynamic Type size (`xcrun simctl ui booted
  appearance dark`, `… content_size accessibility-extra-extra-extra-large`) before judging.
- **Registry:** `python3 .claude/skills/ship/design/bin/design_model.py validate` — raw values
  and unregistered components are findings before taste is.

## 3. AI slop patterns

Generated UI regresses to the median of its training data. Flag these; each fix is a direction,
the registry decides the values.

| Pattern | The tell | Fix |
|---|---|---|
| Generic hero | Centered big headline, subhead, two buttons, gradient | Show this product's own world doing its job (its photo, its thing in use); specific headline; one primary CTA |
| AI default look (warm version) | Asked for something warm or handmade, AI gives every product the same look: a cream background, brown-black text, a terracotta or brass button, a fancy serif headline | Colour and type from the product's own material (photos, signs, packaging); keep one only with a reason from that material or the founder's pick — `design_model.py sameness` flags it (`design-research.md` §2) |
| Card-grid sameness | 3 or 6 identical icon+title+text cards | If they aren't truly equal, rank them: one featured, varied sizes, or a different layout per section |
| First screen doesn't fit | The headline wraps past two lines, the main button sits below the fold on a laptop or phone, the menu wraps to a second line | Plan type size and the picture together; cut words before shrinking type; one menu line |
| Everything performs | Two or more elements compete to be the focus: a big headline, a big image and a big number at once | One focal move per screen; everything else steps back |
| Container in container | Cards inside cards, panels inside panels | Flatten: spacing, type and one divider do the grouping |
| Echo copy | An intro that repeats its heading; helper text that restates its label | Say it once; cut the echo |
| Repetition without rhythm | The same block 5+ times in a row | Break with a feature, a table, a quote or a section change |
| Imitation material | CSS-faked bevels, emboss, stamped metal, chalk or torn edges | Real material (a photo, a texture from the product's world) or a plain surface |
| Decoration over meaning | Gradients, glassmorphism, floating blobs, stacked shadows with no job; template chrome — a label above every heading, " · "-joined metadata, "→" on every button, numbered markers on content that isn't a sequence | Remove anything whose removal loses nothing; depth only where something is above something; numbers only for real steps |
| Stock or invented imagery | Isometric people, abstract 3D, blobs; stock or generated photos shown as the product; div-built fake screenshots; invented reviews, logos or numbers | The founder's real photos, screenshots and numbers; until then an authored stand-in marked `SAMPLE:` and listed in `TASKS.md`, never an invented claim (`design-research.md` §2) |
| Off-scale spacing | 14/18/22 px values; different gaps for the same relationship | Snap to the registry spacing scale |
| Flat type hierarchy | Heading steps too close; one weight | Bigger steps plus weight contrast (`typography.md` §3) |
| Uniform radius | One radius on badges, buttons, cards and sheets | Radius scale by size; concentric nesting |
| Color everywhere | The action colour on headings, borders, badges, icons | The action colour only on interactive elements; a field colour may own whole regions on a persuading surface (`color.md` §4) |
| Multiple primaries | Two filled brand buttons in one view | One primary; demote the rest |
| Fake personality | Emoji, "Let's go!", bouncy everything | Personality from consistent choices and honest, specific copy |
| Hover theater | Rotations, glows, hover effects on static text | Hover only on interactive elements, subtle and consistent |
| Orphaned states | Hover and default only; no focus, loading, error, disabled | State coverage (`interaction-design.md` §1) |
| Happy path only | No empty, loading, error or first-run screens | Design them as first-class screens (`forms-feedback.md` §4) |
| Contrast theater | Passes on a flat swatch, fails on the gradient/photo; thin small gray text | Measure against the worst background; heavier or larger text; scrim |
| Single-breakpoint layout | Great at 1440 and 390, broken at 768/1024/320 | Intrinsic layouts and container queries; test widths (`layout-responsive.md` §1) |
| Inverted dark mode | `filter: invert`, vibrating saturated accents, invisible shadows | A real dark pass (`dark-mode.md`) |
| Icon–label mismatch | Heart for "Bookmark", cloud for "Save" | Icon and label say the same thing; else label only |
| Navigation overload | 8+ top-level items, flat 20-item menus | Group, prioritise, move rare items to settings/menus |
| Full-width short inputs | Postcode or CVC stretched across the form | Width matches expected length (`forms-feedback.md` §1) |
| Misplaced actions | Buttons floating away from the content they act on; order that fights the platform | Platform order in native dialogs; Ship order on web (`copy-clarity.md` §2) |
| Web-shaped native | A custom nav bar, a dead back swipe, HTML-like buttons, custom toggles, hover-only affordances, a web icon set on iOS | System structure and controls; the brand in the open layer (`ios/references/hig-ios.md` §10) |
| Native defaults untouched (SwiftUI) | Every text `.body`, default blue accent, `cornerRadius(12)` everywhere, bare `.padding()` | Registry text roles, brand accent, radius scale, spacing tokens |
| Web defaults untouched | `system-ui` only with no hierarchy, Tailwind `blue-500`, `rounded-lg` and `p-4` everywhere | Same — registry roles, not framework defaults |

*Hover: a ~10% brightness shift (`ease`, ~150 ms) is enough for buttons. Any hover scale or lift
is motion — web only inside `@media (hover: hover) and (pointer: fine)`, values from
`.claude/skills/ship/motion/references/animation.md`.*

## 4. Consistency across screens

Pick 3–5 recurring elements (primary button, card, H2, section gap, nav) and compare them on
every screen they appear. Same component = same padding, radius, weight, color and behaviour —
identical, not similar. Variation is fine only when it's intentional (featured vs standard) and,
ideally, a registered variant in `design/components.yaml`. Also check:
- Color meaning is stable (blue = action everywhere; red only for errors/destructive).
- Interactive patterns are stable (if cards are tappable here, they're tappable everywhere).
- Navigation position, order and style never move.
- One icon style and stroke weight; a filled icon means selected (EXPERT, Practical UI).
- Items in a row (cards, tabs, buttons) carry text of similar length.

## 5. Coherence — does it feel like one product?

- **Gibberish test:** garble every word (`python3 .claude/skills/ship/design/bin/gibberish.py <screenshot>`,
  or `gibberish.js` in a web page) and ask two people who weren't told the product what it sells and
  who it's for (one guess is noisy). "Software" or "could be anything" means the look carries no identity yet, whatever the copy says.
  A right guess read from the AI default look (cream and a fancy serif for a bakery) doesn't count: the
  cues that told them should belong to this product.
- **The parts nobody draws:** web — text selection, caret, scrollbars, focus ring, link underline
  offset, tabular numerals, autofill; iOS — the tint on system controls and selection, empty and
  loading states, the app icon in light, dark and tinted. Themed from the palette, they're the cheapest
  sign a product was built rather than assembled, and the ones generated UI skips most.
- **One visual language:** corners, borders, density, color energy and type voice all say the
  same thing. Rounded-friendly controls with cold geometric type and neon accents is three products.
- **Motion coherence:** one easing family and duration scale everywhere (UI 150–250 ms ease-out,
  critically damped springs); overshoot only after a gesture with momentum or at a rare delight
  moment — never on plain taps. Values: the motion skill.
- **Copy coherence:** voice matches the visuals (a calm UI with shouty copy fails).
- **Intentionality test:** pick any element and ask why it looks like that. The answer should be
  a registry token, a recorded decision, or a platform convention — not "it was the default".

## 6. Review flow (Pol, Eye, Crit)

1. First impression (§1) — 30 seconds, written down before anything else.
2. Slop scan by eye (§3) — name the pattern and the fix, point at the file.
3. Pre-pass tools (§2) — then compare: confirm what they found and add what you missed; don't let
   their list stand in for looking.
4. Consistency (§4) and coherence (§5).
5. Accessibility REQ failures are blockers regardless of taste (`accessibility.md`).

Report findings as: **what** (pattern), **where** (screen + file), **why it matters** (user
impact or brand mismatch), **fix** (direction + the registry token or decision it should use).
