"""Platform-neutral motion tokens → per-platform values, plus the motion lint.

Springs (either form, both first-class):
    gentle: { response: 0.5, damping: 0.9 }        # SwiftUI .spring(response:dampingFraction:)
    press:  { duration: 0.3, bounce: 0 }           # SwiftUI .spring(duration:bounce:)
Curves (optional, named cubic-béziers; a name here overrides the built-in curve of that name):
    easeOut: [0.23, 1, 0.32, 1]
Durations:
    fade:   { ms: 200, curve: easeOut }            # linear | easeIn | easeOut | easeInOut | <curve name>
    sheet:  { ms: 300, curve: [0.32, 0.72, 0, 1] } # inline cubic-bézier
    fade2:  200                                    # shorthand → easeOut
Stagger (optional): { ms: 50, min_ms: 30, max_ms: 80, max_items: 8 }
Optional on any spring/duration: `use:` (see motion-rules.yaml › uses), `allow: [rule-id]`.
"""

import math
from pathlib import Path

from .yamlsub import YamlError, load_yaml

# Cubic-bezier control points of the named curves. These are the CSS / Core Animation
# definitions (SwiftUI's easeIn/easeOut/easeInOut use the same curves).
NAMED_CURVES = {
    "linear": (0.0, 0.0, 1.0, 1.0),
    "easeIn": (0.42, 0.0, 1.0, 1.0),
    "easeOut": (0.0, 0.0, 0.58, 1.0),
    "easeInOut": (0.42, 0.0, 0.58, 1.0),
}
RULES_PATH = Path(__file__).resolve().parents[2] / "references" / "motion-rules.yaml"


def num(v):
    return f"{v:g}" if isinstance(v, float) else str(v)


def springs(prims):
    """→ [{name, form, response, damping, duration, bounce, use, allow}] — both forms normalised.

    duration/bounce → response/damping uses Apple's documented relation for
    Spring(duration:bounce:): response = duration; bounce ≥ 0 → damping = 1 − bounce,
    bounce < 0 → damping = 1 / (1 + bounce).
    """
    out = []
    for name, s in ((prims.get("motion") or {}).get("springs") or {}).items():
        s = s or {}
        item = {"name": name, "use": s.get("use"), "allow": s.get("allow") or []}
        if "duration" in s or "bounce" in s:
            d, b = float(s.get("duration", 0.5)), float(s.get("bounce", 0))
            item.update(form="bounce", duration=d, bounce=b, response=d,
                        damping=(1 - b) if b >= 0 else 1 / (1 + b))
        else:
            r, z = float(s.get("response", 0.5)), float(s.get("damping", s.get("dampingFraction", 1)))
            item.update(form="response", response=r, damping=z, duration=r,
                        bounce=(1 - z) if z <= 1 else (1 / z - 1))
        item["raw"] = s
        out.append(item)
    return out


DEFAULT_CURVE = "easeOut"


def curve_table(prims):
    """Built-in curves overlaid with the project's named curves."""
    table = dict(NAMED_CURVES)
    for name, pts in ((prims.get("motion") or {}).get("curves") or {}).items():
        if isinstance(pts, list) and len(pts) == 4:
            table[str(name)] = tuple(float(x) for x in pts)
    return table


def durations(prims):
    """→ [{name, ms, curve: name|None, points, custom: bool, use, allow}]
    custom = the points come from the project (inline list or motion.curves), so every platform
    emits the exact cubic-bézier instead of its built-in curve."""
    table = curve_table(prims)
    project = set(((prims.get("motion") or {}).get("curves") or {}))
    out = []
    for name, d in ((prims.get("motion") or {}).get("durations") or {}).items():
        if isinstance(d, dict):
            ms, curve, use, allow = d.get("ms"), d.get("curve", DEFAULT_CURVE), d.get("use"), d.get("allow") or []
        else:
            ms, curve, use, allow = d, DEFAULT_CURVE, None, []
        if isinstance(curve, list):
            points, cname, custom = tuple(float(x) for x in curve), None, True
        else:
            cname = str(curve)
            points = table.get(cname, NAMED_CURVES[DEFAULT_CURVE])
            custom = cname in project
        out.append({"name": name, "ms": ms, "curve": cname, "points": points, "custom": custom,
                    "use": use, "allow": allow})
    return out


def stagger(prims):
    s = (prims.get("motion") or {}).get("stagger")
    return s if isinstance(s, dict) else None


