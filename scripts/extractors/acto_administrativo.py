"""Extractor de metadato Acto Administrativo (Número Ordinario)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

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

        # Patrón flexible para "CIRCULAR ORD. N° 112", "CIRCULAR ORO. N ___ 0_8_, 8 ___ /", "ORD. N° 088", etc.
        pattern_ord = re.compile(
            r"(?:CIRCULAR\s+)?(?:ORD|ORO|OR0|OR)\.?\s*(?:N[°oº\?\s_]*\s*)?([0-9\s_l·\-,]+)",
            re.IGNORECASE,
        )
        match = pattern_ord.search(raw_text[:1500])

        if match:
            raw_val = match.group(1).strip()
            digits = re.sub(r"[^0-9]", "", raw_val)
            if digits:
                numero_ord = f"CIRCULAR ORD. N° {digits}"
            else:
                numero_ord = match.group(0).strip()
        else:
            # Búsqueda secundaria en primeras 20 líneas
            for line in lines[:20]:
                match_sec = pattern_ord.search(line)
                if match_sec:
                    digits = re.sub(r"[^0-9]", "", match_sec.group(1))
                    if digits:
                        numero_ord = f"CIRCULAR ORD. N° {digits}"
                    else:
                        numero_ord = match_sec.group(0).strip()
                    break

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
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = ActoAdministrativoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
