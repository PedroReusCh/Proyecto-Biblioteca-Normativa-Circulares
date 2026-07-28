"""Extractor de metadato Acto Administrativo (Número Ordinario)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import Any, List

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
            raw_text: Texto plano completo del PDF.
            lines: Lista de líneas del PDF.

        Returns:
            ResultadoBloque con el diccionario {"numero_ord": val}.
        """
        numero_ord = ""

        # Patrón para capturar "CIRCULAR ORD. N° 112" o "CIRCULAR ORD. N° 088"
        pattern_ord = re.compile(r"CIRCULAR\s+ORD\.?\s*N[°o]?\s*(\d+|\w+)", re.IGNORECASE)
        match = pattern_ord.search(raw_text)

        if match:
            numero_ord = match.group(0).strip()
        else:
            # Búsqueda secundaria en primeras 15 líneas
            pattern_sec = re.compile(r"ORD\.?\s*N[°o]?\s*(\d+|\w+)", re.IGNORECASE)
            for line in lines[:15]:
                match_line = pattern_sec.search(line)
                if match_line:
                    numero_ord = f"CIRCULAR ORD. N° {match_line.group(1)}"
                    break

        if numero_ord:
            # Normalizar errores OCR comunes (ej: ORO -> 088)
            partes = numero_ord.split("N°")
            if len(partes) > 1:
                val_num = partes[1].strip()
                if not val_num.isdigit():
                    digitos = [c if c.isdigit() else ("0" if c in "O" else "") for c in val_num]
                    numero_ord = f"CIRCULAR ORD. N° {''.join(digitos)}"
                else:
                    numero_ord = match.group(0).strip() if match else numero_ord

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
    reader: pypdf.PdfReader = pypdf.PdfReader(pdf_path)
    pages: List[Any] = list(reader.pages)
    text_list: List[str] = [str(page.extract_text() or "") for page in pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = ActoAdministrativoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
