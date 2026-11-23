import json, os, urllib.request, concurrent.futures as cf, time
KEY=os.environ['FISH_KEY']; V='bd35c17b29c54d3e9d2663863a28d212'
L=json.load(open('lineas.json'))
def tts(x):
    out=f"voz/{x['lang']}-{x['id']}.mp3"
    if os.path.exists(out) and os.path.getsize(out)>1000: return out,'ya'
    body=json.dumps({'text':x['text'],'reference_id':V,'format':'mp3','latency':'normal'}).encode()
    for k in range(3):
        try:
            r=urllib.request.Request('https://api.fish.audio/v1/tts',data=body,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','model':'s1'})
            d=urllib.request.urlopen(r,timeout=180).read()
            if len(d)>1000: open(out,'wb').write(d); return out,len(d)
        except Exception as e: err=e; time.sleep(3)
    return out,'ERROR '+str(err)
with cf.ThreadPoolExecutor(4) as ex:
    for r in ex.map(tts,L): print(r, flush=True)
