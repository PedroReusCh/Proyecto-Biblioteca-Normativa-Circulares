"""Extractor del metadato Nota al Pie (notas explicativas y referencias bibliográficas de pie de página)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
import sys
from typing import Any, List

_PROYECTO_RAIZ = Path(__file__).resolve().parents[2]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

try:
    from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
except ImportError:
    from extractors.base import BaseExtractor, ResultadoBloque, register_extractor


def _limpiar_palabras_divididas_ocr(texto: str) -> str:
    """Re-ensambla palabras fragmentadas por espacios de escaneo/OCR."""
    # 1. Anglicismos y palabras compuestas específicas
    texto = re.sub(r"\bcon\s+tain\s+ers\b", "containers", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bcon\s+tainers\b", "containers", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bcontain\s+ers\b", "containers", texto, flags=re.IGNORECASE)

    # 2. Sufijos terminados en 'ción' / 'ciones' (ej: edificac ión -> edificación)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+(i[óo]n|iones)\b", r"\1\2", texto, flags=re.IGNORECASE)

    # 3. Sufijos terminados en 'lo' / 'los' (ej: artícu lo -> artículo)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+tícu)\s+(lo|los)\b", r"\1\2", texto)

    # 4. Plurales y terminaciones comunes en 'res', 'les', 'nes', 'dos', 'das', 'tos', 'tas', 'nicos', 'mente'
    texto = re.sub(
        r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|mente|nicos|nica|nicas)\b",
        r"\1\2",
        texto,
    )

    # 5. Letra aislada al final de palabra (ej: carácte r -> carácter)
    texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", texto)

    return re.sub(r"\s+", " ", texto).strip()


@register_extractor
class NotaAlPieExtractor(BaseExtractor):
    """Extractor de notas aclaratorias y referencias normativas al pie de página."""

    @property
    def nombre_bloque(self) -> str:
        return "nota_al_pie"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la lista concatenada de notas aclaratorias al pie de página de la circular DDU.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la cadena de notas al pie extraídas.
        """
        notas: List[str] = []
        nota_actual_lines: List[str] = []

        def _guardar_nota_actual() -> None:
            if nota_actual_lines:
                texto_completo = " ".join(nota_actual_lines).strip()
                texto_completo = _limpiar_palabras_divididas_ocr(texto_completo)
                if texto_completo:
                    notas.append(texto_completo)
                nota_actual_lines.clear()

        for line in lines:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Detener si llegamos al pie institucional o firma/cierre de página
            if re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE) or re.search(
                r"(?:Saluda\s+atent|DISTRIBUCI[ÓO\?I\s]+N|GOBIERNO\s+DE\s+CHILE)", line_clean, re.IGNORECASE
            ):
                _guardar_nota_actual()
                continue

            match_nota = re.match(r"^(\d{1,2})\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\.,\(\)\"\'-].+)$", line_clean)
            if match_nota:
                num_nota = match_nota.group(1)
                texto_nota = match_nota.group(2).strip()

                if int(num_nota) <= 20 and not line_clean.startswith(f"{num_nota}. "):
                    if not re.match(r"^\d+\s+(?:de\s+la|de\s+los|del|en\s+la|con\s+la|que|por|para)\b", line_clean, re.IGNORECASE):
                        if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley|Construcci[óo]n|Edificaci[óo]n|OGUC|LGUC)\b", texto_nota, re.IGNORECASE):
                            _guardar_nota_actual()
                            nota_actual_lines.append(f"{num_nota} {texto_nota}")
                            continue

            # Si hay una nota en curso, acumular las líneas continuas
            if nota_actual_lines:
                nota_actual_lines.append(line_clean)

        _guardar_nota_actual()

        notas_texto = " | ".join(notas) if notas else ""
        notas_texto = _limpiar_palabras_divididas_ocr(notas_texto)
        exito = bool(notas_texto)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"notas_al_pie": notas_texto},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se identificaron notas al pie de página en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Nota al Pie Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
