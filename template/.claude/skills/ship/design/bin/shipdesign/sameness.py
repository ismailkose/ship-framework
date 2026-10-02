"""Which of the product's design choices are still defaults — Ship's seed values or the platform's.

Evidence for Pol's care lens (review/references/care-lens.md §2). A product still wearing defaults
has no visual voice yet. Never a failure: good defaults are good; the question is whether they were
chosen for this product.
"""
import math
import re

from .registry import family_range, resolve_color

# Accents that ship with a platform or a popular kit — seeing one usually means nobody chose it.
PLATFORM_ACCENTS = {
    "#007AFF": "iOS system blue", "#0A84FF": "iOS system blue (dark)",
    "#3B82F6": "Tailwind blue-500", "#2563EB": "Tailwind blue-600", "#6366F1": "Tailwind indigo-500",
    "#6750A4": "Material 3 baseline purple", "#0070F3": "Next.js blue",
}
COMMON_FAMILIES = {"system", "system-ui", "-apple-system", "sf pro", "sf pro text", "inter", "roboto",
                   "helvetica", "helvetica neue", "arial"}
# Display faces models reach for by reflex when asked for character (sources: the maintainer ledger).
# A subject association ("books want a serif") isn't a reason.
REFLEX_FACES = {"fraunces", "playfair display", "cormorant", "cormorant garamond", "lora", "crimson pro",
                "crimson text", "newsreader", "syne", "space grotesk", "space mono", "ibm plex sans",
                "ibm plex serif", "ibm plex mono", "dm sans", "dm serif display", "outfit", "plus jakarta sans",
                "instrument sans", "instrument serif", "geist", "satoshi", "cabinet grotesk"}
MOTION_GROUPS = ("springs", "curves", "durations")

# The AI default look (warm version) models fall back on when asked for "warm", "premium" or "not generic":
# cream paper, a warm near-black, a clay / brass / oxblood accent, an editorial serif. Ranges are
# OKLCH, calibrated on field lists of generated sites and Ship's own sample (sources: the maintainer ledger).
EDITORIAL_SERIFS = re.compile(
    r"fraunces|playfair|cormorant|garamond|newsreader|gelasio|lora\b|merriweather|spectral|literata|"
    r"crimson|caslon|baskerville|bodoni|didot|palatino|georgia|times|iowan|tiempos|canela|recoleta|"
    r"sectra|domaine|freight|lyon|editorial|charter|cardo|vollkorn|alegreya|new york|\bogg\b|\bnoe\b")


def _oklch(hexv):
    h = hexv.lstrip("#")[:6]
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", h):
        return None

    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (lin(int(h[i:i + 2], 16)) for i in (0, 2, 4))
    l_, m_, s_ = (x ** (1 / 3) for x in (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b,
                                          0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b,
                                          0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b))
    L = 0.2104542553 * l_ + 0.7936177850 * m_ - 0.0040720468 * s_
    a = 1.9779984951 * l_ - 2.4285922050 * m_ + 0.4505937099 * s_
    bb = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.8086757660 * s_
    return L, math.hypot(a, bb), math.degrees(math.atan2(bb, a)) % 360


def tasteful_default(model):
    """The signs of the models' 'tasteful' look that this registry shows (light mode)."""
    prims, sem = model.get("primitives") or {}, model.get("semantic") or {}

    def lch(key):
        v = sem.get(key)
        return _oklch(resolve_color(prims, v) or "") if isinstance(v, str) else None
    signs = []
    bg, ink, accent = lch("background"), lch("text"), lch("action")
    if bg and bg[0] >= 0.90 and 0.005 <= bg[1] <= 0.035 and 55 <= bg[2] <= 105:
        signs.append("a cream background")
    if ink and ink[0] <= 0.30 and 0.005 <= ink[1] <= 0.035 and 30 <= ink[2] <= 105:
        signs.append("brown-black text")
    if accent and 0.40 <= accent[0] <= 0.70 and 0.07 <= accent[1] <= 0.16 and 10 <= accent[2] <= 85:
        signs.append("a terracotta or brass button colour")
    tp = prims.get("type") or {}
    names = [tp.get("family")] + list((tp.get("families") or {}).values())
    keys = ["default"] + list(tp.get("families") or {})
    if any(isinstance(n, str) and "sans" not in n.lower() and ("serif" in n.lower() or EDITORIAL_SERIFS.search(n.lower()))
           for n in names) or any(family_range(tp, k)[0] == "serif" for k in keys):
        signs.append("a fancy serif headline")
    return signs


