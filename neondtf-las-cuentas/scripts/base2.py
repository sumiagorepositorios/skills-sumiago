import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
from base import (W, H, FPS, BLACK, BOLD, MED, BG, CYAN, MAG, LIME, WHITE, RED, clamp, prog, eo, eio, back, font,
                    add_glow, text_layer, put, rounded_mask, pill, bg_frame, flash, make_design, checker, photo_bg,
                    CURSOR, CHECK, logo, CARD, DS)

# ---------- artwork stages ----------
D = make_design()
S = CARD
light = checker(S, (235, 235, 240), (205, 205, 214))
pb = photo_bg(S)
def onto(bg, layer):
    b = bg.copy(); b.alpha_composite(layer, (80, 80)); return b
pix = D.resize((58, 58), Image.BILINEAR).resize((DS, DS), Image.NEAREST)
bad_d = pix.filter(ImageFilter.GaussianBlur(4))
dull = ImageEnhance.Color(D.filter(ImageFilter.GaussianBlur(4))).enhance(0.55)
STAGES = [np.asarray(x.convert("RGB")).copy() for x in
          [onto(pb, bad_d), onto(light, bad_d), onto(light, dull), onto(light, D)]]
CM = rounded_mask(CARD, CARD, 44)
GOOD = Image.fromarray(STAGES[3]).convert("RGBA")
BAD = Image.fromarray(STAGES[0]).convert("RGBA")

def card_img(arr, border=CYAN):
    c = Image.fromarray(arr).convert("RGBA"); c.putalpha(CM)
    fr = Image.new("RGBA", (CARD + 80, CARD + 80), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((40, 40, 40 + CARD, 40 + CARD), 46, outline=border + (255,), width=6)
    fr = add_glow(fr, border, 40, 1.3)
    fr.alpha_composite(c, (40, 40))
    return fr
_cf = {}
def frame_for(border):
    if border not in _cf:
        fr = Image.new("RGBA", (CARD + 80, CARD + 80), (0, 0, 0, 0))
        ImageDraw.Draw(fr).rounded_rectangle((40, 40, 40 + CARD, 40 + CARD), 46, outline=border + (255,), width=6)
        _cf[border] = add_glow(fr, border, 40, 1.3)
    return _cf[border]

def tint(f, col, a):
    if a > 0: f.alpha_composite(Image.new("RGBA", f.size, col + (int(255 * a),)))

_st = {}
def stamp(text, col, size=90, angle=-6):
    k = (text, col, size, angle)
    if k in _st: return _st[k]
    fnt = font(BLACK, size); bb = fnt.getbbox(text)
    w, h = bb[2] - bb[0] + 70, bb[3] - bb[1] + 50
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), 22, fill=(12, 12, 16, 235), outline=col + (255,), width=9)
    d.text((40 + w / 2 - (bb[0] + bb[2]) / 2, 40 + h / 2 - (bb[1] + bb[3]) / 2), text, font=fnt, fill=col + (255,))
    im = add_glow(im, col, 30, 0.9)
    im = im.rotate(angle, resample=Image.BICUBIC, expand=True)
    _st[k] = im; return im

def slam(f, layer, x, y, t, t0):
    a = prog(t, t0, t0 + 0.18)
    if a <= 0: return
    put(f, layer, x, y, scale=1.8 - 0.8 * eo(a), alpha=clamp(a * 2))

