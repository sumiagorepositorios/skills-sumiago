"""Video del Día 6: "Cómo registrarte y publicar en el Marketplace" (tutorial paso a paso, fondo blanco, 64 s).
Uso (en tu carpeta de trabajo, después de voz.py):
    python scripts/render.py still 40 prueba.png         -> un cuadro de muestra en el segundo 40
    set OUTW=1080 & set ODIR=out1080
    python scripts/render.py 0   (y 1, 2, 3, 4, 5)        -> una escena por comando: a_intro, b_reg, c_ver, d_panel, e_mk, f_outro
"""
import sys, math, os, subprocess
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
import numpy as np

S = 2
W, H = 720, 1280
FPS = 30
OUTW = int(os.environ.get('OUTW', 720)); OUTH = OUTW * 16 // 9
_AQUI = os.path.dirname(os.path.abspath(__file__))
AS = os.path.join(_AQUI, '..', 'assets') + os.sep
FD = os.path.join(_AQUI, '..', 'fonts', 'DMSans.ttf')
FS = os.path.join(_AQUI, '..', 'fonts', 'CrimsonText-SemiBoldItalic.ttf')
RED = (225, 6, 0); RED2 = (214, 6, 0)
BG = (247, 247, 249); CARD = (255, 255, 255); BORDER = (224, 224, 229)
FIELD = (246, 246, 248); GRAY = (104, 104, 112); DIM = (160, 160, 168)
WHITE = (255, 255, 255); ITEM = (243, 243, 245); INK = (20, 20, 24)


@lru_cache(None)
def F(size, w=400):
    f = ImageFont.truetype(FD, int(size * S))
    f.set_variation_by_axes([min(max(size, 9), 40), w])
    return f


@lru_cache(None)
def FSer(size):
    return ImageFont.truetype(FS, int(size * S))


def cl(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    if b <= a:
        return 1.0 if t >= a else 0.0
    return cl((t - a) / (b - a))


def eo(x):
    x = cl(x); return 1 - (1 - x) ** 3


def eio(x):
    x = cl(x); return 3 * x * x - 2 * x * x * x


def col(c, a):
    base = c[3] / 255 if len(c) > 3 else 1
    return (c[0], c[1], c[2], int(255 * cl(a * base)))


class D:
    def __init__(self, im, ox=0, oy=0):
        self.im = im; self.d = ImageDraw.Draw(im, 'RGBA'); self.ox = ox; self.oy = oy

    def P(self, x, y):
        return ((x - self.ox) * S, (y - self.oy) * S)

    def rr(self, x, y, w, h, r, fill=None, outline=None, width=1, a=1.0):
        if a <= 0.003: return
        x0, y0 = self.P(x, y)
        self.d.rounded_rectangle([x0, y0, x0 + w * S, y0 + h * S], radius=r * S,
                                 fill=col(fill, a) if fill else None,
                                 outline=col(outline, a) if outline else None, width=int(width * S))

    def circ(self, x, y, r, fill=None, outline=None, width=1, a=1.0):
        if a <= 0.003: return
        cx, cy = self.P(x, y)
        self.d.ellipse([cx - r * S, cy - r * S, cx + r * S, cy + r * S],
                       fill=col(fill, a) if fill else None,
                       outline=col(outline, a) if outline else None, width=int(width * S))

    def line(self, pts, c, w=2, a=1.0):
        if a <= 0.003: return
        self.d.line([self.P(x, y) for x, y in pts], fill=col(c, a), width=int(w * S), joint='curve')

    def arc(self, x, y, r, a0, a1, c, w=3, a=1.0):
        cx, cy = self.P(x, y)
        self.d.arc([cx - r * S, cy - r * S, cx + r * S, cy + r * S], a0, a1, fill=col(c, a), width=int(w * S))

    def t(self, x, y, s, f, c=INK, a=1.0, anchor='la'):
        if a <= 0.003 or not s: return
        self.d.text(self.P(x, y), s, font=f, fill=col(c, a), anchor=anchor)

    def img(self, im, x, y, a=1.0):
        if a <= 0.003: return
        px, py = self.P(x, y)
        if a < 0.999:
            al = im.getchannel('A').point(lambda v: int(v * a))
            self.im.paste(im, (int(px), int(py)), al)
        else:
            self.im.paste(im, (int(px), int(py)), im)


def tw(s, f):
    return f.getlength(s) / S


# ---------- assets ----------
@lru_cache(None)
def asset(name, h=None, w=None):
    im = Image.open(AS + name).convert('RGBA')
    im = im.crop(im.getbbox())
    if h: im = im.resize((int(im.width * h / im.height * S), int(h * S)), Image.LANCZOS)
    elif w: im = im.resize((int(w * S), int(im.height * w / im.width * S)), Image.LANCZOS)
    return im


@lru_cache(None)
def photo(kind, size):
    n = int(size * S)
    g = np.linspace(0, 1, n)[:, None]
    arr = np.zeros((n, n, 3), np.float32)
    top = np.array([236, 236, 240]); bot = np.array([196, 196, 204])
    arr[:] = (top * (1 - g) + bot * g)[:, None, :][:, 0][:, None, :]
    im = Image.fromarray(arr.astype(np.uint8)).convert('RGBA')
    d = ImageDraw.Draw(im, 'RGBA')
    u = n / 100
    # shadow
    d.ellipse([30 * u, 86 * u, 70 * u, 92 * u], fill=(0, 0, 0, 50))
    d.rounded_rectangle([33 * u, 12 * u, 67 * u, 88 * u], radius=7 * u, fill=(28, 28, 32, 255))
    if kind == 1:
        # screen
        sc = Image.new('RGBA', (int(30 * u), int(72 * u)))
        sa = np.zeros((sc.height, sc.width, 4), np.uint8)
        gg = np.linspace(0, 1, sc.height)[:, None]
        sa[..., 0] = (225 * (1 - gg) + 40 * gg).astype(np.uint8)
        sa[..., 1] = (20 * (1 - gg) + 10 * gg).astype(np.uint8)
        sa[..., 2] = (30 * (1 - gg) + 20 * gg).astype(np.uint8)
        sa[..., 3] = 255
        sc = Image.fromarray(sa)
        m = Image.new('L', sc.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sc.width - 1, sc.height - 1], radius=5 * u, fill=255)
        im.paste(sc, (int(35 * u), int(14 * u)), m)
        d.rounded_rectangle([44 * u, 16 * u, 56 * u, 19.5 * u], radius=2 * u, fill=(10, 10, 12, 255))
        d.ellipse([42 * u, 40 * u, 58 * u, 56 * u], outline=(255, 255, 255, 200), width=int(1.4 * u))
    else:
        d.rounded_rectangle([37 * u, 16 * u, 53 * u, 34 * u], radius=4 * u, fill=(48, 48, 54, 255))
        for cx, cy in [(41.5, 21), (48.5, 21), (41.5, 29)]:
            d.ellipse([(cx - 3) * u, (cy - 3) * u, (cx + 3) * u, (cy + 3) * u], fill=(12, 12, 14, 255), outline=(90, 90, 96, 255), width=max(1, int(0.6 * u)))
        d.ellipse([47 * u, 27.5 * u, 50 * u, 30.5 * u], fill=(240, 230, 200, 255))
        d.ellipse([45 * u, 52 * u, 55 * u, 62 * u], outline=(70, 70, 76, 255), width=int(1 * u))
    return im


