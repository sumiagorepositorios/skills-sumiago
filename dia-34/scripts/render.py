"""Día 34 — "La libreta de la abuela" (historia: una nieta saca a la luz las recetas guardadas → prueba Sumiago).
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
KEY = {'rosa', 'libreta', '40', 'cocadas', 'cajón', 'valentina', '19', 'ningún', 'trabajo', '7', 'igualitas', 'foto', 'portada', 'gratis', 'whatsapp',
       'marketplace', 'inteligencia', 'artificial', 'vecina', 'segundo', 'nunca', '3', 'cafetería', 'viernes', 'ver', 'guardado', 'sumiago', 'link', 'pruébalo', 'historia'}
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

# ---------- dibujo con transparencia real (ImageDraw reemplaza el alfa en vez de mezclarlo) ----------
class BD:
    def __init__(s, im): s.im = im; s.d = ImageDraw.Draw(im)
    def __getattr__(s, name):
        f = getattr(s.d, name)
        def w(*a, **k):
            tr = lambda c: isinstance(c, tuple) and len(c) == 4 and c[3] < 255
            if tr(k.get('fill')) or tr(k.get('outline')):
                L = Image.new('RGBA', s.im.size, (0, 0, 0, 0)); getattr(ImageDraw.Draw(L), name)(*a, **k); s.im.alpha_composite(L); return
            return f(*a, **k)
        return w

# ---------- cocina ----------
CREAM = (250, 238, 220); WOOD = (150, 98, 60); INK = (60, 44, 36)
def kitchen_bg(top=(252, 236, 214), bot=(236, 206, 170), night=0.0):
    im = gradient(mix(top, (40, 48, 80), night), mix(bot, (30, 30, 50), night)); d = BD(im)
    for y in range(300, 900, 64):            # azulejos
        for x in range((y // 64) % 2 * 32 - 32, W, 64):
            d.rectangle((x + 2, y + 2, x + 62, y + 62), outline=mix((232, 210, 182), (50, 54, 80), night), width=2)
    # ventana con cortina
    wc = mix((190, 225, 245), (24, 30, 64), night)
    d.rounded_rectangle((470, 330, 660, 560), 10, fill=wc, outline=(250, 250, 250), width=10); d.line((565, 330, 565, 560), fill=(250, 250, 250), width=8)
    if night > .5: d.ellipse((600, 360, 640, 400), fill=(250, 240, 200)); d.ellipse((612, 352, 650, 392), fill=wc)
    for k in range(5): d.pieslice((450 + k * 46, 300, 500 + k * 46, 370), 0, 180, fill=RED if k % 2 == 0 else (255, 255, 255))
    d.rectangle((440, 300, 680, 316), fill=RED)
    return im
def table(im, y=900, col=WOOD):
    d = BD(im); d.rectangle((0, y, W, H), fill=col); d.rectangle((0, y, W, y + 14), fill=mix(col, (255, 255, 255), .2))
    for k in range(8): d.line((0, y + 50 + k * 44, W, y + 60 + k * 40), fill=mix(col, (0, 0, 0), .18), width=3)
BGK = kitchen_bg(); table(BGK)

def scribble(d, x, y, w, n, col=INK, seed=1, gap=26, wid=3):
    r = random.Random(seed)
    for k in range(n):
        ww = w * (.55 + r.random() * .45); pts = []
        for j in range(30):
            q = j / 29; pts.append((x + q * ww, y + k * gap + math.sin(q * 26 + k + seed) * 3))
        d.line(pts, fill=col, width=wid)

def notebook(im, cx, cy, s, opn=1.0, flip=0.0, title='Receta Nº 7', glow=0):
    """Libreta de la abuela: tapa café de cuero (cerrada) o abierta con recetas escritas a mano."""
    if glow: im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx - 330 * s, cy - 230 * s, cx + 330 * s, cy + 230 * s), fill=255), GOLD, 50, int(200 * glow)))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    w, h = 250 * s, 300 * s
    if opn < .5:
        k = 1 - opn * 2; cw = w * max(.08, k)
        d.rounded_rectangle((cx - w / 2 + 12 * s, cy - h / 2 + 16 * s, cx + w / 2 + 12 * s, cy + h / 2 + 16 * s), 16 * s, fill=(0, 0, 0, 90))
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 14 * s, fill=(246, 240, 226))
        d.rounded_rectangle((cx - w / 2, cy - h / 2, cx - w / 2 + cw, cy + h / 2), 14 * s, fill=(122, 62, 40), outline=(90, 44, 28), width=max(1, int(4 * s)))
        if k > .6:
            d.rounded_rectangle((cx - 80 * s, cy - 50 * s, cx + 80 * s, cy + 30 * s), 8 * s, fill=(240, 226, 196))
            d.text((cx, cy - 22 * s), 'Recetas', font=F('Inter-SemiBoldItalic.otf', int(30 * s)), fill=INK, anchor='mm')
            d.text((cx, cy + 10 * s), 'de Rosa', font=F('Inter-SemiBoldItalic.otf', int(24 * s)), fill=INK, anchor='mm')
            d.rectangle((cx + w / 2 - 40 * s, cy - h / 2, cx + w / 2 - 28 * s, cy + h / 2 + 30 * s), fill=RED)  # cinta
    else:
        W2 = w * 2 * (0.6 + 0.4 * ease((opn - .5) * 2))
        d.rounded_rectangle((cx - W2 / 2 + 12 * s, cy - h / 2 + 16 * s, cx + W2 / 2 + 12 * s, cy + h / 2 + 16 * s), 16 * s, fill=(0, 0, 0, 90))
        d.rounded_rectangle((cx - W2 / 2 - 8 * s, cy - h / 2 - 8 * s, cx + W2 / 2 + 8 * s, cy + h / 2 + 8 * s), 16 * s, fill=(122, 62, 40))
        d.rectangle((cx - W2 / 2, cy - h / 2, cx + W2 / 2, cy + h / 2), fill=(250, 244, 228))
        d.line((cx, cy - h / 2, cx, cy + h / 2), fill=(200, 186, 160), width=max(1, int(4 * s)))
        d.text((cx - W2 / 4, cy - h / 2 + 40 * s), title, font=F('Inter-SemiBoldItalic.otf', int(26 * s)), fill=RED, anchor='mm')
        scribble(d, cx - W2 / 2 + 24 * s, cy - h / 2 + 80 * s, W2 / 2 - 50 * s, 7, seed=3, gap=26 * s, wid=max(1, int(3 * s)))
        scribble(d, cx + 24 * s, cy - h / 2 + 40 * s, W2 / 2 - 50 * s, 9, seed=7, gap=26 * s, wid=max(1, int(3 * s)))
        if flip > 0 and flip < 1:   # hoja que pasa
            x = cx + (W2 / 2) * math.cos(math.pi * flip)
            d.polygon([(cx, cy - h / 2), (x, cy - h / 2 - 20 * s * math.sin(math.pi * flip)), (x, cy + h / 2 - 10 * s * math.sin(math.pi * flip)), (cx, cy + h / 2)], fill=(238, 230, 210), outline=(200, 186, 160))
    im.alpha_composite(L)
    return (cx - w if opn >= .5 else cx - w / 2, cy - h / 2, cx + w if opn >= .5 else cx + w / 2, cy + h / 2)

def cocada(d, x, y, r, seed=0):
    rr = random.Random(seed)
    d.ellipse((x - r + 3, y - r * .55 + 6, x + r + 3, y + r * .55 + 6), fill=(120, 80, 50, 120))
    d.ellipse((x - r, y - r * .6, x + r, y + r * .6), fill=(214, 168, 108))
    d.ellipse((x - r * .9, y - r * .65, x + r * .9, y + r * .35), fill=(244, 226, 190))
    for k in range(int(r * .8)):
        a = rr.random() * 6.28; q = rr.random() ** .5
        px, py = x + math.cos(a) * q * r * .8, y - r * .15 + math.sin(a) * q * r * .4
        d.line((px, py, px + rr.uniform(-5, 5), py + rr.uniform(-2, 2)), fill=(226, 196, 150), width=2)
def tray(im, cx, cy, s=1.0, n=7):
    d = BD(im); w = 260 * s
    d.ellipse((cx - w / 2 + 8, cy - 46 * s + 14, cx + w / 2 + 8, cy + 46 * s + 14), fill=(0, 0, 0, 70))
    d.ellipse((cx - w / 2, cy - 46 * s, cx + w / 2, cy + 46 * s), fill=(235, 235, 240), outline=(200, 200, 210), width=4)
    pos = [(-80, -8), (-28, -14), (24, -14), (76, -8), (-54, 14), (0, 16), (54, 14)][:n]
    for k, (px, py) in enumerate(sorted(pos, key=lambda p: p[1])): cocada(d, cx + px * s, cy + py * s - 10 * s, 30 * s, k)
    return (cx - w / 2, cy - 60 * s, cx + w / 2, cy + 50 * s)

def figure(d, x, y, s, shirt, skin=(226, 180, 140), hair=(50, 36, 30), long=False, bob=0):
    y += bob
    d.rounded_rectangle((x - 9 * s, y + 70 * s, x - 2 * s, y + 130 * s), 3 * s, fill=(40, 40, 50)); d.rounded_rectangle((x + 2 * s, y + 70 * s, x + 9 * s, y + 130 * s), 3 * s, fill=(40, 40, 50))
    d.rounded_rectangle((x - 22 * s, y + 10 * s, x + 22 * s, y + 80 * s), 14 * s, fill=shirt)
    if long: d.rounded_rectangle((x - 20 * s, y - 34 * s, x + 20 * s, y + 20 * s), 12 * s, fill=hair)
    d.ellipse((x - 17 * s, y - 30 * s, x + 17 * s, y + 6 * s), fill=skin)
    d.chord((x - 18 * s, y - 34 * s, x + 18 * s, y - 2 * s), 180, 360, fill=hair)
    d.ellipse((x - 8 * s, y - 14 * s, x - 4 * s, y - 10 * s), fill=(30, 30, 30)); d.ellipse((x + 4 * s, y - 14 * s, x + 8 * s, y - 10 * s), fill=(30, 30, 30))

def face(size, style):
    L = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(L); s = size / 300
    if style == 'vale':
        bgc, skin, hair, shirt = (255, 226, 214), (204, 152, 116), (40, 26, 22), (230, 38, 47)
    else:
        bgc, skin, hair, shirt = (236, 226, 206), (226, 186, 150), (205, 205, 210), (120, 150, 120)
    d.rectangle((0, 0, size, size), fill=bgc)
    if style == 'vale': d.rounded_rectangle((70 * s, 70 * s, 230 * s, 280 * s), 60 * s, fill=hair)
    d.rounded_rectangle((60 * s, 220 * s, 240 * s, 340 * s), 60 * s, fill=shirt)
    d.rectangle((130 * s, 196 * s, 170 * s, 236 * s), fill=mix(skin, (0, 0, 0), .1))
    d.ellipse((86 * s, 66 * s, 214 * s, 214 * s), fill=skin)
    if style == 'vale':
        d.chord((80 * s, 52 * s, 220 * s, 170 * s), 180, 360, fill=hair); d.pieslice((70 * s, 50 * s, 190 * s, 150 * s), 90, 200, fill=hair)
        d.ellipse((84 * s, 150 * s, 96 * s, 162 * s), fill=GOLD); d.ellipse((204 * s, 150 * s, 216 * s, 162 * s), fill=GOLD)
    else:
        d.ellipse((120 * s, 26 * s, 180 * s, 80 * s), fill=hair); d.chord((82 * s, 56 * s, 218 * s, 160 * s), 180, 360, fill=hair)
        for ex in (122, 178): d.ellipse(((ex - 22) * s, 120 * s, (ex + 22) * s, 156 * s), outline=(80, 60, 50), width=max(1, int(4 * s)))
        d.line((144 * s, 138 * s, 156 * s, 138 * s), fill=(80, 60, 50), width=max(1, int(4 * s)))
    for ex in (122, 178): d.ellipse(((ex - 6) * s, 132 * s, (ex + 6) * s, 144 * s), fill=(36, 28, 26))
    d.arc((122 * s, 160 * s, 178 * s, 194 * s), 20, 160, fill=(150, 60, 60), width=max(1, int(5 * s)))
    d.ellipse((96 * s, 160 * s, 116 * s, 172 * s), fill=mix(skin, RED, .25)); d.ellipse((184 * s, 160 * s, 204 * s, 172 * s), fill=mix(skin, RED, .25))
    return L
FACE_V = face(300, 'vale'); FACE_R = face(300, 'rosa')
def polaroid(im, cx, cy, w, ang, label, fc):
    h = int(w * 1.2); L = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((10, 14, w + 14, h + 18), fill=(0, 0, 0, 90)); d.rectangle((0, 0, w, h), fill=(250, 248, 240))
    L.alpha_composite(fc.resize((w - 30, w - 30), Image.LANCZOS), (15, 15))
    d.text((w / 2, w + (h - w) / 2 - 6), label, font=F('Inter-SemiBoldItalic.otf', int(w / 8)), fill=(50, 50, 60), anchor='mm')
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
    return (cx - L.width / 2, cy - L.height / 2, cx + L.width / 2, cy + L.height / 2)

def chip(im, cx, cy, txt, q, col=RED, tcol=WHITE, size=28):
    if q <= 0: return
    b = back_out(q / .35); f = F('Inter-Black.otf', size); d = BD(im); tw = d.textlength(txt, font=f)
    w, h = (tw + 44) * b, (size + 26) * b
    d.rounded_rectangle((cx - w / 2 + 4, cy - h / 2 + 6, cx + w / 2 + 4, cy + h / 2 + 6), h / 2, fill=(0, 0, 0, 60))
    d.rounded_rectangle((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), h / 2, fill=col)
    if b > .6: d.text((cx, cy), txt, font=f, fill=tcol, anchor='mm')

def card(im, r, fill=(255, 255, 255), rad=24, shadow=True):
    d = BD(im)
    if shadow:
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((r[0] + 8, r[1] + 16, r[2] + 8, r[3] + 16), rad, fill=(0, 0, 0, 80))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
    d.rounded_rectangle(r, rad, fill=fill)

def chat_icon(d, cx, cy, r, col=(255, 255, 255)):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=col, width=max(2, int(r / 5)))
    d.polygon([(cx - r * .7, cy + r * .5), (cx - r * 1.05, cy + r * 1.05), (cx - r * .2, cy + r * .9)], fill=col)

def sparkles(im, cx, cy, t, n=22, rad=260, col=GOLD, seed=2):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(L); rr = random.Random(seed)
    for k in range(n):
        ph = rr.random(); sp = .25 + rr.random() * .3; q = (t * sp + ph) % 1
        x = cx + rr.uniform(-rad, rad); y = cy + 120 - q * 380; r = 3 + rr.random() * 5
        a = int(255 * math.sin(math.pi * q)); d.ellipse((x - r, y - r, x + r, y + r), fill=col + (a,))
    im.alpha_composite(L)

# ---------- escenas ----------
def sc0(t, lt):
    im = BGK.copy()
    z = lerp(1.25, 1.0, ease(lt / 3.6))
    polaroid(im, 140, 700, 170, 7, 'Rosa', FACE_R)
    o = ease((t - wt(0, 'libreta') + .1) / .6)
    nb = notebook(im, 400, 760, .82, opn=o)
    q = t - wt(0, '40')
    if q > 0:
        n = min(40, int(40 * ease(q / .8))); d = BD(im)
        chip(im, 560, 560, f'{n} RECETAS', q, size=26)
    q = t - wt(0, 'nunca')
    if q > 0: stamp(im, 400, 1010, ['SOLO EN SU COCINA'], RED, q, ang=-5, size=36)
    im = camera(im, z, 400, 760)
    obj('in', (50, 520, 670, 900)); obj('out', nb); return im

def sc1(t, lt):
    im = BGK.copy(); d = BD(im)
    # guirnalda de diciembre
    for k in range(13):
        x = 20 + k * 56; y = 330 + 18 * math.sin(k * .9)
        on = (int(t * 4) + k) % 3 != 0
        d.line((x, y, x + 56, 330 + 18 * math.sin((k + 1) * .9)), fill=(60, 90, 60), width=3)
        col = [RED, GOLD, (90, 180, 120)][k % 3]
        if on: im.alpha_composite(glow_layer(lambda dd: dd.ellipse((x - 14, y - 4, x + 14, y + 24), fill=255), col, 10, 160))
        d.ellipse((x - 8, y + 2, x + 8, y + 20), fill=col if on else mix(col, (0, 0, 0), .4))
    chip(im, 360, 420, 'DICIEMBRE', lt, col=(36, 36, 40), size=30)
    tr = tray(im, 150, 870, .95)
    cols = [(70, 110, 170), (230, 120, 60), (120, 80, 160), RED, (60, 150, 120), (200, 170, 60), (90, 90, 100)]
    for k in range(7):
        q = ease((lt - .2 - k * .18) / .6); x = lerp(W + 80, 300 + k * 66, q)
        figure(d, x, 640 + (k % 2) * 6, 1.25 if k % 3 else 1.1, cols[k], long=k % 2 == 1, bob=-abs(math.sin(t * 9 + k)) * 6 * (1 - q))
    q = t - wt(1, 'fila')
    if q > 0: chip(im, 520, 560, 'FILA', q, col=WHITE, tcol=RED, size=26)
    pq = ease((t - wt(1, 'cocadas') + .2) / .7)
    im = camera(im, 1.0 + .45 * pq, lerp(360, 160, pq), lerp(700, 860, pq))
    obj('in', (50, 500, 670, 900)); obj('out', tr); return im

def sc2(t, lt):
    dark = ease((t - wt(2, 'cajón') + .1) / .8)
    im = kitchen_bg(night=.25 + .2 * dark); table(im, 1060, (110, 74, 48)); d = BD(im)
    # mueble con cajón
    d.rectangle((110, 600, 610, 1060), fill=(170, 118, 76), outline=(120, 80, 50), width=6)
    d.rectangle((140, 820, 580, 1030), fill=(156, 106, 66), outline=(120, 80, 50), width=4)
    cl = ease((t - wt(2, 'libreta') + .1) / 1.2)      # cajón cerrándose
    dy = lerp(150, 0, cl)
    d.polygon([(150, 640 - dy * .2), (570, 640 - dy * .2), (590, 680 + dy * .1), (130, 680 + dy * .1)], fill=(90, 58, 36))
    if cl < .95:
        nb = Image.new('RGBA', (W, H), (0, 0, 0, 0)); notebook(nb, 360, 640, .45, opn=0)
        nb = nb.crop((0, 0, W, int(690 + dy * .1))); im.alpha_composite(nb)
    d.rectangle((140, 640 + dy * .4, 580, 800 + dy * .4), fill=(186, 130, 86), outline=(120, 80, 50), width=5)
    d.rounded_rectangle((320, 700 + dy * .4, 400, 728 + dy * .4), 10, fill=(90, 60, 40))
    if cl > .9:   # polvo
        rr = random.Random(4); Ld = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dd2 = ImageDraw.Draw(Ld)
        for k in range(30):
            q = (lt * .15 + rr.random()) % 1; x = 130 + rr.random() * 460; y = 600 - q * 300
            dd2.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(255, 240, 210, int(160 * math.sin(math.pi * q))))
        im.alpha_composite(Ld)
    ov = Image.new('RGBA', (W, H), (10, 10, 20, int(120 * dark))); im.alpha_composite(ov)
    im = camera(im, 1.0 + .2 * ease(lt / 3), 360, 760)
    obj('in', (130, 600, 590, 830)); obj('out', (140, 640, 580, 800)); return im

def sc3(t, lt):
    im = BGK.copy(); d = BD(im)
    pr = polaroid(im, 330, 690, 330, -4, 'Valentina', FACE_V)
    chip(im, 560, 470, '19 AÑOS', t - wt(3, '19'), col=(36, 36, 40))
    chip(im, 545, 900, 'SIN TRABAJO', t - wt(3, 'ningún'))
    q = t - wt(3, 'libreta')
    if q > 0:
        nbl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); notebook(nbl, 560, 1060, .45, opn=0, glow=.6)
        b = back_out(q / .4); nbl = nbl.resize((int(W * b), int(H * b))); im.alpha_composite(nbl, (int(560 - 560 * b), int(1060 - 1060 * b)))
    im = camera(im, 1.0 + .08 * ease(lt / 4), 360, 700)
    obj('in', pr); obj('out', pr); return im

def sc4(t, lt):
    im = kitchen_bg(night=1.0); table(im, 960, (96, 64, 44)); d = BD(im)
    # tarjeta de receta
    card(im, (150, 360, 570, 640), (250, 244, 228), 18)
    d.text((360, 410), 'Receta Nº 7', font=F('Inter-SemiBoldItalic.otf', 40), fill=RED, anchor='mm')
    d.text((360, 460), 'Cocadas de la abuela', font=F('Inter-SemiBoldItalic.otf', 28), fill=INK, anchor='mm')
    scribble(d, 190, 510, 340, 4, seed=11, gap=30)
    # olla con vapor
    d.ellipse((190, 900, 450, 960), fill=(60, 60, 70)); d.rectangle((200, 820, 440, 930), fill=(170, 170, 180)); d.ellipse((200, 800, 440, 840), fill=(200, 200, 210))
    d.rectangle((170, 840, 200, 856), fill=(80, 80, 90)); d.rectangle((440, 840, 470, 856), fill=(80, 80, 90))
    St = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(St)
    for k in range(4):
        q = (lt * .5 + k / 4) % 1; x = 260 + k * 40 + math.sin(lt * 3 + k) * 12; y = 790 - q * 160
        sd.ellipse((x - 18 * (1 + q), y - 18 * (1 + q), x + 18 * (1 + q), y + 18 * (1 + q)), fill=(255, 255, 255, int(110 * math.sin(math.pi * q))))
    im.alpha_composite(St.filter(ImageFilter.GaussianBlur(6)))
    q = t - wt(4, 'igualitas')
    pl = (420, 830, 680, 940)
    if q > -.3:
        a = ease((q + .3) / .4); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); tray(L, 550, 900, .95)
        L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L)
    if q > 0:
        im.alpha_composite(glow_layer(lambda dd: dd.ellipse((420, 820, 680, 980), fill=255), GOLD, 40, int(140 * ease(q / .5))))
        stamp(im, 520, 720, ['¡IGUALITAS!'], RED, q, ang=-7, size=46)
    pq = ease((t - wt(4, 'quedaron') + .2) / .8)
    im = camera(im, 1.0 + .25 * pq, lerp(360, 520, pq), lerp(560, 850, pq))
    obj('in', (150, 360, 570, 640)); obj('out', pl); return im

def portada(d, im, cx, cy, w, h, t):
    """Pantalla del celular: portada de 'Dulces de la Abuela Rosa'."""
    x0, y0 = cx - w / 2 + 14, cy - h / 2 + 60
    q = ease((t - wt(5, 'foto') + .1) / .4)
    if q > 0:
        ph = Image.new('RGBA', (int(w - 28), 200), (250, 230, 200, 255)); pd = ImageDraw.Draw(ph); tray(ph, ph.width / 2, 130, .9)
        ph.putalpha(int(255 * q)); im.alpha_composite(ph, (int(x0), int(y0)))
    q = ease((t - wt(5, 'nombre')) / .4)
    if q > 0:
        d.ellipse((cx - 44, y0 + 160, cx + 44, y0 + 248), fill=(255, 255, 255), outline=RED, width=5)
        im.alpha_composite(FACE_R.resize((74, 74)), (int(cx - 37), int(y0 + 167)))
        mask_text(im, (cx, y0 + 285), 'Dulces de la', F('Inter-Black.otf', 30), WHITE, q)
        mask_text(im, (cx, y0 + 322), 'Abuela Rosa', F('Inter-Black.otf', 34), (255, 196, 120), q)
    q = t - wt(5, 'dulces')
    for k, nm in enumerate(['Cocadas', 'Arequipe', 'Panelitas']):
        b = back_out((q - k * .12) / .35)
        if b > 0:
            yy = y0 + 370 + k * 52; d.rounded_rectangle((cx - 120 * b, yy, cx + 120 * b, yy + 42), 12, fill=(34, 36, 48))
            if b > .6: d.text((cx - 100, yy + 21), nm, font=F('Inter-Bold.otf', 22), fill='white', anchor='lm'); d.text((cx + 100, yy + 21), '›', font=F('Inter-Bold.otf', 26), fill=(150, 150, 160), anchor='rm')
    q = t - wt(5, 'botón')
    b = back_out(q / .35)
    if b > 0:
        yy = y0 + 540; gl = 1 + .05 * math.sin(t * 8) if t > wt(5, 'whatsapp') else 1
        d.rounded_rectangle((cx - 125 * b * gl, yy - 30 * b * gl, cx + 125 * b * gl, yy + 30 * b * gl), 30, fill=(37, 190, 100))
        if b > .6: chat_icon(d, cx - 88, yy, 13); d.text((cx + 14, yy), 'Hacer pedido', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, W / 2, 760, 1.25, None)
    im.alpha_composite(L); d = BD(im)
    portada(d, im, W / 2, 760, 375, 750, t)
    q = t - wt(5, 'foto')
    if 0 < q < .35: im.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(230 * (1 - q / .35)))))
    q = t - wt(5, 'gratis')
    if q > 0: stamp(im, 590, 470, ['GRATIS'], RED, q, ang=10, size=44)
    zq = ease((t - wt(5, 'whatsapp') + .3) / .6)
    im = camera(im, 1.0 + .35 * zq, W / 2, lerp(760, 1060, zq))
    obj('in', (200, 440, 520, 640)); obj('out', (172, 385, 548, 1135)); return im

def sc6(t, lt):
    im = gradient((246, 244, 240), (226, 222, 216)); d = BD(im)
    q = ease(lt / .4)
    r1 = (60, 360 + (1 - q) * 40, 420, 760 + (1 - q) * 40); card(im, r1)
    d.rounded_rectangle((r1[0], r1[1], r1[2], r1[1] + 56), 24, fill=(20, 20, 24)); d.rectangle((r1[0], r1[1] + 30, r1[2], r1[1] + 56), fill=(20, 20, 24))
    d.text((r1[0] + 24, r1[1] + 30), 'MARKETPLACE', font=F('Inter-Black.otf', 22), fill='white', anchor='lm')
    ph = Image.new('RGBA', (320, 200), (250, 230, 200, 255)); tray(ph, 160, 120, .9); im.alpha_composite(ph, (int(r1[0] + 20), int(r1[1] + 70)))
    d.text((r1[0] + 22, r1[1] + 300), 'Cocadas de la abuela', font=F('Inter-Black.otf', 26), fill=(30, 30, 36))
    d.text((r1[0] + 22, r1[1] + 336), 'Hechas a mano · Receta Nº 7', font=F('Inter-Medium.otf', 20), fill=(110, 110, 120))
    chip(im, r1[2] - 60, r1[1] + 90, 'NUEVO', t - wt(6, 'marketplace'), size=20)
    q = t - wt(6, 'inteligencia')
    r2 = (250, 700, 670, 1130)
    if q > -.2:
        a = ease((q + .2) / .45); oy = (1 - a) * 120
        r2 = (r2[0], r2[1] + oy, r2[2], r2[3] + oy); card(im, r2, (22, 22, 28))
        nbl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); notebook(nbl, 460, 860 + oy, .48, opn=1, title='Nº 7'); im.alpha_composite(nbl)
        cx, cy = 460, 860 + oy; im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx - 44, cy - 44, cx + 44, cy + 44), fill=255), (0, 0, 0), 20, 120))
        d.ellipse((cx - 38, cy - 38, cx + 38, cy + 38), fill=(255, 255, 255, 230)); d.polygon([(cx - 12, cy - 20), (cx - 12, cy + 20), (cx + 22, cy)], fill=RED)
        waveform(im, r2[0] + 30, r2[3] - 120, 360, 50, t, prog=((t - wt(6, 'inteligencia')) / 4) % 1)
        d.rounded_rectangle((r2[0] + 30, r2[3] - 72, r2[0] + 220, r2[3] - 30), 20, fill=RED); d.text((r2[0] + 125, r2[3] - 51), 'HECHO CON IA', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
        d.text((r2[2] - 30, r2[3] - 51), 'La libreta', font=F('Inter-Bold.otf', 22), fill=(190, 190, 200), anchor='rm')
    pq = ease((t - wt(6, 'inteligencia') + .1) / .8)
    im = camera(im, 1.0 + .15 * pq, lerp(300, 460, pq), lerp(600, 900, pq))
    obj('in', r1); obj('out', r2); return im

def sc7(t, lt):
    im = gradient((236, 240, 236), (210, 220, 214)); d = BD(im)
    # mapa simple con calles
    for k in range(9): d.line((0, 330 + k * 110, W, 300 + k * 110), fill=(255, 255, 255), width=14)
    for k in range(6): d.line((60 + k * 140, 300, 20 + k * 140, H), fill=(255, 255, 255), width=14)
    home = (360, 780)
    d.ellipse((home[0] - 40, home[1] - 40, home[0] + 40, home[1] + 40), fill=RED); d.polygon([(home[0] - 20, home[1] + 4), (home[0], home[1] - 18), (home[0] + 20, home[1] + 4)], fill='white'); d.rectangle((home[0] - 14, home[1] + 4, home[0] + 14, home[1] + 22), fill='white')
    pins = [('primer', (250, 690), 'Vecina Marta', 'Quiero 6 cocadas'), ('segundo', (600, 400), 'Número nuevo', '¿Hacen envíos?')]
    last = None
    for k, (w_, p, who, msg) in enumerate(pins):
        q = t - wt(7, w_)
        if q > 0:
            prog = ease(q / .7); x = lerp(home[0], p[0], prog); y = lerp(home[1], p[1], prog)
            d.line((home[0], home[1], x, y), fill=RED, width=5)
            b = back_out((q - .5) / .35)
            if b > 0:
                d.ellipse((p[0] - 22 * b, p[1] - 22 * b, p[0] + 22 * b, p[1] + 22 * b), fill=(36, 36, 40))
                bx, by = (40, 470) if k == 0 else (240, 990)
                card(im, (bx, by, bx + 440, by + 120), (255, 255, 255), 20); d = BD(im)
                d.ellipse((bx + 20, by + 26, bx + 88, by + 94), fill=(37, 190, 100)); chat_icon(d, bx + 54, by + 58, 16)
                d.text((bx + 106, by + 40), 'Nuevo pedido · ' + who, font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm')
                mask_text(im, (bx + 106 + d.textlength(msg, font=F('Inter-Medium.otf', 24)) / 2, by + 82), msg, F('Inter-Medium.otf', 24), (90, 90, 100), (q - .5) / .4)
                last = (bx, by, bx + 440, by + 120)
    fq = ease((t - wt(7, 'segundo')) / .9)
    im = camera(im, 1.12, lerp(300, 440, fq), lerp(620, 900, fq))
    obj('in', (320, 740, 400, 820)); obj('out', last or (240, 990, 680, 1110)); return im

def sc8(t, lt):
    im = BGK.copy(); d = BD(im)
    # cafetería
    card(im, (60, 360, 660, 700), (250, 246, 238), 20)
    for k in range(10): d.pieslice((60 + k * 60, 340, 120 + k * 60, 420), 0, 180, fill=RED if k % 2 == 0 else (255, 255, 255))
    d.rectangle((60, 340, 660, 362), fill=RED)
    d.text((360, 450), 'CAFÉ LUNA', font=F('Inter-Black.otf', 44), fill=(36, 36, 40), anchor='mm')
    d.rectangle((110, 500, 330, 680), fill=(180, 220, 235)); d.rectangle((390, 500, 610, 680), fill=(120, 80, 50))
    d.ellipse((560, 580, 576, 596), fill=GOLD)
    for k in range(3): cocada(d, 160 + k * 60, 650, 22, k)
    chip(im, 600, 330, '3 SEMANAS', t - wt(8, '3'), col=(36, 36, 40), size=24)
    bubble(im, 70, 730, '¿Nos traes cocadas cada viernes?', t - wt(8, 'preguntó'), col=(36, 38, 48), size=28)
    # calendario
    q = t - wt(8, 'viernes') + .3
    r = (110, 870, 610, 1180)
    if q > 0:
        a = back_out(q / .4); cx, cy = 360, 1025; w, h = 500 * a, 310 * a; r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
        card(im, r, (255, 255, 255), 20); d = BD(im)
        if a > .7:
            d.rounded_rectangle((r[0], r[1], r[2], r[1] + 50), 20, fill=RED); d.rectangle((r[0], r[1] + 30, r[2], r[1] + 50), fill=RED)
            d.text((cx, r[1] + 26), 'CADA VIERNES', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
            for c, lab in enumerate('LMMJVSD'):
                x = r[0] + 40 + c * 70
                d.text((x, r[1] + 76), lab, font=F('Inter-Bold.otf', 20), fill=RED if c == 4 else (120, 120, 130), anchor='mm')
                for rw in range(3):
                    y = r[1] + 120 + rw * 60; d.text((x, y), str(rw * 7 + c + 2), font=F('Inter-Medium.otf', 20), fill=(60, 60, 66), anchor='mm')
                    if c == 4 and q - .4 - rw * .25 > 0: d.ellipse((x - 24, y - 24, x + 24, y + 24), outline=RED, width=5)
    pq = ease((t - wt(8, 'viernes') + .3) / .8)
    im = camera(im, 1.0 + .12 * pq, 360, lerp(640, 960, pq))
    obj('in', (60, 340, 660, 700)); obj('out', r); return im

def sc9(t, lt):
    im = kitchen_bg(); table(im); d = BD(im)
    glow = ease((t - wt(9, 'ver') + .4) / .8)
    im.alpha_composite(Image.new('RGBA', (W, H), (20, 14, 10, int(150 * (1 - glow)))))
    nb = notebook(im, 360, 780, .95, opn=1, title='Receta Nº 7', glow=.35 + .65 * glow)
    sparkles(im, 360, 700, t, n=30, rad=280)
    q = t - wt(9, 'cambió', 1)
    if q > 0:
        for k in range(5):   # siluetas que se acercan a mirar
            a = ease((q - k * .15) / .6); x = [120, 230, 490, 600, 360][k]; y = 1010 if k < 4 else 1050
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), x, y + (1 - a) * 60, 1.4, [(70, 110, 170), (230, 120, 60), (120, 80, 160), RED, (60, 150, 120)][k], long=k % 2 == 0)
            L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L)
    im = camera(im, 1.0 + .12 * ease(lt / 4.5), 360, 780)
    obj('in', nb); obj('out', nb); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90))
    # caja que se abre con luz
    o = ease((t - wt(10, 'guardado') + .1) / .6)
    cx, cy = 360, 560
    if o > 0: im.alpha_composite(glow_layer(lambda dd: dd.polygon([(cx - 120, cy - 40), (cx + 120, cy - 40), (cx + 260, cy - 340), (cx - 260, cy - 340)], fill=255), GOLD, 40, int(170 * o)))
    d.rectangle((cx - 140, cy - 40, cx + 140, cy + 110), fill=(170, 118, 76), outline=(120, 80, 50), width=5)
    lid = -o * 70; d.polygon([(cx - 150, cy - 40), (cx + 150, cy - 40), (cx + 150 + lid * .3, cy - 80 + lid), (cx - 150 - lid * .3, cy - 80 + lid)], fill=(190, 136, 90), outline=(120, 80, 50))
    ks = [('Tu portada', 'portada', True), ('Marketplace', 'publicar', True), ('Videos con IA', 'gratis', False)]
    r0 = None
    for k, (ti, wd, free) in enumerate(ks):
        q = t - wt(10, wd) + .15 - (k == 2) * 0 + (.4 if k == 2 else 0)
        a = back_out(q / .4)
        if a <= 0: continue
        x = 130 + k * 230; y = 860; w, h = 200 * a, 230 * a; r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        if k == 0: r0 = r
        card(im, r, (250, 250, 250), 22); d = BD(im)
        if a > .7:
            if k == 0:
                d.rounded_rectangle((x - 50, y - 90, x + 50, y + 20), 14, fill=(36, 36, 40)); d.ellipse((x - 20, y - 76, x + 20, y - 36), fill=RED); d.rounded_rectangle((x - 36, y - 20, x + 36, y + 2), 8, fill=(37, 190, 100))
            elif k == 1:
                d.rectangle((x - 60, y - 50, x + 60, y + 20), fill=(70, 74, 90)); d.rectangle((x - 70, y - 80, x + 70, y - 52), fill=RED); d.rectangle((x - 18, y - 20, x + 18, y + 20), fill=GOLD)
            else:
                d.rounded_rectangle((x - 64, y - 76, x + 64, y + 10), 22, fill=RED); d.polygon([(x - 16, y - 54), (x - 16, y - 10), (x + 22, y - 32)], fill='white')
            d.text((x, y + 70), ti, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
            if free: chip(im, x, y - 120, 'GRATIS', q - .2, size=20)
    im = camera(im, 1.0, 360, 640)
    obj('in', (220, 440, 500, 680)); obj('out', r0 or (30, 745, 230, 975)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110))
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26)))
    mask_text(im, (W / 2, y + 160), 'Tu portada, tu Marketplace', F('Inter-Black.otf', 30), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 200), 'y videos con IA', F('Inter-Black.otf', 30), (30, 30, 36), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'PRUÉBALO', t - wt(11, 'pruébalo'), size=22)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5)
    im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob)))
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'historia')
    if q > -.3:
        mask_text(im, (W / 2, 760), '…ya es tu historia.', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
    CAM.update(x0=0, y0=0, z=1); obj('in', (60, 330, 660, 630)); obj('out', (60, 330, 660, 630))
    return im

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
        d = BD(im); yo = (1 - a) * 30
        mask_text(im, (W // 2, 800), 'Tu historia empieza aquí', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8, sc9, sc10, sc11]
LOGO_RECT = (50, 500, 670, 700)
TR = 0.32
ST = [c['t0'] - 0.15 for c in CL] + [LOGO_T]
def scene_at(i, t):
    OBJ.clear(); CAM.update(x0=0, y0=0, z=1)
    if i == 12:
        im = end_scene(max(0, t - LOGO_T), t); OBJ['in'] = LOGO_RECT; return im, dict(OBJ)
    im = SC[i](t, max(0, t - ST[i])); return im, dict(OBJ)
NOMORPH = set()
def frame(f):
    t = f / FPS
    i = 0
    for k, s0 in enumerate(ST):
        if t >= s0: i = k
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
        if i < 12: im.alpha_composite(VIG)
        if t < ST[10]:   # aviso: historia ilustrativa
            ImageDraw.Draw(im).text((W - 24, H - 30), 'Historia ilustrativa', font=F('Inter-SemiBold.otf', 20), fill=(255, 255, 255, 150), anchor='rm')
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
