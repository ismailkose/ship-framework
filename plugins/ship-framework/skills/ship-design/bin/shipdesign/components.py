"""Component manifest views: status, suitability matching, extension classification, docs."""

import re
from datetime import date

from .registry import (as_list, components, flatten, resolve_color, resolve_scale, semantic_keys,
                       system_color, token_known, type_styles, variant_in_source)

STOP = {"the", "a", "an", "and", "or", "for", "of", "to", "in", "on", "with", "when", "not", "any",
        "use", "used", "this", "that", "is", "are", "be", "it", "as", "by", "at", "from", "only"}


def words(text):
    return {w for w in re.findall(r"[a-z0-9]+", str(text).lower()) if w not in STOP and len(w) > 2}


def status(root, comps):
    """→ list of {name, role, state, file, variants, missing_variants, origin}."""
    out = []
    for c in components(comps):
        f = str(c.get("file") or "")
        entry = {"name": c.get("name"), "role": c.get("role"), "file": f or None, "origin": c.get("origin"),
                 "variants": as_list(c.get("variants")), "missing_variants": []}
        if c.get("planned"):
            entry["state"] = "planned"
        elif f and (root / f).is_file():
            entry["state"] = "realized"
            text = (root / f).read_text(encoding="utf-8", errors="replace")
            entry["missing_variants"] = [v for v in entry["variants"]
                                         if not variant_in_source(str(v), text, (root / f).suffix.lower())]
        else:
            entry["state"] = "broken"
        out.append(entry)
    return out


# ── Suitability ──────────────────────────────────────────────────────────────

VERDICT_RANK = {"reuse": 0, "extend": 1, "planned": 2, "founder": 3, "conflict": 4, "weak": 5}
VERDICT_TEXT = {
    "reuse": "reuse as-is",
    "extend": "legitimate extension — add it (no founder question), record it in history",
    "planned": "planned, not built yet — realize it (then reuse)",
    "founder": "needs a founder decision (unregistered tokens or changed behaviour)",
    "conflict": "registered as not-for this use — don't force it",
    "weak": "name-only match — suitability unknown (no role registered)",
}


def role_relation(need, have):
    """→ (score, reason, implied_variant) or None."""
    if not need:
        return 10, "no role requested", None
    if not have:
        return None
    if have == need:
        return 50, f"role '{have}' matches", None
    if need.startswith(have + "."):
        sub = need[len(have) + 1:].split(".")[0]
        return 40, f"role '{have}' covers '{need}' through a variant", sub
    if have.startswith(need + "."):
        return 30, f"role '{have}' is a specialisation of '{need}'", None
    if have.split(".")[0] == need.split(".")[0]:
        return 20, f"same role family ('{have}' vs '{need}')", None
    return None


def not_for_conflicts(c, role, context):
    hits = []
    need_words = words(context or "") | ({role} if role else set()) | words(role or "")
    for entry in as_list(c.get("not_for")):
        e = str(entry)
        ew = words(e)
        if role and (e.strip() == role or re.search(rf"(^|[^a-z.]){re.escape(role)}([^a-z.]|$)", e.lower())):
            hits.append(e)
        elif context and len(ew & words(context)) >= 1 and ew & need_words:
            hits.append(e)
    return hits


