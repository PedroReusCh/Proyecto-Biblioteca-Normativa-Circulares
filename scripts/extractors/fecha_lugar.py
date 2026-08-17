"""Extractor de metadato Fecha y Lugar de Emisión."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Sequence

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor



def _reparar_digitos_anio_ocr(anio_str: str) -> str:
    """Repara confusiones tipográficas genéricas de OCR en dígitos de año (siglo XXI: 2000-2099)."""
    s = anio_str.strip()
    if len(s) == 4 and s.startswith("2"):
        d1 = "2"
        d2 = "0" if s[1] in ("3", "o", "O", "Q", "b") else s[1]
        d3 = "2" if s[2] in ("2", "l", "I", "|") else s[2]
        d4 = "6" if (s[3] in ("5", "3", "b") and (s[1] in ("3", "o", "O", "0") or s[2] in ("2", "l", "I"))) else s[3]
        return f"{d1}{d2}{d3}{d4}"
    return s


@register_extractor
class FechaLugarExtractor(BaseExtractor):
    """Extractor para la fecha (YYYY-MM-DD) y lugar de emisión de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "fecha_lugar"

    def extract(self, raw_text: str, lines: Sequence[str] | List[str], pdf_path: Optional[Path] = None) -> ResultadoBloque:
        """Extrae la fecha normalizada y el lugar de emisión.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.
            pdf_path: Ruta opcional al archivo PDF.


        Returns:
            ResultadoBloque con la fecha y el lugar extraídos.
        """
        raw_text_clean = raw_text.replace("\ufffd", "0").replace("\u2013", "-").replace("\u2014", "-")
        meses_regex = (
            r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|"
            r"setiembre|octubre|noviembre|diciembre|ene|feb|mar|abr|may|jun|"
            r"jul|ago|sep|oct|nov|dic)"
        )

        raw_text_norm = re.sub(
            rf"\b([123])\s+[Oo0]\s+(?={meses_regex})",
            r"\g<1>0 ",
            raw_text_clean,
            flags=re.IGNORECASE,
        )
        raw_text_norm = re.sub(
            rf"\b([123])\s+([0-9])\s+(?={meses_regex})",
            r"\g<1>\g<2> ",
            raw_text_norm,
            flags=re.IGNORECASE,
        )
        # Normalizar distorsiones genéricas de OCR en años de 4 dígitos tras un mes
        pattern_anio_ocr = re.compile(
            rf"(\b{meses_regex}\.?\s*(?:de\s+)?)([0-9lI\|oO3b]{{4}})\b",
            re.IGNORECASE,
        )

        def _fix_match(m: re.Match[str]) -> str:
            prefix = m.group(1)
            anio_clean = _reparar_digitos_anio_ocr(m.group(2))
            return f"{prefix}{anio_clean}"

        raw_text_norm = pattern_anio_ocr.sub(_fix_match, raw_text_norm)
        raw_text_norm = re.sub(r"\b([0-3])\s+([0-9])\b", r"\1\2", raw_text_norm)
        raw_text_norm = re.sub(r"\b2[0oO\ufffd]\s*[lI\|]\s*(\d{2})\b", r"20\1", raw_text_norm)
        raw_text_norm = re.sub(r"\b2[^\d\s]{1,3}(\d{2})\b", r"20\1", raw_text_norm)
        raw_text_norm = pattern_anio_ocr.sub(_fix_match, raw_text_norm)

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
                yyyy_str = _reparar_digitos_anio_ocr(match.group("anio"))
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
                    yyyy_str = _reparar_digitos_anio_ocr(match.group("anio"))
                    yyyy = 2000 + int(yyyy_str) if len(yyyy_str) == 2 else int(yyyy_str)
                    mm = mes_map.get(mes_str, "00")
                    fecha = f"{yyyy:04d}-{mm}-{dd:02d}"
                    if match.group("lugar"):
                        lugar = match.group("lugar").capitalize()
                    break

        exito = bool(fecha)
        fecha_lugar = f"{lugar}, {fecha}" if lugar and fecha else (fecha or lugar)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "fecha": fecha,
                "lugar": lugar,
                "fecha_lugar": fecha_lugar,
            },
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se pudo extraer la fecha de emisión.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Fecha y Lugar Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = FechaLugarExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
