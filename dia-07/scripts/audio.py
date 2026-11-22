"""Música propia, efectos (lluvia, trueno, papel, notificaciones, monedas...) y la voz, con la música que baja cuando habla.
Uso: python scripts/audio.py   -> audio.wav
"""
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
import numpy as np, scipy.io.wavfile as Wv
from scipy.signal import butter, lfilter
from scenes import *
SR=44100; N=int(TOTAL*SR); rng=np.random.default_rng(7)
def T(d): return np.arange(int(d*SR))/SR
def bp(x,lo,hi):
    b,a=butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return lfilter(b,a,x)
def lp(x,f):
    b,a=butter(2,f/(SR/2)); return lfilter(b,a,x)
def add(buf,t,x,g=1.0):
    i=int(t*SR); j=min(len(buf),i+len(x)); 
    if i<len(buf): buf[i:j]+=x[:j-i]*g
def tone(f,d,dec=4,harm=(1,.5,.25,.12)):
    t=T(d); return sum(h*np.sin(2*np.pi*f*(k+1)*t) for k,h in enumerate(harm))*np.exp(-dec*t)
def whoosh(d=0.45,up=True):
    n=rng.standard_normal(int(d*SR)); t=T(d); out=np.zeros_like(n)
    seg=256
    for k in range(0,len(n),seg):
        fr=k/len(n); f=300+ (2500*fr if up else 2500*(1-fr))
        out[k:k+seg]=bp(n[max(0,k-2048):k+seg],f*0.6,min(f*1.6,18000))[-len(n[k:k+seg]):]
    return out*np.sin(np.pi*t/d)**2*0.5
def thud(): t=T(.5); return np.sin(2*np.pi*(60+80*np.exp(-20*t))*t)*np.exp(-8*t)*1.0

def knock():
    o=np.zeros(int(.5*SR)); k=np.sin(2*np.pi*180*T(.08))*np.exp(-45*T(.08))+bp(rng.standard_normal(int(.08*SR)),300,1500)*np.exp(-50*T(.08))*.6
    o[:len(k)]+=k; o[int(.2*SR):int(.2*SR)+len(k)]+=k; return o*0.9
def ding(f=1320): return tone(f,1.2,3.5,(1,.3,.15))*0.35+np.pad(tone(f*1.5,1.0,5,(1,)),(0,int(.2*SR)))*0.12
def notif(): o=np.zeros(int(.6*SR)); a=tone(988,.3,8,(1,.2)); b=tone(1319,.45,7,(1,.2)); o[:len(a)]+=a; o[int(.12*SR):int(.12*SR)+len(b)]+=b; return o*0.35
def pop(): t=T(.12); return np.sin(2*np.pi*(900-600*t/.12)*t)*np.exp(-30*t)*0.45
def click(): return bp(rng.standard_normal(int(.03*SR)),2000,8000)*np.exp(-150*T(.03))*0.6
def cash():
    o=np.zeros(int(1.2*SR)); add(o,0,ding(2093)*1.2); add(o,0.05,ding(2637))
    for k in range(10): add(o,0.12+k*0.04,tone(3000+rng.random()*3000,.15,25,(1,))*0.12)
    return o
def sparkle():
    o=np.zeros(int(1.2*SR))
    for k in range(8): add(o,k*0.07,tone(1800+k*220,.4,10,(1,))*0.15)
    return o
def riser(d=1.2):
    t=T(d); n=rng.standard_normal(len(t)); return bp(n,800,6000)*(t/d)**2*0.35+np.sin(2*np.pi*(200+600*(t/d)**2)*t)*(t/d)**2*0.15
def thunder():
    d=2.5; t=T(d); n=lp(rng.standard_normal(len(t)),180)*3
    return n*np.exp(-1.6*t)*(1-np.exp(-30*t))*1.2
def rainloop(d):
    n=rng.standard_normal(int(d*SR)); r=bp(n,1500,8000)*0.07
    for k in range(int(d*30)): add(r,rng.random()*d,tone(2500+rng.random()*3000,.02,200,(1,))*0.08)
    return r
def tick(): return bp(rng.standard_normal(int(.02*SR)),3000,9000)*np.exp(-200*T(.02))*0.35
def paper(): t=T(.5); return bp(rng.standard_normal(len(t)),2000,9000)*np.exp(-6*t)*(np.sin(2*np.pi*14*t)**2)*0.35
def boo(): # sad trombone-ish soft descending
    o=np.zeros(int(1.6*SR))
    for k,f in enumerate([392,370,349,330]): add(o,k*0.32,tone(f,.5 if k<3 else .9,3,(1,.6,.4,.2))*0.12)
    return o
