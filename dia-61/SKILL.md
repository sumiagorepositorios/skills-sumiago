---
name: dia-61
description: Crea el video del Día 61 de Tareas Diarias de Sumiago, "La tasa del día" (historia ilustrativa: Yorman, en Maracaibo, vende una laptop en dólares y todos le preguntan cuánto es en bolívares; en el Marketplace de Sumiago el anuncio muestra solo el equivalente en bolívares a la tasa oficial del BCV y, con la casilla Cashea, el sello «Aceptamos Cashea»), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 61.
---

# Día 61 — "La tasa del día"

Reel vertical de unos 61 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Yorman vende una laptop en Maracaibo por $250 y todos le preguntan «¿Y en bolívares, cuánto es?». Cada vez busca la tasa del día, saca la calculadora y responde uno por uno; al otro día la tasa ya es otra. Publica la laptop en el Marketplace de Sumiago en dólares y debajo del precio aparece solo el **equivalente en bolívares con la tasa oficial del BCV**; Sumiago revisa la tasa varias veces al día. Además marca la casilla **«Cashea — Tus clientes pagan en cuotas»** y su anuncio muestra el sello «Aceptamos Cashea». Ya no le preguntan cuánto es en bolívares, sino «¿Dónde la puedo ver?». Cierra: "Que las cuentas… las haga Sumiago."

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
python ruta/dia-61/scripts/voz.py
python ruta/dia-61/scripts/tl.py
python ruta/dia-61/scripts/align.py
python ruta/dia-61/scripts/audio.py
python ruta/dia-61/scripts/render.py 0 600 a.mp4
python ruta/dia-61/scripts/render.py 600 1200 b.mp4
python ruta/dia-61/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-61.mp4
python ruta/dia-61/scripts/pc.py dia-61.mp4 dia-61-pc.mp4
```

Para revisar un momento: `python ruta/dia-61/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Yorman vende una laptop en Maracaibo, $250 | Yorman y la laptop; chips "MARACAIBO, VENEZUELA" y "$ 250" | se aleja |
| 1 | «¿Y en bolívares, cuánto es?» | Cinco mensajes iguales | dings, música bajita |
| 2 | Tasa del día, calculadora, uno por uno | Yorman, chip "TASA DEL DÍA: ¿?", calculadora y contador de respuestas | teclas |
| 3 | Al otro día la tasa era otra | Calendario MARTES → MIÉRCOLES y la tasa cambia; sello | golpe |
| 4 | Publicó en dólares | Formulario: precio 250, moneda USD, país Venezuela | teclas |
| 5 | Equivalente en bolívares, tasa BCV | El anuncio muestra "$ 250" y "≈ Bs. 60.000,00 · Tasa oficial BCV"; la cámara se acerca | brillo + ding |
| 6 | La tasa se revisa varias veces al día | Flecha que gira alrededor de "BCV"; calculadora tachada | |
| 7 | Casilla Cashea | Casilla marcada "Cashea — Tus clientes pagan en cuotas"; chip "SOLO PARA VENEZUELA" | pop |
| 8 | Sello «Aceptamos Cashea» | El anuncio con el sello resaltado | ding |
| 9 | «¿Dónde la puedo ver?» | "¿Cuánto es en bolívares?" tachado y tres mensajes nuevos | dings |
| 10 | Dólares y bolívares a la tasa del BCV | Tarjeta "$ 250 / ≈ Bs. … / Tasa oficial BCV"; chip "ANUNCIOS DE VENEZUELA" | pops |
| 11 | Entra al link… las haga Sumiago | Tarjeta "Marketplace Sumiago · Dólares y bolívares, al día", mascota y frase final | |
| — | Cierre | Logo; "Publica en dólares" y "LINK EN MI PERFIL" | brillo |

La tasa (Bs. 240,00) y el equivalente del video son **ilustrativos**.

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): en anuncios de Venezuela con precio en USD/USDT, el Marketplace muestra «≈ Bs. …» y «Tasa oficial BCV: Bs. … por dólar» (mp_precio_alt / mp_tasa_bcv, la tasa se consulta y guarda como máximo cada 3 horas; si el precio está en VES muestra el equivalente en USD); vendedores de Venezuela tienen la casilla «Cashea — Tus clientes pagan en cuotas» y el anuncio muestra «Aceptamos: Cashea». No usar el logo de Cashea en el video (solo texto). Las cifras son ilustrativas.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
