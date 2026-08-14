"""Transformador Independiente de CSVs de Circulares DDU a Grafos Semánticos RDF/Turtle.

Este módulo toma archivos CSV generados a partir de circulares DDU (individuales
o datasets) y los transforma a grafos semánticos RDF en sintaxis Turtle (.ttl).
"""

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
        """Inicializa el transformador RDF."""
        self.rdf_builder: DDUToRDF = DDUToRDF()

    def read_csv(self, csv_path: Path) -> DatosCircularDDU:
        """Lee un CSV de circular DDU y reconstruye la estructura DatosCircularDDU.

        Args:
            csv_path: Ruta al archivo CSV individual de la circular.

        Returns:
            Estructura DatosCircularDDU reconstruida desde los valores del CSV.
        """
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
            "modificaciones_posteriores": raw_data.get("modificaciones_posteriores", ""),
        }
        return datos


    def transform(self, csv_path: Path, output_rdf_path: Path) -> Path:
        """Transforma un archivo CSV individual a un grafo RDF Turtle (.ttl).

        Args:
            csv_path: Ruta al archivo CSV de entrada.
            output_rdf_path: Ruta del archivo RDF (.ttl) resultante.

        Returns:
            Ruta al archivo RDF generado.
        """
        output_rdf_path.parent.mkdir(parents=True, exist_ok=True)
        datos = self.read_csv(csv_path)
        rdf_content = self.rdf_builder.generar_rdf(datos)
        output_rdf_path.write_text(rdf_content, encoding="utf-8")
        return output_rdf_path

    def transform_dir(self, csv_dir: Path, output_dir: Path) -> List[Path]:
        """Transforma todos los archivos CSV de un directorio a grafos RDF (.ttl).

        Args:
            csv_dir: Directorio con archivos CSV de entrada.
            output_dir: Directorio de salida para los archivos RDF (.ttl).

        Returns:
            Lista con las rutas a los archivos RDF generados.
        """
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
    """Punto de entrada CLI para la conversión independiente de CSV a RDF Turtle."""
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
