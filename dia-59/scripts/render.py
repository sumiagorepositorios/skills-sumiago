"""Día 59 — "Lo vi tarde" (historia: Hernán pierde un comprador por enterarse tarde; instala Sumiago en su pantalla de inicio y activa las notificaciones).
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
KEY = {'hernán', 'nevera', 'marketplace', 'sumiago', 'sumiago.', 'noche', 'quiero!».', 'vio', 'otro', 'día', 'otra', 'gracias».', '«instala', 'sumiago».', '«instalar».', 'ícono', 'pantalla', 'inicio', '«activa', 'notificaciones', 'instante', '«activar»', 'permiso', 'atajos', 'sonó', 'quiere', '2', 'minutos', 'dueño', 'instalar', 'iphone', 'safari', '«compartir»', 'link', 'vender…', 'tiempo'}
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
        mask_text(im, (W // 2, 800), 'Instala Sumiago', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
GREEN_OK = (37, 190, 100); VG = (22, 163, 74); WA = (37, 211, 102)
def hernan(d, x, y, s, bob=0): figure(d, x, y, s, (70, 130, 110), skin=(196, 146, 110), hair=(40, 30, 24), bob=bob)
def nevera(d, cx, by, s):
    d.rounded_rectangle((cx - 70 * s, by - 260 * s, cx + 70 * s, by), 14 * s, fill=(236, 240, 244), outline=(170, 176, 186), width=max(2, int(4 * s)))
    d.line((cx - 70 * s, by - 170 * s, cx + 70 * s, by - 170 * s), fill=(170, 176, 186), width=max(2, int(4 * s)))
    d.rounded_rectangle((cx + 44 * s, by - 240 * s, cx + 54 * s, by - 190 * s), 4, fill=(150, 156, 166)); d.rounded_rectangle((cx + 44 * s, by - 150 * s, cx + 54 * s, by - 80 * s), 4, fill=(150, 156, 166))
def sg_icon(d, x, y, sz, a=1.0):
    d.rounded_rectangle((x, y, x + sz, y + sz), sz * .24, fill=RED)
    cx, cy, s = x + sz / 2, y + sz / 2, sz / 90
    d.ellipse((cx - 26 * s, cy - 22 * s, cx, cy + 4 * s), fill='white'); d.ellipse((cx, cy - 22 * s, cx + 26 * s, cy + 4 * s), fill='white'); d.polygon([(cx - 25 * s, cy - 4 * s), (cx + 25 * s, cy - 4 * s), (cx, cy + 26 * s)], fill='white')
def bell(d, cx, cy, s, col=GOLD):
    d.pieslice((cx - 24 * s, cy - 26 * s, cx + 24 * s, cy + 22 * s), 180, 360, fill=col); d.rectangle((cx - 24 * s, cy - 2 * s, cx + 24 * s, cy + 14 * s), fill=col); d.rectangle((cx - 30 * s, cy + 12 * s, cx + 30 * s, cy + 20 * s), fill=col); d.ellipse((cx - 7 * s, cy + 18 * s, cx + 7 * s, cy + 32 * s), fill=col)
def scr(im, cx, cy, s):
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, cx, cy, 1.25 * s, None); im.alpha_composite(L)
    w = 375 * s; x0 = cx - w / 2 + 14; xe = x0 + w - 28; y0 = cy - 375 * s + 60; y1 = cy + 375 * s - 50
    return x0, xe, y0, y1
APPC = [(66, 133, 244), (52, 168, 83), (251, 188, 5), (234, 67, 53), (120, 80, 200), (0, 150, 136), (255, 112, 67), (96, 125, 139), (233, 30, 99), (3, 169, 244), (139, 195, 74)]
def home(im, cx, cy, s, t, show=0.0, press=0.0):
    x0, xe, y0, y1 = scr(im, cx, cy, s); d = BD(im)
    d.rectangle((x0, y0, xe, y1), fill=(40, 60, 110))
    n = 0; sz = 62 * s; gap = (xe - x0 - 4 * sz) / 5; pos = None
    for r in range(5):
        for c in range(4):
            x = x0 + gap + c * (sz + gap); y = y0 + 40 * s + r * (sz + 40 * s)
            if r == 2 and c == 1:
                pos = (x, y)
                if show > 0:
                    b = back_out(show / .4); cx2, cy2 = x + sz / 2, y + sz / 2; z = sz * b * (1 + .08 * press)
                    sg_icon(d, cx2 - z / 2, cy2 - z / 2, z)
                    if b > .8: d.text((cx2, y + sz + 16 * s), 'Sumiago', font=F('Inter-Bold.otf', int(13 * s)), fill='white', anchor='mm')
                continue
            d.rounded_rectangle((x, y, x + sz, y + sz), sz * .24, fill=APPC[n % len(APPC)]); n += 1
    return pos, sz
def pwa_bar(im, x0, xe, y, s, t, kind, q, press=0.0):
    a = ease(q / .4)
    if a <= 0: return None
    yy = y + (1 - a) * 120 * s
    d = BD(im); r = (x0 + 8, yy, xe - 8, yy + 84 * s); d.rounded_rectangle(r, 16 * s, fill=(10, 10, 10))
    sg_icon(d, r[0] + 12 * s, yy + 18 * s, 48 * s)
    if kind == 'inst': t1, t2, bt = 'Instala Sumiago', 'Más rápido y con avisos', 'Instalar'
    else: t1, t2, bt = 'Activa las notificaciones', 'Ofertas, mensajes y ventas', 'Activar'
    if kind == 'inst': d.text((r[0] + 72 * s, yy + 32 * s), t1, font=F('Inter-Black.otf', int(17 * s)), fill='white', anchor='lm'); d.text((r[0] + 72 * s, yy + 56 * s), t2, font=F('Inter-SemiBold.otf', int(13 * s)), fill=(212, 212, 216), anchor='lm')
    else: d.text((r[0] + 72 * s, yy + 22 * s), 'Activa las', font=F('Inter-Black.otf', int(16 * s)), fill='white', anchor='lm'); d.text((r[0] + 72 * s, yy + 42 * s), 'notificaciones', font=F('Inter-Black.otf', int(16 * s)), fill='white', anchor='lm'); d.text((r[0] + 72 * s, yy + 64 * s), t2, font=F('Inter-SemiBold.otf', int(11 * s)), fill=(212, 212, 216), anchor='lm')
    br = (r[2] - 98 * s, yy + 22 * s, r[2] - 12 * s, yy + 62 * s); d.rounded_rectangle(br, 10 * s, fill=RED if press <= 0 else mix(RED, (0, 0, 0), .25)); d.text(((br[0] + br[2]) / 2, (br[1] + br[3]) / 2), bt, font=F('Inter-Black.otf', int(15 * s)), fill='white', anchor='mm')
    return br
def market_page(im, cx, cy, s):
    x0, xe, y0, y1 = scr(im, cx, cy, s); d = BD(im)
    d.rectangle((x0, y0, xe, y0 + 50 * s), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25 * s), 'MARKETPLACE', font=F('Inter-Black.otf', int(18 * s)), fill='white', anchor='lm')
    for k in range(4):
        c, r = k % 2, k // 2; bx = x0 + 12 + c * ((xe - x0 - 24) / 2); bw = (xe - x0 - 36) / 2
        d.rounded_rectangle((bx, y0 + 70 * s + r * 220 * s, bx + bw, y0 + 270 * s + r * 220 * s), 12, fill=(48, 50, 60))
    return x0, xe, y0, y1

def sc0(t, lt):
    im = gradient((30, 34, 60), (14, 16, 30)); d = BD(im)
    d.ellipse((560, 120, 640, 200), fill=(240, 236, 210)); d.ellipse((585, 110, 665, 190), fill=(30, 34, 60))
    d.rectangle((0, 1000, W, H), fill=(50, 44, 50)); nevera(d, 520, 1000, 1.5)
    d.rectangle((60, 940, 300, 960), fill=(120, 84, 56)); d.rectangle((80, 960, 96, 1000), fill=(100, 70, 46)); d.rectangle((264, 960, 280, 1000), fill=(100, 70, 46))
    q = t - wt(0, 'quiero')
    lit = 0 < q < 2.5
    d.rounded_rectangle((150, 912, 214, 942), 6, fill=(240, 240, 244) if lit else (30, 30, 34))
    if lit: d.ellipse((140, 880, 224, 964), outline=(255, 255, 255, int(120 * (1 - q / 2.5))), width=3)
    q2 = t - wt(0, 'noche')
    if q2 > 0: chip(im, 360, 420, 'MARTES, 9:40 P. M.', q2, col=(36, 36, 40), size=26)
    if q > 0: chip(im, 182, 840, '¡LO QUIERO!', q, col=RED, size=20)
    obj('in', (420, 740, 620, 1000)); obj('out', (150, 912, 214, 942)); return im

def sc1(t, lt):
    m = t < wt(1, 'enteró')
    im = gradient((30, 34, 60), (14, 16, 30)) if m else gradient((255, 236, 200), (250, 220, 170)); d = BD(im)
    if m:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); hernan(ImageDraw.Draw(L), 360, 760, 1.8); im.alpha_composite(L); d = BD(im)
        for k in range(3): z = (t * .8 + k / 3) % 1; d.text((430 + z * 80, 640 - z * 140), 'z', font=F('Inter-Black.otf', int(30 + z * 30)), fill=(200, 200, 230, int(255 * (1 - z))), anchor='mm')
        q = t - wt(1, 'vio')
        if q > 0: chip(im, 360, 1120, 'NO LO VIO', q, col=RED, size=28)
    else:
        d.ellipse((560, 120, 680, 240), fill=(255, 210, 90))
        x0, xe, y0, y1 = scr(im, 360, 760, 1.0); d = BD(im)
        d.rectangle((x0, y0, xe, y0 + 50), fill=(20, 20, 24)); d.text((x0 + 16, y0 + 25), 'Notificaciones', font=F('Inter-Black.otf', 18), fill='white', anchor='lm')
        d.rounded_rectangle((x0 + 12, y0 + 70, xe - 12, y0 + 170), 14, fill=(255, 255, 255)); d.text((x0 + 28, y0 + 104), 'Alguien quiere tu artículo', font=F('Inter-Black.otf', 18), fill=(30, 30, 36), anchor='lm'); d.text((x0 + 28, y0 + 140), 'Ayer · 9:40 p. m.', font=F('Inter-Bold.otf', 16), fill=RED, anchor='lm')
        q = t - wt(1, 'día')
        if q > 0: chip(im, 360, 1170, 'SE ENTERÓ AL OTRO DÍA', q, col=(36, 36, 40), size=24)
    obj('in', (150, 912, 214, 942)); obj('out', (175, 455, 545, 555)); return im

def sc2(t, lt):
    im = gradient((228, 221, 212), (205, 198, 188)); d = BD(im)
    d.rectangle((0, 290, W, 370), fill=(7, 94, 84)); d.text((40, 330), 'WhatsApp · Comprador', font=F('Inter-Black.otf', 28), fill='white', anchor='lm')
    a = back_out((t - wt(2, 'escribió') + .1) / .35)
    if a > 0:
        d.rounded_rectangle((660 - 420 * a, 430, 660, 520), 22, fill=(220, 248, 198))
        if a > .8: d.text((270, 475), '¡Hola! ¿Aún la quieres?', font=F('Inter-SemiBold.otf', 28), fill=(30, 30, 36), anchor='lm')
    a = back_out((t - wt(2, 'ya') + .2) / .35)
    if a > 0:
        d.rounded_rectangle((60, 570, 60 + 440 * a, 660), 22, fill=(255, 255, 255))
        if a > .8: d.text((90, 615), 'Ya compré otra, gracias.', font=F('Inter-SemiBold.otf', 28), fill=(30, 30, 36), anchor='lm')
    q = t - wt(2, 'gracias')
    if q > 0: stamp(im, 360, 900, ['TARDE'], RED, q, ang=-6, size=80)
    obj('in', (175, 455, 545, 555)); obj('out', (60, 570, 500, 660)); return im

def sc3(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    x0, xe, y0, y1 = market_page(im, 360, 760, 1.0)
    br = pwa_bar(im, x0, xe, y1 - 110, 1.0, t, 'inst', t - wt(3, 'aviso') + .2)
    q = t - wt(3, 'instala')
    if q > 0 and br: d = BD(im); d.rounded_rectangle((x0 + 2, y1 - 116, xe - 2, y1 - 20), 20, outline=GOLD, width=4)
    obj('in', (60, 570, 500, 660)); obj('out', (x0 + 8, y1 - 110, xe - 8, y1 - 26)); return im

def sc4(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238)); d = BD(im)
    q = t - wt(4, 'instalar')
    if q < .5:
        x0, xe, y0, y1 = market_page(im, 360, 760, 1.0)
        br = pwa_bar(im, x0, xe, y1 - 110, 1.0, t, 'inst', 1, press=q)
        if 0 < q < .5: d = BD(im); cx, cy = (br[0] + br[2]) / 2, (br[1] + br[3]) / 2; rr = 20 + q * 120; d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=(255, 255, 255, int(255 * (1 - q / .5))), width=5)
    else:
        pos, sz = home(im, 360, 760, 1.0, t, show=t - wt(4, 'ícono') + .3)
        if t > wt(4, 'ícono'): sparkles(im, pos[0] + sz / 2, pos[1] + sz / 2, t, n=10, rad=90)
        qq = t - wt(4, 'pantalla')
        if qq > 0: chip(im, 360, 1170, 'EN TU PANTALLA DE INICIO', qq, col=RED, size=24)
    obj('in', (182, 1025, 538, 1109)); obj('out', (230, 470, 490, 1050)); return im

def sc5(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    x0, xe, y0, y1 = market_page(im, 360, 760, 1.0)
    br = pwa_bar(im, x0, xe, y1 - 110, 1.0, t, 'push', t - wt(5, 'otro') + .2)
    d = BD(im); q = t - wt(5, 'notificaciones')
    if q > 0: bell(d, 360, 330, 1.6 * back_out(q / .35)); 
    for k, w_ in enumerate(('ofertas', 'mensajes', 'ventas')):
        qq = t - wt(5, w_)
        if qq > 0: chip(im, 140 + k * 220, 1180, w_.upper(), qq, col=WHITE, tcol=RED, size=22)
    obj('in', (230, 470, 490, 1050)); obj('out', (x0 + 8, y1 - 110, xe - 8, y1 - 26)); return im

def sc6(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    x0, xe, y0, y1 = market_page(im, 360, 760, 1.0); d = BD(im)
    d.rectangle((x0, y0, xe, y1), fill=(0, 0, 0, 120))
    r = (x0 + 20, 620, xe - 20, 880); d.rounded_rectangle(r, 20, fill=(250, 250, 250))
    bell(d, 360, 670, .8, RED); d.text((360, 730), '¿Permitir notificaciones', font=F('Inter-Black.otf', 20), fill=(30, 30, 36), anchor='mm'); d.text((360, 758), 'de Sumiago?', font=F('Inter-Black.otf', 20), fill=(30, 30, 36), anchor='mm')
    q = t - wt(6, 'aceptó')
    d.rounded_rectangle((r[0] + 16, 800, 352, 852), 14, fill=(230, 230, 234)); d.text(((r[0] + 16 + 352) / 2, 826), 'Bloquear', font=F('Inter-Black.otf', 18), fill=(90, 90, 100), anchor='mm')
    d.rounded_rectangle((368, 800, r[2] - 16, 852), 14, fill=RED if q <= 0 or q > .3 else mix(RED, (0, 0, 0), .25)); d.text(((368 + r[2] - 16) / 2, 826), 'Permitir', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    if q > .3: d.ellipse((310, 600, 410, 700), fill=GREEN_OK); d.line((338, 652, 356, 670, 386, 630), fill='white', width=9)
    obj('in', (182, 1025, 538, 1109)); obj('out', (368, 800, 504, 852)); return im

def sc7(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    pos, sz = home(im, 360, 760, 1.0, t, show=1, press=1 if t > wt(7, 'presionado') else 0)
    d = BD(im); q = t - wt(7, 'presionado')
    if q > 0:
        d.rectangle((182, 395, 538, 1125), fill=(0, 0, 0, 90)); sg_icon(d, pos[0] - 3, pos[1] - 3, sz + 6)
    qa = t - wt(7, 'atajos') + .2
    if qa > 0:
        a = ease(qa / .35); r = (pos[0], pos[1] + sz + 20, pos[0] + 300 * a, pos[1] + sz + 20 + 190 * a); d.rounded_rectangle(r, 16, fill=(250, 250, 250))
        if a > .9:
            for k, (lab, w_) in enumerate([('Publicar anuncio', 'publicar'), ('Para ti', 'para'), ('Mis ofertas', 'mis')]):
                y = r[1] + 32 + k * 62; on = t > wt(7, w_)
                sg_icon(d, r[0] + 14, y - 18, 36); d.text((r[0] + 62, y), lab, font=F('Inter-Black.otf', 21), fill=(30, 30, 36) if on else (170, 170, 178), anchor='lm')
    obj('in', (368, 800, 504, 852)); obj('out', (pos[0], pos[1], pos[0] + sz, pos[1] + sz)); return im

def sc8(t, lt):
    im = gradient((235, 244, 250), (210, 226, 238))
    x0, xe, y0, y1 = scr(im, 360, 760, 1.0); d = BD(im)
    d.rectangle((x0, y0, xe, y1), fill=(30, 40, 70)); d.text((360, y0 + 110), '7:15', font=F('Inter-Black.otf', 70), fill='white', anchor='mm')
    q = t - wt(8, 'sonó') + .1
    if q > 0:
        sh = math.sin(t * 60) * 4 * max(0, 1 - q / .8)
        a = ease(q / .35); r = (x0 + 10 + sh, y0 + 200 - (1 - a) * 60, xe - 10 + sh, y0 + 300 - (1 - a) * 60); d.rounded_rectangle(r, 18, fill=(250, 250, 250, int(255 * a)))
        if a > .8: sg_icon(d, r[0] + 12, r[1] + 26, 48); d.text((r[0] + 72, r[1] + 34), 'Sumiago · ahora', font=F('Inter-Bold.otf', 14), fill=(120, 120, 130), anchor='lm'); d.text((r[0] + 72, r[1] + 66), 'Alguien quiere tu artículo', font=F('Inter-Black.otf', 17), fill=(30, 30, 36), anchor='lm')
        for k in range(2):
            z = (q * 2 + k / 2) % 1; d.arc((140 - z * 40, 700 - z * 40, 180 + z * 40, 820 + z * 40), 120, 240, fill=(230, 38, 47, int(255 * (1 - z))), width=5); d.arc((540 - z * 40, 700 - z * 40, 580 + z * 40, 820 + z * 40), -60, 60, fill=(230, 38, 47, int(255 * (1 - z))), width=5)
    q = t - wt(8, 'semana')
    if q > 0: chip(im, 360, 1180, 'UNA SEMANA DESPUÉS', q, col=(36, 36, 40), size=24)
    obj('in', (300, 600, 360, 660)); obj('out', (192, 435, 528, 535)); return im

def sc9(t, lt):
    im = gradient((250, 236, 214), (236, 214, 190)); d = BD(im)
    d.rectangle((0, 1000, W, H), fill=(190, 160, 130))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); hernan(dl, 150, 840, 1.5); figure(dl, 560, 840, 1.5, (200, 110, 60), skin=(214, 166, 128), hair=(70, 40, 26), bob=-abs(math.sin(t * 5)) * 3); im.alpha_composite(L); d = BD(im)
    p = ease((t - wt(9, 'noche')) / 1.4); nevera(d, lerp(330, 470, p), 1000, 1.2)
    q = t - wt(9, 'minutos')
    if q > 0:
        d.ellipse((290, 330, 430, 470), fill=(255, 255, 255), outline=RED, width=8); d.line((360, 400, 360, 352), fill=(30, 30, 36), width=6); d.line((360, 400, 360 + 30 * math.sin(q * 3), 400 - 30 * math.cos(q * 3)), fill=RED, width=6)
        chip(im, 360, 520, 'RESPONDIÓ EN 2 MINUTOS', q, col=RED, size=24)
    q = t - wt(9, 'dueño')
    if q > 0: stamp(im, 360, 1130, ['¡NUEVO DUEÑO!'], GREEN_OK, q, ang=-5, size=50)
    obj('in', (192, 435, 528, 535)); obj('out', (300, 740, 520, 1000)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    a = back_out((t - wt(10, 'instalar') + .1) / .35)
    if a > 0:
        card(im, (360 - 290 * a, 430, 360 + 290 * a, 590), (250, 250, 250), 22); d = BD(im)
        if a > .7: sg_icon(d, 100, 470, 80); d.text((210, 490), 'Android y PC', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm'); d.text((210, 534), 'Botón «Instalar»', font=F('Inter-Bold.otf', 24), fill=RED, anchor='lm')
    a = back_out((t - wt(10, 'iphone') + .1) / .35)
    if a > 0:
        card(im, (360 - 290 * a, 630, 360 + 290 * a, 850), (250, 250, 250), 22); d = BD(im)
        if a > .7:
            d.rounded_rectangle((100, 680, 180, 760), 18, fill=(30, 30, 36)); d.rectangle((128, 712, 152, 744), outline='white', width=4); d.line((140, 696, 140, 728), fill='white', width=4); d.polygon([(130, 704), (140, 692), (150, 704)], fill='white')
            d.text((210, 690), 'iPhone (Safari)', font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm')
            if t > wt(10, 'compartir'): d.text((210, 734), '«Compartir»', font=F('Inter-Bold.otf', 24), fill=RED, anchor='lm')
            if t > wt(10, 'agregar'): d.text((210, 774), '«Agregar a pantalla', font=F('Inter-Bold.otf', 24), fill=RED, anchor='lm'); d.text((210, 806), 'de inicio»', font=F('Inter-Bold.otf', 24), fill=RED, anchor='lm')
    obj('in', (300, 740, 520, 1000)); obj('out', (70, 430, 650, 590)); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Sumiago en tu celular', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 202), 'Instálala y activa los avisos', F('Inter-Bold.otf', 26), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'INSTALAR · ACTIVAR', t - wt(11, 'regístrate'), col=GOLD, tcol=(30, 30, 36), size=20)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'vender')
    if q > -.3:
        mask_text(im, (W / 2, 740), 'A veces, vender…', F('Inter-BlackItalic.otf', 44), WHITE, (q + .3) / .4)
        mask_text(im, (W / 2, 795), 'es enterarse a tiempo.', F('Inter-BlackItalic.otf', 42), WHITE, (t - wt(11, 'enterarse') + .3) / .4)
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
