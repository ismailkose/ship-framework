"""Web emitters: CSS custom properties (tokens.css) and a Tailwind v4 theme that references them.

CSS variables: --<prefix>-<group>-<name>, prefix from emit.css.prefix (default `ds`).
Light values on :root; dark values via prefers-color-scheme AND an explicit override, so a page
can follow the OS or pin a theme: [data-theme] by default, or `.dark`/`.light` classes with
emit.css.theme_selector: class (shadcn's `dark:` variant and next-themes' attribute="class").
emit.css.shadcn adds shadcn/ui's role variables (--background, --primary…) pointing at the
semantic tokens, so both switch with the same selector.
"""

import os
import re
from pathlib import Path

from . import motion
from .registry import (color_value, family_range, emit_config, emit_out, flatten, is_system_family, resolve_color,
                       spacing_scale, system_color, type_styles, weight_number)

num = motion.num


def kebab(name):
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", str(name))
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()


def prefix(model):
    return str(emit_config(model, "css").get("prefix") or "ds").strip("-")


def css_names(model):
    """Variable names for every token (follows emit.css.prefix + emit.css.rename)."""
    p = prefix(model)
    prims = model.get("primitives") or {}
    rename = emit_config(model, "css").get("rename") or {}
    names = {"colors": {}, "palette": {}, "fonts": {}, "type": {}, "radius": {}, "spacing": {},
             "durations": {}, "springs": {}, "shadow": {}}
    for key in flatten(model.get("semantic")):
        names["colors"][key] = f"--{p}-color-{kebab(rename.get(key, key))}"
    for ramp, stops in (prims.get("color") or {}).items():
        for stop in (stops or {}):
            names["palette"][f"{ramp}.{stop}"] = f"--{p}-palette-{kebab(ramp)}-{kebab(stop)}"
    for key in _families(prims):
        names["fonts"][key] = f"--{p}-font-{kebab(key)}"
    for key in type_styles(prims):
        names["type"][key] = f"--{p}-text-{kebab(key)}"
    for key in (prims.get("radius") or {}):
        names["radius"][key] = f"--{p}-radius-{kebab(key)}"
    names["spacing"]["unit"] = f"--{p}-space-unit"
    for key in spacing_scale(prims):
        names["spacing"][key] = f"--{p}-space-{kebab(key)}"
    for d in motion.durations(prims):
        names["durations"][d["name"]] = f"--{p}-duration-{kebab(d['name'])}"
    for s in motion.springs(prims):
        names["springs"][s["name"]] = f"--{p}-spring-{kebab(s['name'])}"
    for level in (prims.get("elevation") or {}):
        names["shadow"][level] = f"--{p}-shadow-{kebab(level)}"
    return names


def shadow_value(layers):
    """Layered box-shadow from registry layers ({x, y, blur, spread, alpha, color: 'r g b'})."""
    parts = []
    for l in layers:
        rgb = l.get("color", "0 0 0")
        parts.append(f"{num(l.get('x', 0))}px {num(l.get('y', 0))}px {num(l.get('blur', 0))}px "
                     f"{num(l.get('spread', 0))}px rgb({rgb} / {num(l.get('alpha', 0.1))})")
    return ", ".join(parts)


def _families(prims):
    t = prims.get("type") or {}
    fam = dict(t.get("families") or {})
    if t.get("family"):
        fam.setdefault("default", t["family"])
    return fam


SYSTEM_STACKS = {
    "rounded": 'ui-rounded, "SF Pro Rounded", system-ui, -apple-system, sans-serif',
    "serif": 'ui-serif, "New York", Georgia, serif',
    "monospaced": 'ui-monospace, "SF Mono", SFMono-Regular, Menlo, Consolas, monospace',
}


def font_stack(family, design=None):
    if is_system_family(family):
        return SYSTEM_STACKS.get(design) or 'system-ui, -apple-system, "SF Pro Text", sans-serif'
    return f'"{family}", system-ui, sans-serif'


def rem(px):
    return f"{float(px) / 16:.5g}rem"


