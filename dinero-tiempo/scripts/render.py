"""Dibuja el reel 9:16 "El dinero va y viene, MIRA!" (siluetas al atardecer + logo de Sumiago al final).
Se dibuja a 720x1280 y se escala a 1080x1920 al codificar.
Uso (en la carpeta de trabajo, después de scripts/voz.py):
    python scripts/render.py meta          -> clicks.json y logo_t.json (los usa audio.py)
    python scripts/render.py 0 99999       -> frames/00000.jpg ... (se puede partir en dos rangos y correrlos a la vez)
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
LOGO_T = CL[8]['t0'] + CL[8]['d'] - 0.1
KEY = {'miedo', 'feliz', 'cincuenta', 'dólares', 'recuerdos', 'viaje', 'vida', 'revés', 'moneda', 'dinero', 'tiempo', 'nunca', 'planes', 'viaja', 'comparte', 'lujo', 'escapar', 'sumiago', 'perfil', 'regístrate', 'videos'}

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

LOGO = Image.open(os.path.join(AQUI, '..', 'assets', 'logo-sumiago.png')).convert('RGBA')
LOGO = LOGO.resize((620, int(620 * LOGO.height / LOGO.width)), Image.LANCZOS)

# ---------- escenas (atardecer y siluetas) ----------
YEL = (255, 200, 40); HZ = 760; SIL = (22, 12, 14)
PALS = {'sunset': ((86, 50, 120), (240, 120, 70), (255, 196, 110)),
        'dusk': ((50, 30, 90), (190, 80, 70), (250, 150, 80)),
        'night': ((14, 16, 44), (70, 40, 90), (180, 90, 80)),
        'day': ((90, 150, 220), (170, 200, 235), (250, 225, 190))}
_sky = {}
def sky(p):
    if p in _sky: return _sky[p].copy()
    a, b, c = PALS[p]; im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    for y in range(0, HZ, 3):
        q = y / HZ; col = mix(a, b, q / .6) if q < .6 else mix(b, c, (q - .6) / .4); d.rectangle((0, y, W, y + 3), fill=col)
    for y in range(HZ, H, 3): d.rectangle((0, y, W, y + 3), fill=mix((60, 30, 26), (10, 6, 8), (y - HZ) / (H - HZ)))
    if p == 'night':
        rr = random.Random(1)
        for k in range(60): x, y = rr.randint(0, W), rr.randint(0, 500); d.ellipse((x, y, x + 2, y + 2), fill=(255, 255, 255, 180))
    _sky[p] = im; return im.copy()

def mountains(im, col_far=(120, 70, 100), col_near=(70, 36, 50)):
    d = ImageDraw.Draw(im)
    for k, (col, amp, base) in enumerate([(col_far, 70, HZ - 30), (col_near, 45, HZ)]):
        pts = [(0, H)]
        for x in range(0, W + 20, 20): pts.append((x, base - amp * (0.5 + 0.5 * math.sin(x * .011 + k * 2) * math.cos(x * .004 + k))))
        pts.append((W, H)); d.polygon(pts, fill=col)
    d.rectangle((0, HZ, W, H), fill=None)
    for y in range(HZ, H, 3): d.rectangle((0, y, W, y + 3), fill=mix((50, 24, 22), (8, 5, 6), (y - HZ) / (H - HZ)))

def sun(im, x, y, r=70, col=(255, 236, 170)):
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((x - r * 3, y - r * 3, x + r * 3, y + r * 3), fill=140)
    im2 = Image.composite(Image.new('RGBA', (W, H), (255, 220, 140, 255)), im, g.filter(ImageFilter.GaussianBlur(r * 1.2)))
    ImageDraw.Draw(im2).ellipse((x - r, y - r, x + r, y + r), fill=col); return im2

def fig(d, x, y, s=1.0, pose='stand', t=0.0, col=SIL):
    hr = 15 * s; d.ellipse((x - hr, y - 132 * s, x + hr, y - 102 * s), fill=col)
    d.polygon([(x - 20 * s, y - 98 * s), (x + 20 * s, y - 98 * s), (x + 16 * s, y - 45 * s), (x - 16 * s, y - 45 * s)], fill=col)
    d.line((x - 8 * s, y - 48 * s, x - 10 * s, y), fill=col, width=int(11 * s)); d.line((x + 8 * s, y - 48 * s, x + 10 * s, y), fill=col, width=int(11 * s))
    w = int(9 * s)
    if pose == 'up':
        wv = 8 * math.sin(t * 8) * s
        d.line((x - 18 * s, y - 94 * s, x - 34 * s + wv, y - 150 * s), fill=col, width=w); d.line((x + 18 * s, y - 94 * s, x + 34 * s - wv, y - 150 * s), fill=col, width=w)
    elif pose == 'point':
        d.line((x + 18 * s, y - 92 * s, x + 70 * s, y - 92 * s), fill=col, width=w); d.line((x - 18 * s, y - 94 * s, x - 22 * s, y - 50 * s), fill=col, width=w)
    elif pose == 'cane':
        d.line((x + 16 * s, y - 92 * s, x + 30 * s, y - 56 * s), fill=col, width=w); d.line((x + 32 * s, y - 58 * s, x + 36 * s, y), fill=col, width=int(5 * s))
        d.line((x - 18 * s, y - 94 * s, x - 22 * s, y - 50 * s), fill=col, width=w)
    elif pose == 'kite':
        d.line((x + 18 * s, y - 94 * s, x + 46 * s, y - 130 * s), fill=col, width=w); d.line((x - 18 * s, y - 94 * s, x - 22 * s, y - 50 * s), fill=col, width=w)
    else:
        d.line((x - 18 * s, y - 94 * s, x - 22 * s, y - 50 * s), fill=col, width=w); d.line((x + 18 * s, y - 94 * s, x + 22 * s, y - 50 * s), fill=col, width=w)

def label(im, lt, t_in, big, small='', a_out=None):
    a = ease((lt - t_in) / .25)
    if a <= 0: return
    if a_out is not None: a *= 1 - ease((lt - a_out) / .2)
    d = ImageDraw.Draw(im); sc = .85 + .15 * back_out((lt - t_in) / .35)
    fs0 = 70
    while fs0 > 30 and d.textlength(big, font=F('Inter-Black.otf', fs0)) > 640: fs0 -= 2
    f = F('Inter-Black.otf', max(10, int(fs0 * sc)))
    d.text((W / 2, 900), big, font=f, fill=YEL + (int(255 * a),), anchor='mm')
    if small: d.text((W / 2, 960), small, font=F('Inter-Black.otf', 26), fill=(255, 255, 255, int(255 * a)), anchor='mm')

def birds(d, lt):
    for k in range(5):
        x = (lt * 50 + k * 70) % (W + 100) - 50; y = 330 + k * 18 + 6 * math.sin(lt * 4 + k); wv = 6 * math.sin(lt * 10 + k)
        d.line((x - 10, y - wv, x, y, x + 10, y - wv), fill=(40, 20, 30), width=3)

def wallet(d, x, y, op):
    d.rounded_rectangle((x - 30, y - 18 - 20 * op, x + 30, y + 18), 6, fill=(30, 16, 14))

def sc0(lt, d_, f):
    im = sun(sky('sunset'), 520, 520 + lt * 6); mountains(im); d = ImageDraw.Draw(im)
    birds(d, lt)
    d.line((120, HZ + 10, 120, 600), fill=SIL, width=6); d.ellipse((108, 588, 132, 612), fill=(255, 210, 120))
    fig(d, W / 2, HZ + 10, 1.6, 'stand')
    wallet(d, W / 2 + 40, HZ - 90, 0)
    label(im, lt, wt(0, 'miedo'), 'MIEDO A GASTAR')
    return im

def sc1(lt, d_, f):
    im = sun(sky('sunset'), 360, 540); mountains(im); d = ImageDraw.Draw(im)
    tr = wt(1, 'recuerdos'); up = lt > tr - .1
    for k, x in enumerate([180, 300, 420, 540]):
        fig(d, x, HZ + 10, 1.35, 'up' if up else 'stand', lt + k)
    d.rounded_rectangle((200, HZ - 40, 520, HZ - 26), 4, fill=SIL) if not up else None
    n = int(50 * ease((lt - wt(1, 'cincuenta')) / .6))
    if lt < tr - .1: label(im, lt, wt(1, 'cincuenta'), f'{n}', 'DÓLARES EN UNA CENA')
    else: label(im, lt, tr - .1, 'RECUERDOS')
    if up:
        rr = random.Random(3)
        for k in range(30):
            q = (lt - tr) * .6 + rr.random()
            x = rr.uniform(60, W - 60); y = 600 - (q % 1) * 400
            d.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 230, 150, int(200 * (1 - q % 1))))
    return im

def sc2(lt, d_, f):
    im = sun(sky('sunset'), W / 2, 560); mountains(im); d = ImageDraw.Draw(im)
    d.polygon([(W / 2 - 14, HZ), (W / 2 + 14, HZ), (W / 2 + 330, H), (W / 2 - 330, H)], fill=(58, 34, 30))
    for k in range(10):
        q = ((k / 10) + lt * .25) % 1; y0 = HZ + (H - HZ) * q ** 2; y1 = HZ + (H - HZ) * min(1, (q + .04)) ** 2
        d.line((W / 2, y0, W / 2, y1), fill=(220, 190, 150), width=max(1, int(8 * q)))
    s = 1.4 - .6 * ease(lt / d_); fig(d, W / 2, HZ + 90 - 80 * ease(lt / d_), s)
    tv = wt(2, 'viaje'); tt = wt(2, 'toda')
    if lt < tt - .1: label(im, lt, tv, '1 VIAJE', 'UNA EXPERIENCIA')
    else: label(im, lt, tt - .1, 'TODA TU VIDA')
    return im

def sc3(lt, d_, f):
    tm = wt(3, 'moneda')
    im = sun(sky('dusk'), 470 if lt < tm - .3 else 560, 600); mountains(im); d = ImageDraw.Draw(im)
    if lt < tm - .3:
        fig(d, 300, HZ + 10, 1.5)
        d.line((420, HZ + 10, 420, 560), fill=SIL, width=10)
        d.polygon([(420, 580), (560, 580), (590, 600), (560, 620), (420, 620)], fill=SIL)
        d.polygon([(420, 640), (290, 640), (260, 660), (290, 680), (420, 680)], fill=SIL)
        label(im, lt, wt(3, 'revés') - .1, 'AL REVÉS')
    else:
        x = 300 + (lt - tm) * 30; fig(d, x, HZ + 10, 1.4, 'cane')
        cx, cy = x + 120, HZ - 40 + 10 * math.sin(lt * 3)
        d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=YEL, outline=(170, 120, 20), width=4)
        label(im, lt, tm - .3, 'LA ÚLTIMA MONEDA')
    return im

def sc4(lt, d_, f):
    tt = wt(4, 'tiempo')
    sy = 520 + 260 * ease((lt - tt) / (d_ - tt)) if lt > tt else 520
    im = sun(sky('sunset' if lt < tt else 'dusk'), W / 2, sy); mountains(im); d = ImageDraw.Draw(im)
    fig(d, W / 2, HZ + 10, 1.6)
    if lt < tt - .1:
        for k in range(5):  # monedas que van y vienen
            ph = lt * 2 + k * 1.2; x = W / 2 + 200 * math.sin(ph); y = 560 + 40 * math.cos(ph * 1.3)
            d.ellipse((x - 16, y - 16, x + 16, y + 16), fill=YEL, outline=(170, 120, 20), width=3)
        label(im, lt, wt(4, 'va'), 'VA Y VIENE', 'EL DINERO')
    else:
        label(im, lt, tt - .1, 'SOLO SE VA', 'EL TIEMPO')
    return im

def sc5(lt, d_, f):
    im = sky('night'); mountains(im, (60, 40, 80), (36, 22, 40)); d = ImageDraw.Draw(im)
    tt = wt(5, 'tiempo')
    d.rectangle((210, HZ - 60, 510, HZ - 46), fill=SIL); d.rectangle((230, HZ - 46, 244, HZ + 10), fill=SIL); d.rectangle((476, HZ - 46, 490, HZ + 10), fill=SIL)
    ch = 90 * (1 - ease((lt - tt) / (d_ - tt))) if lt > tt else 90
    cx = W / 2; d.rectangle((cx - 12, HZ - 60 - ch, cx + 12, HZ - 60), fill=(240, 230, 210))
    fl = 1 + .15 * math.sin(lt * 18)
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((cx - 120, HZ - 60 - ch - 140, cx + 120, HZ - 60 - ch + 100), fill=130)
    im = Image.composite(Image.new('RGBA', (W, H), (255, 190, 90, 255)), im, g.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(im)
    d.ellipse((cx - 9 * fl, HZ - 60 - ch - 34 * fl, cx + 9 * fl, HZ - 60 - ch), fill=(255, 220, 120))
    if lt < tt - .1: label(im, lt, wt(5, 'dinero'), 'DINERO', 'LO VUELVES A GANAR')
    else: label(im, lt, tt - .1, 'TIEMPO', 'NUNCA LO RECUPERAS')
    return im

def sc6(lt, d_, f):
    im = sun(sky('day'), 560, 300, 60); mountains(im, (120, 140, 170), (80, 90, 110)); d = ImageDraw.Draw(im)
    tp, tv, tc = wt(6, 'planes'), wt(6, 'viaja'), wt(6, 'comparte')
    if lt < tc - .1:
        fig(d, 300, HZ + 10, 1.5, 'kite'); fig(d, 380, HZ + 10, 1.0)
        kx, ky = 520 + 20 * math.sin(lt * 2), 380 + 15 * math.cos(lt * 2.4)
        d.line((300 + 46 * 1.5, HZ + 10 - 130 * 1.5, kx, ky + 40), fill=(30, 30, 30), width=2)
        d.polygon([(kx, ky - 40), (kx + 30, ky), (kx, ky + 40), (kx - 30, ky)], fill=(20, 20, 26))
        if lt < tv - .1: label(im, lt, tp - .1, 'HAZ PLANES')
        else: label(im, lt, tv - .1, 'VIAJA')
    else:
        for k, (x, s) in enumerate([(160, 1.45), (250, 1.5), (330, 1.0), (420, 1.4), (500, 1.5), (590, 1.3)]):
            fig(d, x, HZ + 10, s, 'cane' if k == 5 else 'stand')
        label(im, lt, tc - .1, 'COMPARTE', 'CON QUIEN QUIERES')
    return im

def house(im, x, y, s, glow):
    if glow > 0:
        g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((x - 200 * s, y - 250 * s, x + 200 * s, y + 80 * s), fill=int(150 * glow))
        im = Image.composite(Image.new('RGBA', (W, H), (255, 200, 110, 255)), im, g.filter(ImageFilter.GaussianBlur(70)))
    d = ImageDraw.Draw(im)
    d.rectangle((x - 120 * s, y - 170 * s, x + 120 * s, y), fill=SIL); d.polygon([(x - 150 * s, y - 165 * s), (x, y - 290 * s), (x + 150 * s, y - 165 * s)], fill=SIL)
    wc = mix((60, 40, 30), (255, 220, 140), glow)
    d.rectangle((x - 80 * s, y - 130 * s, x - 30 * s, y - 80 * s), fill=wc); d.rectangle((x + 20 * s, y - 120 * s, x + 80 * s, y), fill=wc)
    return im

def sc7(lt, d_, f):
    tl_ = wt(7, 'tener')
    if lt < tl_ - .2:
        im = sun(sky('dusk'), W / 2, 640); mountains(im); d = ImageDraw.Draw(im)
        rr = random.Random(6); x = -10
        while x < W:
            bw = rr.randint(60, 120); bh = rr.randint(150, 380); d.rectangle((x, HZ - bh, x + bw - 6, HZ + 10), fill=(46, 26, 30))
            for wy in range(HZ - bh + 16, HZ - 10, 28):
                for wx in range(x + 10, x + bw - 20, 20):
                    if rr.random() < .3: d.rectangle((wx, wy, wx + 8, wy + 12), fill=(255, 200, 110))
            x += bw
        fig(d, W / 2, HZ + 14, 1.5)
        label(im, lt, wt(7, 'acumular') - .2, 'NO ES', 'ACUMULAR DINERO')
    else:
        im = sun(sky('sunset'), 600, 560); mountains(im)
        im = house(im, 470, HZ + 10, 1.0, ease((lt - tl_ + .2) / .6)); d = ImageDraw.Draw(im)
        fig(d, 220, HZ + 10, 1.5); fig(d, 280, HZ + 10, .95)
        label(im, lt, tl_ - .2, 'EL VERDADERO LUJO', 'UNA VIDA DE LA QUE NO QUIERAS ESCAPAR')
    return im

def sc8(lt, d_, f):
    im = sun(sky('sunset'), 560, 540 + lt * 10); mountains(im); d = ImageDraw.Draw(im)
    fig(d, 260, HZ + 10, 1.6, 'point')
    q = ease((lt - .2) / .4); x0, y0 = 330, 380 + (1 - q) * 40
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); al = int(255 * q)
    dl.rounded_rectangle((x0, y0, x0 + 340, y0 + 200), 24, fill=(255, 255, 255, al))
    dl.ellipse((x0 + 20, y0 + 20, x0 + 84, y0 + 84), fill=RED + (al,))
    dl.text((x0 + 52, y0 + 52), 'S', font=F('Inter-Black.otf', 36), fill=(255, 255, 255, al), anchor='mm')
    dl.text((x0 + 100, y0 + 40), '@sumiago', font=F('Inter-Black.otf', 26), fill=(25, 25, 32, al), anchor='lm')
    dl.text((x0 + 100, y0 + 70), 'Videos como este', font=F('Inter-Medium.otf', 18), fill=(110, 110, 125, al), anchor='lm')
    pul = .5 + .5 * math.sin(lt * 9) if lt > wt(8, 'link') else 0
    dl.rounded_rectangle((x0 + 20, y0 + 118, x0 + 320, y0 + 176), 14, fill=mix((240, 240, 246), RED, pul) + (al,))
    dl.text((x0 + 170, y0 + 147), 'Link: Regístrate', font=F('Inter-Bold.otf', 24), fill=mix((30, 30, 40), (255, 255, 255), pul) + (al,), anchor='mm')
    im.alpha_composite(L)
    label(im, lt, wt(8, 'regístrate'), 'REGÍSTRATE', 'EL LINK ESTÁ EN MI PERFIL')
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
        d.text((W // 2, 860 + yo), 'Aprende a crear videos así', font=F('Inter-Bold.otf', 36), fill=(60, 60, 68, int(255 * a)), anchor='mm')
        bx = 1 + 0.04 * math.sin(t * 6)
        d.rounded_rectangle((W / 2 - 250 * bx, 1000 - 38 * bx + yo, W / 2 + 250 * bx, 1000 + 38 * bx + yo), 38, fill=RED + (int(255 * a),))
        d.text((W // 2, 1000 + yo), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', 30), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    return im

SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8]

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
            if clean in KEY:  # palabra clave: recuadro amarillo
                bw = d.textlength(word, font=FB)
                d.rounded_rectangle((x - 6, y - 26, x + bw + 6, y + 26), 8, fill=(RED if white else YEL) + (235,))
                d.text((x, y), word, font=FB, fill='white' if white else (25, 20, 10), anchor='lm')
            else:
                if white: col = (25, 25, 30) if latest else (120, 120, 130)
                else: col = (255, 255, 255) if latest else (160, 165, 185)
                d.text((x, y + (1 - pop) * 8), word, font=FB if latest else FR, fill=col, anchor='lm', stroke_width=0 if white else 4, stroke_fill=(40, 20, 20))
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
        if lt < 0.18 and i > 0:  # pequeño zoom al cambiar de escena
            k = 1 - lt / 0.18; z = 1 + .06 * k
            im = im.resize((int(W * z), int(H * z))).crop((int(W * (z - 1) / 2), int(H * (z - 1) / 2), int(W * (z - 1) / 2) + W, int(H * (z - 1) / 2) + H))
    caption(im, t, white)
    return im.convert('RGB')

def clicks():
    return []  # este video no lleva clics

if __name__ == '__main__':
    if sys.argv[1] == 'meta':
        json.dump(clicks(), open('clicks.json', 'w')); json.dump(LOGO_T, open('logo_t.json', 'w')); print('Listo: clicks.json y logo_t.json')
    else:
        a, b = int(sys.argv[1]), int(sys.argv[2]); os.makedirs('frames', exist_ok=True)
        for f in range(a, min(b, NF)): frame(f).save(f'frames/{f:05d}.jpg', quality=92)
        print('Listo: cuadros', a, '-', min(b, NF) - 1)
