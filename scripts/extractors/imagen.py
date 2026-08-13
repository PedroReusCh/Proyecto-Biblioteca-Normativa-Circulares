"""Extractor independiente para imágenes de la circular DDU."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import List

import fitz

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

    def _numero_ddu(self) -> str:
        numero = str(getattr(self, "numero", "") or "").strip()
        match = re.search(r"DDU[\s_-]*(\d+)", numero, re.IGNORECASE) if numero else None
        return f"DDU_{match.group(1)}" if match else "DDU_desconocida"

    def _extraer_imagenes(self) -> str:
        pdf_path = str(getattr(self, "pdf_path", "") or "")
        if not pdf_path:
            return ""

        salida = Path(pdf_path).resolve().parent.parent / "salidas_imagenes"
        salida.mkdir(parents=True, exist_ok=True)
        elementos: list[dict[str, object]] = []

        with fitz.open(pdf_path) as doc:
            pagina_idx = 2
            if pagina_idx < len(doc):
                pagina = doc[pagina_idx]
                rects = [
                    fitz.Rect(35, 470, 575, 885),
                ]
                for rect in rects:
                    nombre = "Corte Esquemático / Sin Escala y Planta Azotea / Sin Escala"
                    prefijo = self._numero_ddu()
                    nombre_base = self._normalizar_nombre_archivo(nombre)
                    archivo_nombre = f"{prefijo}_imagen_{nombre_base}.png"
                    for obsoleto in (
                        salida / f"{nombre_base}.png",
                        salida / f"DDU_desconocida_imagen_{nombre_base}.png",
                    ):
                        obsoleto.unlink(missing_ok=True)
                    archivo = salida / archivo_nombre
                    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2), clip=rect, alpha=False)
                    pix.save(str(archivo))
                    elementos.append(
                        {
                            "id_imagen": f"{prefijo}_imagen_{nombre_base}",
                            "elemento_xml": "img",
                            "nombre": nombre,
                            "pagina": 3,
                            "width": pix.width,
                            "height": pix.height,
                            "extension": "png",
                            "archivo": archivo_nombre,
                            "descripcion": nombre,
                        }
                    )

        return json.dumps(elementos, ensure_ascii=False)

    def _normalizar_nombre_archivo(self, nombre: str) -> str:
        limpio = re.sub(r"[áÁ]", "a", nombre)
        limpio = re.sub(r"[éÉ]", "e", limpio)
        limpio = re.sub(r"[íÍ]", "i", limpio)
        limpio = re.sub(r"[óÓ]", "o", limpio)
        limpio = re.sub(r"[úÚ]", "u", limpio)
        limpio = re.sub(r"[ñÑ]", "n", limpio)
        limpio = re.sub(r"[^A-Za-z0-9_]+", "_", limpio).strip("_")
        return limpio.lower() or "imagen"
