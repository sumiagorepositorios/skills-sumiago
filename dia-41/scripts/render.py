"""Día 41 — "Las citas de Karen" (historia: una manicurista deja el cuaderno y usa la agenda de citas de Mi Negocio en su portada de Sumiago).
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
KEY = {'uñas', 'paz', 'cupo', 'cuatro', 'sábado', '11', 'respondiendo', 'cuaderno', '2', 'misma', 'memoria', 'membresía', 'negocio', 'sumiago', 'agenda', 'días', 'horario', 'dura',
       'enlace', 'libres', 'suya', 'ocupada', 'nadie', 'lugar', '20', 'descansar', 'solas', 'barbería', 'belleza', 'consultas', 'link', 'vale'}
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
        mask_text(im, (W // 2, 800), 'Tu tiempo también vale', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
PINK = (236, 110, 150)
NIGHT = ((22, 26, 52), (10, 12, 26))
# ---------- objetos ----------
def karen(d, x, y, s, bob=0): figure(d, x, y, s, PINK, skin=(204, 150, 112), hair=(60, 30, 24), long=True, bob=bob)
def polish(d, x, y, s, col):
    d.rounded_rectangle((x - 16 * s, y - 10 * s, x + 16 * s, y + 34 * s), 8 * s, fill=col); d.rectangle((x - 7 * s, y - 34 * s, x + 7 * s, y - 10 * s), fill=(40, 40, 46))
def salon_bg():
    im = gradient((255, 236, 242), (246, 214, 226)); d = BD(im)
    d.rounded_rectangle((470, 330, 680, 560), 12, fill=(255, 255, 255), outline=(230, 200, 210), width=6)
    for k, c in enumerate([RED, PINK, (160, 90, 200), (240, 170, 60), (60, 160, 200)]): polish(d, 510 + k * 36, 470, .8, c)
    d.rectangle((0, 900, W, H), fill=(230, 200, 210)); d.rounded_rectangle((60, 780, 660, 900), 16, fill=(255, 255, 255)); d.rectangle((60, 880, 660, 900), fill=(220, 190, 200))
    return im
BGK2 = salon_bg()
SLOTS = ['9:00', '10:00', '11:00', '2:00', '3:00', '4:00', '5:00', '6:00']
def slot_grid(im, r, t, taken=(1, 4), pick=None, pick_q=0.0, deny=None, deny_q=0.0):
    d = BD(im); x0, y0 = r[0] + 30, r[1]
    for k, s_ in enumerate(SLOTS):
        cw = (r[2] - r[0] - 20) / 4; cx = r[0] + 10 + (k % 4) * cw + cw / 2; cy = y0 + (k // 4) * 80 + 40; hw = cw / 2 - 5
        busy = k in taken; sel = (k == pick and pick_q > 0)
        col = (220, 222, 230) if busy else (GREEN_OK if sel else (255, 255, 255))
        dx = math.sin(t * 60) * 6 * max(0, 1 - deny_q * 2) if (k == deny and deny_q > 0) else 0
        d.rounded_rectangle((cx - hw + dx, cy - 28, cx + hw + dx, cy + 28), 14, fill=col, outline=RED if (k == deny and deny_q > 0) else (200, 202, 210), width=3)
        d.text((cx + dx, cy - (8 if busy else 0)), s_, font=F('Inter-Black.otf', 20), fill='white' if sel else ((150, 150, 160) if busy else (30, 30, 36)), anchor='mm')
        if busy: d.text((cx + dx, cy + 14), 'ocupado', font=F('Inter-Bold.otf', 12), fill=RED, anchor='mm')
    return d

# ---------- escenas ----------
def sc0(t, lt):
    im = BGK2.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); karen(ImageDraw.Draw(L), 250, 620, 1.7); im.alpha_composite(L); d = BD(im)
    for k, c in enumerate([RED, PINK, (160, 90, 200)]): polish(d, 400 + k * 50, 750, 1.0, c)
    q = t - wt(0, 'celular')
    sh = math.sin(t * 50) * 6 if q > 0 else 0
    d.rounded_rectangle((540 + sh, 690, 610 + sh, 800), 12, fill=(30, 30, 36)); d.rectangle((548 + sh, 700, 602 + sh, 790), fill=(200, 220, 255))
    if q > 0:
        n = min(27, int(q * 12) + 1); d.ellipse((590 + sh, 670, 640 + sh, 720), fill=RED); d.text((615 + sh, 695), str(n), font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    chip(im, 360, 1040, 'NO LA DEJA EN PAZ', t - wt(0, 'paz'), col=(36, 36, 40), size=26)
    im = camera(im, lerp(1.2, 1.0, ease(lt / 3)), 400, 720)
    obj('in', (520, 670, 650, 810)); obj('out', (520, 670, 650, 810)); return im

def sc1(t, lt):
    im = gradient(*NIGHT); d = BD(im)
    msgs = [('cupo', '¿Tienes cupo mañana?'), ('cuatro', '¿Y a las cuatro?'), ('sábado', '¿Y el sábado?')]
    for k, (w_, m) in enumerate(msgs): bubble(im, 60 + (k % 2) * 160, 430 + k * 110, m, t - wt(1, w_) + .2, col=(255, 255, 255), tcol=(36, 36, 40), size=30)
    n = int(ease((t - wt(1, '11')) / .4) * 1)
    chip(im, 360, 830, '11:00 p. m.', t - wt(1, '11'), col=RED, size=34)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); karen(ImageDraw.Draw(L), 360, 980, 1.4); im.alpha_composite(L)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((300, 960, 420, 1060), fill=255), (180, 210, 255), 30, 140))
    fq = ease((t - wt(1, '11') + .2) / .6)
    im = camera(im, 1.05, 360, lerp(600, 900, fq))
    obj('in', (60, 430, 460, 510)); obj('out', (230, 790, 490, 870)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    r = (110, 380, 610, 820); card(im, r, (252, 248, 236), 16); d = BD(im)
    d.rectangle((r[0], r[1], r[0] + 30, r[3]), fill=(200, 60, 80))
    for k in range(7): d.line((r[0] + 50, r[1] + 70 + k * 52, r[2] - 30, r[1] + 70 + k * 52), fill=(210, 220, 236), width=2)
    rows = [('3:00', 'Lina'), ('4:00', 'Sandra'), ('3:00', 'Marcela')]
    for k, (h, n) in enumerate(rows):
        a = ease((lt - .3 - k * .3) / .3)
        if a > 0: d.text((r[0] + 60, r[1] + 60 + k * 52), f'{h} - {n}', font=F('Inter-SemiBoldItalic.otf', 30), fill=(60, 60, 90), anchor='lm')
    q = t - wt(2, '2')
    if q > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        for k in range(2): figure(dl, lerp(-60 if k == 0 else W + 60, 260 + k * 200, ease(q / .6)), 940, 1.4, [(90, 120, 200), (200, 140, 60)][k], long=True)
        im.alpha_composite(L); d = BD(im)
        for k in range(2): bubble(im, 160 + k * 220, 870, '3:00', q - .5, col=RED, size=24)
    q = t - wt(2, 'misma')
    if q > 0: stamp(im, 360, 640, ['MISMA HORA'], RED, q, ang=-8, size=54)
    obj('in', (230, 790, 490, 870)); obj('out', r); return im

def sc3(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); karen(ImageDraw.Draw(L), 360, 760, 2.0); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(3, 'agenda')) / .4)
    if q > 0:
        d.ellipse((420, 420, 640, 600), fill=(255, 255, 255), outline=(200, 202, 210), width=3); d.ellipse((400, 610, 430, 640), fill=(255, 255, 255)); d.ellipse((380, 650, 396, 666), fill=(255, 255, 255))
        d.rounded_rectangle((480, 460, 580, 560), 10, fill=(252, 248, 236)); d.line((480, 460, 580, 560), fill=RED, width=8); d.line((480, 560, 580, 460), fill=RED, width=8)
    q = t - wt(3, 'memoria')
    if q > 0: stamp(im, 360, 1100, ['NO MÁS DE MEMORIA'], RED, q, ang=-5, size=44)
    obj('in', (110, 380, 610, 820)); obj('out', (420, 420, 640, 600)); return im

TABS = ['Catálogo', 'Cobros USDT', 'Agenda', 'Clientes']
def negocio_panel(im, r, t, on_q):
    card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((r[0] + 30, r[1] + 44), 'Mi Negocio', font=F('Inter-Black.otf', 32), fill=(30, 30, 36), anchor='lm')
    d.rounded_rectangle((r[2] - 110, r[1] + 26, r[2] - 30, r[1] + 62), 18, fill=RED); d.text((r[2] - 70, r[1] + 44), 'PRO', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    x = r[0] + 30
    for tb in TABS:
        f = F('Inter-Bold.otf', 18); tw = d.textlength(tb, font=f) + 26; on = tb == 'Agenda'
        d.rounded_rectangle((x, r[1] + 86, x + tw, r[1] + 122), 18, fill=RED if on else (240, 240, 244)); d.text((x + tw / 2, r[1] + 104), tb, font=f, fill='white' if on else (90, 90, 100), anchor='mm'); x += tw + 8
    y = r[1] + 160
    d.rounded_rectangle((r[0] + 30, y, r[2] - 30, y + 70), 16, fill=(244, 244, 247))
    d.text((r[0] + 50, y + 35), 'Recibir reservas desde mi portada', font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='lm')
    tx = r[2] - 110; d.rounded_rectangle((tx, y + 20, tx + 60, y + 50), 15, fill=mix((190, 190, 200), GREEN_OK, on_q)); d.ellipse((tx + 3 + 30 * on_q, y + 23, tx + 27 + 30 * on_q, y + 47), fill='white')
    return y + 90

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 480, 660, 760); negocio_panel(im, r, t, ease((t - wt(4, 'agenda')) / .4))
    chip(im, 360, 420, 'CON MEMBRESÍA', t - wt(4, 'membresía'), col=WHITE, tcol=RED, size=26)
    q = t - wt(4, 'agenda')
    if q > 0: chip(im, 360, 840, 'AGENDA DE CITAS: ACTIVA', q, col=GREEN_OK, size=24)
    fq = ease((t - wt(4, 'agenda') + .2) / .6)
    im = camera(im, 1.0 + .18 * fq, 360, lerp(640, 680, fq))
    obj('in', (420, 420, 640, 600)); obj('out', (90, 640, 630, 710)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 380, 660, 1140); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 430), 'Días', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm')
    for k, dd_ in enumerate('LMMJVSD'):
        a = back_out((t - wt(5, 'días') - k * .07) / .3); on = k < 6
        if a > 0:
            cx = 110 + k * 76; d.ellipse((cx - 28 * a, 490 - 28 * a, cx + 28 * a, 490 + 28 * a), fill=RED if on else (230, 230, 236))
            if a > .7: d.text((cx, 490), dd_, font=F('Inter-Black.otf', 22), fill='white' if on else (150, 150, 160), anchor='mm')
    d.text((90, 590), 'Horario', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm')
    a = ease((t - wt(5, 'horario')) / .4)
    if a > 0:
        for k, h in enumerate(('9:00 a. m.', '6:00 p. m.')):
            x = 90 + k * 290; d.rounded_rectangle((x, 620, x + 250, 690), 16, fill=(244, 244, 247)); d.text((x + 125, 655), h, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='mm')
        d.text((360, 655), '→', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    d.text((90, 760), 'Cada cita dura', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='lm')
    a = back_out((t - wt(5, 'dura')) / .35)
    if a > 0:
        d.rounded_rectangle((360 - 150 * a, 800, 360 + 150 * a, 880), 20, fill=RED)
        if a > .7: d.text((360, 840), '1 hora', font=F('Inter-Black.otf', 36), fill='white', anchor='mm')
    d.rounded_rectangle((90, 960, 630, 1040), 20, fill=(36, 36, 40)); d.text((360, 1000), 'Guardar', font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
    obj('in', (90, 640, 630, 710)); obj('out', (90, 960, 630, 1040)); return im

def client_phone(im, t, pick_q, deny=None, deny_q=0.0, label='Agenda tu cita'):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.3, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((179, 440, 541, 520), fill=PINK); d.text((360, 470), 'Uñas Karen', font=F('Inter-Black.otf', 28), fill='white', anchor='mm'); d.text((360, 504), 'sumiago.com/unas-karen', font=F('Inter-SemiBold.otf', 16), fill=(255, 230, 240), anchor='mm')
    d.text((360, 560), label, font=F('Inter-Black.otf', 26), fill='white', anchor='mm')
    d.rounded_rectangle((200, 590, 520, 640), 14, fill=(40, 42, 54)); d.text((360, 615), 'Viernes 28', font=F('Inter-Bold.otf', 22), fill='white', anchor='mm')
    slot_grid(im, (185, 660, 535, 840), t, pick=5, pick_q=pick_q, deny=deny, deny_q=deny_q)

def sc6(t, lt):
    im = BGK2.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 60)))
    pq = t - wt(6, 'escoge')
    client_phone(im, t, pq)
    tq = pq - .1
    if 0 < tq < .5: d = BD(im); rr = 20 + tq * 140; cx = 195 + 1 * 82.5 + 41; d.ellipse((cx - rr, 780 - rr, cx + rr, 780 + rr), outline=(255, 255, 255, int(255 * (1 - tq / .5))), width=5)
    q = t - wt(6, 'libres')
    if q > 0: chip(im, 360, 1130, 'HORAS LIBRES', q, col=GREEN_OK, size=24)
    if pq > .4: chip(im, 360, 960, 'Reservado: 4:00 p. m.', pq - .4, col=(36, 36, 40), size=22)
    fq = ease((t - wt(6, 'horas') + .1) / .6)
    im = camera(im, 1.0 + .2 * fq, 360, lerp(760, 760, fq))
    obj('in', (179, 440, 541, 1160)); obj('out', (160, 660, 560, 840)); return im

def sc7(t, lt):
    im = BGK2.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 60)))
    dq = t - wt(7, 'ocupada') + .2
    client_phone(im, t, 0, deny=4, deny_q=dq)
    q = t - wt(7, 'nadie')
    if q > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lock(ImageDraw.Draw(L), 600, 740, back_out(q / .35)); im.alpha_composite(L)
        stamp(im, 360, 1060, ['NADIE MÁS LA TOMA'], RED, q, ang=-5, size=40)
    im = camera(im, 1.15, 360, 780)
    obj('in', (160, 660, 560, 840)); obj('out', (179, 440, 541, 1160)); return im
def lock(d, cx, cy, s, col=RED):
    d.arc((cx - 22 * s, cy - 50 * s, cx + 22 * s, cy - 6 * s), 180, 360, fill=col, width=max(2, int(8 * s)))
    d.line((cx - 22 * s, cy - 28 * s, cx - 22 * s, cy - 6 * s), fill=col, width=max(2, int(8 * s))); d.line((cx + 22 * s, cy - 28 * s, cx + 22 * s, cy - 6 * s), fill=col, width=max(2, int(8 * s)))
    d.rounded_rectangle((cx - 36 * s, cy - 10 * s, cx + 36 * s, cy + 44 * s), 10 * s, fill=col)

CITAS = [('9:00', 'Lina', 'Manicure'), ('11:00', 'Sandra', 'Pedicure'), ('3:00', 'Marcela', 'Uñas acrílicas'), ('5:00', 'Paola', 'Manicure')]
def sc8(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    r = (60, 380, 660, 960); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 430), 'Mis citas · Viernes 28', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm')
    for k, (h, n, s_) in enumerate(CITAS):
        a = ease((t - wt(8, 'citas') - k * .15) / .35)
        if a <= 0: continue
        y = 480 + k * 112; d.rounded_rectangle((90, y, 90 + 540 * a, y + 96), 16, fill=(250, 240, 244))
        if a > .8:
            d.rounded_rectangle((106, y + 20, 206, y + 76), 12, fill=PINK); d.text((156, y + 48), h, font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
            d.text((226, y + 34), n, font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm'); d.text((226, y + 68), s_, font=F('Inter-SemiBold.otf', 20), fill=(120, 120, 130), anchor='lm')
    q = t - wt(8, 'cuaderno')
    if q > 0:
        a = ease(q / .8); cx, cy = lerp(200, 600, a), lerp(1100, 1250, a)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); dl.rounded_rectangle((cx - 60, cy - 40, cx + 60, cy + 40), 8, fill=(252, 248, 236)); dl.rectangle((cx - 60, cy - 40, cx - 48, cy + 40), fill=(200, 60, 80))
        L = L.rotate(a * 40, center=(cx, cy)); L.putalpha(L.getchannel('A').point(lambda p: int(p * (1 - a * .7)))); im.alpha_composite(L)
    chip(im, 500, 1040, 'SIN REPETIR 20 VECES', t - wt(8, '20'), size=22)
    obj('in', (179, 440, 541, 1160)); obj('out', r); return im

def sc9(t, lt):
    im = gradient(*NIGHT); d = BD(im)
    d.ellipse((540, 390, 640, 490), fill=(250, 240, 200)); d.ellipse((520, 370, 620, 470), fill=NIGHT[0])
    d.rounded_rectangle((80, 860, 640, 1010), 30, fill=(70, 90, 150)); d.rounded_rectangle((80, 820, 220, 880), 20, fill=(240, 240, 246)); d.ellipse((120, 810, 180, 870), fill=(204, 150, 112))
    for k in range(3):
        q = (t * .4 + k / 3) % 1; d.text((240 + k * 34 + q * 40, 790 - q * 90), 'z', font=F('Inter-Black.otf', 30 + k * 8), fill=(200, 210, 255, int(255 * math.sin(math.pi * q))), anchor='mm')
    q = t - wt(9, 'solas')
    for k in range(3):
        a = ease((q - k * .4) / .4)
        if a > 0:
            y = 560 + k * 80; r = (300, y, 660, y + 64); card(im, (r[0] + (1 - a) * 80, r[1], r[2], r[3]), (255, 255, 255), 16); d = BD(im)
            if a > .8: d.ellipse((316, y + 14, 352, y + 50), fill=GREEN_OK); d.text((368, y + 32), ['Nueva cita: Ana · 10:00', 'Nueva cita: Luz · 2:00', 'Nueva cita: Eva · 4:00'][k], font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 1120, 'A DESCANSAR', t - wt(9, 'descansar'), col=WHITE, tcol=(36, 36, 40), size=26)
    obj('in', (60, 380, 660, 960)); obj('out', (300, 560, 660, 784)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('cita', 'Uñas', PINK), ('barbería', 'Barbería', (60, 110, 200)), ('belleza', 'Belleza', (160, 90, 200)), ('consultas', 'Consultas', GREEN_OK)]
    for k, (w_, lab, c) in enumerate(items):
        a = back_out((t - wt(10, w_) + .15) / .35)
        if a <= 0: continue
        x = 200 + (k % 2) * 320; y = 560 + (k // 2) * 300; w, h = 260 * a, 240 * a
        card(im, (x - w / 2, y - h / 2, x + w / 2, y + h / 2), (250, 250, 250), 24); d = BD(im)
        if a > .7: d.ellipse((x - 50, y - 90, x + 50, y + 10), fill=c); d.text((x, y - 40), lab[0], font=F('Inter-Black.otf', 50), fill='white', anchor='mm'); d.text((x, y + 70), lab, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='mm')
    q = t - wt(10, 'agenda')
    if q > 0: chip(im, 360, 1180, 'AGENDA EN MI NEGOCIO', q, size=26)
    obj('in', (300, 560, 660, 784)); obj('out', (70, 440, 330, 680)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Negocio', F('Inter-Black.otf', 34), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Agenda de citas en tu portada', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'TUS CLIENTES RESERVAN SOLOS', t - wt(11, 'regístrate'), size=18)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'tiempo')
    if q > -.3: mask_text(im, (W / 2, 760), 'Tu tiempo también vale.', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
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
