---
name: neondtf-mejor-tenerlo
description: Crea el video de socio "NeonDTF: mejor tenerlo y no necesitarlo" (9:16, historia de pedido urgente con chat, dos caminos, voz de Fish Audio y cierre de Sumiago). Úsala cuando pidan hacer, rehacer o adaptar este video, o una historia parecida para otro socio.
---

# Video de socio "NeonDTF: mejor tenerlo y no necesitarlo"

Video vertical 9:16 (1080x1920, 30 fps, unos 62 s) para Neon Estudio DTF (neondtf.store). Cuenta una historia que vive todo taller DTF: un cliente pide 50 camisetas para mañana con un logo borroso. Muestra dos caminos (sin herramientas: cliente perdido; con NeonDTF: listo en 2:47 y otro pedido en camino), remata con "es mejor tenerlo y no necesitarlo, que necesitarlo y no tenerlo" y cierra con la publicidad de Sumiago.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy`
- Las fuentes vienen en `fonts/` (Inter Display Black, Poppins Bold y Medium, licencia OFL).
- El logo de Sumiago con fondo blanco viene en `assets/logo-sumiago-fondo-blanco.png`.
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Pasos

Trabaja en una carpeta vacía (por ejemplo `trabajo/`) y ejecuta los scripts desde ahí.

1. **Voz.** Lee `guion.txt` (11 líneas: 10 del video y la última del cierre de Sumiago):
   ```
   set FISH_API_KEY=tu_clave
   python ruta/neondtf-mejor-tenerlo/scripts/voz.py
   ```
   Usa la voz `8730dce743254904a745d6e134e18c6b` con el modelo `s1`. Si Fish responde 402 (sin crédito de API), usa el modelo gratis: `set FISH_MODEL=s2.1-pro-free`. Deja `vo/00.wav` a `vo/10.wav`.

2. **Revisión rápida** antes del render completo:
   ```
   python ruta/neondtf-mejor-tenerlo/scripts/escenas.py preview 0@6.5 1@3.2 3@8.0 4@8.0 6@2.5 7@2.0
   ```
   Abre `prueba.jpg` y revisa que los textos y los globos del chat no se tapen.

3. **Armar el video.**
   ```
   python ruta/neondtf-mejor-tenerlo/scripts/armar.py
   ```
   Sale `out/neondtf-mejor-tenerlo.mp4`. Si una frase dura más que su escena, avisa en pantalla.

4. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

| # | Dur. | Frase | En pantalla |
|---|------|-------|-------------|
| 1 | 6,8 s | Son las seis de la tarde… | "6:00 PM" y chat "Cliente nuevo": "Necesito 50 camisetas", "PARA MAÑANA", foto del logo malo, "¿Se puede?" |
| 2 | 3,5 s | Logo borroso, pixelado y con fondo | Logo grande con sellos rojos BORROSO, PIXELADO, CON FONDO |
| 3 | 2,6 s | Dos caminos | "2 CAMINOS" con flecha roja (SIN) y cian (CON NEON) |
| 4 | 8,5 s | Sin las herramientas… | Fondo rojizo, reloj que corre hasta la madrugada, lista con X, chat "Mejor lo hago en otro lado" y sello CLIENTE PERDIDO |
| 5 | 9,2 s | Con Neon DTF… | El logo se arregla en 3 pasos (quitar fondo, vectorizar, mejorar), cronómetro y "LISTO EN 2:47 MIN" |
| 6 | 4,6 s | Pedido entregado… | Sello PEDIDO ENTREGADO, chat "¡Quedó perfecto!" y "+100" |
| 7 | 4,5 s | Es mejor tenerlo y no necesitarlo | "TENERLO" en cian |
| 8 | 3,2 s | Que necesitarlo y no tenerlo | "NECESITARLO" rojo y "Y NO TENERLO." con efecto glitch |
| 9 | 5,6 s | Dieciséis herramientas… | Contador 16, cuadrícula y "MUCHAS SON GRATIS" |
| 10 | 6,8 s | Entra hoy… | Logo, "ENTRA HOY", web, sello URGENTE y "Link en el perfil" |
| 11 | 7,0 s | ¿Quieres videos como este…? | Cierre Sumiago con logo animado y botón "sumiago.com" |

## Estilo y reglas

- Reutiliza el estilo neón de `base.py` (mismas funciones que el video "neondtf-herramientas").
- La música cambia con la historia: tensa con tic-tac de reloj al principio, entra el ritmo completo en "Con Neon DTF", pausa dramática en la frase final y vuelve el ritmo en el cierre.
- El chat es genérico (sin logo de WhatsApp ni de otra app).
- Para otro socio: cambia `guion.txt`, los textos de `escenas.py` y los tiempos de `SCENES` (y los momentos de animación de cada escena si cambian las frases). Conserva la última línea del guion para el cierre de Sumiago.
