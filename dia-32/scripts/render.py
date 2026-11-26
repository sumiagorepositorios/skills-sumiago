"""Día 32 — "La llamada de las 3 a. m." (historia de humor hecha con IA → regístrate en sumiago.com).
Dibuja a 720x1280, 30 fps. Uso (en la carpeta de trabajo):
  python render.py still 3.5 20      -> still_3.5.jpg ...
  python render.py INI FIN salida.mp4 -> video sin audio de los cuadros INI..FIN
"""
import json, math, random, sys, os, subprocess
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 720, 1280, 30
FONT_DIRS = ['/usr/share/fonts/opentype/inter/', os.path.join(RAIZ, 'fonts') + os.sep,
             os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts') + os.sep, 'C:\\Windows\\Fonts\\']
_fc = {}
def F(n, s):
    k = (n, s)
    if k not in _fc:
        for dd in FONT_DIRS:
            if os.path.isfile(dd + n): _fc[k] = ImageFont.truetype(dd + n, s); break
        else: sys.exit(f'No encontré la fuente {n}. Instala Inter o cópiala a fonts/.')
    return _fc[k]
RED = (230, 38, 47); GOLD = (255, 196, 60); WHITE = (255, 255, 255)
TL = json.load(open('tl.json')); CL = TL['clips']; LV = json.load(open('lv.json'))
NF = int(TL['total'] * FPS)
LOGO_T = CL[-1]['t0'] + CL[-1]['d'] + 0.35

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))
def back_out(x):
    x = max(0, min(1, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def ct(i): return CL[i]['t0']

# ---------- palabras ----------
def words_timing(c):
    ws = c['text'].split(); tot = sum(len(w) + 2 for w in ws); t = c['t0'] + 0.03; out = []
    for w in ws:
        dd = (len(w) + 2) / tot * c['d'] * 0.97; out.append((w, t)); t += dd
    return out
WT = [[(w, t) for w, t in c['words']] if 'words' in c else words_timing(c) for c in CL]
def wt(ci, word, n=0):
    k = 0
    for w, t in WT[ci]:
        if w.strip('¿?.,:«»…').lower().startswith(word):
            if k == n: return t
            k += 1
    return ct(ci)
KEY = {'3:00', 'vibrar', 'vibración', 'nada', 'nunca', 'desconocidos', 'contesté', 'aló', 'patricia', 'equivocada', 'tranques',
       'recuerdas', 'escuela', 'redes', 'esposa', 'ojos', 'producto', 'servicio', 'negocio', 'empresa', 'sumiago.com', 'comienza'}
def is_key(w): return w.strip('¿?.,:«»…').lower() in KEY

# ---------- fondos ----------
def gradient(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')
def glow_layer(shape_fn, col, blur, alpha=255):
    m = Image.new('L', (W, H), 0); shape_fn(ImageDraw.Draw(m)); m = m.filter(ImageFilter.GaussianBlur(blur))
    lay = Image.new('RGBA', (W, H), col + (0,)); lay.putalpha(m.point(lambda p: int(p * alpha / 255))); return lay
def vignette():
    y, x = np.mgrid[0:H, 0:W]; r = np.sqrt(((x - W / 2) / (W * .75)) ** 2 + ((y - H / 2) / (H * .7)) ** 2)
    a = np.clip((r - .55) * 1.6, 0, 1) * 200
    v = Image.new('RGBA', (W, H), (0, 0, 0, 0)); v.putalpha(Image.fromarray(a.astype(np.uint8))); return v
VIG = vignette()
_g = np.clip(1 - np.linspace(0, 1, 300) ** 1.4, 0, 1) * 185
TOPB = Image.new('RGBA', (W, H), (0, 0, 0, 0)); TOPB.putalpha(Image.fromarray(np.pad(np.repeat(_g[:, None], W, 1), ((0, H - 300), (0, 0))).astype(np.uint8)))
VIG.alpha_composite(TOPB)
def lamp_bg(top=(26, 32, 52), bot=(8, 10, 18)):
    im = gradient(top, bot)
    im.alpha_composite(glow_layer(lambda d: d.polygon([(W / 2 - 60, 120), (W / 2 + 60, 120), (W + 120, 1150), (-120, 1150)], fill=150), (255, 230, 180), 70, 90))
    d = ImageDraw.Draw(im); d.ellipse((W / 2 - 70, 96, W / 2 + 70, 140), fill=(250, 236, 200)); d.rectangle((W / 2 - 2, 0, W / 2 + 2, 100), fill=(40, 40, 50))
    # pared con tablas
    for x in range(0, W, 90): d.line((x, 0, x, 1000), fill=(0, 0, 0, 40), width=2)
    return im
BG = lamp_bg()
def desk(im, y=980, col=(52, 40, 34)):
    d = ImageDraw.Draw(im); d.rectangle((0, y, W, H), fill=col); d.rectangle((0, y, W, y + 10), fill=mix(col, (255, 255, 255), .15))
    for k in range(9): d.line((0, y + 40 + k * 32, W, y + 50 + k * 30), fill=mix(col, (0, 0, 0), .25), width=2)

# ---------- objetos ----------
def led_text(im, xy, txt, size, col=(255, 40, 40), on=True, anchor='mm'):
    if not on: col = (70, 20, 20)
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).text(xy, txt, font=F('Inter-Black.otf', size), fill=col + (255,), anchor=anchor)
    if on: im.alpha_composite(g.filter(ImageFilter.GaussianBlur(size / 6)))
    im.alpha_composite(g)

def machine(im, cx, cy, s, count, led_on=True, blink=True, t=0):
    """Contestador: cuerpo gris oscuro, ventana de casete, pantalla LED, botones, rejilla."""
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    w, h = 460 * s, 270 * s; x0, y0 = cx - w / 2, cy - h / 2
    d.rounded_rectangle((x0 + 10 * s, y0 + 22 * s, x0 + w + 10 * s, y0 + h + 22 * s), 26 * s, fill=(0, 0, 0, 120))
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 26 * s, fill=(46, 48, 56), outline=(78, 80, 92), width=max(1, int(3 * s)))
    d.rounded_rectangle((x0 + 8 * s, y0 + 8 * s, x0 + w - 8 * s, y0 + 40 * s), 14 * s, fill=(58, 60, 70))
    # casete
    d.rounded_rectangle((x0 + 26 * s, y0 + 60 * s, x0 + 230 * s, y0 + 170 * s), 12 * s, fill=(22, 22, 28), outline=(90, 92, 104), width=max(1, int(2 * s)))
    for k, xx in enumerate([x0 + 85 * s, x0 + 170 * s]):
        r = 26 * s; d.ellipse((xx - r, y0 + 115 * s - r, xx + r, y0 + 115 * s + r), fill=(200, 200, 205))
        a = t * 4 + k
        for j in range(3):
            aa = a + j * 2.09; d.line((xx, y0 + 115 * s, xx + math.cos(aa) * r * .8, y0 + 115 * s + math.sin(aa) * r * .8), fill=(60, 60, 66), width=max(1, int(4 * s)))
    # pantalla LED
    d.rounded_rectangle((x0 + 260 * s, y0 + 60 * s, x0 + w - 26 * s, y0 + 170 * s), 12 * s, fill=(16, 6, 8), outline=(90, 40, 40), width=max(1, int(2 * s)))
    d.text((x0 + 272 * s, y0 + 72 * s), 'MENSAJES', font=F('Inter-Bold.otf', max(8, int(16 * s))), fill=(150, 60, 60))
    # botones y rejilla
    for k in range(5):
        bx = x0 + 30 * s + k * 50 * s; d.rounded_rectangle((bx, y0 + 196 * s, bx + 38 * s, y0 + 226 * s), 8 * s, fill=(30, 31, 38) if k else RED)
    for i in range(7):
        for j in range(3):
            px, py = x0 + 300 * s + i * 18 * s, y0 + 196 * s + j * 18 * s; d.ellipse((px, py, px + 8 * s, py + 8 * s), fill=(24, 24, 30))
    im.alpha_composite(lay)
    on = led_on and (not blink or (t * 2.2) % 1 < .62)
    led_text(im, (x0 + (260 * s + w - 26 * s) / 2, y0 + 130 * s), count, int(70 * s), on=on)
    # luz roja del botón
    if on: im.alpha_composite(glow_layer(lambda dd: dd.ellipse((x0 + 25 * s, y0 + 190 * s, x0 + 75 * s, y0 + 232 * s), fill=255), RED, 14, 160))

def tag(d, x, y, n, s=1):
    d.polygon([(x, y), (x + 54 * s, y), (x + 54 * s, y + 60 * s), (x, y + 60 * s)], fill=(250, 200, 40)); d.polygon([(x, y + 60 * s), (x + 54 * s, y + 60 * s), (x + 64 * s, y + 70 * s), (x + 10 * s, y + 70 * s)], fill=(190, 150, 20))
    d.text((x + 27 * s, y + 30 * s), str(n), font=F('Inter-Black.otf', int(36 * s)), fill=(20, 20, 20), anchor='mm')

def tape(im, y, txt, ang, col=(250, 205, 30), tcol=(20, 20, 20), prog=1.0):
    L = Image.new('RGBA', (1400, 64), (0, 0, 0, 0)); d = ImageDraw.Draw(L); d.rectangle((0, 0, 1400, 64), fill=col + (255,))
    x = 10; f = F('Inter-Black.otf', 30)
    while x < 1400: d.text((x, 32), txt, font=f, fill=tcol, anchor='lm'); x += d.textlength(txt, font=f) + 40
    cw = int(1400 * ease(prog))
    if cw < 2: return
    L = L.crop((0, 0, cw, 64)); L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(L, (int(-340 + 0), int(y - L.height / 2)))

def stamp(im, cx, cy, lines, col, t, ang=-8, size=52):
    if t <= 0: return
    sc = 1 + 1.6 * (1 - ease(t / 0.22)); a = min(1, t / 0.12)
    f = F('Inter-Black.otf', size); tw = max(ImageDraw.Draw(im).textlength(l, font=f) for l in lines)
    w, h = int(tw + 50), int(len(lines) * size * 1.15 + 34)
    L = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((3, 3, w - 3, h - 3), 12, outline=col + (255,), width=6)
    for k, l in enumerate(lines): d.text((w / 2, 17 + size * .58 + k * size * 1.15), l, font=f, fill=col + (255,), anchor='mm')
    rr = random.Random(3); m = L.getchannel('A')
    noise = Image.fromarray((np.array(m) * (np.random.RandomState(4).rand(h, w) > .18)).astype(np.uint8)); L.putalpha(noise.point(lambda p: int(p * a * .92)))
    L = L.resize((int(w * sc), int(h * sc)), Image.LANCZOS).rotate(ang, expand=True, resample=Image.BICUBIC)
    im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def bubble(im, x, y, txt, t, col=(36, 38, 48), tcol=WHITE, w=None, size=34):
    if t <= 0: return
    s = back_out(t / 0.35); a = min(1, t / 0.15)
    f = F('Inter-SemiBold.otf', size); d0 = ImageDraw.Draw(im); tw = d0.textlength(txt, font=f)
    bw, bh = int((w or tw + 56)), int(size * 2)
    L = Image.new('RGBA', (bw + 20, bh + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((0, 0, bw, bh), bh / 2.2, fill=col + (int(240 * a),)); d.polygon([(26, bh - 4), (50, bh - 4), (18, bh + 22)], fill=col + (int(240 * a),))
    d.text((28, bh / 2), txt, font=f, fill=tcol + (int(255 * a),), anchor='lm')
    L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))), Image.LANCZOS)
    im.alpha_composite(L, (int(x), int(y + (1 - s) * 30)))

