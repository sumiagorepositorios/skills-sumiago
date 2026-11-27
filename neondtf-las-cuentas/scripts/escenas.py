import sys, os, math, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
from PIL import Image, ImageDraw
from base import (W, H, FPS, BLACK, BOLD, MED, BG, CYAN, MAG, LIME, WHITE, RED, clamp, prog, eo, eio, back, font,
                    add_glow, text_layer, put, pill, bg_frame, flash, CHECK, logo, CARD)
from base2 import STAGES, CM, frame_for, tint, stamp, slam, clock_layer, BAD

GRAY = (170, 175, 190)

def shirt(size=150, col=WHITE, dot=MAG):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = size / 100
    pts = [(30, 12), (42, 8), (50, 14), (58, 8), (70, 12), (92, 30), (80, 44), (72, 38), (72, 92), (28, 92), (28, 38), (20, 44), (8, 30)]
    d.polygon([(x * s, y * s) for x, y in pts], fill=col + (255,))
    d.ellipse((40 * s, 40 * s, 60 * s, 60 * s), fill=dot + (255,))
    return add_glow(im, col, 14, 0.5)
SHIRT = shirt()

def up_arrow(col, size=60):
    im = Image.new("RGBA", (size, size), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.polygon([(size / 2, 4), (size - 6, size / 2), (size * .64, size / 2), (size * .64, size - 4), (size * .36, size - 4), (size * .36, size / 2), (6, size / 2)], fill=col + (255,))
    return im

def row(f, items, cy, gap=16):
    ws = [it.width for it in items]; tot = sum(ws) + gap * (len(items) - 1); x = W / 2 - tot / 2
    for it in items:
        put(f, it, x + it.width / 2, cy); x += it.width + gap

# ---------- S1 calculadora ----------
KEYS = ["7", "8", "9", "÷", "4", "5", "6", "×", "1", "2", "3", "−", "0", ".", "=", "+"]
def s1(t):  # 4.1
    f = bg_frame(t)
    a = eo(prog(t, 0.1, 0.4))
    put(f, text_layer("LAS CUENTAS", 128, WHITE), W / 2, 330 + (1 - a) * 50, alpha=a)
    a = prog(t, 0.4, 0.75)
    put(f, text_layer("DE TU TALLER", 120, MAG, glow=MAG, gr=34), W / 2, 480, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 3))
    ca = eo(prog(t, 0.6, 1.0))
    if ca > 0:
        cw, ch = 600, 880
        c = Image.new("RGBA", (cw + 100, ch + 100), (0, 0, 0, 0)); d = ImageDraw.Draw(c)
        d.rounded_rectangle((50, 50, 50 + cw, 50 + ch), 60, fill=(22, 24, 32, 255), outline=CYAN + (255,), width=6)
        c = add_glow(c, CYAN, 36, 0.9); d = ImageDraw.Draw(c)
        d.rounded_rectangle((90, 90, 50 + cw - 40, 300), 30, fill=(8, 18, 20, 255))
        rnd = int(t * 14)
        if t < 3.0:
            num = str((rnd * 7919) % 99999)
        else:
            num = "= ?"
        fn = font(BLACK, 120); bb = fn.getbbox(num)
        d.text((50 + cw - 70 - bb[2], 195 - (bb[1] + bb[3]) / 2), num, font=fn, fill=CYAN + (255,))
        lit = (rnd * 5) % 16
        for k, kk in enumerate(KEYS):
            r_, c_ = divmod(k, 4); x0 = 100 + c_ * 130; y0 = 340 + r_ * 145
            on = (k == lit and t < 3.0) or (kk == "=" and t >= 3.0)
            col = (MAG if kk in "÷×−+=" else (52, 56, 70))
            if on: col = LIME
            d.rounded_rectangle((x0, y0, x0 + 110, y0 + 120), 26, fill=col + (255,))
            fk = font(BLACK, 56); bb = fk.getbbox(kk)
            d.text((x0 + 55 - (bb[0] + bb[2]) / 2, y0 + 60 - (bb[1] + bb[3]) / 2), kk, font=fk, fill=((10, 10, 14) if on else WHITE) + (255,))
        put(f, c, W / 2, 1150 + (1 - ca) * 150, alpha=ca, scale=0.92 + 0.08 * ca)
    flash(f, t, 0.2, k=0.6)
    return f

