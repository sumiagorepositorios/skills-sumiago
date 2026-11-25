import os as _os
AQUI = _os.path.dirname(_os.path.abspath(__file__))
RAIZ = _os.path.dirname(AQUI)
FONTS = _os.path.join(RAIZ, "fonts")
OUT = _os.path.join(_os.getcwd(), "out")
import math, random, os, sys, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
BLACK = _os.path.join(FONTS, "InterDisplay-Black.otf")
BOLD = _os.path.join(FONTS, "Poppins-Bold.ttf")
MED = _os.path.join(FONTS, "Poppins-Medium.ttf")

BG = (11, 12, 14)
CYAN = (0, 240, 255)
MAG = (255, 43, 214)
LIME = (182, 255, 59)
WHITE = (255, 255, 255)
RED = (255, 59, 80)

random.seed(3)

# ---------------- helpers ----------------
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)

def eo(x):  # ease out cubic
    x = clamp(x); return 1 - (1 - x) ** 3

def eio(x):
    x = clamp(x); return 3 * x * x - 2 * x * x * x

def back(x, s=1.7):
    x = clamp(x); x -= 1; return x * x * ((s + 1) * x + s) + 1

_fonts = {}
def font(path, size):
    k = (path, size)
    if k not in _fonts:
        _fonts[k] = ImageFont.truetype(path, size)
    return _fonts[k]

