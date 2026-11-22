"""Video del Día 7 (de desempleado a vender en Sumiago), 1080x1920 a 30 fps.
Uso (en tu carpeta de trabajo, con timeline.json):
    python scripts/render.py still 1.5 8 20       -> st/1.5.jpg ... cuadros de muestra (crea antes la carpeta st)
    python scripts/render.py video 0 8            -> out/p00.mp4 (parte 0 de 8; corre las 8 partes, 0 a 7, en paralelo si puedes)
"""
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
import json, math, sys, os, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scenes import *
from faces import V, BOX

FPS = 30
WW, HH = 1080, 1920
FD = os.path.join(_AQUI, '..', 'fonts') + os.sep
_fc = {}
def F(sz, w='Bold'):
    k = (sz, w)
    if k not in _fc: _fc[k] = ImageFont.truetype(FD + f'Poppins-{w}.ttf', sz)
    return _fc[k]

RED = (220, 24, 38); DARK = (26, 26, 30); GREY = (120, 124, 132); LG = (232, 234, 238); WHITE = (255, 255, 255)
MOUTH = TL['mouth']
REPO = _ASSETS
LOGO = Image.open(REPO + 'logo-sumiago.png').convert('RGBA')
PULGAR = Image.open(REPO + 'mascota-pulgar.png').convert('RGBA')

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def outback(x):
    x = max(0, min(1, x)); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def lerp(a, b, t): return a + (b - a) * t

# ---------------------------------------------------------------- drawing helpers
def rr(d, box, r, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

def shadow_card(img, box, r=28, fill=WHITE, blur=18, off=10, alpha=60):
    x0, y0, x1, y1 = [int(v) for v in box]
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    sd.rounded_rectangle((x0, y0 + off, x1, y1 + off), r, fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)); img.alpha_composite(sh)
    ImageDraw.Draw(img).rounded_rectangle((x0, y0, x1, y1), r, fill=fill)

def layer_alpha(img, a):
    if a >= 1: return img
    r = img.copy(); al = r.getchannel('A').point(lambda v: int(v * a)); r.putalpha(al); return r

def paste_scaled(dst, src, cx, cy, sc, a=1.0):
    if sc <= 0.01 or a <= 0.01: return
    w, h = max(1, int(src.width * sc)), max(1, int(src.height * sc))
    s = src.resize((w, h), Image.LANCZOS)
    s = layer_alpha(s, a)
    dst.alpha_composite(s, (int(cx - w / 2), int(cy - h / 2)))

def text_c(d, xy, s, f, fill, anchor='mm', **kw):
    d.text(xy, s, font=f, fill=fill, anchor=anchor, **kw)

# --- icons (drawn on own RGBA, centered, size ~ 200)
def icon_headphones(sz=200, col=DARK):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = sz / 200
    d.arc((30 * s, 25 * s, 170 * s, 165 * s), 180, 360, fill=col, width=int(16 * s))
    rr(d, (18 * s, 95 * s, 62 * s, 170 * s), int(16 * s), fill=RED)
    rr(d, (138 * s, 95 * s, 182 * s, 170 * s), int(16 * s), fill=RED)
    return im
def icon_watch(sz=200, col=DARK):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = sz / 200
    rr(d, (72 * s, 8 * s, 128 * s, 192 * s), int(14 * s), fill=col)
    d.ellipse((40 * s, 40 * s, 160 * s, 160 * s), fill=RED)
    d.ellipse((54 * s, 54 * s, 146 * s, 146 * s), fill=WHITE)
    d.line((100 * s, 100 * s, 100 * s, 68 * s), fill=DARK, width=int(8 * s))
    d.line((100 * s, 100 * s, 124 * s, 112 * s), fill=DARK, width=int(8 * s))
    return im
def icon_lamp(sz=200, col=DARK):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = sz / 200
    d.polygon([(60 * s, 20 * s), (140 * s, 20 * s), (170 * s, 90 * s), (30 * s, 90 * s)], fill=RED)
    d.rectangle((94 * s, 90 * s, 106 * s, 165 * s), fill=col)
    rr(d, (50 * s, 160 * s, 150 * s, 182 * s), int(10 * s), fill=col)
    d.ellipse((85 * s, 88 * s, 115 * s, 112 * s), fill=(255, 214, 80))
    return im
def icon_box(sz=200):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = sz / 200
    d.polygon([(20 * s, 60 * s), (100 * s, 25 * s), (180 * s, 60 * s), (100 * s, 95 * s)], fill=(222, 178, 120))
    d.polygon([(20 * s, 60 * s), (100 * s, 95 * s), (100 * s, 185 * s), (20 * s, 150 * s)], fill=(196, 146, 88))
    d.polygon([(180 * s, 60 * s), (100 * s, 95 * s), (100 * s, 185 * s), (180 * s, 150 * s)], fill=(176, 126, 70))
    d.polygon([(55 * s, 45 * s), (135 * s, 80 * s), (135 * s, 92 * s), (55 * s, 57 * s)], fill=(240, 220, 180))
    return im
ICONS = {'aud': icon_headphones(), 'rel': icon_watch(), 'lam': icon_lamp(), 'box': icon_box()}
def icon(k, sz):
    return ICONS[k].resize((sz, sz), Image.LANCZOS)

# ---------------------------------------------------------------- backgrounds (world, 1080x1920)
def grid_bg(col=(250, 250, 251)):
    im = Image.new('RGBA', (WW, HH), col + (255,)); d = ImageDraw.Draw(im)
    for x in range(0, WW, 60): d.line((x, 0, x, HH), fill=(238, 239, 242), width=2)
    for y in range(0, HH, 60): d.line((0, y, WW, y), fill=(238, 239, 242), width=2)
    return im

def floor(d, y, col=(236, 236, 240), line=(222, 223, 228)):
    d.rectangle((0, y, WW, HH), fill=col); d.line((0, y, WW, y), fill=line, width=6)

