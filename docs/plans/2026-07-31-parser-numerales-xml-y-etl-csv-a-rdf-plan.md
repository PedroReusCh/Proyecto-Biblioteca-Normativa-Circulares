# Plan de Implementación: Segmentación de Numerales XML (`csv_to_akoma_xml.py`) y ETL Independiente CSV ➔ RDF (`csv_to_rdf.py`)

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:**
1. Mejorar `CSVToAkomaXML.read_csv()` en `scripts/csv_to_akoma_xml.py` para parsear el campo `cuerpo` del CSV en numerales (`<num>`) y secciones (`<heading>`) independientes.
2. Implementar el módulo ETL independiente `scripts/csv_to_rdf.py` para transformar CSVs de circulares DDU a grafos semánticos RDF Turtle (`.ttl`) en `salidas_rdf/`.

**Architecture:**
- `scripts/csv_to_akoma_xml.py`: incorporar helper `_parsear_cuerpo_a_secciones(cuerpo_str: str) -> List[SeccionDDU]`.
- `scripts/csv_to_rdf.py`: crear la clase `CSVToRDF` con lectura de CSV y delegación a `DDUToRDF`.
- `test/test_csv_to_akoma_xml.py`: extender para validar numerales `<num>`.
- `test/test_csv_to_rdf.py`: crear prueba unitaria de transformación a RDF desde CSV.

**Tech Stack:** Python 3.13, pytest, git.

---

### Task 1: Segmentación de Numerales y Secciones en `scripts/csv_to_akoma_xml.py`

**Files:**
- Modify: `scripts/csv_to_akoma_xml.py`
- Modify: `test/test_csv_to_akoma_xml.py`

**Step 1: Escribir la prueba para verificar `<num>` en `test/test_csv_to_akoma_xml.py`**

Añadir en `test/test_csv_to_akoma_xml.py`:
```python
def test_csv_to_akoma_xml_numeral_segmentation(tmp_path: Path) -> None:
    """Verifica que la transformación desde CSV extraiga numerales <num> e identificadores <paragraph>."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    out_xml = tmp_path / "DDU_531_num_test.xml"

    converter = CSVToAkomaXML()
    result_path = converter.transform(csv_input, out_xml)

    content = result_path.read_text(encoding="utf-8")
    assert "<num>1.</num>" in content or "<num>1</num>" in content
    assert "<paragraph id=" in content
```

**Step 2: Implementar helper `_parsear_cuerpo_a_secciones` en `scripts/csv_to_akoma_xml.py`**

En `scripts/csv_to_akoma_xml.py`:
```python
    def _parsear_cuerpo_a_secciones(self, cuerpo_str: str) -> List[SeccionDDU]:
        """Divide el texto corrido del cuerpo en secciones y párrafos con numerales."""
        if not cuerpo_str.strip():
            return []

        # Detectar divisor de secciones romanas (ej: "| II. NORMATIVA APLICABLE:" o "II. NORMATIVA APLICABLE:")
        bloques_sec = re.split(r'(?:\||\n|^)\s*(?=[I|V|X]+\.\s+[A-ZÁÉÍÓÚÑ\s]+:)', cuerpo_str)
        secciones: List[SeccionDDU] = []

        for b in bloques_sec:
            b_clean = b.strip()
            if not b_clean:
                continue

            titulo_sec = ""
            m_sec = re.match(r'^([I|V|X]+\.\s+[A-ZÁÉÍÓÚÑ\s]+:)', b_clean)
            if m_sec:
                titulo_sec = m_sec.group(1).strip()
                b_clean = b_clean[m_sec.end():].strip()

            # Dividir párrafos por renglones o numerales (ej. "1. ", "2. ")
            parrafos = [p.strip() for p in re.split(r'\n+|(?=\b\d+\.\s+)', b_clean) if p.strip()]
            if not parrafos and b_clean:
                parrafos = [b_clean]

            secciones.append({
                "titulo": titulo_sec,
                "parrafos": parrafos
            })

        return secciones if secciones else [{"titulo": "", "parrafos": [cuerpo_str]}]
```

