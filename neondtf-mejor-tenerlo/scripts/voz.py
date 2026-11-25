"""Genera la voz del guion con Fish Audio, una línea por archivo.
Uso:  python scripts/voz.py
Requiere la variable de entorno FISH_API_KEY. Nunca escribas la clave en este archivo ni la subas a GitHub.
Opcionales: FISH_VOICE_ID (voz) y FISH_MODEL (modelo; si tu cuenta no tiene crédito de API usa s2.1-pro-free).
Salida: vo/00.wav, vo/01.wav... (sin silencios al inicio y al final), en la carpeta actual.
"""
import json, os, subprocess, sys, urllib.request

KEY = os.environ.get("FISH_API_KEY")
VOZ = os.environ.get("FISH_VOICE_ID", "8730dce743254904a745d6e134e18c6b")
MODELO = os.environ.get("FISH_MODEL", "s1")
if not KEY:
    sys.exit("Falta FISH_API_KEY. En Windows: set FISH_API_KEY=tu_clave")
FILTRO = ("silenceremove=start_periods=1:start_threshold=-45dB,areverse,"
          "silenceremove=start_periods=1:start_threshold=-45dB,areverse")
guion = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "guion.txt")
lineas = [l.strip() for l in open(guion, encoding="utf-8") if l.strip()]
os.makedirs("vo", exist_ok=True)
for i, l in enumerate(lineas):
    req = urllib.request.Request("https://api.fish.audio/v1/tts",
        data=json.dumps({"text": l, "reference_id": VOZ, "format": "wav", "normalize": True}).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json", "model": MODELO})
    crudo, wav = f"vo/{i:02d}_crudo.wav", f"vo/{i:02d}.wav"
    open(crudo, "wb").write(urllib.request.urlopen(req, timeout=120).read())
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y", "-i", crudo, "-af", FILTRO, "-ar", "44100", "-ac", "2", wav], check=True)
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav]))
    print(f"{i + 1}/{len(lineas)}  {d:.2f}s  {l[:60]}")
