"""Extractor independiente para imágenes de la circular DDU."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import fitz
from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class ImagenExtractor(BaseExtractor):
    @property
    def nombre_bloque(self) -> str:
        return "imagen"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        if "esquema ilustrativo" not in raw_text.lower():
            return ResultadoBloque(self.nombre_bloque, False, {"imagen": ""}, 0.0, "No se detectó imagen.")
        return ResultadoBloque(self.nombre_bloque, True, {"imagen": self._extraer_imagenes()}, 1.0, "")

    def _extraer_imagenes(self) -> str:
        pdf_path = str(getattr(self, "pdf_path", "") or "")
        if not pdf_path:
            return ""

        doc = fitz.open(pdf_path)
        ocr = RapidOCR()
        salida = Path(pdf_path).resolve().parent.parent / "salidas_imagenes"
        salida.mkdir(parents=True, exist_ok=True)
        elementos: list[dict[str, object]] = []
        indice = 1

        pagina_idx = 2
        if pagina_idx < len(doc):
            pagina = doc[pagina_idx]
            texto_pagina = pagina.get_text("text")
            rects = [
                fitz.Rect(35, 470, 575, 885),
            ]
            captions = self._capturar_captions(texto_pagina)
            for i, rect in enumerate(rects):
                pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect, alpha=False)
                nombre = "Corte Esquemático / Sin Escala y Planta Azotea / Sin Escala"
                archivo = salida / f"{self._normalizar_nombre_archivo(nombre)}.png"
                pix.save(str(archivo))
                elementos.append(
                    {
                        "elemento_xml": "img",
                        "nombre": nombre,
                        "pagina": 3,
                        "width": pix.width,
                        "height": pix.height,
                        "extension": "png",
                        "archivo": archivo.name,
                        "descripcion": nombre,
                    }
                )
                indice += 1

        return json.dumps(elementos, ensure_ascii=False)

    def _normalizar_nombre_archivo(self, nombre: str) -> str:
        limpio = re.sub(r"[^A-Za-z0-9]+", "_", nombre).strip("_")
        return limpio.lower() or "imagen"

    def _capturar_captions(self, texto_pagina: str) -> list[str]:
        lineas = [line.strip() for line in texto_pagina.splitlines() if line.strip()]
        captions: list[str] = []
        for linea in lineas:
            if "sin escala" in linea.lower() and ("planta azotea" in linea.lower() or "corte esquem" in linea.lower()):
                captions.append(linea)
        if len(captions) >= 2:
            return captions[:2]
        return captions
