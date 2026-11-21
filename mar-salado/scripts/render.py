"""Arma el reel 9:16 (1080x1920, 30 fps) "¿Por qué el mar es salado?" con la mascota animada.
Uso (en la carpeta donde están voice.wav, durs.json y mascot_clean.png):
    python scripts/render.py test 2 5 9 13 16 19 23 30 36 42 46 51   -> test.jpg con cuadros de muestra
    python scripts/render.py full                                     -> mar-salado.mp4
"""
import os, sys, math, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from base import (W, H, FPS, font, txt_c, card, glow, caption, ease, stand, scene, durs, TOTAL,
                  YEL, RED, WHITE, CYAN)

SEA = (30, 110, 190); SEA2 = (15, 60, 130); SKY0 = (120, 185, 240); SKY1 = (210, 235, 255)
SAND = (230, 205, 150); ROCK = (120, 110, 105); GRASS = (90, 170, 90)

def sky(c0=SKY0, c1=SKY1):
    y = np.linspace(0, 1, H)[:, None, None]
    a = (np.array(c0) * (1 - y) + np.array(c1) * y).astype(np.uint8)
    return Image.fromarray(np.repeat(a, W, axis=1)).convert('RGBA')
SKY = sky()
def cloud(d, x, y, s=1.0, col=(255, 255, 255)):
    for ox, oy, r in ((0, 0, 60), (55, -25, 70), (115, 0, 55), (55, 20, 60)):
        d.ellipse([x + (ox - r) * s, y + (oy - r) * s, x + (ox + r) * s, y + (oy + r) * s], fill=col)
def sun(img, x, y, r=70):
    glow(img, x, y, int(r * 2), (255, 220, 120), 120, 30); ImageDraw.Draw(img).ellipse([x - r, y - r, x + r, y + r], fill=(255, 200, 60))

def landscape(t, salt_flow=False, labels=False):
    img = SKY.copy(); d = ImageDraw.Draw(img)
    sun(img, 860, 560); d = ImageDraw.Draw(img)
    cloud(d, 120 + 20 * math.sin(t * 0.5), 520, 0.9); cloud(d, 600 + 15 * math.sin(t * 0.4 + 1), 640, 0.7)
    # montaña y tierra
    d.polygon([(0, 1300), (0, 900), (260, 680), (420, 860), (560, 1000), (640, 1300)], fill=(140, 130, 120))
    d.polygon([(220, 715), (260, 680), (300, 715), (275, 730), (250, 720)], fill=WHITE)
    d.polygon([(0, 1300), (0, 1000), (300, 1020), (620, 1080), (640, 1300)], fill=GRASS)
    d.rectangle([0, 1300, 640, H], fill=(110, 80, 60))
    # mar
    d.rectangle([600, 1180, W, H], fill=SEA)
    d.polygon([(560, 1300), (640, 1180), (640, H), (560, H)], fill=SAND)
    for k in range(6):
        wx = 650 + k * 75 + 20 * math.sin(t * 2 + k); d.arc([wx, 1170, wx + 60, 1200], 200, 340, fill=(200, 230, 255), width=4)
    # río
    pts = [(250, 760), (300, 880), (260, 980), (380, 1060), (520, 1110), (640, 1190)]
    d.line(pts, fill=(90, 170, 240), width=26, joint='curve')
    if salt_flow:
        for k in range(14):
            u = (t * 0.25 + k / 14) % 1
            seg = u * (len(pts) - 1); i = int(seg); f = seg - i
            x = pts[i][0] + (pts[i + 1][0] - pts[i][0]) * f; y = pts[i][1] + (pts[i + 1][1] - pts[i][1]) * f
            d.rectangle([x - 6, y - 6, x + 6, y + 6], fill=WHITE)
        rnd = random.Random(1)
        for k in range(60):
            x, y = rnd.randint(660, W - 20), rnd.randint(1220, H - 40); d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(235, 245, 255))
    if labels:
        for (x, y, s) in ((120, 1120, 'agua dulce'), (720, 1260, 'agua salada')):
            w = d.textlength(s, font=font(40)); d.rounded_rectangle([x - 16, y - 8, x + w + 16, y + 56], 22, fill=(20, 40, 80))
            d.text((x, y), s, font=font(40), fill=WHITE)
    return img

def drop(d, x, y, r, col):
    d.ellipse([x - r, y - r, x + r, y + r], fill=col); d.polygon([(x - r * 0.85, y - r * 0.5), (x, y - r * 2.2), (x + r * 0.85, y - r * 0.5)], fill=col)

