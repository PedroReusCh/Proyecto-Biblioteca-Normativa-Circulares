"""Utilidad de limpieza y reparación tipográfica para texto OCR."""

import re
from typing import Dict

# Correcciones directas seguras con delimitadores de palabra explícitos
CORRECCIONES_DIRECTAS: Dict[str, str] = {
    r"\bBiblioteca del Congreso Nacionar\b": "Biblioteca del Congreso Nacional",
    r"\bterr itori al\b": "territorial",
    r"\bi nmobiliarios\b": "inmobiliarios",
    r"\bpartes uperior\b": "parte superior",
    r"\bcons iderar\b": "considerar",
    r"\binst ituto\b": "instituto",
    r"\bAD!\b": "ADI",
    r"\bpo\s+r\b": "por",
    r"\bN[°º\?]?S,\s*\(V\.\s*y\s*U\.\)": "N° 5, (V. y U.)",
}




def preservar_casing(texto_original: str, texto_reemplazo: str) -> str:
    """Ajusta las mayúsculas/minúsculas del reemplazo según el texto original."""
    if texto_original.isupper():
        return texto_reemplazo.upper()
    if texto_original and texto_original[0].isupper() and not texto_reemplazo[0].isupper():
        return texto_reemplazo.capitalize()
    return texto_reemplazo


_preservar_casing = preservar_casing



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

    # 1. Aplicar correcciones directas delimitadas por palabra
    for patron_str, corr in CORRECCIONES_DIRECTAS.items():
        patron = re.compile(patron_str, re.IGNORECASE)
        resultado = patron.sub(lambda m, c=corr: _preservar_casing(m.group(0), c), resultado)

    # 2. Reparar fragmentaciones de prefijos/raíces comunes
    resultado = re.sub(
        r"\b([a-zA-ZáéíóúÁÉÍÓÚñÑ])\s+(rt[ií]cul\w+|uperior\w*|ecret\w+|rdinanz\w+)\b",
        r"\1\2",
        resultado,
        flags=re.IGNORECASE,
    )
    resultado = re.sub(
        r"\b(vig)\s+([eé]sim\w+)\b",
        r"\1\2",
        resultado,
        flags=re.IGNORECASE,
    )
    resultado = re.sub(
        r"\b(arquitect[oó]ni)\s+(cos)\b",
        r"\1\2",
        resultado,
        flags=re.IGNORECASE,
    )

    # 3. Reparar sufijos/desinencias separadas al final de palabras (ej: "inciso s", "relativo s", "quinch os")
    resultado = re.sub(
        r"\b([a-zA-ZáéíóúÁÉÍÓÚñÑ]{3,})\s+([sS]|os|as|mo|ren)\b",
        r"\1\2",
        resultado,
    )


    # 4. Normalizar espacios espurios antes de signos de puntuación (ej: "N° 58 , " -> "N° 58, ")
    resultado = re.sub(r"\s+([,.:;])", r"\1", resultado)

    # 5. Normalizar espacios múltiples
    resultado = re.sub(r"[ \t]+", " ", resultado).strip()

    return resultado


__all__ = ["limpiar_palabras_ocr", "preservar_casing", "CORRECCIONES_DIRECTAS"]


