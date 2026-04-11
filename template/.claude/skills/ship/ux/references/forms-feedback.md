# Forms & Feedback Reference

> **Agent routing:**
> - **Arc** → Section 1 (plan form architecture, multi-step flows, disclosure patterns)
> - **Dev** → Sections 1–3 (build forms, validation, feedback patterns, state management)
> - **Crit** → Section 2 (review: label visibility, error placement, accessibility, feedback clarity)
> - **Test** → Section 3 (QA: edge cases, rapid submit, paste, empty states, timing)
> - **Pol** → Section 2 (audit form consistency, error messaging standards, tone)

---

## Section 1: Form Architecture

### Visible Labels Are Non-Negotiable

Placeholder-only labels are a UX trap. When a user focuses a field, the placeholder text disappears—leaving no reference point for what they're entering. Even experienced users forget field purpose mid-entry, especially in longer forms. A focused user's attention is on the input itself, not scanning upward for context.

**Why it matters:** Users with cognitive load (distraction, multitasking, screen reader users) cannot recover the field purpose once focus is gained. Mobile users with small screens have even less space to reference label text elsewhere.

**Correct:** Persistent label above or inside the field with visual distinction when focused. Label stays visible, field purpose remains anchored.

**Incorrect:** Placeholder text only ("Enter email"). On focus, users see empty field and guess what goes here.

---

### Error Placement: Below Fields, Not Above

Eye-tracking research shows that after completing input, users look downward at their work, not upward to a form summary. Errors in a summary above the form are discovered only on re-scan. Adjacent inline errors catch attention naturally as the user reviews what they entered.

Top-of-form error summaries are useful for navigation (especially long forms), but cannot substitute for inline errors. Inline errors tell users *exactly where* the problem is without extra cognitive effort.

**Why timing matters:** Users expect validation after they've finished entering data in a field (on blur), not mid-thought (on keystroke). Keystroke validation shows "invalid email" after typing "j", training the user to ignore real-time feedback noise.

**Correct:** Label → Input → Inline error message (below, small text, red icon). Clear, immediate, co-located.

**Incorrect:** Email field → User types "j" → Message appears: "Invalid email format" → User frustrated mid-entry → Turns off notifications → Misses real errors later.

---

### Inline Validation Timing: Blur, Not Keystroke

Keystroke validation penalizes users for thinking out loud. A user typing an email address encounters "Invalid format" after every single keystroke during composition. This creates two problems:

1. **Learned helplessness.** Users train themselves to ignore warnings (notification fatigue).
2. **Interruption.** Real-time feedback breaks focus and flow state.

Blur validation (when user leaves the field) is the natural pause point where they've completed entry and are ready for feedback. At that moment, a clear error message is helpful, not annoying.

**Keystroke validation is justified only for:** Unique username availability (async check), password strength (educational, not blocking), credit card type detection (immediate visual feedback that helps).

**Correct:** User enters email on keystroke (silent), leaves field (blur), error appears if invalid.

**Incorrect:** User types first character, error flashes, user closes browser.

---

### Progressive Disclosure: Overwhelming Choice

Showing all form options upfront violates Hick's Law—choice reaction time increases with the number of options. A form with 20 fields is cognitively heavier than a form with 5 fields visible and 3 hidden under "Advanced Options".

Progressive disclosure works because:
- Users focus on required fields first (lower cognitive load).
- Optional/advanced sections appear only if needed.
- Form appears shorter and less intimidating on initial view.

**Pattern:** Required fields visible → Optional section collapsible or on next step → Advanced options behind "More Settings" link.

**Incorrect:** All 25 fields visible at once, user scrolls past 20 they don't need, completion rate drops.

---

### Multi-Step Form Design

#### Step Indicators
A numbered step indicator (1 of 5) tells users where they are in the journey and how much further remains. This manages expectations. Without it, users abandon mid-flow because they can't estimate time investment.

#### Back Navigation
Users need to revisit previous steps to correct or review data. Preventing back navigation frustrates users and breaks trust. Save their input so they don't re-enter data when backtracking.

#### Save & Resume
Long multi-step forms benefit from "Save and continue later" buttons that store partial progress. Users often leave forms, return later, and expect their work to persist. Session-based or account-based persistence is crucial for completion rates.

