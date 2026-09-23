#!/usr/bin/env python3
"""Ship design registry tool — validate design-model.yaml + design/components.yaml,
emit platform themes from the tokens.

    python3 design_model.py validate      [--root DIR]
    python3 design_model.py emit-swiftui  [--root DIR] [--out PATH]

Deterministic on purpose: the registry check in /ship-build must be a file read,
not inference. Stdlib only (no PyYAML) — parses the YAML subset the schema uses:
block mappings/lists, flow {…} and […], quoted/bare scalars, `>` folded text.
Schema: ../references/design-model-schema.md
"""

import argparse
import re
import sys
from pathlib import Path

REQUIRED_SEMANTIC = ["background", "surface", "text", "muted", "hairline", "action"]
HEX = re.compile(r"^#(?:[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$")


# ── Minimal YAML subset ──────────────────────────────────────────────────────

class YamlError(Exception):
    pass


def strip_comment(line):
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1] in " \t"):
            return line[:i].rstrip()
    return line.rstrip()


def scalar(text):
    t = text.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    if t in ("true", "false"):
        return t == "true"
    if t in ("null", "~", ""):
        return None
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if re.fullmatch(r"-?\d*\.\d+", t):
        return float(t)
    return t


def parse_flow(text):
    pos = 0

    def skip():
        nonlocal pos
        while pos < len(text) and text[pos] in " \t":
            pos += 1

    def value():
        nonlocal pos
        skip()
        if pos < len(text) and text[pos] == "{":
            pos += 1
            out = {}
            skip()
            if text[pos] == "}":
                pos += 1
                return out
            while True:
                skip()
                start = pos
                while text[pos] != ":":
                    pos += 1
                key = str(scalar(text[start:pos]))
                pos += 1
                out[key] = value()
                skip()
                if text[pos] == ",":
                    pos += 1
                    continue
                if text[pos] == "}":
                    pos += 1
                    return out
                raise YamlError(f"expected , or }} in: {text}")
        if pos < len(text) and text[pos] == "[":
            pos += 1
            out = []
            skip()
            if text[pos] == "]":
                pos += 1
                return out
            while True:
                out.append(value())
                skip()
                if text[pos] == ",":
                    pos += 1
                    continue
                if text[pos] == "]":
                    pos += 1
                    return out
                raise YamlError(f"expected , or ] in: {text}")
        start = pos
        quote = text[pos] if pos < len(text) and text[pos] in "\"'" else None
        if quote:
            pos = text.index(quote, pos + 1) + 1
        else:
            while pos < len(text) and text[pos] not in ",}]":
                pos += 1
        return scalar(text[start:pos])

    try:
        result = value()
    except (IndexError, ValueError):
        raise YamlError(f"unbalanced flow value: {text}")
    return result


def inline(text):
    t = text.strip()
    return parse_flow(t) if t[:1] in "{[" else scalar(t)


def load_yaml(src):
    lines = []
    for raw in src.splitlines():
        s = strip_comment(raw)
        if s.strip():
            lines.append((len(s) - len(s.lstrip(" ")), s.strip()))
    value, pos = block(lines, 0, 0)
    if pos != len(lines):
        raise YamlError(f"unexpected indentation near: {lines[pos][1]}")
    return value


def split_key(text):
    m = re.match(r"^([^:\"'{}\[\]]+):(?:\s+(.*))?$", text)
    if not m:
        raise YamlError(f"expected 'key: value', got: {text}")
    return str(scalar(m.group(1))), (m.group(2) or "")


def block(lines, pos, indent):
    if pos < len(lines) and lines[pos][1].startswith("- "):
        return seq(lines, pos, indent)
    out = {}
    while pos < len(lines) and lines[pos][0] == indent and not lines[pos][1].startswith("- "):
        key, rest = split_key(lines[pos][1])
        pos += 1
        if rest in (">", "|"):
            parts = []
            while pos < len(lines) and lines[pos][0] > indent:
                parts.append(lines[pos][1])
                pos += 1
            out[key] = (" " if rest == ">" else "\n").join(parts)
        elif rest:
            out[key] = inline(rest)
        elif pos < len(lines) and lines[pos][0] > indent:
            out[key], pos = block(lines, pos, lines[pos][0])
        elif pos < len(lines) and lines[pos][0] == indent and lines[pos][1].startswith("- "):
            out[key], pos = seq(lines, pos, indent)
        else:
            out[key] = None
    return out, pos


