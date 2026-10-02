#!/usr/bin/env python3
"""Ship taste store — the founder's design judgments, captured with evidence and reused
in the right context.

Two plain-text stores (same YAML shape, schema in ../references/taste-schema.md):
  product scope   <project>/design/taste.yaml     decisions, inferences, expert stances
  founder scope   $SHIP_HOME/taste.yaml           cross-product preferences, expert stances
                  (SHIP_HOME defaults to ~/.ship)

    taste.py add        --kind decision --topic card-elevation --statement ... --rationale ...
                        --source correction --quote "..." [--platform ios --domain layout ...]
    taste.py query      [--platform ios --surface home --component card --domain motion ...]
    taste.py list|show  [ID] [--all] [filters]
    taste.py supersede  ID --statement ... --rationale ... --quote ...
    taste.py confirm    ID --quote "..."          inference -> product decision
    taste.py reject     ID --quote "..."          inference -> rejected (kept on record)
    taste.py promote    ID --confirmed-by-founder "..."   product -> founder scope
    taste.py export-md  [--out PATH]              readable view (generated, not a source)
    taste.py import-learnings [--file LEARNINGS.md]  "## Design Preferences" -> inferences
    taste.py check | summary | init

Exit codes: 0 ok · 1 refused/usage · 2 malformed store · 3 unresolved conflict (query --strict).
Stdlib only; Python 3.9+.
"""

import argparse
import datetime
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path

SCHEMA = 1
KINDS = ("decision", "preference", "inference", "expert")
SCOPE_KINDS = {"product": ("decision", "inference", "expert"),
               "founder": ("preference", "expert")}
STATUSES = ("active", "superseded", "confirmed", "rejected")
SOURCES = ("approval", "rejection", "correction", "example", "inference")
CONTEXT_FIELDS = ("platform", "surface", "component", "domain", "product_type")
EVIDENCE_FIELDS = ("date", "quote", "file", "commit", "screenshot", "url", "note")
STANCES = ("accept", "override")
ALIASES = {"colour": "color", "colors": "color", "colours": "color", "animation": "motion",
           "typography": "type", "microcopy": "copy", "iphone": "ios", "ipad": "ios"}
WILDCARDS = ("*", "any", "all")
ENTRY_KEYS = ("id", "kind", "status", "source", "topic", "statement", "rationale", "context",
              "expert", "evidence", "recorded", "confirmed_by_founder", "overrides",
              "supersedes", "superseded_by", "derived_from", "promoted_from", "promoted_to",
              "imported_from", "status_note")
ID_RE = {"product": re.compile(r"^t-\d{4}-\d{2}-\d{2}-\d{3}$"),
         "founder": re.compile(r"^tf-\d{4}-\d{2}-\d{2}-\d{3}$")}
TOPIC_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
PRODUCT_REL = Path("design") / "taste.yaml"


def _tool():
    """How to call this script from the project root (works for template and plugin installs)."""
    me = Path(__file__).resolve()
    try:
        return "python3 " + str(me.relative_to(find_root(None)))
    except ValueError:
        return f"python3 {me}"


class StoreError(Exception):
    """Malformed store — always fatal, never read as empty."""


class Refused(Exception):
    """The operation is not allowed as asked (missing confirmation, wrong kind, ...)."""


def today():
    return datetime.date.today().isoformat()


# ── YAML subset ──────────────────────────────────────────────────────────────
# Block mappings, block sequences (of scalars or mappings), flow [a, "b"] lists, {} and
# [] empties, double-quoted (JSON escapes) / single-quoted / plain scalars, # comments.
# Anything else (anchors, block scalars, multi-doc) is rejected with a line number.

PLAIN_SAFE = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-/+@]*$")
RESERVED = {"true", "false", "null", "yes", "no", "on", "off", "y", "n", "~"}
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):(?:\s+(.*))?$")


def _strip_comment(text):
    quote = None
    i = 0
    while i < len(text):
        ch = text[i]
        if quote == '"' and ch == "\\":
            i += 2
            continue
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'" and (i == 0 or text[i - 1] in " \t[,-:"):
            quote = ch
        elif ch == "#" and (i == 0 or text[i - 1] in " \t"):
            return text[:i].rstrip()
        i += 1
    return text.rstrip()


def _scalar(text, where):
    t = text.strip()
    if not t:
        return None
    if t[0] == '"':
        try:
            val = json.loads(t)
        except ValueError:
            raise StoreError(f"{where}: bad double-quoted string {t[:40]!r}")
        if not isinstance(val, str):
            raise StoreError(f"{where}: bad double-quoted string {t[:40]!r}")
        return val
    if t[0] == "'":
        if len(t) < 2 or t[-1] != "'":
            raise StoreError(f"{where}: unterminated single-quoted string")
        return t[1:-1].replace("''", "'")
    if t[0] in "|>":
        raise StoreError(f"{where}: block scalars ({t[0]}) are not supported — use a quoted string")
    if t[0] in "&*!%@`":
        raise StoreError(f"{where}: YAML anchors/tags are not supported")
    if t[0] == "[":
        if not t.endswith("]"):
            raise StoreError(f"{where}: unterminated flow list")
        inner = t[1:-1].strip()
        if not inner:
            return []
        return [_scalar(p, where) for p in _split_flow(inner, where)]
    if t[0] == "{":
        if t.replace(" ", "") != "{}":
            raise StoreError(f"{where}: only empty flow mappings {{}} are supported")
        return {}
    if t in ("true", "false"):
        return t == "true"
    if t in ("null", "~"):
        return None
    if re.fullmatch(r"-?\d+", t):
        return int(t)
    if ": " in t or t.endswith(":"):
        raise StoreError(f"{where}: unexpected ':' in value {t[:40]!r} — quote it")
    return t


def _split_flow(inner, where):
    parts, buf, quote, i = [], "", None, 0
    while i < len(inner):
        ch = inner[i]
        if quote == '"' and ch == "\\":
            buf += inner[i:i + 2]
            i += 2
            continue
        if quote:
            buf += ch
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch in "[]{}":
            raise StoreError(f"{where}: nested flow collections are not supported")
        elif ch == ",":
            parts.append(buf)
            buf = ""
        else:
            buf += ch
        i += 1
    if quote:
        raise StoreError(f"{where}: unterminated string in flow list")
    parts.append(buf)
    return [p for p in parts if p.strip()]


