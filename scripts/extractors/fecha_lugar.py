"""Extractor de metadato Fecha y Lugar de Emisión."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
from typing import List

import pypdf

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class FechaLugarExtractor(BaseExtractor):
    """Extractor para la fecha (YYYY-MM-DD) y lugar de emisión de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "fecha_lugar"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la fecha normalizada y el lugar de emisión.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la fecha y el lugar extraídos.
        """
        meses_regex = (
            r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
            r"setiembre|octubre|noviembre|diciembre|ene|feb|mar|abr|may|jun|"
            r"jul|ago|sep|oct|nov|dic)"
        )

        raw_text_norm = re.sub(
            rf"\b([123])\s+[Oo0]\s+(?={meses_regex})",
            r"\g<1>0 ",
            raw_text,
            flags=re.IGNORECASE,
        )
        raw_text_norm = re.sub(
            rf"\b([123])\s+([1-9])\s+(?={meses_regex})",
            r"\g<1>\g<2> ",
            raw_text_norm,
            flags=re.IGNORECASE,
        )
        raw_text_norm = re.sub(r"\b2325\b", "2023", raw_text_norm)

        patron_fecha = (
            rf"(?P<lugar>Santiago|Valpara[íi]so|Concepci[óo]n)?\s*,?\s*"
            rf"(?P<dia>\d{{1,2}})\s+(?:de\s+)?(?P<mes>{meses_regex})\.?\s*(?:de\s+)?(?P<anio>\d{{2,4}})"
        )

        mes_map = {
            "ene": "01", "enero": "01",
            "feb": "02", "febrero": "02",
            "mar": "03", "marzo": "03",
            "abr": "04", "abril": "04",
            "may": "05", "mayo": "05",
            "jun": "06", "junio": "06",
            "jul": "07", "julio": "07",
            "ago": "08", "agosto": "08",
            "sep": "09", "septiembre": "09", "setiembre": "09",
            "oct": "10", "octubre": "10",
            "nov": "11", "noviembre": "11",
            "dic": "12", "diciembre": "12",
        }

        fecha = ""
        lugar = "Santiago"

        lineas_ciudad = [
            l for l in raw_text_norm.splitlines()
            if any(c in l.lower() for c in ["santiago", "valparaiso", "valparaíso", "concepcion", "concepción"])
        ]

        for line in lineas_ciudad:
            match = re.search(patron_fecha, line, re.IGNORECASE)
            if match:
                dd = int(match.group("dia"))
                mes_str = match.group("mes").lower().strip(".")
                yyyy_str = match.group("anio")
                yyyy = 2000 + int(yyyy_str) if len(yyyy_str) == 2 else int(yyyy_str)
                mm = mes_map.get(mes_str, "00")
                fecha = f"{yyyy:04d}-{mm}-{dd:02d}"
                if match.group("lugar"):
                    lugar = match.group("lugar").capitalize()
                break

        if not fecha:
            for line in raw_text_norm.splitlines()[:50]:
                if any(k in line.lower() for k in ["complementa", "modifica", "deroga"]):
                    continue
                match = re.search(patron_fecha, line, re.IGNORECASE)
                if match:
                    dd = int(match.group("dia"))
                    mes_str = match.group("mes").lower().strip(".")
                    yyyy_str = match.group("anio")
                    yyyy = 2000 + int(yyyy_str) if len(yyyy_str) == 2 else int(yyyy_str)
                    mm = mes_map.get(mes_str, "00")
                    fecha = f"{yyyy:04d}-{mm}-{dd:02d}"
                    if match.group("lugar"):
                        lugar = match.group("lugar").capitalize()
                    break

        exito = bool(fecha)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"fecha": fecha, "lugar": lugar},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se pudo extraer la fecha de emisión.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Fecha y Lugar Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([page.extract_text() or "" for page in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines()]

    extractor = FechaLugarExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
