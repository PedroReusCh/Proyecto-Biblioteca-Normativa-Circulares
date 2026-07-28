"""Extractor de metadato Encabezado / Número DDU."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class EncabezadoExtractor(BaseExtractor):
    """Extractor para el número DDU de la circular (bloque 'encabezado')."""

    @property
    def nombre_bloque(self) -> str:
        return "encabezado"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae el número DDU desde las líneas o texto plano.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con el número DDU extraído.
        """
        numero = ""
        # Buscar en las primeras 30 líneas
        for line in lines[:30]:
            match = re.search(r"\bDDU\s*N?[°oº]?\s*(\d+)\b", line, re.IGNORECASE)
            if match:
                numero = match.group(1)
                break

        if not numero:
            match = re.search(r"\bDDU\s*N?[°oº]?\s*(\d+)\b", raw_text, re.IGNORECASE)
            if match:
                numero = match.group(1)

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
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = EncabezadoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