def load_yaml(text, path):
    lines = []
    for n, raw in enumerate(text.splitlines(), 1):
        if raw.strip().startswith("#") or not raw.strip():
            continue
        if raw.strip() in ("---", "..."):
            raise StoreError(f"{path}:{n}: multi-document YAML is not supported")
        body = raw.rstrip()
        lead = body[:len(body) - len(body.lstrip())]
        if "\t" in lead:
            raise StoreError(f"{path}:{n}: tab indentation — use spaces")
        lines.append([n, len(lead), _strip_comment(body.lstrip())])
    if not lines:
        raise StoreError(f"{path}: file is empty — expected `schema: {SCHEMA}` and `entries:`")
    pos = [0]

    def where(i):
        return f"{path}:{lines[i][0]}"

    def is_seq(content):
        return content == "-" or content.startswith("- ")

    def parse_block(indent):
        return parse_seq(indent) if is_seq(lines[pos[0]][2]) else parse_map(indent)

    def parse_map(indent):
        out = {}
        while pos[0] < len(lines):
            n, ind, content = lines[pos[0]]
            if ind < indent:
                break
            if ind > indent:
                raise StoreError(f"{where(pos[0])}: unexpected indentation")
            if is_seq(content):
                raise StoreError(f"{where(pos[0])}: list item where a key was expected")
            m = KEY_RE.match(content)
            if not m:
                raise StoreError(f"{where(pos[0])}: expected `key: value`, got {content[:40]!r}")
            key, rest = m.group(1), (m.group(2) or "").strip()
            if key in out:
                raise StoreError(f"{where(pos[0])}: duplicate key '{key}'")
            here = where(pos[0])
            pos[0] += 1
            if rest:
                out[key] = _scalar(rest, here)
            elif pos[0] < len(lines) and (lines[pos[0]][1] > indent or
                                          (lines[pos[0]][1] == indent and is_seq(lines[pos[0]][2]))):
                out[key] = parse_block(lines[pos[0]][1])
            else:
                out[key] = None
        return out

    def parse_seq(indent):
        out = []
        while pos[0] < len(lines):
            n, ind, content = lines[pos[0]]
            if ind < indent or (ind == indent and not is_seq(content)):
                break
            if ind > indent:
                raise StoreError(f"{where(pos[0])}: unexpected indentation")
            after = content[1:]
            body = after.lstrip()
            if not body:
                pos[0] += 1
                if pos[0] < len(lines) and lines[pos[0]][1] > indent:
                    out.append(parse_block(lines[pos[0]][1]))
                else:
                    out.append(None)
            elif KEY_RE.match(body) and body[0] not in "\"'":
                lines[pos[0]] = [n, indent + 1 + len(after) - len(body), body]
                out.append(parse_map(lines[pos[0]][1]))
            else:
                out.append(_scalar(body, where(pos[0])))
                pos[0] += 1
        return out

    if lines[0][1] != 0:
        raise StoreError(f"{where(0)}: top level must start at column 0")
    result = parse_block(0)
    if pos[0] != len(lines):
        raise StoreError(f"{where(pos[0])}: unexpected content")
    return result


def _emit_scalar(v):
    if v is None:
        return "null"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, int):
        return str(v)
    s = str(v)
    if PLAIN_SAFE.match(s) and s.lower() not in RESERVED:
        return s
    return json.dumps(s, ensure_ascii=False)


def dump_yaml(node, indent=0):
    pad = " " * indent
    out = []
    if isinstance(node, dict):
        for k, v in node.items():
            if isinstance(v, dict) and v:
                out.append(f"{pad}{k}:")
                out.extend(dump_yaml(v, indent + 2))
            elif isinstance(v, list) and v and any(isinstance(x, (dict, list)) for x in v):
                out.append(f"{pad}{k}:")
                out.extend(dump_yaml(v, indent + 2))
            elif isinstance(v, dict):
                out.append(f"{pad}{k}: {{}}")
            elif isinstance(v, list):
                out.append(f"{pad}{k}: [{', '.join(_emit_scalar(x) for x in v)}]")
            else:
                out.append(f"{pad}{k}: {_emit_scalar(v)}")
    elif isinstance(node, list):
        for item in node:
            if isinstance(item, dict) and item:
                sub = dump_yaml(item, indent + 2)
                sub[0] = f"{pad}- " + sub[0][indent + 2:]
                out.extend(sub)
            else:
                out.append(f"{pad}- {_emit_scalar(item)}")
    return out


# ── Stores ───────────────────────────────────────────────────────────────────

HEADER = {
    "product": ("# Ship taste store — product scope: this product's design judgments.\n"
                "# Source of truth. Change it through taste.py (supersede, confirm, reject, promote);\n"
                "# entries are never deleted. Schema: ship taste skill, references/taste-schema.md\n"),
    "founder": ("# Ship taste store — founder scope: preferences that follow you across products.\n"
                "# Written only with the founder's recorded confirmation (taste.py promote / add\n"
                "# --confirmed-by-founder). Schema: ship-taste references/taste-schema.md\n"),
}


class Store:
    def __init__(self, scope, path):
        self.scope, self.path = scope, Path(path)
        self.product = {}
        self.entries = []
        self.exists = self.path.exists()
        if self.exists:
            self._load()

    def _load(self):
        try:
            text = self.path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            raise StoreError(f"{self.path}: cannot read ({exc})")
        data = load_yaml(text, self.path)
        errs = []
        if not isinstance(data, dict):
            raise StoreError(f"{self.path}: top level must be a mapping with `schema` and `entries`")
        if data.get("schema") != SCHEMA:
            errs.append(f"`schema` must be {SCHEMA} (found {data.get('schema')!r})")
        if data.get("scope") != self.scope:
            errs.append(f"`scope` must be '{self.scope}' in this file (found {data.get('scope')!r})")
        unknown = set(data) - {"schema", "scope", "product", "entries"}
        if unknown:
            errs.append(f"unknown top-level keys: {', '.join(sorted(unknown))}")
        prod = data.get("product") or {}
        if not isinstance(prod, dict):
            errs.append("`product` must be a mapping")
        else:
            self.product = prod
        entries = data.get("entries")
        if entries is None:
            entries = []
        if not isinstance(entries, list):
            errs.append("`entries` must be a list")
            entries = []
        seen = set()
        for i, e in enumerate(entries):
            errs.extend(validate_entry(e, self.scope, i, seen))
        ids = {e.get("id") for e in entries if isinstance(e, dict)}
        for e in entries:
            if isinstance(e, dict) and e.get("superseded_by") and e["superseded_by"] not in ids:
                errs.append(f"{e.get('id')}: superseded_by '{e['superseded_by']}' is not in this store")
        if errs:
            raise StoreError(f"{self.path}: malformed taste store:\n  - " + "\n  - ".join(errs))
        self.entries = entries

    def get(self, eid):
        for e in self.entries:
            if e["id"] == eid:
                return e
        return None

    def next_id(self, date=None):
        date = date or today()
        prefix = ("t-" if self.scope == "product" else "tf-") + date + "-"
        nums = [int(e["id"][len(prefix):]) for e in self.entries if e["id"].startswith(prefix)]
        return f"{prefix}{(max(nums) + 1 if nums else 1):03d}"

    def save(self):
        doc = {"schema": SCHEMA, "scope": self.scope}
        if self.product:
            doc["product"] = self.product
        doc["entries"] = [canonical(e) for e in self.entries]
        text = HEADER[self.scope] + "\n".join(dump_yaml(doc)) + "\n"
        load_yaml(text, self.path)  # never write something we cannot read back
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(prefix=".taste-", dir=str(self.path.parent))
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, self.path)
        self.exists = True


