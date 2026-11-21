"""Día 19 — reel "Si no te ven en internet, no te encuentran" (tu negocio en internet).
Uso (en la carpeta de trabajo, después de scripts/voz.py):
    python scripts/render.py meta        -> clicks.json y logo_t.json (los usa audio.py)
    python scripts/render.py 0 2000      -> frames/00000.jpg ...
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import promo_base as B
from promo_base import *

B.LOGO_T = CL[7]['t0'] + CL[7]['d'] - 0.1
B.KEY = {'internet', 'tres', 'diez', 'cierran', 'primer', 'mitad', 'dos', 'latinoamericanos', 'esperas', 'celular', 'crecen', 'redes', 'barrio',
         'ciudad', 'país', 'sumiago', 'ganas', 'bio', 'link', 'regístrate', 'posicionar'}
B.END_TXT1 = 'Posiciona tu negocio'; B.END_TXT2 = 'LINK EN MI BIO'

# ---------- escenas ----------
def make_street():
    im = Image.new('RGBA', (W, H)); d = ImageDraw.Draw(im)
    for y in range(0, H, 4): d.rectangle((0, y, W, y + 4), fill=mix((16, 18, 44), (6, 6, 16), y / H))
    rr = random.Random(4)
    for k in range(40):
        x, y = rr.randint(0, W), rr.randint(20, 420); d.ellipse((x, y, x + 2, y + 2), fill=(255, 255, 255, 160))
    d.ellipse((560, 90, 630, 160), fill=(235, 235, 215))
    x = -20
    while x < W:
        bw = rr.randint(110, 190); bh = rr.randint(500, 760)
        d.rectangle((x, H - 330 - bh, x + bw - 6, H - 330), fill=(20, 22, 40))
        for wy in range(H - 330 - bh + 24, H - 360, 40):
            for wx in range(x + 16, x + bw - 30, 30):
                if rr.random() < .35: d.rectangle((wx, wy, wx + 14, wy + 20), fill=(255, 205, 120) if rr.random() < .6 else (130, 180, 255))
        x += bw
    d.rectangle((0, H - 330, W, H - 300), fill=(48, 50, 66)); d.rectangle((0, H - 300, W, H), fill=(26, 26, 36))
    for k in range(0, W, 120): d.rectangle((k, H - 150, k + 60, H - 140), fill=(80, 80, 90))
    return im
STREET = make_street()

def shop(im, x, y, w, h, closed=0.0, lit=1.0, sign='TIENDA', gray=0.0):
    L = Image.new('RGBA', (w + 40, h + 40), (0, 0, 0, 0)); d = ImageDraw.Draw(L); o = 20
    wall = mix((150, 120, 100), (70, 70, 76), gray)
    d.rectangle((o, o + h * .18, o + w, o + h), fill=wall)
    for k in range(6):
        c = mix(RED if k % 2 == 0 else (245, 245, 245), (90, 90, 96), gray)
        d.polygon([(o + k * w / 6, o + h * .18), (o + (k + 1) * w / 6, o + h * .18), (o + (k + 1) * w / 6 + 4, o + h * .32), (o + k * w / 6 - 4, o + h * .32)], fill=c)
    d.rectangle((o - 4, o, o + w + 4, o + h * .18), fill=(30, 30, 38))
    fs = max(10, int(h * .11)); sc = mix((255, 200, 90), (110, 110, 118), max(gray, 1 - lit))
    d.text((o + w / 2, o + h * .09), sign, font=F('Inter-Black.otf', fs), fill=sc, anchor='mm')
    gl = mix((255, 220, 150), (40, 44, 60), max(gray, 1 - lit))
    d.rectangle((o + w * .08, o + h * .4, o + w * .55, o + h * .9), fill=gl)
    d.rectangle((o + w * .64, o + h * .4, o + w * .92, o + h), fill=mix((90, 60, 40), (50, 50, 56), gray))
    if closed > 0:
        ch = (h * .82) * closed
        d.rectangle((o, o + h * .18, o + w, o + h * .18 + ch), fill=(120, 124, 136))
        for yy in range(int(o + h * .18), int(o + h * .18 + ch), max(4, h // 30)): d.line((o, yy, o + w, yy), fill=(96, 100, 112), width=2)
        if closed > .9:
            d.rounded_rectangle((o + w * .15, o + h * .5, o + w * .85, o + h * .68), 6, fill=RED)
            d.text((o + w / 2, o + h * .59), 'CERRADO', font=F('Inter-Black.otf', max(9, int(h * .09))), fill='white', anchor='mm')
    im.alpha_composite(L, (int(x - o), int(y - o)))

def person(d, x, y, s=1.0, phone=False, col=(14, 14, 22)):
    d.ellipse((x - 16 * s, y - 120 * s, x + 16 * s, y - 88 * s), fill=col)
    d.rounded_rectangle((x - 24 * s, y - 86 * s, x + 24 * s, y - 20 * s), int(14 * s), fill=col)
    d.rectangle((x - 18 * s, y - 24 * s, x - 4 * s, y), fill=col); d.rectangle((x + 4 * s, y - 24 * s, x + 18 * s, y), fill=col)
    if phone:
        d.rounded_rectangle((x + 8 * s, y - 84 * s, x + 24 * s, y - 60 * s), 3, fill=(130, 190, 255))

def pill(d, cx, cy, txt, fill=RED, fs=30, a=1.0):
    f = F('Inter-Black.otf', fs); tw = d.textlength(txt, font=f)
    d.rounded_rectangle((cx - tw / 2 - 22, cy - fs * .9, cx + tw / 2 + 22, cy + fs * .9), int(fs * .9), fill=fill + (int(255 * a),))
    d.text((cx, cy), txt, font=f, fill=(255, 255, 255, int(255 * a)), anchor='mm')

def sc0(lt, d_, f):
    im = STREET.copy(); shop(im, 160, 520, 400, 440, sign='MI NEGOCIO', lit=.6)
    pz = 1 + .06 * max(0, 1 - abs(lt - wt(0, 'escucha')) / .15)
    m = MA_BIG if talking(f) else MC_BIG
    mm = m.resize((int(m.width * pz), int(m.height * pz)))
    im.alpha_composite(mm, ((W - mm.width) // 2, 1330 - int(mm.height * .8)))
    a = back_out(lt / .35)
    if a > 0:
        r = 60 * a; d = ImageDraw.Draw(im)
        d.ellipse((W - 150 - r, 430 - r, W - 150 + r, 430 + r), fill=RED)
        d.text((W - 150, 432), '!', font=F('Inter-Black.otf', int(80 * a) + 1), fill='white', anchor='mm')
    if lt > wt(0, 'internet') - .1:
        d = ImageDraw.Draw(im); q = ease((lt - wt(0, 'internet') + .1) / .2)
        d.rounded_rectangle((60, 380, 330, 470), 18, fill=(255, 255, 255, int(240 * q)))
        d.text((195, 410), 'Búsquedas de', font=F('Inter-SemiBold.otf', 20), fill=(110, 110, 120, int(255 * q)), anchor='mm')
        d.text((195, 445), 'tu negocio: 0', font=F('Inter-Black.otf', 28), fill=RED + (int(255 * q),), anchor='mm')
    return im

def sc1(lt, d_, f):
    im = Image.new('RGBA', (W, H), (10, 10, 18, 255)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 400, 'AÑO 1', RED, 34, ease(lt / .3))
    tc = wt(1, 'cierran'); idx = [1, 5, 8]
    for k in range(10):
        r, c = k // 5, k % 5; x, y = 30 + c * 136, 520 + r * 260
        a = ease((lt - k * .06) / .25)
        if a <= 0: continue
        cl = ease((lt - tc - idx.index(k) * .18) / .25) if k in idx else 0
        sh = (math.sin(lt * 60) * 4 * (1 - ease((lt - tc - .3 - (idx.index(k) * .18 if k in idx else 0)) / .3))) if k in idx and lt > tc else 0
        shop(im, x + sh, y + (1 - a) * 40, 120, 200, closed=cl, gray=cl * .6, sign='')
    if lt > tc:
        d = ImageDraw.Draw(im); q = ease((lt - tc - .5) / .3)
        d.text((W / 2, 1110), '3 de cada 10', font=F('Inter-Black.otf', 64), fill=(255, 255, 255, int(255 * q)), anchor='mm')
        d.text((W / 2, 1172), 'cierran en el primer año', font=F('Inter-SemiBold.otf', 30), fill=(170, 170, 180, int(255 * q)), anchor='mm')
    d = ImageDraw.Draw(im); d.text((W / 2, 1240), 'Fuentes: INEGI (México) y Confecámaras (Colombia)', font=F('Inter-Medium.otf', 18), fill=(110, 110, 120), anchor='mm')
    return im

def sc2(lt, d_, f):
    im = Image.new('RGBA', (W, H), (10, 10, 18, 255)); d = ImageDraw.Draw(im)
    pill(d, W / 2, 400, '2 AÑOS', (60, 60, 72), 34)
    tu = wt(2, 'mitad'); q = ease((lt - tu) / .35)
    for k in range(4):
        x = 30 + k * 168; cl = k in (0, 2)
        shop(im, x, 620, 150, 240, closed=q if cl else 0, gray=q * .7 if cl else 0, sign='')
    d = ImageDraw.Draw(im); a = ease((lt - tu - .3) / .3)
    d.text((W / 2, 1010), 'Casi la mitad', font=F('Inter-Black.otf', 64), fill=(255, 255, 255, int(255 * a)), anchor='mm')
    d.text((W / 2, 1072), 'no llega a los 2 años', font=F('Inter-SemiBold.otf', 30), fill=(170, 170, 180, int(255 * a)), anchor='mm')
    d.text((W / 2, 1240), 'Fuentes: INEGI (México) y Confecámaras (Colombia)', font=F('Inter-Medium.otf', 18), fill=(110, 110, 120), anchor='mm')
    return im

def sc3(lt, d_, f):
    im = STREET.copy(); tl_ = wt(3, 'letrero'); te = wt(3, 'esperas')
    shop(im, 120, 470, 480, 520, sign='MI NEGOCIO', lit=ease((lt - tl_) / .2) * .9 + .1)
    d = ImageDraw.Draw(im)
    for k in range(3):  # gente que pasa sin entrar
        x = (lt * 160 + k * 300) % (W + 200) - 100
        person(d, x, 1140, 1.3)
    if lt > te - .2:  # reloj
        a = ease((lt - te + .2) / .25); cx, cy, r = 600, 400, 60
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 255, int(255 * a)), outline=(30, 30, 30), width=5)
        ang = (lt - te) * 8
        d.line((cx, cy, cx + 40 * math.sin(ang), cy - 40 * math.cos(ang)), fill=(30, 30, 30), width=5)
        d.line((cx, cy, cx + 26 * math.sin(ang / 12), cy - 26 * math.cos(ang / 12)), fill=RED, width=6)
    return im

def sc4(lt, d_, f):
    tc = min(wt(4, 'celular'), 1.3)
    im = STREET.copy(); d = ImageDraw.Draw(im)
    for k in range(5):
        x = (lt * 130 * (1 if k % 2 else -1) + k * 170) % (W + 200) - 100
        person(d, x, 1150 - (k % 2) * 30, 1.4, phone=True)
    if lt > tc - .5:
        q = ease((lt - tc + .5) / .35); y0 = 380 + (1 - q) * 900
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.rounded_rectangle((150, y0, 570, y0 + 760), 44, fill=(16, 16, 20), outline=(70, 70, 80), width=6)
        dl.rounded_rectangle((166, y0 + 16, 554, y0 + 744), 34, fill=(245, 245, 248))
        txt = 'panadería cerca de mí'; n = int(len(txt) * ease((lt - tc + .2) / .8))
        dl.rounded_rectangle((186, y0 + 50, 534, y0 + 100), 25, fill=(255, 255, 255), outline=(210, 210, 220), width=2)
        dl.text((210, y0 + 75), txt[:n], font=F('Inter-Medium.otf', 22), fill=(40, 40, 50), anchor='lm')
        for j, nm in enumerate(['Panadería La Espiga', 'Pan y Café 24h', 'Delicias del Horno']):
            a = ease((lt - tc - .4 - j * .15) / .2); yy = y0 + 140 + j * 120
            if a <= 0: continue
            dl.rounded_rectangle((186, yy, 534, yy + 100), 16, fill=(255, 255, 255, int(255 * a)), outline=(225, 225, 232, int(255 * a)), width=2)
            dl.ellipse((202, yy + 30, 242, yy + 70), fill=RED + (int(255 * a),))
            dl.text((258, yy + 36), nm, font=F('Inter-Bold.otf', 22), fill=(30, 30, 38, int(255 * a)), anchor='lm')
            dl.text((258, yy + 68), '★★★★★  · 0,4 km', font=F('Inter-Medium.otf', 18), fill=(230, 160, 30, int(255 * a)), anchor='lm')
        a = ease((lt - tc - 1.0) / .3)
        if a > 0:
            yy = y0 + 520
            dl.rounded_rectangle((186, yy, 534, yy + 100), 16, fill=(250, 235, 236, int(255 * a)), outline=RED + (int(255 * a),), width=3)
            dl.text((360, yy + 34), 'Tu negocio', font=F('Inter-Black.otf', 24), fill=(30, 30, 38, int(255 * a)), anchor='mm')
            dl.text((360, yy + 68), 'no aparece', font=F('Inter-Bold.otf', 22), fill=RED + (int(255 * a),), anchor='mm')
        im.alpha_composite(L)
    return im

def sc5(lt, d_, f):
    im = Image.new('RGBA', (W, H), (12, 14, 26, 255)); d = ImageDraw.Draw(im)
    rr = random.Random(11)
    for k in range(26):
        x = rr.randint(0, W); d.line((x, 0, x + rr.randint(-200, 200), H), fill=(30, 34, 54), width=rr.randint(2, 8))
    for k in range(20):
        y = rr.randint(0, H); d.line((0, y, W, y + rr.randint(-150, 150)), fill=(30, 34, 54), width=rr.randint(2, 8))
    cx, cy = W / 2, 760
    for k, (w, R) in enumerate([('barrio', 120), ('ciudad', 250), ('país', 380)]):
        tw = wt(5, w); q = ease((lt - tw + .2) / .4)
        if q <= 0: continue
        r = R * back_out((lt - tw + .2) / .5)
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L)
        dl.ellipse((cx - r, cy - r, cx + r, cy + r), fill=RED + (int(40 * q),), outline=RED + (int(220 * q),), width=5)
        im.alpha_composite(L); d = ImageDraw.Draw(im)
        pill(d, cx, cy - R - 2, w.upper(), RED, 24, q)
        rp = random.Random(k)
        for j in range(4 + k * 4):
            a = rp.random() * 2 * math.pi; dd = rp.uniform(.4, .95) * R
            px, py = cx + math.cos(a) * dd, cy + math.sin(a) * dd
            if (lt - tw) > j * .05:
                d.ellipse((px - 7, py - 7, px + 7, py + 7), fill=GOLD)
    d.ellipse((cx - 30, cy - 70, cx + 30, cy - 10), fill='white'); d.polygon([(cx - 26, cy - 34), (cx + 26, cy - 34), (cx, cy + 10)], fill='white')
    d.ellipse((cx - 13, cy - 53, cx + 13, cy - 27), fill=RED)
    tr = wt(5, 'redes')
    if lt > tr - .2:  # iconos sociales genéricos
        for k, ic in enumerate(['heart', 'chat', 'share']):
            a = ease((lt - tr + .2 - k * .12) / .25); x = 180 + k * 180; y = 1190 - 20 * math.sin(lt * 3 + k)
            if a <= 0: continue
            d.ellipse((x - 46, y - 46, x + 46, y + 46), fill=(255, 255, 255, int(255 * a)))
            if ic == 'heart':
                d.ellipse((x - 24, y - 20, x, y + 4), fill=RED); d.ellipse((x, y - 20, x + 24, y + 4), fill=RED); d.polygon([(x - 23, y - 4), (x + 23, y - 4), (x, y + 24)], fill=RED)
            elif ic == 'chat':
                d.rounded_rectangle((x - 26, y - 20, x + 26, y + 14), 12, fill=(40, 40, 50)); d.polygon([(x - 12, y + 12), (x - 18, y + 26), (x + 2, y + 12)], fill=(40, 40, 50))
            else:
                d.polygon([(x - 24, y + 4), (x + 22, y - 22), (x + 10, y + 24)], fill=(40, 40, 50))
            d.text((x, y + 70), ['+1,2 mil', '+340', '+890'][k], font=F('Inter-Black.otf', 24), fill='white', anchor='mm')
    return im

def sc6(lt, d_, f):
    im = Image.new('RGBA', (W, H), (10, 10, 14, 255))
    g = Image.new('L', (W, H), 0); ImageDraw.Draw(g).ellipse((-300, 300, W + 300, 1400), fill=110)
    im = Image.composite(Image.new('RGBA', (W, H), (90, 14, 20, 255)), im, g.filter(ImageFilter.GaussianBlur(160))); d = ImageDraw.Draw(im)
    q = ease(lt / .4); x0, y0 = 70, 380 + (1 - q) * 300
    d.rounded_rectangle((x0, y0, x0 + 420, y0 + 780), 46, fill=(16, 16, 20), outline=(70, 70, 80), width=6)
    d.rounded_rectangle((x0 + 16, y0 + 16, x0 + 404, y0 + 764), 34, fill=(246, 246, 248))
    d.rounded_rectangle((x0 + 16, y0 + 16, x0 + 404, y0 + 170), 34, fill=RED); d.rectangle((x0 + 16, y0 + 120, x0 + 404, y0 + 170), fill=RED)
    d.ellipse((x0 + 40, y0 + 120, x0 + 140, y0 + 220), fill='white', outline=(246, 246, 248), width=6)
    d.text((x0 + 90, y0 + 170), 'MN', font=F('Inter-Black.otf', 34), fill=RED, anchor='mm')
    d.text((x0 + 40, y0 + 255), 'Mi Negocio', font=F('Inter-Black.otf', 32), fill=(25, 25, 30), anchor='lm')
    d.text((x0 + 40, y0 + 292), '★★★★★  Abierto ahora', font=F('Inter-SemiBold.otf', 20), fill=(230, 160, 30), anchor='lm')
    d.text((x0 + 40, y0 + 340), 'Visitas este mes', font=F('Inter-SemiBold.otf', 20), fill=(120, 120, 130), anchor='lm')
    pr = ease((lt - .5) / 2.5); n = int(12480 * pr)
    d.text((x0 + 40, y0 + 380), f'{n:,}'.replace(',', '.'), font=F('Inter-Black.otf', 46), fill=(25, 25, 30), anchor='lm')
    pts = []
    for k in range(12):
        xx = x0 + 40 + k * 30; yy = y0 + 640 - (20 + 180 * (k / 11) ** 2 + 20 * math.sin(k)) * min(1, pr * 12 / max(1, k + 1) * (k + 1) / 12 * 1.0 + 0)
        pts.append((xx, yy))
    vis = pts[:max(2, int(12 * pr) + 1)]
    d.line(vis, fill=RED, width=6, joint='curve')
    for p in vis: d.ellipse((p[0] - 5, p[1] - 5, p[0] + 5, p[1] + 5), fill=RED)
    tg = wt(6, 'ganas')
    for k in range(8):
        s = (lt * .6 + k * .27) % 1
        if lt < tg - .3: break
        cx_ = 520 + (k * 47) % 170; cy_ = lerp(1250, 420, s)
        d.ellipse((cx_ - 22, cy_ - 22, cx_ + 22, cy_ + 22), fill=GOLD, outline=(200, 140, 30), width=4)
        d.text((cx_, cy_), '$', font=F('Inter-Black.otf', 26), fill=(150, 90, 10), anchor='mm')
    mp = M_PUL.resize((300, int(300 * M_PUL.height / M_PUL.width)))
    im.alpha_composite(mp, (420, 1290 - mp.height + int((1 - ease((lt - .3) / .4)) * 400)))
    if lt > tg - .2:
        d = ImageDraw.Draw(im); pill(d, W / 2, 1220, 'APRENDE  +  GANA', RED, 32, ease((lt - tg + .2) / .3))
    return im

def sc7(lt, d_, f):
    im = STREET.copy(); d = ImageDraw.Draw(im)
    tr = wt(7, 'regístrate')
    m = MA_BIG if talking(f) else MC_BIG
    im.alpha_composite(m, ((W - m.width) // 2, 1300 - int(m.height * .85)))
    a = ease(lt / .3)
    L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); al = int(255 * a); yo = (1 - a) * 60
    x0, y0 = 70, 920 + yo
    dl.rounded_rectangle((x0, y0, W - 70, y0 + 230), 24, fill=(255, 255, 255, al))
    dl.ellipse((x0 + 24, y0 + 24, x0 + 104, y0 + 104), fill=RED + (al,))
    dl.text((x0 + 64, y0 + 64), 'S', font=F('Inter-Black.otf', 44), fill=(255, 255, 255, al), anchor='mm')
    dl.text((x0 + 124, y0 + 48), '@sumiago', font=F('Inter-Black.otf', 30), fill=(25, 25, 32, al), anchor='lm')
    dl.text((x0 + 124, y0 + 84), 'Posiciona tu negocio en internet', font=F('Inter-Medium.otf', 20), fill=(110, 110, 125, al), anchor='lm')
    pul = .5 + .5 * math.sin(lt * 9) if lt > tr - .2 else 0
    dl.rounded_rectangle((x0 + 24, y0 + 136, W - 94, y0 + 200), 16, fill=mix((240, 240, 246), RED, pul) + (al,))
    dl.text((x0 + 50, y0 + 168), 'sumiago.com  ·  Regístrate aquí', font=F('Inter-Bold.otf', 26), fill=mix((30, 30, 40), (255, 255, 255), pul) + (al,), anchor='lm')
    im.alpha_composite(L); d = ImageDraw.Draw(im)
    if lt > tr - .6:
        q = ease((lt - (tr - .6)) / .5); cursor(d, lerp(W - 60, W - 200, q), lerp(1250, y0 + 175, q), (lt - tr) / .4 if 0 < lt - tr < .4 else 0)
    return im

B.SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6, sc7]

def clicks():  # golpes de sonido en los datos y en "regístrate"
    return [CL[ci]['t0'] - 0.15 + wt(ci, w, n) for ci, w, n in [(1, 'cierran', 0), (2, 'mitad', 0), (7, 'regístrate', 0)]]

if __name__ == '__main__':
    B.main(clicks)