# ---------- music
def piano(f,d): t=T(d); return (np.sin(2*np.pi*f*t)+.4*np.sin(4*np.pi*f*t)+.15*np.sin(6*np.pi*f*t))*np.exp(-2.2*t)*(1-np.exp(-200*t))
NOTE=lambda n:440*2**((n-69)/12)
mus=np.zeros(N)
# sad: 66bpm, Am F C G
beat=60/66; chords=[(57,60,64),(53,57,60),(48,55,60),(55,59,62)]; t=0.3; k=0
while t<IDEA-0.3:
    ch=chords[(k//8)%4]; arp=[ch[0],ch[1],ch[2],ch[1]+12 if k%8==3 else ch[2]+12,ch[2],ch[1],ch[0]+12,ch[2]]
    add(mus,t,piano(NOTE(arp[k%8]+12),beat*2.2),0.09)
    if k%8==0:
        add(mus,t,piano(NOTE(ch[0]-12),beat*4),0.12)
        pad=sum(np.sin(2*np.pi*NOTE(n)*T(beat*4)) for n in ch)*np.sin(np.pi*T(beat*4)/(beat*4))
        add(mus,t,pad,0.025)
    t+=beat/2; k+=1
# happy: 112bpm C G Am F
beat=60/112; t=IDEA+0.45; k=0; hc=[(60,64,67),(55,59,62),(57,60,64),(53,57,60)]
end=TOTAL-0.6
while t<end:
    ch=hc[(k//16)%4]
    pl=tone(NOTE(ch[(k%4) if k%4<3 else 1]+12+ (12 if k%8>=4 else 0)),beat*0.6,9,(1,.4,.2)); add(mus,t,pl,0.07)
    if k%4==0:
        kk=np.sin(2*np.pi*(50+120*np.exp(-30*T(.3)))*T(.3))*np.exp(-9*T(.3)); add(mus,t,kk,0.35)
        add(mus,t,np.sin(2*np.pi*NOTE(ch[0]-24)*T(beat*0.9))*np.exp(-2*T(beat*0.9)),0.18)
    if k%8==4: add(mus,t,bp(rng.standard_normal(int(.15*SR)),900,5000)*np.exp(-25*T(.15)),0.18)
    if k%2==1: add(mus,t,bp(rng.standard_normal(int(.04*SR)),7000,15000)*np.exp(-90*T(.04)),0.07)
    t+=beat/4; k+=1
# fade end
fe=int((TOTAL-1.6)*SR); mus[fe:]*=np.linspace(1,0,N-fe)
# ---------- sfx
sfx=np.zeros(N)
for i in range(1,11): add(sfx,SC[i]-0.2,whoosh(0.45),0.35 if i<4 else 0.7)
add(sfx,W(0,'ese'),paper(),0.6)
add(sfx,W(0,'despedido'),thud(),0.9); add(sfx,W(0,'despedido')+0.15,boo(),1.0)
r=rainloop(SE[1]-SC[1]); r*=np.minimum(1,np.minimum(np.arange(len(r))/SR/0.4,(len(r)/SR-np.arange(len(r))/SR)/0.4)); add(sfx,SC[1],r,1.0)
add(sfx,SC[1]+0.35,thunder(),0.9)
tt=SC[2]+0.2
while tt<SE[2]-0.2: add(sfx,tt,tick(),1.0); tt+=0.5
add(sfx,W(2,'nadie'),boo(),0.5)
add(sfx,W(3,'celular')-0.1,notif(),1.0)
add(sfx,IDEA-1.1,riser(1.2),1.0); add(sfx,IDEA+0.1,ding(1568),1.2); add(sfx,IDEA+0.1,sparkle(),0.8)
for w in ('productos','china','precios'): add(sfx,W(4,w),pop(),0.8)
add(sfx,W(4,'vendo'),ding(1760),0.6)
for w in ('audífonos','lámparas','relojes'): add(sfx,W(5,w),pop(),0.9); add(sfx,W(5,w)+0.05,click(),0.8)
add(sfx,W(5,'inversión'),sparkle(),0.6)
add(sfx,SC[6]+0.15,knock(),1.0); add(sfx,SC[6]+0.75,thud(),0.7)
add(sfx,W(6,'publiqué'),pop(),0.8); add(sfx,W(6,'marketplace'),sparkle(),0.6)
add(sfx,W(7,'tienda'),pop(),0.8); add(sfx,W(7,'whatsapp'),whoosh(0.4),0.6); add(sfx,W(7,'whatsapp')+0.35,notif(),0.8)
add(sfx,W(8,'un'),notif(),1.0); add(sfx,W(8,'otro'),notif(),1.0); add(sfx,W(8,'vendí'),cash(),1.1)
add(sfx,W(9,'negocio'),sparkle(),0.9); add(sfx,W(9,'negocio'),pop(),0.8)
add(sfx,W(10,'sumiago'),pop(),0.8); add(sfx,W(10,'suscribirte'),ding(1568),0.6); add(sfx,W(10,'cambiar')+0.3,sparkle(),1.0)
# ---------- mix
sr,v=Wv.read('voice.wav'); v=v.astype(float)/32768; v=np.pad(v,(0,max(0,N-len(v))))[:N]
envv=np.convolve(np.abs(v),np.ones(4410)/4410,'same'); duck=1-0.7*np.clip(envv/0.03,0,1)
duck=np.convolve(duck,np.ones(2205)/2205,'same')
mix=v*1.0+mus*duck*0.2+sfx*0.32
mix/=max(1e-6,np.abs(mix).max())/0.9
Wv.write('audio.wav',SR,(mix*32767).astype(np.int16))
print('ok',TOTAL)
