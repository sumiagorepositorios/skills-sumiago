"""Día 42 — "La carta manchada" (historia: el restaurante de don Efraín cambia su carta impresa por el menú QR de Mi Negocio en Sumiago).
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
KEY = {'efraín', 'carta', 'salsa', 'tachados…', 'tachados', 'existía', 'imprimir', 'nunca', 'todavía', 'cocina', 'negocio', 'sumiago', 'catálogo', 'foto', 'descripción', 'precio', 'categoría',
       'menú', 'qr', 'mesa', 'escanea', 'celular', 'cambia', 'listo', 'reimprimir', 'recuerdo', 'restaurante', 'cafetería', 'comidas', 'membresía', 'link', 'fresco', 'comida'}
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
        mask_text(im, (W // 2, 800), 'Tu menú siempre al día', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
# ---------- objetos ----------
def efrain(d, x, y, s, bob=0):
    figure(d, x, y, s, (250, 250, 250), skin=(206, 156, 116), hair=(90, 90, 96), bob=bob)
    d.rounded_rectangle((x - 18 * s, y - 52 * s + bob, x + 18 * s, y - 24 * s + bob), 6 * s, fill=(255, 255, 255))   # gorro de chef
    d.ellipse((x - 22 * s, y - 66 * s + bob, x + 22 * s, y - 38 * s + bob), fill=(255, 255, 255))
def mesera(d, x, y, s, bob=0): figure(d, x, y, s, (40, 40, 46), skin=(196, 140, 104), hair=(40, 26, 20), long=True, bob=bob)
def plato(d, cx, cy, r, kind=0):
    d.ellipse((cx - r + 4, cy - r * .55 + 8, cx + r + 4, cy + r * .55 + 8), fill=(0, 0, 0, 50))
    d.ellipse((cx - r, cy - r * .55, cx + r, cy + r * .55), fill=(250, 250, 252), outline=(210, 212, 220), width=3)
    if kind == 0:
        d.ellipse((cx - r * .7, cy - r * .35, cx - r * .05, cy + r * .2), fill=(255, 255, 255), outline=(230, 230, 230)); d.ellipse((cx, cy - r * .3, cx + r * .6, cy + r * .1), fill=(150, 90, 50))
        d.ellipse((cx - r * .2, cy + r * .05, cx + r * .3, cy + r * .35), fill=(255, 255, 255)); d.ellipse((cx - r * .02, cy + r * .12, cx + r * .14, cy + r * .26), fill=(250, 190, 40))
    elif kind == 1:
        d.ellipse((cx - r * .6, cy - r * .35, cx + r * .6, cy + r * .3), fill=(230, 140, 60)); d.ellipse((cx - r * .3, cy - r * .2, cx + r * .1, cy + r * .1), fill=(240, 200, 120))
    else:
        d.ellipse((cx - r * .55, cy - r * .3, cx + r * .55, cy + r * .3), fill=(120, 170, 80)); d.ellipse((cx - r * .2, cy - r * .2, cx + r * .2, cy + r * .1), fill=(220, 60, 60))
def resto_bg():
    im = gradient((250, 236, 214), (236, 210, 176)); d = BD(im)
    d.rectangle((0, 300, W, 340), fill=(36, 36, 40)); d.text((W / 2, 320), 'RESTAURANTE DON EFRAÍN', font=F('Inter-Black.otf', 24), fill=GOLD, anchor='mm')
    for k in range(5): d.line((0, 400 + k * 110, W, 400 + k * 110), fill=(240, 220, 190), width=3)
    d.rectangle((0, 960, W, H), fill=(150, 98, 60))
    for x in (180, 540):
        d.ellipse((x - 140, 890, x + 140, 960), fill=RED); d.rectangle((x - 140, 920, x + 140, 940), fill=RED); d.rectangle((x - 10, 940, x + 10, 1100), fill=(90, 60, 40))
        d.pieslice((x - 140, 880, x + 140, 960), 0, 180, fill=(200, 30, 38))
    return im
BGRE = resto_bg()
def old_menu(im, cx, cy, s=1.0, ang=0, a=255):
    w, h = int(320 * s), int(440 * s); L = Image.new('RGBA', (w + 30, h + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rectangle((14, 18, w + 14, h + 18), fill=(0, 0, 0, 70)); d.rectangle((0, 0, w, h), fill=(246, 236, 206), outline=(180, 150, 100), width=4)
    d.text((w / 2, 40 * s), 'CARTA', font=F('Inter-Black.otf', int(36 * s)), fill=(90, 50, 30), anchor='mm')
    items = [('Bandeja', '18.000', True), ('Sopa', '8.000', False), ('Pescado', '25.000', True), ('Pollo', '15.000', False), ('Lasaña', '17.000', False)]
    for k, (n, p, tach) in enumerate(items):
        y = 100 * s + k * 62 * s; d.text((30 * s, y), n, font=F('Inter-Bold.otf', int(24 * s)), fill=(70, 50, 40), anchor='lm'); d.text((w - 30 * s, y), p, font=F('Inter-Bold.otf', int(22 * s)), fill=(70, 50, 40), anchor='rm')
        if tach: d.line((w - 120 * s, y, w - 30 * s, y), fill=RED, width=max(2, int(4 * s))); d.text((w - 30 * s, y + 22 * s), ('21.000' if k == 0 else '29.000'), font=F('Inter-SemiBoldItalic.otf', int(18 * s)), fill=(40, 60, 160), anchor='rm')
        if n == 'Lasaña': d.line((30 * s, y, 140 * s, y), fill=(40, 40, 46), width=max(2, int(5 * s)))
    for (mx, my, mr) in ((.7, .35, 40), (.25, .75, 30), (.8, .85, 24)): d.ellipse((w * mx - mr * s, h * my - mr * s * .7, w * mx + mr * s, h * my + mr * s * .7), fill=(190, 80, 40, 110))
    if a < 255: L.putalpha(L.getchannel('A').point(lambda p: int(p * a / 255)))
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))
    return (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
def qr(d, x, y, size, seed=7):
    n = 21; c = size / n; rr = random.Random(seed)
    d.rectangle((x - c, y - c, x + size + c, y + size + c), fill=(255, 255, 255))
    for i in range(n):
        for j in range(n):
            if (i < 7 and j < 7) or (i < 7 and j >= n - 7) or (i >= n - 7 and j < 7): continue
            if rr.random() < .5: d.rectangle((x + i * c, y + j * c, x + (i + 1) * c, y + (j + 1) * c), fill=(20, 20, 24))
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        X, Y = x + fx * c, y + fy * c
        d.rectangle((X, Y, X + 7 * c, Y + 7 * c), fill=(20, 20, 24)); d.rectangle((X + c, Y + c, X + 6 * c, Y + 6 * c), fill='white'); d.rectangle((X + 2 * c, Y + 2 * c, X + 5 * c, Y + 5 * c), fill=(20, 20, 24))
MENU = [('Platos fuertes', [('Bandeja de la casa', '21.000', 0), ('Pescado frito', '29.000', 1)]), ('Ensaladas', [('Ensalada fresca', '12.000', 2)])]
def menu_screen(im, cx, cy, s, t, price_q=0.0, sold_q=0.0, build_q=1.0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; y0 = cy - 375 * s + 60; xe = x0 + w - 28
    d.rectangle((x0, y0, xe, y0 + 60), fill=RED); d.text((cx, y0 + 30), 'Menú · Don Efraín', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    y = y0 + 80; k = 0
    for cat, items in MENU:
        if build_q * 4 < k: break
        d.text((x0 + 16, y + 14), cat.upper(), font=F('Inter-Black.otf', 18), fill=RED, anchor='lm'); y += 36
        for n, p, kind in items:
            k += 1; a = ease(build_q * 4 - k + 1)
            if a <= 0: continue
            d.rounded_rectangle((x0 + 10, y, xe - 10, y + 112), 14, fill=(36, 38, 48)); plato(d, x0 + 70, y + 56, 46, kind)
            d.text((x0 + 130, y + 36), n, font=F('Inter-Black.otf', 20), fill='white', anchor='lm')
            d.text((x0 + 130, y + 62), 'Con arroz y ensalada' if kind < 2 else 'Lechuga y tomate', font=F('Inter-SemiBold.otf', 15), fill=(170, 170, 180), anchor='lm')
            pr = p
            if kind == 0 and price_q > 0: pr = '22.000'
            d.text((x0 + 130, y + 90), '$ ' + pr, font=F('Inter-Black.otf', 20), fill=(255, 210, 120) if (kind == 0 and price_q > 0) else GREEN_OK, anchor='lm')
            if kind == 1 and sold_q > 0:
                d.rounded_rectangle((x0 + 10, y, xe - 10, y + 112), 14, fill=(20, 20, 24, int(170 * min(1, sold_q))))
                d.rounded_rectangle((xe - 130, y + 40, xe - 24, y + 72), 16, fill=(90, 90, 100)); d.text((xe - 77, y + 56), 'Agotado', font=F('Inter-Black.otf', 16), fill='white', anchor='mm')
            y += 124
    return (cx - 190 * s, cy - 375 * s, cx + 190 * s, cy + 375 * s)

# ---------- escenas ----------
def sc0(t, lt):
    im = BGRE.copy(); d = BD(im)
    r = old_menu(im, 360, 700, 1.15, ang=-3)
    q = t - wt(0, 'salsa')
    if q > 0: chip(im, 300, 450, 'MANCHAS DE SALSA', q, size=22)
    q = t - wt(0, 'tachados')
    if q > 0: chip(im, 300, 990, 'PRECIOS TACHADOS', q, col=(36, 36, 40), size=22)
    q = t - wt(0, 'existía')
    if q > 0: stamp(im, 250, 870, ['YA NO EXISTE'], RED, q, ang=-6, size=40)
    fq = ease((t - wt(0, 'salsa') + .2) / 2.0)
    im = camera(im, 1.25, lerp(420, 300, fq), lerp(600, 820, fq))
    obj('in', r); obj('out', r); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # impresora
    d.rounded_rectangle((160, 640, 560, 840), 24, fill=(70, 74, 90)); d.rectangle((210, 600, 510, 650), fill=(250, 250, 250)); d.rectangle((200, 820, 520, 860), fill=(50, 52, 64))
    q = ease((t - wt(1, 'imprimir') + .1) / .8)
    if q > 0: d.rectangle((220, 840, 500, 840 + 220 * q), fill=(250, 250, 250)); d.text((360, 880 + 60 * q), '$$$', font=F('Inter-Black.otf', 40), fill=RED, anchor='mm')
    chip(im, 360, 480, 'SUBIÓ UN PRECIO', t - wt(1, 'precio'), col=(36, 36, 40), size=26)
    q = t - wt(1, 'nunca')
    if q > 0: stamp(im, 360, 1150, ['CASI NUNCA'], RED, q, ang=-6, size=48)
    obj('in', (200, 450, 520, 950)); obj('out', (160, 640, 560, 840)); return im

def sc2(t, lt):
    im = BGRE.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    figure(dl, 180, 760, 1.6, (60, 110, 200)); mx = lerp(420, 700, ease((t - wt(2, 'cocina') + .2) / 1.0)); mesera(dl, mx, 760, 1.6, bob=-abs(math.sin(t * 10)) * 6 if t > wt(2, 'cocina') - .2 else 0)
    im.alpha_composite(L)
    bubble(im, 60, 470, '¿Esto todavía lo tienen?', t - wt(2, 'todavía') + .2, col=(255, 255, 255), tcol=(36, 36, 40), size=28)
    q = t - wt(2, 'averiguar')
    if q > 0: chip(im, 500, 1150, 'A AVERIGUAR…', q, col=(36, 36, 40), size=24)
    obj('in', (160, 640, 560, 840)); obj('out', (60, 470, 520, 550)); return im

def sc3(t, lt):
    im = BGRE.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); efrain(dl, 200, 760, 1.7); figure(dl, 520, 760, 1.7, (230, 120, 60), skin=(200, 150, 112)); im.alpha_composite(L)
    q = t - wt(3, 'negocio')
    if q > 0:
        a = back_out(q / .4); r = (420, 430, 680, 560); card(im, (550 - 130 * a, 495 - 65 * a, 550 + 130 * a, 495 + 65 * a), (255, 255, 255), 20); d = BD(im)
        if a > .7: d.text((550, 470), 'Mi Negocio', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='mm'); d.rounded_rectangle((500, 500, 600, 534), 17, fill=RED); d.text((550, 517), 'PRO', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    chip(im, 360, 1150, 'EN SU PORTADA DE SUMIAGO', t - wt(3, 'sumiago'), size=22)
    obj('in', (60, 470, 520, 550)); obj('out', (420, 430, 680, 560)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (70, 380, 650, 1100); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((100, 430), 'Catálogo · Nuevo plato', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm')
    fields = [('foto', 'Foto'), ('descripción', 'Descripción'), ('precio', 'Precio'), ('categoría', 'Categoría')]
    vals = [None, 'Arroz, carne, huevo y maduro', '$ 21.000', 'Platos fuertes']
    for k, (w_, lab) in enumerate(fields):
        a = ease((t - wt(4, w_) + .1) / .35)
        y = 480 + k * 140
        d.text((100, y + 10), lab, font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
        d.rounded_rectangle((100, y + 30, 620, y + 110 if k == 0 else y + 90), 14, fill=(244, 244, 247))
        if a > 0:
            if k == 0:
                Lp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); plato(ImageDraw.Draw(Lp), 180, y + 70, 60 * a + 1, 0); im.alpha_composite(Lp); d = BD(im)
                d.text((270, y + 70), 'Bandeja de la casa', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
            else:
                n = int(len(vals[k]) * a); d.text((120, y + 60), vals[k][:n], font=F('Inter-Bold.otf', 24), fill=RED if k == 2 else (30, 30, 36), anchor='lm')
    fq = ease((t - wt(4, 'foto') + .2) / 2.0)
    im = camera(im, 1.08, 360, lerp(600, 900, fq))
    obj('in', (420, 430, 680, 560)); obj('out', (100, 900, 620, 990)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = menu_screen(im, 230, 800, .85, t, build_q=ease((lt) / 1.2))
    q = t - wt(5, 'qr')
    if q > 0:
        a = back_out(q / .4); d = BD(im); sz = 210 * a; card(im, (540 - sz / 2 - 20, 760 - sz / 2 - 20, 540 + sz / 2 + 20, 760 + sz / 2 + 60), (255, 255, 255), 20); d = BD(im)
        qr(d, 540 - sz / 2, 760 - sz / 2, sz)
        if a > .8: d.text((540, 760 + sz / 2 + 30), 'Imprimir QR', font=F('Inter-Black.otf', 22), fill=RED, anchor='mm')
    chip(im, 230, 380, 'MENÚ LISTO', t - wt(5, 'menú'), size=24)
    obj('in', (100, 900, 620, 990)); obj('out', (415, 635, 665, 925)); return im

def sc6(t, lt):
    im = BGRE.copy(); d = BD(im)
    for x in (180, 540):
        d.rounded_rectangle((x - 40, 830, x + 40, 900), 8, fill=(255, 255, 255)); qr(d, x - 26, 838, 52)
    q = t - wt(6, 'escanea')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), 400, 700, 1.6, (90, 160, 120), skin=(214, 166, 128), long=True); im.alpha_composite(L)
    if q > 0:
        a = ease(q / .5)
        Lp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); menu_screen(Lp, 360, 800, 1.0, t)
        f = .25 + .3 * a; Lp = Lp.crop((150, 400, 570, 1200)); Lp = Lp.resize((int(420 * f), int(800 * f)), Image.LANCZOS)
        im.alpha_composite(Lp, (int(520 - Lp.width / 2), int(700 - Lp.height / 2)))
    chip(im, 360, 420, 'EN CADA MESA', t - wt(6, 'mesa'), col=(36, 36, 40), size=26)
    fq = ease((t - wt(6, 'escanea') + .1) / .7)
    im = camera(im, 1.0 + .25 * fq, lerp(360, 500, fq), lerp(760, 700, fq))
    obj('in', (415, 635, 665, 925)); obj('out', (415, 490, 625, 910)); return im

def sc7(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = menu_screen(im, 360, 800, 1.0, t, price_q=t - wt(7, 'precio'), sold_q=(t - wt(7, 'acaba')) / .4)
    chip(im, 360, 380, 'LO CAMBIA DESDE SU CELULAR', t - wt(7, 'cambia'), col=WHITE, tcol=RED, size=22)
    q = t - wt(7, 'listo')
    if q > 0: stamp(im, 520, 1160, ['¡LISTO!'], RED, q, ang=-8, size=48)
    obj('in', (172, 425, 548, 1175)); obj('out', (172, 425, 548, 1175)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.rounded_rectangle((160, 640, 560, 840), 24, fill=(70, 74, 90)); d.rectangle((210, 600, 510, 650), fill=(250, 250, 250)); d.rectangle((200, 820, 520, 860), fill=(50, 52, 64))
    q = t - wt(8, 'reimprimir')
    if q > 0:
        sl = ease(q / .35); d.line((130, 900, 130 + 460 * sl, 900 - 340 * sl), fill=RED, width=16)
        stamp(im, 360, 1080, ['NADA QUE REIMPRIMIR'], RED, q, ang=-5, size=40)
    obj('in', (172, 425, 548, 1175)); obj('out', (160, 640, 560, 840)); return im

def sc9(t, lt):
    im = BGRE.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (60, 40, 20, 70))); d = BD(im)
    d.rectangle((60, 380, 660, 960), fill=(200, 200, 196)); 
    for k in range(6): d.line((60, 380 + k * 100, 660, 380 + k * 100), fill=(180, 180, 176), width=3)
    a = ease(lt / .8); r = old_menu(im, 360, lerp(560, 660, a), .9, ang=lerp(-20, 4, a))
    d = BD(im); d.ellipse((350, 440 + 100 * a - 40, 370, 460 + 100 * a - 40), fill=RED)
    chip(im, 360, 1100, 'DE RECUERDO', t - wt(9, 'recuerdo'), col=(36, 36, 40), size=26)
    obj('in', (160, 640, 560, 840)); obj('out', r); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('restaurante', 'Restaurante', 0), ('cafetería', 'Cafetería', 1), ('comidas', 'Puesto de comidas', 2)]
    for k, (w_, lab, kind) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        y = 470 + k * 200; r = (360 - 260 * a, y, 360 + 260 * a, y + 160); card(im, r, (250, 250, 250), 24); d = BD(im)
        if a > .7: plato(d, 180, y + 80, 60, kind); d.text((280, y + 80), lab, font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm')
    q = t - wt(10, 'membresía')
    if q > 0: chip(im, 360, 1150, 'MENÚ QR · CON TU MEMBRESÍA', q, size=22)
    obj('in', (160, 450, 560, 900)); obj('out', (100, 470, 620, 630)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Negocio · Menú QR', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Cámbialo cuando quieras', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'SIN REIMPRIMIR', t - wt(11, 'regístrate'), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'fresco')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Tan fresco', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'como tu comida.', F('Inter-BlackItalic.otf', 44), WHITE, (q + .1) / .4)
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
