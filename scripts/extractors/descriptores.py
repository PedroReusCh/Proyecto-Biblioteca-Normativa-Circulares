"""Extractor de metadato Descriptores / Vocablos (Palabras clave)."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class DescriptoresExtractor(BaseExtractor):
    """Extractor de descriptores / vocablos de materia en la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "descriptores"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la lista o cadena de descriptores del encabezado.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los descriptores extraídos.
        """
        desc_lineas: List[str] = []
        en_descriptores = False

        # Iniciar escaneo tras la materia / antecedentes / circular para omitir ruido de membrete
        idx_inicio = 0
        for i in range(min(15, len(lines))):
            line_str = lines[i].strip()
            if re.match(r"^(?:MAT\s*:|ANT\s*:|CIRCULAR\s+ORD|DDU\s+\d+|ORD\b)", line_str, re.IGNORECASE):
                idx_inicio = i + 1

        def _es_linea_descriptor(line_clean: str) -> bool:
            # Excluir remitentes, destinatarios, fechas, materias y encabezados institucionales
            if re.match(r"^(?:A\b|DE\s+(?:JEFE|MINISTRO|SUBSECRETARI|DIRECTOR|SECRETARI|DIVISI[ÓO]N)|DE\s*:)\b", line_clean, re.IGNORECASE):
                return False
            if re.match(r"^(?:DDU|CIRCULAR|ORD\b|ORO\b|ANT\b|MAT\b|SANTIAGO|VALPARA[ÍI]SO|COMPLEMENTA|TRABAJANDO|GOBIERNO|MINISTERIO)\b", line_clean, re.IGNORECASE):
                return False
            if re.match(r"^\d+\.", line_clean):
                return False

            letras = [c for c in line_clean if c.isalpha()]
            if not letras:
                return False
            prop_mayus = sum(1 for c in letras if c.isupper()) / len(letras)
            return prop_mayus >= 0.65

        for line in lines[idx_inicio:35]:
            line_clean = line.strip()
            if not line_clean:
                continue

            match_exp = re.match(
                r"^(?:DESCRIPTORES|VOCABLOS|PALABRAS\s+CLAVE)\.?(?:\s*:\s*|\s+)(.+)$",
                line_clean,
                re.IGNORECASE,
            )
            if match_exp:
                desc_lineas.append(match_exp.group(1).strip())
                en_descriptores = True
                continue

            if _es_linea_descriptor(line_clean):
                desc_lineas.append(line_clean)
                en_descriptores = True
            elif en_descriptores:
                if re.match(r"^(?:DE\s+(?:JEFE|MINISTRO|SUBSECRETARI|DIRECTOR|SECRETARI|DIVISI[ÓO]N)|DE\s*:|A\s*:|SANTIAGO|VALPARA[ÍI]SO)\b", line_clean, re.IGNORECASE):
                    break


        descriptores = " ".join(desc_lineas)
        descriptores = re.sub(r"\s+", " ", descriptores).strip()
        exito = bool(descriptores)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"descriptores": descriptores},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se identificaron descriptores en el documento.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Descriptores Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = DescriptoresExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
