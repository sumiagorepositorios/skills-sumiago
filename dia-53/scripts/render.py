"""Día 53 — "¿Y si me estafas?" (historia: Andrés, vendedor nuevo de celulares usados, gana confianza con su reputación en el Marketplace de Sumiago).
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
KEY = {'andrés', 'celulares', 'revisados', 'estafas', 'nadie', 'creen', 'marketplace', 'sumiago', 'vendedor', 'verificado', 'whatsapp', 'miembro', 'vendido', 'nuevo', 'calificaciones', 'califícame', 'estrellas', 'fotos', 'termómetro', 'reputación', 'verde', 'confiable', 'tienes', 'califica', 'quiero', 'vista', 'link', 'confianza', 'gana'}
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
        mask_text(im, (W // 2, 800), 'Vende con confianza', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); WA = (37, 211, 102)
TERMO = [(239, 68, 68), (249, 115, 22), (250, 204, 21), (163, 230, 53), (22, 163, 74)]
def andres(d, x, y, s, bob=0): figure(d, x, y, s, (40, 90, 170), skin=(200, 150, 112), hair=(30, 22, 18), bob=bob)
def cel(d, cx, cy, s, col=(30, 30, 36), scr=(90, 140, 200)):
    d.rounded_rectangle((cx - 26 * s, cy - 48 * s, cx + 26 * s, cy + 48 * s), 9 * s, fill=col); d.rounded_rectangle((cx - 21 * s, cy - 40 * s, cx + 21 * s, cy + 38 * s), 5 * s, fill=scr)
def termo(d, x0, y0, w, lv, t=0, h=16):
    bw = (w - 4 * 8) / 5
    for i, c in enumerate(TERMO):
        on = i == lv; x = x0 + i * (bw + 8); hh = h * 1.5 if on else h
        col = (220, 220, 226) if lv < 0 else (c if on else mix(c, (250, 250, 250), .7))
        d.rounded_rectangle((x, y0 + h * 1.5 - hh, x + bw, y0 + h * 1.5), 6, fill=col)
NOM = ['Reputación baja', 'Reputación regular', 'Buena reputación', 'Muy buena reputación', 'Excelente reputación']
def seller_card(im, r, t, badges, lv=-1, ncal=0, vend=0):
    card(im, r, (255, 255, 255), 24); d = BD(im)
    x0, y0 = r[0] + 26, r[1] + 26
    d.ellipse((x0, y0, x0 + 80, y0 + 80), fill=(200, 220, 240)); L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); andres(ImageDraw.Draw(L), x0 + 40, y0 + 18, .62); im.alpha_composite(L.crop((int(x0), int(y0), int(x0 + 80), int(y0 + 80))), (int(x0), int(y0))); d = BD(im)
    d.text((x0 + 100, y0 + 24), 'Andrés M.', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm')
    d.text((x0 + 100, y0 + 60), 'Vendedor', font=F('Inter-SemiBold.otf', 20), fill=(120, 120, 130), anchor='lm')
    termo(d, x0, y0 + 108, r[2] - r[0] - 52, lv)
    txt = 'Vendedor nuevo · aún sin calificaciones' if lv < 0 else f'{NOM[lv]} · {ncal} calificaciones'
    d.text((x0, y0 + 152), txt, font=F('Inter-Bold.otf', 20), fill=(113, 113, 122) if lv < 0 else mix(TERMO[lv], (30, 30, 36), .35), anchor='lm')
    yb = y0 + 190; xb = x0
    for lab, col, tcol, q in badges:
        if q <= 0: continue
        f = F('Inter-Bold.otf', 19); tw = d.textlength(lab, font=f) + 30; b = back_out(q / .3)
        if xb + tw > r[2] - 20: xb = x0; yb += 50
        d.rounded_rectangle((xb, yb, xb + tw * b, yb + 38), 19, fill=col)
        if b > .7: d.text((xb + tw / 2, yb + 19), lab, font=f, fill=tcol, anchor='mm')
        xb += tw + 10
    return (x0, y0 + 108, r[2] - 26, y0 + 170)

def sc0(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    d.rounded_rectangle((300, 820, 700, 860), 10, fill=(150, 104, 70)); d.rectangle((320, 860, 340, 1040), fill=(120, 84, 56)); d.rectangle((660, 860, 680, 1040), fill=(120, 84, 56))
    for k in range(4):
        q = back_out((t - .4 - k * .25) / .35)
        if q > 0: cel(d, 360 + k * 90, 770 - (1 - q) * 30, 1.0 * q, scr=[(90, 140, 200), (200, 120, 160), (120, 190, 140), (230, 180, 90)][k])
    q = t - wt(0, 'cargador')
    if q > 0: d.line((600, 820, 640, 790, 690, 800), fill=(240, 240, 240), width=6); d.rounded_rectangle((680, 780, 710, 815), 6, fill=(250, 250, 250))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); andres(ImageDraw.Draw(L), 160, 760, 1.7); im.alpha_composite(L)
    q = t - wt(0, 'revisados')
    if q > 0: chip(im, 500, 600, '✓ REVISADOS', q, col=GREEN_OK, size=26)
    im = camera(im, lerp(1.12, 1.0, ease(lt / 2.5)), 400, 800)
    obj('in', (300, 700, 700, 860)); obj('out', (330, 720, 390, 820)); return im

def sc1(t, lt):
    im = gradient((26, 20, 34), (10, 8, 14)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 720, 1.05, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((216, 440, 504, 490), fill=(20, 20, 24)); d.text((236, 465), 'Mensajes', font=F('Inter-Black.otf', 20), fill='white', anchor='lm')
    t0 = ct(1) + .5
    for k in range(5):
        q = t - t0 - k * .55
        if q <= 0: continue
        a = back_out(q / .3); y = 510 + k * 92
        d.rounded_rectangle((226, y, 226 + 262 * a, y + 76), 16, fill=(255, 255, 255))
        if a > .8: d.text((242, y + 22), ['Cliente 1', 'Juli', 'Mateo', '+57 31…', 'Caro'][k], font=F('Inter-Bold.otf', 15), fill=(120, 120, 130), anchor='lm'); d.text((242, y + 50), '¿Y si me estafas?', font=F('Inter-Black.otf', 20), fill=RED, anchor='lm')
    q = t - wt(1, 'misma')
    if q > 0: chip(im, 360, 360, 'SIEMPRE LA MISMA PREGUNTA', q, col=WHITE, tcol=RED, size=24)
    obj('in', (330, 600, 390, 700)); obj('out', (226, 510, 488, 950)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); andres(dl, 360, 700, 1.7)
    for k, x in enumerate((90, 200, 520, 630)):
        figure(dl, x, 860, 1.2, (150, 150, 160), skin=(190, 190, 196), hair=(120, 120, 128))
    im.alpha_composite(L); d = BD(im)
    for k, x in enumerate((90, 200, 520, 630)):
        q = t - wt(2, 'nadie') - k * .15
        if q > 0: d.text((x, 820 - 6 * math.sin(t * 4 + k)), '?', font=F('Inter-Black.otf', int(44 * min(1, back_out(q / .3)))), fill=RED, anchor='mm')
    q = t - wt(2, 'creen')
    if q > 0: stamp(im, 360, 1130, ['NO LE CREEN'], RED, q, ang=-5, size=48)
    q = t - wt(2, 'internet')
    if q > 0: chip(im, 360, 440, 'EN INTERNET…', q, col=(36, 36, 40), size=26)
    obj('in', (226, 510, 488, 950)); obj('out', (320, 700, 400, 960)); return im

def listing_cel(im, cx, cy, s, t, hl=0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'MARKETPLACE', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.rectangle((x0, y0 + 50 * s, xe, y0 + 270 * s), fill=(226, 236, 246)); cel(d, cx, y0 + 160 * s, 1.6 * s)
    d.text((x0 + 16, y0 + 296 * s), 'Celular usado, revisado', font=F('Inter-Black.otf', int(21 * s)), fill='white', anchor='lm')
    d.text((x0 + 16, y0 + 334 * s), '$ 450.000', font=F('Inter-Black.otf', int(26 * s)), fill=GREEN_OK, anchor='lm')
    r = (x0 + 12, y0 + 370 * s, xe - 12, y0 + 540 * s)
    d.rounded_rectangle(r, 14, fill=(36, 38, 48), outline=GOLD if hl > 0 else None, width=4)
    d.ellipse((r[0] + 14, r[1] + 16, r[0] + 14 + 50 * s, r[1] + 16 + 50 * s), fill=(200, 220, 240))
    d.text((r[0] + 26 + 50 * s, r[1] + 32 * s), 'Andrés M.', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    d.text((r[0] + 26 + 50 * s, r[1] + 58 * s), 'Vendedor', font=F('Inter-SemiBold.otf', int(14 * s)), fill=(160, 160, 170), anchor='lm')
    for i in range(5): d.rounded_rectangle((r[0] + 14 + i * 50 * s, r[1] + 100 * s, r[0] + 14 + i * 50 * s + 44 * s, r[1] + 110 * s), 4, fill=(90, 92, 104))
    return r

def sc3(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    q = t - wt(3, 'vendedor')
    r = listing_cel(im, 360, 760, 1.0, t, hl=q + .3)
    f = ease((t - wt(3, 'anuncio')) / 1.0)
    im = camera(im, 1.0 + .45 * f, 360, lerp(760, (r[1] + r[3]) / 2, f))
    obj('in', (320, 700, 400, 960)); obj('out', r); return im

def sc4(t, lt):
    im = BGR_LIGHT.copy()
    B = [('Correo verificado', (220, 252, 231), (22, 101, 52), t - wt(4, 'verificado')), ('WhatsApp', (220, 252, 231), (22, 101, 52), t - wt(4, 'whatsapp')),
         ('Miembro Sumiago', (254, 243, 199), (146, 64, 14), t - wt(4, 'miembro')), ('3 vendidos', (241, 241, 244), (60, 60, 70), t - wt(4, 'vendido')), ('Desde 11/2026', (241, 241, 244), (60, 60, 70), t - wt(4, 'desde'))]
    seller_card(im, (50, 440, 670, 820), t, B)
    q = t - wt(4, 'correo')
    if q > 0: chip(im, 360, 360, 'QUIÉN ES EL VENDEDOR', q, col=(36, 36, 40), size=24)
    obj('in', (62, 500, 658, 760)); obj('out', (50, 440, 670, 820)); return im

def sc5(t, lt):
    im = BGR_LIGHT.copy()
    B = [('Correo verificado', (220, 252, 231), (22, 101, 52), 1), ('WhatsApp', (220, 252, 231), (22, 101, 52), 1), ('Miembro Sumiago', (254, 243, 199), (146, 64, 14), 1)]
    tr = seller_card(im, (50, 440, 670, 760), t, B)
    q = t - wt(5, 'nuevo')
    if q > 0: d = BD(im); d.rounded_rectangle((tr[0] - 10, tr[1] - 10, tr[2] + 10, tr[3] + 6), 14, outline=RED, width=4)
    im = camera(im, lerp(1.0, 1.1, ease((t - wt(5, 'decía')) / .8)), 360, lerp(600, tr[1] + 40, ease((t - wt(5, 'decía')) / .8)))
    obj('in', (50, 440, 670, 820)); obj('out', (tr[0], tr[1], tr[2], tr[3])); return im

def sc6(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); andres(dl, 200, 760, 1.6); figure(dl, 520, 760, 1.6, (190, 90, 60), skin=(214, 166, 128), hair=(70, 40, 26), long=True); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(6, 'entrega')) / .6); x = lerp(250, 470, q); cel(d, x, 860, .9)
    q = t - wt(6, 'califícame')
    if q > 0: bubble(im, 60, 560, 'Califícame en Sumiago', q, col=RED, size=28)
    obj('in', (300, 600, 420, 700)); obj('out', (460, 940, 560, 990)); return im

def sc7(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 440, 660, 900); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 495), '¿Ya trataste con este vendedor?', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='lm')
    t0 = wt(7, 'cinco')
    for k in range(5):
        q = t - t0 - k * .12; cx = 130 + k * 78
        s = back_out(q / .3) if q > 0 else 1
        col = (245, 158, 11) if q > 0 else (220, 220, 226)
        pts = [(cx + math.cos(-math.pi / 2 + j * math.pi / 5) * (34 if j % 2 == 0 else 15) * s, 590 + math.sin(-math.pi / 2 + j * math.pi / 5) * (34 if j % 2 == 0 else 15) * s) for j in range(10)]
        d.polygon(pts, fill=col)
    d.rounded_rectangle((90, 660, 630, 780), 14, fill=(244, 244, 247))
    v = 'Llegó igualito a las fotos'; n = int(len(v) * ease((t - wt(7, 'llegó') + .1) / .8))
    d.text((110, 720), v[:n] if n else 'Cuéntale a otros cómo te fue', font=F('Inter-Bold.otf', 24), fill=(30, 30, 36) if n else (160, 160, 170), anchor='lm')
    d.rounded_rectangle((90, 810, 630, 870), 30, fill=(30, 30, 36)); d.text((360, 840), 'Guardar calificación', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    obj('in', (460, 940, 560, 990)); obj('out', (60, 440, 660, 900)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy()
    p = ease((t - ct(8) - .3) / (wt(8, 'verde') - ct(8) - .2)); ncal = int(lerp(1, 23, p))
    p2 = ease((t - wt(8, 'gris') - .4) / max(.3, wt(8, 'verde') - wt(8, 'gris') - .2))
    lv = -1 if p2 <= 0 else 2 + min(2, int(p2 * 2.99))
    B = [('Correo verificado', (220, 252, 231), (22, 101, 52), 1), ('WhatsApp', (220, 252, 231), (22, 101, 52), 1), ('Miembro Sumiago', (254, 243, 199), (146, 64, 14), 1), (f'{ncal + 2} vendidos', (241, 241, 244), (60, 60, 70), 1)]
    seller_card(im, (50, 440, 670, 820), t, B, lv=lv, ncal=ncal)
    q = t - wt(8, 'verde')
    if q > 0: sparkles(im, 360, 620, t, n=18, rad=280, col=(60, 200, 110)); chip(im, 360, 960, 'EXCELENTE REPUTACIÓN', q, col=VG, size=26)
    obj('in', (60, 440, 660, 900)); obj('out', (50, 440, 670, 820)); return im

def sc9(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 760, 1.05, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((216, 480, 504, 530), fill=(20, 20, 24)); d.text((236, 505), 'Mensajes', font=F('Inter-Black.otf', 20), fill='white', anchor='lm')
    t0 = wt(9, 'todavía') - .1
    for k in range(3):
        q = t - t0 - k * .4
        if q <= 0: continue
        a = back_out(q / .3); y = 560 + k * 130
        d.rounded_rectangle((226, y, 226 + 262 * a, y + 100), 18, fill=(255, 255, 255))
        if a > .8: d.text((242, y + 26), ['Laura', 'Felipe', 'Don Óscar'][k], font=F('Inter-Bold.otf', 16), fill=(120, 120, 130), anchor='lm'); d.text((242, y + 64), '¿Todavía lo tienes?', font=F('Inter-Black.otf', 21), fill=VG, anchor='lm')
    q = t - wt(9, 'confiable')
    if q > 0:
        d = BD(im); d.text((360, 400), '¿Es confiable?', font=F('Inter-Black.otf', 36), fill=(150, 150, 160), anchor='mm')
        if q > .2: d.line((220, 400, 220 + 280 * ease((q - .2) / .3), 400), fill=RED, width=7)
    obj('in', (50, 440, 670, 820)); obj('out', (226, 560, 488, 920)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('califica', 'Solo califica quien tocó', '«¡Lo quiero!»'), ('reputación', 'Reputación a la vista', 'termómetro y estrellas')]
    for k, (w_, l1, l2) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        y = 500 + k * 220; card(im, (360 - 290 * a, y, 360 + 290 * a, y + 170), (250, 250, 250), 22); d = BD(im)
        if a > .7:
            if k == 0:
                for j in range(5):
                    cx = 140 + j * 0; 
                pts = [(130 + math.cos(-math.pi / 2 + j * math.pi / 5) * (40 if j % 2 == 0 else 17), y + 85 + math.sin(-math.pi / 2 + j * math.pi / 5) * (40 if j % 2 == 0 else 17)) for j in range(10)]; d.polygon(pts, fill=(245, 158, 11))
            else: termo(d, 92, y + 66, 90, 4, h=10)
            d.text((210, y + 64), l1, font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='lm'); d.text((210, y + 104), l2, font=F('Inter-Bold.otf', 24), fill=RED, anchor='lm')
    chip(im, 360, 1050, 'MARKETPLACE SUMIAGO', t - wt(10, 'marketplace'), size=24)
    obj('in', (226, 560, 488, 920)); obj('out', (70, 500, 650, 670)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Marketplace Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tu reputación, a la vista', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'CALIFICACIONES REALES', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'confianza')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'La confianza no se pide…', F('Inter-BlackItalic.otf', 40), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'se gana, una venta a la vez.', F('Inter-BlackItalic.otf', 38), WHITE, (t - wt(11, 'gana') + .3) / .4)
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
