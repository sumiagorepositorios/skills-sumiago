"""Día 20 — reel "Un fin de semana o tu membresía: tú decides" (sin montos ni valores).
Uso (en la carpeta de trabajo, después de scripts/voz.py):
    python scripts/render.py meta        -> clicks.json (momentos y tipo de efecto) y logo_t.json
    python scripts/render.py 0 2000      -> frames/00000.jpg ...
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import promo_base as B
from promo_base import *

B.LOGO_T = CL[8]['t0'] + CL[8]['d'] - 0.1
B.KEY = {'fin', 'semana', 'cine', 'combo', 'centro', 'dinero', 'lunes', 'activas', 'membresía', 'sumiago', 'cursos', 'portada', 'marketplace',
         'tienda', 'tareas', 'comunidad', 'comisiones', 'exponenciales', 'domingo', 'herramientas', 'constancia', 'disciplina', 'decides', 'link', 'regístrate'}
B.END_TXT1 = 'Tú decides'; B.END_TXT2 = 'REGÍSTRATE · LINK EN MI PERFIL'

# ---------- escenas ----------
def bg(col=(90, 14, 20), cy=700):
    im = Image.new('RGBA', (W, H), (10, 10, 14, 255))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((-250, cy - 450, W + 250, cy + 450), fill=120)
    return Image.composite(Image.new('RGBA', (W, H), col + (255,)), im, g.filter(ImageFilter.GaussianBlur(150)))

def pop_s(lt, t0, dur=.35): return back_out((lt - t0) / dur) if lt > t0 else 0

def price_tag(im, x, y, txt, s, col=RED, rot=-8):
    if s <= 0.02: return
    L = Image.new('RGBA', (360, 200), (0, 0, 0, 0)); d = ImageDraw.Draw(L)
    d.rounded_rectangle((20, 30, 340, 170), 30, fill=col); d.ellipse((40, 85, 70, 115), fill=(10, 10, 14))
    d.text((200, 100), txt, font=F('Inter-Black.otf', 84 if len(txt) < 4 else 64), fill='white', anchor='mm')
    L = L.rotate(rot, expand=True, resample=Image.BICUBIC); L = L.resize((max(1, int(L.width * s)), max(1, int(L.height * s))))
    im.alpha_composite(L, (int(x - L.width / 2), int(y - L.height / 2)))

TOT = [(1, 'cine', 30), (2, 'combo', 25), (3, 'centro', 25)]
def spent(t):
    v = 0
    for ci, w, a in TOT:
        tt = CL[ci]['t0'] - 0.15 + wt(ci, w)
        v += a * ease((t - tt) / .4)
    return v

def counter(im, t, f):  # barra "TU DINERO" que se vacía
    d = ImageDraw.Draw(im); v = spent(t)
    d.rounded_rectangle((W - 300, 360, W - 30, 450), 22, fill=(20, 20, 26), outline=(60, 60, 70), width=3)
    d.text((W - 280, 383), 'TU DINERO', font=F('Inter-Bold.otf', 20), fill=(150, 150, 160), anchor='lm')
    fr = max(0, 1 - v / 100); d.rounded_rectangle((W - 280, 412, W - 50, 436), 12, fill=(50, 50, 58))
    d.rounded_rectangle((W - 280, 412, W - 280 + 230 * fr, 436), 12, fill=mix(RED, (70, 200, 110), fr))

def bill(d, x, y, a, s=1.0):
    c, sn = math.cos(a), math.sin(a)
    pts = [(-46, -24), (46, -24), (46, 24), (-46, 24)]
    P = [(x + (px * c - py * sn) * s, y + (px * sn + py * c) * s) for px, py in pts]
    d.polygon(P, fill=(70, 170, 90), outline=(30, 100, 50)); d.ellipse((x - 12 * s, y - 12 * s, x + 12 * s, y + 12 * s), fill=(40, 120, 60))

def wallet_draw(d, x, y, s=1.0, empty=False):
    d.rounded_rectangle((x - 130 * s, y - 85 * s, x + 130 * s, y + 85 * s), int(26 * s), fill=(60, 34, 24) if not empty else (50, 50, 56))
    d.rounded_rectangle((x + 40 * s, y - 34 * s, x + 140 * s, y + 34 * s), int(16 * s), fill=(80, 46, 32) if not empty else (66, 66, 74))
    d.ellipse((x + 70 * s, y - 12 * s, x + 94 * s, y + 12 * s), fill=GOLD if not empty else (110, 110, 118))

def sc0(lt, d_, f):
    im = bg(); d = ImageDraw.Draw(im)
    rr = random.Random(2)
    for k in range(14):
        q = (lt * .9 + rr.random()) % 1; x = W / 2 + rr.uniform(-1, 1) * 330 * q; y = 760 - 520 * q + 300 * q * q
        bill(d, x, y, lt * 3 + k, 1.0)
    wallet_draw(d, W / 2, 820, 1.2)
    s = pop_s(lt, .1, .4)
    if s: d.text((W / 2, 1080), '?', font=F('Inter-Black.otf', max(10, int(180 * s))), fill=(255, 255, 255), anchor='mm')
    return im

def popcorn(d, x, y, s):
    for k in range(9):
        a = k / 9 * math.pi; d.ellipse((x - 70 * s + k * 16 * s - 14 * s, y - 150 * s - 20 * s * math.sin(a) - 14 * s, x - 70 * s + k * 16 * s + 14 * s, y - 150 * s - 20 * s * math.sin(a) + 14 * s), fill=(255, 240, 200))
    d.polygon([(x - 80 * s, y - 140 * s), (x + 80 * s, y - 140 * s), (x + 60 * s, y + 60 * s), (x - 60 * s, y + 60 * s)], fill='white')
    for k in range(4):
        x0 = x - 80 * s + k * 40 * s; d.polygon([(x0 + 8 * s, y - 140 * s), (x0 + 28 * s, y - 140 * s), (x0 + 24 * s + 5 * s * (k - 1.5) / 2, y + 60 * s), (x0 + 10 * s + 5 * s * (k - 1.5) / 2, y + 60 * s)], fill=RED)

def sc1(lt, d_, f):
    im = bg((30, 40, 110), 600); d = ImageDraw.Draw(im)
    d.rounded_rectangle((70, 480, 650, 760), 12, fill=(180, 200, 255))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rectangle((40, 450, 680, 790), fill=120)
    im = Image.composite(Image.new('RGBA', (W, H), (150, 180, 255, 255)), im, g.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(im)
    for k in range(6):
        d.ellipse((40 + k * 120, 900, 120 + k * 120, 960), fill=(20, 20, 30))
    popcorn(d, 230, 1050, 1.1 * pop_s(lt, .1))
    ts = pop_s(lt, .3)
    if ts:
        d.rounded_rectangle((420, 920 - 50 * ts, 640, 1000 + 20 * ts), 12, fill=GOLD)
        d.text((530, 965), 'CINE', font=F('Inter-Black.otf', 40), fill=(60, 40, 10), anchor='mm')
    price_tag(im, W / 2, 640, 'GASTO', pop_s(lt, wt(1, 'cine') + .2, .35))
    counter(im, CL[1]['t0'] - .15 + lt, f)
    return im

def sc2(lt, d_, f):
    im = bg((120, 50, 10), 800); d = ImageDraw.Draw(im)
    s = pop_s(lt, .05, .4); cx, cy = 290, 920
    if s:  # hamburguesa
        d.ellipse((cx - 130 * s, cy - 120 * s, cx + 130 * s, cy - 10 * s), fill=(220, 150, 60))
        d.rectangle((cx - 135 * s, cy - 20 * s, cx + 135 * s, cy + 6 * s), fill=(80, 180, 80))
        d.rounded_rectangle((cx - 130 * s, cy, cx + 130 * s, cy + 40 * s), int(14 * s), fill=(110, 50, 30))
        d.rectangle((cx - 135 * s, cy + 40 * s, cx + 135 * s, cy + 56 * s), fill=(250, 200, 50))
        d.rounded_rectangle((cx - 130 * s, cy + 56 * s, cx + 130 * s, cy + 110 * s), int(20 * s), fill=(220, 150, 60))
    s2 = pop_s(lt, .25, .4)
    if s2:  # papas
        x = 520
        for k in range(7): d.rounded_rectangle((x - 60 * s2 + k * 18 * s2, 840 - 40 * s2 - (k % 3) * 12 * s2, x - 48 * s2 + k * 18 * s2, 900), 3, fill=(255, 210, 80))
        d.polygon([(x - 75 * s2, 880), (x + 75 * s2, 880), (x + 60 * s2, 1040), (x - 60 * s2, 1040)], fill=RED)
    price_tag(im, W / 2, 640, 'GASTO', pop_s(lt, wt(2, 'combo') + .1, .35))
    counter(im, CL[2]['t0'] - .15 + lt, f)
    return im

def sc3(lt, d_, f):
    im = bg((110, 20, 90), 700); d = ImageDraw.Draw(im)
    d.rectangle((60, 520, 660, 820), fill=(30, 26, 40)); d.rectangle((60, 500, 660, 540), fill=(200, 40, 120))
    d.text((360, 520), 'MALL', font=F('Inter-Black.otf', 30), fill='white', anchor='mm')
    for k in range(3): d.rectangle((90 + k * 195, 570, 250 + k * 195, 800), fill=(255, 220, 160))
    for k, (x, col) in enumerate([(200, (230, 38, 47)), (360, (240, 200, 60)), (520, (90, 160, 240))]):  # bolsas de compra
        s = pop_s(lt, .15 + k * .2, .35); y = 1020 - (1 - min(1, (lt - .15 - k * .2) / .3 if lt > .15 + k * .2 else 0)) * 300
        if s:
            d.rounded_rectangle((x - 70 * s, y - 90 * s, x + 70 * s, y + 90 * s), 10, fill=col)
            d.arc((x - 35 * s, y - 130 * s, x + 35 * s, y - 60 * s), 180, 360, fill=(30, 30, 30), width=6)
    price_tag(im, W / 2, 660, 'GASTO', pop_s(lt, wt(3, 'centro') + .05, .35))
    counter(im, CL[3]['t0'] - .15 + lt, f)
    return im

def sc4(lt, d_, f):
    tl_ = wt(4, 'lunes'); im = bg((60, 60, 70) if lt > tl_ else (90, 14, 20)); d = ImageDraw.Draw(im)
    if lt < tl_ - .1:  # recibo
        h = 520 * ease(lt / .6); x0 = 160
        d.rectangle((x0, 420, W - x0, 420 + h), fill=(245, 245, 240))
        items = [('Cine + crispetas', '✔'), ('Combo de comida', '✔'), ('Centro comercial', '✔')]
        for k, (a, b) in enumerate(items):
            y = 480 + k * 70
            if y < 420 + h - 20:
                d.text((x0 + 30, y), a, font=F('Inter-SemiBold.otf', 26), fill=(40, 40, 46), anchor='lm'); d.text((W - x0 - 30, y), 'PAGADO', font=F('Inter-Bold.otf', 20), fill=RED, anchor='rm')
        if h > 360:
            d.line((x0 + 30, 700, W - x0 - 30, 700), fill=(150, 150, 150), width=3)
            s = pop_s(lt, wt(4, 'dinero') - .05)
            if s: d.text((W / 2, 800), 'SE FUE', font=F('Inter-Black.otf', max(10, int(96 * s))), fill=RED, anchor='mm')
    else:
        q = ease((lt - tl_ + .1) / .4)
        wallet_draw(d, W / 2, 800, 1.3, empty=True)
        for k in range(3):
            y = 640 - 60 * q - k * 30 + 8 * math.sin(lt * 6 + k); x = W / 2 - 60 + k * 60 + 20 * math.sin(lt * 3 + k)
            d.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(180, 180, 190))
        d.text((W / 2, 1020), 'LUNES: VACÍA', font=F('Inter-Black.otf', 60), fill=(200, 200, 210, int(255 * q)), anchor='mm')
    return im

def sc5(lt, d_, f):
    im = bg(); d = ImageDraw.Draw(im); tv = wt(5, 'activas')
    d.rounded_rectangle((40, 460, 340, 1000), 26, fill=(30, 30, 36), outline=(60, 60, 70), width=3)
    d.text((190, 520), 'FIN DE', font=F('Inter-Black.otf', 32), fill=(150, 150, 160), anchor='mm'); d.text((190, 560), 'SEMANA', font=F('Inter-Black.otf', 32), fill=(150, 150, 160), anchor='mm')
    popcorn(d, 190, 720, .7)
    d.text((190, 800), 'se acaba', font=F('Inter-SemiBold.otf', 26), fill=(120, 120, 130), anchor='mm')
    s = pop_s(lt, tv - .2, .45)
    if s:
        g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).rounded_rectangle((360, 440, 700, 1020), 40, fill=int(200 * min(1, s)))
        im = Image.composite(Image.new('RGBA', (W, H), (255, 70, 70, 255)), im, g.filter(ImageFilter.GaussianBlur(30))); d = ImageDraw.Draw(im)
        d.rounded_rectangle((380, 460, 680, 1000), 26, fill=RED)
        lg = LOGO.resize((260, int(260 * LOGO.height / LOGO.width)))
        wbg = Image.new('RGBA', (280, lg.height + 20), (255, 255, 255, 255)); m = Image.new('L', wbg.size, 0); ImageDraw.Draw(m).rounded_rectangle((0, 0, wbg.width - 1, wbg.height - 1), 16, fill=255); wbg.putalpha(m)
        im.alpha_composite(wbg, (390, 480)); im.alpha_composite(lg, (400, 490)); d = ImageDraw.Draw(im)
        d.text((530, 700), 'ACTÍVATE', font=F('Inter-Black.otf', max(10, int(50 * s))), fill='white', anchor='mm')
        d.text((530, 800), 'membresía', font=F('Inter-Bold.otf', 28), fill='white', anchor='mm')
    d.ellipse((W / 2 - 40, 690, W / 2 + 40, 770), fill=(10, 10, 14), outline=(255, 255, 255), width=4)
    d.text((W / 2, 730), 'VS', font=F('Inter-Black.otf', 32), fill='white', anchor='mm')
    return im

TOOLS = [('cursos', 'Cursos'), ('portada', 'Mi Portada'), ('marketplace', 'Marketplace'), ('tienda', 'Mi Tienda'), ('tareas', 'Tareas diarias'), ('comunidad', 'Comunidad'), ('comisiones', 'Comisiones directas')]
def icon(d, k, x, y):
    c = 'white'
    if k == 0: d.polygon([(x - 34, y - 22), (x, y - 38), (x + 34, y - 22), (x, y - 6)], fill=c); d.rectangle((x - 20, y - 14, x + 20, y + 8), fill=c)
    elif k == 1: d.rounded_rectangle((x - 30, y - 34, x + 30, y + 34), 8, outline=c, width=5); d.ellipse((x - 12, y - 24, x + 12, y), fill=c); d.rectangle((x - 18, y + 8, x + 18, y + 14), fill=c)
    elif k == 2: d.polygon([(x - 34, y - 10), (x + 34, y - 10), (x + 26, y + 30), (x - 26, y + 30)], fill=c); d.arc((x - 18, y - 36, x + 18, y + 4), 180, 360, fill=c, width=5)
    elif k == 3: d.rectangle((x - 30, y - 6, x + 30, y + 32), fill=c); d.polygon([(x - 36, y - 6), (x - 26, y - 34), (x + 26, y - 34), (x + 36, y - 6)], fill=c)
    elif k == 4: d.rounded_rectangle((x - 32, y - 30, x + 32, y + 32), 8, outline=c, width=5); d.line((x - 16, y, x - 4, y + 12, x + 18, y - 12), fill=c, width=6)
    elif k == 6:
        d.line((x - 30, y + 24, x - 8, y, x + 8, y + 10, x + 30, y - 26), fill=c, width=6); d.polygon([(x + 32, y - 34), (x + 34, y - 12), (x + 16, y - 26)], fill=c)
    else:
        for dx in (-22, 0, 22): d.ellipse((x + dx - 11, y - 28, x + dx + 11, y - 6), fill=c); d.rounded_rectangle((x + dx - 15, y - 2, x + dx + 15, y + 30), 10, fill=c)

def sc6(lt, d_, f):
    im = bg(); d = ImageDraw.Draw(im)
    for k, (w, lab) in enumerate(TOOLS):
        r, c = k // 2, k % 2; x, y = 200 + c * 320, 480 + r * 205
        if k == 6: x = W / 2
        s = pop_s(lt, wt(6, w) - .1, .35)
        if s <= 0.02: continue
        bw, bh = (140 if k < 6 else 300) * s, 90 * s
        d.rounded_rectangle((x - bw, y - bh, x + bw, y + bh), 26, fill=(26, 26, 32), outline=RED, width=4)
        d.ellipse((x - 46 * s, y - 70 * s, x + 46 * s, y + 22 * s), fill=RED)
        if s > .6: icon(d, k, x, y - 24 * s)
        d.text((x, y + 56 * s), lab, font=F('Inter-Black.otf', max(8, int(28 * s))), fill='white', anchor='mm')
    return im

def sc7(lt, d_, f):
    im = bg(); d = ImageDraw.Draw(im); te = wt(7, 'otro')
    d.rounded_rectangle((40, 440, 340, 960), 26, fill=(30, 30, 36))
    d.rounded_rectangle((110, 500, 270, 650), 14, fill=(240, 240, 244)); d.rectangle((110, 500, 270, 540), fill=(150, 150, 160))
    d.text((190, 595), 'DOM', font=F('Inter-Black.otf', 40), fill=(60, 60, 66), anchor='mm')
    if lt > .4: d.line((110, 500, 270, 650), fill=RED, width=10); d.line((270, 500, 110, 650), fill=RED, width=10)
    d.text((190, 720), 'Gasto que', font=F('Inter-Bold.otf', 28), fill=(160, 160, 170), anchor='mm'); d.text((190, 760), 'se acaba', font=F('Inter-Bold.otf', 28), fill=(160, 160, 170), anchor='mm')
    s = ease((lt - te + .2) / .4)
    if s > 0:
        d.rounded_rectangle((380, 440, 680, 960), 26, fill=RED)
        pts = [(410 + k * 30, 640 - (k / 8) ** 1.6 * 140 * s - 10 * math.sin(k * 1.3)) for k in range(9)]
        d.line(pts, fill='white', width=6, joint='curve'); d.polygon([(pts[-1][0] + 6, pts[-1][1] - 18), (pts[-1][0] + 22, pts[-1][1] + 6), (pts[-1][0] - 6, pts[-1][1] + 6)], fill='white')
        d.text((530, 700), 'Herramientas', font=F('Inter-Black.otf', 30), fill='white', anchor='mm'); d.text((530, 740), 'que trabajan', font=F('Inter-Bold.otf', 26), fill='white', anchor='mm'); d.text((530, 775), 'para ti', font=F('Inter-Bold.otf', 26), fill='white', anchor='mm')
        for k, w in enumerate(['constancia', 'disciplina']):
            q = pop_s(lt, wt(7, w) - .1, .3)
            if q:
                y = 850 + k * 52; d.rounded_rectangle((400, y - 22, 660, y + 22), 22, fill=(255, 255, 255))
                d.text((530, y), w.upper(), font=F('Inter-Black.otf', max(8, int(24 * q))), fill=RED, anchor='mm')
    return im

def sc8(lt, d_, f):
    im = bg(); d = ImageDraw.Draw(im); tr = wt(8, 'regístrate')
    m = M_PUL.resize((520, int(520 * M_PUL.height / M_PUL.width)))
    im.alpha_composite(m, ((W - m.width) // 2, 1300 - m.height + int((1 - ease(lt / .4)) * 300)))
    q = pop_s(lt, tr - .2, .4)
    if q:
        d = ImageDraw.Draw(im); bw = 270 * q; pul = 1 + .05 * math.sin(lt * 8)
        d.rounded_rectangle((W / 2 - bw * pul, 470 - 50 * q * pul, W / 2 + bw * pul, 470 + 50 * q * pul), 50, fill='white')
        d.text((W / 2, 470), 'LINK EN MI PERFIL', font=F('Inter-Black.otf', max(8, int(38 * q))), fill=RED, anchor='mm')
    return im

B.SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7, sc8]

def clicks():  # [momento, tipo de efecto]
    ev = []
    for ci, w, n, k in [(1, 'cine', 0, 'cash'), (2, 'combo', 0, 'cash'), (3, 'centro', 0, 'cash'), (4, 'dinero', 0, 'cash'),
                        (4, 'lunes', 0, 'down'), (5, 'activas', 0, 'ding'), (8, 'regístrate', 0, 'pop')]:
        ev.append([CL[ci]['t0'] - 0.15 + wt(ci, w, n), k])
    for w in ['cursos', 'portada', 'marketplace', 'tienda', 'tareas', 'comunidad', 'comisiones']: ev.append([CL[6]['t0'] - 0.15 + wt(6, w), 'pop'])
    for w in ['constancia', 'disciplina']: ev.append([CL[7]['t0'] - 0.15 + wt(7, w), 'ding'])
    ev.append([CL[5]['t0'] - 0.7, 'riser'])
    for c in CL[1:]: ev.append([c['t0'] - 0.2, 'whoosh'])
    return ev

if __name__ == '__main__':
    B.main(clicks)
