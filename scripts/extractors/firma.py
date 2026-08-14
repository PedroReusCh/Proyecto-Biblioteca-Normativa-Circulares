"""Extractor de la firma y firmante de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
from scripts.extractors.utils_cleaner import limpiar_palabras_ocr


def _limpiar_texto_firma(texto: str) -> str:
    """Repara distorsiones típicas de OCR en nombres, cargos y ministerios del firmante."""
    texto = limpiar_palabras_ocr(texto)
    texto = re.sub(r"\bN\s+DIEGO\s+ZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bN\s+DIEGO\s+IZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bD\s*VISI[ÓO\?I\ufffd\s]+N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bDIVISI[ÓO\?I\ufffd\s]+N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bIS\s+RIO\b", "MINISTERIO", texto, flags=re.IGNORECASE)
    return texto


@register_extractor
class FirmaExtractor(BaseExtractor):
    """Extractor para identificar el firmante (nombre y cargo) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "firma"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la información del firmante de la circular DDU.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con el firmante extraído.
        """
        firmante = ""
        patron_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )
        palabras_descarte = {
            "MOTIVO", "CONSIDERACIONES", "MATERIA", "MATERIAS", "OBSERVACIONES",
            "ANTECEDENTES", "CIRCULAR", "TABLA", "CUADRO", "MODIFICA", "MODIFICAN"
        }

        # 1. Buscar patrón "Saluda atentamente..." y extraer las líneas siguientes
        idx_saludo = -1
        for i, line in enumerate(lines):
            if re.search(r"Saluda\s+atentamente", line, re.IGNORECASE) or re.search(
                r"^Atentamente\b", line, re.IGNORECASE
            ):
                idx_saludo = i
                break

        if idx_saludo != -1:
            partes_firma: List[str] = []
            for line in lines[idx_saludo + 1 : idx_saludo + 16]:
                line_clean = line.strip()
                if not line_clean:
                    continue
                # Detener si llegamos al bloque de distribución o pie de página
                if re.match(
                    patron_distribucion,
                    line_clean,
                    re.IGNORECASE,
                ) or re.search(r"Ministerio\s+de\s+Vivienda", line_clean, re.IGNORECASE):
                    break

                # Descartar cabeceras de tabla o textos residuales
                palabras_linea = set(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]+\b", line_clean.upper()))
                if palabras_linea and palabras_linea.issubset(palabras_descarte):
                    continue
                if re.match(r"^[\d\/\-\(\)\,\.\s\:\_~|]+$", line_clean):
                    continue

                # Limpiar caracteres ruidosos de firma o sellos de OCR
                line_clean = re.sub(r"^[_\s\-|\.\~:]+", "", line_clean).strip()
                if line_clean:
                    partes_firma.append(line_clean)

            if partes_firma:
                # Buscar si alguna línea contiene un cargo formal
                cargos_patron = r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA])\s+(?:DIVISI[ÓO\?I\ufffd\s]+N|GENERAL|DE)?\b"
                idx_cargo = -1
                for j, p in enumerate(partes_firma):
                    if re.search(cargos_patron, p, re.IGNORECASE):
                        idx_cargo = j
                        break

                if idx_cargo != -1:
                    cargo_str = partes_firma[idx_cargo]
                    nombre_str = ""
                    if idx_cargo > 0:
                        candidato_nombre = partes_firma[idx_cargo - 1]
                        if not any(w in candidato_nombre.upper() for w in palabras_descarte):
                            nombre_limpio = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", candidato_nombre).strip()
                            palabras = nombre_limpio.split()
                            # Si es un nombre de persona real (al menos 2 palabras de longitud >= 3) y sin siglas
                            if len(palabras) >= 2 and all(len(w) >= 3 for w in palabras) and not re.search(r"\b(?:JPB|OFPA|DDU|ORD|MINVU)\b", nombre_limpio, re.IGNORECASE):
                                nombre_str = nombre_limpio
                    firmante = f"{nombre_str}, {cargo_str}".strip(", ") if nombre_str else cargo_str


                else:
                    partes_limpias = [
                        p for p in partes_firma
                        if not re.search(r"[\/\~\*\<\>\(\)\;\\]", p)
                        and len(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]{3,}\b", p)) > 0
                        and not any(w in p.upper() for w in palabras_descarte)
                    ]
                    if partes_limpias:
                        firmante = ", ".join(partes_limpias)


        # 2. Si no se encontró mediante saludo o era ruido OCR, buscar patrones de emisor/cargo
        if not firmante:
            for line in lines[:25]:
                line_clean = line.strip()
                match_em = re.search(r"^\s*DE\s+([A-ZÁÉÍÓÚÑ\s]{6,})", line_clean)
                if match_em:
                    cargo_raw = match_em.group(1).strip().rstrip(".")
                    if re.search(r"^(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI|SECRETARI)", cargo_raw):
                        firmante = cargo_raw
                        break



        if not firmante:
            cargos_patron = r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA])\s+(?:DIVISI[ÓO]N|GENERAL|DE)?\b"
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if re.search(cargos_patron, line_clean, re.IGNORECASE) and not re.match(r"^DE\s*:", line_clean, re.IGNORECASE):
                    prev_line = lines[i - 1].strip() if i > 0 else ""
                    if re.match(r"^[A-ZÁÉÍÓÚÑ\s]{4,}$", prev_line) and not re.search(r"MINISTERIO|CIRCULAR|DISTRIBUCION", prev_line):
                        firmante = f"{prev_line}, {line_clean}"
                        break
                    elif re.match(r"^[A-ZÁÉÍÓÚÑ\s]{4,}$", line_clean):
                        firmante = line_clean
                        break

        firmante = _limpiar_texto_firma(firmante)
        firmante = re.sub(r"\s+", " ", firmante).strip()
        if firmante.endswith("."):
            firmante = firmante[:-1].strip()

        exito = bool(firmante)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={"firmante": firmante},
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró firmante en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Firma Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = FirmaExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
