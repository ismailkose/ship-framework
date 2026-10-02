"""Audit code against the registry: raw literals vs the scale, and duplicated patterns.

Counts raw spacing / radius / colour / font-size literals in view code, splits them into
on-scale (matches a token value — should use the token) and off-scale (no token has it — a
design decision nobody made), and finds the same surface+radius combination rebuilt in
several places (rule of three → promote, or use the registered component that already
does it). Token files, generated files and --exclude globs are skipped.
"""

import re

from .adopt import SKIP_DIRS, is_generated, walk_files
from .copycheck import CATALOG_EXTS, copy_findings
from .emit_swiftui import accessors
from .registry import (components, flatten, resolve_color, semantic_keys, spacing_scale, type_styles)

SWIFT = {
    "spacing": [r"\.padding\(\s*(-?\d+(?:\.\d+)?)\s*\)",
                r"\.padding\(\s*(?:\.\w+|\[[^\]]*\])\s*,\s*(-?\d+(?:\.\d+)?)\s*\)",
                r"\bspacing:\s*(-?\d+(?:\.\d+)?)\b",
                r"EdgeInsets\([^)]*?top:\s*(\d+(?:\.\d+)?)"],
    "radius": [r"cornerRadius:\s*(\d+(?:\.\d+)?)\b", r"\.cornerRadius\(\s*(\d+(?:\.\d+)?)\s*\)"],
    "font": [r"\.system\(\s*size:\s*(\d+(?:\.\d+)?)", r"\.custom\(\s*\"[^\"]+\"\s*,\s*(?:size|fixedSize):\s*(\d+(?:\.\d+)?)"],
    "color": [r"(Color\(\s*(?:hex:\s*)?(?:0x|\"#?)[0-9A-Fa-f]{6}[^)]*\))", r"(Color\(\s*red:[^)]*\))",
              r"(Color\(\s*white:[^)]*\))", r"(UIColor\(\s*red:[^)]*\))", r"(#colorLiteral\([^)]*\))"],
    "shadow": [r"\.shadow\(([^\n]*?radius:\s*\d[^\n]*)"],   # color: .black.opacity(…) nests parens
}
SWIFT_TOKEN_USE = {
    "spacing": r"\.padding\(\s*(?:\.\w+\s*,\s*)?[A-Za-z_]", "radius": r"cornerRadius:\s*[A-Za-z_]|\.cornerRadius\(\s*[A-Za-z_]",
    "font": r"\.font\(\s*[A-Z][\w.]*\.\w+\s*\)",
}
WEB = {
    "spacing": [r"(?:^|[\s;{])(?:padding|margin|gap|row-gap|column-gap)(?:-(?:top|right|bottom|left|inline|block))?\s*:\s*(\d+(?:\.\d+)?)px",
                r"\b(?:p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml|gap|space-x|space-y)-\[(\d+(?:\.\d+)?)px\]",
                r"\b(?:padding|margin|gap):\s*(\d+(?:\.\d+)?)\s*[,}]"],
    "radius": [r"border-radius\s*:\s*(\d+(?:\.\d+)?)px", r"\brounded(?:-[trblse]{1,2})?-\[(\d+(?:\.\d+)?)px\]",
               r"\bborderRadius:\s*(\d+(?:\.\d+)?)\b"],
    "font": [r"font-size\s*:\s*(\d+(?:\.\d+)?)px", r"\btext-\[(\d+(?:\.\d+)?)px\]", r"\bfontSize:\s*(\d+(?:\.\d+)?)\b"],
    "color": [r"(#[0-9A-Fa-f]{6}(?:[0-9A-Fa-f]{2})?)\b", r"(rgba?\([^)]*\))",
              # a framework palette class (text-gray-500) instead of a registry role
              r"\b(?:bg|text|border(?:-[trblxy])?|ring|outline|fill|stroke|from|via|to|divide|decoration|placeholder|accent|caret)-"
              r"((?:slate|gray|zinc|neutral|stone|red|orange|amber|yellow|lime|green|emerald|teal|cyan|sky|blue|indigo|violet|purple|fuchsia|pink|rose)"
              r"-(?:50|[1-9]00|950))\b"],
    "shadow": [r"box-shadow\s*:\s*(?!none|var\()([^;}]+)", r"\bshadow-\[([^\]]+)\]", r"\bboxShadow:\s*['\"]([^'\"]+)"],
}
EXTS = {".swift", ".css", ".scss", ".tsx", ".jsx", ".vue", ".svelte", ".html"}


