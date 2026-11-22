"""Fondo de la versión PC 16:9: logo, título, mascota con el pulgar y el hueco redondeado para el video vertical.
Uso: python scripts/pc.py   -> pcbg.png y pcmask.png
"""
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
from PIL import Image, ImageDraw, ImageFilter
from render import F, LOGO, PULGAR, RED, DARK, GREY, shadow_card, text_c
W,H=1920,1080; VX,VY,VW,VH=1262,40,562,1000
bg=Image.new('RGBA',(W,H),(255,255,255,255))
g=Image.new('RGBA',(W,H),(0,0,0,0)); gd=ImageDraw.Draw(g); gd.ellipse((-200,100,900,900),fill=(220,24,38,22)); gd.ellipse((1100,0,2100,1000),fill=(220,24,38,18)); bg.alpha_composite(g.filter(ImageFilter.GaussianBlur(120)))
d=ImageDraw.Draw(bg)
for x in range(0,W,60): d.line((x,0,x,H),fill=(244,244,246),width=2)
for y in range(0,H,60): d.line((0,y,W,y),fill=(244,244,246),width=2)
bg.alpha_composite(LOGO.resize((330,110),Image.LANCZOS),(120,105))
d=ImageDraw.Draw(bg)
d.rounded_rectangle((128,290,468,346),28,fill=RED); text_c(d,(298,318),'HISTORIA QUE INSPIRA',F(26),(255,255,255))
d.text((124,375),'De desempleado',font=F(66),fill=DARK); d.text((124,460),'a vender en',font=F(66),fill=DARK); d.text((124,545),'Sumiago',font=F(74),fill=RED)
d.text((128,665),'Compra en China con poca inversión',font=F(30,'Regular'),fill=(80,82,90)); d.text((128,707),'y vende en el Marketplace de Sumiago.',font=F(30,'Regular'),fill=(80,82,90))
d.rounded_rectangle((128,790,468,870),40,fill=(255,255,255),outline=RED,width=4); text_c(d,(298,830),'sumiago.com',F(36),DARK)
m=PULGAR.resize((int(1199*0.62),int(1312*0.62)),Image.LANCZOS)
sh=Image.new('RGBA',(W,H),(0,0,0,0)); ImageDraw.Draw(sh).ellipse((700,1000,1140,1050),fill=(0,0,0,45)); bg.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
bg.alpha_composite(m,(560,1030-m.height))
shadow_card(bg,(VX-12,VY-12,VX+VW+12,VY+VH+12),44,(30,30,34),24,14,80)
bg.convert('RGB').save('pcbg.png')
mask=Image.new('L',(VW,VH),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,VW-1,VH-1),34,fill=255); mask.save('pcmask.png')
