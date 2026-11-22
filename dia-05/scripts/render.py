"""Arma el video del Día 5 "Las 4 herramientas de Sumiago" (9:16, 1080x1920, 30 fps, unos 50 s): explosivo, con música rápida, golpes y efectos.
Uso (en la carpeta donde están voice.wav, durs.json, mascot_clean.png y mix.wav):
    python scripts/render.py test 0.8 3.6 7 12 20 28.5   -> test.jpg con cuadros de muestra
    python scripts/render.py full                         -> dia-05.mp4 (usa mix.wav: voz + música + efectos)
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import base as render2
from base import W, H, FPS, font, txt_c, glow, ease, stand, scene, durs, YEL, RED, WHITE
from portada_base import emoji, put, pop, stamp, confetti, pill, sky, portada, caption, shake

DARK = (25, 25, 30); GREEN = (37, 211, 102); TEAL = (20, 170, 175); PURP = (124, 58, 237); ORNG = (255, 140, 0)
TOOLS = [('🔗', 'PORTADA', RED), ('🛒', 'MARKETPLACE', ORNG), ('🎬', 'VIDEOS VIRALES', PURP), ('🎓', 'GANA CON MARKETING', TEAL)]
starts = render2.starts
TAIL = 1.4
TOTAL = sum(durs) + TAIL
BG = sky((255, 255, 255), (240, 240, 245))
def tint_bg(col, a=40):
    im = BG.copy(); g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(g).ellipse([-300, 500, W + 300, 2200], fill=col + (a,))
    im.alpha_composite(g.filter(ImageFilter.GaussianBlur(80))); return im
BGS = [tint_bg(c) for _, _, c in TOOLS]

def rays(img, t, col, cx=W / 2, cy=900, a=40):
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for k in range(16):
        ang = t * 0.6 + k * math.pi / 8
        d.polygon([(cx, cy), (cx + math.cos(ang) * 2000, cy + math.sin(ang) * 2000), (cx + math.cos(ang + 0.12) * 2000, cy + math.sin(ang + 0.12) * 2000)], fill=col + (a,))
    img.alpha_composite(lay)

def num_slam(img, t, t0, n, col):
    u = t - t0
    if u < 0: return
    d = ImageDraw.Draw(img)
    if u < 0.7:
        s = 2.2 - 1.2 * ease(u / 0.25)
        a = 1 if u < 0.5 else 1 - (u - 0.5) / 0.2
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay)
        txt_c(ld, (W / 2, 900 - 260 * s), str(n), font(int(400 * s)), col, 14, WHITE)
        if a < 1: lay.putalpha(lay.getchannel('A').point(lambda v: int(v * max(0, a))))
        img.alpha_composite(lay)
    else:
        name = {1: 'PORTADA DE NEGOCIO', 2: 'MARKETPLACE', 3: 'VIDEOS VIRALES', 4: 'GANA CON MARKETING'}[n]
        size = 60
        while d.textlength(name, font=font(size)) > W - 2 * 60 - 150 - 80 and size > 36: size -= 2
        total = 130 + 24 + d.textlength(name, font=font(size)) + 80; bx = (W - total) / 2
        d.ellipse([bx, 320, bx + 130, 450], fill=col)
        bb = d.textbbox((0, 0), str(n), font=font(96)); tw = bb[2] - bb[0]
        d.text((bx + 65 - tw / 2 - bb[0], 385 - (bb[1] + bb[3]) / 2), str(n), font=font(96), fill=WHITE)

def tool_title(d, t, t0, name, col, y=320):
    s = min(1.0, pop(t0, t))
    if s <= 0.05: return
    size = 60
    while d.textlength(name, font=font(size)) > W - 2 * 60 - 150 - 80 and size > 36: size -= 2
    tw = d.textlength(name, font=font(size)); pw = tw + 80; total = 130 + 24 + pw
    x0 = (W - total) / 2 + 130 + 24
    cx = x0 + pw / 2
    d.rounded_rectangle([cx - pw / 2 * s, y, cx + pw / 2 * s, y + 130], 40, fill=col)
    if s > 0.9:
        bb = d.textbbox((0, 0), name, font=font(size))
        d.text((cx - tw / 2, y + 65 - (bb[1] + bb[3]) / 2), name, font=font(size), fill=WHITE)
    return (W - total) / 2

def frame(f):
    t = f / FPS
    i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - starts[-1]
    dur = durs[i]
    img = BG.copy(); d = ImageDraw.Draw(img)
    if i == 0:
        d = ImageDraw.Draw(img)
        for k2, (txt, col, t0) in enumerate((('MIRA LO QUE', DARK, 0.05), ('NO TE HAN DICHO', RED, 0.45))):
            sc = pop(t0, t)
            if sc > 0.05:
                ff = font(int((110 if k2 == 0 else 100) * min(1.15, sc)) + 1)
                txt_c(d, (W / 2, 380 + k2 * 140), txt, ff, col, 8, WHITE)
        if lt > 0.8: put(img, emoji('👀', 100), W / 2, 650 + 6 * math.sin(t * 8))
        for k, (em, nm, col) in enumerate(TOOLS):
            t0 = 1.2 + k * 0.35; u = ease((lt - t0) / 0.4)
            if lt < t0: continue
            a = math.radians(-135 + k * 90); r = 330 * u
            x, y = W / 2 + math.cos(a) * r, 1080 + math.sin(a) * r * 0.75
            d = ImageDraw.Draw(img); d.rounded_rectangle([x - 130, y - 110, x + 130, y + 110], 40, fill=col)
            put(img, emoji(em, 130), x, y)
        if lt > 3.0: pill(ImageDraw.Draw(img), W / 2, 1360, '4 HERRAMIENTAS · 1 LUGAR', DARK, YEL, 52)
        m = stand(f, t, 0.36); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10))
        if lt < 0.2: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(200 * (1 - lt / 0.2)))))
    elif i == 1:
        img = BGS[0].copy(); d = ImageDraw.Draw(img)
        portada(img, 290, 520, 500, 1000, t, starts[1] + 0.9)
        tool_title(ImageDraw.Draw(img), t, starts[1] + 0.6, 'PORTADA DE NEGOCIO', RED)
        if lt > 4.6: stamp(img, starts[1] + 4.6, t, 'GRATIS', GREEN, 1650, 140, -6)
        num_slam(img, t, starts[1], 1, RED)
    elif i == 2:
        img = BGS[1].copy(); d = ImageDraw.Draw(img)
        tool_title(d, t, starts[2] + 0.6, 'MARKETPLACE', ORNG)
        s = pop(starts[2] + 0.9, t)
        if s > 0.05:
            d.rounded_rectangle([150, 520, 930, 1100], 40, fill=WHITE, outline=(225, 225, 230), width=4)
            d.rectangle([170, 540, 910, 840], fill=(255, 236, 214)); put(img, emoji('👟', int(220 * min(1, s)) + 1), 540, 690); d = ImageDraw.Draw(img)
            d.text((190, 860), 'Tenis deportivos', font=font(52), fill=DARK); d.text((190, 930), '$35 · Bogotá', font=font(44), fill=(110, 110, 120))
            pill(d, 540, 1000, 'Publicado gratis', GREEN, WHITE, 40)
        if lt > 2.4:
            d.rounded_rectangle([170, 1160, 910, 1340], 30, fill=(220, 248, 198)); put(img, emoji('💬', 80), 240, 1250); d = ImageDraw.Draw(img)
            d.text((300, 1205), '¿Aún está disponible?', font=font(46), fill=DARK)
        if lt > 3.8: stamp(img, starts[2] + 3.8, t, '0% COMISIÓN', RED, 1600, 110, -5)
        num_slam(img, t, starts[2], 2, ORNG)
    elif i == 3:
        img = BGS[2].copy(); d = ImageDraw.Draw(img)
        tool_title(d, t, starts[3] + 0.6, 'VIDEOS VIRALES', PURP)
        x0, y0 = 330, 500
        d.rounded_rectangle([x0, y0, x0 + 420, y0 + 800], 46, fill=(20, 20, 26))
        scr = (x0 + 16, y0 + 30, x0 + 404, y0 + 770); d.rounded_rectangle(scr, 30, fill=(40, 30, 70))
        m = stand(f, t, 0.3); img.alpha_composite(m, (int(x0 + 210 - m.width / 2), y0 + 330)); d = ImageDraw.Draw(img)
        words = ['ESTO', 'SE', 'HACE', 'VIRAL']; k = int(lt * 3) % 4
        for j, w in enumerate(words[:2]):
            pass
        txt_c(d, (x0 + 210, y0 + 120), words[k], font(76), YEL if k % 2 else WHITE, 6, (0, 0, 0))
        put(img, emoji('🔊', 60), x0 + 360, y0 + 80)
        hearts = int(lt * 2)
        for j in range(min(6, hearts)):
            u = ((lt * 0.8 + j / 6) % 1); put(img, emoji('❤️', 60), x0 + 380 + 20 * math.sin(j + t * 3), y0 + 700 - u * 500)
        d = ImageDraw.Draw(img)
        d.rounded_rectangle([110, 700, 290, 840], 30, fill=WHITE, outline=PURP, width=5); txt_c(d, (200, 722), 'IA', font(72), PURP)
        for j, (s_, c) in enumerate((('TikTok', (20, 20, 25)), ('Reels', (190, 40, 120)), ('Shorts', (220, 30, 30)))):
            if lt > 4.5 + j * 0.5:
                y = 1380 + j * 0
                xx = 160 + j * 260; d.rounded_rectangle([xx, 1380, xx + 240, 1480], 40, fill=c); txt_c(d, (xx + 120, 1400), s_, font(46), WHITE)
        num_slam(img, t, starts[3], 3, PURP)
    elif i == 4:
        img = BGS[3].copy(); d = ImageDraw.Draw(img)
        tool_title(d, t, starts[4] + 0.8, 'GANA CON MARKETING', TEAL)
        items = [('🎓', 'Cursos paso a paso', 1.4), ('✅', 'Tareas diarias de minutos', 2.8), ('👥', 'Comunidad que te acompaña', 4.4)]
        for k, (em, s_, t0) in enumerate(items):
            sc = pop(starts[4] + t0, t)
            if sc <= 0: continue
            y = 560 + k * 220
            d.rounded_rectangle([50, y, 1030, y + 180], 44, fill=WHITE, outline=TEAL, width=5)
            fs = 46
            while d.textlength(s_, font=font(fs)) > 1030 - 250 - 40 and fs > 30: fs -= 2
            put(img, emoji(em, int(100 * min(1.2, sc)) + 1), 150, y + 90); d = ImageDraw.Draw(img)
            bb = d.textbbox((0, 0), s_, font=font(fs)); d.text((250, y + 90 - (bb[1] + bb[3]) / 2), s_, font=font(fs), fill=DARK)
        m = stand(f, t, 0.3); img.alpha_composite(m, (W - m.width - 20, H - m.height - 10))
        num_slam(img, t, starts[4], 4, TEAL)
    elif i == 5:
        rays(img, t, (212, 160, 23), cy=1100, a=35); d = ImageDraw.Draw(img)
        ranks = [('Bronce', (180, 83, 9)), ('Plata', (140, 140, 150)), ('Oro', (212, 160, 23)), ('Platino', (14, 165, 233)), ('Diamante', (124, 58, 237)), ('Corona', (225, 6, 0))]
        lvl = min(5, int(ease(lt / dur * 1.1) * 6))
        for k, (n, c) in enumerate(ranks):
            y = 1600 - k * 175
            d.rounded_rectangle([60, y, 520, y + 140], 30, fill=c if k <= lvl else (210, 210, 215)); txt_c(d, (290, y + 35), n, font(60), WHITE)
            if 2 <= k <= lvl: d.rounded_rectangle([540, y + 30, 760, y + 110], 30, fill=GREEN); txt_c(d, (650, y + 42), 'Sueldo', font(40), WHITE)
        if lvl >= 2:
            for j in range(8):
                u = (t * 0.9 + j / 8) % 1; put(img, emoji('🪙', 70), 820 + 60 * math.sin(j * 2 + t), 500 + u * 1100)
        m = stand(f, t, 0.24); img.alpha_composite(m, (W - m.width - 10, int(1600 - lvl * 175 - m.height + 140)))
    elif i == 6:
        rays(img, t, RED, a=22); d = ImageDraw.Draw(img)
        for k, (em, nm, col) in enumerate(TOOLS):
            s = pop(starts[6] + k * 0.85, t)
            if s <= 0.05: continue
            c, r = k % 2, k // 2; x = 290 + c * 500; y = 640 + r * 420
            w2, h2 = 220 * s, 180 * s
            d.rounded_rectangle([x - w2, y - h2, x + w2, y + h2], 44, fill=col)
            if s > 0.6:
                put(img, emoji(em, 120), x, y - 50); d = ImageDraw.Draw(img); txt_c(d, (x, y + 40), nm if len(nm) < 13 else ('MARKETING' if k == 3 else 'VIDEOS'), font(44), WHITE)
        if lt > 3.6:
            stamp(img, starts[6] + 3.6, t, '1 SOLA MEMBRESÍA', RED, 1550, 90, -4)
            confetti(img, starts[6] + 3.6, t, 70, 3)
    elif i == 7:
        flash = int(t * 6) % 2
        img = Image.new('RGBA', (W, H), (255, 235, 235, 255) if flash else (255, 255, 255, 255)); d = ImageDraw.Draw(img)
        put(img, emoji('⏰', 300), W / 2, 760)
        for k in range(3):
            x = W + 200 - ((lt * 500) + k * 380) % (W + 400)
            put(img, emoji('🏃', 200), x, 1300)
        d = ImageDraw.Draw(img); pill(d, W / 2, 1500, 'TU COMPETENCIA YA VIENE', RED, WHITE, 54)
    else:
        rays(img, t, RED, cy=1000, a=28); d = ImageDraw.Draw(img)
        bounce = abs(math.sin(t * 5)) * 40
        d.polygon([(W / 2, 330 - bounce), (W / 2 - 90, 470 - bounce), (W / 2 + 90, 470 - bounce)], fill=RED)
        d.rectangle([W / 2 - 35, 460 - bounce, W / 2 + 35, 560 - bounce], fill=RED)
        s = 1 + 0.05 * math.sin(t * 9); bw = 450 * s
        d.rounded_rectangle([W / 2 - bw, 600, W / 2 + bw, 840], 60, fill=RED)
        txt_c(d, (W / 2, 620), 'TOCA EL LINK', font(int(78 * s)), WHITE); txt_c(d, (W / 2, 715), 'DE MI PERFIL', font(int(78 * s)), YEL)
        if lt > 1.4: pill(d, W / 2, 890, 'y escríbeme 💬'.replace(' 💬', ''), GREEN, WHITE, 64); put(img, emoji('💬', 90), W / 2 + 280, 950)
        m = stand(f, t, 0.46); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10))
        confetti(img, starts[8] + 2.2, t, 80, 8)
        d = ImageDraw.Draw(img); txt_c(d, (W / 2, 1060), 'Los resultados dependen de tu constancia.', font(30), (110, 110, 120))
    # camera punch + beat shake
    if lt < 0.2 and i > 0:
        z = 1 + 0.08 * (1 - lt / 0.2)
        img = img.resize((int(W * z), int(H * z)), Image.BILINEAR).crop((int((W * z - W) / 2), int((H * z - H) / 2), int((W * z - W) / 2) + W, int((H * z - H) / 2) + H))
    if lt < 0.08 and i > 0: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(220 * (1 - lt / 0.08)))))
    sx, sy = shake(t, 0.05, 20, 0.45)
    if sx or sy: img = img.transform(img.size, Image.AFFINE, (1, 0, -sx, 0, 1, -sy), fillcolor=(255, 255, 255, 255))
    caption(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 14, W * min(1, t / TOTAL), H], fill=RED)
    return img.convert('RGB')

def events():
    S = starts; ev = []
    for i in range(1, len(durs)): ev += [(S[i] - 0.12, 'whoosh', 0), (S[i], 'boom', 0)]
    ev += [(0.05, 'boom', 0), (0.05, 'stamp', 0)] + [(1.2 + k * 0.35, 'pop', 700 + k * 150) for k in range(4)] + [(3.0, 'ding', 1318)]
    ev += [(S[1] + 0.6, 'pop', 900)] + [(S[1] + 0.9 + k * 0.25, 'pop', 1000 + k * 100) for k in range(5)] + [(S[1] + 4.6, 'stamp', 0), (S[1] + 4.6, 'cheer', 0)]
    ev += [(S[2] + 0.6, 'pop', 900), (S[2] + 0.9, 'pop', 700), (S[2] + 2.4, 'msg', 0), (S[2] + 3.8, 'stamp', 0), (S[2] + 3.8, 'coin', 0)]
    ev += [(S[3] + 0.6, 'pop', 900)] + [(S[3] + 4.5 + j * 0.5, 'pop', 1000 + j * 150) for j in range(3)] + [(S[3] + k * 0.333, 'key', 0) for k in range(int(durs[3] * 3))]
    ev += [(S[4] + 0.8, 'pop', 900)] + [(S[4] + x, 'ding', 1046 + k * 200) for k, x in enumerate((1.4, 2.8, 4.4))]
    prev = -1
    for k in range(int(durs[5] * 60)):
        lt = k / 60; lv = min(5, int(ease(lt / durs[5] * 1.1) * 6))
        if lv != prev:
            ev.append((S[5] + lt, 'ding', 784 * 2 ** (lv / 6)))
            if lv >= 2: ev.append((S[5] + lt + 0.05, 'coin', 0))
            prev = lv
    ev += [(S[6] + k * 0.85, 'stamp', 0) for k in range(4)] + [(S[6] + 3.6, 'stamp', 0), (S[6] + 3.6, 'cheer', 0)]
    ev += [(S[7] + k * 0.5, 'buzz', 0) for k in range(4)]
    ev += [(S[8] + 0.1, 'riser', 0), (S[8] + 1.4, 'msg', 0), (S[8] + 2.2, 'cheer', 0), (S[8] + 2.2, 'ding', 2093)]
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
                              '-shortest', '-movflags', '+faststart', 'dia-05.mp4'], stdin=subprocess.PIPE)
        for f in range(n): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait()
        print('Listo: dia-05.mp4')
