# Descontaminación de Tablas e Imágenes en CuerpoExtractor Implementation Plan

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Excluir por completo del cuerpo normativo las tablas de modificaciones multi-página y las etiquetas de diagramas técnicos, manteniendo exclusivamente los párrafos y numerales normativos reales (1 al 7 en DDU 456).

**Architecture:** Modificar `CuerpoExtractor` en `scripts/extractors/cuerpo.py` para detectar el inicio de bloques tabulares normativos (`Circular Materia(s)...` o líneas tabulares Markdown) y omitirlos hasta la firma/distribución, truncando limpiamente el párrafo previo al encabezado de tabla.

**Tech Stack:** Python 3.13, Regex, Pytest, Pylance Strict Mode.

---

### Task 1: Agregar pruebas unitarias de descontaminación en `test/test_extractor_body.py`

**Files:**
- Modify: `test/test_extractor_body.py`

**Step 1: Escribir la prueba fallida**

```python
def test_cuerpo_extractor_ddu_456_exclusion_tablas_e_imagenes() -> None:
    """Verifica que el cuerpo de DDU 456 contenga exactamente 7 párrafos y excluya tablas e imágenes."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([p.extract_text() or "" for p in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    extractor = CuerpoExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text, lines)

    assert resultado.exito is True
    secciones: List[Dict[str, Any]] = resultado.datos.get("secciones", [])
    assert len(secciones) == 1
    parrafos: List[str] = secciones[0].get("parrafos", [])

    # Exactamente 7 párrafos (Numerales 1 al 7)
    assert len(parrafos) == 7, f"Se esperaban 7 párrafos normativos, se obtuvieron {len(parrafos)}"

    # Verificar numeral 4 limpio
    assert parrafos[3].startswith("4.")
    assert "A continuación, se presenta un esquema ilustrativo" in parrafos[3]
    assert "PLANTA AZOTEA" not in parrafos[3]
    assert "CORTE ESQUEMÁTICO" not in parrafos[3]

    # Verificar numeral 7 limpio (sin contenido de la tabla de circulares)
    assert parrafos[6].startswith("7.")
    assert "Circular Materia(s) que se modifica(n)" not in parrafos[6]
    assert "DDU 339" not in parrafos[6]
    assert "DDU 322" not in parrafos[6]
    assert "DDU 168" not in parrafos[6]
```

**Step 2: Ejecutar test para verificar que falla**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_ddu_456_exclusion_tablas_e_imagenes -v`
Expected: FAIL con `assert len(parrafos) == 7` (actualmente da 10 párrafos).

---

### Task 2: Implementar detección y omisión de bloques tabulares en `scripts/extractors/cuerpo.py`

**Files:**
- Modify: `scripts/extractors/cuerpo.py`

**Step 1: Implementar `_es_inicio_bloque_tabla` y omitir líneas tabulares**

```python
def _es_inicio_bloque_tabla(line: str) -> bool:
    """Detecta el inicio de un bloque tabular normativo para excluirlo del cuerpo."""
    line_clean = line.strip()
    if re.search(r"Circular\s+Materia\(s\)\s+que\s+se\s+modifica\(n\)", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^\|\s*Circular\b", line_clean, re.IGNORECASE):
        return True
    return False
```

En `extract()`:
- Al encontrar `_es_inicio_bloque_tabla(line_clean)`:
  - Si `parrafo_actual` contiene texto que fue capturado del inicio de la tabla (ej. `Circular Materia(s)...`), truncarlo en la frase introductoria normativa (antes de `Circular Materia`).
  - Guardar `parrafo_actual` y activar `omitiendo_tabla = True`.
  - Continuar el bucle descartando líneas hasta encontrar `Saluda atentamente` o `DISTRIBUCIÓN`.

**Step 2: Ejecutar test unitario para verificar que pasa**

Run: `pytest test/test_extractor_body.py::test_cuerpo_extractor_ddu_456_exclusion_tablas_e_imagenes -v`
Expected: PASS (7/7 párrafos).

---

### Task 3: Regenerar salidas y validar suite completa

**Files:**
- Modify: `salidas_csv/DDU_456_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Regenerar CSV individual**

Run: `py scripts/ddu_orchestrator.py --pdf "circulares/DDU 456.pdf" --output-dir salidas_csv --export-csv`

**Step 2: Ejecutar suite completa de pruebas**

Run: `pytest -v`
Expected: 72/72 PASSED.
