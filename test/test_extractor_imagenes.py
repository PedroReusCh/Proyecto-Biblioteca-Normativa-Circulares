"""Pruebas unitarias para el extractor modular de imágenes (ImagenesExtractor)."""

from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.imagenes import ImagenesExtractor

PROYECTO_RAIZ = Path(__file__).resolve().parents[1]


def test_imagenes_extractor_registration() -> None:
    """Verifica que ImagenesExtractor esté registrado en ExtractorRegistry con nombre 'imagenes'."""
    registrar_todos_los_extractores()
    extractors = ExtractorRegistry.get_all_extractors()
    assert "imagenes" in extractors
    assert issubclass(extractors["imagenes"], BaseExtractor)
    assert extractors["imagenes"].__name__ == ImagenesExtractor.__name__
    instancia = ImagenesExtractor()
    assert instancia.nombre_bloque == "imagenes"


def test_imagenes_extractor_ddu_456_pdf(tmp_path: Path) -> None:
    """Verifica la extracción estructurada de imágenes y guardado físico en DDU 456."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = ImagenesExtractor()
    salidas_dir = tmp_path / "salidas_imagenes"
    resultado: ResultadoBloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=pdf_path,
        output_dir=salidas_dir,
    )

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    imagenes_lista: List[Dict[str, Any]] = resultado.datos.get("imagenes", [])
    assert len(imagenes_lista) >= 1, "Se esperaba al menos 1 esquema técnico relevante en DDU 456"

    # Verificar el esquema técnico principal de planta azotea y corte en página 3
    img_p3 = next((img for img in imagenes_lista if img.get("pagina") == 3), None)
    assert img_p3 is not None, "No se encontró la imagen técnica de la página 3"
    assert img_p3["id"] == "DDU_456_img_1"
    assert img_p3["ancho"] >= 700
    assert img_p3["alto"] >= 760
    assert "x" in img_p3["dimensiones"]
    assert img_p3["formato"] == "png"
    assert img_p3["xref"] == 5
    assert img_p3["tipo"] == "Esquema técnico"
    assert "archivo_anexo" in img_p3

    assert img_p3["archivo_anexo"] == "salidas_imagenes/DDU_456_img_1.png"

    nombre: str = str(img_p3.get("nombre", "")).lower()
    assert any(k in nombre for k in ["esquema", "planta azotea", "corte", "diagrama"])

    # Verificar existencia física del archivo binario extraído en PNG
    img_file = salidas_dir / "DDU_456_img_1.png"
    assert img_file.exists(), f"No se encontró el archivo guardado {img_file}"
    assert img_file.stat().st_size > 1000, "El archivo de imagen guardado está vacío o corrupto"


def test_imagenes_extractor_filtrado_lineas_y_membretes(tmp_path: Path) -> None:
    """Verifica que líneas menores a 60px y membretes institucionales sean filtrados."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = ImagenesExtractor()
    salidas_dir = tmp_path / "salidas_imagenes"
    resultado: ResultadoBloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=pdf_path,
        output_dir=salidas_dir,
    )

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
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 531.pdf"
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
    assert img["nombre"] == "Esquema técnico de planta y corte"
    assert img["formato"] == "png"
    assert img["pagina"] == 1
    assert "archivo_anexo" in img


def test_imagenes_extractor_ddu_547_pdf(tmp_path: Path) -> None:
    """Verifica la extracción acotada y precisa del organigrama en página 10 de DDU 547 sin incluir texto circundante."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 547.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró {pdf_path}")

    extractor = ImagenesExtractor()
    salidas_dir = tmp_path / "salidas_imagenes"
    resultado: ResultadoBloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=pdf_path,
        output_dir=salidas_dir,
    )

    assert resultado.nombre_bloque == "imagenes"
    assert resultado.exito is True
    imagenes: List[Dict[str, Any]] = resultado.datos.get("imagenes", [])
    assert len(imagenes) == 1, f"Se esperaba exactamente 1 esquema técnico en DDU 547, se obtuvieron {len(imagenes)}"

    img_p10 = imagenes[0]
    assert img_p10["id"] == "DDU_547_img_1"
    assert img_p10["pagina"] == 10
    assert img_p10["formato"] == "png"
    assert "Urbanizaciones voluntarias desvinculadas" in img_p10["descripcion"]
    assert img_p10["archivo_anexo"] == "salidas_imagenes/DDU_547_img_1.png"

    # Verificar que el recorte es ajustado al diagrama y no incluye la página completa
    assert img_p10["alto"] < 800, f"El alto de la imagen ({img_p10['alto']}px) es excesivo y contiene texto de la página"
    assert img_p10["ancho"] >= 1500

    img_file = salidas_dir / "DDU_547_img_1.png"
    assert img_file.exists(), f"No se encontró el archivo {img_file}"
    assert img_file.stat().st_size > 1000

