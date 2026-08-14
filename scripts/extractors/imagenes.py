"""Extractor modular de Imágenes y Diagramas Técnicos con PyMuPDF (ImagenesExtractor)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set

_PROYECTO_RAIZ = Path(__file__).resolve().parents[2]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

try:
    from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from scripts.extractors.utils_cleaner import limpiar_palabras_ocr
except ImportError:
    from extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from extractors.utils_cleaner import limpiar_palabras_ocr


def _generar_descripcion_tecnica(page_text: str, pagina: int, ancho: int, alto: int) -> str:
    """Genera una descripción técnica contextual para una imagen a partir del texto de la página."""
    texto_limpio = limpiar_palabras_ocr(page_text)
    texto_lower = texto_limpio.lower()

    # Detección específica de esquemas de arquitectura / urbanismo frecuentes en circulares DDU
    if "planta azotea" in texto_lower and ("corte esquemático" in texto_lower or "corte esquematico" in texto_lower):
        return "Esquema ilustrativo: Planta azotea y corte esquemático"

    if "planta azotea" in texto_lower:
        return "Esquema técnico: Planta azotea"

    if "corte esquemático" in texto_lower or "corte esquematico" in texto_lower:
        return "Esquema técnico: Corte esquemático"

    # Buscar patrones de introducción de esquemas o figuras
    patron_intro = re.search(
        r"(?:A continuación|se presenta|siguiente)\s+([^\n.]+?(?:esquema|diagrama|plano|figura|croquis|gráfico)[^\n.]*)",
        texto_limpio,
        re.IGNORECASE,
    )
    if patron_intro:
        desc = patron_intro.group(1).strip()
        if len(desc) > 10:
            return desc[0].upper() + desc[1:]

    # Buscar títulos formales como "Figura 1: ...", "Esquema: ..."
    patron_titulo = re.search(
        r"(?:Figura|Esquema|Diagrama|Plano|Gráfico|Croquis)\s*(?:N?[°º0-9]*\s*[:\-–]?\s*)([^\n.]+)",
        texto_limpio,
        re.IGNORECASE,
    )
    if patron_titulo:
        desc_titulo = patron_titulo.group(0).strip()
        if len(desc_titulo) > 5:
            return desc_titulo

    return f"Esquema / diagrama técnico en página {pagina} ({ancho}x{alto} px)"


def _extraer_imagenes_lineas(lines: List[str]) -> List[Dict[str, Any]]:
    """Extrae metadatos de imágenes definidas en formato Markdown dentro del texto plano."""
    imagenes: List[Dict[str, Any]] = []
    patron_md_img = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")

    for num_linea, line in enumerate(lines, 1):
        for match in patron_md_img.finditer(line):
            alt_text = match.group(1).strip()
            src = match.group(2).strip()

            ext_match = re.search(r"\.([a-zA-Z0-9]+)(?:[?#]|$)", src)
            formato = ext_match.group(1).lower() if ext_match else "png"
            descripcion = alt_text if alt_text else f"Imagen referenciada en línea {num_linea}"

            imagenes.append({
                "pagina": 1,
                "xref": 0,
                "ancho": 0,
                "alto": 0,
                "formato": formato,
                "descripcion": descripcion,
            })

    return imagenes


@register_extractor
class ImagenesExtractor(BaseExtractor):
    """Extractor modular para diagramas técnicos, planos e ilustraciones en circulares DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "imagenes"

    def extract(
        self,
        raw_text: str,
        lines: List[str],
        pdf_path: Optional[Path] = None,
    ) -> ResultadoBloque:
        """Extrae e inventaría imágenes y esquemas técnicos con PyMuPDF (fitz) o Markdown.

        Args:
            raw_text: Texto completo de la circular.
            lines: Lista de líneas limpias.
            pdf_path: Ruta opcional al archivo PDF para extracción nativa con PyMuPDF.

        Returns:
            ResultadoBloque con la lista estructurada de imágenes detectadas.
        """
        imagenes_extraidas: List[Dict[str, Any]] = []

        if pdf_path is not None and pdf_path.exists():
            try:
                import importlib
                fitz_mod: Any = importlib.import_module("fitz")

                with fitz_mod.open(str(pdf_path)) as doc:
                    vistos_xrefs: Set[int] = set()

                    for p_idx in range(len(doc)):
                        page = doc[p_idx]
                        num_pag = p_idx + 1
                        p_w = float(page.rect.width)
                        p_h = float(page.rect.height)
                        page_text = str(page.get_text())

                        img_list = page.get_images()
                        if not img_list:
                            continue

                        for img_info in img_list:
                            xref = int(img_info[0])
                            if xref in vistos_xrefs:
                                continue

                            base_img = doc.extract_image(xref)
                            if not base_img:
                                continue

                            w = int(base_img.get("width", 0))
                            h = int(base_img.get("height", 0))
                            ext = str(base_img.get("ext", "png")).lower()
                            image_bytes = base_img.get("image", b"")
                            byte_len = len(image_bytes)

                            # Filtro 1: Dimensiones mínimas (líneas divisorias, filetes menores a 60px)
                            if h < 60 or w < 60:
                                continue

                            # Filtro 2: Fragmentos y artefactos gráficos de muy bajo peso (< 1000 bytes)
                            if byte_len < 1000:
                                continue

                            # Obtener bounding box en la página
                            rects = page.get_image_rects(xref)
                            r = rects[0] if rects else None

                            # Filtro 3: Membrete institucional superior en la primera página
                            if num_pag == 1 and r is not None and float(r.y0) < 150.0:
                                continue

                            # Filtro 4: Escaneos completos de página (cubre >= 90% del ancho y alto)
                            if r is not None and float(r.width) >= p_w * 0.9 and float(r.height) >= p_h * 0.9:
                                continue

                            vistos_xrefs.add(xref)
                            descripcion = _generar_descripcion_tecnica(page_text, num_pag, w, h)

                            imagenes_extraidas.append({
                                "pagina": num_pag,
                                "xref": xref,
                                "ancho": w,
                                "alto": h,
                                "formato": ext,
                                "descripcion": descripcion,
                            })

            except Exception as e:
                return ResultadoBloque(
                    nombre_bloque=self.nombre_bloque,
                    exito=False,
                    datos={"imagenes": []},
                    confianza=0.0,
                    observaciones=f"Error al procesar imágenes con PyMuPDF: {e}",
                )

        if not imagenes_extraidas:
            imagenes_extraidas = _extraer_imagenes_lineas(lines)

        exito = len(imagenes_extraidas) > 0
        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"imagenes": imagenes_extraidas},
            confianza=1.0 if exito else 0.0,
            observaciones=(
                f"Se detectaron {len(imagenes_extraidas)} imagen(es)/diagrama(s) técnico(s) en el documento."
                if exito
                else "No se detectaron imágenes ni esquemas técnicos relevantes en el documento."
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Imágenes Extractor Standalone con PyMuPDF")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    target_pdf = Path(args.pdf)
    extractor = ImagenesExtractor()
    resultado_bloque = extractor.extract(raw_text="", lines=[], pdf_path=target_pdf)
    print(json.dumps(asdict(resultado_bloque), indent=2, ensure_ascii=False))
