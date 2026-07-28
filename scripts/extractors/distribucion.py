"""Extractor de la lista de distribución de la circular DDU."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class DistribucionExtractor(BaseExtractor):
    """Extractor para la lista de distribución formal de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "distribucion"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la nómina de receptores de la lista de distribución al final de la circular.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la lista_distribucion extraída.
        """
        lista_distribucion: List[str] = []
        en_distribucion = False

        patron_encabezado_distribucion = r"^(?:DISTRIBUCI[ÓO]N|BUCI[ÓO]N|STRIBUCI[ÓO]N)[\s:]*"

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            if en_distribucion:
                # Omitir pie de página de OCR o marcas de corte
                if re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE) or re.search(
                    r"Ministerio\s+de\s+Vivienda\s+y\s+Urban\s*ismo", line_clean, re.IGNORECASE
                ) or re.match(r"^!+$", line_clean):
                    continue

                # Si es un elemento numerado o destinatario (ej. "1. Sr. Ministro...", "2. Sra. Subsecretaria...")
                # o una línea perteneciente a la nómina
                item_clean = re.sub(r"\s+", " ", line_clean).strip()
                if item_clean:
                    lista_distribucion.append(item_clean)
            else:
                if re.match(patron_encabezado_distribucion, line_clean, re.IGNORECASE):
                    en_distribucion = True
                    # Comprobar si hay contenido tras los dos puntos en la misma línea
                    sub = re.sub(patron_encabezado_distribucion, "", line_clean, flags=re.IGNORECASE).strip()
                    if sub:
                        lista_distribucion.append(sub)

        exito = len(lista_distribucion) > 0

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"lista_distribucion": lista_distribucion},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró lista de distribución en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Distribucion Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = DistribucionExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
