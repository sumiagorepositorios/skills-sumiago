"""Motor común de videos de Sumiago (Tareas Diarias).
Lee guion.json (frases + escena de cada frase) y tl.json (tiempos de la voz, de voz.py)
y dibuja el reel 9:16 a 720x1280 / 30 fps (se entrega a 1080x1920).

  python motor.py still 3.5 10 22      -> still_3.5.jpg ... (para revisar)
  python motor.py 0 999999 video.mp4   -> video sin audio (se puede partir en dos ventanas)

Qué hace en todos los videos:
- textos que salen desde detrás de una máscara (palabra por palabra, al ritmo de la voz),
- movimientos encadenados (cada elemento entra cuando termina el anterior),
- cámara que sigue al elemento importante de cada escena,
- el objeto principal de una escena se transforma en el de la siguiente,
- cierre con el logo de Sumiago.
"""
import json, math, os, random, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

AQUI = os.path.dirname(os.path.abspath(__file__)); RAIZ = os.path.dirname(AQUI)
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

G = json.load(open('guion.json', encoding='utf-8'))
TL = json.load(open('tl.json', encoding='utf-8'))
CL = TL['clips']; TEMA = G.get('tema', 'oscuro'); CLARO = TEMA == 'claro'
RED = (230, 38, 47); GREEN = (46, 190, 110); GOLD = (255, 196, 60)
INK = (24, 24, 30) if CLARO else (255, 255, 255)
SUB = (110, 110, 120) if CLARO else (170, 170, 180)
CARD = (255, 255, 255) if CLARO else (28, 29, 36)
CARD2 = (244, 244, 247) if CLARO else (40, 41, 50)
LINE = (225, 225, 232) if CLARO else (62, 63, 74)
LOGO_T = CL[-1]['t0'] + CL[-1]['d'] + 0.35
NF = int(TL['total'] * FPS)

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))
def back_out(x):
    x = max(0, min(1, x)); c = 1.7; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2
def lv(t):
    L = TL.get('lv'); i = int(t * FPS)
    return L[i] if L and 0 <= i < len(L) else 0

# ---------- palabras y tiempos ----------
PUNT = '¿?¡!.,:;«»…"()'
def limpia(w): return w.strip(PUNT).lower()
KEY = {limpia(k) for k in G.get('palabras_clave', [])}
def is_key(w): return limpia(w) in KEY
WT = [[(w, t) for w, t in c['words']] for c in CL]
def wt(ci, palabra, n=0):
    """Momento en que se dice la palabra (o su inicio) en la frase ci."""
    if palabra is None: return None
    p = limpia(palabra); k = 0
    for w, t in WT[ci]:
        if limpia(w).startswith(p):
            if k == n: return t
            k += 1
    return None
def ct(i): return CL[i]['t0']
ST = [c['t0'] - 0.15 for c in CL] + [LOGO_T]

# ---------- fondos ----------
def gradient(top, bot):
    a = np.linspace(0, 1, H)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - a) + np.array(bot)[None, None] * a) * np.ones((1, W, 1))
    return Image.fromarray(arr.astype(np.uint8), 'RGB').convert('RGBA')
def glow(shape_fn, col, blur, alpha=255):
    m = Image.new('L', (W, H), 0); shape_fn(ImageDraw.Draw(m)); m = m.filter(ImageFilter.GaussianBlur(blur))
    L = Image.new('RGBA', (W, H), col + (0,)); L.putalpha(m.point(lambda p: int(p * alpha / 255))); return L
def make_bg():
    if CLARO:
        im = gradient((255, 255, 255), (246, 246, 249)); d = ImageDraw.Draw(im); rr = random.Random(2)
        for k in range(60):
            x, y = rr.randint(0, W), rr.randint(0, H); r = rr.choice([2, 2, 3, 4]); d.ellipse((x, y, x + r, y + r), fill=(240, 120, 125, 120))
        im.alpha_composite(glow(lambda d: d.ellipse((-200, 300, 920, 1100), fill=255), (255, 225, 228), 160, 160))
    else:
        im = gradient((16, 12, 16), (6, 6, 10))
        im.alpha_composite(glow(lambda d: d.ellipse((-260, -200, 980, 700), fill=255), (110, 12, 20), 170, 170))
    return im
BG = make_bg()
def vignette():
    y, x = np.mgrid[0:H, 0:W]; r = np.sqrt(((x - W / 2) / (W * .8)) ** 2 + ((y - H / 2) / (H * .75)) ** 2)
    a = np.clip((r - .6) * 1.4, 0, 1) * (60 if CLARO else 190)
    v = Image.new('RGBA', (W, H), (0, 0, 0, 0)); v.putalpha(Image.fromarray(a.astype(np.uint8))); return v
VIG = vignette()

# ---------- piezas comunes ----------
def mask_text(im, xy, txt, f, col, q, anchor='m'):
    """Texto que sube desde detrás de una máscara."""
    if q <= 0 or not txt: return
    d0 = ImageDraw.Draw(im); tw = d0.textlength(txt, font=f); hh = int(f.size * 1.4)
    L = Image.new('RGBA', (int(tw) + 10, hh), (0, 0, 0, 0)); ImageDraw.Draw(L).text((5, hh / 2 + (1 - ease(q)) * hh), txt, font=f, fill=col + (255,), anchor='lm')
    x = xy[0] - tw / 2 - 5 if anchor == 'm' else xy[0] - 5
    im.alpha_composite(L, (int(x), int(xy[1] - hh / 2)))
def wrap(txt, f, maxw):
    d = ImageDraw.Draw(BG); out = [[]]
    for w in txt.split():
        if out[-1] and d.textlength(' '.join(out[-1] + [w]), font=f) > maxw: out.append([])
        out[-1].append(w)
    return [' '.join(l) for l in out]
