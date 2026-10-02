"""Registry model: load design-model.yaml + design/components.yaml, resolve tokens, validate.

Rules come from ../../references/design-model-schema.md.
"""

import re
from pathlib import Path

from . import motion
from .yamlsub import YamlError, load_yaml

REQUIRED_SEMANTIC = ["background", "surface", "text", "muted", "hairline", "action"]
HEX = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")
ORIGINS = ("seed", "adopted", "build")
HISTORY_KINDS = ("extension", "founder")
ROLE = re.compile(r"^[a-z][a-z0-9-]*(\.[a-z0-9-]+)*$")
COMPONENT_KEYS = {"name", "file", "tokens", "variants", "doc", "rule", "added", "planned", "role",
                  "use_when", "not_for", "api", "origin", "extends", "history", "preview"}
# Where emitted files land unless design-model.yaml says otherwise — never product code.
EMIT_TARGETS = {
    "swiftui": "design/generated/Theme.swift",
    "css": "design/generated/tokens.css",
    "tailwind": "design/generated/tailwind-theme.css",
    "compose": "design/generated/Theme.kt",
    "preview-swiftui": "design/generated/ShipDesignPreview.swift",
    "preview-html": "design/preview/index.html",
}
DOCS_DEFAULT = "design/COMPONENTS.md"
DESIGNMD_DEFAULT = "design/DESIGN.spec.md"

# `system.<name>` semantic values → SwiftUI expression. Lets a project keep Apple's
# adaptive colors (text, separators, status) instead of re-declaring them as hex.
SYSTEM_COLORS = {
    "primary": "Color.primary", "secondary": "Color.secondary",
    "label": "Color(uiColor: .label)", "secondaryLabel": "Color(uiColor: .secondaryLabel)",
    "tertiaryLabel": "Color(uiColor: .tertiaryLabel)", "quaternaryLabel": "Color(uiColor: .quaternaryLabel)",
    "separator": "Color(uiColor: .separator)", "opaqueSeparator": "Color(uiColor: .opaqueSeparator)",
    "systemBackground": "Color(uiColor: .systemBackground)",
    "secondarySystemBackground": "Color(uiColor: .secondarySystemBackground)",
    "systemGroupedBackground": "Color(uiColor: .systemGroupedBackground)",
    "red": "Color.red", "orange": "Color.orange", "yellow": "Color.yellow", "green": "Color.green",
    "mint": "Color.mint", "teal": "Color.teal", "cyan": "Color.cyan", "blue": "Color.blue",
    "indigo": "Color.indigo", "purple": "Color.purple", "pink": "Color.pink", "brown": "Color.brown",
    "gray": "Color.gray",
}

# The same system colors as UIKit values, for pairs whose light and dark sides differ
# (e.g. light system.primary, dark a brand color) — resolved per trait, never collapsed.
SYSTEM_UIKIT = {
    "primary": ".label", "secondary": ".secondaryLabel", "label": ".label",
    "secondaryLabel": ".secondaryLabel", "tertiaryLabel": ".tertiaryLabel",
    "quaternaryLabel": ".quaternaryLabel", "separator": ".separator", "opaqueSeparator": ".opaqueSeparator",
    "systemBackground": ".systemBackground", "secondarySystemBackground": ".secondarySystemBackground",
    "systemGroupedBackground": ".systemGroupedBackground",
    "red": ".systemRed", "orange": ".systemOrange", "yellow": ".systemYellow", "green": ".systemGreen",
    "mint": ".systemMint", "teal": ".systemTeal", "cyan": ".systemCyan", "blue": ".systemBlue",
    "indigo": ".systemIndigo", "purple": ".systemPurple", "pink": ".systemPink", "brown": ".systemBrown",
    "gray": ".systemGray",
}

# macOS side (previews and the PNG renderer run there). Background mappings are the nearest
# AppKit role, not the same color — see the Ship repo's maintainers/audit/design-generators.md.
SYSTEM_APPKIT = {
    "primary": ".labelColor", "secondary": ".secondaryLabelColor", "label": ".labelColor",
    "secondaryLabel": ".secondaryLabelColor", "tertiaryLabel": ".tertiaryLabelColor",
    "quaternaryLabel": ".quaternaryLabelColor", "separator": ".separatorColor", "opaqueSeparator": ".gridColor",
    "systemBackground": ".textBackgroundColor", "secondarySystemBackground": ".controlBackgroundColor",
    "systemGroupedBackground": ".windowBackgroundColor",
    "red": ".systemRed", "orange": ".systemOrange", "yellow": ".systemYellow", "green": ".systemGreen",
    "mint": ".systemMint", "teal": ".systemTeal", "cyan": ".systemCyan", "blue": ".systemBlue",
    "indigo": ".systemIndigo", "purple": ".systemPurple", "pink": ".systemPink", "brown": ".systemBrown",
    "gray": ".systemGray",
}

