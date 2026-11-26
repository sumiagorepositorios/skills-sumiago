"""Día 36 — "La moto que no era mía" (historia: Camilo ayuda a vender la moto de su vecino con Dropshipping del Marketplace de Sumiago).
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
KEY = {'moto', 'moto.', 'nunca', '2', 'meses', 'nadie', 'marketplace', 'dropshipping.', 'dropshipping', 'comisión', 'vender.', 'gana', 'enlace', 'whatsapp', 'barrio.',
       'cuarto', 'semana', 'dropshippero', 'ti.', 'hernán.', 'gracias', 'camilo.', 'vendió', 'cumplió', 'voluntario', 'cobra', 'garantiza.', 'tuyas…', 'tuyas', 'link', 'tuya.'}
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
        mask_text(im, (W // 2, 800), 'Ayuda a vender', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
# ---------- objetos ----------
GREEN = (37, 190, 100)
def street_bg(sky=(190, 222, 246), ground=(214, 206, 196)):
    im = gradient(sky, mix(sky, (255, 255, 255), .5)); d = BD(im)
    cols = [(236, 190, 150), (200, 220, 200), (240, 220, 170), (210, 200, 230)]
    for k in range(5):   # casas del barrio
        x = -40 + k * 170; h = 300 + (k % 2) * 60; c = cols[k % 4]
        d.rectangle((x, 900 - h, x + 160, 900), fill=c); d.polygon([(x - 10, 900 - h), (x + 80, 900 - h - 70), (x + 170, 900 - h)], fill=(170, 90, 70))
        d.rectangle((x + 20, 900 - h + 50, x + 70, 900 - h + 110), fill=(150, 200, 230)); d.rectangle((x + 95, 900 - 120, x + 140, 900), fill=(130, 90, 60))
    d.rectangle((0, 900, W, H), fill=ground); d.rectangle((0, 1010, W, 1030), fill=(250, 250, 250))
    return im
BGS = street_bg()

def moto(d, cx, cy, s=1.0, col=RED):
    """Moto sencilla de perfil."""
    r = 62 * s
    for wx in (cx - 120 * s, cx + 120 * s):
        d.ellipse((wx - r, cy - r, wx + r, cy + r), fill=(30, 30, 34)); d.ellipse((wx - r * .55, cy - r * .55, wx + r * .55, cy + r * .55), fill=(200, 200, 206)); d.ellipse((wx - 10 * s, cy - 10 * s, wx + 10 * s, cy + 10 * s), fill=(60, 60, 66))
    d.polygon([(cx - 120 * s, cy), (cx - 40 * s, cy - 70 * s), (cx + 60 * s, cy - 70 * s), (cx + 120 * s, cy)], outline=(60, 60, 66), width=max(2, int(10 * s)))
    d.rounded_rectangle((cx - 60 * s, cy - 120 * s, cx + 50 * s, cy - 60 * s), 26 * s, fill=col)               # tanque
    d.rounded_rectangle((cx - 150 * s, cy - 104 * s, cx - 40 * s, cy - 80 * s), 10 * s, fill=(30, 30, 34))     # sillín
    d.line((cx + 60 * s, cy - 110 * s, cx + 120 * s, cy), fill=(80, 80, 86), width=max(2, int(10 * s)))       # horquilla
    d.line((cx + 40 * s, cy - 150 * s, cx + 90 * s, cy - 125 * s), fill=(30, 30, 34), width=max(2, int(10 * s)))  # manubrio
    d.ellipse((cx + 80 * s, cy - 108 * s, cx + 110 * s, cy - 82 * s), fill=GOLD)                              # farola
    d.rounded_rectangle((cx - 40 * s, cy - 56 * s, cx + 40 * s, cy - 10 * s), 10 * s, fill=(90, 90, 96))      # motor
    return (cx - 190 * s, cy - 160 * s, cx + 190 * s, cy + 70 * s)

def camilo(d, x, y, s, bob=0): figure(d, x, y, s, RED, skin=(200, 146, 110), hair=(30, 22, 20), bob=bob)
def hernan(d, x, y, s, bob=0): figure(d, x, y, s, (80, 120, 100), skin=(226, 186, 150), hair=(200, 200, 206), bob=bob)

def avatar(im, cx, cy, r, who):
    L = Image.new('RGBA', (int(r * 2), int(r * 2) + int(r)), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    (camilo if who == 'c' else hernan)(d, r, r * .9, r / 40)
    m = Image.new('L', L.size, 0); ImageDraw.Draw(m).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=255)
    bg = Image.new('RGBA', L.size, (236, 240, 246, 255) if who == 'c' else (246, 238, 226, 255)); bg.alpha_composite(L); bg.putalpha(m)
    im.alpha_composite(bg.crop((0, 0, int(r * 2), int(r * 2))), (int(cx - r), int(cy - r)))

def listing(im, cx, cy, t, drop_q=1.0, btn_q=0.0, tap=-1.0, s=1.0):
    """Celular con el anuncio de la moto en el Marketplace."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, x0 + w - 28, y0 + 52), fill=(20, 20, 24)); d.text((x0 + 18, y0 + 26), 'MARKETPLACE', font=F('Inter-Black.otf', 20), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 52, x0 + w - 28, y0 + 262), fill=(226, 236, 246)); moto(d, cx, y0 + 200, .55)
    d.text((x0 + 18, y0 + 300), 'Moto 150 cc · 2021', font=F('Inter-Black.otf', 26), fill='white', anchor='lm')
    d.text((x0 + 18, y0 + 340), 'Vendedor: don Hernán', font=F('Inter-SemiBold.otf', 20), fill=(170, 170, 180), anchor='lm')
    if drop_q > 0:
        a = ease(drop_q); yy = y0 + 392
        d.rounded_rectangle((x0 + 14, yy, x0 + w - 42, yy + 52), 14, fill=(34, 36, 48), outline=mix((34, 36, 48), RED, a), width=3)
        d.text((x0 + 32, yy + 26), 'Dropshipping', font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
        tx = x0 + w - 110; d.rounded_rectangle((tx, yy + 12, tx + 52, yy + 40), 14, fill=mix((90, 90, 100), GREEN, a)); d.ellipse((tx + 4 + 24 * a, yy + 15, tx + 26 + 24 * a, yy + 37), fill='white')
    if btn_q > 0:
        b = back_out(btn_q / .35); yy = y0 + 500; bw = (w - 60) / 2 * b
        d.rounded_rectangle((cx - bw, yy - 32 * b, cx + bw, yy + 32 * b), 30, fill=GREEN)
        if b > .6: d.text((cx, yy), 'Gana comisión 5 %', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
        if tap >= 0 and tap < .6:
            rr = 20 + tap * 120; d.ellipse((cx - rr, yy - rr, cx + rr, yy + rr), outline=(255, 255, 255, int(255 * (1 - tap / .6))), width=5)
    return (cx - 190 * s, cy - 375 * s, cx + 190 * s, cy + 375 * s)

def notif(im, x, y, w, who, l1, l2, q):
    if q <= 0: return None
    a = ease(q / .35); y = y - (1 - a) * 40; r = (x, y, x + w, y + 120)
    card(im, r, (255, 255, 255), 22); d = BD(im)
    avatar(im, x + 60, y + 60, 40, who); d = BD(im)
    d.text((x + 116, y + 42), l1, font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm')
    d.text((x + 116, y + 80), l2, font=F('Inter-SemiBold.otf', 21), fill=(110, 110, 120), anchor='lm')
    return r

# ---------- escenas ----------
def sc0(t, lt):
    im = BGS.copy(); d = BD(im)
    mr = moto(d, 400, 900, 1.0)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); camilo(ImageDraw.Draw(L), 140, 760, 1.7); im.alpha_composite(L)
    q = t - wt(0, 'vendió')
    if q > 0: stamp(im, 420, 640, ['VENDIDA'], RED, q, ang=-8, size=56)
    q = t - wt(0, 'nunca')
    if q > 0:
        d = BD(im); d.text((140, 620 - 10 * math.sin(t * 6)), '?', font=F('Inter-Black.otf', 80), fill=RED, anchor='mm')
        chip(im, 360, 1150, 'NUNCA TUVO UNA MOTO', q, col=(36, 36, 40), size=28)
    im = camera(im, lerp(1.2, 1.0, ease(lt / 2.5)), 330, 820)
    obj('in', mr); obj('out', mr); return im

def sc1(t, lt):
    im = BGS.copy(); d = BD(im)
    mr = moto(d, 400, 900, 1.0)
    d.rounded_rectangle((300, 640, 500, 720), 10, fill=(255, 255, 255), outline=(40, 40, 46), width=4); d.line((400, 720, 400, 780), fill=(40, 40, 46), width=6)
    d.text((400, 680), 'SE VENDE', font=F('Inter-Black.otf', 32), fill=RED, anchor='mm')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hernan(ImageDraw.Draw(L), 140, 760, 1.7); im.alpha_composite(L)
    chip(im, 560, 400, '1 SEMANA', t - wt(1, 'semana'), col=(36, 36, 40), size=28)
    q = t - wt(1, 'nadie')
    if q > 0:
        r = (440, 450, 680, 560); card(im, r, (255, 255, 255), 20); d = BD(im)
        d.text((560, 480), 'Preguntas', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='mm'); d.text((560, 528), '0', font=F('Inter-Black.otf', 48), fill=RED, anchor='mm')
    # días que pasan (hojas que caen)
    rr = random.Random(3); Lf = Image.new('RGBA', (W, H), (0, 0, 0, 0)); fd = ImageDraw.Draw(Lf)
    for k in range(8):
        qq = (lt * .3 + rr.random()) % 1; x = rr.random() * W + math.sin(lt * 2 + k) * 30; y = 300 + qq * 800
        fd.ellipse((x - 10, y - 5, x + 10, y + 5), fill=(220, 150, 60, int(220 * math.sin(math.pi * qq))))
    im.alpha_composite(Lf)
    im = camera(im, 1.0 + .06 * ease(lt / 4), 360, 760)
    obj('in', mr); obj('out', (300, 640, 500, 720)); return im

def sc2(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    dq = (t - wt(2, 'dropshipping') + .2) / .5
    r = listing(im, 360, 780, t, drop_q=dq)
    q = t - wt(2, 'notó')
    if q > 0 and dq < 1.5: im.alpha_composite(glow_layer(lambda dd: dd.rounded_rectangle((186, 853, 534, 913), 14, fill=255), RED, 20, int(160 * ease(q / .4))))
    zq = ease((t - wt(2, 'notó') + .1) / .7)
    im = camera(im, 1.0 + .45 * zq, 360, lerp(780, 830, zq))
    obj('in', (172, 465, 548, 675)); obj('out', (186, 853, 534, 913)); return im

def sc3(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    a1 = (80, 560, 300, 860); a2 = (420, 560, 640, 860)
    for r, who, name, lab in ((a1, 'h', 'Don Hernán', 'VENDEDOR'), (a2, 'c', 'Camilo', 'TE AYUDA')):
        q = 1 if who == 'h' else ease((t - wt(3, 'ayude')) / .4)
        if q <= 0: continue
        card(im, r, (255, 255, 255), 24); d = BD(im)
        avatar(im, (r[0] + r[2]) / 2, r[1] + 100, 70, who); d = BD(im)
        d.text(((r[0] + r[2]) / 2, r[1] + 210), name, font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm')
        d.text(((r[0] + r[2]) / 2, r[1] + 250), lab, font=F('Inter-Bold.otf', 18), fill=RED, anchor='mm')
    q = ease((t - wt(3, 'comisión') + .1) / .6)
    if q > 0:
        x = lerp(300, 420, q); d.line((300, 710, x, 710), fill=RED, width=8)
        if q > .9: d.polygon([(420, 710), (396, 696), (396, 724)], fill=RED)
        chip(im, 360, 640, 'COMISIÓN %', t - wt(3, 'comisión'), size=24)
    im = camera(im, 1.08, 360, 710)
    obj('in', (186, 853, 534, 913)); obj('out', a2); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    tp = t - wt(4, 'tocó') - .4
    r = listing(im, 360, 760, t, drop_q=1.0, btn_q=t - ct(4) + .3, tap=tp)
    q = t - wt(4, 'copió')
    if q > 0:
        a = back_out(q / .35); tr = (110, 1060, 610, 1160); card(im, (360 - 250 * a, 1110 - 50 * a, 360 + 250 * a, 1110 + 50 * a), (36, 36, 40), 50); d = BD(im)
        if a > .7:
            d.ellipse((140, 1088, 184, 1132), fill=GREEN); d.line((150, 1110, 160, 1122, 176, 1098), fill='white', width=5)
            d.text((200, 1096), 'Tu enlace se copió', font=F('Inter-Black.otf', 24), fill='white', anchor='lm')
            d.text((200, 1128), 'sumiago.com/…/moto-150#14', font=F('Inter-SemiBold.otf', 20), fill=(180, 180, 190), anchor='lm')
    zq = ease((t - wt(4, 'botón') + .2) / .6)
    im = camera(im, 1.0 + .2 * zq, 360, lerp(760, 1000, zq))
    obj('in', (172, 385, 548, 1135)); obj('out', (110, 1060, 610, 1160)); return im

def sc5(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    src = (360, 420)
    lr = (150, 380, 570, 460); card(im, lr, (36, 36, 40), 40); d = BD(im)
    d.text((360, 420), '🔗 sumiago.com/…#14'.replace('🔗 ', ''), font=F('Inter-Bold.otf', 24), fill='white', anchor='mm')
    items = [('whatsapp', 'Mi estado', 'WhatsApp', GREEN), ('grupos', 'Vecinos del barrio', 'Grupo', (60, 100, 200)), ('barrio', 'Compra y venta barrio', 'Grupo', (60, 100, 200))]
    last = None
    for k, (w_, l1, l2, col) in enumerate(items):
        q = t - wt(5, w_) + .1 + (.35 if k == 2 else 0)
        a = ease(q / .5)
        if a <= 0: continue
        y = 600 + k * 190; r = (90, y, 630, y + 150); last = r
        px, py = lerp(360, 360, a), lerp(470, y, a)
        if a < 1: d.line((360, 460, 360, py), fill=(200, 200, 210), width=4)
        card(im, r, (255, 255, 255), 24); d = BD(im)
        d.ellipse((120, y + 35, 200, y + 115), fill=col); chat_icon(d, 160, y + 75, 18)
        d.text((230, y + 55), l1, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm'); d.text((230, y + 98), l2, font=F('Inter-SemiBold.otf', 22), fill=(120, 120, 130), anchor='lm')
        chip(im, 560, y + 30, 'COMPARTIDO', q - .4, size=16)
    im = camera(im, 1.0, 360, 640)
    obj('in', lr); obj('out', last or (90, 600, 630, 750)); return im

def sc6(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    days = ['DÍA 1', 'DÍA 2', 'DÍA 3', 'DÍA 4']; k = min(3, int(max(0, t - ct(6)) / .25))
    r0 = (230, 330, 490, 450); card(im, r0, (255, 255, 255), 22); d = BD(im)
    d.rounded_rectangle((r0[0], r0[1], r0[2], r0[1] + 40), 22, fill=RED); d.rectangle((r0[0], r0[1] + 20, r0[2], r0[1] + 40), fill=RED)
    d.text((360, 410), days[k], font=F('Inter-Black.otf', 44), fill=(30, 30, 36), anchor='mm')
    q = t - wt(6, 'alguien')
    if q > 0:
        a = ease(q / .5); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), lerp(-60, 170, a), 700, 1.7, (90, 90, 170), skin=(180, 130, 100), long=True); im.alpha_composite(L); d = BD(im)
        if a > .9: d.rounded_rectangle((240, 620, 360, 660), 20, fill=(36, 36, 40)); d.text((300, 640), '#14', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    q = t - wt(6, 'escribió')
    br = (230, 860, 680, 1000)
    if q > -.2:
        bubble(im, 230, 880, '¿Todavía está la moto?', q + .2, col=(36, 38, 48), size=30)
    q2 = t - wt(6, 'hernán')
    if q2 > 0: avatar(im, 620, 760, 60, 'h')
    im = camera(im, 1.0 + .1 * ease(q / .6) if q > 0 else 1.0, 400, 760)
    obj('in', r0); obj('out', (560, 700, 680, 820)); return im

def sc7(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    q = t - wt(7, 'avisó')
    r1 = notif(im, 60, 440, 600, 'h', 'Para don Hernán', 'Este comprador llegó por Camilo', q)
    r2 = notif(im, 60, 640, 600, 'c', 'Para Camilo', 'Tu enlace funcionó · moto 150', q - .35)
    q3 = t - wt(7, 'gracias')
    if q3 > 0: stamp(im, 360, 960, ['GRACIAS A CAMILO'], RED, q3, ang=-6, size=42)
    im = camera(im, 1.0 + .08 * ease(lt / 3), 360, 680)
    obj('in', (60, 440, 660, 560)); obj('out', r2 or (60, 640, 660, 760)); return im

def sc8(t, lt):
    im = BGS.copy(); d = BD(im)
    mr = moto(d, 470, 900, .9)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    hernan(dl, 130, 760, 1.6); figure(dl, 640, 760, 1.6, (90, 90, 170), skin=(180, 130, 100), long=True); im.alpha_composite(L); d = BD(im)
    q = t - wt(8, 'vendió')
    if q > 0: stamp(im, 470, 640, ['VENDIDA'], RED, q, ang=-8, size=56)
    q = t - wt(8, 'cumplió')
    if q > 0:
        a = ease(q / .7); x = lerp(150, 330, a)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); camilo(ImageDraw.Draw(L), 330, 1000, 1.3); im.alpha_composite(L); d = BD(im)
        d.rounded_rectangle((x - 40, 1080 - 30 * math.sin(math.pi * a), x + 40, 1130 - 30 * math.sin(math.pi * a)), 8, fill=(250, 250, 250), outline=(200, 200, 210), width=3)
        d.line((x - 40, 1082 - 30 * math.sin(math.pi * a), x, 1106 - 30 * math.sin(math.pi * a), x + 40, 1082 - 30 * math.sin(math.pi * a)), fill=RED, width=4)
        chip(im, 360, 1230, 'COMISIÓN CUMPLIDA', q - .6, size=26)
    pq = ease((t - wt(8, 'cumplió') + .1) / .7)
    im = camera(im, 1.0 + .15 * pq, 360, lerp(800, 960, pq))
    obj('in', (60, 640, 660, 760)); obj('out', (260, 860, 440, 1160)); return im

def sc9(t, lt):
    im = gradient((60, 60, 66), (30, 30, 36)); d = BD(im)
    r = (80, 420, 640, 1020); card(im, r, (255, 255, 255), 26); d = BD(im)
    cx = 360
    d.polygon([(cx, 470), (cx + 70, 500), (cx + 70, 570), (cx, 620), (cx - 70, 570), (cx - 70, 500)], fill=(36, 36, 40)); d.text((cx, 545), '!', font=F('Inter-Black.otf', 60), fill='white', anchor='mm')
    mask_text(im, (cx, 680), 'ACUERDO VOLUNTARIO', F('Inter-Black.otf', 38), RED, (t - wt(9, 'voluntario') + .1) / .4)
    d.text((cx, 730), 'entre el vendedor y tú', font=F('Inter-SemiBold.otf', 24), fill=(120, 120, 130), anchor='mm')
    for k, (w_, txt) in enumerate((('cobra', 'Sumiago no la cobra'), ('garantiza', 'Sumiago no la garantiza'))):
        q = ease((t - wt(9, w_) + .1) / .35)
        if q > 0:
            y = 800 + k * 86; d = BD(im); d.rounded_rectangle((130, y, 130 + 460 * q, y + 64), 16, fill=(244, 244, 247))
            if q > .8: d.ellipse((150, y + 14, 186, y + 50), fill=(36, 36, 40)); d.line((158, y + 22, 178, y + 42), fill='white', width=4); d.line((158, y + 42, 178, y + 22), fill='white', width=4); d.text((206, y + 32), txt, font=F('Inter-Bold.otf', 26), fill=(30, 30, 36), anchor='lm')
    obj('in', r); obj('out', r); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); camilo(ImageDraw.Draw(L), 360, 760, 1.8, bob=-abs(math.sin(t * 4)) * 4); im.alpha_composite(L); d = BD(im)
    things = [('Moto', 160, 470), ('Celular', 560, 470), ('Nevera', 120, 1010), ('Bicicleta', 600, 1010), ('Sofá', 360, 1160)]
    for k, (nm, x, y) in enumerate(things):
        q = ease((t - wt(10, 'cosas') - k * .12) / .4)
        if q <= 0: continue
        y += math.sin(t * 2 + k) * 8; w = 150 * back_out(q); r = (x - w / 2, y - 60, x + w / 2, y + 60)
        card(im, r, (255, 255, 255), 20); d = BD(im)
        if q > .7:
            d.text((x, y - 12), nm, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
            d.rounded_rectangle((x - 58, y + 14, x + 58, y + 42), 14, fill=GREEN); d.text((x, y + 28), 'Comisión', font=F('Inter-Bold.otf', 16), fill='white', anchor='mm')
    q = t - wt(10, 'ayudar')
    if q > -.2: mask_text(im, (360, 380), 'AYÚDALAS A VENDER', F('Inter-Black.otf', 44), WHITE, (q + .2) / .4)
    obj('in', (230, 600, 490, 1000)); obj('out', (230, 600, 490, 1000)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Marketplace Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 200), 'Anuncios con Dropshipping', F('Inter-Bold.otf', 28), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'GANA COMISIÓN', t - wt(11, 'dropshipping'), col=GREEN, size=22)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'sino')
    if q > -.3:
        mask_text(im, (W / 2, 730), '…sino un dropshippero', F('Inter-BlackItalic.otf', 42), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 790), 'de Sumiago por ti.', F('Inter-BlackItalic.otf', 42), WHITE, (q + .1) / .4)
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
