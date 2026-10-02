"""Jetpack Compose theme emitter (Theme.kt).

Colors: a data class with light + dark instances and a composable accessor
(`<Name>.colors` follows isSystemInDarkTheme()). Typography: TextStyle values. Shapes and
radii, spacing (Dp), motion (spring / tween AnimationSpec factories).

Apple system colors have no Android equivalent: they're emitted as fixed iOS approximations
with a comment saying so. Custom font families need Android font resources, which Ship can't
see — map them with emit.compose.fonts (family key → Kotlin FontFamily expression); unmapped
families fall back to FontFamily.Default with a comment.
"""

import re

from . import motion
from .registry import (color_value, family_range, emit_config, flatten, is_system_family, resolve_color, spacing_scale,
                       system_color, type_styles, weight_number)

KOTLIN_KEYWORDS = {"as", "break", "class", "continue", "do", "else", "false", "for", "fun", "if", "in",
                   "interface", "is", "null", "object", "package", "return", "super", "this", "throw",
                   "true", "try", "typealias", "typeof", "val", "var", "when", "while", "default"}
num = motion.num


def kident(name, upper=False):
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", str(name)) if p]
    out = "".join(p[:1].upper() + p[1:] for p in parts)
    if not upper:
        out = out[:1].lower() + out[1:]
    if out[:1].isdigit():
        out = f"_{out}"
    return f"`{out}`" if out in KOTLIN_KEYWORDS else out


def fnum(v):
    s = f"{float(v):.6g}"
    return (s if "." in s or "e" in s else s + ".0") + "f"


def argb(hexv):
    h = hexv.lstrip("#").upper()
    rgb, a = h[:6], (h[6:] if len(h) == 8 else "FF")
    return f"Color(0x{a}{rgb})"