def canonical(e):
    out = {k: e[k] for k in ENTRY_KEYS if k in e and e[k] not in (None, "", [])}
    out["context"] = {k: e.get("context", {})[k] for k in CONTEXT_FIELDS if e.get("context", {}).get(k)}
    return {k: out[k] for k in ENTRY_KEYS if k in out}


def validate_entry(e, scope, i, seen):
    label = f"entry {i + 1}"
    if not isinstance(e, dict):
        return [f"{label}: must be a mapping"]
    errs = []
    eid = e.get("id")
    label = f"entry {i + 1} ({eid})" if eid else label
    if not isinstance(eid, str) or not ID_RE[scope].match(eid):
        want = "t-YYYY-MM-DD-NNN" if scope == "product" else "tf-YYYY-MM-DD-NNN"
        errs.append(f"{label}: id must look like {want}")
    elif eid in seen:
        errs.append(f"{label}: duplicate id")
    seen.add(eid)
    unknown = set(e) - set(ENTRY_KEYS)
    if unknown:
        errs.append(f"{label}: unknown keys {', '.join(sorted(unknown))}")
    if e.get("kind") not in SCOPE_KINDS[scope]:
        errs.append(f"{label}: kind must be one of {', '.join(SCOPE_KINDS[scope])} in {scope} scope")
    if e.get("status") not in STATUSES:
        errs.append(f"{label}: status must be one of {', '.join(STATUSES)}")
    if e.get("source") not in SOURCES:
        errs.append(f"{label}: source must be one of {', '.join(SOURCES)}")
    if (e.get("kind") == "inference") != (e.get("source") == "inference"):
        errs.append(f"{label}: kind 'inference' and source 'inference' go together")
    for field in ("statement", "rationale"):
        if not isinstance(e.get(field), str) or not e[field].strip():
            errs.append(f"{label}: {field} is required")
    topic = e.get("topic")
    if topic is not None and (not isinstance(topic, str) or not TOPIC_RE.match(topic)):
        errs.append(f"{label}: topic must be a lowercase-hyphenated slug")
    ctx = e.get("context", {})
    if ctx is None:
        ctx = {}
    if not isinstance(ctx, dict):
        errs.append(f"{label}: context must be a mapping")
    else:
        for k, v in ctx.items():
            if k not in CONTEXT_FIELDS:
                errs.append(f"{label}: unknown context field '{k}'")
            elif not isinstance(v, list) or not all(isinstance(x, str) for x in v):
                errs.append(f"{label}: context.{k} must be a list of strings")
    ev = e.get("evidence")
    if not isinstance(ev, list) or not ev:
        errs.append(f"{label}: evidence must be a non-empty list")
    else:
        for item in ev:
            if not isinstance(item, dict) or set(item) - set(EVIDENCE_FIELDS):
                errs.append(f"{label}: evidence items are mappings of {', '.join(EVIDENCE_FIELDS)}")
                break
    if e.get("kind") == "expert":
        ex = e.get("expert")
        if not isinstance(ex, dict) or not ex.get("ref") or ex.get("stance") not in STANCES:
            errs.append(f"{label}: expert entries need expert: {{ref, stance: accept|override}}")
    if scope == "founder" and e.get("status") == "active":
        cbf = e.get("confirmed_by_founder")
        if not isinstance(cbf, dict) or not cbf.get("quote"):
            errs.append(f"{label}: founder-scope entries need confirmed_by_founder.quote")
    if e.get("status") in ("superseded", "confirmed") and not e.get("superseded_by"):
        errs.append(f"{label}: status {e.get('status')} needs superseded_by")
    return errs


def find_root(explicit):
    if explicit:
        return Path(explicit).resolve()
    env = os.environ.get("CLAUDE_PROJECT_DIR")
    if env:
        return Path(env).resolve()
    here = Path.cwd().resolve()
    for d in [here] + list(here.parents):
        if (d / PRODUCT_REL).exists() or (d / ".ship" / "framework.yaml").exists() \
                or (d / "CLAUDE.md").exists() or (d / "AGENTS.md").exists() or (d / ".git").exists():
            return d
    return here


def founder_path():
    home = os.environ.get("SHIP_HOME")
    return (Path(home) if home else Path.home() / ".ship") / "taste.yaml"


def open_stores(args):
    root = find_root(getattr(args, "root", None))
    return root, Store("product", root / PRODUCT_REL), Store("founder", founder_path())


def store_for(eid, product, founder):
    if isinstance(eid, str) and eid.startswith("tf-"):
        return founder
    return product


# ── Context ──────────────────────────────────────────────────────────────────

def norm(v):
    v = re.sub(r"\s+", "-", v.strip().lower())
    return ALIASES.get(v, v)


def context_from(args):
    ctx = {}
    for f in CONTEXT_FIELDS:
        for raw in getattr(args, f, None) or []:
            for v in raw.split(","):
                if v.strip():
                    ctx.setdefault(f, []).append(norm(v))
    for raw in getattr(args, "context", None) or []:
        for pair in re.split(r"[;\s]+", raw.strip()):
            if not pair:
                continue
            if "=" not in pair:
                raise Refused(f"--context expects field=value pairs, got '{pair}'")
            k, v = pair.split("=", 1)
            k = k.strip().replace("-", "_")
            if k not in CONTEXT_FIELDS:
                raise Refused(f"unknown context field '{k}' (use {', '.join(CONTEXT_FIELDS)})")
            for x in v.split(","):
                if x.strip():
                    ctx.setdefault(k, []).append(norm(x))
    return {k: sorted(set(v)) for k, v in ctx.items()}


def matches(entry_ctx, query):
    """Entry applies unless a field both sides specify has no value in common."""
    score = 0
    for f, want in query.items():
        have = [norm(x) for x in (entry_ctx or {}).get(f, [])]
        if not have or any(h in WILDCARDS for h in have):
            continue
        if not set(have) & set(want):
            return None
        score += 1
    return score


def ctx_text(ctx):
    parts = [f"{k}={','.join(v)}" for k, v in (ctx or {}).items() if v]
    return " ".join(parts) if parts else "any context"


