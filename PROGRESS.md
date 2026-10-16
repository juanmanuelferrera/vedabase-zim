# PROGRESS — Rehacer vedabase_en_all desde la fuente (16-oct-2026)

Motivo: revisión de Kiwix (openzim/zim-requests#1703, Popolechien): títulos
cortados («1. Observing the Armies on the») e índice sin enlaces en
Light of the Bhagavata. El ZIM 2026-10 anterior era una copia del vedabase.zim
de marzo (generador perdido): 62 títulos cortados a 80 caracteres, 3 libros en
una sola página con índice en texto, conversaciones tituladas con su primera
frase. El usuario decidió rehacerlo ahora.

## Hecho (con la verificación)
- Export D1 de vedabase.cc (solo lectura) → `build/d1md/` (24 ficheros).
- `build_zim_d1.py` nuevo → `build/vedabase_en_all_2026-10.zim`
  (61,8 MB, sha256 54b03640cc06a69bd2eb75c8b2c52aa87093f58c57193f0af44d8db5ff5687b9).
  - 30.959 páginas de contenido = 30.959 filas D1 (dos recuentos).
  - 31.332 páginas HTML en total (con índices); 0 enlaces internos rotos;
    0 títulos de entrada repetidos.
  - Índice de títulos y de texto completo presentes; búsqueda «Kurukṣetra
    armies» → bg/1 primero; sugerencia «Observing the» → bg/1.
  - Comprobado a ojo (capturas headless Chrome): Bg. 1.1, índice de BG 1,
    SB 1.8.36 (conferencia 28-4-1973).
  - Títulos: «Chapter 1: Observing the Armies on the Battlefield of Kurukṣetra»,
    «SB 2.7: Scheduled Incarnations with Specific Functions»,
    conferencias «<título> — <lugar>, <fecha>», cartas «Letter to X — lugar, fecha».
  - LoB, Reservoir y el resto: índice enlazado, una página por capítulo.

## NO probado
- No abierto en Kiwix (no hay kiwix-serve ni zimcheck instalados).

## Siguiente paso exacto
El usuario: abrir `build/vedabase_en_all_2026-10.zim` en Kiwix Desktop y dar GO
para subirlo a R2 (misma URL que usa landing/index.html) y responder en
zim-requests#1703.

## Pendiente del usuario
- Libros que el ZIM viejo tenía y D1 no: Teachings of Lord Kapila,
  Teachings of Prahlāda Mahārāja, Second Chance. Quedan fuera.
- Subida a R2 y respuesta en GitHub: con GO.