def rounded(im, r):
    m = Image.new('L', im.size, 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=r * S, fill=255)
    out = im.copy(); out.putalpha(m); return out


@lru_cache(None)
def photo_r(kind, size, r):
    return rounded(photo(kind, size), r)


@lru_cache(None)
def photo_rect(kind, w, h, r):
    p = photo(kind, max(w, h)).resize((int(max(w, h) * S), int(max(w, h) * S)))
    left = (p.width - int(w * S)) // 2; top = (p.height - int(h * S)) // 2
    p = p.crop((left, top, left + int(w * S), top + int(h * S)))
    return rounded(p, r)


def make_bg():
    w, h = W * S, H * S
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    img = np.zeros((h, w, 3), np.float32) + np.array(BG, np.float32)
    grid = ((xx % (48 * S) < S) | (yy % (48 * S) < S)).astype(np.float32)
    fade = np.clip(1 - np.abs(yy / h - 0.45) * 1.4, 0, 1)
    img -= grid[..., None] * fade[..., None] * np.array([12, 12, 12], np.float32)
    d = np.sqrt(((xx - w * 0.5) / (w * 0.75)) ** 2 + ((yy - h * 0.28) / (h * 0.32)) ** 2)
    glow = np.clip(1 - d, 0, 1) ** 2
    img -= glow[..., None] * np.array([0, 26, 26], np.float32)
    v = np.clip((yy / h - 0.72) / 0.28, 0, 1)
    img -= 0 * v[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


BGIM = None

# ---------- widgets ----------

def card(d, x, y, w, h, a=1.0, glow=False):
    if glow:
        for i in range(4, 0, -1):
            d.rr(x - i * 3, y - i * 3, w + i * 6, h + i * 6, 26 + i * 3, fill=RED, a=a * 0.035)
    for i in range(3, 0, -1):
        d.rr(x - i * 2, y - i * 2 + 6, w + i * 4, h + i * 4, 26 + i * 2, fill=(0, 0, 0), a=a * 0.025)
    d.rr(x, y, w, h, 26, fill=CARD, outline=RED if glow else BORDER, width=1.5 if glow else 1, a=a)


def typed(s, t, a, b):
    return s[:int(round(len(s) * prog(t, a, b)))]


def chevron(d, x, y, a=1.0):
    d.line([(x - 7, y - 4), (x, y + 3), (x + 7, y - 4)], GRAY, 2.5, a)


def lock(d, x, y, a=1.0, c=GRAY):
    d.rr(x - 8, y - 2, 16, 13, 3, fill=c, a=a)
    d.arc(x, y - 3, 5.5, 180, 360, c, 2.4, a)
    d.line([(x - 5.5, y - 3), (x - 5.5, y - 1)], c, 2.4, a)
    d.line([(x + 5.5, y - 3), (x + 5.5, y - 1)], c, 2.4, a)


def check(d, x, y, s, c=WHITE, w=4, a=1.0, p=1.0):
    pts = [(x - s * 0.5, y), (x - s * 0.15, y + s * 0.35), (x + s * 0.55, y - s * 0.4)]
    if p < 1:
        L1 = math.dist(pts[0], pts[1]); L2 = math.dist(pts[1], pts[2]); L = (L1 + L2) * p
        if L <= L1:
            k = L / L1; pts = [pts[0], (pts[0][0] + (pts[1][0] - pts[0][0]) * k, pts[0][1] + (pts[1][1] - pts[0][1]) * k)]
        else:
            k = (L - L1) / L2; pts = [pts[0], pts[1], (pts[1][0] + (pts[2][0] - pts[1][0]) * k, pts[1][1] + (pts[2][1] - pts[1][1]) * k)]
    if p > 0.01: d.line(pts, c, w, a)


def flag_co(d, x, y, a=1.0):
    d.rr(x, y, 30, 20, 3, fill=(252, 209, 22), a=a)
    d.d.rectangle([*d.P(x, y + 10), *d.P(x + 30, y + 15)], fill=col((0, 56, 147), a))
    d.d.rectangle([*d.P(x, y + 15), *d.P(x + 30, y + 20)], fill=col((206, 17, 38), a))


def spinner(d, x, y, r, t, c=WHITE, a=1.0):
    a0 = (t * 520) % 360
    d.arc(x, y, r, a0, a0 + 270, c, 3.5, a)


def field(d, x, y, w, label, value, t, ts, te, a=1.0, pwd=False, h=60, ph='', hold=0.35, right=None, select=False, help=None, wrap=False):
    d.t(x, y, label, F(19, 500), GRAY, a)
    by = y + 30
    foc = ts - 0.25 <= t <= te + hold
    d.rr(x, by, w, h, 14, fill=FIELD, outline=RED if foc else BORDER, width=2 if foc else 1, a=a)
    shown = typed(value, t, ts, te)
    if pwd: shown = '•' * len(shown)
    f = F(25, 500)
    pad = 20
    if right == 'flag' and shown:
        flag_co(d, x + pad, by + h / 2 - 10, a); pad += 42
    if wrap:
        lines = []; cur = ''
        for wd in shown.split(' '):
            tst = (cur + ' ' + wd).strip()
            if tw(tst, f) > w - 40 and cur:
                lines.append(cur); cur = wd
            else: cur = tst
        lines.append(cur)
        for i, ln in enumerate(lines):
            d.t(x + pad, by + 18 + i * 36, ln, f, INK, a)
        if not shown and ph: d.t(x + pad, by + 18, ph, f, DIM, a)
        if foc and int(t * 2.6) % 2 == 0:
            cx = x + pad + tw(lines[-1], f) + 3; cy = by + 18 + (len(lines) - 1) * 36
            d.line([(cx, cy + 2), (cx, cy + 30)], RED2, 2.5, a)
    else:
        cy = by + h / 2
        if shown:
            d.t(x + pad, cy, shown, f, INK, a, 'lm')
        elif ph:
            d.t(x + pad, cy, ph, f, DIM, a, 'lm')
        if foc and not select and int(t * 2.6) % 2 == 0:
            cx = x + pad + (tw(shown, f) if shown else 0) + 3
            d.line([(cx, cy - 15), (cx, cy + 15)], RED2, 2.5, a)
    if select: chevron(d, x + w - 26, by + h / 2, a)
    if right == 'lock': lock(d, x + w - 28, by + h / 2 - 3, a)
    ny = by + h + 16
    if help:
        d.t(x, ny - 6, help, F(17, 400), DIM, a); ny += 22
    return ny


def button(d, x, y, w, h, text, t, ttap=None, a=1.0, style='red', fsize=24, loading=None, glow=False):
    k = 1.0
    if ttap is not None and ttap - 0.04 <= t <= ttap + 0.18:
        k = 1 - 0.05 * math.sin(math.pi * prog(t, ttap - 0.04, ttap + 0.18))
    cx, cy = x + w / 2, y + h / 2
    ww, hh = w * k, h * k
    if style == 'red':
        if glow:
            for i in range(3, 0, -1):
                d.rr(cx - ww / 2 - i * 4, cy - hh / 2 - i * 4, ww + i * 8, hh + i * 8, 16 + i * 4, fill=RED, a=a * 0.06)
        d.rr(cx - ww / 2, cy - hh / 2, ww, hh, 16, fill=RED, a=a)
        tc = WHITE
    else:
        d.rr(cx - ww / 2, cy - hh / 2, ww, hh, 16, fill=(240, 240, 243), outline=BORDER, a=a)
        tc = INK
    if loading is not None and loading > 0:
        spinner(d, cx, cy, 13, t, WHITE, a * loading)
        d.t(cx, cy, text, F(fsize * k, 700), tc, a * (1 - loading), 'mm')
    else:
        d.t(cx, cy, text, F(fsize * k, 700), tc, a, 'mm')


def tapfx(d, x, y, t, t0, a=1.0):
    if t0 - 0.32 <= t <= t0 + 0.55:
        if t <= t0 + 0.12:
            p = prog(t, t0 - 0.32, t0 - 0.12)
            d.circ(x, y, 20, fill=(20, 20, 24), a=a * 0.38 * p)
            d.circ(x, y, 20, outline=(20, 20, 24), width=2, a=a * 0.6 * p)
        if t >= t0:
            p = prog(t, t0, t0 + 0.55)
            d.circ(x, y, 20 + 34 * eo(p), outline=(20, 20, 24), width=3, a=a * 0.7 * (1 - p))


def success(d, cx, cy, t, t0, title, sub, a=1.0):
    p = eo(prog(t, t0, t0 + 0.35))
    r = 64 * (0.6 + 0.4 * p) + 6 * math.sin(math.pi * prog(t, t0, t0 + 0.5))
    for i in range(4, 0, -1):
        d.circ(cx, cy, r + i * 10, fill=RED, a=a * p * 0.05)
    d.circ(cx, cy, r, fill=RED, a=a * p)
    check(d, cx, cy + 2, 56, WHITE, 7, a * p, prog(t, t0 + 0.15, t0 + 0.5))
    d.t(cx, cy + 120, title, F(36, 700), INK, a * eo(prog(t, t0 + 0.25, t0 + 0.6)), 'mm')
    d.t(cx, cy + 166, sub, F(22, 400), GRAY, a * eo(prog(t, t0 + 0.35, t0 + 0.7)), 'mm')


# ---------- captions ----------
import json as _j
VO = 0.05
try: VD = _j.load(open(os.path.join('vo', 'dur.json')))
except Exception: VD = None
CAPS = [
    (0.2, 2.45, 'Oye, te voy a enseñar a *vender* en Sumiago'),
    (2.45, 5.2, 'es muy *sencillo*'),
    (5.3, 8.0, 'Entra a *sumiago.com* y toca Crear cuenta'),
    (8.0, 10.6, 'Escribe tu *usuario,* nombre y apellido'),
    (10.6, 13.4, 'acepta los términos y dale *Siguiente*'),
    (13.6, 16.4, 'Pon tu *correo* y tu país'),
    (16.4, 19.9, 'agrega tu *WhatsApp* para que te contacten'),
    (20.1, 22.6, 'Crea una *contraseña* segura'),
    (22.6, 25.4, 'y toca *Crear mi cuenta*'),
    (25.6, 28.4, 'Te llega un *código* a tu correo'),
    (28.4, 31.9, 'escríbelo y tu cuenta queda *verificada*'),
    (32.1, 34.4, 'Ya dentro, abre el *Marketplace*'),
    (34.4, 36.9, 'y toca *Publicar*'),
    (37.1, 39.3, 'Sube las *fotos* de tu artículo'),
    (39.3, 42.3, 'ponle un *título* y elige la categoría'),
    (42.3, 44.6, 'pon el *precio* y el estado'),
    (44.6, 48.9, 'agrega una *descripción,* tu ciudad y WhatsApp'),
    (49.1, 52.1, 'Toca *Publicar* y queda en línea al instante'),
    (52.1, 55.4, 'compártelo por *WhatsApp* con vista previa'),
    (55.6, 58.7, 'Tu primer artículo es *gratis*'),
    (58.7, 60.9, 'con membresía publicas *hasta 5*'),
    (61.0, 63.9, '*Síguenos* para más tutoriales'),
]


def parse(text):
    out = []; acc = False
    for wd in text.split(' '):
        st = wd.startswith('*'); en = wd.endswith('*') or wd.rstrip(',.').endswith('*')
        w = wd.replace('*', '')
        if st: acc = True
        out.append((w, acc))
        if en and acc: acc = False
    return out


def captions(d, tg):
    for a, b, text in CAPS:
        if not (a - 0.05 <= tg <= b + 0.12): continue
        words = parse(text)
        n = len(words)
        ci = [c[2] for c in CAPS].index(text)
        vd = VD[ci] if VD else 0.72 * (b - a)
        lens = [len(w) + 1 for w, _ in words]; tot = sum(lens); acc = 0; starts = []
        for L in lens: starts.append(a + VO + vd * acc / tot); acc += L
        fN, fA = F(42, 600), FSer(54)
        sp = 12
        items = []
        for i, (w, ac) in enumerate(words):
            f = fA if ac else fN
            items.append((w, ac, f, tw(w, f), starts[i] - 0.06))
        lines = [[]]; lw = 0
        for it in items:
            add = it[3] + (sp if lines[-1] else 0)
            if lw + add > 640 and lines[-1]:
                lines.append([]); lw = 0; add = it[3]
            lines[-1].append(it); lw += add
        out_a = 1 - prog(tg, b - 0.1, b + 0.1)
        LH = 64
        base0 = 1120 - (len(lines) - 1) * LH / 2 + 15
        for li, ln in enumerate(lines):
            total = sum(i[3] for i in ln) + sp * (len(ln) - 1)
            x = W / 2 - total / 2
            by = base0 + li * LH
            for w, ac, f, wdt, t0 in ln:
                p = eo(prog(tg, t0, t0 + 0.2))
                al = p * out_a
                yo = 16 * (1 - p)
                if ac:
                    d.t(x, by + yo, w, f, RED2, al, 'ls')
                    d.line([(x, by + 9 + yo), (x + wdt * p, by + 9 + yo)], RED, 2.5, al)
                else:
                    d.t(x, by + yo, w, f, INK, al, 'ls')
                x += wdt + sp


# ---------- scenes ----------

def scene_intro(d, t, dur):
    # logo
    pa = eo(prog(t, 0.35, 1.0))
    logo = asset('img/logo-sumiago.png', w=420)
    d.img(logo, 360 - 210, 150 - 20 * (1 - pa), pa)
    pb = eo(prog(t, 0.8, 1.3))
    pw = tw('MARKETPLACE', F(24, 800)) + 56
    d.rr(360 - pw / 2, 318 - 12 * (1 - pb), pw, 52, 26, fill=RED, a=pb)
    d.t(360, 344 - 12 * (1 - pb), 'MARKETPLACE', F(24, 800), WHITE, pb, 'mm')
    # mascot
    pm = eo(prog(t, 0.1, 0.95))
    m = asset('videos-virales/mascota-frontal.png', h=600)
    mw = m.width / S
    bob = math.sin(t * 2.2) * 6
    d.img(m, 360 - mw / 2, 410 + 140 * (1 - pm) + bob, pm)
    # chips
    for i, (tx, x, y, t0) in enumerate([('Vende gratis', 40, 560, 1.5), ('Fotos + WhatsApp', 450, 700, 1.9), ('Comparte tu enlace', 40, 840, 2.3)]):
        p = eo(prog(t, t0, t0 + 0.4))
        f = F(21, 600)
        cw = tw(tx, f) + 64
        yy = y + 20 * (1 - p) + math.sin(t * 1.8 + i) * 5
        if x > 360: x = 680 - cw
        d.rr(x, yy, cw, 54, 27, fill=(255, 255, 255), outline=BORDER, a=p * 0.96)
        d.circ(x + 26, yy + 27, 9, fill=RED, a=p)
        check(d, x + 26, yy + 27, 10, WHITE, 2.4, p)
        d.t(x + 44, yy + 27, tx, f, INK, p, 'lm')


# registro timing (local)
R = dict(url=(0.2, 1.0), land=1.0, tap_crear=1.7, form=2.2,
         user=(2.7, 3.6), nom=(3.8, 4.2), ape=(4.4, 4.8), tap_terms=5.6, tap_sig1=7.6, c1=7.9,
         mail=(8.5, 9.7), pais=10.4, wa=(11.1, 12.3), tap_sig2=14.1, c2=14.4,
         pw1=(14.9, 15.7), pw2=(16.0, 16.8), tap_crear2=17.8, ok=18.7)
RX, RY, RW = 40, 250, 640


def reg_step(d, k, t, dx, a):
    x = RX + 36 + dx; w = RW - 72; y = RY
    fy = y + 180
    if k == 1:
        ny = field(d, x, fy, w, 'Usuario', 'carlosventas', t, *R['user'], a, ph='tuusuario')
        ny = field(d, x, ny, w, 'Nombre', 'Carlos', t, *R['nom'], a)
        ny = field(d, x, ny, w, 'Apellido', 'Pérez', t, *R['ape'], a)
        on = t >= R['tap_terms']
        d.rr(x, y + 514, 28, 28, 7, fill=RED if on else FIELD, outline=RED if on else BORDER, width=2, a=a)
        if on: check(d, x + 14, y + 528, 16, WHITE, 3, a, prog(t, R['tap_terms'], R['tap_terms'] + 0.2))
        d.t(x + 42, y + 528, 'Acepto los términos y condiciones', F(20, 500), GRAY, a, 'lm')
        button(d, x, y + 562, w, 60, 'Siguiente  →', t, R['tap_sig1'], a)
    elif k == 2:
        ny = field(d, x, fy, w, 'Correo electrónico', 'carlos@gmail.com', t, *R['mail'], a, ph='tucorreo@ejemplo.com', help='Te enviaremos un código para verificarlo.')
        pt = R['pais']
        val = 'Colombia' if t >= pt else ''
        foc_ph = typed('Col', t, pt - 0.5, pt - 0.15) if t < pt else ''
        ny2 = field(d, x, ny, w, 'País', val, t, pt, pt, a, ph=foc_ph or 'Buscar país...', select=True, right='flag')
        field(d, x, ny2, w, 'WhatsApp', '+57 300 123 4567', t, *R['wa'], a, ph='+57 300 123 4567')
        button(d, x, y + 562, 180, 60, '←  Atrás', t, None, a, style='dark')
        button(d, x + 196, y + 562, w - 196, 60, 'Siguiente  →', t, R['tap_sig2'], a)
    else:
        ny = field(d, x, fy, w, 'Contraseña', 'carlos2026', t, *R['pw1'], a, pwd=True, ph='••••••••')
        ny = field(d, x, ny, w, 'Confirmar contraseña', 'carlos2026', t, *R['pw2'], a, pwd=True, ph='••••••••')
        d.t(x, ny + 4, 'Usa mínimo 8 caracteres.', F(18, 400), DIM, a)
        ld = prog(t, R['tap_crear2'] + 0.1, R['tap_crear2'] + 0.3)
        button(d, x, y + 562, 180, 60, '←  Atrás', t, None, a, style='dark')
        button(d, x + 196, y + 562, w - 196, 60, 'Crear mi cuenta', t, R['tap_crear2'], a, loading=ld)


def scene_reg(d, t, dur):
    # url bar
    d.rr(40, 140, 640, 72, 36, fill=(255, 255, 255), outline=BORDER)
    lock(d, 82, 176, 1.0, GRAY)
    u = typed('sumiago.com', t, *R['url'])
    d.t(110, 176, u, F(26, 500), INK, 1, 'lm')
    if R['url'][0] - 0.2 <= t <= R['url'][1] + 0.3 and int(t * 2.6) % 2 == 0:
        cx = 110 + tw(u, F(26, 500)) + 3
        d.line([(cx, 162), (cx, 190)], RED2, 2.5)
    # landing
    la = eo(prog(t, R['land'], R['land'] + 0.35)) * (1 - prog(t, R['form'] - 0.25, R['form']))
    if la > 0:
        y = RY + 20 * (1 - eo(prog(t, R['land'], R['land'] + 0.35)))
        card(d, RX, y, RW, 420, la)
        lg = asset('img/logo-sumiago.png', w=260)
        d.img(lg, 360 - 130, y + 50, la)
        d.t(360, y + 190, 'Únete a la comunidad Sumiago', F(26, 600), INK, la, 'mm')
        d.t(360, y + 228, 'Compra, vende y aprende con nosotros', F(20, 400), GRAY, la, 'mm')
        button(d, RX + 36, y + 290, 270, 62, 'Iniciar sesión', t, None, la, style='dark', fsize=22)
        button(d, RX + 322, y + 290, 282, 62, 'Crear cuenta', t, R['tap_crear'], la, fsize=22)
    tapfx(d, RX + 322 + 141, RY + 321, t, R['tap_crear'])
    fa = eo(prog(t, R['form'], R['form'] + 0.4))
    if fa > 0:
        y = RY + 30 * (1 - fa)
        card(d, RX, y, RW, 650, fa)
        okp = prog(t, R['ok'] - 0.1, R['ok'] + 0.1)
        ha = fa * (1 - okp)
        d.t(RX + 36, y + 36, 'Crear cuenta', F(34, 700), INK, ha)
        d.t(RX + 36, y + 84, 'Únete a la comunidad Sumiago', F(20, 400), GRAY, ha)
        cur = 1 if t < R['c1'] + 0.2 else 2 if t < R['c2'] + 0.2 else 3
        sw = (RW - 72 - 24) / 3
        for i in range(3):
            on = i + 1 <= cur
            d.rr(RX + 36 + i * (sw + 12), y + 128, sw, 6, 3, fill=RED if on else BORDER, a=ha)
        d.t(RX + RW - 36, y + 48, f'Paso {cur} de 3', F(19, 600), GRAY, ha, 'ra')
        # step contents with slide
        for k, c_in, c_out in [(1, R['form'] + 0.2, R['c1']), (2, R['c1'], R['c2']), (3, R['c2'], 99)]:
            pin = eo(prog(t, c_in, c_in + 0.4)) if k > 1 else fa
            pout = eo(prog(t, c_out, c_out + 0.4))
            a = pin * (1 - pout) * (1 - okp)
            if a <= 0.003: continue
            dx = (80 * (1 - pin) if k > 1 else 0) - 80 * pout
            reg_step(d, k, t, dx, a)
        if t >= R['ok'] - 0.1:
            success(d, 360, RY + 270, t, R['ok'], '¡Cuenta creada!', 'Ahora verifica tu correo', fa)
    # taps
    x = RX + 36; w = RW - 72
    for (a_, b_), yy in [(R['user'], RY + 180 + 60), (R['nom'], RY + 286 + 60), (R['ape'], RY + 392 + 60)]:
        tapfx(d, x + 140, yy, t, a_ - 0.12)
    tapfx(d, x + 14, RY + 528, t, R['tap_terms'])
    tapfx(d, 360, RY + 592, t, R['tap_sig1'])
    tapfx(d, x + 140, RY + 240, t, R['mail'][0] - 0.12)
    tapfx(d, x + 140, RY + 368, t, R['pais'] - 0.7)
    tapfx(d, x + 140, RY + 474, t, R['wa'][0] - 0.12)
    tapfx(d, x + 196 + (w - 196) / 2, RY + 592, t, R['tap_sig2'])
    tapfx(d, x + 140, RY + 240, t, R['pw1'][0] - 0.12)
    tapfx(d, x + 140, RY + 346, t, R['pw2'][0] - 0.12)
    tapfx(d, x + 196 + (w - 196) / 2, RY + 592, t, R['tap_crear2'])


V = dict(notif=0.3, tap_box=1.7, digits=2.0, tap_ver=3.9, ok=4.5)


def scene_ver(d, t, dur):
    p = eo(prog(t, V['notif'], V['notif'] + 0.45))
    y = 60 + 70 * p
    d.rr(40, y, 640, 112, 24, fill=(255, 255, 255), outline=BORDER, a=p)
    d.rr(62, y + 24, 64, 64, 16, fill=RED, a=p)
    d.rr(76, y + 41, 36, 28, 4, outline=WHITE, width=2.5, a=p)
    d.line([(77, y + 43), (94, y + 57), (111, y + 43)], WHITE, 2.5, p)
    d.t(146, y + 38, 'Sumiago', F(24, 700), INK, p, 'lm')
    d.t(654, y + 38, 'ahora', F(18, 400), GRAY, p, 'rm')
    d.t(146, y + 74, 'Tu código de verificación: 482915', F(21, 500), (70, 70, 78), p, 'lm')
    ca = eo(prog(t, 0.6, 1.0))
    cy0 = 290 + 30 * (1 - ca)
    card(d, 40, cy0, 640, 560, ca)
    okp = prog(t, V['ok'] - 0.1, V['ok'] + 0.1)
    a = ca * (1 - okp)
    d.t(360, cy0 + 60, 'Verifica tu correo', F(34, 700), INK, a, 'mm')
    d.t(360, cy0 + 110, 'Escribe el código de 6 dígitos', F(22, 400), GRAY, a, 'mm')
    d.t(360, cy0 + 140, 'que enviamos a carlos@gmail.com', F(22, 400), GRAY, a, 'mm')
    code = '482915'
    for i in range(6):
        bx = 85 + i * 94; by = cy0 + 190
        ti = V['digits'] + i * 0.2
        filled = t >= ti
        foc = (t >= V['tap_box'] and not filled and (i == 0 or t >= ti - 0.2))
        pop = 1 + 0.08 * math.sin(math.pi * prog(t, ti, ti + 0.15))
        bw, bh = 80 * pop, 96 * pop
        d.rr(bx + 40 - bw / 2, by + 48 - bh / 2, bw, bh, 16, fill=FIELD, outline=RED if (foc or filled) else BORDER, width=2, a=a)
        if filled: d.t(bx + 40, by + 50, code[i], F(44, 700), INK, a, 'mm')
        elif foc and int(t * 2.6) % 2 == 0: d.line([(bx + 40, by + 30), (bx + 40, by + 66)], RED2, 2.5, a)
    ld = prog(t, V['tap_ver'] + 0.1, V['tap_ver'] + 0.3)
    button(d, 76, cy0 + 360, 568, 64, 'Verificar correo', t, V['tap_ver'], a, loading=ld)
    d.t(360, cy0 + 470, '¿No te llegó? Reenviar código', F(20, 500), GRAY, a, 'mm')
    if t >= V['ok'] - 0.1:
        success(d, 360, cy0 + 220, t, V['ok'], '¡Cuenta verificada!', 'Ya puedes entrar a tu panel', ca)
    tapfx(d, 125, 290 + 190 + 48, t, V['tap_box'])
    tapfx(d, 360, 290 + 392, t, V['tap_ver'])


P = dict(tap_mk=1.6, swap=2.4, tap_pub=3.6)
MENU = ['Dashboard', 'Mi membresía', 'Mi rango', 'Tareas diarias', 'Marketplace', 'Soporte']


def scene_panel(d, t, dur):
    ma = eo(prog(t, 0.0, 0.35)) * (1 - prog(t, P['swap'], P['swap'] + 0.3))
    if ma > 0:
        x, y = 40, 130
        card(d, x, y, 640, 700, ma)
        lg = asset('img/logo-sumiago.png', w=170)
        d.img(lg, x + 30, y + 28, ma)
        d.t(x + 30, y + 110, 'Hola, Carlos', F(32, 700), INK, ma)
        d.t(x + 30, y + 154, 'Bienvenido a tu panel', F(20, 400), GRAY, ma)
        for i, it in enumerate(MENU):
            p = eo(prog(t, 0.1 + i * 0.07, 0.45 + i * 0.07)) * ma
            iy = y + 200 + i * 80 + 12 * (1 - p)
            hl = i == 4 and t >= P['tap_mk'] + 0.05
            d.rr(x + 24, iy, 592, 70, 16, fill=RED if hl else ITEM, a=p)
            d.circ(x + 62, iy + 35, 18, fill=(255, 255, 255) if hl else (226, 226, 231), a=p)
            d.t(x + 62, iy + 36, it[0], F(19, 800), RED if hl else INK, p, 'mm')
            d.t(x + 96, iy + 35, it, F(24, 600), WHITE if hl else INK, p, 'lm')
            if i == 4:
                d.rr(x + 520, iy + 22, 76, 26, 13, fill=WHITE if hl else RED, a=p)
                d.t(x + 558, iy + 35, 'NUEVO', F(14, 800), RED if hl else WHITE, p, 'mm')
        tapfx(d, x + 300, y + 200 + 4 * 80 + 35, t, P['tap_mk'])
    va = eo(prog(t, P['swap'] + 0.2, P['swap'] + 0.6))
    if va > 0:
        x, y = 40, 150 + 30 * (1 - va)
        card(d, x, y, 640, 560, va)
        d.t(x + 30, y + 40, 'Marketplace', F(40, 700), INK, va)
        d.t(x + 30, y + 98, 'Compra y vende en tu ciudad', F(21, 400), GRAY, va)
        tabs = ['Mis artículos', '+ Publicar', 'Comprar cupos', 'Alertas']
        on = 1 if t >= P['tap_pub'] + 0.05 else 0
        tx = x + 30
        f = F(19, 600)
        pos = []
        for i, tb in enumerate(tabs):
            w = tw(tb, f) + 32
            if tx + w > x + 620: break
            isn = i == on
            d.rr(tx, y + 150, w, 46, 23, fill=RED if isn else (243, 243, 245), outline=RED if isn else BORDER, a=va)
            d.t(tx + w / 2, y + 173, tb, f, WHITE if isn else INK, va, 'mm')
            pos.append((tx + w / 2, y + 173)); tx += w + 8
        ea = va * (1 - prog(t, P['tap_pub'] + 0.05, P['tap_pub'] + 0.3))
        d.circ(360, y + 300, 46, fill=(243, 243, 245), a=ea)
        d.rr(340, y + 290, 40, 32, 5, outline=INK, width=2.5, a=ea)
        d.arc(360, y + 290, 10, 180, 360, INK, 2.5, ea)
        d.t(360, y + 390, 'Aún no has publicado nada.', F(22, 500), GRAY, ea, 'mm')
        button(d, 90, y + 440, 540, 62, 'Publicar mi primer artículo gratis', t, None, ea, fsize=21, glow=True)
        fa = va * eo(prog(t, P['tap_pub'] + 0.15, P['tap_pub'] + 0.45))
        if fa > 0:
            d.t(x + 30, y + 250, 'Publicar un artículo', F(30, 700), INK, fa)
            for i in range(3):
                d.rr(x + 30 + i * 196, y + 310, 172, 172, 18, fill=FIELD, outline=BORDER, a=fa)
                d.t(x + 116 + i * 196, y + 396, '+', F(40, 300), DIM, fa, 'mm')
        if len(pos) > 1: tapfx(d, pos[1][0], pos[1][1], t, P['tap_pub'])


M = dict(tap1=0.5, ph1=0.75, tap2=1.1, ph2=1.35, tit=(2.2, 3.6), cat=4.0, sub=4.6, pre=(5.4, 5.8), mon=6.1, est=6.8,
         sc1=(7.0, 7.8), desc=(8.0, 9.4), ciu=(9.8, 10.3), sc2=(10.6, 11.1), tap_pub=12.4, hide=13.1,
         art=13.3, tap_share=14.9, wa=15.2)
MX, MY, MCW, MCH = 40, 110, 640, 800


def mk_scroll(t):
    s1 = eio(prog(t, *M['sc1'])) * 330
    s2 = eio(prog(t, *M['sc2'])) * 160
    return s1 + s2


def form_layer(t):
    sc = mk_scroll(t)
    lay = Image.new('RGB', (MCW * S, MCH * S), CARD)
    d = D(lay, MX, MY + sc)
    X = MX + 30; W2 = 580
    Y = lambda cy: MY + cy
    d.t(X, Y(30), 'Publicar un artículo', F(32, 700), INK)
    d.t(X, Y(88), 'Fotos del artículo (mínimo 1, máximo 5)', F(19, 500), GRAY)
    for i in range(3):
        sx = X + i * 204; sy = Y(124)
        d.rr(sx, sy, 172, 172, 18, fill=FIELD, outline=BORDER)
        tp = M['ph1'] if i == 0 else M['ph2'] if i == 1 else 99
        if t >= tp:
            p = eo(prog(t, tp, tp + 0.3))
            s = 172 * (0.85 + 0.15 * p)
            im = photo_r(1 if i == 0 else 2, round(s), 18)
            d.img(im, sx + 86 - s / 2, sy + 86 - s / 2, p)
            if i == 0:
                d.rr(sx + 10, sy + 10, 84, 26, 13, fill=RED, a=p)
                d.t(sx + 52, sy + 23, 'Portada', F(14, 700), WHITE, p, 'mm')
        else:
            d.t(sx + 86, sy + 80, '+', F(44, 300), DIM, 1, 'mm')
            d.t(sx + 86, sy + 126, 'Agregar', F(17, 500), DIM, 1, 'mm')
    field(d, X, Y(330), W2, 'Título', 'Celular 128 GB como nuevo', t, *M['tit'], ph='Ej: Toyota Corolla 2015 automático')
    hw = 282
    field(d, X, Y(436), hw, 'Categoría', 'Electrónica', t, M['cat'], M['cat'], ph='Elige…', select=True, hold=0.2)
    field(d, X + 298, Y(436), hw, 'Subcategoría', 'Celulares', t, M['sub'], M['sub'], ph='Elige…', select=True, hold=0.2)
    field(d, X, Y(542), hw, 'Precio real', '180', t, *M['pre'], ph='Ej: 150')
    field(d, X + 298, Y(542), hw, 'Moneda', 'USD', t, M['mon'], M['mon'], ph='Elige…', select=True, hold=0.2)
    d.t(X, Y(648), 'Estado', F(19, 500), GRAY)
    on = t >= M['est'] + 0.05
    d.rr(X, Y(678), W2, 60, 14, fill=FIELD, outline=BORDER)
    if on:
        p = eo(prog(t, M['est'], M['est'] + 0.25))
        d.rr(X + 4, Y(682), W2 / 2 - 4, 52, 11, fill=RED, a=p)
    d.t(X + W2 / 4, Y(708), 'Usado', F(23, 600), INK, 1, 'mm')
    d.t(X + 3 * W2 / 4, Y(708), 'Nuevo', F(23, 600), GRAY, 1, 'mm')
    field(d, X, Y(770), W2, 'Descripción', 'Batería al 90%, con caja y cargador original. Entrega en Medellín.', t, *M['desc'], h=130, wrap=True,
          ph='Detalles, estado, medidas, qué incluye…')
    field(d, X, Y(962), hw, 'Ciudad', 'Medellín', t, *M['ciu'], ph='Ej: Maracaibo')
    field(d, X + 298, Y(962), hw, 'País', 'Colombia', t, -5, -5, right='lock', hold=0)
    field(d, X, Y(1068), W2, 'WhatsApp', '+57 300 123 4567', t, -5, -5, hold=0)
    ld = prog(t, M['tap_pub'] + 0.1, M['tap_pub'] + 0.3)
    button(d, X, Y(1190), W2, 66, '➤  Publicar', t, M['tap_pub'], 1, loading=ld, glow=True) if False else \
        button(d, X, Y(1190), W2, 66, 'Publicar', t, M['tap_pub'], 1, loading=ld, glow=True)
    return lay, sc


@lru_cache(None)
def card_mask():
    m = Image.new('L', (MCW * S, MCH * S), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, MCW * S - 1, MCH * S - 1], radius=26 * S, fill=255)
    return m