# ── Commands ─────────────────────────────────────────────────────────────────

def evidence_from(args, date=None):
    item = {"date": date or today()}
    for f in ("quote", "file", "commit", "screenshot", "url", "note"):
        v = getattr(args, f, None)
        if v:
            item[f] = v
    return item if len(item) > 1 else None


def active_on_topic(store, topic, kinds):
    return [e for e in store.entries
            if topic and e.get("topic") == topic and e["status"] == "active" and e["kind"] in kinds]


def cmd_add(args):
    root, product, founder = open_stores(args)
    kind = args.kind
    scope = args.scope or ("founder" if kind == "preference" else "product")
    if kind not in SCOPE_KINDS[scope]:
        raise Refused(f"kind '{kind}' does not live in {scope} scope "
                      f"({scope} holds {', '.join(SCOPE_KINDS[scope])}). A product-level judgment is a "
                      f"'decision'; a cross-product one is a founder 'preference'.")
    if (kind == "inference") != (args.source == "inference"):
        raise Refused("an agent's own guess is --kind inference --source inference; founder "
                      "approvals/rejections/corrections/examples are decisions or preferences")
    if scope == "founder" and not args.confirmed_by_founder:
        raise Refused("founder scope applies to every product — record the founder saying so: "
                      "--confirmed-by-founder \"<their words>\"")
    if kind == "expert" and (not args.ref or not args.stance):
        raise Refused("expert stances need --ref <reference path#section> and --stance accept|override")
    if not TOPIC_RE.match(args.topic or ""):
        raise Refused("--topic is required: a short lowercase-hyphenated slug (e.g. card-elevation); "
                      "reuse an existing topic when the judgment is about the same thing "
                      f"(`{_tool()} list --topics`)")
    ev = evidence_from(args)
    if not ev:
        raise Refused("evidence is required: --quote (founder's words), --file, --commit, --screenshot or --url")
    if kind != "inference" and args.source in ("approval", "rejection", "correction") and not args.quote \
            and not args.file and not args.screenshot and not args.url:
        raise Refused("an explicit founder event needs --quote (or the --file/--screenshot/--url they reacted to)")
    store = founder if scope == "founder" else product
    ranked = ("decision", "expert") if scope == "product" else ("preference", "expert")
    if kind != "inference":
        clash = active_on_topic(store, args.topic, ranked)
        if clash and not args.keep_both:
            ids = ", ".join(e["id"] for e in clash)
            raise Refused(f"topic '{args.topic}' already has an active {scope} entry ({ids}). If this "
                          f"replaces it: `{_tool()} supersede {clash[0]['id']} ...`. If both truly hold, "
                          "narrow the context or pass --keep-both.")
    entry = {"id": store.next_id(), "kind": kind, "status": "active", "source": args.source,
             "topic": args.topic, "statement": args.statement.strip(),
             "rationale": args.rationale.strip(), "context": context_from(args),
             "evidence": [ev], "recorded": today()}
    if kind == "expert":
        entry["expert"] = {"ref": args.ref, "stance": args.stance}
    if args.confirmed_by_founder:
        entry["confirmed_by_founder"] = {"quote": args.confirmed_by_founder, "date": today()}
    if args.overrides:
        if not founder.get(args.overrides) and not product.get(args.overrides):
            raise Refused(f"--overrides {args.overrides}: no such entry")
        entry["overrides"] = args.overrides
    store.entries.append(entry)
    store.save()
    print(f"recorded {entry['id']} ({scope} {kind}, topic {args.topic}) in {store.path}")
    if kind == "inference":
        higher = active_on_topic(product, args.topic, ("decision", "expert"))
        if higher:
            print(f"note: outranked by {higher[0]['id']} — an inference never overrides a decision")
    return 0


def cmd_supersede(args):
    root, product, founder = open_stores(args)
    store = store_for(args.id, product, founder)
    old = store.get(args.id)
    if not old:
        raise Refused(f"no entry {args.id} in {store.path}")
    if old["status"] != "active":
        raise Refused(f"{args.id} is {old['status']} (→ {old.get('superseded_by', '-')}); supersede the "
                      "active entry instead")
    if store.scope == "founder" and not args.confirmed_by_founder:
        raise Refused("changing a founder-scope preference changes every product — "
                      "--confirmed-by-founder \"<their words>\" is required")
    ev = evidence_from(args)
    if not ev:
        raise Refused("evidence is required: --quote, --file, --commit, --screenshot or --url")
    ctx = dict(old.get("context") or {})
    ctx.update(context_from(args))
    for f in args.clear or []:
        ctx.pop(f.replace("-", "_"), None)
    source = args.source or ("inference" if old["kind"] == "inference" else "correction")
    new = {"id": store.next_id(), "kind": old["kind"], "status": "active", "source": source,
           "topic": args.topic or old.get("topic"),
           "statement": (args.statement or old["statement"]).strip(),
           "rationale": args.rationale.strip(), "context": ctx, "evidence": [ev],
           "recorded": today(), "supersedes": old["id"]}
    for k in ("expert", "overrides"):
        if old.get(k):
            new[k] = old[k]
    if args.confirmed_by_founder:
        new["confirmed_by_founder"] = {"quote": args.confirmed_by_founder, "date": today()}
    old["status"], old["superseded_by"] = "superseded", new["id"]
    store.entries.append(new)
    store.save()
    print(f"{old['id']} superseded by {new['id']} (kept on record; `show {old['id']}` for history)")
    if old.get("promoted_to"):
        print(f"note: {old['promoted_to']} (founder scope) still holds the old judgment — supersede it "
              "too only if the founder says the change applies everywhere")
    return 0


def cmd_confirm(args):
    root, product, founder = open_stores(args)
    inf = product.get(args.id)
    if not inf or inf["kind"] != "inference":
        raise Refused(f"{args.id} is not an inference in {product.path}")
    if inf["status"] != "active":
        raise Refused(f"{args.id} is already {inf['status']}")
    topic = args.topic or inf.get("topic")
    if not topic or not TOPIC_RE.match(topic):
        raise Refused("this inference has no topic — pass --topic <slug> when confirming")
    clash = active_on_topic(product, topic, ("decision", "expert"))
    if clash and not args.keep_both:
        raise Refused(f"topic '{topic}' already has decision {clash[0]['id']}; if the founder's answer "
                      f"replaces it, `supersede {clash[0]['id']}` and `reject {args.id}` instead")
    ctx = dict(inf.get("context") or {})
    ctx.update(context_from(args))
    new = {"id": product.next_id(), "kind": "decision", "status": "active", "source": "approval",
           "topic": topic, "statement": (args.statement or inf["statement"]).strip(),
           "rationale": (args.rationale or inf["rationale"]).strip(), "context": ctx,
           "evidence": [{"date": today(), "quote": args.quote}] + list(inf.get("evidence") or []),
           "recorded": today(), "derived_from": inf["id"]}
    inf["status"], inf["superseded_by"] = "confirmed", new["id"]
    inf["status_note"] = f"founder confirmed {today()}"
    product.entries.append(new)
    product.save()
    print(f"{inf['id']} confirmed → decision {new['id']}")
    return 0


