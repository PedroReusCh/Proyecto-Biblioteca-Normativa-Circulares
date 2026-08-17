"""Pruebas unitarias para el extractor modular de modificaciones posteriores (ModificacionesPosterioresExtractor)."""

from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.modificaciones_posteriores import ModificacionesPosterioresExtractor

PROYECTO_RAIZ = Path(__file__).resolve().parents[1]


def test_modificaciones_posteriores_registration() -> None:
    """Verifica que ModificacionesPosterioresExtractor esté registrado en ExtractorRegistry."""
    registrar_todos_los_extractores()
    extractors = ExtractorRegistry.get_all_extractors()
    assert "modificaciones_posteriores" in extractors
    assert issubclass(extractors["modificaciones_posteriores"], BaseExtractor)
    instancia = ModificacionesPosterioresExtractor()
    assert instancia.nombre_bloque == "modificaciones_posteriores"


def test_modificaciones_posteriores_ddu_456_pdf() -> None:
    """Verifica la extracción como texto libre de la nota marginal de modificación posterior en DDU 456."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    import pypdf
    reader = pypdf.PdfReader(pdf_path)
    raw_text = "\n".join([str(p.extract_text() or "") for p in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    extractor = ModificacionesPosterioresExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text, lines, pdf_path=pdf_path)

    assert resultado.nombre_bloque == "modificaciones_posteriores"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    texto_mod: str = str(resultado.datos.get("texto", ""))
    assert "Circular Modificada por Circular Ord. N°214" in texto_mod
    assert "02 de mayo de 2024, DDU 498 (numeral 7.)" in texto_mod
    assert "Mediante Circular Ord" not in texto_mod




def test_modificaciones_posteriores_sin_modificaciones() -> None:
    """Verifica el comportamiento cuando la circular no tiene notas marginales de modificación."""
    raw_text = "DDU 100\nCIRCULAR ORD. N° 10\nMAT.: Materia general.\n1. Conforme a las normas..."
    lines = raw_text.splitlines()

    extractor = ModificacionesPosterioresExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text, lines)

    assert resultado.nombre_bloque == "modificaciones_posteriores"
    assert resultado.exito is False
    assert resultado.datos.get("texto") == ""
    assert resultado.confianza == 0.0
