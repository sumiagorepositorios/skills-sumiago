import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from escenas import W, H, FPS, BLACK, BOLD, MED, clamp, prog, eo, eio, back, font, text_layer, put, add_glow, bg_frame

RED = (214, 18, 32)
INK = (28, 28, 30)
DUR = 7.0

# ---- logo with alpha ----
src = np.asarray(Image.open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "logo-sumiago-fondo-blanco.png")).convert("RGB")).astype(np.float32)
src = src[372:662, 66:960]
a = np.clip((255 - src.min(2)) / 255 * 1.35, 0, 1)
col = 255 - (255 - src) / np.maximum(a[..., None], 1e-3)
col = np.clip(col, 0, 255)
rgba = np.dstack([col, a * 255]).astype(np.uint8)
LOGO = Image.fromarray(rgba, "RGBA")
LOGO = LOGO.resize((int(LOGO.width * 1.12), int(LOGO.height * 1.12)), Image.LANCZOS)
SPLIT = int(272 * 1.12)
ICON = LOGO.crop((0, 0, SPLIT, LOGO.height))
WORD = LOGO.crop((SPLIT, 0, LOGO.width, LOGO.height))

# ---- light background ----
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
bgl = np.zeros((H, W, 3), np.float32) + 255
d = np.exp(-(((xx - W / 2) ** 2 + (yy - 1150) ** 2) / (2 * 520 ** 2)))
bgl -= d[..., None] * np.array([0, 40, 40], np.float32) * 0.6
d2 = ((xx - W / 2) ** 2 / (W * 0.8) ** 2 + (yy - H / 2) ** 2 / (H * 0.7) ** 2)
bgl *= np.clip(1.04 - d2 * 0.12, 0.85, 1)[..., None]
LIGHT = Image.fromarray(np.clip(bgl, 0, 255).astype(np.uint8)).convert("RGBA")

