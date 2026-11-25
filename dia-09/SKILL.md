---
name: dia-09
description: Crea el video del Día 9 de Tareas Diarias de Sumiago, "Tu negocio en un solo enlace (Mi Portada paso a paso)", en móvil 9:16 y PC 16:9, con voz de Fish Audio, música bajita, efectos y cierre con el logo. Úsala cuando pidan hacer, rehacer o adaptar el video del Día 9.
---

# Día 9 — "Tu negocio en un solo enlace (Mi Portada paso a paso)"

Reel vertical (dibujado a 720x1280 y entregado a 1080x1920, 30 fps) hecho con el **motor común de Sumiago**: cada frase del guion es una escena. Tema claro (blanco con puntos rojos suaves); música con ritmo, bajita.

**Importante:** esta skill **recrea** el video con el motor común (mismo guion, misma voz y mismo mensaje), pero **no es una copia exacta** del video publicado: ese se hizo con otro código que no se guardó. Cómo era el original: Reel claro con pantallas de la app (registro, código de verificación, menú 'Mi Portada', portada de 'Ferrelandia', redes, plantillas, 'Mi Negocio') y etiqueta 'PASO N' arriba; cierre oscuro con logo y 'sumiago.com'. Voz: presentador (probable).

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH. Paquetes: `pip install pillow numpy`
- Fuente **Inter** (Inter-Black, Inter-Bold, Inter-SemiBold, Inter-Medium .otf), instalada o copiada a una carpeta `fonts/` dentro de la skill.
- Las imágenes ya vienen en `assets/`: `sumiago-a.png` y `sumiago-c.png` (mascota con boca abierta/cerrada), `mascota-pulgar.png` y `logo-sumiago.png`.
- Tu clave de Fish Audio en `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Archivos

- `guion.json`: las 14 frases (texto del subtítulo y, si cambia la pronunciación, `voz_texto`), la escena de cada frase, palabras clave en rojo, tema, música y textos de la versión PC.
- `scripts/voz.py`: voz con Fish Audio — "Presentador" (`6d13d023d0f44401a6070bdfde9ef620`) (voces probables del original); quita silencios, 4 % más rápida, y crea `tl.json` con el momento de cada palabra (usa las pausas reales de la voz). `--sin-voz` estima los tiempos para revisar sin gastar voz.
- `scripts/motor.py`: dibuja las escenas (título, lista numerada, tarjetas, teléfono, cifra, comparación, barras, diálogo, cierre) y el cierre con el logo.
- `scripts/audio.py`: voz + música hecha por código (sin derechos de autor) + whoosh en cada cambio de escena, pops, dings y brillo del logo.
- `scripts/pc.py`: versión 1920x1080 (el reel a la derecha y el mensaje a la izquierda).

## Pasos

Copia `guion.json` a una carpeta vacía y ejecuta desde ahí (en Windows usa `set` en vez de `export`):

```
export FISH_API_KEY=tu_clave
python ruta/dia-09/scripts/voz.py
python ruta/dia-09/scripts/audio.py
python ruta/dia-09/scripts/motor.py 0 999999 video.mp4
ffmpeg -y -i video.mp4 -i mix.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k -shortest -movflags +faststart dia-09.mp4
python ruta/dia-09/scripts/pc.py dia-09.mp4 dia-09-pc.mp4
```

Para ir más rápido, parte el paso de cuadros en dos ventanas (por ejemplo `0 700 a.mp4` y `700 999999 b.mp4`) y únelas con `ffmpeg -f concat`. Para revisar una escena sin hacer todo el video: `python ruta/dia-09/scripts/motor.py still 5 12.5` (deja `still_5.jpg`…). Mira y escucha el video completo antes de publicarlo.

## Escenas

| # | Frase (voz) | En pantalla |
|---|-------------|-------------|
| 0 | ¿Tienes un negocio y tus clientes no saben dónde encontrarte? | Título «¿Tus clientes no saben / dónde encontrarte?» |
| 1 | Con Sumiago creas gratis tu portada de negocio: un solo enlace con todo lo que ofreces. Te muestro cómo, paso a paso. | Teléfono «Ferrelandia» con Catálogo, Cómo llegar, Promo de la semana; botón «Escríbenos»; la cámara sigue la fila nueva |
| 2 | Primero entra a sumiago.com y toca «Registrarme». Elige tu usuario y escribe tu nombre y tu apellido. | Teléfono «sumiago.com/registro» con Registrarme, Usuario, Nombre, Apellido; la cámara sigue la fila nueva |
| 3 | Luego pon tu correo, tu país, tu WhatsApp y una contraseña. Acepta los términos y toca «Crear cuenta». | Teléfono «Tus datos» con Correo, País, WhatsApp, Contraseña, Crear cuenta; la cámara sigue la fila nueva |
| 4 | Te llega un código de seis dígitos a tu correo, lo escribes y tu cuenta queda verificada. | Cifra grande «482913» y «Tu código de verificación» (llega a tu correo) |
| 5 | Ya dentro de tu panel, toca «Mi Portada» en el menú. Son siete pasos sencillos y ves cómo queda en vivo. | «Mi Portada»: tarjetas Perfil, Enlaces, WhatsApp, Redes, Plantilla, Diseño (cada una entra cuando se nombra) |
| 6 | En «Perfil» sube tu logo o tu foto, escribe el nombre de tu negocio y una bio corta, y elige tu dirección: sumiago.com/el-nombre-de-tu-negocio. | Teléfono «Perfil» con Subir logo, Nombre del negocio, Bio corta, sumiago.com/tu-negocio; la cámara sigue la fila nueva |
| 7 | En «Enlaces» agrega lo importante: tu catálogo, tu ubicación, tus promociones. Si no sabes qué poner, toca «Ideas con IA», arrastra para ordenar y destaca el que más te importa. | «Todos tus enlaces»: tarjetas Catálogo, Ubicación, Promociones, Ideas con IA (cada una entra cuando se nombra) |
| 8 | Activa el botón de WhatsApp con tu número y un mensaje listo. Tu cliente toca el botón y te escribe al instante. | Teléfono «Ferrelandia» con Catálogo, Cómo llegar, Promo de la semana; botón «Escríbenos por WhatsApp»; la cámara sigue la fila nueva |
| 9 | Agrega tus redes sociales: Instagram, TikTok, Facebook, YouTube y muchas más. | «Todas tus redes»: tarjetas Instagram, TikTok, Facebook, YouTube (cada una entra cuando se nombra) |
| 10 | Elige tu plantilla. Gratis tienes oscuro, claro y rojo, y con tu membresía desbloqueas plantillas por tipo de negocio, tus propios colores y fuentes. | «Gratis» (INCLUIDO) contra «Membresía» (PRO) con VS |
| 11 | Y con tu membresía, en «Mi Negocio» conviertes tu portada en una tienda: catálogo con pedidos por WhatsApp, agenda de citas, captura de clientes, reseñas, menú digital con QR y cobros en USDT. | «Tu portada en una tienda»: tarjetas Catálogo, Agenda, Clientes, Reseñas, Menú QR, Cobros USDT (cada una entra cuando se nombra) |
| 12 | Por último, compártela: pon tu enlace en la biografía de Instagram y TikTok, envíalo por WhatsApp o imprime tu código QR. | «Compártela en todas partes»: tarjetas Bio de Instagram, WhatsApp, Código QR (cada una entra cuando se nombra) |
| 13 | Tu negocio en un solo enlace. Crea tu portada gratis hoy en sumiago.com. | Logo, «Tu negocio en un solo enlace», mascota con el pulgar y botón «sumiago.com» que late |
| — | Cierre | Pantalla blanca, logo de Sumiago con rebote, ondas, chispas y brillo; «Crea tu portada gratis» y botón «SUMIAGO.COM» |

## Estilo y reglas

- Rojo Sumiago `#E6262F`, blanco, negro y gris; píldora «SUMIAGO» arriba; subtítulos abajo en mayúsculas, en grupos de 3–4 palabras, y las palabras clave en rojo.
- Los textos **salen desde detrás de una máscara**, los elementos **entran encadenados**, la **cámara sigue** al elemento importante, el objeto principal de cada escena **se transforma** en el de la siguiente y cada elemento aparece **cuando la voz lo nombra** (campo `palabra`).
- La mascota oficial lleva el logo; el segundo personaje de los diálogos **no** lleva el logo de Sumiago.
- No escribir «BinanTrader». Las donaciones se llaman «Sumiagos». No prometer ganancias: cuando se hable de dinero, mostrar el aviso «Ejemplo ilustrativo…».
- Si cambias el guion, cada frase necesita su `escena`; para que algo aparezca al decirlo, pon en `palabra` el inicio de esa palabra tal como está en el texto.