def bg_office():
    im = Image.new('RGBA', (WW, HH), (247, 247, 249, 255)); d = ImageDraw.Draw(im)
    # window with blinds
    rr(d, (70, 520, 430, 1060), 14, fill=(232, 240, 248), outline=(205, 210, 220), width=10)
    for y in range(545, 1050, 34): d.line((80, y, 420, y), fill=(214, 220, 230), width=10)
    # sign
    rr(d, (560, 560, 1010, 660), 16, fill=WHITE, outline=(220, 222, 228), width=4)
    text_c(d, (785, 610), 'RECURSOS HUMANOS', F(34), GREY)
    # clock
    d.ellipse((780, 740, 900, 860), fill=WHITE, outline=(200, 204, 212), width=8)
    d.line((840, 800, 840, 760), fill=DARK, width=6); d.line((840, 800, 870, 815), fill=DARK, width=6)
    floor(d, 1640)
    # desk
    rr(d, (640, 1260, 1080, 1300), 10, fill=(200, 205, 214)); d.rectangle((690, 1300, 715, 1640), fill=(185, 190, 200)); d.rectangle((1010, 1300, 1035, 1640), fill=(185, 190, 200))
    rr(d, (760, 1060, 1000, 1220), 12, fill=(60, 64, 72)); rr(d, (772, 1072, 988, 1208), 6, fill=(200, 215, 230)); d.rectangle((865, 1220, 895, 1262), fill=(60, 64, 72))
    # plant
    d.polygon([(110, 1640), (210, 1640), (195, 1520), (125, 1520)], fill=(210, 212, 218))
    for a in (-40, -15, 10, 35): d.ellipse((140 + a * 2, 1380 + abs(a), 200 + a * 2, 1520), fill=(150, 196, 150))
    return im

def bg_street():
    im = Image.new('RGBA', (WW, HH), (236, 239, 243, 255)); d = ImageDraw.Draw(im)
    for i, (x, w, h) in enumerate([(-40, 300, 900), (240, 260, 1100), (480, 320, 820), (780, 340, 1020)]):
        y0 = 1600 - h; d.rectangle((x, y0, x + w, 1600), fill=(214, 218, 226))
        for wy in range(y0 + 60, 1540, 110):
            for wx in range(x + 40, x + w - 50, 90): d.rectangle((wx, wy, wx + 48, wy + 64), fill=(228, 232, 238))
    # clouds
    for cx, cy, r in [(200, 380, 150), (380, 330, 180), (600, 390, 160), (820, 340, 170), (980, 400, 140)]:
        d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=(150, 156, 168))
    d.rectangle((0, 1600, WW, HH), fill=(200, 204, 212)); d.rectangle((0, 1600, WW, 1625), fill=(180, 184, 194))
    d.ellipse((620, 1760, 980, 1840), fill=(186, 194, 206))
    # lamp post
    d.rectangle((140, 900, 162, 1600), fill=(120, 126, 136)); d.rectangle((110, 880, 200, 910), fill=(120, 126, 136))
    return im

def bg_room(night=False):
    base = (232, 236, 250) if night else (248, 246, 242)
    im = Image.new('RGBA', (WW, HH), base + (255,)); d = ImageDraw.Draw(im)
    # window
    wc = (196, 206, 236) if night else (226, 238, 248)
    rr(d, (90, 540, 470, 1000), 12, fill=wc, outline=(210, 205, 196) if not night else (190, 196, 220), width=14)
    d.line((280, 540, 280, 1000), fill=(210, 205, 196) if not night else (190, 196, 220), width=10)
    d.line((90, 770, 470, 770), fill=(210, 205, 196) if not night else (190, 196, 220), width=10)
    if night:
        d.ellipse((350, 590, 430, 670), fill=(255, 250, 225)); d.ellipse((330, 580, 405, 655), fill=wc)
        for sx, sy in [(140, 600), (210, 680), (160, 860), (380, 880), (320, 720)]: d.ellipse((sx, sy, sx + 8, sy + 8), fill=WHITE)
    else:
        d.ellipse((140, 600, 230, 690), fill=(255, 236, 170))
    # calendar
    rr(d, (640, 560, 960, 900), 14, fill=WHITE, outline=(222, 220, 216), width=4)
    d.rectangle((644, 564, 956, 640), fill=RED); text_c(d, (800, 602), 'SEMANAS', F(36), WHITE)
    floor(d, 1640, (230, 226, 220) if not night else (214, 218, 234), (214, 210, 204) if not night else (200, 204, 222))
    # bed
    rr(d, (720, 1380, 1100, 1640), 20, fill=(220, 222, 232) if not night else (200, 206, 226)); rr(d, (720, 1340, 1100, 1420), 20, fill=(240, 240, 246) if not night else (220, 224, 240))
    # table with papers
    rr(d, (40, 1380, 400, 1410), 8, fill=(200, 180, 156)); d.rectangle((70, 1410, 90, 1640), fill=(186, 166, 140)); d.rectangle((350, 1410, 370, 1640), fill=(186, 166, 140))
    for k in range(5): rr(d, (90 + k * 6, 1340 - k * 9, 300 + k * 6, 1384 - k * 9), 4, fill=WHITE, outline=(220, 220, 224), width=2)
    return im