def validate_motion(prims):
    """Structural errors (block) for motion tokens."""
    errors = []
    motion = prims.get("motion") or {}
    for name, s in (motion.get("springs") or {}).items():
        s = s or {}
        has_r = "response" in s or "damping" in s
        has_b = "duration" in s or "bounce" in s
        if has_r and has_b:
            errors.append(f"motion.springs.{name}: use either response/damping or duration/bounce, not both")
        elif has_r and not ("response" in s and "damping" in s):
            errors.append(f"motion.springs.{name}: needs both response and damping")
        elif has_b and "duration" not in s:
            errors.append(f"motion.springs.{name}: duration/bounce form needs duration")
        elif not has_r and not has_b:
            errors.append(f"motion.springs.{name}: needs response + damping, or duration + bounce")
        if "bounce" in s and not -1 <= float(s["bounce"]) <= 1:
            errors.append(f"motion.springs.{name}: bounce must be between -1 and 1")
        if "damping" in s and float(s["damping"]) <= 0:
            errors.append(f"motion.springs.{name}: damping must be > 0")
    curves = motion.get("curves") or {}
    for name, pts in curves.items():
        if not (isinstance(pts, list) and len(pts) == 4 and all(isinstance(x, (int, float)) for x in pts)):
            errors.append(f"motion.curves.{name}: must be [x1, y1, x2, y2]")
        elif not (0 <= pts[0] <= 1 and 0 <= pts[2] <= 1):
            errors.append(f"motion.curves.{name}: cubic-bezier x values must be within 0..1")
    clash = set(motion.get("springs") or {}) & set(motion.get("durations") or {})
    if motion.get("stagger") is not None:
        clash |= {"stagger"} & (set(motion.get("springs") or {}) | set(motion.get("durations") or {}))
    for name in sorted(clash, key=str):
        errors.append(f"motion: '{name}' is both a spring and a duration — names must be unique")
    st = motion.get("stagger")
    if st is not None and not (isinstance(st, dict) and isinstance(st.get("ms"), (int, float))):
        errors.append("motion.stagger: needs ms (e.g. { ms: 50, max_items: 8 })")
    for name, d in (motion.get("durations") or {}).items():
        spec = d if isinstance(d, dict) else {"ms": d}
        if not isinstance(spec.get("ms"), (int, float)):
            errors.append(f"motion.durations.{name}: ms is required (a number)")
        curve = spec.get("curve", DEFAULT_CURVE)
        if isinstance(curve, list):
            if len(curve) != 4 or not all(isinstance(x, (int, float)) for x in curve):
                errors.append(f"motion.durations.{name}: curve list must be [x1, y1, x2, y2]")
            elif not (0 <= curve[0] <= 1 and 0 <= curve[2] <= 1):
                errors.append(f"motion.durations.{name}: cubic-bezier x values must be within 0..1")
        elif curve not in NAMED_CURVES and curve not in curves:
            errors.append(f"motion.durations.{name}: curve '{curve}' — use {', '.join(NAMED_CURVES)}, "
                          f"a name from motion.curves, or [x1, y1, x2, y2]")
    return errors


def load_rules(path=RULES_PATH):
    try:
        return load_yaml(path.read_text(encoding="utf-8"))
    except (OSError, YamlError):
        return None


def ease_in_like(points, x1_min=0.3, y1_max=0.1, x2_max=0.7, y2_min=0.9):
    """Slow start AND no fast finish: easeIn, or a cubic-bézier whose first control point sits
    low and late. An ease-in-out (second control point early and high) is not ease-in."""
    x1, y1, x2, y2 = points
    ease_in_out = x2 < x2_max and y2 > y2_min
    return x1 > x1_min and y1 < y1_max and not ease_in_out and points != NAMED_CURVES["linear"]


def _targets(rule, token):
    """Does the rule look at this token? Explicit `use:` wins; otherwise the name decides."""
    import re as _re
    use, name = token.get("use"), str(token["name"])
    if use is not None:
        if use in (rule.get("except_uses") or []):
            return False
        if rule.get("uses") is not None or rule.get("names") is not None:
            return use in (rule.get("uses") or [])
        return True
    if rule.get("except_names") and _re.search(rule["except_names"], name, _re.I):
        return False
    if rule.get("names") is not None:
        return bool(_re.search(rule["names"], name, _re.I))
    return True