# Motion that contradicts the motion authority, written inline instead of via motion tokens.
MOTION_SMELLS = {
    "swift": [(r"\.easeIn\s*\((?!.*easeInOut)", "ease-in on UI motion (exits and entrances ease out)"),
              (r"\.easeIn\b(?![A-Za-z(])", "ease-in on UI motion (exits and entrances ease out)")],
    "web": [(r"\bease-in\b(?!-out)", "ease-in on UI motion (exits and entrances ease out)"),
            (r"transition\s*:\s*all\b", "transition: all (animate only transform/opacity/colour)"),
            (r"\btransition-all\b", "transition-all (animate only transform/opacity/colour)")],
}


def _nums(values):
    """Numeric values only — an adopt draft can still hold TODO placeholders."""
    out = set()
    for v in values:
        try:
            out.add(float(v))
        except (TypeError, ValueError):
            pass
    return out


def scales(model):
    prims = model.get("primitives") or {}
    sp = prims.get("spacing") or {}
    named = spacing_scale(prims)
    unit = sp.get("unit", 4)
    unit = unit if isinstance(unit, (int, float)) else 4
    spacing = {"values": _nums(named.values()) | {0.0, float(unit)}, "unit": float(unit),
               "named": bool(named)}
    radius = _nums((prims.get("radius") or {}).values()) | {0.0}
    font = set(float(s["size"]) for s in type_styles(prims).values() if isinstance(s.get("size"), (int, float)))
    palette, names = {}, set()
    for ramp, stops in (prims.get("color") or {}).items():
        for stop, hexv in (stops or {}).items():
            palette[str(hexv).upper()[:7]] = f"{ramp}.{stop}"
            names.add(f"{ramp}.{stop}")
    return {"spacing": spacing, "radius": radius, "font": font, "palette": palette, "palette_names": names}


def on_scale(kind, value, sc):
    if kind == "shadow":
        return False          # a literal shadow is never the registry's — use an elevation token
    v = float(value)
    if kind == "spacing":
        s = sc["spacing"]
        return v in s["values"] if s["named"] else (v % s["unit"] == 0)
    if kind == "radius":
        return v in sc["radius"]
    if kind == "font":
        return v in sc["font"]
    return None


def token_files(root, model, exclude):
    """Swift files that define the theme (enum Brand {…}) — definitions, not usage."""
    acc = accessors(model)
    tops = {expr.split(".")[0] for table in acc.values() for expr in table.values()}
    out = set()
    for path, rel in walk_files(root, {".swift"}, exclude):
        text = path.read_text(encoding="utf-8", errors="replace")
        if any(re.search(rf"^\s*(?:public\s+)?enum\s+{re.escape(t)}\b", text, re.M) for t in tops):
            out.add(rel)
    return out  # CSS token files aren't skipped: their custom-property lines are ignored line by line


