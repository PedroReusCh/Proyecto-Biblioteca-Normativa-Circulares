"""Extractor del cuerpo estructurado (secciones y párrafos) de circulares DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.ddu_types import SeccionDDU
from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class CuerpoExtractor(BaseExtractor):
    """Extractor para el cuerpo estructurado por secciones y párrafos."""

    @property
    def nombre_bloque(self) -> str:
        return "cuerpo"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae las secciones y párrafos estructurados del cuerpo de la circular DDU.

        Detecta numerales romanos (ej. I. ALCANCE) como títulos de sección y
        numerales arábigos (ej. 1. De conformidad...) o apartados como párrafos.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la lista de SeccionDDU extraída.
        """
        secciones: List[SeccionDDU] = []
        seccion_actual: SeccionDDU = {"titulo": "ENCABEZADO", "parrafos": []}
        parrafo_actual = ""

        # Ignorar encabezados de metadatos iniciales hasta el cuerpo principal
        # y detenerse al encontrar la firma o distribución
        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Descartar líneas de pie de página de OCR
            if re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE) or re.search(
                r"Ministerio\s+de\s+Vivienda\s+y\s+Urban\s*ismo", line_clean, re.IGNORECASE
            ) or re.match(r"^!+$", line_clean):
                continue

            # Detener extracción si llegamos a la firma o distribución
            if re.match(r"^Saluda\s+atentamente\s+a\s+Ud", line_clean, re.IGNORECASE) or re.match(
                r"^(?:DISTRIBUCI[ÓO]N|BUCI[ÓO]N|STRIBUCI[ÓO]N)[\s:]*", line_clean, re.IGNORECASE
            ):
                break

            # Detectar número romano al inicio (ej. "I. INTRODUCCIÓN", "II. MARCO NORMATIVO")
            match_romano = re.match(r"^([IVXLCDM]+)\.\s+(.+)$", line_clean)
            if match_romano:
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual)
                    parrafo_actual = ""

                if seccion_actual["titulo"] != "ENCABEZADO" or seccion_actual["parrafos"]:
                    secciones.append(seccion_actual)

                seccion_actual = {
                    "titulo": f"{match_romano.group(1)}. {match_romano.group(2).strip()}",
                    "parrafos": [],
                }
                continue

            # Detectar número arábigo al inicio (ej. "1. De conformidad...", "2. MARCO NORMATIVO:")
            match_parrafo = re.match(r"^(\d+)\.\s+(.+)$", line_clean)
            if match_parrafo:
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual)

                parrafo_actual = f"{match_parrafo.group(1)}. {match_parrafo.group(2).strip()}"
                continue

            # Concatenar a párrafo actual
            if parrafo_actual:
                parrafo_actual += " " + line_clean
            else:
                # Si aún estamos en el encabezado de metadatos (antes de 1. o I.), omitir metadatos de cabecera
                if seccion_actual["titulo"] == "ENCABEZADO":
                    if re.match(
                        r"^(?:DDU|CIRCULAR|ORD\.|ANT|MAT|DE|A|SANTIAGO|VALPARA[ÍI]SO|PERMISOS|VIGENCIA)\b",
                        line_clean,
                        re.IGNORECASE,
                    ) or re.match(r"^\d+\)", line_clean):
                        continue
                parrafo_actual = line_clean

        if parrafo_actual:
            seccion_actual["parrafos"].append(parrafo_actual)

        if seccion_actual["titulo"] != "ENCABEZADO" or seccion_actual["parrafos"]:
            secciones.append(seccion_actual)

        exito = len(secciones) > 0 and any(len(s["parrafos"]) > 0 for s in secciones)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"secciones": secciones},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se extrajeron secciones del cuerpo de la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Cuerpo Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = CuerpoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
