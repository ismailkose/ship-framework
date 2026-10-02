"""Generated previews: ShipDesignPreview.swift (SwiftUI gallery + token-only sample screen),
a static HTML preview on the CSS variables, and a macOS PNG renderer for the SwiftUI one."""

import html
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from . import generated, motion
from .emit_swiftui import accessors, emit_swiftui, namespaces
from .emit_web import css_names, emit_css
from .registry import as_list, components, flatten, type_styles

num = motion.num


def swift_str(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"') + '"'


def _roles(model, acc):
    colors = acc["colors"]
    styles = type_styles(model.get("primitives") or {})
    by_size = sorted(styles, key=lambda k: styles[k]["size"] or 0)
    radius = acc["radius"]
    rkeys = sorted(radius, key=lambda k: (model["primitives"]["radius"][k]))
    return {
        "bg": colors.get("background"), "surface": colors.get("surface"), "text": colors.get("text"),
        "muted": colors.get("muted"), "hairline": colors.get("hairline"), "action": colors.get("action"),
        "title": acc["type"][by_size[-1]], "body": acc["type"].get("body", acc["type"][by_size[0]]),
        "caption": acc["type"][by_size[0]],
        "card": radius.get("card", radius[rkeys[-1]]), "control": radius.get("control", radius[rkeys[0]]),
        "space": namespaces(model)["spacing"],
    }


def emit_preview_swiftui(model, comps, include_snippets=True):
    acc = accessors(model)
    r = _roles(model, acc)
    sp = r["space"]
    prims = model.get("primitives") or {}
    L = ["import SwiftUI", "",
         "/// Component-library gallery + a sample screen built only from tokens.",
         "/// `scrolls: false` lets ImageRenderer draw the whole page (the PNG renderer uses it).",
         "struct ShipDesignPreview: View {",
         "    var scrolls = true", "",
         "    var body: some View {",
         "        if scrolls { ScrollView { content } } else { content }",
         "    }", "",
         "    private var content: some View {",
         f"        VStack(alignment: .leading, spacing: {sp}.x(6)) {{",
         f"            Text({swift_str((model.get('brand') or {}).get('name', 'Design system'))}).font({r['title']}).foregroundStyle({r['text']})",
         f"            Text({swift_str(' · '.join(str(f) for f in (model.get('brand') or {}).get('feel') or []))}).font({r['caption']}).foregroundStyle({r['muted']})",
         "",
         "            ShipPreviewSection(title: \"Colours\") {",
         f"                LazyVGrid(columns: [GridItem(.adaptive(minimum: 96), spacing: {sp}.x(3))], alignment: .leading, spacing: {sp}.x(3)) {{"]
    for key, expr in acc["colors"].items():
        L.append(f"                    ShipSwatch(name: {swift_str(key)}, color: {expr})")
    L += ["                }", "            }", "",
          "            ShipPreviewSection(title: \"Type\") {",
          f"                VStack(alignment: .leading, spacing: {sp}.x(2)) {{"]
    for key, spec in type_styles(prims).items():
        label = f"{key} · {spec['font']} {num(spec['size'])}"
        L.append(f"                    Text({swift_str(label)}).font({acc['type'][key]}).foregroundStyle({r['text']})")
    L += ["                }", "            }", "",
          "            ShipPreviewSection(title: \"Radius\") {",
          f"                HStack(spacing: {sp}.x(3)) {{"]
    for key, expr in acc["radius"].items():
        L.append(f"                    VStack {{ RoundedRectangle(cornerRadius: {expr}).fill({r['surface']})"
                 f".overlay(RoundedRectangle(cornerRadius: {expr}).stroke({r['hairline']})).frame(width: 64, height: 64); "
                 f"Text({swift_str(key)}).font({r['caption']}).foregroundStyle({r['muted']}) }}")
    L += ["                }", "            }", "",
          "            ShipPreviewSection(title: \"Spacing\") {",
          f"                VStack(alignment: .leading, spacing: {sp}.x(1)) {{"]
    for key, expr in acc["spacing"].items():
        L.append(f"                    HStack {{ Rectangle().fill({r['action']}).frame(width: {expr}, height: 8); "
                 f"Text({swift_str(key)}).font({r['caption']}).foregroundStyle({r['muted']}) }}")
    L += ["                }", "            }", "",
          "            ShipPreviewSection(title: \"Components\") {",
          f"                VStack(alignment: .leading, spacing: {sp}.x(3)) {{"]
    entries = components(comps)
    if not entries:
        L.append(f"                    Text(\"No registered components yet.\").font({r['body']}).foregroundStyle({r['muted']})")
    for c in entries:
        state = "planned" if c.get("planned") else "realized"
        variants = ", ".join(str(v) for v in as_list(c.get("variants")))
        meta = " · ".join(x for x in (str(c.get("role") or ""), state, variants) if x)
        snippet = ((c.get("preview") or {}).get("swiftui") if include_snippets and not c.get("planned") else None)
        L.append(f"                    ShipComponentCard(name: {swift_str(c.get('name'))}, meta: {swift_str(meta)}) {{")
        if snippet:
            L.append(f"                        {snippet}")
        else:
            L.append("                        EmptyView()")
        L.append("                    }")
    L += ["                }", "            }", "",
          "            ShipPreviewSection(title: \"Sample screen\") { ShipSampleScreen() }",
          "        }",
          f"        .padding({sp}.x(5))",
          f"        .background({r['bg']})",
          "    }",
          "}", "",
          "/// A small screen built only from tokens — the proof that the system composes.",
          "struct ShipSampleScreen: View {",
          "    var body: some View {",
          f"        VStack(alignment: .leading, spacing: {sp}.x(4)) {{",
          f"            Text(\"Today\").font({r['title']}).foregroundStyle({r['text']})",
          f"            VStack(alignment: .leading, spacing: {sp}.x(2)) {{",
          f"                Text(\"This week\").font({r['caption']}).foregroundStyle({r['muted']})",
          f"                Text(\"4 sessions · 3h 20m\").font({r['body']}).foregroundStyle({r['text']})",
          "            }",
          f"            .padding({sp}.x(4))",
          "            .frame(maxWidth: .infinity, alignment: .leading)",
          f"            .background({r['surface']}, in: RoundedRectangle(cornerRadius: {r['card']}))",
          f"            .overlay(RoundedRectangle(cornerRadius: {r['card']}).stroke({r['hairline']}))",
          "            VStack(spacing: 0) {",
          "                ForEach([\"Morning run\", \"Strength\", \"Stretch\"], id: \\.self) { item in",
          "                    HStack {",
          f"                        Text(item).font({r['body']}).foregroundStyle({r['text']})",
          "                        Spacer()",
          f"                        Text(\"›\").font({r['body']}).foregroundStyle({r['muted']})",
          "                    }",
          f"                    .padding(.vertical, {sp}.x(3))",
          f"                    Rectangle().fill({r['hairline']}).frame(height: 1)",
          "                }",
          "            }",
          "            Text(\"Start session\")",
          f"                .font({r['body']})",
          f"                .foregroundStyle({r['bg']})",
          "                .frame(maxWidth: .infinity)",
          f"                .padding(.vertical, {sp}.x(3))",
          f"                .background({r['action']}, in: RoundedRectangle(cornerRadius: {r['control']}))",
          "        }",
          f"        .padding({sp}.x(4))",
          f"        .background({r['bg']}, in: RoundedRectangle(cornerRadius: {r['card']}))",
          f"        .overlay(RoundedRectangle(cornerRadius: {r['card']}).stroke({r['hairline']}))",
          "    }",
          "}", "",
          "private struct ShipPreviewSection<Content: View>: View {",
          "    let title: String",
          "    @ViewBuilder let content: Content",
          "    var body: some View {",
          f"        VStack(alignment: .leading, spacing: {sp}.x(3)) {{",
          f"            Text(title.uppercased()).font({r['caption']}).foregroundStyle({r['muted']})",
          "            content",
          "        }",
          "    }",
          "}", "",
          "private struct ShipSwatch: View {",
          "    let name: String",
          "    let color: Color",
          "    var body: some View {",
          f"        VStack(alignment: .leading, spacing: {sp}.x(1)) {{",
          f"            RoundedRectangle(cornerRadius: {r['control']}).fill(color)",
          f"                .overlay(RoundedRectangle(cornerRadius: {r['control']}).stroke({r['hairline']}))",
          "                .frame(height: 48)",
          f"            Text(name).font({r['caption']}).foregroundStyle({r['text']}).lineLimit(1)",
          "        }",
          "    }",
          "}", "",
          "private struct ShipComponentCard<Content: View>: View {",
          "    let name: String",
          "    let meta: String",
          "    @ViewBuilder let content: Content",
          "    var body: some View {",
          f"        VStack(alignment: .leading, spacing: {sp}.x(2)) {{",
          f"            Text(name).font({r['body']}).foregroundStyle({r['text']})",
          f"            Text(meta).font({r['caption']}).foregroundStyle({r['muted']})",
          "            content",
          "        }",
          f"        .padding({sp}.x(3))",
          "        .frame(maxWidth: .infinity, alignment: .leading)",
          f"        .background({r['surface']}, in: RoundedRectangle(cornerRadius: {r['card']}))",
          "    }",
          "}", "",
          "#if DEBUG",
          "struct ShipDesignPreview_Previews: PreviewProvider {",
          "    static var previews: some View {",
          "        Group {",
          "            ShipDesignPreview()",
          "            ShipDesignPreview().preferredColorScheme(.dark)",
          "        }",
          "    }",
          "}",
          "#endif", ""]
    return "\n".join(L)


# ── HTML preview ─────────────────────────────────────────────────────────────

def emit_preview_html(model, comps):
    names = css_names(model)
    prims = model.get("primitives") or {}
    c = names["colors"]

    def v(key, fallback="currentColor"):
        return f"var({c[key]})" if key in c else fallback

    brand = model.get("brand") or {}
    styles = type_styles(prims)
    by_size = sorted(styles, key=lambda k: styles[k]["size"] or 0)
    tv = names["type"]
    title_t, body_t, cap_t = tv[by_size[-1]], tv.get("body", tv[by_size[0]]), tv[by_size[0]]
    rk = sorted(prims.get("radius") or {}, key=lambda k: prims["radius"][k])
    card_r = names["radius"].get("card", names["radius"][rk[-1]])
    ctl_r = names["radius"].get("control", names["radius"][rk[0]])
    unit = names["spacing"]["unit"]

    def font(t):
        return f"font-family: var({t}-family, system-ui); font-size: var({t}-size); font-weight: var({t}-weight);"

    swatches = "\n".join(
        f'<div class="sw"><div class="chip" style="background: var({var})"></div><code>{html.escape(key)}</code></div>'
        for key, var in c.items())
    type_rows = "\n".join(
        f'<p style="{font(names["type"][k])} margin: 0 0 calc(var({unit}) * 2)">{html.escape(k)} · {html.escape(str(s["font"]))} {num(s["size"])}</p>'
        for k, s in styles.items())
    radius_rows = "\n".join(
        f'<div class="rad"><div style="border-radius: var({var})"></div><code>{html.escape(k)}</code></div>'
        for k, var in names["radius"].items())
    space_rows = "\n".join(
        f'<div class="sp"><div style="width: var({var})"></div><code>{html.escape(k)}</code></div>'
        for k, var in names["spacing"].items())
    motion_rows = []
    for k, var in names["durations"].items():
        motion_rows.append(f'<button class="mo" style="--d: var({var}); --e: var({var}-ease)"><span></span>{html.escape(k)}</button>')
    for k, var in names["springs"].items():
        motion_rows.append(f'<button class="mo" style="--d: var({var}-duration); --e: var({var})"><span></span>{html.escape(k)} (spring)</button>')
    comp_rows = []
    for comp in components(comps):
        state = "planned" if comp.get("planned") else "realized"
        meta = " · ".join(x for x in (str(comp.get("role") or ""), state,
                                      ", ".join(str(x) for x in as_list(comp.get("variants")))) if x)
        snippet = (comp.get("preview") or {}).get("html") if not comp.get("planned") else None
        uw = "; ".join(str(x) for x in as_list(comp.get("use_when")))
        nf = "; ".join(str(x) for x in as_list(comp.get("not_for")))
        comp_rows.append(
            f'<article class="card"><h3>{html.escape(str(comp.get("name")))}</h3><p class="muted">{html.escape(meta)}</p>'
            + (f'<p>{html.escape(str(comp.get("doc")).strip())}</p>' if comp.get("doc") else "")
            + (f'<p class="muted">Use when: {html.escape(uw)}</p>' if uw else "")
            + (f'<p class="muted">Not for: {html.escape(nf)}</p>' if nf else "")
            + (f'<div class="demo">{snippet}</div>' if snippet else "")
            + "</article>")
    body = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(str(brand.get("name", "Design system")))} — design system</title>
