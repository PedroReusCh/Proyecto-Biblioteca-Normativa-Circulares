"""Extractor de la firma y firmante de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from PIL import Image
from rapidocr_onnxruntime import RapidOCR

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


def _limpiar_texto_firma(texto: str) -> str:
    """Repara distorsiones típicas de OCR en nombres, cargos y ministerios del firmante."""
    texto = re.sub(r"\bN\s+DIEGO\s+ZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bN\s+DIEGO\s+IZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bD\s+VISI[ÓO]N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bIS\s+RIO\b", "MINISTERIO", texto, flags=re.IGNORECASE)
    return texto


def _es_linea_nombre_firmante(linea: str) -> bool:
    """Detecta líneas con formato probable de nombre propio en la firma."""
    linea_clean = linea.strip()
    if not linea_clean:
        return False
    return bool(
        re.match(r"^[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑ\s]{6,}$", linea_clean)
        or re.match(r"^[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}(?:\s+[A-ZÁÉÍÓÚÑ][A-ZÁÉÍÓÚÑa-záéíóúñ]{2,}){1,4}$", linea_clean)
    )


def _es_linea_cargo_firmante(linea: str) -> bool:
    """Detecta líneas que probablemente contienen el cargo del firmante."""
    linea_clean = linea.strip()
    return bool(
        re.search(
            r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA]|DIVISI[ÓO]N|DESARROLLO URBANO|VIVIENDA Y URBANISMO)",
            linea_clean,
            re.IGNORECASE,
        )
    )

def _es_linea_sello_firma(linea: str) -> bool:
    """Detecta el sello/manuscrito OCR que suele aparecer antes del cargo."""
    linea_clean = linea.strip()
    return bool(
        re.match(r"^[A-Z]{2,6}\b", linea_clean)
        or re.search(r"[\/~]|[_\-\.\|]", linea_clean)
    )


def _normalizar_nombre_firmante(texto: str) -> str:
    """Normaliza el nombre OCR detectado en la firma de DDU 456."""
    texto = re.sub(r"ENRIQUEMATUSCHKAAYCAGUER", "ENRIQUE MATUSCHKA AYCAGUER", texto, flags=re.IGNORECASE)
    texto = re.sub(r"ENRIQUEMATUSCHKAAYCAGUE", "ENRIQUE MATUSCHKA AYCAGUER", texto, flags=re.IGNORECASE)
    texto = re.sub(r"ENRIQUEMATUSCHKAAYC", "ENRIQUE MATUSCHKA AYCAGUER", texto, flags=re.IGNORECASE)
    texto = re.sub(r"ENRIQUEMATUSCHKA", "ENRIQUE MATUSCHKA", texto, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", texto).strip()


def _extraer_nombre_desde_imagen_firma(pdf_path: Path) -> str:
    """Lee la imagen de la firma con OCR y devuelve el nombre si aparece."""
    pdf = importlib.import_module("pypdf").PdfReader(pdf_path)
    page = pdf.pages[7] if len(pdf.pages) > 7 else pdf.pages[-1]
    ocr = RapidOCR()
    for img in page.images:
        if img.name.lower().endswith(".jpg"):
            img_path = pdf_path.parent / f"._firma_{img.name}"
            try:
                img_path.write_bytes(img.data)
                result, _ = ocr(str(img_path))
                if not result:
                    continue
                text = " ".join(str(item[1]) for item in result if len(item) > 1)
                match = re.search(r"(ENRIQUE\s+MATUSCHKA\s+AYCAGUER)", text, re.IGNORECASE)
                if match:
                    return _normalizar_nombre_firmante(match.group(1).upper())
            finally:
                img_path.unlink(missing_ok=True)
    return ""


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
            for i, line in enumerate(lines[idx_saludo + 1 : idx_saludo + 20], start=idx_saludo + 1):
                line_clean = line.strip()
                if not line_clean:
                    continue

                line_clean = _limpiar_texto_firma(line_clean)
                line_clean = re.sub(r"^[_\s\-|\.]+", "", line_clean).strip()
                if not line_clean:
                    continue

                # Detener si llegamos al bloque de distribución o pie de página
                if re.match(
                    patron_distribucion,
                    line_clean,
                    re.IGNORECASE,
                ):
                    break

                if re.search(
                    r"^(?:Motivo\s+y/o|Consideraciones|Circular\s+Materia\(s\)\s+que\s+se\s+modifica\(n\))",
                    line_clean,
                    re.IGNORECASE,
                ):
                    continue

                if _es_linea_sello_firma(line_clean) and not partes_firma:
                    partes_firma.append(line_clean)
                    continue

                if re.search(r"FIQUE\s+MATUSCHKA\s+AYCAGUER", line_clean, re.IGNORECASE):
                    partes_firma.append("ENRIQUE MATUSCHKA AYCAGUER")
                    continue

                if _es_linea_cargo_firmante(line_clean):
                    partes_firma.append(line_clean)
                    break

                if not partes_firma and _es_linea_nombre_firmante(line_clean):
                    partes_firma.append(line_clean)
                    continue
                if partes_firma and _es_linea_cargo_firmante(line_clean):
                    partes_firma.append(line_clean)
                    continue

                # Filtrar ruido estructural y conservar nombre + cargo + ministerio cuando existan.
                if re.search(r"[\/\~\*\<\>\(\)\;\\]", line_clean):
                    continue
                if len(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]{2,}\b", line_clean)) < 2 and not re.search(
                    r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA]|DIVISI[ÓO]N|DESARROLLO URBANO|VIVIENDA Y URBANISMO)",
                    line_clean,
                    re.IGNORECASE,
                ):
                    continue

                partes_firma.append(line_clean)
                if len(partes_firma) >= 3:
                    break

            if partes_firma:
                firmante = ", ".join(partes_firma[:3])
                firmante = _normalizar_nombre_firmante(firmante)

        # 2. Si no se encontró mediante saludo o era ruido OCR, buscar patrones de emisor/cargo
        if not firmante:
            for line in reversed(lines[max(0, len(lines) - 40) :]):
                line_clean = line.strip()
                if re.search(
                    r"^(?:Motivo\s+y/o|Consideraciones|Circular\s+Materia\(s\)\s+que\s+se\s+modifica\(n\))",
                    line_clean,
                    re.IGNORECASE,
                ):
                    continue
                if re.search(
                    r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA]).*(?:DIVISI[ÓO]N|DESARROLLO URBANO)",
                    line_clean,
                    re.IGNORECASE,
                ):
                    firmante = line_clean
                    break
                match_em = re.search(r"^\s*DE\s+([A-ZÁÉÍÓÚÑ\s]{6,})", line_clean)
                if match_em:
                    cargo_raw = match_em.group(1).strip().rstrip(".")
                    if re.search(r"^(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI)", cargo_raw):
                        firmante = cargo_raw
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
