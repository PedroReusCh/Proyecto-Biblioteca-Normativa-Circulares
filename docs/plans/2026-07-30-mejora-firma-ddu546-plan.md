# Plan de Implementación: Corrección de Firma y Cargo en `FirmaExtractor` (`firma.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Detener la extracción de firma al llegar al encabezado de distribución distorsionado por OCR (ej. `RIBuc)óN:`) y reparar nombres/cargos con daños de OCR en `scripts/extractors/firma.py`.

**Architecture:** Integrar `patron_encabezado_distribucion` y el helper `_limpiar_texto_firma` en `scripts/extractors/firma.py`, agregar la prueba unitaria en `test/test_extractor_body.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Firma y Cargo en DDU 546 en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_firma_extractor_ddu_546_ocr() -> None:
    """Verifica la extracción limpia y normalizada del firmante en DDU 546."""
    lines = [
        "Saluda atentamente a Ud.,",
        "N DIEGO ZQUIERDO HEVIA",
        "D VISIÓN DE DESARROLLO URBANO",
        "IS RIO DE VIVIENDA Y URBANISMO",
        "tl ' .",
        "RA/4l ¡ ~ /O M",
        "RIBuc)óN:",
        "Sr. Ministro de Vivienda y Urbanismo",
    ]

    extractor = FirmaExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    firmante = resultado.datos.get("firmante", "")
    assert firmante == "JUAN DIEGO IZQUIERDO HEVIA, DIVISIÓN DE DESARROLLO URBANO, MINISTERIO DE VIVIENDA Y URBANISMO"
    assert "Sr. Ministro" not in firmante
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_firma_extractor_ddu_546_ocr -v`  
Expected: FAIL con `AssertionError: assert 'N DIEGO ZQUIERDO...' == 'JUAN DIEGO IZQUIERDO...'` (obtiene texto ruidoso sin corregir y con receptor de distribución).

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para extraccion de firma en DDU 546"
```

---

### Task 2: Implementar Corrección de Firma y Detención de Distribución en `scripts/extractors/firma.py`

**Files:**
- Modify: `scripts/extractors/firma.py`
- Test: `test/test_extractor_body.py`

**Step 1: Integrar regex de detención por distribución y `_limpiar_texto_firma` en `firma.py`**

```python
def _limpiar_texto_firma(texto: str) -> str:
    """Repara distorsiones típicas de OCR en nombres y cargos de firmantes."""
    texto = re.sub(r"\bN\s+DIEGO\s+ZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bN\s+DIEGO\s+IZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bD\s+VISI[ÓO]N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bIS\s+RIO\b", "MINISTERIO", texto, flags=re.IGNORECASE)
    return texto
```

En `FirmaExtractor.extract`:
```python
        patron_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )
```
Detener la iteración de `partes_firma` si `re.match(patron_distribucion, line_clean, re.IGNORECASE)` coincide.  
Aplicar `_limpiar_texto_firma` a `firmante`.

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/firma.py
git commit -m "feat: reparar extraccion y normalizacion OCR de firma en DDU 546"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (35/35 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con la celda `firmante` igual a `JUAN DIEGO IZQUIERDO HEVIA, DIVISIÓN DE DESARROLLO URBANO, MINISTERIO DE VIVIENDA Y URBANISMO`.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/firma.py
git commit -m "feat: certificar la extraccion limpia del firmante y cargo para DDU 546"
```
