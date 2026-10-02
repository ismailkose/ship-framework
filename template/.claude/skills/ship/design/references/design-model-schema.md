<!-- ship-reference
id: design-model-schema
kind: ship-default
sources: ship (design_model.py contract); motion values via the Ship repo's maintainers/audit/motion-defaults.yaml (emil-skills@d16ebe6); design-md-spec@9bf8eae (optional export); https://tailwindcss.com/docs/theme (checked 2026-09-23, Tailwind 4.3.3)
reviewed: 2026-09-23
-->

# Design registry — schema, ownership, tool

Load before writing or reading `design-model.yaml` or `design/components.yaml`.
Tool: `python3 .claude/skills/ship/design/bin/design_model.py <command>` (stdlib Python 3.9+).
Every rule below is checked by `validate`; `check` also fails when a generated file is stale.

## Who owns what — one fact, one file

| File | Owns | Written by | Never contains |
|---|---|---|---|
| `DESIGN.md` | intent, principles, rationale, voice, do/don't, exceptions | founder + /shipmate design | token values (hex, sizes, springs) — name tokens instead |
| `design-model.yaml` | every token value (source of truth) | /shipmate design, `adopt` draft | prose rationale |
| `design/components.yaml` | what components exist, where, when to use them, their API | /shipmate build registry loop | implementation |
| component files (`PrimaryButton.swift`, `Button.tsx`) | the implementation | product code — edited freely | raw values (use tokens) |
| generated files (Theme.swift, tokens.css, Tailwind theme, Theme.kt, previews, `design/COMPONENTS.md`, `design/DESIGN.spec.md`) | nothing — derived | `design_model.py` only | hand edits (the hash catches them) |
| `PDC.md` | an index: paths + the exact commands for this install | /shipmate design | facts owned above |

`validate` warns when DESIGN.md holds hex values. A change goes to the owning file, then
re-emit. Precedence when sources disagree: platform requirements & accessibility > product
decisions (these files, DECISIONS.md) > founder preferences > platform guidance > expert
authority > Ship defaults > agent inferences. Generators never rewrite 2–3 silently: they refuse
(see *Generated files*).

**Layering:** hex/raw values → only in `primitives` · `semantic` → dot-paths into primitives
(or `system.<name>`) · components → semantic tokens and scale tokens (`radius.card`,
`type.body`, `spacing.md`, `motion.snappy`) only.

---

## `design-model.yaml`

