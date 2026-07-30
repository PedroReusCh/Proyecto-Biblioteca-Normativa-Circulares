# Plan de Implementación: Captura Multilínea y Delimitación Dinámica en `NotaAlPieExtractor`

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar la captura multilínea y la delimitación dinámica de notas al pie en `NotaAlPieExtractor` para extraer correctamente las notas completas multirrenglón de circulares como la DDU 546.

**Architecture:** Modificar `NotaAlPieExtractor.extract` en `scripts/extractors/nota_al_pie.py` utilizando una Máquina de Estados de acumulación de renglones que se detiene al detectar un nuevo número de nota, pie institucional o cierre de documento. Se extiende `test/test_extractor_nota_al_pie.py` con pruebas para la DDU 546 y se verifica la suite de pruebas al 100%.

**Tech Stack:** Python 3.13, pytest, pypdf, re, git.

---

### Task 1: Agregar Prueba Unitaria Multilínea para DDU 546 en `test/test_extractor_nota_al_pie.py`

**Files:**
- Modify: `test/test_extractor_nota_al_pie.py`

**Step 1: Escribir la prueba unitaria multilínea que actualmente falla**

En `test/test_extractor_nota_al_pie.py`:
```python
def test_nota_al_pie_extractor_ddu_546_multiline() -> None:
    """Verifica la extracción multilínea de notas al pie en la DDU 546."""
    lines = [
        "7. Por lo tanto, las pérgolas que cumplan...",
        "1 En dicha circular se indica que el citado artículo 5.1.2, que define los casos para los cuales no será necesario",
        "el permiso de edificación, en su N° 2 se refiere a elementos exteriores sobrepuestos complementarios a una",
        "edificación, como pueden ser terrazas, parrones, glorietas, u otros...",
        "2 En el artículo 1.1.2. de la OGUC se define \"Construcción\" como \"obras de edificación o de urbanización\".",
        "--========== GOBIERNO DE CHILE ====== ====~",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 2 de 3",
    ]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.nombre_bloque == "nota_al_pie"
    assert resultado.exito is True
    notas: str = str(resultado.datos.get("notas_al_pie", ""))
    assert "el permiso de edificación, en su N° 2" in notas
    assert "2 En el artículo 1.1.2." in notas
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_nota_al_pie.py -v`  
Expected: FAIL con `AssertionError: assert 'el permiso de edificación, en su N° 2' in notas`

**Step 3: Commit de la prueba**

```bash
git add test/test_extractor_nota_al_pie.py
git commit -m "test: agregar prueba unitaria multilineal de notas al pie para DDU 546"
```

---

### Task 2: Implementar Máquina de Estados Multilínea en `scripts/extractors/nota_al_pie.py`

**Files:**
- Modify: `scripts/extractors/nota_al_pie.py`
- Test: `test/test_extractor_nota_al_pie.py`

**Step 1: Implementar la acumulación multilínea en `NotaAlPieExtractor.extract`**

```python
    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        notas: List[str] = []
        nota_actual_lines: List[str] = []

        def _guardar_nota_actual() -> None:
            if nota_actual_lines:
                texto_completo = " ".join(nota_actual_lines).strip()
                texto_completo = re.sub(r"\s+", " ", texto_completo)
                if texto_completo:
                    notas.append(texto_completo)
                nota_actual_lines.clear()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Detener si llegamos al pie institucional o firma/cierre de página
            if re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE) or re.search(
                r"(?:Saluda\s+atent|DISTRIBUCI[ÓO\?I\s]+N|GOBIERNO\s+DE\s+CHILE)", line_clean, re.IGNORECASE
            ):
                _guardar_nota_actual()
                continue

            match_nota = re.match(r"^(\d{1,2})\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\.,\(\)\"\'-].+)$", line_clean)
            if match_nota:
                num_nota = match_nota.group(1)
                texto_nota = match_nota.group(2).strip()

                if int(num_nota) <= 20 and not line_clean.startswith(f"{num_nota}. "):
                    if not re.match(r"^\d+\s+(?:de\s+la|de\s+los|del|en\s+la|con\s+la|que|por|para)\b", line_clean, re.IGNORECASE):
                        if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley|Construcci[óo]n|Edificaci[óo]n|OGUC|LGUC)\b", texto_nota, re.IGNORECASE):
                            _guardar_nota_actual()
                            nota_actual_lines.append(f"{num_nota} {texto_nota}")
                            continue

            # Si hay una nota en curso, acumular las líneas continuas
            if nota_actual_lines:
                nota_actual_lines.append(line_clean)

        _guardar_nota_actual()

        notas_texto = " | ".join(notas) if notas else ""
        exito = bool(notas_texto)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"notas_al_pie": notas_texto},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se identificaron notas al pie de página en la circular.",
        )
```

**Step 2: Ejecutar `pytest test/test_extractor_nota_al_pie.py -v`**

Run: `pytest test/test_extractor_nota_al_pie.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/extractors/nota_al_pie.py
git commit -m "feat: implementar acumulacion multilineal y delimitacion dinamica de notas al pie"
```

---

### Task 3: Verificación de Integración y Exportación CSV de DDU 546

**Files:**
- Output: `salidas_csv/DDU_546_extraido.csv`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar suite completa `pytest -v`**

Run: `pytest -v`  
Expected: PASS (31/31 PASSED)

**Step 2: Exportar CSV para DDU 546**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 546.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_546_extraido.csv` con las 3 notas al pie completas en el bloque 10.

**Step 3: Commit**

```bash
git add test/test_extractor_nota_al_pie.py scripts/extractors/nota_al_pie.py
git commit -m "feat: certificar la extraccion multilineal completa de notas al pie para DDU 546"
```
