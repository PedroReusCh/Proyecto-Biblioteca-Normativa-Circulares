"""Extractor de metadato Materia (MAT:)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import Any, List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class MateriaExtractor(BaseExtractor):
    """Extractor para la materia o tema de la circular (MAT:)."""

    @property
    def nombre_bloque(self) -> str:
        return "materia"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae el texto del campo MAT. / MATERIA.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la materia extraída.
        """
        materia = ""
        en_materia = False

        for line in lines[:50]:
            line_clean = line.strip()
            if not line_clean:
                if en_materia:
                    en_materia = False
                continue

            if en_materia:
                if (
                    re.match(r"^(?:ANT|ANTECEDENTES)\.?(?:\s*:\s*|\s+)", line_clean, re.IGNORECASE)
                    or re.match(r"^DE\s*:\s*", line_clean, re.IGNORECASE)
                    or re.match(r"^DE\s+(?:JEFE|MINISTRO|DIRECTOR|DIVISI[ÓO]N)\b", line_clean, re.IGNORECASE)
                    or re.match(r"^A\s*:\s*", line_clean, re.IGNORECASE)
                    or re.match(r"^A\s+SEGÚN\b", line_clean, re.IGNORECASE)
                    or re.match(r"^(?:CIRCULAR|SANTIAGO|VALPARAÍSO|CONCEPCIÓN|I\.)\b", line_clean, re.IGNORECASE)
                    or re.match(r"^[A-ZÁÉÍÓÚÑ0-9\s;]{3,}(?:,\s*[A-ZÁÉÍÓÚÑ0-9\s;]{3,})+\.?$", line_clean)
                ):
                    en_materia = False
                else:
                    materia += " " + line_clean
            else:
                match_mat = re.match(
                    r"^(?:MAT|MATERIA)[\s\.:]+(.+)$",
                    line_clean,
                    re.IGNORECASE,
                )
                if match_mat:
                    materia = match_mat.group(1).strip()
                    en_materia = True

        materia = re.sub(r"\s+", " ", materia).strip()
        exito = bool(materia)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"materia": materia},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se pudo extraer la materia de la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Materia Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader: pypdf.PdfReader = pypdf.PdfReader(pdf_path)
    pages: List[Any] = list(reader.pages)
    text_list: List[str] = [str(page.extract_text() or "") for page in pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = MateriaExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
