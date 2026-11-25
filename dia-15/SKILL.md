---
name: dia-15
description: Crea el video del Día 15 de Tareas Diarias de Sumiago, "Empléate Ya: deja que las empresas te encuentren", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 15.
---

# Día 15 — "Empléate Ya: deja que las empresas te encuentren"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con foto de trabajadores, teléfono 'CONTRÁTAME SUMIAGO', lista 'TAREAS' de 5 pasos, tarjeta 'EN REVISIÓN → PERFIL APROBADO', mascota femenina con laptop, buscador de empresas y botón 'Contactar candidato'. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 8 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-15/scripts/voz.py
python ruta/dia-15/scripts/audio.py
python ruta/dia-15/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-15.mp4
python ruta/dia-15/scripts/pc.py dia-15.mp4 dia-15-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-15/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Buscas empleo? Deja que las empresas te encuentren. | Título «¿Buscas empleo? / Deja que te encuentren», icono maleta |
| 1 | En Sumiago, en la sección «Empléate Ya», publicas tu hoja de vida totalmente gratis y cientos de empresas pueden descubrir tu talento. | Teléfono «Contrátame Sumiago» con ¿Buscas empleo?, Publicar mi hoja de vida, GRATIS, Buscar talento; la cámara sigue la fila nueva |
| 2 | Te inscribes en cinco pasos: tus datos, tu perfil, tu experiencia, tu disponibilidad y tus documentos. | Teléfono «5 pasos» con ✓ Datos básicos, ✓ Perfil profesional, ✓ Experiencia laboral, ✓ Disponibilidad, ✓ Documentos; la cámara sigue la fila nueva |
| 3 | Revisamos tu perfil y, si falta algo, te avisamos por WhatsApp o correo para que lo completes. | tarjetas En revisión, WhatsApp, Perfil aprobado (cada una entra cuando se nombra) |
| 4 | Tus datos están bajo tu control: tu teléfono y tu correo solo los ven empresas registradas, y tú decides qué se publica. | Título «Tus datos, / bajo tu control» con «Tú decides qué se publica», icono escudo |
| 5 | ¿Tienes una empresa? Busca talento por profesión, ciudad, experiencia y nivel académico, guarda tus favoritos y descarga la hoja de vida en PDF. | «¿Tienes una empresa?»: tarjetas Profesión, Ciudad, Experiencia, Nivel académico, Favoritos, PDF (cada una entra cuando se nombra) |
| 6 | Las empresas te contactan directamente a tu WhatsApp o a tu correo, sin intermediarios. | Título «Sin / intermediarios», icono chat |
| 7 | Publica hoy mismo tu hoja de vida gratis en Sumiago. El link está en mi perfil. | Logo, «Publica gratis tu hoja de vida hoy», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Empléate Ya en Sumiago» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
