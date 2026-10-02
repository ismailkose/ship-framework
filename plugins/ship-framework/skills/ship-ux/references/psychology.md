<!-- ship-reference
id: ux-psychology
kind: mixed
sources: Growth.Design, 106 cognitive biases and principles (growth.design/psychology and its cheat sheet; ideas only, all rights reserved; 2026-10-01); books-and-sites (Jon Yablonski, Laws of UX; Jakob Nielsen; the GOV.UK Design System; Richard Thaler and Cass Sunstein, Nudge: transparent, easy to refuse, for the person's good); https://developer.apple.com/app-store/review/guidelines/ (3.1.1, 3.1.2; 2026-10-01); probe maintainers/probes/2026-10-01-design-psychology.md (what models apply unprompted); the founder's decisions 2026-10-01 (help, never trick; find the balance between; use all 115 principles)
reviewed: 2026-10-01
-->

# How people decide: help, never trick

Models know these principles; asked directly, they apply most of them well. This file says
**where each one decides something** and what Ship does there, so it happens every time, including
the moments nobody planned (a paywall added mid-build, a first run nobody designed). Labels: REQ ·
PLATFORM · EXPERT · SHIP (`accessibility.md`). The product's registry, `DECISIONS.md` and the
founder's taste override every EXPERT and SHIP line. Choice and layout principles (Hick, Fitts,
hierarchy, grouping, Jakob, Tesler, chunking) are in `ux-principles.md` §1 to §3.

**The rule (SHIP, founder decisions 2026-10-01): help people decide, never trick them, and find the
balance in between.** Most persuasion isn't black and white: a real deadline, an offer when
someone cancels or the yearly plan preselected can serve the person and the business at once. Every
nudge (a default, a badge, an offer, a reminder) passes the balance check in §7. A trick is a
blocker in review, whatever it would do for conversion; a pattern close to the line is the
founder's call, recorded with its guardrails.