def lint(prims, rules=None):
    """Warnings from the rules table (motion-rules.yaml). `allow: [rule]` on a token accepts it."""
    rules = rules if rules is not None else load_rules()
    if not rules:
        return ["motion lint skipped: references/motion-rules.yaml missing or unreadable"]
    table = rules.get("rules") or {}
    known = set(rules.get("uses") or [])
    warnings = []

    def fire(rid, token, detail):
        if rid in (token.get("allow") or []):
            return
        where = f"motion.{token['kind']}.{token['name']}" + (f" ({token['use']})" if token.get("use") else "")
        warnings.append(f"{where}: {detail} — {table[rid].get('message', rid)} "
                        f"[{rid}; accept on purpose with allow: [{rid}]]")

    def rule(rid, applies):
        r = table.get(rid)
        return r if r and r.get("applies") == applies else None

    durs = durations(prims)
    sprs = springs(prims)
    for tok in durs + sprs:
        tok["kind"] = "durations" if "ms" in tok else "springs"
        if tok.get("use") is not None and known and tok["use"] not in known:
            warnings.append(f"motion.{tok['kind']}.{tok['name']}: unknown use '{tok['use']}' "
                            f"(known: {', '.join(sorted(known))})")
    for d in durs:
        ms = d["ms"] if isinstance(d["ms"], (int, float)) else None
        r = rule("motion-easein", "durations")
        if r and _targets(r, d):
            ei = r.get("ease_in") or {}
            if d["curve"] == "easeIn" and not d["custom"] or ease_in_like(d["points"], ei.get("x1_min", 0.3), ei.get("y1_max", 0.1),
                                                                               ei.get("x2_max", 0.7), ei.get("y2_min", 0.9)):
                fire("motion-easein", d, f"curve {d['curve'] or list(d['points'])} is ease-in")
        for rid in ("motion-duration-ui", "motion-duration-max"):
            r = rule(rid, "durations")
            if r and ms is not None and _targets(r, d) and ms > r.get("max_ms", 10 ** 9):
                fire(rid, d, f"{num(ms)}ms > {r['max_ms']}ms")
        r = rule("motion-press-duration", "durations")
        if r and ms is not None and _targets(r, d) and not r.get("min_ms", 0) <= ms <= r.get("max_ms", 10 ** 9):
            fire("motion-press-duration", d, f"{num(ms)}ms outside {r.get('min_ms')}–{r.get('max_ms')}ms")
        r = rule("motion-linear-ui", "durations")
        if r and d["curve"] == "linear" and _targets(r, d):
            fire("motion-linear-ui", d, "linear curve")
    for s in sprs:
        r = rule("motion-overshoot-press", "springs")
        if r and _targets(r, s) and s["damping"] < r.get("min_damping", 0.95):
            fire("motion-overshoot-press", s, f"damping {s['damping']:.3g} (bounce {s['bounce']:.2g}) overshoots")
        r = rule("motion-bounce-range", "springs")
        if r and _targets(r, s) and s["damping"] < r.get("min_damping", 0.7):
            fire("motion-bounce-range", s, f"damping {s['damping']:.3g}")
        r = rule("motion-damping-invalid", "springs")
        if r and s["damping"] > r.get("max_damping", 1.0):
            fire("motion-damping-invalid", s, f"damping {s['damping']:.3g}")
    st = stagger(prims)
    r = rule("motion-stagger", "stagger")
    if r and st and isinstance(st.get("ms"), (int, float)) and not r.get("min_ms", 0) <= st["ms"] <= r.get("max_ms", 10 ** 9):
        fire("motion-stagger", {"name": "ms", "kind": "stagger", "allow": st.get("allow") or []}, f"{num(st['ms'])}ms")
    r = rule("motion-no-reduced-path", "model")
    if r and (durs or sprs):
        import re as _re
        has_fade = any(d.get("use") in (r.get("fade_uses") or []) or _re.search(r.get("fade_names", "fade"), str(d["name"]), _re.I)
                       for d in durs)
        allowed = "motion-no-reduced-path" in ((prims.get("motion") or {}).get("allow") or [])
        if not has_fade and not allowed:
            warnings.append(f"motion: no opacity-only duration (e.g. fade) — {r.get('message')} "
                            f"[motion-no-reduced-path; accept with motion.allow: [motion-no-reduced-path]]")
    return warnings


# ── Spring physics (for CSS linear() and Compose stiffness) ──────────────────

def spring_position(t, response, damping):
    """Unit step response of a mass-spring (mass 1, from 0 → 1, zero initial velocity)."""
    w = 2 * math.pi / response
    z = damping
    if z < 1:
        wd = w * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w * t) * (math.cos(wd * t) + (z * w / wd) * math.sin(wd * t))
    if z == 1:
        return 1 - math.exp(-w * t) * (1 + w * t)
    r = math.sqrt(z * z - 1)
    r1, r2 = -w * (z - r), -w * (z + r)
    return 1 + (r2 * math.exp(r1 * t) - r1 * math.exp(r2 * t)) / (r1 - r2)


def settle_time(response, damping, eps=0.001):
    """Seconds until the spring stays within eps of its target."""
    last, t, dt = 0.0, 0.0, 0.001
    while t < 10:
        if abs(1 - spring_position(t, response, damping)) > eps:
            last = t
        t += dt
    return max(last, 0.016)


def css_linear(response, damping, points=32):
    """CSS linear() easing that samples the spring, plus its settle duration in ms."""
    total = settle_time(response, damping)
    stops = []
    for i in range(points + 1):
        v = 1.0 if i == points else round(spring_position(total * i / points, response, damping), 4)
        stops.append("0" if v == 0 else "1" if v == 1 else f"{v:.4f}".rstrip("0").rstrip("."))
    return f"linear({', '.join(stops)})", int(round(total * 1000))


def stiffness(response):
    """Compose spring(stiffness:) for mass 1: k = (2π / response)²."""
    return (2 * math.pi / response) ** 2
