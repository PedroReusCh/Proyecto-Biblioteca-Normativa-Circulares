# Plan de Implementación: Limpiador Universal de Palabras Divididas por OCR en `NotaAlPieExtractor` (`nota_al_pie.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Re-ensamblar palabras fragmentadas por espacios de escaneo/OCR (ej. `carácte r`, `'con tain ers'`, `mirado res`, `higié nicos`, `paño les`, `herramien tas`, `artícu lo`, `edificac ión`) en `scripts/extractors/nota_al_pie.py`.

**Architecture:** Crear e integrar la función `_limpiar_palabras_divididas_ocr` en `scripts/extractors/nota_al_pie.py`, agregar la prueba unitaria en `test/test_extractor_nota_al_pie.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Limpieza de Palabras Divididas en `test/test_extractor_nota_al_pie.py`

**Files:**
- Modify: `test/test_extractor_nota_al_pie.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_nota_al_pie.py`:
```python
def test_nota_al_pie_extractor_limpieza_palabras_divididas() -> None:
    """Verifica la desinfección de palabras divididas por OCR en notas al pie."""
    lines = [
        "1 En dicha circular se indica pero no a recintos que tengan el carácte r de local habitable, como es el caso para los 'con tain ers'.",
        "3 En el artículo 1.1.2. de la OGUC se define Edificaciones con destinos complementarios al área verde como construcciones complementarias a la recreación, tales como sombreaderos, pérgolas, mirado res, juegos infantiles, servicios higié nicos, paño les para herramien tas... Por su parte, en el literal b) del artícu lo 1.6.3. de la OGUC...",
    ]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    notas = resultado.datos.get("notas_al_pie", "")
    assert "carácter de local" in notas
    assert "containers" in notas
    assert "miradores" in notas
    assert "higiénicos" in notas
    assert "pañoles" in notas
    assert "herramientas" in notas
    assert "artículo 1.6.3." in notas
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_nota_al_pie.py::test_nota_al_pie_extractor_limpieza_palabras_divididas -v`  
Expected: FAIL con `AssertionError: assert 'carácter de local' in ...`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_nota_al_pie.py
git commit -m "test: agregar prueba unitaria para limpieza de palabras divididas por OCR en nota_al_pie.py"
```

---

### Task 2: Implementar Helper `_limpiar_palabras_divididas_ocr` en `scripts/extractors/nota_al_pie.py`

**Files:**
- Modify: `scripts/extractors/nota_al_pie.py`
- Test: `test/test_extractor_nota_al_pie.py`

**Step 1: Crear e integrar `_limpiar_palabras_divididas_ocr` en `nota_al_pie.py`**

```python
def _limpiar_palabras_divididas_ocr(texto: str) -> str:
    """Re-ensambla palabras fragmentadas por espacios de escaneo/OCR."""
    # Re-ensamblar anglicismos y términos compuestos divididos
    texto = re.sub(r"\bcon\s+tain\s+ers\b", "containers", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bcon\s+tainers\b", "containers", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bcontain\s+ers\b", "containers", texto, flags=re.IGNORECASE)

    # Re-ensamblar sufijos terminados en 'ción' / 'ciones' (ej: edificac ión -> edificación)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+i([óo]n|iones)\b", r"\1i\2", texto)

    # Re-ensamblar sufijos terminados en 'lo' / 'los' (ej: artícu lo -> artículo)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+tícu)\s+(lo|los)\b", r"\1\2", texto)

    # Re-ensamblar plurales y terminaciones comunes en 'res', 'les', 'nes', 'dos', 'das', 'tos', 'tas', 'nicos', 'mente'
    texto = re.sub(
        r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|mente|nicos|nica|nicas)\b",
        r"\1\2",
        texto,
    )

    # Re-ensamblar letra aislada al final de palabra (ej: carácte r -> carácter)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", texto)

    return re.sub(r"\s+", " ", texto).strip()
```

Invocaciones:
- En `_guardar_nota_actual()` sobre `texto_completo`.
- En `extract()` sobre `notas_texto`.

**Step 2: Ejecutar `pytest test/test_extractor_nota_al_pie.py -v`**

Run: `pytest test/test_extractor_nota_al_pie.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/nota_al_pie.py
git commit -m "feat: implementar limpiador universal de palabras divididas por OCR en nota_al_pie.py"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (36/36 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con la celda `notas_al_pie` completamente desinfectada.

**Step 3: Commit**

```bash
git add test/test_extractor_nota_al_pie.py scripts/extractors/nota_al_pie.py
git commit -m "feat: certificar la desinfeccion de palabras divididas por OCR en nota_al_pie.py"
```