**In review:** when a finding comes from how people decide, name the principle ("nine equal
choices on the first screen: Hick's law"), so the founder learns it once and spots it again.

## 1. First run and empty states (Vi, Arc, Dev, Crit)

| When you are… | Apply | Ship default |
|---|---|---|
| Writing the first screen | **Priming** (EXPERT) | What people see first sets how they read the rest: open with the real value, never a false frame (an inflated "was" price, a fake rush). |
| Planning the first run | **Aha moment** (EXPERT) | Name the moment the product first proves itself; cut every step before it that the moment doesn't need. |
| Choosing the first action | **Spark effect** (EXPERT) | Something doable in seconds, from a preset or a filled-in example; ask a little more each time it works. |
| Deciding what to teach | **Paradox of the active user** (EXPERT) | Nobody reads a tour: teach one thing, in place, the first time it's needed. |
| Placing sign-up, payment, ratings, permissions | **Reciprocity** (EXPERT) | A real result first: sign-up after the first result, a rating after a success, an upgrade after use. |
| Asking for a permission | **Reciprocity** (PLATFORM) | At the moment it helps (the person turns on a reminder, picks a photo), with the reason; never on launch. After a no, only when they reach for that feature again, pointing to Settings. |
| Setting defaults | **Default bias** (EXPERT) | Preselect what most people would choose for themselves. Anything that costs money, shares data or sends marketing starts off. |
| Asking how experienced someone is | **Dunning-Kruger effect** (EXPERT) | Self-ratings miss both ways (beginners rate high, experts low): start from the answer, then adapt to what people actually do. |
| Explaining what the product does | **Picture superiority** (EXPERT) | Show it: a preview, a sample result or a thumbnail beats a paragraph. |
| Showing an empty screen | **Feedforward** (EXPERT) | Say what will appear here, offer one first action, and a sample or template to start from. |
| Letting people build something | **Investment** (EXPERT) | Let them add something of their own early (a name, a first entry), and take it out any time: export and delete. |
| Any prompt, tour or paywall | **Reactance** (EXPERT) | A visible way out; saying no never takes away what people already had. |
| Interrupting a task | **Flow** (EXPERT) | Tips, upsells, rating and permission asks wait for a natural pause, never mid-task. |

## 2. Waiting, progress and endings (Dev, Crit, Eye)

| When you are… | Apply | Ship default |
|---|---|---|
| Starting work that takes more than a few seconds | **Feedforward** (EXPERT) | Before it starts, say what will happen and roughly how long; let people keep using the app or leave. |
| Showing long work | **Labor illusion** (EXPERT) | The real steps and counts as they happen ("640 of 2,100"). Never add delay or invented steps to look thorough. |
| Responding to input | **Doherty threshold** | `ux-principles.md` §2: answer every input at once. |
| Showing progress | **Goal gradient, Zeigarnik** | `ux-principles.md` §2, §4: honest progress and real unfinished items only. |
| Designing the end of any flow | **Peak-end rule** (EXPERT) | Design the best moment and the last screen. A success says what was done and what's next; a cancel, delete or sign-out ends calmly, saying what happens and when. |
| After a purchase or a big choice | **Cognitive dissonance** (EXPERT) | Confirm what they got and what happens next ("Pro is on: every chart, unlimited habits"); it settles doubt. The way back stays as easy (§4). |
| Adding delight | **Delighters** (EXPERT) | For rare moments that matter (the first success, finishing something big), quieter each time it repeats, with a Reduce Motion path. |
| Choosing which states to design first | **Negativity bias** (EXPERT) | Failure moments (a lost entry, a failed payment, a scary error): one bad moment outweighs many good ones. |
| Writing for a stressful moment | **Empathy gap** (EXPERT) | Write for someone tired, rushed or upset: few words, one next step, nothing to decide that can wait. |

## 3. Words that help people decide (Pol, Crit)

| When you are… | Apply | Ship default |
|---|---|---|
| Naming things | **Curse of knowledge** (EXPERT) | Newcomers' words, not the builder's. Before launch, watch one person who didn't build it try the first run. |
| Showing a number that frames two ways | **Framing** (EXPERT) | Show both when they differ: per month and per year, the saving in money, what's in and what isn't. |
| Showing reviews, counts or logos | **Social proof** (EXPERT) | Only real, current numbers and reviews used with permission; none until you have them (`design-quality.md` §3). |
| Citing experts or badges | **Authority bias** (EXPERT) | Only real sources and badges, and exactly what they vouch for. |
| Writing a teaser or a notification | **Curiosity gap** (EXPERT) | The point is in the message; a teaser pays off on the very next screen. |
| Calling something personal | **Barnum effect** (SHIP) | "For you" only when it comes from the person's own data, saying what it's based on. |
| Asking people to remember | **Recognition over recall** (EXPERT) | Recent items, suggestions and pickers instead of remembering or retyping. |
| Telling the product's story | **Storytelling effect** (EXPERT) | A real person's before and after, named and with permission, beats a feature list; never an invented one. |
| Saying you do good | **Noble edge** (EXPERT) | Only what's real, specific and checkable ("1% of revenue to X, reported each year"); vague goodness reads as a pitch. |
| Correcting someone (support, an error, a wrong belief) | **Backfire effect** (EXPERT) | Don't argue: give the evidence plainly and let them check it; pushing harder makes people dig in. |
| Answering criticism in public | **Streisand effect** (EXPERT) | Answer it openly and fix it; hiding or deleting criticism spreads it. |

## 4. Pricing, paywalls and cancelling (money stage, Dev, Crit)

| When you are… | Apply | Ship default |
|---|---|---|
| Showing plans side by side | **Anchoring** (EXPERT) | A real reference: the monthly plan beside the yearly plan's true monthly cost, its total and the saving in money. |
| Highlighting a plan | **Centre-stage** (EXPERT) | At most one recommended plan, the one that fits most people, with the reason; "Most popular" only if it's true. |
| Designing the tiers | **Decoy effect** (guard) | Every plan is the best buy for someone. No tier built to be skipped. |
| Stating the price on iOS | **App Review 3.1.2** (REQ) | The billed amount and period are the most prominent price; renewal, trial end and how to cancel come before purchase (`${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/references/commerce-identity.md` §1). |
| Offering a trial | **Hyperbolic discounting** (EXPERT) | Value in the first session, the later price as plain as today's, and a reminder before the trial turns paid. |
| A limited offer | **Scarcity** (EXPERT) | A limit only when it's real, with its terms ("20 founding seats", "ends 30 June"); no timers that restart. |
| Showing items, templates or photos | **Group attractiveness** (EXPERT) | A curated set looks better than its parts (a bundle, a gallery); check each item still holds up alone. |
| Checkout and credits | **Cashless effect** (EXPERT) | The real total is visible at the moment of paying; credits and coins show their price in money. |
| Designing cancel or downgrade | **Loss aversion, sunk cost** (SHIP) | As easy as joining: where people expect it, at most one honest offer (a pause or a cheaper plan) as easy to skip as to take, then plainly what stops, what's kept, and the date. No guilt, no type-to-confirm. |
| Changing a price or a plan | **Weber's law** (EXPERT) | Small, announced steps; keep existing customers on their price for a while where you can. |

## 5. Habits and reminders, every platform (Vi, Dev, Crit)

| When you are… | Apply | Ship default |
|---|---|---|
| Setting up reminders | **Self-initiated triggers** (EXPERT) | People choose what they're reminded of and when; each reminder says what to do and lets them do it from the notification. |
| Sending them over time | **Banner blindness** (EXPERT) | Specific, never the same every time; when several in a row are ignored, ask whether to move or stop them. |
| Goals and streaks | **Commitment and consistency** (EXPERT) | People set their own small goal, reminded in their words; never turn a small yes into a bigger ask. |
| Someone comes back after a gap | **Fresh start effect** (EXPERT) | A clean start at a natural boundary (a new week); never a broken-streak scold. |
| Rewards | **Variable reward** (guard) | Occasional honest surprises tied to real progress; no random payouts or endless feeds built to keep people pulling. |
| Ending a session | **Exit points** (EXPERT) | End on purpose ("done for today", "all caught up") instead of an endless list. |
| Pairing a habit | **Temptation bundling** (EXPERT) | Let people pair a chore with something they enjoy (a podcast for the run, a friend for the walk), their choice. |
| Adding social features | **Spotlight effect** (EXPERT) | People feel more watched than they are: progress private by default; nobody's lapse shown to others. |
| Adding anything that changes behaviour | **Second-order effects** (EXPERT) | Ask "and then what?": reminders breed fatigue, leaderboards breed gaming, streaks breed anxiety. Design the brake with the feature. |

iOS permission timing, interruption levels and notification actions:
`${CLAUDE_PLUGIN_ROOT}/skills/ship-ios/references/notifications-background.md` §2.

## 6. Reading research and feedback honestly (think, retro, care)

Every reading passes through biases, the builder's first (**cognitive bias** is the family name):

- **Confirmation bias:** write the pass line and what would prove you wrong before looking, then
  read the evidence against you first.
- **Survey bias:** ask what people did the last time, and count commitments (a pre-order, a
  payment); never "would you use it?".
- **Observer expectancy:** one task in the person's words, then stay quiet; trust what they do over
  what they say.
- **Survivorship bias:** ask who's missing from the feedback (people who quit, stalled at sign-up,
  or never came back) and hear from two of them.
