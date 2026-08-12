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

## Resultados de Validación Automatizada

Además del análisis manual del PDF, se ejecutó el script
`scripts/validate_ddu456.py`, que instancia el orquestador existente
(`scripts/ddu_orchestrator.py`, `DDUOrchestrator().process_pdf(Path)`) sobre
`circulares/DDU 456.pdf`, genera un CSV con la extracción y calcula qué campos
quedaron vacíos. La ejecución finalizó con éxito (exit code 0) y su salida
completa está en `validation_output.txt`.

### CSV Generado
- **Archivo:** `salidas_csv/ddu456_validation.csv`
- **Registros:** 1 (una circular = un registro; DDU 456)
- **Campos por registro:** 18
- **Codificación:** `utf-8-sig` (acentos correctos)

Los 18 campos extraídos son: `numero`, `fecha`, `materia`, `emisor`,
`antecedentes`, `secciones`, `referencias`, `elementos_visuales`, `numero_ord`,
`descriptores`, `cuerpo`, `fecha_lugar`, `lugar`, `destinatarios`, `firmante`,
`lista_distribucion`, `distribucion_texto`, `notas_al_pie`.

### Campos Vacíos Detectados

De los 18 campos, la extracción automática dejó **5 campos vacíos** (100 % vacíos
sobre 1 registro):

| Campo vacío | Vacíos / Total | % Vacío |
|-------------|----------------|---------|
| `antecedentes` | 1/1 | 100.0 % |
| `referencias` | 1/1 | 100.0 % |
| `elementos_visuales` | 1/1 | 100.0 % |
| `descriptores` | 1/1 | 100.0 % |
| `notas_al_pie` | 1/1 | 100.0 % |

Los **13 campos restantes sí contienen datos**: `numero` (DDU 456), `fecha`
(2021-02-25), `materia`, `emisor`, `secciones`, `numero_ord`, `cuerpo`,
`fecha_lugar`, `lugar`, `destinatarios`, `firmante`, `lista_distribucion` y
`distribucion_texto`.

### Errores Durante Extracción

No se detectaron errores ni excepciones durante la extracción. El script reportó
`[OK]` en todas las etapas (instanciación del orquestador, carga del PDF,
extracción de 1 registro con 18 campos y generación del CSV).

## Análisis por Bloque

> **Nota metodológica:** la columna "Campos Vacíos" cruza el estado observado en
> el análisis manual del PDF con el resultado real de la extracción automática
> (`ddu456_validation.csv`). Cuando ambos coinciden, el bloque se considera
> confirmado; cuando difieren (p. ej. **Descriptores**, visible en el PDF pero
> vacío en el CSV), la discrepancia se documenta como brecha del extractor.

| Bloque | Estado | Estructura Observada | Campos Vacíos (extracción) | Ajustes Necesarios |
|--------|--------|----------------------|----------------------------|--------------------|
| Encabezado | ✓ OK | "DDU 456" en la parte superior de la página 1. | Ninguno (`numero` poblado) | Ninguno |
| Acto Administrativo | ✓ OK | "CIRCULAR ORD. Nº 88 /" en página 1. | Ninguno (`numero_ord` poblado) | Ninguno |
| Antecedentes | ✗ VACÍO | No hay sección rotulada; referencias normativas embebidas en el cuerpo. | `antecedentes` y `referencias` vacíos (100 %) | Requiere `etl_referencias.py` para poblar desde el cuerpo. |
| Materia | ✓ OK | Campo "MAT.:" con descripción extensa. | Ninguno (`materia` poblado) | Ninguno |
| Descriptores | ⚠️ DISCREPANCIA | Lista en mayúsculas visible tras la materia en el PDF, pero el extractor la dejó vacía. | `descriptores` vacío (100 %) | Ajustar extractor para separar vocablos por ";" y ",". |
| Fecha y Lugar | ✓ OK | "SANTIAGO, 25 FEB 2021". | Ninguno (`fecha`, `fecha_lugar`, `lugar` poblados) | Fecha ya normalizada (2021-02-25). |
| Destinatarios | ✓ OK | "A : SEGÚN DISTRIBUCIÓN." | Ninguno (`destinatarios` poblado) | Ninguno |
| Emisión | ✓ OK | "DE : JEFE DIVISIÓN DE DESARROLLO URBANO." | Ninguno (`emisor` poblado) | Ninguno |
| Cuerpo | ✓ OK | Numerales 1 al 7 con incisos, literales, esquema y tabla. | Ninguno (`cuerpo`, `secciones` poblados); `elementos_visuales` vacío | El texto se extrae, pero el esquema ilustrativo no (ver `elementos_visuales`). |
| Elementos Visuales | ✗ VACÍO | Esquema ilustrativo (pág. 3, "PLANTA AZOTEA" / "CORTE ESQUEMÁTICO"). | `elementos_visuales` vacío (100 %) | Requiere `etl_esquemas_ilustrativos.py`. |
| Nota al Pie | ✗ VACÍO | Notas al margen (columna lateral) con modificaciones por DDU 498. | `notas_al_pie` vacío (100 %) | Requiere `etl_notas_marginales.py`. |
| Firma | ✓ OK | "Saluda atentamente..." + iniciales "JPB" (pág. 8). | Ninguno (`firmante` poblado) | Ninguno |
| Distribución | ✓ OK | Lista numerada de 34 destinatarios (págs. 8–9). | Ninguno (`lista_distribucion`, `distribucion_texto` poblados) | Ninguno |

### Tabla original del análisis manual (referencia)

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

Los ETLs siguientes se derivan del cruce entre el análisis manual y los **5
campos vacíos** confirmados por la extracción automática. Cada uno apunta a un
campo específico de `DatosCircularDDU` que quedó sin datos en
`ddu456_validation.csv`.

