"""Día 38 — "Las 500 tarjetas de don Jairo" (historia: un plomero cambia sus tarjetas de papel por una portada gratis de Sumiago con QR).
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
KEY = {'500', '2', 'nadie', 'billetera…', 'billetera', 'lavadora', 'plomero', 'buenos', 'tiempo', 'internet', 'encuentra', 'nada', 'portada', 'gratis', 'foto', 'servicios', 'trabajos', 'whatsapp',
       'enlace', 'sumiago.com/jairo-plomero', 'qr', 'herramientas', 'moto', 'escanea', 'próxima', 'pierden', 'no', 'oficio', 'negocio', 'sumiago', 'link', 'encuentren'}
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
        mask_text(im, (W // 2, 800), 'Que te encuentren', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
# ---------- objetos ----------
def jairo(d, x, y, s, bob=0):
    figure(d, x, y, s, (40, 90, 160), skin=(196, 140, 104), hair=(40, 30, 26), bob=bob)
    d.chord((x - 20 * s, y - 38 * s + bob, x + 20 * s, y - 8 * s + bob), 180, 360, fill=RED); d.rectangle((x, y - 24 * s + bob, x + 26 * s, y - 18 * s + bob), fill=RED)   # gorra
def sobrina(d, x, y, s, bob=0): figure(d, x, y, s, (230, 120, 60), skin=(204, 152, 116), hair=(50, 30, 24), long=True, bob=bob)

def biz_card(im, cx, cy, s=1.0, ang=0, a=255):
    w, h = int(240 * s), int(140 * s); L = Image.new('RGBA', (w + 20, h + 20), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((14, 16, w + 14, h + 16), 10, fill=(0, 0, 0, 60)); d.rounded_rectangle((0, 0, w, h), 10, fill=(255, 255, 255), outline=(210, 210, 216), width=2)
    d.rectangle((0, 0, 14 * s, h), fill=(40, 90, 160))
    d.text((30 * s, 30 * s), 'JAIRO', font=F('Inter-Black.otf', int(26 * s)), fill=(30, 30, 36), anchor='lm'); d.text((30 * s, 62 * s), 'Plomería', font=F('Inter-SemiBold.otf', int(18 * s)), fill=(110, 110, 120), anchor='lm')
    d.text((30 * s, 108 * s), 'Tel. 300 •••', font=F('Inter-Bold.otf', int(16 * s)), fill=(40, 90, 160), anchor='lm')
    if a < 255: L.putalpha(L.getchannel('A').point(lambda p: int(p * a / 255)))
    L = L.rotate(ang, expand=True, resample=Image.BICUBIC); im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

QRM = None
def qr(d, x, y, size, seed=7):
    n = 21; c = size / n; rr = random.Random(seed)
    d.rectangle((x - c, y - c, x + size + c, y + size + c), fill=(255, 255, 255))
    for i in range(n):
        for j in range(n):
            fin = (i < 7 and j < 7) or (i < 7 and j >= n - 7) or (i >= n - 7 and j < 7)
            if fin: continue
            if rr.random() < .5: d.rectangle((x + i * c, y + j * c, x + (i + 1) * c, y + (j + 1) * c), fill=(20, 20, 24))
    for fx, fy in ((0, 0), (n - 7, 0), (0, n - 7)):
        X, Y = x + fx * c, y + fy * c
        d.rectangle((X, Y, X + 7 * c, Y + 7 * c), fill=(20, 20, 24)); d.rectangle((X + c, Y + c, X + 6 * c, Y + 6 * c), fill='white'); d.rectangle((X + 2 * c, Y + 2 * c, X + 5 * c, Y + 5 * c), fill=(20, 20, 24))

def portada_j(im, cx, cy, s, t, built=1.0, wq=None):
    """Celular con la portada de Jairo."""
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L); d = BD(im)
    w = 375 * s; x0 = cx - w / 2 + 14; y0 = cy - 375 * s + 60; xe = x0 + w - 28
    def q(k): return 1.0 if wq is None else ease((t - wq[k] + .1) / .4)
    a = q(0)
    if a > 0:
        d.ellipse((cx - 56, y0 + 20, cx + 56, y0 + 132), fill=(236, 240, 246), outline=RED, width=5)
        Lf = Image.new('RGBA', (W, H), (0, 0, 0, 0)); jairo(ImageDraw.Draw(Lf), cx, y0 + 90, 1.4)
        m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).ellipse((cx - 52, y0 + 24, cx + 52, y0 + 128), fill=int(255 * a)); Lf.putalpha(ImageChops.multiply(Lf.getchannel('A'), m)); im.alpha_composite(Lf); d = BD(im)
        mask_text(im, (cx, y0 + 168), 'Jairo · Plomero', F('Inter-Black.otf', 30), WHITE, a)
    a = q(1)
    for k, sv in enumerate(['Fugas', 'Baños', 'Calentadores']):
        b = back_out((a * 1.4 - k * .2))
        if b > 0:
            xx = [cx - 110, cx, cx + 110][k]; f = F('Inter-Bold.otf', 18); tw = d.textlength(sv, font=f) + 24
            d.rounded_rectangle((xx - tw / 2 * b, y0 + 210, xx + tw / 2 * b, y0 + 246), 18, fill=(40, 42, 54))
            if b > .7: d.text((xx, y0 + 228), sv, font=f, fill='white', anchor='mm')
    a = q(2)
    for k in range(3):
        b = ease(a * 1.5 - k * .2)
        if b > 0:
            xx = x0 + 14 + k * ((w - 56) / 3 + 7); ww = (w - 56) / 3
            d.rounded_rectangle((xx, y0 + 270 + (1 - b) * 20, xx + ww, y0 + 370 + (1 - b) * 20), 10, fill=[(150, 190, 220), (200, 200, 210), (170, 210, 190)][k])
            d.line((xx + 14, y0 + 350, xx + ww - 14, y0 + 300), fill=(120, 120, 130), width=6); d.ellipse((xx + ww - 24, y0 + 290, xx + ww - 8, y0 + 306), fill=(60, 110, 200))
    a = q(3)
    b = back_out(a / .9) if a > 0 else 0
    if b > 0:
        yy = y0 + 420; gl = 1 + .04 * math.sin(t * 8)
        d.rounded_rectangle((cx - 140 * b * gl, yy - 30 * b, cx + 140 * b * gl, yy + 30 * b), 30, fill=GREEN_OK)
        if b > .6: chat_icon(d, cx - 100, yy, 13); d.text((cx + 14, yy), 'Escríbeme', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    return (cx - 190 * s, cy - 375 * s, cx + 190 * s, cy + 375 * s)

def toolbox(d, cx, cy, s=1.0):
    d.rounded_rectangle((cx - 160 * s, cy - 70 * s, cx + 160 * s, cy + 90 * s), 14 * s, fill=RED)
    d.rectangle((cx - 160 * s, cy - 20 * s, cx + 160 * s, cy - 8 * s), fill=(170, 24, 30))
    d.arc((cx - 60 * s, cy - 130 * s, cx + 60 * s, cy - 30 * s), 180, 360, fill=(60, 60, 66), width=max(2, int(14 * s)))
    return (cx - 160 * s, cy - 70 * s, cx + 160 * s, cy + 90 * s)

# ---------- escenas ----------
def sc0(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    n = int(lerp(500, 0, ease((t - ct(0) - .8) / 3.0)))
    for k in range(min(14, n // 36 + 1)): biz_card(im, 300 + (k % 3) * 4, 820 - k * 10, 1.1, ang=(k % 5 - 2) * 1.5)
    chip(im, 300, 560, f'{n} TARJETAS', 1, col=(36, 36, 40), size=28)
    chip(im, 560, 420, '2 MESES', t - wt(0, '2'), size=24)
    q = t - wt(0, 'nadie')
    r = (430, 900, 680, 1080)
    if q > 0:
        card(im, r, (255, 255, 255), 20); d = BD(im)
        d.text((555, 940), 'Llamadas', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='mm'); d.text((555, 1010), '2', font=F('Inter-Black.otf', 70), fill=RED, anchor='mm')
    im = camera(im, lerp(1.15, 1.0, ease(lt / 3)), 360, 760)
    obj('in', (160, 620, 460, 900)); obj('out', (160, 620, 460, 900)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # billetera
    d.rounded_rectangle((70, 420, 330, 600), 20, fill=(110, 70, 40)); d.rounded_rectangle((70, 420, 330, 470), 20, fill=(130, 86, 52))
    biz_card(im, 200, 450 - 20 * ease(lt / .6), .8, ang=-4)
    d = BD(im); d.rounded_rectangle((70, 470, 330, 600), 20, fill=(110, 70, 40))
    # lavadora
    q = t - wt(1, 'lavadora') + .6
    cx, cy = 450, 900
    d.rounded_rectangle((cx - 170, cy - 210, cx + 170, cy + 210), 24, fill=(245, 246, 248), outline=(200, 202, 210), width=4)
    d.rectangle((cx - 170, cy - 210, cx + 170, cy - 140), fill=(226, 228, 234)); d.ellipse((cx + 90, cy - 190, cx + 130, cy - 150), fill=RED)
    d.ellipse((cx - 130, cy - 100, cx + 130, cy + 160), fill=(190, 200, 214), outline=(150, 156, 170), width=10)
    d.ellipse((cx - 100, cy - 70, cx + 100, cy + 130), fill=(130, 170, 220))
    if q > 0:
        a = q * 9
        biz_card(im, cx + math.cos(a) * 40, cy + 30 + math.sin(a) * 40, .5, ang=math.degrees(a) % 360, a=int(255 * max(.25, 1 - q / 3)))
        rr = random.Random(1); Lb = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(Lb)
        for k in range(12):
            qq = (q * .6 + rr.random()) % 1; x = cx - 80 + rr.random() * 160; y = cy + 120 - qq * 180; r = 6 + rr.random() * 8
            bd.ellipse((x - r, y - r, x + r, y + r), outline=(255, 255, 255, int(220 * math.sin(math.pi * qq))), width=3)
        im.alpha_composite(Lb)
    fq = ease((t - wt(1, 'pantalón')) / .6)
    im = camera(im, 1.1, lerp(220, 450, fq), lerp(520, 880, fq))
    obj('in', (70, 420, 330, 600)); obj('out', (320, 800, 580, 1060)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); jairo(ImageDraw.Draw(L), 360, 700, 2.1, bob=-abs(math.sin(t * 3)) * 3); im.alpha_composite(L); d = BD(im)
    # llave inglesa
    d.line((440, 820, 520, 740), fill=(150, 154, 166), width=16); d.ellipse((500, 710, 550, 760), fill=(150, 154, 166)); d.ellipse((514, 724, 536, 746), fill=BGR_LIGHT.getpixel((10, 10))[:3])
    chip(im, 360, 430, 'PLOMERO', t - wt(2, 'plomero'), col=(40, 90, 160), size=28)
    chip(im, 190, 560, 'DE LOS BUENOS', t - wt(2, 'buenos'), col=(36, 36, 40), size=22)
    q = t - wt(2, 'tiempo')
    if q > 0: stamp(im, 360, 1080, ['LLEGA A TIEMPO'], RED, q, ang=-5, size=44)
    obj('in', (320, 800, 580, 1060)); obj('out', (250, 560, 470, 990)); return im

def sc3(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); jairo(dl, 170, 760, 1.8); sobrina(dl, 540, 770, 1.7); im.alpha_composite(L)
    bubble(im, 250, 440, 'Tío, si te buscan en internet…', t - wt(3, 'tío'), col=(230, 120, 60), size=26)
    bubble(im, 250, 520, '…¿qué encuentran?', t - wt(3, 'encuentra'), col=(230, 120, 60), size=26)
    im = camera(im, 1.06, 360, 700)
    obj('in', (250, 560, 470, 990)); obj('out', (400, 640, 680, 1000)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 70))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 780, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.rounded_rectangle((200, 480, 520, 530), 25, fill=(40, 42, 54)); d.text((228, 505), 'Jairo plomero', font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
    q = t - ct(4) - .2
    if q > 0:
        d.text((360, 720), '0', font=F('Inter-Black.otf', 120), fill=RED, anchor='mm'); d.text((360, 820), 'resultados', font=F('Inter-Bold.otf', 26), fill=(170, 170, 180), anchor='mm')
    q = t - wt(4, 'encontraba')
    if q > 0: stamp(im, 360, 980, ['NADA'], RED, q, ang=-8, size=60)
    obj('in', (172, 405, 548, 1155)); obj('out', (172, 405, 548, 1155)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = portada_j(im, 360, 780, 1.0, t, wq=[wt(5, 'foto'), wt(5, 'servicios'), wt(5, 'trabajos'), wt(5, 'botón')])
    q = t - wt(5, 'gratis')
    if q > 0: stamp(im, 560, 430, ['GRATIS'], RED, q, ang=10, size=44)
    fq = ease((t - wt(5, 'servicios') + .2) / 1.0)
    im = camera(im, 1.0 + .12 * fq, 360, lerp(700, 880, fq))
    obj('in', (172, 405, 548, 1155)); obj('out', r); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    portada_j(im, 360, 900, .8, t)
    d = BD(im); r = (40, 420, 680, 520); card(im, r, (255, 255, 255), 50); d = BD(im)
    url = 'sumiago.com/jairo-plomero'; n = int(len(url) * ease((t - wt(6, 'sumiago')) / 1.4))
    d.ellipse((66, 446, 114, 494), fill=RED); d.text((90, 470), '🔗'[:0] + '↗', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    d.text((132, 470), url[:n] + ('|' if int(t * 3) % 2 else ''), font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 580, 'UN SOLO ENLACE', t - wt(6, 'enlace'), size=26)
    obj('in', (172, 405, 548, 1155)); obj('out', r); return im

def sc7(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = t - wt(7, 'qr')
    qrr = (230, 340, 490, 600)
    a = back_out(q / .4) if q > 0 else 0
    if a > 0:
        sz = 230 * a; qr(d, 360 - sz / 2, 470 - sz / 2, sz)
    tb = toolbox(d, 240, 900, .9)
    if t > wt(7, 'herramientas'):
        b = back_out((t - wt(7, 'herramientas')) / .35); qr(d, 240 - 40 * b, 900 - 10 - 40 * b, 80 * b, seed=7)
    # moto
    mx, my = 540, 1010; d.ellipse((mx - 120, my - 40, mx - 40, my + 40), fill=(30, 30, 34)); d.ellipse((mx + 40, my - 40, mx + 120, my + 40), fill=(30, 30, 34))
    d.rounded_rectangle((mx - 70, my - 110, mx + 60, my - 40), 26, fill=(40, 90, 160)); d.line((mx - 80, my, mx + 80, my), fill=(60, 60, 66), width=10)
    if t > wt(7, 'moto'):
        b = back_out((t - wt(7, 'moto')) / .35); qr(d, mx - 30 * b, my - 105 - 0 * b, 60 * b, seed=7)
    fq = ease((t - wt(7, 'pegó') + .1) / .8)
    im = camera(im, 1.0 + .1 * fq, 360, lerp(560, 880, fq))
    obj('in', qrr); obj('out', (420, 880, 660, 1060)); return im

def sc8(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    tb = toolbox(d, 200, 980, .8); qr(d, 168, 940, 64)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); jairo(dl, 120, 700, 1.6); figure(dl, 560, 690, 1.7, (160, 100, 160), skin=(214, 168, 130), long=True); im.alpha_composite(L)
    def content(dd, cx, cy, w, h):
        q = t - wt(8, 'escanea')
        if q < .8:
            dd.rectangle((cx - w / 2 + 14, cy - h / 2 + 60, cx + w / 2 - 14, cy + h / 2 - 60), fill=(40, 40, 46))
            yy = cy - 60 + 120 * ((t * 1.2) % 1); dd.line((cx - 70, yy, cx + 70, yy), fill=GREEN_OK, width=4)
            dd.rectangle((cx - 80, cy - 80, cx + 80, cy + 80), outline='white', width=3)
        else:
            dd.ellipse((cx - 50, cy - 140, cx + 50, cy - 40), fill=GREEN_OK); dd.line((cx - 22, cy - 90, cx - 6, cy - 72, cx + 24, cy - 108), fill='white', width=8)
            dd.text((cx, cy + 10), 'Guardado', font=F('Inter-Black.otf', 26), fill='white', anchor='mm'); dd.text((cx, cy + 50), 'Jairo · Plomero', font=F('Inter-Bold.otf', 20), fill=(190, 190, 200), anchor='mm')
    Lp = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(Lp, 470, 700, .62, content); im.alpha_composite(Lp)
    chip(im, 470, 1120, 'PARA LA PRÓXIMA', t - wt(8, 'próxima'), size=24)
    obj('in', (130, 900, 270, 1060)); obj('out', (377, 514, 563, 886)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.rectangle((W / 2 - 2, 330, W / 2 + 2, 1200), fill=(200, 202, 210))
    # izquierda: tarjetas que caen a la basura
    for k in range(4):
        q = (lt * .5 + k * .25) % 1; biz_card(im, 180 + math.sin(k) * 30, 420 + q * 520, .55, ang=q * 200 + k * 40, a=int(255 * (1 - q * .6)))
    d = BD(im); d.polygon([(110, 960), (250, 960), (235, 1140), (125, 1140)], fill=(90, 90, 100)); d.rectangle((96, 940, 264, 964), fill=(110, 110, 120))
    chip(im, 180, 1190, 'SE PIERDEN', t - wt(9, 'pierden'), col=(90, 90, 100), size=24)
    q = t - wt(9, 'enlace')
    if q > 0:
        a = back_out(q / .4); r = (380, 640 - 60 * a, 680, 640 + 60 * a)
        im.alpha_composite(glow_layer(lambda dd: dd.rounded_rectangle((380, 580, 680, 700), 30, fill=255), RED, 30, int(160 * min(1, q))))
        card(im, r, (255, 255, 255), 30); d = BD(im)
        if a > .7: d.text((530, 640), 'sumiago.com/jairo…', font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='mm')
        chip(im, 530, 1190, 'NO SE PIERDE', q - .3, size=24)
    obj('in', (380, 580, 680, 700)); obj('out', (380, 580, 680, 700)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    ks = [('oficio', 'Tu oficio'), ('negocio', 'Tu negocio')]
    for k, (w_, lab) in enumerate(ks):
        a = back_out((t - wt(10, w_) + .1) / .4)
        if a <= 0: continue
        x = 200 + k * 320; y = 720; w, h = 260 * a, 300 * a; r = (x - w / 2, y - h / 2, x + w / 2, y + h / 2)
        card(im, r, (250, 250, 250), 24); d = BD(im)
        if a > .7:
            if k == 0:
                d.line((x - 50, y + 20, x + 30, y - 60), fill=(150, 154, 166), width=18); d.ellipse((x + 10, y - 90, x + 66, y - 34), fill=(150, 154, 166))
            else:
                d.rectangle((x - 60, y - 40, x + 60, y + 30), fill=(70, 74, 90)); d.rectangle((x - 70, y - 70, x + 70, y - 42), fill=RED); d.rectangle((x - 18, y - 10, x + 18, y + 30), fill=GOLD)
            d.text((x, y + 100), lab, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='mm')
    q = t - wt(10, 'gratis')
    if q > 0: stamp(im, 360, 1030, ['TU PORTADA GRATIS'], WHITE, q, ang=-5, size=42)
    obj('in', (380, 580, 680, 700)); obj('out', (70, 570, 330, 870)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Portada', F('Inter-Black.otf', 34), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tu negocio en un solo enlace', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'GRATIS · CON QR', t - wt(11, 'crea'), size=22)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'encuentren')
    if q > -.3: mask_text(im, (W / 2, 760), '…te encuentren.', F('Inter-BlackItalic.otf', 50), WHITE, (q + .3) / .4)
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