def clock_layer(hours, col=CYAN, r=150):
    cl = Image.new("RGBA", (420, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(cl); c = 210
    d.ellipse((c - r, c - r, c + r, c + r), outline=col + (255,), width=12)
    for i in range(12):
        an = i / 12 * 2 * math.pi
        d.line([(c + math.sin(an) * (r - 30), c - math.cos(an) * (r - 30)), (c + math.sin(an) * (r - 14), c - math.cos(an) * (r - 14))], fill=col + (255,), width=6)
    hm = hours * 2 * math.pi; hh = hours / 12 * 2 * math.pi
    d.line([(c, c), (c + math.sin(hm) * (r - 40), c - math.cos(hm) * (r - 40))], fill=WHITE + (255,), width=9)
    d.line([(c, c), (c + math.sin(hh) * (r - 75), c - math.cos(hh) * (r - 75))], fill=MAG + (255,), width=13)
    d.ellipse((c - 14, c - 14, c + 14, c + 14), fill=WHITE + (255,))
    return add_glow(cl, col, 30, 1.0)

def hour_str(h):
    h = h % 24; hh = int(h); mm = int((h - hh) * 60)
    ap = "PM" if 12 <= hh < 24 else "AM"
    h12 = hh % 12 or 12
    return "%d:%02d %s" % (h12, mm, ap)

# ---------- chat panel ----------
PW, PH = 920, 1020
_bub = {}
def bubble(kind, content, side):
    k = (kind, content if kind == "text" else id(content), side)
    if k in _bub: return _bub[k]
    col = (40, 44, 58) if side == "in" else (0, 92, 108)
    if kind == "text":
        txt, tc = content
        fnt = font(BOLD if tc != WHITE else MED, 46)
        bb = fnt.getbbox(txt)
        w, h = bb[2] - bb[0] + 60, 96
        im = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, w - 1, h - 1), 30, fill=col + (255,))
        d.text((30 - bb[0], h / 2 - (bb[1] + bb[3]) / 2), txt, font=fnt, fill=tc + (255,))
    else:
        sz = 380
        im = Image.new("RGBA", (sz + 24, sz + 24), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
        d.rounded_rectangle((0, 0, sz + 23, sz + 23), 30, fill=col + (255,))
        th = content.resize((sz, sz), Image.BILINEAR); th.putalpha(rounded_mask(sz, sz, 20))
        im.alpha_composite(th, (12, 12))
    _bub[k] = im; return im

def chat(t, title, msgs, typing_at=None):
    p = Image.new("RGBA", (PW, PH), (0, 0, 0, 0)); d = ImageDraw.Draw(p)
    d.rounded_rectangle((0, 0, PW - 1, PH - 1), 50, fill=(18, 20, 26, 245), outline=(60, 66, 84, 255), width=3)
    d.rounded_rectangle((0, 0, PW - 1, 130), 50, fill=(28, 31, 40, 255))
    d.rectangle((0, 80, PW - 1, 130), fill=(28, 31, 40, 255))
    d.ellipse((40, 30, 110, 100), fill=(90, 96, 120, 255))
    d.ellipse((62, 42, 88, 68), fill=(150, 156, 180, 255)); d.pieslice((48, 66, 102, 120), 180, 360, fill=(150, 156, 180, 255))
    d.text((135, 32), title, font=font(BOLD, 40), fill=WHITE + (255,))
    d.text((135, 80), "en línea", font=font(MED, 28), fill=(90, 230, 140, 255))
    y = 170
    for (t0, side, kind, content) in msgs:
        a = prog(t, t0, t0 + 0.22)
        if a <= 0: break
        b = bubble(kind, content, side)
        sc = 0.75 + 0.25 * back(a)
        bw, bh = int(b.width * sc), int(b.height * sc)
        bs = b.resize((bw, bh), Image.BILINEAR) if sc != 1 else b
        if a < 1:
            bs = bs.copy(); bs.putalpha(bs.getchannel("A").point(lambda v: int(v * clamp(a * 2))))
        x = 40 if side == "in" else PW - 40 - bw
        p.alpha_composite(bs, (x, y + (b.height - bh) // 2))
        y += b.height + 26
    if typing_at and typing_at[0] <= t < typing_at[1]:
        bw = 150
        d.rounded_rectangle((40, y, 40 + bw, y + 80), 30, fill=(40, 44, 58, 255))
        for i in range(3):
            o = 0.5 + 0.5 * math.sin(t * 10 - i * 0.9)
            d.ellipse((68 + i * 34 - 9, y + 40 - 9 - o * 8, 68 + i * 34 + 9, y + 40 + 9 - o * 8), fill=(170, 176, 196, 255))
    return p

# ---------- scenes ----------
def s1(t):  # 6.8
    f = bg_frame(t)
    a = eo(prog(t, 0.1, 0.45))
    put(f, text_layer("6:00 PM", 150, MAG, glow=MAG, gr=40), W / 2, 330, scale=0.7 + 0.3 * back(a), alpha=a)
    put(f, text_layer("Hora de cerrar el taller...", 50, (190, 195, 210), path=MED), W / 2, 450, alpha=eo(prog(t, 0.6, 0.9)))
    pa = eo(prog(t, 1.8, 2.15))
    msgs = [(2.15, "in", "text", ("Hola! Necesito 50 camisetas", WHITE)),
            (3.85, "in", "text", ("PARA MAÑANA", RED)),
            (4.7, "in", "img", BAD),
            (5.6, "in", "text", ("¿Se puede?", WHITE))]
    if pa > 0:
        put(f, chat(t, "Cliente nuevo", msgs, typing_at=(1.9, 2.15)), W / 2, 1110 + (1 - pa) * 120, alpha=pa)
    flash(f, t, 0.2, k=0.6)
    return f

def s2(t):  # 3.5
    f = bg_frame(t + 7)
    put(f, text_layer("El logo del cliente:", 70, WHITE, path=BOLD), W / 2, 330, alpha=eo(prog(t, 0, 0.25)))
    sc = 0.92 + 0.06 * t / 3.5
    jit = (math.sin(t * 90) * 4) if 1.2 < t < 1.35 else 0
    put(f, frame_for(RED), W / 2 + jit, 950, scale=sc)
    c = BAD.copy(); c.putalpha(CM)
    put(f, c, W / 2 + jit, 950, scale=sc)
    slam(f, stamp("BORROSO", RED, 84, 7), 330, 700, t, 1.2)
    slam(f, stamp("PIXELADO", RED, 84, -5), 720, 980, t, 1.8)
    slam(f, stamp("CON FONDO", RED, 84, 4), 420, 1260, t, 2.4)
    flash(f, t, 0.12, RED, 0.3)
    return f

def s3(t):  # 2.6
    f = bg_frame(t + 11)
    a = eo(prog(t, 0.1, 0.4))
    put(f, text_layer("Solo hay", 100, WHITE, path=BOLD), W / 2, 560, alpha=a)
    a = prog(t, 0.5, 0.85)
    put(f, text_layer("2 CAMINOS", 190, WHITE, glow=CYAN, gr=40, gs=0.8), W / 2, 740, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    a = eio(prog(t, 1.0, 1.7))
    ln = Image.new("RGBA", (W, 700), (0, 0, 0, 0)); d = ImageDraw.Draw(ln)
    sx, sy = W / 2, 40
    for (ex, ey, col) in [(250, 420, RED), (830, 420, CYAN)]:
        x1, y1 = sx + (ex - sx) * a, sy + (ey - sy) * a
        d.line([(sx, sy), (x1, y1)], fill=col + (255,), width=16)
        if a > 0.95:
            d.polygon([(ex - 40, ey - 10), (ex + 40, ey - 10), (ex, ey + 50)], fill=col + (255,))
    ln = add_glow(ln, WHITE, 20, 0.4)
    put(f, ln, W / 2, 1200)
    la = eo(prog(t, 1.5, 1.8))
    put(f, pill(330, 110, RED, "SIN", 64, tcolor=WHITE), 250, 1650, alpha=la)
    put(f, pill(400, 110, CYAN, "CON NEON", 56), 830, 1650, alpha=la)
    flash(f, t, 0.15, k=0.5)
    return f

def s4(t):  # 8.5  SIN
    f = bg_frame(t + 14)
    tint(f, (120, 0, 20), 0.18)
    put(f, pill(560, 110, RED, "SIN HERRAMIENTAS", 52, tcolor=WHITE), W / 2, 300, alpha=eo(prog(t, 0.05, 0.3)))
    fade = 1 - prog(t, 5.4, 5.7)
    if fade > 0:
        hrs = 18 + 9 * eio(prog(t, 1.5, 5.4))
        put(f, clock_layer(hrs, RED), W / 2, 680, alpha=fade * eo(prog(t, 0.3, 0.6)))
        put(f, text_layer(hour_str(hrs), 110, RED, path=BOLD, glow=RED, gr=26, gs=1.0), W / 2, 930, alpha=fade * eo(prog(t, 0.3, 0.6)))
        for j, (txt, t0) in enumerate([("Horas en Photoshop", 1.55), ("Tutorial tras tutorial", 2.95), ("Una noche sin dormir", 4.05)]):
            a = eo(prog(t, t0, t0 + 0.3))
            y = 1130 + j * 140
            put(f, stamp("X", RED, 50, 0), 180, y, alpha=a * fade, scale=0.85)
            put(f, text_layer(txt, 66, WHITE, path=BOLD), 250 + (1 - a) * 40, y, alpha=a * fade, anchor="l")
    if t > 5.5:
        msgs = [(5.6, "in", "text", ("¿Y el diseño? Ya es tarde...", WHITE)), (6.5, "in", "text", ("Mejor lo hago en otro lado.", WHITE))]
        put(f, chat(t, "Cliente nuevo", msgs, typing_at=(5.55, 5.6)).crop((0, 0, PW, 470)), W / 2, 720, alpha=eo(prog(t, 5.5, 5.7)))
        slam(f, stamp("CLIENTE PERDIDO", RED, 96, -5), W / 2, 1180, t, 7.0)
        a = eo(prog(t, 7.5, 7.8))
        put(f, text_layer("Y se fue con la competencia", 58, (230, 200, 205), path=MED), W / 2, 1420, alpha=a)
    flash(f, t, 0.12, RED, 0.35)
    return f

def s5(t):  # 9.2  CON
    f = bg_frame(t + 23)
    tint(f, (0, 60, 70), 0.10)
    put(f, pill(600, 110, CYAN, "CON NEON DTF", 56), W / 2, 300, alpha=eo(prog(t, 0.05, 0.3)))
    steps = [1.35, 2.45, 3.6]
    secs = int(167 * eio(prog(t, 1.2, 5.0)))
    done = t >= 5.35
    if not done:
        put(f, text_layer("%02d:%02d" % (secs // 60, secs % 60), 70, CYAN, path=BOLD, glow=CYAN, gr=20, gs=0.9), W / 2, 430, alpha=eo(prog(t, 0.8, 1.1)))
    else:
        a = prog(t, 5.35, 5.6)
        put(f, pill(700, 96, LIME, "LISTO EN 2:47 MIN", 50), W / 2, 430, scale=0.7 + 0.3 * back(a), alpha=clamp(a * 2))
    st = 0; sl = 0
    for k, s0 in enumerate(steps):
        if t >= s0: st = k; sl = eio(prog(t, s0, s0 + 0.7))
    if t < steps[0]: comp = STAGES[0]; xx = 0
    else:
        x = int(CARD * sl); comp = STAGES[st].copy(); comp[:, :x] = STAGES[st + 1][:, :x]; xx = x
    c = Image.fromarray(comp).convert("RGBA")
    if 0 < sl < 1:
        ImageDraw.Draw(c).rectangle((xx - 4, 0, xx + 4, CARD), fill=WHITE + (255,))
    c.putalpha(CM)
    border = LIME if done else CYAN
    sc = 0.78
    put(f, frame_for(border), W / 2, 960, scale=sc)
    put(f, c, W / 2, 960, scale=sc)
    if done:
        put(f, CHECK, W / 2 + 300, 650, scale=1.6 * back(prog(t, 5.4, 5.7)))
    labels = ["Quitar fondo", "Vectorizar", "Mejorar imagen"]
    for k, s0 in enumerate(steps):
        a = eo(prog(t, s0, s0 + 0.3)); y = 1400 + k * 110
        ok = t >= s0 + 0.7
        put(f, CHECK if ok else stamp("·", CYAN, 30, 0), 300, y, scale=0.75 if ok else 0.5, alpha=a)
        put(f, text_layer(labels[k], 62, WHITE if ok else (170, 175, 190), path=BOLD), 360, y, alpha=a, anchor="l")
    if 0.9 < t < 4.2:
        cp = 0.5 + 0.5 * math.sin(t * 3)
        put(f, CURSOR, 260 + 80 * cp, 1450 + (t - 0.9) * 60, alpha=0.9 * (1 - prog(t, 3.9, 4.2)))
    a = eo(prog(t, 5.6, 5.9))
    put(f, text_layer("Listo para imprimir", 64, LIME, glow=LIME, gr=20, gs=0.9), W / 2, 1720, alpha=a)
    flash(f, t, 0.18, CYAN, 0.45)
    return f

def s6(t):  # 4.6
    f = bg_frame(t + 32)
    slam(f, stamp("PEDIDO ENTREGADO", LIME, 92, -3), W / 2, 330, t, 0.15)
    msgs = [(0.3, "out", "img", GOOD), (1.25, "in", "text", ("¡Quedó perfecto!", WHITE)),
            (2.6, "in", "text", ("Te paso otro pedido de 100", LIME))]
    put(f, chat(t, "Cliente feliz", msgs).crop((0, 0, PW, 860)), W / 2, 1010, alpha=eo(prog(t, 0.0, 0.2)))
    a = prog(t, 2.8, 3.2)
    if a > 0:
        put(f, text_layer("+100", 160, LIME, glow=LIME, gr=40), W / 2, 1640 - 60 * eo(a), alpha=clamp(a * 3) * (1 - prog(t, 4.0, 4.5)), scale=0.6 + 0.4 * back(a))
    flash(f, t, 0.15, LIME, 0.35)
    return f

def s7(t):  # 4.5
    f = bg_frame(t + 37)
    put(f, text_layer("Porque en el DTF...", 70, (200, 205, 220), path=BOLD), W / 2, 520, alpha=eo(prog(t, 0.1, 0.4)))
    put(f, text_layer("es mejor", 110, WHITE, path=BOLD), W / 2, 700, alpha=eo(prog(t, 1.3, 1.6)))
    a = prog(t, 2.0, 2.35)
    put(f, text_layer("TENERLO", 195, CYAN, glow=CYAN, gr=56), W / 2, 900, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    a = eo(prog(t, 2.9, 3.2))
    put(f, text_layer("y no necesitarlo", 110, WHITE, path=BOLD), W / 2, 1110 + (1 - a) * 40, alpha=a)
    flash(f, t, 0.12, k=0.4)
    return f

def s8(t):  # 3.2
    f = bg_frame(t + 42)
    tint(f, (110, 0, 20), 0.22 * (1 - prog(t, 0.0, 0.5)) + 0.08)
    put(f, text_layer("que", 90, WHITE, path=BOLD), W / 2, 640, alpha=eo(prog(t, 0.05, 0.25)))
    a = prog(t, 0.25, 0.55)
    put(f, text_layer("NECESITARLO", 132, RED, glow=RED, gr=44), W / 2, 820, scale=0.5 + 0.5 * back(a), alpha=clamp(a * 3))
    a = prog(t, 1.0, 1.25)
    g = 14 * (1 - prog(t, 1.25, 1.9)) if a >= 1 else 0
    lay = text_layer("Y NO TENERLO.", 122, WHITE)
    if a > 0:
        if g > 0:
            put(f, text_layer("Y NO TENERLO.", 122, CYAN), W / 2 - g, 1040, alpha=0.6)
            put(f, text_layer("Y NO TENERLO.", 122, RED), W / 2 + g, 1040, alpha=0.6)
        put(f, lay, W / 2 + math.sin(t * 80) * g * 0.5, 1040, scale=1.6 - 0.6 * eo(a), alpha=clamp(a * 2))
    flash(f, t, 0.2, RED, 0.6)
    if 1.0 <= t < 1.2: flash(f, t - 1.0, 0.2, WHITE, 0.5)
    return f

def s9(t):  # 5.6
    f = bg_frame(t + 45)
    n = int(round(16 * eo(prog(t, 0.15, 1.4))))
    put(f, text_layer(str(n), 360, CYAN, glow=CYAN, gr=80, gs=1.5), W / 2, 470)
    put(f, text_layer("HERRAMIENTAS LISTAS", 72, WHITE), W / 2, 700, alpha=eo(prog(t, 0.3, 0.6)))
    put(f, text_layer("para el día que las necesites", 56, (200, 205, 220), path=MED), W / 2, 790, alpha=eo(prog(t, 1.6, 1.9)))
    s, g = 80, 18; tw = 4 * s + 3 * g
    gl = Image.new("RGBA", (tw + 120, tw + 120), (0, 0, 0, 0)); d = ImageDraw.Draw(gl)
    for k in range(16):
        r, c = divmod(k, 4); x, y = 60 + c * (s + g), 60 + r * (s + g)
        col = (MAG if (r + c) % 2 else CYAN) if k < n else (40, 42, 52)
        d.rounded_rectangle((x, y, x + s, y + s), 16, fill=col + (255,))
    gl = add_glow(gl, MAG, 24, 0.6)
    put(f, gl, W / 2, 900 + tw / 2 + 20, alpha=eo(prog(t, 0.1, 0.4)))
    a = prog(t, 3.75, 4.1)
    put(f, pill(800, 130, LIME, "MUCHAS SON GRATIS", 64), W / 2, 1530, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    flash(f, t, 0.15, CYAN, 0.4)
    return f

LG = logo(170)
def s10(t):  # 6.8
    f = bg_frame(t + 51)
    a = prog(t, 0.0, 0.4)
    put(f, LG, W / 2, 400, scale=0.75 + 0.25 * back(a), alpha=clamp(a * 2))
    a = prog(t, 0.4, 0.8)
    pulse = 1 + 0.04 * math.sin(max(0, t - 0.8) * 6.5)
    put(f, pill(860, 180, MAG, "ENTRA HOY", 90, tcolor=WHITE), W / 2, 700, scale=(0.6 + 0.4 * back(a)) * pulse, alpha=clamp(a * 2))
    a = eo(prog(t, 1.2, 1.5))
    put(f, text_layer("neondtf.store/herramientas", 62, CYAN, path=BOLD, glow=CYAN, gr=20, gs=1.0), W / 2, 900 + (1 - a) * 30, alpha=a)
    a = eo(prog(t, 2.9, 3.2))
    put(f, text_layer("antes de que llegue", 80, WHITE, path=BOLD), W / 2, 1100, alpha=a)
    put(f, text_layer("ese pedido", 80, WHITE, path=BOLD), W / 2, 1200, alpha=a)
    a = prog(t, 4.3, 4.6)
    put(f, stamp("URGENTE", RED, 110, -4), W / 2, 1370, scale=1.8 - 0.8 * eo(a), alpha=clamp(a * 2))
    a = eo(prog(t, 5.3, 5.6)); ay = 1580 + math.sin(t * 7) * 10
    put(f, text_layer("Link en el perfil", 64, LIME, glow=LIME, gr=20, gs=1.0), W / 2, ay, alpha=a)
    ar = Image.new("RGBA", (120, 120), (0, 0, 0, 0))
    ImageDraw.Draw(ar).polygon([(30, 30), (90, 30), (60, 85)], fill=LIME + (255,))
    put(f, ar, W / 2, ay + 90, alpha=a)
    flash(f, t, 0.15, MAG, 0.4)
    return f

SCENES = [("01", 6.8, s1), ("02", 3.5, s2), ("03", 2.6, s3), ("04", 8.5, s4), ("05", 9.2, s5), ("06", 4.6, s6),
          ("07", 4.5, s7), ("08", 3.2, s8), ("09", 5.6, s9), ("10", 6.8, s10)]

def render(idx):
    name, dur, fn = SCENES[idx]
    OUTD = os.path.join(os.getcwd(), "out"); out = os.path.join(OUTD, f"{name}.mp4"); tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(int(round(dur * FPS))):
        p.stdin.write(fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return name

if __name__ == "__main__":
    os.makedirs(os.path.join(os.getcwd(), "out"), exist_ok=True)
    if sys.argv[1] == "preview":
        ims = []
        for spec in sys.argv[2:]:
            i, t = spec.split("@")
            ims.append(SCENES[int(i)][2](float(t)).convert("RGB").resize((360, 640)))
        c = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): c.paste(im, (k * 360, 0))
        c.save("prueba.jpg", quality=88)
    else:
        from multiprocessing import Pool
        with Pool(2) as pool:
            for nm in pool.imap_unordered(render, range(len(SCENES))): print("done", nm, flush=True)