- **Availability heuristic:** the latest or loudest feedback feels most common; count people
  before acting on it.
- **The builder's own habits**, applied where they're decided: the tool you know looks right for
  everything (**law of the instrument**, think); plans run long and polish fills its time
  (**planning fallacy**, **Parkinson's law**, plan); our own misses come first (**self-serving
  bias**, retro).

## 7. Finding the balance: tricks, and what's close to the line

Most persuasion sits between helping and tricking. Before building anything meant to move a
decision (a price, a badge, a default, a reminder, an offer, a cancel step), run **the balance
check**:

1. **True:** every claim holds today (the deadline, the count, the saving, "most popular").
2. **Clear before yes:** people see the price, the period, renewal and what they're agreeing to first.
3. **Free to say no:** no is visible, readable, neutral (no guilt) and respected.
4. **Easy to undo:** leaving is as easy as joining: cancel, unsubscribe, export, delete.
5. **Would they thank you:** if people saw exactly how it works, would they still be glad it's there?

- **A no to 1 to 4, or a clear no to 5, is a trick:** never built, and a blocker in review. Many
  also break App Review rules, accessibility or consumer law, so no product decision overrides them.
- **Yes to all five is honest persuasion:** build it.
- **Yes to 1 to 4 with 5 unsure is close to the line:** the founder decides. Record it in
  `DECISIONS.md` with its guardrails and a measurement plan for both sides: conversion, and what
  it costs people (refunds, cancels in the first week, complaints, ratings). When the cost side
  rises, bring the decision back (retro).

