"""Día 52 — "Info al privado" (historia: doña Rosa arrienda un apartamento y lo publica en Inmuebles del Marketplace de Sumiago con su ficha completa).
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
KEY = {'rosa', 'apartamento.', 'apartamento', 'privado».', '40', 'mismo.', 'habitaciones?', 'parqueadero?', 'estrato?', 'mascotas?', 'medianoche.', 'nadie', 'marketplace', 'sumiago', 'sumiago,', 'inmuebles,', 'alquiler.', 'todo:', 'balcón', 'cerrado.', 'condiciones:', 'ficha', 'completa', 'mapa.', 'distintos:', 'sábado?»', 'familias.', 'quedó', 'inmueble', 'ficha:', 'link', 'responde', 'pregunten.'}
def is_key(w): return w.lower() in KEY or w.strip('¿?.,:«»…').lower() in KEY

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
        mask_text(im, (W // 2, 800), 'Publica tu inmueble', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); WA = (37, 211, 102)
def rosa(d, x, y, s, bob=0): figure(d, x, y, s, (176, 80, 120), skin=(220, 172, 136), hair=(170, 170, 176), long=True, bob=bob)
def sobrina(d, x, y, s, bob=0): figure(d, x, y, s, (60, 140, 120), skin=(206, 156, 120), hair=(40, 26, 20), long=True, bob=bob)
def edificio(d, cx, by, s=1.0, lit=0):
    w, h = 180 * s, 300 * s
    d.rectangle((cx - w / 2, by - h, cx + w / 2, by), fill=(236, 214, 190), outline=(150, 120, 96), width=max(1, int(3 * s)))
    d.rectangle((cx - w / 2 - 8 * s, by - h - 14 * s, cx + w / 2 + 8 * s, by - h), fill=(170, 70, 60))
    for r in range(5):
        for c in range(3):
            x = cx - w / 2 + 22 * s + c * 52 * s; y = by - h + 20 * s + r * 54 * s
            on = lit and (r * 3 + c) % 4 == 1
            d.rectangle((x, y, x + 32 * s, y + 34 * s), fill=(255, 220, 120) if on else (140, 190, 220), outline=(110, 90, 76), width=max(1, int(2 * s)))
    d.rectangle((cx - 20 * s, by - 50 * s, cx + 20 * s, by), fill=(120, 80, 56))
def casita(d, cx, cy, s, col=RED):
    d.polygon([(cx - 34 * s, cy - 4 * s), (cx, cy - 34 * s), (cx + 34 * s, cy - 4 * s)], fill=col); d.rectangle((cx - 24 * s, cy - 4 * s, cx + 24 * s, cy + 28 * s), fill=col); d.rectangle((cx - 7 * s, cy + 8 * s, cx + 7 * s, cy + 28 * s), fill=(255, 255, 255))
def pin(d, cx, cy, s, col=RED):
    d.ellipse((cx - 18 * s, cy - 44 * s, cx + 18 * s, cy - 8 * s), fill=col); d.polygon([(cx - 15 * s, cy - 20 * s), (cx + 15 * s, cy - 20 * s), (cx, cy + 4 * s)], fill=col); d.ellipse((cx - 7 * s, cy - 33 * s, cx + 7 * s, cy - 19 * s), fill='white')
def post_grupo(im, cx, cy, s):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(40, 60, 110)); d.text((x0 + 16, y0 + 25 * s), 'Grupo Arriendos', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 50 * s, xe, y0 + 330 * s), fill=(206, 226, 240)); edificio(d, cx, y0 + 320 * s, .8 * s)
    d.text((x0 + 16, y0 + 370 * s), 'Arriendo apto.', font=F('Inter-Black.otf', int(28 * s)), fill='white', anchor='lm')
    d.text((x0 + 16, y0 + 412 * s), 'Info al privado', font=F('Inter-Black.otf', int(28 * s)), fill=(255, 120, 126), anchor='lm')
    return (x0, y0 + 50 * s, xe, y0 + 330 * s)
def badge(d, cx, cy, n):
    d.ellipse((cx - 34, cy - 34, cx + 34, cy + 34), fill=RED, outline='white', width=4); d.text((cx, cy), str(n), font=F('Inter-Black.otf', 30), fill='white', anchor='mm')

def sc0(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rosa(ImageDraw.Draw(L), 150, 820, 1.6); im.alpha_composite(L)
    r = post_grupo(im, 470, 760, .75)
    q = t - wt(0, 'privado')
    if q > 0: stamp(im, 470, 1140, ['INFO AL PRIVADO'], RED, q, ang=-5, size=36)
    im = camera(im, lerp(1.0, 1.15, ease((t - wt(0, 'escribió')) / 1.5)), 470, 820)
    obj('in', (330, 520, 610, 760)); obj('out', (350, 460, 590, 700)); return im

def sc1(t, lt):
    im = gradient((26, 20, 34), (10, 8, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((60, 300, 660, 900), fill=255), (80, 90, 200), 120, 90)); d = BD(im)
    d.ellipse((560, 120, 640, 200), fill=(240, 236, 210)); d.ellipse((585, 110, 665, 190), fill=(26, 20, 34))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 720, 1.0, None); im.alpha_composite(L); d = BD(im)
    t0 = wt(1, '40') - .9; n = int(max(0, min(40, (t - t0) / .9 * 40)))
    for k in range(min(n, 8)):
        y = 500 + k * 58; d.rounded_rectangle((230, y, 490, y + 48), 14, fill=(44, 46, 58)); d.ellipse((240, y + 8, 272, y + 40), fill=(90 + k * 15 % 120, 120, 160)); d.rounded_rectangle((282, y + 12, 282 + 60 + (k * 37) % 120, y + 22), 5, fill=(150, 150, 164)); d.rounded_rectangle((282, y + 28, 282 + 40 + (k * 53) % 100, y + 36), 4, fill=(100, 100, 114))
    if n: badge(d, 495, 430, n)
    q = t - wt(1, 'mismo')
    if q > 0: chip(im, 360, 1130, 'TODOS PREGUNTABAN LO MISMO', q, col=WHITE, tcol=RED, size=24)
    obj('in', (210, 420, 510, 1020)); obj('out', (210, 420, 510, 1020)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy()
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rosa(ImageDraw.Draw(L), 360, 720, 1.8, bob=math.sin(t * 9) * 2); im.alpha_composite(L)
    qs = [('habitaciones', '¿Cuántas habitaciones?', 60, 380), ('parqueadero', '¿Tiene parqueadero?', 330, 520), ('estrato', '¿Qué estrato?', 70, 1000), ('aceptan', '¿Aceptan mascotas?', 330, 1130)]
    for k, (w_, txt, x, y) in enumerate(qs):
        q = t - wt(2, w_) + .15
        bubble(im, x, y, txt, q, col=(44, 46, 58), size=26)
        if q > .6:
            for j in range(2): bubble(im, x + 30 + j * 26, y + 70 + j * 16 if y < 900 else y - 70 - j * 16, txt, q - .6 - j * .3, col=(120, 122, 134), size=16)
    obj('in', (210, 420, 510, 1020)); obj('out', (320, 720, 400, 960)); return im

def sc3(t, lt):
    tn = t - wt(3, 'otro')
    if tn < 0:
        im = gradient((26, 20, 34), (10, 8, 14)); d = BD(im)
        cx, cy = 360, 470; d.ellipse((cx - 140, cy - 140, cx + 140, cy + 140), fill=(250, 250, 250), outline=RED, width=10)
        for k in range(12): a = k * math.pi / 6; d.line((cx + math.sin(a) * 118, cy - math.cos(a) * 118, cx + math.sin(a) * 104, cy - math.cos(a) * 104), fill=(40, 40, 46), width=5)
        p = ease((t - ct(3)) / 1.6); am = (-math.pi / 2 + p * math.pi / 2) ; ah = -math.pi / 6 * (1 - p)
        d.line((cx, cy, cx + math.sin(am + math.pi / 2) * 0 + math.cos(am) * 100, cy + math.sin(am) * 100), fill=(30, 30, 36), width=8)
        d.line((cx, cy, cx + math.sin(ah) * 66, cy - math.cos(ah) * 66), fill=RED, width=12)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); rosa(ImageDraw.Draw(L), 360, 760, 1.6, bob=4); im.alpha_composite(L); d = BD(im)
        d.text((470, 760), 'z', font=F('Inter-Black.otf', 40), fill=(200, 200, 220), anchor='mm'); d.text((500, 720), 'z', font=F('Inter-Black.otf', 30), fill=(200, 200, 220), anchor='mm')
        chip(im, 360, 1100, '12:00 A. M.', t - wt(3, 'medianoche'), col=RED, size=26)
    else:
        im = gradient((235, 238, 242), (205, 210, 218)); d = BD(im)
        edificio(d, 360, 1010, 1.5)
        chip(im, 360, 420, 'AL OTRO DÍA…', tn + .3, col=(36, 36, 40), size=26)
        q = t - wt(3, 'nadie')
        if q > 0: stamp(im, 360, 1130, ['NADIE FUE A VERLO'], RED, q, ang=-5, size=40)
    obj('in', (320, 720, 400, 960)); obj('out', (225, 560, 495, 1010)); return im

def sc4(t, lt):
    im = BGR_LIGHT.copy()
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); rosa(dl, 170, 860, 1.5); sobrina(dl, 330, 860, 1.5, bob=-abs(math.sin(t * 5)) * 3); im.alpha_composite(L)
    bubble(im, 260, 620, 'Publícalo en el Marketplace', t - wt(4, 'publícalo'), col=RED, size=24)
    path = [('marketplace', 'Marketplace'), ('inmuebles', 'Inmuebles'), ('alquiler', 'Alquiler')]
    for k, (w_, lab) in enumerate(path):
        q = t - wt(4, w_)
        chip(im, 360, 420 + k * 0 if False else 330 + k * 80, ('› ' if k else '') + lab, q, col=(36, 36, 40) if k < 2 else RED, size=26)
    q = t - wt(4, 'inmuebles')
    if q > 0: d = BD(im); casita(d, 590, 1080, 1.6 * back_out(q / .35))
    obj('in', (225, 560, 495, 1010)); obj('out', (280, 370, 440, 470)); return im

def form_card(im, r, rows, t):
    card(im, r, (255, 255, 255), 24); d = BD(im)
    for k, (lab, val, tw) in enumerate(rows):
        y = r[1] + 80 + k * 92
        d.text((r[0] + 30, y - 22), lab, font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
        q = t - tw
        d.rounded_rectangle((r[0] + 24, y, r[2] - 24, y + 52), 12, fill=(244, 244, 247), outline=RED if 0 < q < .7 else (226, 226, 232), width=3)
        if q > 0:
            n = int(len(val) * ease(q / .35)); d.text((r[0] + 42, y + 26), val[:n], font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
            if q > .35: d.text((r[2] - 50, y + 26), '✓', font=F('Inter-Black.otf', 26), fill=GREEN_OK, anchor='mm')

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90)); d = BD(im)
    d.text((360, 300), 'Inmuebles › Alquiler', font=F('Inter-Black.otf', 30), fill='white', anchor='mm')
    rows = [('Área construida', '62 m²', wt(5, 'área')), ('Habitaciones', '3', wt(5, 'habitaciones')), ('Baños', '2', wt(5, 'baños')), ('Parqueaderos', '1', wt(5, 'parqueadero')), ('Estrato', '3', wt(5, 'estrato')), ('Piso', '4', wt(5, 'piso'))]
    form_card(im, (70, 350, 650, 350 + 80 + 6 * 92 - 20), rows, t)
    fy = 350 + 80 + max(0, min(5, sum(1 for r in rows if t > r[2]) - 1)) * 92
    im = camera(im, 1.06, 360, lerp(640, 780, ease((t - wt(5, 'baños')) / 1.6)))
    obj('in', (280, 370, 440, 470)); obj('out', (70, 350, 650, 960)); return im

def check(d, x, y, lab, q, col=GREEN_OK):
    on = q > 0
    d.rounded_rectangle((x, y, x + 40, y + 40), 9, fill=col if on else (255, 255, 255), outline=col if on else (200, 200, 208), width=3)
    if on: d.line((x + 9, y + 21, x + 17, y + 30, x + 32, y + 11), fill='white', width=5)
    d.text((x + 56, y + 20), lab, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')

def sc6(t, lt):
    im = BGR_LIGHT.copy()
    r = (70, 300, 650, 620); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((100, 345), 'Comodidades', font=F('Inter-Black.otf', 26), fill=RED, anchor='lm')
    for k, (lab, w_) in enumerate([('Balcón', 'balcón'), ('Conjunto cerrado', 'conjunto'), ('Cerca a transporte', None)]):
        check(d, 100, 390 + k * 70, lab, (t - wt(6, w_)) if w_ else (t - wt(6, 'cerrado') - .4))
    r = (70, 660, 650, 1040); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((100, 705), 'Condiciones', font=F('Inter-Black.otf', 26), fill=RED, anchor='lm')
    rows = [('Depósito', '1 mes', 'depósito'), ('Contrato mínimo', '6 meses', 'contrato')]
    for k, (lab, val, w_) in enumerate(rows):
        y = 750 + k * 80; q = t - wt(6, w_)
        d.text((100, y + 26), lab, font=F('Inter-Bold.otf', 22), fill=(90, 90, 100), anchor='lm')
        d.rounded_rectangle((380, y, 620, y + 52), 12, fill=(244, 244, 247), outline=RED if 0 < q < .6 else (226, 226, 232), width=3)
        if q > 0: d.text((400, y + 26), val, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
    check(d, 100, 935, 'Acepta mascotas', t - wt(6, 'mascotas'))
    q = t - wt(6, 'mascotas')
    if q > 0: d = BD(im); d.ellipse((560, 925, 620, 985), fill=(255, 236, 200)); d.text((590, 955), '🐾' if False else '♥', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    obj('in', (70, 350, 650, 960)); obj('out', (70, 300, 650, 1040)); return im

def listing_inm(im, cx, cy, s, t, qmap=1.0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'MARKETPLACE', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 50 * s, xe, y0 + 230 * s), fill=(206, 226, 240)); edificio(d, cx, y0 + 226 * s, .55 * s)
    d.text((x0 + 16, y0 + 258 * s), 'Apartamento en arriendo', font=F('Inter-Black.otf', int(21 * s)), fill='white', anchor='lm')
    cells = [('Área', '62 m²'), ('Hab.', '3'), ('Baños', '2'), ('Parq.', '1'), ('Estrato', '3'), ('Piso', '4')]
    cw = (xe - x0 - 24) / 3
    for k, (a, b) in enumerate(cells):
        cx0 = x0 + 12 + (k % 3) * cw; cy0 = y0 + 282 * s + (k // 3) * 64 * s
        d.rounded_rectangle((cx0 + 3, cy0, cx0 + cw - 3, cy0 + 58 * s), 10, fill=(40, 42, 52))
        d.text((cx0 + cw / 2, cy0 + 18 * s), a, font=F('Inter-SemiBold.otf', int(13 * s)), fill=(170, 170, 180), anchor='mm'); d.text((cx0 + cw / 2, cy0 + 40 * s), b, font=F('Inter-Black.otf', int(20 * s)), fill='white', anchor='mm')
    my = y0 + 420 * s
    d.rounded_rectangle((x0 + 12, my, xe - 12, my + 150 * s), 14, fill=(229, 227, 223))
    for k in range(5): d.line((x0 + 12, my + 20 * s + k * 30 * s, xe - 12, my + 10 * s + k * 34 * s), fill=(255, 255, 255), width=max(2, int(6 * s)))
    d.line((x0 + 90 * s, my, x0 + 150 * s, my + 150 * s), fill=(250, 220, 140), width=max(3, int(10 * s)))
    if qmap > 0: pin(d, cx, my + 90 * s - 20 * s * (1 - back_out(qmap / .35)), 1.3 * s)
    return (x0, my, xe, my + 150 * s)

def sc7(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    r = listing_inm(im, 360, 740, .95, t, qmap=t - wt(7, 'mapa'))
    q = t - wt(7, 'ficha')
    if q > 0: chip(im, 360, 300, 'FICHA COMPLETA', q, col=GREEN_OK, size=26)
    sparkles(im, 360, 740, t, n=14, rad=300) if 0 < q < 1.2 else None
    im = camera(im, lerp(1.0, 1.18, ease((t - wt(7, 'ubicación')) / .9)), 360, lerp(740, 960, ease((t - wt(7, 'ubicación')) / .9)))
    obj('in', (70, 300, 650, 1040)); obj('out', (r[0], r[1], r[2], r[3])); return im

def sc8(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 760, 1.05, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((216, 480, 504, 530), fill=(20, 20, 24)); d.text((236, 505), 'Mensajes', font=F('Inter-Black.otf', 20), fill='white', anchor='lm')
    t0 = wt(8, 'puedo') - .1
    for k in range(3):
        q = t - t0 - k * .45
        if q <= 0: continue
        a = back_out(q / .35); y = 560 + k * 140
        d.rounded_rectangle((226, y, 226 + 270 * a, y + 110), 18, fill=(255, 255, 255))
        if a > .8:
            d.ellipse((238, y + 12, 270, y + 44), fill=(120 + k * 40, 140, 190)); d.text((282, y + 28), ['Andrés', 'Familia Gómez', 'Paula'][k], font=F('Inter-Black.otf', 16), fill=(30, 30, 36), anchor='lm')
            d.text((240, y + 64), '¿Puedo ir a verlo', font=F('Inter-SemiBold.otf', 18), fill=(60, 60, 70), anchor='lm'); d.text((240, y + 88), 'el sábado?', font=F('Inter-SemiBold.otf', 18), fill=(60, 60, 70), anchor='lm')
    q = t - wt(8, 'distintos')
    if q > 0: chip(im, 360, 380, 'MENSAJES DISTINTOS', q, col=(36, 36, 40), size=24)
    obj('in', (240, 840, 480, 1000)); obj('out', (226, 560, 496, 950)); return im

def sc9(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    d.rectangle((0, 1040, W, H), fill=(190, 196, 206)); edificio(d, 360, 1040, 1.3)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    rosa(dl, 360, 900, 1.2)
    fams = [(110, (90, 120, 200)), (210, (200, 120, 60)), (520, (90, 160, 90))]
    for k, (x, c) in enumerate(fams):
        q = ease((t - wt(9, 'familias') + .6 - k * .25) / .6)
        if q <= 0: continue
        xx = x + (1 - q) * (-200 if x < 360 else 200)
        figure(dl, xx, 900, 1.2, c, bob=-abs(math.sin(t * 6 + k)) * 3); figure(dl, xx + 34, 930, .9, mix(c, (255, 255, 255), .4))
    im.alpha_composite(L); d = BD(im)
    q = t - wt(9, 'quedó')
    if q > 0:
        d.ellipse((540, 820, 600, 880), outline=GOLD, width=8); d.rectangle((596, 846, 650, 856), fill=GOLD); d.rectangle((630, 856, 640, 872), fill=GOLD)
        stamp(im, 360, 420, ['¡ARRENDADO!'], GREEN_OK, q, ang=-6, size=56)
    obj('in', (226, 560, 496, 950)); obj('out', (243, 650, 477, 1040)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('casas', 'Casas'), ('apartamentos', 'Apartamentos'), ('locales', 'Locales'), ('terrenos', 'Terrenos')]
    for k, (w_, lab) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        cx = 200 + (k % 2) * 320; cy = 560 + (k // 2) * 250
        card(im, (cx - 140 * a, cy - 100 * a, cx + 140 * a, cy + 100 * a), (250, 250, 250), 22); d = BD(im)
        if a > .7:
            if k == 0: casita(d, cx, cy - 20, 1.3)
            elif k == 1: edificio(d, cx, cy + 20, .3)
            elif k == 2: d.rectangle((cx - 44, cy - 50, cx + 44, cy + 14), fill=RED); d.rectangle((cx - 34, cy - 20, cx + 34, cy + 14), fill=(140, 190, 220)); d.rectangle((cx - 50, cy - 62, cx + 50, cy - 46), fill=(40, 40, 46))
            else: d.rectangle((cx - 50, cy - 30, cx + 50, cy + 10), fill=(120, 170, 90)); pin(d, cx, cy - 6, .9)
            d.text((cx, cy + 62), lab, font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm')
    q = t - wt(10, 'ficha')
    if q > 0: chip(im, 360, 380, 'CADA INMUEBLE CON SU FICHA', q, col=WHITE, tcol=RED, size=24)
    chip(im, 360, 1100, 'MARKETPLACE SUMIAGO', t - wt(10, 'marketplace'), size=24)
    obj('in', (243, 650, 477, 1040)); obj('out', (60, 460, 340, 660)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Inmuebles en Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tu anuncio con su ficha completa', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'CASAS · APTOS · LOCALES', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'buen')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Un buen anuncio…', F('Inter-BlackItalic.otf', 42), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'responde antes de que pregunten.', F('Inter-BlackItalic.otf', 34), WHITE, (t - wt(11, 'responde') + .3) / .4)
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
