"""Base común (subtítulos, voz, mascota que habla, fondos y ayudas de dibujo). La usa render.py; no se ejecuta sola."""
import numpy as np, cv2, json, math, os, subprocess, sys, wave, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
def buscar_fuente():
    for f in ('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',
              os.path.join(AQUI, '..', 'Poppins-Bold.ttf'),
              r'C:\Windows\Fonts\Poppins-Bold.ttf',
              os.path.expandvars(r'%LOCALAPPDATA%\Microsoft\Windows\Fonts\Poppins-Bold.ttf'),
              r'C:\Windows\Fonts\arialbd.ttf',
              '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.isfile(f): return f
    sys.exit('No encontré una fuente en negrita. Instala Poppins Bold (Google Fonts).')
F_B = buscar_fuente()
_fc = {}
def font(s):
    if s not in _fc: _fc[s] = ImageFont.truetype(F_B, s)
    return _fc[s]
YEL = (255, 210, 63); RED = (230, 30, 45); WHITE = (255, 255, 255); PINK = (255, 120, 170); CYAN = (110, 200, 255)

lines = open(os.path.join(AQUI, '..', 'guion.txt'), encoding='utf-8').read().strip().split('\n')
durs = json.load(open('durs.json'))
starts = np.cumsum([0] + durs[:-1]).tolist()
TOTAL = sum(durs)
def L(i, off=0.0): return starts[i] + off
def scene(t):
    for i in range(len(starts) - 1, -1, -1):
        if t >= starts[i]: return i, t - starts[i]
    return 0, t

words = []
for i, ln in enumerate(lines):
    ws = ln.split(); tot = sum(len(w) + 1 for w in ws); t = starts[i]; span = durs[i] - 0.3
    for w in ws:
        d = span * (len(w) + 1) / tot; words.append((t, t + d, w, i)); t += d
chunks = []; cur = []
for wd in words:
    cur.append(wd)
    if len(cur) >= 4 or wd[2][-1] in '.,?!:' or wd is words[-1]:
        chunks.append(cur); cur = []

wf = wave.open('voice.wav'); sr = wf.getframerate(); raw = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
spf = sr // FPS; nfr = len(raw) // spf
rms = np.array([np.sqrt(np.mean(raw[k*spf:(k+1)*spf]**2)) for k in range(nfr)])
rms = rms / (np.percentile(rms, 95) + 1e-6)
def mouth_open(f):
    if f >= len(rms): return 0
    return float(np.clip((rms[f] - 0.12) / 0.7, 0, 1))

# ---------- mascot ----------
src = Image.open('mascot_clean.png').convert('RGBA'); A = np.array(src)
mx0, my0, mx1, my1 = 545, 333, 656, 392
patch = A[my0:my1, mx0:mx1].copy()
diff = np.abs(patch[..., :3].astype(int) - np.array([235, 170, 110])).sum(-1)
mmask = cv2.morphologyEx((diff > 120).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
patch[..., 3] = np.minimum(patch[..., 3], mmask)
bm = np.zeros(A.shape[:2], np.uint8); bm[my0:my1, mx0:mx1] = cv2.dilate(mmask, np.ones((7, 7), np.uint8))
cl = A.copy(); inp = cv2.inpaint(cv2.cvtColor(A[..., :3], cv2.COLOR_RGB2BGR), bm, 7, cv2.INPAINT_TELEA)
cl[..., :3] = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
CLOSED = Image.fromarray(cl); d = ImageDraw.Draw(CLOSED); d.arc([566, 335, 636, 370], 20, 160, fill=(90, 35, 25), width=6)
BLINK = Image.new('RGBA', src.size, (0, 0, 0, 0)); d = ImageDraw.Draw(BLINK)
for x0, x1 in ((500, 570), (635, 703)):
    d.rectangle([x0 - 3, 258, x1 + 3, 322], fill=(232, 168, 108, 255)); d.line([(x0, 300), (x1, 300)], fill=(60, 30, 20), width=7)
PATCH = Image.fromarray(patch)
_sc = {}
def stand(f, t, s, talk=True):
    """mascot image at scale s with lip sync and blink"""
    key = s
    if key not in _sc:
        _sc[key] = (CLOSED.resize((int(src.width*s), int(src.height*s)), Image.LANCZOS), BLINK.resize((int(src.width*s), int(src.height*s)), Image.LANCZOS),
                    PATCH.resize((max(1, int(PATCH.width*s)), max(1, int(PATCH.height*s))), Image.LANCZOS))
    b, bl, pt = _sc[key]; im = b.copy()
    mo = mouth_open(f) if talk else 0
    if mo > 0.05:
        ph = max(2, int(pt.height * (0.3 + 0.7 * mo))); im.alpha_composite(pt.resize((pt.width, ph), Image.LANCZOS), (int(mx0*s), int(my0*s)))
    if (t % 3.7) < 0.13: im.alpha_composite(bl)
    return im
# sleeping head
hs = CLOSED.copy(); hs.alpha_composite(BLINK)
HEAD = hs.crop((400, 0, 800, 470)).rotate(90, expand=True, resample=Image.BICUBIC)  # 470x400, lying, cap to the left
HEAD = HEAD.resize((int(HEAD.width * 0.62), int(HEAD.height * 0.62)), Image.LANCZOS)

# ---------- backgrounds ----------
def grad(c0, c1, cy=0.4):
    y, x = np.mgrid[0:H, 0:W]
    r = np.clip(np.sqrt((x - W/2)**2 + (y - H*cy)**2) / (H * 0.75), 0, 1)[..., None]
    return Image.fromarray((np.array(c0) * (1 - r) + np.array(c1) * r).astype(np.uint8)).convert('RGBA')
BG_NIGHT = grad((40, 34, 90), (8, 8, 20))
BG_DARK = grad((55, 18, 30), (6, 6, 10))
BG_SKY = grad((30, 40, 100), (5, 8, 25), 0.3)
d = ImageDraw.Draw(BG_SKY); rnd = random.Random(3)
for _ in range(90):
    x, y, r = rnd.randint(0, W), rnd.randint(0, 1100), rnd.choice([1, 2, 2, 3]); d.ellipse([x-r, y-r, x+r, y+r], fill=(255, 255, 255, rnd.randint(90, 230)))

def room(bg):
    im = bg.copy(); d = ImageDraw.Draw(im)
    # window with moon
    wx, wy = 60, 380
    d.rounded_rectangle([wx, wy, wx + 300, wy + 360], 14, fill=(20, 26, 60), outline=(120, 90, 60), width=14)
    d.ellipse([wx + 150, wy + 60, wx + 250, wy + 160], fill=(245, 240, 210))
    d.ellipse([wx + 175, wy + 50, wx + 275, wy + 150], fill=(20, 26, 60))
    d.line([(wx + 150, wy), (wx + 150, wy + 360)], fill=(120, 90, 60), width=10); d.line([(wx, wy + 180), (wx + 300, wy + 180)], fill=(120, 90, 60), width=10)
    # lamp glow
    gl = Image.new('RGBA', (W, H), (0, 0, 0, 0)); g = ImageDraw.Draw(gl); g.ellipse([820, 840, 1220, 1240], fill=(255, 180, 90, 90))
    im.alpha_composite(gl.filter(ImageFilter.GaussianBlur(60))); d = ImageDraw.Draw(im)
    d.polygon([(980, 1000), (1070, 1000), (1050, 1060), (1000, 1060)], fill=(255, 200, 120)); d.rectangle([1020, 1060, 1028, 1520], fill=(90, 70, 50))
    d.rectangle([0, 1520, W, H], fill=(25, 20, 30))
    return im
SLEEP = Image.open('sleep_clean.png').convert('RGBA') if os.path.isfile('sleep_clean.png') else Image.new('RGBA', (2, 2)); SLEEP = SLEEP.resize((int(SLEEP.width * 0.72), int(SLEEP.height * 0.72)), Image.LANCZOS)
def bed(im, dark=False):
    d = ImageDraw.Draw(im)
    x0, x1, y = 90, 990, 1180
    d.rounded_rectangle([x0 - 20, y - 160, x0 + 30, y + 300], 14, fill=(110, 75, 50))
    d.rounded_rectangle([x0, y + 120, x1, y + 260], 20, fill=(110, 75, 50))
    d.rounded_rectangle([x0 + 10, y + 20, x1 - 10, y + 150], 30, fill=(70, 90, 170) if not dark else (60, 50, 80))
    im.alpha_composite(SLEEP, (110, y + 40 - 750))
BED_ROOM = room(BG_NIGHT); bed(BED_ROOM)
BED_DARK = room(BG_DARK); bed(BED_DARK, True)
HEADPOS = (330, 900)

def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def txt_c(d, xy, s, f, fill=WHITE, stroke=0, sf=(0, 0, 0)):
    w = d.textlength(s, font=f); d.text((xy[0] - w / 2, xy[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf)
def card(img, box, edge=(110, 200, 255)):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    d.rounded_rectangle(box, 28, fill=(14, 16, 32, 225), outline=edge + (255,), width=5); img.alpha_composite(lay); return ImageDraw.Draw(img)
def glow(img, cx, cy, r, col, a=120, blur=30):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); ImageDraw.Draw(lay).ellipse([cx - r, cy - r, cx + r, cy + r], fill=col + (a,))
    img.alpha_composite(lay.filter(ImageFilter.GaussianBlur(blur)))

def _mk_brain():
    w, h = 520, 380
    m = Image.new('L', (w, h), 0); dm = ImageDraw.Draw(m)
    for ox, oy, rx, ry in ((170, 170, 160, 140), (330, 150, 170, 140), (260, 240, 230, 120), (120, 250, 100, 90)):
        dm.ellipse([ox - rx + 10, oy - ry + 10, ox + rx - 10, oy + ry - 10], fill=255)
    m = m.filter(ImageFilter.GaussianBlur(3)).point(lambda v: 255 if v > 128 else 0)
    col = Image.new('RGBA', (w, h), (242, 165, 185, 255)); dc = ImageDraw.Draw(col)
    rnd = random.Random(7)
    for k in range(16):
        y0 = 30 + k * 22; pts = [(x, y0 + 14 * math.sin(x / 26 + rnd.random() * 6) + 6 * math.sin(x / 9)) for x in range(0, w, 6)]
        dc.line(pts, fill=(205, 115, 140, 255), width=5)
    dc.line([(w / 2 + 10, 20), (w / 2 - 10, h - 40)], fill=(190, 100, 125, 255), width=8)
    out = Image.new('RGBA', (w, h), (0, 0, 0, 0)); out.paste(col, (0, 0), m)
    edge = m.filter(ImageFilter.FIND_EDGES); ol = Image.new('RGBA', (w, h), (170, 80, 105, 255)); out.paste(ol, (0, 0), edge.filter(ImageFilter.MaxFilter(5)))
    return out
BRAIN = _mk_brain(); _bc = {}
def brain(img, cx, cy, s, emo=0.0, logic=1.0, t=0):
    if s not in _bc: _bc[s] = BRAIN.resize((int(BRAIN.width * s * 0.8), int(BRAIN.height * s * 0.8)), Image.LANCZOS)
    b = _bc[s]
    if logic < 1:
        glow(img, int(cx + 60 * s), int(cy - 50 * s), int(120 * s), (60, 120, 255), int(140 * (1 - logic)), 25)
    img.alpha_composite(b, (int(cx - b.width / 2), int(cy - b.height / 2)))
    if emo > 0:
        pr = (60 + 10 * math.sin(t * 8)) * s
        glow(img, int(cx - 20 * s), int(cy + 50 * s), int(pr * 1.5), (255, 50, 80), int(210 * emo), 16)

FC = font(64)
def caption(img, t):
    d = ImageDraw.Draw(img)
    for ch in chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is chunks[-1] and t >= ch[0][0]):
            line = ' '.join(w[2] for w in ch); tw = d.textlength(line, font=FC)
            ff = FC if tw < W - 120 else font(int(64 * (W - 120) / tw))
            tw = d.textlength(line, font=ff); x = (W - tw) / 2
            for (a, b, w, _) in ch:
                d.text((x, 230), w, font=ff, fill=YEL if a <= t < b + 0.02 else WHITE, stroke_width=6, stroke_fill=(0, 0, 0))
                x += d.textlength(w + ' ', font=ff)
            return

def zzz(img, t, x, y):
    d = ImageDraw.Draw(img)
    for k in range(3):
        u = (t * 0.6 + k / 3) % 1
        d.text((x + u * 120 + k * 10, y - u * 220), 'Z', font=font(int(40 + 40 * u)), fill=(200, 210, 255, int(255 * (1 - u))))

def frame(f):
    t = f / FPS; i, lt = scene(t); dur = durs[i]
    if i in (0, 3, 12):
        img = BED_ROOM.copy()
        d = ImageDraw.Draw(img)
        if i == 0:
            # dream bubble then nightmare bubble
            nm = lt > 1.4
            bx, by = 800, 560
            for k, r in enumerate((14, 22)):
                d.ellipse([700 + k * 30 - r, 800 - k * 60 - r, 700 + k * 30 + r, 800 - k * 60 + r], fill=(60, 50, 80) if nm else (240, 240, 255))
            d.ellipse([bx - 230, by - 150, bx + 230, by + 150], fill=(60, 50, 80) if nm else (240, 240, 255))
            if not nm:
                for k in range(5):
                    sx, sy = bx - 150 + k * 75, by - 40 + 25 * math.sin(t * 3 + k)
                    d.regular_polygon((sx, sy, 28), 5, rotation=t * 60, fill=YEL)
                txt_c(d, (bx, by + 50), 'SUEÑOS', font(54), (40, 40, 80))
            else:
                if int(t * 8) % 3: d.polygon([(bx - 20, by - 120), (bx + 40, by - 120), (bx + 5, by - 10), (bx + 60, by - 10), (bx - 40, by + 120), (bx - 5, by + 20), (bx - 60, by + 20)], fill=YEL)
                txt_c(d, (bx + 140, by - 40), '¿?', font(90), RED)
        if i == 3:
            img2 = card(img, (300, 340, 1020, 660), (255, 120, 120)); d = img2
            txt_c(d, (660, 360), 'MÚSCULOS', font(64), WHITE)
            on = lt < 2.2
            sx = 560; d.rounded_rectangle([sx, 470, sx + 200, 560], 45, fill=(60, 200, 110) if on else (90, 90, 100))
            kx = sx + 155 if on else sx + 45; d.ellipse([kx - 38, 477, kx + 38, 553], fill=WHITE)
            txt_c(d, (660, 580), 'ENCENDIDOS' if on else 'APAGADOS', font(48), (60, 200, 110) if on else RED)
        if i == 12:
            bxx, byy = 800, 620
            brain(img, bxx, byy, 0.9, emo=0.8, logic=0.6, t=t)
            d = ImageDraw.Draw(img)
            txt_c(d, (W / 2, 1620), 'PRACTICANDO', font(90), YEL, 7)
        if i == 3 or i == 12:
            pass
    elif i in (1, 4):
        img = BG_NIGHT.copy(); d = ImageDraw.Draw(img)
        if i == 1:
            m = stand(f, t, 0.75); mx, my = (W - m.width) // 2, 900
            img.alpha_composite(m, (mx, my))
            brain(img, W // 2, 600, 0.9, emo=0.4, t=t)
            d = ImageDraw.Draw(img)
            if lt > 1.1:
                d.rounded_rectangle([240, 790, 840, 880], 40, fill=RED); txt_c(d, (W/2, 795), 'ENSAYANDO', font(64), WHITE)
            else:
                d.rounded_rectangle([240, 790, 840, 880], 40, fill=(70, 70, 90)); txt_c(d, (W/2, 795), '¿DESCANSA?', font(60), WHITE)
        else:
            k = ease((lt - 0.3) / 1.2); k2 = ease((lt - 2.0) / 1.2)
            brain(img, W // 2, 800, 1.6, emo=k, logic=1 - 0.8 * k2, t=t)
            d = ImageDraw.Draw(img)
            # meters
            for j, (lab, val, col) in enumerate((('EMOCIONES', k, (255, 70, 100)), ('LÓGICA', 1 - 0.8 * k2, CYAN))):
                y = 1240 + j * 170; txt_c(d, (W/2, y), lab, font(46), col)
                d.rounded_rectangle([190, y + 70, 890, y + 110], 20, fill=(40, 40, 60))
                d.rounded_rectangle([190, y + 70, 190 + int(700 * max(0.05, val)), y + 110], 20, fill=col)
            m = stand(f, t, 0.35); img.alpha_composite(m, (W - m.width - 10, H - m.height - 20))
    elif i == 2:
        img = BG_NIGHT.copy(); d = ImageDraw.Draw(img)
        # sleep cycle graph
        x0, x1, ytop, ybot = 90, 990, 700, 1150
        prog = ease(lt / (dur * 0.85))
        pts = []
        for k in range(300):
            u = k / 299; x = x0 + (x1 - x0) * u
            ph = (u * 4) % 1; depth = 0.5 - 0.5 * math.cos(ph * 2 * math.pi)
            pts.append((x, ytop + 60 + (ybot - ytop - 60) * depth))
        n = int(300 * prog)
        if n > 1: d.line(pts[:n], fill=(150, 170, 255), width=10, joint='curve')
        for c in range(4):
            u = c / 4 + 0.001; px = x0 + (x1 - x0) * (c + 1) / 4
            if prog >= (c + 1) / 4 - 0.02:
                glow(img, int(px), ytop + 60, 50, (255, 210, 63), 160, 15); d = ImageDraw.Draw(img)
                txt_c(d, (px, ytop - 20), 'REM', font(40), YEL)
        d.line([(x0, ybot + 40), (x0 + (x1 - x0) / 4, ybot + 40)], fill=WHITE, width=4)
        d.rounded_rectangle([x0 + 20, ybot + 70, x0 + 220, ybot + 140], 18, fill=(30, 30, 60), outline=WHITE, width=3)
        txt_c(d, (x0 + 120, ybot + 78), '90 min', font(42), WHITE)
        if lt > dur * 0.6:
            for k in range(6):
                sx, sy = 200 + k * 140, 520 + 20 * math.sin(t * 4 + k)
                d.regular_polygon((sx, sy, 26), 5, rotation=t * 50, fill=YEL)
        m = stand(f, t, 0.4); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 20))
    elif i == 5:
        img = BG_SKY.copy(); d = ImageDraw.Draw(img)
        d.ellipse([720, 420, 920, 620], fill=(245, 240, 210)); glow(img, 820, 520, 160, (245, 240, 210), 60, 40); d = ImageDraw.Draw(img)
        for k in range(9):
            hx = k * 130 - 20; hh = 300 + (k * 53) % 220
            d.rectangle([hx, H - hh, hx + 110, H], fill=(12, 14, 30))
            for wy in range(H - hh + 40, H - 60, 90):
                if (k + wy // 90) % 3 == 0: d.rectangle([hx + 40, wy, hx + 70, wy + 34], fill=(255, 200, 110))
        m = stand(f, t, 0.5, talk=True).rotate(-80, expand=True, resample=Image.BICUBIC)
        px = -m.width + (W + m.width * 1.2) * (lt / dur); py = 900 + 60 * math.sin(t * 2)
        img.alpha_composite(m, (int(px), int(py)))
        if lt > dur * 0.45:
            # ghost friend
            gx, gy = 780, 1000 + 20 * math.sin(t * 3)
            gl = Image.new('RGBA', img.size, (0, 0, 0, 0)); g = ImageDraw.Draw(gl)
            g.ellipse([gx - 70, gy - 70, gx + 70, gy + 70], fill=(220, 230, 255, 140)); g.rounded_rectangle([gx - 80, gy + 40, gx + 80, gy + 240], 60, fill=(220, 230, 255, 120))
            img.alpha_composite(gl); d = ImageDraw.Draw(img)
            d.rounded_rectangle([gx - 170, gy - 230, gx + 170, gy - 120], 30, fill=WHITE); txt_c(d, (gx, gy - 220), '¡Hola!', font(60), (40, 40, 80))
        txt_c(d, (W/2, 420), '¡NORMAL!', font(100), YEL, 8) if lt > dur * 0.75 else None
    elif i == 6:
        img = BG_NIGHT.copy(); d = card(img, (110, 420, 970, 900), (255, 150, 200))
        txt_c(d, (W/2, 450), 'SOÑAR =', font(72), WHITE)
        txt_c(d, (W/2, 550), 'TERAPIA', font(130), PINK)
        txt_c(d, (W/2, 710), 'DE NOCHE', font(80), WHITE)
        hx, hy, s = W/2, 1050, 1 + 0.08 * math.sin(t * 6)
        d.ellipse([hx - 90 * s, hy - 60 * s, hx, hy + 30 * s], fill=RED); d.ellipse([hx, hy - 60 * s, hx + 90 * s, hy + 30 * s], fill=RED)
        d.polygon([(hx - 86 * s, hy), (hx + 86 * s, hy), (hx, hy + 110 * s)], fill=RED)
        m = stand(f, t, 0.45); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 20))
    elif i == 7:
        img = BG_NIGHT.copy(); d = ImageDraw.Draw(img)
        # stress gauge
        cx, cy, R = W/2, 820, 260
        d.arc([cx - R, cy - R, cx + R, cy + R], 180, 240, fill=(80, 200, 120), width=40)
        d.arc([cx - R, cy - R, cx + R, cy + R], 240, 300, fill=(240, 200, 60), width=40)
        d.arc([cx - R, cy - R, cx + R, cy + R], 300, 360, fill=RED, width=40)
        v = 1 - 0.8 * ease((lt - 0.5) / 2.0); a = math.radians(180 + 180 * v)
        d.line([(cx, cy), (cx + math.cos(a) * (R - 50), cy + math.sin(a) * (R - 50))], fill=WHITE, width=14); d.ellipse([cx - 26, cy - 26, cx + 26, cy + 26], fill=WHITE)
        txt_c(d, (cx, cy + 50), 'ESTRÉS', font(56), WHITE)
        if lt > dur * 0.45:
            d = card(img, (230, 1000, 850, 1300), (255, 210, 63))
            # memory photo
            d.rectangle([300, 1030, 780, 1230], fill=(60, 70, 100))
            k = ease((lt - dur * 0.55) / 1.5)
            for j in range(4):
                cxx = 360 + j * 120; d.ellipse([cxx - 60, 1060, cxx + 60, 1150], fill=(int(90 + 120 * k), int(90 + 120 * k), int(110 + 120 * k)))
            if k < 0.6:
                for j in range(5): d.line([(330 + j * 100, 1160), (310 + j * 100, 1220)], fill=CYAN, width=6)
            txt_c(d, (540, 1240), 'lo que te dolió', font(40), WHITE)
        m = stand(f, t, 0.35); img.alpha_composite(m, (W - m.width, H - m.height - 20))
    elif i == 8:
        img = BG_NIGHT.copy(); d = ImageDraw.Draw(img)
        px0, py0 = 330, 420
        d.rounded_rectangle([px0, py0, px0 + 420, py0 + 820], 50, fill=(20, 20, 26), outline=(150, 150, 160), width=8)
        mini = BED_ROOM.crop((0, 400, W, 1700)).resize((380, 457)); d.rounded_rectangle([px0 + 20, py0 + 40, px0 + 400, py0 + 780], 30, fill=(30, 30, 50))
        img.paste(mini.convert('RGB'), (px0 + 20, py0 + 180)); d = ImageDraw.Draw(img)
        if lt > 1.3:
            s = 1 + 0.05 * math.sin(t * 10); w2 = int(380 * s)
            d.rounded_rectangle([W/2 - w2, 1300, W/2 + w2, 1480], 50, fill=YEL)
            txt_c(d, (W/2, 1305), 'COMENTA', font(56), (20, 20, 20)); txt_c(d, (W/2, 1365), 'VIRAL', font(88), RED)
    elif i == 9:
        img = BED_DARK.copy(); d = ImageDraw.Draw(img)
        cx, cy = 560, 640
        for ox, r in ((-140, 120), (0, 160), (150, 120)): d.ellipse([cx + ox - r, cy - r, cx + ox + r, cy + r], fill=(45, 40, 60))
        if int(t * 7) % 3 == 0: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, 40)))
        d = ImageDraw.Draw(img); txt_c(d, (cx, cy - 60), 'PESADILLAS', font(70), RED, 6)
    elif i in (10, 11):
        img = BG_DARK.copy(); d = ImageDraw.Draw(img)
        d.rectangle([0, 1500, W, H], fill=(20, 12, 16))
        # exit door
        d.rectangle([860, 980, 1000, 1500], fill=(255, 240, 200)); glow(img, 930, 1240, 200, (255, 220, 150), 90, 40); d = ImageDraw.Draw(img)
        bobv = abs(math.sin(t * 9)) * 30
        m = stand(f, t, 0.45).rotate(-6 if i == 10 else 6 * math.sin(t * 9), resample=Image.BICUBIC, expand=True)
        prog = (lt / dur)
        mxp = int(80 + 380 * prog) if i == 10 else int(300 + 60 * math.sin(t * 2))
        img.alpha_composite(m, (mxp, int(1500 - m.height + 20 - bobv)))
        if i == 10:
            sx = mxp - 260 + 40 * math.sin(t * 4)
            d.ellipse([sx - 130, 1100, sx + 130, 1360], fill=(10, 8, 12)); d.rectangle([sx - 130, 1230, sx + 130, 1500], fill=(10, 8, 12))
            d.ellipse([sx - 60, 1180, sx - 25, 1215], fill=RED); d.ellipse([sx + 25, 1180, sx + 60, 1215], fill=RED)
            d.rounded_rectangle([290, 420, 790, 520], 40, fill=(40, 40, 60), outline=YEL, width=4); txt_c(d, (W/2, 430), 'SIMULACRO', font(64), YEL)
        else:
            n = min(5, 1 + int(lt / (dur / 5)))
            d.rounded_rectangle([340, 420, 740, 520], 40, fill=(40, 40, 60), outline=YEL, width=4); txt_c(d, (W/2, 430), f'ensayo {n}', font(64), YEL)
            cx, cy, R = W/2, 760, 150
            d.arc([cx - R, cy - R, cx + R, cy + R], 180, 360, fill=(70, 70, 80), width=30)
            v = min(1, lt / 1.5); d.arc([cx - R, cy - R, cx + R, cy + R], 180, 180 + 170 * v, fill=RED, width=30)
            txt_c(d, (cx, cy + 10), 'ESTRÉS', font(44), WHITE)
    else:
        img = BG_NIGHT.copy(); d = ImageDraw.Draw(img)
        m = stand(f, t, 0.7); img.alpha_composite(m, ((W - m.width) // 2, H - m.height - 20))
        cx, cy = W/2, 560; dx = (lt * 160) % 140
        d.polygon([(cx - 130 + dx, cy + 10), (cx + 110 + dx, cy - 90), (cx + 10 + dx, cy + 90), (cx - 20 + dx, cy + 30)], fill=WHITE)
        d.line([(cx - 20 + dx, cy + 30), (cx + 110 + dx, cy - 90)], fill=(160, 160, 170), width=6)
        txt_c(d, (W/2, 700), 'ENVÍASELO A ESE AMIGO', font(58), YEL, 6)
    # quick fade at scene start
    if lt < 0.12 and i > 0:
        img.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * (1 - lt / 0.12)))))
    caption(img, t)
    return img.convert('RGB')

