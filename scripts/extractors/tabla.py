"""Extractor independiente para tablas de la circular DDU."""

from __future__ import annotations

import json
from typing import List

import pdfplumber

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class TablaExtractor(BaseExtractor):
    """Extrae tablas reales con celdas y texto desde el PDF."""

    @property
    def nombre_bloque(self) -> str:
        return "tabla"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        if "circular materia(s) que se modifica(n)" not in raw_text.lower():
            return ResultadoBloque(self.nombre_bloque, False, {"tabla": ""}, 0.0, "No se detectó tabla.")

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=True,
            datos={"tabla": self._extraer_tablas()},
            confianza=1.0,
            observaciones="",
        )

    def _extraer_tablas(self) -> str:
        pdf_path = getattr(self, "pdf_path", "")
        if not pdf_path:
            return ""

        elementos: list[dict[str, object]] = []
        with pdfplumber.open(pdf_path) as pdf:
            for pagina_idx, pagina in enumerate(pdf.pages, start=1):
                for tabla_idx, tabla in enumerate(pagina.extract_tables() or [], start=1):
                    elementos.append(
                        {
                            "elemento_xml": "table",
                            "nombre": f"tabla_{pagina_idx}_{tabla_idx}",
                            "pagina": pagina_idx,
                            "filas": len(tabla),
                            "columnas": max((len(fila) for fila in tabla if fila), default=0),
                            "contenido": tabla,
                        }
                    )
        return json.dumps(elementos, ensure_ascii=False)
