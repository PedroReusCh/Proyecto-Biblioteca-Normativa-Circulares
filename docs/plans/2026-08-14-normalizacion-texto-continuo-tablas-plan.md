# Plan de Implementación: Normalización de Flujo Continuo en Celdas de Tablas CSV

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar `normalizar_texto_celda_tabla` en `scripts/extractors/tablas.py` para formatear el contenido de las celdas de forma fluida y continua sin saltos de columna artificiales.

**Architecture:** Función de normalización adaptable basada en expresiones regulares para límites de ítems/párrafos, integrada en el pipeline de consolidación y exportación de tablas.

**Tech Stack:** Python 3.13, PyMuPDF, pdfplumber, typing estricto, pytest.

---

### Task 1: Crear Tests Unitarios para `normalizar_texto_celda_tabla` en `test/test_extractor_tablas.py`

**Files:**
- Modify: `test/test_extractor_tablas.py`

**Step 1: Escribir tests unitarios probando:**
- Unificación de líneas continuas en celdas.
- Preservación de saltos entre letras `a)`, `b)` o numerales `1.`, `2.`.
- Limpieza tipográfica OCR.

**Step 2: Ejecutar test para verificar fallo inicial**
`pytest test/test_extractor_tablas.py -v`

---

### Task 2: Implementar `normalizar_texto_celda_tabla` en `scripts/extractors/tablas.py`

**Files:**
- Modify: `scripts/extractors/tablas.py`

**Step 1: Implementar `normalizar_texto_celda_tabla` y aplicarla en `_compactar_tabla_pdf`, `_consolidar_tablas_multipagina` y `_exportar_tabla_csv`**

**Step 2: Ejecutar tests para verificar que pasen**
`pytest test/test_extractor_tablas.py -v`

**Step 3: Commit**
`git add scripts/extractors/tablas.py test/test_extractor_tablas.py`
`git commit -m "feat: implementar normalización de flujo continuo inteligente en celdas de tablas"`

---

### Task 3: Regeneración de Tablas, Verificación Completa y Documentación

**Files:**
- Modify: `salidas_tablas/DDU_456_tabla_1.csv`
- Modify: `CHANGELOG.md`

**Step 1: Regenerar `salidas_tablas/DDU_456_tabla_1.csv`**
**Step 2: Ejecutar suite completa (78+ tests)**
`pytest -v`
**Step 3: Actualizar `CHANGELOG.md`**
**Step 4: Commit y Push**
`git add salidas_tablas/DDU_456_tabla_1.csv CHANGELOG.md`
`git commit -m "docs: registrar normalización de flujo continuo en celdas de tablas en CHANGELOG y regenerar tabla DDU 456"`
`git push origin feature/ddu-456`