def shadow(im, r, rad=24, a=110, off=14):
    im.alpha_composite(glow(lambda d: d.rounded_rectangle((r[0] + 6, r[1] + off, r[2] + 6, r[3] + off), rad, fill=255), (0, 0, 0), 18, a if not CLARO else a // 2))
def card(im, r, fill=None, outline=None, rad=24, sh=True):
    if sh: shadow(im, r, rad)
    ImageDraw.Draw(im).rounded_rectangle(r, rad, fill=fill or CARD, outline=outline or LINE, width=2 if not outline else 4)
def scaled(im, layer, cx, cy, s, a=1.0):
    if s <= 0.02: return
    L = layer.resize((max(1, int(layer.width * s)), max(1, int(layer.height * s))), Image.LANCZOS)
    if a < 1: L.putalpha(L.getchannel('A').point(lambda p: int(p * a)))
    im.alpha_composite(L, (int(cx - L.width / 2), int(cy - L.height / 2)))

# ---------- iconos (dibujados, sin imágenes externas) ----------
def icon(d, kind, cx, cy, s, col=RED, fg=(255, 255, 255)):
    r = 34 * s; d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=col); k = s
    def P(pts): return [(cx + x * k, cy + y * k) for x, y in pts]
    if kind == 'estrella':
        pts = []
        for i in range(10):
            a = -math.pi / 2 + i * math.pi / 5; rr = 18 if i % 2 == 0 else 8; pts.append((math.cos(a) * rr, math.sin(a) * rr))
        d.polygon(P(pts), fill=fg)
    elif kind == 'ubicacion':
        d.ellipse((cx - 12 * k, cy - 18 * k, cx + 12 * k, cy + 6 * k), fill=fg); d.polygon(P([(-11, 0), (11, 0), (0, 20)]), fill=fg); d.ellipse((cx - 5 * k, cy - 11 * k, cx + 5 * k, cy - 1 * k), fill=col)
    elif kind == 'chat':
        d.rounded_rectangle((cx - 18 * k, cy - 14 * k, cx + 18 * k, cy + 10 * k), 8 * k, fill=fg); d.polygon(P([(-8, 9), (2, 9), (-10, 19)]), fill=fg)
        for i in (-9, 0, 9): d.ellipse((cx + (i - 3) * k, cy - 5 * k, cx + (i + 3) * k, cy + 1 * k), fill=col)
    elif kind == 'persona':
        d.ellipse((cx - 9 * k, cy - 18 * k, cx + 9 * k, cy), fill=fg); d.chord((cx - 18 * k, cy + 2 * k, cx + 18 * k, cy + 34 * k), 180, 360, fill=fg)
    elif kind == 'escudo':
        d.polygon(P([(0, -19), (16, -12), (14, 6), (0, 19), (-14, 6), (-16, -12)]), fill=fg); d.line(P([(-7, 0), (-2, 6), (8, -6)]), fill=col, width=max(2, int(4 * k)))
    elif kind == 'alerta':
        d.polygon(P([(0, -18), (19, 15), (-19, 15)]), fill=fg); d.rectangle((cx - 2 * k, cy - 7 * k, cx + 2 * k, cy + 5 * k), fill=col); d.ellipse((cx - 2.5 * k, cy + 8 * k, cx + 2.5 * k, cy + 12 * k), fill=col)
    elif kind == 'libro':
        d.rectangle((cx - 18 * k, cy - 13 * k, cx - 2 * k, cy + 13 * k), fill=fg); d.rectangle((cx + 2 * k, cy - 13 * k, cx + 18 * k, cy + 13 * k), fill=fg)
    elif kind == 'tienda':
        d.rectangle((cx - 17 * k, cy - 4 * k, cx + 17 * k, cy + 16 * k), fill=fg); d.polygon(P([(-21, -4), (21, -4), (15, -17), (-15, -17)]), fill=fg); d.rectangle((cx - 5 * k, cy + 3 * k, cx + 5 * k, cy + 16 * k), fill=col)
    elif kind == 'play':
        d.polygon(P([(-8, -13), (-8, 13), (14, 0)]), fill=fg)
    elif kind == 'telefono':
        d.rounded_rectangle((cx - 11 * k, cy - 19 * k, cx + 11 * k, cy + 19 * k), 5 * k, fill=fg); d.rectangle((cx - 7 * k, cy - 13 * k, cx + 7 * k, cy + 10 * k), fill=col)
    elif kind == 'maleta':
        d.rounded_rectangle((cx - 19 * k, cy - 9 * k, cx + 19 * k, cy + 15 * k), 4 * k, fill=fg); d.rounded_rectangle((cx - 7 * k, cy - 16 * k, cx + 7 * k, cy - 7 * k), 3 * k, outline=fg, width=max(2, int(3 * k)))
    elif kind == 'reloj':
        d.ellipse((cx - 18 * k, cy - 18 * k, cx + 18 * k, cy + 18 * k), fill=fg); d.line((cx, cy, cx, cy - 12 * k), fill=col, width=max(2, int(3 * k))); d.line((cx, cy, cx + 9 * k, cy + 4 * k), fill=col, width=max(2, int(3 * k)))
    elif kind == 'dinero':
        d.text((cx, cy + 1), '$', font=F('Inter-Black.otf', int(34 * k)), fill=fg, anchor='mm')
    elif kind == 'check':
        d.line(P([(-12, 0), (-3, 10), (13, -10)]), fill=fg, width=max(3, int(6 * k)))
    elif kind == 'enlace':
        d.rounded_rectangle((cx - 20 * k, cy - 8 * k, cx - 1 * k, cy + 8 * k), 8 * k, outline=fg, width=max(2, int(4 * k))); d.rounded_rectangle((cx + 1 * k, cy - 8 * k, cx + 20 * k, cy + 8 * k), 8 * k, outline=fg, width=max(2, int(4 * k)))
    elif kind == 'foto':
        d.rounded_rectangle((cx - 18 * k, cy - 13 * k, cx + 18 * k, cy + 13 * k), 4 * k, fill=fg); d.polygon(P([(-14, 10), (-3, -3), (5, 6), (10, 1), (15, 10)]), fill=col)
    elif kind == 'carro':
        d.rounded_rectangle((cx - 20 * k, cy - 4 * k, cx + 20 * k, cy + 9 * k), 4 * k, fill=fg); d.polygon(P([(-12, -4), (-7, -13), (8, -13), (13, -4)]), fill=fg)
        for x in (-11, 11): d.ellipse((cx + (x - 5) * k, cy + 5 * k, cx + (x + 5) * k, cy + 15 * k), fill=col)
    elif kind == 'tijera':
        for y in (-8, 8): d.ellipse((cx - 18 * k, cy + (y - 6) * k, cx - 6 * k, cy + (y + 6) * k), outline=fg, width=max(2, int(3 * k)))
        d.line(P([(-8, -5), (18, 9)]), fill=fg, width=max(2, int(4 * k))); d.line(P([(-8, 5), (18, -9)]), fill=fg, width=max(2, int(4 * k)))
    elif kind == 'regalo':
        d.rectangle((cx - 16 * k, cy - 6 * k, cx + 16 * k, cy + 16 * k), fill=fg); d.rectangle((cx - 18 * k, cy - 12 * k, cx + 18 * k, cy - 4 * k), fill=fg); d.rectangle((cx - 3 * k, cy - 12 * k, cx + 3 * k, cy + 16 * k), fill=col)
    elif kind == 'grafica':
        for i, hh in enumerate((8, 14, 22)): d.rectangle((cx + (-16 + i * 12) * k, cy + (14 - hh) * k, cx + (-8 + i * 12) * k, cy + 14 * k), fill=fg)
        d.line(P([(-16, -6), (-4, -12), (4, -8), (16, -18)]), fill=fg, width=max(2, int(3 * k)))
    elif kind == 'mundo':
        d.ellipse((cx - 18 * k, cy - 18 * k, cx + 18 * k, cy + 18 * k), outline=fg, width=max(2, int(3 * k))); d.ellipse((cx - 8 * k, cy - 18 * k, cx + 8 * k, cy + 18 * k), outline=fg, width=max(2, int(3 * k))); d.line((cx - 18 * k, cy, cx + 18 * k, cy), fill=fg, width=max(2, int(3 * k)))
    elif kind == 'correo':
        d.rectangle((cx - 18 * k, cy - 12 * k, cx + 18 * k, cy + 12 * k), fill=fg); d.line(P([(-18, -12), (0, 3), (18, -12)]), fill=col, width=max(2, int(3 * k)))
    elif kind == 'bici':
        for x in (-11, 11): d.ellipse((cx + (x - 8) * k, cy - 2 * k, cx + (x + 8) * k, cy + 14 * k), outline=fg, width=max(2, int(3 * k)))
        d.line(P([(-11, 6), (-2, -8), (11, 6), (0, 6), (-11, 6)]), fill=fg, width=max(2, int(3 * k)))
    elif kind == 'ia':
        d.text((cx, cy + 1), 'IA', font=F('Inter-Black.otf', int(24 * k)), fill=fg, anchor='mm')
    else:  # texto corto como icono (número, letra o emoji simple)
        d.text((cx, cy + 1), str(kind)[:3], font=F('Inter-Black.otf', int(28 * k)), fill=fg, anchor='mm')

# ---------- mascota y logo ----------
def load_png(f, w):
    p = os.path.join(RAIZ, 'assets', f)
    if not os.path.isfile(p): return None
    im = Image.open(p).convert('RGBA'); return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
M_A = load_png('sumiago-a.png', 430); M_C = load_png('sumiago-c.png', 430); M_PUL = load_png('mascota-pulgar.png', 430)
LOGO = load_png('logo-sumiago.png', 600); LOGO_S = load_png('logo-sumiago.png', 220)
def mascot(im, x, y, t, talk=True, pulgar=False, a=1.0, flip=False):
    m = M_PUL if pulgar else (M_A if (talk and lv(t) > .035) else M_C)
    if m is None: return
    if flip: m = m.transpose(Image.FLIP_LEFT_RIGHT)
    bob = math.sin(t * 4) * 5
    if a < 1: m = m.copy(); m.putalpha(m.getchannel('A').point(lambda p: int(p * a)))
    im.alpha_composite(m, (int(x - m.width / 2), int(y - m.height + bob)))
def amigo(im, x, y, t, talk, a=1.0):
    """Segundo personaje (no oficial de la marca, sin logo): figura redonda sencilla."""
    if a <= 0: return
    L = Image.new('RGBA', (300, 420), (0, 0, 0, 0)); d = ImageDraw.Draw(L); chica = G.get('personaje_b') == 'amiga'
    if chica: d.rounded_rectangle((52, 90, 248, 330), 60, fill=(92, 58, 40))  # cabello largo
    d.rounded_rectangle((60, 220, 240, 420), 70, fill=(40, 160, 160) if chica else (40, 90, 170)); d.ellipse((70, 60, 230, 230), fill=(232, 190, 160) if chica else (170, 120, 90))
    d.chord((64, 40, 236, 170), 180, 360, fill=(40, 170, 170) if chica else (30, 26, 26)); d.rectangle((64, 104, 236, 112), fill=(240, 240, 240) if chica else (30, 26, 26))
    for ex in (118, 182): d.ellipse((ex - 11, 140, ex + 11, 162), fill=(30, 26, 26))
    op = talk and lv(t) > .035
    d.ellipse((130, 185 - (6 if op else 1), 170, 185 + (10 if op else 3)), fill=(120, 40, 40))
    if a < 1: L.putalpha(L.getchannel('A').point(lambda p: int(p * a)))
    im.alpha_composite(L, (int(x - 150), int(y - 420 + math.sin(t * 4 + 1) * 5)))

# ---------- subtítulos (abajo, mayúsculas, palabra por palabra con máscara) ----------
CAP_Y = 1060
def caption(im, t):
    if not G.get('subtitulos', True): return
    ci = None
    for i, c in enumerate(CL):
        if c['t0'] - 0.05 <= t <= c['t0'] + c['d'] + 0.25: ci = i
    if ci is None: return
    tp = G['frases'][ci]['escena'].get('tipo')
    if tp in ('dialogo', 'mascota') or G['frases'][ci]['escena'].get('sin_subtitulo'): return
    cy = 640 if tp == 'cierre' else CAP_Y
    ws = [(w, tw) for w, tw in WT[ci] if tw <= t]
    if not ws: return
    d = ImageDraw.Draw(im)
    # grupos de 3 a 4 palabras (como los reels): se muestra el grupo actual
    grp = []; cur = []
    for w, tw in WT[ci]:
        cur.append((w, tw))
        if len(cur) >= 4 or w[-1] in '.,?!:…': grp.append(cur); cur = []
    if cur: grp.append(cur)
    g = next((g for g in grp if g[0][1] <= t and (g is grp[-1] or grp[grp.index(g) + 1][0][1] > t)), grp[0])
    txt = [w.upper().strip('«»"') for w, _ in g]; sz = 40
    while sz > 26 and d.textlength(' '.join(txt), font=F('Inter-Black.otf', sz)) > 640: sz -= 2
    f = F('Inter-Black.otf', sz); tws = [d.textlength(w + ' ', font=f) for w in txt]; x = W / 2 - (sum(tws) - d.textlength(' ', font=f)) / 2
    band = Image.new('RGBA', (W, 70), (0, 0, 0, 0)); bd = ImageDraw.Draw(band)
    for (w, tw), s, lw in zip(g, txt, tws):
        q = ease((t - tw) / 0.2)
        if q > 0:
            col = RED if is_key(w) else INK
            bd.text((x, 8 + (1 - q) * 64), s, font=f, fill=col + (255,))
        x += lw
    if not CLARO:
        shd = Image.new('RGBA', (W, 70), (0, 0, 0, 0)); shd.putalpha(band.getchannel('A').filter(ImageFilter.GaussianBlur(6)))
        im.alpha_composite(shd, (0, cy))
    im.alpha_composite(band, (0, cy))

def header(im):
    d = ImageDraw.Draw(im); f = F('Inter-Black.otf', 20); tw = d.textlength('SUMIAGO', font=f)
    d.rounded_rectangle((W / 2 - tw / 2 - 22, 46, W / 2 + tw / 2 + 34, 84), 19, fill=(20, 20, 24) if CLARO else (255, 255, 255))
    d.text((W / 2 - 6, 65), 'SUMIAGO', font=f, fill=(255, 255, 255) if CLARO else (20, 20, 24), anchor='mm'); d.ellipse((W / 2 + tw / 2 + 8, 59, W / 2 + tw / 2 + 20, 71), fill=RED)

# ---------- cámara y objetos para transformar ----------
CAM = {'x0': 0, 'y0': 0, 'z': 1}
OBJ = {}
def camera(im, z, cx=W / 2, cy=H / 2):
    w, h = W / z, H / z; x0 = min(max(cx - w / 2, 0), W - w); y0 = min(max(cy - h / 2, 0), H - h)
    CAM.update(x0=x0, y0=y0, z=z)
    if z <= 1.001: return im
    return im.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.BILINEAR)
