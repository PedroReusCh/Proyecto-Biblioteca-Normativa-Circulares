# Plan de Implementación: Exclusión de Notas al Pie en `CuerpoExtractor` (`cuerpo.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Filtrar y omitir líneas de notas al pie dentro de `CuerpoExtractor.extract` en `scripts/extractors/cuerpo.py` para que el cuerpo normativo extraído no incluya las notas explicativas de pie de página.

**Architecture:** Crear e integrar el helper `_es_inicio_nota_al_pie` y la máquina de descarte de notas en `scripts/extractors/cuerpo.py`, agregar la prueba unitaria en `test/test_extractor_body.py`, re-exportar el CSV de DDU 546 y certificar la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, re, git.

---

### Task 1: Agregar Prueba Unitaria de Exclusión de Notas al Pie en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba unitaria que actualmente falla**

En `test/test_extractor_body.py`:
```python
def test_cuerpo_extractor_exclusion_notas_al_pie() -> None:
    """Verifica que el extractor de cuerpo excluya las notas explicativas al pie de página."""
    lines = [
        "1. De conformidad a lo dispuesto en el artículo 4°...",
        "7. Por lo tanto, las pérgolas que cumplan...",
        "1 En dicha circular se indica que el citado artículo 5.1.2...",
        "2 En el artículo 1.1.2. de la OGUC se define...",
        "8. Con todo, debe advertirse que la circunstancia...",
        "Saluda atentamente a Ud.,",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    secciones: List[Any] = list(resultado.datos.get("secciones", []))
    texto_completo = " ".join([p for s in secciones for p in s.get("parrafos", [])])

    assert "7. Por lo tanto, las pérgolas que cumplan..." in texto_completo
    assert "8. Con todo, debe advertirse que la circunstancia..." in texto_completo
    assert "1 En dicha circular se indica" not in texto_completo
    assert "2 En el artículo 1.1.2. de la OGUC" not in texto_completo
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_exclusion_notas_al_pie -v`  
Expected: FAIL con `AssertionError: assert '1 En dicha circular se indica' not in ...`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_body.py
git commit -m "test: agregar prueba unitaria para exclusion de notas al pie en cuerpo.py"
```

---

### Task 2: Implementar Filtrado de Notas al Pie en `scripts/extractors/cuerpo.py`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`
- Test: `test/test_extractor_body.py`

**Step 1: Crear e integrar `_es_inicio_nota_al_pie` y la máquina de descarte en `cuerpo.py`**

```python
def _es_inicio_nota_al_pie(line: str) -> bool:
    """Detecta si una línea corresponde al inicio de una nota al pie explicativa."""
    line_clean = line.strip()
    match = re.match(r"^(\d{1,2})\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\.,\(\)\"\'-].+)$", line_clean)
    if match:
        num = match.group(1)
        texto = match.group(2).strip()
        if int(num) <= 20 and not line_clean.startswith(f"{num}. "):
            if not re.match(r"^\d+\s+(?:de\s+la|de\s+los|del|en\s+la|con\s+la|que|por|para)\b", line_clean, re.IGNORECASE):
                if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley|Construcci[óo]n|Edificaci[óo]n|OGUC|LGUC)\b", texto, re.IGNORECASE):
                    return True
    return False
```

En `CuerpoExtractor.extract`:
Integrar el descarte de líneas pertenecientes a bloques de notas al pie durante la iteración de párrafos.

**Step 2: Ejecutar `pytest test/test_extractor_body.py -v`**

Run: `pytest test/test_extractor_body.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/cuerpo.py
git commit -m "feat: implementar exclusión de notas al pie en cuerpo.py"
```

---

### Task 3: Verificación Completa y Re-exportación de CSVs

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (33/33 PASSED)

**Step 2: Re-exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con el cuerpo limpio sin notas al pie.

**Step 3: Commit**

```bash
git add test/test_extractor_body.py scripts/extractors/cuerpo.py
git commit -m "feat: certificar la exclusion limpia de notas al pie en cuerpo.py"
```
