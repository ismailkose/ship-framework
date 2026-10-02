<!-- ship-reference
id: ux-principles
kind: mixed
sources: books-and-sites (Jon Yablonski, Laws of UX — lawsofux.com, 2026-09-23); https://developer.apple.com/design/human-interface-guidelines (2026-09-23); Adham Dannaway, Practical UI (2nd ed.); userinterface-wiki@256a954 (ideas only; raphaelsalaja/userinterface-wiki, MIT); impeccable@9d715cc (idea only: first success from a filled-in example; pbakaus/impeccable, Apache-2.0); growth-design-psychology (skeuomorphism; ideas only, 2026-10-01)
reviewed: 2026-10-01
-->

# UX Principles — road signs at the point of decision

The model knows these laws. This file says **where each one decides something** in a Ship
build, and states Ship's defaults where there's a choice. Labels: REQ / PLATFORM / EXPERT / SHIP
(see `accessibility.md`). The project registry and `DECISIONS.md` override every SHIP line here.

Deeper references: accessibility → `accessibility.md` · states, gestures, touch →
`interaction-design.md` · spacing/grids → `layout-responsive.md` · type → `typography.md` ·
color → `color.md` · forms → `forms-feedback.md` · words → `copy-clarity.md` ·
review taste → `design-quality.md`.

---

## 1. Deciding what goes on a screen (Arc, Vi, Crit)

