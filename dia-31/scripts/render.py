"""Día 31 — "Los 12 mensajes" (historia de misterio hecha con IA → únete a Sumiago).
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
KEY = {'12', 'solo', '2:14', 'puerta', 'escaleras', 'minuto', 'mismo', 'fijo', 'desconectado', 'último',
       'nunca', 'pasó', 'inteligencia', 'artificial', 'historia', 'canal', 'negocio', 'grabarte', 'sumiago', 'link'}
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
M_PUL = load_m('mascota-pulgar.png', 470)
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

# ---------- escenas ----------
MSGS = ['No abras la puerta.', 'Ya subió las escaleras.', 'No te muevas.', 'Está en el pasillo.', 'Apaga la luz.', 'No hagas ruido.',
        'Está en la puerta.', 'No contestes.', 'Respira despacio.', 'Ya sabe.', 'Lo siento.', '…']
NUM = '601 555 0142'

def sc0(t, lt):
    im = BG.copy(); desk(im)
    machine(im, W / 2, 760, 1.2, '12', t=t)
    d = ImageDraw.Draw(im); tag(d, 80, 930, 1); tag(d, 560, 940, 2, .9)
    # etiqueta de evidencia
    d.rounded_rectangle((150, 1040, 570, 1150), 8, fill=(240, 236, 224)); d.text((170, 1060), 'EVIDENCIA · CASO 12', font=F('Inter-Black.otf', 26), fill=RED)
    d.text((170, 1100), 'Contestador · Apto. de Tomás', font=F('Inter-Medium.otf', 22), fill=(60, 60, 70))
    tape(im, 1225, 'NO PASAR   ·   ESCENA', -6, prog=lt / 0.8)
    q = max(0, lt - wt(0, '12') + ct(0))
    if q > 0: stamp(im, 500, 560, ['12 NUEVOS'], RED, q, 8, 40)
    im = camera(im, 1.0 + 0.1 * ease(lt / 5), W / 2, lerp(760, 700, ease(lt / 5)))
    obj('out', (190, 640, 530, 860)); return im

def sc1(t, lt):
    im = BG.copy(); d = ImageDraw.Draw(im)
    d.rectangle((60, 330, 660, 1060), fill=(150, 112, 70)); d.rectangle((60, 330, 660, 1060), outline=(110, 80, 50), width=10)  # corcho
    rr = random.Random(9)
    for k in range(260): x, y = rr.randint(70, 650), rr.randint(340, 1050); d.point((x, y), fill=(120, 88, 52))
    polaroid(im, W / 2 - 40, 640, 320, 4 * math.sin(lt * 1.3) + 3, 'Tomás')
    # calendario 9 años
    a = ease((lt - .3) / .4)
    if a > 0:
        cx, cy = 530, 880 + (1 - a) * 60; d.rounded_rectangle((cx - 100, cy - 90, cx + 100, cy + 100), 12, fill=(250, 250, 250)); d.rectangle((cx - 100, cy - 90, cx + 100, cy - 40), fill=RED)
        d.text((cx, cy - 65), 'VIVE SOLO', font=F('Inter-Black.otf', 24), fill='white', anchor='mm'); d.text((cx, cy + 20), '9', font=F('Inter-Black.otf', 90), fill=(30, 30, 30), anchor='mm')
        d.text((cx, cy + 78), 'AÑOS', font=F('Inter-Bold.otf', 22), fill=(80, 80, 80), anchor='mm')
    im = camera(im, 1.04 + 0.08 * ease(lt / 2.4), lerp(W / 2 - 40, 420, ease((lt - .4) / 1.5)), lerp(640, 760, ease((lt - .4) / 1.5)))
    obj('in', (160, 448, 480, 832)); obj('out', (160, 448, 480, 832)); return im

def bedroom(t, lt, glow=1.0):
    im = gradient((14, 18, 36), (4, 6, 12)); d = ImageDraw.Draw(im)
    d.rectangle((420, 300, 640, 640), fill=(20, 28, 54)); d.rectangle((420, 300, 640, 640), outline=(10, 12, 20), width=12); d.line((530, 300, 530, 640), fill=(10, 12, 20), width=8)
    d.ellipse((560, 340, 600, 380), fill=(220, 220, 200))
    im.alpha_composite(glow_layer(lambda dd: dd.rectangle((420, 300, 640, 640), fill=255), (90, 120, 200), 60, 60))
    d.rectangle((0, 980, W, H), fill=(20, 18, 24)); d.rectangle((60, 860, 420, 1000), fill=(48, 36, 30)); d.rectangle((60, 860, 420, 878), fill=(70, 54, 44))  # mesa de noche
    d.rectangle((420, 760, W, 1060), fill=(40, 46, 70)); d.ellipse((480, 700, 700, 800), fill=(200, 200, 210))  # cama, almohada
    return im

def sc2(t, lt):
    im = bedroom(t, lt); clock(im, 240, 790, '2:14', .9); machine(im, 400, 930, .55, '01', t=t)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((90, 700, 400, 880), fill=255), (255, 40, 40), 60, 90))
    tb = wt(2, '«no') - ct(2) + .15; fq = ease((lt - tb + .4) / .9)
    im = camera(im, 1.2 - .1 * fq, lerp(240, 330, fq), lerp(790, 700, fq))
    obj('in', (105, 731, 375, 849))
    counter(im, 1, t, 550, 300)
    bubble(im, 70, 470, '«No abras la puerta.»', t - wt(2, '«no') + .1, col=(40, 12, 16), tcol=(255, 210, 210))
    obj('out', (550, 300, 680, 396), False)
    return im

def sc3(t, lt):
    im = gradient((10, 12, 22), (2, 2, 6)); d = ImageDraw.Draw(im)
    # pasillo con escalera en perspectiva
    vx, vy = W / 2, 520
    d.polygon([(0, 0), (vx - 90, vy - 160), (vx - 90, vy + 120), (0, H)], fill=(24, 26, 38)); d.polygon([(W, 0), (vx + 90, vy - 160), (vx + 90, vy + 120), (W, H)], fill=(20, 22, 32))
    for k in range(10):
        q = k / 10; y = lerp(H, vy + 120, q ** .7); hw = lerp(W / 2, 90, q ** .7)
        d.rectangle((vx - hw, y - 26 * (1 - q) - 4, vx + hw, y), fill=mix((60, 50, 44), (20, 18, 18), q)); d.line((vx - hw, y - 26 * (1 - q) - 4, vx + hw, y - 26 * (1 - q) - 4), fill=(90, 76, 64), width=2)
    d.rectangle((vx - 90, vy - 160, vx + 90, vy + 120), fill=(30, 34, 50))
    im.alpha_composite(glow_layer(lambda dd: dd.rectangle((vx - 90, vy - 160, vx + 90, vy + 120), fill=255), (140, 160, 220), 40, 80))
    # silueta que aparece arriba
    a = ease((lt - 1.2) / 1.0)
    if a > 0:
        sl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(sl)
        sd.ellipse((vx - 22, vy - 70, vx + 22, vy - 26), fill=(4, 4, 8, int(255 * a))); sd.rounded_rectangle((vx - 40, vy - 30, vx + 40, vy + 110), 24, fill=(4, 4, 8, int(255 * a)))
        im.alpha_composite(sl)
    fq = ease((lt - .9) / 1.6); im = camera(im, 1.0 + 0.35 * fq, vx, lerp(H / 2, vy + 10, fq), shake=2 * ease((lt - 2) / 1), t=t)
    counter(im, 2, t, 550, 300); clock(im, 150, 1100, '2:15', .6)
    bubble(im, 90, 860, '«Ya subió las escaleras.»', t - wt(3, '«ya') + .1, col=(40, 12, 16), tcol=(255, 210, 210))
    obj('in', (550, 300, 680, 396), False); obj('out', (550, 300, 680, 396), False)
    return im

def sc4(t, lt):
    im = BG.copy(); desk(im, 1100)
    def content(d, cx, cy, w, h):
        n = 2 + int(min(10, max(0, (lt - .3) / (CL[4]['d'] - .4) * 10)))
        d.text((cx, cy - h / 2 + 70), 'Contestador', font=F('Inter-Bold.otf', 22), fill=(200, 200, 210), anchor='mm')
        rows = list(range(max(0, n - 8), n))
        for j, k in enumerate(rows):
            y = cy - h / 2 + 110 + j * 52; d.rounded_rectangle((cx - w / 2 + 26, y, cx + w / 2 - 26, y + 44), 14, fill=(36, 38, 50) if k < n - 1 else (90, 20, 26))
            d.text((cx - w / 2 + 40, y + 22), MSGS[k], font=F('Inter-SemiBold.otf', 18), fill='white', anchor='lm')
            d.text((cx + w / 2 - 38, y + 22), f'2:{14 + k}', font=F('Inter-Medium.otf', 14), fill=(160, 160, 170), anchor='rm')
    phone(im, 300, 720, 1.05, content)
    n = 2 + int(min(10, max(0, (lt - .3) / (CL[4]['d'] - .4) * 10)))
    counter(im, n, t, 540, 300)
    d = ImageDraw.Draw(im); bx, by = 600, 520
    for k in range(12):
        d.rectangle((bx + 30, by + 300 - k * 24, bx + 70, by + 318 - k * 24), fill=RED if k < n else (50, 40, 44))
    clock(im, 590, 1040, f'2:{13 + n}', .55)
    nf = 2 + min(10, max(0, (lt - .3) / (CL[4]['d'] - .4) * 10)); j = min(nf, 8) - 1
    ty = 720 - 315 + 110 * 1.05 + j * 52 * 1.05
    zq = ease(lt / .6) * (1 - ease((lt - CL[4]['d'] + .1) / .5))
    im = camera(im, 1.0 + .25 * zq, lerp(360, 300, zq), lerp(720, max(ty, 700), zq))
    obj('in', (540, 300, 670, 396), False); obj('out', (142, 405, 457, 1035)); return im

def sc5(t, lt):
    im = BG.copy(); desk(im, 1100); d = ImageDraw.Draw(im)
    SW = max(.05, (wt(5, 'mismo') - ct(5) - .3) / 12)
    d.rounded_rectangle((60, 380, 660, 1040), 24, fill=(236, 232, 220)); d.text((90, 420), 'REGISTRO DE LLAMADAS', font=F('Inter-Black.otf', 28), fill=(40, 40, 48))
    d.line((90, 460, 630, 460), fill=(180, 175, 165), width=2)
    for k in range(12):
        y = 482 + k * 45; d.text((90, y), f'{k + 1:02d}', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130)); d.text((150, y), NUM, font=F('Inter-Bold.otf', 24), fill=(30, 30, 40))
        d.text((630, y), f'2:{14 + k}', font=F('Inter-Medium.otf', 20), fill=(120, 120, 130), anchor='ra')
        q = (lt - .3 - k * SW)
        if q > 0:
            a = ease(q / .25); d.rounded_rectangle((140, y - 6, 140 + 200 * a, y + 34), 8, outline=RED, width=4)
    q = t - wt(5, 'mismo')
    if q > 0: stamp(im, 470, 760, ['MISMO', 'NÚMERO'], RED, q, -10, 50)
    kf = min(11, max(0, (lt - .3) / SW)); sq = ease((t - wt(5, 'mismo')) / .5)
    zq = ease(lt / .5) * (1 - sq)
    im = camera(im, 1.0 + .3 * zq, lerp(W / 2, 330, zq), lerp(710, 560 + kf * 45, zq))
    obj('in', (60, 380, 660, 1040)); obj('out', (300, 690, 640, 830)); return im

def sc6(t, lt, unpl=0.0):
    im = gradient((30, 30, 36), (12, 12, 16)); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line((x, 0, x, H), fill=(36, 36, 44), width=2)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((60, 360, 660, 1100), fill=255), (255, 230, 180), 90, 80))
    wall_phone(im, 390, 620, 1.2, unpl, t)
    d.rounded_rectangle((210, 290, 470, 350), 10, fill=(240, 236, 224)); d.text((340, 320), 'FIJO · TOMÁS', font=F('Inter-Black.otf', 26), fill=(30, 30, 40), anchor='mm')
    return im

def sc6w(t, lt):
    im = camera(sc6(t, lt), 1.0 + .25 * ease(lt / 1.8), 400, 560); obj('in', (354, 410, 510, 458)); return im
def sc7(t, lt):
    im = sc6(t, lt, ease(lt / .8))
    # polvo
    rr = random.Random(7); d = ImageDraw.Draw(im)
    for k in range(40):
        x = rr.randint(0, W); y = (rr.randint(0, H) + lt * 20 * (1 + rr.random())) % H; d.ellipse((x, y, x + 3, y + 3), fill=(255, 240, 210, 90))
    q = t - wt(7, 'desconectado')
    if q > 0: stamp(im, W / 2, 1080, ['DESCONECTADO', 'HACE 2 AÑOS'], RED, q, -6, 48)
    zq = ease(lt / 1.0)
    im = camera(im, 1.25 - .25 * zq, lerp(400, W / 2, zq), lerp(560, 760, zq))
    obj('out', (246, 380, 534, 860)); return im

def sc8(t, lt):
    im = BG.copy(); desk(im, 1100); d = ImageDraw.Draw(im)
    cx, cy = W / 2, 700
    d.rounded_rectangle((70, cy - 150, 650, cy + 150), 30, fill=(20, 20, 28), outline=(120, 30, 34), width=4)
    d.text((110, cy - 110), 'MENSAJE 12 · 2:25', font=F('Inter-Black.otf', 28), fill=(255, 90, 96))
    d.ellipse((110, cy - 30, 190, cy + 50), fill=RED); d.polygon([(140, cy - 8), (140, cy + 28), (170, cy + 10)], fill='white')
    waveform(im, 220, cy + 10, 400, 90, t, prog=min(1, lt / 2.0), seed=12)
    d.text((110, cy + 90), 'Duración: 0:03 · 1 palabra', font=F('Inter-Medium.otf', 22), fill=(150, 150, 160))
    a = ease((lt - .6) / .5)
    if a > 0: d.text((W / 2, cy - 260), '?', font=F('Inter-Black.otf', 200), fill=RED + (int(220 * a),), anchor='mm')
    ph = 220 + 400 * min(1, lt / 2.0)
    im = camera(im, 1.0 + .3 * ease(lt / CL[8]['d']), lerp(W / 2, ph, .5 * ease(lt / 2)), cy)
    obj('in', (70, 550, 650, 850)); obj('out', (70, 550, 650, 850))
    q = t - wt(8, 'yo')
    if q > 0: static(im, min(.55, q * .9), int(t * 30))
    return im

def sc9(t, lt):
    im = BG.copy(); desk(im, 1080); d = ImageDraw.Draw(im)
    # carpeta
    d.rounded_rectangle((90, 360, 640, 1080), 16, fill=(196, 160, 104)); d.rounded_rectangle((90, 330, 330, 380), 12, fill=(196, 160, 104))
    d.rounded_rectangle((120, 400, 610, 1050), 10, fill=(246, 242, 230))
    d.text((150, 430), 'EXPEDIENTE 12 · TOMÁS', font=F('Inter-Black.otf', 24), fill=(60, 60, 66))
    polaroid(im, 260, 620, 200, -5, 'Tomás')
    machine(im, 480, 620, .45, '12', t=t)
    waveform(im, 150, 900, 420, 60, t, col=(60, 60, 70), seed=4); d.text((150, 950), 'VOZ · NARRADOR', font=F('Inter-Bold.otf', 18), fill=(120, 120, 130))
    q = t - wt(9, 'nunca')
    if q > 0: stamp(im, W / 2, 790, ['ESTA HISTORIA', 'NUNCA PASÓ'], RED, q + .05, -9, 54)
    q2 = t - wt(9, 'inteligencia')
    if q2 > 0:
        tape(im, 1010, 'HECHO CON IA   ·   FICCIÓN', 7, col=RED, tcol=WHITE, prog=q2 / .6)
        tape(im, 380, 'HECHO CON IA   ·   FICCIÓN', -5, col=(20, 20, 24), tcol=WHITE, prog=(q2 - .25) / .6)
    sq = ease((t - wt(9, 'nunca') + .3) / .6)
    im = camera(im, 1.0 + .15 * sq * (1 - ease((t - wt(9, 'inteligencia')) / .8)), W / 2, lerp(700, 790, sq), shake=4 * max(0, 1 - q * 5) if q > 0 else 0, t=t)
    obj('in', (120, 400, 610, 1050)); obj('out', (150, 500, 360, 760))
    if lt < .35: static(im, .8 * (1 - lt / .35), int(t * 30) + 3)
    return im

def sc10(t, lt):
    im = BG.copy(); d = ImageDraw.Draw(im)
    ks = [('Tu historia', 'libro', 'historia'), ('Tu canal', 'canal', 'canal'), ('Tu negocio', 'tienda', 'negocio')]
    for k, (ti, kd, wd) in enumerate(ks):
        q = t - wt(10, wd) + .1
        icon_card(im, 130 + k * 230, 470, 200, 220, ti, kd, 1.0 if k == 0 else ease(q / .35), glow=1 if 0 < q < .8 else 0)
    q = t - wt(10, 'crear')
    if q > 0:
        a = ease(q / .4)
        def content(dd, cx, cy, w, h):
            dd.rectangle((cx - w / 2 + 14, cy - h / 2 + 60, cx + w / 2 - 14, cy + 60), fill=(26, 28, 40))
            dd.rounded_rectangle((cx - 60, cy - 160, cx + 60, cy - 40), 14, fill=(36, 38, 52)); dd.text((cx, cy - 100), '12', font=F('Inter-Black.otf', 56), fill=RED, anchor='mm')
            dd.text((cx, cy - 10), 'Los 12 mensajes', font=F('Inter-Bold.otf', 20), fill='white', anchor='mm')
            dd.rounded_rectangle((cx - 100, cy + 90, cx + 100, cy + 140), 12, fill=RED); dd.text((cx, cy + 115), 'HECHO CON IA', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
            for k in range(3): dd.ellipse((cx + 90, cy + 180 + k * 50, cx + 120, cy + 210 + k * 50), fill=(70, 72, 86))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, W / 2, 920, .78, content)
        L = camera(L, 1, ) if False else L
        if a < 1:
            m = L.getchannel('A').point(lambda p: int(p * a)); L.putalpha(m)
        im.alpha_composite(L, (0, int((1 - a) * 120)))
    q = t - wt(10, 'sin')
    if q > 0:
        a = back_out(q / .4); cx, cy = 590, 1000; r = 70 * a
        d = ImageDraw.Draw(im); d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(245, 243, 236))
        d.rounded_rectangle((cx - 36 * a, cy - 22 * a, cx + 20 * a, cy + 22 * a), 6, fill=(40, 40, 48)); d.polygon([(cx + 20 * a, cy - 6 * a), (cx + 40 * a, cy - 18 * a), (cx + 40 * a, cy + 18 * a), (cx + 20 * a, cy + 6 * a)], fill=(40, 40, 48))
        d.line((cx - 46 * a, cy + 46 * a, cx + 46 * a, cy - 46 * a), fill=RED, width=int(10 * a) + 1)
    pq = ease((t - wt(10, 'crear') - .2) / .8)
    im = camera(im, 1.0 + .2 * pq, W / 2, lerp(640, 920, pq))
    obj('in', (30, 360, 230, 580)); obj('out', (243, 686, 477, 1154)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = ImageDraw.Draw(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110))
    # tarjeta de Sumiago
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26)))
    mask_text(im, (W / 2, y + 150), 'Gana con Marketing', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 190), 'e Inteligencia Artificial', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .45) / .4))
    q = t - wt(11, 'herramientas')
    chips = ['VIDEOS VIRALES', 'VOCES IA', 'IDEAS']
    for k, c in enumerate(chips):
        b = back_out((q - k * .12) / .35)
        if b > 0:
            f = F('Inter-Black.otf', 20); tws = [d.textlength(x, font=f) + 32 for x in chips]; gap = 14
            x0 = W / 2 - (sum(tws) + gap * 2) / 2; tw = tws[k] - 32; cx = x0 + sum(tws[:k]) + gap * k + tws[k] / 2
            d.rounded_rectangle((cx - tw / 2 - 16, y + 228, cx + tw / 2 + 16, y + 272), 22, fill=RED); d.text((cx, y + 250), c, font=f, fill='white', anchor='mm')
    # mascota con el pulgar
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5)
    im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob)))
    q = t - wt(11, 'regístrate')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1040
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    CAM.update(x0=0, y0=0, z=1); obj('in', (60, 330, 660, 630)); obj('out', (60, 330, 660, 630))
    return im

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
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6w, sc7, sc8, sc9, sc10, sc11]
LOGO_RECT = (50, 500, 670, 700)
TR = 0.32  # media duración de cada transformación
def starts():
    return [c['t0'] - 0.15 for c in CL] + [LOGO_T]
ST = starts()
def scene_at(i, t):
    """Escena i en el tiempo t (i = 12 → cierre). Devuelve imagen y sus rects."""
    OBJ.clear(); CAM.update(x0=0, y0=0, z=1)
    if i == 12:
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
NOMORPH = {7}
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
    if i < 12 or (b == 12 and t < LOGO_T + TR):
        v = VIG if i < 12 else None
        if i < 12: im.alpha_composite(VIG)
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
