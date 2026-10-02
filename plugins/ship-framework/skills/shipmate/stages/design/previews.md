## Previews (`--preview`, `--motion-tune`) · part of the design stage, read for `--preview`, `--motion-tune` or `split`

Previews are generated from the registry — never hand-built or hand-edited:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py emit preview-html       # design/preview/index.html (or emit.preview_html.out)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py emit preview-swiftui    # Xcode canvas preview (iOS)
python3 ${CLAUDE_PLUGIN_ROOT}/skills/ship-design/bin/design_model.py render --scheme both    # PNGs of the SwiftUI preview
```

They show colours (light and dark side by side), type, radius, spacing, motion demos (Reduce
Motion respected), every registered component with its status, and a sample screen. Want
something different in a preview? Change the registry (e.g. a component's `preview:` snippet),
then re-emit. Android: a `@Preview` composable using the emitted `Theme.kt`.

`--motion-tune`: an HTML page with a card per motion token and sliders for its parameters
(`response`/`damping` or `duration`/`bounce`, `ms` + curve), replaying live, with reset per token.
The page can't write files: it shows the changed tokens as YAML for the founder to approve. You
apply them to `design-model.yaml › primitives.motion` (the source of truth — not DESIGN.md or
`design/motion.md`), `validate`, `emit all`, and record the
decision in taste. CSS approximates springs; the native preview (`emit preview-swiftui`) plays the
real `Animation.spring(response:dampingFraction:)`.

## split <section>

`design split motion`: move DESIGN.md's `## Motion` section (to the next heading of the same
or higher level) into `design/motion.md`, leave `## Motion` + `See [motion.md](design/motion.md)`
in its place, and point PDC.md's `motion:` at `design/motion.md`.
