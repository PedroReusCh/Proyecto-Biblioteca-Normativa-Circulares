"""Extractor de metadato Acto Administrativo (Número Ordinario)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class ActoAdministrativoExtractor(BaseExtractor):
    """Extractor para el número de acto administrativo (ORD. N° / numero_ord)."""

    @property
    def nombre_bloque(self) -> str:
        return "acto_administrativo"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae el número ordinario de acto administrativo.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con el número ordinario del acto administrativo.
        """
        numero_ord = ""
        patron = r"(?:CIRCULAR\s+)?(?:ORD|ORO|ORDINARIO)\.?\s*N[°oº\ufffd\?\.]?\s*([\.\_\s]*[^\n]+)"

        for line in lines[:30]:
            match = re.search(patron, line, re.IGNORECASE)
            if match:
                resto = match.group(1)
                digitos = re.findall(r"\d+", resto)
                if digitos:
                    num_str = "".join(digitos)
                    numero_ord = f"CIRCULAR ORD. N° {num_str}"
                    break
                else:
                    numero_ord = match.group(0).strip()
                    break

        if not numero_ord:
            match = re.search(patron, raw_text[:2000], re.IGNORECASE)
            if match:
                resto = match.group(1)
                digitos = re.findall(r"\d+", resto)
                if digitos:
                    numero_ord = f"CIRCULAR ORD. N° {''.join(digitos)}"
                else:
                    numero_ord = match.group(0).strip()

        exito = bool(numero_ord)
        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"numero_ord": numero_ord},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se pudo extraer el número ordinario del acto administrativo.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Acto Administrativo Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = ActoAdministrativoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
