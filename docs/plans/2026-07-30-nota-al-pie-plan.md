# Plan de Implementación: Componente "Nota al Pie" (`notas_al_pie`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Agregar el nuevo componente normativo "Nota al Pie" (`notas_al_pie`) como el bloque de orden 10 en la especificación CSV de la circular DDU, creando su extractor modular, actualizando `ddu_types.py`, el orquestador y la suite de pruebas.

**Architecture:** Se crea el extractor modular `NotaAlPieExtractor` heredando de `BaseExtractor` con el decorador `@register_extractor`. Se actualiza `DatosCircularDDU` con `notas_al_pie: NotRequired[str]`, la especificación `bcn - documentación/estructura_circular_ddu.csv` insertando la fila de orden 10, el orquestador `DDUOrchestrator` y los test unitarios y de integridad CSV.

**Tech Stack:** Python 3.13, pytest, pypdf, csv, git.

---

### Task 1: Actualizar `bcn - documentación/estructura_circular_ddu.csv` y `scripts/ddu_types.py`

**Files:**
- Modify: `bcn - documentación/estructura_circular_ddu.csv`
- Modify: `scripts/ddu_types.py`
- Test: `test/test_csv_integrity.py`

**Step 1: Modificar `bcn - documentación/estructura_circular_ddu.csv` para insertar la fila de orden 10**

Reordenar `Firma` a 11 y `Distribución` a 12:
```csv
orden,bloque,campo,obligatorio,descripcion,reglas
1,Encabezado,numero_ddu,si,Número identificador de la circular DDU,Secuencial y permite singularizar la circular
2,Acto Administrativo,numero_ord,si,Número del acto de emisión de la DDU,Número de acto administrativo diferente al número DDU
3,Antecedentes,antecedentes,no,Documentos o definiciones en los que se basó para construir la circular,Campo implícito del oficio chileno
4,Materia,materia,si,Descripción del tema abordado,Descripción del tema o norma abordada
5,Descriptores,descriptores,no,Expresiones y vocablos asignados,No relevante para la aplicación de la circular
6,Fecha y Lugar,fecha_emision,si,Fecha de emisión de la circular,Permite singularizar junto con el número DDU
7,Destinatarios,destinatarios,si,A quién va dirigida formalmente la circular,A quién va dirigida formalmente la circular
8,Emisión,emisor,si,Identifica al emisor de la circular DDU,Identifica al emisor de la circular DDU
9,Cuerpo,cuerpo,si,Contenido estructurado del cuerpo de la circular,Secciones numeradas en romano o arábigos y listas anidadas
10,Nota al Pie,notas_al_pie,no,Notas aclaratorias o referencias normativas al pie de página,Notas explicativas o referencias numeradas al pie de las páginas de la circular
11,Firma,firmante,si,Firma del jefe de división respectivo,Jefe de división del periodo de emisión
12,Distribución,lista_distribucion,si,Lista de personas que reciben copia de la circular,Lista de distribución de la circular
```

**Step 2: Agregar `notas_al_pie` en `scripts/ddu_types.py`**

```python
class DatosCircularDDU(TypedDict):
    ...
    notas_al_pie: NotRequired[str]
```

**Step 3: Ejecutar `pytest test/test_csv_integrity.py -v`**

Run: `pytest test/test_csv_integrity.py -v`  
Expected: PASS con 6 columnas en las 12 filas.

**Step 4: Commit**

```bash
git add "bcn - documentación/estructura_circular_ddu.csv" scripts/ddu_types.py
git commit -m "feat: incorporar bloque Nota al Pie (orden 10) en estructura_circular_ddu.csv y ddu_types.py"
```

---

### Task 2: Implementar Extractor Modular `NotaAlPieExtractor` en `scripts/extractors/nota_al_pie.py`

**Files:**
- Create: `scripts/extractors/nota_al_pie.py`
- Modify: `scripts/extractors/__init__.py`
- Create: `test/test_extractor_nota_al_pie.py`

