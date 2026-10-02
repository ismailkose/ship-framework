<!-- ship-reference
id: review-care-lens
kind: ship-default
sources: ideas only, written in Ship's words — six Lenny's Podcast talks and interviews (2026): Katie Dill (Stripe), Claire Vo (ChatPRD), Dan Shipper (Every), Marty Cagan (SVPG), Geoff Charles (Ramp), Cat Wu (Anthropic); the founder's gibberish test (2026-09-28). Where each idea lives: maintainers/audit/talks-claim-map.md in the Ship Framework repository
reviewed: 2026-09-28
-->

# Care lens — what the product is missing, not only what's wrong

Preview. Used by `/shipmate review --care` (one lens per reviewer) and whenever the founder asks
what's missing, what feels generic, or how to make it feel cared for. A review asks "is it right?";
this asks "would the person using it feel it was made for them?" Nothing here is a score.

## 1. The yardstick: the product's point of view

`DESIGN.md › ## Point of view` holds five fields. Each is **confirmed** (the founder's words, quoted)
or **proposed** (Ship's draft, with the evidence it came from):

- **Who and when:** who it's for and the moment they're in.
- **What they care about** in that moment.
- **What we believe**, and what would prove us wrong.
- **The one thing we'll be best at.**
- **What we'll never do.**

Missing fields:
- Draft them from the app, its copy, the README and the store listing, and mark them proposed.
- Offer two concrete versions to pick from: a screen or a line of copy each. Never ask the founder
  for adjectives.
- A proposed field is a hypothesis to show the founder, not a standard to judge findings by.

## 2. One lens per reviewer

**Crit — the editor** (dimension `journey`). Walk the journey end to end as the user, starting from
the point of view's moment:
- **Solves it:** does it solve the problem the person came with, or only look finished?
- **Anticipates:** the small need nobody asked for (today's date where it helps, the next free time
  when a slot is full). Failure help for whoever is really using it: someone in a hurry, a screen
  reader, an agent.
- **Hangs together:** later steps remember what earlier ones knew, and words and states agree across
  screens.
- **Finished:** no dead ends; empty, error and first-run states exist; every step says what happens
  next.

**Pol — expression** (dimension `expression`):
- **Specific or probable:** start from the blind guess (care pass step 4: Eye saw the first screen with
  every word garbled). "Software", "could be anything" or the wrong thing means the look says nothing
  about this product yet; a right guess read from the AI default look (cream and a fancy serif for a bakery)
  doesn't count. With the name swapped, would it pass for another product? Familiar controls
  are fine. Missing specificity — in the content, the words, the moments — is the gap, and so is the
  AI default look (a cream background, brown-black text, a terracotta button, a fancy serif) with no
  reason in the product's own material.
- **Reasons:** take the three most visible choices (a colour, a word, a motion) and say why each is
  this and not something else, tied to the point of view or the moment. "It's a token" is
  consistency, not a reason. An arbitrary choice is a gap.
- **A thread:** does one idea from the point of view recur across screens (a word, a shape, a
  behaviour)?
- **Ship's own defaults:** `design_model.py sameness` lists tokens still at Ship's seed values.
  Report them as evidence that the product has no visual voice yet, not as a defect.

**Eye — the task walk** (dimension `task walk`):
- Run the journey's task in the real build (simulator or browser) as the user would.
- Where reachable, use realistic data: empty, long text, an error, the first run.
- Screenshot each step.
- Count the taps and screens in the task people repeat most, from opening the app to done; each one
  the task could lose is a candidate gap.
- Report where it felt careless, then a short refinement list: small, specific changes a layer below
  what users consciously notice (spacing that crowds, a jolt in a transition, a label that says less
  than it could).
- Stop at refinements that change how the step feels; don't chase perfection.

## 3. Evidence, ranked

1. What real users said or did: reviews, support email, why people left, analytics.
2. Running the app: Eye's walk, screenshots.
3. Reading the code.

Label each finding with its evidence. Findings from 2 or 3 alone are hypotheses about users. For a
big gap, suggest a quick real-user check, such as "ask three people to book a table and watch where
they hesitate".

The founder will watch people use it: plan the sessions first (one goal task in the person's words, what
to note, the pass line set before watching), then read their notes here as first-tier evidence.

Pasted feedback (reviews, support email, interview notes): group it into themes and count people, not
messages. Lost data, money or access comes first; then what most often stops people doing the main
thing, ahead of features and polish.

## 4. The report — in the conversation, not a form

- **Point of view:** one line, saying which fields are proposed.
- **Keep:** what already shows care, so nobody fixes it away.
- **At most 3 gaps,** ranked by what they cost the user. Each gives the moment, the evidence, the
  fix, and how to check the fix. Argue from what happens to the person; a proposed field is never
  stated as fact ("these users care most about…" is the draft talking).
- **Optional ideas:** at most 2 — an unexpected detail, or a bounded unusual idea worth trying.
  Never a blocker.
- **Not checked:** what you couldn't run or see.

Nothing else. Anything more you noticed (a bug, a smaller gap) stays out: one line gives only the
number ("I noticed 4 smaller issues; ask to see them"), with no examples, and you list them when the
founder asks. Three gaps is the point of the report, not a cut-off for a longer list. No scores,
percentages or ratings. End by asking which gap to fix first.

## 5. After the founder picks

- **Build the pick** (the build stage), then check it the way the report said.
- **Record the choice:** `taste.py add --kind decision --source approval --domain care --statement
  "<gap and fix>" --rationale "<why it matters to the user>" --quote "<their words>"`.
- **A gap they turn down** gets `--source rejection` and isn't raised again. Query
  `taste.py query --domain care` before reporting.
- **A proposed field they confirm:** write their words into DESIGN.md and mark it confirmed.

## 6. How strict: the commitment

TASKS items can carry `[probe]`, `[experiment]` or `[promise]`. `ship.py state` reports it, and the
core journey is always a promise.
- **Promise:** gets the whole care bar.
- **Experiment:** gets the three lenses without the refinement list.
- **Probe:** is labelled and kept away from people who'd rely on it. Review it for safety and
  clarity only.

## 7. Guardrails

- Never require taste words, and never treat a proposed word as the founder's standard.
- Conventions people rely on aren't defects. The gap is a missing reason or missing specificity.
- One lens per reviewer: don't repeat another reviewer's lens.
- A report changes no project files. `review.py` keeps care runs out of projects without `.ship/`.
- A copy tweak doesn't get a care pass.
- Say what was verified, what's self-reported, and what's a hypothesis.