def _semantic_block(model, names, dark, indent="  "):
    prims = model.get("primitives") or {}
    light = flatten(model.get("semantic"))
    values = flatten(model.get("semantic_dark")) if dark else light
    lines = []
    for level, layers in ((prims.get("elevation_dark") or {}) if dark else {}).items():
        lines.append(f"{indent}{names['shadow'][level]}: {shadow_value(layers)};")
    for level, layers in ((prims.get("elevation") or {}) if not dark and prims.get("elevation_dark") else {}).items():
        if level in prims["elevation_dark"]:
            lines.append(f"{indent}{names['shadow'][level]}: {shadow_value(layers)};")
    for key in light:
        path = values.get(key, light[key])
        sys_name = system_color(path)
        if sys_name:
            hexv, note = color_value(prims, path, dark=dark)
            lines.append(f"{indent}{names['colors'][key]}: {hexv}; /* {note} */")
        else:
            ref = str(path).removeprefix("color.")
            lines.append(f"{indent}{names['colors'][key]}: var({names['palette'][ref]});")
    return lines


# shadcn/ui roles (ui.shadcn.com/docs/theming) → Ship semantic keys. Only Ship's six required roles
# have a default; the rest map through emit.css.shadcn.roles or are reported, never invented.
SHADCN_REQUIRED = ["background", "foreground", "card", "card-foreground", "popover", "popover-foreground",
                   "primary", "primary-foreground", "secondary", "secondary-foreground", "muted",
                   "muted-foreground", "accent", "accent-foreground", "destructive", "border", "input", "ring"]
SHADCN_DEFAULT = {"background": "background", "foreground": "text", "card": "surface",
                  "card-foreground": "text", "popover": "surface", "popover-foreground": "text",
                  "primary": "action", "muted": "surface", "muted-foreground": "muted",
                  "border": "hairline", "input": "hairline", "ring": "action"}


def shadcn_config(model):
    cfg = emit_config(model, "css").get("shadcn")
    if not cfg:
        return None
    cfg = cfg if isinstance(cfg, dict) else {}
    roles = dict(SHADCN_DEFAULT)
    known = set(flatten(model.get("semantic")))
    if "outline" in known:   # field borders need 3:1 (WCAG 1.4.11); the divider colour isn't checked
        roles["input"] = "outline"
    roles.update(cfg.get("roles") or {})
    for i in range(1, 6):   # a `chart` group feeds shadcn's chart colours unless mapped by hand
        if f"chart-{i}" not in roles and f"chart.{i}" in known:
            roles[f"chart-{i}"] = f"chart.{i}"
    return {"roles": roles, "radius": cfg.get("radius")}


def shadcn_gaps(model):
    """(unmapped required roles, roles pointing at an unknown semantic key)."""
    cfg = shadcn_config(model)
    if not cfg:
        return [], []
    known = set(flatten(model.get("semantic")))
    unmapped = [r for r in SHADCN_REQUIRED if r not in cfg["roles"]]
    unknown = [f"{r} → {k}" for r, k in cfg["roles"].items() if k not in known]
    return unmapped, unknown