def rock(d, x, y, s, col=ROCK):
    pts = [(-120, 40), (-90, -60), (-20, -100), (70, -80), (120, -10), (100, 60), (-40, 80)]
    d.polygon([(x + px * s, y + py * s) for px, py in pts], fill=col)
    d.polygon([(x - 20 * s, y - 100 * s), (70 * s + x, y - 80 * s), (x + 20 * s, y - 20 * s)], fill=tuple(min(255, c + 25) for c in col))

def shaker(d, x, y, s=1.0, ang=0):
    d.rounded_rectangle([x - 70 * s, y - 120 * s, x + 70 * s, y + 120 * s], 30 * s, fill=(235, 240, 250), outline=(180, 190, 210), width=4)
    d.rounded_rectangle([x - 72 * s, y - 150 * s, x + 72 * s, y - 100 * s], 20 * s, fill=(170, 175, 185))
    for k in range(5): d.ellipse([x - 50 * s + k * 25 * s - 5, y - 135 * s - 5, x - 50 * s + k * 25 * s + 5, y - 135 * s + 5], fill=(60, 60, 70))
    rnd = random.Random(2)
    for k in range(40):
        px, py = x + rnd.uniform(-55, 55) * s, y + rnd.uniform(-60, 110) * s; d.rectangle([px - 3, py - 3, px + 3, py + 3], fill=WHITE)

def mascot_corner(img, f, t, s=0.33, side='right'):
    m = stand(f, t, s); x = W - m.width - 10 if side == 'right' else 10
    img.alpha_composite(m, (x, H - m.height - 10))

