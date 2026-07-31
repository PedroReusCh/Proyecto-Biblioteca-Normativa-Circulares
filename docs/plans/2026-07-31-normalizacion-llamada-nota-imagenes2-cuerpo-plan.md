# Plan de Implementación: Normalización de Llamada a Nota al Pie `imá genes 2` en `CuerpoExtractor` (`cuerpo.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Normalizar la llamada a nota al pie en el cuerpo normativo cuando la palabra viene fragmentada por OCR como `imá genes 2` a `imágenes [2]`.

**Architecture:** Modificar `_normalizar_llamadas_nota_al_pie` y `_limpiar_texto_cuerpo` en `scripts/extractors/cuerpo.py` con expresiones regulares con tolerancia a espacios intermedios de OCR.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Actualizar la Prueba Unitaria en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que valida `imá genes 2` ➔ `imágenes [2]`**

En `test/test_extractor_body.py`:
```python
def test_cuerpo_extractor_llamada_nota_imagenes_ocr() -> None:
    """Verifica que 'imá genes 2' se convierta correctamente a 'imágenes [2]'."""
    lines = [
        "DE: JEFE DIVISIÓN DE DESARROLLO URBANO",
        "4. Es decir, deberán ser sometidos a un procesamiento de las imá genes 2 para la conversión...",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    cuerpo = str(resultado.datos.get("cuerpo", ""))
    assert "imágenes [2]" in cuerpo
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_llamada_nota_imagenes_ocr -v`  
Expected: FAIL con `AssertionError: assert 'imágenes [2]' in ...`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para llamada a nota imagenes 2 con espacios OCR en cuerpo.py"
```

---

### Task 2: Implementar la Regla de Re-ensamble en `scripts/extractors/cuerpo.py`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`
- Test: `test/test_extractor_body.py`

**Step 1: Modificar `_normalizar_llamadas_nota_al_pie` y `_limpiar_texto_cuerpo`**

En `_normalizar_llamadas_nota_al_pie`:
```python
    line = re.sub(r"im[áa]\s*genes\s*2\b", "imágenes [2]", line, flags=re.IGNORECASE)
```

En `_limpiar_texto_cuerpo`:
```python
        (r"\bim[áa]\s+genes\b", "imágenes"),
```

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/cuerpo.py
git commit -m "feat: implementar normalizacion de llamada a nota imagenes 2 con tolerancia a OCR en cuerpo.py"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_537_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (39/39 PASSED)

**Step 2: Re-exportar CSV para DDU 537**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 537.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_537_extraido.csv`.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/cuerpo.py
git commit -m "feat: certificar la llamada a nota imagenes [2] en cuerpo.py para DDU 537"
```
