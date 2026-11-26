"""Día 40 — "Las clases de las 10 de la noche" (historia: Andrea aprende en la comunidad Gana con Marketing de Sumiago y deja de adivinar).
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
KEY = {'ropa', 'trabaja…', 'trabaja', 'estudia', 'universidad', 'celular', '10', 'dormidos', 'público', 'objetivo', 'nadie', 'gana', 'marketing', 'sumiago', 'inteligencia', 'artificial',
       'clase', 'fotos', 'descripciones', 'ella', 'minutos', 'nada', 'tercera', 'experta', 'adivinar', 'tiempo', 'ciegas', 'vendes', 'link', 'noche'}
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


INK = (60, 44, 36)
def figure(d, x, y, s, shirt, skin=(226, 180, 140), hair=(50, 36, 30), long=False, bob=0):
    y += bob
    d.rounded_rectangle((x - 9 * s, y + 70 * s, x - 2 * s, y + 130 * s), 3 * s, fill=(40, 40, 50)); d.rounded_rectangle((x + 2 * s, y + 70 * s, x + 9 * s, y + 130 * s), 3 * s, fill=(40, 40, 50))
    d.rounded_rectangle((x - 22 * s, y + 10 * s, x + 22 * s, y + 80 * s), 14 * s, fill=shirt)
    if long: d.rounded_rectangle((x - 20 * s, y - 34 * s, x + 20 * s, y + 20 * s), 12 * s, fill=hair)
    d.ellipse((x - 17 * s, y - 30 * s, x + 17 * s, y + 6 * s), fill=skin)
    d.chord((x - 18 * s, y - 34 * s, x + 18 * s, y - 2 * s), 180, 360, fill=hair)
    d.ellipse((x - 8 * s, y - 14 * s, x - 4 * s, y - 10 * s), fill=(30, 30, 30)); d.ellipse((x + 4 * s, y - 14 * s, x + 8 * s, y - 10 * s), fill=(30, 30, 30))

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
        mask_text(im, (W // 2, 800), 'Deja de adivinar', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
NIGHT = ((22, 26, 52), (10, 12, 26))
# ---------- objetos ----------
def andrea(d, x, y, s, bob=0): figure(d, x, y, s, (220, 90, 130), skin=(196, 140, 104), hair=(36, 24, 20), long=True, bob=bob)
def moon(d, cx, cy, r, bg):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(250, 240, 200)); d.ellipse((cx - r * .4, cy - r * 1.1, cx + r * 1.4, cy + r * .7), fill=bg)
def sun(im, cx, cy, r):
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx - r * 1.8, cy - r * 1.8, cx + r * 1.8, cy + r * 1.8), fill=255), (255, 200, 80), 30, 180))
    BD(im).ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 206, 80))
def shirt(d, cx, cy, s, col):
    d.polygon([(cx - 60 * s, cy - 60 * s), (cx - 20 * s, cy - 76 * s), (cx + 20 * s, cy - 76 * s), (cx + 60 * s, cy - 60 * s), (cx + 90 * s, cy - 20 * s), (cx + 62 * s, cy), (cx + 50 * s, cy - 14 * s), (cx + 50 * s, cy + 80 * s), (cx - 50 * s, cy + 80 * s), (cx - 50 * s, cy - 14 * s), (cx - 62 * s, cy), (cx - 90 * s, cy - 20 * s)], fill=col)
    d.arc((cx - 20 * s, cy - 92 * s, cx + 20 * s, cy - 60 * s), 0, 180, fill=mix(col, (0, 0, 0), .3), width=max(2, int(5 * s)))
COURSES = [('Marketing para redes', .8), ('Fotos que venden', .5), ('IA para tu negocio', .3)]
def gcm_screen(im, r, t, q0, prog=1.0):
    card(im, r, (255, 255, 255), 26); d = BD(im)
    d.rounded_rectangle((r[0], r[1], r[2], r[1] + 110), 26, fill=RED); d.rectangle((r[0], r[1] + 60, r[2], r[1] + 110), fill=RED)
    d.text(((r[0] + r[2]) / 2, r[1] + 42), 'GANA CON MARKETING', font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
    d.text(((r[0] + r[2]) / 2, r[1] + 80), 'e Inteligencia Artificial', font=F('Inter-Bold.otf', 20), fill=(255, 220, 220), anchor='mm')
    for k, (nm, p) in enumerate(COURSES):
        a = ease((q0 - k * .2) / .4)
        if a <= 0: continue
        y = r[1] + 140 + k * 130 + (1 - a) * 30
        d.rounded_rectangle((r[0] + 24, y, r[2] - 24, y + 110), 18, fill=(244, 244, 247))
        d.rounded_rectangle((r[0] + 40, y + 16, r[0] + 140, y + 94), 12, fill=(36, 36, 40)); d.polygon([(r[0] + 80, y + 36), (r[0] + 80, y + 74), (r[0] + 108, y + 55)], fill='white')
        d.text((r[0] + 160, y + 38), nm, font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm')
        bw = (r[2] - r[0] - 210); d.rounded_rectangle((r[0] + 160, y + 66, r[0] + 160 + bw, y + 78), 6, fill=(220, 222, 230)); d.rounded_rectangle((r[0] + 160, y + 66, r[0] + 160 + bw * p * prog, y + 78), 6, fill=RED)

# ---------- escenas ----------
def sc0(t, lt):
    nq = ease((t - wt(0, 'noche') + .2) / .7)
    im = gradient(mix((190, 222, 246), NIGHT[0], nq), mix((240, 246, 252), NIGHT[1], nq)); d = BD(im)
    if nq < 1: L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sun(L, 560, lerp(420, 900, nq), 60); L.putalpha(L.getchannel('A').point(lambda p: int(p * (1 - nq)))); im.alpha_composite(L)
    if nq > 0:
        Lm = Image.new('RGBA', (W, H), (0, 0, 0, 0)); moon(ImageDraw.Draw(Lm), 560, 430, 50, mix((190, 222, 246), NIGHT[0], nq)); Lm.putalpha(Lm.getchannel('A').point(lambda p: int(p * nq))); im.alpha_composite(Lm)
    d = BD(im); d.rectangle((0, 960, W, H), fill=mix((214, 206, 196), (40, 40, 56), nq))
    # ropa colgada
    d.line((40, 600, 680, 600), fill=(120, 120, 130), width=4)
    for k, c in enumerate([RED, (60, 110, 200), (240, 190, 60), (90, 160, 120)]): shirt(d, 120 + k * 160, 690, .8, c)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); andrea(ImageDraw.Draw(L), 360, 830, 1.5); im.alpha_composite(L)
    chip(im, 200, 1150, 'DE DÍA TRABAJA', t - wt(0, 'trabaja'), col=(36, 36, 40), size=22)
    chip(im, 520, 1150, 'DE NOCHE ESTUDIA', t - wt(0, 'estudia'), size=22)
    obj('in', (260, 700, 460, 1100)); obj('out', (260, 700, 460, 1100)); return im

def sc1(t, lt):
    im = gradient(*NIGHT); d = BD(im)
    moon(d, 590, 420, 46, NIGHT[0])
    # cama con niños
    d.rounded_rectangle((60, 860, 400, 1000), 20, fill=(60, 80, 140)); d.rounded_rectangle((60, 820, 140, 880), 16, fill=(240, 240, 246)); d.ellipse((90, 820, 130, 860), fill=(196, 140, 104)); d.ellipse((150, 830, 190, 870), fill=(214, 166, 128))
    for k in range(3):
        q = (t * .5 + k / 3) % 1; d.text((200 + k * 30 + q * 40, 800 - q * 80), 'z', font=F('Inter-Black.otf', 30 + k * 6), fill=(200, 210, 255, int(255 * math.sin(math.pi * q))), anchor='mm')
    chip(im, 230, 1060, 'NIÑOS DORMIDOS', t - wt(1, 'dormidos'), col=(60, 80, 140), size=22)
    # Andrea con celular
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); andrea(ImageDraw.Draw(L), 540, 820, 1.6); im.alpha_composite(L)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((470, 780, 610, 900), fill=255), (180, 210, 255), 30, 150)); d = BD(im)
    d.rounded_rectangle((520, 830, 560, 890), 8, fill=(30, 30, 36)); d.rectangle((524, 836, 556, 884), fill=(200, 220, 255))
    chip(im, 400, 400, '10:00 p. m.', t - wt(1, '10'), col=WHITE, tcol=(36, 36, 40), size=30)
    q = t - wt(1, 'universidad')
    if q > 0 and t < wt(1, 'celular'): stamp(im, 360, 560, ['UNIVERSIDAD'], (150, 150, 160), q, ang=-6, size=40)
    q = t - wt(1, 'celular')
    if q > 0: stamp(im, 360, 560, ['EN SU CELULAR'], RED, q, ang=-6, size=44)
    im = camera(im, 1.1, lerp(450, 420, ease(lt / 4)), 800)
    obj('in', (260, 700, 460, 1100)); obj('out', (500, 800, 580, 920)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = t - wt(2, 'público')
    if q > 0: bubble(im, 90, 420, '¿Público objetivo?', q, col=(36, 36, 40), size=32)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 860, .95, None); im.alpha_composite(L); d = BD(im)
    for k in range(3):
        y = 640 + k * 150; d.rounded_rectangle((230, y, 490, y + 130), 12, fill=(40, 42, 54)); shirt(d, 300, y + 64, .4, [RED, (60, 110, 200), (90, 160, 120)][k])
        d.text((350, y + 50), 'Ropa linda', font=F('Inter-Bold.otf', 18), fill='white', anchor='lm')
        vq = t - wt(2, 'nadie')
        d.text((350, y + 90), '0 vistas' if vq > k * .15 else '…', font=F('Inter-Black.otf', 20), fill=RED, anchor='lm')
    obj('in', (500, 800, 580, 920)); obj('out', (217, 575, 503, 1145)); return im

def sc3(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (80, 420, 640, 1050); gcm_screen(im, r, t, t - wt(3, 'cursos'))
    chip(im, 360, 1120, 'MARKETING + IA', t - wt(3, 'inteligencia'), col=WHITE, tcol=RED, size=26)
    fq = ease((t - wt(3, 'cursos') + .2) / .8)
    im = camera(im, 1.0 + .08 * fq, 360, lerp(700, 780, fq))
    obj('in', (217, 575, 503, 1145)); obj('out', (104, 560, 616, 670)); return im

def sc4(t, lt):
    ph = (lt * 1.4) % 2; night = ph < 1
    im = gradient(*NIGHT) if night else gradient((190, 222, 246), (240, 246, 252)); d = BD(im)
    if night: moon(d, 600, 420, 40, NIGHT[0])
    else: sun(im, 600, 420, 46); d = BD(im)
    r = (110, 540, 610, 760); card(im, r, (255, 255, 255), 24); d = BD(im)
    if night:
        d.rounded_rectangle((140, 570, 260, 730), 14, fill=(36, 36, 40)); d.polygon([(185, 615), (185, 685), (230, 650)], fill='white')
        d.text((290, 620), 'Noche:', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm'); d.text((290, 670), 'Una clase', font=F('Inter-Black.otf', 34), fill=(30, 30, 36), anchor='lm')
    else:
        d.ellipse((150, 590, 250, 690), fill=GREEN_OK); d.text((200, 640), '1', font=F('Inter-Black.otf', 56), fill='white', anchor='mm')
        d.text((290, 620), 'Día:', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm'); d.text((290, 670), 'Probar 1 cosa', font=F('Inter-Black.otf', 34), fill=(30, 30, 36), anchor='lm')
    n = min(7, int(lt * .7) + 1)
    for k in range(7):
        x = 120 + k * 80; on = k < n; d.ellipse((x - 26, 880, x + 26, 932), fill=RED if on else (200, 202, 210))
        if on: d.line((x - 12, 906, x - 2, 918, x + 14, 894), fill='white', width=5)
    obj('in', (104, 560, 616, 670)); obj('out', (110, 540, 610, 760)); return im

def sc5(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = ease((t - wt(5, 'fotos') + .1) / .5)
    r1 = (80, 400, 340, 700); r2 = (380, 400, 640, 700)
    card(im, r1, (120, 120, 126), 18); d = BD(im); shirt(d, 210, 560, .9, (110, 70, 80)); d.text((210, 670), 'ANTES', font=F('Inter-Black.otf', 22), fill=(220, 220, 225), anchor='mm')
    if q > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); card(L, r2, (255, 246, 236), 18); dl = BD(L); shirt(dl, 510, 560, .9, RED); dl.text((510, 670), 'DESPUÉS', font=F('Inter-Black.otf', 22), fill=RED, anchor='mm')
        L.putalpha(L.getchannel('A').point(lambda p: int(p * q))); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(5, 'descripciones') + .1) / .5)
    if q > 0:
        r = (80, 740, 640, 880); card(im, r, (255, 255, 255), 18); d = BD(im)
        txt = 'Blusa roja de algodón, fresca y ligera. Tallas S a XL.'; n = int(len(txt) * q)
        d.text((110, 790), txt[:28], font=F('Inter-SemiBold.otf', 24), fill=(40, 40, 46), anchor='lm') if n > 0 else None
        d.text((110, 830), txt[28:n] if n > 28 else '', font=F('Inter-SemiBold.otf', 24), fill=(40, 40, 46), anchor='lm')
    q = t - wt(5, 'ella')
    if q > 0:
        a = back_out(q / .4); r = (80, 920, 640, 1060); card(im, (360 - 280 * a, 990 - 70 * a, 360 + 280 * a, 990 + 70 * a), (36, 36, 40), 18); d = BD(im)
        if a > .7: d.text((360, 990), '«Soy Andrea y elijo cada prenda yo misma»', font=F('Inter-Bold.otf', 22), fill='white', anchor='mm')
    fq = ease((t - wt(5, 'descripciones')) / 1.5)
    im = camera(im, 1.05, 360, lerp(560, 900, fq))
    obj('in', (110, 540, 610, 760)); obj('out', (80, 920, 640, 1060)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.1, None); im.alpha_composite(L); d = BD(im)
    d.rounded_rectangle((210, 520, 510, 560), 20, fill=RED); d.text((360, 540), '✦ IA'.replace('✦ ', ''), font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    q = t - wt(6, 'publicaciones')
    txt = ['Nueva colección 🌸'.replace(' 🌸', ''), 'Blusas frescas para', 'el calor. Pide la', 'tuya por WhatsApp.']
    for k, l in enumerate(txt):
        n = int(len(l) * ease((t - wt(6, 'inteligencia') - k * .35) / .5))
        d.text((220, 600 + k * 40), l[:n], font=F('Inter-Black.otf' if k == 0 else 'Inter-SemiBold.otf', 24), fill='white', anchor='lm')
    if q > -.2:
        a = ease((q + .2) / .4); d.rounded_rectangle((220, 780, 500, 960), 14, fill=(255, 236, 226)); shirt(d, 360, 880, .7 * a + .01, RED)
    sparkles(im, 360, 760, t, n=14, rad=200)
    chip(im, 360, 1150, 'EN MINUTOS', t - wt(6, 'minutos'), size=28)
    obj('in', (80, 920, 640, 1060)); obj('out', (220, 780, 500, 960)); return im

def sc7(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.text((360, 400), 'Preguntas por semana', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='mm')
    vals = [(1, 'primera', 12), (2, 'primera', 30), (3, 'tercera', 100)]
    for k, (n, w_, v) in enumerate(vals):
        q = ease((t - wt(7, w_) - (k == 1) * .4) / .6)
        x = 160 + k * 200; hgt = 600 * v / 100 * q
        d.rounded_rectangle((x - 60, 1100 - hgt, x + 60, 1100), 12, fill=RED if k == 2 else (180, 184, 196))
        d.text((x, 1140), f'Semana {n}', font=F('Inter-Bold.otf', 22), fill=(90, 90, 100), anchor='mm')
    q = t - wt(7, 'preguntaron')
    if q > 0: chip(im, 560, 440, 'MÁS QUE TODO EL MES', q, size=20)
    obj('in', (220, 780, 500, 960)); obj('out', (500, 500, 620, 1100)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); andrea(ImageDraw.Draw(L), 360, 680, 2.0, bob=-abs(math.sin(t * 2)) * 3); im.alpha_composite(L); d = BD(im)
    q = t - wt(8, 'experta')
    if q > 0: chip(im, 360, 430, 'NO ES EXPERTA (TODAVÍA)', q, col=(36, 36, 40), size=22)
    q = t - wt(8, 'adivinar')
    # dado tachado
    cx, cy = 560, 600
    d.rounded_rectangle((cx - 50, cy - 50, cx + 50, cy + 50), 14, fill=(255, 255, 255), outline=(36, 36, 40), width=5)
    for px, py in ((-22, -22), (0, 0), (22, 22)): d.ellipse((cx + px - 8, cy + py - 8, cx + px + 8, cy + py + 8), fill=(36, 36, 40))
    if q > 0:
        sl = ease(q / .3); d.line((cx - 70, cy + 70, cx - 70 + 140 * sl, cy + 70 - 140 * sl), fill=RED, width=12)
        stamp(im, 360, 1080, ['DEJÓ DE ADIVINAR'], RED, q, ang=-5, size=46)
    obj('in', (500, 500, 620, 1100)); obj('out', (260, 560, 460, 980)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # a ciegas: camino en zigzag largo
    d.text((190, 400), 'A ciegas', font=F('Inter-Black.otf', 30), fill=(120, 120, 130), anchor='mm')
    pts = [(190 + math.sin(k * .9) * 110, 460 + k * 34) for k in range(20)]
    q = ease((t - ct(9)) / 2.5); n = max(2, int(len(pts) * q)); d.line(pts[:n], fill=(160, 160, 170), width=8, joint='curve')
    d.text((530, 400), 'Aprendiendo', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    q2 = ease((t - wt(9, 'ahorra')) / .8)
    if q2 > 0: d.line((530, 460, 530, 460 + 640 * q2), fill=RED, width=12); 
    if q2 > .95: d.polygon([(530, 1130), (505, 1090), (555, 1090)], fill=RED)
    q3 = t - wt(9, 'ciegas')
    if q3 > 0: chip(im, 190, 1180, 'MESES PERDIDOS', q3, col=(120, 120, 130), size=20)
    obj('in', (260, 560, 460, 980)); obj('out', (470, 440, 590, 1140)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90))
    r = (80, 420, 640, 1050); gcm_screen(im, r, t, 9, prog=ease(lt / 3))
    chip(im, 220, 1120, 'SI VENDES ALGO', t - wt(10, 'vendes'), col=WHITE, tcol=RED, size=22)
    chip(im, 500, 1120, 'O QUIERES EMPEZAR', t - wt(10, 'empezar'), col=WHITE, tcol=RED, size=22)
    obj('in', (470, 440, 590, 1140)); obj('out', (80, 420, 640, 530)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Gana con Marketing', F('Inter-Black.otf', 34), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'e Inteligencia Artificial', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'CURSOS DE MARKETING E IA', t - wt(11, 'regístrate'), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'noche')
    if q > -.3: mask_text(im, (W / 2, 760), '…puede ser esta noche.', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
    CAM.update(x0=0, y0=0, z=1); obj('in', (60, 330, 660, 630)); obj('out', (60, 330, 660, 630))
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
