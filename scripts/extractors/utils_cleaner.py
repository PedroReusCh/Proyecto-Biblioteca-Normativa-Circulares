"""Utilidad de limpieza y reparación tipográfica para texto OCR."""

import re
from typing import Dict

# Diccionario de correcciones fijas de alta precisión para fragmentaciones OCR frecuentes
CORRECCIONES_DIRECTAS: Dict[str, str] = {
    "a rtículo": "artículo",
    "a rtículos": "artículos",
    "a rt.": "art.",
    "inciso s": "incisos",
    "relativo s": "relativos",
    "quinch os": "quinchos",
    "vigési mo": "vigésimo",
    "vig ésimo": "vigésimo",
    "encuent ren": "encuentren",
    "arquitectóni cos": "arquitectónicos",
    "arquitectoni cos": "arquitectónicos",
    "partes uperior": "parte superior",
    "cons iderar": "considerar",
    "inst ituto": "instituto",
    "po r": "por",
    "d el": "del",
    "d e": "de",
    "e n": "en",
    "ad!": "ADI",
    "ad )": "ADI",
    "nacionar": "nacional",
    "terr itori al": "territorial",
    "i nmobiliarios": "inmobiliarios",
}


def limpiar_palabras_ocr(texto: str) -> str:
    """Repara palabras y letras fragmentadas comúnmente por procesos OCR y espaciados espurios.

    Args:
        texto: Cadena de texto a procesar.

    Returns:
        Texto saneado con palabras unificadas y puntuación corregida.
    """
    if not texto:
        return ""

    resultado = texto

    # 1. Aplicar correcciones directas conocidas (case-insensitive)
    for err, corr in CORRECCIONES_DIRECTAS.items():
        patron = re.compile(re.escape(err), re.IGNORECASE)
        resultado = patron.sub(corr, resultado)

    # 2. Reparar letras aisladas antes de palabras comunes (ej: "a rtículo", "s uperior")
    resultado = re.sub(
        r"\b([a-zA-ZáéíóúÁÉÍÓÚñÑ])\s+(rt[ií]cul\w+|uperior\w*|ecret\w+|rdinanz\w+)\b",
        r"\1\2",
        resultado,
        flags=re.IGNORECASE,
    )

    # 3. Reparar sufijos/desinencias separadas al final de palabras (ej: "inciso s", "relativo s", "quinch os")
    resultado = re.sub(
        r"\b([a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,})\s+([sS]|os|as|mo|cos|ren)\b",
        r"\1\2",
        resultado,
    )

    # 4. Normalizar espacios espurios antes de signos de puntuación (ej: "N° 58 , " -> "N° 58, ")
    resultado = re.sub(r"\s+([,.:;])", r"\1", resultado)

    # 5. Normalizar espacios múltiples
    resultado = re.sub(r"[ \t]+", " ", resultado).strip()

    return resultado
