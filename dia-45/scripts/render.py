"""Día 45 — "El cliente de otro país" (historia: una diseñadora recibe pagos de un cliente extranjero con los cobros en USDT de Mi Negocio en su portada de Sumiago).
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
KEY = {'daniela', 'logos', 'país', 'trabajo', 'pagar', 'transferencias', 'comisiones', 'espera…', 'espera', 'papeles', 'usdt', 'sumiago', 'membresía', 'negocio', 'billetera', 'bep20', 'montos',
       'qr', 'copiar', 'escaneó', 'directo', 'guarda', 'toca', 'esquina…', 'esquina', 'mundo', 'link', 'fronteras…', 'fronteras', 'tampoco'}
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
        mask_text(im, (W // 2, 800), 'Cobra en cualquier país', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
TEAL = (38, 161, 123)
# ---------- objetos ----------
def daniela(d, x, y, s, bob=0): figure(d, x, y, s, (60, 160, 180), skin=(214, 166, 128), hair=(60, 36, 24), long=True, bob=bob)
def coin(d, cx, cy, r, label='USDT'):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=TEAL, outline=mix(TEAL, (0, 0, 0), .25), width=max(2, int(r / 8)))
    d.text((cx, cy), label, font=F('Inter-Black.otf', max(8, int(r * .55))), fill='white', anchor='mm')
def globe(d, cx, cy, r, t=0):
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(70, 130, 200))
    rr = random.Random(5)
    for k in range(6):
        a = k * 1.1 + t * .3; x = cx + math.cos(a) * r * .5; y = cy + math.sin(a * 1.3) * r * .45
        if (x - cx) ** 2 + (y - cy) ** 2 < (r * .8) ** 2: d.ellipse((x - r * .25, y - r * .15, x + r * .25, y + r * .18), fill=(110, 180, 110))
    d.arc((cx - r, cy - r, cx + r, cy + r), 0, 360, fill=(40, 90, 150), width=4)
def wallet_icon(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 70 * s, cy - 50 * s, cx + 70 * s, cy + 50 * s), 14 * s, fill=(36, 36, 40)); d.rounded_rectangle((cx + 20 * s, cy - 18 * s, cx + 80 * s, cy + 18 * s), 10 * s, fill=(60, 60, 66)); d.ellipse((cx + 34 * s, cy - 8 * s, cx + 50 * s, cy + 8 * s), fill=GOLD)
def qr(d, x, y, size, seed=11):
    n = 21; c = size / n; rr = random.Random(seed)
    d.rectangle((x - c, y - c, x + size + c, y + size + c), fill=(255, 255, 255))
    for i in range(n):
        for j in range(n):
            if (i < 7 and j < 7) or (i < 7 and j >= n - 7) or (i >= n - 7 and j < 7): continue
            if rr.random() < .5: d.rectangle((x + i * c, y + j * c, x + (i + 1) * c, y + (j + 1) * c), fill=(20, 20, 24))
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        X, Y = x + fx * c, y + fy * c
        d.rectangle((X, Y, X + 7 * c, Y + 7 * c), fill=(20, 20, 24)); d.rectangle((X + c, Y + c, X + 6 * c, Y + 6 * c), fill='white'); d.rectangle((X + 2 * c, Y + 2 * c, X + 5 * c, Y + 5 * c), fill=(20, 20, 24))
WAL = '0x8f3A…91c2'
def pay_section(im, r, t, copy_q=0.0):
    card(im, r, (255, 255, 255), 20); d = BD(im); cx = (r[0] + r[2]) / 2
    coin(d, cx - 120, r[1] + 42, 20, '₮'.replace('₮', '$')); d.text((cx + 14, r[1] + 42), 'Págame en USDT', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
    qr(d, cx - 90, r[1] + 80, 180)
    d.rounded_rectangle((r[0] + 20, r[1] + 280, r[2] - 20, r[1] + 316), 10, fill=(244, 244, 247)); d.text((cx, r[1] + 298), WAL + '  · BEP20', font=F('Inter-Bold.otf', 17), fill=(60, 60, 70), anchor='mm')
    d.rounded_rectangle((r[0] + 40, r[1] + 330, r[2] - 40, r[1] + 374), 22, fill=GREEN_OK if copy_q > 0 else RED); d.text((cx, r[1] + 352), '¡Copiada!' if copy_q > 0 else 'Copiar dirección', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')

# ---------- escenas ----------
def sc0(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.rectangle((0, 900, W, H), fill=(200, 190, 180))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); daniela(ImageDraw.Draw(L), 180, 760, 1.6); im.alpha_composite(L); d = BD(im)
    d.rounded_rectangle((300, 620, 620, 820), 14, fill=(40, 42, 50)); d.rounded_rectangle((314, 634, 606, 806), 8, fill=(250, 250, 252)); d.polygon([(270, 846), (650, 846), (620, 820), (300, 820)], fill=(170, 174, 186))
    q = ease((lt - .2) / 1.2)   # logo que se dibuja
    d.ellipse((410, 660, 410 + 100 * q, 660 + 100 * q), fill=RED); d.rounded_rectangle((470, 690, 470 + 90 * q, 750), 10, fill=(36, 36, 40))
    q2 = t - wt(0, 'cliente')
    if q2 > 0:
        a = ease(q2 / .4); r = (300, 430 - (1 - a) * 30, 680, 540 - (1 - a) * 30); card(im, r, (255, 255, 255), 20); d = BD(im)
        globe(d, r[0] + 56, (r[1] + r[3]) / 2, 34, t); d.text((r[0] + 110, r[1] + 40), 'Nuevo cliente', font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm'); d.text((r[0] + 110, r[1] + 76), 'Desde otro país', font=F('Inter-SemiBold.otf', 20), fill=(110, 110, 120), anchor='lm')
    im = camera(im, lerp(1.2, 1.0, ease(lt / 3)), 400, 700)
    obj('in', (300, 620, 620, 820)); obj('out', (300, 430, 680, 540)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    bubble(im, 80, 460, '¡Me encantó el logo!', lt - .1, col=(70, 130, 200), size=32)
    q = t - wt(1, 'pagar')
    if q > -.2: bubble(im, 160, 600, '¿Cómo te pago?', q + .2, col=(70, 130, 200), size=32)
    if q > 0: d = BD(im); d.text((360, 900), '$ ?', font=F('Inter-Black.otf', int(120 * back_out(q / .4)) + 1), fill=RED, anchor='mm')
    obj('in', (300, 430, 680, 540)); obj('out', (230, 800, 490, 1000)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # banco con reloj
    d.polygon([(130, 520), (360, 420), (590, 520)], fill=(110, 114, 126)); d.rectangle((150, 520, 570, 760), fill=(200, 204, 214))
    for k in range(4): d.rectangle((180 + k * 100, 540, 220 + k * 100, 740), fill=(160, 164, 176))
    d.rectangle((130, 760, 590, 790), fill=(110, 114, 126))
    items = [('transferencias', 'TRANSFERENCIA INTERNACIONAL', 380), ('comisiones', 'COMISIONES', 860), ('espera', 'DÍAS DE ESPERA', 940), ('papeles', 'PAPELES', 1020)]
    for k, (w_, lab, y) in enumerate(items):
        if k == 0: chip(im, 360, y, lab, t - wt(2, w_), col=(36, 36, 40), size=22)
        else: chip(im, 360, y, lab, t - wt(2, w_), col=RED if k < 3 else (90, 90, 100), size=24)
    q = t - wt(2, 'papeles')
    for k in range(5):
        a = ease((q - k * .1) / .4)
        if a > 0:
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); x = 120 + k * 120; y = 1150 - k * 8
            dl.rectangle((x - 50, y - 60, x + 50, y + 60), fill=(255, 255, 255), outline=(200, 202, 210), width=2)
            for j in range(4): dl.line((x - 36, y - 36 + j * 22, x + 36, y - 36 + j * 22), fill=(200, 202, 210), width=3)
            L = L.rotate((k - 2) * 8, center=(x, y)); L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L)
    im = camera(im, 1.0, 360, 760)
    obj('in', (230, 800, 490, 1000)); obj('out', (150, 420, 570, 790)); return im

def sc3(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    bubble(im, 90, 560, '¿No recibes en USDT?', t - wt(3, 'recibes') + .2, col=(70, 130, 200), size=36)
    q = t - wt(3, 'usdt')
    if q > 0:
        d = BD(im); b = back_out(q / .4)
        for k in range(3): coin(d, 240 + k * 120, 820 + math.sin(t * 4 + k) * 10, 50 * b + 1)
    obj('in', (150, 420, 570, 790)); obj('out', (190, 770, 530, 870)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 500, 660, 800); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((r[0] + 30, r[1] + 44), 'Mi Negocio', font=F('Inter-Black.otf', 32), fill=(30, 30, 36), anchor='lm')
    d.rounded_rectangle((r[2] - 110, r[1] + 26, r[2] - 30, r[1] + 62), 18, fill=RED); d.text((r[2] - 70, r[1] + 44), 'PRO', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    x = r[0] + 30
    for tb in ['Catálogo', 'Cobros USDT', 'Agenda', 'Clientes']:
        f = F('Inter-Bold.otf', 18); tw = d.textlength(tb, font=f) + 26; on = tb == 'Cobros USDT'
        d.rounded_rectangle((x, r[1] + 86, x + tw, r[1] + 122), 18, fill=RED if on else (240, 240, 244)); d.text((x + tw / 2, r[1] + 104), tb, font=f, fill='white' if on else (90, 90, 100), anchor='mm'); x += tw + 8
    y = r[1] + 150; on_q = ease((t - wt(4, 'cobros')) / .4)
    d.rounded_rectangle((r[0] + 30, y, r[2] - 30, y + 110), 16, fill=(244, 244, 247))
    d.text((r[0] + 50, y + 40), 'Mostrar cobros en USDT', font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm'); d.text((r[0] + 50, y + 72), 'en mi portada', font=F('Inter-SemiBold.otf', 18), fill=(120, 120, 130), anchor='lm')
    tx = r[2] - 110; d.rounded_rectangle((tx, y + 36, tx + 60, y + 66), 15, fill=mix((190, 190, 200), GREEN_OK, on_q)); d.ellipse((tx + 3 + 30 * on_q, y + 39, tx + 27 + 30 * on_q, y + 63), fill='white')
    chip(im, 360, 440, 'CON SU MEMBRESÍA', t - wt(4, 'membresía'), col=WHITE, tcol=RED, size=24)
    im = camera(im, 1.0 + .12 * on_q, 360, 660)
    obj('in', (190, 770, 530, 870)); obj('out', (r[0] + 30, y, r[2] - 30, y + 110)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 420, 660, 1080); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 470), 'Mi dirección de wallet', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm')
    d.rounded_rectangle((90, 500, 630, 570), 14, fill=(244, 244, 247))
    full = '0x8f3A5c0d27b4E91c2'; n = int(len(full) * ease((t - wt(5, 'dirección') + .1) / 1.0)); d.text((110, 535), full[:n], font=F('Inter-Bold.otf', 26), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 620, 'RED BNB SMART CHAIN · BEP20', t - wt(5, 'bep20'), col=(36, 36, 40), size=20)
    d.text((90, 700), 'Montos sugeridos', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm')
    for k, m in enumerate(['50', '100', '200']): chip(im, 170 + k * 190, 770, f'{m} USDT', t - wt(5, 'montos') - k * .12, col=TEAL, size=24)
    d = BD(im); d.rounded_rectangle((90, 880, 630, 1040), 16, fill=(255, 247, 230))
    d.text((360, 930), 'El dinero llega directo a tu wallet.', font=F('Inter-Bold.otf', 20), fill=(150, 90, 20), anchor='mm'); d.text((360, 966), 'Sumiago no guarda ni toca tus fondos.', font=F('Inter-Bold.otf', 20), fill=(150, 90, 20), anchor='mm'); d.text((360, 1002), 'Revisa bien la dirección.', font=F('Inter-Bold.otf', 20), fill=(150, 90, 20), anchor='mm')
    obj('in', (90, 650, 630, 760)); obj('out', (90, 500, 630, 570)); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((186, 440, 534, 520), fill=(60, 160, 180)); d.text((360, 470), 'Daniela Diseño', font=F('Inter-Black.otf', 26), fill='white', anchor='mm'); d.text((360, 502), 'sumiago.com/daniela-diseno', font=F('Inter-SemiBold.otf', 15), fill=(220, 240, 245), anchor='mm')
    q = ease((t - wt(6, 'págame') + .2) / .5)
    if q > 0:
        Lp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pay_section(Lp, (200, 540, 520, 940), t, copy_q=t - wt(6, 'copiar') - .3); Lp.putalpha(Lp.getchannel('A').point(lambda p: int(p * q))); im.alpha_composite(Lp)
    d = BD(im)
    for k, m in enumerate(['50', '100', '200']):
        a = back_out((t - wt(6, 'qr') - k * .1) / .3)
        if a > 0: d.rounded_rectangle((216 + k * 100, 960, 304 + k * 100, 1000), 18, fill=TEAL); d.text((260 + k * 100, 980), m, font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    fq = ease((t - wt(6, 'qr') + .2) / .6)
    im = camera(im, 1.0 + .2 * fq, 360, lerp(760, 760, fq))
    obj('in', (90, 500, 630, 570)); obj('out', (270, 620, 450, 800)); return im

def sc7(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # celular del cliente escaneando
    def content(dd, cx, cy, w, h):
        dd.rectangle((cx - w / 2 + 14, cy - h / 2 + 60, cx + w / 2 - 14, cy + h / 2 - 60), fill=(40, 40, 46))
        qr(dd, cx - 60, cy - 60, 120)
        yy = cy - 60 + 120 * ((t * 1.3) % 1); dd.line((cx - 76, yy, cx + 76, yy), fill=GREEN_OK, width=4)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 170, 620, .62, content); im.alpha_composite(L); d = BD(im)
    d.text((170, 860), 'Cliente', font=F('Inter-Black.otf', 24), fill=(90, 90, 100), anchor='mm')
    wallet_icon(d, 560, 640, 1.3); d.text((560, 860), 'Billetera de Daniela', font=F('Inter-Black.otf', 22), fill=(90, 90, 100), anchor='mm')
    q = t - wt(7, 'envió')
    for k in range(6):
        p = (q - k * .15) / .9
        if 0 < p < 1:
            x = lerp(250, 500, ease(p)); y = 620 - math.sin(math.pi * p) * 160; coin(d, x, y, 26)
    q2 = t - wt(7, 'directo')
    if q2 > 0:
        chip(im, 560, 520, '+100 USDT', q2, col=TEAL, size=28)
        stamp(im, 360, 1060, ['DIRECTO A SU BILLETERA'], RED, q2, ang=-5, size=38)
    obj('in', (270, 620, 450, 800)); obj('out', (450, 560, 680, 720)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), 130, 640, 1.4, (70, 130, 200)); im.alpha_composite(L); d = BD(im)
    d.text((130, 850), 'Tu cliente', font=F('Inter-Black.otf', 22), fill=(60, 60, 70), anchor='mm')
    wallet_icon(d, 590, 600, 1.0); d.text((590, 700), 'Tu billetera', font=F('Inter-Black.otf', 22), fill=(60, 60, 70), anchor='mm')
    p = ease((t - ct(8)) / .8); d.line((200, 600, lerp(200, 500, p), 600), fill=TEAL, width=12)
    if p > .95: d.polygon([(520, 600), (490, 580), (490, 620)], fill=TEAL)
    q = t - wt(8, 'guarda')
    if q > 0:
        a = back_out(q / .4); r = (230, 860, 490, 1080); card(im, (360 - 130 * a, 970 - 110 * a, 360 + 130 * a, 970 + 110 * a), (255, 255, 255), 22)
        if a > .7: im.alpha_composite(LOGO_S.resize((200, int(200 * LOGO_S.height / LOGO_S.width))), (260, 890)); d = BD(im); d.text((360, 1030), 'No guarda ni toca', font=F('Inter-Black.otf', 22), fill=RED, anchor='mm'); d.text((360, 1060), 'tu dinero', font=F('Inter-Black.otf', 22), fill=RED, anchor='mm')
    obj('in', (450, 560, 680, 720)); obj('out', (520, 540, 660, 660)); return im

def sc9(t, lt):
    im = gradient((14, 18, 40), (6, 8, 20)); d = BD(im)
    rr = random.Random(2)
    for k in range(40): x, y = rr.random() * W, rr.random() * H; d.ellipse((x - 1.5, y - 1.5, x + 1.5, y + 1.5), fill=(255, 255, 255, 140))
    globe(d, 360, 760, 230, t)
    pins = [('esquina', (330, 700), 'Tu barrio'), ('mundo', (500, 900), 'Otro país')]
    for w_, (x, y), lab in pins:
        q = back_out((t - wt(9, w_)) / .35)
        if q > 0: d.ellipse((x - 18 * q, y - 18 * q, x + 18 * q, y + 18 * q), fill=RED); chip(im, x, y - 50, lab, t - wt(9, w_), col=WHITE, tcol=RED, size=20); d = BD(im)
    q = ease((t - wt(9, 'mundo')) / .8)
    if q > 0:
        pts = [(330 + (500 - 330) * k / 20, 700 + (900 - 700) * k / 20 - math.sin(math.pi * k / 20) * 160) for k in range(int(20 * q) + 1)]
        if len(pts) > 1: d.line(pts, fill=GOLD, width=6)
    obj('in', (520, 540, 660, 660)); obj('out', (130, 530, 590, 990)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    for k, (w_, lab) in enumerate((('servicios', 'Servicios'), ('productos', 'Productos'))):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        x = 200 + k * 320; y = 640; w, h = 260 * a, 240 * a; card(im, (x - w / 2, y - h / 2, x + w / 2, y + h / 2), (250, 250, 250), 24); d = BD(im)
        if a > .7: coin(d, x, y - 30, 50); d.text((x, y + 70), lab, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='mm')
    q = t - wt(10, 'país')
    if q > 0: d = BD(im); globe(d, 360, 930, 80 * back_out(q / .4) + 1, t)
    chip(im, 360, 1100, 'COBROS EN USDT · MI NEGOCIO', t - wt(10, 'usdt'), size=22)
    obj('in', (130, 530, 590, 990)); obj('out', (70, 520, 330, 760)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Negocio · Cobros USDT', F('Inter-Black.otf', 30), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Directo a tu billetera (BEP20)', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'CON QR Y MONTOS SUGERIDOS', t - wt(11, 'regístrate'), col=TEAL, size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'fronteras')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Tu trabajo no tiene fronteras…', F('Inter-BlackItalic.otf', 38), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 792), 'tus cobros tampoco.', F('Inter-BlackItalic.otf', 38), WHITE, (t - wt(11, 'tampoco') + .3) / .4)
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
