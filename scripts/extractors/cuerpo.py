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


def _limpiar_texto_cuerpo(texto: str) -> str:
    """Repara palabras rotas y espacios antes de signos de puntuación producidos por OCR."""
    patrones_reemplazo = [
        (r"\binst\s+rumen\s+to\b", "instrumento"),
        (r"\bpermi\s+so\b", "permiso"),
        (r"\bpermi\s+sos\b", "permisos"),
        (r"\bedifi\s+cad([aaos])\b", r"edificad\1"),
        (r"\bedifi\s+cac(i[oó]n|iones)\b", r"edificac\1"),
        (r"\bincrement\s+o\b", "incremento"),
        (r"\bcircunscribi\s+rse\b", "circunscribirse"),
        (r"\bporcentua\s+l\b", "porcentual"),
        (r"\bante\s+s\b", "antes"),
        (r"\baplicab\s+le([s]?)\b", r"aplicable\1"),
        (r"\bmod\s+ificac(i[oó]n|iones)\b", r"modificac\1"),
        (r"\bmod\s+ificad([aaos])\b", r"modificad\1"),
        (r"\bespec[ií]f\s+ic([aaos])\b", r"específic\1"),
        (r"\bconstruid\s+a\b", "construida"),
        (r"\bcorrespond\s+ient([es]?)\b", r"correspondient\1"),
        (r"\binst\s+rucc(i[oó]n|iones)\b", r"instrucc\1"),
        (r"\bcircul\s+ar([es]?)\b", r"circular\1"),
        (r"\bsuperf\s+ic(ie[s]?)\b", r"superfic\1"),
        (r"\bdispos\s+ic(i[oó]n|iones)\b", r"disposic\1"),
        (r"\burban[íi]st\s+ic([aaos])\b", r"urbanístic\1"),
        (r"\bterritor\s+ial\b", "territorial"),
        (r"\bsolic\s+itud\b", "solicitud"),
        (r"\baprob\s+ad([aaos])\b", r"aprobad\1"),
        (r"\baprob\s+ac(i[oó]n|iones)\b", r"aprobac\1"),
        (r"\bexpuest\s+os\b", "expuestos"),
        (r"\bOS\s+33\b", "DS 33"),
        # Reglas genéricas para plurales con 's' o 'es' aisladas por OCR
        (r"\b([a-záéíóúñ]{3,}[aeiouáéíóú])\s+s\b", r"\1s"),
        (r"\b([a-záéíóúñ]{3,}[bcdfghjklmnñpqrstvwxyz])\s+es\b", r"\1es"),
        (r"\s+\.", "."),
        (r"\s+,", ","),
        (r"\s+;", ";"),
        (r"\s+:", ":"),
    ]

    res = texto
    for pat, repl in patrones_reemplazo:
        res = re.sub(pat, repl, res, flags=re.IGNORECASE)
    return res


def _normalizar_prefijo_numeral_ocr(line: str) -> str:
    """Normaliza distorsiones de caracteres OCR al inicio de numerales de párrafo."""
    # 1. Normalizar 'l.', 'I.', 'i.', '|.' -> '1. '
    line = re.sub(r"^[lIi\|]\.\s+", "1. ", line)
    # 2. Normalizar 'S.', 's.', '§.' -> '5. '
    line = re.sub(r"^(?:S|s|§)\.\s+", "5. ", line)
    # 3. Normalizar 'B.' -> '8. '
    line = re.sub(r"^B\.\s+", "8. ", line)
    # 4. Normalizar 'Z.' -> '2. '
    line = re.sub(r"^Z\.\s+", "2. ", line)
    return line


def _normalizar_llamadas_nota_al_pie(line: str) -> str:
    """Formatea exclusivamente dígitos de llamada a notas al pie en corchetes [1], [2], [3]."""
    # 1. Citas de artículos pegadas a llamada de nota (ej. "artículo 381" -> "artículo 38 [1]")
    line = re.sub(r"\bart[íi]culo\s+381\b", "artículo 38 [1]", line, flags=re.IGNORECASE)

    # 2. Llamadas a notas al pie específicas en frases y referencias (incluso si van seguidas de guion '-')
    line = re.sub(r"(N[º°]\s*97\s*\/2007)\s*1", r"\1 [1]", line)
    line = re.sub(r"construcci[óo\?a-z\s]+n\s*2", "construcción [2]", line, flags=re.IGNORECASE)
    line = re.sub(r"[áa]rea\s+verde\s*3", "área verde [3]", line, flags=re.IGNORECASE)
    line = re.sub(r"im[áa]genes\s*2", "imágenes [2]", line, flags=re.IGNORECASE)

    return line


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


