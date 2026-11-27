"""Día 54 — "Lo que a ti te sobra" (historia: doña Inés regala la cuna de su nieto con la categoría «Regalo» del Marketplace de Sumiago).
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
KEY = {'inés', 'cuna', 'ropita', 'vender', 'regalarla', 'necesitara', 'comentarios', 'revenderla', 'marketplace', 'sumiago', 'regalo', 'precio', 'regalos', 'primero', 'ciudad', '¡lo', 'quiero!»', 'aviso', 'whatsapp', 'bebé', 'acostarla»', 'regaló', 'regalar', 'link', 'sobra', 'falta'}
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
        mask_text(im, (W // 2, 800), 'Regala lo que no usas', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); WA = (37, 211, 102)
def ines(d, x, y, s, bob=0): figure(d, x, y, s, (120, 90, 170), skin=(222, 176, 140), hair=(196, 196, 200), long=True, bob=bob)
def el(d, x, y, s, bob=0): figure(d, x, y, s, (60, 130, 90), skin=(190, 140, 104), hair=(30, 22, 18), bob=bob)
def ella(d, x, y, s, bob=0): figure(d, x, y, s, (230, 150, 170), skin=(214, 166, 128), hair=(80, 46, 30), long=True, bob=bob)
def cuna(d, cx, by, s=1.0, col=(240, 236, 226)):
    w, h = 200 * s, 150 * s; x0 = cx - w / 2; y0 = by - h
    d.rectangle((x0, y0, x0 + 10 * s, by), fill=(200, 170, 130)); d.rectangle((x0 + w - 10 * s, y0, x0 + w, by), fill=(200, 170, 130))
    d.rectangle((x0, y0 + 10 * s, x0 + w, y0 + 18 * s), fill=(200, 170, 130)); d.rectangle((x0, by - 40 * s, x0 + w, by - 32 * s), fill=(200, 170, 130))
    for k in range(1, 9): x = x0 + k * w / 9; d.line((x, y0 + 18 * s, x, by - 40 * s), fill=(200, 170, 130), width=max(2, int(5 * s)))
    d.rectangle((x0 + 10 * s, by - 54 * s, x0 + w - 10 * s, by - 40 * s), fill=(180, 210, 240))
def gift(d, cx, cy, s, col=RED):
    d.rectangle((cx - 40 * s, cy - 20 * s, cx + 40 * s, cy + 44 * s), fill=col); d.rectangle((cx - 46 * s, cy - 36 * s, cx + 46 * s, cy - 14 * s), fill=mix(col, (0, 0, 0), .15))
    d.rectangle((cx - 7 * s, cy - 36 * s, cx + 7 * s, cy + 44 * s), fill=GOLD)
    d.ellipse((cx - 30 * s, cy - 58 * s, cx - 2 * s, cy - 34 * s), outline=GOLD, width=max(2, int(6 * s))); d.ellipse((cx + 2 * s, cy - 58 * s, cx + 30 * s, cy - 34 * s), outline=GOLD, width=max(2, int(6 * s)))
def bolsa(d, cx, by, s):
    d.polygon([(cx - 40 * s, by), (cx + 40 * s, by), (cx + 34 * s, by - 80 * s), (cx - 34 * s, by - 80 * s)], fill=(250, 214, 224)); d.arc((cx - 20 * s, by - 104 * s, cx + 20 * s, by - 64 * s), 180, 360, fill=(220, 150, 170), width=max(2, int(5 * s)))
    d.ellipse((cx - 14 * s, by - 50 * s, cx + 14 * s, by - 22 * s), fill=(180, 210, 240))
def heart(d, cx, cy, s, col=RED):
    d.ellipse((cx - 30 * s, cy - 24 * s, cx, cy + 6 * s), fill=col); d.ellipse((cx, cy - 24 * s, cx + 30 * s, cy + 6 * s), fill=col); d.polygon([(cx - 29 * s, cy - 4 * s), (cx + 29 * s, cy - 4 * s), (cx, cy + 30 * s)], fill=col)

def sc0(t, lt):
    im = gradient((214, 204, 190), (180, 168, 152)); d = BD(im)
    d.rectangle((0, 980, W, H), fill=(150, 130, 110)); d.rectangle((420, 300, 640, 560), fill=(230, 220, 200), outline=(140, 120, 100), width=6)
    cuna(d, 470, 980, 1.5, ); bolsa(d, 640, 980, 1.0 * ease((t - wt(0, 'bolsa') + .2) / .4)) if t > wt(0, 'bolsa') - .2 else None
    for k in range(14): x = (k * 97 + t * 14) % W; y = 380 + (k * 53 + t * 20) % 600; d.ellipse((x, y, x + 4, y + 4), fill=(255, 255, 240, 120))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ines(ImageDraw.Draw(L), 140, 800, 1.6); im.alpha_composite(L)
    q = t - wt(0, 'años')
    if q > 0: chip(im, 470, 640, '3 AÑOS GUARDADA', q, col=(36, 36, 40), size=26)
    im = camera(im, lerp(1.15, 1.0, ease(lt / 2.5)), 420, 860)
    obj('in', (370, 760, 570, 980)); obj('out', (370, 830, 570, 980)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ines(ImageDraw.Draw(L), 200, 760, 1.8); im.alpha_composite(L); d = BD(im)
    q = t - wt(1, 'vender')
    if q > 0:
        bubble(im, 330, 520, '$ Vender', q, col=(150, 150, 160), size=30); d = BD(im)
        if q > .3: d.line((330, 600, 560, 520), fill=RED, width=8)
    q = t - wt(1, 'regalarla')
    if q > 0: heart(d, 470, 760, 1.6 * back_out(q / .35)); chip(im, 470, 900, 'REGALARLA', q, size=28)
    q = t - wt(1, 'necesitara')
    if q > 0: chip(im, 360, 1080, 'A QUIEN DE VERDAD LA NECESITE', q, col=WHITE, tcol=RED, size=22)
    obj('in', (370, 830, 570, 980)); obj('out', (420, 720, 520, 800)); return im

def sc2(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 740, 1.05, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((216, 460, 504, 510), fill=(40, 60, 110)); d.text((236, 485), 'Grupo del barrio', font=F('Inter-Black.otf', 18), fill='white', anchor='lm')
    d.rectangle((216, 510, 504, 660), fill=(240, 236, 226)); cuna(d, 360, 650, .7)
    cm = ['Yo', 'Info', '¿La mandas?', 'Yo', 'Info', 'Yo!!', '¿Precio?']
    t0 = wt(2, 'comentarios') - .2
    for k, c in enumerate(cm):
        q = t - t0 - k * .3
        if q <= 0: continue
        a = back_out(q / .3); y = 676 + k * 46
        if y > 990: break
        d.ellipse((228, y + 4, 256, y + 32), fill=(120 + k * 18, 140, 170)); d.rounded_rectangle((264, y, 264 + (40 + len(c) * 12) * a, y + 36), 14, fill=(255, 255, 255))
        if a > .8: d.text((276, y + 18), c, font=F('Inter-Bold.otf', 18), fill=(40, 40, 46), anchor='lm')
    q = t - wt(2, 'llovieron')
    if q > 0: chip(im, 360, 380, '+87 COMENTARIOS', q, col=RED, size=26)
    obj('in', (420, 720, 520, 800)); obj('out', (216, 670, 504, 990)); return im

def sc3(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k, x in enumerate((140, 300, 460, 610)): figure(dl, x, 700, 1.3, (110, 110, 120), skin=(170, 170, 176), hair=(90, 90, 96))
    im.alpha_composite(L); d = BD(im)
    q = t - wt(3, 'revenderla')
    for k, x in enumerate((140, 460, 610)):
        qq = q + .3 - k * .12
        if qq > 0: d.text((x, 640 - 6 * math.sin(t * 5 + k)), '$', font=F('Inter-Black.otf', int(52 * min(1, back_out(qq / .3)))), fill=GOLD, anchor='mm')
    if q > 0: stamp(im, 360, 1080, ['PARA REVENDERLA'], RED, q, ang=-5, size=46)
    obj('in', (216, 670, 504, 990)); obj('out', (100, 700, 650, 960)); return im

def sc4(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = t - wt(4, 'marketplace'); chip(im, 360, 420, 'Marketplace Sumiago', q, col=(36, 36, 40), size=28)
    q = t - wt(4, 'categoría')
    if q > 0:
        a = back_out(q / .35); r = (160, 520, 560, 920); card(im, (360 - 200 * a, 720 - 200 * a, 360 + 200 * a, 720 + 200 * a), (255, 255, 255), 30); d = BD(im)
        if a > .7: d.text((360, 580), 'Categoría', font=F('Inter-Bold.otf', 24), fill=(120, 120, 130), anchor='mm')
    q = t - wt(4, 'regalo')
    if q > 0:
        d = BD(im); gift(d, 360, 720, 1.5 * back_out(q / .35))
        d.text((360, 860), 'Regalo (gratis)', font=F('Inter-Black.otf', 32), fill=RED, anchor='mm')
        sparkles(im, 360, 720, t, n=16, rad=220) if q < 1.2 else None
    obj('in', (100, 700, 650, 960)); obj('out', (160, 520, 560, 920)); return im

def listing_reg(im, cx, cy, s, t, hl=0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'MARKETPLACE', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 50 * s, xe, y0 + 300 * s), fill=(240, 236, 226)); cuna(d, cx, y0 + 290 * s, 1.0 * s)
    d.text((x0 + 16, y0 + 330 * s), 'Cuna de bebé + ropita', font=F('Inter-Black.otf', int(22 * s)), fill='white', anchor='lm')
    pr = (x0 + 12, y0 + 352 * s, x0 + 200 * s, y0 + 404 * s)
    if hl > 0: d.rounded_rectangle((pr[0] - 4, pr[1] - 4, pr[2] + 4, pr[3] + 4), 12, outline=GOLD, width=4)
    d.text((x0 + 16, y0 + 378 * s), 'Regalo', font=F('Inter-Black.otf', int(32 * s)), fill=GREEN_OK, anchor='lm')
    d.rounded_rectangle((x0 + 14, y0 + 430 * s, xe - 14, y0 + 486 * s), 26 * s, fill=RED); d.text((cx, y0 + 458 * s), '¡Lo quiero!', font=F('Inter-Black.otf', int(22 * s)), fill='white', anchor='mm')
    return pr

def sc5(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    q = t - wt(5, 'precio')
    if t < wt(5, 'precio', 1) - .5:
        r = (70, 480, 650, 820); card(im, r, (255, 255, 255), 24); d = BD(im)
        d.text((100, 530), 'Categoría', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm'); d.rounded_rectangle((100, 550, 620, 606), 12, fill=(244, 244, 247)); d.text((120, 578), 'Regalo (gratis)', font=F('Inter-Black.otf', 24), fill=RED, anchor='lm')
        d.text((100, 650), 'Precio', font=F('Inter-Bold.otf', 22), fill=(190, 190, 196), anchor='lm'); d.rounded_rectangle((100, 670, 620, 726), 12, fill=(236, 236, 240)); d.text((120, 698), '—', font=F('Inter-Black.otf', 24), fill=(190, 190, 196), anchor='lm')
        if q > 0: stamp(im, 360, 920, ['SIN PRECIO'], GREEN_OK, q, ang=-5, size=46)
        im2 = im
    else:
        pr = listing_reg(im, 360, 760, 1.0, t, hl=t - wt(5, 'regalo'))
        f = ease((t - wt(5, 'regalo') + .3) / .6); im = camera(im, 1.0 + .35 * f, lerp(360, (pr[0] + pr[2]) / 2 + 80, f), lerp(760, (pr[1] + pr[3]) / 2, f))
    obj('in', (70, 480, 650, 820)); obj('out', (100, 670, 620, 726)); return im

def sc6(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.rounded_rectangle((90, 340, 630, 400), 14, fill=(30, 30, 36)); d.text((120, 370), 'Ordenar:', font=F('Inter-Bold.otf', 22), fill=(170, 170, 180), anchor='lm')
    q = t - wt(6, 'ordena'); d.text((240, 370), 'Menor precio' if q > 0 else 'Recientes', font=F('Inter-Black.otf', 22), fill='white', anchor='lm')
    rows = [('Cuna de bebé + ropita', 'Regalo', GREEN_OK), ('Coche de bebé', '$ 180.000', (30, 30, 36)), ('Silla para comer', '$ 95.000', (30, 30, 36)), ('Juguetes', '$ 40.000', (30, 30, 36))]
    order = [1, 2, 3, 0] if q <= 0 else [0, 1, 2, 3]
    p = ease(q / .7) if q > 0 else 0
    old = {r: i for i, r in enumerate([1, 2, 3, 0])}; new = {r: i for i, r in enumerate([0, 1, 2, 3])}
    for k, (tit, pr, col) in enumerate(rows):
        y = 440 + lerp(old[k], new[k], p) * 150
        hl = k == 0 and t > wt(6, 'primero')
        card(im, (90, y, 630, y + 130), (255, 255, 255), 18); d = BD(im)
        if hl: d.rounded_rectangle((86, y - 4, 634, y + 134), 20, outline=GOLD, width=5)
        d.rounded_rectangle((106, y + 15, 206, y + 115), 12, fill=(240, 236, 226))
        if k == 0: cuna(d, 156, y + 108, .42)
        else: d.ellipse((136, y + 45, 176, y + 85), fill=[(150, 180, 220), (230, 180, 120), (200, 140, 200)][k - 1])
        d.text((226, y + 45), tit, font=F('Inter-Bold.otf', 22), fill=(60, 60, 70), anchor='lm'); d.text((226, y + 88), pr, font=F('Inter-Black.otf', 28), fill=col, anchor='lm')
    q = t - wt(6, 'primero')
    if q > 0: chip(im, 360, 1110, 'LOS REGALOS SALEN PRIMERO', q, col=RED, size=24)
    obj('in', (100, 670, 620, 726)); obj('out', (90, 440, 630, 570)); return im

def sc7(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); el(dl, 120, 880, 1.4); ella(dl, 210, 880, 1.4); ines(dl, 600, 880, 1.4); im.alpha_composite(L); d = BD(im)
    d.rounded_rectangle((60, 560, 300, 620), 30, fill=RED); d.text((180, 590), '¡Lo quiero!', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    q = t - wt(7, 'quiero')
    if 0 < q < .5: rr = 20 + q * 160; d.ellipse((180 - rr, 590 - rr, 180 + rr, 590 + rr), outline=(230, 38, 47, int(255 * (1 - q / .5))), width=5)
    if q > 0:
        x = lerp(240, 470, ease(q / .7)); d.ellipse((x - 10, 590 - 10 - 60 * math.sin(ease(q / .7) * math.pi), x + 10, 590 + 10 - 60 * math.sin(ease(q / .7) * math.pi)), fill=RED)
    q = t - wt(7, 'aviso')
    if q > 0:
        a = back_out(q / .35); r = (400, 470, 690, 580); card(im, (r[0], r[1], r[0] + (r[2] - r[0]) * a, r[3]), (255, 255, 255), 18); d = BD(im)
        if a > .8: d.text((420, 500), 'Sumiago', font=F('Inter-Black.otf', 18), fill=RED, anchor='lm'); d.text((420, 540), 'Alguien quiere tu cuna', font=F('Inter-Bold.otf', 19), fill=(40, 40, 46), anchor='lm')
    q = t - wt(7, 'ciudad')
    if q > 0: chip(im, 165, 420, 'MISMA CIUDAD', q, col=(36, 36, 40), size=22)
    obj('in', (90, 440, 630, 570)); obj('out', (400, 470, 690, 580)); return im

def sc8(t, lt):
    im = gradient((228, 221, 212), (205, 198, 188)); d = BD(im)
    d.rectangle((0, 290, W, 370), fill=(7, 94, 84)); d.text((40, 330), 'WhatsApp', font=F('Inter-Black.otf', 30), fill='white', anchor='lm')
    msgs = [('Hola, doña Inés. Vamos a tener', 'escribieron'), ('una bebé, y no teníamos', 'bebé'), ('dónde acostarla. 🙏' if False else 'dónde acostarla.', 'acostarla')]
    q = t - wt(8, 'vamos') + .2
    if q > 0:
        a = back_out(q / .35); r = (60, 420, 60 + 540 * a, 640); d.rounded_rectangle(r, 22, fill=(220, 248, 198))
        if a > .8:
            for k, (ln, w_) in enumerate(msgs):
                if t > wt(8, w_) - .3: d.text((90, 470 + k * 56), ln, font=F('Inter-SemiBold.otf', 28), fill=(30, 30, 36), anchor='lm')
    q = t - wt(8, 'acostarla')
    if q > 0:
        a = back_out(q / .35); d.rounded_rectangle((680 - 300 * a, 700, 680, 790), 22, fill=(255, 255, 255))
        if a > .8: d.text((400, 745), '¡Es suya! ❤' if False else '¡Es suya!', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm'); heart(d, 600, 745, .6)
    obj('in', (400, 470, 690, 580)); obj('out', (60, 420, 600, 640)); return im

def sc9(t, lt):
    im = gradient((250, 236, 214), (236, 214, 190)); d = BD(im)
    d.rectangle((0, 1000, W, H), fill=(190, 160, 130)); d.rectangle((470, 520, 640, 1000), fill=(150, 100, 70)); d.ellipse((610, 760, 624, 774), fill=GOLD)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); ines(dl, 420, 860, 1.4); el(dl, 120, 860, 1.4, bob=-abs(math.sin(t * 5)) * 3); ella(dl, 250, 860, 1.4, bob=-abs(math.sin(t * 5 + 1)) * 3); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(9, 'cuna') + .3) / .6)
    if q > 0: cuna(d, 185, 1000 - 40 * q, .9)
    q = t - wt(9, 'regaló')
    if q > 0:
        x = lerp(420, 300, ease(q / .6)); bolsa(d, x, 960, .8)
        for k in range(5):
            qq = (q - k * .2) % 1.6
            heart(d, 300 + math.sin(k * 2 + t) * 40, 820 - qq * 200, .4, (255, 90, 110, int(255 * max(0, 1 - qq / 1.6))))
    q = t - wt(9, 'sábado')
    if q > 0: chip(im, 360, 400, 'EL SÁBADO', q, col=(36, 36, 40), size=26)
    obj('in', (60, 420, 600, 640)); obj('out', (85, 860, 285, 1000)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('vender', 'Vender', '$'), ('comprar', 'Comprar', 'bag'), ('regalar', 'Regalar', 'gift')]
    for k, (w_, lab, ic) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        y = 470 + k * 170; card(im, (360 - 260 * a, y, 360 + 260 * a, y + 130), (250, 250, 250) if k < 2 else (255, 240, 240), 22); d = BD(im)
        if a > .7:
            cx, cy = 180, y + 65
            if ic == '$': d.ellipse((cx - 36, cy - 36, cx + 36, cy + 36), fill=GREEN_OK); d.text((cx, cy), '$', font=F('Inter-Black.otf', 40), fill='white', anchor='mm')
            elif ic == 'bag': d.rounded_rectangle((cx - 32, cy - 22, cx + 32, cy + 36), 8, fill=(36, 36, 40)); d.arc((cx - 18, cy - 44, cx + 18, cy - 8), 180, 360, fill=(36, 36, 40), width=6)
            else: gift(d, cx, cy + 4, .8)
            d.text((250, cy), lab, font=F('Inter-Black.otf', 36), fill=RED if k == 2 else (30, 30, 36), anchor='lm')
    chip(im, 360, 1050, 'MARKETPLACE SUMIAGO', t - wt(10, 'marketplace'), size=24)
    obj('in', (85, 860, 285, 1000)); obj('out', (100, 810, 620, 940)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Marketplace Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Regala lo que ya no usas', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'CATEGORÍA REGALO', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'sobra')
    if q > -.6:
        mask_text(im, (W / 2, 740), 'Lo que a ti te sobra…', F('Inter-BlackItalic.otf', 42), WHITE, (q + .6) / .4)
        mask_text(im, (W / 2, 795), 'a otro le hace falta.', F('Inter-BlackItalic.otf', 42), WHITE, (t - wt(11, 'otro') + .3) / .4)
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
