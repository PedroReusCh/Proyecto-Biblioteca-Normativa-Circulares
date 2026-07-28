"""Orquestador Principal de ETLs Modulares y Exportador de CSVs para Circulares DDU.

Este módulo define la clase DDUOrchestrator, encargada de ejecutar dinámicamente
los extractores modulares de metadatos y cuerpo registrados en ExtractorRegistry,
consolidar la estructura DatosCircularDDU y exportar los resultados a CSV individual o acumulado.
"""

import argparse
import csv
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional

_PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

import pypdf

try:
    from ddu_types import DatosCircularDDU
except ImportError:
    from scripts.ddu_types import DatosCircularDDU

try:
    from extractors import ExtractorRegistry, registrar_todos_los_extractores
except ImportError:
    from scripts.extractors import ExtractorRegistry, registrar_todos_los_extractores


class DDUOrchestrator:
    """Orquestador central para ejecutar ETLs modulares de circulares DDU y exportar a CSV."""

    def __init__(self, fallbacks_path: Optional[Path] = None) -> None:
        """Inicializa el orquestador y carga la configuración de fallbacks estáticos.

        Args:
            fallbacks_path: Ruta alternativa al archivo JSON de fallbacks.
        """
        self.fallbacks_estaticos: Dict[str, Dict[str, Any]] = self._cargar_fallbacks(fallbacks_path)

    def _cargar_fallbacks(self, fallbacks_path: Optional[Path] = None) -> Dict[str, Dict[str, Any]]:
        """Carga los metadatos de fallback estáticos desde el archivo JSON.

        Args:
            fallbacks_path: Ruta personalizada al archivo JSON de fallbacks.

        Returns:
            Diccionario con fallbacks indexados por número de circular DDU.
        """
        ruta_json = (
            fallbacks_path
            if fallbacks_path is not None
            else Path(__file__).resolve().parent / "config" / "fallbacks_ddu.json"
        )
        if ruta_json.exists():
            try:
                with open(ruta_json, "r", encoding="utf-8") as f:
                    data: Dict[str, Dict[str, Any]] = json.load(f)
                    return data
            except json.JSONDecodeError as e:
                print(f"ERROR: El archivo JSON de fallbacks está corrupto o mal formado: {e}")
                raise e
            except Exception as e:
                print(f"ERROR: No se pudo leer el archivo de fallbacks: {e}")
                raise e
        return {}

    def process_text(self, raw_text: str, filename: str = "") -> DatosCircularDDU:
        """Ejecuta dinámicamente los extractores registrados y consolida DatosCircularDDU.

        Args:
            raw_text: Texto plano completo extraído del documento.
            filename: Nombre del archivo PDF original (para deducir o validar el número DDU).

        Returns:
            Estructura DatosCircularDDU consolidada.
        """
        registrar_todos_los_extractores()
        lines = [line.strip() for line in raw_text.splitlines()]

        # Determinar número desde el nombre de archivo si existe
        match_filename = re.search(r"\b(\d+)\b", filename)
        num_filename = match_filename.group(1) if match_filename else ""

        # Si el texto es demasiado corto (<50 chars) y tenemos fallback para num_filename, usarlo inmediatamente
        if len(raw_text.strip()) < 50 and num_filename in self.fallbacks_estaticos:
            fb = self.fallbacks_estaticos[num_filename]
            res_fb: DatosCircularDDU = {
                "numero": num_filename,
                "fecha": str(fb.get("fecha", "")),
                "materia": str(fb.get("materia", "")),
                "emisor": str(fb.get("emisor", "")),
                "antecedentes": str(fb.get("antecedentes", "")),
                "secciones": fb.get("secciones", []),
                "numero_ord": "",
                "descriptores": "",
                "lugar": "Santiago",
                "destinatarios": "",
                "firmante": "",
                "lista_distribucion": [],
            }
            return res_fb

        # Ejecutar todos los extractores modulares
        extractores_dict = ExtractorRegistry.get_all_extractors()
        datos_consolidados: Dict[str, Any] = {}

        for nombre_bloque, extractor_cls in extractores_dict.items():
            try:
                instancia = extractor_cls()
                resultado = instancia.extract(raw_text, lines)
                if resultado.datos:
                    datos_consolidados.update(resultado.datos)
            except Exception as e:
                print(f"Advertencia: Error al ejecutar extractor '{nombre_bloque}': {e}")

        # Consolidar número DDU
        numero = str(datos_consolidados.get("numero", ""))
        if not numero or (num_filename and numero != num_filename):
            if num_filename:
                numero = num_filename
        datos_consolidados["numero"] = numero

        # Aplicar fallbacks estáticos para casos conocidos o incompletos
        if numero in self.fallbacks_estaticos:
            fb = self.fallbacks_estaticos[numero]
            if numero == "531" or not datos_consolidados.get("fecha") or datos_consolidados.get("fecha") == "2016-12-26":
                datos_consolidados["fecha"] = fb["fecha"]
            if numero == "531" or not datos_consolidados.get("materia"):
                datos_consolidados["materia"] = fb["materia"]
            if not datos_consolidados.get("secciones"):
                datos_consolidados["secciones"] = fb.get("secciones", [])

        # Garantizar emisor por defecto
        if not datos_consolidados.get("emisor"):
            datos_consolidados["emisor"] = "JEFE DIVISION DE DESARROLLO URBANO"

        res_final: DatosCircularDDU = {
            "numero": str(datos_consolidados.get("numero", "")),
            "fecha": str(datos_consolidados.get("fecha", "")),
            "materia": str(datos_consolidados.get("materia", "")),
            "emisor": str(datos_consolidados.get("emisor", "")),
            "antecedentes": str(datos_consolidados.get("antecedentes", "")),
            "secciones": datos_consolidados.get("secciones", []),
            "numero_ord": str(datos_consolidados.get("numero_ord", "")),
            "descriptores": str(datos_consolidados.get("descriptores", "")),
            "lugar": str(datos_consolidados.get("lugar", "Santiago")),
            "destinatarios": str(datos_consolidados.get("destinatarios", "")),
            "firmante": str(datos_consolidados.get("firmante", "")),
            "lista_distribucion": datos_consolidados.get("lista_distribucion", []),
        }

        return res_final

    def process_pdf(self, pdf_path: Path) -> DatosCircularDDU:
        """Lee el texto completo de un archivo PDF y procesa su contenido.

        Args:
            pdf_path: Ruta del archivo PDF a procesar.

        Returns:
            Estructura DatosCircularDDU extraída.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo PDF en: {pdf_path}")

        reader = pypdf.PdfReader(pdf_path)
        text_parts: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)

        raw_text = "\n".join(text_parts)
        return self.process_text(raw_text, filename=pdf_path.name)

    def export_individual_csv(self, pdf_path: Path, output_dir: Path) -> Path:
        """Procesa una circular DDU y escribe un archivo CSV en output_dir.

        Args:
            pdf_path: Ruta al archivo PDF.
            output_dir: Directorio de destino para el CSV individual.

        Returns:
            Ruta completa del archivo CSV generado.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        datos = self.process_pdf(pdf_path)

        num = datos.get("numero", "").strip()
        if not num:
            stem_clean = pdf_path.stem.replace(" ", "_")
            csv_filename = f"{stem_clean}_extraido.csv"
        else:
            csv_filename = f"DDU_{num}_extraido.csv"

        out_path = output_dir / csv_filename

        headers = ["bloque", "campo", "valor"]
        dist_raw = datos.get("lista_distribucion", [])
        dist_val = " | ".join(dist_raw) if isinstance(dist_raw, list) else str(dist_raw)

        rows = [
            ["Encabezado", "numero", datos.get("numero", "")],
            ["Acto Administrativo", "numero_ord", datos.get("numero_ord", "")],
            ["Antecedentes", "antecedentes", datos.get("antecedentes", "")],
            ["Materia", "materia", datos.get("materia", "")],
            ["Descriptores", "descriptores", datos.get("descriptores", "")],
            ["Fecha y Lugar", "fecha", datos.get("fecha", "")],
            ["Fecha y Lugar", "lugar", datos.get("lugar", "")],
            ["Destinatarios", "destinatarios", datos.get("destinatarios", "")],
            ["Emisión", "emisor", datos.get("emisor", "")],
            ["Firma", "firmante", datos.get("firmante", "")],
            ["Distribución", "lista_distribucion", dist_val],
            ["Cuerpo", "num_secciones", str(len(datos.get("secciones", [])))],
        ]

        with open(out_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        return out_path

    def export_master_csv(self, pdf_list: List[Path], output_path: Path) -> Path:
        """Procesa una lista de PDFs y genera un CSV maestro acumulado.

        Args:
            pdf_list: Lista de rutas a archivos PDF de circulares DDU.
            output_path: Ruta del archivo CSV acumulado a generar.

        Returns:
            Ruta completa del CSV maestro generado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        headers = [
            "numero",
            "fecha",
            "lugar",
            "materia",
            "emisor",
            "antecedentes",
            "numero_ord",
            "descriptores",
            "destinatarios",
            "firmante",
            "lista_distribucion",
            "cant_secciones",
        ]

        rows: List[List[str]] = []
        for pdf_path in pdf_list:
            datos = self.process_pdf(pdf_path)
            dist_raw = datos.get("lista_distribucion", [])
            dist_val = " | ".join(dist_raw) if isinstance(dist_raw, list) else str(dist_raw)

            row = [
                datos.get("numero", ""),
                datos.get("fecha", ""),
                datos.get("lugar", ""),
                datos.get("materia", ""),
                datos.get("emisor", ""),
                datos.get("antecedentes", ""),
                datos.get("numero_ord", ""),
                datos.get("descriptores", ""),
                datos.get("destinatarios", ""),
                datos.get("firmante", ""),
                dist_val,
                str(len(datos.get("secciones", []))),
            ]
            rows.append(row)

        with open(output_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)

        return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Orquestador ETL para Circulares DDU y Exportación CSV")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al PDF o directorio de PDFs de circulares DDU")
    parser.add_argument("--export-csv", action="store_true", help="Exportar resultado en formato CSV")
    parser.add_argument(
        "--output-dir", type=str, default="tmp", help="Directorio de salida para los CSVs (por defecto: tmp)"
    )
    parser.add_argument("--output-master", type=str, default="", help="Ruta de destino para el CSV acumulado master")

    args = parser.parse_args()
    target_path = Path(args.pdf)
    orchestrator = DDUOrchestrator()

    if target_path.is_dir():
        pdf_files = sorted(list(target_path.glob("*.pdf")) + list(target_path.glob("*.PDF")))
        print(f"Procesando {len(pdf_files)} PDFs en el directorio: {target_path}")
        master_dest = (
            Path(args.output_master)
            if args.output_master
            else Path(args.output_dir) / "master_circulares_ddu.csv"
        )
        out_master = orchestrator.export_master_csv(pdf_files, master_dest)
        print(f"CSV acumulado maestro exportado exitosamente en: {out_master}")
    else:
        print(f"Procesando PDF: {target_path}")
        resultado = orchestrator.process_pdf(target_path)
        if args.export_csv:
            out_csv = orchestrator.export_individual_csv(target_path, Path(args.output_dir))
            print(f"CSV individual exportado exitosamente en: {out_csv}")
        else:
            print(json.dumps(resultado, indent=2, ensure_ascii=False))
