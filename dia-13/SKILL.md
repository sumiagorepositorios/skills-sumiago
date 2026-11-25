---
name: dia-13
description: Crea el video del Día 13 de Tareas Diarias de Sumiago, "Contrátame Sumiago: empleo y talento", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 13.
---

# Día 13 — "Contrátame Sumiago: empleo y talento"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro con globo terráqueo de líneas rojas, logo 'CONTRÁTAME SUMIAGO #1', tarjeta de 'María González', candado, buscador 'Encuentra talento', etiquetas de áreas y foto de trabajadores. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 11 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-13/scripts/voz.py
python ruta/dia-13/scripts/audio.py
python ruta/dia-13/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-13.mp4
python ruta/dia-13/scripts/pc.py dia-13.mp4 dia-13-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-13/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Buscas empleo o buscas al empleado perfecto? | «Busco empleo» (TALENTO) contra «Busco empleados» (EMPRESAS) con VS |
| 1 | ¡Atención, empresas y personas de todos los países! | Título «¡ATENCIÓN! / Todos los países», icono mundo |
| 2 | Llegó Contrátame Sumiago, la plataforma número uno para conectar el talento con las empresas. | Título «CONTRÁTAME / SUMIAGO» con «Talento + Empresas» y el logo |
| 3 | Si buscas trabajo, publica tu hoja de vida gratis en solo cinco pasos. | Teléfono «Hoja de vida · gratis» con 1. Datos básicos, 2. Perfil profesional, 3. Experiencia, 4. Disponibilidad, 5. Documentos; la cámara sigue la fila nueva |
| 4 | Agrega tu experiencia, tus habilidades, tus idiomas y tu disponibilidad. | «María González»: tarjetas Experiencia, Habilidades, Idiomas, Disponibilidad (cada una entra cuando se nombra) |
| 5 | Tú decides qué se publica: tus datos están protegidos. | Título «Tus datos / protegidos», icono escudo |
| 6 | Y si tienes una empresa, filtra por país, ciudad, experiencia y nivel académico. | Teléfono «Encuentra talento» con País, Ciudad, Experiencia, Nivel académico, BUSCAR TALENTO; la cámara sigue la fila nueva |
| 7 | Encuentra al candidato ideal en segundos y contáctalo directamente. | tarjetas Carlos M., Valentina R., Contactar (cada una entra cuando se nombra) |
| 8 | Administración, ventas, tecnología, salud, construcción, trabajo remoto y mucho más. | tarjetas Administración, Ventas, Tecnología, Salud, Construcción, Remoto (cada una entra cuando se nombra) |
| 9 | Miles de oportunidades te están esperando. | Título «Miles de / oportunidades», icono estrella |
| 10 | Regístrate gratis en Sumiago y entra a Contrataciones. ¡Tu próximo empleo empieza hoy! | Logo, «Tu próximo empleo empieza hoy», mascota con el pulgar y botón «REGÍSTRATE GRATIS» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Contrátame Sumiago» y botón «REGÍSTRATE · LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
