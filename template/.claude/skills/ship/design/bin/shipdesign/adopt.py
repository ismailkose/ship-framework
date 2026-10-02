"""Adopt an existing app's design system: scan code → DRAFT design-model + components inventory.

Never touches design-model.yaml or design/components.yaml; writes design-model.draft.yaml and
design/components.draft.yaml. The draft keeps the app's existing token names and API:
SwiftUI via emit.swiftui.namespaces + rename, web via emit.css.prefix + rename (Tailwind
utility names follow the semantic names). Whatever can't be expressed is listed as a note,
never guessed.
"""

import math
import os
import re
from datetime import date
from pathlib import Path

from .generated import MARK
from .registry import REQUIRED_SEMANTIC, SYSTEM_UIKIT, WEIGHTS

SKIP_DIRS = {".git", "node_modules", "build", "DerivedData", "Pods", ".build", "dist", ".next", ".swiftpm",
             "Carthage", "vendor", ".turbo", "coverage", "out", ".claude", ".ship"}
COMPONENT_DIRS = re.compile(r"(^|/)(components?|ui|designsystem|design-system|design_system|shared|common|primitives)(/|$)", re.I)
ROLE_HINTS = {
    "background": ["background", "bg", "canvas", "appbackground", "base"],
    "surface": ["surface", "card", "cardbackground", "elevated", "panel"],
    "text": ["text", "textprimary", "primarytext", "foreground", "fg", "ink", "label"],
    "muted": ["muted", "textsecondary", "secondarytext", "subtle", "subtext", "secondary", "mutedforeground"],
    "hairline": ["hairline", "separator", "divider", "border", "stroke", "line", "outline"],
    "action": ["action", "accent", "primary", "tint", "brand", "cta"],
}
COMPONENT_ROLES = [("TextField", "input"), ("Button", "button"), ("Card", "card"), ("Row", "list-row"),
                   ("Cell", "list-row"), ("Badge", "badge"), ("Chip", "chip"), ("Tag", "chip"), ("Pill", "chip"),
                   ("Field", "input"), ("Input", "input"), ("Toggle", "toggle"), ("Switch", "toggle"),
                   ("Header", "header"), ("Bubble", "bubble"), ("Avatar", "avatar"), ("Sheet", "sheet"),
                   ("Banner", "banner"), ("Toast", "toast"), ("Divider", "divider"), ("Chart", "chart"),
                   ("EmptyState", "empty-state"), ("Section", "section"), ("Tab", "tab"), ("Menu", "menu"),
                   ("Dialog", "dialog"), ("Modal", "dialog"), ("Icon", "icon"), ("Label", "label")]


def walk_files(root, exts, exclude=()):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for f in filenames:
            p = Path(dirpath) / f
            if p.suffix.lower() in exts:
                rel = p.relative_to(root).as_posix()
                if any(Path(rel).match(g) for g in exclude):
                    continue
                yield p, rel


def is_generated(text):
    return MARK in text[:2000]


def lower_first(s):
    return s[:1].lower() + s[1:]


def slug(s):
    parts = [p for p in re.split(r"[^A-Za-z0-9]+", str(s)) if p]
    if not parts:
        return "palette"
    out = parts[0][:1].lower() + parts[0][1:] + "".join(p[:1].upper() + p[1:] for p in parts[1:])
    return out if not out[:1].isdigit() else f"n{out}"


# ── Colour values ────────────────────────────────────────────────────────────

def to_hex(r, g, b, a=1.0):
    clamp = lambda x: max(0, min(255, int(round(x))))
    h = f"#{clamp(r):02X}{clamp(g):02X}{clamp(b):02X}"
    return h if a >= 0.9995 else h + f"{clamp(a * 255):02X}"


def with_alpha(hexv, alpha):
    h = hexv.lstrip("#")
    base = int(h[6:], 16) / 255 if len(h) == 8 else 1.0
    return to_hex(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), base * alpha)


def norm_hex(h):
    h = h.lstrip("#")
    if len(h) in (3, 4):
        h = "".join(c * 2 for c in h)
    return "#" + h.upper()


def num_expr(s):
    """0.5 · 24/255 · 24.0 / 255.0 → float"""
    s = s.strip()
    m = re.fullmatch(r"([\d.]+)\s*/\s*([\d.]+)", s)
    if m:
        return float(m.group(1)) / float(m.group(2))
    return float(s)


def hsl_to_rgb(h, s, l):
    h = (h % 360) / 360
    if s == 0:
        return l * 255, l * 255, l * 255

    def hue(p, q, t):
        t %= 1
        if t < 1 / 6:
            return p + (q - p) * 6 * t
        if t < 1 / 2:
            return q
        if t < 2 / 3:
            return p + (q - p) * (2 / 3 - t) * 6
        return p
    q = l * (1 + s) if l < 0.5 else l + s - l * s
    p = 2 * l - q
    return hue(p, q, h + 1 / 3) * 255, hue(p, q, h) * 255, hue(p, q, h - 1 / 3) * 255


def oklch_linear(L, C, H):
    a, b = C * math.cos(math.radians(H)), C * math.sin(math.radians(H))
    l_ = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m_ = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s_ = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l_ - 3.3077115913 * m_ + 0.2309699292 * s_,
            -1.2684380046 * l_ + 2.6097574011 * m_ - 0.3413193965 * s_,
            -0.0041960863 * l_ - 0.7034186147 * m_ + 1.7076147010 * s_)


