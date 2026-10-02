"""Stdlib-only YAML subset used by the design registry (no PyYAML on macOS system Python).

Parses what the schema uses: block mappings/lists, flow {…} and […], quoted/bare scalars,
`>` folded and `|` literal text, trailing comments.
"""

import re

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
        raise YamlError(f"a {{ … }} or [ … ] value must close on the same line (Ship reads a small YAML subset; keep each entry on one line): {text}")
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
        raise YamlError(f"unexpected indentation near: {lines[pos][1]} (a value that wraps onto the next line? Ship reads a small YAML subset: keep each value on one line)")
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


# ── Writer (for drafts the tool creates; comments are the caller's job) ─────────

_BARE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-/ ]*$")


def _scalar_out(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return f"{v:g}" if isinstance(v, float) else str(v)
    s = str(v)
    if (_BARE.match(s) and s.strip() == s and s not in ("true", "false", "null", "~")
            and not re.fullmatch(r"-?\d+(\.\d+)?", s)):
        return s
    return '"' + s.replace('\\', '\\\\').replace('"', '\\"') + '"'


def _key_out(k):
    s = str(k)
    return s if re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_.\-]*", s) else _scalar_out(s)


def _flow(v):
    if isinstance(v, dict):
        return "{ " + ", ".join(f"{_key_out(k)}: {_flow(x)}" for k, x in v.items()) + " }" if v else "{}"
    if isinstance(v, list):
        return "[" + ", ".join(_flow(x) for x in v) + "]"
    return _scalar_out(v)


def _leafy(v):
    """Small, flat collections read best as one flow line."""
    if isinstance(v, dict):
        return all(not isinstance(x, (dict, list)) or (isinstance(x, list) and all(not isinstance(y, (dict, list)) for y in x))
                   for x in v.values()) and len(_flow(v)) <= 96
    if isinstance(v, list):
        return all(not isinstance(x, (dict, list)) for x in v) and len(_flow(v)) <= 96
    return True


def dump_yaml(obj, indent=0):
    """Block-style YAML the subset parser reads back (round-trip tested)."""
    pad = " " * indent
    out = []
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(v, (dict, list)) and v and not _leafy(v):
                out.append(f"{pad}{_key_out(k)}:")
                out.append(dump_yaml(v, indent + 2))
            else:
                out.append(f"{pad}{_key_out(k)}: {_flow(v)}")
    elif isinstance(obj, list):
        for item in obj:
            if isinstance(item, dict) and item and not _leafy(item):
                first = True
                for k, v in item.items():
                    lead = f"{pad}- " if first else f"{pad}  "
                    first = False
                    if isinstance(v, (dict, list)) and v and not _leafy(v):
                        out.append(f"{lead}{_key_out(k)}:")
                        out.append(dump_yaml(v, indent + 4))
                    else:
                        out.append(f"{lead}{_key_out(k)}: {_flow(v)}")
            else:
                out.append(f"{pad}- {_flow(item)}")
    return "\n".join(out)