# Fixed approximations of Apple's adaptive colors for platforms without them (CSS, Compose,
# DESIGN.md export): iOS default appearance, standard contrast, (light, dark) as #RRGGBB[AA].
# They are NOT the same colors — no vibrancy, no increased-contrast variants, no elevation.
APPLE_APPROX = {
    "primary": ("#000000", "#FFFFFF"), "label": ("#000000", "#FFFFFF"),
    "secondary": ("#3C3C4399", "#EBEBF599"), "secondaryLabel": ("#3C3C4399", "#EBEBF599"),
    "tertiaryLabel": ("#3C3C434D", "#EBEBF54D"), "quaternaryLabel": ("#3C3C432E", "#EBEBF529"),
    "separator": ("#3C3C434A", "#54545899"), "opaqueSeparator": ("#C6C6C8", "#38383A"),
    "systemBackground": ("#FFFFFF", "#000000"), "secondarySystemBackground": ("#F2F2F7", "#1C1C1E"),
    "systemGroupedBackground": ("#F2F2F7", "#000000"),
    "red": ("#FF3B30", "#FF453A"), "orange": ("#FF9500", "#FF9F0A"), "yellow": ("#FFCC00", "#FFD60A"),
    "green": ("#34C759", "#30D158"), "mint": ("#00C7BE", "#63E6E2"), "teal": ("#30B0C7", "#40C8E0"),
    "cyan": ("#32ADE6", "#64D2FF"), "blue": ("#007AFF", "#0A84FF"), "indigo": ("#5856D6", "#5E5CE6"),
    "purple": ("#AF52DE", "#BF5AF2"), "pink": ("#FF2D55", "#FF375F"), "brown": ("#A2845E", "#AC8E68"),
    "gray": ("#8E8E93", "#8E8E93"),
}

WEIGHTS = {"thin": 100, "ultralight": 200, "extralight": 200, "light": 300, "regular": 400, "book": 400,
           "normal": 400, "medium": 500, "semibold": 600, "demibold": 600, "bold": 700, "extrabold": 800,
           "heavy": 800, "black": 900}
SYSTEM_FAMILIES = {"system", "sf pro", "sf pro text", "sf pro display", "-apple-system"}
# The system face's own range: a voice without a licensed font. Design on every platform that has it
# (web: ui-rounded / ui-serif / ui-monospace; Android: serif and monospace); width on Apple platforms.
SYSTEM_DESIGNS = ("default", "rounded", "serif", "monospaced")
SYSTEM_WIDTHS = ("standard", "condensed", "compressed", "expanded")


def family_range(t, key):
    """(design, width) chosen for a family key; the simple form's `design`/`width` belong to `default`."""
    design = (t.get("designs") or {}).get(key) or (t.get("design") if key == "default" else None)
    width = (t.get("widths") or {}).get(key) or (t.get("width") if key == "default" else None)
    return design, width


def weight_number(weight):
    if weight is None:
        return None
    if isinstance(weight, (int, float)):
        return int(weight)
    return WEIGHTS.get(re.sub(r"[^a-z]", "", str(weight).lower()))


def flatten(node, prefix=""):
    """Nested semantic groups → {'bubble.fill': 'paper.250', ...}."""
    out = {}
    for k, v in (node or {}).items():
        key = f"{prefix}.{k}" if prefix else str(k)
        if isinstance(v, dict):
            out.update(flatten(v, key))
        else:
            out[key] = v
    return out


def system_color(path):
    parts = str(path).split(".")
    return parts[1] if len(parts) == 2 and parts[0] == "system" else None


def resolve_color(prims, path):
    """`paper.50` or `color.paper.50` → hex, else None."""
    parts = str(path).split(".")
    if parts[0] == "color":
        parts = parts[1:]
    node = prims.get("color", {})
    for p in parts:
        if not isinstance(node, dict) or p not in node:
            return None
        node = node[p]
    return node if isinstance(node, str) else None


