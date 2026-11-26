"""Día 39 — "El ayudante que ya sabía" (historia: una ferretería encuentra a su ayudante en Contrátame Sumiago).
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
KEY = {'ferretería', 'mes', 'ayudante', 'letrero', '3', 'ninguna', 'herramientas', '40', 'completo', 'sabe', 'contrátame', 'sumiago', 'profesión', 'ciudad', 'experiencia',
       'segundos', 'revisados', 'mateo', 'bodega', '10', 'contactar', 'whatsapp', 'lunes', 'mostrador', 'cabeza', 'están', 'negocio', 'trabajo', 'ti', 'link', 'ahí'}
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
        mask_text(im, (W // 2, 800), 'Encuentra a quien ya sabe', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
# ---------- objetos ----------
def hammer(d, x, y, s=1.0):
    d.line((x, y, x, y + 70 * s), fill=(150, 98, 60), width=max(2, int(10 * s))); d.rounded_rectangle((x - 26 * s, y - 10 * s, x + 26 * s, y + 10 * s), 4, fill=(110, 114, 126))
def ferre_bg():
    im = gradient((236, 232, 226), (214, 208, 200)); d = BD(im)
    d.rectangle((0, 300, W, 340), fill=(36, 36, 40)); d.text((W / 2, 320), 'FERRETERÍA GLORIA', font=F('Inter-Black.otf', 26), fill=GOLD, anchor='mm')
    for y in (430, 580):
        d.rectangle((30, y + 70, 690, y + 84), fill=(120, 80, 50))
        for k in range(8):
            x = 70 + k * 82
            if k % 3 == 0: hammer(d, x, y - 10, .8)
            elif k % 3 == 1: d.rounded_rectangle((x - 28, y + 10, x + 28, y + 70), 6, fill=[RED, (60, 110, 200)][k % 2]); d.rectangle((x - 20, y + 26, x + 20, y + 40), fill=(255, 255, 255))
            else: d.ellipse((x - 24, y + 22, x + 24, y + 70), fill=(150, 154, 166)); d.ellipse((x - 10, y + 36, x + 10, y + 56), fill=(214, 208, 200))
    d.rectangle((0, 900, W, H), fill=(160, 110, 70)); d.rectangle((0, 900, W, 916), fill=(190, 140, 96))
    return im
BGF = ferre_bg()
def gloria(d, x, y, s, bob=0):
    figure(d, x, y, s, (200, 60, 60), skin=(220, 176, 140), hair=(70, 50, 40), long=True, bob=bob)
def hija(d, x, y, s, bob=0): figure(d, x, y, s, (90, 160, 120), skin=(214, 166, 128), hair=(40, 26, 20), long=True, bob=bob)
def mateo(d, x, y, s, bob=0): figure(d, x, y, s, (60, 110, 200), skin=(176, 122, 90), hair=(24, 18, 16), bob=bob)

def person_av(im, cx, cy, r, fn, bg=(236, 240, 246)):
    L = Image.new('RGBA', (int(r * 2), int(r * 3)), (0, 0, 0, 0)); fn(ImageDraw.Draw(L), r, r * .9, r / 40)
    m = Image.new('L', (int(r * 2), int(r * 2)), 0); ImageDraw.Draw(m).ellipse((0, 0, r * 2 - 1, r * 2 - 1), fill=255)
    b = Image.new('RGBA', (int(r * 2), int(r * 2)), bg + (255,)); b.alpha_composite(L.crop((0, 0, int(r * 2), int(r * 2)))); b.putalpha(m)
    im.alpha_composite(b, (int(cx - r), int(cy - r)))

CANDS = [('Mateo R.', 'Ayudante de ferretería', '3 años', mateo), ('Luisa P.', 'Ventas de mostrador', '2 años', hija), ('Jorge V.', 'Bodega y despachos', '5 años', lambda d, x, y, s: figure(d, x, y, s, (120, 120, 130), skin=(220, 176, 140)))]
def cand_card(im, r, k, hl=0.0, contact=0.0):
    n, p, e, fn = CANDS[k]
    if hl > 0: im.alpha_composite(glow_layer(lambda dd: dd.rounded_rectangle(r, 22, fill=255), RED, 24, int(200 * hl)))
    card(im, r, (255, 255, 255), 22); d = BD(im)
    if hl > 0: d.rounded_rectangle(r, 22, outline=mix((255, 255, 255), RED, hl), width=5)
    person_av(im, r[0] + 70, (r[1] + r[3]) / 2, 46, fn); d = BD(im)
    d.text((r[0] + 136, r[1] + 40), n, font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='lm')
    d.text((r[0] + 136, r[1] + 74), p, font=F('Inter-SemiBold.otf', 20), fill=(110, 110, 120), anchor='lm')
    d.rounded_rectangle((r[0] + 136, r[1] + 94, r[0] + 236, r[1] + 122), 14, fill=(244, 244, 247)); d.text((r[0] + 186, r[1] + 108), e, font=F('Inter-Bold.otf', 16), fill=RED, anchor='mm')
    d.rounded_rectangle((r[2] - 90, r[1] + 20, r[2] - 24, r[1] + 46), 13, fill=GREEN_OK); d.text((r[2] - 57, r[1] + 33), '✓'[:0] + 'Revisado', font=F('Inter-Bold.otf', 12), fill='white', anchor='mm')
    if contact > 0:
        b = back_out(contact / .35); cx, cy = r[2] - 110, r[3] - 36
        d.rounded_rectangle((cx - 90 * b, cy - 22 * b, cx + 90 * b, cy + 22 * b), 22, fill=RED)
        if b > .6: d.text((cx, cy), 'Contactar candidato', font=F('Inter-Black.otf', 15), fill='white', anchor='mm')

# ---------- escenas ----------
def sc0(t, lt):
    im = BGF.copy(); d = BD(im)
    d.rectangle((60, 760, 660, 900), fill=(130, 86, 52)); d.rectangle((60, 760, 660, 778), fill=(170, 120, 80))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gloria(ImageDraw.Draw(L), 360, 600, 1.7, bob=-abs(math.sin(t * 2.5)) * 3); im.alpha_composite(L)
    q = t - wt(0, 'mes')
    if q > 0:
        r = (470, 380, 680, 520); card(im, r, (255, 255, 255), 18); d = BD(im)
        d.rounded_rectangle((r[0], r[1], r[2], r[1] + 34), 18, fill=RED); d.rectangle((r[0], r[1] + 18, r[2], r[1] + 34), fill=RED)
        d.text((575, 470), '30 DÍAS', font=F('Inter-Black.otf', 36), fill=(30, 30, 36), anchor='mm')
    chip(im, 360, 1040, 'BUSCA AYUDANTE', t - wt(0, 'ayudante'), size=28)
    im = camera(im, lerp(1.2, 1.0, ease(lt / 3)), 360, 700)
    obj('in', (260, 480, 460, 900)); obj('out', (470, 380, 680, 520)); return im

def sc1(t, lt):
    im = BGF.copy(); d = BD(im)
    sg = (180, 620, 540, 760); card(im, sg, (255, 255, 255), 10); d = BD(im)
    d.text((360, 668), 'SE NECESITA', font=F('Inter-Black.otf', 34), fill=(30, 30, 36), anchor='mm'); d.text((360, 716), 'AYUDANTE', font=F('Inter-Black.otf', 40), fill=RED, anchor='mm')
    q = t - wt(1, 'llegaron')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(3):
        a = ease((q - k * .2) / .5)
        if a > 0: figure(dl, lerp(W + 60, 180 + k * 180, a), 960, 1.4, [(150, 120, 90), (90, 120, 150), (120, 150, 90)][k], long=k == 1)
    im.alpha_composite(L); d = BD(im)
    q2 = t - wt(1, 'ninguna')
    if q2 > 0:
        for k in range(3):
            x = 180 + k * 180; d.text((x, 860), '?', font=F('Inter-Black.otf', int(50 * back_out((q2 - k * .1) / .3)) + 1), fill=RED, anchor='mm')
        chip(im, 360, 1220, 'NO SABÍAN DE HERRAMIENTAS', q2 - .3, col=(36, 36, 40), size=22)
    fq = ease((q) / .6) if q > 0 else 0
    im = camera(im, 1.05, 360, lerp(690, 900, fq))
    obj('in', sg); obj('out', (100, 800, 620, 1120)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 780, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.text((360, 470), 'Grupo · Empleos', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    n = int(40 * ease((t - wt(2, '40') + .2) / 1.4))
    for k in range(min(n, 9)):
        y = 520 + k * 66; d.rounded_rectangle((200, y, 520, y + 54), 14, fill=(40, 42, 54))
        d.ellipse((212, y + 10, 246, y + 44), fill=[(90, 110, 150), (160, 100, 120), (90, 150, 120)][k % 3])
        d.text((260, y + 27), ['Info?', 'Cuánto pagan?', 'Yo', 'Interesado', 'Info x interno', 'Disponible', 'Precio?', 'Yo!!', 'Info'][k], font=F('Inter-SemiBold.otf', 20), fill=(210, 210, 220), anchor='lm')
    r = (470, 360, 680, 480); card(im, r, (255, 255, 255), 20); d = BD(im)
    d.text((575, 392), 'Mensajes', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='mm'); d.text((575, 440), str(n), font=F('Inter-Black.otf', 46), fill=RED, anchor='mm')
    q = t - wt(2, 'completo')
    if q > 0: stamp(im, 360, 1100, ['NO LEYERON'], RED, q, ang=-6, size=46)
    obj('in', (172, 405, 548, 1155)); obj('out', (172, 405, 548, 1155)); return im

def sc3(t, lt):
    im = BGF.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); gloria(dl, 180, 760, 1.7); hija(dl, 540, 760, 1.7); im.alpha_composite(L)
    bubble(im, 230, 440, 'No busques entre todos', t - wt(3, 'mamá'), col=(90, 160, 120), size=26)
    bubble(im, 230, 520, 'Busca al que ya sabe', t - wt(3, 'busca', 1), col=RED, size=30)
    im = camera(im, 1.06, 360, 700)
    obj('in', (172, 405, 548, 1155)); obj('out', (230, 520, 620, 600)); return im

def search_ui(im, t, ci, rows=True):
    d = BD(im)
    sb = (60, 400, 660, 470); card(im, sb, (255, 255, 255), 35); d = BD(im)
    d.ellipse((88, 418, 122, 452), outline=(140, 140, 150), width=5); d.line((116, 446, 132, 462), fill=(140, 140, 150), width=6)
    txt = 'Ayudante de ferretería'; n = int(len(txt) * ease((t - wt(4, 'profesión') + .2) / 1.0)) if ci == 4 else len(txt)
    d.text((146, 435), txt[:n], font=F('Inter-Bold.otf', 26), fill=(30, 30, 36), anchor='lm')
    fl = [('profesión', 'Ayudante', 150), ('ciudad', 'Mi ciudad', 360), ('experiencia', '+2 años', 560)]
    for w_, lab, x in fl: chip(im, x, 520, lab, (t - wt(4, w_)) if ci == 4 else 1, col=(36, 36, 40), size=20)
    return sb

def sc4(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    chip(im, 360, 340, 'CONTRÁTAME SUMIAGO', t - wt(4, 'contrátame'), size=24)
    sb = search_ui(im, t, 4)
    obj('in', (230, 520, 620, 600)); obj('out', (60, 490, 660, 550)); return im

def sc5(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    search_ui(im, t, 5); last = None
    for k in range(3):
        a = ease((t - ct(5) - .1 - k * .2) / .4)
        if a <= 0: continue
        y = 590 + k * 180 + (1 - a) * 40; r = (60, y, 660, y + 160); cand_card(im, r, k); last = r
    q = t - wt(5, 'revisados')
    if q > 0: chip(im, 560, 1160, 'PERFILES REVISADOS', q, col=GREEN_OK, size=20)
    obj('in', (60, 490, 660, 550)); obj('out', (60, 590, 660, 750)); return im

def sc6(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    hl = ease((t - wt(6, 'mateo')) / .4)
    for k in range(3):
        y = 590 + k * 180; r = (60, y, 660, y + 160)
        if k: 
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); cand_card(L, r, k); L.putalpha(L.getchannel('A').point(lambda p: int(p * (1 - hl)))); im.alpha_composite(L)
    cand_card(im, (60, 590, 660, 750), 0, hl=hl)
    d = BD(im)
    chip(im, 360, 830, '3 AÑOS EN BODEGA DE MATERIALES', t - wt(6, 'bodega'), col=(36, 36, 40), size=22)
    chip(im, 360, 910, 'VIVE A 10 MINUTOS', t - wt(6, '10'), size=24)
    fq = ease((t - wt(6, 'mateo') + .1) / .6)
    im = camera(im, 1.0 + .2 * fq, 360, lerp(700, 760, fq))
    obj('in', (60, 590, 660, 750)); obj('out', (60, 590, 660, 750)); return im

def sc7(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 80))
    cand_card(im, (60, 420, 660, 580), 0, hl=1, contact=t - wt(7, 'contactar'))
    tq = t - wt(7, 'contactar') - .3
    if 0 < tq < .5: d = BD(im); rr = 20 + tq * 140; d.ellipse((550 - rr, 544 - rr, 550 + rr, 544 + rr), outline=(255, 255, 255, int(255 * (1 - tq / .5))), width=5)
    q = t - wt(7, 'whatsapp')
    if q > 0:
        a = ease(q / .4); r = (120, 700 + (1 - a) * 40, 640, 900 + (1 - a) * 40); card(im, r, (255, 255, 255), 24); d = BD(im)
        d.ellipse((r[0] + 24, r[1] + 24, r[0] + 84, r[1] + 84), fill=GREEN_OK); chat_icon(d, r[0] + 54, r[1] + 54, 15)
        d.text((r[0] + 104, r[1] + 44), 'Ferretería Gloria', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm')
        mask_text(im, (r[0] + 104 + 190, r[1] + 110), 'Hola Mateo, vi tu perfil.', F('Inter-SemiBold.otf', 24), (60, 60, 66), (q - .3) / .3)
        mask_text(im, (r[0] + 104 + 190, r[1] + 150), '¿Puedes venir mañana?', F('Inter-SemiBold.otf', 24), (60, 60, 66), (q - .5) / .3)
    chip(im, 360, 1000, 'ESA MISMA TARDE', t - wt(7, 'tarde'), col=WHITE, tcol=RED, size=24)
    obj('in', (60, 420, 660, 580)); obj('out', (120, 700, 640, 900)); return im

def sc8(t, lt):
    im = BGF.copy(); d = BD(im)
    d.rectangle((60, 760, 660, 900), fill=(130, 86, 52)); d.rectangle((60, 760, 660, 778), fill=(170, 120, 80))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); mateo(dl, 300, 600, 1.7, bob=-abs(math.sin(t * 4)) * 3); gloria(dl, 560, 610, 1.5); im.alpha_composite(L); d = BD(im)
    hammer(d, 200, 700, 1.0)
    chip(im, 150, 420, 'LUNES', t - wt(8, 'lunes'), col=(36, 36, 40), size=28)
    q = t - wt(8, 'mostrador')
    if q > 0: stamp(im, 360, 1060, ['YA SABÍA'], RED, q, ang=-6, size=56)
    obj('in', (120, 700, 640, 900)); obj('out', (200, 480, 400, 900)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # izquierda: lío de mensajes; derecha: lupa sobre perfiles
    q = ease((t - wt(9, 'buscar', 1)) / .6)
    rr = random.Random(3)
    for k in range(14):
        x = 60 + rr.random() * 260; y = 420 + rr.random() * 500; a = int(255 * (1 - q * .8))
        Lb = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(Lb).rounded_rectangle((x, y, x + 90, y + 34), 12, fill=(150, 150, 160, a)); im.alpha_composite(Lb)
    d = BD(im); d.text((190, 980), 'Todos', font=F('Inter-Black.otf', 30), fill=(120, 120, 130), anchor='mm')
    if q > 0:
        cx, cy = 530, 650
        for k in range(3): person_av(im, cx - 80 + k * 80, cy + 40, 32, CANDS[k][3])
        d = BD(im); d.ellipse((cx - 150 * q, cy - 110 * q, cx + 150 * q, cy + 190 * q), outline=RED, width=12); d.line((cx + 100 * q, cy + 160 * q, cx + 170 * q, cy + 250 * q), fill=RED, width=20)
        d.text((530, 980), 'Los que ya saben', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    q2 = t - wt(9, 'cabeza')
    if q2 > 0: chip(im, 360, 380, 'SIN DOLOR DE CABEZA', q2, col=(36, 36, 40), size=24)
    obj('in', (200, 480, 400, 900)); obj('out', (380, 540, 680, 840)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    for k, (w_, lab, fn) in enumerate((('negocio', 'Tu negocio busca', gloria), ('trabajo', 'Tú buscas trabajo', mateo))):
        a = back_out((t - wt(10, w_) + .1) / .4)
        if a <= 0: continue
        x = 200 + k * 320; y = 720; w, h = 270 * a, 320 * a; r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        card(im, r, (250, 250, 250), 24)
        if a > .7: person_av(im, x, y - 40, 70, fn); d = BD(im); d.text((x, y + 100), lab, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
    q = t - wt(10, 'ti', 1)
    if q > 0: stamp(im, 360, 1050, ['ES PARA TI'], WHITE, q, ang=-5, size=46)
    obj('in', (380, 540, 680, 840)); obj('out', (65, 560, 335, 880)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Contrátame Sumiago', F('Inter-Black.otf', 34), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Talento y empresas, conectados', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'BUSCA POR PROFESIÓN Y CIUDAD', t - wt(11, 'regístrate'), size=18)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'ahí')
    if q > -.3: mask_text(im, (W / 2, 760), '…puede que ya esté ahí.', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
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
