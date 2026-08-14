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
from scripts.extractors.utils_cleaner import limpiar_palabras_ocr


_PATRON_DIAGRAMA_ESQUEMA = re.compile(
    r"^(?:"
    r"EDIFICIO|"
    r"Piscinas?\.?|"
    r"Chimeneas?\.?|"
    r"P[eé]rgolas?\.?|"
    r"Ascensores\.?|"
    r"Barandas?\.?|"
    r"Paramentos(?:\s+perimetrales)?\.?|"
    r"perimetrales\.?|"
    r"escalera\.?|"
    r"jardineras\.?|"
    r"ornamentales\.?|"
    r"quinchos?\.?|"
    r"otros\.?|"
    r"Salida\s+caja\s+de(?:\s+escalera)?\.?|"
    r"Terraza(?:\s+Terraza)?\.?|"
    r"Vegetaci[oó]n,?(?:\s+jardineras)?\.?|"
    r"M[aá]ximo\s+25%(?:\s+de\s+la\s+superficie(?:\s+de\s+la\s+azotea\.?)?)?|"
    r"de\s+la\s+superficie(?:\s+de\s+la\s+azotea\.?)?|"
    r"superficie\s+de\s+la\s+azotea\.?|"
    r"de\s+la\s+azotea\.?|"
    r"Altura\s+m[aá]xima\s+de(?:\s+edificaci[oó]n\s+permitida(?:\s+por\s+el\s+IPT\.?)?)?|"
    r"edificaci[oó]n\s+permitida(?:\s+por\s+el\s+IPT\.?)?|"
    r"por\s+el\s+IPT\.?|"
    r"Piscinas,\s+vegetaci[oó]n,?(?:\s+jardineras,?\s+elementos(?:\s+ornamentales\.?)?)?|"
    r"jardineras,?\s+elementos(?:\s+ornamentales,?\s+resto\s+de\s+la)?|"
    r"ornamentales,?\s+resto\s+de\s+la|"
    r"resto\s+de\s+la|"
    r"Salas\s+de\s+M[aá]quinas,?(?:\s+Cajas\s+de\s+escalera,?\s+Chimeneas\.?)?|"
    r"Cajas\s+de\s+escalera,?(?:\s+Chimeneas\.?)?|"
    r"\(con\s+un\s+m[aá]ximo\s+de\s+99%\)|"
    r"P[eé]rgolas,?(?:\s+quinchos,?(?:\s+otros\.?)?)?"
    r")$",
    re.IGNORECASE,
)



def _es_etiqueta_diagrama(line: str) -> bool:
    """Detecta fragmentos de texto y etiquetas de planos, diagramas o esquemas técnicos."""
    line_clean = line.strip()
    if not line_clean:
        return False
    # Símbolos y fracciones aisladas (ej. ½, ¼, ¾, \ufffd)
    if re.match(r"^[\u00bd\u00bc\u00be\ufffd\?]+$", line_clean):
        return True

    # Encabezados típicos de planos o esquemas técnicos
    if re.search(r"\b(?:PLANTA\s+AZOTEA|CORTE\s+ESQUEM[AÁ]TICO|SIN\s+ESCALA)\b", line_clean, re.IGNORECASE):
        return True

    # Etiquetas cortas (< 80 caracteres) de diagramas
    if len(line_clean) < 80 and _PATRON_DIAGRAMA_ESQUEMA.match(line_clean):
        return True

    return False


def _limpiar_texto_cuerpo(texto: str) -> str:
    """Repara palabras rotas y preserva el casing original de mayúsculas/minúsculas."""
    res = limpiar_palabras_ocr(texto)

    # Reparaciones morfológicas agrupadas para preservar casing exacto (\1\2)
    res = re.sub(r"\b(inst)\s+(rumen\s+to|rucc[ií]on\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(permi)\s+(so[s]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(edifi)\s+(cad\w+|cac[ií]on\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(increment)\s+(o[s]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(circunscribi)\s+(rse)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(porcentua)\s+(l[es]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(ante)\s+(s)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(aplicab)\s+(le[s]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(mod)\s+(ificac[ií]on\w*|ificad\w+)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(espec[ií]f)\s+(ic\w+)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(construid)\s+(a[s]?|o[s]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(correspond)\s+(ient\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(circul)\s+(ar\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(superf)\s+(ic\w+)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(dispos)\s+(ic\w+)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(urban[íi]st)\s+(ic\w+)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(territor)\s+(ial\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(solic)\s+(itud\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(aprob)\s+(ad\w+|ac[ií]on\w*)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(expuest)\s+(o[s]?|a[s]?)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\b(im[áa])\s+(genes)\b", r"\1\2", res, flags=re.IGNORECASE)
    res = re.sub(r"\bOS\s+33\b", "DS 33", res)

    return res



