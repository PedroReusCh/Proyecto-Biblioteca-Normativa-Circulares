# Plan de Implementación: Extracción Completa de Modificaciones Posteriores

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Actualizar `ModificacionesPosterioresExtractor` para escanear todas las páginas del PDF y capturar íntegramente las notas marginales de vigencia y aclaración de modificaciones posteriores.

**Architecture:** Modificar `scripts/extractors/modificaciones_posteriores.py` para iterar sobre todos los bloques de texto de todas las páginas del PDF (con PyMuPDF o pypdf) o texto completo, y consolidar las notas completas con `; `.

**Tech Stack:** Python 3.13, PyMuPDF (`fitz`), typing estricto, pytest.

---

### Task 1: Actualizar `test/test_extractor_modificaciones_posteriores.py` con Tests para Ambas Notas en DDU 456

**Files:**
- Modify: `test/test_extractor_modificaciones_posteriores.py`

**Step 1: Escribir tests que validen las 2 notas completas**
- Nota 1: `Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.)`
- Nota 2: `Mediante Circular Ord. N°214, de fecha 02.05.2024, DDU 498, se aclara que la materia contenida en la Circular DDU 339 se aborda en el punto 6 y no en el 5 como de había indicado previamente.`

**Step 2: Ejecutar test para verificar estado actual**
`pytest test/test_extractor_modificaciones_posteriores.py -v`

---

### Task 2: Implementar Escaneo Multi-Página y Expresiones Robustas en `scripts/extractors/modificaciones_posteriores.py`

**Files:**
- Modify: `scripts/extractors/modificaciones_posteriores.py`

**Step 1: Implementar extracción sobre todas las páginas y bloques**
Escanear todos los bloques de texto de todas las páginas si `pdf_path` está disponible, o sobre `raw_text`/`lines`.

**Step 2: Ejecutar tests para verificar que pasen**
`pytest test/test_extractor_modificaciones_posteriores.py -v`

**Step 3: Commit**
`git add scripts/extractors/modificaciones_posteriores.py test/test_extractor_modificaciones_posteriores.py`
`git commit -m "feat: implementar escaneo multi-página exhaustivo en ModificacionesPosterioresExtractor"`

---

### Task 3: Regeneración de Salidas, Validación de Suite Completa y Actualización de CHANGELOG

**Files:**
- Modify: `salidas_csv/DDU_456_extraido.csv`
- Modify: `CHANGELOG.md`
- Modify: `test/test_orchestrator.py`

**Step 1: Actualizar `test_export_individual_csv_ddu_456` en `test/test_orchestrator.py`**
**Step 2: Regenerar `salidas_csv/DDU_456_extraido.csv`, `salidas_xml/DDU_456_akoma.xml` y `salidas_rdf/DDU_456_rdf.ttl`**
**Step 3: Ejecutar suite completa (78+ tests)**
`pytest -v`
**Step 4: Actualizar `CHANGELOG.md`**
**Step 5: Commit y Push**
`git add salidas_csv/DDU_456_extraido.csv test/test_orchestrator.py CHANGELOG.md`
`git commit -m "docs: registrar captura completa de notas de modificaciones posteriores y regenerar DDU 456"`
`git push origin feature/ddu-456`