def oklch_to_rgb(L, C, H):
    lin = oklch_linear(L, C, H)

    def gamma(x):
        x = max(0.0, min(1.0, x))
        return 12.92 * x if x <= 0.0031308 else 1.055 * x ** (1 / 2.4) - 0.055
    return tuple(gamma(x) * 255 for x in lin)


def css_color(value):
    """CSS colour → (hex, note) or (None, None)."""
    v = value.strip()
    m = re.fullmatch(r"#([0-9A-Fa-f]{3,4}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})", v)
    if m:
        return norm_hex(m.group(1)), None
    m = re.fullmatch(r"(rgba?|hsla?|oklch)\(\s*(.+?)\s*\)", v, re.I)
    if not m:
        return None, None
    fn, args = m.group(1).lower(), re.split(r"[\s,/]+", m.group(2).strip())
    try:
        alpha = 1.0
        if len(args) == 4:
            a = args[3]
            alpha = float(a[:-1]) / 100 if a.endswith("%") else float(a)
        if fn.startswith("rgb"):
            ch = [float(x[:-1]) * 2.55 if x.endswith("%") else float(x) for x in args[:3]]
            return to_hex(*ch, alpha), None
        if fn.startswith("hsl"):
            h = float(args[0].replace("deg", ""))
            s, l = (float(x.rstrip("%")) / 100 for x in args[1:3])
            return to_hex(*hsl_to_rgb(h, s, l), alpha), None
        L = float(args[0][:-1]) / 100 if args[0].endswith("%") else float(args[0])
        C, H = float(args[1]), float(args[2].replace("deg", "")) if args[2] != "none" else 0.0
        clipped = any(x < -1e-4 or x > 1 + 1e-4 for x in oklch_linear(L, C, H))
        return to_hex(*oklch_to_rgb(L, C, H), alpha), ("outside sRGB: the hex is a clipped, duller copy of the "
                                                         "oklch colour" if clipped else None)
    except (ValueError, IndexError):
        return None, None


# ── Swift scanning ───────────────────────────────────────────────────────────

SCOPE_RE = re.compile(r"^\s*(?:@\w+(?:\([^)]*\))?\s+)*(?:(?:public|internal|private|fileprivate|open|final|indirect)\s+)*"
                      r"(enum|struct|extension|class)\s+([A-Za-z_][\w.]*)")
STATIC_RE = re.compile(r"^\s*(?:@\w+\s+)*(?:(?:public|internal|private|fileprivate|open|nonisolated)\s+)*static\s+(?:let|var)\s+"
                       r"`?(\w+)`?\s*(?::\s*([\w.]+))?\s*=\s*(.+?)\s*$")
UIKIT_REV = {}
for _n, _e in SYSTEM_UIKIT.items():
    UIKIT_REV.setdefault(_e.lstrip("."), _n)
UIKIT_REV["label"] = "label"
SWIFTUI_SYSTEM = {"primary", "secondary", "red", "orange", "yellow", "green", "mint", "teal", "cyan", "blue",
                  "indigo", "purple", "pink", "brown", "gray"}


def code_only(line):
    line = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
    return line.split("//", 1)[0]


def split_top(s, sep):
    """Split at `sep` outside parentheses/brackets."""
    depth, out, cur, i = 0, [], "", 0
    while i < len(s):
        ch = s[i]
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        if depth == 0 and s.startswith(sep, i):
            out.append(cur)
            cur = ""
            i += len(sep)
            continue
        cur += ch
        i += 1
    out.append(cur)
    return out


def swift_single_color(seg):
    """One side of a colour expression → ('hex', '#..') | ('system', name) | ('asset', name) | None."""
    s = seg.strip()
    alpha = 1.0
    m = re.search(r"\.opacity\(\s*([\d.]+)\s*\)\s*$", s)
    if m:
        alpha = float(m.group(1))
        s = s[:m.start()]
    am = re.search(r"\b(?:alpha|opacity):\s*([\d.]+)", s)
    m = re.search(r"0x([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)\b|\"#?([0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)\"", s)
    if m:
        h = norm_hex(m.group(1) or m.group(2))
        a = float(am.group(1)) if am else 1.0
        return ("hex", with_alpha(h, a * alpha))
    m = re.search(r"red:\s*([^,]+),\s*green:\s*([^,]+),\s*blue:\s*([^,)]+)", s)
    if m:
        try:
            r, g, b = (num_expr(x) for x in m.groups())
            a = float(am.group(1)) if am else 1.0
            return ("hex", to_hex(r * 255, g * 255, b * 255, a * alpha))
        except ValueError:
            return None
    m = re.search(r"hue:\s*([\d./ ]+),\s*saturation:\s*([\d./ ]+),\s*brightness:\s*([\d./ ]+)", s)
    if m:
        import colorsys
        try:
            r, g, b = colorsys.hsv_to_rgb(*(num_expr(x) for x in m.groups()))
        except ValueError:
            return None
        a = float(am.group(1)) if am else 1.0
        return ("hex", to_hex(r * 255, g * 255, b * 255, a * alpha))
    m = re.search(r"white:\s*([\d.]+)", s)
    if m:
        w = float(m.group(1)) * 255
        a = float(am.group(1)) if am else 1.0
        return ("hex", to_hex(w, w, w, a * alpha))
    m = re.fullmatch(r"(?:Color|SwiftUI\.Color)?\.(\w+)", s)
    if m and m.group(1) in SWIFTUI_SYSTEM:
        return ("system", m.group(1)) if alpha == 1 else ("unsupported", f"{s}.opacity({alpha})")
    m = re.search(r"(?:UIColor)?\.(\w+)\s*\)?\s*$", s)
    if m and m.group(1) in UIKIT_REV and ("uiColor" in s or "UIColor" in s or s.startswith(".") or s.startswith("Color(.")):
        return ("system", UIKIT_REV[m.group(1)]) if alpha == 1 else ("unsupported", f"{s} with opacity {alpha}")
    m = re.search(r'Color\(\s*"([^"]+)"', s)
    if m:
        return ("asset", m.group(1))
    return None


