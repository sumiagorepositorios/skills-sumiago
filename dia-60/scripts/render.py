"""Día 60 — "Deja de buscar" (historia: Paola, amante de las plantas, descubre la pestaña «Para ti» del Marketplace de Sumiago, que aprende de lo que mira y guarda).
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
KEY = {'paola', 'plantas', 'todo', 'carros', 'celulares', 'sofás', '10', 'matera', 'marketplace', 'sumiago', 'sumiago,', 'favoritos', 'monstera', 'suculenta', 'materas', '«para', 'ti»', 'ti».', 'gusta', 'tierra', 'estante', 'miras', 'interesa', 'ofertas', 'país', 'suyos', 'nuevo', 'barro…', 'buscarlas', 'registrados', 'conoce', 'link', 'buscar…', 'encontrar'}
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
        mask_text(im, (W // 2, 800), 'Descubre lo tuyo', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); LEAF = (46, 140, 80); TERRA = (196, 110, 70)
def paola(d, x, y, s, bob=0): figure(d, x, y, s, (120, 170, 90), skin=(206, 156, 120), hair=(60, 36, 24), long=True, bob=bob)
def matera(d, cx, by, s, col=TERRA):
    d.polygon([(cx - 34 * s, by - 56 * s), (cx + 34 * s, by - 56 * s), (cx + 24 * s, by), (cx - 24 * s, by)], fill=col); d.rectangle((cx - 38 * s, by - 64 * s, cx + 38 * s, by - 52 * s), fill=mix(col, (0, 0, 0), .15))
def monstera(d, cx, by, s):
    matera(d, cx, by, s, (230, 230, 226))
    for k, (dx, dy, r) in enumerate([(-30, -110, 34), (28, -126, 38), (0, -160, 34), (-40, -170, 26), (40, -180, 28)]):
        d.ellipse((cx + (dx - r) * s, by + (dy - r) * s, cx + (dx + r) * s, by + (dy + r) * s), fill=LEAF)
        d.line((cx + dx * s, by + (dy - r * .6) * s, cx + dx * s, by + (dy + r * .6) * s), fill=(30, 100, 56), width=max(1, int(3 * s)))
def suculenta(d, cx, by, s):
    matera(d, cx, by, s * .8)
    for k in range(8):
        a = k * math.pi / 4; x = cx + math.cos(a) * 22 * s; y = by - 74 * s + math.sin(a) * 12 * s
        d.ellipse((x - 14 * s, y - 10 * s, x + 14 * s, y + 10 * s), fill=(120, 180, 150))
    d.ellipse((cx - 12 * s, by - 86 * s, cx + 12 * s, by - 62 * s), fill=(150, 200, 170))
def icon(d, kind, cx, cy, s):
    if kind == 'carro': d.rounded_rectangle((cx - 40 * s, cy - 6 * s, cx + 40 * s, cy + 16 * s), 8, fill=(60, 110, 170)); d.rounded_rectangle((cx - 24 * s, cy - 24 * s, cx + 20 * s, cy - 2 * s), 8, fill=(60, 110, 170)); [d.ellipse((x - 9 * s, cy + 8 * s, x + 9 * s, cy + 26 * s), fill=(30, 30, 34)) for x in (cx - 22 * s, cx + 22 * s)]
    elif kind == 'cel': d.rounded_rectangle((cx - 16 * s, cy - 30 * s, cx + 16 * s, cy + 30 * s), 6, fill=(30, 30, 36)); d.rounded_rectangle((cx - 12 * s, cy - 24 * s, cx + 12 * s, cy + 22 * s), 3, fill=(90, 140, 200))
    elif kind == 'sofa': d.rounded_rectangle((cx - 44 * s, cy - 14 * s, cx + 44 * s, cy + 16 * s), 8, fill=(150, 90, 150)); d.rounded_rectangle((cx - 36 * s, cy - 32 * s, cx + 36 * s, cy - 8 * s), 8, fill=(170, 110, 170))
    elif kind == 'monstera': monstera(d, cx, cy + 40 * s, .4 * s)
    elif kind == 'suculenta': suculenta(d, cx, cy + 30 * s, .55 * s)
    elif kind == 'matera': matera(d, cx, cy + 30 * s, .8 * s)
    elif kind == 'barro': matera(d, cx, cy + 30 * s, .8 * s, (160, 90, 60))
    elif kind == 'tierra': d.rounded_rectangle((cx - 28 * s, cy - 32 * s, cx + 28 * s, cy + 32 * s), 8, fill=(120, 84, 56)); d.rectangle((cx - 20 * s, cy - 10 * s, cx + 20 * s, cy + 10 * s), fill=(240, 220, 180))
    elif kind == 'estante': [d.rectangle((cx - 40 * s, cy - 30 * s + k * 26 * s, cx + 40 * s, cy - 24 * s + k * 26 * s), fill=(150, 104, 70)) for k in range(3)]; matera(d, cx - 16 * s, cy - 30 * s, .3 * s); matera(d, cx + 18 * s, cy - 4 * s, .3 * s)
    elif kind == 'yo': d.rounded_rectangle((cx - 34 * s, cy - 26 * s, cx + 34 * s, cy + 26 * s), 8, fill=(200, 200, 206))
LABELS = {'carro': 'Carro', 'cel': 'Celular', 'sofa': 'Sofá', 'monstera': 'Monstera', 'suculenta': 'Suculenta', 'matera': 'Matera', 'barro': 'Materas de barro', 'tierra': 'Tierra abonada', 'estante': 'Estante colgante', 'yo': 'Tu anuncio'}
def fcard(im, r, kind, fav=False, extra=None):
    card(im, r, (255, 255, 255), 16); d = BD(im)
    d.rounded_rectangle((r[0] + 10, r[1] + 10, r[2] - 10, r[3] - 54), 12, fill=(236, 244, 236) if kind in ('monstera', 'suculenta', 'matera', 'barro', 'tierra', 'estante') else (236, 240, 246))
    s = (r[2] - r[0]) / 300; icon(d, kind, (r[0] + r[2]) / 2, (r[1] + r[3] - 44) / 2, 1.3 * s)
    d.text((r[0] + 16, r[3] - 30), LABELS[kind], font=F('Inter-Black.otf', int(20 * s)), fill=(30, 30, 36), anchor='lm')
    if fav:
        cx, cy, z = r[2] - 30, r[1] + 30, .5
        d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill='white'); d.ellipse((cx - 30 * z, cy - 24 * z, cx, cy + 6 * z), fill=RED); d.ellipse((cx, cy - 24 * z, cx + 30 * z, cy + 6 * z), fill=RED); d.polygon([(cx - 29 * z, cy - 4 * z), (cx + 29 * z, cy - 4 * z), (cx, cy + 30 * z)], fill=RED)
def grid(im, kinds, y0, t, off=0.0, start=None, favs=()):
    for i, k in enumerate(kinds):
        c, rr = i % 2, i // 2; y = y0 + rr * 260 - off
        if y > H or y < -260: continue
        if start is not None:
            q = t - start[i] if isinstance(start, list) else t - start - i * .15
            if q <= 0: continue
            a = back_out(q / .35); cx = 205 + c * 310; cy = y + 120
            r = (cx - 145 * a, cy - 120 * a, cx + 145 * a, cy + 120 * a)
            if a < .5: continue
        else: r = (60 + c * 310, y, 350 + c * 310, y + 240)
        fcard(im, r, k, fav=k in favs)
def tabs(im, sel, y=330):
    d = BD(im); d.rounded_rectangle((40, y, 680, y + 64), 32, fill=(20, 20, 24))
    for i, lab in enumerate(['Anuncios', 'Para ti', 'Destacados']):
        x = 40 + i * 213; on = i == sel
        if on: d.rounded_rectangle((x + 6, y + 6, x + 207, y + 58), 26, fill=RED)
        d.text((x + 106, y + 32), lab, font=F('Inter-Black.otf', 22), fill='white' if on else (170, 170, 180), anchor='mm')

def sc0(t, lt):
    if t < wt(0, 'veía'):
        im = gradient((235, 244, 236), (214, 232, 216)); d = BD(im)
        d.rectangle((0, 1000, W, H), fill=(190, 170, 140))
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paola(ImageDraw.Draw(L), 250, 760, 1.8); im.alpha_composite(L); d = BD(im)
        monstera(d, 500, 1000, 1.4); suculenta(d, 640, 1000, 1.0)
        q = t - wt(0, 'plantas')
        if q > 0: chip(im, 360, 420, 'AMA LAS PLANTAS', q, col=VG, size=28)
        im = camera(im, lerp(1.12, 1.0, ease(lt / 2.5)), 400, 800)
    else:
        im = BGR_LIGHT.copy()
        off = max(0, t - wt(0, 'todo')) * 120
        grid(im, ['carro', 'cel', 'sofa', 'carro', 'cel', 'sofa', 'sofa', 'carro', 'cel', 'cel'], 330, t, off)
        for k, w_ in enumerate(('carros', 'celulares', 'sofás')):
            q = t - wt(0, w_)
            if q > 0: chip(im, 160 + k * 200, 1180, w_.upper(), q, col=(36, 36, 40), size=22)
    obj('in', (60, 430, 660, 910)); obj('out', (60, 430, 660, 910)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy()
    off = (t - ct(1)) * 900
    kinds = ['carro', 'cel', 'sofa', 'cel', 'carro', 'sofa'] * 6
    grid(im, kinds, 330, t, off % (260 * 3))
    d = BD(im); q = t - wt(1, 'minutos')
    if q > 0:
        d.ellipse((260, 520, 460, 720), fill=(255, 255, 255), outline=RED, width=10); d.text((360, 620), '10 MIN', font=F('Inter-Black.otf', 40), fill=RED, anchor='mm')
    q = t - wt(1, 'matera')
    if q > 0: stamp(im, 360, 950, ['NI UNA MATERA'], RED, q, ang=-6, size=52)
    obj('in', (60, 430, 660, 910)); obj('out', (260, 520, 460, 720)); return im

def sc2(t, lt):
    im = gradient((235, 244, 236), (214, 232, 216))
    fcard(im, (60, 420, 350, 760), 'monstera', fav=t > wt(2, 'favoritos'))
    fcard(im, (370, 420, 660, 760), 'suculenta', fav=t > wt(2, 'suculenta') + .2)
    q = t - wt(2, 'favoritos')
    if q > 0: chip(im, 360, 860, 'GUARDADAS EN FAVORITOS', q, col=RED, size=24)
    q = t - wt(2, 'marketplace')
    if q > 0: chip(im, 360, 340, 'MARKETPLACE SUMIAGO', q, col=(36, 36, 40), size=22)
    obj('in', (260, 520, 460, 720)); obj('out', (60, 420, 660, 760)); return im

def sc3(t, lt):
    im = gradient((235, 244, 236), (214, 232, 216))
    for k in range(2):
        q = t - wt(3, 'abrió') - k * .4
        if q <= 0: continue
        a = ease(q / .4); r = (60 + k * 310, 440, 350 + k * 310, 780); fcard(im, r, 'matera')
        d = BD(im); d.rounded_rectangle((r[0] + 14, r[1] + 14, r[0] + 120, r[1] + 50), 18, fill=(20, 20, 24, int(220 * a))); d.text((r[0] + 67, r[1] + 32), 'Visto', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    obj('in', (60, 420, 660, 760)); obj('out', (60, 440, 660, 780)); return im

PT = ['monstera', 'matera', 'tierra', 'suculenta', 'estante', 'barro']
def sc4(t, lt):
    im = BGR_LIGHT.copy()
    sel = 1 if t > wt(4, 'para') - .1 else 0
    tabs(im, sel)
    if sel: grid(im, PT[:4], 430, t, start=wt(4, 'llena') - .3)
    else: grid(im, ['carro', 'cel', 'sofa', 'carro'], 430, t)
    q = t - wt(4, 'gusta')
    if q > 0: chip(im, 360, 1000, 'LLENA DE LO QUE LE GUSTA', q, col=VG, size=24)
    obj('in', (60, 440, 660, 780)); obj('out', (253, 330, 466, 394)); return im

def sc5(t, lt):
    im = BGR_LIGHT.copy(); tabs(im, 1)
    st = [wt(5, 'plantas'), wt(5, 'materas'), wt(5, 'tierra'), wt(5, 'plantas') + .2, wt(5, 'estante'), wt(5, 'materas') + .2]
    grid(im, PT, 430, t, start=st)
    obj('in', (253, 330, 466, 394)); obj('out', (60, 430, 660, 670)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90)); d = BD(im)
    cx, cy = 360, 920
    ins = [('miras', 'Lo que miras', 120, 460), ('favoritos', 'Favoritos', 600, 460), ('interesa', 'Te interesa', 120, 660), ('ofertas', 'Tus ofertas', 600, 660)]
    for k, (w_, lab, x, y) in enumerate(ins):
        q = t - wt(6, w_)
        if q <= 0: continue
        a = back_out(q / .35); d.ellipse((x - 64 * a, y - 64 * a, x + 64 * a, y + 64 * a), fill=(255, 255, 255))
        if a > .8:
            if k == 0: d.ellipse((x - 34, y - 18, x + 34, y + 18), outline=(30, 30, 36), width=5); d.ellipse((x - 10, y - 10, x + 10, y + 10), fill=(30, 30, 36))
            elif k == 1: z = .9; d.ellipse((x - 30 * z, y - 24 * z, x, y + 6 * z), fill=RED); d.ellipse((x, y - 24 * z, x + 30 * z, y + 6 * z), fill=RED); d.polygon([(x - 29 * z, y - 4 * z), (x + 29 * z, y - 4 * z), (x, y + 30 * z)], fill=RED)
            elif k == 2: d.rounded_rectangle((x - 40, y - 18, x + 40, y + 18), 18, fill=RED); d.text((x, y), '¡Lo quiero!', font=F('Inter-Black.otf', 12), fill='white', anchor='mm')
            else: d.rounded_rectangle((x - 34, y - 22, x + 34, y + 22), 10, fill=GOLD); d.text((x, y), '$?', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
            d.text((x, y + 86), lab, font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
            p = min(1, q / .6); d.line((x, y + 110, lerp(x, cx, p), lerp(y + 110, cy - 80, p)), fill=(255, 255, 255, 120), width=4)
    a = back_out((t - ct(6)) / .4)
    d.ellipse((cx - 90 * a, cy - 90 * a, cx + 90 * a, cy + 90 * a), fill=RED)
    if a > .8: d.text((cx, cy), 'Para ti', font=F('Inter-Black.otf', 34), fill='white', anchor='mm')
    obj('in', (60, 430, 660, 670)); obj('out', (270, 830, 450, 1010)); return im

def sc7(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = t - wt(7, 'país')
    if q > -.3:
        a = back_out((q + .3) / .4); cx, cy = 360, 560
        d.ellipse((cx - 120 * a, cy - 120 * a, cx + 120 * a, cy + 120 * a), fill=(90, 150, 220))
        if a > .8:
            d.ellipse((cx - 70, cy - 60, cx + 10, cy + 20), fill=(90, 170, 100)); d.ellipse((cx + 10, cy - 10, cx + 80, cy + 70), fill=(90, 170, 100)); pin_y = cy - 20
            d.ellipse((cx - 18, pin_y - 44, cx + 18, pin_y - 8), fill=RED); d.polygon([(cx - 15, pin_y - 20), (cx + 15, pin_y - 20), (cx, pin_y + 4)], fill=RED)
        chip(im, 360, 730, 'DE SU MISMO PAÍS', q + .3, col=(36, 36, 40), size=24)
    q = t - wt(7, 'suyos')
    if q > -.2:
        r = (210, 820, 510, 1060); fcard(im, r, 'yo'); d = BD(im)
        if q > 0: p = ease(q / .3); d.line((r[0], r[1], lerp(r[0], r[2], p), lerp(r[1], r[3], p)), fill=RED, width=10); d.line((r[2], r[1], lerp(r[2], r[0], p), lerp(r[1], r[3], p)), fill=RED, width=10)
    obj('in', (270, 830, 450, 1010)); obj('out', (210, 820, 510, 1060)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy(); tabs(im, 1)
    p = ease((t - wt(8, 'baja')) / .8)
    r0 = (60, lerp(430, 950, p), 350, lerp(670, 1190, p)); fcard(im, (370, 430, 660, 670), 'tierra')
    if p > 0: a = ease((p - .2) / .8) if p > .2 else 0; r1 = (60, lerp(950, 430, p), 350, lerp(1190, 670, p)); fcard(im, (60, 690, 350, 930), 'suculenta'); fcard(im, r1, 'estante')
    else: fcard(im, (60, 690, 350, 930), 'suculenta')
    fcard(im, r0, 'monstera'); d = BD(im)
    d.rounded_rectangle((r0[0] + 14, r0[1] + 14, r0[0] + 170, r0[1] + 50), 18, fill=(20, 20, 24)); d.text((r0[0] + 92, r0[1] + 32), 'Visto 3 veces', font=F('Inter-Black.otf', 16), fill='white', anchor='mm')
    q = t - wt(8, 'nuevo')
    if q > 0: chip(im, 360, 1240, 'ESPACIO PARA LO NUEVO', q, col=VG, size=22)
    obj('in', (210, 820, 510, 1060)); obj('out', (60, 430, 350, 670)); return im

def sc9(t, lt):
    im = gradient((250, 236, 214), (236, 214, 190)); d = BD(im)
    d.rectangle((0, 1000, W, H), fill=(190, 160, 130))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); paola(ImageDraw.Draw(L), 360, 760, 1.8, bob=-abs(math.sin(t * 4)) * 4); im.alpha_composite(L); d = BD(im)
    q = t - wt(9, 'materas')
    if q > -.3:
        for k, x in enumerate((230, 490)):
            a = back_out((q + .3 - k * .2) / .35)
            if a > 0: matera(d, x, 1000, 1.3 * a, (160, 90, 60)); monstera(d, x, 1000 - 70 * 1.3, .5 * a) if k == 0 else suculenta(d, x, 1000 - 60, .8 * a)
    q = t - wt(9, 'buscarlas')
    if q > 0: chip(im, 360, 420, 'SIN BUSCARLAS', q, col=RED, size=28)
    obj('in', (60, 430, 350, 670)); obj('out', (190, 880, 530, 1000)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    a = back_out((t - wt(10, 'para') + .1) / .35)
    if a > 0:
        card(im, (360 - 290 * a, 460, 360 + 290 * a, 660), (250, 250, 250), 24); d = BD(im)
        if a > .7:
            d.ellipse((100, 500, 220, 620), fill=RED); d.text((160, 560), 'Para ti', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
            d.text((250, 530), 'Solo usuarios', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm'); d.text((250, 576), 'registrados', font=F('Inter-Black.otf', 28), fill=RED, anchor='lm')
    q = t - wt(10, 'conoce')
    if q > 0: chip(im, 360, 760, 'ENTRE MÁS LA USAS, MEJOR TE CONOCE', q, col=WHITE, tcol=RED, size=22)
    chip(im, 360, 1050, 'MARKETPLACE SUMIAGO', t - wt(10, 'marketplace'), size=24)
    obj('in', (190, 880, 530, 1000)); obj('out', (70, 460, 650, 660)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Marketplace Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tu pestaña «Para ti»', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'APRENDE DE TI', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'deja')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Deja de buscar…', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'y empieza a encontrar.', F('Inter-BlackItalic.otf', 42), WHITE, (t - wt(11, 'empieza') + .3) / .4)
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