def counter(im, n, t, x=560, y=330):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((x, y, x + 130, y + 96), 14, fill=(14, 10, 14, 230), outline=(120, 30, 34), width=3)
    d.text((x + 65, y + 18), 'MENSAJE', font=F('Inter-Bold.otf', 15), fill=(200, 90, 90), anchor='mm')
    led_text(im, (x + 65, y + 60), f'{n:02d}', 46)
    d.text((x + 112, y + 80), '/12', font=F('Inter-Bold.otf', 15), fill=(160, 80, 80), anchor='mm')

def clock(im, cx, cy, txt, s=1.0):
    d = ImageDraw.Draw(im); w, h = 300 * s, 130 * s
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 20 * s, fill=(12, 12, 16), outline=(50, 50, 60), width=4)
    led_text(im, (cx, cy + 4 * s), txt, int(92 * s))

def person_face(size, hair=(150, 150, 155), skin=(226, 184, 150)):
    """Tomás: señor de unos 60, canoso, gafas. Dibujo simple original."""
    L = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(L); s = size / 300
    d.rectangle((0, 0, size, size), fill=(205, 210, 214))
    d.rounded_rectangle((60 * s, 220 * s, 240 * s, 330 * s), 60 * s, fill=(70, 86, 110))
    d.rectangle((128 * s, 200 * s, 172 * s, 240 * s), fill=mix(skin, (0, 0, 0), .1))
    d.ellipse((80 * s, 60 * s, 220 * s, 220 * s), fill=skin)
    d.chord((76 * s, 46 * s, 224 * s, 170 * s), 180, 360, fill=hair); d.ellipse((70 * s, 110 * s, 92 * s, 150 * s), fill=skin); d.ellipse((208 * s, 110 * s, 230 * s, 150 * s), fill=skin)
    for ex in (118, 182):
        d.ellipse(((ex - 22) * s, 118 * s, (ex + 22) * s, 156 * s), outline=(40, 40, 46), width=max(1, int(5 * s)))
        d.ellipse(((ex - 6) * s, 132 * s, (ex + 6) * s, 144 * s), fill=(40, 40, 46))
    d.line((140 * s, 137 * s, 160 * s, 137 * s), fill=(40, 40, 46), width=max(1, int(5 * s)))
    d.line((100 * s, 112 * s, 134 * s, 108 * s), fill=(110, 110, 115), width=max(1, int(6 * s))); d.line((166 * s, 108 * s, 200 * s, 112 * s), fill=(110, 110, 115), width=max(1, int(6 * s)))
    d.arc((125 * s, 168 * s, 175 * s, 196 * s), 20, 160, fill=(130, 70, 60), width=max(1, int(5 * s)))
    d.line((150 * s, 145 * s, 144 * s, 172 * s), fill=mix(skin, (0, 0, 0), .25), width=max(1, int(4 * s)))
    return L
FACE = person_face(300)
def polaroid(im, cx, cy, w, ang, label, face=FACE, gray=False):
    h = int(w * 1.2); L = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((10, 14, w + 14, h + 18), fill=(0, 0, 0, 90)); d.rectangle((0, 0, w, h), fill=(246, 244, 236))
    fc = face.resize((w - 30, w - 30), Image.LANCZOS)
    if gray: fc = fc.convert('LA').convert('RGBA')
    L.alpha_composite(fc, (15, 15)); d.text((w / 2, w + (h - w) / 2 - 6), label, font=F('Inter-SemiBoldItalic.otf', int(w / 8)), fill=(50, 50, 60), anchor='mm')
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
    ImageDraw.Draw(im).ellipse((cx - 10, cy - L.height / 2 + 4, cx + 10, cy - L.height / 2 + 24), fill=RED)

