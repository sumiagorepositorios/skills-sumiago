---
name: dia-22
description: Crea el video del Día 22 de Tareas Diarias de Sumiago, "20 años estudiando (versión con enlace del perfil)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 22.
---

# Día 22 — "20 años estudiando (versión con enlace del perfil)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música tensa al inicio y con ritmo desde el giro, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Igual al Día 21 (misma historia y estilo claro), pero el cierre invita a dar clic al enlace del perfil en vez de comentar. Voz: narrador (probable). Nota: se añadió el aviso 'Ejemplo ilustrativo…' a la frase de los sueldos mínimos.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 9 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-22/scripts/voz.py
python ruta/dia-22/scripts/audio.py
python ruta/dia-22/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-22.mp4
python ruta/dia-22/scripts/pc.py dia-22.mp4 dia-22-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-22/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Sabías que pasas casi 20 años de tu vida estudiando para ganar un sueldo que no te alcanza? | Cifra grande «19» y «años estudiando» (para un sueldo que no te alcanza) |
| 1 | Naces, y apenas tienes uso de conciencia, tus padres te ponen a estudiar. | Título «NACES… / ¡Y A ESTUDIAR!», icono libro |
| 2 | Preescolar, hasta tres años. Primaria, cinco años. Bachillerato, seis años más. Y la universidad, cuatro o cinco años. | «Tu vida estudiando»: barras Preescolar 3 años, Primaria 5 años, Bachillerato 6 años, Universidad 4–5 años |
| 3 | En total, de 16 a 19 años de tu vida. | Cifra grande «16–19» y «años de tu vida» |
| 4 | ¿Y todo para qué? Para conseguir un empleo y dedicarle muchos años más. | Título «¿Y todo para qué? / UN EMPLEO», icono maleta |
| 5 | Tanto tiempo aprendiendo para ser empleado y terminar con ingresos lineales que no alcanzan para nada. Irónico, ¿no? | «Sueldo» (LINEAL) contra «Gastos» (SUBEN) con VS |
| 6 | En Sumiago le dedicas unas horas al día a tu propio negocio, con las herramientas que te damos. | «SUMIAGO»: tarjetas Unas horas al día, Tu propio negocio, Herramientas (cada una entra cuando se nombra) |
| 7 | Y aprendiendo con las tareas diarias que te recomendamos, puedes ganar desde los primeros meses de dos a cinco sueldos mínimos. | Cifra grande «2 a 5» y «sueldos mínimos» (con tareas diarias y constancia); aviso pequeño «Ejemplo ilustrativo…» |
| 8 | Ve a mi perfil y dale clic al enlace para que te registres en Sumiago. | Logo, «Regístrate en Sumiago», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Tu propio negocio con Sumiago» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
