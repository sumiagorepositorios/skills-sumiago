import json,os,sys,urllib.request
KEY=os.environ['FISH_KEY']; V='bd35c17b29c54d3e9d2663863a28d212'
text,out=sys.argv[1],sys.argv[2]
body=json.dumps({'text':text,'reference_id':V,'format':'mp3','latency':'normal','temperature':0.6,'top_p':0.7}).encode()
r=urllib.request.Request('https://api.fish.audio/v1/tts',data=body,headers={'Authorization':'Bearer '+KEY,'Content-Type':'application/json','model':'s1'})
open(out,'wb').write(urllib.request.urlopen(r,timeout=180).read())
