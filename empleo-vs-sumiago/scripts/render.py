"""Arma el reel 9:16 (1080x1920, 30 fps) "Empleo vs Sumiago, MIRA!" con fondo blanco, la mascota animada, música y efectos.
Uso (en la carpeta donde están voice.wav, durs.json, mix.wav y mascot_clean.png):
    python scripts/render.py test 2 5 9 20 24 30 35 41 45.5 48   -> test.jpg con cuadros de muestra
    python scripts/render.py full                                 -> empleo-vs-sumiago.mp4 (usa mix.wav: voz + música + efectos)
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import base
from base import (W, H, FPS, font, txt_c, card, glow, ease, stand, scene, durs, TOTAL, YEL, RED, WHITE, CYAN)

def sky(c0, c1):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c0) * (1 - y) + np.array(c1) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1)).convert('RGBA')

# subtítulos oscuros con la palabra que suena en rojo (para fondo blanco)
def caption(img, t):
    d = ImageDraw.Draw(img)
    for ch in base.chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is base.chunks[-1] and t >= ch[0][0]):
            line = ' '.join(w[2] for w in ch); ff = font(64); tw = d.textlength(line, font=ff)
            if tw > W - 120: ff = font(int(64 * (W - 120) / tw)); tw = d.textlength(line, font=ff)
            x = (W - tw) / 2
            for (a, b, w, _) in ch:
                d.text((x, 230), w, font=ff, fill=RED if a <= t < b + 0.02 else (25, 25, 30), stroke_width=5, stroke_fill=(255, 255, 255))
                x += d.textlength(w + ' ', font=ff)
            return

GREEN = (60, 200, 110); GRAY = (150, 150, 160)
BG = sky((255, 255, 255), (238, 238, 242))
BG2 = sky((255, 255, 255), (238, 238, 242))

def coin(d, x, y, r=34):
    d.ellipse([x - r, y - r, x + r, y + r], fill=(240, 190, 40), outline=(190, 140, 20), width=5); txt_c(d, (x, y - r * 0.75), '$', font(int(r * 1.2)), (150, 100, 10))

def phone(d, x, y, w=360, h=700):
    d.rounded_rectangle([x, y, x + w, y + h], 46, fill=(20, 20, 26), outline=(150, 150, 160), width=8)
    d.rounded_rectangle([x + 18, y + 40, x + w - 18, y + h - 40], 26, fill=(35, 35, 45))
    return (x + 18, y + 40, x + w - 18, y + h - 40)

def pill(d, cx, y, s, col, tc=WHITE, size=52):
    w = d.textlength(s, font=font(size)); d.rounded_rectangle([cx - w / 2 - 34, y, cx + w / 2 + 34, y + size + 40], 40, fill=col); txt_c(d, (cx, y + 12), s, font(size), tc)

def clock(d, cx, cy, r, ang):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=WHITE, outline=(60, 60, 70), width=14)
    for k in range(12):
        a = math.radians(k * 30); d.line([(cx + math.cos(a) * r * 0.8, cy + math.sin(a) * r * 0.8), (cx + math.cos(a) * r * 0.92, cy + math.sin(a) * r * 0.92)], fill=(60, 60, 70), width=6)
    d.line([(cx, cy), (cx + math.cos(ang) * r * 0.75, cy + math.sin(ang) * r * 0.75)], fill=(30, 30, 40), width=10)
    d.line([(cx, cy), (cx + math.cos(ang / 12) * r * 0.5, cy + math.sin(ang / 12) * r * 0.5)], fill=RED, width=14)

def frame(f):
    t = f / FPS; i, lt = scene(t); dur = durs[i]; p = min(1, lt / dur)
    img = BG.copy(); d = ImageDraw.Draw(img)
    if i == 0:
        d.rectangle([0, 380, W / 2 - 6, 1480], fill=(45, 45, 55)); d.rectangle([W / 2 + 6, 380, W, 1480], fill=(120, 10, 15))
        txt_c(d, (W / 4, 430), 'EMPLEO', font(76), WHITE); txt_c(d, (3 * W / 4, 430), 'SUMIAGO', font(76), YEL)
        d.ellipse([W / 2 - 80, 840, W / 2 + 80, 1000], fill=(15, 15, 18), outline=WHITE, width=6); txt_c(d, (W / 2, 870), 'VS', font(70), WHITE)
        clock(d, W / 4, 700, 110, t * 3)
        ph = phone(d, 3 * W / 4 - 110, 560, 220, 400)
        for k in range(3):
            y = ph[1] + 30 + k * 105; d.rounded_rectangle([ph[0] + 15, y, ph[2] - 15, y + 85], 14, fill=(225, 30, 40) if k == 0 else (60, 60, 75))
        m = stand(f, t, 0.42); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10))
    elif i == 1:
        clock(d, W / 2, 800, 260, t * 4)
        on = lt < dur * 0.55
        if on:
            for k in range(5):
                u = (t * 0.9 + k / 5) % 1; coin(d, 300 + k * 120, 1150 + u * 330)
            pill(d, W / 2, 420, 'TIEMPO = DINERO', (60, 60, 75), YEL, 60)
        else:
            pill(d, W / 2, 420, 'SI NO VAS, NO COBRAS', RED, WHITE, 56)
            d.line([(250, 560), (830, 1040)], fill=RED, width=26)
        m = stand(f, t, 0.3); img.alpha_composite(m, (W - m.width - 10, H - m.height - 10))
    elif i == 2:
        img = BG2.copy(); d = ImageDraw.Draw(img)
        x0, y0, x1, y1 = 120, 650, 980, 1450
        d.line([(x0, y1), (x1, y1)], fill=(40, 40, 50), width=5); d.line([(x0, y0), (x0, y1)], fill=(40, 40, 50), width=5)
        n = min(8, 1 + int(lt / (dur * 0.7) * 8))
        for k in range(n):
            bx = x0 + 40 + k * 105; d.rectangle([bx, 1080, bx + 70, y1 - 3], fill=GRAY)
        d.line([(x0, 1060), (x1, 1060)], fill=RED, width=10)
        d.rounded_rectangle([700, 970, 960, 1045], 30, fill=RED); txt_c(d, (830, 978), 'TECHO', font(48), WHITE)
        for k, mes in enumerate(['E', 'F', 'M', 'A', 'M', 'J', 'J', 'A'][:n]): txt_c(d, (x0 + 75 + k * 105, y1 + 15), mes, font(36), (80, 80, 90))
        pill(d, W / 2, 420, 'MISMO SUELDO', (60, 60, 75), WHITE, 60)
    elif i == 3:
        m = stand(f, t, 0.55); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10)); d = ImageDraw.Draw(img)
        d.rounded_rectangle([60, 420, 500, 640], 36, fill=(45, 45, 55)); txt_c(d, (280, 440), 'EMPLEO', font(54), WHITE); txt_c(d, (280, 520), 'lo mantienes', font(44), GREEN)
        if lt > 1.8:
            d.rounded_rectangle([580, 420, 1020, 640], 36, fill=RED); txt_c(d, (800, 440), '+ SUMIAGO', font(54), WHITE); txt_c(d, (800, 520), 'ratos libres', font(44), YEL)
        if lt > 3.2: pill(d, W / 2, 700, 'SEGUNDO INGRESO', YEL, (20, 20, 20), 56)
    elif i == 4:
        ph = phone(d, 360, 520, 360, 760)
        k = int(lt * 1.6) % 4
        for j in range(3):
            y = ph[1] + 30 + j * 225; act = j <= k
            d.rounded_rectangle([ph[0] + 20, y, ph[2] - 20, y + 200], 18, fill=(225, 30, 40) if act else (60, 60, 75))
            if act: d.polygon([(ph[0] + 140, y + 70), (ph[0] + 140, y + 130), (ph[0] + 190, y + 100)], fill=WHITE)
        gl = 0.5 + 0.5 * math.sin(t * 5); glow(img, 230, 760, 120, (255, 60, 60), int(140 * gl), 25); d = ImageDraw.Draw(img)
        d.rounded_rectangle([140, 690, 320, 830], 30, fill=(20, 20, 26), outline=RED, width=5); txt_c(d, (230, 712), 'IA', font(70), YEL)
        for j, (s, c) in enumerate((('TikTok', (30, 30, 35)), ('Reels', (190, 40, 120)), ('Shorts', (220, 30, 30)))):
            if lt > 2.2 + j * 0.5: d.rounded_rectangle([760, 700 + j * 150, 1040, 810 + j * 150], 30, fill=c, outline=WHITE, width=3); txt_c(d, (900, 722 + j * 150), s, font(46), WHITE)
        pill(d, W / 2, 1380, 'TÚ SOLO PUBLICAS', YEL, (20, 20, 20), 56)
    elif i == 5:
        d.rectangle([0, 380, W / 2 - 4, 1500], fill=(110, 170, 230)); d.rectangle([W / 2 + 4, 380, W, 1500], fill=(15, 20, 50))
        d.ellipse([170, 470, 330, 630], fill=(255, 210, 60)); d.ellipse([780, 480, 900, 600], fill=(240, 240, 220)); d.ellipse([810, 465, 920, 575], fill=(15, 20, 50))
        d.rectangle([120, 800, 420, 1500], fill=(80, 90, 110))
        for r in range(8):
            for c in range(3): d.rectangle([150 + c * 90, 840 + r * 80, 200 + c * 90, 880 + r * 80], fill=(200, 220, 240))
        txt_c(d, (W / 4, 1380), 'en tu empleo', font(44), WHITE, 4)
        rnd = random.Random(1)
        for k in range(14):
            x, y = rnd.randint(560, 1040), rnd.randint(650, 1250); d.ellipse([x - 2, y - 2, x + 2, y + 2], fill=WHITE)
        txt_c(d, (3 * W / 4, 1380), 'mientras duermes', font(44), WHITE, 4)
        views = int(120 + 9800 * ease(p))
        pill(d, W / 2, 1560, f'+{views:,} vistas'.replace(',', '.'), RED, WHITE, 60)
        for k in range(4):
            u = (t * 0.7 + k / 4) % 1; x = 600 + k * 110; y = 1200 - u * 500
            d.rounded_rectangle([x - 50, y - 26, x + 50, y + 26], 26, fill=(255, 255, 255)); txt_c(d, (x, y - 22), '+1', font(34), RED)
    elif i == 6:
        dd = card(img, (110, 420, 970, 1300), (225, 30, 40)); d = dd
        txt_c(d, (W / 2, 450), 'GANA CON MARKETING', font(54), YEL)
        tasks = ['Crear tu video del día', 'Publicar en tus redes', 'Ver la clase corta', 'Responder comentarios']
        for k, s in enumerate(tasks):
            y = 590 + k * 160; done = lt > 0.8 + k * 0.8
            d.rounded_rectangle([170, y, 250, y + 80], 18, fill=GREEN if done else (60, 60, 75))
            if done: d.line([(188, y + 42), (205, y + 60), (235, y + 22)], fill=WHITE, width=10)
            d.text((280, y + 12), s, font=font(46), fill=WHITE)
        pill(d, W / 2, 1360, 'pocos minutos al día', (60, 60, 75), WHITE, 50)
    elif i == 7:
        ranks = [('Bronce', (180, 83, 9)), ('Plata', (140, 140, 150)), ('Oro', (212, 160, 23)), ('Platino', (14, 165, 233)), ('Diamante', (124, 58, 237)), ('Corona', (225, 6, 0))]
        lvl = min(5, int(ease(p * 1.1) * 6))
        for k, (n, c) in enumerate(ranks):
            y = 1550 - k * 175; x0 = 50
            d.rounded_rectangle([x0, y, x0 + 470, y + 140], 30, fill=c if k <= lvl else (50, 50, 58))
            txt_c(d, (x0 + 235, y + 35), n, font(60), WHITE)
            if k >= 2 and k <= lvl:
                d.rounded_rectangle([x0 + 490, y + 30, x0 + 700, y + 110], 30, fill=GREEN); txt_c(d, (x0 + 595, y + 42), 'Sueldo', font(40), WHITE)
        m = stand(f, t, 0.24); k = lvl; img.alpha_composite(m, (W - m.width - 20, int(1550 - k * 175 - m.height + 140)))
    elif i == 8:
        img = BG2.copy(); d = ImageDraw.Draw(img)
        d.rounded_rectangle([50, 420, 520, 1500], 36, fill=(45, 45, 55)); d.rounded_rectangle([560, 420, 1030, 1500], 36, fill=(120, 10, 15), outline=YEL, width=5)
        txt_c(d, (285, 450), 'EMPLEO', font(60), WHITE); txt_c(d, (795, 450), 'SUMIAGO', font(60), YEL)
        left = ['1 ingreso', 'horario fijo', 'tiene techo']; right = ['tu sueldo +', 'negocio', 'semiautomático', 'crece con tu', 'constancia']
        for k, s in enumerate(left):
            if lt > 0.4 + k * 0.4: txt_c(d, (285, 620 + k * 140), s, font(50), (210, 210, 220))
        for k, s in enumerate(right):
            if lt > 2.0 + k * 0.4: txt_c(d, (795, 620 + k * 120), s, font(50), WHITE)
    elif i == 9:
        k = ease(lt / 0.4); sc = 0.6 + 0.4 * k + 0.03 * math.sin(t * 8)
        glow(img, W // 2, 860, int(330 * sc), (225, 30, 40), 120, 40); d = ImageDraw.Draw(img)
        bw, bh = 360 * sc, 300 * sc
        d.rounded_rectangle([W / 2 - bw, 860 - bh, W / 2 + bw, 860 + bh], 40, fill=(20, 20, 26), outline=YEL, width=6)
        txt_c(d, (W / 2, 860 - bh + 40), 'MEMBRESÍA', font(int(70 * sc)), WHITE)
        txt_c(d, (W / 2, 860 - 40 * sc), 'SUMIAGO', font(int(110 * sc)), RED)
        if lt > 0.8: pill(d, W / 2, 860 + bh - 130 * sc, 'TODO EMPIEZA AQUÍ', YEL, (20, 20, 20), int(48 * sc))
        m = stand(f, t, 0.32); img.alpha_composite(m, (W - m.width - 10, H - m.height - 10))
    else:
        m = stand(f, t, 0.5); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 10)); d = ImageDraw.Draw(img)
        s = 1 + 0.05 * math.sin(t * 10); w2 = int(400 * s)
        d.rounded_rectangle([W / 2 - w2, 420, W / 2 + w2, 620], 50, fill=YEL)
        txt_c(d, (W / 2, 428), 'COMENTA', font(60), (20, 20, 20)); txt_c(d, (W / 2, 495), 'SUMIAGO', font(96), RED)
        pill(d, W / 2, 680, 'sin dejar tu empleo', (60, 60, 75), WHITE, 50)
        txt_c(d, (W / 2, 800), 'Los resultados dependen de tu constancia.', font(36), (80, 80, 90))
    if lt < 0.12 and i > 0:
        img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(255 * (1 - lt / 0.12)))))
    caption(img, t)
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        ts = [float(x) for x in sys.argv[2:]]
        ims = [frame(int(x * FPS)).resize((300, 533)) for x in ts]
        c = Image.new('RGB', (300 * len(ims), 533))
        for k, im in enumerate(ims): c.paste(im, (k * 300, 0))
        c.save('test.jpg'); print('Listo: test.jpg')
    else:
        if not os.path.isfile('mix.wav'): sys.exit('Falta mix.wav: ejecuta antes python scripts/audio.py')
        n = int(TOTAL * FPS) - 1
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'mix.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                              '-shortest', '-movflags', '+faststart', 'empleo-vs-sumiago.mp4'], stdin=subprocess.PIPE)
        for f in range(n):
            p.stdin.write(frame(f).tobytes())
            if f % 300 == 0: print(f'{f}/{n} cuadros')
        p.stdin.close(); p.wait(); print('Listo: empleo-vs-sumiago.mp4')
