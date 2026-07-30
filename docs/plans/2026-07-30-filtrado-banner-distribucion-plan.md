# Plan de Implementación: Filtrado de Banners de Pie de Página en `DistribucionExtractor` (`distribucion.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Omitir banners decorativos (`=::::= ========= GOBIERNO DE CHILE...`) y pies de página institucionales en `distribucion.py` para que la nómina de la lista de distribución en DDU 546 finalice en el último receptor real.

**Architecture:** Añadir regex de exclusión de banners de pie de página en `scripts/extractors/distribucion.py`, actualizar las aserciones de `test_distribucion_extractor_ddu_546_ocr` en `test/test_extractor_body.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Actualizar Prueba Unitaria para Excluir Banner de Gobierno de Chile en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_distribucion_extractor_ddu_546_ocr() -> None:
    """Verifica la extracción limpia de la lista de distribución en DDU 546 con OCR distorsionado y sin banners de pie de página."""
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
        "=::::= ========= GOBIERNO DE CHILE ====== ==-== = :-=",
    ]

    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    distribucion: List[str] = list(resultado.datos.get("lista_distribucion", []))
    assert len(distribucion) == 3
    assert distribucion[0] == "1. Sr. Ministro de Vivienda y Urbanismo"
    assert distribucion[1] == "2. Sra. Subsecretaria de Vivienda y Urbanismo"
    assert distribucion[2] == "3. Sra. Contralora General de la República"
    assert not any("GOBIERNO DE CHILE" in d for d in distribucion)
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_distribucion_extractor_ddu_546_ocr -v`  
Expected: FAIL con `AssertionError: assert len(distribucion) == 3` (obtiene 4 ítems al incluir el banner del Gobierno de Chile).

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: actualizar prueba unitaria para filtrado de banner de Gobierno de Chile en distribucion.py"
```

---

### Task 2: Implementar Filtrado de Banners en `scripts/extractors/distribucion.py`

**Files:**
- Modify: `scripts/extractors/distribucion.py`
- Test: `test/test_extractor_body.py`

**Step 1: Añadir reglas de omisión de banners e isologos de pie de página en `distribucion.py`**

```python
                if (
                    re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE)
                    or re.search(r"Ministerio\s+de\s+Vivienda\s+y\s+Urban\s*ismo", line_clean, re.IGNORECASE)
                    or re.search(r"GOBIERNO\s+DE\s+CHILE", line_clean, re.IGNORECASE)
                    or re.search(r"Alameda\s+924", line_clean, re.IGNORECASE)
                    or re.search(r"Santiago\s*-\s*Chile", line_clean, re.IGNORECASE)
                    or re.match(r"^[\=\:\-\~\s]{4,}$", line_clean)
                    or re.match(r"^!+$", line_clean)
                    or re.match(r"^(?:VICENTE|BURGOS|SALAS|JEFE\s+DIVISI[ÓO]N)\b", line_clean, re.IGNORECASE)
                ):
                    continue
```

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/distribucion.py
git commit -m "feat: omitir banners decorativos e isologos del Gobierno de Chile en distribucion.py"
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
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con la nómina de distribución limpia de exactamente 33 receptores finalizando en `33. Oficina de Partes MINVU Ley 20.285`.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/distribucion.py
git commit -m "feat: certificar el filtrado limpio de banners de pie de página en la lista de distribución"
```