def match(model, comps, role=None, variant=None, tokens=(), context=None):
    tokens = [t for t in tokens if t]
    results = []
    for c in components(comps):
        name = str(c.get("name"))
        reasons = []
        rel = role_relation(role, c.get("role"))
        weak = False
        if rel is None:
            base = (role or "").split(".")[0].replace("-", "")
            if role and not c.get("role") and base and base in name.lower():
                rel = (5, f"name '{name}' mentions '{base}' but no role is registered", None)
                weak = True
            else:
                continue
        score, why, implied = rel
        reasons.append({"check": "role", "ok": not weak, "detail": why})
        want_variant = variant or implied
        variants = [str(v) for v in as_list(c.get("variants"))]
        missing_variant = False
        if want_variant:
            if want_variant in variants:
                score += 20
                reasons.append({"check": "variant", "ok": True, "detail": f"variant '{want_variant}' exists"})
            else:
                missing_variant = True
                reasons.append({"check": "variant", "ok": False,
                                "detail": f"no '{want_variant}' variant (has: {', '.join(variants) or 'none'})"})
        have_tokens = set(as_list(c.get("tokens")))
        unregistered, additive = [], []
        for t in tokens:
            if not token_known(model, t):
                unregistered.append(t)
            elif t not in have_tokens:
                additive.append(t)
        if tokens:
            if unregistered:
                reasons.append({"check": "tokens", "ok": False,
                                "detail": f"not in design-model.yaml: {', '.join(unregistered)} — new tokens are a design decision"})
            elif additive:
                reasons.append({"check": "tokens", "ok": False,
                                "detail": f"registered but not used by {name}: {', '.join(additive)} — an additive variant could use them"})
            else:
                score += 15
                reasons.append({"check": "tokens", "ok": True, "detail": f"uses {', '.join(tokens)} already"})
        conflicts = not_for_conflicts(c, role, context)
        for e in conflicts:
            reasons.append({"check": "not_for", "ok": False, "detail": f"not_for: {e}"})
        uw = as_list(c.get("use_when"))
        if context and uw:
            overlap = words(context) & set().union(*(words(u) for u in uw))
            if overlap:
                score += 5
                reasons.append({"check": "use_when", "ok": True, "detail": f"use_when mentions {', '.join(sorted(overlap))}"})
        planned = bool(c.get("planned"))
        if planned:
            reasons.append({"check": "status", "ok": False, "detail": "planned — no implementation yet"})
        if conflicts:
            verdict = "conflict"
        elif weak:
            verdict = "weak"
        elif unregistered:
            verdict = "founder"
        elif planned:
            verdict = "planned"
        elif missing_variant or additive:
            verdict = "extend"
        else:
            verdict = "reuse"
        results.append({"name": name, "file": c.get("file"), "role": c.get("role"), "score": score,
                        "verdict": verdict, "summary": VERDICT_TEXT[verdict], "reasons": reasons,
                        "variant": want_variant})
    results.sort(key=lambda r: (VERDICT_RANK[r["verdict"]], -r["score"], r["name"]))
    return results


def format_match(results, need):
    if not results:
        return [f"miss — no registered component fits {need}. Classify it: reusable primitive → build + register; one-off → compose locally."]
    lines = []
    for r in results:
        lines.append(f"{r['verdict']:8} {r['name']}  ({r['role'] or 'no role'}; {r['file'] or 'no file'}) — {r['summary']}")
        for x in r["reasons"]:
            lines.append(f"           {'✓' if x['ok'] else '✗'} {x['check']}: {x['detail']}")
    return lines


# ── Legitimate extension ─────────────────────────────────────────────────────

def classify_extension(model, comps, name, variant=None, params=(), tokens=(), changes_existing=False):
    """Adding a variant/param that uses only registered tokens and keeps existing call sites'
    behaviour = legitimate extension (no founder question; record it). Anything that changes
    existing behaviour/visuals, or needs new tokens = founder decision."""
    comp = next((c for c in components(comps) if str(c.get("name")) == name), None)
    if comp is None:
        return {"ok": False, "verdict": "unknown", "reasons": [f"{name} is not registered"]}
    reasons = []
    ok = True
    variants = [str(v) for v in as_list(comp.get("variants"))]
    if variant and variant in variants:
        reasons.append(f"variant '{variant}' already exists — reuse it")
    if variant and not re.fullmatch(r"[a-z][A-Za-z0-9]*", variant):
        ok = False
        reasons.append(f"variant '{variant}' must be lowerCamel")
    bad = [t for t in tokens if not token_known(model, t)]
    prims = model.get("primitives") or {}
    prim_refs = [t for t in tokens if t not in semantic_keys(model) and resolve_color(prims, t) is not None]
    if bad:
        ok = False
        reasons.append(f"tokens not in design-model.yaml: {', '.join(bad)} — adding tokens is a design decision")
    if prim_refs:
        ok = False
        reasons.append(f"color primitives referenced directly: {', '.join(prim_refs)} — use semantic tokens")
    if changes_existing:
        ok = False
        reasons.append("changes existing behaviour/visuals at current call sites — founder decision")
    if comp.get("planned"):
        reasons.append("component is planned — realize it first")
    today = date.today().isoformat()
    change = []
    if variant and variant not in variants:
        change.append(f"variant {variant}")
    change += [f"param {p}" for p in params]
    new_tokens = [t for t in tokens if t not in as_list(comp.get("tokens"))]
    snippet = []
    if ok and change:
        if variant and variant not in variants:
            snippet.append(f"    variants: [{', '.join(variants + [variant])}]")
        if new_tokens:
            snippet.append(f"    tokens: [{', '.join(as_list(comp.get('tokens')) + new_tokens)}]")
        if params:
            snippet.append("    api:  # add: " + ", ".join(f"{p}: <what it does>" for p in params))
        snippet.append("    history:")
        snippet.append(f"      - {{ date: {today}, kind: extension, change: \"added {', '.join(change)}\" }}")
    verdict = "extension" if ok else "founder"
    if ok and not change:
        verdict = "nothing-to-add"
    return {"ok": ok, "verdict": verdict, "reasons": reasons, "snippet": snippet}


