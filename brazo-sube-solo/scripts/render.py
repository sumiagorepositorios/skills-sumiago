"""Arma el reel 9:16 (1080x1920, 30 fps) "Tu brazo se mueve solo" con la mascota animada.
Uso (en la carpeta donde están voice.wav, durs.json y mascot_clean.png):
    python scripts/render.py test 2 6 12 20 26 38 44 47   -> test.jpg con cuadros de muestra
    python scripts/render.py full                          -> brazo-sube-solo.mp4
"""
import json, math, os, random, subprocess, sys, wave
import cv2, numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
AQUI = os.path.dirname(os.path.abspath(__file__))
SALIDA = 'brazo-sube-solo.mp4'

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
def font(s): return ImageFont.truetype(F_B, s)
YEL = (255, 210, 63); RED = (230, 30, 45); WHITE = (255, 255, 255)

# ---------- tiempos ----------
lines = open(os.path.join(AQUI, '..', 'guion.txt'), encoding='utf-8').read().strip().split('\n')
durs = json.load(open('durs.json'))
starts = np.cumsum([0] + durs[:-1]).tolist()
TOTAL = sum(durs) + 0.6
def L(i, off=0.0): return starts[i] + off

# subtítulos palabra por palabra (tiempo proporcional a las letras)
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
if cur: chunks.append(cur)

# ---------- volumen de la voz -> boca ----------
wf = wave.open('voice.wav'); sr = wf.getframerate()
raw = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
spf = sr // FPS; nfr = len(raw) // spf
rms = np.array([np.sqrt(np.mean(raw[k*spf:(k+1)*spf]**2)) for k in range(nfr)])
rms = rms / (np.percentile(rms, 95) + 1e-6)
def mouth_open(f):
    if f >= len(rms): return 0
    return float(np.clip((rms[f] - 0.12) / 0.7, 0, 1))