def heart(size, c):
    im = Image.new("RGBA", (size * 2, size * 2), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    s = size
    dd.ellipse((s * 0.2, s * 0.35, s * 1.05, s * 1.2), fill=c)
    dd.ellipse((s * 0.95, s * 0.35, s * 1.8, s * 1.2), fill=c)
    dd.polygon([(s * 0.24, s * 0.95), (s * 1.76, s * 0.95), (s, s * 1.8)], fill=c)
    return im
rng = np.random.default_rng(7)
HEARTS = [(rng.uniform(60, W - 60), rng.uniform(0, 1), rng.uniform(18, 38), rng.uniform(0.25, 0.6)) for _ in range(16)]
HL = {}

def pill_red(text, size, w, h):
    im = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0)); dd = ImageDraw.Draw(im)
    dd.rounded_rectangle((40, 40, 40 + w, 40 + h), h // 2, fill=RED + (255,))
    im = add_glow(im, RED, 30, 0.6); dd = ImageDraw.Draw(im)
    f = font(BLACK, size); bb = f.getbbox(text)
    dd.text((40 + w / 2 - (bb[0] + bb[2]) / 2, 40 + h / 2 - (bb[1] + bb[3]) / 2), text, font=f, fill=(255, 255, 255, 255))
    return im
PILL = pill_red("sumiago.com", 78, 640, 150)

def frame(t):
    f = bg_frame(t + 60)
    # circular reveal
    r = eio(prog(t, 0.0, 0.5)) * 1200
    if r > 0:
        m = Image.new("L", (W, H), 0)
        ImageDraw.Draw(m).ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r), fill=255)
        ring = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((W / 2 - r - 18, H / 2 - r - 18, W / 2 + r + 18, H / 2 + r + 18), fill=RED + (255,))
        if t < 0.5: f.alpha_composite(ring)
        f.paste(LIGHT, (0, 0), m)
    # floating hearts
    for i, (hx, ph, sz, sp) in enumerate(HEARTS):
        k = (i, int(sz))
        if k not in HL: HL[k] = heart(int(sz), RED + (255,))
        y = H + 60 - ((ph * H + t * sp * 260) % (H + 120))
        put(f, HL[k], hx + math.sin(t * 1.5 + i) * 20, y, alpha=0.12 * prog(t, 0.4, 1.0))
    a = eo(prog(t, 0.4, 0.75))
    put(f, text_layer("¿Quieres videos así", 92, INK), W / 2, 560 + (1 - a) * 40, alpha=a)
    L1 = text_layer("para tu", 92, INK); L2 = text_layer("EMPRESA?", 110, RED)
    tot = L1.width + 10 + L2.width; x0 = W / 2 - tot / 2
    a = eo(prog(t, 1.2, 1.55))
    put(f, L1, x0 + L1.width / 2, 700 + (1 - a) * 40, alpha=a)
    a2 = prog(t, 1.4, 1.75)
    put(f, L2, x0 + L1.width + 10 + L2.width / 2, 694, scale=0.6 + 0.4 * back(a2), alpha=clamp(a2 * 2))
    a = eo(prog(t, 2.75, 3.05))
    put(f, text_layer("Regístrate en", 64, (90, 90, 96), path=BOLD), W / 2, 950 + (1 - a) * 30, alpha=a)
    # logo
    lx = W / 2 - LOGO.width / 2; ly = 1190
    ai = prog(t, 3.3, 3.7)
    if ai > 0:
        put(f, ICON, lx + ICON.width / 2, ly, scale=0.3 + 0.7 * back(ai, 2.2), alpha=clamp(ai * 2.5))
    aw = eio(prog(t, 3.55, 4.15))
    if aw > 0:
        wd = WORD.copy()
        cut = int(wd.width * aw)
        al = np.asarray(wd.getchannel("A")).copy(); al[:, cut:] = 0
        wd.putalpha(Image.fromarray(al))
        put(f, wd, lx + SPLIT + WORD.width / 2 + (1 - aw) * 40, ly)
    # shine
    sp = prog(t, 4.3, 5.0)
    if 0 < sp < 1:
        sh = Image.new("L", LOGO.size, 0)
        cx = -200 + (LOGO.width + 400) * sp
        ImageDraw.Draw(sh).polygon([(cx - 60, 0), (cx + 20, 0), (cx - 40, LOGO.height), (cx - 120, LOGO.height)], fill=200)
        sh = sh.filter(ImageFilter.GaussianBlur(14))
        m = np.minimum(np.asarray(sh, np.float32), np.asarray(LOGO.getchannel("A"), np.float32)).astype(np.uint8)
        wl = Image.new("RGBA", LOGO.size, (255, 255, 255, 0)); wl.putalpha(Image.fromarray(m))
        put(f, wl, W / 2, ly)
    # pulse ring at logo landing
    if 3.5 < t < 4.3:
        rr = (t - 3.5) / 0.8
        ring = Image.new("RGBA", (900, 900), (0, 0, 0, 0)); R = 80 + 360 * rr
        ImageDraw.Draw(ring).ellipse((450 - R, 450 - R, 450 + R, 450 + R), outline=RED + (int(160 * (1 - rr)),), width=8)
        put(f, ring, lx + ICON.width / 2, ly)
    ap = prog(t, 4.6, 4.95)
    pulse = 1 + 0.03 * math.sin(max(0, t - 5.0) * 6)
    put(f, PILL, W / 2, 1490, scale=(0.5 + 0.5 * back(ap)) * pulse, alpha=clamp(ap * 2))
    a = eo(prog(t, 5.3, 5.6))
    put(f, text_layer("Crea los videos de tu negocio", 52, (90, 90, 96), path=MED), W / 2, 1640, alpha=a)
    return f

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        ims = [frame(float(x)).convert("RGB").resize((360, 640)) for x in sys.argv[2:]]
        c = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): c.paste(im, (k * 360, 0))
        c.save("prueba_cierre.jpg", quality=88)
    else:
        tmp = os.path.join(os.getcwd(), "out", "cierre.tmp.mp4")
        p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                              "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
        for k in range(int(DUR * FPS)):
            p.stdin.write(frame(k / FPS).convert("RGB").tobytes())
        p.stdin.close()
        if p.wait() == 0: os.replace(tmp, os.path.join(os.getcwd(), "out", "cierre.mp4"))
        print("ok")
