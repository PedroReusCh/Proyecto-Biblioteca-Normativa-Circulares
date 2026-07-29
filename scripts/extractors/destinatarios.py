"""Extractor de metadato Destinatarios (A:)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class DestinatariosExtractor(BaseExtractor):
    """Extractor para los destinatarios (A: / PARA:) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "destinatarios"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae el valor del campo A: / PARA:.

        Soporta tanto el orden moderno (A: ... DE:) como el orden invertido
        de circulares antiguas (DE: ... A:).

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los destinatarios extraídos.
        """
        destinatarios = ""

        # Fase 1: Localizar posiciones de A:/PARA: y DE: en las primeras 40 líneas
        idx_a: int = -1
        idx_de: int = -1
        scan_limit = min(40, len(lines))

        for i in range(scan_limit):
            line = lines[i]
            if idx_a == -1 and re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*.+$", line, re.IGNORECASE):
                # Descartar falsos positivos como "A LA FECHA"
                m_check = re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*:?\s*(.+)$", line, re.IGNORECASE)
                if m_check and not re.match(r"^LA\s+FECHA", m_check.group(1).strip(), re.IGNORECASE):
                    idx_a = i
            if idx_de == -1 and re.match(r"^DE\s*:?\s*(?:JEFE|MINISTRO|SUBSECRETARI[OA]|DIRECTOR|DIVISI[ÓO]N|\w).+$", line, re.IGNORECASE):
                idx_de = i

        # Fase 2: Extraer contenido de A:/PARA: acotado por la posición de DE:
        if idx_a != -1:
            match_a = re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*:?\s*(.+)$", lines[idx_a], re.IGNORECASE)
            if match_a:
                destinatarios = match_a.group(1).strip()

        # Fase 3: Fallback sobre raw_text si no se encontró en líneas
        if not destinatarios:
            match = re.search(r"\b(?:A|PARA)\s*:\s*([^\n]+)", raw_text[:1500], re.IGNORECASE)
            if match:
                val = match.group(1).strip()
                if not re.match(r"^LA\s+FECHA", val, re.IGNORECASE):
                    destinatarios = val

        destinatarios = re.sub(r"\s+", " ", destinatarios).strip()
        exito = bool(destinatarios)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"destinatarios": destinatarios},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontraron destinatarios en el encabezado.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Destinatarios Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = DestinatariosExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
