---
name: dia-23
description: Crea el video del Día 23 de Tareas Diarias de Sumiago, "Trabajas para los sueños de otros", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 23.
---

# Día 23 — "Trabajas para los sueños de otros"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música tensa al inicio y con ritmo desde el giro, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con franjas rosadas y píldora 'SUMIAGO': reloj '8 A 11 HORAS', lista 'TU DÍA NORMAL' (5:00 AM, 1 hora, 8 horas), '5 días × 48 semanas', '× 40 años = 76.800 horas', '¿Quién se queda con esas horas? La empresa de otro', casa/carro/avión, 'Y a ti: lo justo… LUNES', 'Sumiago' con tres beneficios, luna 'en tus horas libres' y 'ESCRIBE SUMIAGO'. Voz: narrador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 11 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-23/scripts/voz.py
python ruta/dia-23/scripts/audio.py
python ruta/dia-23/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-23.mp4
python ruta/dia-23/scripts/pc.py dia-23.mp4 dia-23-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-23/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Trabajas todos los días de 8 a 12 horas para los sueños de otros? | Cifra grande «8 a 12» y «horas todos los días» (para los sueños de otros) |
| 1 | Te levantas a las 5, una hora de trayecto, 8 horas de trabajo y otra hora de regreso. | Teléfono «Tu día normal» con 5:00 AM · Despertar, 1 hora · Trayecto, 8 horas · Trabajo, 1 hora · Regreso; la cámara sigue la fila nueva |
| 2 | 5 días a la semana, 48 semanas al año: casi 2000 horas. | Cifra grande «2000» y «horas al año» (5 días × 48 semanas) |
| 3 | Multiplícalo por 40 años de trabajo: 76.800 horas. | Cifra grande «76.800» y «horas de tu vida» (× 40 años) |
| 4 | ¿Y quién se queda con el fruto de esas horas? La empresa de otro. | Título «¿Quién se queda / con esas horas?» con «La empresa de otro», icono maleta |
| 5 | Tú construyes su casa, su carro y sus vacaciones, y a ti te pagan lo justo para que vuelvas el lunes. | «Tú construyes…»: tarjetas Su casa, Su carro, Sus vacaciones (cada una entra cuando se nombra) |
| 6 | Si un día faltas, te descuentan. Si un día no estás, te reemplazan. | «Si faltas» (DESCUENTO) contra «Si no estás» (REEMPLAZO) con VS |
| 7 | No es tu culpa: te enseñaron a trabajar para otros, nunca para ti. | Título «No es / tu culpa» con «te enseñaron a trabajar para otros», icono libro |
| 8 | En Sumiago, cada hora que inviertes construye tu propio negocio, con herramientas y tareas diarias guiadas. | «SUMIAGO»: tarjetas Cada hora es para ti, Tu propio negocio, Herramientas + tareas (cada una entra cuando se nombra) |
| 9 | Puedes comenzar en tus horas libres, sin renunciar hoy a tu empleo. | Título «En tus / horas libres», icono reloj |
| 10 | Escribe «Sumiago» y te paso la información para comenzar hoy. | Logo, «Escribe SUMIAGO y comienza hoy», mascota con el pulgar y botón «COMENTA SUMIAGO» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Comienza hoy en tus horas libres» y botón «COMENTA «SUMIAGO»» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
