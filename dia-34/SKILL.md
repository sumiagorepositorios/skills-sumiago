---
name: dia-34
description: Crea el video del Día 34 de Tareas Diarias de Sumiago, "La libreta de la abuela" (historia ilustrativa: Valentina saca a la luz las recetas guardadas de su abuela con una portada gratis, el Marketplace y un video con IA, y llegan los pedidos; invita sin vender a registrarse y probar Sumiago), en móvil 9:16 y PC 16:9, con narrador, música cálida, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 34.
---

# Día 34 — "La libreta de la abuela"

Reel vertical de unos 65 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Historia ilustrativa: la abuela Rosa tenía 40 recetas que nunca salieron de su cocina; su nieta Valentina (19 años, sin trabajo) hace la receta Nº 7, arma una **portada gratis** con botón de pedidos a WhatsApp, publica en el **Marketplace** y hace un **video con IA**. Llegan pedidos de una vecina, de un desconocido y de una cafetería cada viernes. Mensaje: "la libreta nunca cambió; lo que cambió es que alguien la pudo ver". Cierra invitando a registrarse en el link del perfil y probar Sumiago, sin prometer ganancias.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-BlackItalic, Inter-Bold, Inter-SemiBold, Inter-SemiBoldItalic, Inter-Medium .otf), instalada o en una carpeta `fonts/` dentro de la skill.
- Imágenes en `assets/`: `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.** Modelo por defecto `s2.1-pro-free` (cámbialo con `FISH_MODEL`).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-34/scripts/voz.py
python ruta/dia-34/scripts/tl.py
python ruta/dia-34/scripts/align.py
python ruta/dia-34/scripts/audio.py
python ruta/dia-34/scripts/render.py 0 650 a.mp4
python ruta/dia-34/scripts/render.py 650 1300 b.mp4
python ruta/dia-34/scripts/render.py 1300 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-34.mp4
python ruta/dia-34/scripts/pc.py dia-34.mp4 dia-34-pc.mp4
```

Las tres partes de `render.py` pueden correr a la vez. Para revisar un momento: `python ruta/dia-34/scripts/render.py still 19 46`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | La abuela Rosa… 40 recetas | Cocina cálida, foto de Rosa, la libreta se abre, chip "40 RECETAS", sello "SOLO EN SU COCINA" | se aleja; hojas que pasan |
| 1 | Cada diciembre… fila por sus cocadas | Guirnalda de luces, familia que llega en fila, bandeja de cocadas | la libreta se vuelve la bandeja; la cámara va de la fila a la bandeja |
| 2 | …la libreta se quedó en un cajón | Mueble; la libreta entra y el cajón se cierra; polvo y luz que baja | la música baja; cajón + golpe |
| 3 | Su nieta, Valentina… 19 años, ningún trabajo | Polaroid de Valentina, chips "19 AÑOS", "SIN TRABAJO" y la libreta brillando | pops sincronizados |
| 4 | Receta número 7… igualitas | Cocina de noche, tarjeta "Receta Nº 7", olla con vapor, cocadas y sello "¡IGUALITAS!" | la cámara baja de la tarjeta al plato |
| 5 | Foto… portada gratis… WhatsApp | Celular: flash, portada "Dulces de la Abuela Rosa", lista de dulces, botón "Hacer pedido", sello "GRATIS" | la cámara sigue hasta el botón; obturador |
| 6 | Marketplace… video con IA | Anuncio del Marketplace y tarjeta de video "HECHO CON IA" con onda | la cámara va del anuncio al video |
| 7 | Primer pedido… el segundo | Mapa: líneas desde la casa y notificaciones "Nuevo pedido" | la cámara sigue a las notificaciones; dings |
| 8 | 3 semanas… cafetería… cada viernes | "CAFÉ LUNA", burbuja "¿Nos traes cocadas cada viernes?", calendario con los viernes marcados | la cámara baja al calendario |
| 9 | La libreta nunca cambió… alguien la pudo ver | La libreta brilla con chispas y llegan personas a verla | acercamiento lento; brillo |
| 10 | Si tú también tienes algo guardado… gratis | Caja que se abre con luz; tarjetas "Tu portada" y "Marketplace" (GRATIS) y "Videos con IA" | pops |
| 11 | Entra al link de mi perfil… ya es tu historia | Tarjeta de Sumiago, chip "PRUÉBALO", mascota con el pulgar, botón "LINK EN MI PERFIL", "…ya es tu historia." | pops |
| — | Cierre | Logo con rebote, ondas, chispas y brillo; "Tu historia empieza aquí" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Historia: crema, madera y rojo Sumiago `#E6262F`; parte final en rojo, negro, blanco y gris. Rótulo pequeño "Historia ilustrativa" hasta la parte de Sumiago.
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma en la siguiente escena (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- `BD` en `render.py` dibuja con transparencia real (ImageDraw por sí solo no mezcla el alfa).
- No prometer ganancias ni decir que todo es gratis (gratis: crear la portada y publicar). No escribir «BinanTrader».