def cmd_reject(args):
    root, product, founder = open_stores(args)
    inf = product.get(args.id)
    if not inf:
        raise Refused(f"no entry {args.id} in {product.path}")
    if inf["kind"] != "inference":
        raise Refused(f"{args.id} is a {inf['kind']}, not an inference — founder judgments change "
                      f"through `supersede`, not `reject`")
    if inf["status"] != "active":
        raise Refused(f"{args.id} is already {inf['status']}")
    inf["status"] = "rejected"
    inf["status_note"] = f"founder rejected {today()}: \"{args.quote}\"" + \
        (f" — {args.reason}" if args.reason else "")
    product.save()
    print(f"{inf['id']} rejected (kept on record so it isn't re-proposed)")
    return 0


def cmd_promote(args):
    root, product, founder = open_stores(args)
    src = product.get(args.id)
    if not src:
        raise Refused(f"no entry {args.id} in {product.path}")
    if src["kind"] == "inference":
        raise Refused("inferences can't be promoted — `confirm` it with the founder first")
    if src["status"] != "active":
        raise Refused(f"{args.id} is {src['status']}; promote the active entry")
    if src.get("promoted_to"):
        raise Refused(f"{args.id} was already promoted to {src['promoted_to']}")
    if not args.confirmed_by_founder or not args.confirmed_by_founder.strip():
        raise Refused("promotion makes this apply to every product — --confirmed-by-founder "
                      "\"<the founder's words>\" is required")
    ctx = dict(src.get("context") or {})
    ctx.update(context_from(args))
    for f in args.clear or []:
        ctx.pop(f.replace("-", "_"), None)
    clash = active_on_topic(founder, src.get("topic"), ("preference", "expert"))
    if clash and not args.keep_both:
        raise Refused(f"founder scope already has {clash[0]['id']} on topic '{src.get('topic')}' — "
                      f"supersede it (with the founder's confirmation) instead")
    name = product.product.get("name") or root.name
    new = {"id": founder.next_id(), "kind": "preference" if src["kind"] == "decision" else "expert",
           "status": "active", "source": src["source"], "topic": src.get("topic"),
           "statement": src["statement"], "rationale": src["rationale"], "context": ctx,
           "evidence": list(src.get("evidence") or []), "recorded": today(),
           "confirmed_by_founder": {"quote": args.confirmed_by_founder.strip(), "date": today()},
           "promoted_from": f"{name}:{src['id']}"}
    if src.get("expert"):
        new["expert"] = src["expert"]
    founder.entries.append(new)
    founder.save()
    src["promoted_to"] = f"founder:{new['id']}"
    product.save()
    print(f"promoted {src['id']} → founder preference {new['id']} ({ctx_text(ctx)}) in {founder.path}")
    return 0


def rank_of(entry, scope):
    if entry["kind"] == "inference":
        return 4
    return 1 if scope == "product" else 2


LEVEL = {1: "product decision", 2: "founder preference", 4: "inference"}


def run_query(product, founder, qctx):
    hits = []
    for scope, store in (("product", product), ("founder", founder)):
        for e in store.entries:
            if e["status"] != "active":
                continue
            score = matches(e.get("context"), qctx)
            if score is None:
                continue
            hits.append({"entry": e, "scope": scope, "rank": rank_of(e, scope), "score": score,
                         "note": None, "applies": True})
    by_id = {h["entry"]["id"]: h for h in hits}
    conflicts = []
    # explicit overrides: a product decision that overrides a founder preference here
    for h in hits:
        tgt = h["entry"].get("overrides")
        if tgt in by_id and by_id[tgt]["rank"] > h["rank"]:
            by_id[tgt]["applies"] = False
            by_id[tgt]["note"] = f"overridden in this product by {h['entry']['id']}"
    # topic collisions
    topics = {}
    for h in hits:
        if h["entry"].get("topic"):
            topics.setdefault(h["entry"]["topic"], []).append(h)
    for topic, group in sorted(topics.items()):
        if len(group) < 2:
            continue
        group.sort(key=lambda h: h["rank"])
        top = group[0]["rank"]
        tops = [h for h in group if h["rank"] == top]
        if len(tops) > 1:
            distinct = {h["entry"]["statement"].strip().lower() for h in tops}
            if len(distinct) > 1:
                conflicts.append({"topic": topic, "unresolved": True,
                                  "ids": [h["entry"]["id"] for h in tops],
                                  "message": f"{len(tops)} active {LEVEL[top]}s disagree — ask the "
                                             "founder, then supersede one"})
        winner = tops[0]
        for h in group:
            if h["rank"] == top or not h["applies"]:
                continue
            same = h["entry"]["statement"].strip().lower() == winner["entry"]["statement"].strip().lower()
            h["applies"] = False
            if same:
                h["note"] = f"same judgment as {winner['entry']['id']}"
                continue
            h["note"] = f"outranked by {winner['entry']['id']}"
            conflicts.append({"topic": topic, "unresolved": False,
                              "ids": [winner["entry"]["id"], h["entry"]["id"]],
                              "message": f"{winner['entry']['id']} ({LEVEL[top]}) applies; "
                                         f"{h['entry']['id']} ({LEVEL[h['rank']]}) says otherwise"})
    hits.sort(key=lambda h: (h["rank"], -h["score"], h["entry"]["id"]))
    return hits, conflicts


def query_context(args, product):
    qctx = context_from(args)
    defaulted = []
    if not args.no_defaults:
        for f in ("platform", "product_type"):
            vals = product.product.get(f)
            if f not in qctx and isinstance(vals, list) and vals:
                qctx[f] = sorted({norm(v) for v in vals})
                defaulted.append(f)
    return qctx, defaulted


def brief(e):
    ev = (e.get("evidence") or [{}])[0]
    said = f"\"{ev['quote']}\"" if ev.get("quote") else (ev.get("file") or ev.get("screenshot")
                                                          or ev.get("commit") or "")
    if ev.get("url"):   # a reference the founder showed: keep the link where the next agent can open it
        said = f"{said} · {ev['url']}" if said else ev["url"]
    return f"{e['source']}, {ev.get('date', e.get('recorded', '?'))}" + (f": {said}" if said else "")


