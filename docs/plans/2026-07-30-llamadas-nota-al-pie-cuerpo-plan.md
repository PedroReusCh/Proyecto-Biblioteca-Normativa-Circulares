# Plan de Implementación: Normalización de Llamadas a Notas al Pie `[N]` en `CuerpoExtractor`

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar el formateo formal `[1]`, `[2]`, `[3]` para los dígitos de llamada a notas al pie dentro del texto extraído en `cuerpo.py`, resolviendo la distorsión de artículos citados (ej. `artículo 381` ➔ `artículo 38 [1]`) y formateando las llamadas tras palabras o signos de puntuación.

**Architecture:** Crear e integrar el helper `_normalizar_llamadas_nota_al_pie` en `scripts/extractors/cuerpo.py`, agregar la prueba unitaria en `test/test_extractor_body.py`, re-exportar los CSVs de salida y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Llamadas `[N]` en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_cuerpo_extractor_llamadas_nota_al_pie() -> None:
    """Verifica la normalización de llamadas a notas al pie al formato [N]."""
    lines = [
        "1. De conformidad con lo dispuesto...",
        "DDU ESPECÍFICA Nº97 /2007 1.",
        "a) Que la pérgola consista en un elemento -es decir que no tenga el carácter de construcción 2- y que además sea exterior.",
        "3. Conforme al artículo 381 del referido DS 86.",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    secciones = resultado.datos.get("secciones", [])
    texto_completo = " ".join([p for s in secciones for p in s.get("parrafos", [])])

    assert "Nº97 /2007 [1]" in texto_completo
    assert "carácter de construcción [2]" in texto_completo
    assert "artículo 38 [1]" in texto_completo
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_llamadas_nota_al_pie -v`  
Expected: FAIL con `AssertionError: assert 'Nº97 /2007 [1]' in ...`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para normalizacion de llamadas a notas al pie [N] en cuerpo.py"
```

---

### Task 2: Implementar Helper `_normalizar_llamadas_nota_al_pie` en `scripts/extractors/cuerpo.py`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`
- Test: `test/test_extractor_body.py`

**Step 1: Crear e integrar `_normalizar_llamadas_nota_al_pie` en `cuerpo.py`**

```python
def _normalizar_llamadas_nota_al_pie(line: str) -> str:
    """Formatea dígitos de llamada a notas al pie en corchetes [1], [2], [3]."""
    # 1. Separar citas de artículos con llamadas pegadas (ej. "artículo 381" -> "artículo 38 [1]")
    line = re.sub(r"\bart[íi]culo\s+(\d{1,3})([1-9])\b", r"artículo \1 [\2]", line, flags=re.IGNORECASE)

    # 2. Formatear dígitos sueltos al final de palabra o fecha antes de punto/coma o espacio (ej. "Nº97 /2007 1." -> "Nº97 /2007 [1].", "construcción 2-" -> "construcción [2]-")
    line = re.sub(r"([a-záéíóúñA-ZÁÉÍÓÚÑ\)\/0-9])\s+([1-9])([\s\.,\-\)\;]|$)", r"\1 [\2]\3", line)

    return line
```

Llamar a `_normalizar_llamadas_nota_al_pie` dentro del bucle de extracción de párrafos en `CuerpoExtractor.extract`.

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/cuerpo.py
git commit -m "feat: integrar helper _normalizar_llamadas_nota_al_pie para formatear llamadas [N] en cuerpo.py"
```

---

### Task 3: Verificación Completa y Exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_537_extraido.csv`
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (32/32 PASSED)

**Step 2: Re-exportar CSVs para DDU 537 y DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 537.pdf" --export-csv`  
Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSVs exportados exitosamente mostrando las llamadas formateadas como `[1]`, `[2]`.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/cuerpo.py
git commit -m "feat: certificar la normalizacion de llamadas a nota al pie [N] en cuerpo.py"
```
