"""Día 49 — "Hago muebles. Llamar." (historia: un carpintero usa los textos con IA de su portada de Sumiago para contar lo que hace).
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
KEY = {'ramiro', 'carpintero', 'preciosos', 'llamar', 'pereza', 'nada', 'mesa', 'perfecta', 'contarlo', 'sumiago', 'inteligencia', 'artificial', 'línea', 'tono', 'cercano', 'segundos', '3',
       'él', 'botones', 'descripciones', 'catálogo', 'copió', 'palabra', 'voz', 'decir', 'muebles', 'mostrarlos', 'blanco', 'membresía', 'link', 'trabajo…', 'trabajo', 'ayuden'}
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
        mask_text(im, (W // 2, 800), 'Que las palabras te ayuden', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
WOOD2 = (176, 120, 70)
# ---------- objetos ----------
def ramiro(d, x, y, s, bob=0):
    figure(d, x, y, s, (90, 120, 80), skin=(206, 156, 116), hair=(70, 50, 36), bob=bob)
    d.rounded_rectangle((x - 18 * s, y + 24 * s + bob, x + 18 * s, y + 76 * s + bob), 6 * s, fill=(150, 110, 70))   # delantal de cuero
def mesa(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 170 * s, cy - 20 * s, cx + 170 * s, cy + 6 * s), 6 * s, fill=WOOD2)
    for k in range(4): d.line((cx - 160 * s + k * 100 * s, cy - 16 * s, cx - 100 * s + k * 100 * s, cy - 4 * s), fill=mix(WOOD2, (0, 0, 0), .15), width=max(1, int(3 * s)))
    for x in (cx - 150 * s, cx + 136 * s): d.rectangle((x, cy + 6 * s, x + 14 * s, cy + 140 * s), fill=mix(WOOD2, (0, 0, 0), .2))
def taller_bg():
    im = gradient((246, 232, 210), (226, 204, 172)); d = BD(im)
    for k in range(7): d.rectangle((0, 330 + k * 80, W, 400 + k * 80), fill=(214, 188, 150) if k % 2 else (222, 198, 162)); d.line((0, 400 + k * 80, W, 400 + k * 80), fill=(190, 160, 120), width=2)
    d.rectangle((0, 920, W, H), fill=(150, 104, 64))
    rr = random.Random(3)
    for k in range(40): x = rr.random() * W; y = 930 + rr.random() * 300; d.ellipse((x - 3, y - 2, x + 3, y + 2), fill=(220, 190, 140))
    return im
BGT = taller_bg()
BIO_OLD = 'Hago muebles. Llamar.'
BIOS = ['Muebles a tu medida en madera maciza, hechos con cariño en mi taller. ¡Escríbeme!',
        'Carpintería de barrio con acabados de lujo. Diseñemos juntos tu próximo mueble.',
        'Mesas, closets y cocinas que duran toda la vida. Pide tu cotización hoy.']
BTNS = ['Ver mis trabajos', 'Cotiza tu mueble', 'Escríbeme por WhatsApp', 'Así trabajo', 'Opiniones', 'Visita el taller']
def portada_r(im, cx, cy, s, bio, btns, t):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 110 * s), fill=WOOD2); d.ellipse((cx - 36 * s, y0 + 20 * s, cx + 36 * s, y0 + 92 * s), fill=(250, 240, 220))
    Lf = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ramiro(ImageDraw.Draw(Lf), cx, y0 + 70 * s, .9 * s); m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((cx - 34 * s, y0 + 22 * s, cx + 34 * s, y0 + 90 * s), fill=255); Lf.putalpha(ImageChops.multiply(Lf.getchannel('A'), m)); im.alpha_composite(Lf); d = BD(im)
    d.text((cx, y0 + 140 * s), 'Ramiro Carpintería', font=F('Inter-Black.otf', int(24 * s)), fill='white', anchor='mm')
    # bio en varias líneas
    f = F('Inter-SemiBold.otf', int(18 * s)); words = bio.split(); lines = ['']; 
    for wd in words:
        if d.textlength(lines[-1] + ' ' + wd, font=f) > w - 70: lines.append(wd)
        else: lines[-1] = (lines[-1] + ' ' + wd).strip()
    for k, l in enumerate(lines): d.text((cx, y0 + 180 * s + k * 26 * s), l, font=f, fill=(220, 220, 228), anchor='mm')
    y = y0 + 200 * s + len(lines) * 26 * s
    for k, b in enumerate(btns):
        d.rounded_rectangle((x0 + 14, y, xe - 14, y + 52 * s), 22 * s, fill=GREEN_OK if 'WhatsApp' in b else (60, 62, 74)); d.text((cx, y + 26 * s), b, font=F('Inter-Black.otf', int(19 * s)), fill='white', anchor='mm'); y += 66 * s
    return (cx - 190 * s, cy - 375 * s, cx + 190 * s, cy + 375 * s)

# ---------- escenas ----------
def sc0(t, lt):
    im = BGT.copy(); d = BD(im)
    mesa(d, 230, 800, .9)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ramiro(ImageDraw.Draw(L), 120, 760, 1.5); im.alpha_composite(L)
    chip(im, 230, 640, 'MUEBLES PRECIOSOS', t - wt(0, 'preciosos'), col=(36, 36, 40), size=20)
    q = ease((t - wt(0, 'portada') + .2) / .5)
    if q > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); portada_r(L, 530, 700, .62, BIO_OLD, ['Llamar'], t); L.putalpha(L.getchannel('A').point(lambda p: int(p * q))); im.alpha_composite(L)
    q = t - wt(0, 'llamar')
    if q > 0: stamp(im, 530, 1080, ['¿ESO ES TODO?'], RED, q, ang=-6, size=40)
    im = camera(im, lerp(1.15, 1.0, ease(lt / 3)), 360, 720)
    obj('in', (60, 780, 420, 940)); obj('out', (412, 467, 648, 933)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 740, 1.1, None); im.alpha_composite(L); d = BD(im)
    d.text((240, 560), 'Escribe tu bio…', font=F('Inter-SemiBold.otf', 24), fill=(150, 150, 160), anchor='lm')
    if int(t * 2.2) % 2: d.rectangle((240, 600, 244, 640), fill='white')
    q = t - wt(1, 'nada')
    if q > 0: chip(im, 360, 1110, 'NO SE LE OCURRÍA NADA', q, col=(36, 36, 40), size=26)
    obj('in', (412, 467, 648, 933)); obj('out', (195, 410, 525, 1070)); return im

def sc2(t, lt):
    im = BGT.copy(); d = BD(im)
    mesa(d, 360, 760, 1.2)
    q = ease((t - wt(2, 'perfecta')) / .5)
    if q > 0: d.rounded_rectangle((300, 700, 420, 724), 8, fill=(240, 200, 40)); d.ellipse((350, 704, 370, 720), fill=(120, 220, 120)); sparkles(im, 360, 620, t, n=12, rad=180)
    chip(im, 360, 560, 'MESA PERFECTA', t - wt(2, 'perfecta'), col=(36, 36, 40), size=26)
    bubble(im, 160, 420, '¿Y cómo lo cuento?', t - wt(2, 'contarlo') + .2, col=RED, size=32)
    obj('in', (195, 410, 525, 1070)); obj('out', (156, 700, 564, 930)); return im

def editor_ia(im, t, q_in=0.0, tone_q=0.0, opts_q=-1.0, pick_q=-1.0):
    r = (50, 380, 670, 1180); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.rounded_rectangle((80, 410, 400, 460), 25, fill=RED); d.text((240, 435), 'Textos con IA', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    sparkles(im, 380, 420, t, n=6, rad=40); d = BD(im)
    d.text((80, 500), '¿Qué haces?', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
    d.rounded_rectangle((80, 520, 640, 580), 14, fill=(244, 244, 247))
    tx = 'Muebles a la medida en madera maciza'; d.text((100, 550), tx[:int(len(tx) * min(1, max(0, q_in)))], font=F('Inter-Bold.otf', 22), fill=(30, 30, 36), anchor='lm')
    d.text((80, 620), 'Tono', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
    for k, tn in enumerate(['Cercano', 'Profesional', 'Divertido', 'Elegante']):
        f = F('Inter-Bold.otf', 18); x = 80 + k * 142; sel = k == 0 and tone_q > 0
        d.rounded_rectangle((x, 640, x + 132, 684), 22, fill=RED if sel else (240, 240, 244)); d.text((x + 66, 662), tn, font=f, fill='white' if sel else (90, 90, 100), anchor='mm')
    for k, b in enumerate(BIOS):
        a = ease((opts_q - k * .2) / .4)
        if a <= 0: continue
        y = 720 + k * 145; sel = k == 0 and pick_q > 0
        d.rounded_rectangle((80, y + (1 - a) * 20, 640, y + 130 + (1 - a) * 20), 16, fill=(255, 244, 244) if sel else (244, 244, 247), outline=RED if sel else None, width=4 if sel else 1)
        f = F('Inter-SemiBold.otf', 19); words = b.split(); lines = ['']
        for wd in words:
            if d.textlength(lines[-1] + ' ' + wd, font=f) > 500: lines.append(wd)
            else: lines[-1] = (lines[-1] + ' ' + wd).strip()
        for j, l in enumerate(lines[:3]): d.text((100, y + 28 + j * 30), l, font=f, fill=(40, 40, 46), anchor='lm')
        if sel: d.ellipse((590, y + 10, 630, y + 50), fill=GREEN_OK); d.line((600, y + 30, 608, y + 40, 622, y + 22), fill='white', width=4)
    return r

def sc3(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    a = ease((t - wt(3, 'botón') + .2) / .5)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); editor_ia(L, t); L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L, (0, int((1 - a) * 40)))
    tq = t - wt(3, 'textos') - .1
    if 0 < tq < .5: d = BD(im); rr = 20 + tq * 140; d.ellipse((240 - rr, 435 - rr, 240 + rr, 435 + rr), outline=(255, 255, 255, int(255 * (1 - tq / .5))), width=5)
    chip(im, 360, 340, 'INTELIGENCIA ARTIFICIAL', t - wt(3, 'inteligencia'), col=WHITE, tcol=RED, size=24)
    obj('in', (156, 700, 564, 930)); obj('out', (80, 410, 400, 460)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    editor_ia(im, t, q_in=(t - wt(4, 'línea') + .2) / 1.0, tone_q=t - wt(4, 'cercano'))
    im = camera(im, 1.15, 360, 600)
    obj('in', (80, 410, 400, 460)); obj('out', (80, 640, 212, 684)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    editor_ia(im, t, q_in=9, tone_q=9, opts_q=t - wt(5, 'segundos') + .1, pick_q=t - wt(5, 'escogió'))
    q = t - wt(5, 'él')
    if q > 0: chip(im, 360, 1230, 'LA QUE MÁS SE PARECÍA A ÉL', q, col=WHITE, tcol=RED, size=22)
    fq = ease((t - wt(5, 'segundos')) / 1.0)
    im = camera(im, 1.0 + .1 * fq, 360, lerp(700, 900, fq))
    obj('in', (80, 640, 212, 684)); obj('out', (80, 720, 640, 850)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90)); d = BD(im)
    r = (50, 390, 670, 760); card(im, r, (255, 255, 255), 22); d = BD(im); d.text((80, 430), 'Ideas para tus botones', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
    for k, b in enumerate(BTNS):
        a = back_out((t - wt(6, 'botones') - k * .1) / .3)
        if a > 0:
            x = 80 + (k % 2) * 290; y = 470 + (k // 2) * 90; d.rounded_rectangle((x, y, x + 270 * a, y + 70), 20, fill=(244, 244, 247))
            if a > .8: d.text((x + 135, y + 35), b, font=F('Inter-Bold.otf', 19), fill=(30, 30, 36), anchor='mm')
    r2 = (50, 800, 670, 1180); card(im, r2, (255, 255, 255), 22); d = BD(im); d.text((80, 840), 'Descripciones del catálogo', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
    descs = [('Mesa de comedor', 'Roble macizo para 6 personas, hecha para durar generaciones.'), ('Closet a medida', 'Aprovecha cada centímetro con un diseño hecho para tu espacio.')]
    for k, (n, dsc) in enumerate(descs):
        a = ease((t - wt(6, 'descripciones') - k * .25) / .4)
        if a > 0:
            y = 880 + k * 140; mesa(d, 140, y + 60, .25)
            d.text((210, y + 30), n, font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm')
            n2 = int(len(dsc) * a); d.text((210, y + 66), dsc[:n2][:38], font=F('Inter-SemiBold.otf', 17), fill=(90, 90, 100), anchor='lm'); d.text((210, y + 92), dsc[:n2][38:], font=F('Inter-SemiBold.otf', 17), fill=(90, 90, 100), anchor='lm')
    obj('in', (80, 720, 640, 850)); obj('out', (50, 800, 670, 1180)); return im

def sc7(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    r = (60, 470, 660, 760); card(im, r, (255, 255, 255), 22); d = BD(im)
    t1 = 'Muebles a tu medida en madera maciza,'; t2a = 'hechos con cariño en mi taller.'; t2b = 'hechos a mano en mi taller del barrio.'
    d.text((90, 560), t1, font=F('Inter-Bold.otf', 26), fill=(30, 30, 36), anchor='lm')
    sw = ease((t - wt(7, 'palabra') + .1) / .6)
    txt = t2a if sw < .5 else t2b
    d.text((90, 610), txt, font=F('Inter-Bold.otf', 26), fill=RED if sw >= .5 else (30, 30, 36), anchor='lm')
    if int(t * 3) % 2: d.rectangle((90 + d.textlength(txt, font=F('Inter-Bold.otf', 26)) + 4, 592, 94 + d.textlength(txt, font=F('Inter-Bold.otf', 26)) + 4, 628), fill=(30, 30, 36))
    d.text((90, 670), '¡Escríbeme!', font=F('Inter-Bold.otf', 26), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 420, 'NO LO COPIÓ TAL CUAL', t - wt(7, 'copió'), col=(36, 36, 40), size=24)
    q = t - wt(7, 'voz')
    if q > 0: stamp(im, 360, 900, ['CON SU VOZ'], RED, q, ang=-6, size=56)
    obj('in', (50, 800, 670, 1180)); obj('out', r); return im

def sc8(t, lt):
    im = BGT.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 60)))
    bio = 'Muebles a tu medida en madera maciza, hechos a mano en mi taller del barrio. ¡Escríbeme!'
    r = portada_r(im, 360, 800, 1.0, bio, BTNS[:4], t)
    sparkles(im, 360, 700, t, n=10, rad=200)
    obj('in', (60, 470, 660, 760)); obj('out', r); return im

def sc9(t, lt):
    im = BGT.copy(); d = BD(im)
    mesa(d, 360, 820, 1.3)
    q = t - wt(9, 'muebles')
    if q > -.2: mask_text(im, (360, 470), 'La IA no hizo los muebles.', F('Inter-Black.otf', 38), (30, 30, 36), (q + .2) / .4)
    q2 = t - wt(9, 'mostrarlos')
    if q2 > -.2:
        mask_text(im, (360, 540), 'Le ayudó a mostrarlos.', F('Inter-Black.otf', 38), RED, (q2 + .2) / .4)
        im.alpha_composite(glow_layer(lambda dd: dd.ellipse((140, 700, 580, 900), fill=255), GOLD, 50, int(150 * ease(q2 / .6))))
    obj('in', (172, 425, 548, 1175)); obj('out', (140, 790, 580, 1000)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    q = ease((t - wt(10, 'blanco')) / .5)
    r1 = (80, 480, 330, 800); card(im, r1, (255, 255, 255), 18); d = BD(im)
    if int(t * 2.2) % 2: d.rectangle((110, 520, 114, 556), fill=(30, 30, 36))
    d.text((205, 760), 'En blanco', font=F('Inter-Black.otf', 22), fill=(150, 150, 160), anchor='mm')
    a = ease((t - wt(10, 'inteligencia') + .1) / .5)
    r2 = (390, 480, 640, 800); card(im, r2, (255, 255, 255), 18); d = BD(im)
    for k in range(6):
        if a * 6 > k: d.rounded_rectangle((414, 520 + k * 34, 414 + [200, 180, 205, 150, 190, 120][k], 540 + k * 34), 6, fill=(225, 225, 232))
    d.text((515, 760), 'Con IA', font=F('Inter-Black.otf', 22), fill=RED, anchor='mm')
    if a > 0: sparkles(im, 515, 620, t, n=8, rad=100)
    chip(im, 360, 900, 'TEXTOS CON IA · CON TU MEMBRESÍA', t - wt(10, 'membresía'), size=20)
    obj('in', (140, 790, 580, 1000)); obj('out', (390, 480, 640, 800)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Textos con IA', F('Inter-Black.otf', 34), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Bio, botones y descripciones', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'PORTADA PRO', t - wt(11, 'regístrate'), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'trabajo')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Tú haces el trabajo…', F('Inter-BlackItalic.otf', 40), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 792), 'deja que las palabras te ayuden.', F('Inter-BlackItalic.otf', 36), WHITE, (t - wt(11, 'palabras') + .3) / .4)
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
