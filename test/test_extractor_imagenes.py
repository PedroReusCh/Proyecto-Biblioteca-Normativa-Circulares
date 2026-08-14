"""Pruebas unitarias para el extractor modular de imágenes (ImagenesExtractor)."""

from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.imagenes import ImagenesExtractor


def test_imagenes_extractor_registration() -> None:
    """Verifica que ImagenesExtractor esté registrado en ExtractorRegistry con nombre 'imagenes'."""
    registrar_todos_los_extractores()
    extractors = ExtractorRegistry.get_all_extractors()
    assert "imagenes" in extractors
    assert issubclass(extractors["imagenes"], BaseExtractor)
    assert extractors["imagenes"].__name__ == ImagenesExtractor.__name__
    instancia = ImagenesExtractor()
    assert instancia.nombre_bloque == "imagenes"


def test_imagenes_extractor_ddu_456_pdf() -> None:
    """Verifica la extracción estructurada de imágenes y esquemas en la circular DDU 456."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = ImagenesExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    imagenes_lista: List[Dict[str, Any]] = resultado.datos.get("imagenes", [])
    assert len(imagenes_lista) >= 1, "Se esperaba al menos 1 esquema técnico relevante en DDU 456"

    # Verificar el esquema técnico principal de planta azotea y corte en página 3
    img_p3 = next((img for img in imagenes_lista if img.get("pagina") == 3), None)
    assert img_p3 is not None, "No se encontró la imagen técnica de la página 3"
    assert img_p3["ancho"] == 700
    assert img_p3["alto"] == 760
    assert img_p3["formato"] == "jpeg"
    assert img_p3["xref"] == 5
    descripcion: str = str(img_p3.get("descripcion", "")).lower()
    assert any(k in descripcion for k in ["esquema", "planta azotea", "corte", "diagrama"])


def test_imagenes_extractor_filtrado_lineas_y_membretes() -> None:
    """Verifica que líneas menores a 60px y membretes institucionales sean filtrados."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = ImagenesExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    imagenes_lista: List[Dict[str, Any]] = resultado.datos.get("imagenes", [])

    # Ninguna imagen extraída debe tener alto o ancho menor a 60px
    for img in imagenes_lista:
        assert img["alto"] >= 60, f"Imagen {img} tiene alto < 60px"
        assert img["ancho"] >= 60, f"Imagen {img} tiene ancho < 60px"

    # La línea de pie de página de 8px (xref 458) no debe estar presente
    xrefs = [img["xref"] for img in imagenes_lista]
    assert 458 not in xrefs, "La línea de pie de página (xref 458) no fue filtrada"


def test_imagenes_extractor_sin_imagenes_texto() -> None:
    """Verifica el comportamiento con texto plano que no contiene imágenes."""
    raw_text = "Esta es una circular sin imágenes.\nSolo contiene párrafos narrativos."
    lines = raw_text.splitlines()

    extractor = ImagenesExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text=raw_text, lines=lines)

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is False
    assert resultado.datos == {"imagenes": []}
    assert resultado.confianza == 0.0
    assert "No se detectaron imágenes" in resultado.observaciones


def test_imagenes_extractor_sin_imagenes_pdf() -> None:
    """Verifica el comportamiento con un PDF escaneado sin diagramas técnicos (DDU 531)."""
    pdf_path = Path("circulares/DDU 531.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró {pdf_path}")

    extractor = ImagenesExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is False
    assert resultado.datos == {"imagenes": []}
    assert resultado.confianza == 0.0


def test_imagenes_extractor_texto_markdown() -> None:
    """Verifica la extracción de una imagen en formato Markdown desde líneas de texto."""
    lines = [
        "A continuación se presenta el esquema descriptivo:",
        "![Esquema técnico de planta y corte](esquema_planta_corte.png)",
        "Fin del documento.",
    ]
    raw_text = "\n".join(lines)

    extractor = ImagenesExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text=raw_text, lines=lines)

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    imagenes: List[Dict[str, Any]] = resultado.datos.get("imagenes", [])
    assert len(imagenes) == 1
    img = imagenes[0]
    assert img["descripcion"] == "Esquema técnico de planta y corte"
    assert img["formato"] == "png"
    assert img["pagina"] == 1