def wall_phone(im, cx, cy, s, unplugged=0.0, t=0):
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - 120 * s, cy - 200 * s, cx + 120 * s, cy + 200 * s), 30 * s, fill=(225, 220, 205), outline=(170, 165, 150), width=4)
    d.rounded_rectangle((cx - 150 * s, cy - 240 * s, cx - 70 * s, cy + 180 * s), 34 * s, fill=(210, 205, 190), outline=(160, 155, 140), width=4)  # auricular
    for i in range(3):
        for j in range(4):
            bx, by = cx - 20 * s + i * 44 * s, cy - 110 * s + j * 54 * s
            d.rounded_rectangle((bx, by, bx + 34 * s, by + 40 * s), 8 * s, fill=(245, 242, 232), outline=(170, 165, 150), width=2)
            d.text((bx + 17 * s, by + 20 * s), '123456789*0#'[j * 3 + i], font=F('Inter-Bold.otf', int(20 * s)), fill=(80, 80, 80), anchor='mm')
    d.rounded_rectangle((cx - 30 * s, cy - 175 * s, cx + 100 * s, cy - 135 * s), 6 * s, fill=(30, 40, 36))
    d.text((cx + 35 * s, cy - 155 * s), 'TOMÁS', font=F('Inter-Bold.otf', int(18 * s)), fill=(120, 200, 150), anchor='mm')
    # cable en espiral hasta la pared / enchufe
    px, py = cx - 110 * s, cy + 180 * s
    pts = []
    for k in range(60):
        q = k / 59; x = px + math.sin(q * 30) * 14 * s + q * 40 * s; y = py + q * 250 * s; pts.append((x, y))
    d.line(pts, fill=(200, 195, 180), width=max(2, int(6 * s)))
    # cable de línea a la toma
    sx, sy = cx + 60 * s, cy + 200 * s
    end = (cx + 170 * s, cy + 330 * s) if unplugged < .5 else (cx + 150 * s + 40 * ease((unplugged - .5) * 2) * s, cy + 430 * s + 60 * ease((unplugged - .5) * 2) * s)
    d.line((sx, sy, sx, cy + 300 * s, end[0], end[1]), fill=(40, 40, 44), width=max(2, int(6 * s)), joint='curve')
    d.rounded_rectangle((cx + 150 * s, cy + 300 * s, cx + 220 * s, cy + 370 * s), 10 * s, fill=(235, 232, 222), outline=(150, 150, 140), width=3)
    d.rectangle((cx + 175 * s, cy + 325 * s, cx + 195 * s, cy + 345 * s), fill=(40, 40, 40))
    d.rounded_rectangle((end[0] - 10 * s, end[1] - 14 * s, end[0] + 12 * s, end[1] + 14 * s), 4 * s, fill=(60, 60, 64))

def waveform(im, x, y, w, h, t, col=RED, prog=1.0, seed=1):
    d = ImageDraw.Draw(im); n = 46; r = random.Random(seed)
    amps = [abs(math.sin(k * .7 + seed)) * .6 + r.random() * .4 for k in range(n)]
    for k in range(n):
        xx = x + k * w / n; a = amps[k] * (0.7 + .3 * math.sin(t * 9 + k)); hh = h * a / 2
        c = col if k / n < prog else (90, 92, 104)
        d.rounded_rectangle((xx, y - hh, xx + w / n * .55, y + hh), 3, fill=c)

def static(im, a, seed):
    if a <= 0: return
    n = (np.random.RandomState(seed).rand(H // 4, W // 4) * 255).astype(np.uint8)
    L = Image.fromarray(n).resize((W, H), Image.NEAREST).convert('RGBA'); L.putalpha(int(255 * a)); im.alpha_composite(L)

def icon_card(im, cx, cy, w, h, title, kind, a, glow=0):
    if a <= 0: return
    s = back_out(a); L = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((20, 20, w + 20, h + 20), 22, fill=(245, 243, 236), outline=RED if glow else (210, 205, 195), width=5 if glow else 2)
    c = (w / 2 + 20, h / 2 + 4)
    if kind == 'libro':
        d.rectangle((c[0] - 60, c[1] - 50, c[0] - 4, c[1] + 30), fill=(60, 64, 80)); d.rectangle((c[0] + 4, c[1] - 50, c[0] + 60, c[1] + 30), fill=(60, 64, 80))
        for k in range(4): d.line((c[0] - 50, c[1] - 34 + k * 16, c[0] - 14, c[1] - 34 + k * 16), fill=(220, 220, 225), width=3); d.line((c[0] + 14, c[1] - 34 + k * 16, c[0] + 50, c[1] - 34 + k * 16), fill=(220, 220, 225), width=3)
    elif kind == 'canal':
        d.rounded_rectangle((c[0] - 64, c[1] - 46, c[0] + 64, c[1] + 40), 22, fill=RED); d.polygon([(c[0] - 16, c[1] - 22), (c[0] - 16, c[1] + 18), (c[0] + 22, c[1] - 2)], fill='white')
    else:
        d.rectangle((c[0] - 60, c[1] - 20, c[0] + 60, c[1] + 40), fill=(70, 74, 90)); d.rectangle((c[0] - 20, c[1] + 4, c[0] + 16, c[1] + 40), fill=(230, 200, 120))
        for k in range(5): d.pieslice((c[0] - 70 + k * 28, c[1] - 44, c[0] - 42 + k * 28, c[1] - 12), 0, 180, fill=RED if k % 2 == 0 else 'white')
        d.rectangle((c[0] - 70, c[1] - 52, c[0] + 70, c[1] - 30), fill=RED)
    d.text((w / 2 + 20, h + 20 - 34), title, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='mm')
    L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))), Image.LANCZOS)
    if glow: im.alpha_composite(glow_layer(lambda dd: dd.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 22, fill=255), RED, 30, int(150 * glow)))
    im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

def phone(im, cx, cy, s, content_fn=None):
    w, h = 300 * s, 600 * s; d = ImageDraw.Draw(im)
    d.rounded_rectangle((cx - w / 2 + 12, cy - h / 2 + 18, cx + w / 2 + 12, cy + h / 2 + 18), 46 * s, fill=(0, 0, 0, 120))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 46 * s, fill=(18, 18, 22), outline=(80, 82, 92), width=5)
    d.rounded_rectangle((cx - w / 2 + 12 * s, cy - h / 2 + 12 * s, cx + w / 2 - 12 * s, cy + h / 2 - 12 * s), 36 * s, fill=(10, 12, 20))
    d.rounded_rectangle((cx - 40 * s, cy - h / 2 + 22 * s, cx + 40 * s, cy - h / 2 + 44 * s), 11 * s, fill=(0, 0, 0))
    if content_fn: content_fn(d, cx, cy, w, h)

# ---------- mascota ----------
def load_m(f, w):
    im = Image.open(os.path.join(RAIZ, 'assets', f)).convert('RGBA'); return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
M_PUL = load_m('mascota-pulgar.png', 470); M_PUL2 = load_m('mascota-pulgar.png', 330)
LOGO = load_m('logo-sumiago.png', 620); LOGO_S = load_m('logo-sumiago.png', 300)