| When you are… | Apply | Ship default |
|---|---|---|
| Choosing how many options/actions to show | **Hick's law** — choice time grows with count and complexity | Show what matters now; put the rest behind "More"/Advanced (progressive disclosure). When people can't easily choose, recommend one honestly. |
| Laying out features/toolbars | **Pareto** — a few features carry most use | The critical path is prominent; secondary actions go in an overflow menu. With room, key actions stay visible; hidden content stays discoverable (the next item's edge shows). |
| Deciding who absorbs complexity | **Tesler** — complexity moves, it doesn't vanish | The system absorbs it: pickers for near dates (memorable ones: `forms-feedback.md` §1), detected defaults over questions. |
| Showing long numbers, codes, lists | **Chunking** (Miller's 7±2 is about memory, not a menu limit) | Group digits (card, phone, IBAN) and long lists into scannable sections. Don't cap nav at 7 "because Miller". |
| Adding any element | **Cognitive load** | Every element earns its place; cut duplicate labels, extra confirmations, decorative icons. Nothing pops up or moves for attention inside a task. |
| Asking people to remember | **Recognition over recall** (EXPERT, Nielsen) | Options visible, recent items offered, and the code, total or item kept on screen while it's being used. |
| Choosing a pattern for a common task | **Jakob's law** — people expect your app to work like the others they use | Use the platform's standard control and placement first; novelty needs a reason in `DECISIONS.md`. |
| Borrowing from the physical world | **Skeuomorphism** (EXPERT) | A physical metaphor (a dial, a shutter sound, a page turn) when it teaches how something works; never decoration that fights the platform's look. |
| Placing the primary action | **Control hierarchy** (PLATFORM) | One primary action per view (SHIP); secondary actions discoverable (menu, swipe with alternative, toolbar). |

## 2. Making interactions feel right (Dev, Eye, Test)

| When you are… | Apply | Ship default |
|---|---|---|
| Sizing and placing targets | **Fitts's law** | Big, close targets for frequent actions; expand hit areas with padding/`contentShape`, not bigger glyphs. Sizes: `accessibility.md` §3. |
| Placing primary actions on phones | **Thumb reach** | Primary actions in the lower half (bottom bar, toolbar, sheet button); rare actions can live at the top. |
| Handling latency | **Doherty threshold** (~400 ms keeps flow) | Acknowledge input immediately (pressed state, optimistic update); skeletons for content > ~1 s; progress + estimate for long jobs. |
| Accepting input | **Postel's law** | Accept messy input (spaces in card numbers, "jan 5", pasted formatting); normalise on the way in. |
| Showing progress in multi-step flows | **Goal gradient** | "Step 2 of 4" or a progress bar; show the remaining effort honestly. |
| Shaping the most repeated task | **Efficiency** (EXPERT, Nielsen, Saffer) | It takes the fewest steps; start from the last choice or the context, never from zero; swipe, context menu and keyboard shortcuts sit on top of visible controls. |

*Animation timing is the motion skill's call (`.claude/skills/ship/motion/references/animation.md`)
— Doherty sets the response budget, not animation durations.*

## 3. Making layout communicate (Pol, Dev)

| Principle | Road sign |
|---|---|
| **Proximity** | Tighter spacing inside a group than between groups (`layout-responsive.md` §2). |
| **Common region** | Use a surface/section only when proximity alone can't group. |
| **Similarity** | Same function → same look. Two styles for one action is a bug; static things never look like buttons. |
| **Uniform connectedness** | Connectors (step lines, breadcrumbs) show sequence and relation. |
| **Von Restorff** | Make exactly one thing different — the primary or the destructive action. |
| **Prägnanz** | Simplest readable form wins: fewer borders, one shadow style, one radius scale. |
| **Serial position** | First and last slots of a nav/list are remembered — put the key items there. |
| **Aesthetic-usability** | Polish buys trust and patience — it doesn't excuse a usability failure. |

## 4. Making experiences stick (Vi, Crit)

- **Peak-end:** design the success moment and the ending (confirmation, completion screen, a
  quiet "done" state) — don't redirect away from the peak.
- **Zeigarnik:** show honest incomplete states ("2 of 5 set up") to invite completion. Never
  manufacture fake incompleteness to nag.
- **First run (PLATFORM, SHIP):** value before sign-in, permissions or tutorials; a real result from
  a filled-in example; at most three ideas, skippable, never shown again once dismissed. The rest of
  the first run, pricing, cancelling and reminders: `psychology.md`.

## 5. Platform-aware patterns (HIG/Material ideas that apply everywhere)

- **Respect system preferences (REQ where accessibility-related):** appearance, Reduce Motion,
  text size, Increase Contrast, Reduce Transparency. These are expectations, not features.
  Reduce Motion is **gentler, not none**: swap movement for a short (~150–200 ms) opacity fade;
  keep color/opacity feedback and progress. Never a global `0.01ms` kill switch
  (`.claude/skills/ship/motion/references/reduced-motion.md`).
  ```css
  :root { color-scheme: light dark; }
  ```
- **Use device capabilities** before fields: autofill, contacts, location, camera/scan, Apple
  Pay / wallet, passkeys, Sign in with Apple.
- **Smart data entry:** pickers/segmented controls over free text when choices are known;
  prefill from context; validate on blur (`forms-feedback.md`).
- **Feedback hierarchy:** match weight to significance — quiet inline/haptic for routine success,
  inline message for warnings, a blocking dialog only for destructive or irreversible decisions.
- **Loading & launch:** content or skeleton first, never a blank screen; restore where the user left off.
- **Modality:** a modal is for a self-contained task (compose, confirm, pick); always a visible
  way out; prefer sheets on iOS, dialogs sparingly on web.
- **Settings:** good defaults beat options; put task-specific options (sort, filter, view) in the
  screen they affect.
- **Charts:** one insight per chart; values readable without hovering (a labelled axis from zero, or
  a value on each mark); consistent chart colors across the app; a text summary or
  data table for screen readers (REQ 1.1.1); don't encode series by color alone (REQ 1.4.1).

## 6. Inclusion & language (Vi, Pol, Crit)

- Plain words; define unavoidable jargon. Plain language also localises better.
- Gender-neutral by default ("they", role names); don't assume family structure, names or
  culture in forms, security questions or examples.
- Disability language: follow the community and the person — some prefer person-first
  ("person with low vision"), many Deaf and autistic people prefer identity-first. Never use
  disability as a negative metaphor ("crippled", "blind to").
- Avoid idioms and culture-specific humour in UI strings; leave room for longer translations —
  short labels can double in length (W3C i18n guidance) — and test right-to-left if you localise into RTL languages.
- Represent a range of people in imagery and sample data.

## 7. Branding inside the product (Pol)

- Brand shows up through voice, one accent color, typography, and motion character — not logos
  on every screen (PLATFORM: HIG says launch screens aren't branding moments).
- Brand accent marks interactive things (EXPERT, Practical UI): links, primary buttons, selected
  and focus states — not headings or decoration (`color.md` §4).
- A custom display face is fine; body text uses the system face or a highly legible text face
  unless `design-model.yaml` says otherwise (`typography.md`).
- Standard placement first, brand expression second (Jakob).