<style>
{emit_css(model)}
* {{ box-sizing: border-box; }}
body {{ margin: 0; background: {v("background")}; color: {v("text")}; {font(body_t)} }}
main {{ max-width: 960px; margin: 0 auto; padding: calc(var({unit}) * 6) calc(var({unit}) * 4); }}
h1 {{ {font(title_t)} margin: 0; }}
h2 {{ {font(cap_t)} text-transform: uppercase; letter-spacing: .06em; color: {v("muted")}; margin: calc(var({unit}) * 10) 0 calc(var({unit}) * 3); }}
h3 {{ margin: 0; }}
.muted {{ color: {v("muted")}; {font(cap_t)} margin: calc(var({unit}) * 1) 0; }}
.modes {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: calc(var({unit}) * 4); }}
.mode {{ background: {v("background")}; color: {v("text")}; border: 1px solid {v("hairline")}; border-radius: var({card_r}); padding: calc(var({unit}) * 4); }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(96px, 1fr)); gap: calc(var({unit}) * 3); }}
.chip {{ height: 48px; border-radius: var({ctl_r}); border: 1px solid {v("hairline")}; }}
code {{ {font(cap_t)} font-family: ui-monospace, monospace; overflow-wrap: anywhere; }}
.rad {{ display: inline-flex; flex-direction: column; gap: 4px; margin-right: calc(var({unit}) * 3); }}
.rad div {{ width: 64px; height: 64px; background: {v("surface")}; border: 1px solid {v("hairline")}; }}
.sp {{ display: flex; align-items: center; gap: calc(var({unit}) * 2); margin: 4px 0; }}
.sp div {{ height: 8px; background: {v("action")}; }}
.mo {{ display: block; width: 100%; text-align: left; font: inherit; color: inherit; background: {v("surface")}; border: 1px solid {v("hairline")}; border-radius: var({ctl_r}); padding: calc(var({unit}) * 3); margin: 0 0 calc(var({unit}) * 2); cursor: pointer; position: relative; }}
.mo span {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; background: {v("action")}; margin-right: calc(var({unit}) * 2); transition: transform var(--d) var(--e); }}
.mo.on span {{ transform: translateX(180px); }}
.card {{ background: {v("surface")}; border-radius: var({card_r}); padding: calc(var({unit}) * 4); margin: 0 0 calc(var({unit}) * 3); }}
.screen {{ max-width: 375px; border: 1px solid {v("hairline")}; border-radius: var({card_r}); padding: calc(var({unit}) * 4); }}
.row {{ display: flex; justify-content: space-between; padding: calc(var({unit}) * 3) 0; border-bottom: 1px solid {v("hairline")}; }}
.cta {{ display: block; width: 100%; margin-top: calc(var({unit}) * 4); padding: calc(var({unit}) * 3); border: 0; border-radius: var({ctl_r}); background: {v("action")}; color: {v("background")}; font: inherit; }}
.toggle {{ position: fixed; top: 12px; right: 12px; font: inherit; }}
@media (prefers-reduced-motion: reduce) {{ .mo span {{ transition: none; }} }}
</style>
</head>
<body>
<button class="toggle" type="button" onclick="var r=document.documentElement;r.dataset.theme=r.dataset.theme==='dark'?'light':'dark'">Toggle theme</button>
<main>
<h1>{html.escape(str(brand.get("name", "Design system")))}</h1>
<p class="muted">{html.escape(" · ".join(str(f) for f in brand.get("feel") or []))}</p>

