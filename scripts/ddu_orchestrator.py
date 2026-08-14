"""Orquestador Central y Exportador CSV para Circulares DDU.

Este módulo define la clase DDUOrchestrator, encargada de coordinar la ejecución
de los 14 extractores modulares (ETLs independientes en scripts/extractors/),
consolidar el diccionario de datos estricto DatosCircularDDU, y exportar
archivos CSV estructurados (individuales o dataset acumulado).
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

_PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

import importlib

from scripts.ddu_types import DatosCircularDDU
from scripts.extractors import ExtractorRegistry, registrar_todos_los_extractores


class DDUOrchestrator:
    """Orquestador central para ejecutar ETLs modulares de circulares DDU y exportar a CSV."""

    def __init__(self) -> None:
        """Inicializa el orquestador."""
        pass

    def process_text(
        self,
        raw_text: str,
        filename: str = "",
        pdf_path: Optional[Path] = None,
    ) -> DatosCircularDDU:
        """Ejecuta dinámicamente los extractores registrados y consolida DatosCircularDDU.

        Args:
            raw_text: Texto plano completo extraído del documento.
            filename: Nombre del archivo PDF original (para deducir o validar el número DDU).
            pdf_path: Ruta opcional al archivo PDF para extractores que requieren análisis estructural.

        Returns:
            Estructura DatosCircularDDU consolidada.
        """
        registrar_todos_los_extractores()
        lines = [line.strip() for line in raw_text.splitlines()]

        # Determinar número desde el nombre de archivo si existe
        match_filename = re.search(r"\b(\d+)\b", filename)
        num_filename = match_filename.group(1) if match_filename else ""

        # Ejecutar todos los extractores modulares
        extractores_dict = ExtractorRegistry.get_all_extractors()
        datos_consolidados: Dict[str, Any] = {}

        for nombre_bloque, extractor_cls in extractores_dict.items():
            try:
                instancia = extractor_cls()
                if pdf_path is not None and nombre_bloque in ("tablas", "imagenes", "modificaciones_posteriores"):
                    resultado = instancia.extract(raw_text, lines, pdf_path=pdf_path)
                else:
                    resultado = instancia.extract(raw_text, lines)
                if resultado.datos:
                    if nombre_bloque == "modificaciones_posteriores":
                        datos_consolidados["modificaciones_posteriores"] = resultado.datos.get("texto", "")
                    datos_consolidados.update(resultado.datos)
            except Exception as e:
                print(f"Advertencia: Error al ejecutar extractor '{nombre_bloque}': {e}")

        # Consolidar número DDU (garantizando prefijo 'DDU ')
        numero = str(datos_consolidados.get("numero", "")).strip()
        if numero:
            if not numero.upper().startswith("DDU"):
                numero = f"DDU {numero}"
        elif num_filename:
            numero = f"DDU {num_filename}"
        datos_consolidados["numero"] = numero

        # Garantizar emisor por defecto si no se detectó
        if not datos_consolidados.get("emisor"):
            datos_consolidados["emisor"] = "JEFE DIVISION DE DESARROLLO URBANO"

        res_final: DatosCircularDDU = {
            "numero": str(datos_consolidados.get("numero", "")),
            "fecha": str(datos_consolidados.get("fecha", "")),
            "materia": str(datos_consolidados.get("materia", "")),
            "emisor": str(datos_consolidados.get("emisor", "")),
            "antecedentes": str(datos_consolidados.get("antecedentes", "")),
            "secciones": datos_consolidados.get("secciones", []),
            "referencias": str(datos_consolidados.get("referencias", "")),
            "elementos_visuales": str(datos_consolidados.get("elementos_visuales", "")),
            "numero_ord": str(datos_consolidados.get("numero_ord", "")),
            "descriptores": str(datos_consolidados.get("descriptores", "")),
            "cuerpo": str(datos_consolidados.get("cuerpo", "")),
            "fecha_lugar": str(datos_consolidados.get("fecha_lugar", "")),
            "lugar": str(datos_consolidados.get("lugar", "Santiago")),
            "destinatarios": str(datos_consolidados.get("destinatarios", "")),
            "firmante": str(datos_consolidados.get("firmante", "")),
            "lista_distribucion": datos_consolidados.get("lista_distribucion", []),
            "distribucion_texto": str(datos_consolidados.get("distribucion_texto", "")),
            "notas_al_pie": str(datos_consolidados.get("notas_al_pie", "")),
            "tablas": datos_consolidados.get("tablas", []),
            "imagenes": datos_consolidados.get("imagenes", []),
            "modificaciones_posteriores": str(datos_consolidados.get("modificaciones_posteriores", "")),
        }

        return res_final


    def process_pdf(self, pdf_path: Path) -> DatosCircularDDU:
        """Extrae el texto de un PDF y procesa la circular con el pipeline de ETLs.

        Args:
            pdf_path: Ruta al archivo PDF de la circular DDU.

        Returns:
            Estructura DatosCircularDDU consolidada.
        """
        if not pdf_path.exists():
            raise FileNotFoundError(f"No se encontró el archivo PDF: {pdf_path}")

        pypdf_mod: Any = importlib.import_module("pypdf")
        pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
        pdf_pages: Any = pdf_reader.pages
        text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
        raw_text: str = "\n".join(text_list)

        return self.process_text(raw_text, filename=pdf_path.name, pdf_path=pdf_path)

    def export_individual_csv(self, pdf_path: Path, output_dir: Path) -> Path:
        """Genera un archivo CSV individual estructurado para una circular DDU con los 14 bloques normativos.

        Args:
            pdf_path: Ruta al archivo PDF de entrada.
            output_dir: Directorio de salida para guardar el CSV.

        Returns:
            Ruta al archivo CSV generado.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        datos = self.process_pdf(pdf_path)

        ddu_num = datos["numero"].replace(" ", "_") or "desconocido"
        csv_filename = f"{ddu_num}_extraido.csv"
        csv_path = output_dir / csv_filename

        fecha_lugar_val = str(datos.get("fecha_lugar") or "").strip()
        if not fecha_lugar_val:
            lugar_str = str(datos.get("lugar", "Santiago")).strip()
            fecha_str = str(datos.get("fecha", "")).strip()
            fecha_lugar_val = f"{lugar_str}, {fecha_str}" if lugar_str and fecha_str else (fecha_str or lugar_str)

        tablas_list = datos.get("tablas") or []
        tablas_val = json.dumps(tablas_list, ensure_ascii=False) if tablas_list else ""

        imagenes_list = datos.get("imagenes") or []
        imagenes_val = json.dumps(imagenes_list, ensure_ascii=False) if imagenes_list else ""

        filas_csv: List[Dict[str, str]] = [
            {"bloque": "Encabezado", "campo": "numero_ddu", "valor_extraido": datos["numero"]},
            {"bloque": "Acto Administrativo", "campo": "numero_ord", "valor_extraido": datos.get("numero_ord", "")},
            {"bloque": "Antecedentes", "campo": "antecedentes", "valor_extraido": datos["antecedentes"]},
            {"bloque": "Materia", "campo": "materia", "valor_extraido": datos["materia"]},
            {"bloque": "Descriptores", "campo": "descriptores", "valor_extraido": datos.get("descriptores", "")},
            {"bloque": "Fecha y Lugar", "campo": "fecha_emision", "valor_extraido": fecha_lugar_val},
            {"bloque": "Destinatarios", "campo": "destinatarios", "valor_extraido": datos.get("destinatarios", "")},
            {"bloque": "Emisión", "campo": "emisor", "valor_extraido": datos["emisor"]},
            {"bloque": "Cuerpo", "campo": "cuerpo", "valor_extraido": str(datos.get("cuerpo") or "").strip()},
            {"bloque": "Tablas", "campo": "tablas", "valor_extraido": tablas_val},
            {"bloque": "Imágenes", "campo": "imagenes", "valor_extraido": imagenes_val},
            {"bloque": "Modificaciones Posteriores", "campo": "modificaciones_posteriores", "valor_extraido": str(datos.get("modificaciones_posteriores") or "").strip()},
            {"bloque": "Nota al Pie", "campo": "notas_al_pie", "valor_extraido": str(datos.get("notas_al_pie") or "").strip()},
            {"bloque": "Firma", "campo": "firmante", "valor_extraido": datos.get("firmante", "")},
            {"bloque": "Distribución", "campo": "lista_distribucion", "valor_extraido": str(datos.get("distribucion_texto") or "")},
        ]

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["bloque", "campo", "valor_extraido"],
                delimiter=";",
                quoting=csv.QUOTE_ALL,
                lineterminator="\r\n",
            )
            writer.writeheader()
            writer.writerows(filas_csv)

        return csv_path

    def export_master_csv(self, pdf_list: List[Path], output_path: Path) -> Path:
        """Procesa una lista de PDFs y genera un CSV maestro acumulado donde cada fila es una circular.

        Args:
            pdf_list: Lista de rutas a los PDFs a procesar.
            output_path: Ruta del archivo CSV consolidado a generar.

        Returns:
            Ruta al archivo CSV maestro generado.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        master_rows: List[Dict[str, str]] = []

        for pdf_path in pdf_list:
            try:
                datos = self.process_pdf(pdf_path)
                dist_val = str(datos.get("distribucion_texto") or "")
                cuerpo_resumen = str(datos.get("cuerpo") or "")

                master_rows.append({
                    "numero_ddu": datos["numero"],
                    "numero_ord": datos.get("numero_ord", ""),
                    "antecedentes": datos["antecedentes"],
                    "materia": datos["materia"],
                    "descriptores": datos.get("descriptores", ""),
                    "fecha_emision": datos["fecha"],
                    "lugar": datos.get("lugar", "Santiago"),
                    "destinatarios": datos.get("destinatarios", ""),
                    "emisor": datos["emisor"],
                    "cuerpo_resumen": cuerpo_resumen,
                    "modificaciones_posteriores": str(datos.get("modificaciones_posteriores") or ""),
                    "notas_al_pie": datos.get("notas_al_pie", ""),
                    "firmante": datos.get("firmante", ""),
                    "lista_distribucion": dist_val,
                })
            except Exception as e:
                print(f"Advertencia: Error al procesar PDF '{pdf_path}' para el CSV maestro: {e}")
                continue

        fieldnames = [
            "numero_ddu",
            "numero_ord",
            "antecedentes",
            "materia",
            "descriptores",
            "fecha_emision",
            "lugar",
            "destinatarios",
            "emisor",
            "cuerpo_resumen",
            "modificaciones_posteriores",
            "notas_al_pie",
            "firmante",
            "lista_distribucion",
        ]

        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:

            writer = csv.DictWriter(
                f,
                fieldnames=fieldnames,
                delimiter=";",
                quoting=csv.QUOTE_ALL,
                lineterminator="\r\n",
            )
            writer.writeheader()
            writer.writerows(master_rows)

        return output_path


def main() -> None:
    """Punto de entrada CLI para ejecutar el orquestador desde la línea de comandos."""
    parser = argparse.ArgumentParser(description="Orquestador DDU - Extracción y Exportación a CSV")
    parser.add_argument("--pdf", type=str, help="Ruta al archivo PDF a procesar")
    parser.add_argument("--output-dir", type=str, default="salidas_csv", help="Directorio de salida para los CSVs")
    parser.add_argument("--export-csv", action="store_true", help="Exportar CSV individual")
    args = parser.parse_args()

    if args.pdf:
        pdf_path = Path(args.pdf)
        orchestrator = DDUOrchestrator()
        if args.export_csv:
            csv_out = orchestrator.export_individual_csv(pdf_path, Path(args.output_dir))
            print(f"CSV exportado exitosamente en: {csv_out}")
        else:
            res = orchestrator.process_pdf(pdf_path)
            print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
