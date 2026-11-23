import asyncio, sys, subprocess, time, base64
from playwright.async_api import async_playwright
lang, o = sys.argv[1], sys.argv[2]; FPS = 25
out = f'/home/claude/pres/out/vid-{lang}-{o}.mp4'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        vp = {'width':1920,'height':1080} if o=='h' else {'width':1080,'height':1920}
        pg = await b.new_page(viewport=vp)
        await pg.goto(f'http://127.0.0.1:8100/render.php?lang={lang}&o={o}'); await pg.wait_for_function('window.__ready'); await pg.wait_for_timeout(2000)
        cdp = await pg.context.new_cdp_session(pg)
        Ls = await pg.evaluate('DATA.map(s=>s.L)')
        ff = subprocess.Popen(['ffmpeg','-y','-v','error','-f','image2pipe','-framerate',str(FPS),'-c:v','mjpeg','-i','-','-c:v','libx264','-preset','veryfast','-crf','22','-pix_fmt','yuv420p','-r',str(FPS),out], stdin=subprocess.PIPE)
        t0=time.time(); n=0
        for i,L in enumerate(Ls):
            nf = round(L*FPS)
            for f in range(nf):
                await pg.evaluate(f'seek({i},{f/FPS})')
                if f==0: await pg.wait_for_timeout(400); await pg.evaluate(f'seek({i},0)')
                r = await cdp.send('Page.captureScreenshot',{'format':'jpeg','quality':90})
                ff.stdin.write(base64.b64decode(r['data'])); n+=1
            print(f'{lang}-{o} seg {i+1}/{len(Ls)} frames {n} {time.time()-t0:.0f}s', flush=True)
        ff.stdin.close(); ff.wait(); await b.close()
asyncio.run(main())