def _normalizar_prefijo_numeral_ocr(line: str) -> str:
    """Normaliza distorsiones de caracteres OCR al inicio de numerales de párrafo."""
    # 0. Normalizar espacios entre dígito y punto (ej. "4 . ", "7 . ") -> "4. "
    line = re.sub(r"^(\d+)\s+\.\s*", r"\1. ", line)
    # 1. Normalizar 'l.', '|.' -> '1. ' (sin alterar el número romano I. o i.)
    line = re.sub(r"^[l\|]\.\s+", "1. ", line)

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
    line = re.sub(r"im[áa]\s*genes\s*2\b", "imágenes [2]", line, flags=re.IGNORECASE)

    return line


def _es_inicio_nota_al_pie(line: str) -> bool:
    """Detecta si una línea corresponde al inicio de una nota al pie explicativa."""
    line_clean = line.strip()
    match = re.match(r"^(\d{1,2})\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\.,\(\)\"\'-].+)$", line_clean)
    if match:
        num = match.group(1)
        texto = match.group(2).strip()
        if int(num) <= 20 and not line_clean.startswith(f"{num}. "):
            if not re.match(r"^\d+\s+(?:de\s+la|de\s+los|del|en\s+la|con\s+la|que|por|para)\b", line_clean, re.IGNORECASE):
                if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley|Construcci[óo]n|Edificaci[óo]n|OGUC|LGUC)\b", texto, re.IGNORECASE):
                    return True
    return False


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
        if prefix_clean in ("l", "i", "1"):
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
            if idx_a == -1 and (
                re.match(r"^A\s*:\s*.+$", line, re.IGNORECASE)
                or re.match(r"^PARA\s*:\s*.+$", line, re.IGNORECASE)
                or re.match(
                    r"^A\s+((?:SEGÚN|TODOS|TODAS|LOS|LAS|SRES|SRA|SR|DIRECTOR|SECRETARIO|GOBERNA|CONTRALO|BIBLIO)\b.+)$",
                    line,
                    re.IGNORECASE,
                )
            ):
                m_check = re.match(r"^(?:A\s*:?|PARA\s*:)\s*:?\s*(.+)$", line, re.IGNORECASE)
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
        omitiendo_nota_al_pie = False

        lines_cuerpo = lines[inicio_cuerpo:]
        total_lineas = len(lines_cuerpo)
        curr_idx = 0

        while curr_idx < total_lineas:
            line_clean = lines_cuerpo[curr_idx].strip()
            if not line_clean:
                curr_idx += 1
                continue

            # Descartar líneas de pie de página de OCR (incluyendo espacios rotos) y resetear estado de descarte
            if _es_pie_de_pagina(line_clean):
                omitiendo_nota_al_pie = False
                curr_idx += 1
                continue

            # Descartar fragmentos y etiquetas sueltas de diagramas/planos técnicos
            if _es_etiqueta_diagrama(line_clean):
                curr_idx += 1
                continue

            # Aplicar normalización de numerales distorsionados por OCR (l. -> 1., S. -> 5., B. -> 8.)
            line_clean = _normalizar_prefijo_numeral_ocr(line_clean)
            # Aplicar formateo de llamadas a notas al pie [1], [2], [3]
            line_clean = _normalizar_llamadas_nota_al_pie(line_clean)

            # Detectar e ignorar bloques de notas al pie dentro del cuerpo
            if _es_inicio_nota_al_pie(line_clean):
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual.strip())
                    parrafo_actual = ""
                omitiendo_nota_al_pie = True
                curr_idx += 1
                continue

            if omitiendo_nota_al_pie:
                if re.match(r"^\d+\.\s+", line_clean) or re.match(r"^[IVXLCDM]+\.\s+", line_clean, re.IGNORECASE):
                    omitiendo_nota_al_pie = False
                else:
                    curr_idx += 1
                    continue


            # Detener extracción si llegamos a la firma o distribución
            if re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE) or re.match(
                r"^(?:DISTRIBUCI[ÓO\?I\s]+N|BUCI[ÓO\?I\s]+N|STRIBUCI[ÓO\?I\s]+N)[\s:]*", line_clean, re.IGNORECASE
            ):
                break

            # Omitir metadatos de cabecera si aún no hemos comenzado ningún párrafo/sección
            if not parrafo_actual and not secciones and not seccion_actual["titulo"] and not seccion_actual["parrafos"]:
                if re.match(
                    r"^(?:DDU|CIRCULAR|ORD\.|ORO\.|ANT|MAT|DE|A\s*:|PARA\s*:|SANTIAGO|VALPARA[ÍI]SO|PERMISOS)\b",
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

            # Detectar número romano o distorsión OCR de sección (ej. "I. ANTECEDENTES", "1. ANTECEDENTES", "11. NORMATIVA APLICABLE")
            match_romano = re.match(r"^([IVXLCDM]+|l+|\d+)\.\s+(.+)$", line_clean, re.IGNORECASE)

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