# ---------- subtítulos (arriba a la izquierda, palabra por palabra, como el ejemplo) ----------
def caption(im, t):
    ci = None
    for i, c in enumerate(CL):
        if c['t0'] - 0.05 <= t <= c['t0'] + c['d'] + 0.3: ci = i
    if ci is None: return
    ws = [(w, tw) for w, tw in WT[ci] if tw <= t]
    # ventana: solo las últimas palabras que caben en 3 líneas
    fN, fK = F('Inter-Bold.otf', 44), F('Inter-BlackItalic.otf', 46)
    lines = [[]]; x = 0; maxw = 620
    d = ImageDraw.Draw(im)
    for w, tw in ws:
        f = fK if is_key(w) else fN; lw = d.textlength(w + ' ', font=f)
        if x + lw > maxw and lines[-1]: lines.append([]); x = 0
        lines[-1].append((w, tw, f, x)); x += lw
    lines = lines[-3:]
    cap = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    for li, ln in enumerate(lines):
        LH = 62; band = Image.new('RGBA', (W, LH), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
        for w, tw, f, x in ln:
            q = ease((t - tw) / 0.22); yo = (1 - q) * LH          # la palabra sube desde detrás de la máscara
            col = (255, 70, 78) if is_key(w) else WHITE
            bd.text((50 + x, 2 + yo), w, font=f, fill=col + (255,))
            if is_key(w) and q > .2:                                # subrayado que se dibuja tras la palabra
                lw = bd.textlength(w.strip('¿?.,:«»…'), font=f) * ease((t - tw - .12) / .25); bd.rectangle((50 + x, 56, 50 + x + lw, 60), fill=RED)
        cap.alpha_composite(band, (0, 88 + li * 58))
    shd = Image.new('RGBA', (W, H), (0, 0, 0, 0)); shd.putalpha(cap.getchannel('A').point(lambda p: int(p * .85)).filter(ImageFilter.GaussianBlur(6)))
    im.alpha_composite(shd); im.alpha_composite(cap)

def mask_text(im, xy, txt, f, col, q):
    """Texto que aparece deslizándose desde detrás de una máscara (de abajo hacia arriba)."""
    if q <= 0: return
    d0 = ImageDraw.Draw(im); tw = d0.textlength(txt, font=f); hh = int(f.size * 1.35)
    L = Image.new('RGBA', (int(tw) + 8, hh), (0, 0, 0, 0)); ImageDraw.Draw(L).text((4, hh / 2 + (1 - ease(q)) * hh), txt, font=f, fill=col + (255,), anchor='lm')
    im.alpha_composite(L, (int(xy[0] - tw / 2 - 4), int(xy[1] - hh / 2)))

# ---------- cámara ----------
CAM = {'x0': 0, 'y0': 0, 'z': 1}
OBJ = {}
def camera(im, z, cx=W / 2, cy=H / 2, shake=0, t=0):
    sx = math.sin(t * 53) * shake; sy = math.cos(t * 47) * shake
    w, h = W / z, H / z; x0 = min(max(cx - w / 2 + sx, 0), W - w); y0 = min(max(cy - h / 2 + sy, 0), H - h)
    CAM.update(x0=x0, y0=y0, z=z)
    if z <= 1.001 and shake == 0: return im
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)
def obj(kind, r, raw=True):
    """Guarda el rectángulo del objeto clave (entrada/salida) en coordenadas finales."""
    if raw: r = tuple((v - (CAM['x0'] if k % 2 == 0 else CAM['y0'])) * CAM['z'] for k, v in enumerate(r))
    OBJ[kind] = r
def follow(key, target, k=1.0):
    return target

# ---------- personajes (dibujos originales) ----------
SKIN_M = (196, 138, 100); SKIN_W = (234, 192, 160); HAIR_M = (24, 20, 20); HAIR_W = (78, 44, 26)
def face(d, cx, cy, r, who='m', eyes='closed', mouth=0.0, brow=0, sweat=False, smile=False):
    """Cabeza frontal simple. eyes: closed/open/wide. mouth 0..1 abre la boca."""
    sk = SKIN_M if who == 'm' else SKIN_W; hr = HAIR_M if who == 'm' else HAIR_W
    if who == 'w':  # pelo largo detrás
        d.rounded_rectangle((cx - r * 1.15, cy - r * .9, cx + r * 1.15, cy + r * 1.5), r * .9, fill=hr)
    d.ellipse((cx - r * 1.08, cy - r * .1, cx - r * .82, cy + r * .35), fill=sk); d.ellipse((cx + r * .82, cy - r * .1, cx + r * 1.08, cy + r * .35), fill=sk)
    d.ellipse((cx - r * .9, cy - r, cx + r * .9, cy + r * 1.05), fill=sk)
    if who == 'm': d.chord((cx - r * .95, cy - r * 1.12, cx + r * .95, cy + r * .2), 180, 360, fill=hr)
    else:
        d.chord((cx - r * .98, cy - r * 1.1, cx + r * .98, cy + r * .45), 180, 360, fill=hr)
        d.polygon([(cx - r * .95, cy - r * .2), (cx - r * .1, cy - r * .62), (cx - r * .95, cy + r * .3)], fill=hr)
    ey = cy + r * .12; ex = r * .38; lw = max(2, int(r * .09))
    for sx in (-1, 1):
        x = cx + sx * ex
        if eyes == 'closed': d.arc((x - r * .2, ey - r * .14, x + r * .2, ey + r * .14), 10, 170, fill=(40, 30, 30), width=lw)
        elif eyes == 'open': d.ellipse((x - r * .09, ey - r * .12, x + r * .09, ey + r * .12), fill=(30, 24, 24))
        else:
            d.ellipse((x - r * .24, ey - r * .24, x + r * .24, ey + r * .24), fill=(255, 255, 255), outline=(30, 24, 24), width=max(1, lw // 2))
            d.ellipse((x - r * .1 + sx * -r * .05, ey - r * .1, x + r * .1 + sx * -r * .05, ey + r * .1), fill=(30, 24, 24))
        by = ey - r * (.32 if eyes != 'wide' else .42) - (r * .1 if (brow and sx == brow) else 0)
        d.line((x - r * .2, by + (r * .06 if who == 'w' else 0), x + r * .2, by), fill=hr if who == 'm' else (60, 34, 20), width=lw)
    my = cy + r * .62
    if mouth > .05: d.ellipse((cx - r * .18, my - r * .12 * mouth - 2, cx + r * .18, my + r * .14 * mouth + 2), fill=(120, 30, 34))
    elif smile: d.arc((cx - r * .26, my - r * .2, cx + r * .26, my + r * .12), 20, 160, fill=(150, 50, 50), width=lw)
    else: d.line((cx - r * .16, my, cx + r * .16, my), fill=(130, 60, 50), width=lw)
    if sweat:
        sx_, sy_ = cx + r * .85, cy - r * .35; d.polygon([(sx_, sy_ - r * .25), (sx_ - r * .12, sy_ + r * .05), (sx_ + r * .12, sy_ + r * .05)], fill=(150, 200, 255)); d.ellipse((sx_ - r * .12, sy_ - r * .05, sx_ + r * .12, sy_ + r * .18), fill=(150, 200, 255))
def back_head(d, cx, cy, r):
    d.rounded_rectangle((cx - r * 1.1, cy - r * 1.0, cx + r * 1.1, cy + r * 1.45), r * .95, fill=HAIR_W)
    for k in range(5): d.arc((cx - r * .9 + k * r * .3, cy - r * .7, cx - r * .3 + k * r * .3, cy + r * 1.3), 200, 300, fill=(98, 58, 36), width=3)

def lv_at(t): return LV[min(max(0, int(t * FPS)), len(LV) - 1)]
def speaking(t, sp):
    for c in CL:
        if c['sp'] == sp and c['t0'] <= t <= c['t0'] + c['d']: return min(1, lv_at(t) / .08)
    return 0

def night_bg():
    im = gradient((16, 20, 40), (4, 6, 12)); d = ImageDraw.Draw(im)
    d.rectangle((440, 150, 650, 430), fill=(22, 30, 60)); d.rectangle((440, 150, 650, 430), outline=(10, 12, 22), width=12); d.line((545, 150, 545, 430), fill=(10, 12, 22), width=8)
    d.ellipse((575, 190, 615, 230), fill=(230, 230, 210))
    im.alpha_composite(glow_layer(lambda dd: dd.rectangle((440, 150, 650, 430), fill=255), (90, 120, 210), 60, 55))
    return im
NIGHT = night_bg()

def phone_small(im, cx, cy, s, vib=0.0, t=0, lit=True, ang=0):
    """Celular pequeño (sobre la mesa o en la mano). vib>0 = vibrando."""
    sx = math.sin(t * 90) * 4 * vib
    L = Image.new('RGBA', (int(90 * s) + 40, int(170 * s) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((20, 20, 20 + 90 * s, 20 + 170 * s), 14 * s, fill=(18, 18, 22), outline=(90, 92, 104), width=3)
    d.rounded_rectangle((20 + 7 * s, 20 + 9 * s, 20 + 83 * s, 20 + 161 * s), 9 * s, fill=(70, 120, 230) if lit else (10, 12, 18))
    if lit:
        d.ellipse((20 + 30 * s, 20 + 40 * s, 20 + 60 * s, 20 + 70 * s), fill=(235, 240, 255))
        d.ellipse((20 + 14 * s, 20 + 130 * s, 20 + 34 * s, 20 + 150 * s), fill=RED); d.ellipse((20 + 56 * s, 20 + 130 * s, 20 + 76 * s, 20 + 150 * s), fill=(40, 200, 90))
    if ang: L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
    if lit: im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx - 110 * s, cy - 130 * s, cx + 110 * s, cy + 130 * s), fill=255), (90, 140, 255), 50, 90))
    im.alpha_composite(L, (int(cx - L.width / 2 + sx), int(cy - L.height / 2)))
    if vib > 0:
        d = ImageDraw.Draw(im)
        for k in range(2):
            for sg in (-1, 1):
                x = cx + sg * (70 * s + k * 18 * s); a = int(220 * vib * (0.5 + .5 * math.sin(t * 20 + k)))
                d.arc((x - 24 * s, cy - 50 * s, x + 24 * s, cy + 50 * s), 300 if sg > 0 else 120, 60 if sg > 0 else 240, fill=(255, 255, 255, a), width=4)