def scene_mk(d, t, dur):
    fa = eo(prog(t, 0, 0.35)) * (1 - prog(t, M['hide'], M['hide'] + 0.3))
    if fa > 0:
        lay, sc = form_layer(t)
        m = card_mask()
        if fa < 0.999: m = m.point(lambda v: int(v * fa))
        d.rr(MX - 1, MY - 1, MCW + 2, MCH + 2, 27, outline=BORDER, a=fa)
        d.im.paste(lay, (MX * S, MY * S), m)
        # scroll bar
        d.rr(MX + MCW - 10, MY + 20 + sc / 490 * (MCH - 40 - 200), 4, 200, 2, fill=(200, 200, 206), a=fa * 0.8)
        sy = lambda cy: MY + cy - sc
        tapfx(d, MX + 30 + 86, sy(210), t, M['tap1'])
        tapfx(d, MX + 30 + 204 + 86, sy(210), t, M['tap2'])
        tapfx(d, MX + 200, sy(390), t, M['tit'][0] - 0.12)
        tapfx(d, MX + 150, sy(496), t, M['cat'] - 0.1)
        tapfx(d, MX + 450, sy(496), t, M['sub'] - 0.1)
        tapfx(d, MX + 150, sy(602), t, M['pre'][0] - 0.12)
        tapfx(d, MX + 450, sy(602), t, M['mon'] - 0.1)
        tapfx(d, MX + 175, sy(708), t, M['est'])
        tapfx(d, MX + 200, sy(860), t, M['desc'][0] - 0.12)
        tapfx(d, MX + 150, sy(1022), t, M['ciu'][0] - 0.12)
        tapfx(d, 360, sy(1223), t, M['tap_pub'])
    # published card
    pa = eo(prog(t, M['art'], M['art'] + 0.45))
    if pa > 0:
        x, w = 90, 540
        y = 120 + 40 * (1 - pa)
        sc_ = 0.94 + 0.06 * pa
        card(d, x, y, w, 600, pa)
        im = photo_rect(1, 540, 400, 26)
        d.img(im, x, y, pa)
        d.rr(x + 20, y + 20, 150, 38, 19, fill=RED, a=pa)
        check(d, x + 42, y + 39, 14, WHITE, 3, pa)
        d.t(x + 58, y + 39, 'Publicado', F(18, 700), WHITE, pa, 'lm')
        d.t(x + 28, y + 432, 'Celular 128 GB como nuevo', F(29, 700), INK, pa)
        d.t(x + 28, y + 478, '$180 USD', F(38, 800), RED2, pa)
        d.t(x + 28, y + 540, 'Medellín, Colombia  ·  Usado', F(21, 400), GRAY, pa)
        # share button
        bx, by = x + w - 62, y + 500
        k = 1 - 0.08 * math.sin(math.pi * prog(t, M['tap_share'] - 0.04, M['tap_share'] + 0.18))
        d.circ(bx, by, 28 * k, fill=(37, 211, 102), a=pa)
        for (ax, ay) in [(-8, 0), (7, -9), (7, 9)]:
            d.circ(bx + ax, by + ay, 4.2, fill=WHITE, a=pa)
        d.line([(bx - 8, by), (bx + 7, by - 9)], WHITE, 2.2, pa)
        d.line([(bx - 8, by), (bx + 7, by + 9)], WHITE, 2.2, pa)
        tapfx(d, bx, by, t, M['tap_share'])
    wa = eo(prog(t, M['wa'], M['wa'] + 0.45))
    if wa > 0:
        x, y, w, h = 110, 760 + 40 * (1 - wa), 570, 214
        d.rr(x, y, w, h, 18, fill=(217, 253, 211), outline=(190, 230, 185), a=wa)
        d.rr(x + 10, y + 10, w - 20, 124, 12, fill=(196, 238, 190), a=wa)
        im = photo_rect(1, 124, 124, 12)
        d.img(im, x + 10, y + 10, wa)
        d.t(x + 150, y + 26, 'Celular 128 GB como nuevo', F(21, 700), INK, wa)
        d.t(x + 150, y + 60, '$180 USD · Medellín, Colombia', F(18, 400), (60, 80, 70), wa)
        d.t(x + 150, y + 96, 'sumiago.com', F(17, 400), (100, 120, 110), wa)
        d.t(x + 18, y + 150, 'sumiago.com/marketplace/articulo.php?id=celu…', F(18, 500), (2, 122, 190), wa)
        d.t(x + w - 52, y + 196, '10:52', F(15, 400), (100, 120, 110), wa, 'rs')
        check(d, x + w - 36, y + 190, 11, (83, 189, 235), 2, wa)
        check(d, x + w - 28, y + 190, 11, (83, 189, 235), 2, wa)


