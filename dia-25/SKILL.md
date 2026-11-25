---
name: dia-25
description: Crea el video del Día 25 de Tareas Diarias de Sumiago, "Dos barberos en la misma calle: Carlos y Andrés", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 25.
---

# Día 25 — "Dos barberos en la misma calle: Carlos y Andrés"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro con figuras de palitos: dos barberías 'CARLOS' y 'ANDRÉS' (letrero 'LLENO'), reloj y silla vacía, teléfono del Marketplace 'Cortes para caballero', chat '¿Tienes cita el sábado?', 'CITA RESERVADA', portada 'Andrés Barber' con 'RESERVAR CITA', camino de recomendaciones 'HERMANO · BODA', 'SIN ANUNCIO' y lista 'LA DIFERENCIA'. Voz: narrador (probable). Nota: la voz original dice 'Summago'; aquí está corregido.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 12 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "narrador educativo sumiago" (`bd35c17b29c54d3e9d2663863a28d212`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-25/scripts/voz.py
python ruta/dia-25/scripts/audio.py
python ruta/dia-25/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-25.mp4
python ruta/dia-25/scripts/pc.py dia-25.mp4 dia-25-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-25/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | Dos barberos en la misma calle. Mismo corte, mismo precio, pero uno vive lleno y el otro esperando. | «Carlos» (VACÍO) contra «Andrés» (LLENO) con VS |
| 1 | Carlos corta bien, pero su silla pasa casi todo el día vacía. | Título «CARLOS / corta bien… pero nadie llega», icono reloj |
| 2 | Andrés, en cambio, publicó su servicio en el marketplace de Sumiago: | Teléfono «Marketplace» con Cortes para caballero, Barbería · Tu ciudad; botón «CONTACTAR»; la cámara sigue la fila nueva |
| 3 | «Cortes para caballeros que quieren verse espectaculares en su boda, sus 15 años, su cumpleaños o cualquier evento». | «Su anuncio»: tarjetas Boda, 15 años, Cumpleaños, Eventos (cada una entra cuando se nombra) |
| 4 | Un joven ve el anuncio, le escribe y reserva su cita. | Habla el segundo personaje (burbuja) |
| 5 | Andrés le hace el corte y le dice: «Estás listo». | Habla la mascota (burbuja) |
| 6 | Y antes de que se vaya, le regala el enlace de su portada de negocio en Sumiago. | Título «El regalo: / su portada» con «sumiago.com/andres», icono enlace |
| 7 | Ahí están su WhatsApp, sus redes sociales, los videos de sus cortes y un botón para reservar citas personalizadas. | Teléfono «Andrés Barber» con WhatsApp, Instagram · TikTok, Videos de cortes, RESERVAR CITA; la cámara sigue la fila nueva |
| 8 | Para su próximo evento, el cliente reserva en un clic y comparte la portada con su hermano y sus amigos. | «Y la comparte»: tarjetas Reserva en un clic, Su hermano, Sus amigos (cada una entra cuando se nombra) |
| 9 | Carlos también corta bien, pero nadie lo encuentra, y sus clientes no saben cómo volver. | Título «CARLOS… / nadie lo encuentra», icono alerta |
| 10 | Un anuncio, un enlace: clientes que llegan, vuelven y traen más. | «La diferencia»: tarjetas Un anuncio, Un enlace, Vuelven y traen más (cada una entra cuando se nombra) |
| 11 | Publica gratis tu servicio en Sumiago y crea tu portada de negocio. Entra al enlace de mi perfil. | Logo, «Publica gratis tu servicio y crea tu portada», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Marketplace · WhatsApp · redes · reservas» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
