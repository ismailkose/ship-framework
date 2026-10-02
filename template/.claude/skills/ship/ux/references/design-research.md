<!-- ship-reference
id: ux-design-research
kind: ship-default
sources: .claude/skills/ship/design/references/design-model-schema.md (Ship contract); design-md-spec@9bf8eae (google-labs-code/design.md, Apache-2.0 — section headings and lint, via /shipmate design); books-and-sites (Jon Yablonski, Laws of UX — Jakob's law); impeccable@9d715cc (ideas only, Ship's words: naming the rut, candidates from the audience's world, dealing by lot, the direction contract, colour strategy; pbakaus/impeccable, Apache-2.0); taste-skill@ce26fc2 (ideas only: the second default look models reach for; leonxlnx/taste-skill, MIT); lennys-talks-2026 (Katie Dill: specific vs probable); the founder's review 2026-09-28 (real material first; the gibberish test)
reviewed: 2026-09-28
-->

# Design Research & Direction

Labels: REQ / PLATFORM / EXPERT / SHIP (see `accessibility.md`). Used in the think and design
stages (§2 before every new direction); §3 says where decisions land.

**Where decisions are written (Ship's registry — never elsewhere):**

| File | Holds | Never holds |
|---|---|---|
| `DESIGN.md` | Prose: intent, principles, `brand.feel` rationale, voice & tone, do/don't, SAFE/RISK decisions and *why* | Hex values, sizes, spacing numbers, token tables |
| `design-model.yaml` | Tokens as data: color primitives (hex lives only here) → semantic roles, type, radius, spacing, motion, modes | Rationale prose |
| `design/components.yaml` | The component manifest: name, file, semantic tokens used, variants, rule | Page-specific compositions |
| `PDC.md` | The index the design gate reads — points at the three above | Content of its own |

Schema and validation: `.claude/skills/ship/design/references/design-model-schema.md`;
`/shipmate design --init` scaffolds all four; `--tokens` edits `design-model.yaml`.

---

## 1. Competitive research (Vi, Pol)

**Purpose:** learn the conventions users already expect in this category (Jakob's law) and find
where competitors are weak — not to copy their look.

- **3–5 products** (SHIP): fewer misses category norms, more adds little. Include one
  best-in-class product from outside the category for craft reference.
- **Use them, don't just screenshot:** onboarding, the primary task, an error, an empty state,
  the phone experience, keyboard/VoiceOver basics, dark mode.
- **Extract per product:** navigation model and depth; what's above the fold; gestures and
  micro-interactions; type scale, palette use, spacing rhythm, radius; voice; where it's weak.
- **Classify every finding:**
  - **SAFE** — the category convention users rely on (keep it).
  - **RISK** — a deliberate break that creates identity (needs a reason and confidence).

Template (keep in the research notes, not in `DESIGN.md`):

```markdown
## <Product> — <category>, <audience>
Nav: <tab/sidebar/…>, depth <n taps to key features>
Above the fold: <…>   Hidden: <…>
Interaction: <gestures, feedback, primary-action affordance>
Visual: type <scale feel>, color <how used>, spacing <rhythm>, radius <…>, voice <…>
Strong: <patterns worth understanding>
Weak / opportunity: <gaps: states, mobile, accessibility, dark mode, speed>
SAFE: <…>   RISK candidates: <…>
```

**Look at the best, for the bar and never the composition:** `inspiration.md` says where, per need,
what you may open yourself, which sites only the founder can use, and what to ask them to bring back.

**Going deeper when it matters:** time the same journey (sign-up → first value) across
competitors and count steps; plot everyone on a 2×2 of the two dimensions that matter most for
this product (e.g. dense ↔ minimal, playful ↔ professional) and look for the open quadrant.

## 2. Direction — from the product's world, not its category (Pol → founder)

Models give the probable answer, and so does anyone in a hurry. A direction has to come from what only
this product has, and still say what the product is when every word is removed.

**Material, when there is some.** The founder's photos (the thing, the place, the people), their words
(a menu, a note to a customer, a review they loved) and artefacts (signage, packaging, receipts). A
colour sampled from their photos and lettering taken from their own signs beat a palette picked for a
feeling. Mockups never supply copy, prices, reviews or product shots.

**When there's none** (most solo builders: no photos, no logo, not a designer), the direction still
comes from the product, not from a template:
- from what the product does and the audience's world (candidates below), rendered in code: type,
  colour fields, shape, layout, and the product's own interface or data as the hero;
- stand-ins authored at full fidelity where the concept needs them: sample content, an illustrative
  image if an image tool is available, a diagram or notation drawn from the audience's world. Mark each
  `SAMPLE:` in a code comment and list it in `TASKS.md`. Never an empty "photo here" box, a random stock
  photo, or clip art assembled from SVG shapes;
- claims are never invented: prices, customers, ratings, reviews, numbers, awards. Leave them out or ask;
- a drawn stand-in reads as the thing at a glance: the silhouette everyone knows (a scored loaf, not a
  cross-section, which can pass for a dumpling). One unmistakable cue of the subject is a convention
  to keep (SAFE); the identity lives in how everything else departs (RISK).

Don't ask designer questions. Show two rendered concepts and let the founder point.

**Name the obvious versions before proposing**, one line each:
- what this category always ships (a restaurant: a full-bleed food photo, a centred serif name, "Book a
  table");
- its predictable opposite: the category plus "not generic";
- the AI default look, the handful of looks generated products share whatever the subject: for warm
  or handmade things a cream background, brown-black text, a terracotta or brass button and a fancy,
  often italic, serif; for tech a near-black page with one neon colour and a glow; for "editorial"
  thin rules and tiny capital labels. Treat the first palette that comes to mind as already spent.

A ban list with fixed replacements only makes the next default. The test is whether someone could guess
the look from the category alone, or from the category plus "not generic". `design_model.py sameness`
flags the colour-and-type side of it in the registry.

**Candidates from the audience's world.** List 5–7 concrete things the audience knows by heart:
objects, places, rituals, and their graphic traditions (a menu board, a train ticket, a field guide, a
scoreboard, a seed packet). Give each one line on how it could carry the one thing we'll be best at.
Span at least three material families (paper and print, tools and hardware, signs and places, screens
and notation…); when most land in one, you stopped at the most obvious artefact. Ask what the product
would be as a physical object, and what its world looked like before the web. Then look at the
best of the kind (`inspiration.md`) to set the bar, not to pick the concept.

**Deal, don't rank.** Your ranking drifts to the probable, so the two concepts to render are picked by
lot (seed S2). Add your own pick when it differs, with an honest line on how familiar it is, and keep
the plain category standard as a quiet door: if the founder takes it, build it at full craft, without
irony. A candidate that can't carry the product's truth is replaced before the deal, never rescued by it.

**The concept's contract**, in plain words (about 100 words; DESIGN.md › Direction once picked):
- *The idea:* the one idea, grown from the point of view's "one thing we'll be best at", and the usual
  arrangement for this kind of product it refuses.
- *The look:* colour strategy first — restrained (neutrals plus one accent), committed (one colour
  carries 30–60% of the surface), full (three or four named roles) or drenched (the surface is the
  colour) — then the palette; faces chosen like objects from that world (a subject association such as
  books → serif is not a reason); shape, density, texture. Recognisable with every word removed.
- *First screen:* what sits where and at what size, where the primary action is, what it proves. If
  someone saw only this screen, what would they describe an hour later? A mood means it hasn't committed.
- *The special touch:* the one moment only this product has, used once rather than scattered.
- *The risk:* what could go wrong, said plainly.

Light or dark leads by the scene (who, where, in what light), never by category; both modes still
ship. If a line of the contract reads like a mood, the direction isn't decided yet.

**How loud, by surface.** What the visitor came to do sets how much the concept shows. A landing page,
onboarding or a paywall persuades: the concept leads. An app's working screens operate: the task,
states and platform conventions lead, and the concept lives in precise details (a colour's job, one
typeface moment, the special touch). Help and docs are read: comprehension first. A portfolio or gallery
lets the work lead. Decide per surface, not per product.

**Build it committed.** On web, every control speaks the concept's vocabulary (a stock component left
in its default look is a lapse); on native, system controls stay and the brand lives in the open layer
(`.claude/skills/ship/ios/references/hig-ios.md` §10). The first screen proves the thing rather than claiming it; one decisive real
photo beats five weak ones. Then the blind look (seed S6): the words garbled, two reviewers who weren't
told the product say what it sells and who it's for (one guess is noisy). A wrong subject ("a coffee
roaster", "a dumpling bar") means the subject's cue isn't clear yet: fix that first, with a clearer
drawing or a real photo. Before the first launch, three real people take the same test (launch Phase 4).

Also:
- **References:** name what each admired product lends — "Things (restraint)" → `brand.references`.
- **Audience shapes density and disclosure:** frequent or expert use → density and shortcuts;
  occasional or novice use → progressive disclosure and guidance. Older or low-vision audiences →
  larger default type and higher contrast (the REQ floor applies to everyone).
- **Coherence:** every choice (type, colour energy, radius, density, motion character, voice) serves
  the same idea; contradictions go back to the founder as a choice.
- **Feel words** are optional and only ever the founder's (`brand.feel`), never invented to fill a field.

Each direction choice is recorded: tokens in the YAML, the reason in `DESIGN.md` (Direction, SAFE /
RISK), cross-cutting product decisions in `DECISIONS.md`.

## 3. From decision to registry (Arc, Dev)

```
DESIGN.md (why)            design-model.yaml (what)          design/components.yaml
feel, voice, do/don't  ──►  primitives → semantic roles  ──►  components use semantic roles only
                                   │
                                   └─► emitters: Theme.swift (iOS), CSS variables (web), Compose theme
```

- Tokens are defined **before** UI is built; a missing token is added to the registry, never
  improvised in a component.
- Changing a brand color = one registry edit + `design_model.py validate` + re-emit; views don't change.
- `DESIGN.md` may *name* a role ("the action color is reserved for primary actions") but never
  restates its value — duplicate values drift.

## 4. Auditing an existing product (adopt, don't restart)

When a codebase has no registry or an inconsistent one:
1. **Inventory** every unique screen by flow (onboarding, core, settings, errors, empty).
2. **Extract** the values actually used: colors, sizes/weights/families, spacing, radii, shadows,
   icon sets (DevTools, Xcode view debugger, grep for literals).
3. **Cluster** near-duplicates (typically many grays and font sizes where a few are meant).
4. **Consolidate** clusters into registry primitives and semantic roles; note outliers as fixes.
5. **Adopt:** write `design-model.yaml` with `emit.swiftui` names matching the existing theme so
   views don't change, register existing reusable components in `design/components.yaml`, move
   rationale into `DESIGN.md`, then `/shipmate design --init` generates `PDC.md`. Diff emitted tokens
   against the old theme before replacing it (schema: "Adopting an existing app").