def color_value(prims, path, dark=False):
    """Hex for a semantic value on platforms without Apple system colors.
    → (hex, note) — note is set when the value is an approximation."""
    sys_name = system_color(path)
    if sys_name:
        light, darkv = APPLE_APPROX[sys_name]
        return (darkv if dark else light), f"system.{sys_name} ≈ iOS {SYSTEM_UIKIT[sys_name].lstrip('.')} (fixed approximation)"
    return resolve_color(prims, path), None


def type_styles(prims):
    """Unified view of type tokens: {name: {family, font, size, weight, line_height, tracking}}.
    Supports the simple form (family + scale) and the rich form (families + styles)."""
    t = prims.get("type") or {}
    families = dict(t.get("families") or {})
    if t.get("family"):
        families.setdefault("default", t["family"])
    styles = {}
    heights = t.get("line_height") if isinstance(t.get("line_height"), dict) else {}
    for name, size in (t.get("scale") or {}).items():
        design, width = family_range(t, "default")
        styles[name] = {"family_key": "default", "family": families.get("default"),
                        "font": families.get("default"), "size": size, "weight": None,
                        "line_height": heights.get(name), "design": design, "width": width}
    for name, spec in (t.get("styles") or {}).items():
        spec = spec or {}
        key = spec.get("family", "default")
        family = families.get(key)
        weight = spec.get("weight")
        font = spec.get("font") or (f"{family}-{weight}" if family and weight else family)
        design, width = family_range(t, key)
        styles[name] = {"family_key": key, "family": family, "font": font, "size": spec.get("size"),
                        "weight": weight, "line_height": spec.get("line_height"), "tracking": spec.get("tracking"),
                        "design": design, "width": width}
    return styles


def is_system_family(family):
    return str(family).lower() in SYSTEM_FAMILIES


def spacing_scale(prims):
    spacing = prims.get("spacing") or {}
    return {k: v for k, v in (spacing.get("scale") or {}).items()}


def resolve_scale(prims, path):
    """Non-color token refs used by components: radius.card, type.body, spacing.md, motion.snappy."""
    parts = str(path).split(".")
    if len(parts) != 2:
        return None
    group, name = parts
    m = prims.get("motion") or {}
    table = {
        "radius": prims.get("radius", {}),
        "type": type_styles(prims),
        "spacing": {**{k: v for k, v in (prims.get("spacing") or {}).items() if k != "scale"}, **spacing_scale(prims)},
        "motion": {**(m.get("springs") or {}), **(m.get("durations") or {})},
        "elevation": prims.get("elevation") or {},
    }.get(group)
    return table.get(name) if isinstance(table, dict) else None


def walk(node, path, pred, found):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, f"{path}.{k}" if path else k, pred, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", pred, found)
    elif pred(node):
        found.append(path)


def load_registry(root):
    model_path = root / "design-model.yaml"
    if not model_path.exists():
        raise YamlError(f"missing {model_path} — run /shipmate design to plant the seed "
                        f"(or `design_model.py adopt` for an existing app)")
    model = load_yaml(model_path.read_text(encoding="utf-8"))
    comp_path = root / "design" / "components.yaml"
    comps = load_yaml(comp_path.read_text(encoding="utf-8")) if comp_path.exists() else None
    return model, comps


def components(comps):
    return [c for c in ((comps or {}).get("components") or []) if isinstance(c, dict)]


def emit_config(model, target):
    """emit.<target> mapping (target keys use _ in YAML: preview_swiftui)."""
    return ((model.get("emit") or {}).get(target.replace("-", "_")) or {})


def emit_out(model, target):
    return emit_config(model, target).get("out") or EMIT_TARGETS[target]


def semantic_keys(model):
    return set(flatten(model.get("semantic")))


def token_known(model, tok):
    prims = model.get("primitives") or {}
    return tok in semantic_keys(model) or resolve_scale(prims, tok) is not None


def as_list(v):
    if v is None:
        return []
    return v if isinstance(v, list) else [v]


# ── Variant presence (best effort, per platform) ─────────────────────────────