def obj(kind, r):
    OBJ[kind] = tuple((v - (CAM['x0'] if k % 2 == 0 else CAM['y0'])) * CAM['z'] for k, v in enumerate(r))

# ---------- escenas ----------
def appear_times(ci, items, key='palabra'):
    """Momento de entrada de cada elemento: su palabra si la tiene; si no, repartidos en la frase (encadenados)."""
    c = CL[ci]; n = len(items); out = []
    for k, it in enumerate(items):
        p = it.get(key) if isinstance(it, dict) else None
        t = wt(ci, p) if p else None
        out.append(t if t is not None else c['t0'] + 0.15 + k * max(.25, (c['d'] - .3) / max(1, n)))
    return out

def sc_titulo(im, e, ci, t, lt):
    lines = e.get('lineas') or wrap(e.get('texto', ''), F('Inter-Black.otf', 70), 600); rojo = set(e.get('rojo', [len(lines) - 1]))
    f = F('Inter-Black.otf', int(e.get('tam', 70))); y0 = 560 - len(lines) * f.size * .6 + (e.get('dy', 0))
    if e.get('icono') == 'logo' and LOGO_S: scaled(im, LOGO_S, W / 2, y0 - 150, back_out(lt / .4))
    elif e.get('icono'):
        s = back_out(lt / .4); L = Image.new('RGBA', (200, 200), (0, 0, 0, 0)); icon(ImageDraw.Draw(L), e['icono'], 100, 100, 2.6); scaled(im, L, W / 2, y0 - 150, s)
    for k, l in enumerate(lines):
        mask_text(im, (W / 2, y0 + k * f.size * 1.12), l, f, RED if k in rojo else INK, (lt - .1 - k * .18) / .35)
    if e.get('sub'):
        mask_text(im, (W / 2, y0 + len(lines) * f.size * 1.12 + 30), e['sub'], F('Inter-SemiBold.otf', 32), SUB, (lt - .3 - len(lines) * .18) / .35)
    r = (60, y0 - f.size, 660, y0 + len(lines) * f.size * 1.12); obj('in', r); obj('out', r)
    return camera(im, 1 + .05 * ease(lt / 3), W / 2, 560)