def _shadcn_block(model, names):
    cfg = shadcn_config(model)
    prims = model.get("primitives") or {}
    known = set(flatten(model.get("semantic")))
    # Declared on the theme selectors too: var() resolves where it's declared, so a pinned subtree
    # must re-declare the roles or it would inherit :root's already-resolved values.
    # Doubled selectors (:root:root, .dark.dark) outrank shadcn's own :root/.dark role blocks wherever
    # this file is imported, without editing the project's stylesheet: mapped roles follow the
    # registry; unmapped roles, other variables and scoped overrides (.marketing { --primary }) stay.
    sel = ":root:root"
    if "dark" in (model.get("modes") or ["light", "dark"]):
        cls = emit_config(model, "css").get("theme_selector") == "class"
        sel = (":root:root, .dark.dark, .light.light" if cls else
               ':root:root, [data-theme="dark"][data-theme="dark"], [data-theme="light"][data-theme="light"]')
    L = ["", "/* shadcn/ui roles — derived from the semantic tokens; they switch with the same selector and",
         "   outrank the project's own :root/.dark role values (doubled selectors). Unmapped roles aren't",
         "   declared here, so the project's values stay. Edit design-model.yaml, then re-emit. */", sel + " {"]
    for role in SHADCN_REQUIRED + sorted(set(cfg["roles"]) - set(SHADCN_REQUIRED)):
        key = cfg["roles"].get(role)
        if key in known:
            L.append(f"  --{role}: var({names['colors'][key]});")
    radius_key = cfg["radius"] or ("md" if "md" in (prims.get("radius") or {}) else next(iter(prims.get("radius") or {}), None))
    if radius_key in names["radius"]:
        L.append(f"  --radius: var({names['radius'][radius_key]});")
    unmapped, _ = shadcn_gaps(model)
    if unmapped:
        L.append(f"  /* not mapped (shadcn's generated values still apply): {', '.join(unmapped)} */")
    L.append("}")
    return L


def emit_css(model):
    prims = model.get("primitives") or {}
    names = css_names(model)
    modes = model.get("modes") or ["light", "dark"]
    has_dark = "dark" in modes
    cls = has_dark and emit_config(model, "css").get("theme_selector") == "class"
    # Native controls and scrollbars must follow the same appearance as the tokens: `light dark` lets
    # the browser follow the OS, which is right only when the tokens do too (data-theme mode). In
    # class mode the app's class decides, so the root is light until .dark/.light says otherwise.
    scheme = "light" if (cls or not has_dark) else "light dark"
    L = [":root {", f"  color-scheme: {scheme};", "", "  /* palette (primitives) */"]
    for ramp, stops in (prims.get("color") or {}).items():
        for stop, hexv in (stops or {}).items():
            L.append(f"  {names['palette'][f'{ramp}.{stop}']}: {hexv};")
    L += ["", "  /* semantic colors — light */"]
    L += _semantic_block(model, names, dark=False)
    L += ["", "  /* type */"]
    for key, fam in _families(prims).items():
        L.append(f"  {names['fonts'][key]}: {font_stack(fam, family_range(prims.get('type') or {}, key)[0])};")
    for key, spec in type_styles(prims).items():
        base = names["type"][key]
        fam_var = names["fonts"].get(spec.get("family_key") or "default")
        if fam_var:
            L.append(f"  {base}-family: var({fam_var});")
        L.append(f"  {base}-size: {rem(spec['size'])};")
        L.append(f"  {base}-weight: {weight_number(spec.get('weight')) or 400};")
        if spec.get("line_height") is not None:
            L.append(f"  {base}-line-height: {num(spec['line_height'])};")
        if spec.get("tracking") is not None:
            L.append(f"  {base}-tracking: {num(spec['tracking'])}em;")
    L += ["", "  /* radius */"]
    for key, v in (prims.get("radius") or {}).items():
        L.append(f"  {names['radius'][key]}: {num(v)}px;")
    L += ["", "  /* spacing */", f"  {names['spacing']['unit']}: {num((prims.get('spacing') or {}).get('unit', 4))}px;"]
    for key, v in spacing_scale(prims).items():
        L.append(f"  {names['spacing'][key]}: {num(v)}px;")
    L += ["", "  /* motion */"]
    for d in motion.durations(prims):
        base = names["durations"][d["name"]]
        x1, y1, x2, y2 = (num(v) for v in d["points"])
        ease = "linear" if d["curve"] == "linear" and not d["custom"] else f"cubic-bezier({x1}, {y1}, {x2}, {y2})"
        L.append(f"  {base}: {num(d['ms'])}ms;")
        L.append(f"  {base}-ease: {ease};")
    for s in motion.springs(prims):
        base = names["springs"][s["name"]]
        lin, ms = motion.css_linear(s["response"], s["damping"])
        L.append(f"  /* spring response {s['response']:.3g}s, damping {s['damping']:.3g} — sampled; settles in {ms}ms */")
        L.append(f"  {base}: {lin};")
        L.append(f"  {base}-duration: {ms}ms;")
    st = motion.stagger(prims)
    if st:
        L.append(f"  --{prefix(model)}-stagger: {num(st['ms'])}ms;")
    if prims.get("elevation"):
        L += ["", "  /* elevation — box-shadow is dropped in forced-colors mode: keep a real border on edges that matter */"]
        for level, layers in prims["elevation"].items():
            L.append(f"  {names['shadow'][level]}: {shadow_value(layers)};")
    L.append("}")
    if has_dark:
        dark_sel, light_sel = ('.dark', '.light') if cls else ('[data-theme="dark"]', '[data-theme="light"]')
        if cls:
            # The app's class is the one control (shadcn's `dark:` variant, next-themes — whose
            # "system" setting applies the class from the OS). Following the OS here too would
            # darken Ship's roles while the app's own roles stayed light.
            L += ["", "/* dark — only where the app sets .dark (its toggle; next-themes \"system\" sets it from the OS) */"]
        else:
            L += ["", "/* dark — follows the OS unless a page pins data-theme=\"light\" */",
                  "@media (prefers-color-scheme: dark) {", f"  :root:not({light_sel}) {{"]
            L += _semantic_block(model, names, dark=True, indent="    ")
            L += ["  }", "}"]
        L += ["", "/* explicit overrides — on <html> or any subtree */",
              f"{dark_sel} {{", "  color-scheme: dark;"]
        L += _semantic_block(model, names, dark=True)
        L += ["}", "", f"{light_sel} {{", "  color-scheme: light;"]
        L += _semantic_block(model, names, dark=False)
        L.append("}")
    if shadcn_config(model):
        L += _shadcn_block(model, names)
    return "\n".join(L) + "\n"


