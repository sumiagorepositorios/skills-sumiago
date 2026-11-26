"""Día 44 — "Lo voy a pensar" (historia: una mueblería activa la captura de clientes de Mi Negocio en su portada de Sumiago y vuelve a escribirles a los interesados).
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
KEY = {'nubia', 'mueblería', 'pensar', 'nombre', 'número', 'nunca', 'nadie', 'escribir', 'membresía', 'captura', 'clientes', 'negocio', 'sumiago', 'datos', 'contacto', 'whatsapp', 'correo', '10',
       'lista', 'panel', 'excel', 'colección', 'esperar', 'todos', 'pensado', 'oportunidad', 'pierde', 'link'}
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
        mask_text(im, (W // 2, 800), 'Guarda a tus interesados', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100)
XL = (33, 115, 70)
# ---------- objetos ----------
def nubia(d, x, y, s, bob=0): figure(d, x, y, s, (120, 70, 140), skin=(220, 176, 140), hair=(110, 70, 40), long=True, bob=bob)
def sofa(d, cx, cy, s=1.0, col=(70, 110, 160)):
    d.rounded_rectangle((cx - 150 * s, cy - 80 * s, cx + 150 * s, cy + 10 * s), 26 * s, fill=mix(col, (0, 0, 0), .15))
    d.rounded_rectangle((cx - 170 * s, cy - 20 * s, cx + 170 * s, cy + 50 * s), 22 * s, fill=col)
    d.rounded_rectangle((cx - 190 * s, cy - 50 * s, cx - 140 * s, cy + 50 * s), 18 * s, fill=mix(col, (0, 0, 0), .1)); d.rounded_rectangle((cx + 140 * s, cy - 50 * s, cx + 190 * s, cy + 50 * s), 18 * s, fill=mix(col, (0, 0, 0), .1))
    d.rectangle((cx - 160 * s, cy + 50 * s, cx - 146 * s, cy + 74 * s), fill=(90, 60, 40)); d.rectangle((cx + 146 * s, cy + 50 * s, cx + 160 * s, cy + 74 * s), fill=(90, 60, 40))
def lamp(d, x, y):
    d.line((x, y, x, y + 200), fill=(60, 60, 66), width=6); d.polygon([(x - 50, y), (x + 50, y), (x + 30, y - 60), (x - 30, y - 60)], fill=GOLD); d.ellipse((x - 40, y + 190, x + 40, y + 214), fill=(60, 60, 66))
def mueble_bg():
    im = gradient((246, 238, 226), (230, 216, 196)); d = BD(im)
    d.rectangle((0, 300, W, 340), fill=(36, 36, 40)); d.text((W / 2, 320), 'MUEBLERÍA NUBIA', font=F('Inter-Black.otf', 26), fill=GOLD, anchor='mm')
    d.rectangle((0, 920, W, H), fill=(170, 130, 96)); lamp(d, 620, 640)
    sofa(d, 300, 850, .9)
    return im
BGM = mueble_bg()
def form_card(im, r, t, fill_q=(0, 0, 0)):
    card(im, r, (255, 255, 255), 22); d = BD(im)
    d.text(((r[0] + r[2]) / 2, r[1] + 40), 'Déjame tus datos', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm')
    d.text(((r[0] + r[2]) / 2, r[1] + 74), 'y te contacto', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm')
    labs = [('Nombre', 'Laura Ríos'), ('WhatsApp', '+57 310 555 0199'), ('Correo', 'laura@correo.com')]
    for k, (lab, val) in enumerate(labs):
        y = r[1] + 110 + k * 82
        d.text((r[0] + 26, y + 10), lab, font=F('Inter-Bold.otf', 16), fill=(120, 120, 130), anchor='lm')
        d.rounded_rectangle((r[0] + 22, y + 22, r[2] - 22, y + 66), 12, fill=(244, 244, 247))
        n = int(len(val) * fill_q[k]); d.text((r[0] + 38, y + 44), val[:n], font=F('Inter-Bold.otf', 20), fill=(30, 30, 36), anchor='lm')
    d.rounded_rectangle((r[0] + 40, r[3] - 70, r[2] - 40, r[3] - 22), 24, fill=RED); d.text(((r[0] + r[2]) / 2, r[3] - 46), 'Enviar', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
LEADS = [('Laura Ríos', '310 555 0199'), ('Jorge P.', '300 555 0123'), ('Diana M.', '315 555 0177'), ('Hugo T.', '321 555 0145'), ('Sara L.', '318 555 0101')]

# ---------- escenas ----------
def sc0(t, lt):
    im = BGM.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); nubia(dl, 560, 760, 1.6); figure(dl, 160, 760, 1.6, (60, 110, 200), skin=(200, 150, 112)); im.alpha_composite(L)
    bubble(im, 120, 470, 'Lo voy a pensar…', t - wt(0, 'pensar') + .15, col=(255, 255, 255), tcol=(36, 36, 40), size=32)
    chip(im, 560, 420, 'LA FRASE MÁS ESCUCHADA', t - wt(0, 'frase'), col=(36, 36, 40), size=18)
    im = camera(im, lerp(1.2, 1.0, ease(lt / 3)), 360, 720)
    obj('in', (100, 620, 620, 960)); obj('out', (120, 470, 520, 550)); return im

def sc1(t, lt):
    im = BGM.copy(); d = BD(im)
    d.rectangle((40, 420, 200, 920), fill=(150, 98, 60)); d.rectangle((56, 436, 184, 920), fill=(190, 222, 246))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(3):
        q = ease((lt - k * .5) / 1.2); x = lerp(560 - k * 40, 100, q)
        figure(dl, x, 760, 1.4, [(60, 110, 200), (200, 140, 60), (90, 150, 120)][k], long=k == 1)
    L.putalpha(L.getchannel('A').point(lambda p: p)); im.alpha_composite(L); d = BD(im)
    r = (360, 420, 680, 620); card(im, r, (255, 255, 255), 18); d = BD(im)
    for k, (lab, w_) in enumerate((('Nombre: —', 'nombre'), ('Número: —', 'número'))):
        if t > wt(1, w_): d.text((r[0] + 24, r[1] + 50 + k * 60), lab, font=F('Inter-Black.otf', 28), fill=(150, 150, 160), anchor='lm')
    q = t - wt(1, 'nunca')
    if q > 0: stamp(im, 360, 1060, ['CASI NUNCA VOLVÍAN'], RED, q, ang=-5, size=42)
    obj('in', (120, 470, 520, 550)); obj('out', r); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    q = back_out((t - wt(2, 'gustara') + .1) / .4)
    if q > 0:   # corazón
        cx, cy, s = 360, 560, 1.3 * q
        d.ellipse((cx - 60 * s, cy - 50 * s, cx, cy + 10 * s), fill=RED); d.ellipse((cx, cy - 50 * s, cx + 60 * s, cy + 10 * s), fill=RED); d.polygon([(cx - 58 * s, cy - 10 * s), (cx + 58 * s, cy - 10 * s), (cx, cy + 60 * s)], fill=RED)
        chip(im, 360, 700, 'SÍ LES GUSTABA', q, col=(36, 36, 40), size=24)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 980, .55, None); im.alpha_composite(L); d = BD(im)
    q = t - wt(2, 'escribir')
    if q > 0: d.text((360, 980), '0', font=F('Inter-Black.otf', 70), fill=RED, anchor='mm'); chip(im, 360, 1190, 'NADIE LES ESCRIBIÓ', q, size=22)
    obj('in', (360, 420, 680, 620)); obj('out', (277, 815, 443, 1145)); return im

def sc3(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = (60, 500, 660, 800); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((r[0] + 30, r[1] + 44), 'Mi Negocio', font=F('Inter-Black.otf', 32), fill=(30, 30, 36), anchor='lm')
    d.rounded_rectangle((r[2] - 110, r[1] + 26, r[2] - 30, r[1] + 62), 18, fill=RED); d.text((r[2] - 70, r[1] + 44), 'PRO', font=F('Inter-Black.otf', 20), fill='white', anchor='mm')
    x = r[0] + 30
    for tb in ['Agenda', 'Clientes', 'Reseñas', 'Menú QR']:
        f = F('Inter-Bold.otf', 18); tw = d.textlength(tb, font=f) + 26; on = tb == 'Clientes'
        d.rounded_rectangle((x, r[1] + 86, x + tw, r[1] + 122), 18, fill=RED if on else (240, 240, 244)); d.text((x + tw / 2, r[1] + 104), tb, font=f, fill='white' if on else (90, 90, 100), anchor='mm'); x += tw + 8
    y = r[1] + 150; on_q = ease((t - wt(3, 'captura')) / .4)
    d.rounded_rectangle((r[0] + 30, y, r[2] - 30, y + 110), 16, fill=(244, 244, 247))
    d.text((r[0] + 50, y + 40), 'Captura de clientes', font=F('Inter-Black.otf', 22), fill=(30, 30, 36), anchor='lm'); d.text((r[0] + 50, y + 72), 'Formulario en tu portada', font=F('Inter-SemiBold.otf', 18), fill=(120, 120, 130), anchor='lm')
    tx = r[2] - 110; d.rounded_rectangle((tx, y + 36, tx + 60, y + 66), 15, fill=mix((190, 190, 200), GREEN_OK, on_q)); d.ellipse((tx + 3 + 30 * on_q, y + 39, tx + 27 + 30 * on_q, y + 63), fill='white')
    chip(im, 360, 440, 'CON SU MEMBRESÍA', t - wt(3, 'membresía'), col=WHITE, tcol=RED, size=24)
    im = camera(im, 1.0 + .12 * on_q, 360, 660)
    obj('in', (277, 815, 443, 1145)); obj('out', (r[0] + 30, y, r[2] - 30, y + 110)); return im

def portada_n(im, t, fill_q=(0, 0, 0), form_q=1.0):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((186, 440, 534, 540), fill=(120, 70, 140)); d.text((360, 476), 'Mueblería Nubia', font=F('Inter-Black.otf', 28), fill='white', anchor='mm'); d.text((360, 512), 'sumiago.com/muebleria-nubia', font=F('Inter-SemiBold.otf', 16), fill=(230, 210, 240), anchor='mm')
    if form_q > 0:
        L2 = Image.new('RGBA', (W, H), (0, 0, 0, 0)); form_card(L2, (200, 570, 520, 1000), t, fill_q); L2.putalpha(L2.getchannel('A').point(lambda p: int(p * form_q))); im.alpha_composite(L2, (0, int((1 - form_q) * 40)))

def sc4(t, lt):
    im = BGM.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 80)))
    portada_n(im, t, form_q=ease((t - wt(4, 'déjame') + .2) / .5))
    fq = ease((t - wt(4, 'déjame')) / .6)
    im = camera(im, 1.0 + .15 * fq, 360, lerp(760, 760, fq))
    obj('in', (90, 650, 630, 760)); obj('out', (200, 570, 520, 1000)); return im

def sc5(t, lt):
    im = BGM.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 80)))
    fq = tuple(ease((t - wt(5, w) + .1) / .6) for w in ('nombre', 'whatsapp', 'correo'))
    portada_n(im, t, fill_q=fq)
    q = t - wt(5, '10')
    if q > 0:
        chip(im, 360, 1150, 'EN 10 SEGUNDOS', q, col=WHITE, tcol=RED, size=28)
    im = camera(im, 1.15, 360, 790)
    obj('in', (200, 570, 520, 1000)); obj('out', (200, 570, 520, 1000)); return im

def sc6(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    r = (50, 380, 670, 960); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((80, 430), 'Clientes', font=F('Inter-Black.otf', 30), fill=(30, 30, 36), anchor='lm')
    d.rectangle((70, 470, 650, 510), fill=(244, 244, 247))
    for x, h in ((90, 'Nombre'), (300, 'WhatsApp'), (520, 'Fecha')): d.text((x, 490), h, font=F('Inter-Bold.otf', 18), fill=(120, 120, 130), anchor='lm')
    for k, (n, w) in enumerate(LEADS):
        a = ease((t - wt(6, 'lista') - k * .12) / .3)
        if a <= 0: continue
        y = 520 + k * 70; d.line((70, y + 64, 650, y + 64), fill=(236, 236, 240), width=2)
        d.text((90, y + 32), n, font=F('Inter-Bold.otf', 22), fill=(30, 30, 36), anchor='lm'); d.text((300, y + 32), w, font=F('Inter-SemiBold.otf', 20), fill=(80, 80, 90), anchor='lm'); d.text((520, y + 32), f'{20 + k}/11', font=F('Inter-SemiBold.otf', 20), fill=(120, 120, 130), anchor='lm')
    q = t - wt(6, 'descargar')
    if q > 0:
        b = back_out(q / .35); d.rounded_rectangle((360 - 220 * b, 1010 - 36 * b, 360 + 220 * b, 1010 + 36 * b), 36, fill=XL)
        if b > .7: d.text((360, 1010), '⬇ Descargar para Excel'.replace('⬇ ', ''), font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    q = t - wt(6, 'excel')
    if q > 0:
        a = back_out(q / .35); cx, cy = 360, 1150
        d.rounded_rectangle((cx - 50 * a, cy - 60 * a, cx + 50 * a, cy + 60 * a), 10, fill=(255, 255, 255), outline=XL, width=4)
        if a > .7: d.rectangle((cx - 50, cy - 20, cx + 50, cy + 20), fill=XL); d.text((cx, cy), 'CSV', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    fq = ease((t - wt(6, 'descargar') + .2) / .7)
    im = camera(im, 1.0, 360, 640)
    obj('in', (200, 570, 520, 1000)); obj('out', (140, 974, 580, 1046)); return im

def sc7(t, lt):
    im = BGM.copy(); d = BD(im)
    a = ease(lt / 1.0); x = lerp(W + 200, 420, a)
    d.rounded_rectangle((x - 200, 560, x + 60, 800), 14, fill=(245, 245, 248)); d.rounded_rectangle((x + 60, 640, x + 180, 800), 14, fill=RED); d.rectangle((x + 80, 660, x + 150, 720), fill=(190, 222, 246))
    d.ellipse((x - 160, 770, x - 100, 830), fill=(30, 30, 34)); d.ellipse((x + 90, 770, x + 150, 830), fill=(30, 30, 34)); d.text((x - 70, 680), 'NUEVO', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
    q = t - wt(7, 'colección')
    if q > 0: chip(im, 360, 430, 'NUEVA COLECCIÓN', q, size=30)
    q = t - wt(7, 'esperar')
    if q > 0: stamp(im, 360, 1080, ['SIN ESPERAR'], RED, q, ang=-6, size=48)
    obj('in', (140, 974, 580, 1046)); obj('out', (220, 560, 600, 830)); return im

def sc8(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 800, 1.25, None); im.alpha_composite(L); d = BD(im)
    d.text((360, 470), 'Mensaje para tu lista', font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    d.rounded_rectangle((200, 500, 520, 600), 14, fill=(37, 120, 80)); d.text((220, 530), '¡Llegó la nueva colección!', font=F('Inter-Bold.otf', 18), fill='white', anchor='lm'); d.text((220, 566), 'Te guardé uno de los primeros.', font=F('Inter-SemiBold.otf', 16), fill=(220, 240, 230), anchor='lm')
    for k, (n, w) in enumerate(LEADS):
        a = ease((t - wt(8, 'escribió') - k * .18) / .3)
        y = 630 + k * 90; d.rounded_rectangle((200, y, 520, y + 76), 14, fill=(36, 38, 48)); d.text((220, y + 38), n, font=F('Inter-Bold.otf', 20), fill='white', anchor='lm')
        if a > 0: d.line((468, y + 38, 478, y + 50, 500, y + 26), fill=GREEN_OK, width=5)
    chip(im, 360, 1190, 'A TODOS LOS «LO VOY A PENSAR»', t - wt(8, 'todos'), col=WHITE, tcol=RED, size=20)
    obj('in', (220, 560, 600, 830)); obj('out', (200, 630, 520, 1086)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    msgs = ['¡Sí! Lo quiero', '¿Todavía está el sofá azul?', 'Paso el sábado']
    for k, m in enumerate(msgs): bubble(im, 60 + (k % 2) * 120, 470 + k * 140, m, lt - .2 - k * .35, col=GREEN_OK if k != 1 else (36, 38, 48), size=28)
    q = t - wt(9, 'pensado')
    if q > 0: stamp(im, 360, 1060, ['YA LO HABÍAN', 'PENSADO'], RED, q, ang=-5, size=44)
    obj('in', (200, 630, 520, 1086)); obj('out', (60, 470, 500, 550)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    q = t - ct(10)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    a = ease(q / 4.5); figure(dl, lerp(200, 60, a), 700, 1.5, (60, 110, 200)); L.putalpha(L.getchannel('A').point(lambda p: int(p * (1 - .8 * a)))); im.alpha_composite(L); d = BD(im)
    if q > .5: d.text((200, 520), '?', font=F('Inter-Black.otf', 60), fill=(150, 150, 160), anchor='mm')
    q2 = t - wt(10, 'pierde')
    if q2 > 0: chip(im, 200, 960, 'OPORTUNIDAD PERDIDA', q2, col=(90, 90, 100), size=20)
    q3 = t - wt(10, 'captura')
    if q3 > 0:
        b = back_out(q3 / .4); r = (380, 560, 660, 880); card(im, (520 - 140 * b, 720 - 160 * b, 520 + 140 * b, 720 + 160 * b), (255, 255, 255), 22); d = BD(im)
        if b > .7:
            d.text((520, 600), 'Interesados', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='mm')
            for k in range(4): d.rounded_rectangle((410, 640 + k * 50, 630, 676 + k * 50), 10, fill=(244, 244, 247)); d.ellipse((418, 646 + k * 50, 442, 670 + k * 50), fill=GREEN_OK)
        chip(im, 520, 960, 'GUARDADOS', q3 - .3, col=GREEN_OK, size=22)
    obj('in', (60, 470, 500, 550)); obj('out', (380, 560, 660, 880)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Mi Negocio · Clientes', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Tus interesados en una lista', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'DESCARGABLE PARA EXCEL', t - wt(11, 'regístrate'), col=XL, size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'nadie')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'Que nadie se vaya', F('Inter-BlackItalic.otf', 42), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'sin dejar su número.', F('Inter-BlackItalic.otf', 42), WHITE, (q + .1) / .4)
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