<h2>Colours — light and dark</h2>
<div class="modes">
<section class="mode" data-theme="light"><p class="muted">light</p><div class="grid">
{swatches}
</div></section>
<section class="mode" data-theme="dark"><p class="muted">dark</p><div class="grid">
{swatches}
</div></section>
</div>

<h2>Type</h2>
{type_rows}

<h2>Radius</h2>
{radius_rows}

<h2>Spacing</h2>
{space_rows}

<h2>Motion (CSS approximation — springs are sampled into linear())</h2>
{"".join(motion_rows) or '<p class="muted">No motion tokens.</p>'}

<h2>Components</h2>
{"".join(comp_rows) or '<p class="muted">No registered components yet.</p>'}

<h2>Sample screen</h2>
<div class="screen">
<h1>Today</h1>
<div class="card" style="margin-top: calc(var({unit}) * 4)"><p class="muted">This week</p><p style="margin:0">4 sessions · 3h 20m</p></div>
<div class="row"><span>Morning run</span><span class="muted">›</span></div>
<div class="row"><span>Strength</span><span class="muted">›</span></div>
<div class="row"><span>Stretch</span><span class="muted">›</span></div>
<button class="cta" type="button">Start session</button>
</div>
<p class="muted">This page mirrors design-model.yaml + design/components.yaml — regenerate after registry changes.</p>
</main>
<script>document.querySelectorAll('.mo').forEach(function(b){{b.addEventListener('click',function(){{b.classList.toggle('on')}})}})</script>
</body>
</html>
"""
    return body


# ── PNG renderer (macOS, no simulator) ───────────────────────────────────────

RENDER_MAIN = """import SwiftUI
import AppKit

