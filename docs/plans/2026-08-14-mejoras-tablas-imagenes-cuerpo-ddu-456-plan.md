# Plan de Implementación: Nuevos ETLs de Tablas e Imágenes y Limpieza de Materia y Cuerpo

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar dos nuevos extractores independientes (`TablasExtractor` e `ImagenesExtractor`), sanear tipografía fragmentada por OCR en materia/cuerpo y descontaminar el texto del cuerpo en DDU 456.

**Architecture:** Paquete de ETLs modulares en `scripts/extractors/` coordinados por `DDUOrchestrator`. Los nuevos bloques `tablas` e `imagenes` estructuran información tabular y técnica aislada del texto narrativo de `cuerpo`.

**Tech Stack:** Python 3.13, `pdfplumber`, `fitz` (PyMuPDF), `pypdf`, `pytest`.

---

### Task 1: Saneamiento Tipográfico OCR Universal (`utils_cleaner.py`)

**Files:**
- Create: `scripts/extractors/utils_cleaner.py`
- Create: `test/test_utils_cleaner.py`
- Modify: `scripts/extractors/materia.py`

**Step 1: Escribir la prueba unitaria que falla**
Crear `test/test_utils_cleaner.py` probando la reparación de palabras fragmentadas por OCR:
```python
def test_limpiar_palabras_ocr() -> None:
    from scripts.extractors.utils_cleaner import limpiar_palabras_ocr
    raw = "Aplicación a rtículo 2.6.3. inciso s vigésimo, relativo s a terrazas y quinch os."
    esperado = "Aplicación artículo 2.6.3. incisos vigésimo, relativos a terrazas y quinchos."
    assert limpiar_palabras_ocr(raw) == esperado
```

**Step 2: Ejecutar test para verificar que falla**
`pytest test/test_utils_cleaner.py -v`

**Step 3: Implementar `scripts/extractors/utils_cleaner.py` e integrar en `materia.py`**
Definir `limpiar_palabras_ocr` con reemplazos regex de patrones de separación OCR.

**Step 4: Ejecutar test para verificar que pasa**
`pytest test/test_utils_cleaner.py test/test_extractor_metadata.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/utils_cleaner.py scripts/extractors/materia.py test/test_utils_cleaner.py test/test_extractor_metadata.py`
`git commit -m "feat: implementar módulo de limpieza tipográfica OCR e integrar en extractor de materia"`

---

### Task 2: Nuevo ETL Modular `TablasExtractor` (`tablas.py`)

**Files:**
- Create: `scripts/extractors/tablas.py`
- Create: `test/test_extractor_tablas.py`
- Modify: `scripts/extractors/__init__.py`

**Step 1: Escribir la prueba unitaria**
Crear `test/test_extractor_tablas.py` probando la extracción de tablas en `circulares/DDU 456.pdf` con `pdfplumber`.

**Step 2: Ejecutar test para verificar fallo**
`pytest test/test_extractor_tablas.py -v`

**Step 3: Implementar `scripts/extractors/tablas.py`**
Clase `TablasExtractor(BaseExtractor)` decorada con `@register_extractor`, `nombre_bloque = "tablas"`, extracción con `pdfplumber`, formateo a JSON / Markdown tabular y CLI con `--pdf`.

**Step 4: Ejecutar test para verificar que pasa**
`pytest test/test_extractor_tablas.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/tablas.py scripts/extractors/__init__.py test/test_extractor_tablas.py`
`git commit -m "feat: implementar extractor independiente de tablas con pdfplumber"`

---

### Task 3: Nuevo ETL Modular `ImagenesExtractor` (`imagenes.py`)

**Files:**
- Create: `scripts/extractors/imagenes.py`
- Create: `test/test_extractor_imagenes.py`
- Modify: `scripts/extractors/__init__.py`

**Step 1: Escribir la prueba unitaria**
Crear `test/test_extractor_imagenes.py` verificando el inventario de imágenes y diagramas técnicos en `circulares/DDU 456.pdf` (esquema de planta azotea y corte).

**Step 2: Ejecutar test para verificar fallo**
`pytest test/test_extractor_imagenes.py -v`

**Step 3: Implementar `scripts/extractors/imagenes.py`**
Clase `ImagenesExtractor(BaseExtractor)` decorada con `@register_extractor`, `nombre_bloque = "imagenes"`, extracción con `fitz`, filtrado de logos/membretes, descripción técnica y CLI con `--pdf`.

**Step 4: Ejecutar test para verificar que pasa**
`pytest test/test_extractor_imagenes.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/imagenes.py scripts/extractors/__init__.py test/test_extractor_imagenes.py`
`git commit -m "feat: implementar extractor independiente de imágenes y esquemas técnicos con PyMuPDF"`

---

### Task 4: Descontaminación de `CuerpoExtractor` y Refinamiento de `FirmaExtractor`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`
- Modify: `scripts/extractors/firma.py`
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir pruebas unitarias**
Agregar pruebas en `test/test_extractor_body.py` para certificar que el cuerpo de DDU 456 no contenga texto residual de diagramas ni volcados desordenados de tablas, y que la firma capture limpiamente el cargo y emisor.

**Step 2: Ejecutar test para verificar fallo o comportamiento previo**
`pytest test/test_extractor_body.py -v`

**Step 3: Modificar `cuerpo.py` y `firma.py`**
Aplicar `limpiar_palabras_ocr` y filtrado de etiquetas gráficas en `cuerpo.py` y depuración en `firma.py`.

**Step 4: Ejecutar test para verificar éxito**
`pytest test/test_extractor_body.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/cuerpo.py scripts/extractors/firma.py test/test_extractor_body.py`
`git commit -m "feat: descontaminar cuerpo de etiquetas de diagramas y ajustar captura de firma"`

---

### Task 5: Actualización del Orquestador, Regeneración de Salidas y Verificación Total

**Files:**
- Modify: `salidas_csv/DDU_456_extraido.csv`
- Modify: `salidas_xml/DDU_456_akoma.xml`
- Modify: `salidas_rdf/DDU_456_rdf.ttl`
- Modify: `CHANGELOG.md`
- Modify: `docs/plans/task.md`

**Step 1: Ejecutar exportación de CSV de DDU 456 con los 14 bloques**
`py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 456.pdf" --export-csv`

**Step 2: Regenerar Akoma XML y RDF**
`py -3 scripts/csv_to_akoma_xml.py --csv "salidas_csv/DDU_456_extraido.csv" --output "salidas_xml/DDU_456_akoma.xml"`
`py -3 scripts/csv_to_rdf.py --csv "salidas_csv/DDU_456_extraido.csv" --output "salidas_rdf/DDU_456_rdf.ttl"`

**Step 3: Ejecutar la suite completa de pruebas**
`pytest -v` (confirmar 100% pasando).

**Step 4: Actualizar documentación (`CHANGELOG.md`, `task.md`) y commit final**
`git add .`
`git commit -m "feat: completar integración de tablas, imágenes y saneamiento tipográfico en DDU 456"`
`git push origin feature/ddu-456`
