# UX Copy & Clarity Reference

> Words are interface elements. Bad copy causes the same friction as bad buttons — users hesitate, misunderstand, or abandon. This reference teaches how to write UI text that's clear, specific, and honest. It also covers AI-generated copy patterns that signal "no human reviewed this."
>
> **Agent routing:**
> Vi → Section 1 (define voice and tone during product strategy)
> Dev → Section 2 (implement copy patterns — button labels, errors, empty states)
> Pol → Sections 1-3 (audit copy consistency, voice alignment, AI copy detection)
> Crit → Section 2 (unclear copy = task failure; review error messages, labels, CTAs)

---

## Section 1: Voice & Tone Framework

### Voice Is Constant, Tone Varies

**Voice** = your product's personality. It doesn't change. If your product is professional and direct, it's always professional and direct — on the homepage, in error messages, in emails.

**Tone** = how you adapt voice to context. Professional and direct sounds different in a success state ("Project created") vs an error state ("We couldn't save your changes. Try again.") vs onboarding ("Let's set up your first project.").

### Defining Voice in 3 Dimensions

Pick your position on each spectrum:

| Dimension | Spectrum | Example |
|-----------|----------|---------|
| Formality | Casual ←→ Formal | "Oops, that didn't work" vs "An error occurred" |
| Energy | Calm ←→ Energetic | "Your file is ready" vs "Your file is ready!" |
| Authority | Peer ←→ Expert | "Try this approach" vs "Best practice recommends" |

Most products land somewhere in the middle. Extremes work for specific audiences (gaming = casual + energetic, banking = formal + calm). Write your voice as a one-liner: "We're a knowledgeable friend who respects your time." Then test every piece of copy against it.

### Tone Map by Context

| Context | Tone Shift | Example |
|---------|------------|---------|
| Onboarding | Warmer, encouraging | "Let's get you started" |
| Success | Confirming, brief | "Saved" |
| Error | Direct, helpful | "Password must be 8+ characters" |
| Destructive action | Serious, clear | "This will permanently delete 12 files" |
| Empty state | Guiding, optimistic | "No projects yet — create your first one" |
| Loading/waiting | Reassuring | "Setting things up..." |
| Upgrade prompt | Honest, specific | "Pro gives you 10 team members and unlimited projects" |

---

## Section 2: Copy Patterns That Work

### Button Labels: Verbs, Not Descriptions

Buttons should say what they do, using a verb. Not what they are.

```
Incorrect:
  "Submit"        → submit what?
  "OK"            → ok what?
  "Click here"    → where is "here"?
  "Let's go!"     → go where?
  "Yes"           → yes to what?

Correct:
  "Create project"     → specific action
  "Save changes"       → specific action
  "Delete account"     → specific action (scary, intentionally)
  "Send invitation"    → specific action
  "Download report"    → specific action
```

**Verb + noun pattern always.** Every button label should include the verb (action) and the noun (object): "Save post", "Delete account", "Export report", "Send invitation." Never just "Save", "Delete", or "Submit" — the noun tells the user what they're acting on without needing surrounding context. The only exception is when the object is completely unambiguous from the UI (a single-field form with one obvious action).

**Destructive buttons** get extra specificity: "Delete" becomes "Delete this project." Users should never wonder "delete what?"

**Confirmation dialogs** match the action: if the dialog says "Delete this project?", the confirm button says "Delete project" (not "Yes" or "OK").

**Button group ordering.** Left-to-right = most important to least important. Primary action leftmost, secondary next, tertiary/cancel rightmost. On mobile, stack vertically in the same priority order (primary on top). This follows natural reading direction and Fitts's Law — the most important action is closest to where the user's attention already is.

### Destructive Action Friction

Not all destructive actions need the same friction. Match the confirmation pattern to the severity:

**Reversible + low impact** (archive, hide, mark as read): No confirmation needed. Use a secondary or tertiary button. Offer undo via toast: "Archived. [Undo]".