```yaml
schema_version: 1
modes: [light, dark]              # light-only needs a "Dark mode exception" note in DESIGN.md
brand:
  name: Tempo
  feel: [calm, warm, precise]     # optional, the founder's own words (1-5)
  feel_status: confirmed          # proposed = Ship's draft: a hypothesis, never the standard
primitives:                       # LAYER 1 — the only place for raw values
  color:
    paper: { 50: "#FAF9F6", 100: "#F3F1EC" }   # free ramp/stop names; 8-digit hex = alpha
    brand: { 500: "#E0633C", 300: "#EE9A7E" }
  type:
    family: Inter                 # simple form: family + scale { body: 17, title: 28 }
    # design: rounded             # the system family only: rounded | serif | monospaced — its own range
    # width: condensed            # the system family only: condensed | compressed | expanded (Apple)
    scale: { caption: 13, body: 17, title: 22, display: 28 }
    line_height: { body: 1.5, title: 1.2 }   # optional, simple form: names from the scale, 1 to 2.5
    # rich form (multi-font; document why in DESIGN.md):
    # families: { display: Gelasio, text: Inter, ui: system }
    # designs: { ui: rounded }    # rich form: design / width per system family key (widths: { … })
    # styles: { body: { family: text, weight: Regular, size: 17, line_height: 1.5 }, title: { family: display, size: 34, tracking: -0.01 } }
    #   font name = <family>-<weight> unless `font: "Exact-PostScriptName"`; family `system` = SF
    # dynamic_type: false         # default true (SwiftUI relativeTo:)
    # system_text_styles: true    # system font at a standard size → a Dynamic Type text style (.body, .subheadline…)
  radius: { control: 10, card: 18 }
  spacing: { unit: 4, scale: { sm: 8, md: 16 } }  # scale names can't start with a digit; no `x`
  motion:
    springs:                      # either form; emitted as written
      snappy:   { response: 0.3, damping: 1.0 }          # .spring(response:dampingFraction:)
      settle:   { duration: 0.4, bounce: 0 }             # .spring(duration:bounce:)
    curves:                       # named cubic-béziers; a name here overrides the built-in
      easeOut: [0.23, 1, 0.32, 1]
    durations:
      fade:  { ms: 200, curve: easeOut }                 # easeOut (default) | easeInOut | linear | <curve>
      sheet: { ms: 300, curve: [0.32, 0.72, 0, 1], use: enter }   # inline curve
    stagger: { ms: 50, max_items: 8 }
    # any spring/duration: `use:` (enter exit ui press move page momentum progress ambient
    # reduced) and `allow: [rule-id]` to accept a warning on purpose
  elevation:                      # optional — only if the product uses shadows; web emits --<prefix>-shadow-<level>
    raised: [ { y: 1, blur: 2, alpha: 0.06 }, { y: 4, blur: 12, spread: -2, alpha: 0.08 } ]   # x y blur spread alpha color:"r g b"
  elevation_dark: { raised: [ { y: 1, blur: 2, alpha: 0.4 } ] }   # optional per-level override; dark elevation is mostly a lighter surface
semantic:                         # LAYER 2 — meaning
  background: paper.50            # REQUIRED: background surface text muted hairline action
  surface: paper.100
  text: system.primary            # Apple adaptive colours: system.<name>
  muted: system.secondary
  hairline: system.separator
  action: brand.500
  on_action: paper.50             # recommended: text and icons on the action colour
  focus: brand.600                # recommended: the focus ring
  error: red.600                  # recommended: error text and icons
  success: green.700              # recommended: success text and icons (warning: … the same way)
  outline: ink.400                # recommended: field and checkbox borders, 3:1 (hairline is for dividers)
  chart: { 1: brand.500, 2: …  }  # optional: chart series (up to 5); web maps them to shadcn's --chart-1…5
  pnl: { gain: …, loss: … }       # groups → nested names (Theme.Colors.Pnl.gain)
semantic_dark: { … }              # same key set, required while dark ∈ modes
emit:                             # optional — where generated files go + naming
  swiftui:  { out: App/Theme/Theme.swift, namespaces: { colors: Brand, typography: Typo }, rename: { action: accent } }
  css:      { out: web/src/tokens.css, prefix: app, rename: { hairline: border },
              theme_selector: class,             # data-theme (default) | class — .dark/.light, what shadcn + next-themes use
              shadcn: { roles: { primary-foreground: on_action, destructive: danger }, radius: control } }  # shadcn/ui role bridge
  tailwind: { out: web/src/tailwind-theme.css }
  compose:  { out: app/src/main/java/…/Theme.kt, package: com.acme.ui.theme, name: Theme, fonts: { display: "FontFamily(Font(R.font.gelasio_bold))" } }
  preview_swiftui: { out: App/Debug/ShipDesignPreview.swift }
  preview_html:    { out: design/preview/index.html }
  docs:     { out: design/COMPONENTS.md }
  designmd: { out: design/DESIGN.spec.md }   # optional DESIGN.md-format export; off unless set
```

Without `emit.<target>.out`, output goes to `design/generated/…` — never onto product code.
`rename` maps a Ship role to the name the codebase already uses. Motion warnings come from
`references/motion-rules.yaml` (one table; values from the motion workstream).

