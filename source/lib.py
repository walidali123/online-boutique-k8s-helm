"""Tiny diagram toolkit: absolutely-positioned cards + SVG arrows, rendered to PNG with Chromium."""
import base64, html, pathlib
from playwright.sync_api import sync_playwright

FONT_DIR = pathlib.Path("/home/claude/fonts/node_modules/@fontsource")
W, H = 1920, 1080

def _font(face, path, weight):
    b64 = base64.b64encode((FONT_DIR / path).read_bytes()).decode()
    return f"@font-face{{font-family:'{face}';font-weight:{weight};src:url(data:font/woff2;base64,{b64}) format('woff2');}}"

FONTS = "".join(
    [_font("Inter", f"inter/files/inter-latin-{w}-normal.woff2", w) for w in (400, 500, 600, 700, 800)]
    + [_font("JBM", f"jetbrains-mono/files/jetbrains-mono-latin-{w}-normal.woff2", w) for w in (400, 500)]
)

# category -> (accent, tint)
C = {
    "src":   ("#334155", "#F1F5F9"),
    "ci":    ("#4F46E5", "#EEF2FF"),
    "reg":   ("#0284C7", "#E0F2FE"),
    "proxy": ("#059669", "#D1FAE5"),
    "web":   ("#D97706", "#FEF3C7"),
    "api":   ("#7C3AED", "#EDE9FE"),
    "db":    ("#E11D48", "#FFE4E6"),
    "store": ("#475569", "#E2E8F0"),
    "sec":   ("#0F766E", "#CCFBF1"),
}

I = {  # 24x24 stroke icons (generic, no brand logos)
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4.2 3.6-6.5 8-6.5s8 2.3 8 6.5"/>',
    "branch": '<circle cx="6" cy="5" r="2.2"/><circle cx="6" cy="19" r="2.2"/><circle cx="18" cy="7" r="2.2"/><path d="M6 7.2v9.6M18 9.2c0 5-12 2.8-12 7.6"/>',
    "play": '<circle cx="12" cy="12" r="9"/><path d="M10 8.5l5.5 3.5-5.5 3.5z"/>',
    "layers": '<path d="M12 3l9 4.5-9 4.5-9-4.5z"/><path d="M3 12l9 4.5 9-4.5"/><path d="M3 16.5l9 4.5 9-4.5"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><ellipse cx="12" cy="12" rx="4" ry="9"/><path d="M3 12h18"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8.2-8 9.2-4.5-1-8-4.2-8-9.2V6z"/>',
    "server": '<rect x="3" y="4" width="18" height="7" rx="2"/><rect x="3" y="13" width="18" height="7" rx="2"/><path d="M7 7.5h.01M7 16.5h.01"/>',
    "db": '<ellipse cx="12" cy="5.5" rx="8" ry="3"/><path d="M4 5.5v13c0 1.7 3.6 3 8 3s8-1.3 8-3v-13"/><path d="M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "cube": '<path d="M12 2.5l8.5 4.8v9.4L12 21.5l-8.5-4.8V7.3z"/><path d="M12 12l8.5-4.7M12 12v9.5M12 12L3.5 7.3"/>',
    "lock": '<rect x="5" y="11" width="14" height="10" rx="2"/><path d="M8 11V7.5a4 4 0 018 0V11"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16.5 6.5l3 3"/>',
    "code": '<path d="M8 7l-5 5 5 5M16 7l5 5-5 5"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9.5l3 2.5-3 2.5M12.5 15h4.5"/>',
    "net": '<circle cx="12" cy="5" r="2.2"/><circle cx="5" cy="18" r="2.2"/><circle cx="19" cy="18" r="2.2"/><path d="M12 7.2v4.3M12 11.5L6.5 16.3M12 11.5l5.5 4.8"/>',
    "disk": '<rect x="3" y="6" width="18" height="12" rx="2"/><path d="M16.5 12h.01M6.5 12h6"/>',
    "check": '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    "redirect": '<path d="M4 12h14M13 6.5l5.5 5.5-5.5 5.5"/>',
    "cert": '<rect x="4" y="3" width="16" height="13" rx="2"/><circle cx="12" cy="17" r="3"/><path d="M10.5 19.5L10 22l2-1 2 1-.5-2.5M8 7h8M8 10h5"/>',
    "file": '<path d="M6 3h8l4 4v14H6z"/><path d="M14 3v4h4M9 12h6M9 16h6"/>',
    "clone": '<rect x="8" y="8" width="12" height="12" rx="2"/><path d="M16 8V5a1 1 0 00-1-1H5a1 1 0 00-1 1v10a1 1 0 001 1h3"/>',
    "eye": '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/>',
}