# ---------- capas de la mascota ----------
S = 0.9
src = Image.open('mascot_clean.png').convert('RGBA')
A = np.array(src)
poly = [(370,440),(465,445),(455,520),(425,660),(415,740),(405,870),(250,870),(250,700),(280,640)]  # brazo
pm = Image.new('L', src.size, 0); ImageDraw.Draw(pm).polygon(poly, fill=255)
pmn = np.array(pm) > 0
arm = A.copy(); arm[~pmn, 3] = 0
body = A.copy(); body[pmn, 3] = 0
PIV = (425, 485)  # hombro
mx0, my0, mx1, my1 = 545, 333, 656, 392  # boca
patch = A[my0:my1, mx0:mx1].copy()
diff = np.abs(patch[..., :3].astype(int) - np.array([235, 170, 110])).sum(-1)
mmask = cv2.morphologyEx((diff > 120).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
patch[..., 3] = np.minimum(patch[..., 3], mmask)
bm = np.zeros(A.shape[:2], np.uint8); bm[my0:my1, mx0:mx1] = cv2.dilate(mmask, np.ones((7, 7), np.uint8))
bodyc = body.copy()
inp = cv2.inpaint(cv2.cvtColor(body[..., :3], cv2.COLOR_RGB2BGR), bm, 7, cv2.INPAINT_TELEA)
bodyc[..., :3] = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
bc = Image.fromarray(bodyc); d = ImageDraw.Draw(bc)
d.arc([566, 335, 636, 370], 20, 160, fill=(90, 35, 25), width=6)
blink = Image.new('RGBA', src.size, (0, 0, 0, 0)); d = ImageDraw.Draw(blink)
for x0, x1 in ((500, 570), (635, 703)):
    d.rectangle([x0 - 3, 258, x1 + 3, 322], fill=(232, 168, 108, 255))
    d.line([(x0, 300), (x1, 300)], fill=(60, 30, 20), width=7)

def sc(img): return img.resize((int(img.width * S), int(img.height * S)), Image.LANCZOS)
BODY_C = sc(bc); ARM = sc(Image.fromarray(arm)); BLINK = sc(blink)
PATCH = sc(Image.fromarray(patch))
MW, MH = BODY_C.size
piv = (PIV[0] * S, PIV[1] * S)
mouth_xy = (mx0 * S, my0 * S)

# ---------- fondo y puerta ----------
def make_bg():
    y, x = np.mgrid[0:H, 0:W]
    r = np.sqrt((x - W/2)**2 + (y - H*0.45)**2) / (H * 0.7)
    c0 = np.array([70, 18, 26]); c1 = np.array([12, 10, 14])
    img = (c0 * (1 - r[..., None]).clip(0, 1) + c1 * r[..., None].clip(0, 1)).astype(np.uint8)
    bg = Image.fromarray(img).convert('RGBA'); d = ImageDraw.Draw(bg)
    for yy in []:  # fondo liso, sin puntos
        for xx in range(30, W, 60): d.ellipse([xx-2, yy-2, xx+2, yy+2], fill=(255, 255, 255, 18))
    return bg
OX0 = (W - MW) // 2 + 40; OY = 640
FX = OX0 + int(250 * S) - 46  # marco izquierdo
def door_layer():
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    x0, x1, top, bot = FX, FX + 800, 470, 1880
    oh, ow = bot - top - 30, x1 - x0 - 60
    g = np.linspace(0, 1, oh)[:, None]
    arr = np.zeros((oh, ow, 4), np.uint8)
    arr[..., 0] = (60 + 60 * g).astype(np.uint8); arr[..., 1] = (55 + 40 * g).astype(np.uint8); arr[..., 2] = (75 + 20 * g).astype(np.uint8); arr[..., 3] = 255
    lay.paste(Image.fromarray(arr), (x0 + 30, top + 30))
    wood = (120, 78, 45); dark = (80, 50, 28)
    for xa in (x0, x1 - 30):
        d.rectangle([xa, top, xa + 30, bot], fill=wood); d.line([(xa + 6, top), (xa + 6, bot)], fill=dark, width=3)
    d.rectangle([x0 - 10, top - 20, x1 + 10, top + 30], fill=wood); d.line([(x0 - 10, top + 30), (x1 + 10, top + 30)], fill=dark, width=4)
    d.rectangle([0, bot, W, H], fill=(30, 22, 20))
    return lay
BASE = make_bg(); BASE.alpha_composite(door_layer())

# ---------- ayudas ----------
def ease(t): t = max(0, min(1, t)); return t * t * (3 - 2 * t)
def seg(t, a, b): return ease((t - a) / (b - a)) if b > a else float(t >= a)
def txt_c(d, xy, s, f, fill=WHITE, stroke=0, sf=(0, 0, 0)):
    w = d.textlength(s, font=f); d.text((xy[0] - w / 2, xy[1]), s, font=f, fill=fill, stroke_width=stroke, stroke_fill=sf)
def rrect(d, box, r, fill, outline=None, width=0): d.rounded_rectangle(box, r, fill=fill, outline=outline, width=width)

TIMER_A = L(2, 4.0); TIMER_B = L(8, 2.0)
def timer_val(t): return 30 * (1 - (t - TIMER_A) / (TIMER_B - TIMER_A))

def arm_angle(t):
    a = 0.0
    if t < L(1): a = -60 * (seg(t, 0.8, 1.8) - seg(t, 2.6, 3.4))
    if TIMER_A <= t < TIMER_B: a = -3 + 1.5 * math.sin(t * 40)
    if t >= L(9, 1.4):
        a = -72 * seg(t, L(9, 1.4), L(9, 3.4))
        a += 3 * math.sin(t * 2.2) * seg(t, L(9, 3.4), L(9, 4))
        a = a * (1 - seg(t, L(12, 1.6), L(12, 2.8)))
    return a

def mascot_x(t): return OX0 + int(150 * seg(t, L(8, 2.1), L(8, 2.9)))

FONT_CAP = font(66); FONT_M = font(54); FONT_S = font(40)

def draw_caption(img, t):
    d = ImageDraw.Draw(img)
    for ch in chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is chunks[-1] and t >= ch[0][0]):
            line = ' '.join(w[2] for w in ch); tw = d.textlength(line, font=FONT_CAP)
            fsz = FONT_CAP if tw < W - 120 else font(int(66 * (W - 120) / tw))
            tw = d.textlength(line, font=fsz); x = (W - tw) / 2; y = 250
            for (a, b, w, _) in ch:
                d.text((x, y), w, font=fsz, fill=YEL if a <= t < b + 0.02 else WHITE, stroke_width=6, stroke_fill=(0, 0, 0))
                x += d.textlength(w + ' ', font=fsz)
            break

