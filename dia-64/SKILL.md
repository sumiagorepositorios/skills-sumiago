---
name: dia-64
description: Crea el video del Día 64 de Tareas Diarias de Sumiago, "Este video lo hizo una IA" (tipografía en movimiento estilo motion graphics sobre la sección VIDEOS VIRALES: escribes una idea, la IA hace guion, voz, música, efectos y subtítulos, lo renderiza, Ideas Virales y subida a YouTube; cierre "Comenta VIRAL y te paso el enlace"), en móvil 9:16 y PC 16:9, con narrador, música, efectos y logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 64 o un video "viral" de texto animado con este estilo.
---

# Día 64 — "Este video lo hizo una IA"

Reel vertical de unos 55 s (1080x1920, 30 fps) hecho solo con texto animado e interfaces, al estilo de los videos virales de "motion graphics hechos con IA". El gancho habla del propio video: «Este video que estás viendo ahora… no lo hizo ningún editor. Lo hizo una inteligencia artificial». Después muestra cómo cualquiera puede hacer lo mismo con **VIDEOS VIRALES** de Sumiago y cierra pidiendo comentar una palabra clave (**VIRAL**) para subir los comentarios.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+, FFmpeg en el PATH y Google Chrome. Paquetes: `pip install playwright numpy pillow`
- Fuentes **Inter Display** (Black, ExtraBold), **Inter** (Medium, Black, Bold, SemiBold) y **Crimson Text** SemiBold Italic, instaladas o en una carpeta `fonts/` junto a `anim.html`.
- `assets/logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free`. Voz: "narrador educativo sumiago".

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
export CHROME=/ruta/a/chrome          (en Windows: set CHROME=C:\Program Files\Google\Chrome\Application\chrome.exe)
python ruta/dia-64/scripts/voz.py
python ruta/dia-64/scripts/tl.py
python ruta/dia-64/scripts/sound.py
python ruta/dia-64/scripts/shoot.py full
ffmpeg -y -i video_tmp.mp4 -i fx.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-64.mp4
python ruta/dia-64/scripts/pc.py dia-64.mp4 dia-64-pc.mp4
```

Para revisar momentos sueltos sin renderizar todo: `python ruta/dia-64/scripts/shoot.py test 2.3,19.5,44`.

## Escenas

| # | Voz | En pantalla | Técnica / sonido |
|---|-----|-------------|------------------|
| 0 | Este video que estás viendo ahora… | "ESTE VIDEO" se escribe con cursor "Sumiago"; "ahora" en recuadro rojo | tecleo |
| 1 | no lo hizo ningún editor | "NINGÚN EDITOR" tachado; íconos de edición con ✕ | barrido, pops |
| 2 | Ni CapCut, ni Premiere… | Tarjetas tachadas | barrido |
| 3 | Lo hizo una inteligencia artificial | Flash blanco, "una IA." en cursiva serif | golpe |
| 4 | Y ahora tú puedes hacer lo mismo | "LO MISMO" en recuadro que gira; cursor "Tú" | pop |
| 5 | con Videos Virales, dentro de Sumiago | El cursor hace clic y aparece la sección VIDEOS VIRALES; figuras flotando | clic |
| 6 | Escribes una idea… | Caja de chat que se escribe sola y botón enviar | tecleo, clic |
| 7 | y la IA te escribe el guion | Archivo guion_viral.txt con escenas | — |
| 8 | Le pone voz | "VOZ" gigante y onda de audio | — |
| 9 | música, efectos y subtítulos | Línea de tiempo con 5 pistas y cabezal | pop |
| 10 | y lo renderiza solita | Barra 0→100 % y "¡Listo!" | ding |
| 11 | ¿Sin ideas? Ideas Virales… | Tarjetas de videos con vistas que suben y "×41" | pops |
| 12 | Y lo subes a tu YouTube con un clic | Fondo claro (segundo acto), botón Publicar → Publicado | golpe, clic, ding |
| 13 | Sin saber editar nada | "EDITAR" tachado, "nada." | barrido |
| 14 | ¿Quieres probarlo? Comenta VIRAL… | "VIRAL" gigante, caja de comentarios con corazón | tecleo, clic, ding |
| — | Cierre | Logo, "Crea tus videos con IA", "LINK EN MI PERFIL" | golpe |

## Estilo y reglas

- Fondo negro con brillo rojo Sumiago que se mueve; el segundo acto cambia a fondo claro. Rojo `#E10600`, blanco, gris.
- Palabras que suben desde una máscara, palabras tachadas con una línea roja animada, palabras clave en recuadro rojo, acentos en cursiva serif roja, cursor con etiqueta ("Sumiago"/"Tú") que hace clic, acercamiento lento de cámara en cada escena y transición con desenfoque.
- La duración de cada escena se ajusta a su frase (`tl.py`) y la música baja cuando habla el narrador.
- Para cambiar la palabra del cierre (por ejemplo SUMIAGO), cambia la frase 14 en `guion.json` y la palabra `VIRAL` en la escena 15 de `anim.html`.
- Funciones reales (verificadas en el código): VIDEOS VIRALES tiene Estudio de Video (guion → voz → Short 9:16 con subtítulos palabra por palabra, música suave y efectos), Ideas Virales (videos de canales pequeños con más vistas que suscriptores) y Mi YouTube (publicar en tu canal). Cada usuario usa sus propias claves; es para miembros con membresía activa.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