**Step 3: Probar con `pytest test/test_csv_to_akoma_xml.py -v`**

Run: `pytest test/test_csv_to_akoma_xml.py -v`  
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/csv_to_akoma_xml.py test/test_csv_to_akoma_xml.py
git commit -m "feat: implementar segmentacion automatica de numerales y secciones en csv_to_akoma_xml.py"
```

---

### Task 2: Implementar el Módulo ETL Independiente `scripts/csv_to_rdf.py`

**Files:**
- Create: `scripts/csv_to_rdf.py`
- Create: `test/test_csv_to_rdf.py`

**Step 1: Crear `test/test_csv_to_rdf.py`**

```python
"""Pruebas unitarias para el transformador independiente CSV a RDF Turtle."""

from pathlib import Path
from scripts.csv_to_rdf import CSVToRDF


def test_csv_to_rdf_transformation(tmp_path: Path) -> None:
    """Verifica la transformación de un archivo CSV a un grafo semántico RDF/Turtle."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    assert csv_input.exists(), "El CSV de prueba DDU_531_extraido.csv debe existir"

    out_ttl = tmp_path / "DDU_531_rdf.ttl"
    converter = CSVToRDF()
    result_path = converter.transform(csv_input, out_ttl)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "@prefix bcn-norms:" in content
    assert "@prefix minvu-ddu:" in content
    assert 'bcn-norms:hasNumber "DDU 531"' in content or 'bcn-norms:hasNumber "531"' in content
```

**Step 2: Implementar `scripts/csv_to_rdf.py`**

```python
"""Transformador Independiente de CSVs de Circulares DDU a Grafos Semánticos RDF/Turtle."""

import argparse
import csv
from pathlib import Path
import sys
from typing import Dict, List

_PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

try:
    from ddu_types import DatosCircularDDU, SeccionDDU
except ImportError:
    from scripts.ddu_types import DatosCircularDDU, SeccionDDU

try:
    from ddu_to_rdf import DDUToRDF
except ImportError:
    from scripts.ddu_to_rdf import DDUToRDF


class CSVToRDF:
    """Transformador independiente de archivos CSV de circulares a grafos RDF Turtle (.ttl)."""

    def __init__(self) -> None:
        self.rdf_builder: DDUToRDF = DDUToRDF()

    def read_csv(self, csv_path: Path) -> DatosCircularDDU:
        raw_data: Dict[str, str] = {}
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                campo = str(row.get("campo", "")).strip()
                valor = str(row.get("valor_extraido", "")).strip()
                if campo:
                    raw_data[campo] = valor

        cuerpo_str = raw_data.get("cuerpo", "")
        secciones: List[SeccionDDU] = [{"titulo": "", "parrafos": [cuerpo_str]}] if cuerpo_str else []

        fecha_lugar_val = raw_data.get("fecha_emision", "")
        fecha_val = ""
        lugar_val = "Santiago"
        if "," in fecha_lugar_val:
            partes = fecha_lugar_val.split(",", 1)
            lugar_val = partes[0].strip()
            fecha_val = partes[1].strip()
        else:
            fecha_val = fecha_lugar_val

        dist_texto = raw_data.get("lista_distribucion", "").strip()

        datos: DatosCircularDDU = {
            "numero": raw_data.get("numero_ddu", ""),
            "fecha": fecha_val,
            "materia": raw_data.get("materia", ""),
            "emisor": raw_data.get("emisor", ""),
            "antecedentes": raw_data.get("antecedentes", ""),
            "secciones": secciones,
            "referencias": "",
            "elementos_visuales": "",
            "numero_ord": raw_data.get("numero_ord", ""),
            "descriptores": raw_data.get("descriptores", ""),
            "cuerpo": cuerpo_str,
            "fecha_lugar": fecha_lugar_val,
            "lugar": lugar_val,
            "destinatarios": raw_data.get("destinatarios", ""),
            "firmante": raw_data.get("firmante", ""),
            "lista_distribucion": [d.strip() for d in dist_texto.split(";") if d.strip()],
            "distribucion_texto": dist_texto,
            "notas_al_pie": raw_data.get("notas_al_pie", ""),
        }
        return datos

    def transform(self, csv_path: Path, output_rdf_path: Path) -> Path:
        output_rdf_path.parent.mkdir(parents=True, exist_ok=True)
        datos = self.read_csv(csv_path)
        rdf_content = self.rdf_builder.generar_rdf(datos)
        output_rdf_path.write_text(rdf_content, encoding="utf-8")
        return output_rdf_path

    def transform_dir(self, csv_dir: Path, output_dir: Path) -> List[Path]:
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: List[Path] = []
        for csv_file in csv_dir.glob("*.csv"):
            stem_clean = csv_file.stem.replace("_extraido", "")
            out_filename = f"{stem_clean}_rdf.ttl"
            out_path = output_dir / out_filename
            self.transform(csv_file, out_path)
            generated.append(out_path)
        return generated


def main() -> None:
    parser = argparse.ArgumentParser(description="Transformador Independiente CSV a RDF Turtle (.ttl)")
    parser.add_argument("--csv", type=str, help="Ruta al archivo CSV individual de una circular")
    parser.add_argument("--output", type=str, help="Ruta de salida para el archivo RDF (.ttl)")
    parser.add_argument("--csv-dir", type=str, help="Directorio origen con archivos CSV")
    parser.add_argument("--output-dir", type=str, default="salidas_rdf", help="Directorio destino para los archivos RDF")
    args = parser.parse_args()

    converter = CSVToRDF()

    if args.csv:
        csv_path = Path(args.csv)
        out_path = Path(args.output) if args.output else Path(args.output_dir) / f"{csv_path.stem.replace('_extraido', '')}_rdf.ttl"
        res = converter.transform(csv_path, out_path)
        print(f"Grafo RDF generado exitosamente en: {res}")
    elif args.csv_dir:
        generated = converter.transform_dir(Path(args.csv_dir), Path(args.output_dir))
        print(f"Se generaron {len(generated)} grafos RDF en: {args.output_dir}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
```

**Step 3: Probar con `pytest test/test_csv_to_rdf.py -v`**

Run: `pytest test/test_csv_to_rdf.py -v`  
Expected: PASS

**Step 4: Commit**

```bash
git add scripts/csv_to_rdf.py test/test_csv_to_rdf.py
git commit -m "feat: implementar transformador independiente CSV a RDF Turtle (csv_to_rdf.py)"
```

---

### Task 3: Generación en Lote, Verificación Completa y Documentación

**Files:**
- Modify: `salidas_xml/` (Regeneración con numerales)
- Create: `salidas_rdf/` (Generación de grafos .ttl para DDU 531, 533, 537 y 546)
- Modify: `README.md` & `CHANGELOG.md`
- Test: Suite completa `pytest -v`

**Step 1: Ejecutar regeneración de XMLs y generación de grafos RDF**

Run: `py -3 scripts/csv_to_akoma_xml.py --csv-dir "salidas_csv" --output-dir "salidas_xml"`  
Run: `py -3 scripts/csv_to_rdf.py --csv-dir "salidas_csv" --output-dir "salidas_rdf"`

**Step 2: Ejecutar suite de pruebas `pytest -v`**

Run: `pytest -v`  
Expected: PASS (43+ PASSED)

**Step 3: Actualizar README.md, CHANGELOG.md y commit final**

```bash
git add README.md CHANGELOG.md
git commit -m "docs: registrar la implementacion de la segmentacion de numerales XML y el ETL independiente CSV a RDF"
git push origin master
```