def bed_scene(t, wife_turn=0.0, wife_eyes='closed', man='sleep', vib=0.0, phone_lit=False, man_mouth=0, sweat=False):
    im = NIGHT.copy(); d = ImageDraw.Draw(im)
    d.rectangle((0, 1020, W, H), fill=(22, 20, 26))
    # cabecera y cama
    d.rounded_rectangle((150, 520, 690, 800), 30, fill=(58, 40, 34)); d.rounded_rectangle((170, 540, 670, 780), 22, fill=(70, 50, 42))
    d.ellipse((220, 700, 400, 790), fill=(214, 214, 224)); d.ellipse((420, 700, 600, 790), fill=(214, 214, 224))
    # personas
    if man == 'sleep': face(d, 310, 700, 62, 'm', 'closed')
    if wife_turn < .5:
        sq = max(.05, abs(math.cos(math.pi * wife_turn)))
        L = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); back_head(ImageDraw.Draw(L), 150, 150, 62)
        L = L.resize((max(1, int(300 * sq)), 300)); im.alpha_composite(L, (int(510 - L.width / 2), 550))
    else:
        sq = max(.05, abs(math.cos(math.pi * wife_turn)))
        L = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); face(ImageDraw.Draw(L), 150, 150, 62, 'w', wife_eyes)
        L = L.resize((max(1, int(300 * sq)), 300)); im.alpha_composite(L, (int(510 - L.width / 2), 550))
    d = ImageDraw.Draw(im)
    # cobija
    d.rounded_rectangle((120, 760, 720, 1080), 40, fill=(44, 52, 86)); d.rounded_rectangle((120, 760, 720, 800), 20, fill=(62, 72, 110))
    for k in range(4): d.arc((160 + k * 130, 820, 300 + k * 130, 1000), 200, 320, fill=(36, 42, 72), width=4)
    if man == 'sit':
        # sentado con el celular en la oreja
        d.rounded_rectangle((210, 690, 410, 900), 60, fill=(120, 124, 134))
        face(d, 310, 610, 62, 'm', 'open', man_mouth, brow=1, sweat=sweat)
        d.ellipse((360, 600, 400, 660), fill=SKIN_M); d.rounded_rectangle((370, 560, 394, 625), 6, fill=(18, 18, 22))
        im.alpha_composite(glow_layer(lambda dd: dd.ellipse((280, 520, 470, 700), fill=255), (90, 140, 255), 40, 80))
    # mesitas
    d = ImageDraw.Draw(im)
    d.rectangle((0, 840, 130, 1040), fill=(48, 36, 30)); d.rectangle((0, 840, 130, 856), fill=(70, 54, 44))
    d.rectangle((690, 840, W, 1040), fill=(48, 36, 30)); d.rectangle((690, 840, W, 856), fill=(70, 54, 44))
    if man != 'sit': phone_small(im, 68, 800, .5, vib, t, phone_lit, ang=90)
    return im

def zzz(im, x, y, t, a=1.0):
    d = ImageDraw.Draw(im)
    for k in range(3):
        q = ((t * .6 + k / 3) % 1)
        d.text((x + q * 60 + k * 6, y - q * 120), 'z', font=F('Inter-Black.otf', int(26 + 14 * q)), fill=(200, 210, 255, int(220 * (1 - q) * a)))