def seq(lines, pos, indent):
    out = []
    while pos < len(lines) and lines[pos][0] == indent and lines[pos][1].startswith("- "):
        item = lines[pos][1][2:].strip()
        if re.match(r"^[^:\"'{}\[\]]+:(\s|$)", item):
            # "- key: v" starts a mapping; its other keys sit at indent + 2
            child = indent + 2
            sub = [(child, item)]
            pos += 1
            while pos < len(lines) and lines[pos][0] >= child:
                sub.append(lines[pos])
                pos += 1
            value, used = block(sub, 0, child)
            if used != len(sub):
                raise YamlError(f"bad list item near: {sub[used][1]}")
            out.append(value)
        else:
            out.append(inline(item))
            pos += 1
    return out, pos


# ── Registry model ───────────────────────────────────────────────────────────

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


def type_styles(prims):
    """Unified view of type tokens: {name: {font, size}}. Supports the simple form
    (family + scale) and the rich form (families + styles with family/weight/size)."""
    t = prims.get("type") or {}
    families = dict(t.get("families") or {})
    if t.get("family"):
        families.setdefault("default", t["family"])
    styles = {}
    for name, size in (t.get("scale") or {}).items():
        styles[name] = {"family": families.get("default"), "font": families.get("default"), "size": size}
    for name, spec in (t.get("styles") or {}).items():
        spec = spec or {}
        family = families.get(spec.get("family", "default"))
        weight = spec.get("weight")
        font = spec.get("font") or (f"{family}-{weight}" if family and weight else family)
        styles[name] = {"family": family, "font": font, "size": spec.get("size")}
    return styles


def resolve_scale(prims, path):
    """Non-color token refs used by components: radius.card, type.body, spacing.md, motion.snappy."""
    parts = str(path).split(".")
    if len(parts) != 2:
        return None
    group, name = parts
    motion = prims.get("motion") or {}
    table = {
        "radius": prims.get("radius", {}),
        "type": type_styles(prims),
        "spacing": {**(prims.get("spacing") or {}), **((prims.get("spacing") or {}).get("scale") or {})},
        "motion": {**(motion.get("springs") or {}), **(motion.get("durations") or {})},
    }.get(group)
    return table.get(name) if isinstance(table, dict) else None


