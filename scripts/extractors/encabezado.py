"""Extractor de metadato Encabezado / Número DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Sequence

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class EncabezadoExtractor(BaseExtractor):
    """Extractor para el número DDU de la circular (bloque 'encabezado')."""

    @property
    def nombre_bloque(self) -> str:
        return "encabezado"

    def extract(self, raw_text: str, lines: Sequence[str] | List[str], pdf_path: Optional[Path] = None) -> ResultadoBloque:
        """Extrae el número DDU desde las líneas o texto plano.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.
            pdf_path: Ruta opcional al archivo PDF.


        Returns:
            ResultadoBloque con el número DDU extraído.
        """
        digits = ""
        # Buscar en las primeras 30 líneas
        for line in lines[:30]:
            match = re.search(r"\bDDU\s*N?[°oº]?\s*(\d+)\b", line, re.IGNORECASE)
            if match:
                digits = match.group(1)
                break

        if not digits:
            match = re.search(r"\bDDU\s*N?[°oº]?\s*(\d+)\b", raw_text, re.IGNORECASE)
            if match:
                digits = match.group(1)

        numero = f"DDU {digits}" if digits else ""
        exito = bool(numero)
        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"numero": numero},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se pudo identificar el número DDU en el texto.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Encabezado Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = EncabezadoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