def sc_lista(im, e, ci, t, lt):
    """Un punto numerado: número grande + tarjeta con título, detalle e icono."""
    n = str(e.get('n', '1')); s = back_out(lt / .4)
    L = Image.new('RGBA', (220, 220), (0, 0, 0, 0)); d = ImageDraw.Draw(L); d.ellipse((10, 10, 210, 210), fill=RED)
    d.text((110, 112), n, font=F('Inter-Black.otf', 120 if len(n) < 2 else 80), fill='white', anchor='mm'); scaled(im, L, W / 2, 330, s)
    q = ease((lt - .25) / .4); y = 470 + (1 - q) * 80
    if q > 0:
        r = (60, y, 660, y + 380); card(im, r); d = ImageDraw.Draw(im)
        if e.get('icono'): icon(d, e['icono'], 130, y + 80, 1.3)
        mask_text(im, (190, y + 80), e.get('titulo', ''), F('Inter-Black.otf', 38), INK, (lt - .4) / .35, anchor='l')
        f = F('Inter-Medium.otf', 30)
        for k, l in enumerate(wrap(e.get('detalle', ''), f, 520)[:5]):
            mask_text(im, (100, y + 170 + k * 44), l, f, SUB, (lt - .6 - k * .15) / .35, anchor='l')
    obj('in', (W / 2 - 100, 230, W / 2 + 100, 430)); obj('out', (60, 470, 660, 850))
    return camera(im, 1 + .08 * ease(lt / 2.5), W / 2, lerp(500, 640, ease(lt / 2.5)))

