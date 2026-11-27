"""Día 56 — "El letrero que hablaba" (historia: don Gilberto cambia su cartón de «Se vende» por el afiche imprimible del Marketplace de Sumiago, con fotos, QR y código de referencia).
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
KEY = {'gilberto', 'carro', 'cartón', 'vende»', 'seguía', 'precio', 'dentro', 'nadie', 'desconocido', 'hija', 'marketplace', 'sumiago', 'fotos', 'imprimir', 'afiche', 'vende', 'whatsapp', 'qr', 'qr…', 'escanea', 'referencia', 'paso', 'semáforo', 'escaneó', 'bajarse', 'probar', 'link', 'letrero…', 'hable'}
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
        mask_text(im, (W // 2, 800), 'Imprime tu afiche', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); WA = (37, 211, 102)
def gilberto(d, x, y, s, bob=0): figure(d, x, y, s, (110, 110, 70), skin=(204, 150, 110), hair=(180, 180, 186), bob=bob)
def hija(d, x, y, s, bob=0): figure(d, x, y, s, (200, 60, 90), skin=(210, 160, 124), hair=(50, 30, 22), long=True, bob=bob)
def carro(d, cx, by, s, col=(60, 110, 170)):
    d.rounded_rectangle((cx - 170 * s, by - 90 * s, cx + 170 * s, by - 30 * s), 22 * s, fill=col)
    d.polygon([(cx - 100 * s, by - 88 * s), (cx - 62 * s, by - 150 * s), (cx + 70 * s, by - 150 * s), (cx + 112 * s, by - 88 * s)], fill=col)
    d.polygon([(cx - 84 * s, by - 92 * s), (cx - 54 * s, by - 140 * s), (cx - 2 * s, by - 140 * s), (cx - 2 * s, by - 92 * s)], fill=(200, 226, 244))
    d.polygon([(cx + 8 * s, by - 92 * s), (cx + 8 * s, by - 140 * s), (cx + 64 * s, by - 140 * s), (cx + 96 * s, by - 92 * s)], fill=(200, 226, 244))
    for wx in (cx - 100 * s, cx + 100 * s): d.ellipse((wx - 36 * s, by - 66 * s, wx + 36 * s, by + 6 * s), fill=(30, 30, 34)); d.ellipse((wx - 15 * s, by - 45 * s, wx + 15 * s, by - 15 * s), fill=(170, 170, 176))
    d.ellipse((cx + 150 * s, by - 80 * s, cx + 166 * s, by - 64 * s), fill=(255, 230, 140))
def carton(d, cx, cy, s):
    d.rectangle((cx - 40 * s, cy - 26 * s, cx + 40 * s, cy + 26 * s), fill=(196, 160, 110)); d.text((cx, cy - 8 * s), 'SE VENDE', font=F('Inter-Black.otf', max(6, int(13 * s))), fill=(40, 30, 20), anchor='mm'); d.text((cx, cy + 12 * s), '300 …', font=F('Inter-Bold.otf', max(6, int(11 * s))), fill=(40, 30, 20), anchor='mm')
def qr(d, x, y, sz, seed=3):
    rnd = random.Random(seed); n = 21; c = sz / n
    d.rectangle((x, y, x + sz, y + sz), fill='white')
    for i in range(n):
        for j in range(n):
            fin = (i < 7 and j < 7) or (i < 7 and j >= n - 7) or (i >= n - 7 and j < 7)
            if fin:
                ii, jj = i % (n - 7) if i >= n - 7 else i, j % (n - 7) if j >= n - 7 else j
                on = ii in (0, 6) or jj in (0, 6) or (2 <= ii <= 4 and 2 <= jj <= 4)
            else: on = rnd.random() < .48
            if on: d.rectangle((x + j * c, y + i * c, x + (j + 1) * c, y + (i + 1) * c), fill=(20, 20, 24))
def afiche(im, r, t, hl=None):
    hl = hl or {}
    x0, y0, x1, y1 = r; w = x1 - x0; s = w / 520
    card(im, r, (255, 255, 255), 6); d = BD(im)
    d.rectangle((x0, y0, x1, y0 + 120 * s), fill=RED); d.text(((x0 + x1) / 2, y0 + 62 * s), 'SE VENDE', font=F('Inter-Black.otf', int(70 * s)), fill='white', anchor='mm')
    d.text((x0 + 24 * s, y0 + 150 * s), 'Sumiago.com · Ref. #1834', font=F('Inter-Bold.otf', int(16 * s)), fill=(120, 120, 130), anchor='lm')
    d.text((x0 + 24 * s, y0 + 190 * s), 'Carro familiar 2016', font=F('Inter-Black.otf', int(30 * s)), fill=(30, 30, 36), anchor='lm')
    for k in range(4):
        px = x0 + 24 * s + (k % 2) * 240 * s; py = y0 + 220 * s + (k // 2) * 150 * s
        d.rounded_rectangle((px, py, px + 230 * s, py + 140 * s), 8, fill=[(214, 230, 244), (226, 236, 222), (240, 232, 218), (230, 224, 240)][k])
        if k == 0: carro(d, px + 115 * s, py + 120 * s, .6 * s)
        elif k == 1: d.ellipse((px + 75 * s, py + 30 * s, px + 155 * s, py + 110 * s), outline=(40, 40, 46), width=max(2, int(10 * s)))
        elif k == 2: d.rounded_rectangle((px + 40 * s, py + 40 * s, px + 190 * s, py + 110 * s), 12, fill=(120, 90, 70))
        else: d.rounded_rectangle((px + 60 * s, py + 50 * s, px + 170 * s, py + 100 * s), 10, fill=(60, 60, 70))
    if hl.get('fotos', 0) > 0 and hl['fotos'] < 1.2: d.rounded_rectangle((x0 + 18 * s, y0 + 214 * s, x0 + 500 * s, y0 + 516 * s), 12, outline=GOLD, width=5)
    d.text((x0 + 24 * s, y0 + 560 * s), '$ 38.000.000', font=F('Inter-Black.otf', int(40 * s)), fill=RED, anchor='lm')
    if 0 < hl.get('precio', 0) < 1.2: d.rounded_rectangle((x0 + 16 * s, y0 + 530 * s, x0 + 330 * s, y0 + 590 * s), 10, outline=GOLD, width=5)
    d.text((x0 + 24 * s, y0 + 610 * s), 'Pereira, Colombia', font=F('Inter-Bold.otf', int(20 * s)), fill=(90, 90, 100), anchor='lm')
    if 0 < hl.get('ciudad', 0) < 1.2: d.rounded_rectangle((x0 + 16 * s, y0 + 592 * s, x0 + 230 * s, y0 + 628 * s), 10, outline=GOLD, width=5)
    d.line((x0 + 20 * s, y0 + 650 * s, x1 - 20 * s, y0 + 650 * s), fill=(226, 226, 232), width=2)
    d.text((x0 + 24 * s, y0 + 690 * s), 'INTERESADOS', font=F('Inter-Black.otf', int(18 * s)), fill=RED, anchor='lm')
    d.text((x0 + 24 * s, y0 + 724 * s), 'WhatsApp: 300 555 0199', font=F('Inter-Black.otf', int(22 * s)), fill=(30, 30, 36), anchor='lm')
    if 0 < hl.get('wa', 0) < 1.2: d.rounded_rectangle((x0 + 16 * s, y0 + 704 * s, x0 + 320 * s, y0 + 744 * s), 10, outline=GOLD, width=5)
    qx = x1 - 140 * s; qy = y0 + 668 * s; qr(d, qx, qy, 116 * s)
    d.text((x0 + 24 * s, y0 + 758 * s), 'Escanea el QR y mira todas las fotos', font=F('Inter-Bold.otf', int(14 * s)), fill=(82, 82, 91), anchor='lm')
    if 0 < hl.get('qr', 0) < 1.5: d.rounded_rectangle((qx - 8 * s, qy - 8 * s, qx + 124 * s, qy + 124 * s), 10, outline=GOLD, width=5)
    if 0 < hl.get('ref', 0): d.rounded_rectangle((x0 + 16 * s, y0 + 134 * s, x0 + 290 * s, y0 + 166 * s), 8, outline=GOLD, width=4)
    return (qx, qy, qx + 116 * s, qy + 116 * s)

def street(im):
    d = BD(im); d.rectangle((0, 960, W, H), fill=(120, 124, 132)); d.rectangle((0, 960, W, 990), fill=(190, 190, 196))
    for k in range(6): d.rectangle((k * 140 + 20, 1110, k * 140 + 90, 1122), fill=(240, 240, 240))

def sc0(t, lt):
    im = gradient((200, 226, 246), (226, 236, 246)); street(im); d = BD(im)
    carro(d, 420, 1000, 1.4)
    q = t - wt(0, 'cartón')
    if q > 0: carton(d, 420 + 50 * 1.4, 1000 - 116 * 1.4, 1.2 * back_out(q / .35))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gilberto(ImageDraw.Draw(L), 120, 800, 1.6); im.alpha_composite(L)
    f = ease((t - wt(0, 'cartón')) / 1.2); im = camera(im, 1.0 + .9 * f, lerp(380, 490, f), lerp(860, 840, f))
    obj('in', (250, 790, 590, 1000)); obj('out', (442, 800, 538, 862)); return im

def sc1(t, lt):
    im = gradient((200, 226, 246), (226, 236, 246)); street(im); d = BD(im)
    carro(d, 360, 1000, 1.4); carton(d, 430, 838, 1.2)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(3):
        x = (-120 + (t - ct(1)) * 130 + k * 260) % (W + 240) - 120
        figure(dl, x, 830, 1.2, [(90, 120, 200), (200, 120, 60), (90, 160, 90)][k], bob=-abs(math.sin(t * 7 + k)) * 3)
    im.alpha_composite(L)
    q = t - wt(1, 'precio')
    if q > 0: bubble(im, 60, 460, '¿Precio?', q, col=(150, 150, 160), size=30)
    q = t - wt(1, 'dentro')
    if q > 0: bubble(im, 330, 560, '¿Cómo está por dentro?', q, col=(150, 150, 160), size=26)
    q = t - wt(1, 'seguía')
    if q > 0: chip(im, 360, 400 if t < wt(1, 'precio') else 1180, 'Y SEGUÍAN', q, col=(36, 36, 40), size=26)
    obj('in', (442, 800, 538, 862)); obj('out', (190, 790, 530, 1000)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), 360, 720, 1.8, (90, 120, 200)); im.alpha_composite(L); d = BD(im)
    q = t - wt(2, 'desconocido')
    if q > 0:
        d.rounded_rectangle((470, 560, 610, 700), 20, fill=(40, 40, 46)); d.text((540, 600), 'Llamar', font=F('Inter-Bold.otf', 20), fill='white', anchor='mm'); d.text((540, 650), '300 …', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
        if q > .4: d.line((470, 700, 610, 560), fill=RED, width=8)
    q = t - wt(2, 'nadie')
    if q > 0: stamp(im, 360, 1100, ['CASI NADIE LLAMA'], RED, q, ang=-5, size=46)
    obj('in', (190, 790, 530, 1000)); obj('out', (320, 720, 400, 960)); return im

def listing_car(im, cx, cy, s, t, hlb=0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'MARKETPLACE', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 50 * s, xe, y0 + 270 * s), fill=(214, 230, 244)); carro(d, cx, y0 + 250 * s, .8 * s)
    d.text((x0 + 16, y0 + 296 * s), 'Carro familiar 2016', font=F('Inter-Black.otf', int(22 * s)), fill='white', anchor='lm')
    d.text((x0 + 16, y0 + 334 * s), '$ 38.000.000', font=F('Inter-Black.otf', int(26 * s)), fill=GREEN_OK, anchor='lm')
    d.rounded_rectangle((x0 + 14, y0 + 370 * s, xe - 14, y0 + 426 * s), 26 * s, fill=RED); d.text((cx, y0 + 398 * s), '¡Lo quiero!', font=F('Inter-Black.otf', int(22 * s)), fill='white', anchor='mm')
    br = (xe - 170 * s, y0 + 446 * s, xe - 14, y0 + 496 * s)
    d.rounded_rectangle(br, 25 * s, fill=(240, 240, 244), outline=GOLD if hlb > 0 else None, width=4); d.text(((br[0] + br[2]) / 2, (br[1] + br[3]) / 2), '🖨 Imprimir' if False else 'Imprimir', font=F('Inter-Black.otf', int(19 * s)), fill=(30, 30, 36), anchor='mm')
    return br

def sc3(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); hija(dl, 110, 860, 1.5); gilberto(dl, 220, 860, 1.5); im.alpha_composite(L)
    listing_car(im, 480, 720, .78, t)
    q = t - wt(3, 'fotos')
    if q > 0: chip(im, 480, 1110, 'CON FOTOS Y PRECIO', q, col=(36, 36, 40), size=22)
    obj('in', (320, 720, 400, 960)); obj('out', (344, 448, 616, 992)); return im

def sc4(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    q = t - wt(4, 'imprimir')
    br = listing_car(im, 360, 740, 1.0, t, hlb=q + .4); d = BD(im)
    if 0 < q < .5: rr = 20 + q * 140; cx, cy = (br[0] + br[2]) / 2, (br[1] + br[3]) / 2; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(230, 38, 47, int(255 * (1 - q / .5))), width=5)
    f = ease((t - wt(4, 'botón')) / .8); im = camera(im, 1.0 + .5 * f, lerp(360, (br[0] + br[2]) / 2, f), lerp(740, br[1], f))
    obj('in', (172, 365, 548, 1115)); obj('out', br); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    p = ease((t - ct(5)) / 1.0); r = (100, 1260 - 900 * p, 620, 1260 - 900 * p + 780)
    hl = {'fotos': t - wt(5, 'fotos'), 'precio': t - wt(5, 'precio'), 'ciudad': t - wt(5, 'ciudad')}
    afiche(im, r, t, hl)
    d = BD(im); d.rounded_rectangle((60, 1150, 660, H), 24, fill=(60, 62, 70)); d.rectangle((90, 1150, 630, 1170), fill=(20, 20, 24))
    q = t - wt(5, 'vende')
    if 0 < q < 1: d.rounded_rectangle((r[0] - 6, r[1] - 6, r[2] + 6, r[1] + 126), 10, outline=GOLD, width=6)
    obj('in', (420, 640, 560, 690)); obj('out', (100, 360, 620, 1140)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    r = (100, 360, 620, 1140); qrr = afiche(im, r, t, {'wa': t - wt(6, 'whatsapp'), 'qr': t - wt(6, 'qr')})
    f = ease((t - ct(6)) / 1.0); im = camera(im, 1.0 + .5 * f, lerp(360, 400, f), lerp(750, 1000, f))
    obj('in', (100, 360, 620, 1140)); obj('out', qrr); return im

def sc7(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    q = t - wt(7, 'encontrar')
    if q < 0:
        r = (100, 360, 620, 1140); afiche(im, r, t, {'ref': t - wt(7, 'referencia') + .3})
        f = ease((t - ct(7)) / .8); im = camera(im, 1.0 + .8 * f, lerp(360, 220, f), lerp(750, 510, f))
    else:
        d = BD(im); d.text((360, 430), 'Sumiago.com', font=F('Inter-Black.otf', 34), fill='white', anchor='mm')
        d.rounded_rectangle((80, 480, 640, 560), 40, fill=(255, 255, 255)); v = '#1834'; n = int(len(v) * ease(q / .5))
        d.text((130, 520), v[:n], font=F('Inter-Black.otf', 32), fill=(30, 30, 36), anchor='lm'); d.ellipse((570, 496, 618, 544), fill=RED)
        if q > .7:
            a = back_out((q - .7) / .35); card(im, (80, 600, 80 + 560 * a, 760), (255, 255, 255), 18); d = BD(im)
            if a > .8: d.rounded_rectangle((96, 616, 236, 744), 12, fill=(214, 230, 244)); carro(d, 166, 730, .35); d.text((256, 650), 'Carro familiar 2016', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm'); d.text((256, 700), '$ 38.000.000', font=F('Inter-Black.otf', 26), fill=GREEN_OK, anchor='lm')
        q2 = t - wt(7, 'paso')
        if q2 > 0: chip(im, 360, 880, 'EN UN SOLO PASO', q2, col=WHITE, tcol=RED, size=26)
    obj('in', (420, 980, 540, 1100)); obj('out', (80, 600, 640, 760)); return im

def sc8(t, lt):
    im = gradient((250, 200, 150), (236, 220, 200)); street(im); d = BD(im)
    d.rectangle((640, 480, 660, 980), fill=(50, 50, 56)); d.rounded_rectangle((610, 430, 690, 600), 14, fill=(30, 30, 34))
    for k, c in enumerate([(240, 60, 60), (90, 70, 40), (40, 80, 50)]): d.ellipse((628, 446 + k * 52, 672, 490 + k * 52), fill=c)
    carro(d, 210, 1000, 1.3)
    a = afiche_mini = (210 + 4 * 1.3 + 8, 1000 - 136 * 1.3, 210 + 4 * 1.3 + 48, 1000 - 136 * 1.3 + 54)
    d.rectangle(a, fill=(255, 255, 255)); d.rectangle((a[0], a[1], a[2], a[1] + 9), fill=RED); qr(d, a[0] + 14, a[1] + 30, 20)
    q = ease((t - wt(8, 'semáforo') + .6) / .8)
    carro(d, lerp(900, 520, q), 1150, 1.1, col=(180, 60, 60))
    qs = t - wt(8, 'escaneó')
    if qs > 0:
        px, py = lerp(900, 520, q) - 10, 1150 - 120
        d.rounded_rectangle((px - 20, py - 34, px + 20, py + 34), 6, fill=(30, 30, 34))
        if qs < 1.2: d.polygon([(px - 18, py - 10), ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2 - 10), ((a[0] + a[2]) / 2, (a[1] + a[3]) / 2 + 10), (px - 18, py + 10)], fill=(255, 230, 120, 110))
    qv = t - wt(8, 'vio')
    if qv > 0:
        b = back_out(qv / .35); r = (360 - 170 * b, 360, 360 + 170 * b, 720); card(im, r, (20, 20, 24), 26); d = BD(im)
        if b > .8:
            for k in range(4):
                px = 210 + (k % 2) * 154; py = 400 + (k // 2) * 150
                d.rounded_rectangle((px, py, px + 144, py + 140), 10, fill=[(214, 230, 244), (226, 236, 222), (240, 232, 218), (230, 224, 240)][k])
                if k == 0: carro(d, px + 72, py + 120, .38)
    q = t - wt(8, 'bajarse')
    if q > 0: chip(im, 360, 780, 'SIN BAJARSE', q, col=RED, size=26)
    obj('in', (80, 600, 640, 760)); obj('out', (190, 360, 530, 720)); return im

def sc9(t, lt):
    im = gradient((228, 221, 212), (205, 198, 188)); d = BD(im)
    d.rectangle((0, 290, W, 370), fill=(7, 94, 84)); d.text((40, 330), 'WhatsApp · Don Gilberto', font=F('Inter-Black.otf', 28), fill='white', anchor='lm')
    q = t - wt(9, 'ya') + .1
    if q > 0:
        a = back_out(q / .35); d.rounded_rectangle((60, 440, 60 + 520 * a, 600), 22, fill=(255, 255, 255))
        if a > .8:
            d.text((90, 490), 'Ya vi las fotos. 👍' if False else 'Ya vi las fotos.', font=F('Inter-SemiBold.otf', 30), fill=(30, 30, 36), anchor='lm')
            if t > wt(9, 'me') - .2: d.text((90, 550), '¿Me lo deja probar mañana?', font=F('Inter-SemiBold.otf', 30), fill=(30, 30, 36), anchor='lm')
    q = t - wt(9, 'probar') - .3
    if q > 0:
        a = back_out(q / .35); d.rounded_rectangle((660 - 300 * a, 660, 660, 750), 22, fill=(220, 248, 198))
        if a > .8: d.text((390, 705), '¡Claro que sí!', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm')
    obj('in', (190, 360, 530, 720)); obj('out', (60, 440, 580, 600)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('imprimir', 'Afiche para imprimir'), ('qr', 'QR a todas las fotos'), ('referencia', 'Código de referencia')]
    for k, (w_, lab) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        y = 470 + k * 170; card(im, (360 - 280 * a, y, 360 + 280 * a, y + 130), (250, 250, 250), 22); d = BD(im)
        if a > .7:
            cx, cy = 160, y + 65
            if k == 0: d.rectangle((cx - 30, cy - 40, cx + 30, cy + 40), fill='white', outline=(200, 200, 206), width=3); d.rectangle((cx - 30, cy - 40, cx + 30, cy - 22), fill=RED)
            elif k == 1: qr(d, cx - 36, cy - 36, 72)
            else: d.rounded_rectangle((cx - 46, cy - 24, cx + 46, cy + 24), 12, fill=RED); d.text((cx, cy), '#1834', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
            d.text((230, cy), lab, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 1050, 'MARKETPLACE SUMIAGO', t - wt(10, 'marketplace'), size=24)
    obj('in', (60, 440, 580, 600)); obj('out', (80, 470, 640, 600)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Marketplace Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Imprime tu afiche con QR', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'SE VENDE · FOTOS · QR', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'letrero')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Que tu letrero…', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'hable por ti.', F('Inter-BlackItalic.otf', 44), WHITE, (t - wt(11, 'hable') + .3) / .4)
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
