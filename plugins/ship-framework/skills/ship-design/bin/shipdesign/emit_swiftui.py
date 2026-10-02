"""SwiftUI theme emitter (Theme.swift) + the accessor map the preview uses."""

import re

from . import motion
from .registry import (SYSTEM_APPKIT, SYSTEM_COLORS, SYSTEM_UIKIT, flatten, is_system_family,
                       resolve_color, system_color, type_styles)

SWIFT_KEYWORDS = {"default", "class", "struct", "enum", "case", "func", "var", "let", "static",
                  "return", "in", "is", "as", "self", "Type", "extension", "protocol", "import",
                  "switch", "where", "while", "for", "repeat", "if", "else", "guard", "do", "try"}
EASING = {"linear": "linear", "easeIn": "easeIn", "easeOut": "easeOut", "easeInOut": "easeInOut"}
DEFAULT_NAMESPACES = {"colors": "Theme.Colors", "typography": "Theme.Typography",
                      "radius": "Theme.Radius", "spacing": "Theme.Spacing", "motion": "Theme.Motion"}
SWIFT_WEIGHTS = {"thin": ".thin", "ultralight": ".ultraLight", "extralight": ".ultraLight", "light": ".light",
                 "regular": ".regular", "medium": ".medium", "semibold": ".semibold", "demibold": ".semibold",
                 "bold": ".bold", "heavy": ".heavy", "extrabold": ".heavy", "black": ".black"}
num = motion.num


def ident(name):
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", str(name)) if p]
    out = parts[0][:1].lower() + parts[0][1:] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    if out[:1].isdigit():
        out = f"_{out}"
    return f"`{out}`" if out in SWIFT_KEYWORDS else out


def bare(name):
    return ident(name).strip("`")


def type_ident(name):
    return re.sub(r"[^A-Za-z0-9]", "", str(name)[:1].upper() + str(name)[1:])


def swift_hex(value):
    h = value.lstrip("#").upper()
    return f"0x{h}" if len(h) == 6 else f"0x{h[:6]}, alpha: {int(h[6:], 16) / 255:.4g}"


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
        out += [f"{inner}{line}" if not line.startswith("#") else line for line in self.lines]
        for i, (child, node) in enumerate(self.children.items()):
            if out and (self.lines or i):
                out.append("")
            out += node.render(child, depth + 1 if name else depth)
        if name:
            out.append(f"{pad}}}")
        return out


def namespaces(model):
    swift = (model.get("emit") or {}).get("swiftui") or {}
    return {**DEFAULT_NAMESPACES, **(swift.get("namespaces") or {})}


def accessors(model):
    """Swift expressions for every token — {'colors': {semantic key: expr}, 'type': …, …}.
    The preview and audit use this so they follow namespaces + rename exactly."""
    prims = model.get("primitives") or {}
    swift = (model.get("emit") or {}).get("swiftui") or {}
    ns = namespaces(model)
    rename = swift.get("rename") or {}
    out = {"colors": {}, "type": {}, "radius": {}, "spacing": {}, "motion": {}}
    for key in flatten(model.get("semantic")):
        *groups, leaf = str(rename.get(key, key)).split(".")
        out["colors"][key] = ".".join([ns["colors"]] + [type_ident(g) for g in groups] + [bare(leaf)])
    for key in type_styles(prims):
        out["type"][key] = f"{ns['typography']}.{bare(key)}"
    for key in (prims.get("radius") or {}):
        out["radius"][key] = f"{ns['radius']}.{bare(key)}"
    out["spacing"]["unit"] = f"{ns['spacing']}.unit"
    for key in ((prims.get("spacing") or {}).get("scale") or {}):
        out["spacing"][key] = f"{ns['spacing']}.{bare(key)}"
    m = prims.get("motion") or {}
    for key in list((m.get("springs") or {})) + list((m.get("durations") or {})):
        out["motion"][key] = f"{ns['motion']}.{bare(key)}"
    return out


# Apple's default point sizes for each Dynamic Type text style (large content size category).
TEXT_STYLE_SIZES = {34: ".largeTitle", 28: ".title", 22: ".title2", 20: ".title3", 17: ".body",
                    16: ".callout", 15: ".subheadline", 13: ".footnote", 12: ".caption", 11: ".caption2"}


def font_expr(spec, dynamic, system_text_styles=False):
    size = spec["size"]
    if is_system_family(spec["family"]):
        w = SWIFT_WEIGHTS.get(re.sub(r"[^a-z]", "", str(spec.get("weight") or "").lower()))
        design = spec.get("design") if spec.get("design") not in (None, "default") else None
        width = f".width(.{spec['width']})" if spec.get("width") not in (None, "standard") else ""
        style = TEXT_STYLE_SIZES.get(size) if (dynamic and system_text_styles) else None
        if style:  # scales with Dynamic Type (opt-in: type.system_text_styles — adopted apps keep their sizes)
            args = [style] + ([f"design: .{design}"] if design else []) + ([f"weight: {w}"] if w else [])
            return f".system({', '.join(args)}){width}"
        args = [f"size: {num(size)}"] + ([f"weight: {w}"] if w else []) + ([f"design: .{design}"] if design else [])
        return f".system({', '.join(args)}){width}"
    if dynamic:
        return f".custom(\"{spec['font']}\", size: {num(size)}, relativeTo: {text_style_for(size)})"
    return f".custom(\"{spec['font']}\", size: {num(size)})"


