# Plan de Implementación: Corrección de Lista de Distribución en `DistribucionExtractor` (`distribucion.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Reparar la extracción de la lista de distribución en `distribucion.py` para la DDU 546 reconociendo encabezados OCR distorsionados (ej. `RIBuc)óN:`), purgando ruido y capturando la nómina limpia de receptores.

**Architecture:** Modificar `patron_encabezado_distribucion` y `_limpiar_item_distribucion` en `scripts/extractors/distribucion.py`, agregar la prueba unitaria en `test/test_extractor_body.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Distribución en DDU 546 en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_distribucion_extractor_ddu_546_ocr() -> None:
    """Verifica la extracción limpia de la lista de distribución en DDU 546 con OCR distorsionado."""
    lines = [
        "Saluda atentamente a Ud.,",
        "N DIEGO ZQUIERDO HEVIA",
        "D VISIÓN DE DESARROLLO URBANO",
        "tl ' .",
        "RA/4l ¡ ~ /O M",
        "RIBuc)óN:",
        "Sr. Ministro de Vivienda y Urbanismo",
        ",2. Sra. Subsecretaria de Vivienda y Urbanismo",
        "3. Sra. Contralora General de la República",
    ]

    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    distribucion: List[str] = list(resultado.datos.get("lista_distribucion", []))
    assert len(distribucion) == 3
    assert distribucion[0] == "1. Sr. Ministro de Vivienda y Urbanismo"
    assert distribucion[1] == "2. Sra. Subsecretaria de Vivienda y Urbanismo"
    assert distribucion[2] == "3. Sra. Contralora General de la República"
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_distribucion_extractor_ddu_546_ocr -v`  
Expected: FAIL con `AssertionError: assert len(distribucion) == 3` (obtiene ítems ruidosos del firmante).

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para extraccion de distribucion en DDU 546"
```

---

### Task 2: Implementar Corrección de OCR y Filtrado en `scripts/extractors/distribucion.py`

**Files:**
- Modify: `scripts/extractors/distribucion.py`
- Test: `test/test_extractor_body.py`

**Step 1: Ampliar regex de encabezado y desinfección de prefijos en `distribucion.py`**

```python
        patron_encabezado_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )
```

En `_limpiar_item_distribucion`:
```python
        item = re.sub(r"^[\,\!\;\:\_\-\s]+(\d+)", r"\1", item)
```

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/distribucion.py
git commit -m "feat: reparar reconocimiento de encabezado OCR y desinfeccion de distribucion en DDU 546"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (34/34 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con la nómina de distribución limpia de 33 receptores.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/distribucion.py
git commit -m "feat: certificar la extraccion limpia de la lista de distribucion para DDU 546"
```