def cmd_query(args):
    root, product, founder = open_stores(args)
    qctx, defaulted = query_context(args, product)
    hits, conflicts = run_query(product, founder, qctx)
    unresolved = any(c["unresolved"] for c in conflicts)
    if args.json:
        print(json.dumps({"context": qctx, "defaulted_from_product": defaulted,
                          "results": [{"rank": h["rank"], "level": LEVEL[h["rank"]],
                                       "scope": h["scope"], "applies": h["applies"],
                                       "note": h["note"], **canonical(h["entry"])} for h in hits],
                          "conflicts": conflicts}, indent=2, ensure_ascii=False))
        return 3 if (args.strict and unresolved) else 0
    src = f" ({', '.join(defaulted)} from {PRODUCT_REL})" if defaulted else ""
    print(f"Taste for {ctx_text(qctx)}{src}")
    print("Order: platform/accessibility rules > product decisions > founder preferences > "
          "expert references > inferences.")
    if not hits:
        total = len([e for e in product.entries + founder.entries if e["status"] == "active"])
        print(f"No taste entries match. ({total} active outside this context — `taste.py list`)")
        return 0
    sections = [(1, "APPLY — product decisions"),
                (2, "APPLY — founder preferences (matched by context)"),
                (4, "ASK FIRST — tentative inferences (never override the above)")]
    for rank, title in sections:
        group = [h for h in hits if h["rank"] == rank]
        if not group:
            continue
        print(f"\n{title}")
        for h in group:
            e = h["entry"]
            flag = "" if h["applies"] else f"  [not applied: {h['note']}]"
            print(f"  {e['id']} [{e.get('topic') or '-'}] {e['statement']}{flag}")
            extra = f" · stance: {e['expert']['stance']} {e['expert']['ref']}" if e.get("expert") else ""
            print(f"      why: {e['rationale']}")
            print(f"      {ctx_text(e.get('context'))} · {brief(e)}{extra}")
    print("\nEXPERT DEFAULTS — not stored here: follow the loaded references where nothing above speaks.")
    if conflicts:
        print("\nCONFLICTS")
        for c in conflicts:
            tag = "UNRESOLVED" if c["unresolved"] else "resolved by precedence"
            print(f"  - {c['topic']}: {c['message']} ({tag})")
    return 3 if (args.strict and unresolved) else 0


def line_for(e, scope):
    extra = f" → {e['superseded_by']}" if e.get("superseded_by") else ""
    return (f"{e['id']:<18} {e['status']:<10} {scope[0]}:{e['kind']:<10} "
            f"[{e.get('topic') or '-'}] {e['statement']}  ({ctx_text(e.get('context'))}){extra}")


def select(args, product, founder):
    qctx = context_from(args)
    rows = []
    scopes = [args.scope] if args.scope else ["product", "founder"]
    for scope, store in (("product", product), ("founder", founder)):
        if scope not in scopes:
            continue
        for e in store.entries:
            if not args.all and not args.status and e["status"] != "active":
                continue
            if args.status and e["status"] != args.status:
                continue
            if args.kind and e["kind"] != args.kind:
                continue
            if args.topic and e.get("topic") != args.topic:
                continue
            if qctx and matches(e.get("context"), qctx) is None:
                continue
            rows.append((scope, e))
    return rows


def cmd_list(args):
    root, product, founder = open_stores(args)
    if getattr(args, "id", None):
        return show_one(args, product, founder)
    rows = select(args, product, founder)
    if args.topics:
        seen = {}
        for scope, e in rows:
            if e.get("topic"):
                seen.setdefault(e["topic"], []).append(e["id"])
        for t, ids in sorted(seen.items()):
            print(f"{t}: {', '.join(ids)}")
        return 0
    if args.json:
        print(json.dumps([{"scope": s, **canonical(e)} for s, e in rows], indent=2, ensure_ascii=False))
        return 0
    if not rows:
        print("No entries." + ("" if args.all else " (active only; --all shows history)"))
    for scope, e in rows:
        print(line_for(e, scope))
    return 0


def show_one(args, product, founder):
    store = store_for(args.id, product, founder)
    e = store.get(args.id)
    if not e:
        raise Refused(f"no entry {args.id} in {store.path}")
    if args.json:
        print(json.dumps({"scope": store.scope, **canonical(e)}, indent=2, ensure_ascii=False))
        return 0
    print(f"# {store.path}")
    print("\n".join(dump_yaml([canonical(e)])))
    chain, cur = [], e
    while cur and cur.get("superseded_by"):
        cur = store.get(cur["superseded_by"])
        if cur:
            chain.append(f"{cur['id']} ({cur['status']})")
    if chain:
        print("current: " + " → ".join(chain))
    for other in store.entries:
        if other.get("supersedes") == e["id"] or other.get("derived_from") == e["id"]:
            print(f"replaced by: {other['id']}")
    return 0


def cmd_export(args):
    root, product, founder = open_stores(args)
    out = [f"# Taste — {product.product.get('name') or root.name}", "",
           f"> Generated by `taste.py export-md` on {today()} from `{PRODUCT_REL}` and the founder "
           "store. Not a source of truth — change taste through `taste.py`.", ""]
    for scope, store, title in (("product", product, "Product decisions"),
                                ("founder", founder, "Founder preferences (cross-product)")):
        if args.scope and args.scope != scope:
            continue
        act = [e for e in store.entries if e["status"] == "active" and e["kind"] != "inference"]
        inf = [e for e in store.entries if e["status"] == "active" and e["kind"] == "inference"]
        old = [e for e in store.entries if e["status"] != "active"]
        out.append(f"## {title}")
        out.append("")
        if not act:
            out.append("_None yet._")
        for e in act:
            stance = f" _(expert {e['expert']['stance']}: {e['expert']['ref']})_" if e.get("expert") else ""
            out.append(f"- **{e['statement']}**{stance} — {e['rationale']}  ")
            out.append(f"  `{e['id']}` · {e.get('topic') or '-'} · {ctx_text(e.get('context'))} · {brief(e)}")
        out.append("")
        if inf:
            out += ["### Awaiting the founder's confirmation", ""]
            for e in inf:
                out.append(f"- {e['statement']} — {e['rationale']} (`{e['id']}`)")
            out.append("")
        if old:
            out += ["### History", ""]
            for e in old:
                nxt = f" → `{e['superseded_by']}`" if e.get("superseded_by") else ""
                note = f" — {e['status_note']}" if e.get("status_note") else ""
                out.append(f"- ~~{e['statement']}~~ `{e['id']}` {e['status']}{nxt}{note}")
            out.append("")
    text = "\n".join(out).rstrip() + "\n"
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


BULLET = re.compile(r"^\s*-\s+(?:\*\*\[?(\d{4}-\d{2}-\d{2})\]?\*\*\s*)?(.+?)\s*$")


