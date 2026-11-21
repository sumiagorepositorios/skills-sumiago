"""Arma el reel 9:16 (1080x1920, 30 fps) "¿Por qué arriba hace frío?" con la mascota animada.
Uso (en la carpeta donde están voice.wav, durs.json y mascot_clean.png):
    python scripts/render.py test 2 6 11 15 19 23 28 32 36 40 45 51 57   -> test.jpg con cuadros de muestra
    python scripts/render.py full                                         -> montana-fria.mp4
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import (W, H, FPS, font, txt_c, card, glow, caption, ease, stand, scene, durs, TOTAL, YEL, RED, WHITE, CYAN)

# --- ayudas de paisaje (cielo, nubes, sol, mascota en la esquina) ---
def sky(c0, c1):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c0) * (1 - y) + np.array(c1) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1)).convert('RGBA')
def cloud(d, x, y, s=1.0, col=(255, 255, 255)):
    for ox, oy, r in ((0, 0, 60), (55, -25, 70), (115, 0, 55), (55, 20, 60)):
        d.ellipse([x + (ox - r) * s, y + (oy - r) * s, x + (ox + r) * s, y + (oy + r) * s], fill=col)
def sun(img, x, y, r=70):
    glow(img, x, y, int(r * 2), (255, 220, 120), 120, 30); ImageDraw.Draw(img).ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 60))
def mascot_corner(img, f, t, s=0.33, side='right'):
    m = stand(f, t, s); x = W - m.width - 10 if side == 'right' else 10
    img.alpha_composite(m, (x, H - m.height - 10))

NIGHT = sky((14, 30, 80), (40, 90, 170))
rnd0 = random.Random(4); d0 = ImageDraw.Draw(NIGHT)
for _ in range(120):
    x, y, r = rnd0.randint(0, W), rnd0.randint(0, 1300), rnd0.choice([1, 1, 2]); d0.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 160))
DAY = sky((70, 140, 220), (180, 220, 250))

def mountain(d, cx, base, h, w, snow=True):
    top = (cx, base - h)
    L, R = (cx - w / 2, base), (cx + w / 2, base)
    mid1, mid2 = (cx - w * 0.18, base - h * 0.45), (cx + w * 0.2, base - h * 0.4)
    d.polygon([L, top, mid1], fill=(120, 115, 125)); d.polygon([L, mid1, (cx, base)], fill=(95, 90, 100))
    d.polygon([top, R, mid2], fill=(150, 145, 155)); d.polygon([mid2, R, (cx, base)], fill=(125, 120, 130))
    d.polygon([top, mid1, (cx, base), mid2], fill=(105, 100, 112))
    if snow:
        s = 0.32
        d.polygon([top, (cx - w * 0.5 * s, base - h * (1 - s)), (cx - w * 0.06, base - h * (1 - s) + 30), (cx + w * 0.05, base - h * (1 - s) - 10), (cx + w * 0.5 * s, base - h * (1 - s))], fill=(245, 248, 255))
        d.polygon([top, (cx + w * 0.5 * s, base - h * (1 - s)), (cx + w * 0.05, base - h * (1 - s) - 10)], fill=(215, 225, 240))
    return top

def thermo(d, x, y, val, col):
    d.rounded_rectangle([x, y, x + 230, y + 90], 30, fill=(15, 20, 40)); txt_c(d, (x + 115, y + 8), f'{val}°C', font(58), col)

def scene_mtn(img, t, f, shiver=False, flag=False):
    d = ImageDraw.Draw(img)
    mountain(d, 300, 1700, 900, 900); mountain(d, 820, 1700, 650, 700)
    top = mountain(d, 560, 1750, 1150, 1000)
    d.rectangle([0, 1700, W, H], fill=(80, 150, 80))
    return top

def frame(f):
    t = f / FPS; i, lt = scene(t); dur = durs[i]; p = min(1, lt / dur)
    if i in (0, 10, 12):
        img = NIGHT.copy() if i != 10 else DAY.copy()
        sun(img, 880, 520, 85); d = ImageDraw.Draw(img)
        top = scene_mtn(img, t, f)
        m = stand(f, t, 0.3); mx = int(top[0] - m.width / 2 + 4 * math.sin(t * 40)); my = int(top[1] - m.height + 90)
        img.alpha_composite(m, (mx, my)); d = ImageDraw.Draw(img)
        if i == 0:
            thermo(d, 60, 1000, -33, CYAN)
            if lt > 1.5: txt_c(d, (W / 2, 1380), '¿POR QUÉ?', font(120), YEL, 9)
        elif i == 10:
            d.rounded_rectangle([600, 1500, 1040, 1590], 36, fill=(20, 30, 60)); txt_c(d, (820, 1508), 'te calienta', font(46), YEL)
            d.line([(820, 1600), (820, 1700)], fill=YEL, width=10); d.polygon([(795, 1690), (845, 1690), (820, 1730)], fill=YEL)
            thermo(d, 60, 1000, -20, CYAN)
        else:
            # carámbanos
            for k in range(6):
                x = mx + 70 + k * 30; d.polygon([(x, my + 200), (x + 12, my + 200), (x + 6, my + 240 + 10 * (k % 2))], fill=(200, 230, 255))
            cx, cy = W / 2, 1420; dx = (lt * 160) % 140
            d.polygon([(cx - 130 + dx, cy + 10), (cx + 110 + dx, cy - 90), (cx + 10 + dx, cy + 90), (cx - 20 + dx, cy + 30)], fill=WHITE)
            txt_c(d, (W / 2, 1560), 'ENVÍASELO A ESE AMIGO', font(58), YEL, 6)
    elif i == 1:
        img = sky((2, 4, 14), (10, 12, 30)); d = ImageDraw.Draw(img)
        glow(img, 960, 420, 260, (255, 200, 80), 160, 50); d = ImageDraw.Draw(img); d.ellipse([900, 360, 1020, 480], fill=(255, 210, 90))
        ex, ey, r = 300, 1200, 230
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=(40, 110, 210))
        for ox, oy, rr in ((-80, -60, 90), (60, 50, 110), (-40, 120, 60)): d.ellipse([ex + ox - rr, ey + oy - rr, ex + ox + rr, ey + oy + rr * 0.7], fill=(70, 160, 80))
        d.line([(ex, ey - r), (960, 420)], fill=(255, 255, 255), width=3)
        d.ellipse([ex - 10, ey - r - 10, ex + 10, ey - r + 10], fill=RED)
        d.rounded_rectangle([ex + 30, ey - r - 80, ex + 260, ey - r - 20], 25, fill=(30, 30, 40)); txt_c(d, (ex + 145, ey - r - 76), 'Everest', font(40), WHITE)
        d.rounded_rectangle([140, 1520, 940, 1700], 40, fill=(20, 20, 30), outline=YEL, width=4)
        txt_c(d, (540, 1530), '9 km', font(70), YEL); txt_c(d, (540, 1615), 'de 150.000.000 km', font(48), WHITE)
    elif i == 2:
        img = sky((30, 20, 15), (90, 55, 30)); d = ImageDraw.Draw(img)
        d.polygon([(0, H), (W, H), (600, 900), (480, 900)], fill=(120, 80, 45))
        d.polygon([(470, H), (610, H), (548, 900), (532, 900)], fill=(240, 200, 60))
        for k in range(20):
            y = 900 + (H - 900) * (k / 20) ** 1.6; wdt = 8 + 70 * (k / 20) ** 1.6; d.line([(540 - wdt, y), (540 + wdt, y)], fill=(150, 110, 30), width=3)
        glow(img, 540, 820, 140, (255, 180, 80), 170, 30); d = ImageDraw.Draw(img); d.ellipse([505, 785, 575, 855], fill=(255, 220, 140))
        txt_c(d, (540, 1520), '10 m', font(70), WHITE, 6)
        if lt > dur * 0.45:
            dd = card(img, (90, 380, 990, 720), (255, 210, 63))
            dd.line([(150, 520), (930, 470)], fill=(140, 90, 50), width=60)
            dd.text((130, 400), 'un pelo: 0,07 mm', font=font(44), fill=WHITE)
            dd.ellipse([530, 610, 546, 626], fill=RED); dd.text((130, 640), 'te acercas: 0,0006 mm', font=font(44), fill=(255, 120, 120))
    elif i == 3:
        img = DAY.copy(); sun(img, 860, 520, 90); d = ImageDraw.Draw(img)
        scene_mtn(img, t, f)
        if lt < dur * 0.45:
            d.rounded_rectangle([140, 700, 940, 820], 40, fill=(20, 20, 30)); txt_c(d, (540, 715), 'distancia', font(70), WHITE)
            d.line([(180, 700), (900, 820)], fill=RED, width=16)
        else:
            for k in range(6):
                x = 700 - k * 90; d.line([(860, 520), (x, 1500)], fill=(255, 240, 160), width=6)
            d.rounded_rectangle([90, 700, 990, 860], 40, fill=(20, 20, 30)); txt_c(d, (540, 712), 'el sol casi no', font(56), WHITE); txt_c(d, (540, 775), 'calienta el aire', font(56), YEL)
    elif i == 4:
        img = sky((40, 45, 70), (60, 60, 80)); d = ImageDraw.Draw(img)
        d.rectangle([0, 1350, W, H], fill=(140, 95, 55))
        for k in range(10): d.line([(0, 1350 + k * 60), (W, 1350 + k * 60)], fill=(120, 80, 45), width=3)
        wx0, wy0 = 520, 560; d.rectangle([wx0, wy0, wx0 + 360, wy0 + 420], fill=(170, 220, 255)); d.rectangle([wx0, wy0, wx0 + 360, wy0 + 420], outline=WHITE, width=14)
        d.line([(wx0 + 180, wy0), (wx0 + 180, wy0 + 420)], fill=WHITE, width=10)
        beam = Image.new('RGBA', (W, H), (0, 0, 0, 0)); bd = ImageDraw.Draw(beam)
        k = ease(lt / 1.5)
        bd.polygon([(wx0, wy0), (wx0 + 360, wy0), (wx0 + 360 - 600 * k, wy0 + 420 + 650 * k), (wx0 - 600 * k, wy0 + 420 + 300 * k)], fill=(255, 245, 200, 70))
        img.alpha_composite(beam.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(img)
        if k > 0.95:
            heat = 0.5 + 0.5 * math.sin(t * 4)
            d.polygon([(wx0 - 600, 1500), (wx0 - 240, 1500), (wx0 - 240, 1640), (wx0 - 600, 1640)], fill=(255, int(190 + 40 * heat), 90))
            txt_c(d, (wx0 - 420, 1530), 'suelo', font(52), (90, 50, 20))
        mascot_corner(img, f, t, 0.3)
    elif i == 5:
        img = DAY.copy(); sun(img, 860, 480, 70); d = ImageDraw.Draw(img)
        d.rectangle([0, 1450, W, H], fill=(200, 120, 50))
        glow(img, W // 2, 1500, 500, (255, 140, 50), 120, 60); d = ImageDraw.Draw(img)
        for k in range(8):
            x = 80 + k * 130; ph = t * 3 + k
            pts = [(x + 18 * math.sin(ph + y / 40), y) for y in range(1430, 900, -20)]
            d.line(pts, fill=(255, 170, 90), width=6)
        dd = card(img, (620, 380, 1000, 760), (255, 140, 60))
        dd.rectangle([700, 500, 920, 640], fill=(190, 195, 205)); dd.rectangle([712, 520, 908, 630], fill=(80, 160, 230))
        for k in range(6): dd.polygon([(710 + k * 36, 700), (726 + k * 36, 660 - 8 * math.sin(t * 15 + k)), (742 + k * 36, 700)], fill=(90, 140, 255))
        txt_c(dd, (810, 400), 'como una olla', font(36), WHITE)
    elif i == 6:
        img = DAY.copy(); d = ImageDraw.Draw(img)
        top = scene_mtn(img, t, f)
        u = ease(lt / dur)
        bx, by = 300 + 200 * u, 1550 - 900 * u; r = 50 + 90 * u
        glow(img, int(bx), int(by), int(r * 1.5), (255, 140, 60), 120, 20); d = ImageDraw.Draw(img)
        d.ellipse([bx - r, by - r, bx + r, by + r], fill=(255, 150, 70), outline=WHITE, width=4)
        for a in range(0, 360, 45):
            ra = math.radians(a); L = 60 * (1 - u) + 20
            ox, oy = bx + math.cos(ra) * (r + 20 + L), by + math.sin(ra) * (r + 20 + L)
            d.line([(ox, oy), (bx + math.cos(ra) * (r + 15), by + math.sin(ra) * (r + 15))], fill=WHITE, width=5)
        txt_c(d, (W / 2, 420), 'menos aire = se estira', font(60), YEL, 6)
    elif i == 7:
        img = sky((25, 30, 40), (50, 55, 65)); d = ImageDraw.Draw(img)
        cx, cy = W / 2, 1650
        d.ellipse([cx - 520, cy - 520, cx + 520, cy + 520], fill=(30, 30, 34)); d.ellipse([cx - 330, cy - 330, cx + 330, cy + 330], fill=(170, 175, 185))
        d.rectangle([cx - 18, cy - 640, cx + 18, cy - 500], fill=(190, 160, 70))
        pl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
        for k in range(16):
            u = (t * 1.2 + k / 16) % 1; a = -math.pi / 2 + (k % 5 - 2) * 0.35
            x = cx + math.cos(a) * u * 380; y = cy - 640 + math.sin(a) * u * 380
            pd.ellipse([x - 20 - 30 * u, y - 20 - 30 * u, x + 20 + 30 * u, y + 20 + 30 * u], fill=(170, 220, 255, int(200 * (1 - u))))
        img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(img)
        d.rounded_rectangle([390, 1180, 690, 1270], 40, fill=(20, 40, 80)); txt_c(d, (540, 1188), 'frío', font(64), CYAN)
        mascot_corner(img, f, t, 0.3, 'left')
    elif i in (8, 9):
        img = NIGHT.copy() if i == 9 else DAY.copy(); sun(img, 880, 500, 70); d = ImageDraw.Draw(img)
        if i == 8:
            scene_mtn(img, t, f)
            for k in range(6):
                y = 1700 - k * 200; temp = 15 - 6 * k
                d.line([(30, y), (70, y)], fill=WHITE, width=4)
                d.text((80, y - 40), f'{k} km', font=font(34), fill=WHITE, stroke_width=3, stroke_fill=(0, 0, 0))
                d.text((80, y - 4), f'{temp:+d}°C', font=font(34), fill=YEL if temp > 0 else CYAN, stroke_width=3, stroke_fill=(0, 0, 0))
            u = ease(lt / dur); my = 1700 - 1000 * u
            d.polygon([(250, my), (290, my - 20), (290, my + 20)], fill=RED)
            d.rounded_rectangle([300, 600, 780, 700], 40, fill=(20, 20, 30)); txt_c(d, (540, 610), '-6°C por km', font(60), YEL)
        else:
            mountain(d, 700, H, 500, 700)
            for k in range(4):
                y = 1300 - k * 220
                d.line([(30, y), (70, y)], fill=WHITE, width=4); d.text((80, y - 20), f'{9 + k} km', font=font(36), fill=WHITE)
            ax = -200 + (W + 400) * (lt / dur); ay = 820
            d.polygon([(ax, ay), (ax + 260, ay - 10), (ax + 300, ay), (ax + 260, ay + 14), (ax, ay + 14)], fill=WHITE)
            d.polygon([(ax + 110, ay + 4), (ax + 170, ay + 4), (ax + 90, ay + 90)], fill=(220, 225, 235)); d.polygon([(ax + 10, ay), (ax + 40, ay), (ax + 5, ay - 50)], fill=(220, 225, 235))
            thermo(d, 680, 1000, -50, CYAN)
    else:
        img = sky((14, 30, 80), (8, 10, 30)); d = ImageDraw.Draw(img)
        px0, py0 = 330, 420
        d.rounded_rectangle([px0, py0, px0 + 420, py0 + 820], 50, fill=(20, 20, 26), outline=(150, 150, 160), width=8)
        mini = NIGHT.copy(); md = ImageDraw.Draw(mini); mountain(md, 540, 1700, 1100, 1000)
        img.paste(mini.crop((0, 450, W, H)).resize((380, 520)).convert('RGB'), (px0 + 20, py0 + 150)); d = ImageDraw.Draw(img)
        if lt > 1.6:
            s = 1 + 0.05 * math.sin(t * 10); w2 = int(400 * s)
            d.rounded_rectangle([W / 2 - w2, 1300, W / 2 + w2, 1480], 50, fill=YEL)
            txt_c(d, (W / 2, 1305), 'COMENTA', font(56), (20, 20, 20)); txt_c(d, (W / 2, 1365), 'SUMIAGO', font(88), RED)
    if lt < 0.12 and i > 0:
        img.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - lt / 0.12)))))
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
        n = int(TOTAL * FPS) - 1
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'voice.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '160k',
                              '-shortest', '-movflags', '+faststart', 'montana-fria.mp4'], stdin=subprocess.PIPE)
        for f in range(n):
            p.stdin.write(frame(f).tobytes())
            if f % 300 == 0: print(f'{f}/{n} cuadros')
        p.stdin.close(); p.wait(); print('Listo: montana-fria.mp4')
