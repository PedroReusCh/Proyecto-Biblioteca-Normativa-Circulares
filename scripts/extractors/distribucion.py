"""Extractor de la lista de distribución de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

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

        patron_encabezado_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N)[\s:]*"
        )

        def _limpiar_item_distribucion(item: str) -> str:
            # 1. Normalizar prefijo numérico ruidoso como "1!", "1 !", "2 .", "4 ." -> "1. ", "2. ", "4. "
            item = re.sub(r"^(\d+)[\!\;\:\,\_\-]+\s*", r"\1. ", item)
            item = re.sub(r"^(\d+)\s*\.\s*", r"\1. ", item)

            # 2. Corregir palabras divididas erróneamente por OCR
            correcciones = [
                (r"\bUrban\s+ismo\b", "Urbanismo"),
                (r"\bRegio\s+nales\b", "Regionales"),
                (r"\bRegio\s+nal\b", "Regional"),
                (r"\bSecreta\s+ria\b", "Secretaria"),
                (r"\bSecreta\s+rias\b", "Secretarias"),
                (r"\bSecreta\s+rios\b", "Secretarios"),
                (r"\bSubsecreta\s+ria\b", "Subsecretaria"),
                (r"\bDesarro\s+llo\b", "Desarrollo"),
                (r"\bTerr\s+itorial\b", "Territorial"),
                (r"\bDirecto\s+res\b", "Directores"),
                (r"\bReviso\s+res\b", "Revisores"),
                (r"\bI\s+ndependientes\b", "Independientes"),
                (r"\bBibliot\s+eca\b", "Biblioteca"),
                (r"\bMiniste\s+rio\b", "Ministerio"),
                (r"\bInstitu\s+to\b", "Instituto"),
                (r"\bPlanificac\s+i[óo]n\b", "Planificación"),
                (r"\bOrdenamien\s+to\b", "Ordenamiento"),
                (r"\bAmbie\s+nte\b", "Ambiente"),
                (r"\bDivisi[óo]\s+n\b", "División"),
                (r"\bNaciona\s+l\b", "Nacional"),
            ]
            for p, r in correcciones:
                item = re.sub(p, r, item, flags=re.IGNORECASE)

            return re.sub(r"\s+", " ", item).strip()

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

                item_clean = _limpiar_item_distribucion(line_clean)
                if item_clean:
                    lista_distribucion.append(item_clean)
            else:
                if re.match(patron_encabezado_distribucion, line_clean, re.IGNORECASE):
                    en_distribucion = True
                    sub = re.sub(patron_encabezado_distribucion, "", line_clean, flags=re.IGNORECASE).strip()
                    if sub and not re.match(r"^\d+$", sub):
                        lista_distribucion.append(_limpiar_item_distribucion(sub))

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
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = DistribucionExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
