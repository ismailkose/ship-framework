"""Optional interop: export the registry as a Google DESIGN.md (spec version "alpha") file.

Off by default and never written to DESIGN.md (that is the product's prose). Default path:
design/DESIGN.spec.md. Ship token names are kept (kebab-cased, the spec's convention);
dark values become `<name>-dark` tokens; Apple system colors are exported as labelled fixed
approximations. Spec: github.com/google-labs-code/design.md docs/spec.md.
"""

from . import motion
from .emit_web import kebab
from .registry import (as_list, color_value, components, flatten, is_system_family, resolve_scale,
                       semantic_keys, spacing_scale, system_color, type_styles, weight_number)
from .yamlsub import dump_yaml

num = motion.num


def emit_designmd(model, comps):
    """→ body WITHOUT the opening `---` (the caller writes it before the generated header)."""
    prims = model.get("primitives") or {}
    brand = model.get("brand") or {}
    light = flatten(model.get("semantic"))
    dark = flatten(model.get("semantic_dark"))
    modes = model.get("modes") or ["light", "dark"]
    approx = []
    colors = {}
    for key, path in light.items():
        hexv, note = color_value(prims, path)
        colors[kebab(key)] = hexv
        if note:
            approx.append(f"`{kebab(key)}`: {note}")
        if "dark" in modes and key in dark:
            dhex, dnote = color_value(prims, dark[key], dark=True)
            if dhex != hexv:
                colors[f"{kebab(key)}-dark"] = dhex
                if dnote:
                    approx.append(f"`{kebab(key)}-dark`: {dnote}")
    if "primary" not in colors and "action" in colors:
        # the spec requires a `primary` colour; Ship's is `action` — exported under both names
        colors = {"primary": colors["action"], **colors}
        approx.append("`primary`: alias of Ship's `action` (the format requires a primary colour)")
    typography = {}
    for key, spec in type_styles(prims).items():
        fam = spec.get("family") or ""
        entry = {"fontFamily": "SF Pro" if is_system_family(fam) else fam, "fontSize": f"{num(spec['size'])}px",
                 "fontWeight": weight_number(spec.get("weight")) or 400}
        if spec.get("line_height") is not None:
            entry["lineHeight"] = spec["line_height"]
        if spec.get("tracking") is not None:
            entry["letterSpacing"] = f"{num(spec['tracking'])}em"
        typography[kebab(key)] = entry
    rounded = {kebab(k): f"{num(v)}px" for k, v in (prims.get("radius") or {}).items()}
    sp = prims.get("spacing") or {}
    spacing = {"unit": f"{num(sp.get('unit', 4))}px"}
    spacing.update({kebab(k): f"{num(v)}px" for k, v in spacing_scale(prims).items()})
    comp_tokens = {}
    sem = semantic_keys(model)
    for c in components(comps):
        props = {}
        for tok in as_list(c.get("tokens")):
            if tok in sem:
                k = kebab(tok)
                if any(w in tok.lower() for w in ("hairline", "border", "separator", "divider", "scrim", "stroke")):
                    continue  # no border property in the spec's component tokens
                prop = "textColor" if any(w in tok.lower() for w in ("text", "label", "muted", "ink")) else "backgroundColor"
                props.setdefault(prop, f"{{colors.{k}}}")
            elif str(tok).startswith("radius.") and resolve_scale(prims, tok) is not None:
                props.setdefault("rounded", f"{{rounded.{kebab(tok.split('.', 1)[1])}}}")
            elif str(tok).startswith("type.") and resolve_scale(prims, tok) is not None:
                props.setdefault("typography", f"{{typography.{kebab(tok.split('.', 1)[1])}}}")
        if props:
            comp_tokens[kebab(c.get("name"))] = props
    front = {"version": "alpha", "name": brand.get("name", ""),
             "description": ", ".join(str(f) for f in brand.get("feel") or []),
             "colors": colors, "typography": typography, "rounded": rounded, "spacing": spacing}
    if comp_tokens:
        front["components"] = comp_tokens
    body = [dump_yaml(front), "---", "",
            f"# {brand.get('name', '')}", "",
            "## Overview", "",
            "Exported from Ship's design registry for tools that read the DESIGN.md format. "
            "The source of truth is `design-model.yaml` (tokens), `design/components.yaml` (components) "
            "and the prose in `DESIGN.md` — edit those, then re-export.", "",
            f"Feel: {', '.join(str(f) for f in brand.get('feel') or [])}.", "",
            "## Colors", "",
            "Token names are Ship's semantic roles. Dark-mode values are exported as `<name>-dark` "
            "tokens because the format has no appearance modes."]
    if approx:
        body += ["", "Aliases and approximations (Apple adaptive colors have no fixed value; these are the "
                 "iOS default-appearance values):", ""] + [f"- {a}" for a in approx]
    body += ["", "## Components", "",
             "Component property mapping is heuristic (semantic text roles → textColor, other colors → "
             "backgroundColor). See design/COMPONENTS.md for the real component library.", ""]
    return "\n".join(body)