def swift_color(expr):
    """→ {'light': value, 'dark': value} or None."""
    e = expr.strip()
    if "light:" in e and "dark:" in e:
        li, di = e.index("light:"), e.index("dark:")
        if li < di:
            lseg, dseg = e[li + 6:di], e[di + 5:]
        else:
            dseg, lseg = e[di + 5:li], e[li + 6:]
        return {"light": swift_single_color(lseg.rstrip(", ")), "dark": swift_single_color(dseg.rstrip(") ,"))}
    m = re.search(r"==\s*\.dark\s*\?", e)
    if m:
        rest = e[m.end():]
        parts = split_top(rest, " : ")
        if len(parts) >= 2:
            return {"light": swift_single_color(parts[1].rstrip("}) ")), "dark": swift_single_color(parts[0])}
    one = swift_single_color(e)
    return {"light": one, "dark": one} if one else None


def swift_font(expr):
    m = re.search(r'\.custom\(\s*"([^"]+)"\s*,\s*(?:size|fixedSize):\s*([\d.]+)(.*)', expr)
    if m:
        name, size, rest = m.group(1), float(m.group(2)), m.group(3)
        family, weight = (name.rsplit("-", 1) + [None])[:2] if "-" in name else (name, None)
        return {"family": family, "weight": weight, "size": size, "relative": "relativeTo" in rest,
                "fixed": "fixedSize" in expr, "font": name}
    m = re.search(r"\.system\(\s*size:\s*([\d.]+)(?:\s*,\s*weight:\s*\.(\w+))?", expr)
    if m:
        w = m.group(2)
        return {"family": "system", "weight": (w[:1].upper() + w[1:]) if w else None, "size": float(m.group(1)),
                "relative": False, "font": None}
    return None


def swift_animation(expr):
    m = re.search(r"\.spring\(\s*response:\s*([\d.]+)\s*,\s*dampingFraction:\s*([\d.]+)", expr)
    if m:
        return ("spring", {"response": float(m.group(1)), "damping": float(m.group(2))})
    m = re.search(r"\.spring\(\s*duration:\s*([\d.]+)(?:\s*,\s*bounce:\s*(-?[\d.]+))?", expr)
    if m:
        return ("spring", {"duration": float(m.group(1)), "bounce": float(m.group(2) or 0)})
    m = re.search(r"\.timingCurve\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*duration:\s*([\d.]+)", expr)
    if m:
        a = [float(x) for x in m.groups()]
        return ("duration", {"ms": round(a[4] * 1000), "curve": a[:4]})
    m = re.search(r"\.(linear|easeIn|easeOut|easeInOut)\(\s*duration:\s*([\d.]+)", expr)
    if m:
        return ("duration", {"ms": round(float(m.group(2)) * 1000), "curve": m.group(1)})
    return None


def clean_num(v):
    return int(v) if float(v).is_integer() else float(v)


def product_name(root):
    """The product's name from CLAUDE.md's first heading (the template placeholder doesn't
    count); the folder name only as a last resort."""
    claude = Path(root) / "CLAUDE.md"
    if claude.is_file():
        for line in claude.read_text(encoding="utf-8", errors="replace").splitlines():
            if line.startswith("# "):
                name = line[2:].strip()
                if name and not name.startswith("["):
                    return name
                break
    return Path(root).resolve().name


def unfold_one_liners(lines):
    """`enum Spacing { static let sm: CGFloat = 8; static let md: CGFloat = 16 }` → one
    declaration per line, so the line scanner sees scopes and statics the same way."""
    out = []
    for raw in lines:
        code = code_only(raw)
        if "static " in code and (";" in code or ("{" in code and "}" in code and SCOPE_RE.match(code))):
            m = SCOPE_RE.match(code)
            rest = code
            if m and "{" in code:
                head, rest = code.split("{", 1)
                out.append(head + "{")
            closing = rest.rstrip().endswith("}") and rest.count("}") > rest.count("{")
            body = rest.rstrip()[:-1] if closing else rest
            out += [part.strip() for part in split_top(body, ";") if part.strip()]
            if closing:
                out.append("}")
        else:
            out.append(raw)
    return out


