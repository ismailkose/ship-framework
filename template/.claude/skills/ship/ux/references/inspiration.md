<!-- ship-reference
id: ux-inspiration
kind: ship-default
sources: the founder's list of design sites (2026-09-28); each site checked on 2026-09-28 for what it collects and whether an agent may open it (robots.txt, and terms where found)
reviewed: 2026-09-28
-->

# Looking at the best: where to look, and what to bring back

Great work sets the bar: the finish, the detail, how motion starts and settles, how a product shows
itself doing its job. It never picks the concept, which comes from the product's world
(`design-research.md` §2), and nothing is copied: not the layout, the palette, the logo or the words.

**When:** before a new direction, a signature interaction, an app icon, logo or share image, or a kind
of screen the product hasn't had yet (the design stage, variants). It's optional: never block on it.

**How:**
1. Pick the need in the table.
2. Open two or three examples yourself from the "you can open" column: one page per site, read-only,
   no downloads, no crawling. Say what you looked at and what it taught, one line each.
3. Name one or two sites from the founder's column, with exactly what to look at and what to bring
   back ("on 60fps.design, filter by Sheets and screenshot the two closest to how our pre-order sheet
   should open"). A founder who isn't a designer gets the same: a place and a thing to look for,
   never "find some inspiration".
4. Keep what comes back: screenshots in `design/references/`, and what each one lends, in the
   founder's words, in taste (`taste.py add --kind decision --source example --screenshot <file>
   --url <link> --statement "<what it lends>" --quote "<their words>"`; a founder preference when it
   holds across products). The next design step starts from it.

| Need | You can open | Only the founder can (their browser, account or screenshots), and what to bring back |
|---|---|---|
| A new visual direction, a whole site | recent.design and inspora.design (broad feeds); seesaw.website, then the live sites it links | admiretheweb.com (filter by type and colour): two or three sites whose finish they'd want, a line on each |
| A signature interaction or motion | designspells.com (small delightful details); motion.zajno.com (motion principles) | 60fps.design (iOS and web interactions, mostly paid): a recording or two screenshots of the moment and how it should feel; Mobbin's animations (account) |
| An iOS screen or flow | (none) | Mobbin (shipped apps' screens and flows; account; its terms bar scraping): the same flow from two or three apps they trust; collectui.com (needs a real browser) |
| An app icon | (none) | icon.museum (needs a real browser): three icons they love and what they love in each |
| A logo or wordmark | brandlogo.co (logos as SVG) | (none) |
| A share image (Open Graph) | ogfolio.com, posts.design | (none) |

**Not for agents** (checked 2026-09-28): viewport-ui.design (its robots file blocks AI crawlers) and
umanmade.com (its terms forbid scraping); the founder may browse both. webinteractions.gallery was
down and wellmade.fyi's scope was unclear. A site's own rules come first: when it says no, only the
founder browses it.

## Code you can take (component and effect libraries, web)

For one signature moment on a web surface, a library piece can save days. Rules: one piece, tied to
the product's own content and restyled with its tokens (a shader orb or a goo button shipped as is
is the next generic look); take code only under a license that allows it; register it in
`design/components.yaml`; it passes the motion authority and accessibility (a reduced-motion version,
contrast, keyboard) and gets a static fallback and an off-screen pause if it's heavy (GSAP, WebGL,
WebGPU). None of these are for SwiftUI: on iOS they're references to rebuild natively.

| Library | What it offers | License (checked 2026-09-28) | You may |
|---|---|---|---|
| uselayouts.com | Animated React micro-interactions (React, Tailwind, Motion, via the shadcn CLI) | MIT | open it and use its code |
| shadercn.run | React shader components on WebGPU; publishes docs for agents (llms.txt) | MIT | open it and use its code; add a static fallback |
| gooey-shyt.vercel.app | shadcn/ui parts rebuilt with an SVG goo effect | not stated | look; ask the author before shipping its code |
| 23rd.dev | A shadcn registry of expressive pieces (shaders, ASCII fluid, a dithered 404), React or Svelte | not stated at the root | look; ask the author before shipping its code |
| annnimate.com | Paid GSAP animation components | proprietary; its terms forbid scraping and giving its components to AI tools | don't fetch or paste its code; the founder may browse the previews and buy after clearing the terms in writing |