def variant_in_source(variant, text, suffix):
    v = re.escape(variant)
    if suffix == ".swift":
        pats = [rf"\bcase\s+(?:[A-Za-z_]\w*\s*,\s*)*{v}\b", rf"\bstatic\s+(?:let|var|func)\s+{v}\b"]
    elif suffix in (".css", ".scss", ".less"):
        pats = [rf"\.{v}\b", rf"--{v}\b", rf"\[data-variant=[\"']?{v}"]
    elif suffix in (".kt", ".kts"):
        pats = [rf"\b{v}\b", rf"\b{variant[:1].upper() + variant[1:]}\b", rf"\b{variant.upper()}\b"]
    else:  # tsx / jsx / ts / js / vue / svelte / html
        pats = [rf"[\"'`]{v}[\"'`]", rf"\b{v}\s*:", rf"\.{v}\b"]
    return any(re.search(p, text) for p in pats)


def variant_warnings(root, comps):
    out = []
    for c in components(comps):
        if c.get("planned") or not c.get("variants") or not c.get("file"):
            continue
        path = root / str(c["file"])
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for v in c.get("variants") or []:
            if not variant_in_source(str(v), text, path.suffix.lower()):
                out.append(f"{c.get('name')}: variant '{v}' is listed in components.yaml but not found in {c['file']} "
                           f"(looked for an enum case / static member / CSS class / prop value)")
    return out


# Colour pairs people read, and the contrast each needs (WCAG 2.2 AA).
CONTRAST_PAIRS = [("text", "background", 4.5, "text"), ("text", "surface", 4.5, "text"),
                  ("muted", "background", 4.5, "text"), ("muted", "surface", 4.5, "text"),
                  # shadcn's muted background (adopt names it muted-surface) carries muted text too
                  ("text", "muted-surface", 4.5, "text"), ("muted", "muted-surface", 4.5, "text"),
                  ("on_action", "action", 4.5, "text on the action colour"),
                  ("error", "background", 4.5, "error text"), ("error", "surface", 4.5, "error text"),
                  ("focus", "background", 3.0, "a focus ring"), ("focus", "surface", 3.0, "a focus ring"),
                  # a control's border (field outlines, checkboxes): the optional `outline` role
                  ("outline", "background", 3.0, "a control's border"), ("outline", "surface", 3.0, "a control's border")]
# Colours used as text and as fills or icons: under 3:1 fails either way; under 4.5:1 they're fine as
# fills, icons and large text, not as text in a sentence (Practical UI; WCAG 1.4.3, 1.4.11).
DUAL_USE = [("action", "the action colour (links, selected states)"), ("success", "success text and icons"),
            ("warning", "warning text and icons")]
SURFACE_KEY = re.compile(r"^(background|surface)([.\-_][\w-]+|\d+)?$")


def _channels(hexv):
    h = hexv.lstrip("#")
    return [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], (int(h[6:8], 16) / 255 if len(h) == 8 else 1.0)


def _luminance(c):
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(fg, bg):
    """WCAG contrast ratio; a see-through foreground is composited over the background first."""
    (f, alpha), (b, _) = _channels(fg), _channels(bg)
    f = [alpha * x + (1 - alpha) * y for x, y in zip(f, b)]
    hi, lo = sorted([_luminance(f), _luminance(b)], reverse=True)
    return (hi + 0.05) / (lo + 0.05)


# ── Validation ───────────────────────────────────────────────────────────────