def scan_swift(root, exclude=(), include_generated=False):
    tokens, notes = [], []
    for path, rel in walk_files(root, {".swift"}, exclude):
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_generated(text) and not include_generated:
            continue
        lines = unfold_one_liners(text.split("\n"))
        stack, depth, i = [], 0, 0
        while i < len(lines):
            raw = lines[i]
            code = code_only(raw)
            scope = SCOPE_RE.match(code)
            m = STATIC_RE.match(code if '"' not in raw else raw.split("//", 1)[0])
            j = i
            if m and stack:
                expr = m.group(3)
                while expr.count("(") > expr.count(")") and j + 1 < len(lines) and j - i < 10:
                    j += 1
                    expr += " " + lines[j].split("//", 1)[0].strip()
                tokens.append({"file": rel, "line": i + 1, "scope": [s for s, _ in stack], "name": m.group(1),
                               "type": m.group(2), "expr": expr.strip()})
            for k in range(i, j + 1):
                c = code_only(lines[k])
                before = depth
                depth += c.count("{") - c.count("}")
                if k == i and scope and "{" in c:
                    stack.append((scope.group(2), before + 1))
                while stack and depth < stack[-1][1]:
                    stack.pop()
            i = j + 1
    return tokens, notes


def classify_swift(tokens):
    colors, fonts, numbers, anims, other = [], [], [], [], []
    for t in tokens:
        typ, expr = (t["type"] or ""), t["expr"]
        if typ in ("Color", "SwiftUI.Color") or re.match(r"(Color\b|Color\(|\.init\(light)", expr):
            colors.append(t)
        elif typ == "Font" or re.match(r"(Font\.|\.custom\(|\.system\()", expr):
            fonts.append(t)
        elif typ == "Animation" or re.match(r"(Animation\.|\.spring\(|\.easeOut\(|\.easeIn\(|\.easeInOut\(|\.linear\(|\.timingCurve\()", expr):
            anims.append(t)
        elif typ in ("CGFloat", "Double", "Float", "Int", "") and re.fullmatch(r"-?[\d.]+", expr):
            numbers.append(t)
        else:
            other.append(t)
    return colors, fonts, numbers, anims, other


def common_scope(items):
    """Most common top scope, then the longest prefix shared by that group's scopes."""
    if not items:
        return None, []
    tops = {}
    for t in items:
        tops.setdefault(tuple(t["scope"][:1]), []).append(t)
    group = max(tops.values(), key=len)
    prefix = list(group[0]["scope"])
    for t in group:
        n = 0
        while n < min(len(prefix), len(t["scope"])) and prefix[n] == t["scope"][n]:
            n += 1
        prefix = prefix[:n]
    return prefix, group


def pick_roles(keys):
    """{role: existing key} for the six required roles, by exact then fuzzy name."""
    chosen, used = {}, set()
    norm = {k: re.sub(r"[^a-z0-9]", "", k.lower()) for k in keys}
    for role in REQUIRED_SEMANTIC:
        hints = ROLE_HINTS[role]
        cands = [k for k in keys if k not in used and norm[k] == role]
        cands += [k for k in keys if k not in used and "." not in k and norm[k] in hints]
        cands += [k for k in keys if k not in used and norm[k] in hints]
        cands += [k for k in keys if k not in used and "." not in k and any(norm[k].startswith(h) for h in hints)]
        if cands:
            chosen[role] = cands[0]
            used.add(cands[0])
    return chosen


def build_semantic(named, ramp, notes):
    """named: {key: {'light': v, 'dark': v}} → primitives ramps, semantic, semantic_dark, rename.
    v is ('hex', '#..') | ('system', name) | ('ref', 'ramp.stop') | ('asset'|'unsupported', text) | None."""
    light_ramp, dark_ramp = {}, {}
    sem, sem_dark = {}, {}

    def path_for(value, key, table, ramp_name):
        kind, val = value
        if kind == "system":
            return f"system.{val}"
        if kind == "ref":
            return val
        stop = slug(key.replace(".", " "))
        table[stop] = val
        return f"{ramp_name}.{stop}"

    roles = pick_roles(list(named))
    rename, keymap = {}, {}
    for key in named:
        keymap[key] = key
    for role, existing in roles.items():
        if existing == role:
            continue
        if role in named or any(k.startswith(role + ".") for k in named):
            notes.append(f"role '{role}' looks like '{existing}', but '{role}' already names another token — map it by hand")
            continue
        keymap[existing] = role
        rename[role] = existing
    readable = ("hex", "system", "ref")
    for key, v in named.items():
        lv, dv = v.get("light"), v.get("dark") or v.get("light")
        if lv is None or lv[0] not in readable:
            what = f"asset catalog colour '{lv[1]}'" if lv and lv[0] == "asset" else (f"`{lv[1]}`" if lv else "unparsed expression")
            notes.append(f"colour '{key}': {what} — can't be read from code; fill it in by hand")
            lpath = dpath = "TODO"
        else:
            lpath = path_for(lv, key, light_ramp, ramp)
            if dv is None or dv[0] not in readable:
                notes.append(f"colour '{key}': dark side unreadable — copied light")
                dpath = lpath
            else:
                dpath = lpath if dv == lv else path_for(dv, key, dark_ramp, f"{ramp}Dark")
        for table, path in ((sem, lpath), (sem_dark, dpath)):
            node, parts = table, keymap[key].split(".")
            for p in parts[:-1]:
                node = node.setdefault(p, {})
            node[parts[-1]] = path
    for role in REQUIRED_SEMANTIC:
        if role not in sem:
            sem[role] = "TODO"
            sem_dark[role] = "TODO"
            notes.append(f"no existing colour looks like the '{role}' role — map one by hand (then add emit rename if needed)")
    prims = {ramp: light_ramp}
    if dark_ramp:
        prims[f"{ramp}Dark"] = dark_ramp
    return prims, sem, sem_dark, rename


