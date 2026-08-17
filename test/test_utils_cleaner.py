"""Pruebas unitarias para el saneador tipográfico OCR universal."""

from scripts.extractors.utils_cleaner import limpiar_palabras_ocr


def test_limpiar_palabras_ocr_ddu_456_materia() -> None:
    """Verifica la reparación de palabras y letras fragmentadas en la materia de DDU 456."""
    texto_sucio = (
        "Aplicación a rtículo 2.6.3. inciso s vigésimo, vigésimo primero, vigésimo segundo y "
        "vigésimo tercero de la OGUC, sobre terrazas y elementos exteriores ubicados en la parte "
        "superior de los edificios y pisos mecánicos."
    )
    esperado = (
        "Aplicación artículo 2.6.3. incisos vigésimo, vigésimo primero, vigésimo segundo y "
        "vigésimo tercero de la OGUC, sobre terrazas y elementos exteriores ubicados en la parte "
        "superior de los edificios y pisos mecánicos."
    )
    assert limpiar_palabras_ocr(texto_sucio) == esperado


def test_limpiar_palabras_ocr_patrones_recurrentes() -> None:
    """Verifica reparaciones comunes de OCR como terminaciones en -s, -mo, -os, -ren, -cos."""
    texto = "relativo s a los quinch os que se encuent ren con elementos arquitectóni cos en la partes uperior"
    esperado = "relativos a los quinchos que se encuentren con elementos arquitectónicos en la parte superior"
    assert limpiar_palabras_ocr(texto) == esperado


def test_limpiar_palabras_ocr_puntuacion() -> None:
    """Verifica la normalización de espacios antes de signos de puntuación."""
    texto = "El Decreto Supremo N° 58 , publicado en el D.O. el 28.02.2019 ."
    esperado = "El Decreto Supremo N° 58, publicado en el D.O. el 28.02.2019."
    assert limpiar_palabras_ocr(texto) == esperado


def test_limpiar_palabras_ocr_cadena_vacia() -> None:
    """Verifica que cadenas vacías o compuestas solo de espacios se manejen de forma segura."""
    assert limpiar_palabras_ocr("") == ""
    assert limpiar_palabras_ocr("   ") == ""


def test_limpiar_palabras_ocr_casos_especificos() -> None:
    """Verifica individualmente los casos de palabras fragmentadas requeridos por la especificación."""
    assert limpiar_palabras_ocr("a rtículo") == "artículo"
    assert limpiar_palabras_ocr("inciso s") == "incisos"
    assert limpiar_palabras_ocr("relativo s") == "relativos"
    assert limpiar_palabras_ocr("quinch os") == "quinchos"
    assert limpiar_palabras_ocr("vigési mo") == "vigésimo"
    assert limpiar_palabras_ocr("vig ésimo") == "vigésimo"
    assert limpiar_palabras_ocr("encuent ren") == "encuentren"
    assert limpiar_palabras_ocr("arquitectóni cos") == "arquitectónicos"


def test_limpiar_palabras_ocr_no_corrompe_palabras_validas() -> None:
    """Verifica que palabras válidas similares no sean alteradas o corrompidas por límites de palabra."""
    frase_valida = (
        "fraccionar terrenos para estacionar vehículos en propiedad exclusiva "
        "según el informe sobre normas de copropiedad (por razones de seguridad)."
    )
    assert limpiar_palabras_ocr(frase_valida) == frase_valida


def test_limpiar_palabras_ocr_preserva_mayusculas() -> None:
    """Verifica que si el texto original está en mayúsculas sostenidas, la reparación preserve el casing."""
    assert limpiar_palabras_ocr("APLICACIÓN A RTÍCULO") == "APLICACIÓN ARTÍCULO"
    assert limpiar_palabras_ocr("INCISO S VIGÉSIMO") == "INCISOS VIGÉSIMO"

