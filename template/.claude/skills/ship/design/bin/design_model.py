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


def resolve_scale(prims, path):
    """Non-color token refs used by components: radius.card, type.body, spacing.unit, motion.snappy."""
    parts = str(path).split(".")
    if len(parts) != 2:
        return None
    group, name = parts
    table = {
        "radius": prims.get("radius", {}),
        "type": (prims.get("type") or {}).get("scale", {}),
        "spacing": prims.get("spacing", {}),
        "motion": (prims.get("motion") or {}).get("springs", {}),
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
    layers = [("semantic", model.get("semantic") or {})]
    if "dark" in modes:
        layers.append(("semantic_dark", model.get("semantic_dark") or {}))

    # 1 + 4: required keys, every semantic value resolves to a color primitive
    used = set()
    for name, layer in layers:
        for key in REQUIRED_SEMANTIC:
            if key not in layer:
                errors.append(f"{name}.{key} is required")
        for key, path in layer.items():
            if resolve_color(prims, path) is None:
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
    if not type_.get("family"):
        errors.append("primitives.type.family is required")
    scale = type_.get("scale") or {}
    if "body" not in scale or len(scale) < 2:
        errors.append("primitives.type.scale needs `body` plus at least one display size")
    for key in ("control", "card"):
        if key not in (prims.get("radius") or {}):
            errors.append(f"primitives.radius.{key} is required")

    # 5: light-only needs the documented exception
    if "dark" not in modes:
        design_md = root / "DESIGN.md"
        if not design_md.exists() or "dark mode exception" not in design_md.read_text(encoding="utf-8").lower():
            errors.append("modes: [light] needs a 'Dark mode exception' note in DESIGN.md")

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


def walk_todo(node, path, found):
    if isinstance(node, dict):
        for k, v in node.items():
            walk_todo(v, f"{path}.{k}" if path else k, found)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk_todo(v, f"{path}[{i}]", found)
    elif node == "TODO" or (isinstance(node, str) and node.startswith("TODO")):
        found.append(path)


# ── SwiftUI emitter ──────────────────────────────────────────────────────────

SWIFT_TEXT_STYLE = {
    "caption": ".caption", "footnote": ".footnote", "subheadline": ".subheadline",
    "body": ".body", "callout": ".callout", "headline": ".headline",
    "title": ".title2", "title2": ".title2", "title3": ".title3",
    "display": ".largeTitle", "largeTitle": ".largeTitle",
}
SYSTEM_FAMILIES = {"system", "sf pro", "sf pro text", "sf pro display", "-apple-system"}


def ident(name):
    parts = re.split(r"[^A-Za-z0-9]+", str(name))
    out = parts[0][:1].lower() + parts[0][1:] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    return out if out and not out[0].isdigit() else f"_{out}"


def swift_hex(value):
    h = value.lstrip("#")
    return f"0x{h.upper()}" if len(h) == 6 else f"0x{h[:6].upper()}, alpha: {int(h[6:], 16) / 255:.3f}"


def num(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def emit_swiftui(model):
    prims = model["primitives"]
    light = model.get("semantic") or {}
    dark = model.get("semantic_dark") or light
    family = str(prims["type"]["family"])
    brand = (model.get("brand") or {}).get("name", "")

    out = [
        "// Generated by Ship from design-model.yaml — do not edit by hand.",
        "// Regenerate: python3 .claude/skills/ship/design/bin/design_model.py emit-swiftui",
        f"// Brand: {brand}",
        "",
        "import SwiftUI",
        "#if canImport(UIKit)",
        "import UIKit",
        "#endif",
        "",
        "enum Theme {",
        "    enum Colors {",
    ]
    for key in light:
        l_hex, d_hex = resolve_color(prims, light[key]), resolve_color(prims, dark.get(key, light[key]))
        out.append(f"        static let {ident(key)} = Color(light: {swift_hex(l_hex)}, dark: {swift_hex(d_hex)})")
    out += ["    }", "", "    enum Radius {"]
    for key, v in (prims.get("radius") or {}).items():
        out.append(f"        static let {ident(key)}: CGFloat = {num(v)}")
    unit = (prims.get("spacing") or {}).get("unit", 4)
    out += [
        "    }",
        "",
        "    enum Spacing {",
        f"        static let unit: CGFloat = {num(unit)}",
        "        /// n × unit — Spacing.x(4) == 16 when unit is 4",
        "        static func x(_ n: CGFloat) -> CGFloat { n * unit }",
        "    }",
        "",
        "    enum Typography {",
    ]
    system = family.lower() in SYSTEM_FAMILIES
    for key, size in (prims["type"].get("scale") or {}).items():
        style = SWIFT_TEXT_STYLE.get(key, ".body")
        font = (f".system(size: {num(size)})" if system
                else f".custom(\"{family}\", size: {num(size)}, relativeTo: {style})")
        out.append(f"        static let {ident(key)}: Font = {font}")
    out += ["    }", "", "    enum Motion {"]
    motion = prims.get("motion") or {}
    for key, s in (motion.get("springs") or {}).items():
        out.append(f"        static let {ident(key)} = Animation.spring(response: {num(s['response'])}, "
                   f"dampingFraction: {num(s['damping'])})")
    for key, ms in (motion.get("durations") or {}).items():
        out.append(f"        static let {ident(key)} = Animation.easeInOut(duration: {num(ms / 1000)})")
    out += [
        "    }",
        "}",
        "",
        "extension Color {",
        "    /// Light/dark pair that follows the system appearance.",
        "    init(light: UInt32, dark: UInt32) {",
        "        #if canImport(UIKit)",
        "        self.init(uiColor: UIColor { traits in",
        "            UIColor(rgb: traits.userInterfaceStyle == .dark ? dark : light)",
        "        })",
        "        #else",
        "        self.init(rgb: light)",
        "        #endif",
        "    }",
        "",
        "    init(rgb: UInt32, alpha: Double = 1) {",
        "        self.init(.sRGB, red: Double((rgb >> 16) & 0xFF) / 255, green: Double((rgb >> 8) & 0xFF) / 255,",
        "                  blue: Double(rgb & 0xFF) / 255, opacity: alpha)",
        "    }",
        "}",
        "",
        "#if canImport(UIKit)",
        "private extension UIColor {",
        "    convenience init(rgb: UInt32) {",
        "        self.init(red: CGFloat((rgb >> 16) & 0xFF) / 255, green: CGFloat((rgb >> 8) & 0xFF) / 255,",
        "                  blue: CGFloat(rgb & 0xFF) / 255, alpha: 1)",
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
    print(f"✓ wrote {out.relative_to(root) if out.is_relative_to(root) else out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