# ---------- S2 ecuación ----------
def s2(t):  # 6.8
    f = bg_frame(t + 4)
    tint(f, (110, 0, 20), 0.10)
    put(f, pill(560, 100, RED, "A LA ANTIGUA", 52, tcolor=WHITE), W / 2, 280, alpha=eo(prog(t, 0.05, 0.3)))
    a = eo(prog(t, 0.2, 0.5))
    th = BAD.resize((300, 300)); th.putalpha(Image.new("L", (300, 300), 255))
    fr = Image.new("RGBA", (330, 330), (0, 0, 0, 0)); ImageDraw.Draw(fr).rounded_rectangle((0, 0, 329, 329), 30, fill=RED + (255,)); fr.alpha_composite(th, (15, 15))
    put(f, text_layer("1 DISEÑO", 70, WHITE, path=BOLD), 260, 470, alpha=a)
    put(f, fr, 260, 700, alpha=a, scale=0.8 + 0.2 * a)
    a = prog(t, 1.7, 2.0)
    put(f, text_layer("=", 140, WHITE), 520, 700, alpha=clamp(a * 2))
    hrs = 6 + 1.0 * eio(prog(t, 1.8, 3.6))
    put(f, clock_layer(hrs * 1.0 + (t * 3 if t > 1.8 else 0), RED, 120), 800, 650, alpha=eo(a), scale=0.75)
    put(f, text_layer("1 HORA", 100, RED, glow=RED, gr=26), 800, 860, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    a = prog(t, 3.9, 4.2)
    put(f, text_layer("×", 140, WHITE), W / 2, 1060, alpha=clamp(a * 2))
    for k in range(5):
        sa = prog(t, 4.3 + k * 0.22, 4.55 + k * 0.22)
        put(f, SHIRT, 180 + k * 180, 1250, scale=0.4 + 0.6 * back(sa), alpha=clamp(sa * 2))
    a = prog(t, 5.4, 5.75)
    put(f, text_layer("5 PEDIDOS AL DÍA", 96, WHITE, glow=MAG, gr=26, gs=0.8), W / 2, 1450, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    flash(f, t, 0.12, RED, 0.3)
    return f

# ---------- S3 30 horas ----------
DIAS = ["LUN", "MAR", "MIÉ", "JUE", "VIE", "SÁB"]
def s3(t):  # 4.3
    f = bg_frame(t + 11)
    tint(f, (110, 0, 20), 0.14)
    n = int(round(30 * eio(prog(t, 0.15, 1.9))))
    put(f, text_layer(str(n), 330, RED, glow=RED, gr=70, gs=1.4), W / 2, 470)
    put(f, text_layer("HORAS A LA SEMANA", 76, WHITE), W / 2, 680, alpha=eo(prog(t, 0.3, 0.6)))
    g = Image.new("RGBA", (W, 640), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    bw, gap = 120, 40; x0 = (W - (6 * bw + 5 * gap)) / 2
    for k in range(6):
        p = eio(prog(t, 0.15 + k * 0.29, 0.45 + k * 0.29))
        x = x0 + k * (bw + gap); hgt = 420 * p
        d.rounded_rectangle((x, 40, x + bw, 460), 20, fill=(40, 30, 36, 255))
        if hgt > 2: d.rounded_rectangle((x, 460 - hgt, x + bw, 460), 20, fill=RED + (255,))
        fn = font(BOLD, 40); bb = fn.getbbox(DIAS[k])
        d.text((x + bw / 2 - (bb[0] + bb[2]) / 2, 500), DIAS[k], font=fn, fill=GRAY + (255,))
        if p > 0.9:
            fh = font(BLACK, 44); s = "5H"; bb = fh.getbbox(s)
            d.text((x + bw / 2 - (bb[0] + bb[2]) / 2, 400 - 20), s, font=fh, fill=WHITE + (255,))
    g = add_glow(g, RED, 26, 0.5)
    put(f, g, W / 2, 1120)
    slam(f, stamp("SOLO DISEÑANDO", RED, 80, -4), W / 2, 1560, t, 2.3)
    flash(f, t, 0.12, RED, 0.35)
    return f

# ---------- S4 con Neon ----------
def s4(t):  # 5.7
    f = bg_frame(t + 15)
    tint(f, (0, 60, 70), 0.10)
    a = prog(t, 0.1, 0.4)
    put(f, pill(620, 110, CYAN, "CON NEON DTF", 58), W / 2, 290, scale=0.7 + 0.3 * back(a), alpha=clamp(a * 2))
    steps = [1.8, 2.6, 3.4]
    st = 0; sl = 0
    for k, s0 in enumerate(steps):
        if t >= s0: st = k; sl = eio(prog(t, s0, s0 + 0.6))
    if t < steps[0]: comp = STAGES[0]; xx = 0
    else:
        xx = int(CARD * sl); comp = STAGES[st].copy(); comp[:, :xx] = STAGES[st + 1][:, :xx]
    c = Image.fromarray(comp).convert("RGBA")
    if 0 < sl < 1: ImageDraw.Draw(c).rectangle((xx - 4, 0, xx + 4, CARD), fill=WHITE + (255,))
    c.putalpha(CM)
    done = t >= 4.1
    ca = eo(prog(t, 0.3, 0.7)); sc = 0.74 * (0.9 + 0.1 * ca)
    put(f, frame_for(LIME if done else CYAN), W / 2, 900, scale=sc, alpha=ca)
    put(f, c, W / 2, 900, scale=sc, alpha=ca)
    secs = int(167 * eio(prog(t, 1.7, 4.0)))
    if not done:
        put(f, text_layer("%d:%02d" % (secs // 60, secs % 60), 120, CYAN, path=BOLD, glow=CYAN, gr=26, gs=0.9), W / 2, 1460, alpha=eo(prog(t, 1.5, 1.8)))
    else:
        put(f, CHECK, W / 2 + 290, 610, scale=1.6 * back(prog(t, 4.1, 4.4)))
        a = prog(t, 4.1, 4.4)
        put(f, pill(800, 140, LIME, "LISTO EN < 3 MIN", 70), W / 2, 1460, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    flash(f, t, 0.2, CYAN, 0.5)
    return f

# ---------- S5 comparación ----------
def s5(t):  # 3.5
    f = bg_frame(t + 21)
    put(f, text_layer("5 × 6 × 3 min = 90 min", 64, GRAY, path=BOLD), W / 2, 300, alpha=eo(prog(t, 0.1, 0.4)))
    a = prog(t, 0.3, 0.7)
    put(f, text_layer("1,5 HORAS", 170, CYAN, glow=CYAN, gr=44), W / 2, 470, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    put(f, text_layer("A LA SEMANA", 70, WHITE), W / 2, 620, alpha=eo(prog(t, 0.6, 0.9)))
    g = Image.new("RGBA", (W, 900), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    p = eio(prog(t, 0.6, 1.8)); base = 720; bw = 260
    for x, hh, col, lab, val in [(220, 640, RED, "ANTES", "30 H"), (600, 32, CYAN, "AHORA", "1,5 H")]:
        h_ = max(8, hh * p)
        d.rounded_rectangle((x, base - h_, x + bw, base), 24, fill=col + (255,))
        fn = font(BOLD, 48); bb = fn.getbbox(lab)
        d.text((x + bw / 2 - (bb[0] + bb[2]) / 2, base + 30), lab, font=fn, fill=GRAY + (255,))
        fv = font(BLACK, 70); bb = fv.getbbox(val)
        d.text((x + bw / 2 - (bb[0] + bb[2]) / 2, base - h_ - 100), val, font=fv, fill=col + (255,))
    g = add_glow(g, WHITE, 20, 0.3)
    put(f, g, W / 2, 1180)
    flash(f, t, 0.12, CYAN, 0.35)
    return f

# ---------- S6 horas libres ----------
def s6(t):  # 6.5
    f = bg_frame(t + 25)
    n = int(round(28 * eio(prog(t, 0.3, 2.0))))
    put(f, text_layer("+" + str(n), 300, LIME, glow=LIME, gr=70, gs=1.4), W / 2, 450, scale=1 + 0.05 * math.sin(t * 9) * (n == 28) * (1 - prog(t, 2.0, 2.6)))
    put(f, text_layer("HORAS LIBRES", 96, WHITE), W / 2, 660, alpha=eo(prog(t, 0.5, 0.8)))
    put(f, text_layer("para...", 60, GRAY, path=MED), W / 2, 780, alpha=eo(prog(t, 2.3, 2.6)))
    for j, (txt, col, st) in enumerate([("IMPRIMIR MÁS", CYAN, 2.65), ("VENDER MÁS", MAG, 3.35), ("ATENDER MÁS CLIENTES", LIME, 4.4)]):
        a = prog(t, st, st + 0.35)
        put(f, pill(820, 130, col, txt, 62, tcolor=WHITE if col == MAG else (10, 10, 14)), W / 2 + (1 - back(a)) * (700 if j % 2 else -700), 960 + j * 175, alpha=clamp(a * 2))
    flash(f, t, 0.15, LIME, 0.4)
    return f

# ---------- S7 gráfica ----------
PTS = [(0, .1), (.15, .18), (.28, .15), (.42, .35), (.55, .32), (.7, .58), (.82, .55), (1, .92)]
def s7(t):  # 5.6
    f = bg_frame(t + 32)
    for j, (txt, col, st) in enumerate([("MÁS PEDIDOS", LIME, 0.2), ("ENTREGAS MÁS RÁPIDAS", CYAN, 1.45), ("CLIENTES QUE VUELVEN", MAG, 3.35)]):
        a = eo(prog(t, st, st + 0.3)); y = 330 + j * 120
        tl = text_layer(txt, 70, WHITE); ar = up_arrow(col, 64)
        tot = ar.width + 20 + tl.width; x = W / 2 - tot / 2
        put(f, ar, x + ar.width / 2, y - (1 - a) * 30, alpha=a); put(f, tl, x + ar.width + 20 + tl.width / 2, y, alpha=a)
    gw, gh = 900, 640
    g = Image.new("RGBA", (gw + 80, gh + 80), (0, 0, 0, 0)); d = ImageDraw.Draw(g)
    for k in range(5):
        y = 40 + gh * k / 4; d.line([(40, y), (40 + gw, y)], fill=(40, 44, 58, 255), width=2)
    p = eio(prog(t, 0.3, 4.6))
    pts = []
    for i in range(len(PTS) - 1):
        (x0, y0), (x1, y1) = PTS[i], PTS[i + 1]
        for s in range(12):
            u = s / 12; pts.append((x0 + (x1 - x0) * u, y0 + (y1 - y0) * u))
    pts.append(PTS[-1])
    vis = [(40 + x * gw, 40 + gh - y * gh) for x, y in pts if x <= p]
    if len(vis) > 1:
        d.polygon(vis + [(vis[-1][0], 40 + gh), (vis[0][0], 40 + gh)], fill=LIME + (40,))
        d.line(vis, fill=LIME + (255,), width=12, joint="curve")
        ex, ey = vis[-1]; d.ellipse((ex - 18, ey - 18, ex + 18, ey + 18), fill=WHITE + (255,))
    g = add_glow(g, LIME, 24, 0.8)
    put(f, g, W / 2, 1150, alpha=eo(prog(t, 0.1, 0.4)))
    put(f, text_layer("TU TALLER", 50, GRAY, path=BOLD), W / 2, 1560, alpha=eo(prog(t, 0.4, 0.7)))
    flash(f, t, 0.12, LIME, 0.3)
    return f

# ---------- S8 herramientas ----------
def s8(t):  # 8.0
    f = bg_frame(t + 38)
    n = int(round(16 * eo(prog(t, 0.15, 1.5))))
    put(f, text_layer(str(n), 280, CYAN, glow=CYAN, gr=60, gs=1.4), W / 2, 400)
    put(f, text_layer("HERRAMIENTAS ONLINE", 74, WHITE), W / 2, 590, alpha=eo(prog(t, 0.3, 0.6)))
    tools = [("QUITAR FONDO", 1.95, MAG), ("VECTORIZAR", 3.0, CYAN), ("SEMITONOS", 4.2, MAG), ("MEJORAR IMAGEN", 4.6, CYAN), ("SIN HALO BLANCO", 5.0, MAG), ("Y MÁS...", 5.4, (90, 96, 120))]
    for j, (txt, st, col) in enumerate(tools):
        a = prog(t, st, st + 0.3)
        r_, c_ = divmod(j, 2); x = 290 + c_ * 500; y = 760 + r_ * 150
        p = pill(460, 112, None, txt, 44, tcolor=WHITE, glow=False, border=col)
        put(f, p, x, y, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
        if a >= 1 and j < 5: put(f, CHECK, x - 200, y - 40, scale=0.45)
    a = prog(t, 6.1, 6.45)
    put(f, pill(860, 150, LIME, "MUCHAS SON GRATIS", 74), W / 2, 1330, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    flash(f, t, 0.15, CYAN, 0.4)
    return f

LG = logo(170)
def s9(t):  # 7.0
    f = bg_frame(t + 46)
    a = prog(t, 0.0, 0.4)
    put(f, LG, W / 2, 360, scale=0.75 + 0.25 * back(a), alpha=clamp(a * 2))
    a = prog(t, 0.2, 0.55)
    put(f, text_layer("HAZ TUS CUENTAS", 100, WHITE, glow=MAG, gr=30, gs=0.9), W / 2, 590, scale=0.6 + 0.4 * back(a), alpha=clamp(a * 2))
    a = prog(t, 1.45, 1.8); pulse = 1 + 0.04 * math.sin(max(0, t - 1.8) * 6.5)
    put(f, pill(800, 170, MAG, "ENTRA HOY", 90, tcolor=WHITE), W / 2, 840, scale=(0.6 + 0.4 * back(a)) * pulse, alpha=clamp(a * 2))
    a = eo(prog(t, 3.4, 3.7))
    put(f, text_layer("neondtf.store/herramientas", 62, CYAN, path=BOLD, glow=CYAN, gr=20, gs=1.0), W / 2, 1030 + (1 - a) * 30, alpha=a)
    a = eo(prog(t, 3.9, 4.2))
    put(f, text_layer("16 herramientas · muchas gratis", 52, GRAY, path=MED), W / 2, 1140, alpha=a)
    a = eo(prog(t, 5.0, 5.3)); ay = 1420 + math.sin(t * 7) * 10
    put(f, text_layer("Link en el perfil", 66, LIME, glow=LIME, gr=20, gs=1.0), W / 2, ay, alpha=a)
    ar = Image.new("RGBA", (120, 120), (0, 0, 0, 0)); ImageDraw.Draw(ar).polygon([(30, 30), (90, 30), (60, 85)], fill=LIME + (255,))
    put(f, ar, W / 2, ay + 90, alpha=a)
    flash(f, t, 0.15, MAG, 0.4)
    return f

SCENES = [("01", 4.1, s1), ("02", 6.8, s2), ("03", 4.3, s3), ("04", 5.7, s4), ("05", 3.5, s5), ("06", 6.5, s6),
          ("07", 5.6, s7), ("08", 8.0, s8), ("09", 7.0, s9)]

def render(idx):
    name, dur, fn = SCENES[idx]
    OUTD = os.path.join(os.getcwd(), "out"); os.makedirs(OUTD, exist_ok=True); out = os.path.join(OUTD, f"{name}.mp4"); tmp = out.replace(".mp4", ".tmp.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
                          "-i", "-", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for k in range(int(round(dur * FPS))):
        p.stdin.write(fn(k / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.replace(tmp, out)
    return name

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        ims = []
        for spec in sys.argv[2:]:
            i, t = spec.split("@"); ims.append(SCENES[int(i)][2](float(t)).convert("RGB").resize((360, 640)))
        c = Image.new("RGB", (360 * len(ims), 640))
        for k, im in enumerate(ims): c.paste(im, (k * 360, 0))
        c.save("prueba.jpg", quality=88)
    else:
        from multiprocessing import Pool
        with Pool(2) as pool:
            for nm in pool.imap_unordered(render, range(len(SCENES))): print("done", nm, flush=True)
