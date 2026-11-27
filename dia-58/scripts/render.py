"""Día 58 — "Pedir ayuda bien" (historia: don Ramiro no logra agregar su método de pago y abre un ticket en Soporte de Sumiago con categoría, prioridad y una captura).
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
KEY = {'ramiro', 'método', 'pago', 'salía', 'tres', 'después»', 'nieta', 'soporte', '«nuevo', 'ticket»', 'métodos', 'pago»', 'problema', 'prioridad', 'media', 'adjuntar', 'imágenes', '5', 'captura', '¡ticket', 'creado!', 'notificación', 'respondió', 'primera', 'listo', 'categorías', 'respuesta', 'guardada', 'link', 'ayuda', 'mitad', 'solución'}
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
        mask_text(im, (W // 2, 800), 'Abre tu ticket', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); BLUE = (37, 99, 235)
def ramiro(d, x, y, s, bob=0): figure(d, x, y, s, (90, 110, 140), skin=(200, 150, 112), hair=(200, 200, 204), bob=bob)
def nieta(d, x, y, s, bob=0): figure(d, x, y, s, (236, 120, 160), skin=(214, 166, 128), hair=(60, 36, 24), long=True, bob=bob)
def headset(d, cx, cy, s, col=RED):
    d.arc((cx - 34 * s, cy - 40 * s, cx + 34 * s, cy + 28 * s), 180, 360, fill=col, width=max(2, int(8 * s)))
    d.rounded_rectangle((cx - 42 * s, cy - 8 * s, cx - 24 * s, cy + 26 * s), 6, fill=col); d.rounded_rectangle((cx + 24 * s, cy - 8 * s, cx + 42 * s, cy + 26 * s), 6, fill=col)
    d.line((cx + 32 * s, cy + 26 * s, cx + 10 * s, cy + 40 * s), fill=col, width=max(2, int(4 * s))); d.ellipse((cx + 2 * s, cy + 34 * s, cx + 14 * s, cy + 46 * s), fill=col)
def screen_phone(im, cx, cy, s):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60
    return x0, xe, y0
def pay_screen(im, cx, cy, s, t, err=0.0):
    x0, xe, y0 = screen_phone(im, cx, cy, s); d = BD(im)
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'Métodos de pago', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    for k in range(3): d.rounded_rectangle((x0 + 14, y0 + 80 * s + k * 70 * s, xe - 14, y0 + 130 * s + k * 70 * s), 10, fill=(48, 50, 60))
    d.rounded_rectangle((x0 + 14, y0 + 300 * s, xe - 14, y0 + 356 * s), 26 * s, fill=RED); d.text(((x0 + xe) / 2, y0 + 328 * s), 'Guardar', font=F('Inter-Black.otf', int(22 * s)), fill='white', anchor='mm')
    if err > 0:
        a = back_out(err / .3); cy2 = y0 + 430 * s
        d.ellipse(((x0 + xe) / 2 - 40 * s * a, cy2 - 40 * s * a, (x0 + xe) / 2 + 40 * s * a, cy2 + 40 * s * a), fill=(240, 160, 60))
        if a > .7: d.text(((x0 + xe) / 2, cy2), '!', font=F('Inter-Black.otf', int(50 * s)), fill='white', anchor='mm')
    return (x0, y0, xe, y0 + 500 * s)

def sc0(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ramiro(ImageDraw.Draw(L), 150, 820, 1.6); im.alpha_composite(L)
    r = pay_screen(im, 470, 760, .75, t, err=t - wt(0, 'salía'))
    q = t - wt(0, 'salía')
    if q > 0: chip(im, 470, 1110, 'ALGO NO LE SALÍA', q, col=(36, 36, 40), size=24)
    im = camera(im, lerp(1.12, 1.0, ease(lt / 2.5)), 400, 780)
    obj('in', (330, 520, 610, 760)); obj('out', (330, 520, 610, 1000)); return im

def sc1(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ramiro(ImageDraw.Draw(L), 200, 760, 1.8, bob=2); im.alpha_composite(L); d = BD(im)
    for k in range(3):
        q = t - wt(1, 'tres') - k * .25 + .2
        if q > 0:
            s = back_out(q / .3); cx = 400 + k * 100
            d.ellipse((cx - 38 * s, 520 - 38 * s, cx + 38 * s, 520 + 38 * s), fill=RED); d.line((cx - 16 * s, 504, cx + 16 * s, 536), fill='white', width=7); d.line((cx + 16 * s, 504, cx - 16 * s, 536), fill='white', width=7)
    q = t - wt(1, 'pensó')
    if q > 0: bubble(im, 330, 640, 'Mejor lo dejo para después…', q, col=(150, 150, 160), size=24)
    q = t - wt(1, 'después')
    if q > 0: d = BD(im); d.rounded_rectangle((420, 900, 500, 1020), 12, fill=(30, 30, 36)); d.rectangle((300, 1020, 620, 1040), fill=(150, 104, 70))
    obj('in', (330, 520, 610, 1000)); obj('out', (420, 900, 500, 1020)); return im

def sc2(t, lt):
    im = gradient((250, 236, 214), (236, 214, 190)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); ramiro(dl, 200, 800, 1.6); nieta(dl, 470, 820, 1.4, bob=-abs(math.sin(t * 5)) * 3); im.alpha_composite(L); d = BD(im)
    bubble(im, 290, 470, 'Abuelo, pregunta en Soporte', t - wt(2, 'abuelo'), col=RED, size=26)
    q = t - wt(2, 'soporte')
    if q > 0: d = BD(im); headset(d, 600, 640, 1.4 * back_out(q / .35))
    obj('in', (420, 900, 500, 1020)); obj('out', (540, 580, 660, 700)); return im

def sop_header(d, x0, xe, y0, s, title='Soporte'):
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); headset(d, x0 + 30 * s, y0 + 24 * s, .35 * s, 'white'); d.text((x0 + 56 * s, y0 + 25 * s), title, font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')

def sc3(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    x0, xe, y0 = screen_phone(im, 360, 760, 1.0); d = BD(im); s = 1.0
    sop_header(d, x0, xe, y0, s)
    d.text((x0 + 16, y0 + 80), 'Mis Tickets (0)', font=F('Inter-Bold.otf', 18), fill=(170, 170, 180), anchor='lm')
    d.text((x0 + 16, y0 + 130), '¿Tienes un problema?', font=F('Inter-Black.otf', 20), fill='white', anchor='lm'); d.text((x0 + 16, y0 + 160), 'Abre un ticket y adjunta', font=F('Inter-SemiBold.otf', 16), fill=(170, 170, 180), anchor='lm'); d.text((x0 + 16, y0 + 184), 'hasta 5 imágenes.', font=F('Inter-SemiBold.otf', 16), fill=(170, 170, 180), anchor='lm')
    br = (x0 + 14, y0 + 220, xe - 14, y0 + 276); q = t - wt(3, 'nuevo')
    d.rounded_rectangle(br, 28, fill=RED, outline=GOLD if q > 0 else None, width=4); d.text(((br[0] + br[2]) / 2, br[1] + 28), '+ Nuevo Ticket', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    if 0 < q < .5: rr = 20 + q * 140; d.ellipse((360 - rr, br[1] + 28 - rr, 360 + rr, br[1] + 28 + rr), outline=(255, 255, 255, int(255 * (1 - q / .5))), width=5)
    obj('in', (540, 580, 660, 700)); obj('out', br); return im

CATS = [('Mi cuenta', (90, 120, 200)), ('Métodos de pago', RED), ('Gana con Marketing', (240, 160, 40)), ('Otro', (120, 120, 130))]
def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 340, 660, 1060); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 390), 'Abrir Nuevo Ticket', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm'); d.text((90, 440), 'Categoría', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
    sel = t > wt(4, 'métodos')
    for k, (lab, c) in enumerate(CATS):
        x = 90 + (k % 2) * 275; y = 465 + (k // 2) * 100; on = sel and k == 1
        d.rounded_rectangle((x, y, x + 260, y + 84), 16, fill=(255, 241, 241) if on else (244, 244, 247), outline=RED if on else (226, 226, 232), width=4 if on else 2)
        d.ellipse((x + 14, y + 22, x + 54, y + 62), fill=c); d.text((x + 66, y + 42), lab, font=F('Inter-Black.otf', 19 if len(lab) > 14 else 21), fill=(30, 30, 36), anchor='lm')
    q = t - wt(4, 'debajo')
    if q > 0:
        a = ease(q / .4); d.text((90, 700), 'Subcategoría', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
        opts = ['No puedo agregar mi método de pago', 'Quiero cambiar mi wallet']
        for k, o in enumerate(opts):
            y = 724 + k * 70; hl = k == 0 and t > wt(4, 'puedo')
            d.rounded_rectangle((90, y, 90 + 540 * a, y + 58), 12, fill=(255, 241, 241) if hl else (244, 244, 247), outline=RED if hl else None, width=3)
            if a > .9: d.text((110, y + 29), o, font=F('Inter-Bold.otf', 21), fill=(30, 30, 36), anchor='lm')
        if t > wt(4, 'puedo'): d.text((604, 753), '✓', font=F('Inter-Black.otf', 26), fill=RED, anchor='mm')
    pass
    obj('in', (172, 655, 548, 711)); obj('out', (90, 724, 630, 782)); return im

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 380, 660, 960); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((90, 430), 'Describe tu situación', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm'); d.rounded_rectangle((90, 450, 630, 680), 14, fill=(244, 244, 247))
    txt = ['Intenté agregar mi método de', 'pago 3 veces y me sale un', 'mensaje. Adjunto la captura.']
    tot = sum(len(x) for x in txt); n = int(tot * ease((t - wt(5, 'escribió')) / 2.0))
    for k, ln in enumerate(txt):
        m = max(0, min(len(ln), n)); n -= len(ln)
        if m: d.text((110, 490 + k * 44), ln[:m], font=F('Inter-SemiBold.otf', 24), fill=(30, 30, 36), anchor='lm')
    d.text((90, 730), 'Prioridad', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='lm')
    pr = [('Baja', BLUE), ('Media', (217, 119, 6)), ('Alta', RED), ('Urgente', (120, 20, 30))]
    for k, (lab, c) in enumerate(pr):
        x = 90 + k * 136; on = k == 1 and t > wt(5, 'media')
        d.rounded_rectangle((x, 755, x + 126, 811), 28, fill=c if on else (244, 244, 247), outline=c, width=3); d.text((x + 63, 783), lab, font=F('Inter-Black.otf', 20), fill='white' if on else c, anchor='mm')
    obj('in', (90, 724, 630, 782)); obj('out', (226, 755, 352, 811)); return im

def thumb_err(d, x, y, w, h):
    d.rounded_rectangle((x, y, x + w, y + h), 8, fill=(36, 38, 48)); d.ellipse((x + w / 2 - 16, y + h / 2 - 16, x + w / 2 + 16, y + h / 2 + 16), fill=(240, 160, 60)); d.text((x + w / 2, y + h / 2), '!', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 420, 660, 900); card(im, r, (255, 255, 255), 24); d = BD(im)
    q = t - wt(6, 'adjuntar')
    d.rounded_rectangle((90, 470, 630, 560), 16, fill=(244, 244, 247), outline=RED if q > 0 else (200, 200, 206), width=3)
    d.rounded_rectangle((120, 495, 170, 535), 6, outline=RED, width=4); d.polygon([(126, 530), (142, 510), (156, 530)], fill=RED)
    d.text((190, 515), 'Adjuntar imágenes', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='lm')
    q2 = t - wt(6, '5')
    for k in range(5):
        x = 90 + k * 110; d.rounded_rectangle((x, 600, x + 96, 700), 12, outline=(200, 200, 206), width=3)
        if q2 > k * .1: d.rounded_rectangle((x, 600, x + 96, 700), 12, fill=(255, 241, 241), outline=RED, width=3); d.text((x + 48, 650), str(k + 1), font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    if q2 > 0: chip(im, 360, 800, 'HASTA 5 IMÁGENES', q2, col=RED, size=26)
    obj('in', (226, 755, 352, 811)); obj('out', (90, 600, 186, 700)); return im

def sc7(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    q = t - wt(7, 'captura')
    if t < wt(7, 'envió'):
        pay_screen(im, 360, 760, 1.0, t, err=1)
        if 0 < q < .35: d = BD(im); d.rectangle((0, 0, W, H), fill=(255, 255, 255, int(255 * (1 - q / .35))))
        if q > .35:
            a = ease((q - .35) / .5); d = BD(im); x, y = lerp(200, 90, a), lerp(400, 1000, a); w = lerp(320, 120, a)
            thumb_err(d, x, y, w, w * 1.4)
    else:
        q = t - wt(7, '¡ti')
        r = (90, 520, 630, 900); card(im, r, (255, 255, 255), 26); d = BD(im)
        a = back_out((q + .2) / .4)
        d.ellipse((360 - 60 * a, 600 - 60 * a, 360 + 60 * a, 600 + 60 * a), fill=GREEN_OK)
        if a > .7: d.line((330, 602, 352, 624, 392, 580), fill='white', width=10)
        if q > -.1: d.text((360, 720), '¡Ticket creado!', font=F('Inter-Black.otf', 40), fill=(30, 30, 36), anchor='mm'); d.text((360, 775), 'Métodos de pago · Media', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='mm')
        if q > .2: d.rounded_rectangle((285, 815, 435, 857), 21, fill=(22, 163, 74)); d.text((360, 836), 'Abierto', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
        sparkles(im, 360, 650, t, n=12, rad=200) if 0 < q < 1.2 else None
    obj('in', (90, 600, 186, 700)); obj('out', (90, 520, 630, 900)); return im

def sc8(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ramiro(ImageDraw.Draw(L), 360, 760, 1.8); im.alpha_composite(L); d = BD(im)
    q = t - wt(8, 'notificación')
    if q > -.2:
        a = ease((q + .2) / .4); r = (50, 380 - (1 - a) * 200, 670, 520 - (1 - a) * 200); card(im, r, (255, 255, 255), 22); d = BD(im)
        d.ellipse((r[0] + 20, r[1] + 30, r[0] + 100, r[1] + 110), fill=(255, 236, 236)); headset(d, r[0] + 60, r[1] + 70, .7)
        d.text((r[0] + 120, r[1] + 46), 'Sumiago', font=F('Inter-Black.otf', 20), fill=RED, anchor='lm')
        d.text((r[0] + 120, r[1] + 90), 'Soporte respondió tu ticket', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='lm')
    obj('in', (90, 520, 630, 900)); obj('out', (50, 380, 670, 520)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    d.rounded_rectangle((300, 330, 670, 560), 20, fill=(255, 241, 241)); d.text((320, 360), 'Tú', font=F('Inter-Bold.otf', 18), fill=(120, 120, 130), anchor='lm'); d.text((320, 400), 'Me sale este mensaje…', font=F('Inter-SemiBold.otf', 20), fill=(30, 30, 36), anchor='lm'); thumb_err(d, 320, 425, 110, 120)
    q = t - wt(9, 'entendieron')
    if q > -.3:
        a = back_out((q + .3) / .35); d.rounded_rectangle((50, 600, 50 + 470 * a, 900), 20, fill=(255, 255, 255))
        if a > .8:
            headset(d, 90, 640, .45); d.text((120, 640), 'Soporte', font=F('Inter-Black.otf', 20), fill=RED, anchor='lm')
            for k, ln in enumerate(['Gracias por la captura.', '1. Revisa este dato', '2. Toca «Guardar» otra vez', '3. ¡Listo!']):
                if t > wt(9, 'primera') - .3 + k * .35: d.text((80, 700 + k * 48), ln, font=F('Inter-SemiBold.otf', 22), fill=(30, 30, 36), anchor='lm')
    q = t - wt(9, 'listo')
    if q > 0: stamp(im, 360, 1050, ['¡QUEDÓ LISTO!'], GREEN_OK, q, ang=-5, size=52)
    q = t - wt(9, 'pasos')
    if q > 0: d = BD(im); d.rounded_rectangle((500, 930, 680, 972), 21, fill=(10, 10, 10)); d.text((590, 951), 'Solucionado', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    obj('in', (50, 380, 670, 520)); obj('out', (50, 600, 520, 900)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('categorías', 'Categorías'), ('prioridad', 'Prioridad'), ('imágenes', 'Hasta 5 imágenes'), ('guardada', 'Respuestas guardadas')]
    for k, (w_, lab) in enumerate(items):
        a = back_out((t - wt(10, w_) + .1) / .35)
        if a <= 0: continue
        y = 420 + k * 150; card(im, (360 - 280 * a, y, 360 + 280 * a, y + 120), (250, 250, 250), 22); d = BD(im)
        if a > .7:
            cx, cy = 150, y + 60
            if k == 0: [d.rounded_rectangle((cx - 34 + (j % 2) * 36, cy - 34 + (j // 2) * 36, cx - 2 + (j % 2) * 36, cy - 2 + (j // 2) * 36), 6, fill=[RED, (90, 120, 200), (240, 160, 40), (120, 120, 130)][j]) for j in range(4)]
            elif k == 1: [d.rounded_rectangle((cx - 40 + j * 22, cy + 20 - j * 14, cx - 24 + j * 22, cy + 30), 4, fill=[BLUE, (217, 119, 6), RED, (120, 20, 30)][j]) for j in range(4)]
            elif k == 2: d.rounded_rectangle((cx - 30, cy - 26, cx + 30, cy + 26), 6, outline=RED, width=5); d.polygon([(cx - 22, cy + 20), (cx - 2, cy - 6), (cx + 18, cy + 20)], fill=RED)
            else: headset(d, cx, cy - 4, .8)
            d.text((220, cy), lab, font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm')
    chip(im, 360, 1080, 'SOPORTE SUMIAGO', t - wt(10, 'soporte'), size=24)
    obj('in', (50, 600, 520, 900)); obj('out', (80, 420, 640, 540)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Soporte Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Abre tu ticket con capturas', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'NUEVO TICKET', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'pedir')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Pedir ayuda bien…', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'es la mitad de la solución.', F('Inter-BlackItalic.otf', 40), WHITE, (t - wt(11, 'mitad') + .5) / .4)
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