**Step 1: Escribir la prueba unitaria fallida**

En `test/test_extractor_nota_al_pie.py`:
```python
from scripts.extractors.nota_al_pie import NotaAlPieExtractor

def test_nota_al_pie_extractor_ddu_537() -> None:
    lines = [
        "1 Artículo 38. Lineamientos y estándares de los mapas de amenaza y riesgo.",
        "2 La orientación técnica específica para estas materias está contenida en el punto 2.3",
    ]
    extractor = NotaAlPieExtractor()
    res = extractor.extract("\n".join(lines), lines)
    assert res.nombre_bloque == "nota_al_pie"
    assert res.exito is True
    assert "Artículo 38" in res.datos["notas_al_pie"]
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_extractor_nota_al_pie.py -v`  
Expected: FAIL con `ModuleNotFoundError: No module named 'scripts.extractors.nota_al_pie'`

**Step 3: Implementar `scripts/extractors/nota_al_pie.py`**

```python
"""Extractor del metadato Nota al Pie (notas explicativas y referencias bibliográficas de pie de página)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class NotaAlPieExtractor(BaseExtractor):
    """Extractor de notas aclaratorias y referencias normativas al pie de página."""

    @property
    def nombre_bloque(self) -> str:
        return "nota_al_pie"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        notas: List[str] = []
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Detectar notas numeradas de pie de página (ej. "1 Artículo 38...", "2 La orientación técnica...")
            match_nota = re.match(r"^(\d+)\s+([A-ZÁÉÍÓÚÑa-záéíóúñ].+)$", line_clean)
            if match_nota:
                # Filtrar falsos positivos de pie de página institucional o numeración de numerales
                if not re.search(r"P[áa]gina\s+\d+", line_clean, re.IGNORECASE) and not line_clean.startswith("1. "):
                    num_nota = match_nota.group(1)
                    texto_nota = match_nota.group(2).strip()
                    # Asegurar que sea una nota al pie de página de referencia
                    if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley)\b", texto_nota, re.IGNORECASE):
                        notas.append(f"{num_nota} {texto_nota}")

        notas_texto = " | ".join(notas) if notas else ""
        exito = bool(notas_texto)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"notas_al_pie": notas_texto},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se identificaron notas al pie de página.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Nota al Pie Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
```

Actualizar `scripts/extractors/__init__.py` para importar `nota_al_pie`.

**Step 4: Ejecutar `pytest test/test_extractor_nota_al_pie.py -v`**

Run: `pytest test/test_extractor_nota_al_pie.py -v`  
Expected: PASS

**Step 5: Commit**

```bash
git add scripts/extractors/nota_al_pie.py scripts/extractors/__init__.py test/test_extractor_nota_al_pie.py
git commit -m "feat: implementar extractor modular NotaAlPieExtractor para notas al pie de página"
```

---

### Task 3: Integrar `notas_al_pie` en `DDUOrchestrator` y Exportadores CSV

**Files:**
- Modify: `scripts/ddu_orchestrator.py`
- Modify: `test/test_orchestrator.py`

**Step 1: Actualizar `DDUOrchestrator` en `scripts/ddu_orchestrator.py`**

Incluir el mapeo del bloque `nota_al_pie` / `notas_al_pie` en `export_individual_csv` y `export_master_csv` en el orden 10.

**Step 2: Ejecutar la suite completa de pruebas**

Run: `pytest -v`  
Expected: PASS (30/30 PASSED)

**Step 3: Re-exportar CSV para DDU 537**

Run: `py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 537.pdf" --export-csv`  
Expected: CSV exportado exitosamente en `salidas_csv/DDU_537_extraido.csv` con 12 filas.

**Step 4: Commit**

```bash
git add scripts/ddu_orchestrator.py test/test_orchestrator.py
git commit -m "feat: integrar notas_al_pie en DDUOrchestrator y exportadores CSV en el orden 10"
```