def animation_expr(item, kind):
    if kind == "spring":
        if item["form"] == "bounce":
            return f"Animation.spring(duration: {num(item['raw']['duration'])}, bounce: {num(item['raw'].get('bounce', 0))})"
        return (f"Animation.spring(response: {num(item['raw']['response'])}, "
                f"dampingFraction: {num(item['raw']['damping'])})")
    secs = num(item["ms"] / 1000)
    if item["curve"] is None or item.get("custom"):
        x1, y1, x2, y2 = (num(v) for v in item["points"])
        return f"Animation.timingCurve({x1}, {y1}, {x2}, {y2}, duration: {secs})"
    return f"Animation.{EASING.get(item['curve'], 'easeInOut')}(duration: {secs})"


def emit_swiftui(model):
    """→ body text (no generated header; the caller adds it)."""
    prims = model["primitives"]
    dynamic = (prims.get("type") or {}).get("dynamic_type", True)
    light = flatten(model.get("semantic"))
    dark = flatten(model.get("semantic_dark")) or light
    acc = accessors(model)
    ns = namespaces(model)
    tree = Tree()

    def rgb_parts(path):
        h = resolve_color(prims, path).lstrip("#")
        return h[:6].upper(), (int(h[6:], 16) / 255 if len(h) == 8 else 1)

    def uikit_expr(path):
        sys_name = system_color(path)
        if sys_name:
            return SYSTEM_UIKIT[sys_name]
        h, a = rgb_parts(path)
        return f"UIColor(rgb: 0x{h}, alpha: {a:.4g})"

    def appkit_expr(path):
        sys_name = system_color(path)
        if sys_name:
            return SYSTEM_APPKIT[sys_name]
        h, a = rgb_parts(path)
        return f"NSColor(rgb: 0x{h}, alpha: {a:.4g})"

    def color_lines(name, path_l, path_d):
        sys_l, sys_d = system_color(path_l), system_color(path_d)
        if not sys_l and not sys_d:
            return [f"static let {name} = Color(light: {swift_hex(resolve_color(prims, path_l))}, "
                    f"dark: {swift_hex(resolve_color(prims, path_d))})"]
        if sys_l and sys_l == sys_d:
            expr = SYSTEM_COLORS[sys_l]
            if not expr.startswith("Color(uiColor:"):
                return [f"static let {name} = {expr}"]
            return ["#if canImport(UIKit)",
                    f"static let {name} = {expr}",
                    "#elseif canImport(AppKit)",
                    f"static let {name} = Color(nsColor: {SYSTEM_APPKIT[sys_l]})",
                    "#endif"]
        # Mixed or differing system values: resolve per appearance so neither side is lost.
        return ["#if canImport(UIKit)",
                f"static let {name} = Color(uiColor: UIColor {{ $0.userInterfaceStyle == .dark ? "
                f"{uikit_expr(path_d)} : {uikit_expr(path_l)} }})",
                "#elseif canImport(AppKit)",
                f"static let {name} = Color(nsColor: NSColor(name: nil) {{ $0.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua ? "
                f"{appkit_expr(path_d)} : {appkit_expr(path_l)} }})",
                "#endif"]

    for key, path in light.items():
        expr = acc["colors"][key]
        *parents, leaf = expr.split(".")
        node = tree.at(".".join(parents))
        node.lines += color_lines(ident(leaf), path, dark.get(key, path))

    typo = tree.at(ns["typography"])
    for key, spec in type_styles(prims).items():
        typo.lines.append(f"static let {ident(key)}: Font = "
                          f"{font_expr(spec, dynamic, bool((prims.get('type') or {}).get('system_text_styles')))}")

    radius = tree.at(ns["radius"])
    for key, v in (prims.get("radius") or {}).items():
        radius.lines.append(f"static let {ident(key)}: CGFloat = {num(v)}")

    spacing = prims.get("spacing") or {}
    space = tree.at(ns["spacing"])
    unit = spacing.get("unit", 4)
    space.lines.append(f"static let unit: CGFloat = {num(unit)}")
    for key, v in (spacing.get("scale") or {}).items():
        space.lines.append(f"static let {ident(key)}: CGFloat = {num(v)}")
    space.lines += [f"/// n × unit — x(4) == {num(4 * unit)}",
                    "static func x(_ n: CGFloat) -> CGFloat { n * unit }"]

    mo = tree.at(ns["motion"])
    for s in motion.springs(prims):
        mo.lines.append(f"static let {ident(s['name'])} = {animation_expr(s, 'spring')}")
    for d in motion.durations(prims):
        mo.lines.append(f"static let {ident(d['name'])} = {animation_expr(d, 'duration')}")
    st = motion.stagger(prims)
    if st:
        mo.lines.append(f"/// Delay between items in a staggered entrance (cap at {st.get('max_items', 'a few')} items)")
        mo.lines.append(f"static let stagger: Double = {num(st['ms'] / 1000)}")

    out = [
        "import SwiftUI",
        "#if canImport(UIKit)",
        "import UIKit",
        "#elseif canImport(AppKit)",
        "import AppKit",
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
        "        #elseif canImport(AppKit)",
        "        self.init(nsColor: NSColor(name: nil) { appearance in",
        "            appearance.bestMatch(from: [.darkAqua, .aqua]) == .darkAqua",
        "                ? NSColor(rgb: dark, alpha: darkAlpha)",
        "                : NSColor(rgb: light, alpha: lightAlpha)",
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
        "#elseif canImport(AppKit)",
        "private extension NSColor {",
        "    convenience init(rgb: UInt32, alpha: Double) {",
        "        self.init(srgbRed: CGFloat((rgb >> 16) & 0xFF) / 255, green: CGFloat((rgb >> 8) & 0xFF) / 255,",
        "                  blue: CGFloat(rgb & 0xFF) / 255, alpha: alpha)",
        "    }",
        "}",
        "#endif",
        "",
    ]
    return "\n".join(out)