def adopt_swift(root, exclude=()):
    tokens, notes = scan_swift(root, exclude)
    colors, fonts, numbers, anims, _ = classify_swift(tokens)
    model = {"schema_version": 1, "modes": ["light", "dark"],
             "brand": {"name": product_name(root), "feel": []}}
    namespaces = {}
    prims = {}

    # colours
    cprefix, cgroup = common_scope(colors)
    named = {}
    for t in colors:
        if t not in cgroup:
            notes.append(f"colour {'.'.join(t['scope'] + [t['name']])} ({t['file']}:{t['line']}) is outside the "
                         f"main colour namespace — not adopted")
            continue
        rel = t["scope"][len(cprefix):]
        key = ".".join([lower_first(s) for s in rel] + [t["name"]])
        val = swift_color(t["expr"])
        if val is None:
            val = {"light": ("unsupported", t["expr"][:60]), "dark": None}
        named[key] = val
    ramp = slug(cprefix[-1]) if cprefix else "palette"
    if named:
        namespaces["colors"] = ".".join(cprefix)
        cprims, sem, sem_dark, rename = build_semantic(named, ramp, notes)
        prims["color"] = cprims
    else:
        sem = {r: "TODO" for r in REQUIRED_SEMANTIC}
        sem_dark = dict(sem)
        rename = {}
        notes.append("no colour tokens found in Swift enums/extensions")

    # type
    fprefix, fgroup = common_scope(fonts)
    families, styles, relative = {}, {}, set()
    for t in fonts:
        f = swift_font(t["expr"])
        if f is None or t not in fgroup:
            notes.append(f"font {t['name']} ({t['file']}:{t['line']}): `{t['expr'][:60]}` — not a custom/system font literal; not adopted")
            continue
        fam_key = "system" if f["family"] == "system" else slug(f["family"])
        families[fam_key] = f["family"]
        spec = {"family": fam_key}
        if f["weight"]:
            spec["weight"] = f["weight"]
        spec["size"] = clean_num(f["size"])
        styles[t["name"]] = spec
        relative.add(f["relative"])
    if styles:
        namespaces["typography"] = ".".join(fprefix)
        t = {"families": families}
        if relative == {False} or relative == {True, False}:
            t["dynamic_type"] = False
            if relative == {True, False}:
                notes.append("fonts mix relativeTo: and fixed sizes — draft uses fixed sizes (dynamic_type: false); check it")
        elif relative == {True}:
            notes.append("custom fonts use relativeTo: — Ship derives the text style from the size; diff the emitted file")
        t["styles"] = styles
        prims["type"] = t
    else:
        prims["type"] = {"family": "TODO", "scale": {"body": "TODO", "title": "TODO"}}

    # radius + spacing
    radius, spacing, rscope, sscope = {}, {}, None, None
    for t in numbers:
        scope = ".".join(t["scope"])
        low = scope.lower()
        v = clean_num(float(t["expr"]))
        if re.search(r"radi|corner|round", low):
            radius[t["name"]] = v
            rscope = rscope or scope
        elif re.search(r"spac|gap|pad|inset|margin|gutter", low):
            spacing[t["name"]] = v
            sscope = sscope or scope
    prims["radius"] = radius or {"control": "TODO", "card": "TODO"}
    if rscope:
        namespaces["radius"] = rscope
    sp = {"unit": 4}
    if spacing:
        ints = [int(v) for v in spacing.values() if float(v).is_integer() and v > 0]
        g = 0
        for v in ints:
            g = math.gcd(g, v)
        if "unit" in spacing:
            sp["unit"] = spacing.pop("unit")
        elif g >= 2:
            sp["unit"] = g
        sp["scale"] = spacing
        namespaces["spacing"] = sscope
        if "x" in spacing:
            notes.append("spacing token named 'x' collides with Ship's x(n) helper — rename it")
    prims["spacing"] = sp

    # motion
    mo = {"springs": {}, "durations": {}}
    mscope = None
    for t in anims:
        a = swift_animation(t["expr"])
        if a is None:
            notes.append(f"animation {t['name']} ({t['file']}:{t['line']}): `{t['expr'][:60]}` — preset/modifier Ship can't express; not adopted")
            continue
        mo["springs" if a[0] == "spring" else "durations"][t["name"]] = a[1]
        mscope = mscope or ".".join(t["scope"])
    if mscope:
        namespaces["motion"] = mscope
    prims["motion"] = {k: v for k, v in mo.items() if v} or {"springs": {}}

    model["primitives"] = prims
    model["semantic"] = sem
    model["semantic_dark"] = sem_dark
    swift = {}
    if namespaces:
        swift["namespaces"] = namespaces
    if rename:
        swift["rename"] = rename
    if swift:
        model["emit"] = {"swiftui": swift}
    stats = {"colors": len(named), "type": len(styles), "radius": len(radius), "spacing": len(spacing),
             "motion": len(mo["springs"]) + len(mo["durations"])}
    return model, notes, stats


# ── Web scanning ─────────────────────────────────────────────────────────────

def css_blocks(text):
    """→ [(context tuple of preludes, declarations text)] with at-rule context kept."""
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    stack, buf, out = [], "", []
    for ch in text:
        if ch == "{":
            head, _, prelude = buf.rpartition(";")
            if stack and head:
                stack[-1][1] += head + ";"
            stack.append([prelude.strip(), ""])
            buf = ""
        elif ch == "}":
            if stack:
                sel, decl = stack.pop()
                out.append((tuple(s for s, _ in stack) + (sel,), decl + buf))
            buf = ""
        else:
            buf += ch
    return out