def scene_outro(d, t, dur):
    sw = 5.2
    a1 = eo(prog(t, 0.15, 0.5)) * (1 - prog(t, sw, sw + 0.35))
    a2 = eo(prog(t, 3.2, 3.6)) * (1 - prog(t, sw, sw + 0.35))
    if a1 > 0:
        y = 190 + 20 * (1 - eo(prog(t, 0.15, 0.5)))
        card(d, 40, y, 640, 220, a1)
        d.t(76, y + 40, 'GRATIS', F(20, 800), GRAY, a1)
        d.t(76, y + 78, '1 artículo', F(48, 800), INK, a1)
        d.t(76, y + 152, '1 foto por artículo', F(22, 400), GRAY, a1)
        d.t(644, y + 110, '$0', F(56, 800), INK, a1, 'rm')
    if a2 > 0:
        y = 450 + 20 * (1 - eo(prog(t, 3.2, 3.6)))
        card(d, 40, y, 640, 250, a2, glow=True)
        d.t(76, y + 40, 'CON MEMBRESÍA', F(20, 800), RED2, a2)
        d.t(76, y + 78, 'Hasta 5 artículos', F(48, 800), INK, a2)
        d.t(76, y + 152, '5 fotos por artículo', F(22, 400), GRAY, a2)
        d.t(76, y + 186, '+ cupos extra disponibles', F(22, 400), GRAY, a2)
    pm = eo(prog(t, sw + 0.2, sw + 0.9))
    if pm > 0:
        lg = asset('img/logo-sumiago.png', w=380)
        d.img(lg, 360 - 190, 120 + 20 * (1 - pm), pm)
        pw = tw('sumiago.com', F(28, 700)) + 64
        d.rr(360 - pw / 2, 290, pw, 60, 30, fill=(255, 255, 255), outline=RED, width=1.5, a=pm)
        d.t(360, 320, 'sumiago.com', F(28, 700), INK, pm, 'mm')
        m = asset('videos-virales/mascota-pulgar.png', h=580)
        bob = math.sin(t * 2.2) * 6
        d.img(m, 360 - m.width / S / 2, 410 + 140 * (1 - pm) + bob, pm)


