"""Pruebas unitarias para el extractor del metadato Nota al Pie (NotaAlPieExtractor)."""

from typing import Any, List

from scripts.extractors.nota_al_pie import NotaAlPieExtractor


def test_nota_al_pie_extractor_ddu_537() -> None:
    """Verifica la extracción de notas explicativas y referencias al pie de página."""
    lines = [
        "DE LA PLANIFICACION URBANA.",
        "1. De conformidad con lo dispuesto...",
        "1 Artículo 38. Lineamientos y estándares de los mapas de amenaza y riesgo. Mapas de Amenaza deberán cumplir con los estándares.",
        "2 La orientación técnica específica para estas materias está contenida en el punto 2.3 de la Circular DDU 510.",
        "Saluda atentamente a Ud.,",
    ]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.nombre_bloque == "nota_al_pie"
    assert resultado.exito is True
    notas: str = str(resultado.datos.get("notas_al_pie", ""))
    assert "1 Artículo 38" in notas
    assert "2 La orientación técnica" in notas