def icon(name, color, size=26):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">{I[name]}</svg>')

e = html.escape

class Diagram:
    def __init__(self, eyebrow, title, subtitle):
        self.parts, self.arrows, self.labels = [], [], []
        self.eyebrow, self.title, self.subtitle = eyebrow, title, subtitle

    # ---- building blocks -------------------------------------------------
    def zone(self, x, y, w, h, label, cat="src", dashed=True, fill="#FBFCFE", note=None):
        a, t = C[cat]
        style = "dashed" if dashed else "solid"
        n = f'<div class="znote">{note}</div>' if note else ""
        self.parts.append(
            f'<div class="zone" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;'
            f'border:2px {style} {a}55;background:{fill}">'
            f'<div class="zlabel" style="color:{a};background:{t}">{label}</div>{n}</div>')

    def node(self, x, y, w, h, cat, ic, title, sub="", chips=(), big=False, center=False):
        a, t = C[cat]
        chip_html = "".join(f'<span class="chip" style="color:{a};background:{t}">{e(c)}</span>' for c in chips)
        sub_html = f'<div class="nsub">{sub}</div>' if sub else ""
        cls = "node big" if big else "node"
        if center: cls += " center"
        self.parts.append(
            f'<div class="{cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;--a:{a}">'
            f'<div class="nhead"><div class="ic" style="background:{t}">{icon(ic, a)}</div>'
            f'<div class="ntitle">{title}</div></div>{sub_html}'
            f'<div class="chips">{chip_html}</div></div>')

    def pill(self, x, y, text, cat="src", mono=False, anchor="center"):
        a, t = C[cat]
        tr = {"center": "translate(-50%,-50%)", "left": "translate(0,-50%)", "right": "translate(-100%,-50%)"}[anchor]
        f = "JBM" if mono else "Inter"
        self.labels.append(f'<div class="pill" style="left:{x}px;top:{y}px;transform:{tr};color:{a};'
                           f'border-color:{a}40;font-family:{f}">{text}</div>')

    def text(self, x, y, w, content, size=17, color="#475569", weight=500, align="left"):
        self.parts.append(f'<div style="position:absolute;left:{x}px;top:{y}px;width:{w}px;font-size:{size}px;'
                          f'color:{color};font-weight:{weight};text-align:{align};line-height:1.45">{content}</div>')

    def raw(self, s):
        self.parts.append(s)

    def arrow(self, pts, color="#64748B", dashed=False, width=2.6, head=True, both=False):
        d = "M" + " L".join(f"{x},{y}" for x, y in pts)
        mid = f"m{abs(hash((tuple(pts), color))) % 10**8}"
        dash = 'stroke-dasharray="9 8"' if dashed else ""
        ms = f'marker-end="url(#{mid})"' if head else ""
        mstart = f'marker-start="url(#{mid}s)"' if both else ""
        self.arrows.append(
            f'<defs><marker id="{mid}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M0,0 L10,5 L0,10 z" fill="{color}"/></marker>'
            f'<marker id="{mid}s" viewBox="0 0 10 10" refX="1.5" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
            f'<path d="M10,0 L0,5 L10,10 z" fill="{color}"/></marker></defs>'
            f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" {dash} {ms} {mstart}/>')

    def legend(self, items, y=1030, x=80):
        html_items = "".join(
            f'<span class="lg"><i style="background:{C[c][0]}"></i>{e(t)}</span>' for c, t in items)
        self.parts.append(f'<div class="legend" style="left:{x}px;top:{y}px">{html_items}</div>')

    # ---- render ------------------------------------------------------------
    def html(self):
        return f"""<!doctype html><html><head><meta charset="utf-8"><style>
{FONTS}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{width:{W}px;height:{H}px;font-family:Inter,sans-serif;color:#0F172A;background:#fff;
  -webkit-font-smoothing:antialiased}}
.canvas{{position:relative;width:{W}px;height:{H}px;overflow:hidden;
  background-image:radial-gradient(#E2E8F0 1.1px,transparent 1.1px);background-size:28px 28px;background-color:#fff}}
.hdr{{position:absolute;left:80px;top:56px;right:80px}}
.eyebrow{{font-size:15px;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#4F46E5}}
.title{{font-size:44px;font-weight:800;letter-spacing:-.02em;margin-top:10px}}
.subtitle{{font-size:20px;color:#64748B;margin-top:8px;font-weight:500}}
.zone{{position:absolute;border-radius:22px}}
.zlabel{{position:absolute;left:22px;top:-15px;font-size:14px;font-weight:700;letter-spacing:.08em;
  text-transform:uppercase;padding:5px 12px;border-radius:8px}}
.znote{{position:absolute;right:22px;top:-13px;font:500 14px JBM,monospace;color:#64748B;background:#fff;
  padding:3px 10px;border-radius:6px;border:1px solid #E2E8F0}}
.node{{position:absolute;background:#fff;border-radius:16px;border:1.5px solid #E2E8F0;
  box-shadow:0 1px 2px rgba(15,23,42,.05),0 10px 28px rgba(15,23,42,.07);padding:18px 20px 16px 24px;overflow:hidden}}
.node::before{{content:"";position:absolute;left:0;top:0;bottom:0;width:6px;background:var(--a)}}
.nhead{{display:flex;align-items:center;gap:13px}}
.ic{{width:46px;height:46px;border-radius:12px;display:flex;align-items:center;justify-content:center;flex:none}}
.ntitle{{font-size:21px;font-weight:700;letter-spacing:-.01em;line-height:1.2}}
.nsub{{font-size:16px;color:#475569;margin-top:10px;line-height:1.45;font-weight:500}}
.chips{{display:flex;flex-wrap:wrap;gap:7px;margin-top:11px}}
.chip{{font:500 13.5px JBM,monospace;padding:4px 9px;border-radius:7px;white-space:nowrap}}
.node.center .nhead{{flex-direction:column;text-align:center;gap:10px}}
.node.center .nsub,.node.center{{text-align:center}}
.node.center .chips{{justify-content:center}}
.pill{{position:absolute;background:#fff;border:1.5px solid;border-radius:999px;padding:5px 13px;
  font-size:14.5px;font-weight:600;white-space:nowrap;box-shadow:0 2px 6px rgba(15,23,42,.06);z-index:5}}
svg.wires{{position:absolute;left:0;top:0;z-index:4;pointer-events:none}}
.legend{{position:absolute;display:flex;gap:26px;font-size:15px;color:#475569;font-weight:500}}
.lg{{display:flex;align-items:center;gap:8px}} .lg i{{width:12px;height:12px;border-radius:3px;display:inline-block}}
.foot{{position:absolute;right:80px;bottom:34px;font-size:14px;color:#94A3B8;font-weight:500}}
code,.mono{{font-family:JBM,monospace}}
</style></head><body><div class="canvas">
<div class="hdr"><div class="eyebrow">{self.eyebrow}</div><div class="title">{self.title}</div>
<div class="subtitle">{self.subtitle}</div></div>
{''.join(self.parts)}
<svg class="wires" width="{W}" height="{H}">{''.join(self.arrows)}</svg>
{''.join(self.labels)}
<div class="foot">Based strictly on repository configuration · Challenge-solve</div>
</div></body></html>"""

    def render(self, out_png, scale=2):
        out_png = pathlib.Path(out_png)
        out_png.parent.mkdir(parents=True, exist_ok=True)
        src = out_png.with_suffix(".html")
        src.write_text(self.html())
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": W, "height": H}, device_scale_factor=scale)
            pg.goto(src.as_uri()); pg.wait_for_timeout(250)
            pg.screenshot(path=str(out_png), full_page=False)
            b.close()
        return out_png
