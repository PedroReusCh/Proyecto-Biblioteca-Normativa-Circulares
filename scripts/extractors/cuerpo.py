"""Extractor del cuerpo estructurado (secciones y párrafos) de circulares DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional, Sequence

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
    r"M[aá]ximo\s+25%\s+de\s+la\s+superficie\s+de\s+la\s+azotea\.?|"
    r"Altura\s+m[aá]xima\s+de\s+edificaci[oó]n\s+permitida\s+por\s+el\s+IPT\.?|"
    r"Piscinas,\s+vegetaci[oó]n,?\s+jardineras,?\s+elementos\s+ornamentales\.?|"
    r"Salas\s+de\s+M[aá]quinas,?\s+Cajas\s+de\s+escalera,?\s+Chimeneas\.?|"
    r"\(con\s+un\s+m[aá]ximo\s+de\s+99%\)|"
    r"P[eé]rgolas,?\s+quinchos,?\s+otros\.?"
    r")$",
    re.IGNORECASE,
)




def _es_inicio_diagrama(line: str) -> bool:
    """Detecta el inicio de un diagrama o esquema técnico."""
    line_clean = line.strip()
    if not line_clean:
        return False
    return bool(re.search(r"\b(?:PLANTA\s+AZOTEA|CORTE\s+ESQUEM[AÁ]TICO|SIN\s+ESCALA)\b", line_clean, re.IGNORECASE))


def _es_etiqueta_diagrama(line: str) -> bool:
    """Detecta fragmentos de texto y etiquetas de planos, diagramas o esquemas técnicos."""
    line_clean = line.strip()
    if not line_clean:
        return False
    # Símbolos y fracciones aisladas (ej. ½, ¼, ¾, \ufffd)
    if re.match(r"^[\u00bd\u00bc\u00be\ufffd\?]+$", line_clean):
        return True

    # Encabezados típicos de planos o esquemas técnicos
    if _es_inicio_diagrama(line_clean):
        return True

    # Etiquetas cortas (< 80 caracteres) de diagramas
    if len(line_clean) < 80 and _PATRON_DIAGRAMA_ESQUEMA.match(line_clean):
        return True
    return False


def _es_inicio_bloque_tabla(line: str) -> bool:
    """Detecta el inicio de un bloque tabular normativo para excluirlo del cuerpo."""
    line_clean = line.strip()
    if not line_clean:
        return False
    if re.search(r"Circular\s+Materia\(s\)\s+que\s+se\s+modifica\(n\)", line_clean, re.IGNORECASE):
        return True
    if re.search(r"\bMateria\(s\)\s+que\s+se\s+modifica\(n\)", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^\|\s*Circular\b", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^\|\s*TIPO\s+DE\s+GESTI[ÓO]N\b", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^\|\s*DDU\s+N\b", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^TIPO\s+DE\s+GESTI[ÓO]N\b", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^CASOS\s+QUE\s+COMPRENDE\b", line_clean, re.IGNORECASE):
        return True
    if re.search(r"^N[°º\?]?\s*CIRCULAR", line_clean, re.IGNORECASE):
        return True
    if re.search(r"^N[°º\?]?\s+ORD", line_clean, re.IGNORECASE):
        return True
    if re.search(r"^DDU\s+N[°º\?]?\s+N[°º\?]?\s+ORD", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^DDU\s+N[°º\?]?\s*$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^MATERIA\s+DE\s+LA\s+CIRCULAR\s*$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^MOTIVOS\s*/\s*CONSIDERACIONES\s*$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^MODIFICACIONES\s*$", line_clean, re.IGNORECASE):
        return True
    return False





def _es_nota_modificacion_posterior(line: str) -> bool:
    """Detecta líneas de notas marginales de timbre de modificación posterior / vigencia jurídica."""
    line_clean = line.strip()
    if not line_clean:
        return False
    if re.search(r"\(?\s*Circular\s+Modificada\s+por\b", line_clean, re.IGNORECASE):
        return True
    if re.search(r"\(?\s*Modificada\s+por\s+Circular\b", line_clean, re.IGNORECASE):
        return True
    if re.search(r"\(?\s*Dejada\s+sin\s+efecto\s+por\b", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^Circular\s+Ord\.?\s*N[°º\?]?\s*\d+\s*,?$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^de\s+fecha\s+\d{1,2}\s+de\s+[a-záéíóúñ]+(?:\s+de\s+\d{4})?,?\s*$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^de\s+\d{4},\s*DDU\s*\d+\s*$", line_clean, re.IGNORECASE):
        return True
    if re.match(r"^\(?numeral\s+\d+\.?\)?$", line_clean, re.IGNORECASE):
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
    res = re.sub(r"\bOS\s+33\b", "DS 33", res)

    # Remover notas marginales de modificación posterior incrustadas (timbres explícitos)
    res = re.sub(
        r"\(?\s*(?:Circular\s+Modificada\s+por|Modificada\s+por\s+Circular|Dejada\s+sin\s+efecto\s+por)\s+Circular\s+Ord\.?\s*N[°º\?]?\s*\d+[^\n\)]*\)?",
        "",
        res,
        flags=re.IGNORECASE,
    )


    # Remover remanentes de encabezados de tablas al final de párrafos
    m_tbl = re.search(r"\s*(?:Circular\s+)?Materia\(s\)\s+que\s+se\s+modifica\(n\).*", res, re.IGNORECASE)
    if m_tbl:
        res = res[:m_tbl.start()].strip()
        if res.endswith(";"):
            res = res[:-1] + ":"

    res = re.sub(r"\s+", " ", res).strip()
    return res


def _descontaminar_parrafo_de_tablas(p: str) -> str:
    """Elimina colas de tablas y encabezados adheridos al final de párrafos de transición."""
    m_dej = re.search(r"(se\s+dejan\s+sin\s+efecto\s+las\s+siguientes\s+circulares\s*:?)", p, re.IGNORECASE)
    if m_dej:
        p = p[:m_dej.end()].strip()
        if not p.endswith(":"):
            p += ":"

    m_mod = re.search(r"(se\s+modifican\s+las\s+siguientes\s+Circulares\s+en\s+la\s+forma\s+que\s+se\s+indica\s*:?)", p, re.IGNORECASE)
    if m_mod:
        p = p[:m_mod.end()].strip()
        if not p.endswith(":"):
            p += ":"

    m_urb = re.search(r"(la\s+urbanizaci[óo]n\s+solo\s+comprende\s+los\s+siguientes\s+tipos\s+de\s+gesti[óo]n\s*:?)", p, re.IGNORECASE)
    if m_urb:
        p = p[:m_urb.end()].strip()
        if not p.endswith(":"):
            p += ":"

    return p








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

    # 2. Llamadas a notas al pie específicas en frases y referencias
    line = re.sub(r"(N[º°]\s*97\s*\/2007)\s*1", r"\1 [1]", line)
    line = re.sub(r"construcci[óo\?a-z\s]+n\s*2\b", "construcción [2]", line, flags=re.IGNORECASE)
    line = re.sub(r"[áa]rea\s+verde\s*3\b", "área verde [3]", line, flags=re.IGNORECASE)
    line = re.sub(r"im[áa]\s*genes\s*2\b", "imágenes [2]", line, flags=re.IGNORECASE)

    llamadas_especificas = [
        (r"(\bcesi[óo]n\s+obligatoria)1([\.\,\;\:\s]|$)", r"\1 [1]\2"),
        (r"(\bcomunidad\s+toda)2([\.\,\;\:\s]|$)", r"\1 [2]\2"),
        (r"(\bal\s+interior\s+de\s+un\s+predio[”\"\']?)\s*3([\.\,\;\:\s]|$)", r"\1 [3]\2"),
        (r"(\b2\.2\.1\.\s+de\s+la\s+OGUC)4([\.\,\;\:\s]|$)", r"\1 [4]\2"),
        (r"(\bexigencias\s+y\s+efectos\s+aplicables)\s*5([\.\,\;\:\s]|$)", r"\1 [5]\2"),
        (r"(\bcorrespondiente\s+urbanizaci[óo]n)6([\.\,\;\:\s]|$)", r"\1 [6]\2"),
        (r"(\bsuperficie\s+de\s+este)\s*7([\.\,\;\:\s]|$)", r"\1 [7]\2"),
        (r"(\bcesi[óo]n\s+obligatoria)8([\.\,\;\:\s]|$)", r"\1 [8]\2"),
        (r"(\bpermiso\s+de\s+urbanizaci[óo]n\s+de\s+la\s+DOM\))\s*9([\.\,\;\:\s]|$)", r"\1 [9]\2"),
        (r"(\burbanizaci[óo]n)\s*10([\.\,\;\:\s]|$)", r"\1 [10]\2"),
        (r"(\bart[íi]culo\s+135\s+de\s+la\s+LGUC)11([\.\,\;\:\s]|$)", r"\1 [11]\2"),
        (r"(\bLGUC)11([\.\,\;\:\s]|$)", r"\1 [11]\2"),
        (r"(\bpendientes\))\s*12([\.\,\;\:\s]|$)", r"\1 [12]\2"),
        (r"(\b2\.2\.1\.\s+de\s+la\s+OGUC)\s*13([\.\,\;\:\s]|$)", r"\1 [13]\2"),
        (r"(\ben\s+su\s+predio)14([\.\,\;\:\s]|$)", r"\1 [14]\2"),
        (r"(\bsubdivisi[óo]n\s+del\s+predio)\s*15([\.\,\;\:\s]|$)", r"\1 [15]\2"),
        (r"(\bpermiso\s+de\s+la\s+DOM)\s*16([\.\,\;\:\s]|$)", r"\1 [16]\2"),
        (r"(\bart[íi]culo\s+3\.1\.5\.\s+de\s+la\s+OGUC)17([\.\,\;\:\s]|$)", r"\1 [17]\2"),
        (r"(\b3\.1\.8\.\s+de\s+la\s+OGUC)\s*18([\.\,\;\:\s]|$)", r"\1 [18]\2"),
        (r"(\bOGUC)\s*18\s+se\s+dispone", r"\1 [18] se dispone"),
        (r"(\bverifica\s+lo\s+siguiente)19([\.\,\;\:\s]|$)", r"\1 [19]\2"),
        (r"^20\s+y\s+cumplan\b", "[20] y cumplan"),
        (r"(\bv[íi]a\s+de\s+uso\s+p[úu]blico)\s*20([\.\,\;\:\s]|$)", r"\1 [20]\2"),
        (r"(\bp[úu]blico)\s*20([\.\,\;\:\s]|$)", r"\1 [20]\2"),
        (r"(\botorgada\s+por\s+la\s+DOM\))21([\.\,\;\:\s]|$)", r"\1 [21]\2"),
        (r"(\banteproyectos)\s*22([\.\,\;\:\s]|$)", r"\1 [22]\2"),
        (r"(\bentre\s+otros\s+fines)23([\.\,\;\:\s]|$)", r"\1 [23]\2"),
        (r"(\ba\s+trav[ée]s\s+de\s+servidumbres)\s*24([\.\,\;\:\s]|$)", r"\1 [24]\2"),
        (r"(\bcondominio\s+en\s+ellos)25([\.\,\;\:\s]|$)", r"\1 [25]\2"),
        (r"(\bpresentados\s+a\s+la\s+DOM)\s*26([\.\,\;\:\s]|$)", r"\1 [26]\2"),
        (r"(\brecepci[óo]n\s+indicada)27([\.\,\;\:\s]|$)", r"\1 [27]\2"),
        (r"(\b2\.2\.9\.\s+de\s+la\s+OGUC)\s*28([\.\,\;\:\s]|$)", r"\1 [28]\2"),
        (r"(\b2\.2\.9\s+de\s+la\s+OGUC)\s*28([\.\,\;\:\s]|$)", r"\1 [28]\2"),
        (r"(\b2\.2\.4\.\s+de\s+la\s+OGUC)29([\.\,\;\:\s]|$)", r"\1 [29]\2"),
        (r"(\bde\s+ese\s+inciso)\s*30([\.\,\;\:\s]|$)", r"\1 [30]\2"),
        (r"(\bart[íi]culo\s+1\.1\.2\s*\.)\s*31([\.\,\;\:\s]|$)", r"\1 [31]\2"),
        (r"(\bart[íi]culo\s+1\.1\.2\.)31([\.\,\;\:\s]|$)", r"\1 [31]\2"),
    ]
    for p, r in llamadas_especificas:
        line = re.sub(p, r, line, flags=re.IGNORECASE)

    def _reemplazo_generico(m: re.Match[str]) -> str:
        palabra = m.group(1)
        num = m.group(2)
        sep = m.group(3)
        pal_lower = palabra.lower()
        if pal_lower in ("artículo", "ley", "decreto", "año", "punto", "letra", "numeral", "página", "n", "no", "ds", "ddu", "ord", "bis", "inciso", "párrafo", "tabla", "figura") or palabra.isdigit():
            return m.group(0)
        return f"{palabra} [{num}]{sep}"

    line = re.sub(
        r"(\b[a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}|[\)\]”\"\»])(\d{1,2})(?![\.\,]\d)([\,\.\;\:\s]|$)",
        _reemplazo_generico,
        line
    )

    return line


def _es_inicio_nota_al_pie(line: str) -> bool:
    """Detecta si una línea corresponde al inicio de una nota al pie explicativa auténtica."""
    line_clean = line.strip()
    match = re.match(
        r"^(\d{1,2})\s*([a-z]\))?\s+([A-ZÁÉÍÓÚÑ\"“'‘\(]|Cuando\b|Que\b|Para\b|En\b|De\b|Según\b|Con\b|Tal\b|La\b|El\b|Inciso\b|Sin\b|Dicho\b|Dictamen\b|Esta\b|Sea\b|Aplica\b)",
        line_clean,
    )
    if match:
        num = match.group(1)
        if re.match(r"^\d+\s+(?:o\s+m[áa]s|para\s+todas|y\s+cumplan|de\s+la\s+Ley|de\s+la\s+LGUC|de\s+la\s+OGUC|de\s+enero|de\s+febrero|de\s+marzo|de\s+abril|de\s+mayo|de\s+junio|de\s+julio|de\s+agosto|de\s+septiembre|de\s+octubre|de\s+noviembre|de\s+diciembre)\b", line_clean, re.IGNORECASE):
            return False
        if re.match(r"^\d+\,\s+de\s+acuerdo\b", line_clean, re.IGNORECASE):
            return False
        if re.match(r"^\d+\.\s+En\s+esos\s+casos\b", line_clean, re.IGNORECASE):
            return False
        if not line_clean.startswith(f"{num}. "):
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


def _es_inicio_indice(line: str) -> bool:

    """Detecta el inicio del índice o tabla de contenidos."""
    line_clean = line.strip()
    if not line_clean:
        return False
    return bool(re.match(r"^(?:[IVXLCDM\d\.\s]*\b(?:[IÍ]NDICE|TABLA\s+DE\s+CONTENIDO[S]?|CONTENIDO[S]?)\b\s*:?)", line_clean, re.IGNORECASE))


def _es_linea_indice(line: str) -> bool:
    """Detecta si una línea pertenece al índice / tabla de contenidos (incluyendo líneas con guías de puntos)."""
    line_clean = line.strip()
    if not line_clean:
        return False
    if _es_inicio_indice(line_clean):
        return True
    if re.search(r"\.{4,}", line_clean) or re.search(r"\.{3,}\s*\d+$", line_clean):
        return True
    return False


def _normalizar_romano_ocr(prefix: str, texto_titulo: str) -> str | None:
    """Diferencia entre números arábigos y romanos detectando errores de OCR (ej. 11. -> II. o l. -> I.)."""
    prefix_clean = prefix.lower().strip()

    # Si es parte del índice o contiene puntos de tabla de contenidos, no es macro-sección
    if re.search(r"\b(?:[IÍ]NDICE|TABLA\s+DE\s+CONTENIDO)\b", texto_titulo, re.IGNORECASE):
        return None
    if re.search(r"\.{4,}", texto_titulo):
        return None


    # Analizar si el texto del título es principalmente mayúsculas
    letras = [c for c in texto_titulo if c.isalpha()]
    if not letras:
        return None
    es_mayusculas = (sum(1 for c in letras if c.isupper()) / len(letras)) >= 0.65

    if not es_mayusculas:
        return None

    # Si es número romano directo estricto (ej. I, II, III, IV, V, VI, VII, VIII, IX, X)
    if re.match(r"^(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII)$", prefix, re.IGNORECASE):
        return f"{prefix.upper()}."

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

    def extract(self, raw_text: str, lines: Sequence[str] | List[str], pdf_path: Optional[Path] = None) -> ResultadoBloque:
        """Extrae las secciones y párrafos estructurados del cuerpo de la circular DDU.

        Localiza ambos marcadores A:/PARA: y DE: (en cualquier orden) y comienza
        la extracción del cuerpo a partir de la línea siguiente al segundo marcador.
        La extracción se detiene al encontrar la fórmula de cierre (firma o distribución).

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.
            pdf_path: Ruta opcional al archivo PDF.


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
        omitiendo_tabla = False
        omitiendo_diagrama = False
        omitiendo_indice = False

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

            # Detectar e ignorar completamente el bloque de Índice / Tabla de Contenidos
            if _es_inicio_indice(line_clean):
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual.strip())
                    parrafo_actual = ""
                omitiendo_indice = True
                curr_idx += 1
                continue

            if omitiendo_indice:
                if _es_linea_indice(line_clean):
                    curr_idx += 1
                    continue
                elif (
                    (re.match(r"^\d+\.\s+[A-ZÁÉÍÓÚÑ]", line_clean) and not re.search(r"\.{2,}", line_clean))
                    or (
                        re.match(r"^\d+\.\s*$", line_clean)
                        and curr_idx + 1 < total_lineas
                        and not re.search(r"\.{2,}", lines_cuerpo[curr_idx + 1])
                    )
                ):
                    omitiendo_indice = False
                elif _es_pie_de_pagina(line_clean):
                    curr_idx += 1
                    continue
                else:
                    curr_idx += 1
                    continue


            # Detectar e ignorar bloques de diagramas o esquemas técnicos dentro del cuerpo
            if _es_inicio_diagrama(line_clean):
                if parrafo_actual:
                    seccion_actual["parrafos"].append(parrafo_actual.strip())
                    parrafo_actual = ""
                omitiendo_diagrama = True
                curr_idx += 1
                continue


            if omitiendo_diagrama:
                if re.match(r"^\d+\.\s+", line_clean) or re.match(r"^[IVXLCDM]+\.\s+", line_clean, re.IGNORECASE) or re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE):
                    omitiendo_diagrama = False
                else:
                    curr_idx += 1
                    continue

            # Descartar fragmentos y etiquetas sueltas de diagramas/planos técnicos
            if _es_etiqueta_diagrama(line_clean):
                curr_idx += 1
                continue

            # Descartar notas marginales de modificación posterior / timbres de vigencia
            if _es_nota_modificacion_posterior(line_clean):
                curr_idx += 1
                continue



            # Detectar e ignorar bloques de tablas normativas dentro del cuerpo
            if _es_inicio_bloque_tabla(line_clean):
                if parrafo_actual:
                    for pat in [
                        r"(?:Circular\s+)?Materia\(s\)\s+que\s+se\s+modifica\(n\).*",
                        r"TIPO\s+DE\s+GESTI[ÓO]N.*",
                        r"CASOS\s+QUE\s+COMPRENDE.*",
                        r"N[°º\?]?\s*CIRCULAR.*",
                        r"DDU\s*N[°º\?]?.*",
                    ]:
                        m_th = re.search(pat, parrafo_actual, re.IGNORECASE)
                        if m_th:
                            parrafo_actual = parrafo_actual[:m_th.start()].strip()
                    if parrafo_actual.endswith(";"):
                        parrafo_actual = parrafo_actual[:-1] + ":"
                    if parrafo_actual:
                        seccion_actual["parrafos"].append(parrafo_actual.strip())
                    parrafo_actual = ""
                omitiendo_tabla = True
                curr_idx += 1
                continue


            if omitiendo_tabla:
                if (
                    re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE)
                    or re.match(r"^(?:DISTRIBUCI[ÓO\?I\s]+N|BUCI[ÓO\?I\s]+N|STRIBUCI[ÓO\?I\s]+N)[\s:]*", line_clean, re.IGNORECASE)
                    or re.match(r"^(?:1\.|2\.|3\.)\s+(?:Sr\.|Sra\.|Sres\.)\s+(?:Ministr|Subsecretari|Contralor)", line_clean, re.IGNORECASE)
                ):
                    omitiendo_tabla = False
                elif (
                    (
                        re.match(r"^(?:5|6|7|8|9|10|11|12)\.\s+[A-ZÁÉÍÓÚÑ]", line_clean)
                        and not _es_inicio_nota_al_pie(line_clean)
                        and not re.match(r"^\d+\.\s+Con\s+anterioridad\b", line_clean, re.IGNORECASE)
                    )
                    or (
                        re.match(r"^(?:5|6|7|8|9|10|11|12)\.\s*$", line_clean)
                        and curr_idx + 1 < total_lineas
                        and not _es_inicio_nota_al_pie(lines_cuerpo[curr_idx + 1])
                    )
                    or re.match(r"^12\.2\.\s+En\s+atenci[óo]n", line_clean, re.IGNORECASE)
                    or re.match(r"^[IVXLCDM]+\.\s+[A-ZÁÉÍÓÚÑ]", line_clean)
                ):
                    omitiendo_tabla = False
                else:
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
                if (
                    (
                        re.match(r"^\d+(?:\.\d+)*\.\s+[A-ZÁÉÍÓÚÑ]", line_clean)
                        and not _es_inicio_nota_al_pie(line_clean)
                        and not re.match(r"^\d+\.\s+Con\s+anterioridad\b", line_clean, re.IGNORECASE)
                    )
                    or (
                        re.match(r"^\d+\.\s*$", line_clean)
                        and curr_idx + 1 < total_lineas
                        and not _es_inicio_nota_al_pie(lines_cuerpo[curr_idx + 1])
                    )
                    or re.match(r"^[IVXLCDM]+\.\s+[A-ZÁÉÍÓÚÑ]", line_clean)
                    or re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE)
                    or re.match(r"^(?:DISTRIBUCI[ÓO\?I\s]+N|BUCI[ÓO\?I\s]+N|STRIBUCI[ÓO\?I\s]+N)[\s:]*", line_clean, re.IGNORECASE)
                ):
                    omitiendo_nota_al_pie = False
                else:
                    curr_idx += 1
                    continue



            # Detener extracción si llegamos a la firma o distribución
            if (
                re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE)
                or re.match(r"^(?:DISTRIBUCI[ÓO\?I\s]+N|BUCI[ÓO\?I\s]+N|STRIBUCI[ÓO\?I\s]+N)[\s:]*", line_clean, re.IGNORECASE)
                or re.match(r"^(?:1\.|2\.|3\.)\s+(?:Sr\.|Sra\.|Sres\.)\s+(?:Ministr|Subsecretari|Contralor)", line_clean, re.IGNORECASE)
                or re.match(r"^(?:JUAN\s+DIEGO\s+IZQUIERDO|ENRIQUE\s+MATUSCHKA|VICENTE\s+BURGOS)", line_clean, re.IGNORECASE)
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

            # Si la línea es un número solo aislado en su propia línea (ej. "15.", "16", "23.", "26.", "28.")
            match_num_solo = re.match(r"^(\d{1,2})\s*(\.?)\s*$", line_clean)
            if match_num_solo and 1 <= int(match_num_solo.group(1)) <= 35:
                num_val = match_num_solo.group(1)
                # Verificar si la siguiente línea es un título de sección (ej. "MARCO NORMATIVO:", "¿QUÉ ES LA URBANIZACIÓN?", "HIPÓTESIS...")
                sig_line = lines_cuerpo[curr_idx + 1].strip() if curr_idx + 1 < total_lineas else ""
                if sig_line and (
                    sig_line.isupper()
                    or any(k in sig_line.upper() for k in ["MARCO", "URBANIZACIÓN", "HIPÓTESIS", "OBRAS", "PERMISOS", "RECEPCIÓN", "CIRCULARES", "OTRAS"])
                ):
                    if parrafo_actual:
                        seccion_actual["parrafos"].append(parrafo_actual)
                        parrafo_actual = ""
                    parrafo_actual = f"{num_val}. {sig_line}"
                    curr_idx += 2
                    continue

                tiene_pto = match_num_solo.group(2) == "."
                if parrafo_actual:
                    parrafo_actual += f" [{num_val}]." if tiene_pto else f" [{num_val}]"
                curr_idx += 1
                continue


            # Si la línea inicia con número de llamada seguido de continuación (ej. "10, de acuerdo...", "12 para todas...", "13. En esos casos...", "20 y cumplan...")
            match_num_inicio = re.match(r"^(\d{1,2})([\,\.\;\:])?\s+(.+)$", line_clean)
            if match_num_inicio and parrafo_actual and 1 <= int(match_num_inicio.group(1)) <= 35:
                num_val = match_num_inicio.group(1)
                sep_val = match_num_inicio.group(2) or ""
                resto_texto = match_num_inicio.group(3).strip()
                if (
                    sep_val == ","
                    or resto_texto.startswith("para todas")
                    or resto_texto.startswith("En esos casos")
                    or resto_texto.startswith("y cumplan")
                ):
                    parrafo_actual += f" [{num_val}]{sep_val} {resto_texto}"
                    curr_idx += 1
                    continue

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

            # Detectar numeral arábigo o sub-numeral al inicio (ej. "1. De conformidad...", "2.1. Con fecha...", "5.1. LOTEO")
            match_parrafo = re.match(r"^(\d+(?:\.\d+)*)\.\s+(.+)$", line_clean)
            if match_parrafo:
                num_str, texto_num = match_parrafo.group(1), match_parrafo.group(2).strip()
                if not (
                    texto_num.startswith("En el punto 2,")
                    or texto_num.startswith("En el punto 5,")
                    or texto_num.startswith("En el punto 6,")
                    or texto_num.startswith("En el punto 15,")
                    or texto_num.startswith("Se reemplaza el punto")
                ):
                    if parrafo_actual:
                        seccion_actual["parrafos"].append(parrafo_actual)

                    parrafo_actual = f"{num_str}. {texto_num}"
                    curr_idx += 1
                    continue

            # Concatenar a párrafo actual
            if parrafo_actual:
                parrafo_actual += " " + line_clean
            else:
                parrafo_actual = line_clean

            curr_idx += 1

        if parrafo_actual:
            m_th = re.search(r"(?:Circular\s+)?Materia\(s\)\s+que\s+se\s+modifica\(n\).*", parrafo_actual, re.IGNORECASE)
            if m_th:
                parrafo_actual = parrafo_actual[:m_th.start()].strip()
            if parrafo_actual.endswith(";"):
                parrafo_actual = parrafo_actual[:-1] + ":"
            if parrafo_actual:
                seccion_actual["parrafos"].append(parrafo_actual)

        if seccion_actual["titulo"] or seccion_actual["parrafos"]:
            secciones.append(seccion_actual)

        def _es_parrafo_de_tabla(p_cand: str) -> bool:
            p_strip = p_cand.strip()
            if not p_strip:
                return False
            # Encabezados de tabla
            if re.match(r"^N[°º\?]?\s*CIRCULAR\b", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^N[°º\?]?\s+ORD\s+FECHA", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^DDU\s*N[°º\?]?\s*N[°º\?]?\s*ORD", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^TIPO\s+DE\s+GESTI[ÓO]N\b", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^CASOS\s+QUE\s+COMPRENDE\b", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^MATERIA\s+DE\s+LA\s+CIRCULAR\b", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^MOTIVOS\s*/\s*CONSIDERACIONES\b", p_strip, re.IGNORECASE):
                return True
            if re.match(r"^MODIFICACIONES\b", p_strip, re.IGNORECASE):
                return True

            # Celdas de Tabla 1
            if p_strip.startswith("1. Loteos (Art. 2.2.4."):
                return True
            if p_strip.startswith("2. Proyectos que se acojan al régimen de copropiedad"):
                return True
            if p_strip.startswith("3. División afecta a declaratoria de utilidad"):
                return True
            if p_strip.startswith("1. Obras de urbanización voluntarias en el espacio"):
                return True
            if p_strip.startswith("2. Obras de urbanización voluntarias al interior"):
                return True
            if p_strip.startswith("La ejecución de obras de urbanización") and "Art. 2.2.1." in p_strip:
                return True
            if p_strip.startswith("Cualquiera de las obras de urbanización contempladas en el artículo 134"):
                return True

            # Celdas de Tabla 2 y Tabla 3
            if p_strip.startswith("Específica "):
                return True
            if re.match(r"^\d{3}\s+\d+\s+\d{2}[-\.]\d{2}[-\.]\d{2}", p_strip):
                return True
            if re.match(r"^(?:2\.6\.19\.|2\.2\.4\.|2\.6\.4\.|2\.3\.2\.)\s+(?:mediante|N[°º\?]|y\s+2\.6\.15\.|y\s+3\.2\.11\.|y\s+2\.3\.2\.)", p_strip):
                return True
            if p_strip.startswith("Se aborda esta materia en la presente circular"):
                return True
            if p_strip.startswith("Expiró el plazo que se informaba"):
                return True
            if p_strip.startswith("1. En el punto 2") or p_strip.startswith("2. En el punto 2"):
                return True
            if p_strip.startswith("1. Se reemplaza el punto") or p_strip.startswith("2. Se reemplaza el punto"):
                return True
            if p_strip.startswith("3. En el punto 4") or p_strip.startswith("2. En el punto 3"):
                return True
            if p_strip.startswith("Se deja sin efecto por completo la Circular"):
                return True
            if re.search(r"\b435\s+228\s+20-05-20\b", p_strip):
                return True

            return False

        # Filtrar secciones espurias de índice / tabla de contenidos y notas al pie o filas residuales de tabla
        secciones_filtradas: List[SeccionDDU] = []
        for sec in secciones:
            tit = str(sec.get("titulo", "")).strip()
            if re.search(r"\b(?:[IÍ]NDICE|TABLA\s+DE\s+CONTENIDO)\b", tit, re.IGNORECASE) or re.search(r"\.{4,}", tit):
                continue
            pars = [
                p for p in sec.get("parrafos", [])
                if not re.search(r"\.{5,}", p)
                and not re.search(r"\.{3,}\s*\d+$", p)
                and not re.search(r"\b[IÍ]NDICE\b\s*:", p, re.IGNORECASE)
                and not _es_inicio_nota_al_pie(p)
                and not _es_parrafo_de_tabla(p)
                and not re.match(r"^(?:\d+\.\s+)?(?:Sr\.|Sra\.|Sres\.|Biblioteca|Colegio|Instituto|Cámara|Depto|Archivo|Jefe|OIRS|Oficina)\b", p)
            ]

            if pars or tit:
                sec["parrafos"] = pars
                secciones_filtradas.append(sec)



        secciones = secciones_filtradas



        # Aplicar reparación de palabras OCR y descontaminación de tablas a cada párrafo de las secciones
        for sec in secciones:
            sec["parrafos"] = [_descontaminar_parrafo_de_tablas(_limpiar_texto_cuerpo(p)) for p in sec.get("parrafos", [])]



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
