"""Extractor modular de Modificaciones Posteriores y Notas Marginales de Vigencia (ModificacionesPosterioresExtractor)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
import sys
from typing import Any, List, Optional

_PROYECTO_RAIZ = Path(__file__).resolve().parents[2]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

try:
    from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from scripts.extractors.utils_cleaner import limpiar_palabras_ocr
except ImportError:
    from extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from extractors.utils_cleaner import limpiar_palabras_ocr


_PATRONES_MODIFICACION = [
    r"Circular\s+Modificada\s+por\b",
    r"Dejada\s+sin\s+efecto\s+por\s+Circular\b",
    r"Aclarada\s+por\s+Circular\b",
    r"Complementada\s+por\s+Circular\b",
]


def _extraer_notas_modificacion_desde_pdf(pdf_path: Path) -> List[str]:
    """Escanea las páginas iniciales del PDF extrayendo notas marginales de modificación posterior."""
    notas_encontradas: List[str] = []
    try:
        fitz_mod: Any = importlib.import_module("fitz")
        doc: Any = fitz_mod.open(str(pdf_path))
        try:
            num_pages: int = int(len(doc))
            pages_to_check: int = min(2, num_pages)
            # Las notas marginales de vigencia de la circular residen en la portada / primeras páginas
            for i in range(pages_to_check):
                page: Any = doc[i]
                blocks: List[Any] = list(page.get_text("blocks"))
                for b in blocks:
                    txt: str = str(b[4]).strip()
                    for patron in _PATRONES_MODIFICACION:
                        if re.search(patron, txt, re.IGNORECASE):
                            limpio: str = limpiar_palabras_ocr(txt)
                            limpio = re.sub(r"\s+", " ", limpio).strip()
                            if limpio and limpio not in notas_encontradas:
                                notas_encontradas.append(limpio)
                            break
        finally:
            doc.close()
    except Exception:
        pass
    return notas_encontradas



def _extraer_notas_modificacion_texto(texto: str) -> List[str]:
    """Busca notas marginales de modificación posterior en el texto libre."""
    texto_limpio = limpiar_palabras_ocr(texto)
    notas_encontradas: List[str] = []

    patron_bloque = re.search(
        r"Circular\s+Modificada\s+por\s*(?:\n\s*)?Circular\s+Ord\.?\s*N[°º\?]?\s*\d+[^\n]*(?:\n[^\n]*){0,4}\bDDU\s*\d+[^\n]*(?:\s*\([^\)]+\))?",
        texto_limpio,
        re.IGNORECASE,
    )
    if patron_bloque:
        bloque_texto = re.sub(r"\s+", " ", patron_bloque.group(0)).strip()
        notas_encontradas.append(bloque_texto)

    if not notas_encontradas:
        for patron in _PATRONES_MODIFICACION:
            matches = re.finditer(rf"{patron}[^\n]+", texto_limpio, re.IGNORECASE)
            for m in matches:
                nota = re.sub(r"\s+", " ", m.group(0)).strip()
                if nota and nota not in notas_encontradas:
                    notas_encontradas.append(nota)

    return notas_encontradas



@register_extractor
class ModificacionesPosterioresExtractor(BaseExtractor):
    """Extractor modular para notas marginales y timbres de modificación posterior de circulares DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "modificaciones_posteriores"

    def extract(
        self,
        raw_text: str,
        lines: List[str],
        pdf_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> ResultadoBloque:
        """Extrae las notas de modificación posterior como texto libre.

        Args:
            raw_text: Texto completo de la circular.
            lines: Lista de líneas limpias.
            pdf_path: Ruta opcional al archivo PDF.
            output_dir: Directorio opcional de salida.

        Returns:
            ResultadoBloque con el texto consolidado y lista de notas de modificación posterior.
        """
        notas: List[str] = []

        # 1. Si hay PDF, escanear todos los bloques del PDF
        if pdf_path is not None and pdf_path.exists():
            notas = _extraer_notas_modificacion_desde_pdf(pdf_path)

        # 2. Si no se encontraron o no hay PDF, analizar texto plano
        if not notas:
            texto_analizar = raw_text if raw_text else "\n".join(lines)
            if texto_analizar:
                notas = _extraer_notas_modificacion_texto(texto_analizar)

        texto_consolidado = "; ".join(notas) if notas else ""
        exito = len(notas) > 0

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "texto": texto_consolidado,
                "notas": notas,
            },
            confianza=1.0 if exito else 0.0,
            observaciones="Notas de modificación posterior extraídas" if exito else "No se detectaron notas de modificación posterior",
        )



def main() -> None:
    """Punto de entrada CLI para ModificacionesPosterioresExtractor."""
    parser = argparse.ArgumentParser(description="Extractor de Modificaciones Posteriores (Notas Marginales de Vigencia)")
    parser.add_argument("--pdf", type=str, help="Ruta al archivo PDF a procesar")
    parser.add_argument("--text", type=str, help="Texto plano a procesar")
    args = parser.parse_args()

    extractor = ModificacionesPosterioresExtractor()
    if args.pdf:
        pdf_path = Path(args.pdf)
        res = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)
        print(json.dumps(asdict(res), indent=2, ensure_ascii=False))
    elif args.text:
        res = extractor.extract(raw_text=args.text, lines=args.text.splitlines())
        print(json.dumps(asdict(res), indent=2, ensure_ascii=False))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
