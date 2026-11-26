"""Día 35 — "Que te busquen a ti" (historia: Laura deja de buscar empleo y se deja encontrar en Contrátame Sumiago).
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
KEY = {'47', '3', 'cero.', 'cero', 'correo', 'puertas', 'existía.', 'existía', 'contrario', 'encontrar.', 'encontrar', 'gratis', 'contrátame', 'sumiago', 'teléfono',
       'registradas.', 'registradas', '10', 'empresa', 'profesión', 'ciudad.', 'ciudad', 'nada.', 'conocían.', 'talento.', 'vean.', 'trabajo,', 'link', 'ti.'}
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
        mask_text(im, (W // 2, 800), 'Que te busquen a ti', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

# ---------- objetos ----------
BLUE_BG = ((226, 234, 244), (196, 208, 224))
def room_bg(top=BLUE_BG[0], bot=BLUE_BG[1]):
    im = gradient(top, bot); d = ImageDraw.Draw(im)
    for x in range(0, W, 60): d.line((x, 0, x, H), fill=mix(top, (255, 255, 255), .35), width=1)
    for y in range(0, H, 60): d.line((0, y, W, y), fill=mix(top, (255, 255, 255), .35), width=1)
    return im
BGR = room_bg()

def face_laura(size=300):
    L = Image.new('RGBA', (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(L); s = size / 300
    skin, hair = (176, 122, 90), (34, 24, 20)
    d.rectangle((0, 0, size, size), fill=(220, 230, 244))
    for k in range(14):   # pelo rizado
        a = k / 14 * math.pi * 1.25 + math.pi * .87; r = 92 * s
        x, y = 150 * s + math.cos(a) * r, 140 * s + math.sin(a) * r * 1.05; d.ellipse((x - 30 * s, y - 30 * s, x + 30 * s, y + 30 * s), fill=hair)
    d.rounded_rectangle((60 * s, 222 * s, 240 * s, 340 * s), 60 * s, fill=(40, 52, 80)); d.polygon([(120 * s, 222 * s), (180 * s, 222 * s), (150 * s, 262 * s)], fill=(250, 250, 250))
    d.rectangle((132 * s, 196 * s, 168 * s, 232 * s), fill=mix(skin, (0, 0, 0), .1))
    d.ellipse((90 * s, 70 * s, 210 * s, 214 * s), fill=skin)
    for k in range(6): x = 100 * s + k * 20 * s; d.ellipse((x - 18 * s, 50 * s, x + 18 * s, 92 * s), fill=hair)
    for ex in (124, 176): d.ellipse(((ex - 7) * s, 132 * s, (ex + 7) * s, 146 * s), fill=(30, 22, 20))
    d.arc((124 * s, 158 * s, 176 * s, 192 * s), 20, 160, fill=(120, 40, 40), width=max(1, int(5 * s)))
    d.ellipse((98 * s, 160 * s, 116 * s, 172 * s), fill=mix(skin, RED, .25)); d.ellipse((184 * s, 160 * s, 202 * s, 172 * s), fill=mix(skin, RED, .25))
    d.ellipse((88 * s, 150 * s, 98 * s, 164 * s), fill=GOLD); d.ellipse((202 * s, 150 * s, 212 * s, 164 * s), fill=GOLD)
    return L
FACE_L = face_laura()
def laura(d, x, y, s, bob=0, gray=0.0):
    figure(d, x, y, s, mix((40, 52, 80), (150, 150, 155), gray), skin=mix((176, 122, 90), (170, 170, 170), gray), hair=mix((34, 24, 20), (120, 120, 120), gray), long=True, bob=bob)

def laptop(im, cx, cy, s=1.0):
    d = BD(im); w, h = 400 * s, 250 * s
    d.rounded_rectangle((cx - w / 2, cy - h, cx + w / 2, cy), 16 * s, fill=(40, 42, 50))
    d.rounded_rectangle((cx - w / 2 + 14 * s, cy - h + 14 * s, cx + w / 2 - 14 * s, cy - 14 * s), 8 * s, fill=(245, 247, 250))
    d.polygon([(cx - w / 2 - 40 * s, cy + 26 * s), (cx + w / 2 + 40 * s, cy + 26 * s), (cx + w / 2, cy), (cx - w / 2, cy)], fill=(170, 174, 186))
    d.rectangle((cx - w / 2 + 14 * s, cy - h + 14 * s, cx + w / 2 - 14 * s, cy - h + 50 * s), fill=RED)
    d.text((cx - w / 2 + 30 * s, cy - h + 32 * s), 'Hoja de vida · Laura', font=F('Inter-Bold.otf', int(18 * s)), fill='white', anchor='lm')
    for k in range(5): d.rounded_rectangle((cx - w / 2 + 34 * s, cy - h + 70 * s + k * 28 * s, cx - w / 2 + (120 + (k * 47) % 200) * s, cy - h + 82 * s + k * 28 * s), 5, fill=(200, 205, 215))
    return (cx - w / 2 - 40 * s, cy - h, cx + w / 2 + 40 * s, cy + 26 * s)

def envelope(d, x, y, s, a=255):
    d.rounded_rectangle((x - 34 * s, y - 22 * s, x + 34 * s, y + 22 * s), 6 * s, fill=(255, 255, 255, a), outline=(200, 205, 215, a), width=2)
    d.line((x - 34 * s, y - 20 * s, x, y + 4 * s, x + 34 * s, y - 20 * s), fill=(RED[0], RED[1], RED[2], a), width=max(1, int(3 * s)))

def door(d, x, y, w, h, op=0.0, col=(170, 118, 76)):
    d.rectangle((x - 6, y - 6, x + w + 6, y + h), fill=(120, 80, 50))
    d.rectangle((x, y, x + w, y + h), fill=col)
    for k in range(2): d.rectangle((x + 14, y + 20 + k * (h / 2 - 10), x + w - 14, y + h / 2 - 10 + k * (h / 2 - 10)), outline=mix(col, (0, 0, 0), .2), width=3)
    d.ellipse((x + w - 26, y + h / 2, x + w - 14, y + h / 2 + 12), fill=GOLD)

def lock(d, cx, cy, s, col=RED):
    d.arc((cx - 22 * s, cy - 50 * s, cx + 22 * s, cy - 6 * s), 180, 360, fill=col, width=max(2, int(8 * s)))
    d.line((cx - 22 * s, cy - 28 * s, cx - 22 * s, cy - 6 * s), fill=col, width=max(2, int(8 * s))); d.line((cx + 22 * s, cy - 28 * s, cx + 22 * s, cy - 6 * s), fill=col, width=max(2, int(8 * s)))
    d.rounded_rectangle((cx - 36 * s, cy - 10 * s, cx + 36 * s, cy + 44 * s), 10 * s, fill=col)
    d.ellipse((cx - 7 * s, cy + 6 * s, cx + 7 * s, cy + 20 * s), fill='white'); d.rectangle((cx - 3 * s, cy + 16 * s, cx + 3 * s, cy + 32 * s), fill='white')

def building(d, cx, cy, s, col=(36, 36, 40)):
    d.rectangle((cx - 30 * s, cy - 50 * s, cx + 30 * s, cy + 40 * s), fill=col)
    for i in range(2):
        for j in range(3): d.rectangle((cx - 20 * s + i * 24 * s, cy - 40 * s + j * 24 * s, cx - 8 * s + i * 24 * s, cy - 28 * s + j * 24 * s), fill=GOLD)

# ---------- escenas ----------
def sc0(t, lt):
    im = BGR.copy(); d = BD(im)
    lr = laptop(im, 300, 800, 1.0)
    n = min(47, int(47 * max(0, (t - ct(0) - .3)) / (CL[0]['d'] * .75)))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
    for k in range(n):
        q = (t - (ct(0) + .3 + k * CL[0]['d'] * .75 / 47)) / .9
        if 0 < q < 1:
            x = lerp(300, 760, ease(q)); y = lerp(640, 420 + (k % 5) * 30, ease(q)) - math.sin(math.pi * q) * 80
            envelope(dl, x, y, .9, int(255 * (1 - q * .3)))
    im.alpha_composite(L)
    r = (430, 880, 690, 1060); card(im, r, (255, 255, 255), 22); d = BD(im)
    d.text((560, 920), 'ENVIADAS', font=F('Inter-Bold.otf', 22), fill=(120, 120, 130), anchor='mm')
    d.text((560, 990), str(n), font=F('Inter-Black.otf', 80), fill=RED, anchor='mm')
    chip(im, 150, 960, '3 MESES', t - wt(0, '3'), col=(36, 36, 40), size=26)
    im = camera(im, lerp(1.15, 1.0, ease(lt / 3)), 380, 800)
    obj('in', (100, 520, 600, 830)); obj('out', r); return im

def sc1(t, lt):
    im = BGR.copy(); r = (80, 360, 640, 1100); card(im, r, (255, 255, 255), 26); d = BD(im)
    d.rounded_rectangle((r[0], r[1], r[2], r[1] + 80), 26, fill=(36, 36, 40)); d.rectangle((r[0], r[1] + 50, r[2], r[1] + 80), fill=(36, 36, 40))
    d.text((r[0] + 30, r[1] + 40), 'Bandeja de entrada', font=F('Inter-Black.otf', 28), fill='white', anchor='lm')
    for k in range(4): d.rounded_rectangle((r[0] + 30, r[1] + 120 + k * 70, r[2] - 30, r[1] + 170 + k * 70), 12, outline=(225, 228, 235), width=3)
    q = t - wt(1, 'cero')
    b = back_out(q / .4)
    if b > 0:
        d.text((360, 900), '0', font=F('Inter-Black.otf', int(220 * b) + 1), fill=RED, anchor='mm')
        d.text((360, 1030), 'Sin respuestas', font=F('Inter-Bold.otf', 30), fill=(120, 120, 130), anchor='mm')
    # bola de polvo que rueda
    x = lerp(-60, 780, (lt / 2.2) % 1); ang = x / 20; d = BD(im)
    for k in range(8): a = ang + k * .8; d.line((x, 1150, x + math.cos(a) * 26, 1150 + math.sin(a) * 26), fill=(170, 150, 120), width=4)
    im = camera(im, 1.0 + .15 * ease(q / .5) if q > 0 else 1.0, 360, 860, shake=6 * max(0, 1 - q * 4) if q > 0 else 0, t=t)
    obj('in', r); obj('out', (230, 780, 490, 1020)); return im

def sc2(t, lt):
    im = gradient((255, 214, 170), (226, 200, 220)); d = BD(im)
    d.rounded_rectangle((440, 340, 660, 560), 10, fill=(255, 236, 180), outline=(255, 255, 255), width=10)
    sun = 520 - 80 * ease(lt / 3.5); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((520, sun - 40, 600, sun + 40), fill=255), (255, 200, 80), 30, 220)); d = BD(im)
    d.ellipse((530, sun - 30, 590, sun + 30), fill=(255, 210, 90))
    d.rounded_rectangle((-40, 900, 760, 1180), 40, fill=(250, 250, 252)); d.rounded_rectangle((-40, 960, 760, 1280), 30, fill=(120, 150, 200))
    d.ellipse((40, 860, 260, 960), fill=(255, 255, 255))
    # mano + celular
    pl = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    def content(dd, cx, cy, w, h):
        dd.text((cx, cy - h / 2 + 90), 'Correo', font=F('Inter-Black.otf', 26), fill='white', anchor='mm')
        a = t * 7; r = 26
        for k in range(8):
            aa = a + k * .785; dd.line((cx + math.cos(aa) * r * .5, cy - 80 + math.sin(aa) * r * .5, cx + math.cos(aa) * r, cy - 80 + math.sin(aa) * r), fill=(255, 255, 255, 60 + k * 24), width=5)
        dd.text((cx, cy), 'No hay mensajes', font=F('Inter-Bold.otf', 22), fill=(170, 170, 180), anchor='mm')
    phone(pl, 360, 760, .9, content); im.alpha_composite(pl); d = BD(im)
    days = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']; k = int(lt * 2.4) % 7
    chip(im, 150, 420, days[k], 1, col=(36, 36, 40), size=30)
    chip(im, 150, 500, '6:30 a. m.', t - wt(2, 'mañana'), col=WHITE, tcol=RED, size=24)
    im = camera(im, 1.0 + .1 * ease(lt / 3), 360, 760)
    obj('in', (225, 490, 495, 1030)); obj('out', (225, 490, 495, 1030)); return im

def sc3(t, lt):
    gr = ease((t - wt(3, 'existía') + .1) / .7)
    im = room_bg(mix(BLUE_BG[0], (150, 154, 166), gr), mix(BLUE_BG[1], (110, 114, 126), gr)); d = BD(im)
    d.rectangle((0, 1000, W, H), fill=mix((180, 160, 140), (110, 110, 116), gr))
    lx = 80 + min(1, lt / max(.1, CL[3]['d'])) * 520
    for k in range(6):
        x = 40 + k * 190; door(d, x, 640, 140, 360, col=mix((170, 118, 76), (130, 130, 136), gr))
        knock = (lx - x - 70) / 190
        if 0 < knock < .6 and gr < .5:
            bubble(im, x + 10, 560 + 10 * math.sin(t * 20), 'toc toc', knock * 3, col=(255, 255, 255), tcol=(36, 36, 40), size=26); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); laura(ImageDraw.Draw(L), lx, 860, 1.5, bob=-abs(math.sin(t * 8)) * 6, gray=gr); im.alpha_composite(L); d = BD(im)
    if gr > 0: d.text((lx, 760 - 20 * gr), '?', font=F('Inter-Black.otf', int(60 + 30 * gr)), fill=(255, 255, 255, int(255 * gr)), anchor='mm')
    im = camera(im, 1.35, lx, 820)
    obj('in', (40, 640, 180, 1000)); obj('out', (lx - 60, 760, lx + 60, 1060)); return im

def sc4(t, lt):
    im = BGR.copy(); d = BD(im); cx, cy = 360, 780
    rev = ease((t - wt(4, 'contrario')) / .7)
    spot = ease((t - wt(4, 'encontrar') + .2) / .6)
    if spot > 0: im.alpha_composite(Image.new('RGBA', (W, H), (14, 14, 22, int(170 * spot)))); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((cx - 180, cy - 220, cx + 180, cy + 260), fill=255), (255, 240, 200), 50, int(230 * spot))); d = BD(im)
    for k in range(8):
        a = k / 8 * math.tau + .2; r0, r1 = 120, 330
        x0, y0 = cx + math.cos(a) * r0, cy + math.sin(a) * r0; x1, y1 = cx + math.cos(a) * r1, cy + math.sin(a) * r1
        if rev < .5: sx, sy, ex, ey = x0, y0, x1, y1; col = (150, 150, 160)
        else: sx, sy, ex, ey = x1, y1, x0, y0; col = RED
        sc = abs(1 - rev * 2)
        mx, my = lerp(sx, ex, .5), lerp(sy, ey, .5); ex, ey = lerp(mx, ex, sc), lerp(my, ey, sc); sx, sy = lerp(mx, sx, sc), lerp(my, sy, sc)
        d.line((sx, sy, ex, ey), fill=col, width=8)
        ang = math.atan2(ey - sy, ex - sx)
        if sc > .3: d.polygon([(ex, ey), (ex - 26 * math.cos(ang - .5), ey - 26 * math.sin(ang - .5)), (ex - 26 * math.cos(ang + .5), ey - 26 * math.sin(ang + .5))], fill=col)
        if rev >= .5: building(d, x1 + math.cos(a) * 40, y1 + math.sin(a) * 40, .55)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); laura(ImageDraw.Draw(L), cx, cy - 40, 1.6); im.alpha_composite(L)
    chip(im, 360, 420, 'DEJÓ DE BUSCAR', t - wt(4, 'dejó'), col=(36, 36, 40), size=26)
    chip(im, 360, 1180, 'SE DEJÓ ENCONTRAR', t - wt(4, 'encontrar'), size=28)
    obj('in', (cx - 60, cy - 110, cx + 60, cy + 140)); obj('out', (cx - 110, cy - 150, cx + 110, cy + 150)); return im

SK = ['Contabilidad', 'Excel', 'Atención al cliente']
def profile_card(im, t, r=(70, 340, 650, 1150), ci=5):
    card(im, r, (255, 255, 255), 26); d = BD(im)
    d.rounded_rectangle((r[0], r[1], r[2], r[1] + 70), 26, fill=RED); d.rectangle((r[0], r[1] + 40, r[2], r[1] + 70), fill=RED)
    d.text(((r[0] + r[2]) / 2, r[1] + 36), 'CONTRÁTAME SUMIAGO', font=F('Inter-Black.otf', 26), fill='white', anchor='mm')
    q = ease((t - wt(5, 'foto') + .15) / .4) if ci == 5 else 1
    cx = (r[0] + r[2]) / 2
    if q > 0:
        fc = FACE_L.resize((180, 180)); m = Image.new('L', (180, 180), 0); ImageDraw.Draw(m).ellipse((0, 0, 179, 179), fill=int(255 * q)); fc.putalpha(m)
        d.ellipse((cx - 98, r[1] + 102, cx + 98, r[1] + 298), fill=(255, 255, 255)); im.alpha_composite(fc, (int(cx - 90), int(r[1] + 110))); d = BD(im)
        mask_text(im, (cx, r[1] + 340), 'Laura Gómez', F('Inter-Black.otf', 38), (30, 30, 36), q)
        mask_text(im, (cx, r[1] + 384), 'Contadora · Medellín', F('Inter-Bold.otf', 26), (120, 120, 130), q)
    q = t - wt(5, 'experiencia') if ci == 5 else 9
    for k, (a, b) in enumerate([('Auxiliar contable', '2 años'), ('Facturación', '1 año')]):
        bb = ease((q - k * .15) / .35)
        if bb > 0:
            y = r[1] + 430 + k * 66; d.rounded_rectangle((r[0] + 40, y, r[0] + 40 + (r[2] - r[0] - 80) * bb, y + 52), 14, fill=(244, 244, 247))
            if bb > .8: d.text((r[0] + 64, y + 26), a, font=F('Inter-Bold.otf', 24), fill=(40, 40, 46), anchor='lm'); d.text((r[2] - 64, y + 26), b, font=F('Inter-SemiBold.otf', 22), fill=RED, anchor='rm')
    q = t - wt(5, 'sabe') if ci == 5 else 9
    xs = [r[0] + 130, cx + 40, cx]
    for k, s_ in enumerate(SK): chip(im, [cx - 140, cx + 120, cx][k], r[1] + 620 + (k == 2) * 66, s_, q - k * .12, col=(36, 36, 40), size=22)
    return r

def sc5(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    r = profile_card(im, t)
    q = t - wt(5, 'gratis')
    if q > 0: stamp(im, 520, 1095, ['GRATIS'], RED, q, ang=-8, size=44)
    zq = ease((t - wt(5, 'experiencia') + .2) / .8)
    im = camera(im, 1.0 + .12 * zq, 360, lerp(700, 860, zq))
    obj('in', (270, 450, 450, 640)); obj('out', r); return im

def sc6(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 70))
    r = (70, 360, 650, 620); card(im, r, (255, 255, 255), 24); d = BD(im)
    d.text((110, 420), 'Teléfono', font=F('Inter-Bold.otf', 24), fill=(120, 120, 130), anchor='lm')
    hid = ease((t - wt(6, 'teléfono') - .2) / .6)
    num = '+57 300 482 1945'; msk = '+57 300 ••• ••45'
    d.text((110, 480), num if hid < .5 else msk, font=F('Inter-Black.otf', 44), fill=(30, 30, 36), anchor='lm')
    d.text((110, 560), 'Correo:  l•••••@•••••.com' if hid >= .5 else 'Correo:  laura.gomez@correo.com', font=F('Inter-SemiBold.otf', 24), fill=(120, 120, 130), anchor='lm')
    if hid > 0: L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); lock(ImageDraw.Draw(L), 590, 480, back_out(hid)); im.alpha_composite(L); d = BD(im)
    # público (bloqueado) y empresas (ven)
    q = t - wt(6, 'cualquiera')
    for k in range(4):
        a = ease((q - k * .1) / .4)
        if a > 0:
            L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), 110 + k * 70, 820, 1.0, (120, 120, 130)); L.putalpha(L.getchannel('A').point(lambda p: int(p * a * .8))); im.alpha_composite(L)
    if q > .4: d = BD(im); d.line((60, 700, 380, 960), fill=RED, width=10); d.line((60, 960, 380, 700), fill=RED, width=10)
    q = t - wt(6, 'empresas')
    if q > 0:
        b = back_out(q / .4); rr = (420, 700, 660, 980)
        card(im, (540 - 120 * b, 840 - 140 * b, 540 + 120 * b, 840 + 140 * b), (255, 255, 255), 22); d = BD(im)
        if b > .7:
            building(d, 540, 790, 1.2); d.text((540, 900), 'Empresas', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm'); d.text((540, 936), 'registradas', font=F('Inter-Black.otf', 26), fill=(30, 30, 36), anchor='mm')
            d.ellipse((610, 700, 670, 760), fill=(37, 190, 100)); d.line((626, 730, 638, 744, 656, 716), fill='white', width=6)
    pq = ease((t - wt(6, 'empresas') + .2) / .7)
    im = camera(im, 1.0 + .15 * pq, lerp(360, 520, pq), lerp(600, 840, pq))
    obj('in', r); obj('out', (420, 700, 660, 980)); return im

def sc7(t, lt):
    im = gradient((246, 246, 248), (226, 228, 234)); d = BD(im)
    chip(im, 360, 340, 'MARTES · 10:00 a. m.', t - wt(7, 'martes'), col=(36, 36, 40), size=24)
    sb = (60, 400, 660, 480); card(im, sb, (255, 255, 255), 40); d = BD(im)
    d.ellipse((90, 422, 126, 458), outline=(140, 140, 150), width=5); d.line((120, 452, 136, 468), fill=(140, 140, 150), width=6)
    typed = 'Contadora'[:int(max(0, t - wt(7, 'empresa')) * 14)]
    d.text((150, 440), typed + ('|' if int(t * 3) % 2 else ''), font=F('Inter-Bold.otf', 30), fill=(30, 30, 36), anchor='lm')
    chip(im, 220, 530, 'Contadora', t - wt(7, 'profesión'), size=22); chip(im, 400, 530, 'Medellín', t - wt(7, 'ciudad'), size=22)
    res = [('Andrés P.', 'Contador · Bogotá', (90, 110, 150)), ('Laura Gómez', 'Contadora · Medellín', None), ('Camila R.', 'Contadora · Cali', (160, 100, 120))]
    hl = ease((t - wt(7, 'ciudad') - .2) / .5); out = (60, 720, 660, 860)
    for k, (n, p, c) in enumerate(res):
        a = ease((t - wt(7, 'encontró') - k * .12) / .4)
        if a <= 0: continue
        y = 580 + k * 160 + (1 - a) * 40; rr = (60, y, 660, y + 140)
        sel = c is None
        if sel and hl > 0: im.alpha_composite(glow_layer(lambda dd: dd.rounded_rectangle(rr, 22, fill=255), RED, 24, int(200 * hl))); out = rr
        card(im, rr, (255, 255, 255), 22); d = BD(im)
        if sel: d.rounded_rectangle(rr, 22, outline=mix((255, 255, 255), RED, hl), width=5)
        if sel: fc = FACE_L.resize((96, 96)); m = Image.new('L', (96, 96), 0); ImageDraw.Draw(m).ellipse((0, 0, 95, 95), fill=255); fc.putalpha(m); im.alpha_composite(fc, (84, int(y + 22))); d = BD(im)
        else: d.ellipse((84, y + 22, 180, y + 118), fill=c)
        d.text((204, y + 52), n, font=F('Inter-Black.otf', 28), fill=(30, 30, 36), anchor='lm'); d.text((204, y + 92), p, font=F('Inter-SemiBold.otf', 22), fill=(120, 120, 130), anchor='lm')
        if sel and hl > .5: d.rounded_rectangle((500, y + 46, 640, y + 94), 22, fill=RED); d.text((570, y + 70), 'Contactar', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    pq = ease((t - wt(7, 'ciudad') - .1) / .7)
    im = camera(im, 1.0 + .2 * pq, 360, lerp(640, 800, pq))
    obj('in', sb); obj('out', out); return im

def sc8(t, lt):
    im = BGR.copy(); d = BD(im)
    pr = polaroid(im, 200, 560, 260, -6, 'Laura', FACE_L)
    def content(dd, cx, cy, w, h): pass
    q = ease(lt / .4); r = (300, 760 + (1 - q) * 60, 680, 1000 + (1 - q) * 60); card(im, r, (255, 255, 255), 24); d = BD(im)
    building(d, r[0] + 50, r[1] + 70, .6); d.text((r[0] + 90, r[1] + 50), 'Empresa', font=F('Inter-Black.otf', 24), fill=(30, 30, 36), anchor='lm'); d.text((r[0] + 90, r[1] + 80), 'Recursos Humanos', font=F('Inter-SemiBold.otf', 18), fill=(130, 130, 140), anchor='lm')
    msg = ['Hola Laura, vimos tu', 'perfil. ¿Podemos', 'hablar mañana?']
    for k, l in enumerate(msg): mask_text(im, (r[0] + 30 + d.textlength(l, font=F('Inter-SemiBold.otf', 28)) / 2, r[1] + 130 + k * 36), l, F('Inter-SemiBold.otf', 28), (40, 40, 46), (lt - .3 - k * .15) / .3)
    q = t - wt(8, 'conocían')
    if q > 0: stamp(im, 360, 1130, ['ELLOS LA BUSCARON'], RED, q, ang=-6, size=40)
    im = camera(im, 1.0 + .06 * ease(lt / 3), 400, 760)
    obj('in', (300, 760, 680, 1000)); obj('out', pr); return im

def sc9(t, lt):
    im = gradient((20, 18, 26), (6, 6, 10)); cx, cy = 360, 780
    im.alpha_composite(glow_layer(lambda dd: dd.polygon([(cx - 60, 300), (cx + 60, 300), (cx + 230, 1100), (cx - 230, 1100)], fill=255), (255, 240, 200), 40, int(200 * ease(lt / .6))))
    pr = polaroid(im, cx, cy, 300, 3, 'Laura', FACE_L)
    sparkles(im, cx, cy - 60, t, n=26, rad=260)
    q = t - wt(9, 'vean')
    if q > -.2:
        mask_text(im, (cx, 1130), 'TE FALTA QUE TE VEAN', F('Inter-Black.otf', 44), WHITE, (q + .2) / .4)
    im = camera(im, 1.0 + .1 * ease(lt / 3), cx, cy)
    obj('in', pr); obj('out', pr); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    cx, cy = 360, 700
    r = (cx - 110, cy - 130, cx + 110, cy + 130); card(im, r, (255, 255, 255), 22); d = BD(im)
    d.rounded_rectangle((r[0], r[1], r[2], r[1] + 46), 22, fill=RED); d.rectangle((r[0], r[1] + 26, r[2], r[1] + 46), fill=RED)
    d.text((cx, r[1] + 24), 'HOJA DE VIDA', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    for k in range(4): d.rounded_rectangle((r[0] + 26, r[1] + 80 + k * 36, r[2] - 26 - (k % 2) * 40, r[1] + 96 + k * 36), 6, fill=(220, 222, 230))
    q = t - wt(10, 'conoces')
    pts = [(110, 480), (610, 480), (110, 1000), (610, 1000)]; cols = [(70, 110, 170), (230, 120, 60), (60, 150, 120), (200, 170, 60)]
    for k, (px, py) in enumerate(pts):
        a = ease((q - k * .12) / .45)
        if a <= 0: continue
        d = BD(im); d.line((cx, cy, lerp(cx, px, a), lerp(cy, py, a)), fill=(255, 255, 255, 120), width=4)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); figure(ImageDraw.Draw(L), px, py - 40, 1.2, cols[k], long=k % 2 == 1); L.putalpha(L.getchannel('A').point(lambda p: int(p * a))); im.alpha_composite(L)
    chip(im, cx, 1150, 'PUBLICAR ES GRATIS', t - wt(10, 'gratis'), size=28)
    obj('in', (230, 450, 490, 1010)); obj('out', r); return im

def sc11(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    mask_text(im, (W / 2, y + 160), 'Contrátame Sumiago', F('Inter-Black.otf', 32), (30, 30, 36), ease((lt - .3) / .4))
    mask_text(im, (W / 2, y + 200), 'Publica tu hoja de vida', F('Inter-Bold.otf', 28), (90, 90, 100), ease((lt - .45) / .4))
    chip(im, W / 2, y + 252, 'GRATIS', t - wt(11, 'publica'), size=22)
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(11, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    q = t - wt(11, 'busquen')
    if q > -.3: mask_text(im, (W / 2, 760), '…te busquen a ti.', F('Inter-BlackItalic.otf', 46), WHITE, (q + .3) / .4)
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