let args = CommandLine.arguments
let outURL = URL(fileURLWithPath: args[1])
let dark = args.count > 2 && args[2] == "dark"
let width = args.count > 3 ? Double(args[3]) ?? 430 : 430

MainActor.assumeIsolated {
    let appearance = NSAppearance(named: dark ? .darkAqua : .aqua)!
    var png: Data?
    appearance.performAsCurrentDrawingAppearance {
        let view = ShipDesignPreview(scrolls: false)
            .frame(width: width)
            .environment(\\.colorScheme, dark ? .dark : .light)
        let renderer = ImageRenderer(content: view)
        renderer.scale = 2
        if let image = renderer.nsImage, let tiff = image.tiffRepresentation,
           let rep = NSBitmapImageRep(data: tiff) {
            png = rep.representation(using: .png, properties: [:])
        }
    }
    guard let data = png else { FileHandle.standardError.write("render failed\\n".data(using: .utf8)!); exit(1) }
    do { try data.write(to: outURL) } catch { FileHandle.standardError.write("\\(error)\\n".data(using: .utf8)!); exit(1) }
}
"""


def render_png(model, comps, root, out, schemes=("light",), width=430):
    """Compile Theme + preview (+ realized component files with preview snippets) for macOS and
    render with ImageRenderer. → (ok, messages, written paths)."""
    msgs = []
    if not shutil.which("xcrun"):
        return False, ["xcrun not found — the PNG renderer needs Xcode's command-line tools (macOS)"], []
    work = Path(tempfile.mkdtemp(prefix="ship-render-"))
    try:
        theme = work / "Theme.swift"
        theme.write_text(emit_swiftui(model), encoding="utf-8")
        comp_files = []
        for c in components(comps):
            if c.get("planned") or not (c.get("preview") or {}).get("swiftui"):
                continue
            src = root / str(c.get("file") or "")
            if src.is_file() and src.suffix == ".swift":
                comp_files.append(src)

        def build(with_components):
            (work / "ShipDesignPreview.swift").write_text(
                emit_preview_swiftui(model, comps, include_snippets=with_components), encoding="utf-8")
            (work / "main.swift").write_text(RENDER_MAIN, encoding="utf-8")
            files = [str(theme), str(work / "ShipDesignPreview.swift"), str(work / "main.swift")]
            if with_components:
                files += [str(p) for p in comp_files]
            cmd = ["xcrun", "swiftc", "-swift-version", "5", "-target", "arm64-apple-macos14.0",
                   "-module-cache-path", str(work / "mc"), "-o", str(work / "render")] + files
            return subprocess.run(cmd, capture_output=True, text=True)

        res = build(bool(comp_files))
        if res.returncode != 0 and comp_files:
            msgs.append("component sources don't compile standalone (they depend on other app code) — "
                        "rendered without component snippets")
            res = build(False)
        if res.returncode != 0:
            errs = [l for l in res.stderr.splitlines() if "error:" in l][:5]
            return False, msgs + ["compile failed:"] + errs, []
        written = []
        out = Path(out)
        out.parent.mkdir(parents=True, exist_ok=True)
        for scheme in schemes:
            target = out if len(schemes) == 1 else out.with_name(f"{out.stem}-{scheme}{out.suffix}")
            r = subprocess.run([str(work / "render"), str(target), scheme, str(width)],
                               capture_output=True, text=True, timeout=120)
            if r.returncode != 0 or not target.exists():
                return False, msgs + [f"render ({scheme}) failed: {r.stderr.strip()}"], written
            written.append(target)
        return True, msgs, written
    finally:
        shutil.rmtree(work, ignore_errors=True)
