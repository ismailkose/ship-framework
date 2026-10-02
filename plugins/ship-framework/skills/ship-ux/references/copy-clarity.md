<!-- ship-reference
id: ux-copy
kind: mixed
sources: https://developer.apple.com/design/human-interface-guidelines/writing (2026-09-23); https://developer.apple.com/design/human-interface-guidelines/alerts (2026-09-23); https://m3.material.io/foundations/content-design/style-guide/ux-writing-best-practices (2026-09-23); https://m3.material.io/components/dialogs/guidelines (2026-09-23); https://www.w3.org/TR/WCAG22/ (2.5.3, 3.3.3; 2026-09-23); books-and-sites (Adham Dannaway, Practical UI); impeccable@9d715cc (ideas only: aphoristic cadence, dash saturation; pbakaus/impeccable, Apache-2.0); taste-skill@ce26fc2 (ideas only: poetic labels, the dash as an AI tell; leonxlnx/taste-skill, MIT); the founder's decision 2026-09-28 (no dashes in product copy)
reviewed: 2026-10-01
-->

# UX Copy & Clarity

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`).
**Registry first:** voice & tone and terminology live in `DESIGN.md` (prose layer). If it defines
a voice, a glossary or capitalization, follow it; this file fills the gaps.

---

## 1. Voice and tone

- **Voice is constant, tone flexes.** Write the voice as one line in `DESIGN.md` ("a calm expert
  who respects your time") and test copy against it.
- Place the product on three dials: casual ↔ formal, calm ↔ energetic, peer ↔ expert. Most
  products sit near the middle; extremes need an audience reason.

| Context | Tone | Example |
|---|---|---|
| Onboarding | warm, brief | "Add your first workout" |
| Success | confirming, quiet | "Saved" |
| Error | direct, helpful | "Password needs at least 8 characters" |
| Destructive | serious, specific | "This deletes 12 files permanently" |
| Empty | guiding | "No projects yet. Create one to get started." |
| Waiting | reassuring, specific | "Importing 240 photos…" |
| Upgrade | honest, concrete | "Pro adds 10 team seats and unlimited projects" |

## 2. Patterns

**Buttons and links**
- Start with a **specific verb** (PLATFORM: HIG, Material): "Save", "Send invite", "Add to Cart" —
  never "Click here", "Let's go!", "Yes/No".
- **Add the object when context doesn't make it obvious (SHIP):** "Export report" in a toolbar of
  several exports; plain "Save" is fine in an edit sheet whose title names the thing.
- Dialog buttons repeat the dialog's verb: "Delete project?" → **Delete** / **Cancel**. Cancel is
  always "Cancel" (HIG). The safe choice may be named for what it keeps ("Keep editing").
- Accessible name contains the visible label (REQ 2.5.3); capitalization per element type,
  consistent across the app (HIG: title case for alert buttons; Ship default sentence case elsewhere).
- **Links name their destination (REQ 2.4.4):** "Pricing details", never a bare "Learn more" or
  "Read more". A single-field web form (search, email signup) attaches its button to the field.
- **Checkbox and switch labels read as a plain yes:** "Email me about new features", not "Don't
  send me…" (a double negative is a trick: `psychology.md` §7).

**Button order — follow the platform, then Ship:**
- **Native dialogs and alerts (PLATFORM wins):** iOS/macOS put the default/most likely button on
  the trailing side (or top of a stack) and Cancel on the leading side (or bottom). Material
  dialogs put the confirming action trailing. Use system alerts and let them order buttons.
- **Web forms and in-page actions (EXPERT: Practical UI → SHIP default):** left-align buttons with
  the content, primary first, then secondary, then tertiary; on phones stack full-width with
  primary on top. If the product follows the platform order on web too, record it in `DECISIONS.md`.

**Destructive friction — match severity:**

| Severity | Pattern |
|---|---|
| Reversible, low impact (archive, hide, mark read) | No dialog; toast with **Undo** (HIG: don't alert for common undoable actions) |
| Reversible, wider impact (bulk move, status change) | Dialog naming count and effect: "Move 12 items to Trash?" → **Move to Trash** |
| Irreversible, high impact (delete account, purge data, revoke access) | Dialog with specific consequences + type-to-confirm; the confirm button may stay disabled until the text matches |

**Errors: what happened + what to do** (REQ 3.3.3). Specific, in the user's words, next to the problem.
- ✗ "Invalid input", "Something went wrong", "Error 422", "Try again later"
- ✓ "Enter an email like name@example.com" · "File is over 10 MB. Choose a smaller one." ·
  "Couldn't save: you're offline. Changes will sync when you reconnect."
- Don't blame ("You entered…"), don't joke about failure, don't expose codes without a human sentence.

**Empty states:** what goes here + why it's empty + the next action. "No results for 'xyzzy'"
+ "Check the spelling or browse all projects".

**Confirmations:** title names action and object ("Delete 'Q4 plan'?"); body states the concrete
consequence ("23 comments will be deleted. Collaborators lose access."); buttons are verbs.

**Waiting:** say what's happening for anything past ~1 s ("Loading your projects…"); past ~10 s
add progress or an estimate. No copy needed for sub-second actions. Work you know will be long:
say what and how long before it starts (`psychology.md` §2).

**Writing that scans (EXPERT: Practical UI, GOV.UK):**
- The word people scan for comes first in headings, labels, list items, links and messages;
  the point first, the detail next, background a tap away.
- Short sentences (about 25 words at most), short common words, "you", the active voice.
- Numerals for numbers ("3 projects"), the locale's grouping (1,250), big ones shortened (1.2M);
  ranges read "to". Spell out abbreviations people might not know.
- No period on fragments (labels, buttons, list items); siblings punctuate alike; items in a row
  run to similar lengths.
- Labels name the thing ("Email"), not the task ("Enter your email").
- Help and marketing pages: headings that say what's below, lists, one idea per paragraph.

**System messages (PLATFORM, HIG):** avoid "we" — it's unclear who "we" is ("Couldn't load
messages", not "We're having trouble…"). Prefer "Favorites" over "Your Favorites"; if you use
possessives, keep one perspective. Match input vocabulary to the device ("tap" on touch, "click"
with a pointer) or use device-neutral verbs ("select", "choose").

**Consistency:** one term per concept across the product (Create ≠ Generate ≠ New); keep a
glossary in `DESIGN.md` once the product has more than a handful of nouns.

## 3. AI copy slop — flag in review (Pol, Crit)

| Pattern | Tell | Fix |
|---|---|---|
| Exclamation inflation | Several "!" per screen | Calm statements; at most one where genuine delight fits |
| Vague value props | "Powerful", "seamless", "next level" | Concrete facts: numbers, named integrations, time saved (only if true) |
| Synonym cycling | Create / Generate / Build / Make for one action | One verb per action everywhere |
| Emoji seasoning | 🚀 ✨ 🎉 on CTAs, headings, errors | Remove; emoji are read aloud by screen readers ("rocket") — keep only where content is social/casual by design |
| "We" as system voice | "We're having trouble…" | State the fact and the fix |
| Hedged filler | "Please note that…", "Simply…", "Just…" | Delete the filler; "simply" blames users who find it hard |
| Fake urgency / confirmshaming | "Only 2 left!" (untrue), "No thanks, I hate saving money" | Honest scarcity only; neutral decline labels. Every other trick, and what to do instead: `psychology.md` §7 |
| Dashes as punctuation | "Fresh bread — every morning", a spaced "–" between clauses | No dashes in product copy (SHIP, 2026-09-28): a period, a comma, a colon or parentheses; ranges read "7:30 to 13:00" |
| Aphoristic cadence | Sections that land on a short rebuttal: "X. No Y.", "Not a feature. A platform." | Say the plain thing once |
| Poetic labels | "Field notes", "From the kitchen", "Quietly trusted by" | A plain label ("Menu", "Hours") or none |

## 4. Audit checklist

- [ ] Voice line exists in `DESIGN.md`; tone shifts by context, voice doesn't.
- [ ] Every button starts with a specific verb; ambiguous ones name the object; dialogs repeat the verb.
- [ ] Button order follows the platform in native dialogs and the recorded Ship/product rule elsewhere.
- [ ] Every error: what happened + how to fix, next to the problem, no blame.
- [ ] Every empty state: what, why, next action.
- [ ] Destructive actions use the friction level their severity needs.
- [ ] One term per concept; capitalization consistent per element type.
- [ ] No slop patterns from §3.
