---
name: dia-65
description: Crea el video del Día 65 de Tareas Diarias de Sumiago, "¿Cómo decide TikTok a quién le muestra tu video?" (tipografía en movimiento estilo motion graphics: primero lo prueba con un grupo pequeño, se fija en 4 señales —3 primeros segundos, verlo hasta el final, repetirlo, comentar—, si responden lo pasa a grupos cada vez más grandes, si no ahí se queda; "Así NO" vs "Así SÍ"; cierre "Comenta SUMIAGO y te envío la información"), en móvil 9:16 y PC 16:9, con narrador, música, efectos y logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 65 o un video "viral" educativo de texto animado con este estilo.
---

# Día 65 — "¿Cómo decide TikTok a quién le muestra tu video?"

Reel vertical de unos 55 s (1080x1920, 30 fps) hecho solo con texto animado, figuras e interfaces, al estilo de los videos virales que explican "algo que casi nadie sabe" (referencia: video sobre Andromeda de Meta). Una nube de puntos representa a la audiencia; el video explica de forma sencilla cómo una plataforma prueba un video con un grupo pequeño, mira cuatro señales y, si el grupo responde, lo muestra a grupos cada vez más grandes. Cierra con la dinámica de comentar la palabra **SUMIAGO**.

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
python ruta/dia-65/scripts/voz.py
python ruta/dia-65/scripts/tl.py
python ruta/dia-65/scripts/sound.py
python ruta/dia-65/scripts/shoot.py full
ffmpeg -y -i video_tmp.mp4 -i fx.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-65.mp4
python ruta/dia-65/scripts/pc.py dia-65.mp4 dia-65-pc.mp4
```

Para revisar momentos sueltos sin renderizar todo: `python ruta/dia-65/scripts/shoot.py test 1.0,14.5,30.5`.

## Escenas

| # | Voz | En pantalla | Técnica / sonido |
|---|-----|-------------|------------------|
| 0 | ¿Cómo decide TikTok a quién le muestra tu video? | Galaxia de puntos que se abre; "TikTok" lo escribe el cursor "Sumiago"; "tu video?" en recuadro rojo que gira | tecleo, pop |
| 1 | Casi nadie lo sabe. | "CASI NADIE" y "lo sabe." en cursiva serif | golpe |
| 2 | Cuando lo publicas, no se lo muestra a todo el mundo. | Cursor "Tú" hace clic en Publicar → Publicado; "TODO EL MUNDO" tachado | clic, barridos |
| 3 | Primero lo prueba con un grupo pequeño. | Celular al centro y un anillo de 14 personitas | pops |
| 4 | Y se fija en cuatro señales. | "4 SEÑALES" y cuatro tarjetas numeradas | pops |
| 5 | ¿Se quedaron los primeros tres segundos? | SEÑAL 1: reloj 0:00→0:03 y algunas personas que se van | tic de reloj |
| 6 | ¿Lo vieron hasta el final? | SEÑAL 2: celular con barra de progreso hasta ✓ | ding |
| 7 | ¿Lo volvieron a ver? | SEÑAL 3: flecha que gira y "×2" | pops |
| 8 | ¿Comentaron? | SEÑAL 4: comentarios que aparecen con corazón | pops |
| 9 | Si ese grupo responde, se lo muestra a un grupo más grande… y a otro… y a otro. | "responde," en recuadro; tres anillos de personas cada vez más grandes | pops |
| 10 | Si no responde… ahí se queda. | La galaxia se encoge y se vuelve gris | tono que baja |
| 11 | Por eso este video no empezó con: hola, bienvenidos a mi canal. | Fondo claro (segundo acto); tarjeta "ASÍ NO" que se escribe, se tacha y la gente se va | golpe, tecleo, barrido |
| 12 | Empezó con una pregunta. | Tarjeta "ASÍ SÍ" con la pregunta del gancho y la gente que se queda | pop, ding |
| 13 | Ahora ya sabes cómo piensa. | "CÓMO piensa." | — |
| 14 | ¿Quieres saber cómo crear videos así? Comenta SUMIAGO, y te envío la información. | "SUMIAGO" gigante, caja de comentarios que se escribe sola, el cursor "Sumiago" le da corazón | tecleo, clic, ding |
| — | Cierre | Logo y "LINK EN MI PERFIL" | golpe |

## Estilo y reglas

- Fondo negro con brillo rojo Sumiago que se mueve; el segundo acto (escenas 11-13 y logo) cambia a fondo claro. Solo rojo `#E10600`, negro, blanco y gris ("ASÍ NO" en gris, "ASÍ SÍ" en rojo).
- Palabras que suben desde una máscara, palabras tachadas con línea roja animada, palabras clave en recuadro rojo, acentos en cursiva serif roja, cursor con etiqueta ("Sumiago"/"Tú") que hace clic, acercamiento lento de cámara en cada escena y transición con desenfoque.
- La duración de cada escena se ajusta a su frase (`tl.py`) y la música baja cuando habla el narrador.
- Para cambiar la palabra del cierre, cambia la frase 14 en `guion.json` y la palabra `SUMIAGO` en la escena 14 de `anim.html`.
- La explicación del algoritmo es general e ilustrativa (señales comúnmente conocidas); no inventes cifras exactas de usuarios por grupo.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
