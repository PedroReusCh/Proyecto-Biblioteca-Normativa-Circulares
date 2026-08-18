"""Extractor modular de Imágenes y Diagramas Técnicos con PyMuPDF (ImagenesExtractor)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Sequence, Set


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
    if "urbanizaciones voluntarias desvinculadas" in texto_lower:
        return "Esquema ilustrativo: Urbanizaciones voluntarias desvinculadas del proceso de división del suelo"

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


def _extraer_imagenes_lineas(
    lines: Sequence[str] | List[str],
    num_str: str = "desconocido",
    dir_imagenes: Optional[Path] = None,
) -> List[Dict[str, Any]]:
    """Extrae metadatos de imágenes definidas en formato Markdown dentro del texto plano."""
    imagenes_manifest: List[Dict[str, Any]] = []
    patron_md_img = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
    idx = 1

    for num_linea, line in enumerate(lines, 1):
        for match in patron_md_img.finditer(line):
            alt_text = match.group(1).strip()
            descripcion = alt_text if alt_text else f"Imagen referenciada en línea {num_linea}"
            img_id = f"DDU_{num_str}_img_{idx}"
            rel_path = f"salidas_imagenes/{img_id}.png"

            imagenes_manifest.append({
                "id": img_id,
                "nombre": descripcion,
                "pagina": 1,
                "tipo": "Esquema técnico" if "esquema" in descripcion.lower() else "Imagen / Diagrama",
                "formato": "png",
                "dimensiones": "0x0",
                "ancho": 0,
                "alto": 0,
                "xref": 0,
                "descripcion": descripcion,
                "archivo_anexo": rel_path,
            })
            idx += 1

    return imagenes_manifest


def _calcular_clip_diagrama(page: Any, r: Any, p_w: float, p_h: float) -> Any:
    """Calcula el rectángulo envolvente ajustado para capturar el diagrama técnico o esquema sin incluir párrafos del cuerpo normativo."""
    import importlib
    fitz_mod: Any = importlib.import_module("fitz")

    if r is None:
        return None

    # 1. Obtener todos los rectángulos de imágenes relevantes en la página (para esquemas compuestos de varios elementos/cajas)
    page_img_rects: List[Any] = []
    try:
        doc = getattr(page, "parent", None)
        if doc is not None:
            for img_info in page.get_images():
                x = int(img_info[0])
                base_img = doc.extract_image(x)
                if not base_img or int(base_img.get("height", 0)) < 60 or int(base_img.get("width", 0)) < 60:
                    continue
                rects = page.get_image_rects(x)
                for img_r in rects:
                    if float(img_r.y1) < (p_h - 50.0) and float(img_r.y0) > 100.0:
                        page_img_rects.append(img_r)
    except Exception:
        pass

    if not page_img_rects:
        page_img_rects = [r]

    x0 = min(float(img_r.x0) for img_r in page_img_rects)
    y0 = min(float(img_r.y0) for img_r in page_img_rects)
    x1 = max(float(img_r.x1) for img_r in page_img_rects)
    y1 = max(float(img_r.y1) for img_r in page_img_rects)

    # 2. Revisar bloques de texto que correspondan a etiquetas internas o cotas del esquema técnico
    # Excluyendo estrictamente párrafos del cuerpo normativo y encabezados de sección
    blocks = page.get_text("blocks")
    for b in blocks:
        bx0, by0, bx1, by1, btext = float(b[0]), float(b[1]), float(b[2]), float(b[3]), str(b[4]).strip()
        if not btext:
            continue
        # Excluir encabezado institucional y pie de página
        if by0 < 60.0 or by1 > (p_h - 40.0):
            continue
        # Excluir numerales de sección (ej. "7.", "7.1.", "4.", "5.")
        if re.match(r"^\d+(?:\.\d+)*\.\s+[A-ZÁÉÍÓÚÑ]", btext):
            continue
        # Excluir párrafos continuos normativos que inician con fórmulas narrativas
        if re.match(r"^(?:En el artículo|Es importante destacar|Se trata de obras|De conformidad|Por otra parte|Asimismo)\b", btext, re.IGNORECASE):
            continue
        if len(btext) > 180:
            continue

        # El bloque debe estar acotado dentro o inmediatamente adyacente a la franja del diagrama
        if by0 >= (y0 - 25.0) and by1 <= (y1 + 25.0):
            if bx0 >= (x0 - 60.0) and bx1 <= (x1 + 60.0):
                x0 = min(x0, bx0)
                y0 = min(y0, by0)
                x1 = max(x1, bx1)
                y1 = max(y1, by1)

    # Margen de seguridad estricto y ajustado (8pt)
    final_x0 = max(20.0, x0 - 8.0)
    final_y0 = max(40.0, y0 - 8.0)
    final_x1 = min(p_w - 20.0, x1 + 8.0)
    final_y1 = min(p_h - 20.0, y1 + 8.0)

    return fitz_mod.Rect(final_x0, final_y0, final_x1, final_y1)



@register_extractor
class ImagenesExtractor(BaseExtractor):

    """Extractor modular para diagramas técnicos, planos e ilustraciones en circulares DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "imagenes"

    def extract(
        self,
        raw_text: str,
        lines: Sequence[str] | List[str],
        pdf_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> ResultadoBloque:

        """Extrae e inventaría imágenes y esquemas técnicos con PyMuPDF (fitz) y exporta en formato PNG sin pérdida.

        Args:
            raw_text: Texto completo de la circular.
            lines: Lista de líneas limpias.
            pdf_path: Ruta opcional al archivo PDF para extracción nativa con PyMuPDF.
            output_dir: Directorio opcional de salida para guardar las imágenes extraídas.

        Returns:
            ResultadoBloque con la lista estructurada del manifiesto ligero de imágenes.
        """
        # Determinar identificador base DDU (ej. 456)
        num_str = "desconocido"
        if pdf_path is not None:
            m_pdf = re.search(r"\b(\d+)\b", pdf_path.stem)
            if m_pdf:
                num_str = m_pdf.group(1)
        if num_str == "desconocido" and raw_text:
            m_txt = re.search(r"DDU\s*(\d+)", raw_text, re.IGNORECASE)
            if m_txt:
                num_str = m_txt.group(1)

        dir_imagenes = output_dir if output_dir is not None else (_PROYECTO_RAIZ / "salidas_imagenes")
        manifest_imagenes: List[Dict[str, Any]] = []

        if pdf_path is not None and pdf_path.exists():
            try:
                import importlib
                fitz_mod: Any = importlib.import_module("fitz")

                with fitz_mod.open(str(pdf_path)) as doc:
                    vistos_xrefs: Set[int] = set()
                    img_idx = 1

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
                            image_bytes: bytes = base_img.get("image", b"")
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
                            img_id = f"DDU_{num_str}_img_{img_idx}"
                            filename = f"{img_id}.png"

                            dir_imagenes.mkdir(parents=True, exist_ok=True)
                            img_out_path = dir_imagenes / filename

                            # Exportar en formato PNG sin pérdida (lossless) con DPI 300 capturando el esquema completo
                            clip_rect = _calcular_clip_diagrama(page, r, p_w, p_h) if r is not None else None
                            if clip_rect is not None:
                                pix = page.get_pixmap(dpi=300, clip=clip_rect)
                            else:
                                pix = fitz_mod.Pixmap(doc, xref)
                                if pix.n >= 5:
                                    pix = fitz_mod.Pixmap(fitz_mod.csRGB, pix)

                            pix.save(str(img_out_path))

                            final_w = int(pix.width)
                            final_h = int(pix.height)

                            rel_path = f"salidas_imagenes/{filename}"
                            manifest_imagenes.append({
                                "id": img_id,
                                "nombre": descripcion,
                                "pagina": num_pag,
                                "tipo": "Esquema técnico" if "esquema" in descripcion.lower() else "Imagen / Diagrama",
                                "formato": "png",
                                "dimensiones": f"{final_w}x{final_h}",
                                "ancho": final_w,
                                "alto": final_h,
                                "xref": xref,
                                "descripcion": descripcion,
                                "archivo_anexo": rel_path,
                            })
                            img_idx += 1


            except Exception as e:
                return ResultadoBloque(
                    nombre_bloque=self.nombre_bloque,
                    exito=False,
                    datos={"imagenes": []},
                    confianza=0.0,
                    observaciones=f"Error al procesar imágenes con PyMuPDF: {e}",
                )

        if not manifest_imagenes:
            manifest_imagenes = _extraer_imagenes_lineas(lines, num_str, dir_imagenes)

        exito = len(manifest_imagenes) > 0
        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"imagenes": manifest_imagenes},
            confianza=1.0 if exito else 0.0,
            observaciones=(
                f"Se detectaron {len(manifest_imagenes)} imagen(es)/diagrama(s) y se exportaron en PNG a {dir_imagenes.name}/."
                if exito
                else "No se detectaron imágenes ni esquemas técnicos relevantes en el documento."
            ),
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Imágenes Extractor Standalone con PyMuPDF")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    parser.add_argument("--output-dir", type=str, default="salidas_imagenes", help="Directorio de salida para imágenes")
    args = parser.parse_args()

    target_pdf = Path(args.pdf)
    extractor = ImagenesExtractor()
    resultado_bloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=target_pdf,
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(asdict(resultado_bloque), indent=2, ensure_ascii=False))