def duplicates_swift(rel, lines, acc_rev, radius_values):
    """Background/fill + the nearest corner radius (within 3 lines) = one surface pattern."""
    found = []
    rad = re.compile(r"cornerRadius:\s*([\w.]+)|\.cornerRadius\(\s*([\w.]+)\s*\)")
    for i, line in enumerate(lines):
        m = re.search(r"\.background\(\s*([^,)]+(?:\([^)]*\))?)", line) or re.search(r"\.fill\(\s*([^)]+)\)", line)
        if not m:
            continue
        r = None
        for off in (0, 1, -1, 2, -2, 3, -3):
            if 0 <= i + off < len(lines):
                r = rad.search(lines[i + off].split("//", 1)[0])
                if r:
                    break
        if not r:
            continue
        bg = re.sub(r"\s+", "", m.group(1)).split(",in:")[0]
        radius = r.group(1) or r.group(2)
        radius = acc_rev.get(radius, radius)
        if re.fullmatch(r"\d+(\.\d+)?", radius) and float(radius) in radius_values:
            radius = f"{radius_values[float(radius)]} (literal {radius})"
        found.append({"file": rel, "line": i + 1, "surface": acc_rev.get(bg, bg), "radius": radius})
    return found


def duplicates_web(rel, text):
    found = []
    for m in re.finditer(r"class(?:Name)?=\{?[\"'`]([^\"'`]+)[\"'`]", text):
        classes = m.group(1).split()
        bg = sorted(c for c in classes if c.startswith("bg-"))
        rounded = sorted(c for c in classes if c.startswith("rounded"))
        if bg and rounded:
            line = text[:m.start()].count("\n") + 1
            found.append({"file": rel, "line": line, "surface": " ".join(bg), "radius": " ".join(rounded)})
    return found


