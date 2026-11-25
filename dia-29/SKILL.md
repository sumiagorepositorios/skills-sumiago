---
name: dia-29
description: Crea el video del Día 29 de Tareas Diarias de Sumiago, "Conversación: Nico quiere entrar a Sumiago", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 29.
---

# Día 29 — "Conversación: Nico quiere entrar a Sumiago"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Diálogo de 50 s sobre fondo oscuro con resplandor rojo: Nico (personaje de gorra azul y gafas, sin logo) y la mascota Sumiago en planos alternos, subtítulos arriba con palabras en dorado y etiquetas ('¿TIENES GANAS?', 'GANA CON MARKETING', 'TAREAS DIARIAS', 'REFERIDOS DE REGALO', 'NOS AYUDAMOS', 'LINK EN MI PERFIL'); cierre blanco con logo. Voces: Esqueleto (Sumiago) y Lee know (Nico). En este motor Nico es un personaje dibujado sencillo, sin logo.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 13 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Esqueleto", la mascota (`a335d470fff248e8890dce6550a2874b`), "Lee know", Nico (`95f7b8fe6a264953bad59931c6f8c571`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-29/scripts/voz.py
python ruta/dia-29/scripts/audio.py
python ruta/dia-29/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-29.mp4
python ruta/dia-29/scripts/pc.py dia-29.mp4 dia-29-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-29/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¡Sumiago! Me contaron que en tu comunidad se gana muchísimo. ¡Yo quiero entrar ya! | Habla el segundo personaje (burbuja) |
| 1 | Jaja, tranquilo. Primero dime algo: ¿tienes ganas de aprender y de trabajar en serio? | Habla la mascota (burbuja) |
| 2 | ¡Claro que sí! Estoy dispuesto a trabajar. | Habla el segundo personaje (burbuja) |
| 3 | Eso es lo más importante. Aquí entras a Gana con Marketing, con cursos de marketing e inteligencia artificial. | Habla la mascota (burbuja) |
| 4 | ¿Y si no sé nada de redes sociales? | Habla el segundo personaje (burbuja) |
| 5 | Por eso existen las tareas diarias. Cada día te decimos qué hacer, paso a paso. | Habla la mascota (burbuja) |
| 6 | Pero yo no conozco a nadie. | Habla el segundo personaje (burbuja) |
| 7 | Tranquilo. Con tu portada y tus videos, las personas interesadas te escriben a ti. | Habla la mascota (burbuja) |
| 8 | Y cuando alguien se registra directo en Sumiago, el sistema se lo asigna a quien menos referidos tenga. | Habla la mascota (burbuja) |
| 9 | ¿Referidos de regalo? ¡Eso no lo hace nadie! | Habla el segundo personaje (burbuja) |
| 10 | Y lo mejor: aquí nos ayudamos entre todos. Cuando a tu equipo le va bien, a ti también. | Habla la mascota (burbuja) |
| 11 | ¡Ya quiero empezar! ¿Qué tengo que hacer? | Habla el segundo personaje (burbuja) |
| 12 | Ve al link de mi perfil y te acompaño desde el primer paso. Esto es Sumiago. | Logo, «Te acompaño desde el primer paso», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Aprendemos y crecemos juntos» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