def emit_compose(model):
    prims = model.get("primitives") or {}
    cfg = emit_config(model, "compose")
    pkg = cfg.get("package") or "design.theme"
    name = cfg.get("name") or "Theme"
    rename = cfg.get("rename") or {}
    fonts_map = cfg.get("fonts") or {}
    light = flatten(model.get("semantic"))
    dark = flatten(model.get("semantic_dark")) or light

    L = [f"package {pkg}", "",
         "import androidx.compose.animation.core.CubicBezierEasing",
         "import androidx.compose.animation.core.FiniteAnimationSpec",
         "import androidx.compose.animation.core.LinearEasing",
         "import androidx.compose.animation.core.spring",
         "import androidx.compose.animation.core.tween",
         "import androidx.compose.foundation.isSystemInDarkTheme",
         "import androidx.compose.foundation.shape.RoundedCornerShape",
         "import androidx.compose.runtime.Composable",
         "import androidx.compose.runtime.Immutable",
         "import androidx.compose.ui.graphics.Color",
         "import androidx.compose.ui.text.TextStyle",
         "import androidx.compose.ui.text.font.FontFamily",
         "import androidx.compose.ui.text.font.FontWeight",
         "import androidx.compose.ui.unit.Dp",
         "import androidx.compose.ui.unit.dp",
         "import androidx.compose.ui.unit.em",
         "import androidx.compose.ui.unit.sp",
         ""]

    # palette
    L += [f"/** Raw palette (primitives). Use {name}.colors in UI code, not these. */",
          f"object {name}Palette {{"]
    for ramp, stops in (prims.get("color") or {}).items():
        for stop, hexv in (stops or {}).items():
            L.append(f"    val {kident(f'{ramp} {stop}', upper=True)} = {argb(hexv)}")
    L += ["}", ""]

    def prop(key):
        return kident(rename.get(key, key))

    def value(path, is_dark):
        if system_color(path):
            hexv, note = color_value(prims, path, dark=is_dark)
            return f"{argb(hexv)} /* {note} */"
        ramp_stop = str(path).removeprefix("color.").split(".")
        return f"{name}Palette.{kident(' '.join(ramp_stop), upper=True)}"

    L += ["@Immutable", f"data class {name}Colors("]
    L += [f"    val {prop(k)}: Color," for k in light]
    L += [")", ""]
    for label, table, is_dark in (("Light", light, False), ("Dark", dark, True)):
        L.append(f"val {label}{name}Colors = {name}Colors(")
        L += [f"    {prop(k)} = {value(table.get(k, light[k]), is_dark)}," for k in light]
        L += [")", ""]

    # fonts + typography
    t = prims.get("type") or {}
    families = dict(t.get("families") or {})
    if t.get("family"):
        families.setdefault("default", t["family"])
    L.append(f"object {name}Fonts {{")
    for key, fam in families.items():
        design = family_range(t, key)[0]
        if key in fonts_map:
            expr = str(fonts_map[key])
        elif is_system_family(fam) and design in ("serif", "monospaced"):
            expr = "FontFamily.Serif" if design == "serif" else "FontFamily.Monospace"
        elif is_system_family(fam) and design == "rounded":
            expr = "FontFamily.Default // no system rounded face on Android; map one in emit.compose.fonts"
        elif is_system_family(fam):
            expr = "FontFamily.Default"
        else:
            expr = f"FontFamily.Default // \"{fam}\" — map it in emit.compose.fonts once the font resource exists"
        L.append(f"    val {kident(key)}: FontFamily = {expr}")
    L += ["}", "", f"object {name}Typography {{"]
    for key, spec in type_styles(prims).items():
        args = [f"fontFamily = {name}Fonts.{kident(spec.get('family_key') or 'default')}",
                f"fontWeight = FontWeight({weight_number(spec.get('weight')) or 400})",
                f"fontSize = {num(spec['size'])}.sp"]
        if spec.get("line_height") is not None:
            args.append(f"lineHeight = {num(spec['line_height'])}.em")
        if spec.get("tracking") is not None:
            args.append(f"letterSpacing = ({num(spec['tracking'])}).em")
        L.append(f"    val {kident(key)} = TextStyle({', '.join(args)})")
    L += ["}", ""]

    # radius + shapes
    L.append(f"object {name}Radius {{")
    for key, v in (prims.get("radius") or {}).items():
        L.append(f"    val {kident(key)}: Dp = {num(v)}.dp")
    L += ["}", "", f"object {name}Shapes {{"]
    for key in (prims.get("radius") or {}):
        L.append(f"    val {kident(key)} = RoundedCornerShape({name}Radius.{kident(key)})")
    L += ["}", ""]

    # spacing
    sp = prims.get("spacing") or {}
    L += [f"object {name}Spacing {{", f"    val unit: Dp = {num(sp.get('unit', 4))}.dp"]
    for key, v in spacing_scale(prims).items():
        L.append(f"    val {kident(key)}: Dp = {num(v)}.dp")
    L += [f"    /** n × unit — x(4) == {num(4 * sp.get('unit', 4))}.dp */", "    fun x(n: Int): Dp = unit * n", "}", ""]

    # motion
    L.append(f"object {name}Motion {{")
    for s in motion.springs(prims):
        L.append(f"    /** response {s['response']:.3g}s, damping {s['damping']:.3g} (mass 1) */")
        L.append(f"    fun <T> {kident(s['name'])}(): FiniteAnimationSpec<T> = "
                 f"spring(dampingRatio = {fnum(s['damping'])}, stiffness = {fnum(motion.stiffness(s['response']))})")
    for d in motion.durations(prims):
        if d["curve"] == "linear" and not d["custom"]:
            easing = "LinearEasing"
        else:
            easing = "CubicBezierEasing(" + ", ".join(fnum(v) for v in d["points"]) + ")"
        L.append(f"    fun <T> {kident(d['name'])}(): FiniteAnimationSpec<T> = "
                 f"tween(durationMillis = {int(round(d['ms']))}, easing = {easing})")
    st = motion.stagger(prims)
    if st:
        L.append(f"    /** delay between items in a staggered entrance (cap at {st.get('max_items', 'a few')} items) */")
        L.append(f"    const val STAGGER_MILLIS: Int = {int(round(st['ms']))}")
    L += ["}", ""]

    # accessor
    L += [f"/** Token entry point: {name}.colors follows the system appearance. */",
          f"object {name} {{",
          f"    val colors: {name}Colors",
          f"        @Composable get() = if (isSystemInDarkTheme()) Dark{name}Colors else Light{name}Colors",
          f"    val typography = {name}Typography",
          f"    val radius = {name}Radius",
          f"    val shapes = {name}Shapes",
          f"    val spacing = {name}Spacing",
          f"    val motion = {name}Motion",
          "}", ""]
    return "\n".join(L)
