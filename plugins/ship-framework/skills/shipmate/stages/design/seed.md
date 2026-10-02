## Seed — a new product · part of the design stage, read only on this path

Small and visible: core tokens, a few primitives, one real screen, grown from what only this product
has, not from its category. Read `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/design-research.md` §2 before S2.

**S1. Say it back, then material and context** (skip what the brief and taste already answer). First one
plain sentence back to the founder: what it is, who it's for, how it should feel ("a neighbourhood bakery
page for people ordering on their phones; warm and local, not a chain"), so they can correct it.
**Material:** use what only this product has when it exists (photos, the founder's own words, signage, a
menu). Most founders have none yet, and that's fine: the concepts come from what the product does and the
audience's world (S2), and you author the stand-ins at full fidelity (sample content, illustrative images,
the product's own UI with sample data), each marked `SAMPLE:` in a code comment and listed in `TASKS.md`
to replace. Claims (prices, reviews, customers, numbers) are never invented. Then: product type, audience
and scene (who, where, in what light); the point of view (care-lens §1: plain questions, only what's
unknown; draft and mark proposed what they can't answer); any products they admire and *what* they borrow.
Never ask designer questions: show the choices. Research an unfamiliar category (`--research`, §1).

**S2. Direction: concepts from the product's world** (design-research §2). Name the obvious versions
first: what the category always ships, its predictable opposite, and the AI default look (for warm
subjects a cream background, a fancy serif, a terracotta button); treat that palette as spent. List 5–7
candidates from the audience's world across three or more material families; deal two of the N by lot, not
your favourites (`python3 -c "import random; print(random.sample(range(1, N + 1), 2))"`), add your own
pick if it differs, and keep the plain category standard as a quiet third door. Look at the best of the
kind for the bar (`inspiration.md`: open what you can; name one or two sites for the founder, with what to
look at and bring back). Render each concept on the first screen, not as swatches, with its contract: the
idea, the look, the first screen, the special touch, the risk. Keep conventions people rely on (SAFE);
depart where identity lives (RISK). These are proposals: **values land only in `design-model.yaml`**,
after the founder picks. Record the contract in DESIGN.md › Direction and the pick as a taste decision.

Motion: the template's defaults are the motion authority's (`${CLAUDE_PLUGIN_ROOT}/skills/ship-motion/SKILL.md`); only
the founder changes one. Recipes come with the `motion` route; Reduce Motion keeps a short fade.

**S3. Core tokens.** Copy `${CLAUDE_PLUGIN_ROOT}/skills/ship-design/references/design-model-template.yaml` to
`design-model.yaml`, fill every TODO from S2 (`brand.feel` only with the founder's words), keep `modes: [light, dark]`
(light-only needs a "Dark mode exception" in DESIGN.md), and set `emit:` for the Stack — e.g.
`swiftui` + `preview_swiftui` on iOS, `css` or `tailwind` + `preview_html` on web, `compose` on
Android, plus `docs`. Then `design_model.py validate`; fix every error and REQ warning.

**S4. A few primitives.** Register only what the first screens need and a second screen would plausibly
reuse (a button, a surface, a list row, a text field) in `design/components.yaml`, as the schema says
(`origin: seed`, `planned: true` before code exists). No speculative entries. `validate` again. **S5.
Emit** (`design_model.py emit all`, then `design_model.py docs`) and write **PDC.md** (below) now: the
design gate needs it before any UI file.

**S6. Prove it on a real screen** — the highlight of this command. Build the first screen from the brief
with the generated theme, the seeded primitives and the real material, fully committed — on web every
control in the direction's vocabulary; on native the system's controls, with the brand in the open layer
(`hig-ios.md` §10) — and the parts nobody draws themed too (design-quality §5). Light and dark, then
screenshot. Before app code exists, the registry's own sample screen stands in:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py render --scheme both    # iOS: PNGs, macOS, no simulator
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py emit preview-html        # web: open it and screenshot
```
Then the **blind look**: garble every word (`python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/gibberish.py <shot>`;
web: `gibberish.js` in the page) and give only that image to `ship-eye` in blind mode, twice (one guess is
noisy); a wrong subject means redraw it first. "Software", "could be anything", a guess that needs the
words, or a right guess read from the AI default look (cream, a fancy serif, the usual photo) means the
direction isn't done yet. Run `design_model.py sameness` too (web: the web scan as well, web skill): each
default needs a reason from the material or a pick. Inspect in one batched round (sizes × modes), fix in
one batch, confirm once. Show the founder the screen and the blind guess, not the token list; their
reaction is the approval gate — adjust, re-emit, re-render until they say yes, save the approved screens
to `design/approved/` (the reference later screens are checked against) and record what they said.
**S7.** Write the short **DESIGN.md** (below) from the approved screen.
