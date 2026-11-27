---
name: dia-55
description: Crea el video del Día 55 de Tareas Diarias de Sumiago, "La rebaja invisible" (historia ilustrativa: Camila rebaja sus morrales nuevos pero lo escribe al final de la descripción y nadie lo ve; en el Marketplace de Sumiago usa «Precio de oferta» y su anuncio muestra el precio de antes tachado, -21 % y «Ahorras $ 25.000»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 55.
---

# Día 55 — "La rebaja invisible"

Reel vertical de unos 64 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Camila vende morrales nuevos para el regreso a clases a $ 120.000. Los rebaja a $ 95.000, pero lo escribe al final de la descripción: nadie llega hasta ahí, ven $ 120.000 y siguen de largo. En el Marketplace de Sumiago, cuando el artículo es nuevo aparece la casilla **«Precio de oferta»**: deja el precio real en $ 120.000 y la oferta en $ 95.000. Su anuncio muestra el precio de antes tachado y una etiqueta roja **-21 %**, y adentro dice **«Ahorras $ 25.000»**. Entre todos los morrales, el suyo es el único que se nota en oferta; ya no le preguntan cuánto vale, sino si le quedan en azul. Cierra: "Una rebaja que no se ve… no es rebaja."

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
python ruta/dia-55/scripts/voz.py
python ruta/dia-55/scripts/tl.py
python ruta/dia-55/scripts/align.py
python ruta/dia-55/scripts/audio.py
python ruta/dia-55/scripts/render.py 0 600 a.mp4
python ruta/dia-55/scripts/render.py 600 1200 b.mp4
python ruta/dia-55/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-55.mp4
python ruta/dia-55/scripts/pc.py dia-55.mp4 dia-55-pc.mp4
```

Para revisar un momento: `python ruta/dia-55/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Morrales nuevos a $ 120.000 | Camila y su mesa de morrales de colores; chips "NUEVOS" y "$ 120.000" | se aleja |
| 1 | Los rebajó… al final de la descripción | Anuncio con descripción larga; la cámara baja hasta "PD: rebajados a $ 95.000" en letra diminuta | acerca mucho |
| 2 | Veían $ 120.000 y seguían de largo | Feed de morrales que pasa con el dedo; chip "SEGUÍAN DE LARGO" | música bajita |
| 3 | Nadie la veía | Lupa sobre el texto diminuto; sello "NADIE LA VEÍA" | golpe |
| 4 | Artículo nuevo: casilla «Precio de oferta» | Formulario: Condición "Nuevo" y aparece la casilla | brillo |
| 5 | Precio real y precio de oferta | Se escriben $ 120.000 y $ 95.000 | teclas |
| 6 | Precio de antes tachado y -21 % | Tarjeta del anuncio: $ 95.000, $ 120.000 tachado y etiqueta roja | ding |
| 7 | «Ahorras $ 25.000» | Detalle del anuncio con la píldora verde | brillo |
| 8 | El único que se notaba en oferta | Cuadrícula de morrales; el suyo con borde dorado | ding |
| 9 | ¿Te quedan en azul? | "¿Cuánto vale?" tachado y tres mensajes nuevos | dings |
| 10 | Solo artículos nuevos y siempre menor | Tarjetas de las reglas; chip "PRECIO DE OFERTA" | pops |
| 11 | Entra al link… no es rebaja | Tarjeta "Marketplace Sumiago · Tu rebaja, a la vista", mascota y frase final | |
| — | Cierre | Logo; "Que tu oferta se vea" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): «Precio de oferta (opcional)» solo para artículos de condición nueva (no en «Regalo»), debe ser mayor que 0 y menor que el precio real; la tarjeta muestra el precio de antes tachado y la etiqueta roja -%; el anuncio muestra «Ahorras …».
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
