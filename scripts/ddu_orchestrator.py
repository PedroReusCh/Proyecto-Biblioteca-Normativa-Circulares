"""Orquestador Central y Exportador CSV para Circulares DDU.

Este módulo define la clase DDUOrchestrator, encargada de coordinar la ejecución
de los 11 extractores modulares (ETLs independientes en scripts/extractors/),
consolidar el diccionario de datos estricto DatosCircularDDU, y exportar
archivos CSV estructurados (individuales o dataset acumulado).
"""

import argparse
import csv
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

_PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

import importlib

try:
    from ddu_types import DatosCircularDDU, SeccionDDU
except ImportError:
    from scripts.ddu_types import DatosCircularDDU, SeccionDDU

try:
    from extractors import ExtractorRegistry, registrar_todos_los_extractores
except ImportError:
    from scripts.extractors import ExtractorRegistry, registrar_todos_los_extractores


class DDUOrchestrator:
    """Orquestador central para ejecutar ETLs modulares de circulares DDU y exportar a CSV."""

    def __init__(self) -> None:
        """Inicializa el orquestador."""
        pass

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
            "lugar": str(datos_consolidados.get("lugar", "Santiago")),
            "destinatarios": str(datos_consolidados.get("destinatarios", "")),
            "firmante": str(datos_consolidados.get("firmante", "")),
            "lista_distribucion": datos_consolidados.get("lista_distribucion", []),
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
        text_parts: List[str] = []
        for page in pdf_pages:
            text_fn: Any = getattr(page, "extract_text", None)
            if callable(text_fn):
                page_text: Any = text_fn()
                if page_text:
                    text_parts.append(str(page_text))

        raw_text = "\n".join(text_parts)
        return self.process_text(raw_text, filename=pdf_path.name)

    def export_individual_csv(self, pdf_path: Path, output_dir: Path) -> Path:
        """Procesa una circular DDU y exporta un archivo CSV individual con los datos extraídos.

        Args:
            pdf_path: Ruta al archivo PDF de origen.
            output_dir: Directorio donde se guardará el CSV exportado.

        Returns:
            Ruta al archivo CSV generado.
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        datos = self.process_pdf(pdf_path)

        ddu_num = datos["numero"] or "desconocido"
        csv_filename = f"DDU_{ddu_num}_extraido.csv"
        csv_path = output_dir / csv_filename

        lugar_str = datos.get("lugar", "Santiago").strip()
        fecha_str = datos["fecha"].strip()
        fecha_lugar_comb = f"{lugar_str}, {fecha_str}" if lugar_str else fecha_str

        filas_csv: List[Dict[str, str]] = [
            {"bloque": "Encabezado", "campo": "numero_ddu", "valor_extraido": datos["numero"]},
            {"bloque": "Acto Administrativo", "campo": "numero_ord", "valor_extraido": datos.get("numero_ord", "")},
            {"bloque": "Antecedentes", "campo": "antecedentes", "valor_extraido": datos["antecedentes"]},
            {"bloque": "Materia", "campo": "materia", "valor_extraido": datos["materia"]},
            {"bloque": "Descriptores", "campo": "descriptores", "valor_extraido": datos.get("descriptores", "")},
            {"bloque": "Fecha y Lugar", "campo": "fecha_emision", "valor_extraido": fecha_lugar_comb},
            {"bloque": "Destinatarios", "campo": "destinatarios", "valor_extraido": datos.get("destinatarios", "")},
            {"bloque": "Emisión", "campo": "emisor", "valor_extraido": datos["emisor"]},
        ]

        secciones: List[SeccionDDU] = datos.get("secciones", [])
        partes_cuerpo: List[str] = []
        for sec in secciones:
            titulo = sec.get("titulo", "").strip()
            parrafos = " ".join(sec.get("parrafos", [])).strip()
            if titulo and parrafos:
                partes_cuerpo.append(f"{titulo}: {parrafos}")
            elif parrafos:
                partes_cuerpo.append(parrafos)
            elif titulo:
                partes_cuerpo.append(titulo)

        cuerpo_consolidado = " | ".join(partes_cuerpo)
        filas_csv.append({"bloque": "Cuerpo", "campo": "cuerpo", "valor_extraido": cuerpo_consolidado})

        filas_csv.append({"bloque": "Firma", "campo": "firmante", "valor_extraido": datos.get("firmante", "")})

        dist_val = datos.get("lista_distribucion", "")
        if isinstance(dist_val, list):
            dist_val = "; ".join(dist_val)
        filas_csv.append({"bloque": "Distribución", "campo": "lista_distribucion", "valor_extraido": dist_val})

        with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["bloque", "campo", "valor_extraido"], delimiter=";")
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
                dist_val = datos.get("lista_distribucion", "")
                if isinstance(dist_val, list):
                    dist_val = "; ".join(dist_val)

                sec_resumen = " | ".join(
                    [f"{s.get('titulo', '')}: {' '.join(s.get('parrafos', []))}" for s in datos.get("secciones", [])]
                )

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
                    "cuerpo_resumen": sec_resumen,
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
            "firmante",
            "lista_distribucion",
        ]

        with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
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
