# Plan de Implementación: Arquitectura Desacoplada de Tablas e Imágenes (Opción A)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar el desacople físico de tablas e imágenes en carpetas dedicadas (`salidas_tablas/` y `salidas_imagenes/`) y generar manifiestos ligeros con IDs canónicos en el CSV principal de las circulares DDU.

**Architecture:** Módulos `TablasExtractor` e `ImagenesExtractor` exportan artefactos individuales y emiten manifiestos ligeros en `ResultadoBloque.datos`. `DDUOrchestrator` consolida y escribe los manifiestos en el CSV individual.

**Tech Stack:** Python 3.13, `pdfplumber`, `fitz` (PyMuPDF), `pytest`.

---

### Task 1: Implementación Base de los 14 Bloques ETL y Saneamiento OCR DDU 456
*(Completado previamente en `feature/ddu-456`)*

---

### Task 2: Refactorizar `TablasExtractor` (`tablas.py`) para Manifiesto y Exportación Anexa

**Files:**
- Modify: `scripts/extractors/tablas.py`
- Modify: `test/test_extractor_tablas.py`

**Step 1: Escribir la prueba unitaria que verifica manifiesto y CSVs anexos**
En `test/test_extractor_tablas.py`, verificar que para DDU 456 se creen los archivos en `salidas_tablas/` y que cada ítem del manifiesto contenga `id`, `nombre`, `pagina`, `filas`, `columnas` y `archivo_anexo`.

**Step 2: Ejecutar test para verificar fallo o comportamiento actual**
`pytest test/test_extractor_tablas.py -v`

**Step 3: Refactorizar `scripts/extractors/tablas.py`**
- Deducción de número DDU (`DDU_{num}`).
- Generación de IDs canónicos `DDU_{num}_tabla_{idx}`.
- Exportación automática a `salidas_tablas/DDU_{num}_tabla_{idx}.csv`.
- Generación del manifiesto ligero en `ResultadoBloque.datos["tablas"]`.

**Step 4: Ejecutar test para verificar éxito**
`pytest test/test_extractor_tablas.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/tablas.py test/test_extractor_tablas.py`
`git commit -m "feat: refactorizar TablasExtractor con manifiesto ligero y exportación a salidas_tablas"`

---

### Task 3: Refactorizar `ImagenesExtractor` (`imagenes.py`) para Manifiesto y Exportación Anexa

**Files:**
- Modify: `scripts/extractors/imagenes.py`
- Modify: `test/test_extractor_imagenes.py`

**Step 1: Escribir la prueba unitaria que verifica manifiesto y guardado físico de imágenes**
En `test/test_extractor_imagenes.py`, verificar que para DDU 456 se guarde el archivo en `salidas_imagenes/` y que el manifiesto contenga `id`, `nombre`, `pagina`, `ancho`, `alto`, `formato` y `archivo_anexo`.

**Step 2: Ejecutar test para verificar fallo**
`pytest test/test_extractor_imagenes.py -v`

**Step 3: Refactorizar `scripts/extractors/imagenes.py`**
- Guardar imagen binaria extraída en `salidas_imagenes/DDU_{num}_img_{idx}.{ext}`.
- Generar manifiesto ligero en `ResultadoBloque.datos["imagenes"]`.

**Step 4: Ejecutar test para verificar éxito**
`pytest test/test_extractor_imagenes.py -v`

**Step 5: Commit local en español**
`git add scripts/extractors/imagenes.py test/test_extractor_imagenes.py`
`git commit -m "feat: refactorizar ImagenesExtractor con manifiesto ligero y exportación a salidas_imagenes"`

---

### Task 4: Actualizar `DDUOrchestrator`, Tests de Integración y Salidas

**Files:**
- Modify: `scripts/ddu_orchestrator.py`
- Modify: `test/test_orchestrator.py`
- Modify: `salidas_csv/DDU_456_extraido.csv`
- Modify: `salidas_xml/DDU_456_akoma.xml`
- Modify: `salidas_rdf/DDU_456_rdf.ttl`

**Step 1: Actualizar `test/test_orchestrator.py`**
Validar manifiestos ligeros en `test_orchestrator_process_pdf_ddu_456` y `test_export_individual_csv_ddu_456`.

**Step 2: Ejecutar regeneración de CSV individual con DDU 456**
`py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 456.pdf" --export-csv`

**Step 3: Regenerar Akoma XML y RDF**
`py -3 scripts/csv_to_akoma_xml.py --csv "salidas_csv/DDU_456_extraido.csv" --output "salidas_xml/DDU_456_akoma.xml"`
`py -3 scripts/csv_to_rdf.py --csv "salidas_csv/DDU_456_extraido.csv" --output "salidas_rdf/DDU_456_rdf.ttl"`

**Step 4: Commit local en español**
`git add scripts/ddu_orchestrator.py test/test_orchestrator.py salidas_csv/DDU_456_extraido.csv salidas_xml/DDU_456_akoma.xml salidas_rdf/DDU_456_rdf.ttl`
`git commit -m "feat: integrar manifiesto ligero en orquestador y regenerar salidas DDU 456"`

---

### Task 5: Verificación Final de la Suite Completa y Documentación

**Files:**
- Modify: `CHANGELOG.md`
- Modify: `docs/plans/task.md`

**Step 1: Ejecutar la suite completa**
`pytest -v` (100% pasando).

**Step 2: Actualizar `CHANGELOG.md` y `task.md`**

**Step 3: Commit final**
`git add CHANGELOG.md docs/plans/task.md`
`git commit -m "docs: registrar arquitectura desacoplada de tablas e imagenes en CHANGELOG"`