def is_dark(ctx):
    joined = " ".join(ctx).replace("'", '"').replace(" ", "")
    return any(k in joined for k in (".dark", 'data-theme="dark"', "data-theme=dark", "prefers-color-scheme:dark"))


def length_px(v):
    m = re.fullmatch(r"(-?[\d.]+)(px|rem)?", v.strip())
    if not m:
        return None
    n = float(m.group(1)) * (16 if m.group(2) == "rem" else 1)
    return clean_num(round(n, 3))


def scan_web(root, exclude=()):
    light, dark, theme_block = {}, {}, set()
    for path, rel in walk_files(root, {".css", ".scss"}, exclude):
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_generated(text):
            continue
        for ctx, decls in css_blocks(text):
            in_theme = any(c.startswith("@theme") for c in ctx)
            target = dark if is_dark(ctx) else light
            for m in re.finditer(r"(--[\w-]+)\s*:\s*([^;]+);?", decls):
                target[m.group(1)] = m.group(2).strip()
                if in_theme:
                    theme_block.add(m.group(1))
    configs = []
    for path, rel in walk_files(root, {".js", ".ts", ".cjs", ".mjs"}, exclude):
        if path.name.startswith("tailwind.config"):
            configs.append((rel, path.read_text(encoding="utf-8", errors="replace")))
    return light, dark, theme_block, configs


def resolve_var(value, table, seen=()):
    """Follow var(--x) to a value: (the value, the first variable followed). A loop stops where it
    closes and returns the var() unresolved."""
    m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", value.strip())
    if m and m.group(1) in table and m.group(1) not in seen and len(seen) < 8:
        return resolve_var(table[m.group(1)], table, seen + (m.group(1),))[0], m.group(1)
    return value, None


def loops_back(var, table):
    """True when var's var() chain comes back to itself: the browser drops the declaration."""
    seen, value = {var}, table.get(var, "")
    for _ in range(8):
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", value.strip())
        if not m or m.group(1) not in table:
            return False
        if m.group(1) in seen:
            return True
        seen.add(m.group(1))
        value = table[m.group(1)]
    return False


# shadcn/ui role names → Ship's semantic keys, by meaning. shadcn's `muted` and `accent` are
# backgrounds (their text is the `-foreground` pair): never Ship's muted text or action colour.
SHADCN_ADOPT = {"foreground": "text", "card": "surface", "muted": "muted-surface", "muted-foreground": "muted",
                "border": "hairline", "primary": "action", "primary-foreground": "on_action", "ring": "focus",
                "destructive": "error"}


def shadcn_roles(named):
    """(named with shadcn's colour roles renamed to Ship's keys, {shadcn role: Ship key}). The
    mapping reproduces the project's current look, so adopting moves nothing."""
    out, roles = {}, {}
    for key, v in named.items():
        m = re.fullmatch(r"chart-(\d+)", key)
        new = f"chart.{m.group(1)}" if m else SHADCN_ADOPT.get(key, key)
        out[new] = v
        roles[key] = new
    return out, roles


def theme_sheet(root, exclude=()):
    """(path, text) of the stylesheet that holds the theme: Tailwind's import, else the most variables."""
    best, score = None, 0
    for path, rel in walk_files(root, {".css", ".scss"}, exclude):
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_generated(text):
            continue
        n = len(re.findall(r"--[\w-]+\s*:", text)) + (1000 if re.search(r"@import\s+[\"']tailwindcss", text) else 0)
        if n > score:
            best, score = (rel, text), n
    return best


