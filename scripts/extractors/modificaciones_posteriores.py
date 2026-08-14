"""Extractor modular de Modificaciones Posteriores y Notas Marginales de Vigencia (ModificacionesPosterioresExtractor)."""

import argparse
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional

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
    r"Circular\s+Modificada\s+por\b[^\n]+",
    r"Modificada\s+por\s+Circular\b[^\n]+",
    r"Dejada\s+sin\s+efecto\s+por\s+Circular\b[^\n]+",
    r"Dejada\s+sin\s+efecto\s+por\b[^\n]+",
    r"Aclarada\s+por\s+Circular\b[^\n]+",
    r"Complementada\s+por\s+Circular\b[^\n]+",
]


def _extraer_notas_modificacion_texto(texto: str) -> List[str]:
    """Busca notas marginales o timbres de modificación posterior en el texto libre."""
    texto_limpio = limpiar_palabras_ocr(texto)
    notas_encontradas: List[str] = []

    # 1. Búsqueda de bloque multilínea de nota marginal típica de DDU (ej. Página 1 de DDU 456)
    patron_bloque = re.search(
        r"Circular\s+Modificada\s+por\s*(?:\n\s*)?Circular\s+Ord\.?\s*N[°º\?]?\s*\d+[^\n]*(?:\n[^\n]*){0,3}\bDDU\s*\d+[^\n]*",
        texto_limpio,
        re.IGNORECASE,
    )
    if patron_bloque:
        bloque_texto = re.sub(r"\s+", " ", patron_bloque.group(0)).strip()
        notas_encontradas.append(bloque_texto)

    # 2. Búsqueda línea por línea de otros patrones de modificación posterior
    if not notas_encontradas:
        for patron in _PATRONES_MODIFICACION:
            matches = re.finditer(patron, texto_limpio, re.IGNORECASE)
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
        # Si no hay texto pero hay PDF, extraer texto de las primeras páginas
        texto_analizar = raw_text
        if (not texto_analizar or len(texto_analizar) < 50) and pdf_path is not None and pdf_path.exists():
            try:
                import importlib
                pypdf_mod: Any = importlib.import_module("pypdf")
                reader = pypdf_mod.PdfReader(pdf_path)
                # Las notas marginales de vigencia se ubican típicamente en la primera página
                texto_analizar = "\n".join([str(p.extract_text() or "") for p in reader.pages[:2]])
            except Exception:
                texto_analizar = raw_text

        notas = _extraer_notas_modificacion_texto(texto_analizar)
        if not notas and lines:
            # Intentar también uniendo las primeras 40 líneas
            notas = _extraer_notas_modificacion_texto("\n".join(lines[:40]))

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
