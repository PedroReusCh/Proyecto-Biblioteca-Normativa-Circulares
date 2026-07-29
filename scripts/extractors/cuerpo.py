"""Extractor del cuerpo estructurado (secciones y párrafos) de circulares DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.ddu_types import SeccionDDU
from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


def _es_pie_de_pagina(line: str) -> bool:
    """Detecta líneas de pie de página de OCR incluso con espacios rotos entre caracteres."""
    line_norm = re.sub(r"\s+", " ", line).strip()
    patterns = [
        r"P[áa]\s*g\s*i\s*n\s*a\s*\d+",
        r"Minister\s*io\s+de\s+Vivienda",
        r"Alameda\s+924",
        r"Santiago\s*-\s*Chile",
        r"Gobierno\s+de\s+Chile",
    ]
    for p in patterns:
        if re.search(p, line_norm, re.IGNORECASE):
            return True
    return re.match(r"^!+$", line_norm) is not None


def _normalizar_romano_ocr(prefix: str, texto_titulo: str) -> str | None:
    """Diferencia entre números arábigos y romanos detectando errores de OCR (ej. 11. -> II. o l. -> I.)."""
    prefix_clean = prefix.lower().strip()

    # Si es número romano directo estricto (ej. I, II, III, IV, V, VI, VII, VIII, IX, X)
    if re.match(r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)$", prefix, re.IGNORECASE):
        return f"{prefix.upper()}."

    # Analizar si el texto del título es principalmente mayúsculas
    letras = [c for c in texto_titulo if c.isalpha()]
    es_mayusculas = len(letras) > 0 and (sum(1 for c in letras if c.isupper()) / len(letras) >= 0.65)

    if es_mayusculas:
        if prefix_clean in ("l", "i"):
            return "I."
        elif prefix_clean in ("11", "ll", "1l", "l1", "ii"):
            return "II."
        elif prefix_clean in ("111", "lll", "iii"):
            return "III."
        elif prefix_clean in ("iv", "v", "vi", "vii", "viii", "ix", "x"):
            return f"{prefix_clean.upper()}."

    return None


@register_extractor
class CuerpoExtractor(BaseExtractor):
    """Extractor para el cuerpo estructurado por secciones y párrafos."""

    @property
    def nombre_bloque(self) -> str:
        return "cuerpo"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae las secciones y párrafos estructurados del cuerpo de la circular DDU.

        Localiza ambos marcadores A:/PARA: y DE: (en cualquier orden) y comienza
        la extracción del cuerpo a partir de la línea siguiente al segundo marcador.
        La extracción se detiene al encontrar la fórmula de cierre (firma o distribución).

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la lista de SeccionDDU extraída.
        """
        # Fase 1: Localizar posiciones de A:/PARA: y DE: para determinar inicio del cuerpo
        idx_a: int = -1
        idx_de: int = -1
        scan_limit = min(50, len(lines))

        for i in range(scan_limit):
            line = lines[i]
            if idx_a == -1 and re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*.+$", line, re.IGNORECASE):
                m_check = re.match(r"^(?:A(?:\s|:)|PARA\s*:)\s*:?\s*(.+)$", line, re.IGNORECASE)
                if m_check and not re.match(r"^LA\s+FECHA", m_check.group(1).strip(), re.IGNORECASE):
                    idx_a = i
            if idx_de == -1:
                match_de = re.match(r"^DE\s*:\s*(.+)$", line, re.IGNORECASE)
                if not match_de:
                    match_de = re.match(
                        r"^DE\s+((?:JEFE|MINISTRO|SUBSECRETARI[OA]|DIRECTOR|DIVISI[ÓO]N)\b.+)$",
                        line,
                        re.IGNORECASE,
                    )
                if match_de:
                    idx_de = i

        # El cuerpo comienza después del segundo marcador (el que aparece último)
        if idx_a != -1 and idx_de != -1:
            inicio_cuerpo = max(idx_a, idx_de) + 1
        elif idx_de != -1:
            inicio_cuerpo = idx_de + 1
        elif idx_a != -1:
            inicio_cuerpo = idx_a + 1
        else:
            inicio_cuerpo = 0

        # Fase 2: Extraer secciones y párrafos del cuerpo
        secciones: List[SeccionDDU] = []
        seccion_actual: SeccionDDU = {"titulo": "", "parrafos": []}
        parrafo_actual = ""

        for line in lines[inicio_cuerpo:]:
            line_clean = line.strip()
            if not line_clean:
                continue

            # Descartar líneas de pie de página de OCR (incluyendo espacios rotos)
            if _es_pie_de_pagina(line_clean):
                continue

            # Detener extracción si llegamos a la firma o distribución
            if re.match(r"^Saluda\s+atentamente\s+a\s+Ud", line_clean, re.IGNORECASE) or re.match(
                r"^(?:DISTRIBUCI[ÓO]N|BUCI[ÓO]N|STRIBUCI[ÓO]N)[\s:]*", line_clean, re.IGNORECASE
            ):
                break

            # Omitir metadatos de cabecera si aún no hemos comenzado ningún párrafo/sección
            if not parrafo_actual and not secciones and not seccion_actual["titulo"]:
                if re.match(
                    r"^(?:DDU|CIRCULAR|ORD\.|ORO\.|ANT|MAT|DE|A|PARA|SANTIAGO|VALPARA[ÍI]SO|PERMISOS)\b",
                    line_clean,
                    re.IGNORECASE,
                ) or re.match(r"^\d+\)", line_clean):
                    continue

            # Detectar número romano o distorsión OCR de sección (ej. "I. ANTECEDENTES", "11. NORMATIVA APLICABLE")
            match_romano = re.match(r"^([IVXLCDM]+|l+|11+|1l|l1)\.\s+(.+)$", line_clean, re.IGNORECASE)
            if match_romano:
                prefijo, texto_titulo = match_romano.group(1), match_romano.group(2).strip()
                romano_norm = _normalizar_romano_ocr(prefijo, texto_titulo)
                if romano_norm is not None:
                    if parrafo_actual:
                        seccion_actual["parrafos"].append(parrafo_actual)
                        parrafo_actual = ""

                    if seccion_actual["titulo"] or seccion_actual["parrafos"]:
                        secciones.append(seccion_actual)

                    seccion_actual = {
                        "titulo": f"{romano_norm} {texto_titulo}",
                        "parrafos": [],
                    }
                    continue

            # Detectar número arábigo al inicio (ej. "1. De conformidad...", "2. MARCO NORMATIVO:")
            match_parrafo = re.match(r"^(\d+)\.\s+(.+)$", line_clean)
            if match_parrafo:
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual)

                parrafo_actual = f"{match_parrafo.group(1)}. {match_parrafo.group(2).strip()}"
                continue

            # Concatenar a párrafo actual
            if parrafo_actual:
                parrafo_actual += " " + line_clean
            else:
                parrafo_actual = line_clean

        if parrafo_actual:
            seccion_actual["parrafos"].append(parrafo_actual)

        if seccion_actual["titulo"] or seccion_actual["parrafos"]:
            secciones.append(seccion_actual)

        exito = len(secciones) > 0 and any(len(s["parrafos"]) > 0 for s in secciones)

        partes_cuerpo: List[str] = []
        for sec in secciones:
            titulo = str(sec.get("titulo", "")).strip()
            parrafos = " ".join(sec.get("parrafos", [])).strip()
            if titulo and parrafos:
                partes_cuerpo.append(f"{titulo}: {parrafos}")
            elif parrafos:
                partes_cuerpo.append(parrafos)
            elif titulo:
                partes_cuerpo.append(titulo)

        cuerpo_texto = " | ".join(partes_cuerpo)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "secciones": secciones,
                "cuerpo": cuerpo_texto,
            },
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se extrajeron secciones del cuerpo de la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Cuerpo Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = CuerpoExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