def audit(root, model, comps=None, exclude=(), include_token_files=False):
    sc = scales(model)
    acc = accessors(model)
    acc_rev = {}
    for group, table in acc.items():
        for key, expr in table.items():
            acc_rev[expr] = key if group == "colors" else f"{group}.{key}"
    radius_values = {float(v): f"radius.{k}" for k, v in ((model.get("primitives") or {}).get("radius") or {}).items()
                     if isinstance(v, (int, float))}
    skip = set() if include_token_files else token_files(root, model, exclude)
    findings, token_uses, dups, files_scanned = [], {"spacing": 0, "radius": 0, "font": 0}, [], 0
    motion = []
    copy_files = []
    swift_seen = False
    for path, rel in walk_files(root, EXTS, exclude):
        if rel in skip or rel.startswith("design/"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if is_generated(text):
            continue
        files_scanned += 1
        copy_files.append((path, rel, text))
        swift = path.suffix == ".swift"
        swift_seen = swift_seen or swift
        table = SWIFT if swift else WEB
        lines = text.split("\n")
        for n, line in enumerate(lines, 1):
            code = line.split("//", 1)[0] if swift else line
            if not swift and re.match(r"\s*--[\w-]+\s*:", code):
                continue  # a custom-property definition, not a usage
            for kind, pats in table.items():
                for pat in pats:
                    for m in re.finditer(pat, code):
                        raw = m.group(1)
                        f = {"file": rel, "line": n, "kind": kind, "value": raw, "text": line.strip()[:120]}
                        if kind == "color":
                            cls = re.fullmatch(r"([a-z]+)-(\d+)", raw)
                            if cls:   # a palette class counts only when the registry has that ramp and stop
                                prim = f"{cls.group(1)}.{cls.group(2)}"
                                prim = prim if prim in sc["palette_names"] else None
                            else:
                                hexm = re.search(r"(?:0x|#)([0-9A-Fa-f]{6})", raw)
                                prim = sc["palette"].get("#" + hexm.group(1).upper()) if hexm else None
                            f["on_scale"] = bool(prim)
                            f["token"] = prim
                        else:
                            f["on_scale"] = on_scale(kind, raw, sc)
                        findings.append(f)
            for pat, why in MOTION_SMELLS["swift" if swift else "web"]:
                if re.search(pat, code):
                    motion.append({"file": rel, "line": n, "why": why, "text": line.strip()[:120]})
                    break
            if swift:
                for kind, pat in SWIFT_TOKEN_USE.items():
                    token_uses[kind] += len(re.findall(pat, code))
        dups += duplicates_swift(rel, lines, acc_rev, radius_values) if swift else duplicates_web(rel, text)

    for path, rel in walk_files(root, CATALOG_EXTS, exclude):   # string catalogs and locale files
        if not rel.startswith("design/"):
            copy_files.append((path, rel, path.read_text(encoding="utf-8", errors="replace")))
    copy = copy_findings(copy_files)

    summary = {}
    for kind in ("spacing", "radius", "color", "font", "shadow"):
        fs = [f for f in findings if f["kind"] == kind]
        off = [f for f in fs if f["on_scale"] is False]
        hist = {}
        for f in off:
            hist[f["value"]] = hist.get(f["value"], 0) + 1
        summary[kind] = {"literals": len(fs), "on_scale": len(fs) - len(off), "off_scale": len(off),
                         "off_scale_values": dict(sorted(hist.items(), key=lambda kv: -kv[1])),
                         "token_uses": token_uses.get(kind) if swift_seen else None}
    groups = {}
    for d in dups:
        groups.setdefault((d["surface"], d["radius"]), []).append(d)
    comp_list = components(comps)
    dup_out = []
    for (surface, radius), items in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        if len(items) < 2:
            continue
        files = sorted({i["file"] for i in items})
        rtok = radius.split(" ")[0]
        match = [c.get("name") for c in comp_list
                 if surface in (c.get("tokens") or []) and rtok in (c.get("tokens") or [])]
        dup_out.append({"surface": surface, "radius": radius, "count": len(items), "files": files,
                        "sites": [f"{i['file']}:{i['line']}" for i in items],
                        "rule_of_three": len(items) >= 3, "registered": match})
    return {"root": str(root), "files_scanned": files_scanned, "skipped_token_files": sorted(skip),
            "summary": summary, "duplicates": dup_out, "findings": findings, "motion": motion, "copy": copy,
            "total_literals": len(findings), "total_off_scale": sum(1 for f in findings if f["on_scale"] is False)}


def format_report(rep, limit=15):
    L = [f"Design audit — {rep['files_scanned']} files scanned"
         + (f" (skipped token files: {', '.join(rep['skipped_token_files'])})" if rep["skipped_token_files"] else "")]
    L.append(f"Raw literals: {rep['total_literals']} · off-scale: {rep['total_off_scale']}")
    for kind, s in rep["summary"].items():
        vals = ", ".join(f"{v}×{n}" for v, n in list(s["off_scale_values"].items())[:8])
        line = f"  {kind:8} {s['literals']:4} literals · {s['on_scale']} on-scale (use the token) · {s['off_scale']} off-scale"
        if s.get("token_uses") is not None:
            line += f" · {s['token_uses']} token uses"
        L.append(line + (f"  [{vals}]" if vals else ""))
    if rep["duplicates"]:
        L.append("Repeated surface + radius combinations:")
        for d in rep["duplicates"]:
            tag = "rule of three reached — promote" if d["rule_of_three"] else "watch"
            if d["registered"]:
                tag = f"use registered {', '.join(d['registered'])}"
            L.append(f"  {d['count']}× surface={d['surface']} radius={d['radius']} in {len(d['files'])} file(s) — {tag}")
            L.append(f"     {', '.join(d['sites'][:6])}{' …' if len(d['sites']) > 6 else ''}")
    if rep.get("motion"):
        L.append(f"Motion against the motion guidance ({len(rep['motion'])}):")
        for m in rep["motion"][:limit]:
            L.append(f"  {m['file']}:{m['line']}  {m['why']}  — {m['text']}")
    if rep.get("copy"):
        L.append(f"Copy against Ship's copy rules ({len(rep['copy'])}):")
        for c in rep["copy"][:limit]:
            where = f"{c['file']}:{c['line']}" if c["line"] else c["file"]
            L.append(f"  {where}  {c['rule']}: {c['why']}  ({c['text']})")
    off = [f for f in rep["findings"] if f["on_scale"] is False]
    if off:
        L.append(f"Off-scale sites (first {min(limit, len(off))}):")
        for f in off[:limit]:
            L.append(f"  {f['file']}:{f['line']}  {f['kind']} {f['value']}  — {f['text']}")
    return "\n".join(L)