def card(img, box, alpha=1.0):
    lay = Image.new('RGBA', img.size, (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    rrect(d, box, 28, (20, 20, 24, int(225 * alpha)), outline=(230, 30, 45, int(255 * alpha)), width=5)
    img.alpha_composite(lay); return ImageDraw.Draw(img)

def overlays(img, t, mx):
    d = ImageDraw.Draw(img)
    if t < L(1):  # gancho
        txt_c(d, (W/2, 400), 'TU BRAZO SE', font(84), WHITE, 7)
        txt_c(d, (W/2, 495), 'MUEVE SOLO', font(96), YEL, 8)
    if L(1) <= t < L(2):  # paso 1 + flecha roja con borde blanco a la mano
        d = card(img, (60, 400, 520, 600))
        txt_c(d, (290, 420), 'PASO 1', FONT_S, YEL); txt_c(d, (290, 470), 'Brazo pegado', FONT_S); txt_c(d, (290, 520), 'dorso al marco', FONT_S)
        hx, hy = FX + 34, OY + int(800 * S); p = (math.sin(t * 6) + 1) * 10
        d.polygon([(hx + 30 + p, hy), (hx + 90 + p, hy - 35), (hx + 90 + p, hy + 35)], fill=RED, outline=WHITE)
    if TIMER_A - 0.3 <= t < TIMER_B + 0.6:  # temporizador 30 s
        v = max(0, timer_val(t)); cx, cy, R = 900, 1180, 105; last = v <= 5
        Rr = int(R * (1 + (0.06 * math.sin(t * 12) if last else 0)))
        d.ellipse([cx - Rr, cy - Rr, cx + Rr, cy + Rr], fill=(15, 15, 18, 235), outline=(70, 70, 75), width=10)
        d.arc([cx - Rr, cy - Rr, cx + Rr, cy + Rr], -90, -90 + 360 * v / 30, fill=RED if last else YEL, width=14)
        txt_c(d, (cx, cy - 60), f'{math.ceil(v)}', font(92), RED if last else WHITE)
        txt_c(d, (cx, cy + 38), 'seg', font(30), (200, 200, 200))
    if TIMER_A <= t < TIMER_B:  # flechas de empuje rojas con borde blanco
        hx, hy = FX + 34, OY + int(780 * S)
        for k in range(3):
            ph = (t * 1.5 + k / 3) % 1; x = hx + 150 - ph * 90; al = int(255 * (1 - ph))
            d.polygon([(x, hy - 30), (x - 50, hy), (x, hy + 30)], fill=(230, 30, 45, al), outline=(255, 255, 255, al))
        if L(2, 3.6) <= t < L(3): txt_c(d, (W/2, 420), '¡EMPUJA!', font(110), RED, 8)
    if L(3) <= t < L(4): txt_c(d, (W/2, 420), '???', font(130), YEL, 8)
    if L(4) <= t < L(5):  # 1915
        d = card(img, (70, 390, 560, 640), seg(t, L(4), L(4, 0.4)))
        txt_c(d, (315, 400), '1915', font(130), YEL); txt_c(d, (315, 565), 'Neurólogo alemán', FONT_S)
        if t > L(4, 3.0):
            d = card(img, (600, 420, 1010, 600))
            txt_c(d, (805, 440), '¿POR', font(64), WHITE); txt_c(d, (805, 510), 'QUÉ?', font(64), RED)
    if L(5, 1.6) <= t < L(6):  # 1 de cada 3
        d = card(img, (240, 390, 840, 640))
        for k in range(3):
            cx = 360 + k * 180; cy = 480; col = (90, 90, 95) if k == 2 else WHITE
            d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=col)
            d.rounded_rectangle([cx - 55, cy + 45, cx + 55, cy + 110], 30, fill=col)
            if k == 2 and t > L(5, 3.0):
                d.line([(cx - 60, cy - 50), (cx + 60, cy + 110)], fill=RED, width=14)
                d.line([(cx + 60, cy - 50), (cx - 60, cy + 110)], fill=RED, width=14)
    if L(6) <= t < L(7):  # truco
        d = card(img, (60, 380, 640, 660))
        txt_c(d, (350, 395), 'TRUCO', FONT_M, YEL)
        d.text((100, 470), '✕  No lo ayudes', font=FONT_S, fill=WHITE)
        d.text((100, 525), '✕  No lo frenes', font=FONT_S, fill=WHITE)
        d.text((100, 580), '✓  Solo míralo', font=FONT_S, fill=(120, 230, 120))
    if L(7) <= t < L(8):  # aguanta + sudor
        if int(t * 4) % 2 == 0: txt_c(d, (W/2, 420), '¡AGUANTA!', font(110), RED, 8)
        sx, sy = mx + int(760 * S), OY + int(230 * S) + int((t * 60) % 40)
        d.ellipse([sx - 14, sy, sx + 14, sy + 34], fill=(140, 200, 255)); d.polygon([(sx - 13, sy + 12), (sx, sy - 18), (sx + 13, sy + 12)], fill=(140, 200, 255))
    if L(8) <= t < L(9):  # 3, 2, 1, ¡YA!
        tl = t - L(8); cur = None
        for a, s in [(0, '3'), (0.55, '2'), (1.1, '1'), (1.75, '¡YA!')]:
            if tl >= a: cur = (a, s)
        if cur:
            k = 1 + 0.4 * (1 - seg(tl, cur[0], cur[0] + 0.25))
            txt_c(d, (W/2, 700 - 115 * k), cur[1], font(int(230 * k)), YEL if cur[1] != '¡YA!' else RED, 12)
        if tl > 2.4: txt_c(d, (W/2, 420), 'BRAZO FLOJO', font(90), WHITE, 7)
    if L(9, 1.2) <= t < L(12, 3):  # chispas en la mano
        ang = math.radians(arm_angle(t)); px, py = mx + piv[0], OY + piv[1]; hl = 360 * S
        hx = px + math.sin(ang) * hl; hy = py + math.cos(ang) * hl
        rnd = random.Random(int(t * 10))
        for k in range(10):
            ox, oy = rnd.uniform(-70, 70), rnd.uniform(-70, 70); r = rnd.uniform(4, 11)
            d.ellipse([hx + ox - r, hy + oy - r, hx + ox + r, hy + oy + r], fill=(255, 230, 120, 220))
    if L(9) <= t < L(10): txt_c(d, (W/2, 420), '¿LO NOTAS?', font(100), YEL, 8)
    if L(10) <= t < L(12):  # señal del cerebro al hombro
        bx, by = mx + int(600 * S), OY + int(150 * S); px, py = mx + piv[0], OY + piv[1]
        glow = Image.new('RGBA', img.size, (0, 0, 0, 0)); g = ImageDraw.Draw(glow)
        pr = 90 + 12 * math.sin(t * 8)
        g.ellipse([bx - pr, by - pr, bx + pr, by + pr], fill=(255, 70, 160, 120))
        g.ellipse([bx - 50, by - 50, bx + 50, by + 50], fill=(255, 140, 210, 200))
        g.line([(bx, by), (bx - 60, by + 230), (px, py)], fill=(120, 220, 255, 230), width=10)
        img.alpha_composite(glow.filter(ImageFilter.GaussianBlur(6))); d = ImageDraw.Draw(img)
        d.line([(bx, by), (bx - 60, by + 230), (px, py)], fill=(200, 245, 255), width=4)
        pts = [(bx, by), (bx - 60, by + 230), (px, py)]
        for k in range(3):
            u = (t * 1.2 + k / 3) % 1
            a, b, v = (pts[0], pts[1], u / 0.5) if u < 0.5 else (pts[1], pts[2], (u - 0.5) / 0.5)
            qx, qy = a[0] + (b[0] - a[0]) * v, a[1] + (b[1] - a[1]) * v
            d.ellipse([qx - 14, qy - 14, qx + 14, qy + 14], fill=WHITE)
        if t < L(11):
            rrect(d, (90, 420, 520, 560), 40, WHITE)
            d.polygon([(380, 555), (430, 555), (px - 30, py - 40)], fill=WHITE)
            txt_c(d, (305, 438), '¡ARRIBA!', font(80), RED)
        else:
            for k in range(3):
                u = (t * 0.9 + k / 3) % 1; rr = 60 + u * 260
                d.ellipse([bx - rr, by - rr, bx + rr, by + rr], outline=(255, 120, 200, int(200 * (1 - u))), width=6)
            txt_c(d, (W/2, 420), 'ECO DEL GRITO', font(88), YEL, 7)
    if L(12) <= t < L(13):  # es tuyo + stop
        txt_c(d, (W/2, 420), 'ES TUYO', font(110), WHITE, 8)
        if t > L(12, 1.6):
            hx = mx + int(170 * S); hy = OY + int(820 * S)
            rrect(d, (hx - 120, hy - 260, hx + 120, hy - 170), 30, RED)
            txt_c(d, (hx, hy - 252), 'STOP', font(56), WHITE)
    if L(13) <= t < L(14):  # SÍ / NO y COMENTA VIRAL
        if t < L(13, 1.5):
            for k, (s, col) in enumerate((('SÍ', (40, 170, 80)), ('NO', RED))):
                x0 = 190 + k * 380; rrect(d, (x0, 420, x0 + 320, 580), 40, col)
                txt_c(d, (x0 + 160, 445), s, font(90), WHITE)
        else:
            w2 = int(430 * (1 + 0.05 * math.sin(t * 10)))
            rrect(d, (W/2 - w2, 400, W/2 + w2, 600), 50, YEL)
            txt_c(d, (W/2, 410), 'COMENTA', font(64), (20, 20, 20)); txt_c(d, (W/2, 480), 'VIRAL', font(96), RED)
    if L(14) <= t:  # envíaselo a ese amigo
        cx, cy = W/2, 500; dx = ((t - L(14)) * 160) % 120
        d.polygon([(cx - 130 + dx, cy + 10), (cx + 110 + dx, cy - 90), (cx + 10 + dx, cy + 90), (cx - 20 + dx, cy + 30)], fill=WHITE)
        d.line([(cx - 20 + dx, cy + 30), (cx + 110 + dx, cy - 90)], fill=(160, 160, 170), width=6)
        txt_c(d, (W/2, 620), 'ENVÍASELO A ESE AMIGO', font(58), YEL, 6)

def frame(f):
    t = f / FPS
    img = BASE.copy(); mx = mascot_x(t)
    lean = 2 * math.sin(t * 40) if TIMER_A <= t < TIMER_B else 0
    oy = OY + int(4 * math.sin(t * 3))
    ang = arm_angle(t)
    a2 = ARM.rotate(ang, resample=Image.BICUBIC, center=piv) if abs(ang) > 0.05 else ARM
    body = BODY_C.copy(); mo = mouth_open(f)
    if mo > 0.05:
        pt = PATCH.resize((PATCH.width, max(2, int(PATCH.height * (0.3 + 0.7 * mo)))), Image.LANCZOS)
        body.alpha_composite(pt, (int(mouth_xy[0]), int(mouth_xy[1])))
    if (t % 3.7) < 0.13: body.alpha_composite(BLINK)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    lay.alpha_composite(a2, (mx + int(lean), oy)); lay.alpha_composite(body, (mx + int(lean), oy))
    sh = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([mx + 160, OY + MH - 40, mx + MW - 160, OY + MH + 10], fill=(0, 0, 0, 120))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10))); img.alpha_composite(lay)
    overlays(img, t, mx); draw_caption(img, t)
    return img.convert('RGB')

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        ims = [frame(int(float(x) * FPS)).resize((360, 640)) for x in sys.argv[2:]]
        c = Image.new('RGB', (360 * len(ims), 640))
        for k, im in enumerate(ims): c.paste(im, (k * 360, 0))
        c.save('test.jpg'); print('Listo: test.jpg')
    else:
        p = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                              '-i', 'voice.wav', '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '20', '-pix_fmt', 'yuv420p',
                              '-c:a', 'aac', '-b:a', '160k', '-shortest', '-movflags', '+faststart', SALIDA], stdin=subprocess.PIPE)
        n = int(TOTAL * FPS)
        for f in range(n):
            p.stdin.write(frame(f).tobytes())
            if f % 300 == 0: print(f'{f}/{n} cuadros')
        p.stdin.close(); p.wait(); print('Listo:', SALIDA)