def motion_defaults(model, template):
    """(names still at Ship's seed values, how many seed values there are)."""
    mm = (model.get("primitives") or {}).get("motion") or {}
    tm = (template.get("primitives") or {}).get("motion") or {}
    same, total = [], 0
    for group in MOTION_GROUPS:
        for name, value in (tm.get(group) or {}).items():
            total += 1
            if (mm.get(group) or {}).get(name) == value:
                same.append(f"{group}.{name}")
    return same, total


def sameness(model, template):
    prims = model.get("primitives") or {}
    items = []
    action = (model.get("semantic") or {}).get("action")
    if isinstance(action, str) and action.startswith("system."):
        items.append({"area": "accent", "token": "semantic.action", "value": action,
                      "why": "the platform's own accent colour"})
    elif isinstance(action, str):
        hexv = resolve_color(prims, action)
        if hexv and hexv.upper() in PLATFORM_ACCENTS:
            items.append({"area": "accent", "token": "semantic.action", "value": hexv,
                          "why": PLATFORM_ACCENTS[hexv.upper()]})
    tp = prims.get("type") or {}
    family = tp.get("family")
    ranged = any(v not in (None, "default", "standard") for v in family_range(tp, "default"))
    if isinstance(family, str) and family.strip().lower() in COMMON_FAMILIES and not ranged:
        items.append({"area": "type", "token": "primitives.type.family", "value": family,
                      "why": "the platform's or a very common family"})
    named = [("primitives.type.family", family)] + [(f"primitives.type.families.{k}", v)
                                                    for k, v in (tp.get("families") or {}).items()]
    for token, face in named:
        if isinstance(face, str) and face.strip().lower() in REFLEX_FACES:
            items.append({"area": "type", "token": token, "value": face,
                          "why": "a face models reach for by reflex — keep it with a reason beyond the "
                                 "subject (a serif for books is the association, not a reason)"})
    radius = {k: v for k, v in (prims.get("radius") or {}).items() if isinstance(v, (int, float))}
    if len(radius) >= 2 and len(set(radius.values())) == 1:
        items.append({"area": "shape", "token": "primitives.radius", "value": next(iter(radius.values())),
                      "why": "one radius on everything"})
    same, total = motion_defaults(model, template)
    if total and len(same) == total:
        items.append({"area": "motion", "token": "primitives.motion", "value": "every seed value",
                      "why": "springs, curves and durations are all Ship's seed values"})
    elif same:
        items.append({"area": "motion", "token": "primitives.motion", "value": f"{len(same)} of {total}",
                      "why": "some motion values are Ship's seed values: " + ", ".join(same[:4])
                             + ("…" if len(same) > 4 else "")})
    signs = tasteful_default(model)
    if len(signs) >= 3:
        items.append({"area": "look", "token": "semantic + primitives.type", "value": ", ".join(signs),
                      "why": "the AI default look: what AI gives everything meant to feel warm or handmade — keep it "
                             "only if this product's own material (its photos, signage, packaging) says so"})
    checked = ["accent", "type", "shape", "motion", "look"]
    return {"defaults": items, "areas_checked": checked,
            "still_default": sorted({i["area"] for i in items}),
            "note": "evidence, not a defect — defaults are fine when chosen; say whether these were"}


def format_report(rep):
    if not rep["defaults"]:
        return "Sameness: no brand-defining choice is still a default (accent, type, shape, motion, look)."
    lines = [f"Sameness: {len(rep['still_default'])} of {len(rep['areas_checked'])} brand-defining areas "
             f"are still defaults — {rep['note']}"]
    for i in rep["defaults"]:
        lines.append(f"  {i['area']:7} {i['token']} = {i['value']} — {i['why']}")
    return "\n".join(lines)
