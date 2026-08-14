"""Pruebas unitarias para el extractor modular de tablas (TablasExtractor)."""

import csv
from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.tablas import TablasExtractor

PROYECTO_RAIZ = Path(__file__).resolve().parents[1]


def test_tablas_extractor_registration() -> None:
    """Verifica que TablasExtractor esté registrado en ExtractorRegistry con nombre 'tablas'."""
    registrar_todos_los_extractores()
    extractors = ExtractorRegistry.get_all_extractors()
    assert "tablas" in extractors
    assert issubclass(extractors["tablas"], BaseExtractor)
    assert extractors["tablas"].__name__ == TablasExtractor.__name__
    instancia = TablasExtractor()
    assert instancia.nombre_bloque == "tablas"


def test_tablas_extractor_ddu_456_pdf(tmp_path: Path) -> None:
    """Verifica la extracción de tablas en DDU 456, generación de manifiesto y archivos CSV anexos."""
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    extractor = TablasExtractor()
    salidas_dir = tmp_path / "salidas_tablas"
    resultado: ResultadoBloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=pdf_path,
        output_dir=salidas_dir,
    )

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    tablas_manifest: List[Dict[str, Any]] = resultado.datos.get("tablas", [])
    assert len(tablas_manifest) == 4, f"Se esperaban 4 tablas en DDU 456, se encontraron {len(tablas_manifest)}"

    # 1. Verificar IDs canónicos
    ids = [t["id"] for t in tablas_manifest]
    assert ids == ["DDU_456_tabla_1", "DDU_456_tabla_2", "DDU_456_tabla_3", "DDU_456_tabla_4"]

    # 2. Páginas esperadas: 5, 6, 7, 8
    paginas = [t["pagina"] for t in tablas_manifest]
    assert paginas == [5, 6, 7, 8]

    # 3. Metadatos del manifiesto
    for t in tablas_manifest:
        assert "id" in t
        assert "nombre" in t
        assert "pagina" in t
        assert "filas" in t
        assert "columnas" in t
        assert "archivo_anexo" in t
        assert t["filas"] >= 1
        assert t["columnas"] >= 2

    # 4. Verificar existencia y contenido de archivos CSV generados
    t1 = tablas_manifest[0]
    assert "DDU 339" in t1["nombre"] or "DDU 322" in t1["nombre"]
    csv1_path = salidas_dir / "DDU_456_tabla_1.csv"
    assert csv1_path.exists(), f"No se encontró el archivo anexo {csv1_path}"

    with open(csv1_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert any("Circular" in h for h in header)
        assert any("Materia" in h for h in header)

        rows = list(reader)
        assert len(rows) >= 2
        todo_texto = " ".join([" ".join(r) for r in rows])
        assert "DDU 339" in todo_texto
        assert "DDU 322" in todo_texto

    # Verificar tabla 2 (DDU 168)
    csv2_path = salidas_dir / "DDU_456_tabla_2.csv"
    assert csv2_path.exists()
    with open(csv2_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        next(reader)
        rows = list(reader)
        todo_texto2 = " ".join([" ".join(r) for r in rows])
        assert "DDU 168" in todo_texto2


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
    pdf_path = PROYECTO_RAIZ / "circulares" / "DDU 531.pdf"
    if not pdf_path.exists():
        pytest.skip(f"No se encontró {pdf_path}")

    extractor = TablasExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text="", lines=[], pdf_path=pdf_path)

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is False
    assert resultado.datos == {"tablas": []}
    assert resultado.confianza == 0.0


def test_tablas_extractor_texto_markdown(tmp_path: Path) -> None:
    """Verifica la extracción de una tabla en formato Markdown desde líneas de texto y exportación a CSV."""
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
    salidas_dir = tmp_path / "salidas_tablas"
    resultado: ResultadoBloque = extractor.extract(
        raw_text=raw_text,
        lines=lines,
        output_dir=salidas_dir,
    )

    assert resultado.nombre_bloque == "tablas"
    assert resultado.exito is True
    assert resultado.confianza == 1.0

    tablas: List[Dict[str, Any]] = resultado.datos.get("tablas", [])
    assert len(tablas) == 1
    t = tablas[0]
    assert t["pagina"] == 1
    assert t["filas"] == 2
    assert t["columnas"] == 3
    assert "DDU" in t["id"]
    assert "archivo_anexo" in t

    csv_path = salidas_dir / f"{t['id']}.csv"
    assert csv_path.exists()
    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert header == ["Circular", "Modificación", "Motivo"]
        rows = list(reader)
        assert len(rows) == 2
        assert rows[0] == ["DDU 100", "Modifica art 1", "Actualización"]


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
