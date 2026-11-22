"""Arma el video del Día 3 "Portadas Sumiago" (9:16, 1080x1920, 30 fps, unos 60 s) con fondo blanco, la mascota que habla, música y efectos.
Uso (en la carpeta donde están voice.wav, durs.json, mascot_clean.png y mix.wav):
    python scripts/render.py test 0.6 3.5 6 10.5 14 18.5    -> test.jpg con cuadros de muestra
    python scripts/render.py full                            -> dia-03.mp4 (usa mix.wav: voz + música + efectos)
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import base as render2
from base import (W, H, FPS, font, txt_c, glow, ease, stand, scene, durs, YEL, RED, WHITE)

def sky(c0, c1):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c0) * (1 - y) + np.array(c1) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1)).convert('RGBA')

TAIL = 1.6
TOTAL = sum(durs) + TAIL
starts = render2.starts
DARK = (25, 25, 30); GREEN = (37, 211, 102); GRAY = (235, 235, 240)
BG = sky((255, 255, 255), (240, 240, 245))

def _fuente_emoji():
    aqui = os.path.dirname(os.path.abspath(__file__))
    for f in ('/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf', os.path.join(aqui, '..', 'NotoColorEmoji.ttf'),
              r'C:\Windows\Fonts\seguiemj.ttf', '/System/Library/Fonts/Apple Color Emoji.ttc'):
        if os.path.isfile(f):
            try: return ImageFont.truetype(f, 109)
            except OSError: pass
    sys.exit('No encontré una fuente de emojis. Copia NotoColorEmoji.ttf (Google Fonts) a la carpeta de la skill.')
_ef = _fuente_emoji()
_ec = {}
def emoji(ch, size):
    k = (ch, size)
    if k not in _ec:
        im = Image.new('RGBA', (136, 128), (0, 0, 0, 0)); ImageDraw.Draw(im).text((0, 0), ch, font=_ef, embedded_color=True)
        im = im.crop(im.getbbox() or (0, 0, 136, 128)); r = size / max(im.size)
        _ec[k] = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    return _ec[k]
def put(img, im, cx, cy, s=1.0):
    if s != 1.0: im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.LANCZOS)
    img.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))
def pop(t0, t, dur=0.35):
    """scale with overshoot for pop-in"""
    u = (t - t0) / dur
    if u <= 0: return 0.0
    if u >= 1: return 1.0
    return 1 + 0.25 * math.sin(u * math.pi) * (1 - u) * 2 if u > 0.5 else ease(u * 2) * 1.15

def caption(img, t):
    d = ImageDraw.Draw(img)
    for ch in render2.chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is render2.chunks[-1] and t >= ch[0][0]):
            line = ' '.join(w[2] for w in ch); ff = font(66); tw = d.textlength(line, font=ff)
            if tw > W - 100: ff = font(int(66 * (W - 100) / tw)); tw = d.textlength(line, font=ff)
            x = (W - tw) / 2
            for (a, b, w, _) in ch:
                act = a <= t < b + 0.02
                d.text((x, 200 - (6 if act else 0)), w, font=ff, fill=RED if act else DARK, stroke_width=6, stroke_fill=WHITE)
                x += d.textlength(w + ' ', font=ff)
            return

AV = stand(0, 1.0, 0.2).crop((70, 0, 170, 100)).resize((150, 150), Image.LANCZOS)
def avatar(img, cx, cy, r=75):
    m = Image.new('L', (2 * r, 2 * r), 0); ImageDraw.Draw(m).ellipse([0, 0, 2 * r, 2 * r], fill=255)
    bgc = Image.new('RGBA', (2 * r, 2 * r), (255, 230, 230, 255)); bgc.alpha_composite(AV.resize((2 * r, 2 * r)))
    img.paste(bgc, (int(cx - r), int(cy - r)), m)
    ImageDraw.Draw(img).ellipse([cx - r, cy - r, cx + r, cy + r], outline=RED, width=6)

BTN = [('📸', 'Instagram', (225, 48, 108)), ('🎵', 'TikTok', (20, 20, 25)), ('💬', 'WhatsApp', GREEN), ('🛒', 'Mi catálogo', (255, 140, 0)), ('💰', 'Pagar en USDT', (38, 161, 123))]
def portada(img, x, y, w, h, t, t0=-9, theme=(225, 30, 40), name='@tunombre', nb=5, scale=1.0):
    d = ImageDraw.Draw(img)
    sh = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle([x + 10, y + 20, x + w + 10, y + h + 20], 60, fill=(0, 0, 0, 70))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18))); d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + w, y + h], 60, fill=(20, 20, 26))
    sx0, sy0, sx1, sy1 = x + 16, y + 16, x + w - 16, y + h - 16
    scr = Image.new('RGBA', (sx1 - sx0, sy1 - sy0), (255, 255, 255, 255)); sd = ImageDraw.Draw(scr)
    sd.rectangle([0, 0, scr.width, int(scr.height * 0.27)], fill=theme)
    img2 = scr
    cw = scr.width
    avatar(img2, cw / 2, int(scr.height * 0.27), int(cw * 0.14)); sd = ImageDraw.Draw(img2)
    txt_c(sd, (cw / 2, int(scr.height * 0.27) + cw * 0.16), name, font(int(cw * 0.085)), DARK)
    txt_c(sd, (cw / 2, int(scr.height * 0.27) + cw * 0.27), 'Tu negocio en un link', font(int(cw * 0.05)), (110, 110, 120))
    by = int(scr.height * 0.27 + cw * 0.40); bh = int(cw * 0.15)
    for k, (em, lab, col) in enumerate(BTN[:nb]):
        s = pop(t0 + k * 0.25, t)
        if s <= 0: continue
        bw = (cw - 60) * s; bx = (cw - bw) / 2; yy = by + k * (bh + 18)
        sd.rounded_rectangle([bx, yy, bx + bw, yy + bh], bh // 2, fill=col)
        if s > 0.6:
            put(img2, emoji(em, int(bh * 0.6)), bx + bh * 0.6, yy + bh / 2)
            sd.text((bx + bh * 1.15, yy + bh * 0.18), lab, font=font(int(bh * 0.42)), fill=WHITE)
    m = Image.new('L', scr.size, 0); ImageDraw.Draw(m).rounded_rectangle([0, 0, scr.width, scr.height], 46, fill=255)
    img.paste(img2, (sx0, sy0), m)

def pill(d, cx, y, s, col, tc=WHITE, size=52):
    w = d.textlength(s, font=font(size)); d.rounded_rectangle([cx - w / 2 - 34, y, cx + w / 2 + 34, y + size + 40], 40, fill=col); txt_c(d, (cx, y + 12), s, font(size), tc)
def stamp(img, t0, t, text, col=RED, y=900, size=170, rot=-8):
    s = pop(t0, t, 0.3)
    if s <= 0.01: return
    lay = Image.new('RGBA', (W, 600), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
    tw = ld.textlength(text, font=font(size))
    ld.rounded_rectangle([W / 2 - tw / 2 - 50, 300 - size * 0.75, W / 2 + tw / 2 + 50, 300 + size * 0.75], 40, outline=col, width=16, fill=(255, 255, 255, 235))
    txt_c(ld, (W / 2, 300 - size * 0.62), text, font(size), col)
    lay = lay.rotate(rot, resample=Image.BICUBIC)
    lay = lay.resize((int(W * s), int(600 * s)), Image.LANCZOS)
    img.alpha_composite(lay, (int(W / 2 - lay.width / 2), int(y - lay.height / 2)))
def confetti(img, t0, t, n=60, seed=1):
    u = t - t0
    if u < 0 or u > 2.2: return
    d = ImageDraw.Draw(img); rnd = random.Random(seed)
    cols = [RED, YEL, GREEN, (60, 140, 255), (255, 120, 200)]
    for k in range(n):
        a = rnd.uniform(0, 2 * math.pi); v = rnd.uniform(600, 1400)
        x = W / 2 + math.cos(a) * v * u; y = 900 + math.sin(a) * v * u + 900 * u * u
        s = rnd.uniform(10, 22); d.rectangle([x - s / 2, y - s / 4, x + s / 2, y + s / 4], fill=cols[k % 5])
def shake(t, t0, amp=18, dur=0.4):
    u = t - t0
    return (amp * math.sin(u * 60) * (1 - u / dur), amp * math.cos(u * 55) * (1 - u / dur)) if 0 <= u < dur else (0, 0)

def qr(d, x, y, s):
    rnd = random.Random(5); n = 21; c = s / n
    d.rectangle([x, y, x + s, y + s], fill=WHITE)
    for i in range(n):
        for j in range(n):
            fin = (i < 7 and j < 7) or (i < 7 and j > 13) or (i > 13 and j < 7)
            on = (fin and (i in (0, 6) or j in (0, 6) or (i % 7 in (0, 6)) or (j % 7 in (0, 6)) or (2 <= i % 14 <= 4 and 2 <= j % 14 <= 4))) if fin else rnd.random() > 0.5
            if fin:
                ii, jj = i % 14 if i > 13 else i, j % 14 if j > 13 else j
                ii = i - 14 if i > 13 else i; jj = j - 14 if j > 13 else j
                on = ii in (0, 6) or jj in (0, 6) or (2 <= ii <= 4 and 2 <= jj <= 4)
            if on: d.rectangle([x + j * c, y + i * c, x + (j + 1) * c, y + (i + 1) * c], fill=DARK)

TEMPL = [('Restaurante', (230, 90, 30), '@sabor.casero'), ('Barbería', (30, 30, 35), '@barber.king'), ('Tienda', (140, 60, 220), '@moda.luna'), ('Coach', (20, 140, 120), '@coach.ana')]

def frame(f):
    t = f / FPS
    i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - starts[-1]
    dur = durs[i]; p = min(1, lt / dur)
    img = BG.copy(); d = ImageDraw.Draw(img)
    if i == 0:
        # hook: old bio with single link, red flash, PARA stamp
        sx, sy = shake(t, 0.05)
        prof = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(prof)
        pd.rounded_rectangle([160, 420, 920, 1300], 50, fill=WHITE, outline=(220, 220, 225), width=4)
        avatar(prof, 300, 560, 90); pd = ImageDraw.Draw(prof)
        pd.text((420, 500), 'tu_negocio', font=font(56), fill=DARK); pd.text((420, 570), 'Bio aburrida...', font=font(40), fill=(130, 130, 140))
        pd.rounded_rectangle([220, 720, 860, 820], 24, fill=GRAY); pd.text((320, 742), 'un-solo-link.com/xyz', font=font(40), fill=(60, 90, 200)); put(prof, emoji('🔗', 56), 275, 770)
        for k in range(3): pd.rounded_rectangle([220 + k * 215, 880, 420 + k * 215, 1080], 20, fill=(225, 225, 230))
        img.alpha_composite(prof, (int(sx), int(sy)))
        if lt < 0.25: img.alpha_composite(Image.new('RGBA', (W, H), (255, 0, 0, int(160 * (1 - lt / 0.25)))))
        stamp(img, 0.05, t, '¡PARA!', RED, 1450, 190)
        if lt > 2.6:
            d = ImageDraw.Draw(img); s = pop(2.6, t)
            put(img, emoji('📉', int(150 * s) + 1), 820, 760)
            pill(d, W / 2, 1180, 'pierdes clientes', DARK, WHITE, 56)
    elif i == 1:
        k = ease(lt / 0.6); y = int(1900 - 1400 * k)
        portada(img, 290, y, 500, 1000, t, starts[1] + 0.5)
        glow(img, W // 2, 1000, 420, (225, 30, 40), int(60 * k), 60)
        portada(img, 290, y, 500, 1000, t, starts[1] + 0.5)
        if lt > 2.2: stamp(img, starts[1] + 2.2, t, '1 SOLO LINK', RED, 1660, 110, -4)
    elif i == 2:
        portada(img, 290, 450, 500, 1000, t, starts[2] - 5)
        icons = ['📸', '🎵', '💬', '🛒', '💰']
        for k, em in enumerate(icons):
            t0 = 0.3 + k * 0.6; u = ease((lt - t0) / 0.5)
            if lt < t0: continue
            a = math.radians(200 + k * 35); sx, sy = W / 2 + math.cos(a) * 520, 950 + math.sin(a) * 700
            x = sx + (540 - sx) * u; y = sy + (950 - sy) * u
            if u < 1: put(img, emoji(em, 130), x, y, 1.0 - 0.4 * u)
        if lt > 3.0:
            d = ImageDraw.Draw(img); url = 'sumiago.com/@tunombre'; n = min(len(url), int((lt - 3.0) * 14))
            d.rounded_rectangle([110, 1520, 970, 1640], 60, fill=DARK); d.text((160, 1545), url[:n] + ('|' if int(t * 4) % 2 else ''), font=font(56), fill=WHITE)
    elif i == 3:
        stamp(img, starts[3] + 0.4, t, 'GRATIS', GREEN, 640, 200, -6)
        confetti(img, starts[3] + 0.4, t)
        d = ImageDraw.Draw(img)
        items = [('💳', 'Sin tarjeta', 1.3), ('⏱️', 'Lista en 2 minutos', 2.2), ('📱', 'Desde tu celular', 3.2)]
        for k, (em, s, t0) in enumerate(items):
            sc = pop(starts[3] + t0, t)
            if sc <= 0: continue
            y = 1010 + k * 190
            d.rounded_rectangle([170, y, 910, y + 150], 40, fill=WHITE, outline=(225, 225, 230), width=4)
            put(img, emoji(em, int(90 * sc) + 1), 260, y + 75); d.text((330, y + 44), s, font=font(52), fill=DARK)
            d.ellipse([820, y + 40, 890, y + 110], fill=GREEN); d.line([(838, y + 76), (852, y + 92), (875, y + 58)], fill=WHITE, width=9)
    elif i == 4:
        txt_c(d, (W / 2, 380), 'PASO 1', font(96), RED)
        d.rounded_rectangle([110, 760, 970, 900], 70, fill=WHITE, outline=DARK, width=6)
        url = 'sumiago.com/@'; nm = 'tunombre'; n = min(len(nm), int(max(0, lt - 0.3) * 10))
        d.text((160, 795), url, font=font(56), fill=(130, 130, 140)); d.text((160 + d.textlength(url, font=font(56)), 795), nm[:n] + ('|' if int(t * 4) % 2 else ''), font=font(56), fill=DARK)
        if lt > 1.3:
            s = pop(starts[4] + 1.3, t); pill(d, W / 2, 960, '✓ ¡Disponible!', GREEN, WHITE, int(60 * min(1, s)) + 1)
        m = stand(f, t, 0.4); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10))
    elif i == 5:
        txt_c(d, (W / 2, 330), 'PASO 2', font(96), RED)
        k = min(3, int(max(0, lt - 2.2) / 1.0))
        u = ease((max(0, lt - 2.2) % 1.0) / 0.35) if lt > 2.2 else 1
        for j, (lab, col, nm) in enumerate(TEMPL):
            off = (j - k) * 560 - (1 - u) * 560 * (1 if lt > 2.2 and j >= 0 else 0) * 0
            x = W / 2 - 230 + (j - k) * 560 + (1 - u) * 560
            if -600 < x < W + 100:
                portada(img, int(x), 560, 460, 920, t, starts[5] - 9, col, nm, 4)
        d = ImageDraw.Draw(img)
        lab = TEMPL[k][0] if lt > 2.2 else 'Tu logo · tu bio · tus enlaces'
        pill(d, W / 2, 1560, lab, DARK, YEL, 56)
    elif i == 6:
        txt_c(d, (W / 2, 330), 'PASO 3', font(96), RED)
        portada(img, 90, 560, 420, 840, t, -9, nb=4)
        for k, (em, lab) in enumerate((('📸', 'Instagram'), ('🎵', 'TikTok'), ('💬', 'Estados'))):
            sc = pop(starts[6] + 0.6 + k * 0.7, t)
            if sc <= 0: continue
            y = 620 + k * 210; d.rounded_rectangle([580, y, 1000, y + 170], 40, fill=WHITE, outline=(225, 225, 230), width=4)
            put(img, emoji(em, int(100 * sc) + 1), 660, y + 85); d.text((730, y + 55), lab, font=font(50), fill=DARK)
        if lt > 3.4:
            s = pop(starts[6] + 3.4, t); qs = int(300 * min(1, s)); qr(d, 640, 1300, max(21, qs))
            put(img, emoji('🖨️', 90), 980, 1420)
    elif i == 7:
        # catalog -> whatsapp
        portada(img, 60, 480, 440, 880, t, -9, nb=4)
        d = ImageDraw.Draw(img)
        if lt > 0.6:
            put(img, emoji('👆', 110), 300 + 20 * math.sin(t * 6), 1180)
        if lt > 1.4:
            u = ease((lt - 1.4) / 0.8)
            put(img, emoji('🛒', 120), 500 + 260 * u, 900 - 150 * u)
        if lt > 2.3:
            s = pop(starts[7] + 2.3, t)
            bx0, by0 = 560, 560
            d.rounded_rectangle([bx0, by0, 1030, 1420], 40, fill=(236, 229, 221))
            d.rectangle([bx0, by0, 1030, by0 + 110], fill=(7, 94, 84)); d.text((bx0 + 30, by0 + 28), 'WhatsApp', font=font(46), fill=WHITE)
            if s > 0.2:
                d.rounded_rectangle([bx0 + 30, by0 + 160, 1000, by0 + 520], 26, fill=(220, 248, 198))
                for k, line in enumerate(['🧾 NUEVO PEDIDO', '2x Hamburguesa', '1x Papas grandes', 'Total: $14']):
                    d.text((bx0 + 60, by0 + 190 + k * 75), line.replace('🧾 ', ''), font=font(44 if k else 46), fill=DARK if k < 3 else (7, 94, 84))
            if lt > 3.4: pill(d, 795, 1460, 'directo a tu chat', GREEN, WHITE, 44)
    elif i == 8:
        stamp(img, starts[8] + 0.2, t, 'PRO', (200, 150, 0), 520, 150, 0)
        feats = [('💰', 'Pagos USDT'), ('📅', 'Agenda'), ('🍽️', 'Menú QR'), ('⭐', 'Reseñas'), ('📊', 'Estadísticas')]
        for k, (em, lab) in enumerate(feats):
            sc = pop(starts[8] + 1.2 + k * 1.0, t)
            if sc <= 0: continue
            c, r = k % 2, k // 2
            x = 110 + c * 450 if k < 4 else W / 2 - 210; y = 760 + r * 300
            w0, h0 = 420 * sc, 260 * sc
            d.rounded_rectangle([x + 210 - w0 / 2, y + 130 - h0 / 2, x + 210 + w0 / 2, y + 130 + h0 / 2], 40, fill=WHITE, outline=RED, width=5)
            if sc > 0.6:
                put(img, emoji(em, 100), x + 210, y + 90); txt_c(d, (x + 210, y + 160), lab, font(46), DARK)
        if lt > 6.0:
            for k in range(6):
                hh = 40 + k * 30 * ease((lt - 6.0) / 0.8); d.rectangle([700 + k * 40, 1660 - hh, 730 + k * 40, 1660], fill=RED)
    elif i == 9:
        avatar(img, W / 2, 1000, 120)
        for k in range(5):
            a = math.radians(-90 + k * 72); fx, fy = W / 2 + math.cos(a) * 400, 1000 + math.sin(a) * 400
            sc = pop(starts[9] + 0.3 + k * 0.3, t)
            if sc <= 0: continue
            put(img, emoji('🙋', int(120 * sc) + 1), fx, fy)
            if lt > 2.0:
                u = ((lt - 2.0) * 0.9 + k * 0.2) % 1
                put(img, emoji('🪙', 70), fx + (W / 2 - fx) * u, fy + (1000 - fy) * u)
        if lt > 2.0: pill(d, W / 2, 1560, '+ comisión', GREEN, WHITE, 70)
    elif i == 10:
        d.line([(W / 2, 400), (W / 2, 1700)], fill=(210, 210, 215), width=4)
        txt_c(d, (W / 4, 420), 'OTROS', font(60), (130, 130, 140)); txt_c(d, (3 * W / 4, 420), 'TÚ', font(60), RED)
        rnd = random.Random(3)
        for k in range(10):
            x = 40 + rnd.randint(0, 380); y = 560 + k * 105 + 6 * math.sin(t * 5 + k)
            d.rounded_rectangle([x, y, x + 210, y + 70], 20, fill=(225, 225, 230)); d.text((x + 16, y + 14), f'link{k + 1}…', font=font(34), fill=(120, 120, 130))
        if lt > 1.6: d.line([(60, 560), (480, 1600)], fill=RED, width=14); d.line([(480, 560), (60, 1600)], fill=RED, width=14)
        portada(img, 600, 600, 420, 840, t, -9, nb=5)
        if lt > 2.6: stamp(img, starts[10] + 2.6, t, 'VENDE POR TI', GREEN, 1620, 80, -3)
    else:
        s = 1 + 0.06 * math.sin(t * 9)
        glow(img, W // 2, 700, int(360 * s), (225, 30, 40), 90, 50); d = ImageDraw.Draw(img)
        bw = 440 * s
        d.rounded_rectangle([W / 2 - bw, 560, W / 2 + bw, 820], 70, fill=RED)
        txt_c(d, (W / 2, 585), 'RECLAMA', font(int(72 * s)), WHITE); txt_c(d, (W / 2, 670), 'TU NOMBRE', font(int(90 * s)), YEL)
        d.rounded_rectangle([170, 880, 910, 980], 50, fill=DARK); txt_c(d, (W / 2, 895), 'sumiago.com/portadas', font(54), WHITE)
        if lt > 2.6: pill(d, W / 2, 1030, '👇 link en mi perfil'.replace('👇 ', ''), YEL, DARK, 56); put(img, emoji('👇', 110), W / 2 + 330, 1075)
        m = stand(f, t, 0.48); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10))
        confetti(img, starts[11] + 3.0, t, 70, 9)
    # punch zoom on scene start
    if lt < 0.18 and i > 0:
        z = 1 + 0.06 * (1 - lt / 0.18)
        img = img.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
    caption(img, t)
    # progress bar (retención)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 14, W * min(1, t / TOTAL), H], fill=RED)
    return img.convert('RGB')

# --- efectos de sonido (tiempo, tipo, parámetro) que usa audio.py ---
def events():
    S = starts; ev = []
    for i in range(1, len(durs)): ev.append((S[i] - 0.12, 'whoosh', 0))
    ev += [(0.05, 'boom', 0), (0.05, 'stamp', 0), (2.6, 'pop', 500)]
    ev += [(S[1] + 0.5 + k * 0.25, 'pop', 900 + k * 120) for k in range(5)] + [(S[1] + 2.2, 'stamp', 0)]
    ev += [(S[2] + 0.3 + k * 0.6 + 0.45, 'pop', 1200) for k in range(5)] + [(S[2] + 3.0 + k / 14, 'key', 0) for k in range(21)]
    ev += [(S[3] + 0.4, 'stamp', 0), (S[3] + 0.4, 'cheer', 0)] + [(S[3] + x, 'ding', 1046 + k * 200) for k, x in enumerate((1.3, 2.2, 3.2))]
    ev += [(S[4] + 0.3 + k / 10, 'key', 0) for k in range(8)] + [(S[4] + 1.3, 'ding', 1568)]
    ev += [(S[5] + 2.2 + k * 1.0, 'swipe', 0) for k in range(4)]
    ev += [(S[6] + 0.6 + k * 0.7, 'pop', 900 + k * 150) for k in range(3)] + [(S[6] + 3.4, 'pop', 700)]
    ev += [(S[7] + 0.6, 'tap', 0), (S[7] + 1.4, 'pop', 800), (S[7] + 2.3, 'msg', 0)]
    ev += [(S[8] + 0.2, 'stamp', 0)] + [(S[8] + 1.2 + k, 'pop', 900 + k * 100) for k in range(5)] + [(S[8] + 6.0, 'riser', 0)]
    ev += [(S[9] + 0.3 + k * 0.3, 'pop', 1000 + k * 100) for k in range(5)] + [(S[9] + 2.0 + k * 0.45, 'coin', 0) for k in range(5)]
    ev += [(S[10] + 1.6, 'buzz', 0), (S[10] + 2.6, 'stamp', 0), (S[10] + 2.6, 'ding', 1318)]
    ev += [(S[11] + 0.1, 'riser', 0), (S[11] + 2.6, 'pop', 900), (S[11] + 3.0, 'cheer', 0), (S[11] + 3.0, 'ding', 2093)]
    return ev

if __name__ == '__main__':
    if sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]
        ims = [frame(int(x * FPS)).resize((300, 533)) for x in ts]
        c = Image.new('RGB', (300 * len(ims), 533))
        for k, im in enumerate(ims): c.paste(im, (k * 300, 0))
        c.save('test.jpg')
    else:
        n = int(TOTAL * FPS)
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                              '-shortest', '-movflags', '+faststart', 'dia-03.mp4'], stdin=subprocess.PIPE)
        for f in range(n): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait()
        print('Listo: dia-03.mp4')