def walk_hex(node, path, found):
    if isinstance(node, dict):
        for k, v in node.items():
            walk_hex(v, f"{path}.{k}" if path else k, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_hex(v, f"{path}[{i}]", found)
    elif isinstance(node, str) and HEX.match(node):
        found.append(path)


def walk_todo(node, path, found):
    if isinstance(node, dict):
        for k, v in node.items():
            walk_todo(v, f"{path}.{k}" if path else k, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_todo(v, f"{path}[{i}]", found)
    elif isinstance(node, str) and node.startswith("TODO"):
        found.append(path)


def load_registry(root):
    model_path = root / "design-model.yaml"
    if not model_path.exists():
        raise YamlError(f"missing {model_path} — run /ship-design to plant the seed")
    model = load_yaml(model_path.read_text(encoding="utf-8"))
    comp_path = root / "design" / "components.yaml"
    comps = load_yaml(comp_path.read_text(encoding="utf-8")) if comp_path.exists() else None
    return model, comps


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
    walk_hex({k: v for k, v in model.items() if k != "primitives"}, "", stray)
    errors += [f"hex value outside primitives: {p}" for p in stray]

    # 3: brand.feel
    feel = (model.get("brand") or {}).get("feel") or []
    if not 3 <= len(feel) <= 5:
        errors.append(f"brand.feel needs 3-5 adjectives (has {len(feel)})")

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
    styles = type_styles(prims)
    if "body" not in styles or len(styles) < 2:
        errors.append("primitives.type needs a `body` style plus at least one display size")
    if not prims.get("radius"):
        errors.append("primitives.radius needs at least one value (control + card recommended)")

    # 5: light-only needs the documented exception
    if "dark" not in modes:
        design_md = root / "DESIGN.md"
        if not design_md.exists() or "dark mode exception" not in design_md.read_text(encoding="utf-8").lower():
            errors.append("modes: [light] needs a 'Dark mode exception' note in DESIGN.md")

    # emit config
    swift = ((model.get("emit") or {}).get("swiftui") or {})
    for old in (swift.get("rename") or {}):
        if old not in layers[0][1]:
            errors.append(f"emit.swiftui.rename: '{old}' is not a semantic token")

    # TODO placeholders left from the template
    todo = []
    walk_todo(model, "", todo)
    errors += [f"unfilled TODO: {p}" for p in todo]

    # 6: unused color primitives (warn)
    for ramp, stops in (prims.get("color") or {}).items():
        for stop in (stops or {}):
            if f"{ramp}.{stop}" not in used:
                warnings.append(f"primitives.color.{ramp}.{stop} is not used by any semantic token")

    # components.yaml
    if comps is not None:
        seen = set()
        semantic_keys = set(layers[0][1])
        for i, c in enumerate((comps or {}).get("components") or []):
            label = c.get("name") or f"components[{i}]"
            if not re.fullmatch(r"[A-Z][A-Za-z0-9]*", str(c.get("name", ""))):
                errors.append(f"{label}: name must be PascalCase")
            if label in seen:
                errors.append(f"{label}: duplicate component name")
            seen.add(label)
            if not c.get("planned") and not (root / str(c.get("file", ""))).exists():
                errors.append(f"{label}: file '{c.get('file')}' not found (or mark planned: true)")
            variants = c.get("variants")
            if variants is not None and (not isinstance(variants, list)
                                         or not all(re.fullmatch(r"[a-z][A-Za-z0-9]*", str(v)) for v in variants)):
                errors.append(f"{label}: variants must be a list of lowerCamel names, e.g. [content, grouped]")
            for tok in c.get("tokens") or []:
                if HEX.match(str(tok)):
                    errors.append(f"{label}: raw hex '{tok}' — reference a semantic token")
                elif tok in semantic_keys or resolve_scale(prims, tok) is not None:
                    continue
                elif resolve_color(prims, tok) is not None:
                    errors.append(f"{label}: '{tok}' is a color primitive — use a semantic token")
                else:
                    errors.append(f"{label}: token '{tok}' not found in design-model.yaml")
    return errors, warnings


# ── SwiftUI emitter ──────────────────────────────────────────────────────────

SYSTEM_FAMILIES = {"system", "sf pro", "sf pro text", "sf pro display", "-apple-system"}
SWIFT_KEYWORDS = {"default", "class", "struct", "enum", "case", "func", "var", "let", "static",
                  "return", "in", "is", "as", "self", "Type", "extension", "protocol", "import",
                  "switch", "where", "while", "for", "repeat", "if", "else", "guard", "do", "try"}
EASING = {"linear": "linear", "easeIn": "easeIn", "easeOut": "easeOut", "easeInOut": "easeInOut"}
DEFAULT_NAMESPACES = {"colors": "Theme.Colors", "typography": "Theme.Typography",
                      "radius": "Theme.Radius", "spacing": "Theme.Spacing", "motion": "Theme.Motion"}


def ident(name):
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", str(name)) if p]
    out = parts[0][:1].lower() + parts[0][1:] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    if out[:1].isdigit():
        out = f"_{out}"
    return f"`{out}`" if out in SWIFT_KEYWORDS else out


def type_ident(name):
    return re.sub(r"[^A-Za-z0-9]", "", str(name)[:1].upper() + str(name)[1:])


def swift_hex(value):
    h = value.lstrip("#").upper()
    return f"0x{h}" if len(h) == 6 else f"0x{h[:6]}, alpha: {int(h[6:], 16) / 255:.4g}"


def num(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def text_style_for(size):
    for limit, style in ((34, ".largeTitle"), (28, ".title"), (22, ".title2"), (20, ".title3"),
                         (17, ".body"), (16, ".callout"), (15, ".subheadline"), (13, ".footnote"),
                         (12, ".caption")):
        if size >= limit:
            return style
    return ".caption2"


class Tree:
    """Nested Swift enums built from dotted namespace paths ('Theme.Colors', 'Brand')."""

    def __init__(self):
        self.children, self.lines = {}, []

    def at(self, path):
        node = self
        for part in path.split("."):
            node = node.children.setdefault(part, Tree())
        return node

    def render(self, name=None, depth=0):
        pad = "    " * depth
        out = [f"{pad}enum {name} {{"] if name else []
        inner = "    " * (depth + 1) if name else pad
        out += [f"{inner}{line}" for line in self.lines]
        for i, (child, node) in enumerate(self.children.items()):
            if out and (self.lines or i):
                out.append("")
            out += node.render(child, depth + 1 if name else depth)
        if name:
            out.append(f"{pad}}}")
        return out


def emit_swiftui(model):
    prims = model["primitives"]
    swift = (model.get("emit") or {}).get("swiftui") or {}
    ns = {**DEFAULT_NAMESPACES, **(swift.get("namespaces") or {})}
    rename = swift.get("rename") or {}
    dynamic = (prims.get("type") or {}).get("dynamic_type", True)
    light = flatten(model.get("semantic"))
    dark = flatten(model.get("semantic_dark")) or light
    tree = Tree()

    def color_expr(path_l, path_d):
        sys_l, sys_d = system_color(path_l), system_color(path_d)
        if sys_l or sys_d:
            return SYSTEM_COLORS[sys_l or sys_d]
        return f"Color(light: {swift_hex(resolve_color(prims, path_l))}, dark: {swift_hex(resolve_color(prims, path_d))})"

    for key, path in light.items():
        *groups, leaf = str(rename.get(key, key)).split(".")
        node = tree.at(".".join([ns["colors"]] + [type_ident(g) for g in groups]))
        node.lines.append(f"static let {ident(leaf)} = {color_expr(path, dark.get(key, path))}")

    typo = tree.at(ns["typography"])
    for key, spec in type_styles(prims).items():
        font, size = spec["font"], spec["size"]
        if str(spec["family"]).lower() in SYSTEM_FAMILIES:
            expr = f".system(size: {num(size)})"
        elif dynamic:
            expr = f".custom(\"{font}\", size: {num(size)}, relativeTo: {text_style_for(size)})"
        else:
            expr = f".custom(\"{font}\", size: {num(size)})"
        typo.lines.append(f"static let {ident(key)}: Font = {expr}")

    radius = tree.at(ns["radius"])
    for key, v in (prims.get("radius") or {}).items():
        radius.lines.append(f"static let {ident(key)}: CGFloat = {num(v)}")

    spacing = prims.get("spacing") or {}
    space = tree.at(ns["spacing"])
    unit = spacing.get("unit", 4)
    space.lines.append(f"static let unit: CGFloat = {num(unit)}")
    for key, v in (spacing.get("scale") or {}).items():
        space.lines.append(f"static let {ident(key)}: CGFloat = {num(v)}")
    space.lines += ["/// n × unit — x(4) == 16 when unit is 4",
                    "static func x(_ n: CGFloat) -> CGFloat { n * unit }"]

    motion = prims.get("motion") or {}
    mo = tree.at(ns["motion"])
    for key, s in (motion.get("springs") or {}).items():
        mo.lines.append(f"static let {ident(key)} = Animation.spring(response: {num(s['response'])}, "
                        f"dampingFraction: {num(s['damping'])})")
    for key, d in (motion.get("durations") or {}).items():
        ms, curve = (d.get("ms"), d.get("curve", "easeInOut")) if isinstance(d, dict) else (d, "easeInOut")
        mo.lines.append(f"static let {ident(key)} = Animation.{EASING.get(curve, 'easeInOut')}(duration: {num(ms / 1000)})")

    brand = (model.get("brand") or {}).get("name", "")
    out = [
        "// Generated by Ship from design-model.yaml — do not edit by hand.",
        "// Change design-model.yaml, then re-emit (the command for this project is in PDC.md).",
        f"// Brand: {brand}",
        "",
        "import SwiftUI",
        "#if canImport(UIKit)",
        "import UIKit",
        "#endif",
        "",
    ]
    for i, (name, node) in enumerate(tree.children.items()):
        if i:
            out.append("")
        out += node.render(name)
    out += [
        "",
        "extension Color {",
        "    /// Light/dark pair that follows the system appearance.",
        "    init(light: UInt32, alpha lightAlpha: Double = 1, dark: UInt32, alpha darkAlpha: Double = 1) {",
        "        #if canImport(UIKit)",
        "        self.init(uiColor: UIColor { traits in",
        "            traits.userInterfaceStyle == .dark",
        "                ? UIColor(rgb: dark, alpha: darkAlpha)",
        "                : UIColor(rgb: light, alpha: lightAlpha)",
        "        })",
        "        #else",
        "        self.init(.sRGB, red: Double((light >> 16) & 0xFF) / 255, green: Double((light >> 8) & 0xFF) / 255,",
        "                  blue: Double(light & 0xFF) / 255, opacity: lightAlpha)",
        "        #endif",
        "    }",
        "}",
        "",
        "#if canImport(UIKit)",
        "private extension UIColor {",
        "    convenience init(rgb: UInt32, alpha: Double) {",
        "        self.init(red: CGFloat((rgb >> 16) & 0xFF) / 255, green: CGFloat((rgb >> 8) & 0xFF) / 255,",
        "                  blue: CGFloat(rgb & 0xFF) / 255, alpha: alpha)",
        "    }",
        "}",
        "#endif",
        "",
    ]
    return "\n".join(out)


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("command", choices=["validate", "emit-swiftui"])
    ap.add_argument("--root", default=".", help="project root (default: cwd)")
    ap.add_argument("--out", help="emit-swiftui output path (default: Theme.swift in root)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    errors, warnings = validate(root)
    for w in warnings:
        print(f"warn: {w}")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        print(f"✗ design registry invalid ({len(errors)} errors)", file=sys.stderr)
        return 1

    if args.command == "validate":
        print("✓ design registry valid")
        return 0

    model, _ = load_registry(root)
    out = Path(args.out) if args.out else root / "Theme.swift"
    if not out.is_absolute():
        out = root / out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(emit_swiftui(model), encoding="utf-8")
    try:
        shown = out.relative_to(root)
    except ValueError:
        shown = out
    print(f"✓ wrote {shown}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
