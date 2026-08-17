"""Extractor de metadato Emisor (DE:)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Sequence

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class EmisorExtractor(BaseExtractor):
    """Extractor para el emisor (DE:) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "emisor"

    def extract(self, raw_text: str, lines: Sequence[str] | List[str], pdf_path: Optional[Path] = None) -> ResultadoBloque:
        """Extrae el emisor indicado en la circular.

        Soporta tanto el orden moderno (A: ... DE:) como el orden invertido
        de circulares antiguas (DE: ... A:).

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.
            pdf_path: Ruta opcional al archivo PDF.


        Returns:
            ResultadoBloque con el emisor extraído.
        """
        emisor = ""

        # Fase 1: Localizar posiciones de DE: y A:/PARA: en las primeras 40 líneas
        idx_de: int = -1
        idx_a: int = -1
        scan_limit = min(40, len(lines))

        for i in range(scan_limit):
            line = lines[i]
            if idx_de == -1:
                match_de = re.match(r"^DE\s*:\s*(.+)$", line, re.IGNORECASE)
                if not match_de:
                    match_de = re.match(
                        r"^DE\s+((?:JEFE|MINISTRO|SUBSECRETARI[OA]|DIRECTOR|DIVISI[ÓO]N)\b.+)$",
                        line,
                        re.IGNORECASE,
                    )
                if match_de:
                    idx_de = i
            if idx_a == -1 and re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*.+$", line, re.IGNORECASE):
                m_check = re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*:?\s*(.+)$", line, re.IGNORECASE)
                if m_check and not re.match(r"^LA\s+FECHA", m_check.group(1).strip(), re.IGNORECASE):
                    idx_a = i

        # Fase 2: Extraer contenido de DE: acotado por la posición de A:/PARA:
        if idx_de != -1:
            match_de = re.match(r"^DE\s*:\s*(.+)$", lines[idx_de], re.IGNORECASE)
            if not match_de:
                match_de = re.match(
                    r"^DE\s+((?:JEFE|MINISTRO|SUBSECRETARI[OA]|DIRECTOR|DIVISI[ÓO]N)\b.+)$",
                    lines[idx_de],
                    re.IGNORECASE,
                )
            if match_de:
                emisor = match_de.group(1).strip()

        # Fase 3: Fallback sobre raw_text si no se encontró en líneas
        if not emisor:
            match = re.search(
                r"\bDE\s*:\s*([^\n]+)",
                raw_text[:1500],
                re.IGNORECASE,
            )
            if match:
                emisor = match.group(1).strip()

        if emisor.endswith("."):
            emisor = emisor[:-1].strip()

        emisor = re.sub(r"\s+", " ", emisor).strip()
        exito = bool(emisor)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"emisor": emisor},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró emisor en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Emisor Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = EmisorExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