def emit_tailwind(model, root=None):
    """Tailwind v4 theme: `@theme inline` maps Tailwind namespaces onto the CSS variables, so
    utilities (bg-surface, rounded-card, p-md, font-display, text-body, ease-fade) resolve to
    whatever the tokens say in the current mode."""
    prims = model.get("primitives") or {}
    names = css_names(model)
    rename = emit_config(model, "tailwind").get("rename") or emit_config(model, "css").get("rename") or {}
    L = []
    if root is not None:
        tw = Path(emit_out(model, "tailwind"))
        css = Path(emit_out(model, "css"))
        rel = os.path.relpath(css, tw.parent)
        L += [f'@import "{rel if rel.startswith(".") else "./" + rel}";', ""]
    L += ["@theme inline {"]
    for key, var in names["colors"].items():
        L.append(f"  --color-{kebab(rename.get(key, key))}: var({var});")
    for key, var in names["fonts"].items():
        L.append(f"  --font-{kebab(key)}: var({var});")
    for key, spec in type_styles(prims).items():
        base = names["type"][key]
        tk = kebab(key)
        L.append(f"  --text-{tk}: var({base}-size);")
        if spec.get("line_height") is not None:
            L.append(f"  --text-{tk}--line-height: var({base}-line-height);")
        L.append(f"  --text-{tk}--font-weight: var({base}-weight);")
        if spec.get("tracking") is not None:
            L.append(f"  --text-{tk}--letter-spacing: var({base}-tracking);")
    for key, var in names["radius"].items():
        L.append(f"  --radius-{kebab(key)}: var({var});")
    L.append(f"  --spacing: var({names['spacing']['unit']});")
    for key, var in names["spacing"].items():
        if key != "unit":
            L.append(f"  --spacing-{kebab(key)}: var({var});")
    for key, var in names["durations"].items():
        L.append(f"  --ease-{kebab(key)}: var({var}-ease);")
    for key, var in names["springs"].items():
        L.append(f"  --ease-{kebab(key)}: var({var});")
    for key, var in names["shadow"].items():
        L.append(f"  --shadow-{kebab(key)}: var({var});")
    L.append("}")
    return "\n".join(L) + "\n"