def add_glow(im, color, radius, strength=1.6):
    a = im.getchannel("A")
    sw, sh = max(1, im.width // 4), max(1, im.height // 4)
    small = a.resize((sw, sh), Image.BILINEAR).filter(ImageFilter.GaussianBlur(max(1, radius / 4)))
    g = small.resize(im.size, Image.BILINEAR).point(lambda v: min(255, int(v * strength)))
    glow = Image.new("RGBA", im.size, color + (0,))
    glow.putalpha(g)
    out = Image.alpha_composite(glow, im)
    return out

_tl = {}
def text_layer(text, size, color, path=BLACK, glow=None, gr=None, gs=1.6, stroke=0, stroke_fill=None):
    k = (text, size, color, path, glow, gr, gs, stroke, stroke_fill)
    if k in _tl:
        return _tl[k]
    f = font(path, size)
    bb = f.getbbox(text, stroke_width=stroke)
    w, h = bb[2] - bb[0], bb[3] - bb[1]
    pad = int(size * 0.4) + 24 if glow else 8 + stroke
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.text((pad - bb[0], pad - bb[1]), text, font=f, fill=color + (255,),
           stroke_width=stroke, stroke_fill=stroke_fill)
    if glow:
        im = add_glow(im, glow, gr or size * 0.25, gs)
    _tl[k] = im
    return im

def put(frame, layer, cx, cy, scale=1.0, alpha=1.0, anchor="c"):
    if alpha <= 0.003 or scale <= 0.01:
        return
    if abs(scale - 1) > 1e-3:
        layer = layer.resize((max(1, int(layer.width * scale)), max(1, int(layer.height * scale))), Image.BILINEAR)
    if alpha < 0.999:
        layer = layer.copy()
        a = np.asarray(layer.getchannel("A"), dtype=np.float32) * alpha
        layer.putalpha(Image.fromarray(a.astype(np.uint8)))
    w, h = layer.size
    x = int(round(cx - w / 2)) if anchor == "c" else int(round(cx))
    y = int(round(cy - h / 2))
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(frame.width, x + w), min(frame.height, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    crop = layer.crop((x0 - x, y0 - y, x1 - x, y1 - y))
    frame.alpha_composite(crop, dest=(x0, y0))

def rounded_mask(w, h, r):
    m = Image.new("L", (w, h), 0)
    ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m

_pills = {}
def pill(w, h, fill, text, tsize, tcolor=(10, 10, 14), glow=True, border=None):
    k = (w, h, fill, text, tsize, tcolor, glow, border)
    if k in _pills: return _pills[k]
    pad = 70 if glow else 6
    im = Image.new("RGBA", (w + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if fill:
        d.rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, fill=fill + (255,))
    if border:
        d.rounded_rectangle((pad, pad, pad + w, pad + h), h // 2, outline=border + (255,), width=5)
    if glow:
        im = add_glow(im, fill or border, 50, 1.1)
        d = ImageDraw.Draw(im)
    f = font(BLACK, tsize)
    bb = f.getbbox(text)
    d.text((pad + w / 2 - (bb[0] + bb[2]) / 2, pad + h / 2 - (bb[1] + bb[3]) / 2), text, font=f, fill=tcolor + (255,))
    _pills[k] = im
    return im

# ---------------- background ----------------
def make_bg():
    gh = H + 80
    yy, xx = np.mgrid[0:gh, 0:W].astype(np.float32)
    base = np.zeros((gh, W, 3), np.float32) + np.array(BG, np.float32)
    def blob(cx, cy, r, col, k):
        d = np.exp(-(((xx - cx) ** 2 + (yy - cy) ** 2) / (2 * r * r)))
        return d[..., None] * np.array(col, np.float32) * k
    base += blob(100, 300, 520, CYAN, 0.16)
    base += blob(1000, 1650, 600, MAG, 0.18)
    grid = ((xx % 80 < 2) | (yy % 80 < 2)).astype(np.float32)
    base += grid[..., None] * np.array([18, 22, 34], np.float32)
    # vignette
    v = ((xx - W / 2) / (W * 0.75)) ** 2 + ((yy - gh / 2) / (gh * 0.7)) ** 2
    base *= np.clip(1.15 - v * 0.6, 0.35, 1)[..., None]
    return np.clip(base, 0, 255).astype(np.uint8)

BGARR = make_bg()

def bg_frame(t):
    off = int(t * 36) % 80
    arr = BGARR[off:off + H]
    return Image.fromarray(arr).convert("RGBA")

def flash(frame, t, dur=0.18, col=WHITE, k=0.8):
    if t < dur:
        a = (1 - t / dur) * k
        ov = Image.new("RGBA", frame.size, col + (int(255 * a),))
        frame.alpha_composite(ov)

# ---------------- demo artwork ----------------
DS = 700
def make_design():
    im = Image.new("RGBA", (DS, DS), (0, 0, 0, 0))
    cx, cy, r = 350, 310, 280
    yy, xx = np.mgrid[0:DS, 0:DS].astype(np.float32)
    tt = np.clip((yy - (cy - r)) / (2 * r), 0, 1)[..., None]
    c1, c2, c3 = np.array([255, 40, 170.]), np.array([255, 120, 60.]), np.array([255, 225, 70.])
    col = np.where(tt < 0.5, c1 + (c2 - c1) * (tt / 0.5), c2 + (c3 - c2) * ((tt - 0.5) / 0.5))
    mask = ((xx - cx) ** 2 + (yy - cy) ** 2) < r * r
    for i, (y0, hh) in enumerate([(372, 7), (408, 10), (446, 14), (488, 18)]):
        mask &= ~((yy >= y0) & (yy < y0 + hh))
    arr = np.zeros((DS, DS, 4), np.uint8)
    arr[..., :3] = col.astype(np.uint8)
    arr[..., 3] = mask * 255
    im = Image.fromarray(arr)
    d = ImageDraw.Draw(im)
    d.polygon([(40, 560), (170, 380), (250, 450), (360, 300), (470, 430), (540, 360), (660, 560)], fill=(95, 35, 150, 255))
    d.polygon([(70, 560), (220, 450), (300, 500), (420, 410), (560, 520), (630, 560)], fill=(45, 15, 85, 255))
    # snow caps
    d.polygon([(360, 300), (330, 345), (350, 338), (365, 352), (392, 334)], fill=(255, 240, 250, 255))
    for (sx, sy, sr) in [(110, 110, 7), (600, 90, 6), (560, 200, 4), (150, 230, 5), (630, 280, 4)]:
        d.polygon([(sx, sy - sr * 3), (sx + sr, sy - sr), (sx + sr * 3, sy), (sx + sr, sy + sr), (sx, sy + sr * 3),
                   (sx - sr, sy + sr), (sx - sr * 3, sy), (sx - sr, sy - sr)], fill=(255, 255, 255, 255))
    f = font(BLACK, 200)
    txt = "WILD"
    bb = f.getbbox(txt, stroke_width=12)
    d.text((350 - (bb[0] + bb[2]) / 2, 610 - (bb[1] + bb[3]) / 2), txt, font=f, fill=(255, 255, 255, 255),
           stroke_width=12, stroke_fill=(30, 10, 60, 255))
    return im

def checker(size, c1, c2, s=44):
    yy, xx = np.mgrid[0:size, 0:size]
    m = ((xx // s + yy // s) % 2).astype(bool)
    arr = np.where(m[..., None], np.array(c1, np.uint8), np.array(c2, np.uint8)).astype(np.uint8)
    return Image.fromarray(arr).convert("RGBA")

def fabric(size, base=(28, 28, 33)):
    rng = np.random.default_rng(5)
    n = rng.normal(0, 5, (size, size, 1))
    yy, xx = np.mgrid[0:size, 0:size]
    weave = (np.sin(xx * 1.3) * np.sin(yy * 1.3))[..., None] * 3
    arr = np.clip(np.array(base, np.float32) + n + weave, 0, 255).astype(np.uint8)
    return Image.fromarray(np.repeat(arr, 1, axis=2) if arr.shape[2] == 3 else arr).convert("RGBA")

def photo_bg(size):
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32)
    t = (yy / size)[..., None]
    col = np.array([196, 178, 152.]) * (1 - t) + np.array([120, 110, 100.]) * t
    rng = np.random.default_rng(2)
    col += rng.normal(0, 7, (size, size, 1))
    for (bx, by, br, bc) in [(150, 200, 180, (90, 120, 80)), (720, 160, 220, (80, 100, 140)), (680, 760, 200, (150, 90, 70))]:
        dd = np.exp(-(((xx - bx) ** 2 + (yy - by) ** 2) / (2 * br * br)))[..., None]
        col = col * (1 - dd * 0.6) + np.array(bc, np.float32) * dd * 0.6
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8)).convert("RGBA")

def halftone(layer, cell=16, col=MAG):
    a = np.asarray(layer.getchannel("A"), np.float32) / 255
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    for y in range(0, layer.height, cell):
        for x in range(0, layer.width, cell):
            v = a[y:y + cell, x:x + cell].mean()
            if v > 0.03:
                r = cell * 0.62 * math.sqrt(v)
                c = (x + cell / 2, y + cell / 2)
                d.ellipse((c[0] - r, c[1] - r, c[0] + r, c[1] + r), fill=col + (255,))
    return out

CARD = 860
def on(bg, layer, off=(80, 80)):
    b = bg.copy()
    b.alpha_composite(layer, dest=off)
    return b

def build_tools():
    D = make_design()
    S = CARD
    dark_ck = checker(S, (44, 44, 52), (30, 30, 36))
    light_ck = checker(S, (235, 235, 240), (205, 205, 214))
    tee = fabric(S)
    tools = []
    # 1 background removal
    pb = photo_bg(S)
    shadow = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    sh = D.getchannel("A").filter(ImageFilter.GaussianBlur(18)).point(lambda v: int(v * 0.55))
    shl = Image.new("RGBA", D.size, (20, 10, 0, 0)); shl.putalpha(sh)
    before = on(on(pb, shl, (100, 105)), D)
    after = on(light_ck, D)
    tools.append(("QUITAR FONDO", "Sin recortar a mano.", before, after))
    # 2 vectorize
    pix = D.resize((58, 58), Image.BILINEAR).resize((DS, DS), Image.NEAREST)
    pix = pix.filter(ImageFilter.GaussianBlur(1.2))
    tools.append(("VECTORIZAR", "De pixelado a nítido para imprimir.", on(dark_ck, pix), on(dark_ck, D)))
    # 3 halftones
    glow = Image.new("RGBA", (DS + 0, DS), (0, 0, 0, 0))
    ga = D.getchannel("A").filter(ImageFilter.MaxFilter(41)).filter(ImageFilter.GaussianBlur(38))
    gl = Image.new("RGBA", D.size, MAG + (0,)); gl.putalpha(ga)
    soft = Image.alpha_composite(gl, D)
    ht = Image.alpha_composite(halftone(gl, 15), D)
    tools.append(("SEMITONOS", "Degradados listos para DTF.", on(tee, soft), on(tee, ht)))
    # 4 enhance
    blur = D.filter(ImageFilter.GaussianBlur(9))
    tools.append(("MEJORAR IMAGEN", "Fotos borrosas, ahora nítidas.", on(dark_ck, blur), on(dark_ck, D)))
    # 5 white halo
    dil = D.getchannel("A").filter(ImageFilter.MaxFilter(15)).filter(ImageFilter.GaussianBlur(2))
    ring = Image.new("RGBA", D.size, (250, 250, 250, 0)); ring.putalpha(dil.point(lambda v: int(v * 0.92)))
    haloed = Image.alpha_composite(ring, D)
    tools.append(("SIN HALO BLANCO", "Bordes limpios en la prenda.", on(tee, haloed), on(tee, D)))
    out = []
    for name, sub, b, a in tools:
        out.append((name, sub, np.asarray(b.convert("RGB")).copy(), np.asarray(a.convert("RGB")).copy()))
    return out

TOOLS = None
CMASK = None
def tools():
    global TOOLS, CMASK
    if TOOLS is None:
        TOOLS = build_tools()
        CMASK = rounded_mask(CARD, CARD, 44)
    return TOOLS

def cursor_layer():
    im = Image.new("RGBA", (90, 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    pts = [(8, 6), (8, 92), (30, 72), (46, 108), (62, 100), (46, 66), (76, 66)]
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(10, 10, 14, 255))
    d.line(pts + [pts[0]], fill=(10, 10, 14, 255), width=5)
    return im
CURSOR = cursor_layer()

def check_layer(size=70, col=LIME):
    im = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    o = size / 2
    d.ellipse((o, o, o + size, o + size), fill=col + (255,))
    d.line([(o + size * .27, o + size * .52), (o + size * .44, o + size * .69), (o + size * .75, o + size * .34)], fill=(10, 10, 14, 255), width=int(size * .12), joint="curve")
    return add_glow(im, col, 26, 1.2)
CHECK = check_layer()

# ---------------- scenes ----------------
def sc_hook(t):
    f = bg_frame(t)
    a1 = eo(prog(t, 0.05, 0.35))
    put(f, text_layer("¿SIGUES", 130, WHITE), W / 2, 470 + (1 - a1) * 60, alpha=a1)
    a2 = eo(prog(t, 0.3, 0.6))
    put(f, text_layer("PERDIENDO", 150, WHITE), W / 2, 620 + (1 - a2) * 60, alpha=a2)
    a3 = prog(t, 0.65, 0.95)
    sh = (math.sin(t * 70) * 9 * (1 - prog(t, 0.95, 1.6))) if t > 0.95 else 0
    put(f, text_layer("HORAS", 250, MAG, glow=MAG, gr=60), W / 2 + sh, 860, scale=0.4 + 0.6 * back(a3), alpha=clamp(a3 * 3))
    a4 = eo(prog(t, 1.2, 1.5))
    put(f, text_layer("en diseño?", 110, WHITE, path=BOLD), W / 2, 1080 + (1 - a4) * 50, alpha=a4)
    # clock
    a5 = eo(prog(t, 1.6, 2.0))
    if a5 > 0:
        cl = Image.new("RGBA", (420, 420), (0, 0, 0, 0))
        d = ImageDraw.Draw(cl)
        c = 210; r = 150
        d.ellipse((c - r, c - r, c + r, c + r), outline=CYAN + (255,), width=12)
        for i in range(12):
            an = i / 12 * 2 * math.pi
            d.line([(c + math.sin(an) * (r - 30), c - math.cos(an) * (r - 30)), (c + math.sin(an) * (r - 14), c - math.cos(an) * (r - 14))], fill=CYAN + (255,), width=6)
        sp = max(0, t - 1.6)
        hm = sp * 12 * math.pi * (1 + sp)
        hh = hm / 12
        d.line([(c, c), (c + math.sin(hm) * (r - 40), c - math.cos(hm) * (r - 40))], fill=WHITE + (255,), width=9)
        d.line([(c, c), (c + math.sin(hh) * (r - 75), c - math.cos(hh) * (r - 75))], fill=MAG + (255,), width=13)
        d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=WHITE + (255,))
        cl = add_glow(cl, CYAN, 30, 1.0)
        put(f, cl, W / 2, 1390, scale=0.7 + 0.3 * a5, alpha=a5)
        secs = int(3 * 3600 + 47 * 60 + sp * 2500 * (1 + sp))
        s = "%02d:%02d:%02d" % (secs // 3600, secs // 60 % 60, secs % 60)
        put(f, text_layer(s, 96, RED, path=BOLD, glow=RED, gr=24, gs=1.2), W / 2, 1640, alpha=a5)
    flash(f, t)
    return f

APPS = ["PHOTOSHOP", "ILLUSTRATOR", "CORELDRAW"]
def sc_pain(t):
    f = bg_frame(t + 5)
    put(f, text_layer("Lo de siempre:", 76, (170, 175, 190), path=BOLD), W / 2, 400, alpha=eo(prog(t, 0.0, 0.3)))
    strike = prog(t, 1.7, 2.3)
    for i, nm in enumerate(APPS):
        st0 = [0.1, 0.85, 2.1][i]; a = prog(t, st0, st0 + 0.45)
        y = 600 + i * 190
        dead = prog(t, 2.6 + i * 0.1, 2.85 + i * 0.1)
        col = tuple(int(c * (1 - dead) + 130 * dead) for c in (230, 232, 240))
        p = pill(720, 140, None, nm, 72, tcolor=col, glow=False, border=col)
        put(f, p, W / 2, y - (1 - back(a)) * 260, alpha=clamp(a * 2))
        if dead > 0:
            ln = Image.new("RGBA", (W, 60), (0, 0, 0, 0))
            d = ImageDraw.Draw(ln)
            x0, x1 = 150, 150 + 780 * eo(dead)
            d.line([(x0, 34), (x1, 26)], fill=RED + (255,), width=16)
            ln = add_glow(ln, RED, 20, 1.2)
            put(f, ln, W / 2, y)
    a = eo(prog(t, 2.85, 3.15))
    put(f, text_layer("Caros. Lentos.", 110, WHITE), W / 2, 1300 + (1 - a) * 40, alpha=a)
    a = eo(prog(t, 4.15, 4.45))
    put(f, text_layer("COMPLICADOS.", 130, RED, glow=RED, gr=34), W / 2, 1450, scale=0.6 + 0.4 * back(a), alpha=a)
    flash(f, t, 0.12, k=0.5)
    return f

def logo(size=150):
    a = text_layer("NEON", size, CYAN, glow=CYAN, gr=size * 0.3, gs=1.8)
    b = text_layer("DTF", size, MAG, glow=MAG, gr=size * 0.3, gs=1.8)
    gap = -2 * (int(size * 0.4) + 24) + int(size * 0.28)
    im = Image.new("RGBA", (a.width + b.width + gap, max(a.height, b.height)), (0, 0, 0, 0))
    im.alpha_composite(a, (0, 0)); im.alpha_composite(b, (a.width + gap, 0))
    return im
LOGO = None

def sc_reveal(t):
    global LOGO
    if LOGO is None: LOGO = logo(170)
    f = bg_frame(t + 9)
    a = eo(prog(t, 0.1, 0.4))
    put(f, text_layer("Hay una forma", 110, WHITE, path=BOLD), W / 2, 640 + (1 - a) * 50, alpha=a)
    a = prog(t, 0.45, 0.8)
    put(f, text_layer("MÁS FÁCIL", 190, LIME, glow=LIME, gr=50), W / 2, 820, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    a = prog(t, 2.2, 2.65)
    flick = 1.0 if t > 2.8 or int(t * 30) % 3 else 0.45
    put(f, LOGO, W / 2, 1180, scale=0.7 + 0.3 * back(a), alpha=clamp(a * 2) * flick)
    put(f, text_layer("E S T U D I O", 54, (220, 225, 235), path=BOLD), W / 2, 1340, alpha=eo(prog(t, 2.7, 3.1)))
    flash(f, t, 0.25, k=1.0)
    if 2.2 <= t < 2.4:
        flash(f, t - 2.2, 0.2, CYAN, 0.35)
    return f

TOOL_DUR = 4.5
def sc_tool(i):
    def fn(t):
        name, sub, before, after = tools()[i]
        f = bg_frame(t + 13 + i * 4)
        a = eo(prog(t, 0.0, 0.3))
        put(f, text_layer("HERRAMIENTA  %02d / 16" % (i + 1), 46, CYAN, path=BOLD), W / 2, 290 + (1 - a) * 30, alpha=a)
        ts = 116 if len(name) < 14 else 92
        put(f, text_layer(name, ts, WHITE, glow=MAG, gr=30, gs=0.9), W / 2, 400, scale=0.85 + 0.15 * back(a), alpha=a)
        # card
        sl = eio(prog(t, 1.35, 2.85))
        x = int(CARD * sl)
        comp = before.copy()
        if x > 0:
            comp[:, :x] = after[:, :x]
        card = Image.fromarray(comp).convert("RGBA")
        d = ImageDraw.Draw(card)
        if 0 < sl < 1:
            d.rectangle((x - 4, 0, x + 4, CARD), fill=WHITE + (255,))
            d.ellipse((x - 34, CARD / 2 - 34, x + 34, CARD / 2 + 34), fill=WHITE + (255,))
            d.polygon([(x - 8, CARD / 2 - 14), (x - 24, CARD / 2), (x - 8, CARD / 2 + 14)], fill=(20, 20, 26, 255))
            d.polygon([(x + 8, CARD / 2 - 14), (x + 24, CARD / 2), (x + 8, CARD / 2 + 14)], fill=(20, 20, 26, 255))
        lab_b = text_layer("ANTES", 40, WHITE, path=BOLD)
        lab_a = text_layer("DESPUÉS", 40, (10, 10, 14), path=BOLD)
        if x < CARD - 200:
            tag = Image.new("RGBA", (lab_b.width + 30, 70), (10, 10, 14, 200))
            tag.alpha_composite(lab_b, ((tag.width - lab_b.width) // 2, (70 - lab_b.height) // 2))
            card.alpha_composite(tag, (CARD - tag.width - 24, 24))
        if x > 230:
            tag = Image.new("RGBA", (lab_a.width + 30, 70), LIME + (240,))
            tag.alpha_composite(lab_a, ((tag.width - lab_a.width) // 2, (70 - lab_a.height) // 2))
            card.alpha_composite(tag, (24, 24))
        card.putalpha(CMASK)
        fr = Image.new("RGBA", (CARD + 80, CARD + 80), (0, 0, 0, 0))
        ImageDraw.Draw(fr).rounded_rectangle((40, 40, 40 + CARD, 40 + CARD), 46, outline=CYAN + (255,), width=6)
        if not hasattr(sc_tool, "frame"):
            sc_tool.frame = add_glow(fr, CYAN, 40, 1.3)
        ca = eo(prog(t, 0.1, 0.5))
        sc = 0.88 + 0.12 * ca
        put(f, sc_tool.frame, W / 2, 970, scale=sc, alpha=ca)
        put(f, card, W / 2, 970, scale=sc, alpha=ca)
        # button
        ba = eo(prog(t, 0.35, 0.65))
        press = prog(t, 1.12, 1.2) * (1 - prog(t, 1.2, 1.35))
        btn = pill(440, 120, MAG, "1 CLIC", 64, tcolor=WHITE)
        put(f, btn, W / 2, 1515, scale=(0.8 + 0.2 * back(ba)) * (1 - 0.08 * press), alpha=ba * (1 - prog(t, 2.85, 3.05)))
        # cursor
        cp = eio(prog(t, 0.5, 1.12))
        cx = 900 + (W / 2 + 40 - 900) * cp
        cy = 1800 + (1530 - 1800) * cp
        cal = clamp(prog(t, 0.5, 0.7)) * (1 - prog(t, 1.7, 2.0))
        put(f, CURSOR, cx + 45, cy + 60, scale=1 - 0.12 * press, alpha=cal)
        if 1.15 < t < 1.6:
            rr = (t - 1.15) / 0.45
            ring = Image.new("RGBA", (300, 300), (0, 0, 0, 0))
            R = 30 + 110 * rr
            ImageDraw.Draw(ring).ellipse((150 - R, 150 - R, 150 + R, 150 + R), outline=WHITE + (int(255 * (1 - rr)),), width=6)
            put(f, ring, W / 2 + 40, 1530)
        # done
        da = prog(t, 2.9, 3.2)
        if da > 0:
            put(f, CHECK, W / 2 - 250, 1515, scale=back(da), alpha=clamp(da * 2))
            put(f, text_layer("LISTO", 84, LIME, glow=LIME, gr=24, gs=1.0), W / 2 + 40, 1515, alpha=eo(da))
        sa = eo(prog(t, 3.1, 3.4))
        put(f, text_layer(sub, 58, (225, 228, 240), path=MED), W / 2, 1650 + (1 - sa) * 30, alpha=sa)
        flash(f, t, 0.12, CYAN, 0.35)
        return f
    return fn

def sc_stats(t):
    f = bg_frame(t + 40)
    n = int(round(16 * eo(prog(t, 0.15, 1.5))))
    put(f, text_layer(str(n), 400, CYAN, glow=CYAN, gr=80, gs=1.5), W / 2, 500, scale=1 + 0.06 * math.sin(t * 8) * (n == 16) * (1 - prog(t, 1.5, 2.2)))
    put(f, text_layer("HERRAMIENTAS ONLINE", 74, WHITE), W / 2, 760, alpha=eo(prog(t, 0.3, 0.6)))
    # grid of 16
    s, g = 72, 18
    tw = 4 * s + 3 * g
    ox, oy = W / 2 - tw / 2, 850
    gl = Image.new("RGBA", (tw + 120, tw + 120), (0, 0, 0, 0))
    d = ImageDraw.Draw(gl)
    for k in range(16):
        r, c = divmod(k, 4)
        x, y = 60 + c * (s + g), 60 + r * (s + g)
        lit = k < n
        col = (MAG if (r + c) % 2 else CYAN) if lit else (40, 42, 52)
        d.rounded_rectangle((x, y, x + s, y + s), 16, fill=col + (255,))
    gl = add_glow(gl, MAG, 24, 0.6) if n > 0 else gl
    put(f, gl, W / 2, oy + tw / 2, alpha=eo(prog(t, 0.1, 0.4)))
    chips = [("MUCHAS GRATIS", LIME, 2.35), ("SIN PHOTOSHOP NI COREL", CYAN, 3.0), ("TODO EN MENOS DE 3 MIN", MAG, 3.75)]
    for j, (txt, col, st) in enumerate(chips):
        a = prog(t, st, st + 0.35)
        p = pill(860, 112, col, txt, 54, tcolor=(10, 10, 14) if col != MAG else WHITE)
        put(f, p, W / 2 + (1 - back(a)) * -700, 1330 + j * 145, alpha=clamp(a * 2))
    flash(f, t, 0.15, MAG, 0.4)
    return f

def sc_sell(t):
    f = bg_frame(t + 46)
    a = eo(prog(t, 0.05, 0.35))
    put(f, text_layer("Tú enfócate en", 100, WHITE, path=BOLD), W / 2, 560 + (1 - a) * 40, alpha=a)
    a = prog(t, 0.9, 1.25)
    put(f, text_layer("VENDER", 250, LIME, glow=LIME, gr=60), W / 2, 760, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    a = eo(prog(t, 1.85, 2.15))
    put(f, text_layer("nosotros te ahorramos", 86, WHITE, path=BOLD), W / 2, 1060 + (1 - a) * 40, alpha=a)
    a = prog(t, 3.2, 3.55)
    put(f, text_layer("EL DISEÑO", 200, CYAN, glow=CYAN, gr=50), W / 2, 1250, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    flash(f, t, 0.12, k=0.5)
    return f

def sc_cta(t):
    global LOGO
    if LOGO is None: LOGO = logo(170)
    f = bg_frame(t + 50)
    a = prog(t, 0.0, 0.4)
    put(f, LOGO, W / 2, 420, scale=0.75 + 0.25 * back(a), alpha=clamp(a * 2))
    put(f, text_layer("16 herramientas para tu taller DTF", 56, (220, 225, 235), path=MED), W / 2, 590, alpha=eo(prog(t, 0.3, 0.6)))
    a = prog(t, 0.6, 1.0)
    pulse = 1 + 0.04 * math.sin(max(0, t - 1.0) * 6.5)
    press = prog(t, 2.3, 2.38) * (1 - prog(t, 2.38, 2.55))
    btn = pill(860, 190, MAG, "PRUÉBALAS GRATIS", 72, tcolor=WHITE)
    put(f, btn, W / 2, 900, scale=(0.6 + 0.4 * back(a)) * pulse * (1 - 0.07 * press), alpha=clamp(a * 2))
    cp = eio(prog(t, 1.5, 2.3))
    cal = prog(t, 1.5, 1.7) * (1 - prog(t, 3.0, 3.3))
    put(f, CURSOR, 980 + (640 - 980) * cp, 1500 + (960 - 1500) * cp, scale=1 - 0.12 * press, alpha=cal)
    if 2.35 < t < 2.85:
        rr = (t - 2.35) / 0.5
        ring = Image.new("RGBA", (360, 360), (0, 0, 0, 0)); R = 30 + 150 * rr
        ImageDraw.Draw(ring).ellipse((180 - R, 180 - R, 180 + R, 180 + R), outline=WHITE + (int(255 * (1 - rr)),), width=7)
        put(f, ring, 600, 905)
    a = eo(prog(t, 1.0, 1.3))
    put(f, text_layer("neondtf.store/herramientas", 70, CYAN, path=BOLD, glow=CYAN, gr=20, gs=1.0), W / 2, 1120 + (1 - a) * 30, alpha=a)
    a = eo(prog(t, 1.3, 1.6))
    put(f, text_layer("Tutoriales nuevos cada semana", 52, (210, 214, 226), path=MED), W / 2, 1250, alpha=a)
    put(f, text_layer("en YouTube y Telegram", 52, (210, 214, 226), path=MED), W / 2, 1320, alpha=a)
    a = eo(prog(t, 3.6, 3.9))
    arrow_y = 1500 + math.sin(t * 7) * 12
    put(f, text_layer("Link en el perfil", 70, LIME, glow=LIME, gr=20, gs=1.0), W / 2, arrow_y, alpha=a)
    ar = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    ImageDraw.Draw(ar).polygon([(30, 30), (90, 30), (60, 85)], fill=LIME + (255,))
    put(f, ar, W / 2, arrow_y + 100, alpha=a)
    fo = prog(t, 5.4, 6.0)
    if fo > 0:
        f.alpha_composite(Image.new("RGBA", f.size, BG + (int(255 * fo * 0.0),)))
    flash(f, t, 0.15, MAG, 0.4)
    return f

SCENES = [("01_hook", 4.5, sc_hook), ("02_pain", 5.6, sc_pain), ("03_reveal", 3.8, sc_reveal)]
for i in range(5):
    SCENES.append(("%02d_tool%d" % (4 + i, i + 1), TOOL_DUR, sc_tool(i)))
SCENES += [("09_stats", 6.0, sc_stats), ("10_sell", 4.5, sc_sell), ("11_cta", 6.5, sc_cta)]

def render(idx):
    name, dur, fn = SCENES[idx]
    out = _os.path.join(OUT, f"{name}.mp4")
    tmp = _os.path.join(OUT, f"{name}.tmp.mp4")
    n = int(round(dur * FPS))
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(n):
        p.stdin.write(fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0:
        os.replace(tmp, out)
    return name

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    mode = sys.argv[1]
    if mode == "preview":
        for spec in sys.argv[2:]:
            i, t = spec.split("@")
            SCENES[int(i)][2](float(t)).convert("RGB").save(f"prev_{i}_{t}.jpg", quality=88)
    else:
        from multiprocessing import Pool
        with Pool(2) as pool:
            for nm in pool.imap_unordered(render, range(len(SCENES))):
                print("done", nm, flush=True)