def silhouette(im, cx, cy, s, t, talk=0.0):
    """Patricia: silueta femenina misteriosa (pelo largo ondulado, cuello, hombros) con luz roja de contorno."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); col = (16, 8, 14, 255)
    # hombros y torso
    d.rounded_rectangle((cx - 230 * s, cy + 210 * s, cx + 230 * s, cy + 800 * s), 170 * s, fill=col)
    d.polygon([(cx - 38 * s, cy + 90 * s), (cx + 38 * s, cy + 90 * s), (cx + 50 * s, cy + 240 * s), (cx - 50 * s, cy + 240 * s)], fill=col)
    # pelo largo y ondulado (detrás)
    pts = []
    for k in range(41):
        q = k / 40; ang = math.pi * (1.05 + .9 * q)
        pts.append((cx + math.cos(ang) * 125 * s, cy - 10 * s + math.sin(ang) * 135 * s))
    right = [(cx + 128 * s + math.sin(y / 18 + t * 2) * 10 * s, cy + y * s) for y in range(0, 360, 12)]
    left = [(cx - 135 * s + math.sin(y / 16 + t * 2 + 1) * 12 * s, cy + y * s) for y in range(360, -1, -12)]
    d.polygon(pts + right + [(cx + 60 * s, cy + 370 * s), (cx - 70 * s, cy + 380 * s)] + left, fill=col)
    # cabeza (ligeramente de lado)
    d.ellipse((cx - 82 * s, cy - 115 * s, cx + 82 * s, cy + 110 * s), fill=col)
    # mechón que cae sobre la cara
    d.polygon([(cx - 90 * s, cy - 80 * s), (cx + 20 * s, cy - 125 * s), (cx - 40 * s, cy + 10 * s), (cx - 95 * s, cy + 160 * s)], fill=col)
    # mano con el celular en la oreja
    d.rounded_rectangle((cx + 66 * s, cy - 45 * s, cx + 104 * s, cy + 75 * s), 12 * s, fill=(34, 32, 40, 255))
    d.ellipse((cx + 60 * s, cy + 30 * s, cx + 130 * s, cy + 110 * s), fill=col)
    rim = L.getchannel('A').filter(ImageFilter.GaussianBlur(16 * s))
    g = Image.new('RGBA', (W, H), (255, 40, 70, 0)); g.putalpha(rim.point(lambda p: int(min(255, p * (.9 + .3 * talk)))))
    im.alpha_composite(g); im.alpha_composite(L)
    # luz del celular sobre la mejilla
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx + 30 * s, cy - 50 * s, cx + 110 * s, cy + 80 * s), fill=255), (255, 140, 160), 22 * s, 110))
    d2 = ImageDraw.Draw(im)
    # labios rojos y arete dorado (únicos detalles visibles)
    my = cy + 52 * s; o = 5 * s * talk
    d2.chord((cx - 26 * s, my - 10 * s - o, cx + 26 * s, my + 4 * s), 180, 360, fill=(215, 30, 55)); d2.chord((cx - 26 * s, my - 6 * s, cx + 26 * s, my + 12 * s + o), 0, 180, fill=(190, 20, 45))
    d2.ellipse((cx + 8 * s, my - 6 * s, cx + 16 * s, my - 2 * s), fill=(255, 170, 180))
    ex, ey = cx + 70 * s, cy + 40 * s
    d2.ellipse((ex - 7 * s, ey - 7 * s, ex + 7 * s, ey + 7 * s), fill=GOLD)
    # ojos entrecerrados con brillo
    for sx in (-1, 1):
        x = cx + sx * 34 * s - 6 * s; y = cy - 2 * s
        d2.arc((x - 18 * s, y - 8 * s, x + 18 * s, y + 10 * s), 200, 340, fill=(255, 110, 130), width=max(2, int(4 * s)))

def whisper_wave(im, x, y, w, h, t, a=1.0):
    d = ImageDraw.Draw(im); n = 40
    for k in range(n):
        xx = x + k * w / n; amp = abs(math.sin(k * .5 + t * 6)) * (.3 + .7 * a); hh = h * amp / 2 + 2
        d.rounded_rectangle((xx, y - hh, xx + w / n * .5, y + hh), 3, fill=(255, 120, 150, 230))

def red_room():
    im = gradient((46, 6, 18), (6, 2, 6)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((120, 200, 760, 1000), fill=255), (180, 20, 50), 120, 140)); return im
REDROOM = red_room()

# ---------- escenas ----------
def sc0(t, lt):
    vib_t = wt(0, 'vibrar'); vib = ease((t - vib_t + .5) / .3)
    im = bed_scene(t, vib=vib, phone_lit=vib > 0)
    zzz(im, 360, 640, t); zzz(im, 560, 640, t + .4)
    d = ImageDraw.Draw(im); d.rounded_rectangle((694, 760, 720, 838), 8, fill=(12, 12, 16))
    clock(im, 600, 470 + 330, '3:00', .45)
    q = t - wt(0, '3:00')
    if q > 0: stamp(im, 250, 330, ['3:00 A. M.'], RED, q, -7, 54)
    fq = ease((t - vib_t + .7) / 1.0)
    im = camera(im, 1.0 + .55 * fq, lerp(W / 2, 120, fq), lerp(700, 800, fq), shake=3 * vib, t=t)
    obj('out', (40, 760, 100, 840)); return im

def sc1(t, lt):
    im = NIGHT.copy(); d = ImageDraw.Draw(im)
    d.rectangle((0, 760, W, H), fill=(214, 214, 224)); d.rounded_rectangle((-40, 980, W + 40, H + 40), 60, fill=(44, 52, 86))
    face(d, 380, 820, 170, 'w', 'closed', smile=True)
    d = ImageDraw.Draw(im); d.rounded_rectangle((-40, 1010, W + 40, H + 40), 60, fill=(44, 52, 86))
    zzz(im, 560, 640, t, 1)
    # chip de vibración
    a = back_out(lt / .4)
    if a > .02:
        cw, ch_ = 360 * a, 90 * a; cx, cy = 260, 330
        d.rounded_rectangle((cx - cw / 2, cy - ch_ / 2, cx + cw / 2, cy + ch_ / 2), 45 * a, fill=(20, 22, 32), outline=(90, 140, 255), width=3)
        if a > .6:
            d.rounded_rectangle((cx - 150, cy - 26, cx - 120, cy + 26), 6, fill=(90, 140, 255))
            for k in range(2): d.arc((cx - 175 - k * 12, cy - 22, cx - 155 - k * 12, cy + 22), 120, 240, fill=(90, 140, 255), width=3); d.arc((cx - 115 + k * 12, cy - 22, cx - 95 + k * 12, cy + 22), 300, 60, fill=(90, 140, 255), width=3)
            d.text((cx - 80, cy), 'VIBRACIÓN', font=F('Inter-Black.otf', 32), fill='white', anchor='lm')
    q = t - wt(1, 'nada')
    if q > 0: stamp(im, 470, 560, ['NO ESCUCHÓ', 'NADA'], RED, q, 8, 44)
    im = camera(im, 1.05 + .12 * ease(lt / 2.5), lerp(300, 380, ease(lt / 2)), lerp(560, 760, ease(lt / 2)))
    obj('in', (80, 285, 440, 375), False); obj('out', (80, 285, 440, 375), False); return im

def call_ui(d, cx, cy, w, h, t, thumb=0.0, accepted=0.0):
    d.text((cx, cy - h / 2 + 90), 'Llamada entrante', font=F('Inter-Medium.otf', 22), fill=(170, 175, 190), anchor='mm')
    d.ellipse((cx - 60, cy - 160, cx + 60, cy - 40), fill=(50, 54, 70)); d.text((cx, cy - 100), '?', font=F('Inter-Black.otf', 70), fill='white', anchor='mm')
    d.text((cx, cy + 10), 'Número', font=F('Inter-Black.otf', 34), fill='white', anchor='mm'); d.text((cx, cy + 52), 'desconocido', font=F('Inter-Black.otf', 34), fill='white', anchor='mm')
    d.text((cx, cy + 100), '+58 4•• ••• ••47', font=F('Inter-Medium.otf', 22), fill=(170, 175, 190), anchor='mm')
    by = cy + h / 2 - 110
    d.ellipse((cx - 110, by - 38, cx - 34, by + 38), fill=RED); d.line((cx - 90, by + 6, cx - 54, by + 6), fill='white', width=8)
    gx = lerp(cx + 72, cx - 72, 0) ; d.ellipse((cx + 34, by - 38, cx + 110, by + 38), fill=(40, 200, 90) if accepted < .5 else (40, 220, 100))
    d.arc((cx + 52, by - 18, cx + 92, by + 22), 200, 340, fill='white', width=7)

def sc2(t, lt):
    im = NIGHT.copy(); desk(im, 1100, (30, 24, 22))
    tc = wt(2, 'contesté'); thumb = ease((t - tc + .5) / .5)
    def content(d, cx, cy, w, h): call_ui(d, cx, cy, w, h, t, thumb, thumb)
    phone(im, W / 2, 680, 1.15, content)
    # pulgar que contesta
    if thumb > 0:
        d = ImageDraw.Draw(im); bx, by = W / 2 + 72, 680 + 345 - 110
        tx_, ty_ = lerp(bx + 120, bx, thumb), lerp(by + 220, by + 20, thumb)
        d.rounded_rectangle((tx_ - 40, ty_, tx_ + 40, ty_ + 260), 40, fill=SKIN_M); d.ellipse((tx_ - 30, ty_ + 6, tx_ + 30, ty_ + 56), fill=(226, 180, 150))
        if thumb >= 1:
            r = 40 + (t - tc) * 160; d.ellipse((bx - r, by - r, bx + r, by + r), outline=(40, 220, 100, max(0, int(200 - (t - tc) * 300))), width=6)
    q = t - wt(2, 'nunca')
    if q > 0: stamp(im, 520, 300, ['YO NUNCA', 'CONTESTO'], RED, q, 7, 42)
    vib = 1 - thumb
    sx = math.sin(t * 80) * 3 * vib
    fq = ease((t - tc + .8) / .8)
    im = camera(im, 1.0 + .35 * fq, lerp(W / 2, W / 2 + 72, fq) + sx, lerp(680, 900, fq))
    obj('in', (185, 335, 535, 1025)); obj('out', (300, 860, 470, 1000)); return im

def sc3(t, lt):
    im = bed_scene(t, man='sit', man_mouth=speaking(t, 'N'))
    bubble(im, 90, 380, '¿Aló?', t - ct(3) + .05, size=44)
    im = camera(im, 1.35, 330, 640)
    obj('in', (300, 420, 470, 560)); obj('out', (330, 380, 500, 560)); return im

def call_card(im, t, name_q):
    d = ImageDraw.Draw(im)
    Y0 = 300; d.rounded_rectangle((60, Y0, 660, Y0 + 120), 30, fill=(20, 10, 16, 230), outline=(160, 40, 60), width=3)
    sec = int(max(0, t - ct(4) + 3)); d.text((100, Y0 + 35), f'LLAMADA EN CURSO · 00:{sec:02d}', font=F('Inter-Bold.otf', 22), fill=(255, 160, 170))
    mask_text(im, (240, Y0 + 82), 'PATRICIA', F('Inter-Black.otf', 40), (255, 255, 255), name_q)
    if name_q <= 0: d.text((100, Y0 + 66), 'Desconocido', font=F('Inter-Black.otf', 34), fill=(200, 200, 210))

def sc4(t, lt):
    im = REDROOM.copy()
    silhouette(im, 380, 700, 1.0, t, speaking(t, 'P'))
    fq = ease(lt / CL[4]['d'])
    im = camera(im, 1.0 + .15 * fq, lerp(W / 2, 400, fq), lerp(700, 720, fq))
    call_card(im, t, ease((t - wt(4, 'patricia')) / .35))
    whisper_wave(im, 120, 1180, 480, 60, t, speaking(t, 'P'))
    bubble(im, 50, 1010, 'Hola… soy yo. Patricia.', t - ct(4) - .1, col=(70, 10, 26), tcol=(255, 220, 228), size=36)
    obj('in', (60, 300, 660, 420), False); obj('out', (60, 300, 660, 420), False); return im

def man_close(t, mouth, sweat=False, brow=1):
    im = NIGHT.copy(); d = ImageDraw.Draw(im)
    d.rounded_rectangle((60, 900, 660, 1400), 200, fill=(120, 124, 134))
    face(d, 340, 650, 200, 'm', 'open', mouth, brow=brow, sweat=sweat)
    d.ellipse((520, 640, 620, 790), fill=SKIN_M); d.rounded_rectangle((540, 520, 600, 690), 12, fill=(18, 18, 22))
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((420, 440, 720, 780), fill=255), (90, 140, 255), 60, 80))
    return im

def sc5(t, lt):
    im = man_close(t, speaking(t, 'N'), sweat=lt > .6)
    bubble(im, 70, 300, 'Creo que estás equivocada.', t - ct(5) + .05, size=36)
    im = camera(im, 1.0 + .08 * ease(lt / 1.4), 360, 640)
    obj('in', (140, 450, 540, 860)); obj('out', (140, 450, 540, 860)); return im

def sc6(t, lt):
    im = REDROOM.copy()
    silhouette(im, 360, 640, 1.3, t, speaking(t, 'P'))
    im = camera(im, 1.05 + .12 * ease(lt / 2), 380, lerp(700, 660, ease(lt / 2)))
    call_card(im, t, 1)
    bubble(im, 30, 1040, 'No me tranques…', t - ct(6) - .05, col=(70, 10, 26), tcol=(255, 220, 228), size=34)
    bubble(im, 230, 1135, '¿No me recuerdas?', t - wt(6, '¿no', 0) - .05 if False else t - wt(6, 'recuerdas') + .3, col=(70, 10, 26), tcol=(255, 220, 228), size=34)
    obj('in', (200, 420, 520, 900), False); obj('out', (60, 300, 660, 420), False); return im

def sc7(t, lt):
    im = man_close(t, speaking(t, 'N'), sweat=True, brow=0)
    q = t - ct(7)
    if q > 0: stamp(im, W / 2, 330, ['NO.'], RED, q, -6, 110)
    im = camera(im, 1.12 - .08 * ease(lt / .5), 360, 600, shake=5 * max(0, 1 - q * 4) if q > 0 else 0, t=t)
    obj('in', (140, 450, 540, 860)); obj('out', (100, 400, 400, 760)); return im

def girl_face(size):
    L = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((0, 0, size, size), fill=(210, 220, 236)); s = size / 300
    d.rounded_rectangle((60 * s, 230 * s, 240 * s, 340 * s), 60 * s, fill=(200, 40, 60))
    d.ellipse((30 * s, 120 * s, 90 * s, 230 * s), fill=(40, 26, 20)); d.ellipse((210 * s, 120 * s, 270 * s, 230 * s), fill=(40, 26, 20))  # coletas
    face(d, 150 * s, 150 * s, 82 * s, 'w', 'open', smile=True)
    return L
GIRL = girl_face(300)

def sc8(t, lt):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rectangle((40, 300, 680, 1100), fill=(150, 112, 70)); d.rectangle((40, 300, 680, 1100), outline=(110, 80, 50), width=10)
    rr = random.Random(9)
    for k in range(240): x, y = rr.randint(50, 670), rr.randint(310, 1090); d.point((x, y), fill=(120, 88, 52))
    polaroid(im, 230, 560, 300, -5 + 2 * math.sin(lt * 1.5), 'Patricia · escuela', face=GIRL)
    q = t - wt(8, 'escuela')
    if q > 0: stamp(im, 240, 830, ['LA DE LA', 'ESCUELA'], RED, q, -8, 40)
    # tarjeta de redes sociales (genérica)
    rq = t - wt(8, 'redes') + .6
    a = back_out(rq / .45)
    if a > .02:
        L = Image.new('RGBA', (330, 470), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.rounded_rectangle((0, 0, 329, 469), 28, fill=(250, 250, 252)); dl.rounded_rectangle((0, 0, 329, 90), 28, fill=RED); dl.rectangle((0, 60, 329, 90), fill=RED)
        dl.ellipse((115, 45, 215, 145), fill=(250, 250, 252)); L.alpha_composite(GIRL.resize((88, 88)), (121, 51))
        msk = Image.new('L', (330, 470), 0); ImageDraw.Draw(msk).rounded_rectangle((0, 0, 329, 469), 28, fill=255)
        dl.text((165, 175), 'Patricia', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='mm')
        dl.text((165, 210), 'Perfil · Redes sociales', font=F('Inter-Medium.otf', 18), fill=(120, 120, 130), anchor='mm')
        for k, (lab, val) in enumerate([('Amigos', '1.248'), ('Fotos', '386')]):
            dl.text((90 + k * 150, 260), val, font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm'); dl.text((90 + k * 150, 290), lab, font=F('Inter-Medium.otf', 16), fill=(120, 120, 130), anchor='mm')
        dl.rounded_rectangle((30, 330, 300, 380), 25, fill=(240, 240, 244)); dl.text((165, 355), '+58 4•• ••• ••47', font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='mm')
        dl.rounded_rectangle((30, 395, 300, 445), 25, fill=RED); dl.text((165, 420), 'TU NÚMERO', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
        L = L.resize((max(1, int(330 * a)), max(1, int(470 * a))), Image.LANCZOS); im.alpha_composite(L, (int(500 - L.width / 2), int(720 - L.height / 2)))
    fq = ease((t - wt(8, 'conseguí') + .2) / 1.2)
    im = camera(im, 1.15 + .1 * fq, lerp(260, 500, fq), lerp(600, 720, fq))
    obj('in', (80, 370, 380, 750)); obj('out', (80, 370, 380, 750)); return im

def sc9(t, lt):
    turn = ease((t - wt(9, 'volteó') + .2) / .5)
    eo = t > wt(9, 'ojos') - .05
    im = bed_scene(t, wife_turn=turn, wife_eyes='wide' if eo else 'closed', man='sit', sweat=True)
    if eo:
        im.alpha_composite(glow_layer(lambda dd: dd.rectangle((0, 0, W, H), fill=255), (200, 0, 20), 1, int(60 * min(1, (t - wt(9, 'ojos')) / .2))))
    fq = ease((t - wt(9, 'ojos') + .4) / .5)
    zq = ease((t - wt(9, 'volteó') + .3) / .8)
    z = 1.15 + .35 * zq + 1.3 * fq
    q = t - wt(9, 'ojos')
    im = camera(im, z, lerp(lerp(400, 480, zq), 510, fq), lerp(640, 690, fq), shake=6 * max(0, 1 - q * 3) if q > 0 else 0, t=t)
    obj('in', (300, 420, 470, 560)); obj('out', (210, 440, 510, 700)); return im

CHIPS = [('Producto', 'producto'), ('Servicio', 'servicio'), ('Negocio', 'negocio'), ('Empresa', 'empresa')]
def sc10(t, lt):
    im = gradient((40, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 200, 820, 1100), fill=255), RED, 120, 110))
    d = ImageDraw.Draw(im)
    # la esposa (despierta) habla a cámara
    L = Image.new('RGBA', (300, 300), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); dl.ellipse((0, 0, 299, 299), fill=(214, 214, 224))
    face(dl, 150, 165, 95, 'w', 'open', speaking(t, 'E'), smile=True)
    m = Image.new('L', (300, 300), 0); ImageDraw.Draw(m).ellipse((0, 0, 299, 299), fill=255); L.putalpha(m)
    im.alpha_composite(L, (210, 290)); d = ImageDraw.Draw(im); d.ellipse((210, 290, 510, 590), outline='white', width=6)
    mask_text(im, (W / 2, 650), '¿Te gustó este video?', F('Inter-Black.otf', 44), WHITE, ease((t - ct(10) - .1) / .4))
    mask_text(im, (W / 2, 705), 'Haz videos así para tu…', F('Inter-SemiBold.otf', 32), (230, 200, 205), ease((t - wt(10, 'deseas')) / .4))
    for k, (lab, w_) in enumerate(CHIPS):
        b = back_out((t - wt(10, w_) + .08) / .35)
        if b > .02:
            cx, cy = 200 + (k % 2) * 320, 790 + (k // 2) * 100; cw, ch_ = 280 * b, 84 * b
            d.rounded_rectangle((cx - cw / 2, cy - ch_ / 2, cx + cw / 2, cy + ch_ / 2), 42 * b, fill=(250, 250, 252))
            if b > .6: d.text((cx, cy), lab.upper(), font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    q = t - wt(10, 'regístrate')
    if q > 0:
        bx = 1 + .04 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 450, 1070
        d.rounded_rectangle((cx - 255 * bx * b, cy - 48 * bx * b, cx + 255 * bx * b, cy + 48 * bx * b), 48, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy - 2), 'SUMIAGO.COM', font=F('Inter-Black.otf', 44), fill=RED, anchor='mm')
        if b > .5: d.text((cx, cy - 78), 'REGÍSTRATE EN', font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
    mq = ease((t - wt(10, 'regístrate') + .6) / .5)
    if mq > 0:
        mm = M_PUL2; bob = math.sin(t * 5) * 6
        im.alpha_composite(mm, (int(-50 - (1 - mq) * 320), int(H - mm.height * .8 + bob)))
    q2 = t - wt(10, 'comienza')
    if q2 > 0:
        d = ImageDraw.Draw(im); ay = 1080 + 10 * math.sin(t * 8)
        d.polygon([(450 - 24, ay + 160), (450 + 24, ay + 160), (450, ay + 126)], fill='white')
    CAM.update(x0=0, y0=0, z=1); obj('in', (210, 290, 510, 590), False); obj('out', (195, 1022, 705, 1118), False)
    return im

SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9, sc10]
NOMORPH = {7}

# ---------- cierre ----------
def end_scene(lt, t):
    im = Image.new('RGBA', (W, H), (8, 10, 22, 255)); rr = ease(lt / 0.4) * 1500
    ImageDraw.Draw(im).ellipse((W / 2 - rr, 640 - rr, W / 2 + rr, 640 + rr), fill=(255, 255, 255, 255))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cy = 600
    for k in range(3):
        q = (lt - 0.45 - k * 0.35) / 1.4
        if 0 < q < 1: r = 120 + q * 520; d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), outline=RED + (int(170 * (1 - q)),), width=6)
    rnd = random.Random(5)
    for k in range(26):
        q = (lt - 0.45) / 1.1
        if 0 < q < 1:
            a = rnd.random() * 2 * math.pi; sp = 220 + rnd.random() * 320; r = 6 + rnd.random() * 8
            x = W / 2 + math.cos(a) * sp * ease(q); y = cy + math.sin(a) * sp * ease(q) + 80 * q * q
            col = RED if k % 3 else (40, 40, 46); d.ellipse((x - r * (1 - q), y - r * (1 - q), x + r * (1 - q), y + r * (1 - q)), fill=col + (int(255 * (1 - q)),))
    im.alpha_composite(ov)
    sc = back_out((lt - 0.3) / 0.55) if lt > 0.3 else 0
    if sc > 0.02:
        fl = 1 + 0.025 * math.sin(max(0, lt - 1) * 3); lw, lh = int(LOGO.width * sc * fl), int(LOGO.height * sc * fl)
        lg = LOGO.resize((max(1, lw), max(1, lh)), Image.LANCZOS)
        q = (lt - 1.0) / 0.7
        if 0 < q < 1:
            band = Image.new('L', lg.size, 0); bd = ImageDraw.Draw(band); bx = -200 + q * (lw + 400)
            bd.polygon([(bx, 0), (bx + 70, 0), (bx - 50, lh), (bx - 120, lh)], fill=200)
            m = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(12)), lg.getchannel('A'))
            wl = Image.new('RGBA', lg.size, (255, 255, 255, 0)); wl.putalpha(m); lg = Image.alpha_composite(lg, wl)
        im.alpha_composite(lg, ((W - lw) // 2, cy - lh // 2))
    a = ease((lt - 1.1) / 0.5)
    if a > 0:
        d = ImageDraw.Draw(im); yo = (1 - a) * 30
        mask_text(im, (W // 2, 800), 'Crea videos con IA', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 290 * bx, 940 - 38 * bx + yo, W / 2 + 290 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'REGÍSTRATE EN SUMIAGO.COM', font=F('Inter-Black.otf', 28), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

LOGO_RECT = (50, 500, 670, 700)
TR = 0.32  # media duración de cada transformación
def starts():
    return [c['t0'] - 0.15 for c in CL] + [LOGO_T]
ST = starts()
def scene_at(i, t):
    """Escena i en el tiempo t (i = 12 → cierre). Devuelve imagen y sus rects."""
    OBJ.clear(); CAM.update(x0=0, y0=0, z=1)
    if i == len(CL):
        im = end_scene(max(0, t - LOGO_T), t); OBJ['in'] = LOGO_RECT; return im, dict(OBJ)
    im = SC[i](t, max(0, t - ST[i])); return im, dict(OBJ)
def rr_mask(size, rad):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), rad, fill=255); return m
def morph(A, ra, B, rb, p):
    e = ease(p); bk = math.sin(math.pi * p) * 0.06   # pequeño rebote de escala a mitad de camino
    r = [lerp(a, b, e) for a, b in zip(ra, rb)]
    cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2; w = (r[2] - r[0]) * (1 + bk); h = (r[3] - r[1]) * (1 + bk)
    r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    base = Image.blend(A.filter(ImageFilter.GaussianBlur(8 * e)), B.filter(ImageFilter.GaussianBlur(8 * (1 - e))), e)
    sz = (max(2, int(r[2] - r[0])), max(2, int(r[3] - r[1])))
    ca = A.crop(tuple(int(v) for v in ra)).resize(sz, Image.BILINEAR); cb = B.crop(tuple(int(v) for v in rb)).resize(sz, Image.BILINEAR)
    piece = Image.blend(ca, cb, ease((p - .25) / .5))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((r[0] + 10, r[1] + 18, r[2] + 10, r[3] + 18), 20, fill=(0, 0, 0, int(140 * math.sin(math.pi * p))))
    base.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    piece.putalpha(rr_mask(sz, 18)); base.alpha_composite(piece, (int(r[0]), int(r[1])))
    return base
def frame(f):
    t = f / FPS
    i = 0
    for k, s0 in enumerate(ST):
        if t >= s0: i = k
    # ¿estamos cerca de un cambio de escena?
    nxt = i + 1 if i + 1 < len(ST) and ST[i + 1] - t < TR else None
    prv = i if i > 0 and t - ST[i] < TR else None
    b = nxt if nxt is not None else prv
    if b is not None and b not in NOMORPH:
        p = (t - (ST[b] - TR)) / (2 * TR)
        A, oa = scene_at(b - 1, t if t < ST[b] else ST[b] - 0.001)
        B, ob = scene_at(b, max(t, ST[b]))
        im = morph(A, oa.get('out', (0, 0, W, H)), B, ob.get('in', (0, 0, W, H)), p)
    else:
        im, _ = scene_at(i, t)
    if i < len(CL) or (b == len(CL) and t < LOGO_T + TR):
        if i < len(CL): im.alpha_composite(VIG)
        caption(im, t)
    return im.convert('RGB')

if __name__ == '__main__':
    if sys.argv[1] == 'still':
        for s in sys.argv[2:]:
            frame(int(float(s) * FPS)).save(f'still_{s}.jpg', quality=90)
        sys.exit()
    a, b, out = int(sys.argv[1]), min(int(sys.argv[2]), NF), sys.argv[3]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', 'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    for f in range(a, b):
        p.stdin.write(frame(f).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(out + '.tmp.mp4', out)
