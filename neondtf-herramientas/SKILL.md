---
name: neondtf-herramientas
description: Crea el video de socio "NeonDTF: 16 herramientas DTF" (9:16, estilo neón, voz de Fish Audio, demostraciones antes/después y cierre de Sumiago). Úsala cuando pidan hacer, rehacer o adaptar este video, o un video parecido para el negocio de otro socio.
---

# Video de socio "NeonDTF: 16 herramientas DTF"

Video vertical 9:16 (1080x1920, 30 fps, unos 60 s) para Neon Estudio DTF (neondtf.store), un negocio de herramientas online para estampado DTF. Vende sin parecer anuncio: muestra el problema (horas en Photoshop, Illustrator y Corel), la solución con demostraciones de antes y después, y cierra con la publicidad de Sumiago.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy`
- Las fuentes vienen en `fonts/` (Inter Display Black, Poppins Bold y Medium, licencia OFL).
- El logo de Sumiago con fondo blanco viene en `assets/logo-sumiago-fondo-blanco.png`.
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Pasos

Trabaja en una carpeta vacía (por ejemplo `trabajo/`) y ejecuta los scripts desde ahí.

1. **Voz.** Lee `guion.txt` (12 líneas: 11 del video y la última del cierre de Sumiago):
   ```
   set FISH_API_KEY=tu_clave
   python ruta/neondtf-herramientas/scripts/voz.py
   ```
   Usa la voz `8730dce743254904a745d6e134e18c6b` con el modelo `s1`. Si Fish responde 402 (sin crédito de API), usa el modelo gratis: `set FISH_MODEL=s2.1-pro-free`. Deja `vo/00.wav` a `vo/11.wav`.

2. **Revisión rápida** antes del render completo:
   ```
   python ruta/neondtf-herramientas/scripts/escenas.py preview 0@2.6 3@2.2 8@4.0 10@3.2
   ```
   Abre los `prev_*.jpg` y revisa que ningún texto se salga de la pantalla.

3. **Armar el video.**
   ```
   python ruta/neondtf-herramientas/scripts/armar.py
   ```
   Renderiza las escenas, la música, el cierre de Sumiago y mezcla la voz (la música baja sola cuando habla). Sale `out/neondtf-herramientas.mp4`. Si una frase dura más que su escena, avisa en pantalla.

4. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

| # | Dur. | Frase | En pantalla |
|---|------|-------|-------------|
| 1 | 4,5 s | ¿Sigues perdiendo horas…? | "¿SIGUES PERDIENDO HORAS en diseño?", reloj girando y contador rojo |
| 2 | 5,6 s | Photoshop, Illustrator, Corel… | Tres píldoras que caen y se tachan en rojo; "Caros. Lentos. COMPLICADOS." |
| 3 | 3,8 s | Hay una forma más fácil | "MÁS FÁCIL" y logo NEON DTF con parpadeo de neón |
| 4–8 | 4,5 s c/u | Quitar fondo, vectorizar, semitonos, mejorar, halo blanco | Tarjeta antes/después con barra que revela el resultado, cursor que pulsa "1 CLIC" y "✓ LISTO" |
| 9 | 6,0 s | Dieciséis herramientas… | Contador 0→16, cuadrícula de 16 que se enciende y tres píldoras |
| 10 | 4,5 s | Tú enfócate en vender… | "VENDER" verde y "EL DISEÑO" cian |
| 11 | 6,5 s | Pruébalas gratis… | Logo, botón "PRUÉBALAS GRATIS", web y "Link en el perfil" |
| 12 | 7,0 s | ¿Quieres videos como este…? | Cierre Sumiago: círculo que abre fondo blanco, logo que salta y se revela con destello, corazones flotando y botón "sumiago.com" |

## Estilo y reglas

- Fondo oscuro `#0B0C0E` con cuadrícula que se desliza; colores neón: cian `#00F0FF`, magenta `#FF2BD6`, verde `#B6FF3B`, rojo `#FF3B50`.
- El diseño de muestra "WILD" es original (sol retro con montañas); no uses logos ni personajes de otras marcas.
- Los nombres de programas van solo como texto, sin sus logos.
- Para otro socio: cambia `guion.txt`, los textos de `escenas.py` (busca `NEON`, `neondtf.store`) y los tiempos de `SCENES` si cambian las frases. Conserva la última línea del guion para el cierre de Sumiago.
- Para hacerlo de 60 s o menos, acorta escenas en `SCENES` (no el cierre).
