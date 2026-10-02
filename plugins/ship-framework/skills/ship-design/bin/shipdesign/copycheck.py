"""Copy check: the words people read in the product, against Ship's copy rules.

Reads only user-facing text: SwiftUI strings (Text, Button, Label, titles, alerts, accessibility
labels), JSX/HTML text and text props, and string catalogs (.xcstrings, .strings, locale JSON).
Code, comments and identifiers are left alone. Each finding names the rule and the fix
(copy-clarity.md §2–3, typography.md §5, psychology.md). Findings are checks, never errors: the
product's own decisions win, and a reviewer judges them.
"""

import json
import re
from pathlib import Path

RULES = [
    ("dash", re.compile(r"\s[—–-]\s|[A-Za-z][—][A-Za-z]|\d\s?[–—]\s?\d"),
     "a dash as punctuation: use a period, a comma, a colon or parentheses; ranges read \"7:30 to 13:00\""),
    ("ellipsis", re.compile(r"(?<!\.)\.\.\.(?!\.)"),
     "three dots: use the ellipsis character …"),
    ("link text", re.compile(r"^\s*(?:learn more|read more|more|click here|tap here)\s*[.…]?\s*$|\b(?:click|tap) here\b", re.I),
     "link text that doesn't name its destination: say where it goes (\"Pricing details\")"),
    ("please", re.compile(r"\bplease\b", re.I),
     "\"please\" in an instruction: say what to do"),
    ("abbreviation", re.compile(r"\b(?:e\.g\.|i\.e\.|etc\.)", re.I),
     "a Latin abbreviation: \"for example\", \"that is\", or the list itself"),
    ("vague error", re.compile(r"\b(?:invalid|an error (?:has )?occurred|something went wrong|oops)\b", re.I),
     "a vague error: say what happened and how to fix it"),
]
LONG_SENTENCE = 25   # words

SWIFT_STRING = re.compile(
    r"\b(?:Text|Button|Label|Toggle|TextField|SecureField|Section|Link|Picker|Menu|NavigationLink|"
    r"LocalizedStringKey|LabeledContent|ContentUnavailableView)\(\s*\"((?:[^\"\\]|\\.)*)\"|"
    r"\.(?:navigationTitle|alert|confirmationDialog|help|accessibilityLabel|accessibilityHint|badge)\(\s*\"((?:[^\"\\]|\\.)*)\"|"
    r"String\(localized:\s*\"((?:[^\"\\]|\\.)*)\"")
WEB_TEXT = re.compile(r">([^<>{}]*[A-Za-z]{2}[^<>{}]*)<")
WEB_PROP = re.compile(r"\b(?:placeholder|title|alt|aria-label|label)=(?:\"([^\"]+)\"|'([^']+)')")
CODEISH = re.compile(r"[=;(){}\[\]]|&&|\|\||=>|\bconst\b|\breturn\b")
LOCALE_DIRS = {"locales", "locale", "i18n", "lang", "langs", "messages", "translations"}
TEXT_EXTS = {".swift", ".tsx", ".jsx", ".vue", ".svelte", ".html"}
CATALOG_EXTS = {".xcstrings", ".strings", ".json"}


def strings_in(path, text):
    """(line, string) pairs a person reads in this file."""
    suffix = path.suffix.lower()
    out = []
    if suffix == ".swift":
        for n, line in enumerate(text.split("\n"), 1):
            code = line.split("//", 1)[0]
            for m in SWIFT_STRING.finditer(code):
                s = next(g for g in m.groups() if g is not None)
                if s.strip():
                    out.append((n, s))
    elif suffix in (".tsx", ".jsx", ".vue", ".svelte", ".html"):
        body = re.sub(r"<(script|style)\b.*?</\1>", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S | re.I)
        body = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group(0).count("\n"), body, flags=re.S)
        for m in WEB_TEXT.finditer(body):
            s = " ".join(m.group(1).split())
            if s and not CODEISH.search(s):
                out.append((body[:m.start()].count("\n") + 1, s))
        for m in WEB_PROP.finditer(body):
            s = m.group(1) or m.group(2)
            out.append((body[:m.start()].count("\n") + 1, s))
    elif suffix == ".strings":
        for n, line in enumerate(text.split("\n"), 1):
            m = re.match(r'\s*"(?:[^"\\]|\\.)*"\s*=\s*"((?:[^"\\]|\\.)*)"\s*;', line)
            if m:
                out.append((n, m.group(1)))
    elif suffix == ".xcstrings":
        try:
            data = json.loads(text)
        except ValueError:
            return out
        for key, entry in (data.get("strings") or {}).items():
            out.append((0, key))
            for loc in ((entry or {}).get("localizations") or {}).values():
                value = ((loc or {}).get("stringUnit") or {}).get("value")
                if value:
                    out.append((0, value))
    elif suffix == ".json" and LOCALE_DIRS & {p.lower() for p in path.parts}:
        try:
            data = json.loads(text)
        except ValueError:
            return out
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                stack += list(node.values())
            elif isinstance(node, list):
                stack += node
            elif isinstance(node, str) and node.strip():
                out.append((0, node))
    return out


def check_string(s):
    """[(rule, why)] for one string."""
    found = [(name, why) for name, rx, why in RULES if rx.search(s)]
    for sentence in re.split(r"(?<=[.!?])\s+", s):
        if len(sentence.split()) > LONG_SENTENCE:
            found.append(("long sentence", f"a sentence over {LONG_SENTENCE} words: split it"))
            break
    return found


def check_css(rel, text):
    """Justified text without hyphenation leaves gaps between words."""
    if "hyphens" in text:
        return []
    return [{"file": rel, "line": text[:m.start()].count("\n") + 1, "rule": "justify",
             "why": "justified text without hyphens: align reading text to the start", "text": m.group(0)}
            for m in re.finditer(r"text-align\s*:\s*justify\b", text)]


def copy_findings(files):
    """files: (path, rel, text). Returns findings: {file, line, rule, why, text}."""
    out = []
    for path, rel, text in files:
        if Path(rel).suffix.lower() in (".css", ".scss"):
            out += check_css(rel, text)
            continue
        for line, s in strings_in(path, text):
            for rule, why in check_string(s):
                out.append({"file": rel, "line": line, "rule": rule, "why": why, "text": s[:120]})
    return out
