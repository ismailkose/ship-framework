<!-- ship-reference
id: components-shadcn
kind: mixed
sources: shadcn-ui (call: its CLI and docs; shadcn-ui/ui@98a1fe6, MIT — skills/shadcn, apps docs cli.mdx + theming.mdx, packages/shadcn add/init source) — https://ui.shadcn.com/docs/cli, /docs/theming, /docs/tailwind-v4, /docs/forms, /docs/mcp, /docs/skills, /docs/changelog (all checked 2026-09-23; the August 2026 private GitHub registries entry and components-json registries, 2026-09-28); https://base-ui.com (2026-09-23); https://react-spectrum.adobe.com/react-aria/ (2026-09-23); https://tailwindcss.com/docs/theme (2026-09-23)
reviewed: 2026-09-23
-->

# shadcn/ui on web stacks — Ship's rules on top of the upstream

Labels: REQ / PLATFORM / EXPERT / SHIP (see `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/accessibility.md`).
**Call, don't mirror.** shadcn/ui changes monthly; Ship doesn't copy its catalog or source. For
component APIs, install commands and examples, run shadcn's own CLI, which a shadcn project
already has; nothing else to install:

| Need | Use |
|---|---|
| Browse or search a registry | `npx shadcn@latest search <registry>` · `npx shadcn@latest view <item>` |
| Docs for one component, for this project's base | `npx shadcn@latest docs <component>` · preview against *this* project: `npx shadcn@latest add <item> --dry-run` (`--view <file>` shows the incoming file) |
| What's installed / project config | `npx shadcn@latest info` |

Ship's job here: the **decisions** — which base, how tokens flow from the registry, where
customisations live, what review checks. Registry rules from `components.md` apply unchanged.
The official skill runs `npx shadcn@latest info --json` each time it loads and pre-approves
`npx shadcn@latest *` (including `add --overwrite` and `apply`); under Ship, overwrites and theme
changes still follow §2 — theme and color edits go through `/shipmate design --tokens`.

---

## 1. Current state (verified 2026-09-23 — re-check the changelog when it matters)

- **CLI:** `npx shadcn@latest init` (or `create`) with `--template` (next, vite, start,
  react-router, laravel, astro), `--base base|radix|aria` (Base UI, Radix, or React Aria as the
  Layer-1 primitives) and `--preset` (`--defaults` = the `nova` preset; `new-york` is the legacy
  fallback); `add` (`--overwrite`, `--all`, `--dry-run`, `--diff [file]`, `--view [file]`), `search`/`list`, `view`,
  `docs`, `info`, `apply` (`--only theme|font`), `migrate` (e.g. `cn`, `icons`, `radix`, `rtl`),
  `build` (publish your own registry).
- **Tailwind v4 + React 19:** CSS-first config — theme variables exposed with `@theme inline`,
  dark mode via `@custom-variant dark`; colors in **OKLCH**; components are plain functions
  (no `forwardRef`) with `data-slot` attributes for styling; `tw-animate-css` replaced
  `tailwindcss-animate`. **Toasts depend on the base** — read `base` in `components.json`
  (or `info`): Base UI → the `toast` component (`toast.add(...)`); Radix and React Aria → `sonner`.
- **Theme roles:** `background/foreground`, `card`, `popover`, `primary`, `secondary`, `muted`,
  `accent`, `destructive`, `border`, `input`, `ring`, `chart-1…5`, `sidebar-*`, and a
  `--radius` scale.
- **Forms:** the `Field` family (`Field`, `FieldLabel`, `FieldDescription`, `FieldError`,
  `FieldGroup`) with React Hook Form, TanStack Form and others; older projects may still use the
  `Form`/`FormField` wrapper — follow what the project has.
- **Class merging:** `cn()` now ships as its own `cn` package (`npx shadcn@latest migrate cn`
  moves an existing project).
- **Registries:** namespaced registries install with `add @<namespace>/<item>`; GitHub repositories
  (private ones too, through the GitHub CLI or `GH_TOKEN`) with `add <owner>/<repo>/<item>`. A team
  design system can be a registry.

## 2. Ship decisions

