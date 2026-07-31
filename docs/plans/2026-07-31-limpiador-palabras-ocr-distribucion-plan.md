# Plan de Implementación: Limpiador Universal de Palabras Divididas por OCR en `DistribucionExtractor` (`distribucion.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Re-ensamblar palabras fragmentadas por espacios de escaneo/OCR (ej. `Contra loría I nterna MINVU`, `Territor ial`, `Territo rial`, `Autorizac iones`, `Reviso res`, `Secreta rias`) en `scripts/extractors/distribucion.py`.

**Architecture:** Potenciar `_limpiar_item_distribucion` en `scripts/extractors/distribucion.py`, agregar la prueba unitaria en `test/test_extractor_body.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria para Limpieza de Palabras Divididas en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_distribucion_extractor_limpieza_palabras_divididas() -> None:
    """Verifica la desinfección universal de palabras divididas por OCR en la distribución."""
    lines = [
        "DISTRIBUCIÓN:",
        "7. Contra loría I nterna MINVU.",
        "13. Depto. de Ordenamiento Territor ial y Medio Ambiente (GORE Metropolitano)",
        "16. Sr. Jefe de la Oficina de Autorizac iones Sectoriales e Inversión",
        "26. Consejo Nacional de Desarrollo Territo rial.",
    ]

    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    distribucion: List[str] = list(resultado.datos.get("lista_distribucion", []))
    assert len(distribucion) == 4
    assert distribucion[0] == "7. Contraloría Interna MINVU."
    assert distribucion[1] == "13. Depto. de Ordenamiento Territorial y Medio Ambiente (GORE Metropolitano)"
    assert distribucion[2] == "16. Sr. Jefe de la Oficina de Autorizaciones Sectoriales e Inversión"
    assert distribucion[3] == "26. Consejo Nacional de Desarrollo Territorial."
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_distribucion_extractor_limpieza_palabras_divididas -v`  
Expected: FAIL con `AssertionError: assert '7. Contra loría I nterna MINVU.' == '7. Contraloría Interna MINVU.'`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para limpieza de palabras divididas por OCR en distribucion.py"
```

---

### Task 2: Implementar Limpieza Sufijal General en `scripts/extractors/distribucion.py`

**Files:**
- Modify: `scripts/extractors/distribucion.py`
- Test: `test/test_extractor_body.py`

**Step 1: Potenciar `_limpiar_item_distribucion` en `distribucion.py`**

```python
def _limpiar_item_distribucion(item: str) -> str:
    # 1. Normalizar prefijo numérico ruidoso o confundido por OCR
    item = re.sub(r"^[\,\!\;\:\_\-\s]+(\d+)", r"\1", item)
    item = re.sub(r"^[lIi\|][\.\!\;\:\,\_\-\s]+\s*", r"1. ", item)
    item = re.sub(r"^(\d+)[\!\;\:\,\_\-]+\s*", r"\1. ", item)
    item = re.sub(r"^(\d+)\s*\.\s*", r"\1. ", item)

    # 2. Siglas e instituciones
    item = re.sub(r"\bMI\s+NVU\b", "MINVU", item, flags=re.IGNORECASE)
    item = re.sub(r"\bSERE\s+MI\b", "SEREMI", item, flags=re.IGNORECASE)
    item = re.sub(r"\bSER\s+VIU\b", "SERVIU", item, flags=re.IGNORECASE)
    item = re.sub(r"\bI\s+nterna\b", "Interna", item, flags=re.IGNORECASE)

    # 3. Re-ensamblar sufijos en '-ial', '-rial', '-loría' (ej: Territor ial -> Territorial, Contra loría -> Contraloría)
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{2,})\s+(ial|rial|loría)\b", r"\1\2", item, flags=re.IGNORECASE)

    # 4. Re-ensamblar sufijos terminados en '-ción' / '-ciones' (ej: Autorizac iones -> Autorizaciones)
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+i([óo]n|iones)\b", r"\1i\2", item, flags=re.IGNORECASE)

    # 5. Re-ensamblar plurales y terminaciones comunes
    item = re.sub(
        r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|ria|rias|rios|tiva|tivas)\b",
        r"\1\2",
        item,
        flags=re.IGNORECASE,
    )

    # 6. Letra aislada al final de palabra
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", item, flags=re.IGNORECASE)

    item = re.sub(r"[\s;]+$", "", item)
    item = re.sub(r"\s*;\s*", " ", item)
    item = re.sub(r"\s+\.", ".", item)
    return re.sub(r"\s+", " ", item).strip()
```

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/distribucion.py
git commit -m "feat: implementar limpiador universal de palabras divididas por OCR en distribucion.py"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (37/37 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con la celda `lista_distribucion` completamente limpia.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/distribucion.py
git commit -m "feat: certificar la desinfeccion de palabras divididas por OCR en distribucion.py"
```