**Reversible + moderate impact** (bulk edit, status change, remove from list): Confirmation dialog with a descriptive button. "Archive 12 items" not "OK". The button label names the action and the count.

**Irreversible + high impact** (delete account, purge data, revoke access): Type-to-confirm pattern. Require the user to type the resource name (e.g., "my-project") before the confirm button enables. This is the one case where a disabled button is correct — it's intentional friction, not a usability gap.

```
Low friction (archive):
  [Archive]  ← secondary button, no dialog
  → Toast: "Conversation archived. [Undo]"

Medium friction (bulk delete):
  Dialog: "Delete 12 items?"
  Body: "These items will be moved to trash for 30 days."
  [Cancel]  [Delete 12 items]  ← destructive primary

High friction (delete account):
  Dialog: "Delete your account?"
  Body: "This permanently removes all data. Type 'delete my account' to confirm."
  Input: [                    ]
  [Cancel]  [Delete account]  ← disabled until input matches
```

### Error Messages: What Happened + What To Do

Every error message has two parts:

1. **What went wrong** (specific, not generic)
2. **How to fix it** (actionable, not vague)

```
Incorrect:
  "Invalid input"                     → what's invalid? how do I fix it?
  "Something went wrong"              → what? should I retry? wait? scream?
  "Error 422"                         → is this a puzzle?
  "Please try again later"            → how much later? will it work then?

Correct:
  "Email must include @"              → what's wrong + implicit fix
  "Password needs 8+ characters"      → what's wrong + clear requirement
  "Couldn't save — you're offline"    → what happened + why
  "File too large (max 10MB)"         → what's wrong + the limit
  "Username taken — try another"      → what happened + what to do
```

**Placement:** Error messages go immediately below the field they're about. Not at the top of the form. Not in an alert. Below the field, in red or error color, with an icon.

### Empty States: Guide, Don't Abandon

Empty states are the first thing new users see. They're onboarding moments, not dead ends.

```
Incorrect:
  "No data"
  "Nothing here"
  "0 results"
  [blank white space]

Correct:
  "No projects yet"
  → "Create your first project to get started" [Create Project button]

  "No messages"
  → "When your team sends messages, they'll appear here"

  "No search results for 'xyzzy'"
  → "Try a different search term or [browse all projects]"
```

**Structure:** Description of the empty state + why it's empty (if helpful) + CTA to resolve it.

### Confirmation Dialogs: Specific Consequences

Generic confirmations teach users to click "OK" without reading. Specific consequences make them think.

```
Incorrect:
  Title: "Are you sure?"
  Body: "This action cannot be undone."
  Buttons: [Cancel] [OK]

Correct:
  Title: "Delete 'Q4 Marketing Plan'?"
  Body: "This will permanently remove the document and its 23 comments.
         Team members will lose access immediately."
  Buttons: [Keep document] [Delete permanently]
```

**Rules:**
- Title names the action and the object
- Body states the specific consequence (numbers help: "23 comments", "12 files")
- Buttons describe actions, not abstract choices ("Delete permanently" not "Yes")
- Cancel button is the safe choice — label it as the safe action ("Keep document")

### Loading Copy: Set Expectations

```
Incorrect:
  "Loading..."          → how long? what's loading?
  [spinner with no text] → is it broken or loading?

Correct:
  "Loading your projects..."           → specific
  "Analyzing 847 data points..."       → specific + impressive
  "Setting up your workspace..."       → specific to onboarding
  "This usually takes about 10 seconds" → sets expectation
```

For fast operations (< 2 seconds), no copy needed — just a spinner or skeleton. For slow operations (> 3 seconds), add context. For very slow operations (> 10 seconds), add progress or a time estimate.

---

## Section 3: AI Copy Slop Patterns

When AI generates UI copy, it falls into predictable patterns that feel generic. Learn to spot them.

### Pattern: Exclamation Inflation

