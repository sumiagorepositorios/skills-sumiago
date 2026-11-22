"""Inicio de cada escena (SC) y ayudas de tiempo (W = segundo en que suena una palabra). La usan render.py y audio.py.
"""
import os, sys
_AQUI = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, _AQUI)
_ASSETS = os.path.join(_AQUI, '..', 'assets') + os.sep
import json
TL=json.load(open('timeline.json')); L=TL['lines']; TOTAL=TL['total']
GAP=[0.6,0.5,0.5,0.6,1.3,0.5,0.5,0.5,0.5,0.6,0.6]
def W(i,word):
    for w,a,b in L[i]['words']:
        if w.lower().strip('¡!¿?.,:').startswith(word): return a
    raise KeyError(word)
SC=[0.0]+[round(L[i]['start']-GAP[i]*0.55,3) for i in range(1,11)]
SE=SC[1:]+[TOTAL]
IDEA=SC[4]
