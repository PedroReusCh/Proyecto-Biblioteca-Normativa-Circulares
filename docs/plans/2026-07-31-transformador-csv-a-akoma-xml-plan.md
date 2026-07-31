# Plan de Implementación: Transformador Independiente CSV ➔ Akoma Ntoso XML (`csv_to_akoma_xml.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar un proceso independiente `scripts/csv_to_akoma_xml.py` que tome cualquier CSV de circular DDU y lo transforme a un documento XML Akoma Ntoso v2.0 BCN conforme según la matriz de homologación.

**Architecture:** Crear `CSVToAkomaXML` en `scripts/csv_to_akoma_xml.py` para leer CSVs (individuales o por directorio), mapear campos a la estructura de datos DDU y generar archivos XML en `salidas_xml/` usando `DDUToXML`.

**Tech Stack:** Python 3.13, pytest, xml.etree, csv, git.

---

### Task 1: Crear la Prueba Unitaria en `test/test_csv_to_akoma_xml.py`

**Files:**
- Create: `test/test_csv_to_akoma_xml.py`

**Step 1: Escribir la prueba unitaria para `CSVToAkomaXML`**

En `test/test_csv_to_akoma_xml.py`:
```python
from pathlib import Path
import pytest
from scripts.csv_to_akoma_xml import CSVToAkomaXML


def test_csv_to_akoma_xml_transformation(tmp_path: Path) -> None:
    """Verifica la transformación de un archivo CSV a XML Akoma Ntoso BCN."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    assert csv_input.exists(), "El CSV de prueba DDU_531_extraido.csv debe existir"

    out_xml = tmp_path / "DDU_531_akoma.xml"
    converter = CSVToAkomaXML()
    result_path = converter.transform(csv_input, out_xml)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "<akomaNtoso" in content
    assert "<doc name=\"circular\">" in content
    assert "FRBRnumber value=\"531\"" in content
    assert "Santiago, 2026-02-17" in content or "2026-02-17" in content
```

**Step 2: Verificar que el test falla**

Run: `pytest test/test_csv_to_akoma_xml.py -v`  
Expected: FAIL con `ModuleNotFoundError: No module named 'scripts.csv_to_akoma_xml'`

**Step 3: Commit de la prueba**

```bash
git add test/test_csv_to_akoma_xml.py
git commit -m "test: agregar prueba unitaria para transformador independiente CSV a Akoma Ntoso XML"
```

---

### Task 2: Implementar el Módulo `scripts/csv_to_akoma_xml.py`

**Files:**
- Create: `scripts/csv_to_akoma_xml.py`
- Test: `test/test_csv_to_akoma_xml.py`

**Step 1: Crear `scripts/csv_to_akoma_xml.py` con tipado estricto y CLI**

