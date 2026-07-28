"""Extractor de metadato Descriptores / Vocablos (Palabras clave)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class DescriptoresExtractor(BaseExtractor):
    """Extractor de descriptores / vocablos de materia en la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "descriptores"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la lista o cadena de descriptores del encabezado.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los descriptores extraídos.
        """
        descriptores = ""
        for line in lines[:45]:
            match_exp = re.match(
                r"^(?:DESCRIPTORES|VOCABLOS|PALABRAS\s+CLAVE)\.?(?:\s*:\s*|\s+)(.+)$",
                line,
                re.IGNORECASE,
            )
            if match_exp:
                descriptores = match_exp.group(1).strip()
                break

            if re.match(r"^[A-ZÁÉÍÓÚÑ0-9\s;]{3,}(?:,\s*[A-ZÁÉÍÓÚÑ0-9\s;]{3,})+\.?$", line):
                if not re.match(r"^(?:DE|A|PARA|MAT|ANT|SANTIAGO|CIRCULAR|MINISTERIO)\b", line, re.IGNORECASE):
                    descriptores = line.strip()
                    break

        descriptores = re.sub(r"\s+", " ", descriptores).strip()
        exito = bool(descriptores)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"descriptores": descriptores},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se identificaron descriptores en el documento.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Descriptores Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = DescriptoresExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