def sc_tarjetas(im, e, ci, t, lt):
    items = e['items']; n = len(items); cols = 2 if n in (2, 4) else 3 if n >= 3 else 1
    rows = (n + cols - 1) // cols; cw = (600 - (cols - 1) * 20) / cols; ch = 170 if rows > 2 else 210
    y0 = 560 - (rows * ch + (rows - 1) * 20) / 2; T = appear_times(ci, items); last = (W / 2, 560)
    if e.get('titulo'): mask_text(im, (W / 2, y0 - 70), e['titulo'], F('Inter-Black.otf', 44), INK, lt / .35)
    for k, it in enumerate(items):
        it = it if isinstance(it, dict) else {'t': it}
        x = 60 + (k % cols) * (cw + 20); y = y0 + (k // cols) * (ch + 20); s = back_out((t - T[k]) / .35)
        if s <= 0.02: continue
        L = Image.new('RGBA', (int(cw) + 40, int(ch) + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        hot = 0 < t - T[k] < .7
        d.rounded_rectangle((20, 20, cw + 20, ch + 20), 22, fill=CARD, outline=RED if hot else LINE, width=4 if hot else 2)
        icon(d, it.get('i', 'check'), cw / 2 + 20, 20 + ch * .4, 1.2)
        f = F('Inter-Black.otf', 26 if cols == 3 else 30); lines = wrap(it['t'], f, cw - 30)
        for j, l in enumerate(lines[:2]): d.text((cw / 2 + 20, 20 + ch * .72 + j * 30 - (len(lines[:2]) - 1) * 15), l, font=f, fill=INK, anchor='mm')
        shadow(im, (x, y, x + cw, y + ch), 22, int(100 * min(1, s))); scaled(im, L, x + cw / 2, y + ch / 2, s); last = (x + cw / 2, y + ch / 2)
    r = (60, y0, 660, y0 + rows * ch + (rows - 1) * 20); obj('in', r); obj('out', r)
    return camera(im, 1 + .1 * ease(lt / 1.5), lerp(W / 2, last[0], .35), lerp(560, last[1], .35))

def phone_frame(im, cx, cy, s, title, fill_fn):
    w, h = 330 * s, 660 * s; r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2); shadow(im, r, 48 * s, 140, 20)
    d = ImageDraw.Draw(im); d.rounded_rectangle(r, 48 * s, fill=(18, 18, 22), outline=(80, 82, 92), width=5)
    sc = (r[0] + 12 * s, r[1] + 12 * s, r[2] - 12 * s, r[3] - 12 * s); d.rounded_rectangle(sc, 38 * s, fill=(250, 250, 252))
    d.rounded_rectangle((cx - 44 * s, r[1] + 22 * s, cx + 44 * s, r[1] + 46 * s), 12 * s, fill=(18, 18, 22))
    d.rectangle((sc[0], sc[1] + 60 * s, sc[2], sc[1] + 120 * s), fill=RED); d.text((cx, sc[1] + 90 * s), title, font=F('Inter-Black.otf', int(24 * s)), fill='white', anchor='mm')
    fill_fn(d, sc); return r

def sc_telefono(im, e, ci, t, lt):
    rows = e.get('filas', []); T = appear_times(ci, rows); s = 1.0
    def fill(d, sc):
        for k, it in enumerate(rows):
            it = it if isinstance(it, dict) else {'t': it}
            q = back_out((t - T[k]) / .3)
            if q <= 0: continue
            y = sc[1] + 140 + k * 64; x0, x1 = sc[0] + 18, sc[2] - 18; xm = (x0 + x1) / 2; hw = (x1 - x0) / 2 * q
            d.rounded_rectangle((xm - hw, y, xm + hw, y + 50), 14, fill=RED if it.get('rojo') else (238, 238, 242))
            if q > .6: d.text((xm, y + 25), it['t'], font=F('Inter-Bold.otf', 21), fill='white' if it.get('rojo') else (30, 30, 36), anchor='mm')
        if e.get('boton'):
            q = back_out((t - (wt(ci, e.get('boton_palabra')) or (CL[ci]['t0'] + CL[ci]['d'] * .7))) / .3)
            if q > 0: d.rounded_rectangle((sc[0] + 40, sc[3] - 90, sc[2] - 40, sc[3] - 40), 25, fill=GREEN); d.text(((sc[0] + sc[2]) / 2, sc[3] - 65), e['boton'], font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
    a = ease(lt / .35); y = 600 + (1 - a) * 200
    r = phone_frame(im, W / 2, y, s, e.get('titulo', 'Sumiago'), fill)
    k = sum(1 for x in T if x <= t); fy = r[1] + 152 + max(0, k - 1) * 64
    obj('in', r); obj('out', r)
    return camera(im, 1 + .25 * ease((lt - .4) / .8), W / 2, lerp(600, fy, ease((lt - .4) / .8)))

def sc_dato(im, e, ci, t, lt):
    v = str(e.get('valor', '')); q = ease((lt - .1) / max(.4, min(1.2, CL[ci]['d'] * .5)))
    num = ''.join(ch for ch in v if ch.isdigit())
    if e.get('conteo', True) and num:
        cur = int(int(num) * q); s = f'{cur:,}'.replace(',', '.') if '.' in v or ',' in v else str(cur)
        pre = v[:len(v) - len(v.lstrip('$'))]; suf = v[len(v.rstrip(' %+xX')):]
        txt = pre + s + suf
    else: txt = v
    sz = 150; full = v if len(v) >= len(txt) else txt
    while sz > 50 and ImageDraw.Draw(BG).textlength(full, font=F('Inter-Black.otf', sz)) > 600: sz -= 6
    sc = back_out(lt / .4); L = Image.new('RGBA', (700, 260), (0, 0, 0, 0)); f = F('Inter-Black.otf', sz)
    ImageDraw.Draw(L).text((350, 130), txt, font=f, fill=RED, anchor='mm'); scaled(im, L, W / 2, 520, sc)
    mask_text(im, (W / 2, 680), e.get('etiqueta', ''), F('Inter-Bold.otf', 40), INK, (lt - .35) / .35)
    if e.get('sub'): mask_text(im, (W / 2, 740), e['sub'], F('Inter-Medium.otf', 30), SUB, (lt - .5) / .35)
    obj('in', (100, 420, 620, 620)); obj('out', (100, 420, 620, 620))
    return camera(im, 1 + .12 * ease(lt / 2), W / 2, 560)

def sc_comparacion(im, e, ci, t, lt):
    A, B = e['a'], e['b']; TA = wt(ci, A.get('palabra')) or CL[ci]['t0'] + .1; TB = wt(ci, B.get('palabra')) or CL[ci]['t0'] + CL[ci]['d'] * .5
    focus = W / 2
    for k, (it, T0) in enumerate(((A, TA), (B, TB))):
        q = back_out((t - T0) / .4)
        if q <= 0: continue
        x = 55 + k * 320; mal = it.get('mal', k == 0)
        L = Image.new('RGBA', (330, 520), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
        d.rounded_rectangle((15, 15, 305, 505), 24, fill=CARD2 if mal else CARD, outline=(150, 150, 160) if mal else RED, width=4)
        icon(d, it.get('i', 'persona'), 160, 120, 2.0, col=(120, 120, 130) if mal else RED)
        d.text((160, 230), it.get('t', ''), font=F('Inter-Black.otf', 38), fill=INK, anchor='mm')
        f = F('Inter-Medium.otf', 25)
        for j, l in enumerate(wrap(it.get('d', ''), f, 250)[:6]): d.text((160, 285 + j * 34), l, font=f, fill=SUB, anchor='mm')
        d.rounded_rectangle((60, 440, 260, 485), 22, fill=(150, 150, 160) if mal else GREEN); d.text((160, 462), it.get('res', 'NO' if mal else 'SÍ'), font=F('Inter-Black.otf', 22), fill='white', anchor='mm')
        shadow(im, (x, 300, x + 290, 790), 24, int(100 * min(1, q))); scaled(im, L, x + 145, 545, q); focus = x + 145
    if t > TB - .1: ImageDraw.Draw(im).ellipse((W / 2 - 34, 510, W / 2 + 34, 578), fill=INK); ImageDraw.Draw(im).text((W / 2, 545), 'VS', font=F('Inter-Black.otf', 26), fill=(255, 255, 255) if CLARO else (20, 20, 24), anchor='mm')
    obj('in', (75, 300, 365, 790)); obj('out', (385, 300, 675, 790))
    return camera(im, 1 + .05 * ease(lt / 2), lerp(W / 2, focus, .12), 560)

def sc_linea(im, e, ci, t, lt):
    """Línea de tiempo / barras que se suman (ej.: años de estudio)."""
    items = e['items']; T = appear_times(ci, items); mx = max(float(it.get('v', 1)) for it in items); y0 = 330; last = y0
    if e.get('titulo'): mask_text(im, (W / 2, 260), e['titulo'], F('Inter-Black.otf', 40), INK, lt / .35)
    for k, it in enumerate(items):
        q = ease((t - T[k]) / .45)
        if q <= 0: continue
        y = y0 + k * 110; d = ImageDraw.Draw(im)
        mask_text(im, (80, y + 20), it['t'], F('Inter-Bold.otf', 30), INK, q, anchor='l')
        bw = 560 * float(it.get('v', 1)) / mx * q
        d.rounded_rectangle((80, y + 50, 640, y + 86), 18, fill=LINE); d.rounded_rectangle((80, y + 50, 80 + max(36, bw), y + 86), 18, fill=RED)
        d.text((640, y + 20), it.get('etq', ''), font=F('Inter-Black.otf', 28), fill=RED, anchor='rm'); last = y
    if e.get('total'):
        q = back_out((t - (wt(ci, e.get('total_palabra')) or T[-1] + .6)) / .4)
        if q > 0:
            L = Image.new('RGBA', (600, 130), (0, 0, 0, 0)); d = ImageDraw.Draw(L); d.rounded_rectangle((0, 0, 600, 130), 26, fill=RED)
            d.text((300, 65), e['total'], font=F('Inter-Black.otf', 44), fill='white', anchor='mm'); scaled(im, L, W / 2, y0 + len(items) * 110 + 80, q); last = y0 + len(items) * 110 + 80
    obj('in', (60, 300, 660, 900)); obj('out', (60, 300, 660, 900))
    return camera(im, 1 + .15 * ease(lt / 2), W / 2, lerp(560, last, .4))

def bubble(im, x, y, txt, q, right=False, col=None, maxw=470):
    if q <= 0: return 0
    f = F('Inter-SemiBold.otf', 30); lines = wrap(txt, f, maxw - 50)[:5]; d0 = ImageDraw.Draw(im)
    bw = int(max(d0.textlength(l, font=f) for l in lines) + 50); bh = int(len(lines) * 40 + 30)
    col = col or (RED if right else CARD)
    L = Image.new('RGBA', (bw + 20, bh + 30), (0, 0, 0, 0)); d = ImageDraw.Draw(L); d.rounded_rectangle((10, 0, bw + 10, bh), 26, fill=col, outline=None if right else LINE, width=2)
    tx = bw - 16 if right else 30; d.polygon([(tx, bh - 2), (tx + 18, bh - 2), (tx + (22 if right else -4), bh + 22)], fill=col)
    for k, l in enumerate(lines): d.text((35, 18 + k * 40), l, font=f, fill='white' if right else INK)
    s = back_out(q / .3); L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))), Image.LANCZOS)
    im.alpha_composite(L, (int(x - (L.width if right else 0)), int(y - L.height))); return bh + 30

