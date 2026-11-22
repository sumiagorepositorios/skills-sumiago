"""Motor común de los reels promocionales de Sumiago (720x1280 dibujado, se entrega a 1080x1920).
Incluye: fuentes, tiempos por palabra, mascota que habla, cuarto de noche, ventana tipo asistente, cursor,
cierre con el logo y subtítulos con palabras clave en rojo. Lo usa scripts/render.py; no se ejecuta solo.
Antes de dibujar, render.py debe fijar: KEY, LOGO_T, SC, END_TXT1, END_TXT2.
"""
import json, math, random, sys, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

W, H, FPS = 720, 1280, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
FONT_DIRS = ['/usr/share/fonts/opentype/inter/', os.path.join(AQUI, '..', 'fonts') + os.sep,
             os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts') + os.sep, 'C:\\Windows\\Fonts\\']
_fc = {}
def F(n, s):
    k = (n, s)
    if k not in _fc:
        for dd in FONT_DIRS:
            if os.path.isfile(dd + n): _fc[k] = ImageFont.truetype(dd + n, s); break
        else: sys.exit(f'No encontré la fuente {n}. Instala la familia Inter (rsms.me/inter) o copia los .otf a la carpeta fonts/ de la skill.')
    return _fc[k]
FB, FR = F('Inter-Bold.otf', 38), F('Inter-Medium.otf', 38)
RED = (230, 38, 47); GOLD = (255, 196, 60); GREEN = (46, 190, 110)
TL = json.load(open('tl.json')); CL = TL['clips']; LV = json.load(open('lv.json'))
NF = int(TL['total'] * FPS)
KEY = set(); LOGO_T = 0; SC = []; END_TXT1 = ''; END_TXT2 = ''

def ease(x): x = max(0, min(1, x)); return x * x * (3 - 2 * x)
def lerp(a, b, x): return a + (b - a) * x
def mix(c1, c2, x): return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))
def back_out(x):
    x = max(0, min(1, x)); c = 1.9; return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

# ---------- timing de palabras ----------
def words_timing(c):
    ws = c['text'].split(); tot = sum(len(w) + 2 for w in ws); t = c['t0'] + 0.05; out = []
    for w in ws:
        dd = (len(w) + 2) / tot * c['d'] * 0.96; out.append((w, t, t + dd)); t += dd
    return out
WT = [words_timing(c) for c in CL]
def wt(ci, word, n=0):
    k = 0
    for w in WT[ci]:
        if w[0].strip('¿?.,:').lower().startswith(word):
            if k == n: return w[1] - CL[ci]['t0'] + 0.15
            k += 1
    return 0

# ---------- imágenes (carpeta assets/ de la skill) ----------
VA = os.path.join(AQUI, '..', 'assets') + os.sep
def load_m(f, w):
    im = Image.open(VA + f).convert('RGBA'); return im.resize((w, int(w * im.height / im.width)), Image.LANCZOS)
def tint(im, col, a):
    ov = Image.new('RGBA', im.size, col + (0,)); ov.putalpha(im.getchannel('A').point(lambda p: int(p * a)))
    return Image.alpha_composite(im, ov)
MA_BIG = load_m('sumiago-a.png', 640); MC_BIG = load_m('sumiago-c.png', 640)       # boca abierta / cerrada
MA_BIG, MC_BIG = tint(MA_BIG, (40, 70, 160), .28), tint(MC_BIG, (40, 70, 160), .28)
MA_S = load_m('sumiago-a.png', 300); MC_S = load_m('sumiago-c.png', 300)
M_PUL = tint(load_m('mascota-pulgar.png', 640), (40, 70, 160), .2)
LOGO = load_m('logo-sumiago.png', 620)