def adopt_web(root, exclude=()):
    notes = []
    light, dark, theme_block, configs = scan_web(root, exclude)
    for rel, text in configs:
        m = re.search(r"colors\s*:\s*\{(.*?)\n\s*\}", text, re.S)
        if m:
            for k, v in re.findall(r"['\"]?([\w-]+)['\"]?\s*:\s*['\"](#[0-9A-Fa-f]{3,8})['\"]", m.group(1)):
                light.setdefault(f"--color-{k}", v)
            notes.append(f"{rel}: Tailwind v3 config colours read best-effort (nested palettes are skipped)")
    model = {"schema_version": 1, "modes": ["light", "dark"],
             "brand": {"name": product_name(root), "feel": []}}
    palette, named, radius, spacing, families, sizes = {}, {}, {}, {}, {}, {}
    prefixes, palette_vars, named_prefix = {}, {}, {}
    color_re = re.compile(r"(?:(\w+)-)?colou?r-(.+)$")
    for var, raw in light.items():                      # pass 1: palette ramps (name-NNN, one value)
        m = color_re.match(var[2:])
        key = m.group(2) if m else var[2:]
        rs = re.fullmatch(r"([a-z][\w]*?)-(\d{2,3})", key)
        hexv = css_color(resolve_var(raw, light)[0])[0]
        if rs and hexv and var not in dark:
            palette.setdefault(slug(rs.group(1)), {})[rs.group(2)] = hexv
            palette_vars[var] = f"{slug(rs.group(1))}.{rs.group(2)}"

    def side(raw, table):
        if raw is None:
            return None
        m = re.fullmatch(r"var\(\s*(--[\w-]+)\s*(?:,[^)]*)?\)", raw.strip())
        if m and m.group(1) in palette_vars:
            return ("ref", palette_vars[m.group(1)])
        hexv, _ = css_color(resolve_var(raw, table)[0])
        return ("hex", hexv) if hexv else None

    for var, raw in light.items():                      # pass 2: semantic colours, lengths, fonts
        if var in palette_vars:
            continue
        name = var[2:]
        val, alias = resolve_var(raw, light)
        hexv, cnote = css_color(val)
        m = color_re.match(name)
        if hexv or m:
            key = m.group(2) if m else name
            if m and m.group(1):
                prefixes[m.group(1)] = prefixes.get(m.group(1), 0) + 1
                named_prefix[key] = m.group(1)
            if hexv is None:
                notes.append(f"{var}: `{raw}` is not a colour Ship can read — skipped")
                continue
            if cnote:
                notes.append(f"{var}: {cnote}")
            lv = side(raw, light)
            dv = side(dark.get(var), {**light, **dark}) if var in dark else lv
            named[key] = {"light": lv, "dark": dv}
            continue
        px = length_px(val)
        if re.search(r"radius|rounded", name) and px is not None:
            radius[slug(re.sub(r"^.*?(radius|rounded)-?", "", name) or "default")] = px
        elif re.search(r"(^|-)(spacing|space|gap)(-|$)", name) and px is not None:
            k = re.sub(r"^.*?(spacing|space|gap)-?", "", name)
            spacing[slug(k) if k else "unit"] = px
        elif re.search(r"(^|-)font-(?!size|weight)", name) and not re.fullmatch(r"[\d.]+(px|rem)?", val):
            fam = val.split(",")[0].strip().strip("'\"")
            key = re.sub(r"^.*?font-", "", name)
            families[slug(key)] = "system" if fam.lower() in ("system-ui", "-apple-system", "ui-sans-serif") else fam
        elif re.search(r"(^|-)text-[\w-]+$", name) and "--" not in name and px is not None:
            sizes[slug(re.sub(r"^.*?text-", "", name))] = px
    pfx = max(prefixes, key=prefixes.get) if prefixes else None
    if not named:
        notes.append("no semantic colour custom properties found")
    both = {**light, **dark}
    for var in sorted(v for v in both if loops_back(v, both)):
        notes.append(f"{var}: `{both[var]}` leads into a loop of variables, so the browser drops it (a font "
                     f"falls back to the default serif): a bug in the app's stylesheet to fix")
    shadcn_map = None
    if (Path(root) / "components.json").is_file() and named:
        named, shadcn_map = shadcn_roles(named)
        named_prefix = {}
        notes.append("shadcn/ui project: roles mapped by meaning (primary → action, primary-foreground → "
                     "on_action, muted-foreground → muted, ring → focus, destructive → error, chart-N → chart.N); "
                     "emit.css writes tokens.css with the shadcn bridge, so the old stylesheet stays as it is")
    ramp = "web"
    # palette aliases: a semantic var that points at a palette var keeps the reference
    cprims, sem, sem_dark, rename = build_semantic(named, ramp, notes)
    for pname, stops in palette.items():
        cprims[pname] = stops
    prims = {"color": cprims}
    if families:
        fam_key = "sans" if "sans" in families else next(iter(families))
        styles = {k: {"family": fam_key, "size": v} for k, v in sizes.items()}
        if "body" not in styles and "base" in styles:
            styles["body"] = styles.pop("base")
            notes.append("text-base adopted as the body style")
        prims["type"] = {"families": families, "styles": styles} if styles else {"families": families, "styles": {"body": {"family": fam_key, "size": "TODO"}}}
    else:
        prims["type"] = {"family": "TODO", "scale": {"body": "TODO", "title": "TODO"}}
    prims["radius"] = radius or {"control": "TODO", "card": "TODO"}
    sp = {"unit": spacing.pop("unit", 4)}
    if spacing:
        sp["scale"] = spacing
    prims["spacing"] = sp
    prims["motion"] = {"springs": {}}
    model["primitives"] = prims
    model["semantic"] = sem
    model["semantic_dark"] = sem_dark
    css = {}
    if pfx and named and all(named_prefix.get(k) == pfx for k in named):
        css["prefix"] = pfx
    if rename:
        css["rename"] = rename
    if shadcn_map:
        from .emit_web import SHADCN_REQUIRED
        sheet = theme_sheet(root, exclude)
        if sheet:
            css["out"] = str(Path(sheet[0]).parent / "tokens.css")
            if re.search(r"@custom-variant\s+dark\s*\(\s*&:is\(\s*\.dark", sheet[1]) or re.search(r"(^|\s)\.dark\s*\{", sheet[1]):
                css["theme_selector"] = "class"
        css["shadcn"] = {"roles": {k: v for k, v in shadcn_map.items()
                                   if k in SHADCN_REQUIRED or re.fullmatch(r"chart-\d+", k)}}
    if css:
        model["emit"] = {"css": css}
    tw = sum(1 for v in theme_block if v.startswith("--color-"))
    if tw:
        notes.append(f"{tw} Tailwind v4 @theme colours found — emit tailwind keeps their utility names "
                     f"(bg-<name>); palette ramps become primitives, and Ship only emits semantic utilities")
    stats = {"colors": len(named), "palette": sum(len(v) for v in palette.values()), "type": len(sizes),
             "radius": len(radius), "spacing": len(spacing)}
    return model, notes, stats


# ── Component inventory ──────────────────────────────────────────────────────