def sc_dialogo(im, e, ci, t, lt):
    """Conversación: personaje A (mascota) a la izquierda y B (amigo, sin logo) a la derecha; muestra la frase actual y la anterior."""
    quien = e.get('quien', 'A'); prev = None
    if ci > 0 and G['frases'][ci - 1]['escena'].get('tipo') == 'dialogo': prev = G['frases'][ci - 1]
    talkA = quien == 'A'; mascot(im, 190, 1040, t, talk=talkA, a=1.0 if talkA else .85)
    amigo(im, 540, 1030, t, talk=not talkA, a=1.0 if not talkA else .85)
    y = 640
    if prev and lt < 1.2:
        pq = 1 - ease((lt - .6) / .6); pr = prev['escena'].get('quien', 'A') == 'B'
        if pq > 0: bubble(im, 680 if pr else 40, 380, prev['texto'], 1, right=pr, col=(CARD2 if not pr else mix(RED, CARD, .4)))
    right = quien == 'B'; bubble(im, 680 if right else 40, y, e.get('burbuja', G['frases'][ci]['texto']), lt - .05, right=right)
    obj('in', (40, 380, 680, 660)); obj('out', (40, 380, 680, 660))
    return camera(im, 1 + .06 * ease(lt / 2), 190 if talkA else 540, 700)

