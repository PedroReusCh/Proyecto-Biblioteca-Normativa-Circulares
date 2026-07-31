"""Transformador Independiente de CSVs de Circulares DDU a Akoma Ntoso XML.

Este módulo toma archivos CSV generados a partir de circulares DDU (individuales
o datasets) y los transforma al estándar XML Akoma Ntoso v2.0 BCN aplicando
la matriz de homologación.
"""

import argparse
import csv
from pathlib import Path
import re
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
    from ddu_to_xml import DDUToXML
except ImportError:
    from scripts.ddu_to_xml import DDUToXML


class CSVToAkomaXML:
    """Transformador independiente de archivos CSV de circulares a XML Akoma Ntoso v2.0 BCN."""

    def __init__(self) -> None:
        """Inicializa el transformador."""
        self.xml_builder: DDUToXML = DDUToXML()

    def _parsear_cuerpo_a_secciones(self, cuerpo_str: str) -> List[SeccionDDU]:

        """Divide el texto corrido del cuerpo en secciones y párrafos con numerales."""
        if not cuerpo_str.strip():
            return []

        # Detectar divisor de secciones romanas (ej: "| II. NORMATIVA APLICABLE:" o "III. INSTRUCCIÓN COMPLEMENTARIA...")
        bloques_sec = re.split(r'(?:\||\n|^)\s*(?=[IVX]+\.\s+[A-ZÁÉÍÓÚÑ\s\d]+\s*:)', cuerpo_str)
        secciones: List[SeccionDDU] = []

        for b in bloques_sec:
            b_clean = b.strip()
            if not b_clean:
                continue

            titulo_sec = ""
            m_sec = re.match(r'^([IVX]+\.\s+[A-ZÁÉÍÓÚÑ\s\d]+\s*:)', b_clean)
            if m_sec:
                titulo_sec = m_sec.group(1).strip()
                b_clean = b_clean[m_sec.end():].strip()

            # Dividir párrafos por renglones o numerales que inician oración/párrafo (ej. "1. ", "3. ", "6. ")
            parrafos = [p.strip() for p in re.split(r'\n+|(?:(?<=\.\s)|(?<=:\s)|(?<=\)\s)|(?<=^)|(?<=\|\s))(?=(?<!N[º°]\s)(?<!\d\.)\b\d{1,2}\.\s+[A-ZÁÉÍÓÚÑa-z])', b_clean) if p.strip()]






            if not parrafos and b_clean:
                parrafos = [b_clean]

            secciones.append({
                "titulo": titulo_sec,
                "parrafos": parrafos
            })

        return secciones if secciones else [{"titulo": "", "parrafos": [cuerpo_str]}]

    def read_csv(self, csv_path: Path) -> DatosCircularDDU:
        """Lee un CSV de circular DDU y reconstruye el diccionario DatosCircularDDU.


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

        # Extraer campos de la matriz de homologación
        cuerpo_str = raw_data.get("cuerpo", "")
        secciones: List[SeccionDDU] = self._parsear_cuerpo_a_secciones(cuerpo_str)


        fecha_lugar_val = raw_data.get("fecha_emision", "")
        fecha_val = ""
        lugar_val = "Santiago"
        if "," in fecha_lugar_val:
            partes = fecha_lugar_val.split(",", 1)
            lugar_val = partes[0].strip()
            fecha_val = partes[1].strip()
        else:
            fecha_val = fecha_lugar_val

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
            "lista_distribucion": [d.strip() for d in raw_data.get("lista_distribucion", "").split(";") if d.strip()],
            "distribucion_texto": raw_data.get("lista_distribucion", ""),
            "notas_al_pie": raw_data.get("notas_al_pie", ""),
        }

        return datos

    def transform(self, csv_path: Path, output_xml_path: Path) -> Path:
        """Transforma un archivo CSV individual a un archivo XML Akoma Ntoso.

        Args:
            csv_path: Ruta al archivo CSV de entrada.
            output_xml_path: Ruta del archivo XML resultante.

        Returns:
            Ruta al archivo XML generado.
        """
        output_xml_path.parent.mkdir(parents=True, exist_ok=True)
        datos = self.read_csv(csv_path)
        xml_content = self.xml_builder.generar_xml(datos)
        output_xml_path.write_text(xml_content, encoding="utf-8")
        return output_xml_path

    def transform_dir(self, csv_dir: Path, output_dir: Path) -> List[Path]:
        """Transforma todos los archivos CSV de un directorio a XMLs Akoma Ntoso.

        Args:
            csv_dir: Directorio origen con archivos CSV.
            output_dir: Directorio destino para los archivos XML.

        Returns:
            Lista de rutas de archivos XML generados.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        generated: List[Path] = []
        for csv_file in csv_dir.glob("*.csv"):
            stem_clean = csv_file.stem.replace("_extraido", "")
            out_filename = f"{stem_clean}_akoma.xml"
            out_path = output_dir / out_filename
            self.transform(csv_file, out_path)
            generated.append(out_path)
        return generated


def main() -> None:
    """Punto de entrada CLI para ejecutar la conversión independiente CSV -> Akoma Ntoso XML."""
    parser = argparse.ArgumentParser(description="Transformador Independiente CSV a Akoma Ntoso XML")
    parser.add_argument("--csv", type=str, help="Ruta al archivo CSV individual de una circular")
    parser.add_argument("--output", type=str, help="Ruta de salida para el archivo XML Akoma Ntoso")
    parser.add_argument("--csv-dir", type=str, help="Directorio origen con archivos CSV de circulares")
    parser.add_argument("--output-dir", type=str, default="salidas_xml", help="Directorio destino para los XMLs")
    args = parser.parse_args()

    converter = CSVToAkomaXML()

    if args.csv:
        csv_path = Path(args.csv)
        out_path = Path(args.output) if args.output else Path(args.output_dir) / f"{csv_path.stem.replace('_extraido', '')}_akoma.xml"
        res = converter.transform(csv_path, out_path)
        print(f"XML Akoma Ntoso generado exitosamente en: {res}")
    elif args.csv_dir:
        generated = converter.transform_dir(Path(args.csv_dir), Path(args.output_dir))
        print(f"Se generaron {len(generated)} archivos XML Akoma Ntoso en: {args.output_dir}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
