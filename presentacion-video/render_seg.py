import asyncio, sys, subprocess, base64
from playwright.async_api import async_playwright
lang, o, sid = sys.argv[1], sys.argv[2], sys.argv[3]; FPS = 25
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        vp = {'width':1920,'height':1080} if o=='h' else {'width':1080,'height':1920}
        pg = await b.new_page(viewport=vp)
        await pg.goto(f'http://127.0.0.1:8100/render.php?lang={lang}&o={o}'); await pg.wait_for_function('window.__ready'); await pg.wait_for_timeout(2000)
        cdp = await pg.context.new_cdp_session(pg)
        ids = await pg.evaluate('DATA.map(s=>s.id)'); i = ids.index(sid); L = await pg.evaluate(f'DATA[{i}].L')
        ff = subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-r',str(FPS),f'/home/claude/pres/out/seg-{lang}-{o}-{sid}.mp4'], stdin=subprocess.PIPE)
        for f in range(round(L*FPS)):
            await pg.evaluate(f'seek({i},{f/FPS})')
            if f==0: await pg.wait_for_timeout(400); await pg.evaluate(f'seek({i},0)')
            r = await cdp.send('Page.captureScreenshot',{'format':'jpeg','quality':90}); ff.stdin.write(base64.b64decode(r['data']))
        ff.stdin.close(); ff.wait(); await b.close(); print('ok', sid, round(L*FPS))
asyncio.run(main())