def bg_rays(t):
    im = Image.new('RGBA', (WW, HH), (255, 255, 255, 255)); d = ImageDraw.Draw(im)
    cx, cy = 540, 760; a0 = t * 12
    for k in range(18):
        a = math.radians(a0 + k * 20); b = math.radians(a0 + k * 20 + 9)
        d.polygon([(cx, cy), (cx + 2000 * math.cos(a), cy + 2000 * math.sin(a)), (cx + 2000 * math.cos(b), cy + 2000 * math.sin(b))], fill=(255, 246, 214))
    g = Image.new('RGBA', (WW, HH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse((cx - 420, cy - 420, cx + 420, cy + 420), fill=(255, 255, 255, 200)); g = g.filter(ImageFilter.GaussianBlur(90))
    im.alpha_composite(g); d = ImageDraw.Draw(im); floor(d, 1700, (246, 246, 248), (232, 232, 236))
    return im

def bg_door():
    im = Image.new('RGBA', (WW, HH), (249, 247, 244, 255)); d = ImageDraw.Draw(im)
    rr(d, (650, 760, 1000, 1640), 10, fill=(214, 176, 132)); rr(d, (690, 800, 960, 1180), 8, fill=(200, 160, 116)); rr(d, (690, 1220, 960, 1600), 8, fill=(200, 160, 116))
    d.ellipse((900, 1200, 930, 1230), fill=(240, 200, 90))
    rr(d, (690, 640, 960, 720), 12, fill=WHITE, outline=(226, 222, 216), width=4); text_c(d, (825, 680), 'CASA', F(36), GREY)
    floor(d, 1640, (236, 232, 226), (222, 218, 212)); rr(d, (640, 1640, 1010, 1680), 10, fill=(200, 80, 80))
    d.polygon([(120, 1640), (240, 1640), (225, 1500), (135, 1500)], fill=(215, 210, 205))
    for a in (-40, -15, 10, 35): d.ellipse((150 + a * 2, 1360 + abs(a), 210 + a * 2, 1500), fill=(150, 196, 150))
    return im

def bg_park():
    im = Image.new('RGBA', (WW, HH), (240, 248, 255, 255)); d = ImageDraw.Draw(im)
    d.ellipse((760, 330, 960, 530), fill=(255, 222, 100))
    for cx, cy, r in [(220, 520, 110), (330, 480, 130), (450, 530, 100)]: d.ellipse((cx - r, cy - r * 0.6, cx + r, cy + r * 0.6), fill=WHITE)
    d.ellipse((-400, 1250, 700, 1900), fill=(200, 232, 196)); d.ellipse((300, 1300, 1500, 1950), fill=(186, 224, 182))
    d.rectangle((0, 1600, WW, HH), fill=(176, 216, 172))
    for tx in (120, 900):
        d.rectangle((tx - 18, 1180, tx + 18, 1560), fill=(170, 130, 96)); d.ellipse((tx - 130, 900, tx + 130, 1260), fill=(140, 196, 136))
    return im

BG = {}
def get_bg(i, t):
    if i == 4: return bg_rays(t)
    if i not in BG:
        BG[i] = {0: bg_office, 1: bg_street, 2: bg_room, 3: lambda: bg_room(True), 5: grid_bg, 6: bg_door,
                 7: grid_bg, 8: grid_bg, 9: bg_park, 10: lambda: grid_bg((255, 255, 255))}[i]()
    return BG[i].copy()

# ---------------------------------------------------------------- shots
# per scene: char world pos (x, feet_y), scale ; shots list (time, 'w'|'c')
CH = {0: (400, 1890, .78), 1: (560, 1880, .78), 2: (540, 1890, .78), 3: (540, 1890, .78), 4: (540, 1900, .74),
      5: (540, 1900, .62), 6: (420, 1890, .74), 7: (540, 1900, .6), 8: (540, 1900, .66), 9: (540, 1890, .78), 10: (540, 1800, .6)}
SHOTS = {
    0: [(0, 'c'), (W(0, 'ese') - 0.1, 'w'), (W(0, 'despedido') - 0.05, 'c')],
    1: [(0, 'c'), (W(1, 'cuentas'), 'w')],
    2: [(0, 'w'), (W(2, 'nadie') - 0.1, 'c')],
    3: [(0, 'c'), (W(3, 'vi') - 0.1, 'w')],
    4: [(0, 'c'), (W(4, 'pensé') - 0.1, 'w')],
    5: [(0, 'w')],
    6: [(0, 'w'), (W(6, 'paquete') - 0.3, 'c'), (W(6, 'publiqué') - 0.1, 'w')],
    7: [(0, 'w')],
    8: [(0, 'w'), (W(8, 'vendí') - 0.1, 'c')],
    9: [(0, 'w'), (W(9, 'tengo') - 0.2, 'c')],
    10: [(0, 'w')],
}
MOOD = {0: 'sad', 1: 'sad', 2: 'sad', 3: 'sad', 4: 'happy', 5: 'happy', 6: 'happy', 7: 'happy', 8: 'happy', 9: 'happy', 10: 'happy'}
ANCH = ((BOX[0] + BOX[2]) / 2, 1312)  # feet anchor in source
FACE = (600, 300)

def shot_at(i, t):
    lst = SHOTS[i]; cur = lst[0][1]; prev = cur; ts = -9
    for tt, s in lst:
        if t >= (tt if tt > 0 else SC[i]):
            if s != cur: prev = cur; cur = s; ts = tt
    return prev, cur, ts

def camera(i, t):
    x, fy, s = CH[i]
    face = (x + (FACE[0] - ANCH[0]) * s, fy + (FACE[1] - ANCH[1]) * s)
    def cam(kind):
        if kind == 'w': return (1.0, 540.0, 960.0, 540.0, 960.0)
        return (2.0, face[0], face[1] + 60, 540.0, 900.0)
    prev, cur, ts = shot_at(i, t)
    a = cam(cur)
    if ts > 0 and t - ts < 0.3:
        b = cam(prev); k = ease((t - ts) / 0.3)
        a = tuple(lerp(bb, aa, k) for aa, bb in zip(a, b))
    # scene-entry punch
    e = t - SC[i]
    if e < 0.35 and i > 0:
        z = a[0] * (1 + 0.08 * (1 - ease(e / 0.35))); a = (z,) + a[1:]
    # subtle drift
    z = a[0] * (1 + 0.012 * math.sin(t * 0.8))
    return (z,) + a[1:]

def cam_xf(img, cam):
    z, fx, fy, cx, cy = cam
    return img.transform((WW, HH), Image.AFFINE, (1 / z, 0, fx - cx / z, 0, 1 / z, fy - cy / z), Image.BILINEAR)

def tears_on(src, t):
    d = ImageDraw.Draw(src)
    for k, (ex, ph) in enumerate([(530, 0.0), (676, 0.55)]):
        p = ((t + ph) % 1.3) / 1.3
        y = 322 + p * 110; a = int(255 * (1 - max(0, p - 0.7) / 0.3))
        d.ellipse((ex - 9, y - 6, ex + 9, y + 18), fill=(120, 190, 255, a))
        d.polygon([(ex - 7, y + 2), (ex + 7, y + 2), (ex, y - 16)], fill=(120, 190, 255, a))

def char_layer(i, t, fr, cam):
    x, fy, s = CH[i]
    mood = MOOD[i]
    if i == 3 and t >= W(3, 'celular'): mood = 'happy'
    mo = MOUTH[fr] if fr < len(MOUTH) else 0
    blink = (fr % 97) < 4
    src = V[(mood, mo) + (('b',) if blink and not mo else ())]
    # pose overrides
    if i == 10 and t > L[10]['start'] + L[10]['dur'] + 0.15: src = PULGAR
    if i == 8 and W(8, 'vendí') + 0.5 < t < SE[8] - 0.1 and not mo: src = PULGAR
    need_tears = i in (1, 2) and src is not PULGAR
    if need_tears:
        src = src.copy(); tears_on(src, t)
    # motion
    e = t - SC[i]
    if mood == 'sad':
        bob = 4 * math.sin(t * 2.2); sy = 1 + 0.008 * math.sin(t * 2.2); dx = 0
    else:
        bob = -abs(12 * math.sin(t * 5.2)) if i in (4, 8, 9) else 6 * math.sin(t * 3.4)
        sy = 1 + 0.015 * math.sin(t * 5.2 if i in (4, 8, 9) else t * 3.4); dx = 0
    if i == 8 and t > W(8, 'vendí'):
        j = t - W(8, 'vendí'); bob -= 120 * max(0, math.sin(min(j, 0.6) / 0.6 * math.pi))
    if e < 0.4:  # entry squash
        sy *= 1 - 0.06 * math.sin(e / 0.4 * math.pi)
    sx = 2 - sy
    z, fx, fyc, cx, cy = cam
    # screen = ((pos + (src-anchor)*s*S) - f)*z + c ; invert
    px, py = x + dx, fy + bob
    ax, ay = ANCH
    a_ = 1 / (z * s * sx); e_ = 1 / (z * s * sy)
    c_ = ax - (cx / z + fx - px) / (s * sx) * 1  # src_x = (scr_x - cx)/(z*s*sx) + (fx - px)/(s*sx) + ax
    c_ = -cx * a_ + (fx - px) / (s * sx) + ax
    f_ = -cy * e_ + (fyc - py) / (s * sy) + ay
    lay = src.transform((WW, HH), Image.AFFINE, (a_, 0, c_, 0, e_, f_), Image.BICUBIC)
    # shadow
    sh = Image.new('RGBA', (WW, HH), (0, 0, 0, 0)); sd = ImageDraw.Draw(sh)
    shx = (px - fx) * z + cx; shy = (fy - fyc) * z + cy; rw = 300 * s * z
    sd.ellipse((shx - rw, shy - rw * 0.12, shx + rw, shy + rw * 0.12), fill=(0, 0, 0, 40))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    return sh, lay

# ---------------------------------------------------------------- overlays (screen space)
TITLES = {0: ('EL DÍA QUE LO', 'PERDÍ TODO'), 1: ('SIN TRABAJO', 'Y SIN AHORROS'), 2: ('SEMANAS', 'SIN RESPUESTA'),
          3: ('HASTA QUE', 'UNA NOCHE...'), 4: ('¡LA IDEA QUE', 'LO CAMBIÓ TODO!'), 5: ('COMPRÉ EN CHINA', 'CON POCO DINERO'),
          6: ('¡LLEGÓ MI', 'PAQUETE!'), 7: ('MI PROPIA', 'TIENDA'), 8: ('¡MIS PRIMERAS', 'VENTAS!'), 9: ('MI PROPIO', 'NEGOCIO')}

def draw_title(img, i, t):
    if i not in TITLES: return
    e = t - SC[i]; k = outback(e / 0.45); a = ease(e / 0.25)
    l1, l2 = TITLES[i]
    lay = Image.new('RGBA', (WW, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    f1, f2 = F(60), F(84)
    w = max(d.textlength(l1, font=f1), d.textlength(l2, font=f2)) + 90
    shadow_card(lay, (540 - w / 2, 70, 540 + w / 2, 330), 34, WHITE, 16, 8, 50)
    d = ImageDraw.Draw(lay)
    text_c(d, (540, 140), l1, f1, DARK)
    text_c(d, (540, 240), l2, f2, RED)
    paste_scaled(img, lay, 540, 210 + 40 * (1 - k), 0.6 + 0.4 * k, a)

def draw_subs(img, t):
    for ln in L:
        ws = ln['words']
        if not (ws[0][1] - 0.15 <= t <= ws[-1][2] + 0.35): continue
        # chunks of max 4 words / 22 chars
        chunks = []; cur = []
        for w in ws:
            cur.append(w)
            if len(cur) >= 4 or len(' '.join(x[0] for x in cur)) > 20 or w[0][-1] in '.,:!?': chunks.append(cur); cur = []
        if cur: chunks.append(cur)
        ch = chunks[0]
        for c in chunks:
            if t >= c[0][1] - 0.1: ch = c
        f = F(64)
        d0 = ImageDraw.Draw(img)
        widths = [d0.textlength(w[0], font=f) for w in ch]; sp = 18
        tw = sum(widths) + sp * (len(ch) - 1)
        y = 1700; x = 540 - tw / 2
        e = t - (ch[0][1] - 0.1); k = outback(e / 0.2)
        lay = Image.new('RGBA', (WW, 260), (0, 0, 0, 0))
        shadow_card(lay, (x - 36, 60, x + tw + 36, 190), 30, WHITE, 14, 6, 60)
        d = ImageDraw.Draw(lay)
        for (w, a, b), ww in zip(ch, widths):
            on = a - 0.05 <= t
            col = RED if (a - 0.05 <= t < b + 0.05) else (DARK if on else (150, 152, 160))
            d.text((x, 125), w, font=f, fill=col, anchor='lm'); x += ww + sp
        paste_scaled(img, lay, 540, y, 0.85 + 0.15 * k)
        return

def phone_card(w=520, h=760):
    lay = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0))
    shadow_card(lay, (40, 40, 40 + w, 40 + h), 56, (30, 30, 34), 20, 12, 70)
    d = ImageDraw.Draw(lay); rr(d, (54, 54, 26 + w, 26 + h), 46, fill=WHITE)
    rr(d, (40 + w / 2 - 60, 66, 40 + w / 2 + 60, 88), 11, fill=(30, 30, 34))
    return lay, d

def ui_scene0(img, t):
    td = W(0, 'despedido')
    if t < td - 0.05: return
    e = t - td + 0.05
    lay = Image.new('RGBA', (560, 420), (0, 0, 0, 0))
    shadow_card(lay, (40, 40, 520, 380), 18, WHITE, 14, 8, 60); d = ImageDraw.Draw(lay)
    text_c(d, (280, 95), 'CARTA DE DESPIDO', F(36), DARK)
    for k in range(4): rr(d, (80, 140 + k * 36, 480 - (k % 2) * 80, 156 + k * 36), 8, fill=LG)
    st = Image.new('RGBA', (420, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
    rr(sd, (10, 10, 410, 130), 16, outline=RED, width=10); text_c(sd, (210, 72), 'DESPEDIDO', F(64), RED)
    st = st.rotate(-10, expand=True, resample=Image.BICUBIC)
    sk = max(1, 2.2 - 1.2 * ease(e / 0.18))
    k = outback(e / 0.3)
    rot = lay.rotate(4, expand=True, resample=Image.BICUBIC)
    paste_scaled(img, rot, 800, 1230 + 60 * (1 - k), 0.8 * k)
    if e > 0.12: paste_scaled(img, st, 810, 1290, sk * 0.6, min(1, (e - 0.12) / 0.06))

def ui_scene1(img, t):
    # rain + thunder flash (screen)
    d = ImageDraw.Draw(img)
    rnd = random.Random(3)
    for k in range(110):
        x0 = rnd.random() * 1200 - 60; sp = 1400 + rnd.random() * 600; ph = rnd.random()
        y = ((t * sp / 1920 + ph) % 1) * 2100 - 100; x = x0 - (y * 0.12)
        d.line((x, y, x - 10, y + 70), fill=(150, 170, 200, 200), width=4)
    e = t - (SC[1] + 0.35)
    if 0 < e < 0.5:
        a = (1 - e / 0.5) * (0.85 if e < 0.08 or 0.16 < e else 0.3)
        img.alpha_composite(Image.new('RGBA', (WW, HH), (255, 255, 255, int(255 * a))))
    tc = W(1, 'cuentas')
    if t > tc:
        e = t - tc; k = outback(e / 0.35)
        lay = Image.new('RGBA', (460, 300), (0, 0, 0, 0)); shadow_card(lay, (30, 30, 430, 270), 24, WHITE, 12, 6, 60)
        dd = ImageDraw.Draw(lay)
        text_c(dd, (230, 80), 'CUENTAS POR PAGAR', F(30), GREY)
        for j, (n, v) in enumerate([('Arriendo', '$ ---'), ('Servicios', '$ ---'), ('Comida', '$ ---')]):
            dd.text((70, 130 + j * 44), n, font=F(30, 'Medium'), fill=DARK, anchor='lm'); dd.text((390, 130 + j * 44), v, font=F(30), fill=RED, anchor='rm')
        paste_scaled(img, lay.rotate(-5, expand=True, resample=Image.BICUBIC), 760, 720, k)

def ui_scene2(img, t):
    # calendar Xs added on world? draw screen-space counter of days + phone 0 llamadas
    e = t - SC[2]
    d = ImageDraw.Draw(img)
    tn = W(2, 'nadie') - 0.1
    if t > tn:
        e2 = t - tn; k = outback(e2 / 0.35)
        lay, dd = phone_card(400, 520)
        text_c(dd, (240, 150), 'Llamadas', F(36), DARK)
        dd.ellipse((175, 210, 305, 340), fill=(250, 232, 234)); text_c(dd, (240, 275), '0', F(80), RED)
        text_c(dd, (240, 390), 'Sin llamadas', F(32, 'Medium'), GREY)
        text_c(dd, (240, 432), 'nuevas', F(32, 'Medium'), GREY)
        paste_scaled(img, lay, 790, 640, 0.95 * k)
    # CV papers flying out
    tm = W(2, 'mandé')
    if t > tm:
        for j in range(4):
            p = (t - tm - j * 0.25)
            if p <= 0 or p > 1.4: continue
            q = p / 1.4
            x = 300 + q * 700 + j * 30; y = 900 - math.sin(q * math.pi) * 260 - j * 40
            lay = Image.new('RGBA', (220, 150), (0, 0, 0, 0)); shadow_card(lay, (20, 20, 200, 130), 10, WHITE, 6, 4, 50)
            dd = ImageDraw.Draw(lay); text_c(dd, (110, 50), 'HOJA DE VIDA', F(20), DARK)
            for r in range(3): rr(dd, (40, 75 + r * 15, 180 - r * 20, 83 + r * 15), 4, fill=LG)
            paste_scaled(img, lay.rotate(q * 70 - 20, expand=True, resample=Image.BICUBIC), x, y, 1, 1 - max(0, q - 0.8) / 0.2)

def ui_scene3(img, t):
    tv = W(3, 'vi') - 0.1
    if t < tv: return
    e = t - tv; k = outback(e / 0.4)
    lay, dd = phone_card(460, 640)
    # glow
    g = Image.new('RGBA', (WW, HH), (0, 0, 0, 0)); gd = ImageDraw.Draw(g); gd.ellipse((560, 330, 1020, 1000), fill=(255, 240, 180, int(120 * k))); img.alpha_composite(g.filter(ImageFilter.GaussianBlur(60)))
    text_c(dd, (270, 140), '23:47', F(54), DARK)
    tc = W(3, 'celular') - 0.1
    if t > tc:
        e2 = t - tc; kk = outback(e2 / 0.3)
        nb = Image.new('RGBA', (440, 230), (0, 0, 0, 0)); shadow_card(nb, (10, 10, 430, 220), 24, (250, 250, 252), 8, 4, 50)
        nd = ImageDraw.Draw(nb); nd.ellipse((30, 30, 90, 90), fill=RED); text_c(nd, (60, 60), '!', F(40), WHITE)
        nd.text((110, 60), 'Oferta mayorista', font=F(28), fill=DARK, anchor='lm')
        nd.text((32, 120), 'Productos de China', font=F(30, 'Medium'), fill=DARK, anchor='lm')
        nd.text((32, 168), 'desde $1 por unidad', font=F(30), fill=RED, anchor='lm')
        lay.alpha_composite(layer_alpha(nb, min(1, kk)), (50, int(230 - 40 * (1 - kk))))
    paste_scaled(img, lay, 790, 670, 0.95 * k)

def product_card(key, name, price, w=300):
    lay = Image.new('RGBA', (w + 40, 400), (0, 0, 0, 0)); shadow_card(lay, (20, 20, 20 + w, 380), 26, WHITE, 12, 6, 55)
    d = ImageDraw.Draw(lay); rr(d, (40, 40, w, 230), 20, fill=(246, 246, 248))
    ic = icon(key, 170); lay.alpha_composite(ic, (int(20 + w / 2 - 85), 50))
    text_c(d, (20 + w / 2, 275), name, F(32), DARK); text_c(d, (20 + w / 2, 330), price, F(44), RED)
    return lay

def ui_scene4(img, t):
    # flash + bulb
    e = t - SC[4]
    if e < 0.4: img.alpha_composite(Image.new('RGBA', (WW, HH), (255, 255, 255, int(255 * (1 - e / 0.4)))))
    items = [('aud', 'Audífonos', '$3.50', 'productos', 210, 560), ('rel', 'Reloj', '$4.20', 'china', 540, 470), ('lam', 'Lámpara', '$2.80', 'precios', 870, 560)]
    pv = W(4, 'pensé') - 0.1
    for key, nm, pr, wd, x, y in items:
        ts = W(4, wd) - 0.05
        if t < ts: continue
        k = outback((t - ts) / 0.35); fl = 8 * math.sin(t * 3 + x)
        cpos = {210: (165, 1060), 540: (540, 1330), 870: (915, 1060)}[x]
        q = ease((t - pv) / 0.35) if t > pv else 0
        sc = lerp(0.62, 0.5, q); xx = lerp(cpos[0], x, q); yy = lerp(cpos[1], y, q) + fl
        x = xx
        paste_scaled(img, product_card(key, nm, pr), xx, yy, sc * k)
    if t < pv:
        # bulb above head in close shot: head top at ~ y 300 screen
        k = outback(e / 0.4)
        b = Image.new('RGBA', (260, 300), (0, 0, 0, 0)); bd = ImageDraw.Draw(b)
        g = Image.new('RGBA', (260, 300), (0, 0, 0, 0)); gd = ImageDraw.Draw(g); gd.ellipse((10, 0, 250, 240), fill=(255, 220, 80, 160)); b.alpha_composite(g.filter(ImageFilter.GaussianBlur(25)))
        bd.ellipse((60, 40, 200, 180), fill=(255, 214, 60)); bd.rectangle((100, 170, 160, 230), fill=(190, 190, 196)); bd.line((100, 195, 160, 195), fill=(150, 150, 156), width=6)
        for a in range(0, 360, 45):
            r = math.radians(a + t * 60)
        if t < W(4, 'productos') - 0.05:
            paste_scaled(img, b, 540, 330, k)
    tv = W(4, 'vendo') - 0.05
    if t > tv:
        k = outback((t - tv) / 0.3)
        lay = Image.new('RGBA', (760, 170), (0, 0, 0, 0)); shadow_card(lay, (20, 20, 740, 150), 65, RED, 12, 6, 70)
        d = ImageDraw.Draw(lay); text_c(d, (380, 85), 'COMPRAR Y VENDER', F(54), WHITE)
        paste_scaled(img, lay, 540, 840, k)

def ui_scene5(img, t):
    # laptop browser
    lay = Image.new('RGBA', (960, 760), (0, 0, 0, 0))
    shadow_card(lay, (30, 30, 930, 650), 24, (40, 42, 48), 16, 10, 70)
    d = ImageDraw.Draw(lay); rr(d, (46, 46, 914, 634), 14, fill=WHITE)
    d.polygon([(0, 650), (960, 650), (930, 700), (30, 700)], fill=(196, 198, 206))
    d.rectangle((46, 46, 914, 110), fill=(242, 242, 245)); [d.ellipse((70 + j * 34, 66, 92 + j * 34, 88), fill=c) for j, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)])]
    rr(d, (200, 62, 760, 94), 16, fill=WHITE); d.text((222, 78), 'Tienda mayorista · envío desde China', font=F(22, 'Medium'), fill=GREY, anchor='lm')
    cnt = 0
    for j, (key, nm, pr, wd) in enumerate([('aud', 'Audífonos', '$3.50', 'audífonos'), ('lam', 'Lámpara', '$2.80', 'lámparas'), ('rel', 'Reloj', '$4.20', 'relojes')]):
        x0 = 80 + j * 280; ts = W(5, wd) - 0.05; on = t >= ts
        if on: cnt += 1
        rr(d, (x0, 140, x0 + 250, 520), 18, fill=(248, 248, 250), outline=RED if on else (232, 232, 236), width=5 if on else 3)
        lay.alpha_composite(icon(key, 150), (x0 + 50, 160))
        text_c(d, (x0 + 125, 345), nm, F(30), DARK); text_c(d, (x0 + 125, 395), pr, F(38), RED)
        rr(d, (x0 + 30, 440, x0 + 220, 496), 28, fill=RED if not on else (34, 160, 90))
        text_c(d, (x0 + 125, 468), 'Agregar' if not on else 'Agregado ✓' if False else 'Agregado', F(26), WHITE)
    rr(d, (80, 545, 880, 615), 16, fill=(246, 246, 248))
    d.text((110, 580), f'Carrito: {cnt} productos', font=F(30), fill=DARK, anchor='lm')
    ti = W(5, 'inversión') - 0.05
    k = ease((t - SC[5]) / 0.35)
    paste_scaled(img, lay, 540, 700 + 80 * (1 - k), 0.98, k)
    if t > ti:
        kk = outback((t - ti) / 0.35)
        b = Image.new('RGBA', (640, 170), (0, 0, 0, 0)); shadow_card(b, (20, 20, 620, 150), 65, RED, 12, 6, 70)
        bd = ImageDraw.Draw(b); text_c(bd, (320, 85), 'INVERSIÓN MÍNIMA', F(54), WHITE)
        paste_scaled(img, b.rotate(3, expand=True, resample=Image.BICUBIC), 700, 1005, 0.75 * kk)

def world_scene6(wimg, t):
    # box drop in world space near door
    td = SC[6] + 0.45
    if t < td: return
    e = t - td
    y = 1640 - 150
    if e < 0.35: y = lerp(500, 1640 - 150, (e / 0.35) ** 2)
    else:
        b = e - 0.35; y = 1640 - 150 - 60 * abs(math.sin(b * 9)) * math.exp(-b * 5)
    paste_scaled(wimg, icon('box', 300), 820, y, 1)
    # label
    if e > 0.5:
        d = ImageDraw.Draw(wimg); rr(d, (720, 1520, 900, 1560), 8, fill=WHITE); text_c(d, (810, 1540), 'DESDE CHINA', F(22), RED)

def market_phone(t, t0, store=False):
    lay, d = phone_card(500, 820)
    lay.alpha_composite(LOGO.resize((210, 70), Image.LANCZOS), (80, 110))
    rr(d, (330, 122, 510, 168), 23, fill=RED); text_c(d, (420, 145), 'Marketplace', F(22), WHITE)
    if not store:
        rr(d, (80, 210, 500, 520), 22, fill=(246, 246, 248)); lay.alpha_composite(icon('aud', 260), (160, 230))
        d.text((84, 560), 'Audífonos inalámbricos', font=F(30), fill=DARK, anchor='lm')
        d.text((84, 610), '$12', font=F(48), fill=RED, anchor='lm')
        d.text((84, 660), 'Bogotá · Nuevo', font=F(24, 'Medium'), fill=GREY, anchor='lm')
        k = outback((t - t0 - 0.3) / 0.3) if t > t0 + 0.3 else 0
        if k > 0:
            b = Image.new('RGBA', (380, 90), (0, 0, 0, 0)); bd = ImageDraw.Draw(b); rr(bd, (0, 0, 380, 90), 45, fill=(34, 160, 90)); text_c(bd, (190, 45), 'PUBLICADO', F(36), WHITE)
            paste_scaled(lay, b, 290, 760, k)
    else:
        rr(d, (80, 200, 500, 300), 20, fill=(250, 236, 238)); d.ellipse((96, 214, 168, 286), fill=RED); text_c(d, (132, 250), 'MT', F(28), WHITE)
        d.text((186, 232), 'Mi Tienda', font=F(32), fill=DARK, anchor='lm'); d.text((186, 272), 'sumiago.com/tiendas/mi-tienda', font=F(17, 'Medium'), fill=GREY, anchor='lm')
        for j, (k_, p) in enumerate([('aud', '$12'), ('lam', '$9'), ('rel', '$14'), ('box', 'Pronto')]):
            x0 = 80 + (j % 2) * 215; y0 = 320 + (j // 2) * 250
            rr(d, (x0, y0, x0 + 205, y0 + 235), 18, fill=(246, 246, 248)); lay.alpha_composite(icon(k_, 140), (x0 + 32, y0 + 14))
            text_c(d, (x0 + 102, y0 + 195), p, F(32), RED)
        rr(d, (80, 830 - 0, 500, 0 + 830), 0)
    return lay

def ui_scene6(img, t):
    tp = W(6, 'publiqué') - 0.1
    if t < tp: return
    k = outback((t - tp) / 0.4)
    paste_scaled(img, market_phone(t, tp), 760, 760, 0.82 * k)

def ui_scene7(img, t):
    k = outback((t - SC[7]) / 0.4)
    paste_scaled(img, market_phone(t, SC[7], True), 540, 690, 0.8 * k)
    tw = W(7, 'whatsapp') - 0.1
    if t > tw:
        kk = outback((t - tw) / 0.35)
        lay = Image.new('RGBA', (640, 330), (0, 0, 0, 0)); shadow_card(lay, (20, 20, 620, 310), 26, (226, 248, 214), 12, 6, 60)
        d = ImageDraw.Draw(lay); rr(d, (44, 44, 596, 220), 18, fill=WHITE)
        lay.alpha_composite(LOGO.resize((150, 50), Image.LANCZOS), (64, 64))
        d.text((64, 150), 'Mi Tienda · Sumiago', font=F(28), fill=DARK, anchor='lm'); d.text((64, 190), 'sumiago.com/tiendas/mi-tienda', font=F(22, 'Medium'), fill=GREY, anchor='lm')
        d.text((50, 265), '¡Mira mis productos! 👇'.replace(' 👇', ''), font=F(28, 'Medium'), fill=DARK, anchor='lm')
        d.text((590, 275), '9:41 ✓✓'.replace(' ✓✓', ''), font=F(20, 'Medium'), fill=GREY, anchor='rm')
        paste_scaled(img, lay, 600, 930, 0.9 * kk)

def ui_scene8(img, t):
    msgs = [('un', '¿Todavía está disponible?', 470), ('otro', '¡Lo quiero! ¿Envías hoy?', 650)]
    for wd, m, y in msgs:
        ts = W(8, wd) - 0.05
        if t < ts: continue
        k = outback((t - ts) / 0.35)
        lay = Image.new('RGBA', (900, 170), (0, 0, 0, 0)); shadow_card(lay, (20, 20, 880, 150), 30, WHITE, 12, 6, 60)
        d = ImageDraw.Draw(lay); d.ellipse((46, 46, 124, 124), fill=RED); text_c(d, (85, 85), '✉'.replace('✉', '@'), F(40), WHITE)
        d.text((150, 62), 'Nuevo mensaje', font=F(26), fill=GREY, anchor='lm'); d.text((150, 108), m, font=F(36), fill=DARK, anchor='lm')
        tv0 = W(8, 'vendí') - 0.1
        fade = 1 - ease((t - tv0) / 0.25) if t > tv0 else 1
        paste_scaled(img, lay, 540 + 300 * (1 - k), y, 0.95, min(1, k) * fade)
    tv = W(8, 'vendí') - 0.05
    if t > tv:
        e = t - tv
        st = Image.new('RGBA', (560, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        rr(sd, (10, 10, 550, 190), 24, fill=(255, 255, 255, 230), outline=RED, width=14); text_c(sd, (280, 100), '¡VENDIDO!', F(86), RED)
        st = st.rotate(8, expand=True, resample=Image.BICUBIC)
        sk = max(1, 2.0 - ease(e / 0.18))
        paste_scaled(img, st, 560, 1230, sk * 0.85, min(1, e / 0.08))
        # coins
        rnd = random.Random(5)
        for j in range(16):
            p = e - j * 0.05
            if p <= 0: continue
            vx = rnd.uniform(-700, 700); vy = rnd.uniform(-1500, -900)
            x = 540 + vx * p; y = 1200 + vy * p + 1800 * p * p
            if y > 2000: continue
            d = ImageDraw.Draw(img); r = 30
            d.ellipse((x - r, y - r, x + r, y + r), fill=(255, 196, 40), outline=(220, 150, 20), width=6); d.text((x, y), '$', font=F(34), fill=(200, 130, 10), anchor='mm')

def confetti(img, t0, t, n=90, seed=1):
    if t < t0: return
    e = t - t0; rnd = random.Random(seed); d = ImageDraw.Draw(img)
    cols = [RED, (255, 196, 40), (60, 170, 240), (40, 190, 110), (30, 30, 34)]
    for j in range(n):
        vx = rnd.uniform(-900, 900); vy = rnd.uniform(-1900, -800); x = 540 + vx * e; y = 1300 + vy * e + 1600 * e * e
        if y > 2000: continue
        a = e * rnd.uniform(4, 10); s = rnd.uniform(14, 24)
        pts = [(x + s * math.cos(a + q), y + s * 0.5 * math.sin(a + q)) for q in (0, 1.6, 3.14, 4.7)]
        d.polygon(pts, fill=rnd.choice(cols))

def ui_scene9(img, t):
    confetti(img, W(9, 'negocio') - 0.05, t)

def ui_scene10(img, t):
    e = t - SC[10]; k = outback(e / 0.4)
    paste_scaled(img, LOGO, 540, 210, 0.95 * k)
    lay = Image.new('RGBA', (1000, 300), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    text_c(d, (500, 90), 'Compra barato,', F(72), DARK); text_c(d, (500, 190), 'vende en Sumiago', F(78), RED)
    paste_scaled(img, lay, 540, 470, k)
    tg = W(10, 'crea') - 0.1
    if t > tg:
        kk = outback((t - tg) / 0.35); pul = 1 + 0.04 * math.sin(t * 7)
        b = Image.new('RGBA', (1000, 190), (0, 0, 0, 0)); shadow_card(b, (20, 20, 980, 160), 70, RED, 14, 8, 80)
        bd = ImageDraw.Draw(b); text_c(bd, (500, 90), 'CREA TU TIENDA AL SUSCRIBIRTE', F(46), WHITE)
        paste_scaled(img, b, 540, 690, kk * pul)
        u = Image.new('RGBA', (560, 130), (0, 0, 0, 0)); shadow_card(u, (20, 20, 540, 110), 45, WHITE, 10, 5, 50)
        ud = ImageDraw.Draw(u); rr(ud, (20, 20, 540, 110), 45, outline=RED, width=5); text_c(ud, (280, 65), 'sumiago.com', F(48), DARK)
        paste_scaled(img, u, 540, 850, kk)
    ds = Image.new('RGBA', (1000, 60), (0, 0, 0, 0)); dd = ImageDraw.Draw(ds)
    text_c(dd, (500, 30), 'Historia ilustrativa. Los resultados dependen de tu esfuerzo.', F(24, 'Medium'), (140, 142, 150))
    img.alpha_composite(layer_alpha(ds, k), (40, 1850))
    confetti(img, L[10]['start'] + L[10]['dur'] + 0.1, t, 70, 9)

UI = {0: ui_scene0, 1: ui_scene1, 2: ui_scene2, 3: ui_scene3, 4: ui_scene4, 5: ui_scene5, 6: ui_scene6, 7: ui_scene7, 8: ui_scene8, 9: ui_scene9, 10: ui_scene10}
WORLD = {6: world_scene6}

def scene_at(t):
    for i in range(10, -1, -1):
        if t >= SC[i]: return i
    return 0

def frame(fr):
    t = fr / FPS; i = scene_at(t)
    cam = camera(i, t)
    w = get_bg(i, t)
    if i in WORLD: WORLD[i](w, t)
    sh, ch = char_layer(i, t, fr, cam)
    w.alpha_composite(Image.new('RGBA', (WW, HH)))
    img = cam_xf(w, cam).convert('RGBA')
    if cam[0] > 1.3: img = img.filter(ImageFilter.GaussianBlur(min(6, (cam[0] - 1.3) * 8)))
    img.alpha_composite(sh); img.alpha_composite(ch)
    UI[i](img, t)
    if cam[0] < 1.3 or i in (4,): draw_title(img, i, t)
    else: draw_title(img, i, t)
    draw_subs(img, t)
    # scene entry white flash (happy part) / soft fade (sad)
    e = t - SC[i]
    if i > 0 and e < 0.25:
        img.alpha_composite(Image.new('RGBA', (WW, HH), (255, 255, 255, int(200 * (1 - e / 0.25)))))
    if t < 0.3: img.alpha_composite(Image.new('RGBA', (WW, HH), (255, 255, 255, int(255 * (1 - t / 0.3)))))
    return img.convert('RGB')

if __name__ == '__main__':
    import subprocess
    mode = sys.argv[1]
    if mode == 'still':
        for ts in sys.argv[2:]:
            frame(int(float(ts) * FPS)).resize((540, 960)).save(f'st/{ts}.jpg', quality=85)
    else:
        part, nparts = int(sys.argv[2]), int(sys.argv[3])
        nf = int(TOTAL * FPS); a = nf * part // nparts; b = nf * (part + 1) // nparts
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WW}x{HH}', '-r', str(FPS), '-i', '-',
                              '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', f'out/p{part:02d}.mp4'], stdin=subprocess.PIPE)
        for fr in range(a, b): p.stdin.write(frame(fr).tobytes())
        p.stdin.close(); p.wait()
