---
name: dia-26
description: Crea el video del Día 26 de Tareas Diarias de Sumiago, "Convierte tu teléfono en una herramienta para ganar (4 pasos)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 26.
---

# Día 26 — "Convierte tu teléfono en una herramienta para ganar (4 pasos)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con fondo de puntos, etiqueta 'SUMIAGO' arriba a la izquierda, @sumiagolatam y sumiago.com abajo: teléfono con 'Ganado hoy: $0', '$ 449', tarjetas de los 4 pasos, registro, portada 'Mi Negocio', Marketplace (bicicleta, celular, guitarra, tenis), hoja de vida con sello '¡CONTRATADO!', red 'TÚ' con comisiones, tablero 'Mi constancia' y 'Sueldo mensual'. Voz: narrador (probable). Nota: se añadió el aviso 'Ejemplo ilustrativo…' en las frases de dinero.

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
python ruta/dia-26/scripts/voz.py
python ruta/dia-26/scripts/audio.py
python ruta/dia-26/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-26.mp4
python ruta/dia-26/scripts/pc.py dia-26.mp4 dia-26-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-26/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¡Para, para, para! ¿Andas scrolleando video tras video y sin monetizar nada? | Cifra grande «$0» y «Ganado hoy» (video tras video, sin monetizar) |
| 1 | Quédate, que aquí te enseño a convertir tu teléfono en una máquina de generar dinero. | Teléfono «Ganancias» con Tu portada, Marketplace, Comisiones; la cámara sigue la fila nueva; aviso pequeño «Ejemplo ilustrativo…» |
| 2 | Solo en unos simples pasos. | «Solo en 4 pasos»: tarjetas Regístrate, Portada, Marketplace, Empleos (cada una entra cuando se nombra) |
| 3 | Uno: dale clic al enlace de mi perfil y regístrate rápido en Sumiago. | Número 1 grande y tarjeta «Regístrate en Sumiago»: Dale clic al enlace de mi perfil. ¡Registro listo! |
| 4 | Dos: crea tu portada de negocio, con tu WhatsApp, tus redes y tus productos. | Número 2 grande y tarjeta «Tu portada de negocio»: Con tu WhatsApp, tus redes y tus productos. |
| 5 | Tres: sube los artículos usados que quieras vender en el marketplace. | Número 3 grande y tarjeta «Vende en el Marketplace»: Bicicleta, celular, guitarra, tenis… lo que quieras vender. |
| 6 | Cuatro: si eres estudiante o profesional, llena tu hoja de vida en Empleos para que las empresas te contraten. | Número 4 grande y tarjeta «Tu hoja de vida en Empleos»: Para que las empresas te encuentren y te contraten. |
| 7 | Y usa todas las herramientas para monetizar. | Título «Usa todas las / herramientas», icono check |
| 8 | Ahora, si recomiendas la oportunidad a tu familia, amigos y conocidos, ganas comisiones directas, continuas y exponenciales. | «Comisiones directas»: tarjetas Familia, Amigos, Conocidos, Comisiones (cada una entra cuando se nombra) |
| 9 | Y con constancia y disciplina puedes lograr un sueldo en Sumiago a mediano plazo. | «Mi constancia»: tarjetas Constancia, Disciplina, Sueldo mensual (cada una entra cuando se nombra); aviso pequeño «Ejemplo ilustrativo…» |
| 10 | ¿Qué esperas? Comienza hoy en Sumiago. Dale clic al enlace de mi perfil. | Logo, «Comienza hoy en Sumiago», mascota con el pulgar y botón «LINK EN MI PERFIL» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «¿Qué esperas? Comienza hoy» y botón «LINK EN MI PERFIL» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