def validate(root):
    """Returns (errors, warnings). Rules from design-model-schema.md."""
    errors, warnings = [], []
    try:
        model, comps = load_registry(root)
    except YamlError as exc:
        return [str(exc)], []
    if not isinstance(model, dict):
        return ["design-model.yaml must be a mapping"], []

    prims = model.get("primitives") or {}
    modes = model.get("modes") or ["light", "dark"]
    layers = [("semantic", flatten(model.get("semantic")))]
    if "dark" in modes:
        layers.append(("semantic_dark", flatten(model.get("semantic_dark"))))

    # 1 + 4: required keys; every value resolves to a color primitive or a system color
    used = set()
    for name, layer in layers:
        for key in REQUIRED_SEMANTIC:
            if key not in layer:
                errors.append(f"{name}.{key} is required")
        for key, path in layer.items():
            sys_name = system_color(path)
            if sys_name is not None:
                if sys_name not in SYSTEM_COLORS:
                    errors.append(f"{name}.{key} → unknown system color '{sys_name}' "
                                  f"(known: {', '.join(sorted(SYSTEM_COLORS))})")
            elif resolve_color(prims, path) is None:
                errors.append(f"{name}.{key} → '{path}' does not resolve to a color in primitives")
            else:
                used.add(str(path).removeprefix("color."))
    if "dark" in modes:
        light_keys, dark_keys = set(layers[0][1]), set(layers[1][1])
        for key in sorted((light_keys ^ dark_keys) - set(REQUIRED_SEMANTIC)):
            errors.append(f"semantic key '{key}' must exist in both semantic and semantic_dark")

    # 2: hex only under primitives
    stray = []
    walk({k: v for k, v in model.items() if k != "primitives"}, "",
         lambda n: isinstance(n, str) and bool(HEX.match(n)), stray)
    errors += [f"hex value outside primitives: {p}" for p in stray]

    # 3: brand.feel — optional: the founder's own words (1-5), never invented to pass validation.
    # The yardstick is DESIGN.md › Point of view; feel_status says whether the words are theirs.
    brand = model.get("brand") or {}
    feel = brand.get("feel") or []
    if not isinstance(feel, list) or len(feel) > 5:
        errors.append(f"brand.feel: a list of at most 5 words (has {feel if not isinstance(feel, list) else len(feel)})")
    status = brand.get("feel_status")
    if status is not None and status not in ("proposed", "confirmed"):
        errors.append(f"brand.feel_status: proposed or confirmed (has {status!r})")

    # required scales
    type_ = prims.get("type") or {}
    families = type_.get("families") or {}
    if not type_.get("family") and not families:
        errors.append("primitives.type needs `family` (or `families` for a multi-font system)")
    for name, spec in (type_.get("styles") or {}).items():
        fam = (spec or {}).get("family", "default")
        if not (spec or {}).get("font") and fam not in families and not (fam == "default" and type_.get("family")):
            errors.append(f"primitives.type.styles.{name}: family '{fam}' is not in type.families")
        if not isinstance((spec or {}).get("size"), (int, float)):
            errors.append(f"primitives.type.styles.{name}: size is required")
        w = (spec or {}).get("weight")
        if w is not None and weight_number(w) is None:
            warnings.append(f"primitives.type.styles.{name}: weight '{w}' has no numeric mapping "
                            f"(CSS/Compose fall back to 400)")
    all_families = dict(families)
    if type_.get("family"):
        all_families.setdefault("default", type_.get("family"))
    for field, allowed, many in (("design", SYSTEM_DESIGNS, "designs"), ("width", SYSTEM_WIDTHS, "widths")):
        chosen = dict(type_.get(many) or {})
        if type_.get(field) is not None:
            chosen.setdefault("default", type_.get(field))
        for key, value in chosen.items():
            where = f"primitives.type.{many}.{key}" if key in (type_.get(many) or {}) else f"primitives.type.{field}"
            if key not in all_families:
                errors.append(f"{where}: no family '{key}' in type.families")
            elif not is_system_family(all_families[key]):
                errors.append(f"{where}: only the system family has a {field} range "
                              f"('{all_families[key]}' carries its own)")
            if value not in allowed:
                errors.append(f"{where}: one of {', '.join(allowed)} (has {value!r})")
    styles = type_styles(prims)
    if "body" not in styles or len(styles) < 2:
        errors.append("primitives.type needs a `body` style plus at least one display size")
    heights = type_.get("line_height")
    if heights is not None and not isinstance(heights, dict):
        errors.append("primitives.type.line_height: a mapping of scale names to numbers (body: 1.5)")
    for k, v in (heights.items() if isinstance(heights, dict) else []):
        if k not in (type_.get("scale") or {}):
            errors.append(f"primitives.type.line_height.{k}: no '{k}' in type.scale")
        elif not isinstance(v, (int, float)) or isinstance(v, bool) or not 1 <= v <= 2.5:
            errors.append(f"primitives.type.line_height.{k}: a number from 1 to 2.5 (has {v!r})")
    # Reading comfort (Butterick, Practical UI; typography.md §2–3): checks, never errors.
    emit_cfg = model.get("emit") or {}
    web = bool(emit_cfg.get("css") or emit_cfg.get("tailwind")) or (root / "package.json").exists()
    body = styles.get("body") or {}
    blh = body.get("line_height")
    if isinstance(blh, (int, float)) and not isinstance(blh, bool) and not 1.3 <= blh <= 1.6:
        warnings.append(f"check: body line height {blh:g}; reading text reads best at 1.4 to 1.6 (typography.md §3)")
    elif blh is None and web:
        warnings.append("check: body has no line height, so the web falls back to about 1.2; set "
                        "primitives.type.line_height.body: 1.5 (typography.md §3)")
    if body.get("tracking") not in (None, 0):
        warnings.append("check: body text is tracked; tracking is for caps labels and large display text, "
                        "and system fonts track themselves (typography.md §3)")
    bsize = body.get("size")
    if web and isinstance(bsize, (int, float)) and bsize < 16:
        warnings.append(f"check: body is {bsize:g} px on the web; 16 or more reads better, and fields under 16 px "
                        "make iOS Safari zoom in (typography.md §2)")
    for name, spec in styles.items():
        if isinstance(spec.get("size"), (int, float)) and spec["size"] < 11:
            warnings.append(f"check: type style {name} is {spec['size']:g}; nothing under 11 stays readable (typography.md §2)")
    if not prims.get("radius"):
        errors.append("primitives.radius needs at least one value (control + card recommended)")

    # elevation (optional): named levels of shadow layers; web emits --<prefix>-shadow-<level>
    for key in ("elevation", "elevation_dark"):
        for level, layers in (prims.get(key) or {}).items():
            if not isinstance(layers, list) or not layers:
                errors.append(f"primitives.{key}.{level} must be a list of shadow layers")
                continue
            for i, layer in enumerate(layers):
                if not isinstance(layer, dict) or not all(isinstance(layer.get(k, 0), (int, float))
                                                          for k in ("x", "y", "blur", "spread", "alpha")):
                    errors.append(f"primitives.{key}.{level}[{i}]: x/y/blur/spread/alpha must be numbers")
                elif not 0 <= float(layer.get("alpha", 0.1)) <= 1:
                    errors.append(f"primitives.{key}.{level}[{i}]: alpha must be 0–1")
    for level in (prims.get("elevation_dark") or {}):
        if level not in (prims.get("elevation") or {}):
            errors.append(f"primitives.elevation_dark.{level} has no light level to override")
    css = (model.get("emit") or {}).get("css") or {}
    if css.get("theme_selector") not in (None, "data-theme", "class"):
        errors.append("emit.css.theme_selector must be data-theme (default) or class")
    if css.get("shadcn"):
        from . import emit_web
        unmapped, unknown = emit_web.shadcn_gaps(model)
        for u in unknown:
            errors.append(f"emit.css.shadcn.roles: {u} is not a semantic key")
        if unmapped:
            warnings.append("emit.css.shadcn: roles without a Ship token keep shadcn's generated values: "
                            + ", ".join(unmapped) + " — add semantic keys and map them in emit.css.shadcn.roles")
        if ((model.get("emit") or {}).get("tailwind") or {}).get("out"):
            warnings.append("emit.tailwind with emit.css.shadcn: shadcn's own `@theme inline` already maps the roles; "
                            "Ship's Tailwind file would redefine --color-*/--radius-* — emit css only on shadcn projects")

    # motion: structure blocks; the rules table only warns
    errors += motion.validate_motion(prims)
    if not any(e.startswith("motion.") for e in errors):
        warnings += motion.lint(prims)

    # 5: light-only needs the documented exception
    design_md = root / "DESIGN.md"
    prose = design_md.read_text(encoding="utf-8") if design_md.exists() else ""
    if "dark" not in modes and "dark mode exception" not in prose.lower():
        errors.append("modes: [light] needs a 'Dark mode exception' note in DESIGN.md")
    # ownership: token values live in design-model.yaml, not in the prose
    hexes = sorted(set(re.findall(r"#[0-9A-Fa-f]{6}\b", prose)))
    if hexes:
        warnings.append(f"DESIGN.md contains {len(hexes)} hex value(s) ({', '.join(hexes[:4])}{'…' if len(hexes) > 4 else ''}) "
                        f"— values belong in design-model.yaml; the prose should name tokens")

    # emit config
    emit = model.get("emit") or {}
    known_targets = {t.replace("-", "_") for t in EMIT_TARGETS} | {"designmd", "docs"}
    for tgt in emit:
        if tgt not in known_targets:
            errors.append(f"emit.{tgt}: unknown target (known: {', '.join(sorted(known_targets))})")
    for tgt, cfg in emit.items():
        for old in ((cfg or {}).get("rename") or {}):
            if old not in layers[0][1]:
                errors.append(f"emit.{tgt}.rename: '{old}' is not a semantic token")
        out = (cfg or {}).get("out")
        if out and Path(str(out)).name == "DESIGN.md":
            errors.append(f"emit.{tgt}.out: DESIGN.md is the prose file — generated output can't go there")
    outs = {}
    for tgt in EMIT_TARGETS:
        o = emit_out(model, tgt)
        if o in outs:
            errors.append(f"emit: {tgt} and {outs[o]} both write {o}")
        outs[o] = tgt

    # 7: contrast of the colour pairs people read (WCAG 2.2: 1.4.3 text, 1.4.11 focus and chart marks).
    # Custom colours only: a system colour adapts and Increase Contrast raises it, so it's Apple's to keep.
    # Warnings marked REQ, never errors: a new seed fixes them; an adopted app's are the founder's call,
    # and emit keeps working meanwhile.
    colour_layers = [("semantic", flatten(model.get("semantic")))]
    if "dark" in modes:
        colour_layers.append(("semantic_dark", flatten(model.get("semantic_dark"))))
    for name, layer in colour_layers:
        grounds = [k for k in sorted(layer) if SURFACE_KEY.match(k)]
        extra = [k for k in grounds if k not in ("background", "surface", "muted-surface")]
        pairs = list(CONTRAST_PAIRS) + [(k, bg, 3.0, "chart marks") for k in sorted(layer)
                                        if k.startswith("chart.") for bg in ("background", "surface")]
        pairs += [(fg, g, 4.5, "text") for g in extra for fg in ("text", "muted")]
        for fg, what in DUAL_USE:
            for g in grounds:
                if fg not in layer or system_color(layer[fg]) or system_color(layer[g]):
                    continue
                hf, hb = resolve_color(prims, layer[fg]), resolve_color(prims, layer[g])
                if not (hf and hb and HEX.match(hf) and HEX.match(hb)) or len(hb) == 9:
                    continue
                r = contrast(hf, hb)
                if r < 3.0:
                    warnings.append(f"REQ: {name}.{fg} on {g}: {r:.2f}:1 for {what}, under 3:1 as text, icons or "
                                    f"a selected state (WCAG 1.4.3, 1.4.11); pick a stop further from {layer[g]}")
                elif r < 4.5:
                    warnings.append(f"check: {name}.{fg} on {g}: {r:.2f}:1, fine for fills, icons and large text; "
                                    f"as text in a sentence (a link, a message) it needs 4.5:1 (WCAG 1.4.3)")
        if name == "semantic_dark" and all(k in layer and not system_color(layer[k]) for k in ("background", "surface")):
            hb, hs = resolve_color(prims, layer["background"]), resolve_color(prims, layer["surface"])
            if hb and hs and HEX.match(hb) and HEX.match(hs) and len(hb) == 7 and len(hs) == 7 \
                    and _luminance(_channels(hs)[0]) <= _luminance(_channels(hb)[0]):
                warnings.append("check: semantic_dark.surface isn't lighter than semantic_dark.background; in dark "
                                "mode, raised surfaces get lighter (dark-mode.md §2)")
        for fg, bg, need, what in pairs:
            if fg not in layer or bg not in layer or system_color(layer[fg]) or system_color(layer[bg]):
                continue
            hf, hb = resolve_color(prims, layer[fg]), resolve_color(prims, layer[bg])
            if not (hf and hb and HEX.match(hf) and HEX.match(hb)) or len(hb) == 9:
                continue      # unfilled, or a see-through background whose backdrop isn't known
            r = contrast(hf, hb)
            msg = (f"{name}.{fg} on {bg}: {r:.2f}:1, needs {need:g}:1 for {what} "
                   f"({'WCAG 1.4.3' if need > 3 else 'WCAG 1.4.11'}); pick a stop further from {layer[bg]}")
            if r >= need:
                continue
            if fg == "on_action" and r >= 3.0:
                warnings.append("check: " + msg.replace("; pick", ", fine only for large or bold labels (18 pt, or 14 pt bold); pick"))
            else:
                warnings.append("REQ: " + msg)

    # TODO placeholders left from the template
    todo = []
    walk(model, "", lambda n: isinstance(n, str) and n.startswith("TODO"), todo)
    errors += [f"unfilled TODO: {p}" for p in todo]

    # 6: unused color primitives (warn)
    for ramp, stops in (prims.get("color") or {}).items():
        for stop in (stops or {}):
            if f"{ramp}.{stop}" not in used:
                warnings.append(f"primitives.color.{ramp}.{stop} is not used by any semantic token")

    if comps is not None:
        e, w = validate_components(root, model, comps)
        errors += e
        warnings += w
    return errors, warnings


