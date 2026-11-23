---
name: presentacion-video
description: Rehacer la Presentación de Negocio en video de Sumiago (es/en, 16:9 y 9:16) con cámara, máscaras, transiciones, música, efectos y voz Fish sincronizada.
---
Rutas absolutas pensadas para /home/claude/pres (copiar esta carpeta allí) y el repo binantrader en /home/claude/binantrader.
1. `lineas.json` sale de `sumiago/assets/tareas/presentacion-video/guion.json`. Voz: `FISH_KEY=... python3 gen.py` (voz bd35c17b29c54d3e9d2663863a28d212).
2. Escenas HTML nuevas (03, 03b, 03c) en `site/pres_scenes.php`; tiempos por palabra con la API ASR de Fish.
3. `python3 prep.py` → data-es/en.json (pasos, cámara, títulos, subtítulos).
4. Servidor: `cd site && ln -s /home/claude/binantrader/sumiago sumiago && php -S 127.0.0.1:8100`.
5. `python3 audio.py es|en` · `python3 render.py es|en h|v` (≈25 min c/u) · `python3 assemble.py lang o [ids re-renderizados]` · `python3 stills.py lang`.
6. Los MP4 van a `sumiago/app/uploads/tareas/presentacion-video/presentacion-{es,en}-{16x9,9x16}.mp4` (+ .jpg) en el VPS (no van a git).
