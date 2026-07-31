# Plan de Implementación: Exclusión de Notas al Pie y Preservación de Numerales en `CuerpoExtractor` (`cuerpo.py`) para DDU 537

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Prevenir la pérdida de numerales del cuerpo (ej. Numeral 4) y excluir limpiamente las notas al pie de página (ej. Nota 1 y Nota 2) en `scripts/extractors/cuerpo.py` para la DDU 537.

**Architecture:** Normalizar prefijos numerales con espacios intermedios (`^\d+\s+\.\s*` ➔ `\1. `) en `_normalizar_prefijo_numeral_ocr` y controlar el reseteo de `omitiendo_nota_al_pie` al detectar pies de página o nuevos numerales en `scripts/extractors/cuerpo.py`.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Exclusión de Notas al Pie en DDU 537 en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_cuerpo_extractor_ddu_537_exclusion_notas_al_pie() -> None:
    """Verifica la inclusión completa del Numeral 4 y exclusión de notas al pie en DDU 537."""
    lines = [
        "3. En atención a las normas antes citadas, es posible afirmar que...",
        "1 Artículo 38. Lineamientos y estándares de los mapas de amenaza y riesgo...",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 2 de 4",
        "4 . Si bien la utilización de estos mapas de amenazas resulta obligatoria para la elaboración de los IPT...",
        "5. Sin embargo, en caso de no existir los mapas de amenazas...",
        "2 La orientación técnica específica para estas materias está contenida en el punto 2.3...",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 3 de 4",
        "a lo establecido en el artículo 29 del Decreto N° 32 de 2015...",
        "8. Por su parte, respecto del artículo 36 de la Ley N° 21.364...",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    cuerpo = resultado.datos.get("cuerpo", "")
    assert "4. Si bien la utilización" in cuerpo
    assert "1 Artículo 38" not in cuerpo
    assert "2 La orientación técnica" not in cuerpo
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_ddu_537_exclusion_notas_al_pie -v`  
Expected: FAIL con `AssertionError: assert '4. Si bien la utilización' in ...`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para exclusion de notas al pie en DDU 537 en cuerpo.py"
```

---

### Task 2: Implementar Normalización de Numerales y Reseteo de Estado en `scripts/extractors/cuerpo.py`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`
- Test: `test/test_extractor_body.py`

**Step 1: Normalizar `^\d+\s+\.` y resetear `omitiendo_nota_al_pie` en `cuerpo.py`**

En `_normalizar_prefijo_numeral_ocr`:
```python
def _normalizar_prefijo_numeral_ocr(line: str) -> str:
    """Normaliza distorsiones de caracteres OCR al inicio de numerales de párrafo."""
    # 0. Normalizar espacios entre dígito y punto (ej. "4 . ", "7 . ") -> "4. "
    line = re.sub(r"^(\d+)\s+\.\s*", r"\1. ", line)
    # ...
```

En `CuerpoExtractor.extract`:
```python
            # Descartar líneas de pie de página de OCR (incluyendo espacios rotos) y resetear estado de notas al pie
            if _es_pie_de_pagina(line_clean):
                omitiendo_nota_al_pie = False
                curr_idx += 1
                continue
```

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/cuerpo.py
git commit -m "feat: corregir normalizacion de numerales y exclusión de notas al pie en cuerpo.py para DDU 537"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (38/38 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv`.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/cuerpo.py
git commit -m "feat: certificar la exclusion limpia de notas al pie en cuerpo.py para DDU 537"
```