AI adds exclamation marks to signal friendliness. One per page is fine. Three per screen is noise.

```
AI default:
  "Welcome back!"
  "Great job completing your profile!"
  "Your project is ready to share!"
  "Exciting news — new features are here!"

Human edit:
  "Welcome back"                          → calm is confident
  "Profile complete"                      → brief confirmation
  "Your project is ready to share"        → no exclamation needed
  "New: dark mode, faster exports, and 3 new templates" → specific > excited
```

### Pattern: Vague Value Propositions

AI defaults to abstract benefits instead of specific ones.

```
AI default:
  "Powerful integrations"
  "Seamless experience"
  "Boost your productivity"
  "Take your workflow to the next level"

Human edit:
  "Connects to Slack, GitHub, and 200+ tools"
  "Loads in under 2 seconds on any device"
  "Users save 4 hours per week on reporting"
  "Automate weekly reports in 3 clicks"
```

**The fix:** Replace adjectives with numbers. Replace abstractions with specifics. If you can't be specific, the feature isn't defined well enough.

### Pattern: Synonym Cycling

AI uses different words for the same action across the interface to avoid "repetition."

```
AI default:
  Button 1: "Create"
  Button 2: "Generate"
  Button 3: "Build"
  Button 4: "Make"
  (All do the same thing: create a project)

Human edit:
  All buttons: "Create"
  (Consistency > variety in UI copy)
```

**Rule:** Pick one term per action and use it everywhere. "Create" means create. "Delete" means delete. Don't cycle through "Remove", "Delete", "Discard", "Trash" for the same action.

### Pattern: Emoji Seasoning

AI adds emoji to appear modern and friendly. Emoji work for decorative purposes but fail as functional indicators.

```
AI default:
  "🚀 Launch your project"
  "✨ New features available"
  "💡 Pro tip: try keyboard shortcuts"
  "🎉 You did it!"

Human edit:
  "Launch your project"           → the button is enough context
  "New features available"        → or: "New: dark mode and faster exports"
  "Keyboard shortcuts: ⌘K for search, ⌘S for save" → specific > cute
  "Project published"             → calm confirmation
```

**When emoji work:** Status indicators (✓ Done, ⚠ Warning), category labels in casual products, user-generated content. **When they don't:** CTAs, error messages, navigation, professional products.

### Pattern: "We" Overuse

AI defaults to "we" because it sounds friendly. But "we" is vague — who is "we"?

```
AI default:
  "We're having trouble loading your data"
  "We've updated our privacy policy"
  "We recommend enabling two-factor auth"

Human edit:
  "Couldn't load your data — check your connection"    → direct
  "Privacy policy updated on March 15"                  → factual
  "Two-factor authentication adds a security layer"     → informative
```

"We" works when referencing the team/company specifically: "We're a team of 12 based in Berlin." It doesn't work as a generic subject for system messages.

---

## Audit Checklist

**Voice consistency:**
- [ ] Voice defined in 3 dimensions (formality, energy, authority)
- [ ] Tone varies by context but voice stays constant
- [ ] Same terminology for same actions across the product
- [ ] No "we" in system messages (unless referencing the team specifically)

**Copy clarity:**
- [ ] Every button uses a specific verb ("Create project" not "Submit")
- [ ] Every error message: what happened + how to fix it
- [ ] Every empty state: what's empty + CTA to resolve
- [ ] Every confirmation dialog: names the object + states consequences
- [ ] Loading states: context for slow operations (> 3 seconds)

**AI slop:**
- [ ] No more than 1 exclamation mark per screen
- [ ] No vague adjectives where numbers could go ("powerful" → "200+ integrations")
- [ ] Same action = same word everywhere (no synonym cycling)
- [ ] Emoji used functionally or not at all
- [ ] No "we" as system message subject

---

*Based on UX writing patterns from Material Design writing guidelines, Apple HIG terminology standards, and Stripe's editorial voice guide.*
