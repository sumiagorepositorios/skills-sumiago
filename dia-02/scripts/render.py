"""Arma el video del Día 2 "¿Cuántas horas pierdes en redes?" (3 cambios: crear, usar el celular como herramienta y una hora al día).
Dos formatos con el mismo código:
    móvil 9:16 (1080x1920): gráficos arriba, la mascota grande abajo dentro de un círculo y el subtítulo en un recuadro oscuro;
    PC 16:9 (1920x1080): gráficos a la izquierda, la mascota a la derecha y el subtítulo abajo al centro (diseño propio, no es el móvil estirado).
Uso (en la carpeta donde están voice.wav, durs.json, mascot_clean.png y mix.wav):
    python scripts/render.py test movil 1 5 12 20 35 55     -> test.jpg con cuadros de muestra (o 'test pc ...')
    python scripts/render.py full movil                      -> dia-02.mp4
    python scripts/render.py full pc                         -> dia-02-pc.mp4
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from PIL import Image, ImageDraw, ImageFilter
import base as B
from base import FPS, font, ease, stand, scene, durs, RED, WHITE

AQUI = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(AQUI, '..', 'assets')
TAIL = 1.4
TOTAL = sum(durs) + TAIL
S = B.starts
DARK = (28, 28, 34); GREEN = (34, 170, 90); GOLD = (255, 196, 40); GRIS_T = (110, 110, 120)
CREMA, ROSA, GRIS, NOCHE, ROJO = (251, 245, 238), (249, 222, 222), (236, 236, 241), (30, 30, 36), (226, 8, 18)

# ---------- guion con palabras clave (*así*) ----------
RAW = [l for l in open(os.path.join(AQUI, '..', 'guion.txt'), encoding='utf-8').read().strip().split('\n') if l.strip()]
PAL = []  # por escena: [(palabra, es_clave, t0, t1)]
for i, ln in enumerate(RAW):
    ws, clave = [], False
    for w in ln.split():
        ini = w.startswith('*'); clave = clave or ini; fin = w.rstrip('?.,…:!¡').endswith('*') or w.endswith('*')
        ws.append((w.replace('*', ''), clave)); clave = clave and not fin
    tot = sum(len(w) + 1 for w, _ in ws); t = S[i]; span = durs[i] - 0.3; out = []
    for w, c in ws:
        d = span * (len(w) + 1) / tot; out.append((w, c, t, t + d)); t += d
    PAL.append(out)
TROZOS = []  # subtítulo: trozos de hasta ~44 letras, cortando en la puntuación
for i, ws in enumerate(PAL):
    cur, n = [], 0
    for k, w in enumerate(ws):
        cur.append(w); n += len(w[0]) + 1
        if k == len(ws) - 1 or n > 44 or (w[0][-1] in ',.:?…' and n > 14): TROZOS.append((i, cur)); cur, n = [], 0

# ---------- imágenes ----------
def cargar(nombre, ancho, espejo=False):
    im = Image.open(os.path.join(ASSETS, nombre)).convert('RGBA'); im = im.crop(im.getbbox())
    if espejo: im = im.transpose(Image.FLIP_LEFT_RIGHT)
    return im.resize((ancho, int(ancho * im.height / im.width)), Image.LANCZOS)
LOGO = cargar('logo-sumiago.png', 520)
_mc = {}
def mascota(pose, ancho, f, t):
    """pose: 'f' de frente y hablando (labios), 'l' de lado mirando a la izquierda, 'p' pulgar arriba."""
    if pose == 'f':
        m = stand(f, t, 1.0); r = ancho / m.width
        return m.resize((ancho, int(m.height * r)), Image.LANCZOS)
    k = (pose, ancho)
    if k not in _mc: _mc[k] = cargar('mascota-lado.png' if pose == 'l' else 'mascota-pulgar.png', ancho)  # sin espejo: el logo se leería al revés
    return _mc[k]

# ---------- escenas: fondo, pose y paso (chips de arriba) ----------
#            fondo, pose, paso
ESC = [(CREMA, 'f', 0), (ROSA, 'f', 0), (GRIS, 'l', 0), (NOCHE, 'l', 0), (GRIS, 'l', 0), (CREMA, 'p', 0), (ROSA, 'f', 0),
       (CREMA, 'f', 1), (ROSA, 'l', 1), (GRIS, 'f', 1), (CREMA, 'f', 2), (ROSA, 'f', 2), (ROJO, 'f', 3), (GRIS, 'f', 3),
       (NOCHE, 'l', 4), (GRIS, 'l', 4), (CREMA, 'f', 0), (ROSA, 'f', 0), (GRIS, 'l', 0), (NOCHE, 'l', 0), (ROJO, 'f', 0),
       (CREMA, 'p', 0), (ROSA, 'p', 0)]

def pop(t0, t, dur=0.35):
    u = (t - t0) / dur
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return ease(u * 2) * 1.15 if u < 0.5 else 1 + 0.15 * (1 - u) * 2
def put(img, im, cx, cy, s=1.0):
    if s <= 0.01: return
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def tc(d, xy, s, size, fill=DARK):
    d.text(xy, s, font=font(size), fill=fill, anchor='mm')
def sombra(img, box, r=34, a=60):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).rounded_rectangle([box[0] + 6, box[1] + 14, box[2] + 6, box[3] + 14], r, fill=(0, 0, 0, a))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(16)))
def tarjeta(img, box, r=34, fill=WHITE):
    sombra(img, box, r); ImageDraw.Draw(img).rounded_rectangle(box, r, fill=fill)
def pill(img, cx, cy, txt, fill=RED, col=WHITE, size=46, s=1.0):
    if s <= 0.01: return
    f = font(size); tw = ImageDraw.Draw(img).textlength(txt, font=f); w, h = int(tw + size * 1.1), int(size * 1.6)
    lay = Image.new('RGBA', (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(lay); d.rounded_rectangle([0, 0, w - 1, h - 1], h // 2, fill=fill)
    d.text((w / 2, h / 2), txt, font=f, fill=col, anchor='mm'); put(img, lay, cx, cy, s)
def corazon(d, cx, cy, r, col=RED):
    d.ellipse([cx - r, cy - r * .8, cx + .02, cy + r * .2], fill=col)
    d.ellipse([cx, cy - r * .8, cx + r, cy + r * .2], fill=col); d.polygon([(cx - r * .95, cy - r * .15), (cx + r * .95, cy - r * .15), (cx, cy + r)], fill=col)
def check(d, cx, cy, r, ok=True):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GREEN if ok else RED)
    if ok: d.line([(cx - r * .45, cy), (cx - r * .1, cy + r * .4), (cx + r * .5, cy - r * .35)], fill=WHITE, width=max(3, int(r * .28)), joint='curve')
    else:
        for a, b in (((-1, -1), (1, 1)), ((-1, 1), (1, -1))): d.line([(cx + a[0] * r * .4, cy + a[1] * r * .4), (cx + b[0] * r * .4, cy + b[1] * r * .4)], fill=WHITE, width=max(3, int(r * .28)))
def moneda(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=GOLD, outline=(220, 150, 20), width=max(2, int(r * .12))); tc(d, (cx, cy), '$', int(r * 1.1), (180, 110, 10))
def reloj(d, cx, cy, r, t, borde=RED):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=borde, width=int(r * .14))
    for k in range(12):
        a = k * math.pi / 6; d.line([(cx + math.cos(a) * r * .72, cy + math.sin(a) * r * .72), (cx + math.cos(a) * r * .82, cy + math.sin(a) * r * .82)], fill=DARK, width=max(2, int(r * .04)))
    a1 = t * 2.5 - math.pi / 2; a2 = t * .3 - math.pi / 2
    d.line([(cx, cy), (cx + math.cos(a1) * r * .62, cy + math.sin(a1) * r * .62)], fill=DARK, width=int(r * .06))
    d.line([(cx, cy), (cx + math.cos(a2) * r * .42, cy + math.sin(a2) * r * .42)], fill=DARK, width=int(r * .08)); d.ellipse([cx - r * .07, cy - r * .07, cx + r * .07, cy + r * .07], fill=RED)
def reloj_arena(d, cx, cy, h, col=GOLD, k=0.5):
    w = h * .5; d.rectangle([cx - w / 2 - 10, cy - h / 2 - 14, cx + w / 2 + 10, cy - h / 2], fill=DARK); d.rectangle([cx - w / 2 - 10, cy + h / 2, cx + w / 2 + 10, cy + h / 2 + 14], fill=DARK)
    d.polygon([(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2), (cx, cy)], fill=(245, 245, 248)); d.polygon([(cx - w / 2, cy + h / 2), (cx + w / 2, cy + h / 2), (cx, cy)], fill=(245, 245, 248))
    a = (1 - k) * .9; d.polygon([(cx - w / 2 * a, cy - h / 2 * a), (cx + w / 2 * a, cy - h / 2 * a), (cx, cy)], fill=col)
    b = k * .9; d.polygon([(cx - w / 2 * b, cy + h / 2), (cx + w / 2 * b, cy + h / 2), (cx, cy + h / 2 * (1 - b))], fill=col)
def telefono(img, cx, cy, w, h, t, contenido='feed', velocidad=60):
    sombra(img, (cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), 44, 70); d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], 44, fill=DARK)
    x0, y0, x1, y1 = cx - w / 2 + 14, cy - h / 2 + 14, cx + w / 2 - 14, cy + h / 2 - 14
    scr = Image.new('RGBA', (int(x1 - x0), int(y1 - y0)), (250, 250, 252, 255)); sd = ImageDraw.Draw(scr); sw, sh = scr.size
    if contenido == 'feed':
        cols = [(214, 240, 222), (232, 222, 252), (255, 236, 214), (222, 232, 252), (252, 222, 228)]
        off = (t * velocidad) % (sh * .42)
        for k in range(-1, 4):
            yy = k * sh * .42 - off + 14; sd.rounded_rectangle([14, yy, sw - 14, yy + sh * .38], 22, fill=cols[k % 5])
            sd.polygon([(sw / 2 - 18, yy + sh * .13), (sw / 2 - 18, yy + sh * .25), (sw / 2 + 22, yy + sh * .19)], fill=WHITE)
            corazon(sd, sw - 44, yy + sh * .32, 14)
    elif contenido == 'publicar':
        sd.rounded_rectangle([20, 30, sw - 20, sh * .55], 22, fill=(252, 216, 220))
        sd.polygon([(sw / 2 - 30, sh * .2), (sw / 2 - 30, sh * .38), (sw / 2 + 36, sh * .29)], fill=WHITE)
        sd.rounded_rectangle([sw * .2, sh * .64, sw * .8, sh * .64 + sh * .09], 40, fill=RED); tc(sd, (sw / 2, sh * .685), 'Publicar', int(sh * .045), WHITE)
    elif contenido == 'lista':
        for k, c in enumerate([(252, 216, 220), (222, 232, 252), (214, 240, 222)]): sd.rounded_rectangle([20, 60 + k * sh * .2, sw - 20, 60 + k * sh * .2 + sh * .15], 18, fill=c)
    elif contenido == 'prospectos':
        for k in range(3):
            yy = 40 + k * sh * .22; sd.rounded_rectangle([14, yy, sw - 14, yy + sh * .17], 20, fill=WHITE, outline=(230, 230, 236), width=3)
            sd.ellipse([28, yy + sh * .04, 28 + sh * .09, yy + sh * .13], fill=RED); tc(sd, (sw * .62, yy + sh * .085), 'Nuevo prospecto', int(sh * .042))
    m = Image.new('L', scr.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, sw, sh], 32, fill=255); img.paste(scr, (int(x0), int(y0)), m)
def barras(img, box, titulo, vals, k, etiquetas=None, col_fin=RED, col=(240, 160, 168)):
    tarjeta(img, box, 30); d = ImageDraw.Draw(img); x0, y0, x1, y1 = box
    d.text((x0 + 40, y0 + 46), titulo, font=font(40), fill=DARK, anchor='lm')
    n = len(vals); bw = (x1 - x0 - 120) / n
    for j, v in enumerate(vals):
        q = ease((k * (n + 1) - j) / 1.2); hh = (y1 - y0 - 190) * v * q; x = x0 + 60 + j * bw
        if q <= 0: continue
        d.rounded_rectangle([x + 10, y1 - 70 - hh, x + bw - 10, y1 - 70], 10, fill=col_fin if j == n - 1 else col)
        if etiquetas: tc(d, (x + bw / 2, y1 - 70 - hh - 26), etiquetas[j], 28, RED if j == n - 1 else DARK); tc(d, (x + bw / 2, y1 - 40), f'Mes {j + 1}', 24, GRIS_T)

# ---------- los gráficos de cada escena, en un lienzo de 1080x1000 (centro 540, 500) ----------
GW, GH = 1080, 1000
def grafico(i, lt, t, dur, fondo):
    g = Image.new('RGBA', (GW, GH), (0, 0, 0, 0)); d = ImageDraw.Draw(g); T0 = S[i]
    claro = fondo not in (NOCHE, ROJO)
    if i == 0:
        for k, (tx, caja) in enumerate((('¿Cuántas horas', True), ('pierdes', True), ('en redes?', False))):
            s = pop(T0 + .2 + k * .25, t)
            if s <= 0: continue
            f = font(64); tw = d.textlength(tx, font=f); y = 330 + k * 92
            if caja: d.rectangle([60, y - 42, 60 + tw + 30, y + 42], fill=RED)
            d.text((75, y), tx, font=f, fill=WHITE if caja else DARK, anchor='lm')
        telefono(g, 860, 430, 300, 580, t)
    elif i == 1:
        reloj(d, 540, 400, 230, t * 4)
        pill(g, 540, 760, '+2 HORAS AL DÍA', RED, WHITE, 60, pop(T0 + .5, t))
    elif i == 2:
        s = pop(T0 + .2, t); box = (540 - 230 * s, 160, 540 + 230 * s, 160 + 470 * s)
        if s > .05:
            tarjeta(g, box, 30); d = ImageDraw.Draw(g); d.rounded_rectangle([box[0], box[1], box[2], box[1] + 110 * s], 30, fill=RED); d.rectangle([box[0], box[1] + 70 * s, box[2], box[1] + 110 * s], fill=RED)
            tc(d, (540, box[1] + 56 * s), 'AL AÑO', int(44 * s) + 1, WHITE); tc(d, (540, box[1] + 260 * s), '+1 MES', int(110 * s) + 1); tc(d, (540, box[1] + 380 * s), 'en redes sociales', int(34 * s) + 1, GRIS_T)
    elif i == 3:
        telefono(g, 540, 470, 360, 680, t, velocidad=140)
        rnd = random.Random(4)
        for k in range(8):
            u = (t * .4 + k / 8) % 1; x = 540 + rnd.uniform(-380, 380); corazon(d, x, 900 - u * 800, 34 * (1 - u * .5))
    elif i == 4:
        if lt < dur * .45: reloj_arena(d, 540, 420, 300, GOLD, ease(lt / (dur * .45)))
        else:
            for k, tx in enumerate(('+ $', '+ $$', '+ $$$')):
                s = pop(T0 + dur * .45 + k * .4, t)
                if s <= 0: continue
                y = 200 + k * 190; box = (220, y, 860, y + 150); tarjeta(g, box, 28); d = ImageDraw.Draw(g)
                d.ellipse([260, y + 35, 340, y + 115], fill=GREEN); tc(d, (300, y + 75), '$', 50, WHITE)
                d.text((380, y + 55), 'Nuevo ingreso', font=font(30), fill=GRIS_T, anchor='lm'); d.text((380, y + 102), tx, font=font(46), fill=DARK, anchor='lm')
    elif i == 5:
        barras(g, (140, 120, 940, 760), 'Ejemplo: sueldo mes a mes', [.08, .14, .26, .5, 1], min(1, lt / (dur * .8)), ['$20', '$40', '$80', '$160', '$320'])
        tc(d, (540, 800), 'Ejemplo ilustrativo: los resultados dependen de cada persona', 24, GRIS_T)
    elif i == 6:
        for k in range(3):
            s = pop(T0 + dur * (.25 + .2 * k), t); cx = 260 + k * 280
            if s <= 0: continue
            sz = 210 * s; d.rounded_rectangle([cx - sz / 2, 450 - sz / 2, cx + sz / 2, 450 + sz / 2], 40, fill=DARK); tc(d, (cx, 450), str(k + 1), int(130 * s) + 1, WHITE)
    elif i == 7:
        for k, (tx, ok) in enumerate((('Consumir', False), ('Crear', True))):
            s = pop(T0 + .3 + k * dur * .4, t); cx = 330 + k * 420
            if s <= 0: continue
            box = (cx - 170 * s, 300 - 130 * s, cx + 170 * s, 300 + 130 * s); tarjeta(g, box, 30); d = ImageDraw.Draw(g)
            tc(d, (cx, 300), tx, int(54 * s) + 1); check(d, cx + 150 * s, 300 - 130 * s, 46 * s, ok)
    elif i == 8:
        telefono(g, 420, 480, 330, 620, t, velocidad=220); reloj(d, 800, 360, 130, t * 6)
        pill(g, 800, 560, '- tiempo', RED, WHITE, 40, pop(T0 + .6, t))
    elif i == 9:
        telefono(g, 470, 480, 340, 640, t, 'publicar')
        for k in range(3):
            s = pop(T0 + .6 + k * .35, t)
            if s > 0: moneda(d, 800, 260 + k * 150, 56 * s)
    elif i == 10:
        telefono(g, 440, 480, 330, 620, t, 'lista')
        a = math.radians(-35 + 10 * math.sin(t * 4)); cx, cy = 800, 360
        d.line([(cx - math.cos(a) * 170, cy - math.sin(a) * 170), (cx + math.cos(a) * 120, cy + math.sin(a) * 120)], fill=(140, 140, 150), width=36)
        ex, ey = cx + math.cos(a) * 140, cy + math.sin(a) * 140; d.ellipse([ex - 62, ey - 62, ex + 62, ey + 62], fill=(140, 140, 150)); d.ellipse([ex - 26, ey - 26, ex + 26, ey + 26], fill=(0, 0, 0, 0))
        pill(g, 540, 880, 'HERRAMIENTA', DARK, WHITE, 42, pop(T0 + dur * .7, t))
    elif i == 11:
        if lt < dur * .55:
            s = pop(T0 + .3, t); box = (180, 300, 760, 420)
            if s > 0: tarjeta(g, box, 30); d = ImageDraw.Draw(g); d.text((220, 360), 'Hola, ¿cómo funciona?', font=font(40), fill=DARK, anchor='lm')
        else:
            s = pop(T0 + dur * .55, t)
            if s > 0:
                box = (540 - 300 * s, 360 - 110 * s, 540 + 300 * s, 360 + 110 * s); tarjeta(g, box, 30); d = ImageDraw.Draw(g)
                tc(d, (540, 360), 'Venta cerrada', int(62 * s) + 1); check(d, 540 + 290 * s, 260, 48 * s)
    elif i == 12:
        if lt < dur * .5:
            r = 200 * pop(T0 + .1, t)
            for k in range(12):
                a = k * math.pi / 6 + t; d.ellipse([540 + math.cos(a) * 280 - 18, 450 + math.sin(a) * 280 - 18, 540 + math.cos(a) * 280 + 18, 450 + math.sin(a) * 280 + 18], fill=GOLD)
            if r > 1: d.ellipse([540 - r, 450 - r, 540 + r, 450 + r], fill=WHITE); tc(d, (540, 450), '3', int(r * 1.1) + 1, RED)
        else:
            reloj(d, 540, 380, 220, t * 3); pill(g, 540, 700, '1 hora al día', RED, WHITE, 54, pop(T0 + dur * .55, t))
    elif i == 13:
        barras(g, (160, 160, 920, 760), 'Tu ingreso', [.25, .4, .55, .75, 1], min(1, lt / (dur * .8)))
    elif i == 14:
        telefono(g, 540, 470, 360, 680, t)
        s = pop(T0 + .5, t); bob = 12 * math.sin(t * 5)
        if s > 0:
            cx, cy = 540, 140 + bob; r = 60 * s; d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED); d.polygon([(cx - r * .8, cy + r * .5), (cx + r * .8, cy + r * .5), (cx, cy + r * 1.8)], fill=RED)
            d.ellipse([cx - r * .4, cy - r * .4, cx + r * .4, cy + r * .4], fill=WHITE); pill(g, 820, 820, 'AQUÍ', RED, WHITE, 44, s)
    elif i == 15:
        if lt < dur * .5:
            s = pop(T0 + .2, t)
            if s > 0:
                box = (540 - 190 * s, 380 - 120 * s, 540 + 190 * s, 380 + 120 * s); tarjeta(g, box, 30); d = ImageDraw.Draw(g)
                d.ellipse([540 - 120 * s, 380 - 60 * s, 540 + 120 * s, 380 + 60 * s], fill=DARK); d.ellipse([540 - 50 * s, 380 - 50 * s, 540 + 50 * s, 380 + 50 * s], fill=WHITE)
                d.ellipse([540 - 22 * s, 380 - 22 * s, 540 + 22 * s, 380 + 22 * s], fill=DARK)
            pill(g, 540, 620, 'solo miras', WHITE, DARK, 46, pop(T0 + .5, t))
        else:
            k = pop(T0 + dur * .5, t); y = 520 - 120 * k
            d.polygon([(540, y - 260), (700, y - 60), (600, y - 60), (600, y + 200), (480, y + 200), (480, y - 60), (380, y - 60)], fill=WHITE)
            pill(g, 540, 760, 'empiezas a ganar', DARK, WHITE, 46, pop(T0 + dur * .55, t))
    elif i == 16:
        put(g, LOGO, 540, 250, pop(T0 + .1, t) * .9)
        for k in range(3):
            s = pop(T0 + dur * (.45 + .12 * k), t); cx = 260 + k * 280
            pill(g, cx, 560, f'DÍA {k + 1}', RED if k == 0 else WHITE, WHITE if k == 0 else DARK, 50, s)
    elif i == 17:
        telefono(g, 540, 470, 380, 700, t, 'prospectos')
    elif i == 18:
        telefono(g, 540, 470, 360, 680, t)
    elif i == 19:
        reloj_arena(d, 540, 400, 380, GOLD, ease(lt / dur)); pill(g, 540, 760, 'perdiendo tiempo', RED, WHITE, 48, pop(T0 + .4, t))
    elif i == 20:
        for k in range(6):
            u = (t * .5 + k / 6) % 1; moneda(d, 200 + k * 140, 900 - u * 800, 46)
    elif i == 21:
        put(g, LOGO, 540, 220, .8)
        box = (160, 420, 920, 620); tarjeta(g, box, 30); d = ImageDraw.Draw(g)
        d.text((200, 460), 'Escribe un comentario...', font=font(28), fill=GRIS_T, anchor='lm')
        d.rounded_rectangle([190, 500, 890, 590], 20, fill=(244, 244, 247)); txt = 'SUMIAGO'; n = min(7, int(max(0, lt - .3) * 9))
        d.text((220, 545), txt[:n] + ('|' if int(t * 4) % 2 else ''), font=font(54), fill=RED, anchor='lm')
    elif i == 22:
        put(g, LOGO, 540, 220, .8)
        s = pop(T0 + .2, t)
        if s > 0:
            box = (540 - 330 * s, 470 - 120 * s, 540 + 330 * s, 470 + 120 * s); tarjeta(g, box, 30); d = ImageDraw.Draw(g)
            tc(d, (540, 470 - 50 * s), 'Te envío el enlace', int(44 * s) + 1)
            d.rounded_rectangle([540 - 270 * s, 470 + 5 * s, 540 + 270 * s, 470 + 85 * s], 40, fill=RED); tc(d, (540, 470 + 45 * s), 'EMPEZAR HOY', int(40 * s) + 1, WHITE)
    return g

def chips(img, x, y, paso, esc, s=1.0):
    """Indicador de los 3 cambios (1 Crear · 2 Herramienta · 3 Una hora) con check en los que ya pasaron."""
    d = ImageDraw.Draw(img); nombres = ['Crear', 'Herramienta', 'Una hora']; f = font(int(28 * s))
    for k in range(3):
        r = 22 * s
        if k + 1 < paso or paso == 4: check(d, x + r, y, r); x += 2 * r + 10 * s
        elif k + 1 == paso:
            tw = d.textlength(nombres[k], font=f); d.rounded_rectangle([x, y - r - 4 * s, x + 2 * r + tw + 30 * s, y + r + 4 * s], r + 4 * s, fill=DARK)
            d.ellipse([x + 4 * s, y - r + 2 * s, x + 2 * r, y + r - 2 * s], fill=RED); tc(d, (x + r + 2 * s, y), str(k + 1), int(24 * s), WHITE)
            d.text((x + 2 * r + 14 * s, y), nombres[k], font=f, fill=WHITE, anchor='lm'); x += 2 * r + tw + 40 * s
        else:
            d.ellipse([x, y - r, x + 2 * r, y + r], fill=(205, 205, 212)); tc(d, (x + r, y), str(k + 1), int(24 * s), WHITE); x += 2 * r + 10 * s

def subtitulo(img, t, cx, cy, ancho, size):
    """Recuadro oscuro con el trozo de frase que suena; las palabras clave (*así* en el guion) en rojo."""
    act = None
    for (i, ws) in TROZOS:
        if ws[0][2] - 0.05 <= t: act = ws
        if ws[0][2] > t: break
    if not act or t > act[-1][3] + 0.6: return
    d = ImageDraw.Draw(img); f = font(size); lineas, cur, lw = [], [], 0
    for w in act:
        ww = d.textlength(w[0] + ' ', font=f)
        if lw + ww > ancho and cur: lineas.append(cur); cur, lw = [], 0
        cur.append((w, ww)); lw += ww
    lineas.append(cur)
    wmax = max(sum(q[1] for q in ln) for ln in lineas); lh = size * 1.3; hh = lh * len(lineas)
    d.rounded_rectangle([cx - wmax / 2 - 30, cy - hh / 2 - 22, cx + wmax / 2 + 22, cy + hh / 2 + 22], 26, fill=(24, 24, 28, 245))
    y = cy - hh / 2 + lh / 2
    for ln in lineas:
        x = cx - sum(q[1] for q in ln) / 2
        for (w, ww) in ln:
            d.text((x, y), w[0], font=f, fill=(255, 70, 80) if w[1] else WHITE, anchor='lm'); x += ww
        y += lh

# ---------- composición por formato ----------
FORMATOS = {
    #        tamaño,       lienzo gráfico (x, y, escala), mascota (centro x, abajo, ancho), círculo (cx, cy, r), subtítulo (cx, cy, ancho, letra), chips (x, y, escala)
    'movil': ((1080, 1920), (0, 140, 1.0), (540, 1920, 820), (540, 1520, 470), (540, 1590, 860, 46), (40, 70, 1.15)),
    'pc':    ((1920, 1080), (110, 60, 0.82), (1540, 1080, 700), (1540, 660, 410), (900, 975, 880, 40), (40, 50, 1.0)),
}
def frame(f, fmt='movil'):
    (W, H), (gx, gy, gs), (mx, mb, mw), (ccx, ccy, cr), (sx, sy, sw, ss), (hx, hy, hs) = FORMATOS[fmt]
    t = f / FPS; i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - S[-1]
    fondo, pose, paso = ESC[i]; dur = durs[i]
    img = Image.new('RGBA', (W, H), fondo + (255,)); d = ImageDraw.Draw(img)
    circ = tuple(min(255, c + 12) if fondo in (NOCHE,) else max(0, c - (18 if fondo != ROJO else 25)) for c in fondo)
    d.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=circ)
    m = mascota(pose, mw, f, t); bob = int(6 * math.sin(t * 2.4))
    img.alpha_composite(m, (int(mx - m.width / 2), int(mb - m.height * (0.93 if fmt == 'movil' else 0.86) + bob)))
    g = grafico(i, lt, t, dur, fondo)
    if gs != 1.0: g = g.resize((int(GW * gs), int(GH * gs)), Image.LANCZOS)
    img.alpha_composite(g, (int(gx), int(gy)))
    if paso: chips(img, hx, hy, paso, i, hs)
    if lt < 0.16 and i > 0:  # acercamiento corto al cambiar de escena
        z = 1 + 0.05 * (1 - lt / 0.16)
        img = img.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
    subtitulo(img, t, sx, sy, sw, ss)
    ImageDraw.Draw(img).rectangle([0, H - 12, W * min(1, t / TOTAL), H], fill=RED)
    return img.convert('RGB')

def events():
    """Efectos de sonido (tiempo, tipo, parámetro) que usa audio.py."""
    ev = [(S[k] - 0.12, 'whoosh', 0) for k in range(1, len(durs))]
    ev += [(S[0] + .2 + k * .25, 'pop', 700 + k * 150) for k in range(3)] + [(S[1] + .5, 'stamp', 0), (S[2] + .2, 'pop', 900)]
    ev += [(S[4] + durs[4] * .45 + k * .4, 'coin', 0) for k in range(3)] + [(S[5] + .5 + k * .5, 'pop', 800 + k * 120) for k in range(5)]
    ev += [(S[6] + durs[6] * (.25 + .2 * k), 'pop', 700 + k * 200) for k in range(3)]
    ev += [(S[7] + .3, 'buzz', 0), (S[7] + .3 + durs[7] * .4, 'ding', 1568), (S[8] + .6, 'pop', 600)] + [(S[9] + .6 + k * .35, 'coin', 0) for k in range(3)]
    ev += [(S[10] + durs[10] * .7, 'pop', 900), (S[11] + .3, 'msg', 0), (S[11] + durs[11] * .55, 'ding', 2093), (S[12] + .1, 'boom', 0), (S[12] + durs[12] * .55, 'pop', 900)]
    ev += [(S[13] + .5 + k * .45, 'pop', 700 + k * 120) for k in range(5)] + [(S[14] + .5, 'pop', 1000), (S[15] + durs[15] * .5, 'riser', 0)]
    ev += [(S[16] + durs[16] * (.45 + .12 * k), 'pop', 800 + k * 150) for k in range(3)] + [(S[17] + .3 + k * .5, 'msg', 0) for k in range(3)]
    ev += [(S[19] + .4, 'stamp', 0), (S[20] + .1, 'coin', 0), (S[20] + .4, 'coin', 0)] + [(S[21] + .3 + k / 9, 'key', 0) for k in range(7)]
    ev += [(S[22] + .2, 'ding', 1568), (S[22] + .5, 'cheer', 0)]
    return ev

if __name__ == '__main__':
    modo = sys.argv[1]; fmt = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in FORMATOS else 'movil'
    if modo == 'test':
        ts = [float(x) for x in sys.argv[3:]]; (W, H) = FORMATOS[fmt][0]; tw, th = (300, 533) if fmt == 'movil' else (480, 270)
        ims = [frame(int(x * FPS), fmt).resize((tw, th)) for x in ts]
        cols = 9 if fmt == 'movil' else 4; c = Image.new('RGB', (tw * min(cols, len(ims)), th * ((len(ims) + cols - 1) // cols)))
        for k, im in enumerate(ims): c.paste(im, ((k % cols) * tw, (k // cols) * th))
        c.save('test.jpg'); print('Listo: test.jpg')
    else:
        (W, H) = FORMATOS[fmt][0]; n = int(TOTAL * FPS); salida = 'dia-02.mp4' if fmt == 'movil' else 'dia-02-pc.mp4'
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                              '-shortest', '-movflags', '+faststart', salida], stdin=subprocess.PIPE)
        for f in range(n): p.stdin.write(frame(f, fmt).tobytes())
        p.stdin.close(); p.wait()
        print('Listo:', salida)
