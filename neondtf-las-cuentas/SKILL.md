---
name: neondtf-las-cuentas
description: Crea el video de socio "NeonDTF: las cuentas no mienten" (9:16, calculadora, contadores y gráficas de horas ahorradas, voz de Fish Audio y cierre de Sumiago). Úsala cuando pidan hacer, rehacer o adaptar este video, o un video de "haz tus cuentas" para el negocio de otro socio.
---

# Video de socio "NeonDTF: las cuentas no mienten"

Video vertical 9:16 (1080x1920, 30 fps, unos 58 s) para Neon Estudio DTF (neondtf.store). Convence con números simples: si cada diseño toma 1 hora y llegan 5 pedidos al día, son 30 horas a la semana diseñando; con NeonDTF son menos de 3 minutos por diseño (1,5 horas a la semana) y sobran más de 28 horas para imprimir, vender y atender más clientes. Cierra con la publicidad de Sumiago.

Copyright © Sumiago. Uso solo con autorización (ver LICENSE del repositorio).

## Qué necesitas

- Python 3.10+ y FFmpeg en el PATH.
- Paquetes: `pip install pillow numpy`
- Las fuentes vienen en `fonts/` (Inter Display Black, Poppins Bold y Medium, licencia OFL).
- El logo de Sumiago con fondo blanco viene en `assets/logo-sumiago-fondo-blanco.png`.
- Tu clave de Fish Audio en la variable `FISH_API_KEY`. **Nunca la escribas en los archivos ni la subas a GitHub.**

## Pasos

Trabaja en una carpeta vacía (por ejemplo `trabajo/`) y ejecuta los scripts desde ahí.

1. **Voz.** Lee `guion.txt` (10 líneas: 9 del video y la última del cierre de Sumiago):
   ```
   set FISH_API_KEY=tu_clave
   python ruta/neondtf-las-cuentas/scripts/voz.py
   ```
   Usa la voz `8730dce743254904a745d6e134e18c6b` con el modelo gratis `s2.1-pro-free` (con el que se hizo el video). Si tienes crédito de API puedes usar `set FISH_MODEL=s1`. Si una línea falla con 402, espera unos segundos y vuelve a correrlo. Deja `vo/00.wav` a `vo/09.wav`.

2. **Revisión rápida** antes del render completo:
   ```
   python ruta/neondtf-las-cuentas/scripts/escenas.py preview 0@2.0 1@6.3 2@3.5 3@5.0 4@2.5 5@5.5 6@5.0 7@7.0 8@6.0
   ```
   Abre `prueba.jpg` y revisa que ningún texto se salga de la pantalla.

3. **Armar el video.**
   ```
   python ruta/neondtf-las-cuentas/scripts/armar.py
   ```
   Sale `out/neondtf-las-cuentas.mp4`. Si una frase dura más que su escena, avisa en pantalla.

4. **Escúchalo completo** antes de publicarlo.

## Escenas (línea del guion → lo que se ve)

| # | Dur. | Frase | En pantalla |
|---|------|-------|-------------|
| 1 | 4,1 s | Hagamos cuentas rápidas… | "LAS CUENTAS DE TU TALLER" y calculadora neón que teclea sola y termina en "= ?" |
| 2 | 6,8 s | Si cada diseño te toma una hora… | "A LA ANTIGUA": 1 DISEÑO = reloj y "1 HORA" × 5 camisetas que aparecen, "5 PEDIDOS AL DÍA" |
| 3 | 4,3 s | Son treinta horas a la semana… | Contador hasta 30, barras rojas de lunes a sábado (5 h c/u) y sello "SOLO DISEÑANDO" |
| 4 | 5,7 s | Con Neon DTF… menos de tres minutos | El logo malo se arregla en 3 barridos, cronómetro y "LISTO EN < 3 MIN" |
| 5 | 3,5 s | Menos de dos horas a la semana | "5 × 6 × 3 min = 90 min", "1,5 HORAS" y barras ANTES 30 H / AHORA 1,5 H |
| 6 | 6,5 s | Te sobran más de 28 horas… | Contador "+28 HORAS LIBRES" y píldoras IMPRIMIR MÁS, VENDER MÁS, ATENDER MÁS CLIENTES |
| 7 | 5,6 s | Más pedidos, entregas, clientes | Tres frases con flecha hacia arriba y gráfica verde que sube |
| 8 | 8,0 s | Dieciséis herramientas… | Contador 16, nombres de herramientas con ✓ y "MUCHAS SON GRATIS" |
| 9 | 7,0 s | Haz tus cuentas y entra hoy… | Logo, "HAZ TUS CUENTAS", botón "ENTRA HOY", web y "Link en el perfil" |
| 10 | 7,0 s | ¿Quieres videos como este…? | Cierre Sumiago con logo animado y botón "sumiago.com" |

## Estilo y reglas

- Reutiliza el estilo neón de `base.py` y `base2.py` (mismas funciones que los videos "neondtf-herramientas" y "neondtf-mejor-tenerlo").
- Las cuentas son un ejemplo ("si cada diseño te toma una hora…"): si cambias un número, cambia también los demás para que la suma cuadre (pedidos × días × minutos).
- Música: tensa con pitidos de calculadora al principio, entra el ritmo completo en "Con Neon DTF".
- Para otro socio: cambia `guion.txt`, los textos y números de `escenas.py` y los tiempos de `SCENES`. Conserva la última línea del guion para el cierre de Sumiago.
