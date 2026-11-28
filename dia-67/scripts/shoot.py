"""Dibuja el video cuadro por cuadro con Chrome (Playwright) desde anim.html.
Uso:  python scripts/shoot.py full      -> video_tmp.mp4 (sin sonido)
      python scripts/shoot.py test 2.3,19.5  -> t00.jpg, t01.jpg ...
"""
import sys, os, shutil, subprocess, asyncio
from playwright.async_api import async_playwright

mode = sys.argv[1]  # "test" or "full"
FPS = 30
AQUI = os.path.dirname(os.path.abspath(__file__))
shutil.copy(os.path.join(AQUI, "anim.html"), "anim.html")
shutil.copy(os.path.join(AQUI, "..", "assets", "logo-sumiago.png"), "logo-sumiago.png")
CHROME = os.environ.get("CHROME")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files"])
        pg = await b.new_page(viewport={"width": 1080, "height": 1920})
        await pg.goto("file://" + os.path.abspath("anim.html").replace(os.sep, "/"))
        await pg.wait_for_timeout(500)
        total = await pg.evaluate("TOTAL")
        if mode == "test":
            times = [float(x) for x in sys.argv[2].split(",")]
            for i, t in enumerate(times):
                await pg.evaluate(f"render({t})")
                await pg.screenshot(path=f"t{i:02d}.jpg", type="jpeg", quality=80)
            print("total", total)
        else:
            n = int(total * FPS)
            ff = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-",
                                   "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-pix_fmt", "yuv420p", "video_tmp.mp4"],
                                  stdin=subprocess.PIPE)
            for f in range(n):
                await pg.evaluate(f"render({f / FPS})")
                ff.stdin.write(await pg.screenshot(type="jpeg", quality=92))
            ff.stdin.close(); ff.wait()
            print("frames", n, "rc", ff.returncode)
        await b.close()

asyncio.run(main())