| Trick (never) | What it looks like | Ship's default | Close to the line (the founder's call, with its guardrails) |
|---|---|---|---|
| Fake urgency | Countdowns that restart; "ends tonight" every night | A real deadline with its terms, or none | A countdown to a real end (a launch price, a welcome offer per person); it never restarts and the price really changes |
| Fake scarcity | Invented stock or seat counts | A real limit, with its terms | A live count of a real limit ("6 of 20 seats left") |
| Fake social proof | Invented reviews or numbers; "someone just bought" toasts; asking only happy users to rate | Real, permitted reviews; ask everyone or no one | Real proof placed at the moment of choice; the system rating prompt right after a success, for everyone who reaches it |
| Misleading decoy | A tier built only to make another look cheap; a false "Most popular" | Plans that each suit someone; one honest recommendation | A top tier that anchors the price, as long as it's real and someone buys it |
| Confirmshaming | "No thanks, I hate saving money" | A neutral decline: "Not now" | A decline that names the plain consequence ("Continue with the free plan"); personality, never guilt |
| Visual interference | The decline tiny, faint or styled as a link beside a loud primary | The decline keeps text contrast and a full-size target (`${CLAUDE_PLUGIN_ROOT}/skills/ship-components/references/components.md` §4) | A much louder primary (filled, beside a text-button decline), as long as the decline stays readable, full size and where people expect it |
| Hidden costs | Fees, tax, the renewal price or the period only at the last step | The full price and period from the first price shown | A per-month figure beside a yearly price, smaller than the billed amount; "plus tax" said up front where tax varies |
| Forced continuity | A trial turns paid with no warning | A reminder before the first charge; cancel in a few taps | A trial that needs a card, with its terms shown before it starts |
| Roach motel | Cancelling harder than joining: hidden, phone only, screens of offers, type-to-confirm | The §4 cancel flow (at most one offer) | Asking why before the last step, with an offer matched to the reason; still one screen, skipped as easily as taken |
| Pre-ticked extras | Add-ons, marketing email or data sharing on by default | Off until the person turns them on | Defaults that serve the person: the yearly plan preselected when it's cheaper, the reminders they asked for; never money, data sharing or marketing |
| Trick questions | Double negatives in opt-outs ("Untick to not receive") | One plain, positive question | The benefit stated in the question ("Get a weekly progress email"), unticked |
| Nagging | Asking again after a no (ratings, upsells, permission banners) | Respect the no; one gentle reminder at most, in context | A standing, quiet way back (an upgrade row in Settings, a small badge), never a screen in the way; the system's own limits stay |
| Disguised ads | Promotions styled as alerts, system messages or content | Label a promotion as one | A promotion in the app's own style, labelled and dismissible |
| Guilt and shame | Streak shaming, "we miss you" guilt pushes, "giving up on your goals?" | Kind, specific copy; a fresh start | True loss framing with a way back ("Your streak ends at midnight", a streak freeze) |
| Fake work or personalization | Artificial delay, invented steps, generic lines dressed as insight | Real steps; insight from the person's own data | A short pause that shows real work ("Using your 5 answers"), no longer than it takes to read |
| Lock-in | No way to export what people made; deletion pressure | Export in a common format; data kept until people delete it | Value that's hard to leave (history, integrations, people), while export and delete always work |
| Bait and switch | The price or plan changes after people commit | The price shown is the price charged | An intro price shown with the price after it; a price rise announced ahead, with the date |