```python
"""Transformador Independiente de CSVs de Circulares DDU a Akoma Ntoso XML."""

import argparse
import csv

import importlib

from pathlib import Path

from typing import Any, Dict, List


from scripts.ddu_to_xml import DDUToXML

from scripts.ddu_types import DatosCircularDDU, SeccionDDU


class CSVToAkomaXML:

    """Transformador independiente de archivos CSV de circulares a XML Akoma Ntso v2.0 BCN."""


    def __init__(self) -> None:

        self.xml_builder: DDUToXML = DDUToXML()


    def read_csv(self, csv_path: Path) -> DatosCircularDDU:

        """Lee un CSV de circular DDU y reconstruye el diccionario DatosCircularDDU."""

        raw_data: Dict[str, str] = {}

        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:

            reader = csv.DictReader(f, delimiter=";")

            for row in reader:

                campo = str(row.get("campo", "")).strip()

                valor = str(row.get("valor_extraido", "")).strip()

                if campo:

                    raw_data[campo] = valor


        # Reconstruir secciones del cuerpo

        cuerpo_str = raw_data.get("cuerpo", "")

        secciones: List[SeccionDDU] = []

        if cuerpo_str:

            secciones.append({"titulo": "", "parrafos": [cuerpo_str]})


        datos: DatosCircularDDU = {

            "numero": raw_data.get("numero_ddu", ""),

            "fecha": raw_data.get("fecha_emision", ""),

            "materia": raw_data.get("materia", ""),

            "emisor": raw_data.get("emisor", ""),

            "antecedentes": raw_data.get("antecedentes", ""),

            "secciones": secciones,

            "referencias": "",

            "elementos_visuales": "",

            "numero_ord": raw_data.get("numero_ord", ""),

            "descriptores": raw_data.get("descriptores", ""),

            "cuerpo": cuerpo_str,

            "fecha_lugar": raw_data.get("fecha_emision", ""),

            "lugar": "Santiago",

            "destinatarios": raw_data.get("destinatarios", ""),

            "firmante": raw_data.get("firmante", ""),

            "lista_distribucion": [],

            "distribucion_texto": raw_data.get("lista_distribucion", ""),

            "notas_al_pie": raw_data.get("notas_al_pie", ""),

        }

        return datos


    def transform(self, csv_path: Path, output_xml_path: Path) -> Path:

        """Transforma un archivo CSV individual a un archivo XML Akoma Ntso."""

        output_xml_path.parent.mkdir(parents=True, exist_ok=True)

        datos = self.read_csv(csv_path)

        xml_content = self.xml_builder.build_xml(datos)

        output_xml_path.write_text(xml_content, encoding="utf-8")

        return output_xml_path


    def transform_dir(self, csv_dir: Path, output_dir: Path) -> List[Path]:

        """Transforma todos los CSVs de un directorio a XMLs Akoma Ntso."""

        output_dir.mkdir(parents=True, exist_ok=True)

        generated: List[Path] = []

        for csv_file in csv_dir.glob("*.csv"):

            out_filename = csv_file.stem.replace("_extraido", "") + "_akoma.xml"

            out_path = output_dir / out_filename

            self.transform(csv_file, out_path)

            generated.append(out_path)

        return generated


def main() -> None:

    """Punto de entrada CLI para ejecutar la conversión CSV -> Akoma Ntso XML."""

    parser = argparse.ArgumentParser(description="Transformador CSV a Akoma Ntso XML")

    parser.add_argument("--csv", type=str, help="Ruta al archivo CSV individual")

    parser.add_argument("--output", type=str, help="Ruta de salida para el archivo XML")

    parser.add_argument("--csv-dir", type=str, help="Directorio con archivos CSV")

    parser.add_argument("--output-dir", type=str, default="salidas_xml", help="Directorio de salida para XMLs")

    args = parser.parse_args()


    converter = CSVToAkomaXML()

    if args.csv:

        out_path = Path(args.output) if args.output else Path(args.output_dir) / (Path(args.csv).stem + "_akoma.xml")

        res = converter.transform(Path(args.csv), out_path)

        print(f"XML Akoma Ntso generado exitosamente en: {res}")

    elif args.csv_dir:

        generated = converter.transform_dir(Path(args.csv_dir), Path(args.output_dir))

        print(f"Se generaron {len(generated)} archivos XML en: {args.output_dir}")

    else:

        parser.print_help()


if __name__ == "__main__":

    main()

```

**Step 2: Ejecutar `pytest test/test_csv_to_akoma_xml.py -v`**

Run: `pytest test/test_csv_to_akoma_xml.py -v`  
Expected: PASS

**Step 3: Commit**

```bash
git add scripts/csv_to_akoma_xml.py
git commit -m "feat: implementar transformador independiente CSV a Akoma Ntoso XML (csv_to_akoma_xml.py)"
```

---

### Task 3: Ejecución en Lote, Verificación Completa y Documentación

**Files:**
- Modify: `salidas_xml/` (Generación de XMLs para DDU 531, 533, 537 y 546)
- Test: Suite completa `pytest -v`

**Step 1: Generar todos los XMLs desde `salidas_csv/` a `salidas_xml/`**

Run: `py -3 scripts/csv_to_akoma_xml.py --csv-dir "salidas_csv" --output-dir "salidas_xml"`  
Expected: Generación de `DDU_531_extraido_akoma.xml`, `DDU_533_extraido_akoma.xml`, `DDU_537_extraido_akoma.xml` y `DDU_546_extraido_akoma.xml` en `salidas_xml/`.

**Step 2: Ejecutar la suite de pruebas automatizadas `pytest -v`**

Run: `pytest -v`  
Expected: PASS (41/41 PASSED)

**Step 3: Commit final**

```bash
git add test/test_csv_to_akoma_xml.py scripts/csv_to_akoma_xml.py
git commit -m "feat: certificar la transformacion independiente CSV a Akoma Ntoso XML"
```