def guess_role(name):
    for suffix, role in COMPONENT_ROLES:
        if name.endswith(suffix):
            return role
    for suffix, role in COMPONENT_ROLES:
        if suffix in name:
            return role
    return None


def inventory(root, model, platform, exclude=()):
    from .emit_swiftui import accessors
    from .emit_web import css_names, kebab
    entries = []
    if platform == "swiftui":
        acc = accessors(model)
        reverse = {}
        for group, table in acc.items():
            for key, expr in table.items():
                reverse[expr] = key if group == "colors" else f"{ {'type': 'type', 'radius': 'radius', 'spacing': 'spacing', 'motion': 'motion'}[group]}.{key}"
        files = list(walk_files(root, {".swift"}, exclude))
        texts = {rel: p.read_text(encoding="utf-8", errors="replace") for p, rel in files}
        for rel, text in texts.items():
            if not COMPONENT_DIRS.search(rel) or is_generated(text):
                continue
            for m in re.finditer(r"^\s*(?:public\s+|internal\s+)?struct\s+([A-Z]\w*)\s*(?:<[^>]*>)?\s*:\s*[^{]*\bView\b", text, re.M):
                name = m.group(1)
                used = sum(1 for r, t in texts.items() if r != rel and re.search(rf"\b{name}\s*[({{<]", t))
                variants = []
                vm = re.search(r"enum\s+(?:Style|Variant|Kind|Appearance)\b[^{]*\{(.*?)\}", text, re.S)
                if vm:
                    for cm in re.finditer(r"\bcase\s+([^\n{(=;]+)", vm.group(1)):
                        variants += [v.strip() for v in cm.group(1).split(",") if re.fullmatch(r"[a-z]\w*", v.strip())]
                toks = []
                for expr, key in reverse.items():
                    if re.search(rf"{re.escape(expr)}\b", text) and key not in toks:
                        toks.append(key)
                entry = {"name": name, "file": rel}
                role = guess_role(name)
                if role:
                    entry["role"] = role
                if toks:
                    entry["tokens"] = toks
                if variants:
                    entry["variants"] = variants
                entry.update({"origin": "adopted", "doc": f"Adopted from existing code; used in {used} other file(s).",
                              "added": date.today().isoformat()})
                entries.append(entry)
    else:
        names = css_names(model)
        files = list(walk_files(root, {".tsx", ".jsx", ".vue", ".svelte"}, exclude))
        texts = {rel: p.read_text(encoding="utf-8", errors="replace") for p, rel in files}
        sem = list(names["colors"])
        for rel, text in texts.items():
            if not COMPONENT_DIRS.search(rel):
                continue
            m = re.search(r"export\s+(?:default\s+)?(?:function|const)\s+([A-Z]\w*)", text)
            listed = re.search(r"export\s*\{([^}]*)\}", text)   # shadcn: function Button(…) … export { Button }
            name = m.group(1) if m else next((n for n in (x.split(" as ")[-1].strip() for x in
                                                          (listed.group(1).split(",") if listed else []))
                                              if re.fullmatch(r"[A-Z]\w*", n)), None)
            if not name:
                continue
            used = sum(1 for r, t in texts.items() if r != rel and re.search(rf"<{name}\b", t))
            variants = []
            um = re.search(r"variant\??\s*:\s*((?:['\"][\w-]+['\"]\s*\|?\s*)+)", text)
            if um:
                variants = [slug(v) for v in re.findall(r"['\"]([\w-]+)['\"]", um.group(1))]
            cm = re.search(r"variants\s*:\s*\{\s*variant\s*:\s*\{(.*?)\}", text, re.S)
            if cm:
                variants += [slug(v) for v in re.findall(r"^\s*['\"]?([\w-]+)['\"]?\s*:", cm.group(1), re.M) if slug(v) not in variants]
            css_cfg = (model.get("emit") or {}).get("css") or {}
            ren = css_cfg.get("rename") or {}
            shadcn_roles_ = (css_cfg.get("shadcn") or {}).get("roles") or {}
            # on a shadcn project the classes use shadcn's names: bg-primary is the action colour, and
            # bg-muted is a background, never Ship's muted text
            util = {k: [u] if (u := kebab(ren.get(k, k))) not in shadcn_roles_ else [] for k in sem}
            for role, key in shadcn_roles_.items():
                util.setdefault(key, []).append(role)
            toks = [k for k in sem if any(re.search(rf"(bg|text|border|ring|fill|stroke|outline)-{re.escape(u)}(?![\w-])", text)
                                          for u in util.get(k, []))
                    or names["colors"][k] in text]
            entry = {"name": name, "file": rel}
            role = guess_role(name)
            if role:
                entry["role"] = role
            if toks:
                entry["tokens"] = toks
            if variants:
                entry["variants"] = variants
            entry.update({"origin": "adopted", "doc": f"Adopted from existing code; used in {used} other file(s).",
                          "added": date.today().isoformat()})
            entries.append(entry)
    return entries


def detect_platform(root):
    for _p, rel in walk_files(root, {".swift"}):
        return "swiftui"
    return "web"


def adopt(root, platform="auto", exclude=()):
    platform = detect_platform(root) if platform == "auto" else platform
    if platform == "swiftui":
        model, notes, stats = adopt_swift(root, exclude)
    else:
        model, notes, stats = adopt_web(root, exclude)
    comps = inventory(root, model, platform, exclude)
    return platform, model, {"schema_version": 1, "components": comps}, notes, stats
