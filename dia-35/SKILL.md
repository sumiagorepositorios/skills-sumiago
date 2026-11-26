---
name: dia-35
description: Crea el video del Día 35 de Tareas Diarias de Sumiago, "Que te busquen a ti" (historia ilustrativa: Laura envía 47 hojas de vida sin respuesta, deja de buscar y se deja encontrar publicando gratis en Contrátame Sumiago, y una empresa la contacta), en móvil 9:16 y PC 16:9, con narrador, música, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 35.
---

# Día 35 — "Que te busquen a ti"

Reel vertical de unos 57 s (dibujado a 720x1280 y entregado a 1080x1920, 30 fps). Historia ilustrativa sobre buscar empleo: Laura envía 47 hojas de vida en 3 meses y recibe cero respuestas. Entiende que toca puertas pero nadie sabe que existe, así que publica gratis su hoja de vida en **Contrátame Sumiago** (foto, experiencia y habilidades; su teléfono y correo solo los ven empresas registradas). Un martes, una empresa la encuentra buscando por profesión y ciudad. Mensaje: "A veces no te falta talento. Te falta que te vean." Invita a publicar la hoja de vida o a compartirlo con quien busca trabajo, sin prometer empleo.

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
python ruta/dia-35/scripts/voz.py
python ruta/dia-35/scripts/tl.py
python ruta/dia-35/scripts/align.py
python ruta/dia-35/scripts/audio.py
python ruta/dia-35/scripts/render.py 0 580 a.mp4
python ruta/dia-35/scripts/render.py 580 1160 b.mp4
python ruta/dia-35/scripts/render.py 1160 99999 c.mp4
(echo file a.mp4 & echo file b.mp4 & echo file c.mp4) > l.txt     (Linux/Mac: printf "file a.mp4\nfile b.mp4\nfile c.mp4\n" > l.txt)
ffmpeg -y -f concat -i l.txt -i mix.wav -map 0:v -map 1:a -c:v libx264 -preset slow -b:v 1150k -maxrate 1600k -bufsize 3000k -c:a aac -b:a 160k -shortest -movflags +faststart dia-35.mp4
python ruta/dia-35/scripts/pc.py dia-35.mp4 dia-35-pc.mp4
```

Para revisar un momento: `python ruta/dia-35/scripts/render.py still 12 27.5`.

## Escenas

| # | Frase | En pantalla | Cámara / sonido |
|---|-------|-------------|-----------------|
| 0 | Laura envió 47 hojas de vida en 3 meses | Portátil con la hoja de vida, sobres que salen volando, contador "ENVIADAS" de 0 a 47, chip "3 MESES" | se aleja; un pop por cada sobre |
| 1 | Respuestas: cero | Bandeja de entrada vacía, "0" rojo gigante, "Sin respuestas", bolita de polvo que rueda | temblor + golpe en "cero" |
| 2 | Cada mañana revisaba el correo… | Amanecer, cama, celular con el correo cargando "No hay mensajes", días que pasan (LUN…DOM), "6:30 a. m." | |
| 3 | …tocaba puertas… nadie sabía que existía | Pasillo de puertas, Laura camina tocando ("toc toc"); todo se vuelve gris y aparece "?" | la cámara sigue a Laura; toques |
| 4 | Hizo lo contrario: dejó de buscar y se dejó encontrar | Flechas que salen de Laura **se invierten** y llegan desde empresas; foco de luz; chips "DEJÓ DE BUSCAR" / "SE DEJÓ ENCONTRAR" | whoosh + brillo |
| 5 | Publicó su hoja de vida gratis en Contrátame Sumiago… | Tarjeta "CONTRÁTAME SUMIAGO": foto, nombre, experiencia, habilidades y sello "GRATIS" | Laura se transforma en la foto del perfil; la cámara baja |
| 6 | Su teléfono… solo lo ven las empresas registradas | Número que se oculta (+57 300 ••• ••45) con candado, público tachado y tarjeta "Empresas registradas" con ✓ | la cámara va a la tarjeta de empresas |
| 7 | Un martes a las 10… por profesión y ciudad | Buscador que escribe "Contadora", chips "Contadora" y "Medellín", resultados con Laura resaltada y botón "Contactar" | la cámara sigue a su resultado; tecleo + ding |
| 8 | No le pidieron que enviara nada. Ya la conocían. | Foto de Laura y mensaje de la empresa "¿Podemos hablar mañana?", sello "ELLOS LA BUSCARON" | |
| 9 | A veces no te falta talento. Te falta que te vean. | Foco sobre la foto de Laura con chispas; "TE FALTA QUE TE VEAN" | brillo |
| 10 | Si estás buscando trabajo, o conoces a alguien… | Hoja de vida en el centro que se comparte con 4 personas; chip "PUBLICAR ES GRATIS" | pops |
| 11 | Entra al link de mi perfil… te busquen a ti | Tarjeta de Sumiago "Contrátame Sumiago · Publica tu hoja de vida · GRATIS", mascota, "LINK EN MI PERFIL" y "…te busquen a ti." | pops |
| — | Cierre | Logo con rebote, ondas, chispas y brillo; "Que te busquen a ti" y "LINK EN MI PERFIL" | brillo |

## Estilo y reglas

- Búsqueda: azul grisáceo con cuadrícula; la parte de Sumiago en rojo, negro, blanco y gris. Rótulo "Historia ilustrativa".
- Subtítulos arriba a la izquierda; cada palabra sube desde detrás de una máscara y las clave van en rojo con subrayado.
- Técnicas: texto desde máscara, movimientos encadenados, cámara que sigue lo importante, objeto que se transforma (`morph`), animaciones sincronizadas con la voz (`wt()` + `align.py`), música bajita (más baja en la parte triste) y efectos.
- Datos reales de Contrátame Sumiago: publicar la hoja de vida es gratis, el perfil se revisa antes de publicarse, el contacto solo lo ven empresas registradas y las empresas buscan por profesión, ciudad, experiencia y nivel académico. No prometer empleo ni ganancias. No escribir «BinanTrader».
