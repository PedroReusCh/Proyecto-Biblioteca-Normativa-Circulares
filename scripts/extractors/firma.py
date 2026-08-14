"""Extractor de la firma y firmante de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
from scripts.extractors.utils_cleaner import _preservar_casing, limpiar_palabras_ocr


def _limpiar_texto_firma(texto: str) -> str:
    """Repara distorsiones típicas de OCR en nombres, cargos y ministerios del firmante."""
    texto = limpiar_palabras_ocr(texto)
    texto = re.sub(r"\bN\s+DIEGO\s+ZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bN\s+DIEGO\s+IZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bD\s+VISI[ÓO\?I\ufffd\s]+N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bDIVISI[ÓO\?I\ufffd\s]+N\b", lambda m: _preservar_casing(m.group(0), "División"), texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bIS\s+RIO\b", "MINISTERIO", texto, flags=re.IGNORECASE)
    return texto


def _es_nombre_persona(line: str) -> bool:
    """Evalúa si una cadena de texto tiene el formato de un nombre de persona válido (2 o más palabras)."""
    palabras_descarte = {
        "MOTIVO", "CONSIDERACIONES", "MATERIA", "MATERIAS", "OBSERVACIONES",
        "ANTECEDENTES", "CIRCULAR", "TABLA", "CUADRO", "MODIFICA", "MODIFICAN",
        "DISTRIBUCION", "DISTRIBUCIÓN", "MINISTERIO", "VIVIENDA", "URBANISMO",
        "DIVISIÓN", "DIVISION", "DESARROLLO", "URBANO", "GOBIERNO", "CHILE",
        "ORD", "DDU", "OFPA", "ANT", "MAT", "DE", "A", "PARA", "SANTIAGO",
        "SALUDA", "ATENTAMENTE", "PÁGINA", "PAGINA", "FECHA", "SUBSECRETARIO",
        "SUBSECRETARIA", "MINISTRO", "MINISTRA", "CONTRALOR", "CONTRALORA",
    }
    line_clean = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", " ", line).strip()
    tokens = [w for w in line_clean.split() if len(w) >= 2 and w[0].isupper()]
    if len(tokens) < 2:
        return False
    # No debe contener palabras exclusivas de cargos/organismos
    if any(t.upper() in palabras_descarte for t in tokens):
        return False
    return True



@register_extractor
class FirmaExtractor(BaseExtractor):
    """Extractor para identificar el firmante (nombre y cargo estructurado) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "firma"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la información del firmante de la circular DDU con nombre y cargo separados.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con firmante, nombre_firmante y cargo_firmante.
        """
        nombre_str = ""
        cargo_str = ""
        patron_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )
        palabras_descarte = {
            "MOTIVO", "CONSIDERACIONES", "MATERIA", "MATERIAS", "OBSERVACIONES",
            "ANTECEDENTES", "CIRCULAR", "TABLA", "CUADRO", "MODIFICA", "MODIFICAN",
        }

        # 1. Buscar patrón "Saluda atentamente..." y extraer las líneas de la firma
        idx_saludo = -1
        for i, line in enumerate(lines):
            if re.search(r"Saluda\s+atentamente", line, re.IGNORECASE) or re.search(
                r"^Atentamente\b", line, re.IGNORECASE
            ):
                idx_saludo = i
                break

        cargos_patron = r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA]|DIVISI[ÓO\?I\ufffd\s]+N\s+DE\s+DESARROLLO\s+URBANO)"

        if idx_saludo != -1:
            partes_firma: List[str] = []
            for line in lines[idx_saludo + 1 : idx_saludo + 16]:
                line_clean = line.strip()
                if not line_clean:
                    continue
                # Detener si llegamos al bloque de distribución o pie de página institucional
                if re.match(
                    patron_distribucion,
                    line_clean,
                    re.IGNORECASE,
                ) or re.search(r"Ministerio\s+de\s+Vivienda\s+y\s+Urbanismo\s*-\s*Alameda", line_clean, re.IGNORECASE):
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
                    partes_firma.append(_limpiar_texto_firma(line_clean))

            if partes_firma:
                # 1.1 Localizar línea del cargo
                idx_cargo = -1
                for j, p in enumerate(partes_firma):
                    if re.search(cargos_patron, p, re.IGNORECASE):
                        idx_cargo = j
                        cargo_str = p
                        # Si hay continuación del cargo o ministerio en la línea siguiente
                        if j + 1 < len(partes_firma) and re.search(r"MINISTERIO\s+DE\s+VIVIENDA", partes_firma[j + 1], re.IGNORECASE):
                            cargo_str += ", " + partes_firma[j + 1]
                        break

                # 1.2 Buscar candidato a nombre o identificador de firmante prioritariamente arriba del cargo
                lineas_previas = partes_firma[:idx_cargo] if idx_cargo != -1 else partes_firma
                for p in reversed(lineas_previas):
                    candidato = _limpiar_texto_firma(p)
                    # A) Nombre completo de persona (2 o más palabras)
                    if _es_nombre_persona(candidato) or re.search(r"JUAN\s+DIEGO|VICENTE|PAZ|RODRIGO", candidato, re.IGNORECASE):
                        nombre_limpio = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", candidato).strip()
                        nombre_str = nombre_limpio
                        break
                    # B) Sigla / identificador alfabético de rúbrica (ej. JPB)
                    m_sigla = re.search(r"\b([A-Z]{2,4})\b", candidato)
                    if m_sigla and m_sigla.group(1).upper() not in {"DDU", "ORD", "PDF", "MINVU", "IS", "RIO"}:
                        nombre_str = m_sigla.group(1).upper()
                        break

                # Si aún no hay nombre y hay líneas posteriores al cargo
                if not nombre_str and idx_cargo != -1 and idx_cargo + 1 < len(partes_firma):
                    for p in partes_firma[idx_cargo + 1:]:
                        if re.search(r"MINISTERIO", p, re.IGNORECASE):
                            continue
                        candidato = _limpiar_texto_firma(p)
                        if _es_nombre_persona(candidato):
                            nombre_str = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", candidato).strip()
                            break

                # Si no encontramos cargo formal pero hay líneas limpias
                if not cargo_str and partes_firma:
                    partes_limpias = [
                        p for p in partes_firma
                        if not re.search(r"[\/\~\*\<\>\(\)\;\\]", p)
                        and len(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]{3,}\b", p)) > 0
                        and not any(w in p.upper() for w in palabras_descarte)
                    ]
                    if partes_limpias:
                        cargo_str = ", ".join(partes_limpias)


        # 2. Si falta cargo o nombre, verificar cabecera DE: en las primeras páginas
        if not cargo_str or not nombre_str:
            for line in lines[:30]:
                line_clean = line.strip()
                m_de = re.search(r"^\s*DE\s*:\s*(.+)$", line_clean, re.IGNORECASE)
                if not m_de:
                    m_de = re.search(r"^\s*DE\s+((?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI|SECRETARI)[A-ZÁÉÍÓÚÑ\s]{5,})", line_clean, re.IGNORECASE)
                if m_de:
                    texto_de = m_de.group(1).strip().rstrip(".")
                    partes_de = [p.strip() for p in re.split(r"[,–—\-]", texto_de) if p.strip()]
                    for p_de in partes_de:
                        p_de_limpio = _limpiar_texto_firma(p_de)
                        if not nombre_str and _es_nombre_persona(p_de_limpio):
                            nombre_str = p_de_limpio
                        elif not cargo_str and re.search(cargos_patron, p_de_limpio, re.IGNORECASE):
                            cargo_str = p_de_limpio

        # 3. Limpieza final y normalización
        nombre_str = _limpiar_texto_firma(nombre_str).strip()
        cargo_str = _limpiar_texto_firma(cargo_str).strip()

        if nombre_str and cargo_str:
            firmante = f"{nombre_str}, {cargo_str}"
        elif nombre_str:
            firmante = nombre_str
        else:
            firmante = cargo_str

        firmante = re.sub(r"\s+", " ", firmante).strip()
        if firmante.endswith("."):
            firmante = firmante[:-1].strip()

        exito = bool(firmante)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "firmante": firmante,
                "nombre_firmante": nombre_str,
                "cargo_firmante": cargo_str,
            },
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