def validate_components(root, model, comps):
    errors, warnings = [], []
    prims = model.get("primitives") or {}
    sem = semantic_keys(model)
    entries = components(comps)
    names = {str(c.get("name")) for c in entries}
    seen = set()
    for i, c in enumerate(entries):
        label = c.get("name") or f"components[{i}]"
        if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", str(c.get("name", ""))):
            errors.append(f"{label}: name must be PascalCase")
        if label in seen:
            errors.append(f"{label}: duplicate component name")
        seen.add(label)
        if not c.get("planned"):
            src = str(c.get("file") or "").strip()
            if not src:
                errors.append(f"{label}: needs `file:` (the component's source) — or `planned: true` if it isn't built yet")
            elif not (root / src).is_file():
                errors.append(f"{label}: file '{src}' not found or not a file (or mark planned: true)")
        variants = c.get("variants")
        if variants is not None and (not isinstance(variants, list)
                                     or not all(re.fullmatch(r"[a-z][A-Za-z0-9]*", str(v)) for v in variants)):
            errors.append(f"{label}: variants must be a list of lowerCamel names, e.g. [content, grouped]")
        for tok in c.get("tokens") or []:
            if HEX.match(str(tok)):
                errors.append(f"{label}: raw hex '{tok}' — reference a semantic token")
            elif tok in sem or resolve_scale(prims, tok) is not None:
                continue
            elif resolve_color(prims, tok) is not None:
                errors.append(f"{label}: '{tok}' is a color primitive — use a semantic token")
            else:
                errors.append(f"{label}: token '{tok}' not found in design-model.yaml")
        role = c.get("role")
        if role is not None and not ROLE.match(str(role)):
            errors.append(f"{label}: role '{role}' — lowercase, dot-separated (card, button.primary, list-row)")
        if role is None:
            warnings.append(f"{label}: no `role` — the build loop can only match it by name (add role: card / button.primary / …)")
        origin = c.get("origin")
        if origin is not None and origin not in ORIGINS:
            errors.append(f"{label}: origin '{origin}' — use one of {', '.join(ORIGINS)}")
        ext = c.get("extends")
        if ext is not None and str(ext) not in names:
            errors.append(f"{label}: extends '{ext}', which is not a registered component")
        if ext is not None and str(ext) == str(c.get("name")):
            errors.append(f"{label}: can't extend itself")
        for key in ("use_when", "not_for"):
            v = c.get(key)
            if v is not None and not (isinstance(v, str) or (isinstance(v, list) and all(isinstance(x, str) for x in v))):
                errors.append(f"{label}: {key} must be a sentence or a list of sentences")
        api = c.get("api")
        if api is not None and not isinstance(api, (dict, list)):
            errors.append(f"{label}: api must map each public parameter to a short description")
        added = c.get("added")
        if added is not None and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(added)):
            warnings.append(f"{label}: added '{added}' is not YYYY-MM-DD")
        for j, h in enumerate(c.get("history") or []):
            if not isinstance(h, dict) or not h.get("date") or not h.get("change"):
                errors.append(f"{label}: history[{j}] needs date + change")
            elif h.get("kind", "extension") not in HISTORY_KINDS:
                errors.append(f"{label}: history[{j}].kind must be extension or founder")
        prev = c.get("preview")
        if prev is not None and not isinstance(prev, dict):
            errors.append(f"{label}: preview must map a platform to a snippet, e.g. {{ swiftui: 'Card {{ Text(\"Hi\") }}' }}")
        extra = set(c) - COMPONENT_KEYS
        if extra:
            warnings.append(f"{label}: unknown key(s) {', '.join(sorted(extra))}")
    warnings += variant_warnings(root, comps)
    return errors, warnings
