# Arma la línea de tiempo con las 11 voces (vo/l01.wav ... vo/l11.wav): pausas, tiempo de cada palabra y boca abierta/cerrada por cuadro.
# Uso: python scripts/timeline.py   -> timeline.json y voice.wav
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
import json, re, numpy as np, scipy.io.wavfile as W
SR=44100
LINES=[l.strip() for l in """No te vayas, que de seguro te identificas conmigo. Ese día llegué a mi empleo... y me dijeron: estás despedido.
Salí a la calle sin trabajo, sin ahorros... y con las cuentas esperando en casa.
Pasaron semanas. Mandé hojas de vida... y nadie me llamó.
Una noche, sin poder dormir, vi algo en mi celular...
¡Productos de China a precios bajísimos! Y pensé: ¿y si los compro y los vendo yo?
Empecé con una inversión mínima: unos audífonos, unas lámparas y unos relojes.
Cuando llegó el paquete, los publiqué en el Marketplace de Sumiago.
Creé mi tienda con mi propio enlace y la compartí por WhatsApp.
Un mensaje... otro mensaje... ¡y vendí mis primeros productos!
Hoy ya no espero que alguien me dé trabajo. Hoy tengo mi propio negocio.
Entra a sumiago punto com y crea tu tienda al suscribirte. ¡Tu historia también puede cambiar!""".split('\n')]
GAP=[0.6,0.5,0.5,0.6,1.3,0.5,0.5,0.5,0.5,0.6,0.6]  # gap before each line
def env(x,hop):
    n=len(x)//hop; return np.array([np.sqrt((x[i*hop:(i+1)*hop]**2).mean()) for i in range(n)])
t=0.0; out=[]; voice=[]
for i,txt in enumerate(LINES):
    r,x=W.read(f'vo/l{i+1:02d}.wav'); x=x.astype(np.float32)/32768
    e=env(x,441); m=e.max(); on=np.where(e>m*0.06)[0]; s0=on[0]*0.01; s1=(on[-1]+1)*0.01
    x=x[int(max(0,s0-0.03)*SR):int((s1+0.08)*SR)]; e=env(x,441); m=e.max()
    t+=GAP[i]; start=t; dur=len(x)/SR
    # phrase split by silences
    voiced=e>m*0.07
    # find gaps >=0.14s
    gaps=[];k=0
    while k<len(voiced):
        if not voiced[k]:
            j=k
            while j<len(voiced) and not voiced[j]: j+=1
            if (j-k)>=8 and k>0 and j<len(voiced): gaps.append((k,j))
            k=j
        else: k+=1
    words=txt.split()
    ph=[[]]
    for w in words:
        ph[-1].append(w)
        if re.search(r'(\.\.\.|[.,:?!])$',w): ph.append([])
    ph=[p for p in ph if p]
    # assign each phrase boundary to nearest gap by expected position (char proportion), big gaps favored
    vs=np.where(voiced)[0]; v0,v1=vs[0],vs[-1]+1
    tot=sum(len(' '.join(p)) for p in ph); cum=0; chosen=[]; used=set()
    for p in ph[:-1]:
        cum+=len(' '.join(p)); exp=v0+(v1-v0)*cum/tot
        best=None;bs=1e9
        for gi,(g0,g1) in enumerate(gaps):
            if gi in used or (chosen and g0<=chosen[-1][1]): continue
            sc=abs((g0+g1)/2-exp)-(g1-g0)*1.5
            if sc<bs: bs=sc;best=gi
        if best is None or abs((gaps[best][0]+gaps[best][1])/2-exp)>(v1-v0)*0.25: chosen.append(None)
        else: used.add(best); chosen.append(gaps[best])
    # merge phrases whose boundary had no gap
    nph=[ph[0]]; ng=[]
    for p,g in zip(ph[1:],chosen):
        if g is None: nph[-1]=nph[-1]+p
        else: nph.append(p); ng.append(g)
    ph=nph; gaps=ng
    # match gaps to phrase ends by char proportion
    bounds=[0.0]+[g[0]*0.01 for g in gaps]; ends=[g[0]*0.01 for g in gaps]+[v1*0.01]
    starts=[v0*0.01]+[g[1]*0.01 for g in gaps]
    wt=[]
    for p,a,z in zip(ph,starts,ends):
        L=[len(w)+1.5 for w in p]; T=sum(L); c=a
        for w,l in zip(p,L): d=(z-a)*l/T; wt.append((w,round(start+c,3),round(start+c+d,3))); c+=d
    out.append(dict(i=i,text=txt,start=round(start,3),dur=round(dur,3),words=wt))
    voice.append((start,x)); t+=dur
TOTAL=t+3.0
v=np.zeros(int(TOTAL*SR),np.float32)
for s,x in voice: v[int(s*SR):int(s*SR)+len(x)]+=x
W.write('voice.wav',SR,(v*32767).astype(np.int16))
# mouth per frame 30fps
FPS=30; e=env(v,SR//FPS); mo=[]
st=0
for k,val in enumerate(e):
    lm=max(e[max(0,k-15):k+15].max(),1e-4)
    o=1 if val>lm*0.32 else 0
    mo.append(o)
# alternate open/closed during long open runs for movement
for k in range(1,len(mo)):
    if mo[k] and mo[k-1] and k%4==3: mo[k]=0
json.dump(dict(lines=out,total=round(TOTAL,3),mouth=mo),open('timeline.json','w'),ensure_ascii=False)
for o in out: print(o['i'],o['start'],o['dur'],[w for w in o['words']][:3])
print('TOTAL',TOTAL)
