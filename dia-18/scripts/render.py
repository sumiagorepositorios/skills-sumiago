"""Día 18 — reel "Crear un canal en 2026: siguiente, siguiente y finalizar".
Uso (en la carpeta de trabajo, después de scripts/voz.py):
    python scripts/render.py meta        -> clicks.json y logo_t.json (los usa audio.py)
    python scripts/render.py 0 2000      -> frames/00000.jpg ...
"""
import os, sys, math, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import promo_base as B
from promo_base import *

B.LOGO_T = CL[6]['t0'] + CL[6]['d'] - 0.15
B.KEY = {'siguiente', 'finalizar', 'nicho', 'visitas', 'competencia', 'viral', 'estructura', 'historias', 'guion', 'voz',
         'imágenes', 'publicas', 'mañana', 'bio', 'link', 'regístrate'}
B.END_TXT1 = 'Visita la bio de mi perfil'; B.END_TXT2 = 'REGÍSTRATE EN EL LINK'

# ---------- escenas ----------
def sc0(lt, d_, f):
    t_s1, t_s2, t_fin = wt(0, 'siguiente', 0), wt(0, 'siguiente', 1), wt(0, 'finalizar')
    if lt < 1.6:  # mascota en su cuarto
        im = room(0); im = screen_glow(im, W / 2, 1200, 500, 200, 1.0)
        z = 1 + .02 * lt
        m = MA_BIG if talking(f) else MC_BIG
        mm = m.resize((int(m.width * z), int(m.height * z)))
        im.alpha_composite(mm, ((W - mm.width) // 2, 1300 - int(mm.height * .78)))
        return im
    step = 0 if lt < t_s1 + .1 else (1 if lt < t_s2 + .1 else 2)
    im, d = window(room(0), min(step, 1) if step < 2 else 1)
    cx = CX0
    if step == 0:
        d.rounded_rectangle((cx + 10, WY + 80, cx + 90, WY + 140), 14, fill=RED); d.polygon([(cx + 40, WY + 96), (cx + 40, WY + 124), (cx + 64, WY + 110)], fill='white')
        d.text((cx + 10, WY + 180), 'Bienvenido al asistente', font=F('Inter-Black.otf', 28), fill=(25, 25, 32), anchor='lm')
        d.text((cx + 10, WY + 216), 'de tu canal de videos', font=F('Inter-Black.otf', 28), fill=(25, 25, 32), anchor='lm')
        d.text((cx + 10, WY + 262), 'Te guiamos paso a paso.', font=F('Inter-Medium.otf', 20), fill=(120, 120, 135), anchor='lm')
        tt = t_s1
    elif step == 1:
        d.text((cx + 10, WY + 90), 'Componentes', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
        for k, s in enumerate(['Nicho que funcione', 'Estructura viral', 'Guion, voz e imágenes', 'Publicación diaria']):
            y = WY + 150 + k * 50; a = ease((lt - t_s1 - .1 - k * .12) / .2)
            d.rounded_rectangle((cx + 10, y - 14, cx + 38, y + 14), 6, fill=GREEN if a > .5 else (210, 212, 222))
            if a > .5: d.line((cx + 16, y, cx + 22, y + 7, cx + 33, y - 7), fill='white', width=4)
            d.text((cx + 52, y), s, font=F('Inter-SemiBold.otf', 21), fill=(40, 40, 50), anchor='lm')
        tt = t_s2
    else:
        d.text((cx + 10, WY + 90), 'Instalando canal...', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
        pr = ease((lt - t_s2 - .1) / max(.2, t_fin - t_s2 - .2))
        d.rounded_rectangle((cx + 10, WY + 160, cx + 430, WY + 190), 15, fill=(222, 224, 234))
        d.rounded_rectangle((cx + 10, WY + 160, cx + 10 + 420 * pr, WY + 190), 15, fill=RED)
        d.text((cx + 10, WY + 225), f'{int(pr * 100)}%', font=F('Inter-Bold.otf', 22), fill=(120, 120, 135), anchor='lm')
        tt = t_fin
    btn(d, 'Finalizar' if step == 2 else 'Siguiente  ›', (lt - tt) / .2 if 0 < lt - tt < .2 else 0)
    bx, by = (BTN[0] + BTN[2]) / 2, (BTN[1] + BTN[3]) / 2 + 6
    px = lerp(bx - 220, bx, ease((lt - (tt - .5)) / .35)); py = lerp(by - 150, by, ease((lt - (tt - .5)) / .35))
    cursor(d, px, py, (lt - tt) / .35 if 0 < lt - tt < .35 else 0)
    if step == 2 and lt > t_fin:
        a = ease((lt - t_fin) / .2); d.rounded_rectangle((W / 2 - 170, 360 - 40 * (1 - a), W / 2 + 170, 410 - 40 * (1 - a)), 25, fill=GREEN)
        d.text((W / 2, 385 - 40 * (1 - a)), 'Canal listo', font=F('Inter-Black.otf', 26), fill='white', anchor='mm')
    return im

NICHOS = ['Historias de misterio', 'Recetas rápidas', 'Finanzas fáciles', 'Curiosidades', 'Tecnología']
def sc1(lt, d_, f):
    im, d = window(room(0), 1); cx = CX0
    d.text((cx + 10, WY + 90), 'Elige tu nicho', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
    tsel, tv, tc = wt(1, 'funcionando'), wt(1, 'visitas'), wt(1, 'competencia')
    for k, s in enumerate(NICHOS):
        y = WY + 150 + k * 58; sel = k == 0 and lt > tsel
        d.rounded_rectangle((cx + 10, y - 22, cx + 440, y + 22), 10, fill=(255, 236, 236) if sel else (255, 255, 255), outline=RED if sel else (220, 222, 232), width=3 if sel else 1)
        d.ellipse((cx + 24, y - 9, cx + 42, y + 9), outline=RED if sel else (180, 182, 196), width=3)
        if sel: d.ellipse((cx + 29, y - 4, cx + 37, y + 4), fill=RED)
        d.text((cx + 56, y), s, font=F('Inter-SemiBold.otf', 21), fill=(40, 40, 50), anchor='lm')
    if lt > tv:
        a = ease((lt - tv) / .2); y = WY + 150 + 30
        d.rounded_rectangle((cx + 10, y + 4, cx + 200, y + 38), 17, fill=GREEN + (int(255 * a),))
        n = int(184000 * ease((lt - tv) / .8))
        d.text((cx + 105, y + 21), f'{n:,} visitas'.replace(',', '.'), font=F('Inter-Bold.otf', 18), fill='white', anchor='mm')
    if lt > tc:
        a = ease((lt - tc) / .2); y = WY + 150 + 30
        d.rounded_rectangle((cx + 212, y + 4, cx + 440, y + 38), 17, fill=(40, 40, 50))
        d.text((cx + 326, y + 21), 'Competencia baja', font=F('Inter-Bold.otf', 18), fill='white', anchor='mm')
    tt = d_ - .35
    btn(d, 'Siguiente  ›', (lt - tt) / .2 if 0 < lt - tt < .2 else 0)
    ty = WY + 150
    if lt < tsel + .3: px, py, ck = lerp(W / 2 + 100, cx + 240, ease((lt - (tsel - .6)) / .5)), lerp(WY + 520, ty + 6, ease((lt - (tsel - .6)) / .5)), (lt - tsel) / .3 if lt > tsel else 0
    else:
        bx, by = (BTN[0] + BTN[2]) / 2, (BTN[1] + BTN[3]) / 2 + 6; q = ease((lt - (tt - .5)) / .35)
        px, py, ck = lerp(cx + 240, bx, q), lerp(ty + 6, by, q), (lt - tt) / .35 if 0 < lt - tt < .35 else 0
    cursor(d, px, py, ck)
    return im

def sc2(lt, d_, f):
    im, d = window(room(0), 2); cx = CX0
    d.text((cx + 10, WY + 90), 'Estructura del viral', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
    tc, tno, th = wt(2, 'estructura'), wt(2, 'contenido'), wt(2, 'historias')
    swap = ease((lt - (th - .5)) / .4)
    card = thumb_card(130, 230, (120, 40, 140) if swap < .5 else (180, 30, 40), '2,4 M' if swap < .5 else 'Tu historia')
    sx = abs(1 - 2 * swap)
    if sx > .02: c2 = card.resize((max(1, int(130 * sx)), 230)); im.alpha_composite(c2, (int(cx + 10 + 65 * (1 - sx)), WY + 120))
    d = ImageDraw.Draw(im)
    for k, (a, b) in enumerate([('1 · Gancho', 'Una promesa en 2 s'), ('2 · Giro', 'Algo que no esperas'), ('3 · Final', 'Vuelve al inicio')]):
        y = WY + 140 + k * 75; al = ease((lt - tc - k * .25) / .25)
        if al <= 0: continue
        d.text((cx + 165 + (1 - al) * 30, y), a, font=F('Inter-Black.otf', 24), fill=RED, anchor='lm')
        d.text((cx + 165 + (1 - al) * 30, y + 28), b, font=F('Inter-Medium.otf', 18), fill=(110, 110, 125), anchor='lm')
    if lt > tno - .3:
        a = ease((lt - tno + .3) / .2); y = WY + 400
        d.rounded_rectangle((cx + 10, y, cx + 190, y + 44), 22, fill=(240, 240, 244), outline=(200, 200, 210))
        d.text((cx + 100, y + 22), 'su contenido', font=F('Inter-SemiBold.otf', 20), fill=(150, 150, 160), anchor='mm')
        if lt > tno: d.line((cx + 20, y + 22, cx + 20 + 160 * ease((lt - tno) / .25), y + 22), fill=RED, width=5)
        d.rounded_rectangle((cx + 210, y, cx + 440, y + 44), 22, fill=GREEN)
        d.text((cx + 325, y + 22), 'su estructura', font=F('Inter-Bold.otf', 20), fill='white', anchor='mm')
    btn(d, 'Siguiente  ›', 0)
    mascot_corner(im, f)
    return im

def sc3(lt, d_, f):
    im, d = window(room(0), 3); cx = CX0
    d.text((cx + 10, WY + 90), 'Producción', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
    ts = [wt(3, 'guion'), wt(3, 'voz'), wt(3, 'imágenes'), wt(3, 'video')]
    for k, s in enumerate(['Guion', 'Voz', 'Imágenes', 'Video']):
        y = WY + 160 + k * 82; pr = ease((lt - ts[k] + .25) / .5)
        d.text((cx + 10, y), s, font=F('Inter-Bold.otf', 22), fill=(40, 40, 50), anchor='lm')
        bx0 = cx + 130
        if k == 0:
            for j in range(3): d.rounded_rectangle((bx0, y - 18 + j * 14, bx0 + (240 - j * 60) * pr, y - 10 + j * 14), 4, fill=(170, 172, 190))
        elif k == 1:
            for j in range(30):
                if j / 30 > pr: break
                hh = 4 + 16 * abs(math.sin(j * .9 + lt * 6)); d.rounded_rectangle((bx0 + j * 9, y - hh, bx0 + j * 9 + 5, y + hh), 2, fill=RED)
        elif k == 2:
            for j in range(3):
                if j / 3 < pr: im.alpha_composite(thumb_card(60, 60, [(40, 80, 160), (150, 40, 60), (40, 130, 100)][j], ''), (bx0 + j * 70, y - 30))
            d = ImageDraw.Draw(im)
        else:
            if pr > 0: im.alpha_composite(thumb_card(46, 80, (110, 40, 140), ''), (bx0, y - 40)); d = ImageDraw.Draw(im)
            d.rounded_rectangle((bx0 + 60, y - 6, bx0 + 60 + 190 * pr, y + 6), 6, fill=RED)
        if pr >= 1:
            d.ellipse((cx + 412, y - 14, cx + 440, y + 14), fill=GREEN); d.line((cx + 419, y, cx + 424, y + 6, cx + 433, y - 6), fill='white', width=4)
    btn(d, 'Siguiente  ›', 0)
    mascot_corner(im, f)
    return im

def sc4(lt, d_, f):
    im, d = window(room(0), 4); cx = CX0
    d.text((cx + 10, WY + 90), 'Publicar', font=F('Inter-Black.otf', 30), fill=(25, 25, 32), anchor='lm')
    tp = wt(4, 'publicas'); pr = ease((lt - tp) / .5)
    im.alpha_composite(thumb_card(130, 230, (180, 30, 40), ''), (cx + 10, WY + 130)); d = ImageDraw.Draw(im)
    d.text((cx + 165, WY + 150), 'Mi primer video', font=F('Inter-Bold.otf', 22), fill=(40, 40, 50), anchor='lm')
    d.rounded_rectangle((cx + 165, WY + 190, cx + 440, WY + 210), 10, fill=(222, 224, 234))
    d.rounded_rectangle((cx + 165, WY + 190, cx + 165 + 275 * pr, WY + 210), 10, fill=RED)
    if pr >= 1:
        d.text((cx + 165, WY + 250), '¡Publicado!', font=F('Inter-Black.otf', 28), fill=GREEN, anchor='lm')
        n = int(3402 * ease((lt - tp - .5) / 1.0))
        d.text((cx + 165, WY + 292), f'{n:,} visitas'.replace(',', '.'), font=F('Inter-Bold.otf', 20), fill=(110, 110, 125), anchor='lm')
        rr = random.Random(9); q = lt - tp - .5
        for k in range(40):
            x = W / 2 + rr.uniform(-300, 300) * min(1, q * 2); y = 380 + rr.uniform(0, 500) * q + 300 * q * q
            col = [RED, GOLD, GREEN, (255, 255, 255)][k % 4]; d.rectangle((x, y, x + 10, y + 6), fill=col)
    btn(d, 'Finalizar', (lt - tp) / .2 if 0 < lt - tp < .2 else 0)
    bx, by = (BTN[0] + BTN[2]) / 2, (BTN[1] + BTN[3]) / 2 + 6; q = ease((lt - (tp - .45)) / .35)
    cursor(d, lerp(bx - 200, bx, q), lerp(by - 160, by, q), (lt - tp) / .35 if 0 < lt - tp < .35 else 0)
    return im

def sc5(lt, d_, f):
    tm, ts = wt(5, 'mañana'), wt(5, 'siguiente')
    if lt < ts - .45:  # amanece en el cuarto
        dawn = ease((lt - .1) / max(.3, tm + .4)); im = room(dawn)
        m = MA_BIG if talking(f) else MC_BIG
        im.alpha_composite(m, ((W - m.width) // 2, 1300 - int(m.height * .78)))
        return im
    im = Image.new('RGBA', (W, H), (8, 10, 22, 255)); im = screen_glow(im, W / 2, 760, 520, 200, 1.0); d = ImageDraw.Draw(im)
    lp = lt - ts; press = 1 - .08 * math.sin(math.pi * min(1, lp / .25)) if 0 < lp < .25 else 1
    bw, bh = 250 * press, 80 * press
    d.rounded_rectangle((W / 2 - bw, 760 - bh, W / 2 + bw, 760 + bh), 40, fill=RED)
    d.text((W / 2, 760), 'Siguiente  ›', font=F('Inter-Black.otf', 64), fill='white', anchor='mm')
    q = ease((lt - (ts - .45)) / .4)
    cursor(d, lerp(W / 2 + 260, W / 2 + 40, q), lerp(1150, 780, q), lp / .4 if 0 < lp < .4 else 0)
    if lp > .2:
        a = ease((lp - .2) / .3); d.text((W / 2, 930 + 20 * (1 - a)), 'Siguiente video en marcha', font=F('Inter-Bold.otf', 30), fill=(200, 205, 225, int(255 * a)), anchor='mm')
        d.rounded_rectangle((W / 2 - 200, 990, W / 2 + 200, 1008), 9, fill=(40, 44, 66))
        d.rounded_rectangle((W / 2 - 200, 990, W / 2 - 200 + 400 * ease((lp - .2) / 1.2), 1008), 9, fill=RED)
    return im

def sc6(lt, d_, f):
    im = room(.15); d = ImageDraw.Draw(im)
    tb, tr = wt(6, 'bio'), wt(6, 'regístrate')
    m = MA_BIG if talking(f) else MC_BIG
    im.alpha_composite(m, ((W - m.width) // 2, 1300 - int(m.height * .85)))
    a = ease((lt - (tb - .3)) / .3)
    if a > 0:
        L = Image.new('RGBA', (W, H), (0, 0, 0, 0)); dl = ImageDraw.Draw(L); al = int(255 * a); yo = (1 - a) * 60
        x0, y0 = 70, 920 + yo
        dl.rounded_rectangle((x0, y0, W - 70, y0 + 230), 24, fill=(255, 255, 255, al))
        dl.ellipse((x0 + 24, y0 + 24, x0 + 104, y0 + 104), fill=RED + (al,))
        dl.text((x0 + 64, y0 + 64), 'S', font=F('Inter-Black.otf', 44), fill=(255, 255, 255, al), anchor='mm')
        dl.text((x0 + 124, y0 + 48), '@sumiago', font=F('Inter-Black.otf', 30), fill=(25, 25, 32, al), anchor='lm')
        dl.text((x0 + 124, y0 + 84), 'Aprende a crear videos que funcionan', font=F('Inter-Medium.otf', 20), fill=(110, 110, 125, al), anchor='lm')
        pul = .5 + .5 * math.sin(lt * 9) if lt > tr - .2 else 0
        dl.rounded_rectangle((x0 + 24, y0 + 136, W - 94, y0 + 200), 16, fill=mix((240, 240, 246), RED, pul) + (al,))
        dl.text((x0 + 50, y0 + 168), 'sumiago.com  ·  Regístrate aquí', font=F('Inter-Bold.otf', 26), fill=mix((30, 30, 40), (255, 255, 255), pul) + (al,), anchor='lm')
        im.alpha_composite(L); d = ImageDraw.Draw(im)
        if lt > tr - .6:
            q = ease((lt - (tr - .6)) / .5); cursor(d, lerp(W - 60, W - 200, q), lerp(1250, y0 + 175, q), (lt - tr) / .4 if 0 < lt - tr < .4 else 0)
    return im

B.SC = [sc0, sc1, sc2, sc3, sc4, sc5, sc6]

def clicks():  # momentos del sonido de clic
    out = []
    for ci, w, n in [(0, 'siguiente', 0), (0, 'siguiente', 1), (0, 'finalizar', 0), (1, 'funcionando', 0), (4, 'publicas', 0), (5, 'siguiente', 0), (6, 'regístrate', 0)]:
        out.append(CL[ci]['t0'] - 0.15 + wt(ci, w, n))
    out.append(CL[1]['t0'] - 0.15 + (CL[2]['t0'] - CL[1]['t0']) - .35)
    return out

if __name__ == '__main__':
    B.main(clicks)