def sc_mascota(im, e, ci, t, lt):
    mascot(im, W / 2, 1050, t, talk=True)
    if e.get('burbuja'): bubble(im, 60, 560, e['burbuja'], lt - .1, maxw=600)
    obj('in', (160, 560, 560, 1050)); obj('out', (160, 560, 560, 1050))
    return camera(im, 1 + .05 * ease(lt / 2), W / 2, 700)

def sc_cierre(im, e, ci, t, lt):
    a = ease(lt / .4); y = 360 + (1 - a) * 40
    if LOGO_S: scaled(im, LOGO_S, W / 2, y + 10, a)
    f = F('Inter-Black.otf', 40)
    for k, l in enumerate(wrap(e.get('texto', 'Regístrate en Sumiago'), f, 600)[:3]):
        mask_text(im, (W / 2, y + 120 + k * 52), l, f, INK, (lt - .2 - k * .15) / .35)
    mascot(im, 180, H + 40, t, pulgar=True)
    tb = wt(ci, e.get('boton_palabra', 'link')) or wt(ci, 'enlace') or (CL[ci]['t0'] + CL[ci]['d'] * .55)
    q = t - tb
    if q > 0:
        bx = 1 + .05 * math.sin(t * 7); b = back_out(q / .35); cx, cy = 470, 900; d = ImageDraw.Draw(im)
        d.rounded_rectangle((cx - 210 * bx * b, cy - 44 * bx * b, cx + 210 * bx * b, cy + 44 * bx * b), 44, fill=RED)
        if b > .5: d.text((cx, cy), e.get('boton', 'LINK EN MI PERFIL'), font=F('Inter-Black.otf', 28), fill='white', anchor='mm')
        ay = cy + 64 + 10 * math.sin(t * 8); d.polygon([(cx - 22, ay), (cx + 22, ay), (cx, ay + 30)], fill=RED)
    obj('in', (60, 300, 660, 560)); obj('out', (100, 280, 620, 480))
    return camera(im, 1.0, W / 2, H / 2)

SC = {'titulo': sc_titulo, 'lista': sc_lista, 'tarjetas': sc_tarjetas, 'telefono': sc_telefono, 'dato': sc_dato,
      'comparacion': sc_comparacion, 'linea': sc_linea, 'dialogo': sc_dialogo, 'mascota': sc_mascota, 'cierre': sc_cierre}

