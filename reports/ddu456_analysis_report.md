# DDU 456 - Análisis de Extracción

**Circular:** Orden Nº 88 (25 FEB 2021) - Elementos Exteriores en Edificios
**Páginas:** 9
**Análisis Realizado:** 12 de agosto de 2026

## Hallazgos Generales

La circular DDU 456 corresponde a la Circular Ord. Nº 88 del Jefe de División de
Desarrollo Urbano (MINVU), emitida el 25 de febrero de 2021, sobre terrazas y
elementos exteriores ubicados en la parte superior de los edificios y pisos
mecánicos (aplicación del artículo 2.6.3. incisos vigésimo al vigésimo tercero
de la OGUC).

Del análisis manual del PDF (9 páginas) se concluye:

- **Los 12 bloques esperados están presentes**, con la salvedad de que los
  **Antecedentes** no aparecen como una sección rotulada independiente, sino
  embebidos dentro del cuerpo (referencias a LGUC, OGUC, Decreto Supremo Nº 58
  y a las Circulares DDU 322, DDU 339 y DDU 168), por lo que se marcan como
  **⚠️ Parcial**.
- **La Nota al Pie** no se presenta como pie de página tradicional, sino como
  **notas al margen** (columna lateral) que indican modificaciones posteriores
  introducidas por la Circular Ord. Nº 214 / DDU 498 (02.05.2024). Se marca como
  **⚠️ Parcial** por su ubicación y formato no estándar.
- Se detectaron **dos estructuras inusuales** relevantes para la extracción: un
  **esquema ilustrativo** (planta de azotea y corte esquemático, "Sin Escala")
  y una **tabla de modificaciones a otras circulares** que se extiende por
  varias páginas (páginas 5 a 8) con columnas "Circular / Materia(s) que se
  modifica(n) / Motivo y/o Consideraciones".

## Análisis por Bloque

| Bloque | Estado | Estructura Observada | Ajustes Necesarios |
|--------|--------|----------------------|-------------------|
| Encabezado | ✓ Presente | "DDU 456" en la parte superior de la página 1. | Ninguno |
| Acto Administrativo | ✓ Presente | "CIRCULAR ORD. Nº 88 /" en página 1. | Ninguno |
| Antecedentes | ⚠️ Parcial | No hay sección rotulada; referencias normativas embebidas en el cuerpo (LGUC art. 4º, OGUC art. 2.6.3., Decreto Supremo Nº 58 de 2019, Circulares DDU 322, 339 y 168). | Extraer referencias desde el cuerpo mediante detección de patrones (art. N.N.N., DDU NNN, Decreto Nº NN). |
| Materia | ✓ Presente | Campo "MAT.:" con descripción extensa (aplicación art. 2.6.3. incisos vigésimo a vigésimo tercero de la OGUC, terrazas, elementos exteriores, pisos mecánicos). | Ninguno |
| Descriptores | ✓ Presente | Lista en mayúsculas tras la materia: "NORMAS URBANISTICAS; ALTURA MÁXIMA DE EDIFICACIÓN, ELEMENTOS EXTERIORES UBICADOS EN LA PARTE SUPERIOR DE LOS EDIFICIOS, PISOS MECÁNICOS." | Separar vocablos por ";" y ",". |
| Fecha y Lugar | ✓ Presente | "SANTIAGO, 25 FEB 2021" en página 1. | Normalizar fecha (25/02/2021). |
| Destinatarios | ✓ Presente | "A : SEGÚN DISTRIBUCIÓN." (remite a la lista de distribución final). | Ninguno |
| Emisión | ✓ Presente | "DE : JEFE DIVISIÓN DE DESARROLLO URBANO." | Ninguno |
| Cuerpo | ✓ Presente | Numerales 1 al 7. Incluye transcripción de incisos (vigésimo al vigésimo tercero), análisis con literales a)–e) y numerales romanos i)–ii), un esquema ilustrativo (pág. 3) y una tabla de modificaciones a otras circulares (págs. 5–8). Es el bloque más extenso. | Manejar estructuras anidadas (incisos citados, literales y tabla). |
| Nota al Pie | ⚠️ Parcial | No hay pies de página normativos; existen **notas al margen** (columna lateral) que indican modificaciones posteriores por Circular Ord. Nº 214 / DDU 498 (numeral 7, y aclaración sobre DDU 339). | Requiere ETL específico para capturar notas marginales de trazabilidad. |
| Firma | ✓ Presente | "Saluda atentamente a Ud., ... Jefe División de Desarrollo Urbano" (pág. 8), con rúbrica/iniciales "JPB". | Ninguno |
| Distribución | ✓ Presente | Lista numerada de 34 destinatarios (págs. 8–9), desde "1. Sr. Ministro de Vivienda y Urbanismo" hasta "34. Oficina de Partes MINVU Ley 20.285". | Parsear lista numerada (continúa entre páginas 8 y 9). |

## Estructuras Nuevas Detectadas

1. **Tabla de modificaciones a otras circulares (págs. 5–8).** Tabla de tres
   columnas — "Circular" / "Materia(s) que se modifica(n)" / "Motivo y/o
   Consideraciones" — que se extiende por varias páginas y contiene texto
   normativo citado (reemplazos de numerales/letras). La extracción de texto
   plano intercala las columnas y fragmenta las celdas, lo que dificulta su
   procesamiento tabular.

2. **Esquema ilustrativo (pág. 3).** Diagrama con "PLANTA AZOTEA / Sin Escala" y
   "CORTE ESQUEMÁTICO / Sin Escala", con etiquetas (piscina, terrazas,
   chimeneas, pérgolas, barandas, paramentos perimetrales, salas de máquinas,
   etc.). Es contenido gráfico cuyo texto queda disperso al extraer con lectores
   de PDF de texto.

3. **Notas al margen de trazabilidad.** Columna lateral con referencias a la
   Circular Ord. Nº 214 / DDU 498 (02.05.2024) que modifican/aclaran esta
   circular. No corresponden a pies de página clásicos y aparecen intercaladas
   con el cuerpo al extraer texto.

## Nuevos ETLs Sugeridos

1. **ETL de tabla de modificaciones (`etl_tabla_modificaciones`).** Extractor
   especializado en la tabla de tres columnas (págs. 5–8) que reconstruya las
   filas "Circular / Materia modificada / Motivo" respetando el salto de página,
   idealmente usando extracción por coordenadas/tablas (p. ej. pdfplumber) en
   lugar de texto plano.

2. **ETL de notas marginales (`etl_notas_marginales`).** Extractor que capture
   las notas al margen de trazabilidad (circulares modificatorias posteriores)
   y las asocie al numeral del cuerpo al que hacen referencia, para alimentar el
   bloque "Nota al Pie".

3. **ETL de referencias normativas (`etl_referencias`).** Detección por patrones
   dentro del cuerpo (artículos "N.N.N.", "DDU NNN", "Decreto Nº NN", "Ley
   NN.NNN") para poblar el bloque "Antecedentes", que en esta circular no está
   rotulado de forma independiente.
