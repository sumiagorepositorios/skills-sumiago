"""Arma el video del Día 4 "Marketplace Sumiago" con Sofi y Sumiago (9:16, 1080x1920, 30 fps, unos 49 s).
Uso (en la carpeta donde están voice.wav, durs.json, speakers.json, mascot_clean.png, sofi.png y mix.wav):
    python scripts/render.py test 1 3.5 6 10.5 15 19     -> test.jpg con cuadros de muestra
    python scripts/render.py full                         -> dia-04.mp4 (usa mix.wav: voces + música + efectos)
"""
import os, sys, math, random, subprocess, json, wave
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
import base as render2
from base import W, H, FPS, font, txt_c, glow, ease, scene, durs, YEL, RED, WHITE
from portada_base import emoji, put, pop, stamp, confetti, pill, sky

TEAL = (20, 170, 175); DARK = (25, 25, 30); GREEN = (37, 211, 102); GRAY = (235, 235, 240)
SPK = json.load(open('speakers.json'))
starts = render2.starts
TAIL = 1.2
TOTAL = sum(durs) + TAIL

# ---------- characters ----------
mx0, my0, mx1, my1 = 545, 333, 656, 392
class Char:
    def __init__(self, path, s):
        src = Image.open(path).convert('RGBA'); A = np.array(src)
        patch = A[my0:my1, mx0:mx1].copy()
        diff = np.abs(patch[..., :3].astype(int) - np.array([235, 170, 110])).sum(-1)
        mm = cv2.morphologyEx((diff > 120).astype(np.uint8) * 255, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
        patch[..., 3] = np.minimum(patch[..., 3], mm)
        bm = np.zeros(A.shape[:2], np.uint8); bm[my0:my1, mx0:mx1] = cv2.dilate(mm, np.ones((7, 7), np.uint8))
        cl = A.copy(); inp = cv2.inpaint(cv2.cvtColor(A[..., :3], cv2.COLOR_RGB2BGR), bm, 7, cv2.INPAINT_TELEA)
        cl[..., :3] = cv2.cvtColor(inp, cv2.COLOR_BGR2RGB)
        C = Image.fromarray(cl); d = ImageDraw.Draw(C); d.arc([566, 335, 636, 370], 20, 160, fill=(90, 35, 25), width=6)
        BL = Image.new('RGBA', src.size, (0, 0, 0, 0)); d = ImageDraw.Draw(BL)
        for x0, x1 in ((500, 570), (635, 703)):
            d.rectangle([x0 - 3, 258, x1 + 3, 322], fill=(232, 168, 108, 255)); d.line([(x0, 300), (x1, 300)], fill=(60, 30, 20), width=7)
        self.s = s; sz = (int(src.width * s), int(src.height * s))
        self.closed = C.resize(sz, Image.LANCZOS); self.blink = BL.resize(sz, Image.LANCZOS)
        P = Image.fromarray(patch); self.patch = P.resize((int(P.width * s), int(P.height * s)), Image.LANCZOS)
        self.w, self.h = sz
    def img(self, mo, blink):
        im = self.closed.copy()
        if mo > 0.05:
            ph = max(2, int(self.patch.height * (0.3 + 0.7 * mo))); im.alpha_composite(self.patch.resize((self.patch.width, ph), Image.LANCZOS), (int(mx0 * self.s), int(my0 * self.s)))
        if blink: im.alpha_composite(self.blink)
        return im
S_ = 0.5
SOFI = Char('sofi.png', S_); SUMI = Char('mascot_clean.png', S_)
FEET = 1900
POS = {'W': (-30, FEET - SOFI.h), 'S': (W - SUMI.w + 30, FEET - SUMI.h)}
def face(k): x, y = POS[k]; return (x + 600 * S_, y + 300 * S_)

# audio envelope
wf = wave.open('voice.wav'); sr = wf.getframerate(); raw = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32) / 32768
spf = sr // FPS; nfr = len(raw) // spf
rms = np.array([np.sqrt(np.mean(raw[k * spf:(k + 1) * spf] ** 2)) for k in range(nfr)]); rms /= np.percentile(rms, 95) + 1e-6
def mouth(f): return float(np.clip((rms[f] - 0.12) / 0.7, 0, 1)) if f < len(rms) else 0