def learnings_bullets(path):
    lines = path.read_text(encoding="utf-8").splitlines()
    out, inside, in_comment = [], False, False
    for n, line in enumerate(lines, 1):
        if line.startswith("## "):
            inside = line.strip().lower() == "## design preferences"
            continue
        if "<!--" in line:
            in_comment = "-->" not in line.split("<!--", 1)[1]
            continue
        if in_comment:
            in_comment = "-->" not in line
            continue
        if inside:
            m = BULLET.match(line)
            if m and m.group(2):
                out.append((n, m.group(1), m.group(2)))
    return out


def fingerprint(text):
    return "LEARNINGS.md#" + hashlib.sha1(text.strip().encode("utf-8")).hexdigest()[:10]


def cmd_import(args):
    root, product, founder = open_stores(args)
    path = Path(args.file) if args.file else root / "LEARNINGS.md"
    if not path.exists():
        raise Refused(f"{path} not found")
    known = {e.get("imported_from") for e in product.entries}
    added = []
    for n, date, text in learnings_bullets(path):
        fp = fingerprint(text)
        if fp in known:
            continue
        statement, _, ctx = text.partition(" — context:")
        rationale = ("Imported from LEARNINGS.md — written by an agent, not a verbatim founder quote; "
                     "confirm or reject before relying on it.")
        if ctx.strip():
            rationale += f" Original context: {ctx.strip()}"
        entry = {"id": product.next_id(), "kind": "inference", "status": "active",
                 "source": "inference", "statement": statement.strip(), "rationale": rationale,
                 "context": {}, "evidence": [{"date": date or today(), "file": f"LEARNINGS.md:{n}"}],
                 "recorded": today(), "imported_from": fp}
        product.entries.append(entry)
        known.add(fp)
        added.append(entry)
    if added and not args.dry_run:
        product.save()
    verb = "would import" if args.dry_run else "imported"
    print(f"{verb} {len(added)} design preference(s) from {path} as tentative inferences"
          + (f" into {product.path}" if added and not args.dry_run else ""))
    for e in added:
        print(f"  {e['id']}  {e['statement']}")
    if added:
        print("Next: ask the founder about each (confirm/reject). LEARNINGS.md is left untouched.")
    return 0


def pending_learnings(root, product):
    path = root / "LEARNINGS.md"
    if not path.exists():
        return 0
    known = {e.get("imported_from") for e in product.entries}
    return sum(1 for _, _, t in learnings_bullets(path) if fingerprint(t) not in known)


def cmd_summary(args):
    try:
        root, product, founder = open_stores(args)
    except StoreError as exc:
        first = str(exc).splitlines()[0]
        print(f"Taste: store is malformed — {first} (run `{_tool()} check`)")
        return 2
    dec = [e for e in product.entries if e["status"] == "active" and e["kind"] != "inference"]
    inf = [e for e in product.entries if e["status"] == "active" and e["kind"] == "inference"]
    qctx, _ = query_context(argparse.Namespace(no_defaults=False, context=None), product)
    pref = [e for e in founder.entries
            if e["status"] == "active" and matches(e.get("context"), qctx) is not None]
    parts = []
    if dec:
        parts.append(f"{len(dec)} product decision{'s' * (len(dec) != 1)}")
    if pref:
        parts.append(f"{len(pref)} founder preference{'s' * (len(pref) != 1)}")
    if inf:
        parts.append(f"{len(inf)} inference{'s' * (len(inf) != 1)} to confirm")
    pend = pending_learnings(root, product)
    if not parts and not pend:
        print("Taste: nothing recorded yet — record founder approvals/corrections with taste.py add")
        return 0
    line = "Taste: " + (" · ".join(parts) if parts else "nothing recorded yet")
    if parts:
        line += f" — before UI work: `{_tool()} query --domain <d> --surface <s>`"
    if pend:
        line += f" · {pend} LEARNINGS design preference(s) not imported (`{_tool()} import-learnings`)"
    print(line)
    return 0


def _entry_date(e):
    dates = [ev.get("date") for ev in (e.get("evidence") or []) if isinstance(ev, dict) and ev.get("date")]
    return min(dates) if dates else None


def cmd_bench(args):
    """Is Ship's taste help getting better? Per period: how often the founder accepts what Ship
    proposed, and how often they correct what it made. Rising acceptance and falling corrections
    mean the proposals fit this founder better. Counts, not a score."""
    try:
        _root, product, founder = open_stores(args)
    except StoreError as exc:
        print(f"taste: error: {exc}", file=sys.stderr)
        return 2
    rows = {}
    for store in ((product, founder) if args.all else (product,)):   # promotions would count twice
        for e in store.entries:
            ctx_dom = (e.get("context") or {}).get("domain")
            doms = ctx_dom if isinstance(ctx_dom, list) else [ctx_dom] if ctx_dom else []
            if args.domain and args.domain not in doms:
                continue
            day = _entry_date(e)
            if not day:
                continue
            key = day[:7] if args.by == "month" else "%s-W%02d" % __import__("datetime").date.fromisoformat(day[:10]).isocalendar()[:2]
            r = rows.setdefault(key, {"accepted": 0, "turned_down": 0, "corrected": 0})
            if e.get("source") == "approval":
                r["accepted"] += 1
            elif e.get("source") == "rejection" or e.get("status") == "rejected":
                r["turned_down"] += 1
            elif e.get("source") == "correction":
                r["corrected"] += 1
    out = []
    for key in sorted(rows):
        r = rows[key]
        judged = r["accepted"] + r["turned_down"]
        total = judged + r["corrected"]
        out.append(dict(r, period=key,
                        acceptance=round(r["accepted"] / judged, 2) if judged else None,
                        corrections=round(r["corrected"] / total, 2) if total else None))
    if args.json:
        print(json.dumps({"by": args.by, "domain": args.domain, "periods": out}, indent=2))
        return 0
    if not out:
        print("Bench: nothing to count yet — approvals, rejections and corrections build it up.")
        return 0
    label = f" ({args.domain})" if args.domain else ""
    print(f"Bench{label} — accepted vs turned down, and corrections, per {args.by}:")
    for r in out:
        acc = f"{int(r['acceptance'] * 100)}% accepted" if r["acceptance"] is not None else "nothing proposed"
        cor = f"{int(r['corrections'] * 100)}% corrected" if r["corrections"] is not None else ""
        print(f"  {r['period']}  {r['accepted']} accepted · {r['turned_down']} turned down · "
              f"{r['corrected']} corrected → {acc}" + (f" · {cor}" if cor else ""))
    if len(out) > 1 and out[-1]["corrections"] is not None and out[-2]["corrections"] is not None:
        trend = ("fewer" if out[-1]["corrections"] < out[-2]["corrections"] else
                 "more" if out[-1]["corrections"] > out[-2]["corrections"] else "as many")
        print(f"  Corrections: {trend} than the period before.")
    return 0


