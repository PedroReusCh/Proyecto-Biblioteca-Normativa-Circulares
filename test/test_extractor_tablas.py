"""Pruebas unitarias para el extractor modular de tablas (TablasExtractor)."""

from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.tablas import TablasExtractor


def test_tablas_extractor_registration() -> None:
    """Verifica que TablasExtractor esté registrado en ExtractorRegistry con nombre 'tablas'."""
    registrar_todos_los_extractores()
    extractors = ExtractorRegistry.get_all_extractors()
    assert "tablas" in extractors
    assert issubclass(extractors["tablas"], BaseExtractor)
    assert extractors["tablas"].__name__ == TablasExtractor.__name__
    instancia = TablasExtractor()
    assert instancia.nombre_bloque == "tablas"


def test_tablas_extractor_ddu_456_pdf() -> None:
    """Verifica la extracción estructurada de tablas en la circular DDU 456."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = TablasExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    tablas_lista: List[Dict[str, Any]] = resultado.datos.get("tablas", [])
    assert len(tablas_lista) == 4, f"Se esperaban 4 tablas en DDU 456, se encontraron {len(tablas_lista)}"

    # Páginas esperadas: 5, 6, 7, 8
    paginas = [t["pagina"] for t in tablas_lista]
    assert paginas == [5, 6, 7, 8]

    # Verificar tabla página 5
    t_pag5 = tablas_lista[0]
    encabezados_p5: List[str] = t_pag5["encabezados"]
    assert any("Circular" in h for h in encabezados_p5)
    assert any("Materia" in h for h in encabezados_p5)
    assert any("Motivo" in h or "Consideraciones" in h for h in encabezados_p5)

    filas_p5: List[List[str]] = t_pag5["filas"]
    assert len(filas_p5) >= 2
    # Verificar modificaciones de DDU 339 y DDU 322
    texto_fila_0 = " ".join(filas_p5[0])
    texto_fila_1 = " ".join(filas_p5[1])
    assert "DDU 339" in texto_fila_0
    assert "DDU 322" in texto_fila_1

    # Verificar tabla página 6 (DDU 168)
    t_pag6 = tablas_lista[1]
    filas_p6: List[List[str]] = t_pag6["filas"]
    texto_p6 = " ".join([" ".join(f) for f in filas_p6])
    assert "DDU 168" in texto_p6

    # Verificar representación Markdown
    for t in tablas_lista:
        md: str = str(t.get("markdown", ""))
        assert md.startswith("|")
        assert "| --- |" in md or "| ---" in md
        assert len(md.splitlines()) >= 3


def test_tablas_extractor_sin_tablas_texto() -> None:
    """Verifica el comportamiento con texto plano que no contiene tablas."""
    raw_text = "Esta es una circular sin tablas.\nSolo contiene párrafos narrativos."
    lines = raw_text.splitlines()

    extractor = TablasExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text=raw_text, lines=lines)

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is False
    assert resultado.datos == {"tablas": []}
    assert resultado.confianza == 0.0
    assert "No se detectaron tablas" in resultado.observaciones


def test_tablas_extractor_sin_tablas_pdf() -> None:
    """Verifica el comportamiento con un PDF real sin tablas (DDU 531 o DDU 533)."""
    pdf_path = Path("circulares/DDU 531.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró {pdf_path}")

    extractor = TablasExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is False
    assert resultado.datos == {"tablas": []}
    assert resultado.confianza == 0.0


def test_tablas_extractor_texto_markdown() -> None:
    """Verifica la extracción de una tabla en formato Markdown desde líneas de texto."""
    lines = [
        "A continuación se presenta el resumen:",
        "| Circular | Modificación | Motivo |",
        "| --- | --- | --- |",
        "| DDU 100 | Modifica art 1 | Actualización |",
        "| DDU 200 | Modifica art 2 | Nueva ley |",
        "Fin del documento.",
    ]
    raw_text = "\n".join(lines)

    extractor = TablasExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text=raw_text, lines=lines)

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    tablas: List[Dict[str, Any]] = resultado.datos.get("tablas", [])
    assert len(tablas) == 1
    t = tablas[0]
    assert t["encabezados"] == ["Circular", "Modificación", "Motivo"]
    assert len(t["filas"]) == 2
    assert t["filas"][0] == ["DDU 100", "Modifica art 1", "Actualización"]
    assert t["filas"][1] == ["DDU 200", "Modifica art 2", "Nueva ley"]
    assert "| Circular | Modificación | Motivo |" in t["markdown"]


def test_compactar_tabla_pdf_encabezados_con_espacios() -> None:
    """Verifica que celdas de encabezado con solo espacios se manejen sin generar IndexError."""
    from scripts.extractors.tablas import _compactar_tabla_pdf
    raw_table = [
        ["Col1", "   ", "Col3"],
        ["Val1", "   ", "Val3"],
    ]
    resultado = _compactar_tabla_pdf(raw_table)
    assert resultado is not None
    assert resultado["encabezados"] == ["Col1", "Col3"]
    assert len(resultado["filas"]) == 1
    assert resultado["filas"][0] == ["Val1", "Val3"]

