"""Arma el video del Día 1 "Hoy es el lanzamiento: ¿pesimista o positivo?" (9:16, 1080x1920, 30 fps, unos 60 s).
Fondo claro, la mascota Sumiago (positivo) frente al pesimista con su nube de lluvia, subtítulos arriba con la palabra
que suena en rojo, música y efectos.
Uso (en la carpeta donde están voice.wav, durs.json, mascot_clean.png, pesimista.png y mix.wav):
    python scripts/render.py test 0.5 3 6 12 30 50     -> test.jpg con cuadros de muestra
    python scripts/render.py full                       -> dia-01.mp4 (usa mix.wav: voz + música + efectos)
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import base as B
from base import W, H, FPS, font, txt_c, glow, ease, stand, scene, durs, YEL, RED, WHITE

AQUI = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(AQUI, '..', 'assets')
TAIL = 1.6
TOTAL = sum(durs) + TAIL
S = B.starts
DARK = (25, 25, 30); GREEN = (34, 160, 80); GRAY_BG = (232, 232, 236); WINE = (110, 10, 18)

def vgrad(c0, c1):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c0) * (1 - y) + np.array(c1) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1)).convert('RGBA')
BG = vgrad((255, 255, 255), (238, 238, 243))
BG_GRIS = vgrad((236, 236, 240), (205, 206, 212))

def cargar(nombre, ancho):
    im = Image.open(nombre).convert('RGBA'); bb = im.getbbox(); im = im.crop(bb)
    return im.resize((ancho, int(ancho * im.height / im.width)), Image.LANCZOS)
PES = Image.open('pesimista.png').convert('RGBA'); PES = PES.crop(PES.getbbox())
PULGAR = cargar(os.path.join(ASSETS, 'mascota-pulgar.png'), 420)
LOGO = cargar(os.path.join(ASSETS, 'logo-sumiago.png'), 560)
_pc = {}
def pes(ancho):
    if ancho not in _pc: _pc[ancho] = PES.resize((ancho, int(ancho * PES.height / PES.width)), Image.LANCZOS)
    return _pc[ancho]

def pop(t0, t, dur=0.35):
    u = (t - t0) / dur
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return ease(u * 2) * 1.15 if u < 0.5 else 1 + 0.15 * (1 - u) * 2
def put(img, im, cx, cy, s=1.0):
    if s <= 0.01: return
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))

def pill(img, cx, cy, txt, fill=RED, tc=WHITE, size=60, s=1.0, rot=0, borde=None):
    """Etiqueta tipo cartel (EL PESIMISTA, LANZAMIENTO...), con aparición elástica s y giro rot."""
    if s <= 0.01: return
    f = font(size); tw = ImageDraw.Draw(img).textlength(txt, font=f); pw, ph = int(tw + size * 0.9), int(size * 1.5)
    lay = Image.new('RGBA', (pw + 40, ph + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, 20 + pw, 20 + ph], int(size * 0.25), fill=fill, outline=borde, width=6 if borde else 0)
    d.text((20 + pw / 2, 20 + ph / 2), txt, font=f, fill=tc, anchor='mm')
    if rot: lay = lay.rotate(rot, expand=True, resample=Image.BICUBIC)
    put(img, lay, cx, cy, s)

def stamp(img, t0, t, txt, cx=W / 2, cy=1000, size=96, rot=-12):
    s = pop(t0, t, 0.3)
    if s <= 0.01: return
    f = font(size); tw = ImageDraw.Draw(img).textlength(txt, font=f)
    lay = Image.new('RGBA', (int(tw + 160), int(size * 2)), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([20, 20, lay.width - 20, lay.height - 20], 22, outline=RED, width=12, fill=(255, 255, 255, 215))
    d.text((lay.width / 2, lay.height / 2), txt, font=f, fill=RED, anchor='mm')
    put(img, lay.rotate(rot, expand=True, resample=Image.BICUBIC), cx, cy, s * (1 + 0.4 * max(0, 1 - (t - t0) / 0.12)))

def bubble(img, cx, cy, txt, s=1.0, size=46, fill=WHITE, tc=DARK, cola='abajo'):
    if s <= 0.01: return
    f = font(size); tw = ImageDraw.Draw(img).textlength(txt, font=f); pw, ph = int(tw + 70), int(size * 1.7)
    lay = Image.new('RGBA', (pw + 20, ph + 60), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle([10, 10, 10 + pw, 10 + ph], ph // 2, fill=fill, outline=DARK, width=5)
    if cola == 'abajo': d.polygon([(pw * 0.55, 8 + ph), (pw * 0.55 + 46, 8 + ph), (pw * 0.5 + 10, ph + 55)], fill=fill)
    d.text((10 + pw / 2, 10 + ph / 2), txt, font=f, fill=tc, anchor='mm')
    put(img, lay, cx, cy, s)

def nube(img, cx, cy, t, s=1.0, lluvia=True, rayo=False, col=(95, 96, 106)):
    d = ImageDraw.Draw(img)
    if lluvia:
        rnd = random.Random(3)
        for k in range(22):
            x = cx + rnd.uniform(-150, 150) * s; v = rnd.uniform(500, 800); y0 = cy + 60 * s
            y = y0 + ((t * v + rnd.uniform(0, 600)) % (520 * s))
            d.line([(x, y), (x - 8 * s, y + 34 * s)], fill=(110, 140, 200), width=max(2, int(5 * s)))
    for ox, oy, r in ((-95, 10, 85), (0, -30, 110), (100, 10, 85), (-40, 45, 80), (55, 45, 80)):
        d.ellipse([cx + (ox - r) * s, cy + (oy - r) * s, cx + (ox + r) * s, cy + (oy + r) * s], fill=col)
    if rayo and int(t * 6) % 4 == 0:
        x, y = cx + 20 * s, cy + 40 * s
        d.polygon([(x, y), (x + 40 * s, y), (x + 5 * s, y + 90 * s), (x + 45 * s, y + 90 * s), (x - 30 * s, y + 220 * s), (x - 5 * s, y + 120 * s), (x - 45 * s, y + 120 * s)], fill=YEL)

def pesimista(img, cx, base_y, ancho, t, lluvia=True, rayo=False):
    p = pes(ancho); bob = 4 * math.sin(t * 2.2)
    img.alpha_composite(p, (int(cx - p.width / 2), int(base_y - p.height + bob)))
    nube(img, cx, base_y - p.height - 90 * ancho / 520, t, ancho / 520, lluvia, rayo)

def positivo(img, f, t, cx, base_y, s=0.62):
    m = stand(f, t, s); img.alpha_composite(m, (int(cx - m.width / 2), int(base_y - m.height)))

def sol(img, cx, cy, t, r=150, rayos=True):
    if rayos:
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
        for k in range(16):
            a = math.radians(k * 22.5 + t * 12); a2 = a + math.radians(6)
            d.polygon([(cx, cy), (cx + math.cos(a) * 1600, cy + math.sin(a) * 1600), (cx + math.cos(a2) * 1600, cy + math.sin(a2) * 1600)], fill=(255, 220, 110, 110))
        img.alpha_composite(lay)
    glow(img, int(cx), int(cy), int(r * 1.6), (255, 210, 60), 150, 40)
    ImageDraw.Draw(img).ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 214, 40))

def tag(img, cx, cy, txt, rot, s):
    pill(img, cx, cy, txt, DARK, WHITE, 40, s, rot)

def telefono(img, x, y, w, h, t, lt):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], 50, fill=DARK); d.rounded_rectangle([x + 16, y + 16, x + w - 16, y + h - 16], 38, fill=WHITE)
    lg = LOGO.resize((int(w * 0.62), int(w * 0.62 * LOGO.height / LOGO.width)), Image.LANCZOS); img.alpha_composite(lg, (int(x + (w - lg.width) / 2), y + 50))
    d = ImageDraw.Draw(img)
    for k, (txt, col) in enumerate((('Tareas diarias', RED), ('Gana con Marketing', DARK), ('Marketplace', RED), ('Comunidad', DARK))):
        yy = y + 200 + k * 95; d.rounded_rectangle([x + 40, yy, x + w - 40, yy + 72], 18, fill=(246, 246, 248))
        d.ellipse([x + 60, yy + 24, x + 84, yy + 48], fill=col); d.text((x + 100, yy + 36), txt, font=font(30), fill=DARK, anchor='lm')

def engranaje(img, cx, cy, r, ang, col):
    d = ImageDraw.Draw(img); n = 10
    pts = []
    for k in range(n * 2):
        a = ang + k * math.pi / n; rr = r if k % 2 == 0 else r * 0.78
        for da in (-0.12, 0.12): pts.append((cx + math.cos(a + da) * rr, cy + math.sin(a + da) * rr))
    d.polygon(pts, fill=col); d.ellipse([cx - r * 0.62, cy - r * 0.62, cx + r * 0.62, cy + r * 0.62], fill=col)
    d.ellipse([cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.25], fill=WHITE)

def rueda(img, cx, cy, r, ang):
    d = ImageDraw.Draw(img)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=DARK); d.ellipse([cx - r * 0.8, cy - r * 0.8, cx + r * 0.8, cy + r * 0.8], fill=WHITE)
    d.ellipse([cx - r * 0.7, cy - r * 0.7, cx + r * 0.7, cy + r * 0.7], outline=RED, width=int(r * 0.12))
    for k in range(6):
        a = ang + k * math.pi / 3; d.line([(cx, cy), (cx + math.cos(a) * r * 0.7, cy + math.sin(a) * r * 0.7)], fill=RED, width=int(r * 0.08))
    d.ellipse([cx - r * 0.14, cy - r * 0.14, cx + r * 0.14, cy + r * 0.14], fill=RED)

def puerta(img, x, y, abierta, candado):
    d = ImageDraw.Draw(img); w, h = 170, 330
    d.rectangle([x - 10, y - 10, x + w + 10, y + h], fill=(70, 50, 35))
    if abierta > 0.02:
        glow(img, int(x + w / 2), int(y + h / 2), 170, (255, 230, 150), int(160 * abierta), 30); d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + w, y + h], fill=(255, 244, 210))
        ww = int(w * (1 - 0.75 * abierta)); d.polygon([(x, y), (x + ww, y + 18 * abierta), (x + ww, y + h - 18 * abierta), (x, y + h)], fill=(150, 100, 60))
    else:
        d.rectangle([x, y, x + w, y + h], fill=(150, 100, 60)); d.ellipse([x + w - 36, y + h / 2 - 8, x + w - 20, y + h / 2 + 8], fill=YEL)
    if candado:
        cx, cy = x + w / 2, y + h / 2
        d.arc([cx - 26, cy - 60, cx + 26, cy - 8], 180, 360, fill=DARK, width=10); d.rounded_rectangle([cx - 38, cy - 30, cx + 38, cy + 34], 10, fill=DARK)
    txt_c(d, (x + w / 2, y - 64), 'NUEVA', font(26), DARK); txt_c(d, (x + w / 2, y - 36), 'OPORTUNIDAD', font(26), DARK)

def confetti(img, t0, t, n=70, seed=1, cy=1000):
    u = t - t0
    if u < 0 or u > 2.4: return
    d = ImageDraw.Draw(img); rnd = random.Random(seed); cols = [RED, YEL, (37, 190, 90), (60, 140, 255), DARK]
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(500, 1300)
        x = W / 2 + math.cos(a) * v * u; y = cy + math.sin(a) * v * u + 900 * u * u; s = rnd.uniform(10, 20)
        d.rectangle([x - s / 2, y - s / 4, x + s / 2, y + s / 4], fill=cols[k % 5])

def cohete(img, cx, cy, s=1.0):
    d = ImageDraw.Draw(img)
    d.polygon([(cx, cy - 90 * s), (cx + 38 * s, cy - 20 * s), (cx + 38 * s, cy + 70 * s), (cx - 38 * s, cy + 70 * s), (cx - 38 * s, cy - 20 * s)], fill=WHITE, outline=DARK, width=5)
    d.ellipse([cx - 18 * s, cy - 25 * s, cx + 18 * s, cy + 11 * s], fill=RED, outline=DARK, width=4)
    d.polygon([(cx - 38 * s, cy + 20 * s), (cx - 70 * s, cy + 80 * s), (cx - 38 * s, cy + 70 * s)], fill=RED)
    d.polygon([(cx + 38 * s, cy + 20 * s), (cx + 70 * s, cy + 80 * s), (cx + 38 * s, cy + 70 * s)], fill=RED)
    d.polygon([(cx - 24 * s, cy + 72 * s), (cx + 24 * s, cy + 72 * s), (cx, cy + (140 + 30 * random.random()) * s)], fill=(255, 170, 40))

def frame(f):
    t = f / FPS; i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - S[-1]
    dur = durs[i]
    img = BG.copy()
    if i == 0:   # ¡Oye! ¿Sabes qué?
        positivo(img, f, t, W / 2, 1880, 0.95)
        bubble(img, 760, 880, '¡OYE!', pop(0.1, t), 70, YEL, DARK)
    elif i == 1:  # Hoy es el lanzamiento de SUMIAGO
        positivo(img, f, t, W / 2, 1880, 0.72)
        bubble(img, 760, 1080, '¡OYE!', 1, 64, YEL, DARK)
        k = ease(lt / 0.5); d = ImageDraw.Draw(img)
        txt_c(d, (W / 2, 330 + 40 * (1 - k)), 'HOY ES EL', font(54), DARK)
        pill(img, W / 2, 470, 'LANZAMIENTO', RED, WHITE, 72, pop(S[1] + 0.2, t))
        put(img, LOGO, W / 2, 640, pop(S[1] + 0.5, t))
        cohete(img, 860, 420 - 260 * ease((lt - 1.0) / 1.5), 1.0)
    elif i == 2:  # dos tipos: VS
        d = ImageDraw.Draw(img); d.rectangle([0, 380, W, 1150], fill=(78, 78, 84)); d.rectangle([0, 1150, W, H], fill=WINE)
        pesimista(img, W / 2, 1120, 300, t, True)
        glow(img, W // 2, 1650, 330, (255, 120, 40), 140, 50)
        positivo(img, f, t, W / 2, 1900, 0.62)
        d = ImageDraw.Draw(img); s = pop(S[2] + 0.4, t)
        if s > 0:
            r = 80 * s; d.ellipse([W / 2 - r, 1150 - r, W / 2 + r, 1150 + r], fill=DARK, outline=WHITE, width=8)
            txt_c(d, (W / 2, 1150 - 44 * s), 'VS', font(max(10, int(70 * s))), WHITE)
        pill(img, 250, 520, 'PESIMISTA', DARK, WHITE, 40, pop(S[2] + dur * 0.62, t))
        pill(img, 820, 1290, 'POSITIVO', RED, WHITE, 40, pop(S[2] + dur * 0.82, t))
    elif 3 <= i <= 8:  # el pesimista
        img = BG_GRIS.copy()
        if i == 3:
            k = ease(lt / 0.8); pesimista(img, W / 2, 1900, int(420 + 160 * k), t, True)
        else:
            pesimista(img, W / 2, 1900, 580, t, True, rayo=(i == 5))
            pill(img, W / 2, 400, 'EL PESIMISTA', DARK, WHITE, 60, 1 if i > 4 else pop(S[4], t))
        if i == 4:
            bubble(img, 380, 610, 'Eso no es para mí', pop(S[4] + 0.9, t), 42)
            bubble(img, 700, 720, 'No soy bueno para eso', pop(S[4] + 1.9, t), 42)
        if i == 5: stamp(img, S[5] + 0.3, t, '¿OTRA ESTAFA?', W / 2, 620, 84, -10)
        if i == 6:
            stamp(img, -9, t, '¿OTRA ESTAFA?', W / 2, 700, 84, -10)
            bubble(img, W / 2, 540, 'Sin trabajar no se gana nada', pop(S[6] + 0.4, t), 40)
        if i == 7:
            img2 = BG_GRIS.copy(); pesimista(img2, W / 2, 1900, 580, t, True); img = img2
            pill(img, W / 2, 400, 'VIVE ASÍ', DARK, WHITE, 64, pop(S[7], t))
            for k, (tx, a) in enumerate((('SE QUEJA', 0.15), ('LO DEJA PARA MAÑANA', 0.4), ('PONE EXCUSAS', 0.7))):
                pill(img, W / 2, 530 + k * 100, tx, DARK, WHITE, 40, pop(S[7] + dur * a, t), borde=RED)
        if i == 8:
            img2 = BG_GRIS.copy(); pesimista(img2, 420, 1900, 520, t, True); img = img2
            pill(img, W / 2, 400, 'AUTOSABOTAJE', RED, WHITE, 64, pop(S[8], t))
            d = ImageDraw.Draw(img); d.rounded_rectangle([120, 540, 640, 580], 20, fill=(210, 210, 215)); d.rounded_rectangle([120, 540, 150, 580], 20, fill=RED)
            txt_c(d, (380, 600), 'AVANCE: 0%', font(36), DARK)
            ab = ease((lt - 0.4) / 0.6) * (1 - ease((lt - dur * 0.65) / 0.4))
            puerta(img, 800, 620, ab, lt > dur * 0.7)
    elif 9 <= i <= 11:  # el positivo
        sol(img, W / 2, 760, t)
        positivo(img, f, t, W / 2, 1900, 0.72)
        if i == 9:
            pill(img, W / 2, 400, 'EL POSITIVO', RED, WHITE, 62, pop(S[9] + 0.2, t))
            d = ImageDraw.Draw(img)
            if lt > dur * 0.6: txt_c(d, (W / 2, 470), 'OPTIMISTA', font(44), RED)
        else:
            pill(img, W / 2, 400, 'EL POSITIVO' if i == 10 else 'INCANSABLE', RED, WHITE, 62, 1 if i == 10 else pop(S[11], t))
            caida = ease((lt - 0.8) / 1.0) if i == 11 else 0
            for k, (tx, x, y, r, a) in enumerate((('ESTAFAS', 330, 1250, 14, 0.2), ('ENGAÑOS', 780, 1160, -12, 0.45), ('FRAUDES', 340, 1440, -6, 0.7))):
                s = 1 if i == 11 else pop(S[10] + dur * a, t)
                tag(img, x, y + 900 * caida * caida, tx, r + 40 * caida, s)
            if i == 11:
                hs = pop(S[11] + dur * 0.45, t) * (1 + 0.06 * math.sin(t * 8)); d = ImageDraw.Draw(img); hx, hy = 210, 1000
                if hs > 0.02:
                    lay = Image.new('RGBA', (260, 240), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
                    ld.ellipse([20, 20, 130, 130], fill=RED); ld.ellipse([110, 20, 220, 130], fill=RED); ld.polygon([(28, 95), (212, 95), (120, 215)], fill=RED)
                    ld.text((120, 95), 'FE', font=font(54), fill=WHITE, anchor='mm'); put(img, lay, hx, hy, hs)
                pill(img, W / 2, 520, 'UNA NUEVA OPORTUNIDAD', DARK, WHITE, 40, pop(S[11] + dur * 0.78, t))
    elif i == 12:  # voy a conocer / probar
        telefono(img, 300, 480, 480, 820, t, lt)
        d = ImageDraw.Draw(img); fase2 = lt > dur * 0.5
        pill(img, W / 2, 400, 'VOY A PROBAR' if fase2 else 'VOY A CONOCER', RED, WHITE, 56, pop(S[12] + (dur * 0.5 if fase2 else 0.1), t))
        if fase2:
            bx, by = W / 2, 1150; s = pop(S[12] + dur * 0.55, t)
            if s > 0:
                d.rounded_rectangle([bx - 130 * s, by - 40 * s, bx + 130 * s, by + 40 * s], 40, fill=RED); txt_c(d, (bx, by - 26 * s), 'PROBAR', font(max(8, int(42 * s))), WHITE)
            mx = 640 + 40 * math.sin(t * 3); d.ellipse([mx - 60, 1000, mx + 60, 1120], outline=DARK, width=12); d.line([(mx + 42, 1102), (mx + 100, 1170)], fill=DARK, width=16)
        img.alpha_composite(PULGAR.resize((300, int(300 * PULGAR.height / PULGAR.width))), (40, 1460))
    elif i == 13:  # que funcione
        k = ease((lt - 0.6) / 0.8)
        g1 = tuple(int(a + (b - a) * k) for a, b in zip((240, 200, 205), RED)); g2 = tuple(int(a + (b - a) * k) for a, b in zip((205, 205, 210), DARK))
        engranaje(img, 420, 700, 190, t * (0.3 + 2 * k), g1); engranaje(img, 720, 600, 120, -t * (0.5 + 3 * k) + 0.3, g2)
        pill(img, W / 2, 1000, '¡QUE FUNCIONE!', RED, WHITE, 58, pop(S[13] + dur * 0.55, t))
        positivo(img, f, t, W / 2, 1900, 0.62)
    elif i == 14:  # la rueda ya está hecha
        d = ImageDraw.Draw(img); d.rectangle([0, 1450, W, H], fill=(70, 70, 76))
        for k in range(-1, 8): x = (k * 180 - (t * 260) % 180); d.rectangle([x, 1560, x + 90, 1574], fill=WHITE)
        for k in range(4):
            cx = (k * 330 - (t * 60) % 330) + 100; d.ellipse([cx - 90, 1020, cx + 90, 1090], fill=(225, 225, 230))
        pill(img, W / 2, 420, 'LA RUEDA YA ESTÁ HECHA', RED, WHITE, 48, pop(S[14] + 0.1, t))
        rueda(img, 620, 1290, 165, t * 3)
        m = stand(f, t, 0.42); img.alpha_composite(m, (180, 1470 - m.height))
        if lt > dur * 0.45:
            for k, tx in enumerate(('TAREAS', 'DIARIAS')):
                pill(img, 860, 640 + k * 90, tx, DARK, WHITE, 40, pop(S[14] + dur * 0.45 + k * 0.2, t))
    elif i == 15:  # constancia y disciplina: primeros 500 a 1000 USD
        d = ImageDraw.Draw(img)
        pill(img, 330, 450, 'CONSTANCIA', WHITE, DARK, 36, pop(S[15] + dur * 0.15, t), borde=DARK)
        pill(img, 760, 450, 'DISCIPLINA', WHITE, DARK, 36, pop(S[15] + dur * 0.3, t), borde=DARK)
        vals = [18, 30, 45, 62, 82, 100]; x0, yb = 150, 1450
        d.line([(x0 - 20, yb), (900, yb)], fill=DARK, width=4)
        for k, v in enumerate(vals):
            hh = 620 * v / 100 * ease((lt - 0.5 - k * 0.35) / 0.6); x = x0 + k * 125
            col = (150, 200, 160) if k < 5 else (34, 175, 90)
            d.rectangle([x, yb - hh, x + 90, yb], fill=col); txt_c(d, (x + 45, yb + 12), f'M{k + 1}', font(28), DARK)
        if lt > dur * 0.6:
            v = int(522 * ease((lt - dur * 0.6) / 1.0)); txt_c(d, (W / 2, 560), 'SUS PRIMEROS', font(40), DARK)
            pill(img, W / 2, 690, f'${v} USD', (34, 160, 80), WHITE, 84, pop(S[15] + dur * 0.6, t))
        img.alpha_composite(PULGAR.resize((330, int(330 * PULGAR.height / PULGAR.width))), (720, 1480))
        d = ImageDraw.Draw(img); txt_c(d, (W / 2, 1850), 'Los resultados dependen de tu constancia y disciplina.', font(26), (90, 90, 100))
    elif i == 16:  # ¿cuál eres tú?
        pill(img, W / 2, 420, '¿CUÁL ERES TÚ?', DARK, WHITE, 64, pop(S[16] + 0.1, t))
        d = ImageDraw.Draw(img)
        for k, (x, col) in enumerate(((90, (70, 72, 80)), (570, WINE))):
            s = pop(S[16] + 0.3 + k * 0.3, t)
            if s <= 0: continue
            d.rounded_rectangle([x, 560, x + 420, 1300], 34, fill=col, outline=YEL if k else None, width=8 if k else 0)
            if k == 0: img.alpha_composite(pes(300), (x + 60, 1180 - pes(300).height))
            else:
                m = stand(f, t, 0.36); img.alpha_composite(m, (x + 210 - m.width // 2, 1190 - m.height))
            d = ImageDraw.Draw(img); txt_c(d, (x + 210, 1210), 'PESIMISTA' if k == 0 else 'POSITIVO', font(44), WHITE if k == 0 else YEL)
    else:  # 17: lanzamiento + comenta
        put(img, LOGO, W / 2, 560, pop(S[17] + 0.1, t))
        pill(img, W / 2, 760, 'HOY ES EL LANZAMIENTO', RED, WHITE, 52, pop(S[17] + 0.4, t))
        confetti(img, S[17] + 0.3, t, 80, 5, 700)
        if lt > durs[17] * 0.45:
            s = pop(S[17] + durs[17] * 0.45, t) * (1 + 0.04 * math.sin(t * 8)); d = ImageDraw.Draw(img)
            if s > 0:
                d.rounded_rectangle([W / 2 - 300 * s, 880 - 80 * s, W / 2 + 300 * s, 880 + 80 * s], 40, fill=YEL, outline=DARK, width=6)
                txt_c(d, (W / 2, 880 - 66 * s), 'COMENTA', font(max(8, int(40 * s))), DARK); txt_c(d, (W / 2, 880 - 20 * s), 'SUMIAGO', font(max(8, int(64 * s))), RED)
        img.alpha_composite(PULGAR, ((W - PULGAR.width) // 2, H - PULGAR.height - 20))
    # acercamiento rápido al empezar cada escena
    if lt < 0.18 and i > 0:
        z = 1 + 0.06 * (1 - lt / 0.18)
        img = img.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
    caption(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 14, W * min(1, t / TOTAL), H], fill=RED)
    return img.convert('RGB')

def caption(img, t):
    """Subtítulos arriba, de 4 en 4 palabras: negro con borde blanco y la palabra que suena en rojo."""
    d = ImageDraw.Draw(img)
    for ch in B.chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is B.chunks[-1] and t >= ch[0][0]):
            line = ' '.join(w[2] for w in ch); ff = font(62); tw = d.textlength(line, font=ff)
            if tw > W - 100: ff = font(int(62 * (W - 100) / tw)); tw = d.textlength(line, font=ff)
            x = (W - tw) / 2
            for (a, b, w, _) in ch:
                act = a <= t < b + 0.02
                d.text((x, 230 - (6 if act else 0)), w, font=ff, fill=RED if act else DARK, stroke_width=6, stroke_fill=WHITE)
                x += d.textlength(w + ' ', font=ff)
            return

def events():
    """Efectos de sonido (tiempo, tipo, parámetro) que usa audio.py."""
    ev = [(S[k] - 0.12, 'whoosh', 0) for k in range(1, len(durs))]
    ev += [(0.1, 'pop', 700), (S[1] + 0.2, 'stamp', 0), (S[1] + 0.5, 'pop', 900), (S[1] + 1.0, 'riser', 0)]
    ev += [(S[2] + 0.4, 'boom', 0), (S[2] + durs[2] * 0.62, 'pop', 600), (S[2] + durs[2] * 0.82, 'pop', 1000)]
    ev += [(S[4] + 0.9, 'pop', 700), (S[4] + 1.9, 'pop', 800), (S[5] + 0.3, 'stamp', 0), (S[5] + 0.3, 'buzz', 0), (S[6] + 0.4, 'pop', 700)]
    ev += [(S[7] + durs[7] * a, 'pop', 600 + k * 100) for k, a in enumerate((0.15, 0.4, 0.7))] + [(S[8] + durs[8] * 0.7, 'buzz', 0)]
    ev += [(S[9] + 0.2, 'ding', 1318), (S[9] + 0.2, 'riser', 0)] + [(S[10] + durs[10] * a, 'stamp', 0) for a in (0.2, 0.45, 0.7)]
    ev += [(S[11] + 0.1, 'pop', 900), (S[11] + durs[11] * 0.45, 'ding', 1568), (S[11] + durs[11] * 0.78, 'pop', 1000)]
    ev += [(S[12] + durs[12] * 0.5, 'pop', 900), (S[12] + durs[12] * 0.55, 'tap', 0), (S[13] + durs[13] * 0.55, 'stamp', 0)]
    ev += [(S[14] + 0.1, 'pop', 800)] + [(S[15] + 0.5 + k * 0.35, 'pop', 700 + k * 120) for k in range(6)] + [(S[15] + durs[15] * 0.6, 'coin', 0), (S[15] + durs[15] * 0.6 + 0.3, 'coin', 0)]
    ev += [(S[16] + 0.1, 'stamp', 0), (S[16] + 0.3, 'pop', 700), (S[16] + 0.6, 'pop', 1000)]
    ev += [(S[17] + 0.1, 'riser', 0), (S[17] + 0.4, 'cheer', 0), (S[17] + durs[17] * 0.45, 'ding', 2093)]
    return ev

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]
        ims = [frame(int(x * FPS)).resize((300, 533)) for x in ts]
        c = Image.new('RGB', (300 * len(ims), 533))
        for k, im in enumerate(ims): c.paste(im, (k * 300, 0))
        c.save('test.jpg'); print('Listo: test.jpg')
    else:
        n = int(TOTAL * FPS)
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                              '-shortest', '-movflags', '+faststart', 'dia-01.mp4'], stdin=subprocess.PIPE)
        for f in range(n): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait()
        print('Listo: dia-01.mp4')
