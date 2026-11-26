"""Día 43 — "Lo que dicen de Wilmer" (historia: un barbero activa las reseñas de Mi Negocio en su portada de Sumiago y sus clientes hablan por él).
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
KEY = {'wilmer', 'barbero', 'nuevo', 'él', 'sabían', 'barbería', 'confiar', 'leemos', 'demás', 'reseñas', 'negocio', 'sumiago', 'corte', 'reseña', 'enlace', 'nombre', 'estrellas', 'palabras',
       'aviso', 'aprueba', 'clientes', 'recomiendan', 'publicidad', 'membresía', 'link', 'ti'}
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
        mask_text(im, (W // 2, 800), 'Deja que hablen por ti', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
# ---------- objetos ----------
def wilmer(d, x, y, s, bob=0): figure(d, x, y, s, (36, 36, 40), skin=(150, 100, 72), hair=(20, 16, 14), bob=bob)
def star(d, cx, cy, r, fill=GOLD, outline=None):
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5; rr = r if k % 2 == 0 else r * .45
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr))
    d.polygon(pts, fill=fill, outline=outline)
def stars(d, cx, cy, r, n=5, filled=5.0, gap=None, empty=(220, 222, 230)):
    gap = gap or r * 2.3
    for k in range(n):
        x = cx - gap * (n - 1) / 2 + k * gap
        star(d, x, cy, r, fill=empty); 
        if filled > k: star(d, x, cy, r * min(1, filled - k), fill=GOLD)
def barber_bg():
    im = gradient((232, 236, 242), (206, 212, 222)); d = BD(im)
    d.rounded_rectangle((420, 330, 680, 640), 20, fill=(190, 210, 226), outline=(120, 120, 130), width=8)   # espejo
    for k in range(8): d.polygon([(70, 340 + k * 50), (110, 360 + k * 50), (110, 380 + k * 50), (70, 360 + k * 50)], fill=RED if k % 2 == 0 else (60, 110, 200))
    d.rounded_rectangle((60, 320, 120, 760), 30, outline=(150, 150, 160), width=6)
    d.rectangle((0, 920, W, H), fill=(60, 60, 66)); 
    for k in range(10): d.rectangle((k * 72, 920, k * 72 + 36, H), fill=(80, 80, 88))
    d.rounded_rectangle((420, 740, 620, 840), 20, fill=(40, 40, 46)); d.rectangle((500, 840, 540, 920), fill=(150, 150, 160))   # silla
    return im
BGBA = barber_bg()
def review_card(im, r, name, txt, n=5):
    card(im, r, (255, 255, 255), 18); d = BD(im)
    d.ellipse((r[0] + 18, r[1] + 18, r[0] + 70, r[1] + 70), fill=[(90, 110, 150), (160, 100, 120), (90, 150, 120)][len(name) % 3]); d.text((r[0] + 44, r[1] + 44), name[0], font=F('Inter-Black.otf', 26), fill='white', anchor='mm')
    d.text((r[0] + 86, r[1] + 32), name, font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm'); stars(d, r[0] + 150, r[1] + 60, 10, filled=n)
    d.text((r[0] + 20, r[1] + 100), txt, font=F('Inter-SemiBoldItalic.otf', 20), fill=(70, 70, 80), anchor='lm')

# ---------- escenas ----------
def sc0(t, lt):
    im = BGBA.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); wilmer(dl, 300, 760, 1.7)
    cx = lerp(520, 640, ease((t - wt(0, 'salen')) / 1.0)); figure(dl, cx, 770, 1.6, (90, 150, 120), skin=(214, 166, 128))
    im.alpha_composite(L)
    bubble(im, 300, 450, '¡Quedé como nuevo!', t - wt(0, 'quedé') + .1, col=(90, 150, 120), size=30)
    chip(im, 300, 1060, 'BARBERO', t - wt(0, 'barbero'), col=(36, 36, 40), size=28)
    im = camera(im, lerp(1.2, 1.0, ease(lt / 3)), 400, 720)
    obj('in', (230, 620, 370, 960)); obj('out', (300, 450, 650, 530)); return im

def sc1(t, lt):
    im = BGBA.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); wilmer(ImageDraw.Draw(L), 200, 760, 1.7); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(1, 'escuchaba')) / .5)
    for k in range(3):
        if q > 0: d.arc((250 - k * 30, 600 - k * 30, 330 + k * 30, 680 + k * 30), -60, 60, fill=(90, 150, 120, int(255 * q * (1 - k * .25))), width=6)
    # pared y clientes nuevos
    d.rectangle((420, 330, 450, 960), fill=(150, 154, 166))
    q2 = t - wt(1, 'nuevos')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(2):
        a = ease((q2 - k * .2) / .5)
        if a > 0: figure(dl, 540 + k * 90, 780 + (1 - a) * 40, 1.4, [(60, 110, 200), (200, 140, 60)][k], long=k == 1)
    im.alpha_composite(L); d = BD(im)
    if t > wt(1, 'sabían'): d.text((585, 640), '?', font=F('Inter-Black.otf', 70), fill=RED, anchor='mm')
    chip(im, 200, 450, 'SOLO LO ESCUCHA ÉL', t - wt(1, 'él'), col=(36, 36, 40), size=22)
    obj('in', (300, 450, 650, 530)); obj('out', (500, 600, 680, 960)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.rounded_rectangle((200, 470, 520, 520), 25, fill=(40, 42, 54)); d.text((228, 495), 'barbería', font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
    for k in range(3):
        a = ease((t - wt(2, 'fotos') - k * .15) / .4)
        if a <= 0: continue
        y = 550 + k * 190; d.rounded_rectangle((200, y, 520, y + 170), 14, fill=(36, 38, 48))
        d.rounded_rectangle((214, y + 14, 340, y + 156), 10, fill=[(150, 180, 210), (200, 190, 170), (170, 200, 180)][k])
        d.text((356, y + 40), ['Barbería X', 'Corte Pro', 'Estilo 10'][k], font=F('Inter-Black.otf', 20), fill='white', anchor='lm'); stars(d, 420, y + 90, 11, filled=0, empty=(70, 72, 86))
        d.text((356, y + 130), 'Sin reseñas', font=F('Inter-SemiBold.otf', 16), fill=(150, 150, 160), anchor='lm')
    q = t - wt(2, 'confiar')
    if q > 0: stamp(im, 360, 1180, ['¿EN QUIÉN CONFÍO?'], RED, q, ang=-5, size=40)
    obj('in', (500, 600, 680, 960)); obj('out', (172, 425, 548, 1175)); return im

def sc3(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(3): figure(dl, 160 + k * 200, 800, 1.6, [(60, 110, 200), (200, 140, 60), (160, 90, 160)][k], long=k == 1)
    im.alpha_composite(L); d = BD(im)
    q = t - wt(3, 'leemos')
    for k in range(3):
        a = back_out((q - k * .12) / .35)
        if a > 0:
            x = 160 + k * 200; d.rounded_rectangle((x - 70 * a, 560 - 40 * a, x + 70 * a, 560 + 40 * a), 16, fill=(255, 255, 255))
            if a > .7: stars(d, x, 560, 10, filled=5 - (k == 1), gap=24)
    chip(im, 360, 420, 'LEEMOS LO QUE DICEN LOS DEMÁS', t - wt(3, 'demás'), col=(36, 36, 40), size=20)
    obj('in', (172, 425, 548, 1175)); obj('out', (90, 520, 630, 600)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 500, 660, 800); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((r[0] + 30, r[1] + 44), 'Mi Negocio', font=F('Inter-Black.otf', 32), fill=(30, 30, 36), anchor='lm')
    d.rounded_rectangle((r[2] - 110, r[1] + 26, r[2] - 30, r[1] + 62), 18, fill=RED); d.text((r[2] - 70, r[1] + 44), 'PRO', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    x = r[0] + 30
    for tb in ['Agenda', 'Clientes', 'Reseñas', 'Menú QR']:
        f = F('Inter-Bold.otf', 18); tw = d.textlength(tb, font=f) + 26; on = tb == 'Reseñas'
        d.rounded_rectangle((x, r[1] + 86, x + tw, r[1] + 122), 18, fill=RED if on else (240, 240, 244)); d.text((x + tw / 2, r[1] + 104), tb, font=f, fill='white' if on else (90, 90, 100), anchor='mm'); x += tw + 8
    y = r[1] + 150; on_q = ease((t - wt(4, 'reseñas')) / .4)
    d.rounded_rectangle((r[0] + 30, y, r[2] - 30, y + 110), 16, fill=(244, 244, 247))
    d.text((r[0] + 50, y + 36), 'Mostrar reseñas y permitir', font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='lm'); d.text((r[0] + 50, y + 66), 'que me dejen nuevas', font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='lm')
    tx = r[2] - 110; d.rounded_rectangle((tx, y + 36, tx + 60, y + 66), 15, fill=mix((190, 190, 200), GREEN_OK, on_q)); d.ellipse((tx + 3 + 30 * on_q, y + 39, tx + 27 + 30 * on_q, y + 63), fill='white')
    chip(im, 360, 440, 'EN SU PORTADA DE SUMIAGO', t - wt(4, 'sumiago'), col=WHITE, tcol=RED, size=22)
    im = camera(im, 1.0 + .12 * on_q, 360, 650)
    obj('in', (90, 520, 630, 600)); obj('out', (r[0] + 30, y, r[2] - 30, y + 110)); return im

def sc5(t, lt):
    im = BGBA.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); wilmer(dl, 250, 760, 1.7); figure(dl, 520, 700, 1.5, (90, 150, 120), skin=(214, 166, 128)); im.alpha_composite(L)
    chip(im, 520, 560, 'CORTE LISTO', t - wt(5, 'corte'), col=(36, 36, 40), size=22)
    bubble(im, 60, 420, 'Si te gustó, déjame tu reseña', t - wt(5, 'gustó') + .1, col=RED, size=26)
    q = t - wt(5, 'enlace')
    if q > 0:
        a = back_out(q / .35); r = (140, 1040, 580, 1130); card(im, (360 - 220 * a, 1085 - 45 * a, 360 + 220 * a, 1085 + 45 * a), (255, 255, 255), 40); d = BD(im)
        if a > .7: d.text((360, 1085), 'sumiago.com/wilmer-barber', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
    obj('in', (r[0] + 30, 650, 630, 760) if False else (90, 650, 630, 760)); obj('out', (140, 1040, 580, 1130)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.text((360, 480), 'Deja tu reseña', font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
    d.text((210, 540), 'Nombre', font=F('Inter-Bold.otf', 18), fill=(170, 170, 180), anchor='lm'); d.rounded_rectangle((200, 560, 520, 610), 12, fill=(40, 42, 54))
    nm = 'Julián'[:int(6 * ease((t - wt(6, 'nombre') + .1) / .5))]; d.text((220, 585), nm, font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
    d.text((210, 660), 'Estrellas', font=F('Inter-Bold.otf', 18), fill=(170, 170, 180), anchor='lm')
    stars(d, 360, 720, 24, filled=5 * ease((t - wt(6, 'estrellas') + .1) / .8))
    d.text((210, 800), 'Tu opinión', font=F('Inter-Bold.otf', 18), fill=(170, 170, 180), anchor='lm'); d.rounded_rectangle((200, 820, 520, 920), 12, fill=(40, 42, 54))
    tx = 'Excelente corte'[:int(15 * ease((t - wt(6, 'palabras') + .2) / .6))]; d.text((220, 850), tx, font=F('Inter-SemiBold.otf', 22), fill='white', anchor='lm')
    d.rounded_rectangle((220, 960, 500, 1020), 30, fill=RED); d.text((360, 990), 'Enviar', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    fq = ease((t - wt(6, 'estrellas') + .2) / .6)
    im = camera(im, 1.0 + .15 * fq, 360, lerp(760, 780, fq))
    obj('in', (140, 1040, 580, 1130)); obj('out', (220, 960, 500, 1020)); return im

def sc7(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    q = t - wt(7, 'aviso')
    r = (60, 440, 660, 600)
    if q > -.2:
        a = ease((q + .2) / .35); r = (60, 440 - (1 - a) * 40, 660, 600 - (1 - a) * 40); card(im, r, (255, 255, 255), 22); d = BD(im)
        d.ellipse((r[0] + 24, r[1] + 30, r[0] + 84, r[1] + 90), fill=GOLD); star(d, r[0] + 54, r[1] + 60, 18, fill='white')
        d.text((r[0] + 104, r[1] + 46), 'Nueva reseña', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
        d.text((r[0] + 104, r[1] + 84), 'Julián dejó una reseña de 5 estrellas.', font=F('Inter-SemiBold.otf', 19), fill=(110, 110, 120), anchor='lm')
        d.text((r[0] + 104, r[1] + 114), 'Apruébala para mostrarla.', font=F('Inter-SemiBold.otf', 19), fill=(110, 110, 120), anchor='lm')
    q2 = t - wt(7, 'revisa')
    if q2 > 0:
        rc = (90, 660, 630, 800); review_card(im, rc, 'Julián', '«Excelente corte»'); d = BD(im)
        apr = ease((t - wt(7, 'aprueba') - .1) / .3)
        d.rounded_rectangle((120, 830, 360, 890), 30, fill=mix((200, 202, 210), GREEN_OK, max(.5, apr))); d.text((240, 860), 'Aprobar', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
        d.rounded_rectangle((380, 830, 600, 890), 30, fill=(230, 230, 236)); d.text((490, 860), 'Rechazar', font=F('Inter-Black.otf', 24), fill=(120, 120, 130), anchor='mm')
        tq = t - wt(7, 'aprueba') - .1
        if 0 < tq < .5: rr = 20 + tq * 140; d.ellipse((240 - rr, 860 - rr, 240 + rr, 860 + rr), outline=(37, 190, 100, int(255 * (1 - tq / .5))), width=5)
    q3 = t - wt(7, 'publican')
    if q3 > 0: chip(im, 360, 1000, 'SOLO SE PUBLICAN LAS QUE ÉL APRUEBA', q3, size=20)
    obj('in', (220, 960, 500, 1020)); obj('out', (90, 660, 630, 800)); return im

REV = [('Julián', '«Excelente corte»', 5), ('Andrés', '«Puntual y muy limpio»', 5), ('Camilo', '«El mejor del barrio»', 5)]
def sc8(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((186, 440, 534, 520), fill=(36, 36, 40)); d.text((360, 480), 'Wilmer Barber', font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
    q = t - wt(8, 'sección')
    mask_text(im, (360, 560), 'Lo que dicen mis clientes', F('Inter-Black.otf', 24), GOLD, q / .4)
    last = (200, 600, 520, 740)
    for k, (n, tx, s_) in enumerate(REV):
        a = ease((q - .3 - k * .2) / .4)
        if a <= 0: continue
        y = 600 + k * 160 + (1 - a) * 30; last = (200, y, 520, y + 140)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); review_card(L, last, n, tx, s_); L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L)
    obj('in', (90, 660, 630, 800)); obj('out', (200, 600, 520, 740)); return im

def sc9(t, lt):
    im = BGBA.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); wilmer(dl, 200, 760, 1.7)
    a = ease(lt / .8); figure(dl, lerp(W + 60, 520, a), 770, 1.6, (200, 140, 60), skin=(200, 150, 112), long=True, bob=-abs(math.sin(t * 9)) * 5 * (1 - a)); im.alpha_composite(L)
    bubble(im, 260, 480, 'Vi que te recomiendan', t - wt(9, 'vi') + .1, col=(200, 140, 60), size=30)
    q = t - wt(9, 'recomiendan')
    if q > 0: d = BD(im); stars(d, 520, 600, 16, filled=5 * ease(q / .6))
    obj('in', (200, 600, 520, 740)); obj('out', (260, 480, 660, 560)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    q = ease((t - wt(10, 'clientes')) / .6)
    for k in range(5):
        a = back_out((t - wt(10, 'clientes') - k * .1) / .35)
        if a > 0: star(d, 140 + k * 110, 640, 44 * a, fill=GOLD)
    q = t - wt(10, 'publicidad')
    if q > -.2: mask_text(im, (360, 790), 'TU MEJOR PUBLICIDAD', F('Inter-Black.otf', 46), WHITE, (q + .2) / .4)
    chip(im, 360, 1000, 'RESEÑAS EN MI NEGOCIO · CON TU MEMBRESÍA', t - wt(10, 'membresía'), size=18)
    obj('in', (260, 480, 660, 560)); obj('out', (90, 590, 630, 690)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Negocio · Reseñas', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tú apruebas lo que se publica', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    if a > .5: stars(BD(im), W / 2, y + 252, 14, filled=5 * ease((lt - .6) / .6))
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'hablen')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Deja que tus clientes', F('Inter-BlackItalic.otf', 40), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 792), 'hablen por ti.', F('Inter-BlackItalic.otf', 40), WHITE, (q + .1) / .4)
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
