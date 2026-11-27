"""Música (sintetizada, sin copyright), efectos y voz con ducking -> fx.wav. Requiere vt/*.wav y dur.json."""
import numpy as np, wave
SR=44100; import json as _j; T=sum(_j.load(open('dur.json')))+.2; N=int(SR*T)
rng=np.random.default_rng(7)
mus=np.zeros(N); sfx=np.zeros(N)
def add(buf,t,sig,g=1.0):
    i=int(t*SR); j=min(N,i+len(sig)); buf[i:j]+=sig[:j-i]*g
def env(n,a=.005,r=.1):
    t=np.arange(n)/SR; return np.minimum(1,t/a)*np.exp(-t/r)
# --- music: 100 bpm, minor pad + kick + hats
bpm=100; beat=60/bpm
chords=[[57,60,64],[53,57,60],[48,52,55],[55,59,62]]  # Am F C G
f=lambda m:440*2**((m-69)/12)
bar=beat*4
for b in range(int(T/bar)+1):
    ch=chords[b%4]; n=int(bar*SR); t=np.arange(n)/SR
    pad=sum(np.sin(2*np.pi*f(m)*t)+.3*np.sin(2*np.pi*f(m)*2*t) for m in ch)
    pad*=np.minimum(1,t/.4)*np.minimum(1,(bar-t)/.3)*.05
    add(mus,b*bar,pad)
    bass=np.sin(2*np.pi*f(ch[0]-24)*t)*np.exp(-t/1.2)*.12; add(mus,b*bar,bass)
for k in range(int(T/beat)):
    t=np.arange(int(.35*SR))/SR
    if k%2==0: add(mus,k*beat,np.sin(2*np.pi*(50+90*np.exp(-t*30))*t)*np.exp(-t/.12)*.35)
    else: add(mus,k*beat,rng.standard_normal(len(t))*np.exp(-t/.06)*.05)
    add(mus,k*beat+beat/2,np.diff(rng.standard_normal(int(.05*SR)),prepend=0)*np.exp(-np.arange(int(.05*SR))/SR/.012)*.04)
# --- sfx
def whoosh(d=.35):
    n=int(d*SR); x=rng.standard_normal(n); t=np.arange(n)/SR
    y=np.convolve(x,np.ones(30)/30,'same')*np.sin(np.pi*t/d)**2; return y*.6
def click(): n=int(.04*SR); return rng.standard_normal(n)*env(n,.0005,.006)*.5
def tick(): n=int(.03*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*2600*t)+rng.standard_normal(n)*.5)*env(n,.0005,.005)*.18
def pop(fr=520):
    n=int(.18*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*fr*(1+2*np.exp(-t*40))*t)*env(n,.002,.06)*.4
def swipe():
    n=int(.25*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*(300+2500*t/.25)*t)*np.sin(np.pi*t/.25)*.12+whoosh(.25)*.3
def hit():
    n=int(1.2*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*(45+60*np.exp(-t*8))*t)*np.exp(-t/.5)*.8+rng.standard_normal(n)*np.exp(-t/.08)*.2)
def ding():
    n=int(1.0*SR); t=np.arange(n)/SR; return sum(np.sin(2*np.pi*fr*t)*np.exp(-t/.35) for fr in (1318,1976))*.18
import json, os
D=json.load(open('dur.json')); starts=[sum(D[:i]) for i in range(len(D))]
S=lambda k,t: starts[k]+t
for s_ in starts[1:]: add(sfx,s_-.18,whoosh(),.7)
def down():
    n=int(.9*SR); t=np.arange(n)/SR; return np.sin(2*np.pi*(420*np.exp(-t*1.6))*t)*np.exp(-t/.45)*.3
for i in range(6): add(sfx,.55+i/12,tick())                      # escribe TikTok
for i in range(18): add(sfx,S(11,1.0+i/12),tick(),.7)            # "Hola, bienvenidos…"
for i in range(7): add(sfx,S(14,2.7+i/8),tick())                 # escribe SUMIAGO
for i in range(4): add(sfx,S(5,.7+i/1.6),tick(),1.4)             # reloj 0:00 -> 0:03
for k,t in ((2,2.15),(2,2.3),(11,2.7)): add(sfx,S(k,t),swipe())   # tachados
pops=[(0,1.6),(2,.15),(4,.15),(4,.7),(4,.82),(4,.94),(4,1.06),(5,0),(6,0),(7,0),(7,1.3),(8,0),(8,.5),(8,.72),(8,.94),
      (9,.25),(9,1.0),(9,2.2),(9,3.4),(12,.6),(15,.1),(15,.7)]+[(3,.9+i*.1) for i in range(7)]
for k,t in pops: add(sfx,S(k,t),pop(480+(S(k,t)*37)%300))
for k,t in ((2,.95),(14,4.1)): add(sfx,S(k,t),click())
for k in (1,11,15): add(sfx,S(k,0),hit(),.8)
add(sfx,S(10,.5),down()); add(sfx,S(11,3.0),down(),.6)
for k,t in ((6,2.3),(12,1.0),(14,4.1)): add(sfx,S(k,t),ding())
# voz
import wave as _w
vo=np.zeros(N)
for i in range(15):
    p=f'vt/{i:02d}.wav'
    if not os.path.exists(p): continue
    with _w.open(p) as w: x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768; sr=w.getframerate()
    if sr!=SR: x=np.interp(np.arange(int(len(x)*SR/sr))*sr/SR,np.arange(len(x)),x)
    x=x/ (np.abs(x).max()+1e-9)*.9
    add(vo,starts[i]+.1,x)
# ducking: bajar música cuando habla
envv=np.convolve(np.abs(vo),np.ones(4410)/4410,'same'); duck=1-.55*np.clip(envv*12,0,1)
mus*=duck
# fade music at end
fade=np.ones(N); e=int(starts[-1]*SR); fade[e:]=np.linspace(1,.3,N-e)
out=mus*fade*.45+sfx*.55+vo*1.0
out=np.tanh(out*1.2)*.8
st=np.stack([out,out],1)
with wave.open('fx.wav','wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st*32767).astype('<i2').tobytes())
print('ok')