def frame(f):
    t = f / FPS; i, lt = scene(t); dur = durs[i]; p = min(1, lt / dur)
    if i == 0:
        img = landscape(t, labels=True); d = ImageDraw.Draw(img)
        m = stand(f, t, 0.36); img.alpha_composite(m, (80, H - m.height - 20))
        if lt > 1.0: txt_c(d, (W / 2, 380), '¿POR QUÉ?', font(110), YEL, 8)
    elif i == 1:
        img = landscape(t, salt_flow=True); d = ImageDraw.Draw(img)
        mascot_corner(img, f, t, 0.36, 'left')
        d.rounded_rectangle([600, 1500, 1020, 1580], 36, fill=(20, 40, 80)); txt_c(d, (810, 1505), 'sal al mar', font(48), WHITE)
    elif i in (2, 3):
        img = sky((110, 120, 140), (190, 200, 215)); d = ImageDraw.Draw(img)
        cloud(d, 180, 520, 1.6, (150, 155, 170)); cloud(d, 560, 480, 1.4, (160, 165, 180))
        rnd = random.Random(int(t * 12))
        for k in range(40):
            x = rnd.randint(60, W - 60); y = 650 + ((t * 900 + k * 97) % 700)
            d.line([(x, y), (x - 6, y + 30)], fill=(150, 200, 255), width=4)
        d.rectangle([0, 1450, W, H], fill=(90, 80, 70))
        crumble = ease((lt - 1.5) / 3) if i == 2 else 1
        rock(d, W / 2, 1360, 2.2 * (1 - 0.15 * crumble))
        rnd = random.Random(5)
        for k in range(int(30 * crumble)):
            x, y = W / 2 + rnd.uniform(-280, 280), 1430 + rnd.uniform(-10, 20); d.polygon([(x, y - 14), (x + 14, y + 8), (x - 12, y + 6)], fill=(150, 140, 130))
        if i == 2:
            # gota ácida
            dd = card(img, (90, 380, 520, 700), (130, 230, 130))
            drop(dd, 300, 560, 70, (160, 230, 150))
            for k in range(6):
                bx = 260 + (k % 3) * 35; by = 600 - ((t * 60 + k * 25) % 110); dd.ellipse([bx - 8, by - 8, bx + 8, by + 8], outline=WHITE, width=3)
            txt_c(dd, (300, 400), 'un poco ácida', font(40), WHITE)
            if lt > 2.0:
                dd = card(img, (580, 380, 1000, 700), (130, 200, 255))
                txt_c(dd, (790, 410), 'agua con gas', font(42), WHITE); txt_c(dd, (790, 470), 'MUY FLOJA', font(54), CYAN)
                for k in range(8):
                    bx = 650 + k * 40; by = 660 - ((t * 80 + k * 30) % 120); dd.ellipse([bx - 7, by - 7, bx + 7, by + 7], outline=WHITE, width=3)
        else:
            # sales que salen de la roca al río
            d.rectangle([0, 1520, W, 1620], fill=(90, 170, 240))
            for k in range(6):
                u = (lt * 0.5 + k / 6) % 1; x = W / 2 - 100 + k * 40; y = 1380 + u * 180
                d.rectangle([x - 7, y - 7, x + 7, y + 7], fill=WHITE)
            dd = card(img, (240, 380, 840, 640), (255, 210, 63))
            txt_c(dd, (540, 400), 'SAL EN EL RÍO', font(52), WHITE)
            dd.rounded_rectangle([300, 500, 780, 550], 25, fill=(50, 50, 70)); dd.rounded_rectangle([300, 500, 320, 550], 10, fill=YEL)
            txt_c(dd, (540, 565), 'casi nada', font(40), YEL)
            mascot_corner(img, f, t, 0.3)
    elif i in (4, 10):
        img = SKY.copy(); d = ImageDraw.Draw(img)
        sun(img, W / 2, 560, 90); d = ImageDraw.Draw(img)
        cloud(d, 100, 480, 0.9); cloud(d, 760, 520, 0.8)
        d.rectangle([0, 1250, W, H], fill=SEA)
        for k in range(8):
            wx = k * 140 + 30 * math.sin(t * 2 + k); d.arc([wx, 1235, wx + 110, 1270], 200, 340, fill=(200, 230, 255), width=5)
        # vapor que sube (gotas azules) y sal que se queda
        for k in range(12):
            u = (t * 0.5 + k / 12) % 1; x = 90 + k * 80; y = 1240 - u * 520
            drop(d, x, y, 14, (150, 210, 255, int(255 * (1 - u))))
        rnd = random.Random(9)
        for k in range(80):
            x, y = rnd.randint(20, W - 20), rnd.randint(1300, H - 30); d.rectangle([x - 5, y - 5, x + 5, y + 5], fill=WHITE)
        if i == 4:
            d.rounded_rectangle([60, 1100, 380, 1180], 36, fill=(20, 40, 80)); txt_c(d, (220, 1105), 'agua sube', font(50), CYAN)
            if lt > 2.0: d.rounded_rectangle([660, 1360, 1020, 1440], 36, fill=(20, 40, 80)); txt_c(d, (840, 1365), 'sal: se queda', font(44), YEL)
        else:
            if lt < 2.5:
                shaker(d, W / 2, 760, 1.0)
                if lt > 1.0:
                    d.line([(W / 2 - 160, 600), (W / 2 + 160, 920)], fill=RED, width=22); d.line([(W / 2 + 160, 600), (W / 2 - 160, 920)], fill=RED, width=22)
            else:
                d.rounded_rectangle([140, 700, 940, 900], 50, fill=(20, 40, 80, 230))
                txt_c(d, (W / 2, 715), 'el agua se va', font(64), CYAN); txt_c(d, (W / 2, 800), 'la sal no', font(72), YEL)
    elif i == 5:
        img = sky((40, 34, 40), (20, 18, 22)); d = ImageDraw.Draw(img)
        cx, top, bot = W / 2, 900, 1300
        lvl = 1 - 0.85 * ease((lt - 0.5) / 2.2)
        d.rectangle([cx - 330, top, cx + 330, bot], fill=(185, 190, 200)); d.rectangle([cx - 360, top - 20, cx + 360, top + 10], fill=(210, 215, 225))
        d.rectangle([cx - 400, top + 60, cx - 330, top + 100], fill=(150, 155, 165)); d.rectangle([cx + 330, top + 60, cx + 400, top + 100], fill=(150, 155, 165))
        wy = bot - 20 - (bot - top - 60) * lvl
        d.rectangle([cx - 310, wy, cx + 310, bot - 20], fill=(70, 150, 220))
        crust = 1 - lvl
        d.rectangle([cx - 310, bot - 20 - 30 * crust, cx + 310, bot - 20], fill=(250, 250, 250))
        for k in range(12):
            fx = cx - 300 + k * 55; fl = 40 + 15 * math.sin(t * 20 + k)
            d.polygon([(fx, bot + 60), (fx + 20, bot + 60 - fl), (fx + 40, bot + 60)], fill=(80, 140, 255))
        d.rectangle([cx - 420, bot + 60, cx + 420, bot + 110], fill=(60, 60, 66))
        st = Image.new('RGBA', (W, H), (0, 0, 0, 0)); sd = ImageDraw.Draw(st)
        for k in range(8):
            u = (t * 0.4 + k / 8) % 1; x = cx - 200 + k * 55 + 30 * math.sin(t + k); y = top - u * 400
            sd.ellipse([x - 50, y - 50, x + 50, y + 50], fill=(230, 230, 230, int(140 * (1 - u))))
        img.alpha_composite(st.filter(ImageFilter.GaussianBlur(14))); d = ImageDraw.Draw(img)
        if crust > 0.6: d.rounded_rectangle([300, 1460, 780, 1540], 36, fill=WHITE); txt_c(d, (540, 1465), 'costra blanca', font(48), (30, 30, 40))
        mascot_corner(img, f, t, 0.3)
    elif i == 6:
        img = sky((40, 90, 170), (10, 30, 80)); d = ImageDraw.Draw(img)
        d.rectangle([0, 1150, W, H], fill=SEA2)
        n = int(30 + 400 * p); rnd = random.Random(3)
        for k in range(n):
            x, y = rnd.randint(10, W - 10), rnd.randint(1170, H - 10); d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=WHITE)
        for k in range(5):
            u = (t * 0.8 + k / 5) % 1; x = -50 + u * 600; d.line([(x, 1100 - k * 8), (x + 80, 1140 - k * 8)], fill=(110, 190, 255), width=16)
        yrs = int(500 * ease(p))
        d.rounded_rectangle([170, 600, 910, 900], 50, fill=(10, 20, 50), outline=YEL, width=5)
        txt_c(d, (W / 2, 620), f'{yrs}', font(150), YEL); txt_c(d, (W / 2, 800), 'millones de años', font(52), WHITE)
    elif i == 7:
        img = sky((10, 40, 90), (2, 8, 25)); d = ImageDraw.Draw(img)
        d.rectangle([0, 1500, W, H], fill=(40, 35, 40))
        for vx in (300, 760):
            d.polygon([(vx - 120, 1500), (vx - 40, 1150), (vx + 40, 1150), (vx + 120, 1500)], fill=(60, 50, 55))
            pl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); pd = ImageDraw.Draw(pl)
            for k in range(10):
                u = (t * 0.6 + k / 10) % 1; y = 1150 - u * 650; r = 30 + u * 90
                pd.ellipse([vx - r + 30 * math.sin(t + k), y - r, vx + r + 30 * math.sin(t + k), y + r], fill=(255, int(150 - 100 * u), 60, int(170 * (1 - u))))
            img.alpha_composite(pl.filter(ImageFilter.GaussianBlur(12))); d = ImageDraw.Draw(img)
            rnd = random.Random(vx)
            for k in range(25):
                u = (t * 0.5 + rnd.random()) % 1; x = vx + rnd.uniform(-120, 120) * u; y = 1150 - u * 650; d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=WHITE)
        d.rounded_rectangle([260, 400, 820, 490], 40, fill=(20, 20, 30), outline=(255, 140, 60), width=4); txt_c(d, (540, 410), 'agua ardiendo', font(56), (255, 160, 80))
    elif i == 8:
        img = sky((250, 230, 200), (220, 190, 150)); d = ImageDraw.Draw(img)
        d.rectangle([0, 1300, W, H], fill=(150, 100, 65))
        # jarra de 1 litro
        d.rounded_rectangle([140, 820, 500, 1300], 30, fill=(200, 230, 250), outline=(140, 170, 200), width=6)
        d.rectangle([150, 900, 490, 1290], fill=(80, 160, 230)); d.arc([460, 900, 600, 1150], 270, 90, fill=(140, 170, 200), width=16)
        txt_c(d, (320, 840), '1 L', font(54), (40, 60, 90))
        # báscula
        g = 35 * ease((lt - 0.6) / 2.2)
        d.rounded_rectangle([600, 1220, 980, 1300], 20, fill=(200, 205, 215)); d.rounded_rectangle([700, 1240, 880, 1285], 10, fill=(30, 40, 30))
        txt_c(d, (790, 1240), f'{g:.0f} g', font(36), (120, 255, 120))
        hgt = 160 * g / 35; d.polygon([(640, 1220), (940, 1220), (790, 1220 - hgt)], fill=WHITE)
        shaker(d, 860, 820, 0.9)
        d.rounded_rectangle([600, 420, 980, 600], 40, fill=(30, 30, 40)); txt_c(d, (790, 430), f'{g:.0f} g', font(110), YEL)
    elif i == 9:
        img = SKY.copy(); d = ImageDraw.Draw(img)
        sun(img, 880, 500, 60); d = ImageDraw.Draw(img)
        d.rectangle([0, 1450, W, H], fill=(130, 95, 60))
        k = ease(lt / 3.0)
        bx0, bx1, btop = 380, 640, 650
        sy = 1450 - (1450 - btop) * k
        d.rectangle([0, sy, W, 1450], fill=(245, 245, 250))
        d.rectangle([bx0, btop, bx1, 1450], fill=(120, 140, 170))
        for fl in range(40):
            y = btop + 10 + fl * ((1450 - btop - 20) / 40)
            for c in range(4): d.rectangle([bx0 + 18 + c * 60, y, bx0 + 50 + c * 60, y + 10], fill=(220, 235, 255))
        lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ld = ImageDraw.Draw(lay); ld.rectangle([bx0, sy, bx1, 1450], fill=(250, 250, 252, 120))
        img.alpha_composite(lay); d = ImageDraw.Draw(img)
        if k > 0.2: d.rounded_rectangle([60, sy + 20, 300, sy + 90], 30, fill=(30, 30, 40)); txt_c(d, (180, sy + 26), 'SAL', font(48), WHITE)
        d.line([(720, btop), (720, 1450)], fill=YEL, width=6); d.line([(700, btop), (740, btop)], fill=YEL, width=6)
        d.rounded_rectangle([760, 900, 1040, 1000], 30, fill=(30, 30, 40)); txt_c(d, (900, 910), '150 m', font(70), YEL)
        if lt > 3.5: d.rounded_rectangle([90, 400, 990, 500], 40, fill=(30, 30, 40)); txt_c(d, (540, 410), 'edificio de 40 plantas', font(54), WHITE)
    elif i == 11:
        img = sky((40, 34, 90), (8, 8, 20)); d = ImageDraw.Draw(img)
        px0, py0 = 330, 420
        d.rounded_rectangle([px0, py0, px0 + 420, py0 + 820], 50, fill=(20, 20, 26), outline=(150, 150, 160), width=8)
        mini = landscape(t, labels=False).crop((0, 450, W, H)).resize((380, 520))
        img.paste(mini.convert('RGB'), (px0 + 20, py0 + 150)); d = ImageDraw.Draw(img)
        if lt > 1.6:
            s = 1 + 0.05 * math.sin(t * 10); w2 = int(380 * s)
            d.rounded_rectangle([W / 2 - w2, 1300, W / 2 + w2, 1480], 50, fill=YEL)
            txt_c(d, (W / 2, 1305), 'COMENTA', font(56), (20, 20, 20)); txt_c(d, (W / 2, 1365), 'VIRAL', font(88), RED)
    else:
        img = SKY.copy(); d = ImageDraw.Draw(img)
        sun(img, 860, 520); d = ImageDraw.Draw(img)
        d.rectangle([0, 1250, W, H], fill=SEA); d.rectangle([0, 1650, W, H], fill=SAND)
        m = stand(f, t, 0.5); mx = 300; my = 1250 - int(m.height * 0.45) + int(10 * math.sin(t * 3))
        img.alpha_composite(m, (mx, my))
        d = ImageDraw.Draw(img)
        d.rectangle([0, 1250 + 120, W, 1650], fill=SEA)  # agua sobre las piernas
        rr = (mx + m.width / 2, my + m.height * 0.55)
        d.ellipse([rr[0] - 190, rr[1] - 40, rr[0] + 190, rr[1] + 70], outline=(255, 90, 90), width=40)  # flotador
        for k in range(8):
            wx = k * 140 + 30 * math.sin(t * 2 + k); d.arc([wx, 1235, wx + 110, 1270], 200, 340, fill=(200, 230, 255), width=5)
        cx, cy = W / 2, 560; dx = (lt * 160) % 140
        d.polygon([(cx - 130 + dx, cy + 10), (cx + 110 + dx, cy - 90), (cx + 10 + dx, cy + 90), (cx - 20 + dx, cy + 30)], fill=WHITE)
        d.line([(cx - 20 + dx, cy + 30), (cx + 110 + dx, cy - 90)], fill=(160, 160, 170), width=6)
        txt_c(d, (W / 2, 700), 'ENVÍASELO A ESE AMIGO', font(58), YEL, 6)
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
                              '-shortest', '-movflags', '+faststart', 'mar-salado.mp4'], stdin=subprocess.PIPE)
        for f in range(n):
            p.stdin.write(frame(f).tobytes())
            if f % 300 == 0: print(f'{f}/{n} cuadros')
        p.stdin.close(); p.wait(); print('Listo: mar-salado.mp4')