def cmd_check(args):
    root, product, founder = open_stores(args)
    for store in (product, founder):
        state = f"{len(store.entries)} entries" if store.exists else "absent (ok)"
        print(f"ok  {store.scope:<8} {store.path} — {state}")
    return 0


def cmd_init(args):
    root, product, founder = open_stores(args)
    if args.name:
        product.product["name"] = args.name
    for f in ("platform", "product_type"):
        vals = context_from(args).get(f)
        if vals:
            product.product[f] = vals
    product.save()
    print(f"product store ready: {product.path} ({ctx_text({k: v for k, v in product.product.items() if isinstance(v, list)})})")
    return 0


# ── CLI ──────────────────────────────────────────────────────────────────────

def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", help="project root (default: $CLAUDE_PROJECT_DIR or nearest project)")
    ctx = argparse.ArgumentParser(add_help=False)
    for f in CONTEXT_FIELDS:
        ctx.add_argument(f"--{f.replace('_', '-')}", dest=f, action="append", metavar="V[,V]")
    ctx.add_argument("--context", action="append", metavar="FIELD=V[,V]",
                     help="alternative spelling, e.g. --context 'platform=ios domain=motion'")
    ev = argparse.ArgumentParser(add_help=False)
    ev.add_argument("--quote", help="the founder's words, verbatim")
    ev.add_argument("--file", help="file (and :line) the judgment is about or came from")
    ev.add_argument("--commit")
    ev.add_argument("--screenshot")
    ev.add_argument("--url", help="a reference the founder showed: a site, or one shot on a gallery page")
    ev.add_argument("--note")

    p = argparse.ArgumentParser(prog="taste.py", description=__doc__.split("\n\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    for name in ("add", "record"):
        a = sub.add_parser(name, parents=[common, ctx, ev], help="record a judgment")
        a.add_argument("--kind", required=True, choices=KINDS)
        a.add_argument("--scope", choices=("product", "founder"))
        a.add_argument("--source", required=True, choices=SOURCES)
        a.add_argument("--topic")
        a.add_argument("--statement", required=True)
        a.add_argument("--rationale", required=True)
        a.add_argument("--ref", help="expert reference (kind expert)")
        a.add_argument("--stance", choices=STANCES)
        a.add_argument("--overrides", help="founder-scope id this product decision overrides here")
        a.add_argument("--confirmed-by-founder", dest="confirmed_by_founder")
        a.add_argument("--keep-both", action="store_true")
        a.set_defaults(fn=cmd_add)

    for name in ("list", "show"):
        a = sub.add_parser(name, parents=[common, ctx], help="inspect entries")
        a.add_argument("id", nargs="?")
        a.add_argument("--all", action="store_true", help="include superseded/confirmed/rejected")
        a.add_argument("--kind", choices=KINDS)
        a.add_argument("--scope", choices=("product", "founder"))
        a.add_argument("--status", choices=STATUSES)
        a.add_argument("--topic")
        a.add_argument("--topics", action="store_true", help="list topics in use")
        a.add_argument("--json", action="store_true")
        a.set_defaults(fn=cmd_list)

    a = sub.add_parser("query", parents=[common, ctx], help="applicable entries in precedence order")
    a.add_argument("--no-defaults", action="store_true", help="don't fill platform/product_type from the product")
    a.add_argument("--strict", action="store_true", help="exit 3 on unresolved conflicts")
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=cmd_query)

    a = sub.add_parser("supersede", parents=[common, ctx, ev], help="replace an entry, keep the old one")
    a.add_argument("id")
    a.add_argument("--statement")
    a.add_argument("--rationale", required=True)
    a.add_argument("--topic")
    a.add_argument("--source", choices=SOURCES)
    a.add_argument("--clear", action="append", choices=[f.replace("_", "-") for f in CONTEXT_FIELDS] + list(CONTEXT_FIELDS))
    a.add_argument("--confirmed-by-founder", dest="confirmed_by_founder")
    a.set_defaults(fn=cmd_supersede)

    a = sub.add_parser("confirm", parents=[common, ctx], help="founder confirms an inference")
    a.add_argument("id")
    a.add_argument("--quote", required=True)
    a.add_argument("--statement")
    a.add_argument("--rationale")
    a.add_argument("--topic")
    a.add_argument("--keep-both", action="store_true")
    a.set_defaults(fn=cmd_confirm)

    a = sub.add_parser("reject", parents=[common], help="founder rejects an inference")
    a.add_argument("id")
    a.add_argument("--quote", required=True)
    a.add_argument("--reason")
    a.set_defaults(fn=cmd_reject)

    a = sub.add_parser("promote", parents=[common, ctx], help="product decision → founder preference")
    a.add_argument("id")
    a.add_argument("--confirmed-by-founder", dest="confirmed_by_founder")
    a.add_argument("--clear", action="append", choices=[f.replace("_", "-") for f in CONTEXT_FIELDS] + list(CONTEXT_FIELDS))
    a.add_argument("--keep-both", action="store_true")
    a.set_defaults(fn=cmd_promote)

    a = sub.add_parser("export-md", parents=[common], help="readable view (generated)")
    a.add_argument("--out")
    a.add_argument("--scope", choices=("product", "founder"))
    a.set_defaults(fn=cmd_export)

    a = sub.add_parser("import-learnings", parents=[common], help="LEARNINGS.md → tentative inferences")
    a.add_argument("--file")
    a.add_argument("--dry-run", action="store_true")
    a.set_defaults(fn=cmd_import)

    a = sub.add_parser("check", parents=[common], help="validate both stores")
    a.set_defaults(fn=cmd_check)
    a = sub.add_parser("summary", parents=[common], help="one line for session start")
    a.set_defaults(fn=cmd_summary)
    a = sub.add_parser("bench", parents=[common], help="accepted / turned down / corrected, per period")
    a.add_argument("--by", choices=("month", "week"), default="month")
    a.add_argument("--domain", help="only this domain, e.g. care")
    a.add_argument("--all", action="store_true", help="also the founder store (across products)")
    a.add_argument("--json", action="store_true")
    a.set_defaults(fn=cmd_bench)
    a = sub.add_parser("init", parents=[common, ctx], help="create/update the product store header")
    a.add_argument("--name")
    a.set_defaults(fn=cmd_init)
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.fn(args)
    except StoreError as exc:
        print(f"taste: error: {exc}", file=sys.stderr)
        return 2
    except Refused as exc:
        print(f"taste: refused: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