# ---------- world ----------
def make_bg():
    img = sky((255, 255, 255), (244, 244, 248)); d = ImageDraw.Draw(img)
    d.rectangle([0, 1760, W, H], fill=(232, 232, 238))
    g = Image.new('RGBA', (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(g)
    gd.ellipse([-120, 1150, 560, 1830], fill=TEAL + (45,)); gd.ellipse([520, 1150, 1200, 1830], fill=RED + (40,))
    img.alpha_composite(g.filter(ImageFilter.GaussianBlur(40)))
    return img
BG = make_bg()

# camera per line: (target, zoom)
CAM = ['W2.3', 'S1.5', 'W1.5', 'W2.3', 'A1.0', 'S2.2', 'A1.0', 'S1.5', 'W2.3', 'S2.2', 'A1.0', 'W2.0', 'A1.0']
def cam_of(i):
    c = CAM[i]; k, z = c[0], float(c[1:])
    if k == 'A': return (W / 2, H / 2, 1.0)
    fx, fy = face(k); return (fx, fy - 0.2 * H / z, z)
def camera(t):
    i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - starts[-1]
    a = cam_of(max(0, i - 1)) if i > 0 else cam_of(0); b = cam_of(i)
    u = ease(lt / 0.4) if i > 0 else 1
    cx, cy, z = (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u, a[2] + (b[2] - a[2]) * u)
    z *= 1 + 0.015 * math.sin(t * 0.8)  # slow breathing push
    return cx, cy, z

def apply_cam(img, cx, cy, z):
    z = max(1.0, z); vw, vh = W / z, H / z
    x0 = min(max(0, cx - vw / 2), W - vw); y0 = min(max(0, cy - vh / 2), H - vh)
    return img.resize((W, H), Image.BICUBIC, box=(x0, y0, x0 + vw, y0 + vh))

# ---------- overlays ----------
def phone(d, x, y, w, h):
    d.rounded_rectangle([x, y, x + w, y + h], 44, fill=(20, 20, 26)); d.rounded_rectangle([x + 14, y + 30, x + w - 14, y + h - 30], 28, fill=WHITE)
    return x + 14, y + 30, x + w - 14, y + h - 30
def bubble(d, x, y, w, text, col=(220, 248, 198), tc=DARK, size=44, right=False):
    h = size + 44; d.rounded_rectangle([x, y, x + w, y + h], 28, fill=col)
    d.text((x + 26, y + 18), text, font=font(size), fill=tc)
    return y + h

def overlays(img, t, f):
    i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - starts[-1]
    d = ImageDraw.Draw(img)
    if i == 0:
        p = phone(d, 300, 330, 480, 520)
        d.rectangle([p[0], p[1], p[2], p[1] + 230], fill=(220, 220, 228)); put(img, emoji('🚲', 170), (p[0] + p[2]) / 2, p[1] + 115); d = ImageDraw.Draw(img)
        d.text((p[0] + 24, p[1] + 250), 'Bicicleta en venta', font=font(40), fill=DARK)
        stamp(img, 0.15, t, 'RECHAZADA', RED, 640, 110, -10)
        if lt < 0.25: img.alpha_composite(Image.new('RGBA', (W, H), (255, 0, 0, int(140 * (1 - lt / 0.25)))))
    elif i == 2:
        d.rounded_rectangle([80, 330, 1000, 880], 34, fill=WHITE, outline=(220, 220, 228), width=4)
        off = (lt * 260) % 120
        for k in range(8):
            y = 350 + k * 120 - off
            if 340 < y < 820:
                d.rounded_rectangle([110, y, 970, y + 100], 20, fill=(240, 240, 245))
                d.rectangle([125, y + 12, 205, y + 88], fill=(210, 210, 218)); d.rectangle([225, y + 25, 700, y + 45], fill=(205, 205, 212)); d.rectangle([225, y + 58, 560, y + 74], fill=(220, 220, 226))
        txt_c(d, (540, 800), '+10.000 publicaciones', font(44), RED)
    elif i == 3:
        d.rounded_rectangle([140, 330, 940, 900], 34, fill=(236, 229, 221))
        y = bubble(d, 180, 370, 330, '¿precio?', WHITE)
        if lt > 1.6: bubble(d, 520, y + 30, 380, '$80, ¿te interesa?', (220, 248, 198))
        if lt > 2.6:
            d.text((600, y + 150), 'Visto', font=font(36), fill=(80, 130, 220))
            txt_c(d, (540, 800), 'Se desconectó…', font(44), (130, 130, 140))
    elif i == 4:
        items = [('🚩', 'Perfiles falsos', 0.4), ('🖼️', 'Fotos robadas', 1.8), ('💸', 'Comisión por venta', 3.2)]
        for k, (em, s, t0) in enumerate(items):
            sc = pop(starts[4] + t0, t)
            if sc <= 0: continue
            y = 330 + k * 180
            d.rounded_rectangle([140, y, 940, y + 150], 40, fill=WHITE, outline=RED, width=5)
            put(img, emoji(em, int(95 * min(1.2, sc)) + 1), 240, y + 75); d.text((320, y + 45), s, font=font(56), fill=DARK)
    elif i == 5:
        s = pop(starts[5] + 0.8, t)
        if s > 0.05:
            w2 = 420 * s; d.rounded_rectangle([W / 2 - w2, 360, W / 2 + w2, 600], 50, fill=RED)
            if s > 0.6: txt_c(d, (W / 2, 385), 'MARKETPLACE', font(80), WHITE); txt_c(d, (W / 2, 485), 'SUMIAGO', font(80), YEL)
    elif i == 6:
        p = phone(d, 290, 320, 500, 800)
        d.rectangle([p[0], p[1], p[2], p[1] + 300], fill=(225, 238, 248)); put(img, emoji('🚲', 210), (p[0] + p[2]) / 2, p[1] + 150); d = ImageDraw.Draw(img)
        d.text((p[0] + 30, p[1] + 320), 'Bicicleta de ruta', font=font(42), fill=DARK); d.text((p[0] + 30, p[1] + 380), '$80 · Maracaibo', font=font(38), fill=(110, 110, 120))
        if lt > 1.0: pill(d, 540, p[1] + 450, 'GRATIS', GREEN, WHITE, 50)
        if lt > 2.0: pill(d, 540, p[1] + 560, 'fotos reales', (60, 60, 75), WHITE, 40)
        if lt > 3.0: stamp(img, starts[6] + 3.0, t, 'VISIBLE YA', TEAL, 1180, 70, -4)
    elif i == 7:
        d.rounded_rectangle([140, 330, 940, 960], 34, fill=(236, 229, 221)); d.rectangle([140, 330, 940, 430], fill=(7, 94, 84))
        txt_c(d, (540, 350), 'WhatsApp', font(48), WHITE)
        if lt > 0.6:
            d.rounded_rectangle([180, 470, 820, 760], 26, fill=WHITE)
            d.rectangle([200, 490, 380, 650], fill=(225, 238, 248)); put(img, emoji('🚲', 130), 290, 570); d = ImageDraw.Draw(img)
            d.text((400, 500), 'Bicicleta de ruta', font=font(36), fill=DARK); d.text((400, 550), '$80', font=font(36), fill=GREEN)
            d.text((200, 670), 'Hola, ¿aún está disponible?', font=font(38), fill=DARK)
        if lt > 2.0: txt_c(d, (540, 850), 'directo a tu chat', font(46), (7, 94, 84))
    elif i == 8:
        put(img, emoji('🤔', 220), 820, 560)
    elif i == 9:
        s = pop(starts[9] + 0.15, t)
        if s > 0.05:
            txt_c(d, (W / 2, 360), '0%', font(int(260 * min(1.2, s)) + 1), GREEN, 10, WHITE)
            if lt > 1.2: pill(d, W / 2, 720, 'de comisión', DARK, WHITE, 60)
            if lt > 2.6: pill(d, W / 2, 840, 'todo es para ti', GREEN, WHITE, 56)
    elif i == 10:
        items = [('⭐', 'Reputación', 0.6), ('🛡️', 'Fotos verificadas', 2.0), ('📍', 'Cerca de ti', 3.6)]
        for k, (em, s, t0) in enumerate(items):
            sc = pop(starts[10] + t0, t)
            if sc <= 0: continue
            y = 330 + k * 180
            d.rounded_rectangle([140, y, 940, y + 150], 40, fill=WHITE, outline=TEAL, width=5)
            put(img, emoji(em, int(95 * min(1.2, sc)) + 1), 240, y + 75); d.text((320, y + 45), s, font=font(56), fill=DARK)
            d.ellipse([850, y + 45, 910, y + 105], fill=GREEN); d.line([(865, y + 76), (877, y + 90), (897, y + 60)], fill=WHITE, width=8)
    elif i == 11:
        d.rounded_rectangle([140, 340, 940, 500], 36, fill=WHITE, outline=(220, 220, 228), width=4)
        put(img, emoji('💬', 90), 230, 420); d = ImageDraw.Draw(img); d.text((300, 365), 'Nuevo mensaje', font=font(46), fill=DARK); d.text((300, 425), '"¡Te la compro!"', font=font(40), fill=(110, 110, 120))
        stamp(img, starts[11] + 1.2, t, 'VENDIDO', GREEN, 700, 130, -8)
        confetti(img, starts[11] + 1.2, t, 70, 4)
    elif i == 12:
        s = 1 + 0.05 * math.sin(t * 9)
        bw = 430 * s
        d.rounded_rectangle([W / 2 - bw, 360, W / 2 + bw, 600], 60, fill=RED)
        txt_c(d, (W / 2, 380), 'PUBLICA', font(int(80 * s)), WHITE); txt_c(d, (W / 2, 475), 'GRATIS HOY', font(int(84 * s)), YEL)
        d.rounded_rectangle([170, 650, 910, 750], 50, fill=DARK); txt_c(d, (W / 2, 665), 'sumiago.com/marketplace', font(50), WHITE)
        if lt > 3.4: pill(d, W / 2, 800, 'link en mi perfil', YEL, DARK, 52)

def caption(img, t):
    d = ImageDraw.Draw(img)
    for ch in render2.chunks:
        if ch[0][0] <= t < ch[-1][1] + 0.05 or (ch is render2.chunks[-1] and t >= ch[0][0]):
            sp = SPK[ch[0][3]]; hi = TEAL if sp == 'W' else RED
            line = ' '.join(w[2] for w in ch); ff = font(66); tw = d.textlength(line, font=ff)
            if tw > W - 100: ff = font(int(66 * (W - 100) / tw)); tw = d.textlength(line, font=ff)
            x = (W - tw) / 2; y = 190
            nm = 'Sofi' if sp == 'W' else 'Sumiago'
            d.rounded_rectangle([W / 2 - 90, y - 70, W / 2 + 90, y - 18], 26, fill=hi); txt_c(d, (W / 2, y - 66), nm, font(34), WHITE)
            for (a, b, w, _) in ch:
                act = a <= t < b + 0.02
                d.text((x, y - (6 if act else 0)), w, font=ff, fill=hi if act else DARK, stroke_width=6, stroke_fill=WHITE)
                x += d.textlength(w + ' ', font=ff)
            return

def frame(f):
    t = f / FPS
    i, lt = scene(t)
    if t >= sum(durs): i, lt = len(durs) - 1, t - starts[-1]
    spk = SPK[i] if t < sum(durs) else None
    img = BG.copy()
    for k, ch in (('W', SOFI), ('S', SUMI)):
        talk = (spk == k)
        mo = mouth(f) if talk else 0
        bl = ((t + (1.3 if k == 'S' else 0)) % 3.6) < 0.13
        im = ch.img(mo, bl)
        x, y = POS[k]
        y += int(-6 * abs(math.sin(t * 7)) * (1 if talk and mo > 0.2 else 0))
        if k == 'W' and i == 0 and lt < 0.5: x += int(14 * math.sin(lt * 70))
        if k == 'W' and i == 11: y -= int(90 * abs(math.sin(lt * 5)) * (1 if lt < 2.5 else 0))
        if k == 'S' and i == 9 and lt < 0.6: y -= int(60 * math.sin(lt / 0.6 * math.pi))
        sh = Image.new('RGBA', (W, H), (0, 0, 0, 0)); ImageDraw.Draw(sh).ellipse([x + 130, FEET - 30, x + ch.w - 130, FEET + 12], fill=(0, 0, 0, 60))
        img.alpha_composite(sh)
        img.alpha_composite(im, (x, y))
    cx, cy, z = camera(t)
    img = apply_cam(img, cx, cy, z)
    if 0 < lt < 0.1 and i > 0 and CAM[i] != CAM[i - 1]: img.alpha_composite(Image.new('RGBA', (W, H), (255, 255, 255, int(150 * (1 - lt / 0.1)))))
    overlays(img, t, f)
    caption(img, t)
    d = ImageDraw.Draw(img); d.rectangle([0, H - 14, W * min(1, t / TOTAL), H], fill=RED)
    return img.convert('RGB')

def events():
    S = starts; ev = []
    for i in range(1, len(durs)):
        if CAM[i] != CAM[i - 1]: ev.append((S[i] - 0.1, 'whoosh', 0))
    ev += [(0.05, 'boom', 0), (0.15, 'stamp', 0)]
    ev += [(S[3] + 0.05, 'msg', 0), (S[3] + 1.6, 'pop', 900), (S[3] + 2.6, 'buzz', 0)]
    ev += [(S[4] + x, 'pop', 600 + k * 120) for k, x in enumerate((0.4, 1.8, 3.2))]
    ev += [(S[5] + 0.8, 'stamp', 0), (S[5] + 0.8, 'ding', 1318)]
    ev += [(S[6] + 1.0, 'ding', 1568), (S[6] + 2.0, 'pop', 1000), (S[6] + 3.0, 'stamp', 0)]
    ev += [(S[7] + 0.6, 'msg', 0)]
    ev += [(S[9] + 0.15, 'stamp', 0), (S[9] + 0.15, 'coin', 0), (S[9] + 1.2, 'pop', 900), (S[9] + 2.6, 'pop', 1100)]
    ev += [(S[10] + x, 'ding', 1046 + k * 200) for k, x in enumerate((0.6, 2.0, 3.6))]
    ev += [(S[11] + 0.05, 'msg', 0), (S[11] + 1.2, 'stamp', 0), (S[11] + 1.2, 'cheer', 0), (S[11] + 1.25, 'coin', 0)]
    ev += [(S[12] + 0.1, 'riser', 0), (S[12] + 3.4, 'pop', 900), (S[12] + 4.5, 'ding', 2093)]
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
                              '-shortest', '-movflags', '+faststart', 'dia-04.mp4'], stdin=subprocess.PIPE)
        for f in range(n): p.stdin.write(frame(f).tobytes())
        p.stdin.close(); p.wait()
        print('Listo: dia-04.mp4')