#### Why Each Matters
- Step indicator: Reduces abandonment (users know the endpoint).
- Back navigation: Builds confidence (users feel in control).
- Save progress: Enables real-world workflows (users don't complete in one sitting).

**Correct:** Step 2 of 5 → User can click back to Step 1 → Data preserved → User completes later.

**Incorrect:** Step 2 of 5 → No back button → User must start over if they leave.

---

## Section 2: Feedback Patterns

> **Overlap note:** This section covers feedback *structure and placement* (where to show errors, how to structure empty states, toast vs inline patterns). For the actual *words* in error messages, empty states, and confirmation dialogs, see `copy-clarity.md` Section 2.

### Empty States: Onboarding, Not Just "No Data"

An empty state is the user's first interaction with a feature. It's a teaching moment, not a failure state. A blank list with no guidance leaves users wondering:
- Is this broken?
- What goes here?
- How do I add something?

A well-designed empty state includes:
1. **Illustration or icon.** Visual anchor that signals "this is intentional empty state, not a bug".
2. **Headline.** Clear label: "No tasks yet" or "Your inbox is clear".
3. **Explanation.** Brief context: "You'll see saved items here once you create them".
4. **Primary CTA.** Call-to-action that shows the next step: "Create your first task" button.

Empty states reduce support tickets and improve onboarding velocity.

**Correct:** Empty list → Illustration → "No projects yet" → "Create a project" button → User knows exactly what to do.

**Incorrect:** Blank white space → User assumes bug → User refreshes or closes app.

---

### Toast Patterns: Dismissible Auto-Dismiss

Toasts are transient notifications that appear briefly then disappear. Auto-dismiss timing is critical:

- **< 3 seconds:** Users don't read it; feels like a flicker.
- **3–5 seconds:** Sweet spot. Readers have time to process; impatient users see results.
- **> 5 seconds:** Feels sticky and intrusive; users feel held hostage.

**Always include a manual dismiss button.** Auto-dismiss timing assumes users are reading at the moment the toast appears. A user focused on their next task might miss the window. A close (×) button lets them dismiss immediately without waiting.

**Placement:** Bottom-right (out of primary content area but visible). Top-center if mobile or full-width layout.

**Correct:** "Saved!" toast → Auto-dismisses after 4 seconds → Manual × button available → User either waits or clicks.

**Incorrect:** Non-dismissible "Processing..." message stuck on screen for 8 seconds → User frustrated, clicks back, loses context.

---

### Confirmation Dialogs vs. Undo

Confirmation dialogs interrupt flow. Before every destructive action, a modal blocks the user, requiring a decision. For non-critical actions, this is overkill.

**Undo is better UX** because it doesn't interrupt. The user completes their action, sees a brief confirmation message with "Undo" option, and continues. If they made a mistake, they tap Undo. If not, they move on.

**Use confirmation dialogs only for:** Irreversible actions (delete account, permanent data loss, billing changes). Use undo for: Marking emails as read, archiving, soft deletes, rebuffable operations.

**Correct:** User marks email as read → Brief toast "Marked as read" with Undo button → User continues workflow.

**Incorrect:** User marks email as read → Modal appears "Are you sure? This cannot be undone!" → User clicks OK → Workflow interrupted for confirmation theater.

---

### Disabled State Design: 0.38–0.5 Opacity

Disabled form fields or buttons must be visually distinct from active states but remain recognizable. Research from Material Design establishes that **0.38–0.5 opacity** is the threshold where disabled state is perceived as unavailable but not completely illegible.

**Why the range:** 0.38 opacity is the minimum perceivable reduction for color contrast. 0.5 opacity is the maximum before users mistake the element for active. Above 0.5, a disabled button might look clickable. Below 0.38, the element becomes unreadable.

**Additional signals:** Pair opacity with a cursor change (not-allowed) and remove pointer events (prevent accidental clicks). Tooltip explaining why ("Complete Step 1 first") is helpful.

**Correct:** Disabled button at 0.45 opacity → Cursor changes to not-allowed on hover → User understands it's inactive but knows what it is.

**Incorrect:** Disabled button at 0.8 opacity → Still looks clickable → User clicks → Nothing happens → Confusion.

---

### Loading States: Skeleton > Spinner

A spinner (rotating circle) tells the user "something is happening" but provides no information about what's arriving. A skeleton (content shape placeholder) sets expectations about the incoming data structure.

**Why skeleton is superior:**
- **Content expectation.** User sees placeholder text, images, layout before real content loads.
- **Perceived speed.** Skeleton content feels faster because the shape is already there; only color/detail fills in.
- **Accessibility.** Screen readers can announce skeleton structure; spinners are just "loading... loading... loading".

Use spinners for lightweight, quick operations (< 1 second). Use skeletons for data-heavy operations where content shape matters.

**Correct:** User loads article → Skeleton shows text block, image, author info → Real content loads → User doesn't see blank space.

**Incorrect:** Loading spinner spins for 3 seconds → Content pops in → Layout shift → User startled.

---

## Section 3: QA Patterns

### Submit with Empty Required Fields
**What to test:** Form submission with all required fields empty.

**Why it matters:** Ensures validation catches incomplete submissions. A form that accepts empty required fields will silently fail on the backend, creating corrupted data or API errors that confuse users.

**Expected behavior:** Form rejects submission, shows error messages on empty fields, prevents API call.

**Edge case:** Hidden required fields (revealed by progressive disclosure). Validate that the form catches empty required fields even if they're initially hidden.

---

### Submit with Invalid Data Per Field Type
**What to test:** Email fields with non-email input ("abc"), phone fields with letters, date fields with invalid dates (Feb 30), number fields with text.

**Why it matters:** Different field types have different validation rules. Email validation must reject "test@" (incomplete). Phone validation must accept "(555) 123-4567" and "555-123-4567" and "5551234567" (variants). Date fields must reject impossible dates.

**Expected behavior:** Each invalid entry shows a specific error message ("Invalid email format", "Phone must be 10 digits", "Date cannot be February 30th"), not generic "Invalid input".

**Error message quality:** Specific errors guide correction ("Must be a valid email with @ symbol") vs. generic errors waste user time ("Error").

---

### Rapid Submit Clicks (Debouncing)
**What to test:** Click submit button 5 times rapidly while form is processing.

**Why it matters:** Prevents double-submission bugs. Without debouncing, rapid clicks create duplicate API calls (duplicate charges, duplicate account signups, duplicate database records). Modern payment systems penalize double charges, so this is a compliance issue, not just UX.

**Expected behavior:** First click submits, button disables, subsequent rapid clicks are ignored. Form shows "Processing..." and prevents further interaction.

**Test with network throttling:** Simulate slow connections (3G, latency 2000ms) and verify that button doesn't re-enable until submission completes.

---

### Paste Into All Fields
**What to test:** Password manager auto-fill and manual paste operations into all input fields (email, password, text, number, phone).

**Why it matters:** Password managers (1Password, LastPass, Bitwarden) rely on paste events to fill credentials. If a form blocks paste (e.g., password confirmation field), users cannot use password managers and must type passwords manually, increasing error rate and reducing security adoption.

**Test scenarios:**
- Paste email into email field (should work).
- Paste password into password field (should work).
- Paste password into password confirmation field (should work).
- Use browser's built-in password manager (1Password, Chrome autofill) to auto-fill login form.

**Expected behavior:** All paste operations work. Password managers fill forms without errors.

---

### Empty States with No Data
**What to test:** Load a feature/page when user has zero items (zero tasks, zero projects, zero purchases).

**Why it matters:** Empty states are not error states. If a page shows broken UI (missing text, layout shifts, truncated labels) when there's no data, users think the app is broken, not that they just need to create something first.

**Test scenarios:**
- Load an empty task list (verify empty state UI, not broken layout).
- Load a new user's profile (verify onboarding empty state, not blank page).
- Delete all items in a list (verify empty state appears, not a broken list).

**Expected behavior:** Empty state displays properly with illustration, text, and CTA button. No layout breaks, no missing elements, no console errors.

---

### Toast Auto-Dismiss Timing
**What to test:** Measure time from toast appearance to auto-dismiss. Verify manual dismiss button works.

**Why it matters:** Toast timing directly affects whether users read notifications. A 2-second toast dismisses before readers finish ("Saved!"). A 10-second toast overstays and feels intrusive. Timing should be consistent across all toasts.

**Test scenarios:**
- Trigger success toast (verify disappears in 3–5 seconds).
- Trigger error toast (verify remains slightly longer, ~5 seconds, to ensure users read).
- Trigger "Undo" toast (verify remains long enough for action, ~6–8 seconds).
- Click manual dismiss button during auto-dismiss countdown.

**Expected behavior:** Toasts dismiss on schedule. Manual dismiss works instantly. Toasts don't pile up (if multiple triggered, only recent one visible or they stack neatly).

---

## Cross-Cutting Principles

1. **Validation is progressive, not punitive.** Show errors after user interaction (blur), not during thought (keystroke).
2. **Errors explain the fix.** "Email must contain @" is better than "Invalid".
3. **Empty states teach, don't shame.** "You have no tasks yet. Create one!" not "No data available".
4. **Feedback is timely and dismissible.** Toasts auto-dismiss but let users close early.
5. **Disabled states are visually distinct.** 0.38–0.5 opacity signals unavailable without confusion.