def talking(f): return LV[min(f, len(LV) - 1)] > 0.035 and (f // 3) % 2 == 0 or LV[min(f, len(LV) - 1)] > 0.09

# ---------- cuarto de noche ----------
def make_room(dawn=0.0):
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    top, bot = mix((14, 20, 48), (120, 90, 140), dawn), mix((6, 8, 20), (30, 24, 50), dawn)
    for y in range(0, H, 4): d.rectangle((0, y, W, y + 4), fill=mix(top, bot, y / H))
    sky1, sky2 = mix((20, 34, 80), (255, 160, 110), dawn), mix((10, 16, 44), (255, 210, 150), dawn)
    for y in range(140, 560, 4): d.rectangle((60, y, 330, y + 4), fill=mix(sky1, sky2, (y - 140) / 420))
    rr = random.Random(2)
    for k in range(30):
        x, y = rr.randint(70, 320), rr.randint(150, 540)
        d.ellipse((x, y, x + 3, y + 3), fill=(255, 255, 255, int(200 * (1 - dawn))))
    if dawn < .5: d.ellipse((230, 190, 290, 250), fill=(240, 240, 220))
    else: d.ellipse((150, 420, 250, 520), fill=(255, 230, 160))
    d.rectangle((52, 132, 338, 568), outline=(30, 30, 48), width=14); d.line((195, 140, 195, 560), fill=(30, 30, 48), width=8)
    d.line((60, 350, 330, 350), fill=(30, 30, 48), width=8)
    d.rectangle((440, 300, 700, 316), fill=(36, 30, 40))
    for k, c in enumerate([(120, 40, 50), (50, 70, 120), (180, 140, 60), (60, 110, 90)]):
        d.rectangle((460 + k * 34, 220 - k % 2 * 18, 488 + k * 34, 300), fill=c)
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((480, 420, 760, 700), fill=90)
    im = Image.composite(Image.new('RGBA', (W, H), (255, 190, 90, 255)), im, g.filter(ImageFilter.GaussianBlur(90)))
    d = ImageDraw.Draw(im); d.rectangle((0, 1080, W, H), fill=(34, 24, 22)); d.rectangle((0, 1070, W, 1090), fill=(60, 42, 34))
    return im
ROOMS = {}
def room(dawn):
    k = round(dawn, 1)
    if k not in ROOMS: ROOMS[k] = make_room(k)
    return ROOMS[k].copy()

def screen_glow(im, cx, cy, w, h, a=1.0):
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rounded_rectangle((cx - w / 2 - 60, cy - h / 2 - 60, cx + w / 2 + 60, cy + h / 2 + 60), 60, fill=int(150 * a))
    return Image.composite(Image.new('RGBA', (W, H), (150, 190, 255, 255)), im, g.filter(ImageFilter.GaussianBlur(70)))

def cursor(d, x, y, click=0.0):
    if click > 0:
        r = 14 + 40 * click; d.ellipse((x - r, y - r, x + r, y + r), outline=(230, 38, 47, int(255 * (1 - click))), width=5)
    pts = [(x, y), (x, y + 38), (x + 10, y + 29), (x + 18, y + 46), (x + 25, y + 43), (x + 17, y + 26), (x + 30, y + 26)]
    d.polygon(pts, fill='white', outline=(20, 20, 20)); d.line(pts + [pts[0]], fill=(20, 20, 20), width=2)

# ---------- ventana tipo asistente de instalación ----------
STEPS = ['Bienvenida', 'Nicho', 'Estructura', 'Producción', 'Publicar']
WX, WY, WW, WH = 40, 430, 640, 600
BTN = (WX + WW - 190, WY + WH - 70, WX + WW - 24, WY + WH - 20)
CX0 = WX + 180  # inicio del área de contenido

def window(im, step, glow=1.0):
    im = screen_glow(im, WX + WW / 2, WY + WH / 2, WW, WH, glow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((WX, WY, WX + WW, WY + WH), 18, fill=(244, 245, 250), outline=(200, 205, 220), width=2)
    d.rounded_rectangle((WX, WY, WX + WW, WY + 46), 18, fill=(225, 228, 238)); d.rectangle((WX, WY + 30, WX + WW, WY + 46), fill=(225, 228, 238))
    for k, c in enumerate([(255, 95, 87), (255, 189, 46), (40, 200, 64)]): d.ellipse((WX + 18 + k * 24, WY + 16, WX + 32 + k * 24, WY + 30), fill=c)
    d.text((WX + WW / 2, WY + 23), 'Asistente · Canal de videos', font=F('Inter-SemiBold.otf', 20), fill=(90, 92, 110), anchor='mm')
    d.rectangle((WX, WY + 46, WX + 170, WY + WH - 18), fill=(234, 236, 244))
    for k, s in enumerate(STEPS):
        y = WY + 80 + k * 46; on = k == step; done = k < step
        if on: d.rounded_rectangle((WX + 10, y - 18, WX + 160, y + 18), 10, fill=(255, 255, 255))
        d.ellipse((WX + 20, y - 9, WX + 38, y + 9), fill=RED if on else (GREEN if done else (190, 192, 205)))
        d.text((WX + 48, y), s, font=F('Inter-Bold.otf' if on else 'Inter-Medium.otf', 19), fill=(30, 30, 40) if on else (120, 122, 140), anchor='lm')
    d.rounded_rectangle((BTN[0] - 150, BTN[1], BTN[0] - 20, BTN[3]), 12, fill=(228, 230, 238))
    d.text((BTN[0] - 85, (BTN[1] + BTN[3]) / 2), 'Atrás', font=F('Inter-SemiBold.otf', 22), fill=(120, 120, 135), anchor='mm')
    return im, d

def btn(d, label, press=0.0):
    s = 1 - 0.06 * math.sin(math.pi * min(1, press)) if press > 0 else 1
    cx, cy = (BTN[0] + BTN[2]) / 2, (BTN[1] + BTN[3]) / 2; bw, bh = (BTN[2] - BTN[0]) / 2 * s, (BTN[3] - BTN[1]) / 2 * s
    d.rounded_rectangle((cx - bw, cy - bh, cx + bw, cy + bh), 12, fill=RED)
    d.text((cx, cy), label, font=F('Inter-Bold.otf', 22), fill='white', anchor='mm')

def mascot_corner(im, f, x=430, y=1000):
    m = MA_S if talking(f) else MC_S
    im.alpha_composite(m, (x, y))

def thumb_card(w, h, col, views):
    im = Image.new('RGBA', (w, h)); d = ImageDraw.Draw(im)
    for y in range(h): d.line((0, y, w, y), fill=mix(col, (10, 10, 16), y / h))
    d.ellipse((w * .3, h * .2, w * .7, h * .42), fill=mix(col, (255, 255, 255), .4))
    x = 0; r = random.Random(w + h)
    while x < w:
        bw = r.randint(w // 8, w // 4); bh = r.randint(h // 5, h // 2); d.rectangle((x, h - bh, x + bw, h), fill=(14, 14, 20)); x += bw + 2
    d.text((8, h - 16), views, font=F('Inter-Bold.otf', max(12, w // 7)), fill='white', anchor='lm')
    m = Image.new('L', (w, h), 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, w - 1, h - 1), 10, fill=255); im.putalpha(m)
    return im

# ---------- cierre: pantalla blanca + logo con rebote, ondas, chispas y brillo ----------
def end_scene(lt, t):
    im = Image.new('RGBA', (W, H), (8, 10, 22, 255))
    rr = ease(lt / 0.4) * 1500
    ImageDraw.Draw(im).ellipse((W / 2 - rr, 700 - rr, W / 2 + rr, 700 + rr), fill=(255, 255, 255, 255))
    ov = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(ov); cy = 640
    for k in range(3):
        q = (lt - 0.45 - k * 0.35) / 1.4
        if 0 < q < 1:
            r = 120 + q * 520; d.ellipse((W / 2 - r, cy - r, W / 2 + r, cy + r), outline=RED + (int(170 * (1 - q)),), width=6)
    rnd = random.Random(5)
    for k in range(26):
        q = (lt - 0.45) / 1.1
        if 0 < q < 1:
            a = rnd.random() * 2 * math.pi; sp = 220 + rnd.random() * 320; r = 6 + rnd.random() * 8
            x = W / 2 + math.cos(a) * sp * ease(q); y = cy + math.sin(a) * sp * ease(q) + 80 * q * q
            col = RED if k % 3 else (40, 40, 46)
            d.ellipse((x - r * (1 - q), y - r * (1 - q), x + r * (1 - q), y + r * (1 - q)), fill=col + (int(255 * (1 - q)),))
    im.alpha_composite(ov)
    sc = back_out((lt - 0.3) / 0.55) if lt > 0.3 else 0
    if sc > 0.02:
        fl = 1 + 0.025 * math.sin(max(0, lt - 1) * 3)
        lw, lh = int(LOGO.width * sc * fl), int(LOGO.height * sc * fl)
        lg = LOGO.resize((max(1, lw), max(1, lh)), Image.LANCZOS)
        sh = Image.new('RGBA', lg.size, (0, 0, 0, 0)); sh.putalpha(lg.getchannel('A').point(lambda p: p * 0.25))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)), ((W - lw) // 2 + 6, cy - lh // 2 + 16))
        q = (lt - 1.0) / 0.7
        if 0 < q < 1:
            band = Image.new('L', lg.size, 0); bd = ImageDraw.Draw(band); bx = -200 + q * (lw + 400)
            bd.polygon([(bx, 0), (bx + 70, 0), (bx - 50, lh), (bx - 120, lh)], fill=200)
            m = ImageChops.multiply(band.filter(ImageFilter.GaussianBlur(12)), lg.getchannel('A'))
            wl = Image.new('RGBA', lg.size, (255, 255, 255, 0)); wl.putalpha(m); lg = Image.alpha_composite(lg, wl)
        im.alpha_composite(lg, ((W - lw) // 2, cy - lh // 2))
    a = ease((lt - 1.1) / 0.5)
    if a > 0:
        d = ImageDraw.Draw(im); yo = (1 - a) * 30
        d.text((W // 2, 860 + yo), END_TXT1, font=F('Inter-Bold.otf', 36), fill=(60, 60, 68, int(255 * a)), anchor='mm')
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 1000 - 38 * bx + yo, W / 2 + 250 * bx, 1000 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 1000 + yo), END_TXT2, font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

# ---------- subtítulos ----------
def chunks(ws):
    out, cur, ln = [], [], 0
    for w in ws:
        cur.append(w); ln += len(w[0]) + 1
        if ln > 22 or w[0][-1] in '.,:?' and ln > 10: out.append(cur); cur, ln = [], 0
    if cur: out.append(cur)
    return out
CH = [chunks(w) for w in WT]

def caption(im, t, white):
    ci = None
    for i, c in enumerate(CL):
        if c['t0'] - 0.1 <= t <= c['t0'] + c['d'] + 0.25: ci = i
    if ci is None: return
    cur = CH[ci][0]
    for ch in CH[ci]:
        if t >= ch[0][1] - 0.05: cur = ch
    vis = [w for w in cur if t >= w[1] - 0.04]
    if not vis: return
    d = ImageDraw.Draw(im); lines, line, lw = [], [], 0
    for w in vis:
        ww = d.textlength(w[0] + ' ', font=FB)
        if lw + ww > 600 and line: lines.append(line); line, lw = [], 0
        line.append((w, ww)); lw += ww
    lines.append(line)
    y = 250 - (len(lines) - 1) * 26
    for ln in lines:
        x = (W - sum(q[1] for q in ln)) / 2
        for (w, ww) in ln:
            word = w[0]; clean = word.strip('¿?.,:').lower(); latest = w is vis[-1]; pop = ease((t - w[1]) / 0.12)
            if clean in KEY:  # palabra clave en recuadro rojo
                bw = d.textlength(word, font=FB)
                d.rounded_rectangle((x - 6, y - 26, x + bw + 6, y + 26), 8, fill=RED + (230,))
                d.text((x, y), word, font=FB, fill='white', anchor='lm')
            else:
                if white: col = (25, 25, 30) if latest else (120, 120, 130)
                else: col = (255, 255, 255) if latest else (160, 165, 185)
                d.text((x, y + (1 - pop) * 8), word, font=FB if latest else FR, fill=col, anchor='lm', stroke_width=0 if white else 4, stroke_fill=(8, 10, 24))
            x += ww
        y += 54

def frame(f):
    t = f / FPS
    if t >= LOGO_T:
        im = end_scene(t - LOGO_T, t); white = t - LOGO_T > .3
    else:
        i = 0
        for k, c in enumerate(CL):
            if t >= c['t0'] - 0.15: i = k
        st = CL[i]['t0'] - 0.15; nxt = CL[i + 1]['t0'] - 0.15 if i + 1 < len(CL) else LOGO_T
        lt = t - st; im = SC[i](lt, nxt - st, f); white = False
        if lt < 0.18 and i > 0:  # zoom corto al cambiar de escena
            k = 1 - lt / 0.18; z = 1 + .06 * k
            im = im.resize((int(W * z), int(H * z))).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    caption(im, t, white)
    return im.convert('RGB')

def main(clicks):
    """meta -> clicks.json y logo_t.json ;  A B -> cuadros frames/A..B-1"""
    if sys.argv[1] == 'meta':
        json.dump(clicks(), open('clicks.json', 'w')); json.dump(LOGO_T, open('logo_t.json', 'w')); print('Listo: clicks.json y logo_t.json')
    else:
        a, b = int(sys.argv[1]), int(sys.argv[2]); os.makedirs('frames', exist_ok=True)
        for f in range(a, min(b, NF)): frame(f).save(f'frames/{f:05d}.jpg', quality=92)
        print('Listo: cuadros', a, '-', min(b, NF) - 1)
