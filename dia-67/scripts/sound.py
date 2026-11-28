"""Música (sintetizada, sin copyright), efectos y voz con ducking -> fx.wav. Requiere vt/*.wav, dur.json y k.json."""
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
KK=json.load(open('k.json')) if os.path.exists('k.json') else [1]*len(D)
S=lambda k,t: starts[k]+t/KK[k]
for s_ in starts[1:]: add(sfx,s_-.18,whoosh(),.7)
for i in range(7): add(sfx,S(5,.3+i*.32),tick(),.8)
for i in range(7): add(sfx,S(14,1.8+i/8),tick())
for k,t in ((0,1.9),(11,1.1)): add(sfx,S(k,t),swipe())
for k,t in ((0,.45),(0,.6),(2,.85),(2,1.1),(2,1.25),(2,1.4),(3,.1),(3,.9),(3,1.08),(3,1.26),(4,0),(4,1.0),(4,1.2),(4,1.4),(4,1.6),(6,0),(7,.8),(7,1.25),(7,1.7),(8,0),(10,.8),(10,1.3),(12,.4),(13,1.6),(14,.6),(15,.1),(15,.9)): add(sfx,S(k,t),pop(480+(S(k,t)*37)%300))
for k,t in ((9,.6),(9,1.4),(9,2.2),(14,3.4)): add(sfx,S(k,t),click())
for k in (1,11,15): add(sfx,S(k,0),hit(),.9)
for k,t in ((13,2.2),(14,3.45)): add(sfx,S(k,t),ding())
# voz
import wave as _w
vo=np.zeros(N)
for i in range(15):
    p=f'vt/{i:02d}.wav'
    if not os.path.exists(p): continue
    with _w.open(p) as w: x=np.frombuffer(w.readframes(w.getnframes()),'<i2').astype(float)/32768; sr=w.getframerate()
    if sr!=SR: x=np.interp(np.arange(int(len(x)*SR/sr))*sr/SR,np.arange(len(x)),x)
    x=x/ (np.abs(x).max()+1e-9)*.9
    add(vo,starts[i]+.05,x)
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
