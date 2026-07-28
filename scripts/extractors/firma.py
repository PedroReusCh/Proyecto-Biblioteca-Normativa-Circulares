"""Extractor de la firma y firmante de la circular DDU."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import Any, List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class FirmaExtractor(BaseExtractor):
    """Extractor para identificar el firmante (nombre y cargo) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "firma"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la información del firmante de la circular DDU.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con el firmante extraído.
        """
        firmante = ""

        # 1. Buscar patrón "Saluda atentamente..." y extraer las líneas siguientes
        idx_saludo = -1
        for i, line in enumerate(lines):
            if re.search(r"Saluda\s+atentamente", line, re.IGNORECASE) or re.search(
                r"^Atentamente\b", line, re.IGNORECASE
            ):
                idx_saludo = i
                break

        if idx_saludo != -1:
            partes_firma: List[str] = []
            for line in lines[idx_saludo + 1 : idx_saludo + 8]:
                line_clean = line.strip()
                if not line_clean:
                    continue
                # Detener si llegamos al bloque de distribución o pie de página
                if re.match(
                    r"^(?:DISTRIBUCI[ÓO]N|BUCI[ÓO]N|STRIBUCI[ÓO]N)[\s:]*",
                    line_clean,
                    re.IGNORECASE,
                ) or re.search(r"Ministerio\s+de\s+Vivienda", line_clean, re.IGNORECASE):
                    break

                # Limpiar caracteres ruidosos de firma o sellos de OCR
                line_clean = re.sub(r"^[_\s\-|\.]+", "", line_clean).strip()
                if line_clean:
                    partes_firma.append(line_clean)

            if partes_firma:
                firmante = ", ".join(partes_firma)

        # 2. Si no se encontró mediante saludo, buscar patrones de nombres en mayúsculas y cargos cerca del final
        if not firmante:
            cargos_patron = r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA])\s+(?:DIVISI[ÓO]N|GENERAL|DE)?\b"
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if re.search(cargos_patron, line_clean, re.IGNORECASE) and not re.match(r"^DE\s*:", line_clean, re.IGNORECASE):
                    # Verificar si la línea anterior o posterior parece un nombre propio
                    prev_line = lines[i - 1].strip() if i > 0 else ""
                    if re.match(r"^[A-ZÁÉÍÓÚÑ\s]{4,}$", prev_line) and not re.search(r"MINISTERIO|CIRCULAR|DISTRIBUCION", prev_line):
                        firmante = f"{prev_line}, {line_clean}"
                        break
                    elif re.match(r"^[A-ZÁÉÍÓÚÑ\s]{4,}$", line_clean):
                        firmante = line_clean
                        break

        firmante = re.sub(r"\s+", " ", firmante).strip()
        if firmante.endswith("."):
            firmante = firmante[:-1].strip()

        exito = bool(firmante)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"firmante": firmante},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró firmante en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Firma Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader: pypdf.PdfReader = pypdf.PdfReader(pdf_path)
    pages: List[Any] = list(reader.pages)
    text_list: List[str] = [str(page.extract_text() or "") for page in pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = FirmaExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
