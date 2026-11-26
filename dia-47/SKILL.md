---
name: dia-47
description: Crea el video del Día 47 de Tareas Diarias de Sumiago, "Publicaba a ciegas" (historia ilustrativa: Sebastián vende tenis, publicaba en Facebook a las 7 a. m. sin saber si funcionaba; la analítica de su portada de Sumiago le muestra que sus visitas vienen de TikTok, a las 8 p. m., y que buscan la tabla de tallas), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 47.
---

# Día 47 — "Publicaba a ciegas"

Reel vertical de unos 59 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Sebastián vende tenis y publicaba todos los días a las 7 a. m. en Facebook, "porque sí", sin saber si alguien lo veía. Con su membresía abre la **analítica de su portada** en Sumiago: visitas, clics y de dónde llega cada persona. Descubre que la mayoría llega desde TikTok, que la hora pico es a las 8 p. m. y que el enlace más tocado es la tabla de tallas. Cambia 3 cosas (TikTok, 8 p. m., tallas de primeras). "No trabajó más. Trabajó donde estaban sus clientes." "Los números no mienten. Solo hay que mirarlos." Cierra: "Deja de publicar a ciegas."

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-BlackItalic, Inter-Bold, Inter-SemiBold, Inter-SemiBoldItalic, Inter-Medium .otf), instalada o en una carpeta `fonts/` dentro de la skill.
- Imágenes en `assets/`: `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free` (cámbialo con `FISH_MODEL`). Voz: "narrador educativo sumiago".

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-47/scripts/voz.py
python ruta/dia-47/scripts/tl.py
python ruta/dia-47/scripts/align.py
python ruta/dia-47/scripts/audio.py
python ruta/dia-47/scripts/render.py 0 590 a.mp4
python ruta/dia-47/scripts/render.py 590 1180 b.mp4
python ruta/dia-47/scripts/render.py 1180 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-47.mp4
python ruta/dia-47/scripts/pc.py dia-47.mp4 dia-47-pc.mp4
```

Para revisar un momento: `python ruta/dia-47/scripts/render.py still 22.5 27`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Sebastián vende tenis… 7 a. m., Facebook… porque sí | Estantes de tenis, Sebastián, chips "7:00 a. m." y "FACEBOOK", sello "¿PORQUE SÍ?" | se aleja |
| 1 | Nunca supo si alguien lo veía… a ciegas | Sebastián con una venda roja, "?" y sello "A CIEGAS" | música bajita |
| 2 | Con su membresía abrió la analítica | Tablero "Analítica de mi portada" vacío; chip "CON SU MEMBRESÍA" | ding |
| 3 | Visitas, clics y de dónde llegaba cada persona | Indicadores Visitas 1.240, Clics 386, 31 %, hora pico 8 p. m. y gráfica de visitas y clics por día | |
| 4 | La mayoría llegaba desde TikTok | Barras "Red de origen": TikTok 62 %, Instagram, Directo/QR, Facebook 6 %; sello "NO ERA FACEBOOK" | |
| 5 | Hora pico: no 7 a. m., sino 8 p. m. | "Visitas por hora del día" con la barra de las 20 h en rojo; chips | ding |
| 6 | El enlace más tocado: la tabla de tallas | "Clics por enlace" con Tabla de tallas 58 % resaltada; sello "TABLA DE TALLAS" | |
| 7 | 3 cambios: TikTok, 8 p. m., tallas de primeras | Tres tarjetas numeradas con ✓ | dings |
| 8 | Trabajó donde estaban sus clientes | Sebastián y clientes que llegan; chips | |
| 9 | Los números no mienten… mirarlos | Números flotando, "LOS NÚMEROS NO MIENTEN" y lupa | brillo |
| 10 | La analítica de tu portada… con tu membresía | Tablero completo y chip | |
| 11 | Entra al link de mi perfil… deja de publicar a ciegas | Tarjeta "Analítica de tu portada · Visitas, clics, origen y hora pico · PORTADA PRO", mascota, "LINK EN MI PERFIL" | |
| — | Cierre | Logo con rebote, ondas y brillo; "Deja de publicar a ciegas" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Tienda clara y tableros blancos con rojo Sumiago `#E6262F`, negro y gris (como la analítica real). Rótulo "Historia ilustrativa"; las cifras son de ejemplo.
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: la analítica avanzada de la portada es **PRO (con la membresía)** y muestra visitas, visitantes únicos, clics, % de clics por visita, hora pico, visitas y clics por día, clics por enlace, países, red de origen (Directo/QR, Instagram, TikTok, YouTube, Facebook, X…), dispositivo y visitas por hora. No prometer ventas ni ganancias. No escribir «BinanTrader».
