---
name: dia-63
description: Crea el video del Día 63 de Tareas Diarias de Sumiago, "Demasiado bueno" (historia ilustrativa: Daniela ve un celular de último modelo a mitad de precio, el vendedor le pide transferir la mitad para apartarlo; no paga, usa «Reportar este artículo» con el motivo «Posible estafa», otros también lo reportan y el anuncio se oculta y queda en revisión), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 63.
---

# Día 63 — "Demasiado bueno"

Reel vertical de unos 67 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Daniela busca un celular y ve el último modelo a la mitad de precio. El vendedor responde rapidísimo: «Transfiéreme la mitad para apartarlo»; las fotos parecen de catálogo y tiene mucha prisa. Daniela no transfiere nada: si es demasiado bueno para ser verdad, algo anda mal. Vuelve al anuncio, baja hasta **«Reportar este artículo»**, elige el motivo **«Posible estafa»** y escribe lo que le pidió el vendedor; le sale «Gracias, revisaremos este artículo». Otras personas también lo reportan y, con **varios reportes, el anuncio se oculta solo y queda en revisión**. Daniela compra su celular a otro vendedor, en persona, en un lugar público y revisándolo antes de pagar. Cierra: "Si es demasiado bueno para ser verdad… repórtalo."

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
python ruta/dia-63/scripts/voz.py
python ruta/dia-63/scripts/tl.py
python ruta/dia-63/scripts/align.py
python ruta/dia-63/scripts/audio.py
python ruta/dia-63/scripts/render.py 0 600 a.mp4
python ruta/dia-63/scripts/render.py 600 1200 b.mp4
python ruta/dia-63/scripts/render.py 1200 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-63.mp4
python ruta/dia-63/scripts/pc.py dia-63.mp4 dia-63-pc.mp4
```

Para revisar un momento: `python ruta/dia-63/scripts/render.py still 25.5 39`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Último modelo a mitad de precio | Daniela y el anuncio; chips "ÚLTIMO MODELO" y "¡LA MITAD DE PRECIO!" | acerca |
| 1 | «Transfiéreme la mitad para apartarlo» | Chat con la respuesta en rojo; chip "EN SEGUNDOS" | música bajita |
| 2 | Fotos de catálogo, mucha prisa | Foto con marca "CATÁLOGO" y reloj acelerado | |
| 3 | No transfirió… algo anda mal | Botón "Transferir" tachado, burbuja y sello "ALGO ANDA MAL" | golpe |
| 4 | «Reportar este artículo» | El anuncio baja hasta el recuadro "Reportar / Calificar" | brillo |
| 5 | Motivo «Posible estafa» y detalle | Lista de motivos y texto que se escribe | teclas |
| 6 | «Gracias, revisaremos este artículo» | Tarjeta con check verde | ding |
| 7 | Otras personas lo reportaron | Personas con banderas; contador de reportes | pops |
| 8 | Se ocultó y quedó en revisión | El anuncio se oscurece con "OCULTO · En revisión"; sello | golpe |
| 9 | Compró en persona, lugar público, revisando | Parque con banca; tres chips | pops |
| 10 | Motivos para reportar | Tarjetas Precio falso / Fotos robadas / Posible estafa / Artículo prohibido | pops |
| 11 | Entra al link… repórtalo | Tarjeta "Marketplace Sumiago · Reporta lo sospechoso", mascota y frase final | |
| — | Cierre | Logo; "Compra con cuidado" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Fondos claros para la historia y oscuros con rojo Sumiago `#E6262F`. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`; aquí además la portada cambia de estilo en vivo con `build_style`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: gratis hay 3 plantillas (Oscuro, Claro, Rojo); la portada **PRO (con la membresía)** desbloquea plantillas por tipo de negocio, colores propios, fuentes, estilos de botón (redondeado, píldora, cuadrado, contorno, sombra), fondo de color, degradado, imagen o video, y quita "Diseñado en Sumiago". No prometer ventas ni ganancias. No escribir «BinanTrader».
- Funciones reales (verificadas en el código): en cada anuncio, «Reportar / Calificar» → «Reportar este artículo» (con sesión; el dueño no puede reportar el suyo); motivos de mp_motivos_reporte (precio falso o engañoso, fotos robadas, posible estafa, artículo prohibido, entre otros) y detalle; mensaje «Gracias, revisaremos este artículo.»; al llegar al límite de reportes abiertos (auto_ocultar, por defecto 3, configurable) el anuncio pasa a «oculto» y el vendedor recibe «Artículo en revisión». No prometer que Sumiago garantiza las compras.
- Nada de promesas de ganancias. No escribir el nombre de la plataforma madre.
