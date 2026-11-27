---
name: dia-56
description: Crea el video del Día 56 de Tareas Diarias de Sumiago, "El letrero que hablaba" (historia ilustrativa: don Gilberto vende su carro con un cartón de «Se vende» y nadie llama; su hija lo publica en el Marketplace de Sumiago y con el botón «Imprimir» sale un afiche con fotos, precio, ciudad, WhatsApp, QR y código de referencia; un señor en el semáforo escanea el QR y ve todas las fotos), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 56.
---

# Día 56 — "El letrero que hablaba"

Reel vertical de unos 66 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Don Gilberto pega en el vidrio de su carro un cartón «Se vende» con su número. La gente lo mira y sigue: un cartón no dice el precio ni muestra cómo está por dentro, y casi nadie llama a un desconocido solo para preguntar. Su hija publica el carro en el Marketplace de Sumiago con fotos y precio y toca **«Imprimir»**: sale un afiche listo con «SE VENDE» en grande, 4 fotos, el precio y la ciudad; abajo su WhatsApp y un **código QR** («Escanea y mira todas las fotos»), y un **código de referencia** para encontrar el anuncio en Sumiago en un solo paso. Esa tarde, un señor en el semáforo escanea el QR y ve todas las fotos sin bajarse; al otro día escribe: «Ya vi las fotos. ¿Me lo deja probar mañana?». Cierra: "Que tu letrero… hable por ti."

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
python ruta/dia-56/scripts/voz.py
python ruta/dia-56/scripts/tl.py
python ruta/dia-56/scripts/align.py
python ruta/dia-56/scripts/audio.py
python ruta/dia-56/scripts/render.py 0 600 a.mp4
python ruta/dia-56/scripts/render.py 600 1200 b.mp4
python ruta/dia-56/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-56.mp4
python ruta/dia-56/scripts/pc.py dia-56.mp4 dia-56-pc.mp4
```

Para revisar un momento: `python ruta/dia-56/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Un cartón: «Se vende» y su número | Don Gilberto y su carro; aparece el cartón en el vidrio | acerca al cartón |
| 1 | La gente pasaba… no dice el precio | Calle con gente que pasa; burbujas "¿Precio?" y "¿Cómo está por dentro?" | música bajita |
| 2 | Casi nadie llama a un desconocido | Botón "Llamar" tachado; sello "CASI NADIE LLAMA" | golpe |
| 3 | Su hija lo publicó con fotos y precio | La hija y don Gilberto junto al anuncio del carro | pop |
| 4 | Tocó un botón: «Imprimir» | El anuncio y el botón «Imprimir» resaltado | acerca |
| 5 | El afiche: SE VENDE, 4 fotos, precio y ciudad | El afiche sale de la impresora y se resalta cada parte | impresora |
| 6 | WhatsApp y el QR | La cámara baja al WhatsApp y al QR | brillo |
| 7 | Código de referencia, en un solo paso | "Ref. #1834" resaltado y búsqueda "#1834" en Sumiago con el resultado | ding |
| 8 | En el semáforo escaneó el QR y vio las fotos | El carro con el afiche, otro carro en el semáforo escanea y aparecen las fotos; chip "SIN BAJARSE" | brillo |
| 9 | «Ya vi las fotos. ¿Me lo deja probar mañana?» | Chat de WhatsApp | burbujas |
| 10 | Afiche, QR y código de referencia | Tarjetas de las tres funciones | pops |
| 11 | Entra al link… hable por ti | Tarjeta "Marketplace Sumiago · Imprime tu afiche con QR", mascota y frase final | |
| — | Cierre | Logo; "Imprime tu afiche" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): en su anuncio, el dueño tiene el botón «Imprimir» que abre un afiche «SE VENDE» con título y precio (editables antes de imprimir), hasta 4 fotos, ciudad, llamada/WhatsApp, un QR al anuncio («Escanea y mira todas las fotos») y el código de referencia para buscarlo en Sumiago.com.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
