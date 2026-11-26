"""Día 37 — "La panadera que no sabía editar" (historia: doña Marta muestra su panadería con Videos Virales de Sumiago, sin grabarse).
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
KEY = {'marta', 'pan', 'bono', 'nunca', 'editado', 'redes', 'quién', 'tiempo', 'sola', 'videos', 'virales', 'sumiago', 'funcionando', 'tutorial', 'idea', 'historia', 'voz…', 'voz', 'crear',
       'cámara', 'grabarse', 'editar', 'vecinos', 'quinto', 'ciudad', 'video', 'falta', 'pena', 'ti', 'link', 'marketing', 'vean…', 'vean'}
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
        mask_text(im, (W // 2, 800), 'Que vean tu negocio', F('Inter-Bold.otf', 38), (60, 60, 68), a)
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx + yo, W / 2 + 250 * bx, 940 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

BGR_LIGHT = gradient((240, 242, 246), (222, 226, 234))
# ---------- objetos ----------
BREAD = (232, 186, 96)
def pandebono(d, x, y, r):
    d.ellipse((x - r, y - r * .8, x + r, y + r * .8), fill=BREAD); d.ellipse((x - r * .6, y - r * .6, x + r * .2, y - r * .1), fill=(246, 214, 140))
    for k in range(3): d.ellipse((x - r * .5 + k * r * .4, y + r * .1, x - r * .4 + k * r * .4, y + r * .2), fill=(200, 140, 60))

def bakery_bg():
    im = gradient((255, 236, 206), (240, 210, 170)); d = BD(im)
    for y in (420, 560):   # estantes con pan
        d.rectangle((40, y + 40, 680, y + 54), fill=(150, 98, 60))
        for k in range(9): pandebono(d, 80 + k * 72, y + 18, 26)
    d.rectangle((0, 300, W, 330), fill=RED); 
    for k in range(10): d.pieslice((k * 72, 300, k * 72 + 72, 370), 0, 180, fill=RED if k % 2 == 0 else (255, 255, 255))
    d.rectangle((0, 880, W, H), fill=(170, 118, 76)); d.rectangle((0, 880, W, 900), fill=(200, 150, 100))
    return im
BGB = bakery_bg()
def marta(d, x, y, s, bob=0):
    figure(d, x, y, s, (120, 90, 150), skin=(214, 168, 130), hair=(205, 205, 210), bob=bob)
    d.rounded_rectangle((x - 16 * s, y + 24 * s + bob, x + 16 * s, y + 76 * s + bob), 6 * s, fill=(250, 250, 250))   # delantal
    d.ellipse((x - 10 * s, y - 46 * s + bob, x + 10 * s, y - 28 * s + bob), fill=(205, 205, 210))                     # moño
def hijo(d, x, y, s, bob=0): figure(d, x, y, s, (60, 110, 200), skin=(200, 150, 112), hair=(30, 22, 20), bob=bob)

def vv_screen(im, cx, cy, s, tab, t, content):
    """Pantalla de Videos Virales (oscura, con pestañas)."""
    w, h = 600 * s, 820 * s; r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    card(im, r, (18, 18, 22), 26); d = BD(im)
    d.text((r[0] + 30, r[1] + 44), 'VIDEOS VIRALES', font=F('Inter-Black.otf', int(28 * s)), fill='white', anchor='lm')
    d.rectangle((r[0] + 30, r[1] + 66, r[0] + 120, r[1] + 70), fill=RED)
    tabs = ['Estudio', 'Ideas', 'Voces', 'Mis videos']; x = r[0] + 30
    for k, tb in enumerate(tabs):
        f = F('Inter-Bold.otf', int(20 * s)); tw = d.textlength(tb, font=f) + 28
        on = tb == tab; d.rounded_rectangle((x, r[1] + 92, x + tw, r[1] + 132), 20, fill=RED if on else (40, 40, 48)); d.text((x + tw / 2, r[1] + 112), tb, font=f, fill='white', anchor='mm'); x += tw + 10
    content(d, r)
    return r

# ---------- escenas ----------
def sc0(t, lt):
    im = BGB.copy(); d = BD(im)
    d.rectangle((60, 760, 660, 900), fill=(200, 150, 100)); d.rectangle((60, 760, 660, 780), fill=(230, 190, 140))
    for k in range(6): pandebono(d, 140 + k * 90, 740, 30)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); marta(ImageDraw.Draw(L), 360, 600, 1.7, bob=-abs(math.sin(t * 3)) * 3); im.alpha_composite(L)
    chip(im, 560, 420, 'EL MEJOR PAN DE BONO', t - wt(0, 'mejor'), size=20)
    q = t - wt(0, 'editado')
    if q > 0: stamp(im, 360, 1040, ['0 VIDEOS EDITADOS'], RED, q, ang=-5, size=40)
    im = camera(im, lerp(1.25, 1.0, ease(lt / 3)), 360, 700)
    obj('in', (260, 480, 460, 900)); obj('out', (260, 480, 460, 900)); return im

def sc1(t, lt):
    im = BGB.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); marta(dl, 180, 700, 1.6); hijo(dl, 540, 690, 1.7); im.alpha_composite(L)
    bubble(im, 300, 430, 'Mamá, hay que subir videos', t - wt(1, 'mamá'), col=(60, 110, 200), size=26)
    bubble(im, 60, 1000, '¿Y quién los hace?', t - wt(1, 'quién') + .1, col=(255, 255, 255), tcol=(36, 36, 40), size=30)
    fq = ease((t - wt(1, 'contestó')) / .5)
    im = camera(im, 1.1, lerp(470, 250, fq), lerp(700, 800, fq))
    obj('in', (260, 480, 460, 900)); obj('out', (60, 1000, 420, 1080)); return im

def sc2(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    # reloj del hijo sin tiempo
    cx, cy = 230, 560; d.ellipse((cx - 120, cy - 120, cx + 120, cy + 120), fill=(255, 255, 255), outline=(36, 36, 40), width=10)
    a = t * 6; d.line((cx, cy, cx + math.cos(a) * 90, cy + math.sin(a) * 90), fill=RED, width=8); d.line((cx, cy, cx + math.cos(a / 12) * 60, cy + math.sin(a / 12) * 60), fill=(36, 36, 40), width=10)
    chip(im, 230, 730, 'SIN TIEMPO', t - wt(2, 'tiempo'), col=(36, 36, 40), size=24)
    q = t - wt(2, 'sola')
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); marta(ImageDraw.Draw(L), 500, 760, 1.6); im.alpha_composite(L); d = BD(im)
    lr = (390, 920, 610, 1060)
    if q > -.3:
        a = ease((q + .3) / .4); d.rounded_rectangle((500 - 110 * a, 990 - 70 * a, 500 + 110 * a, 990 + 70 * a), 12, fill=(40, 42, 50))
        if a > .8: d.rounded_rectangle((404, 934, 596, 1046), 8, fill=(245, 247, 250)); d.rectangle((404, 934, 596, 954), fill=RED)
        chip(im, 500, 1110, 'LO INTENTÓ SOLA', q, size=24)
    obj('in', (60, 1000, 420, 1080)); obj('out', lr); return im

IDEAS = [('Así hago 200 panes antes del amanecer', '1,2 M'), ('El secreto de la abuela', '860 mil'), ('Lo que nadie ve de una panadería', '2,4 M')]
def sc3(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    def content(d, r):
        q0 = t - wt(3, 'ideas')
        for k, (tit, vis) in enumerate(IDEAS):
            a = ease((q0 - k * .18) / .4)
            if a <= 0: continue
            y = r[1] + 170 + k * 170 + (1 - a) * 40
            d.rounded_rectangle((r[0] + 30, y, r[2] - 30, y + 150), 18, fill=(34, 36, 46))
            d.rounded_rectangle((r[0] + 46, y + 16, r[0] + 150, y + 134), 12, fill=(70, 50, 40)); pandebono(d, r[0] + 98, y + 75, 30)
            d.text((r[0] + 170, y + 50), tit[:24], font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
            if len(tit) > 24: d.text((r[0] + 170, y + 78), tit[24:], font=F('Inter-Bold.otf', 22), fill='white', anchor='lm')
            d.rounded_rectangle((r[0] + 170, y + 100, r[0] + 330, y + 132), 16, fill=RED); d.text((r[0] + 250, y + 116), '🔥 ' [:0] + vis + ' vistas', font=F('Inter-Black.otf', 18), fill='white', anchor='mm')
    r = vv_screen(im, 360, 760, 1.0, 'Ideas', t, content)
    q = t - wt(3, 'funcionando')
    if q > 0: stamp(im, 470, 1210, ['YA FUNCIONAN'], RED, q, ang=-6, size=40)
    fq = ease((t - wt(3, 'ideas') + .2) / .9)
    im = camera(im, 1.0 + .1 * fq, 360, lerp(700, 860, fq))
    obj('in', (390, 920, 610, 1060)); obj('out', (90, 690, 630, 840)); return im

def sc4(t, lt):
    im = gradient((40, 22, 24), (14, 10, 14)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 400, 820, 1200), fill=255), RED, 140, 90))
    steps = [('tutorial', '1. Tutorial', 'Conecta tu voz'), ('idea', '2. Idea', 'Lo que nadie ve de una panadería'), ('historia', '3. Guion', 'Mi mamá empezó con un horno…'), ('voz', '4. Voz', 'Narrador cálido')]
    out = [None]
    def content(d, r):
        for k, (w_, a1, a2) in enumerate(steps):
            q = ease((t - wt(4, w_) + .1) / .35)
            if q <= 0: continue
            y = r[1] + 160 + k * 112
            d.rounded_rectangle((r[0] + 30, y, r[0] + 30 + (r[2] - r[0] - 60) * q, y + 96), 16, fill=(34, 36, 46))
            if q > .8:
                d.text((r[0] + 54, y + 32), a1, font=F('Inter-Black.otf', 22), fill=RED, anchor='lm')
                txt = a2 if w_ != 'historia' else a2[:max(0, int((t - wt(4, w_)) * 22))]
                d.text((r[0] + 54, y + 68), txt, font=F('Inter-SemiBold.otf', 22), fill=(210, 210, 220), anchor='lm')
                d.ellipse((r[2] - 80, y + 30, r[2] - 44, y + 66), fill=GREEN_OK); d.line((r[2] - 72, y + 48, r[2] - 64, y + 58, r[2] - 50, y + 38), fill='white', width=4)
        q = t - wt(4, 'crear')
        b = back_out(q / .35)
        if b > 0:
            cy = r[3] - 90; bw = 200 * b; gl = 1 + .05 * math.sin(t * 9)
            d.rounded_rectangle((W / 2 - bw * gl, cy - 40 * b, W / 2 + bw * gl, cy + 40 * b), 40, fill=RED)
            if b > .6: d.text((W / 2, cy), '¡CREAR VIDEO!', font=F('Inter-Black.otf', 30), fill='white', anchor='mm')
            out[0] = (W / 2 - 200, cy - 40, W / 2 + 200, cy + 40)
            if q > .3:
                p = min(1, (q - .3) / 1.2); d.rounded_rectangle((r[0] + 60, cy - 90, r[2] - 60, cy - 70), 10, fill=(50, 50, 60)); d.rounded_rectangle((r[0] + 60, cy - 90, r[0] + 60 + (r[2] - r[0] - 120) * p, cy - 70), 10, fill=GREEN_OK)
    r = vv_screen(im, 360, 760, 1.0, 'Estudio', t, content)
    tq = t - wt(4, 'crear') - .15
    if 0 < tq < .5: d = BD(im); rr = 20 + tq * 140; d.ellipse((W / 2 - rr, r[3] - 90 - rr, W / 2 + rr, r[3] - 90 + rr), outline=(255, 255, 255, int(255 * (1 - tq / .5))), width=5)
    fq = ease((t - wt(4, 'crear') + .2) / .6)
    im = camera(im, 1.0 + .2 * fq, 360, lerp(760, 1000, fq))
    obj('in', (90, 690, 630, 840)); obj('out', out[0] or (160, 1040, 560, 1120)); return im
GREEN_OK = (37, 190, 100)

def sc5(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 90)); d = BD(im)
    items = [('cámara', 'Cámara'), ('grabarse', 'Grabarse'), ('editar', 'Editar')]
    for k, (w_, lab) in enumerate(items):
        q = t - wt(5, w_) + .1
        a = back_out(q / .35)
        if a <= 0: continue
        cx, cy = 360, 470 + k * 240; rr = 90 * a
        d.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), fill=(245, 243, 236))
        if a > .7:
            if k == 0: d.rounded_rectangle((cx - 44, cy - 28, cx + 22, cy + 28), 8, fill=(40, 40, 48)); d.polygon([(cx + 22, cy - 8), (cx + 48, cy - 24), (cx + 48, cy + 24), (cx + 22, cy + 8)], fill=(40, 40, 48))
            elif k == 1: d.ellipse((cx - 24, cy - 24, cx + 24, cy + 24), fill=RED); d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), outline=(40, 40, 48), width=6)
            else:
                for j in range(3): d.rounded_rectangle((cx - 50 + j * 36, cy - 30 + (j % 2) * 20, cx - 22 + j * 36, cy + 10 + (j % 2) * 20), 6, fill=(40, 40, 48))
            sl = ease((q - .2) / .3); d.line((cx - 70, cy + 70, cx - 70 + 140 * sl, cy + 70 - 140 * sl), fill=RED, width=12)
            d.text((cx + 130, cy), 'Sin ' + lab.lower(), font=F('Inter-Black.otf', 34), fill='white', anchor='lm')
    obj('in', (290, 400, 430, 540)); obj('out', (290, 880, 430, 1020)); return im

def sc6(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    for k in range(8): d.line((0, 330 + k * 120, W, 300 + k * 120), fill=(255, 255, 255), width=12)
    home = (360, 820); d.ellipse((home[0] - 40, home[1] - 40, home[0] + 40, home[1] + 40), fill=RED); pandebono(d, home[0], home[1], 20)
    q1 = t - wt(6, 'primer')
    rr = random.Random(2)
    for k in range(7):
        a = ease((q1 - k * .08) / .4)
        if a > 0:
            ang = k / 7 * math.tau; x = home[0] + math.cos(ang) * 150 * a; y = home[1] + math.sin(ang) * 130 * a
            d.ellipse((x - 14, y - 14, x + 14, y + 14), fill=(60, 110, 200))
    chip(im, 360, 600, 'VECINOS', q1, col=(60, 110, 200), size=22)
    q = t - wt(6, 'quinto')
    far = (580, 400)
    if q > 0:
        p = ease(q / .8); x = lerp(home[0], far[0], p); y = lerp(home[1], far[1], p) - math.sin(math.pi * p) * 120
        d.line((home[0], home[1], x, y), fill=RED, width=5)
        if p > .95:
            d.ellipse((far[0] - 30, far[1] - 30, far[0] + 30, far[1] + 30), fill=(36, 36, 40)); chip(im, far[0] - 60, far[1] - 70, 'OTRA CIUDAD', q - .8, size=22)
    vis = int(lerp(38, 4700, ease(max(0, t - wt(6, 'quinto')) / 2)))
    r = (60, 1040, 360, 1170); card(im, r, (255, 255, 255), 20); d = BD(im)
    d.text((210, 1076), 'Vistas', font=F('Inter-Bold.otf', 20), fill=(120, 120, 130), anchor='mm'); d.text((210, 1128), f'{vis:,}'.replace(',', '.'), font=F('Inter-Black.otf', 44), fill=RED, anchor='mm')
    fq = ease((t - wt(6, 'quinto')) / .9)
    im = camera(im, 1.12, lerp(360, 480, fq), lerp(820, 560, fq))
    obj('in', (300, 760, 420, 880)); obj('out', (500, 330, 660, 470)); return im

def sc7(t, lt):
    im = BGB.copy(); d = BD(im)
    d.rectangle((60, 760, 660, 900), fill=(200, 150, 100)); d.rectangle((60, 760, 660, 780), fill=(230, 190, 140))
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); marta(dl, 200, 600, 1.5)
    cols = [(230, 120, 60), (60, 150, 120), (160, 100, 160)]
    for k in range(3):
        a = ease((lt - .2 - k * .25) / .6); figure(dl, lerp(W + 80, 420 + k * 100, a), 900 + (k % 2) * 10, 1.5, cols[k], long=k % 2 == 0, bob=-abs(math.sin(t * 9 + k)) * 5 * (1 - a))
    im.alpha_composite(L)
    bubble(im, 300, 700, '¡La vi en un video!', t - wt(7, 'vi') + .1, col=RED, size=32)
    obj('in', (300, 700, 680, 780)); obj('out', (130, 500, 280, 880)); return im

def sc8(t, lt):
    im = BGB.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 90))); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); marta(ImageDraw.Draw(L), 360, 640, 2.0, bob=-abs(math.sin(t * 2)) * 4); im.alpha_composite(L)
    q = t - wt(8, 'editar')
    if q > 0: chip(im, 360, 420, 'SIGUE SIN SABER EDITAR', q, col=(36, 36, 40), size=26)
    q = t - wt(8, 'falta')
    if q > 0: stamp(im, 360, 1080, ['Y NO LE HACE FALTA'], RED, q, ang=-5, size=44)
    sparkles(im, 360, 640, t, n=16, rad=220)
    obj('in', (260, 520, 460, 960)); obj('out', (260, 520, 460, 960)); return im

def sc9(t, lt):
    im = BGR_LIGHT.copy(); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); figure(dl, 360, 700, 2.0, (90, 90, 100)); im.alpha_composite(L); d = BD(im)
    q = ease((t - wt(9, 'pena')) / .4)
    if q > 0:   # manos tapando la cara
        for sx in (-1, 1): d.ellipse((360 + sx * 16 - 22, 680 - 26 + (1 - q) * 160, 360 + sx * 16 + 22, 680 + 26 + (1 - q) * 160), fill=(214, 168, 128), outline=(180, 130, 100), width=2)
        d.text((470, 560), '//', font=F('Inter-Black.otf', 40), fill=RED, anchor='mm')
    chip(im, 360, 1060, 'NEGOCIO', t - wt(9, 'negocio'), col=(36, 36, 40), size=24)
    q = t - wt(9, 'ti', 1)
    if q > 0: stamp(im, 360, 420, ['ESTO ES PARA TI'], RED, q, ang=-6, size=46)
    obj('in', (260, 520, 460, 960)); obj('out', (100, 360, 620, 480)); return im

def sc10(t, lt):
    im = gradient((34, 8, 12), (8, 6, 10)); d = BD(im)
    im.alpha_composite(glow_layer(lambda dd: dd.ellipse((-100, 300, 820, 1200), fill=255), RED, 120, 110)); d = BD(im)
    a = ease(lt / .4); y = 330 + (1 - a) * 40
    d.rounded_rectangle((60, y, 660, y + 300), 26, fill=(250, 250, 250, int(255 * a)))
    if a > .3: im.alpha_composite(LOGO_S, (int(W / 2 - LOGO_S.width / 2), int(y + 26))); d = BD(im)
    chip(im, 220, y + 175, 'VIDEOS VIRALES', t - wt(10, 'virales'), size=24)
    chip(im, 500, y + 175, 'GANA CON MARKETING', t - wt(10, 'marketing'), col=(36, 36, 40), size=20)
    mask_text(im, (W / 2, y + 245), 'Crea videos sin grabarte', F('Inter-Bold.otf', 28), (90, 90, 100), ease((lt - .45) / .4))
    m = M_PUL; bob = math.sin(t * 5) * 6 if LV[min(int(t * FPS), len(LV) - 1)] > .03 else 0
    ma = ease((lt - .2) / .5); im.alpha_composite(m, (int(-20 - (1 - ma) * 300), int(H - m.height + 40 + bob))); d = BD(im)
    q = t - wt(10, 'link')
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 500, 1000
        d.rounded_rectangle((cx - 190 * bx * b, cy - 42 * bx * b, cx + 190 * bx * b, cy + 42 * bx * b), 42, fill=(255, 255, 255))
        if b > .5: d.text((cx, cy), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=RED, anchor='mm')
        ay = cy + 70 + 10 * math.sin(t * 8); d.polygon([(cx - 24, ay), (cx + 24, ay), (cx, ay + 34)], fill='white')
    CAM.update(x0=0, y0=0, z=1); obj('in', (100, 360, 620, 480)); obj('out', (60, 330, 660, 630))
    return im

def sc11(t, lt):
    im = BGB.copy(); im.alpha_composite(Image.new('RGBA', (W, H), (20, 8, 10, 120))); d = BD(im)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); phone(L, 360, 780, 1.0, None); im.alpha_composite(L); d = BD(im)
    d.rectangle((222, 500, 498, 1060), fill=(255, 236, 206)); 
    for k in range(4): pandebono(d, 270 + (k % 2) * 180, 640 + (k // 2) * 140, 40)
    d.rounded_rectangle((240, 950, 480, 1000), 20, fill=RED); d.text((360, 975), 'Panadería Marta', font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    q = t - wt(11, 'vean')
    if q > 0:
        for k in range(5): x = 120 + k * 120; hq = back_out((q - k * .08) / .35); d.ellipse((x - 22 * hq, 1210 - 22 * hq, x + 22 * hq, 1210 + 22 * hq), fill=RED)
    q = t - wt(11, 'cámara')
    if q > -.3: mask_text(im, (W / 2, 1130), 'aunque no salgas en cámara', F('Inter-BlackItalic.otf', 38), WHITE, (q + .3) / .4)
    im = camera(im, 1.0 + .08 * ease(lt / 3), 360, 780)
    obj('in', (60, 330, 660, 630)); obj('out', (222, 500, 498, 1060)); return im

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