| Decision | Ship default | Why / override |
|---|---|---|
| Primitive base | **Base UI** for new projects (`--base base`); keep Radix in projects that already use it; React Aria when the product needs its i18n/date/drag-and-drop depth | Maintained headless primitives with full a11y; never mix two bases (inconsistent focus/keyboard behaviour) |
| Token source | `design-model.yaml` → emitted CSS variables mapped onto shadcn's role names | Registry wins over the preset/theme the CLI generated |
| Presets / themes | A starting point during `/shipmate design` only; the chosen values move into `design-model.yaml` | Themes applied later with `apply` would silently redesign — that's a registry change, not a CLI run |
| Where changes go | Visual variants (new size, new tone) → edit `components/ui/*` via its variant definition; behaviour (loading, confirm, analytics) → a wrapper in `components/` | `add --overwrite` replaces `components/ui/*`; wrappers survive upgrades |
| Upgrades | `add <x> --dry-run`, then `--diff components/ui/<x>.tsx` for each file: it compares the incoming registry version with your file, **committed customisations included**. No local difference → `--overwrite`; a difference → merge by hand; overwrite custom code only with the founder's OK; run tests. Offline: diff against the file's first commit, `git diff $(git log --diff-filter=A --format=%H -- <file> \| tail -1) -- <file>` — shows what changed since it was added, but that commit may already hold edits: it never authorises an overwrite on its own | `git diff <file>` shows only *uncommitted* edits — a clean tree can still hold shipped customisations, and `--overwrite` would erase them |
| Registering | Each styled component the product reuses gets a `design/components.yaml` entry (`file`, semantic `tokens`, `variants`) | The build loop checks the registry, not the `ui/` folder |

**Token mapping** — the generator writes the bridge; never hand-edit the result. In
`design-model.yaml`: `emit.css: { out: <globals dir>/tokens.css, theme_selector: class, shadcn: {…} }`,
then `design_model.py emit css`, and add `@import "./tokens.css";` at the top of the global
stylesheet. **Adopting an existing project changes nothing else in it:**
- *Mapped roles follow the registry* — the bridge declares them on doubled selectors
  (`:root:root`, `.dark.dark`), so they outrank the project's own `:root`/`.dark` values wherever
  the import sits. To hand a role back to the project, remove it from the mapping.
- *Everything else stays* — unmapped roles (`secondary`, `sidebar-*`…), other variables,
  shadcn's `@theme inline` block and scoped overrides (`.marketing { --primary: … }`) keep working.
- *Charts use the product's colours:* a `chart` group in `semantic` (1 to 5, both modes) maps to
  `--chart-1…5` on its own, and `validate` checks each against background and surface (3:1). Without
  one, charts keep shadcn's stock palette: add the group when the product first shows a chart.
- *One appearance control* — `theme_selector: class` when the app sets `.dark` (shadcn's `dark:`
  variant, next-themes `attribute="class"`, whose "system" setting applies the class from the OS);
  in class mode Ship doesn't also follow the OS, so both halves of the theme switch together.
  Keep the default `data-theme` only if the app's toggle and `@custom-variant dark` use it.
- Emit `css` only on shadcn projects (Ship's Tailwind file would redefine the same `--color-*`).
  Unmapped required roles are listed by `validate`; map them to semantic keys (`on_action`,
  `danger`) in `emit.css.shadcn.roles`. Tested: `scripts/checks/web-behaviour.sh` compiles a
  complete shadcn stylesheet with Tailwind v4 and checks both modes, a nested `.dark`, and a token change.
Contract: `${CLAUDE_PLUGIN_ROOT}/skills/ship-design/references/design-model-schema.md`.

## 3. Build road signs (Dev)

- Before building UI on a shadcn project: `components.json` exists? If not and the stack says
  shadcn, run `init` with the decided base first.
- Check the registry (`design/components.yaml`) → then installed `components/ui/*` → then
  `npx shadcn@latest search <thing>` → only then compose something new.
- Use role utilities (`bg-primary`, `text-muted-foreground`, `border-border`) — never
  arbitrary color values (`bg-[#…]`) or raw palette classes (`bg-blue-500`) in product code.
- Use `cn()` for every conditional or incoming `className`.
- Dialogs for destructive confirmation use `AlertDialog`; menus, popovers, selects come from the
  base primitives — never hand-rolled focus traps.
- Toasts from the base's component — Base UI `toast`, Radix/Aria `sonner` (§1); follow the toast
  rules in `${CLAUDE_PLUGIN_ROOT}/skills/ship-ux/references/forms-feedback.md` §4 (actions persist, messages announced).

## 4. Review checklist (Eye, Pol, Test)

- [ ] One primitive base across the project; `components.json` matches it.
- [ ] Every color/radius class resolves to a role that traces to `design-model.yaml`; dark roles defined.
- [ ] `dark:` utilities and the role tokens switch from the same toggle (`theme_selector` matches the app).
- [ ] An upgraded `components/ui/*` file was diffed against the incoming version, not just `git diff`.
- [ ] No arbitrary values or raw palette classes in product components.
- [ ] Behaviour customisations live in wrappers, not in `components/ui/*`.
- [ ] Reused components are registered in `design/components.yaml` with their variants.
- [ ] Forms use the project's field components with visible labels, descriptions and linked errors.
- [ ] Focus rings visible on every interactive component in both modes (REQ 2.4.7 / 1.4.11).
- [ ] Destructive confirmations use `AlertDialog`; toasts follow the persistence rules.
