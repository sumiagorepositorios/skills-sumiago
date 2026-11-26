---
name: dia-43
description: Crea el video del Día 43 de Tareas Diarias de Sumiago, "Lo que dicen de Wilmer" (historia ilustrativa: un barbero cuyos clientes salen contentos activa las reseñas de Mi Negocio en su portada de Sumiago; los clientes dejan estrellas, él aprueba lo que se publica y los nuevos llegan porque lo recomiendan), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 43.
---

# Día 43 — "Lo que dicen de Wilmer"

Reel vertical de unos 62 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Wilmer es barbero y sus clientes salen diciendo "quedé como nuevo", pero eso solo lo escucha él: quien busca barbería ve fotos bonitas y no sabe en quién confiar, porque antes de probar algo leemos lo que dicen los demás. Wilmer activa las **reseñas** en **Mi Negocio** de su portada de Sumiago; después de cada corte invita al cliente a dejar su reseña en su enlace (nombre, estrellas y dos palabras). Le llega el aviso, la revisa y la aprueba: **solo se publican las que él aprueba**. Su portada muestra "Lo que dicen mis clientes" y los nuevos llegan diciendo "vi que te recomiendan". Cierra: "Deja que tus clientes hablen por ti."

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
python ruta/dia-43/scripts/voz.py
python ruta/dia-43/scripts/tl.py
python ruta/dia-43/scripts/align.py
python ruta/dia-43/scripts/audio.py
python ruta/dia-43/scripts/render.py 0 620 a.mp4
python ruta/dia-43/scripts/render.py 620 1240 b.mp4
python ruta/dia-43/scripts/render.py 1240 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-43.mp4
python ruta/dia-43/scripts/pc.py dia-43.mp4 dia-43-pc.mp4
```

Para revisar un momento: `python ruta/dia-43/scripts/render.py still 32.5 42`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Wilmer es barbero… «quedé como nuevo» | Barbería con poste, espejo y silla; cliente que sale con burbuja; chip "BARBERO" | tijeras |
| 1 | Solo lo escuchaba él… los nuevos no lo sabían | Ondas de sonido hacia Wilmer; pared y clientes nuevos afuera con "?"; chip "SOLO LO ESCUCHA ÉL" | música bajita |
| 2 | Fotos bonitas… en quién confiar | Celular buscando "barbería": tres resultados "Sin reseñas"; sello "¿EN QUIÉN CONFÍO?" | |
| 3 | Leemos lo que dicen los demás | Tres personas con tarjetas de estrellas; chip | dings |
| 4 | Activó las reseñas en Mi Negocio | Panel "Mi Negocio PRO", pestaña Reseñas, interruptor "Mostrar reseñas y permitir que me dejen nuevas" | ding |
| 5 | Después de cada corte… déjame tu reseña en mi enlace | Wilmer y cliente; burbuja; tarjeta `sumiago.com/wilmer-barber` | tijeras + pop |
| 6 | Nombre, estrellas y dos palabras | Formulario "Deja tu reseña": nombre Julián, 5 estrellas que se llenan, "Excelente corte" | pops |
| 7 | Le llega el aviso… solo se publican las que él aprueba | Aviso "Nueva reseña… Apruébala para mostrarla", reseña con botones Aprobar/Rechazar y toque en Aprobar; chip | ding |
| 8 | «Lo que dicen mis clientes» | Portada "Wilmer Barber" con la sección y 3 reseñas | |
| 9 | «Vi que te recomiendan» | Nueva clienta que llega con burbuja y estrellas | brillo |
| 10 | Tus clientes contentos son tu mejor publicidad… con tu membresía | Cinco estrellas grandes, "TU MEJOR PUBLICIDAD", chip "RESEÑAS EN MI NEGOCIO · CON TU MEMBRESÍA" | |
| 11 | Entra al link de mi perfil… hablen por ti | Tarjeta "Mi Negocio · Reseñas · Tú apruebas lo que se publica", mascota, "LINK EN MI PERFIL" y "Deja que tus clientes hablen por ti." | brillo |
| — | Cierre | Logo con rebote, ondas y brillo; "Deja que hablen por ti" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Barbería gris con rojo y azul; pantallas oscuras con rojo Sumiago `#E6262F` y estrellas doradas. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita y efectos.
- Funcionamiento real: las reseñas son parte de **Mi Negocio (PRO, con la membresía)**; el cliente deja nombre, estrellas y texto desde la portada, al dueño le llega el aviso "Nueva reseña… Apruébala para mostrarla" y solo se publican las aprobadas, bajo el título "Lo que dicen mis clientes". No prometer clientes ni ganancias. No escribir «BinanTrader».