# ── Docs (design/COMPONENTS.md) ──────────────────────────────────────────────

def _token_desc(model, tok):
    prims = model.get("primitives") or {}
    light = flatten(model.get("semantic"))
    dark = flatten(model.get("semantic_dark"))
    if tok in light:
        def show(p):
            if system_color(p):
                return str(p)
            return f"{p} {resolve_color(prims, p)}"
        l, d = light[tok], dark.get(tok, light[tok])
        return f"`{tok}` ({show(l)}{'' if l == d else ' / dark ' + show(d)})"
    v = resolve_scale(prims, tok)
    if isinstance(v, dict):
        if tok.startswith("type."):
            spec = type_styles(prims).get(tok.split(".", 1)[1]) or {}
            return f"`{tok}` ({spec.get('font')} {spec.get('size')})"
        return f"`{tok}` ({', '.join(f'{k} {x}' for k, x in v.items())})"
    return f"`{tok}` ({v})" if v is not None else f"`{tok}` (unresolved)"


def emit_docs(model, comps, root):
    entries = components(comps)
    st = {s["name"]: s for s in status(root, comps)}
    brand = (model.get("brand") or {}).get("name", "")
    L = [f"# {brand} — component library".strip(" —"), "",
         "Generated from `design/components.yaml` + `design-model.yaml`. Edit those, then regenerate "
         "(`design_model.py docs`). Planned components are listed so nobody builds a duplicate.", ""]
    if not entries:
        L += ["_No registered components yet._", ""]
        return "\n".join(L)
    L += ["| Component | Role | Status | Variants | File |", "|---|---|---|---|---|"]
    for c in entries:
        s = st.get(c.get("name"), {})
        L.append(f"| [{c.get('name')}](#{str(c.get('name')).lower()}) | {c.get('role') or '—'} | {s.get('state', '?')} | "
                 f"{', '.join(str(v) for v in as_list(c.get('variants'))) or '—'} | "
                 f"{'`' + str(c.get('file')) + '`' if c.get('file') else '—'} |")
    L.append("")
    for c in entries:
        s = st.get(c.get("name"), {})
        L += [f"## {c.get('name')}", ""]
        meta = [f"**Role:** {c.get('role') or '— (unset)'}", f"**Status:** {s.get('state', '?')}"]
        if c.get("origin"):
            meta.append(f"**Origin:** {c['origin']}")
        if c.get("added"):
            meta.append(f"**Added:** {c['added']}")
        if c.get("extends"):
            meta.append(f"**Extends:** {c['extends']}")
        L += [" · ".join(meta), ""]
        if c.get("doc"):
            L += [str(c["doc"]).strip(), ""]
        for label, key in (("Use when", "use_when"), ("Not for", "not_for")):
            vals = as_list(c.get(key))
            if vals:
                L.append(f"- **{label}:** " + "; ".join(str(v) for v in vals))
        if c.get("variants"):
            miss = s.get("missing_variants") or []
            L.append("- **Variants:** " + ", ".join(f"`{v}`" + (" (not found in source)" if v in miss else "")
                                                   for v in as_list(c.get("variants"))))
        api = c.get("api")
        if isinstance(api, dict) and api:
            L.append("- **API:** " + "; ".join(f"`{k}` — {v}" for k, v in api.items()))
        elif isinstance(api, list) and api:
            L.append("- **API:** " + ", ".join(f"`{a}`" for a in api))
        if c.get("tokens"):
            L.append("- **Tokens:** " + ", ".join(_token_desc(model, t) for t in as_list(c.get("tokens"))))
        if c.get("rule"):
            L.append(f"- **Rule:** {c['rule']}")
        L.append(f"- **File:** `{c['file']}`" if c.get("file") else "- **File:** — (planned)")
        for h in as_list(c.get("history")):
            if isinstance(h, dict):
                L.append(f"- **{h.get('date')}** ({h.get('kind', 'extension')}): {h.get('change')}")
        L.append("")
    return "\n".join(L)