# ---------- cierre con logo ----------
def end_scene(lt, t):
    bgc = (255, 255, 255)
    im = Image.new('RGBA', (W, H), bgc + (255,)); ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cy = 600
    for k in range(3):
        q = (lt - .3 - k * .35) / 1.4
        if 0 < q < 1: r = 120 + q * 520; d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), outline=RED + (int(170 * (1 - q)),), width=6)
    rnd = random.Random(5)
    for k in range(26):
        q = (lt - .3) / 1.1
        if 0 < q < 1:
            a = rnd.random() * 2 * math.pi; sp = 220 + rnd.random() * 320; r = 6 + rnd.random() * 8
            x = W / 2 + math.cos(a) * sp * ease(q); y = cy + math.sin(a) * sp * ease(q) + 80 * q * q
            col = RED if k % 3 else (40, 40, 46); d.ellipse((x - r * (1 - q), y - r * (1 - q), x + r * (1 - q), y + r * (1 - q)), fill=col + (int(255 * (1 - q)),))
    im.alpha_composite(ov)
    sc = back_out((lt - .15) / .55) if lt > .15 else 0
    if sc > .02 and LOGO:
        fl = 1 + .025 * math.sin(max(0, lt - 1) * 3); lw, lh = int(LOGO.width * sc * fl), int(LOGO.height * sc * fl)
        lg = LOGO.resize((max(1, lw), max(1, lh)), Image.LANCZOS); q = (lt - .9) / .7
        if 0 < q < 1:
            band = Image.new('L', lg.size, 0); bd = ImageDraw.Draw(band); bx = -200 + q * (lw + 400)
            bd.polygon([(bx, 0), (bx + 70, 0), (bx - 50, lh), (bx - 120, lh)], fill=200)
            m = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(12)), lg.getchannel('A'))
            wl = Image.new('RGBA', lg.size, (255, 255, 255, 0)); wl.putalpha(m); lg = Image.alpha_composite(lg, wl)
        im.alpha_composite(lg, ((W - lw) // 2, cy - lh // 2))
    a = ease((lt - 1.0) / .5)
    if a > 0:
        mask_text(im, (W // 2, 800), G.get('cierre_texto', 'Aprende y crece con Sumiago'), F('Inter-Bold.otf', 36), (60, 60, 68), a)
        d = ImageDraw.Draw(im); bx = 1 + .04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 940 - 38 * bx, W / 2 + 250 * bx, 940 + 38 * bx), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 940), G.get('cierre_boton', 'LINK EN MI PERFIL'), font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

# ---------- transformación entre escenas ----------
LOGO_RECT = (60, 500, 660, 700); TR = .3
def scene_at(i, t):
    OBJ.clear(); CAM.update(x0=0, y0=0, z=1)
    if i == len(CL):
        OBJ['in'] = LOGO_RECT; return end_scene(max(0, t - LOGO_T), t), dict(OBJ)
    e = G['frases'][i]['escena']; im = BG.copy(); header(im)
    im = SC[e.get('tipo', 'titulo')](im, e, i, t, max(0, t - ST[i]))
    if e.get('aviso'):  # aviso legal pequeño (ej.: ejemplo ilustrativo, no garantiza ingresos)
        f = F('Inter-Medium.otf', 20)
        for k, l in enumerate(wrap(e['aviso'], f, 620)): ImageDraw.Draw(im).text((W / 2, 975 + k * 26), l, font=f, fill=SUB, anchor='mm')
    return im, dict(OBJ)
def rr_mask(size, rad):
    m = Image.new('L', size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, size[0] - 1, size[1] - 1), rad, fill=255); return m
def morph(A, ra, B, rb, p):
    e = ease(p); bk = math.sin(math.pi * p) * .06
    r = [lerp(a, b, e) for a, b in zip(ra, rb)]; cx, cy = (r[0] + r[2]) / 2, (r[1] + r[3]) / 2; w = (r[2] - r[0]) * (1 + bk); h = (r[3] - r[1]) * (1 + bk)
    r = (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
    base = Image.blend(A.filter(ImageFilter.GaussianBlur(8 * e)), B.filter(ImageFilter.GaussianBlur(8 * (1 - e))), e)
    clamp = lambda q: (max(0, int(q[0])), max(0, int(q[1])), min(W, max(int(q[0]) + 2, int(q[2]))), min(H, max(int(q[1]) + 2, int(q[3]))))
    sz = (max(2, int(r[2] - r[0])), max(2, int(r[3] - r[1])))
    ca = A.crop(clamp(ra)).resize(sz, Image.BILINEAR); cb = B.crop(clamp(rb)).resize(sz, Image.BILINEAR)
    piece = Image.blend(ca, cb, ease((p - .25) / .5)); piece.putalpha(rr_mask(sz, 18))
    base.alpha_composite(glow(lambda d: d.rounded_rectangle((r[0] + 8, r[1] + 16, r[2] + 8, r[3] + 16), 20, fill=255), (0, 0, 0), 14, int(120 * math.sin(math.pi * p))))
    base.alpha_composite(piece, (int(r[0]), int(r[1]))); return base

def frame(f):
    t = f / FPS; i = 0
    for k, s0 in enumerate(ST):
        if t >= s0: i = k
    nxt = i + 1 if i + 1 < len(ST) and ST[i + 1] - t < TR else None
    prv = i if i > 0 and t - ST[i] < TR else None
    b = nxt if nxt is not None else prv
    if b is not None and not G['frases'][min(b, len(CL) - 1)]['escena'].get('sin_transicion') and not (b < len(CL) and G['frases'][b]['escena'].get('tipo') == 'dialogo' and G['frases'][b - 1]['escena'].get('tipo') == 'dialogo'):
        p = (t - (ST[b] - TR)) / (2 * TR)
        A, oa = scene_at(b - 1, min(t, ST[b] - .001)); B, ob = scene_at(b, max(t, ST[b]))
        im = morph(A, oa.get('out', (0, 0, W, H)), B, ob.get('in', (0, 0, W, H)), p)
    else:
        im, _ = scene_at(i, t)
    if i < len(CL): im.alpha_composite(VIG); caption(im, t)
    return im.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'still':
        for s in sys.argv[2:]: frame(int(float(s) * FPS)).save(f'still_{s}.jpg', quality=90)
        sys.exit()
    a, b, out = int(sys.argv[1]), min(int(sys.argv[2]), NF), sys.argv[3]
    p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-vf', 'scale=1080:1920:flags=lanczos,format=yuv420p', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', out + '.tmp.mp4'], stdin=subprocess.PIPE)
    for k in range(a, b): p.stdin.write(frame(k).tobytes())
    p.stdin.close(); p.wait()
    if p.returncode == 0: os.replace(out + '.tmp.mp4', out)