### Identificados

1. **`etl_referencias.py`** (bloque Antecedentes)
   - **Campos objetivo:** `antecedentes`, `referencias` (ambos 100 % vacíos).
   - **Razón:** DDU 456 no rotula los antecedentes como sección independiente;
     las referencias normativas (LGUC art. 4º, OGUC art. 2.6.3., Decreto Supremo
     Nº 58 de 2019, Circulares DDU 322, 339 y 168) están embebidas en el cuerpo.
   - **Enfoque:** detección por patrones ("art. N.N.N.", "DDU NNN",
     "Decreto Nº NN", "Ley NN.NNN") sobre el texto del `cuerpo`.
   - **Prioridad:** Alta (dos campos vacíos dependen de él).

2. **`etl_esquemas_ilustrativos.py`** (bloque Cuerpo → Elementos Visuales)
   - **Campo objetivo:** `elementos_visuales` (100 % vacío).
   - **Razón:** DDU 456 contiene un esquema ilustrativo en la **página 3**
     ("PLANTA AZOTEA / Sin Escala" y "CORTE ESQUEMÁTICO / Sin Escala") cuyo texto
     queda disperso al extraer con lectores de PDF de texto plano.
   - **Enfoque:** extracción por coordenadas/regiones (p. ej. pdfplumber) o
     captura del gráfico como recurso asociado.
   - **Prioridad:** Media.

3. **`etl_notas_marginales.py`** (bloque Nota al Pie)
   - **Campo objetivo:** `notas_al_pie` (100 % vacío).
   - **Razón:** las notas de trazabilidad no son pies de página clásicos, sino
     **notas al margen** (columna lateral) que indican modificaciones por la
     Circular Ord. Nº 214 / DDU 498 (02.05.2024).
   - **Enfoque:** capturar la columna lateral por coordenadas y asociarla al
     numeral del cuerpo correspondiente.
   - **Prioridad:** Media.

4. **`etl_tabla_modificaciones.py`** (bloque Cuerpo, estructura especial)
   - **Campo objetivo:** enriquecer `cuerpo`/`secciones` (el texto se extrae,
     pero la tabla queda fragmentada).
   - **Razón:** la tabla de tres columnas ("Circular / Materia(s) que se
     modifica(n) / Motivo y/o Consideraciones") se extiende por las
     **páginas 5 a 8** y la extracción de texto plano intercala las columnas.
   - **Enfoque:** extracción tabular por coordenadas respetando el salto de
     página.
   - **Prioridad:** Baja (no genera campo vacío, pero degrada la calidad).

5. **Ajuste del extractor de Descriptores** (no es ETL nuevo, es corrección)
   - **Campo objetivo:** `descriptores` (100 % vacío pese a estar presente en el PDF).
   - **Razón:** los descriptores están visibles en el PDF ("NORMAS
     URBANISTICAS; ALTURA MÁXIMA DE EDIFICACIÓN, ...") pero el extractor actual
     no los captura → **discrepancia manual vs automático**.
   - **Enfoque:** revisar el patrón de detección tras el campo "MAT.:" y separar
     vocablos por ";" y ",".
   - **Prioridad:** Alta (campo presente que debería poblarse sin ETL nuevo).

### No identificados

N/A — todos los campos vacíos tienen una causa identificada y un ETL o ajuste
propuesto.

## Conclusiones

**Resumen de Cobertura (por bloque, sobre los 12 bloques esperados):**
- ✓ Bloques completamente funcionales: **7/12** (Encabezado, Acto Administrativo,
  Materia, Fecha y Lugar, Destinatarios, Emisión, Firma, Distribución — el Cuerpo
  se extrae en texto pero con estructuras especiales pendientes).
- ⚠️ Bloques con cobertura parcial o con discrepancia: **1/12** (Descriptores:
  presente en el PDF pero vacío en la extracción).
- ✗ Bloques no cubiertos por la extracción actual: **3/12** (Antecedentes,
  Elementos Visuales, Nota al Pie).
- No hay bloques no aplicables (0/12).

**Campos Vacíos (a nivel de `DatosCircularDDU`):**
- Total de campos: **18**.
- Campos con datos: **13**.
- Campos vacíos: **5** (`antecedentes`, `referencias`, `elementos_visuales`,
  `descriptores`, `notas_al_pie`).
- **Tasa de cobertura de campos: 72,2 %** (13/18).

**Cruce análisis manual vs automático:**
- Coinciden en que Antecedentes, Elementos Visuales y Nota al Pie no se
  capturan (estructuras no estándar: referencias embebidas, esquema gráfico y
  notas al margen).
- **Difieren en Descriptores:** el análisis manual lo marcó como presente, pero
  la extracción automática lo dejó vacío. Es la brecha más accionable porque el
  dato existe en el PDF y solo requiere ajustar el extractor.

**Hallazgos Principales:**
1. La extracción base es sólida (72,2 % de cobertura, 0 errores) y los bloques
   administrativos estándar se capturan correctamente.
2. Los 5 campos vacíos se deben a **estructuras no estándar** de esta circular
   (referencias embebidas, esquema ilustrativo, notas al margen, tabla
   multipágina) y a **una brecha del extractor de descriptores**.

**Recomendación para próxima fase:**
- **Ahora / prioridad alta:** corregir el extractor de `descriptores` (dato
  presente, esfuerzo bajo) y crear `etl_referencias.py` (poblaría 2 campos).
- **Diferir a la rama DDU 547:** los extractores que requieren extracción por
  coordenadas (`etl_esquemas_ilustrativos.py`, `etl_notas_marginales.py`,
  `etl_tabla_modificaciones.py`), ya que implican una dependencia nueva
  (pdfplumber) y benefician a varias circulares, no solo a DDU 456.
