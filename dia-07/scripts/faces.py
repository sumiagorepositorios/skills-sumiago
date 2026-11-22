"""Caras de la mascota (boca abierta/cerrada, triste/feliz, ojos cerrados) a partir de assets/sumiago-a.png y sumiago-c.png. La usa render.py.
"""
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
from PIL import Image, ImageDraw
import numpy as np
A=Image.open(_ASSETS + 'sumiago-a.png').convert('RGBA'); C=Image.open(_ASSETS + 'sumiago-c.png').convert('RGBA')
BOX=(17,0,1153,1312)
def fillskin(im, x0,y0,x1,y1, ya, yb):
    a=np.array(im).astype(float)
    top=a[ya,x0:x1,:3]; bot=a[yb,x0:x1,:3]
    for y in range(y0,y1):
        t=(y-ya)/(yb-ya); a[y,x0:x1,:3]=top*(1-t)+bot*t
    return Image.fromarray(a.astype('uint8'),'RGBA')
def sad(base_open):
    src = A if base_open else C
    im = fillskin(C, 540,334,662,394, 333,394)   # clean mouth
    # flipped mouth: take mouth area of src, flip vertically
    m = src.crop((546,334,656,392))
    if base_open:
        m = m.transpose(Image.FLIP_TOP_BOTTOM)
        mask = Image.open(_ASSETS + 'sumiago-a.png').convert('RGBA').crop((546,334,656,392)).transpose(Image.FLIP_TOP_BOTTOM)
        # only take non-skin pixels (dark/red) of mouth
        arr=np.array(m).astype(int); sk=np.array([252,192,120])
        d=np.abs(arr[:,:,:3]-sk).sum(2); al=np.clip((d-60)*4,0,255).astype('uint8')
        mm=Image.fromarray(al,'L').resize((88,40))
        m=m.resize((88,40)); im.paste(m,(556,350),mm)
    else:
        d=ImageDraw.Draw(im)
        d.arc((560,362,640,410),200,340,fill=(92,34,22),width=9)
    # sad brows: clean and redraw slanted
    im = fillskin(im, 485,226,575,258, 224,258)
    im = fillskin(im, 628,229,715,258, 227,258)
    d=ImageDraw.Draw(im)
    d.polygon([(487,250),(572,232),(575,246),(490,262)],fill=(70,32,12))
    d.polygon([(630,232),(713,250),(710,262),(627,246)],fill=(70,32,12))
    return im
def blink(im):
    a=np.array(im)
    for x0,x1 in ((497,574),(632,708)):
        a[255:322,x0:x1,:3]=a[324,x0:x1,:3][None,:,:]
    im=Image.fromarray(a,'RGBA')
    d=ImageDraw.Draw(im); d.line((502,300,569,300),fill=(60,26,10),width=7); d.line((637,300,703,300),fill=(60,26,10),width=7)
    return im
V={}
V[('happy',0)]=C; V[('happy',1)]=A
V[('sad',0)]=sad(False); V[('sad',1)]=sad(True)
for k in list(V): V[k+('b',)]=blink(V[k])
if __name__=='__main__':
    ims=[V[k].crop((420,190,780,430)) for k in [('happy',0),('happy',1),('sad',0),('sad',1),('sad',0,'b')]]
    c=Image.new('RGB',(360*5,240),(0,150,0))
    for i,m in enumerate(ims): c.paste(m,(i*360,0),m)
    c.save('ref/faces.png')