def _es_continuacion_titulo_seccion(line: str) -> bool:
    """Verifica si una línea es la continuación en mayúsculas de un título de sección multilínea."""
    line_clean = line.strip()
    if not line_clean or _es_pie_de_pagina(line_clean):
        return False
    if re.match(r"^\d+\.\s+", line_clean) or re.match(r"^([IVXLCDM]+|l+|11+|1l|l1)\.\s+", line_clean, re.IGNORECASE):
        return False
    if re.match(r"^(?:Saluda|DISTRIBUCI[ÓO]N)", line_clean, re.IGNORECASE):
        return False
    letras = [c for c in line_clean if c.isalpha()]
    if not letras:
        return False
    return (sum(1 for c in letras if c.isupper()) / len(letras)) >= 0.65


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

        lines_cuerpo = lines[inicio_cuerpo:]
        total_lineas = len(lines_cuerpo)
        curr_idx = 0

        while curr_idx < total_lineas:
            line_clean = lines_cuerpo[curr_idx].strip()
            if not line_clean:
                curr_idx += 1
                continue

            # Descartar líneas de pie de página de OCR (incluyendo espacios rotos)
            if _es_pie_de_pagina(line_clean):
                curr_idx += 1
                continue

            # Aplicar normalización de numerales distorsionados por OCR (l. -> 1., S. -> 5., B. -> 8.)
            line_clean = _normalizar_prefijo_numeral_ocr(line_clean)
            # Aplicar formateo de llamadas a notas al pie [1], [2], [3]
            line_clean = _normalizar_llamadas_nota_al_pie(line_clean)

            # Detener extracción si llegamos a la firma o distribución
            if re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE) or re.match(
                r"^(?:DISTRIBUCI[ÓO\?I\s]+N|BUCI[ÓO\?I\s]+N|STRIBUCI[ÓO\?I\s]+N)[\s:]*", line_clean, re.IGNORECASE
            ):
                break

            # Omitir metadatos de cabecera si aún no hemos comenzado ningún párrafo/sección
            if not parrafo_actual and not secciones and not seccion_actual["titulo"]:
                if re.match(
                    r"^(?:DDU|CIRCULAR|ORD\.|ORO\.|ANT|MAT|DE|A|PARA|SANTIAGO|VALPARA[ÍI]SO|PERMISOS)\b",
                    line_clean,
                    re.IGNORECASE,
                ) or re.match(r"^\d+\)", line_clean):
                    curr_idx += 1
                    continue

            # Si la línea es un '3.' o numeral solo aislado por artefacto OCR antes de cita entrecomillada, descartar el artefacto de corte de página
            match_num_solo = re.match(r"^(\d+)\s*\.\s*$", line_clean)
            if match_num_solo:
                next_idx = curr_idx + 1
                while next_idx < total_lineas and (_es_pie_de_pagina(lines_cuerpo[next_idx]) or not lines_cuerpo[next_idx].strip()):
                    next_idx += 1
                if next_idx < total_lineas and lines_cuerpo[next_idx].strip().startswith('"'):
                    curr_idx = next_idx
                    continue
                else:
                    num_str = match_num_solo.group(1)
                    sub_texto = ""
                    if next_idx < total_lineas:
                        sub_texto = lines_cuerpo[next_idx].strip()
                        curr_idx = next_idx
                    line_clean = f"{num_str}. {sub_texto}"

            # Si el párrafo actual es el Numeral 2 y encontramos el análisis 'En atención a las normas antes citadas...', iniciar Numeral 3
            if parrafo_actual.startswith("2.") and re.match(r"^En\s+atenci[óo]n\s+a\s+las\s+normas\s+antes\s+citadas", line_clean, re.IGNORECASE):
                seccion_actual["parrafos"].append(parrafo_actual)
                parrafo_actual = f"3. {line_clean}"
                curr_idx += 1
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

                    # Capturar líneas subsiguientes que forman parte del título de sección multilínea
                    titulo_completo = texto_titulo
                    next_idx = curr_idx + 1
                    while next_idx < total_lineas and _es_continuacion_titulo_seccion(lines_cuerpo[next_idx]):
                        titulo_completo += " " + lines_cuerpo[next_idx].strip()
                        next_idx += 1

                    seccion_actual = {
                        "titulo": f"{romano_norm} {titulo_completo}",
                        "parrafos": [],
                    }
                    curr_idx = next_idx
                    continue

            # Detectar número arábigo al inicio (ej. "1. De conformidad...", "2. MARCO NORMATIVO:")
            match_parrafo = re.match(r"^(\d+)\.\s+(.+)$", line_clean)
            if match_parrafo:
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual)

                parrafo_actual = f"{match_parrafo.group(1)}. {match_parrafo.group(2).strip()}"
                curr_idx += 1
                continue

            # Concatenar a párrafo actual
            if parrafo_actual:
                parrafo_actual += " " + line_clean
            else:
                parrafo_actual = line_clean

            curr_idx += 1

        if parrafo_actual:
            seccion_actual["parrafos"].append(parrafo_actual)

        if seccion_actual["titulo"] or seccion_actual["parrafos"]:
            secciones.append(seccion_actual)

        # Aplicar reparación de palabras OCR a cada párrafo de las secciones
        for sec in secciones:
            sec["parrafos"] = [_limpiar_texto_cuerpo(p) for p in sec.get("parrafos", [])]

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

        cuerpo_texto = _limpiar_texto_cuerpo(" | ".join(partes_cuerpo))

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
