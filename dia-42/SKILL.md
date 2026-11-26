---
name: dia-42
description: Crea el video del Día 42 de Tareas Diarias de Sumiago, "La carta manchada" (historia ilustrativa: el restaurante de don Efraín cambia su carta impresa, manchada y tachada, por el menú QR de Mi Negocio en su portada de Sumiago y actualiza precios y platos agotados desde el celular), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 42.
---

# Día 42 — "La carta manchada"

Reel vertical de unos 64 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). La carta del restaurante de don Efraín tiene manchas de salsa, precios tachados y un plato que ya no existe; cada subida de precio obliga a reimprimir, y casi nunca lo hace. Los clientes preguntan "¿esto todavía lo tienen?" y la mesera va a la cocina a averiguar. Su hijo le habla de **Mi Negocio** en su portada de Sumiago: suben los platos al **catálogo** (foto, descripción, precio y categoría) y de ahí sale el **menú con código QR** para imprimir. Lo ponen en cada mesa; el cliente escanea y ve el menú en su celular. Si sube un precio o se acaba un plato, don Efraín lo cambia desde su celular. "Ya no hay que reimprimir nada." Cierra: "Que tu menú esté tan fresco como tu comida."

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
python ruta/dia-42/scripts/voz.py
python ruta/dia-42/scripts/tl.py
python ruta/dia-42/scripts/align.py
python ruta/dia-42/scripts/audio.py
python ruta/dia-42/scripts/render.py 0 640 a.mp4
python ruta/dia-42/scripts/render.py 640 1280 b.mp4
python ruta/dia-42/scripts/render.py 1280 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-42.mp4
python ruta/dia-42/scripts/pc.py dia-42.mp4 dia-42-pc.mp4
```

Para revisar un momento: `python ruta/dia-42/scripts/render.py still 30.5 40`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | La carta: manchas, precios tachados, un plato que no existe | Carta vieja con manchas, precios tachados y "Lasaña" tachada; chips "MANCHAS DE SALSA" / "PRECIOS TACHADOS", sello "YA NO EXISTE" | la cámara recorre la carta |
| 1 | Subía un precio… reimprimir… casi nunca | Impresora que saca "$$$", chip "SUBIÓ UN PRECIO", sello "CASI NUNCA" | ruido de impresora |
| 2 | ¿Esto todavía lo tienen?… a la cocina | Cliente con burbuja y mesera que sale corriendo; chip "A AVERIGUAR…" | |
| 3 | Su hijo le habló de Mi Negocio | Don Efraín (chef) y su hijo; tarjeta "Mi Negocio PRO" | |
| 4 | Catálogo: foto, descripción, precio, categoría | Formulario "Catálogo · Nuevo plato" que se llena campo por campo | la cámara baja |
| 5 | El menú con código QR para imprimir | Celular "Menú · Don Efraín" por categorías y QR "Imprimir QR" | ding |
| 6 | En cada mesa… el cliente escanea | Mesas con el QR; clienta y el menú que aparece en su celular | la cámara sigue al celular |
| 7 | Sube un precio o se acaba un plato… listo | Menú: el precio cambia de 21.000 a 22.000 y "Pescado frito" queda "Agotado"; sello "¡LISTO!" | |
| 8 | Ya no hay que reimprimir nada | Impresora tachada y sello "NADA QUE REIMPRIMIR" | |
| 9 | La carta vieja… de recuerdo | La carta clavada en la pared de la cocina; chip "DE RECUERDO" | |
| 10 | Restaurante, cafetería o puesto de comidas… con tu membresía | Tres tarjetas con platos y chip "MENÚ QR · CON TU MEMBRESÍA" | pops |
| 11 | Entra al link de mi perfil… tan fresco como tu comida | Tarjeta "Mi Negocio · Menú QR · Cámbialo cuando quieras", mascota, "LINK EN MI PERFIL" y "Tan fresco como tu comida." | brillo |
| — | Cierre | Logo con rebote, ondas y brillo; "Tu menú siempre al día" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Restaurante cálido (mesas rojas, madera) y pantallas oscuras con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: el Menú QR de **Mi Negocio (PRO, con la membresía)** usa los productos del catálogo (nombre, categoría, descripción, precio y foto) y se imprime su QR para mesas, mostrador o vitrina. No prometer ventas ni ganancias. No escribir «BinanTrader».
