"""Arma el video completo: escenas + música + voz + cierre de Sumiago.
Uso:  python scripts/armar.py          (después de voz.py)
Salida: out/neondtf-las-cuentas.mp4
"""
import os, subprocess, sys
AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import escenas

OFFSETS = [0.2] + [0.15] * 8   # segundos desde el inicio de cada escena hasta que empieza su frase
NOMBRE = "neondtf-las-cuentas"
os.makedirs("out", exist_ok=True)

def run(*a): subprocess.run(list(a), check=True)
def py(script, *a): run(sys.executable, os.path.join(AQUI, script), *a)

durs = [d for _, d, _ in escenas.SCENES]
starts = [sum(durs[:i]) for i in range(len(durs))]
total = sum(durs)
n = len(durs)
for i in range(n + 1):
    if not os.path.isfile(f"vo/{i:02d}.wav"):
        sys.exit(f"Falta vo/{i:02d}.wav: corre primero scripts/voz.py")
    d = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", f"vo/{i:02d}.wav"]))
    lim = (durs[i] - OFFSETS[i]) if i < n else 6.6
    if d > lim:
        print(f"AVISO: la frase {i + 1} dura {d:.2f}s y su escena deja {lim:.2f}s; se montará sobre la siguiente. Acorta la frase o alarga la escena.")

py("escenas.py", "render")
py("musica.py")
py("cierre.py", "render")
py("musica_cierre.py")

ins, fl = [], []
for i in range(n):
    ins += ["-i", f"vo/{i:02d}.wav"]; ms = int((starts[i] + OFFSETS[i]) * 1000)
    fl.append(f"[{i}:a]adelay={ms}|{ms}[v{i}]")
fl.append("".join(f"[v{i}]" for i in range(n)) + f"amix=inputs={n}:normalize=0,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,volume=1.6,apad=whole_dur={total}[vo]")
run("ffmpeg", "-nostdin", "-y", "-v", "error", *ins, "-filter_complex", ";".join(fl), "-map", "[vo]", "-t", str(total), "out/voz.wav")
DUCK = "[1:a]asplit[vk][vm];[0:a]volume=0.55[m];[m][vk]sidechaincompress=threshold=0.03:ratio=6:attack=10:release=300[md];[md][vm]amix=inputs=2:normalize=0,alimiter=limit=0.95[a]"
run("ffmpeg", "-nostdin", "-y", "-v", "error", "-i", "out/music.wav", "-i", "out/voz.wav", "-filter_complex", DUCK, "-map", "[a]", "-ar", "44100", "out/mezcla.wav")
run("ffmpeg", "-nostdin", "-y", "-v", "error", "-i", "out/musica_cierre.wav", "-i", f"vo/{n:02d}.wav", "-filter_complex",
    "[1:a]adelay=300|300,highpass=f=80,acompressor=threshold=-18dB:ratio=3:attack=5:release=120,volume=1.6,apad=whole_dur=7[v];" + DUCK.replace("[1:a]asplit", "[v]asplit"),
    "-map", "[a]", "-t", "7", "-ar", "44100", "out/mezcla_cierre.wav")
with open("out/lista.txt", "w") as f:
    for nm, _, _ in escenas.SCENES: f.write(f"file '{nm}.mp4'\n")
    f.write("file 'cierre.mp4'\n")
run("ffmpeg", "-nostdin", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", "out/lista.txt", "-c", "copy", "out/video_mudo.mp4")
run("ffmpeg", "-nostdin", "-y", "-v", "error", "-i", "out/mezcla.wav", "-i", "out/mezcla_cierre.wav", "-filter_complex", "[0:a][1:a]concat=n=2:v=0:a=1[a]", "-map", "[a]", "out/audio_final.wav")
run("ffmpeg", "-nostdin", "-y", "-v", "error", "-i", "out/video_mudo.mp4", "-i", "out/audio_final.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", f"out/{NOMBRE}.mp4")
print("Listo: out/" + NOMBRE + ".mp4")