**Theme selector.** Default `data-theme`: dark follows the OS and can be pinned with
`[data-theme]` on any subtree. `theme_selector: class`: dark is wherever the app sets `.dark`
(its toggle; next-themes' "system" sets it from the OS) — Ship doesn't also follow the OS, so a
project's own roles and Ship's switch together. **shadcn/ui bridge:** `emit.css.shadcn` adds
`--background`, `--primary`… pointing at the semantic tokens, declared on doubled theme selectors
(`:root:root`, `.dark.dark`) so they outrank the project's own role values wherever the file is
imported and a pinned subtree switches too; roles it doesn't map aren't declared.
The six required roles map by default (text → foreground, surface → card/popover, action →
primary/ring, hairline → border/input, muted → muted-foreground; `outline`, when present, → input);
map the rest in `roles` to your
own semantic keys. Unmapped roles are reported, never invented, and keep the values shadcn
generated. On shadcn projects emit `css` only — shadcn's `@theme inline` already maps the roles.
**Elevation** is web-only for now (CSS `--<prefix>-shadow-*`, Tailwind `shadow-*`); SwiftUI and
Compose use the platform's elevation (materials, `surfaceContainer*`). `box-shadow` disappears in
forced-colors mode — keep a real border where the edge matters.

**Validation:** semantic values resolve · no hex outside primitives · `brand.feel` at most 5 words,
optional (`feel_status` proposed|confirmed) ·
required keys in both modes · type has `body` + one display size · ≥ 1 radius · motion
structure (one spring form per token, 4-number curves, unique names) · known emit targets,
no two targets on one path, nothing emitted to DESIGN.md · no leftover `TODO` · elevation layers
numeric, alpha 0–1 · `theme_selector` valid · shadcn roles name real semantic keys · contrast in
both modes for custom colours (text and muted 4.5:1 on every background and surface key; error
4.5:1; focus, outline and chart marks 3:1; text on the action colour 4.5:1, a warning down to 3:1
for large or bold labels; action, success and warning on every ground: under 3:1 a REQ warning,
under 4.5:1 a check, fine for fills, icons and large text) · warn: unused primitives, hex in
DESIGN.md, motion rules, unmapped shadcn roles, a Tailwind target beside shadcn, a dark surface
no lighter than the dark background, body line height outside 1.3 to 1.6 (or none on the web),
tracked body text, web body under 16 px, any type style under 11.

## `design/components.yaml`

```yaml
schema_version: 1
components:
  - name: StatCard                    # PascalCase, unique
    file: UI/StatCard.swift           # must exist — or `planned: true` (not built yet)
    role: card                        # lowercase dot-path: card, button.primary, list-row
    tokens: [surface, hairline, radius.card, spacing.md, type.caption]   # semantic/scale only
    variants: [content, grouped]      # lowerCamel; must appear in the file (warned)
    api: { label: "metric name", value: "formatted value", style: "content | grouped" }
    use_when: ["a metric with a label", "grouped summary blocks"]
    not_for: ["dense lists — use ListRow"]
    origin: build                     # seed | adopted | build
    extends: SurfaceCard              # optional: another registered component
    doc: One-line usage note.
    added: 2026-09-01
    history:                          # legitimate extensions, dated (see below)
      - { date: 2026-09-23, kind: extension, change: "added variant compact" }
    preview: { swiftui: 'StatCard(label: "Pace", value: "5:12")', html: '<div class="card">…</div>' }
```

Register only reusable primitives (*would a second screen plausibly want it?*). Screen
compositions stay local. `status` lists realized vs planned; realized entries need a real file.

**Suitability, not names.** Before building UI, run `match --role <role> [--variant v]
[--tokens a,b] [--context "…"]`. Verdicts: `reuse` (role + variant + tokens fit) ·
`extend` (right role, missing variant/param on registered tokens) · `planned` (realize it) ·
`founder` (needs tokens that don't exist) · `conflict` (a `not_for` entry matches) ·
`weak` (name only, no role) · miss → classify (primitive → build + register; one-off → local).

**Legitimate extension (no founder question):** adding a variant or parameter that uses only
registered semantic/scale tokens and leaves every existing call site's behaviour and visuals
unchanged. Record it (`extend` prints the lines: variants/tokens + a dated `history` entry).
Changing existing behaviour or visuals, adding tokens, or referencing primitives directly is a
founder decision.

## Generated files

Every generated file carries `ship-generated: ship-design/<version> target=<t> sha256=<hash>`.
Emitters refuse — exit 1, printing the diff — to overwrite a file without that header
(hand-written), a generated file whose body no longer matches its hash (hand-edited), or an
older Ship file without a hash; `--force` replaces after review. `emit … --check` and `check`
never write and exit 1 when anything is missing, stale or edited (usable in review and CI).

## Adopting an existing app

Don't hand-translate. `adopt` scans SwiftUI (`static let` colours incl. light/dark pairs,
`Color(uiColor:)`, HSB/RGB/white, alpha; `Font.custom` / `.system`; CGFloat enums named
Spacing/Radius; `Animation` springs/curves) or web (CSS custom properties incl. dark blocks,
rgb/hsl/oklch, Tailwind v4 `@theme`, v3 config colours) and writes
`design-model.draft.yaml` + `design/components.draft.yaml` (origin: adopted), keeping existing
names via `emit.swiftui.namespaces`/`rename` or `emit.css.prefix`/`rename`. It never touches
`design-model.yaml`. Then: review the notes (`brand.feel` stays empty unless the founder gives
words), rename the drafts, `validate`,
`emit swiftui --out scratch/Theme.swift`, diff against the old theme, replace. `audit` counts
raw spacing/radius/colour/font literals against the scale and finds repeated surface+radius
combinations (use `--model design-model.draft.yaml` before accepting the draft).

## Commands

`validate` · `emit <swiftui|css|tailwind|compose|preview-swiftui|preview-html|all>` (aliases
`emit-swiftui` …; `--out --check --force --dry-run`) · `check` · `status` · `match` · `extend` ·
`adopt` · `audit [--strict]` · `docs [--check]` (design/COMPONENTS.md) · `render [--scheme
both]` (PNG of the SwiftUI preview on macOS) · `emit-designmd` (optional). `--json` where
listed. Exit 0 ok · 1 invalid / stale / refused / miss / founder decision · 2 usage.