SCENES = [
    ('a_intro', 0.0, 5.5, scene_intro),
    ('b_reg', 5.5, 25.5, scene_reg),
    ('c_ver', 25.5, 32.0, scene_ver),
    ('d_panel', 32.0, 37.0, scene_panel),
    ('e_mk', 37.0, 55.5, scene_mk),
    ('f_outro', 55.5, 64.0, scene_outro),
]


def frame(si, tl):
    global BGIM
    if BGIM is None: BGIM = make_bg()
    name, a, b, fn = SCENES[si]
    im = BGIM.copy()
    d = D(im)
    fn(d, tl, b - a)
    # scene fade (draw bg-colored veil): fade in/out edges
    fin = prog(tl, 0, 0.3) if si > 0 else 1
    fout = 1 - prog(tl, (b - a) - 0.3, (b - a)) if si < len(SCENES) - 1 else 1 - prog(tl, (b - a) - 0.5, (b - a))
    v = 1 - fin * fout
    if v > 0.003:
        im = Image.blend(im, BGIM, v)
        d = D(im)
    captions(d, a + tl)
    if OUTW != W: return im.resize((OUTW, OUTH), Image.LANCZOS)
    return im.reduce(S)


def render_scene(si, out):
    name, a, b, fn = SCENES[si]
    n = int(round((b - a) * FPS))
    tmp = out[:-4] + '.part.mp4'
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{OUTW}x{OUTH}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '18', '-pix_fmt', 'yuv420p', tmp], stdin=subprocess.PIPE)
    for i in range(n):
        p.stdin.write(frame(si, i / FPS).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(tmp, out)


if __name__ == '__main__':
    if sys.argv[1] == 'still':
        tg = float(sys.argv[2])
        for si, (n, a, b, fn) in enumerate(SCENES):
            if a <= tg < b:
                frame(si, tg - a).save(sys.argv[3]); break
    else:
        si = int(sys.argv[1])
        render_scene(si, os.environ.get('ODIR', 'out') + f'/{SCENES[si][0]}.mp4')
