---
name: dia-24
description: Crea el video del Día 24 de Tareas Diarias de Sumiago, "Mismo carro, dos vendedores: Pedro y Juan", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 24.
---

# Día 24 — "Mismo carro, dos vendedores: Pedro y Juan"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema oscuro (negro con resplandor rojo); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel oscuro con figuras de palitos: Pedro y Juan con el mismo carro, periódico 'EL DIARIO clasificados' tachado, calendario 'MARZO', teléfono 'Fotoclasificados' con 'GRATIS', ficha 'Sedán 2019', ciudad con correos, burbujas '¿Sigue disponible?'/'¡Sí! ¿Nos vemos?', sello 'VENDIDO' con 5 estrellas y tarjetas 'MESES' vs 'DÍAS'. Voz: narrador (probable). Nota: la voz original dice 'foto clasificado' y a veces 'Sumeago'; aquí está corregido.

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
python ruta/dia-24/scripts/voz.py
python ruta/dia-24/scripts/audio.py
python ruta/dia-24/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-24.mp4
python ruta/dia-24/scripts/pc.py dia-24.mp4 dia-24-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-24/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | Dos personas venden el mismo carro. Uno tardó meses y el otro lo vendió en días. | «Pedro» (MESES) contra «Juan» (DÍAS) con VS |
| 1 | Pedro le pegó al vidrio un letrero de «Se vende» y pagó un aviso en el clasificado del periódico de su ciudad. | Título «PEDRO / aviso en el periódico», icono libro |
| 2 | Pero hoy casi nadie compra el periódico: las noticias se leen en el celular. | «Periódico» (NADIE) contra «Celular» (TODOS) con VS |
| 3 | Resultado: pasan los meses y el carro de Pedro sigue ahí. | Cifra grande «MESES» y «y el carro sigue ahí» |
| 4 | Juan, en cambio, lo publicó totalmente gratis en el fotoclasificado de Sumiago. | Teléfono «Fotoclasificados» con Sedán 2019, GRATIS; botón «PUBLICAR»; la cámara sigue la fila nueva |
| 5 | Subió sus fotos, el precio y todas las características. | Teléfono «Sedán 2019» con ✓ Fotos, ✓ Precio, ✓ Kilometraje; la cámara sigue la fila nueva |
| 6 | Y cada semana Sumiago envía un correo con los vehículos en venta a los usuarios de la misma ciudad de Juan. | «Cada semana»: tarjetas Correo, Vehículos en venta, Tu ciudad (cada una entra cuando se nombra) |
| 7 | Uno de ellos se interesó, le escribió y se citaron para ver el carro en persona. | Habla el segundo personaje (burbuja) |
| 8 | Le gustó, lo compró y calificó a Juan, que ahora tiene más reputación en Sumiago. | Cifra grande «★★★★★» y «¡VENDIDO!» (+ reputación para Juan) |
| 9 | Así de sencillo se vende hoy: rápido y eficaz. | «Pedro» (LENTO) contra «Juan» (RÁPIDO) con VS |
| 10 | Entra al enlace de mi perfil y comienza a vender tu vehículo hoy en Sumiago. | Logo, «Publica tu vehículo hoy, gratis», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Gratis en el fotoclasificado» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
