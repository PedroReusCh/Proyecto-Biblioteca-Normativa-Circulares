"""Extractor de metadato Antecedentes (ANT:)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class AntecedentesExtractor(BaseExtractor):
    """Extractor para la sección o encabezado de Antecedentes (ANT:)."""

    @property
    def nombre_bloque(self) -> str:
        return "antecedentes"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae el contenido del campo ANT / ANTECEDENTES.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los antecedentes extraídos.
        """
        antecedentes = ""
        en_antecedentes = False

        for line in lines[:60]:
            line_clean = line.strip()
            if not line_clean:
                if en_antecedentes:
                    en_antecedentes = False
                continue

            if en_antecedentes:
                # Comprobar si inicia un nuevo bloque de encabezado
                if (
                    re.match(r"^(?:MAT|MATERIA)\.?(?:\s*:\s*|\s+)", line_clean, re.IGNORECASE)
                    or re.match(r"^DE\s*:\s*", line_clean, re.IGNORECASE)
                    or re.match(r"^DE\s+(?:JEFE|MINISTRO|DIRECTOR|DIVISI[ÓO]N)\b", line_clean, re.IGNORECASE)
                    or re.match(r"^A\s*:\s*", line_clean, re.IGNORECASE)
                    or re.match(r"^A\s+SEGÚN\b", line_clean, re.IGNORECASE)
                    or re.match(r"^(?:CIRCULAR|SANTIAGO|VALPARAÍSO|CONCEPCIÓN|I\.)\b", line_clean, re.IGNORECASE)
                    or re.match(r"^[A-ZÁÉÍÓÚÑ0-9\s;]{3,}(?:,\s*[A-ZÁÉÍÓÚÑ0-9\s;]{3,})+\.?$", line_clean)
                ):
                    en_antecedentes = False
                else:
                    antecedentes += " " + line_clean
            else:
                match_ant = re.match(
                    r"^(?:ANT|ANTECEDENTES)[\s\.:]+(.+)$",
                    line_clean,
                    re.IGNORECASE,
                )
                if match_ant:
                    antecedentes = match_ant.group(1).strip()
                    en_antecedentes = True

        antecedentes = re.sub(r"\s+", " ", antecedentes).strip()
        exito = bool(antecedentes)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"antecedentes": antecedentes},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontraron antecedentes en el documento.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Antecedentes Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = AntecedentesExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
