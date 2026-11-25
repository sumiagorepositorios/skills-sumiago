---
name: dia-14
description: Crea el video del Día 14 de Tareas Diarias de Sumiago, "Publica tu hoja de vida en Contrátame Sumiago (5 pasos)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 14.
---

# Día 14 — "Publica tu hoja de vida en Contrátame Sumiago (5 pasos)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro con ventana 'contrátame · hoja de vida' que avanza por los pasos 01–05 (datos básicos, perfil profesional, disponibilidad, documentos, autorizaciones), tarjeta de 'María González' con mensaje de WhatsApp de una empresa y botones para compartir; cierre 'PUBLICA GRATIS' con flecha. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 10 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-14/scripts/voz.py
python ruta/dia-14/scripts/audio.py
python ruta/dia-14/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-14.mp4
python ruta/dia-14/scripts/pc.py dia-14.mp4 dia-14-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-14/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Buscas empleo? Publica tu hoja de vida gratis en Contrátame Sumiago, en cinco pasos. | Título «¿BUSCAS / EMPLEO?» con «Hoja de vida gratis · 5 pasos», icono maleta |
| 1 | Paso uno: tus datos básicos. Nombre, país, ciudad, correo y WhatsApp. | Teléfono «Datos básicos · 01» con Nombre, País, Ciudad, Correo, WhatsApp; la cámara sigue la fila nueva |
| 2 | Paso dos: tu perfil profesional. Profesión, cargo al que aspiras, experiencia y habilidades. | Teléfono «Perfil profesional · 02» con Profesión, Cargo, Experiencia, Habilidades; la cámara sigue la fila nueva |
| 3 | Paso tres: tu disponibilidad. Modalidad, jornada y tipo de contrato. | Teléfono «Disponibilidad · 03» con Modalidad, Jornada, Tipo de contrato; la cámara sigue la fila nueva |
| 4 | Paso cuatro: sube tu foto profesional y tu hoja de vida en PDF. | «Documentos · 04»: tarjetas Foto profesional, Hoja de vida PDF (cada una entra cuando se nombra) |
| 5 | Y paso cinco: tú autorizas qué se publica. Tu teléfono y tu correo solo los ven empresas registradas. | Teléfono «Autorizaciones · 05» con Publicar mi perfil ✓, Mostrar mi foto ✓, Teléfono y correo: privados; la cámara sigue la fila nueva |
| 6 | Revisamos tu perfil, lo publicamos y las empresas te escriben directo a tu WhatsApp. | «Las empresas te contactan»: tarjetas Revisamos, Publicamos, WhatsApp (cada una entra cuando se nombra) |
| 7 | Además, puedes compartir el enlace de tu hoja de vida con cualquier empresa por tus redes sociales, para que la visiten y te contraten. | «Comparte tu hoja de vida»: tarjetas WhatsApp, Facebook, Instagram, LinkedIn (cada una entra cuando se nombra) |
| 8 | Todo organizado en un solo lugar: Sumiago. | Título «Todo en / un solo lugar» y el logo |
| 9 | Publica tu hoja de vida gratis. Visita el enlace de mi perfil y regístrate en Sumiago. | Logo, «Publica gratis tu hoja de vida», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Publica gratis tu hoja de vida» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
