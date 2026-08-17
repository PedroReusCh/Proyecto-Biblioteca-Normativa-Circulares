"""Pruebas unitarias para el extractor modular de tablas (TablasExtractor)."""

import csv
from pathlib import Path
from typing import Any, Dict, List
import pytest

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import BaseExtractor, ExtractorRegistry, ResultadoBloque
from scripts.extractors.tablas import TablasExtractor, normalizar_texto_celda_tabla


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
    """Verifica la extracción consolidada de tablas multi-página en DDU 456."""
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
    # Tabla consolidada: 4 páginas → 1 tabla lógica (mismos encabezados)
    assert len(tablas_manifest) == 1, f"Se esperaba 1 tabla consolidada, se encontraron {len(tablas_manifest)}"

    t = tablas_manifest[0]

    # 1. ID canónico
    assert t["id"] == "DDU_456_tabla_1"

    # 2. Páginas consolidadas
    assert t["paginas"] == [5, 6, 7, 8]

    # 3. Nombre descriptivo con las 3 circulares
    assert "DDU 339" in t["nombre"]
    assert "DDU 322" in t["nombre"]
    assert "DDU 168" in t["nombre"]

    # 4. Metadatos del manifiesto
    assert t["filas"] >= 3  # Al menos DDU 339, DDU 322, DDU 168
    assert t["columnas"] == 3
    assert "archivo_anexo" in t

    # 5. Verificar existencia y contenido del CSV consolidado
    csv_path = salidas_dir / "DDU_456_tabla_1.csv"
    assert csv_path.exists(), f"No se encontró el archivo anexo {csv_path}"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert any("Circular" in h for h in header)
        assert any("Materia" in h for h in header)

        rows = list(reader)
        assert len(rows) >= 3
        todo_texto = " ".join([" ".join(r) for r in rows])
        assert "DDU 339" in todo_texto
        assert "DDU 322" in todo_texto
        assert "DDU 168" in todo_texto


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
    assert t["paginas"] == [1]
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


def test_normalizar_texto_celda_tabla() -> None:
    """Verifica que normalizar_texto_celda_tabla una saltos de columna y preserve párrafos/numerales."""
    # Caso 1: Fragmentación estrecha por columna de PDF
    fragmentado = (
        "La materia contenida en la\n"
        "Circular DDU 339 se aborda\n"
        "en el punto 5 6 de\n"
        "esta Circular, la que\n"
        "actualiza la referencia al\n"
        "inciso en que quedó la\n"
        "norma que señala que.\n"
        "Mediante Circular Ord. N°214,\n"
        "de fecha 02.05.2024, DDU\n"
        "498, se aclara."
    )
    res = normalizar_texto_celda_tabla(fragmentado)
    lineas = res.splitlines()
    assert len(lineas) == 2, f"Se esperaban 2 párrafos lógicos, se obtuvieron {len(lineas)}"
    assert lineas[0] == "La materia contenida en la Circular DDU 339 se aborda en el punto 5 6 de esta Circular, la que actualiza la referencia al inciso en que quedó la norma que señala que."
    assert lineas[1] == "Mediante Circular Ord. N°214, de fecha 02.05.2024, DDU 498, se aclara."

    # Caso 2: Letras de incisos a), b)
    incisos = (
        "a) Reemplázase el numeral 2\n"
        "por el siguiente:\n"
        "2. Al respecto, cabe\n"
        "hacer presente que.\n"
        "b) Reemplázase el numeral 4\n"
        "por el siguiente:\n"
        "4. Conforme a lo anterior."
    )
    res_incisos = normalizar_texto_celda_tabla(incisos)
    lineas_inc = res_incisos.splitlines()
    assert len(lineas_inc) >= 2
    assert lineas_inc[0].startswith("a) Reemplázase")
    assert any(l.startswith("b) Reemplázase") for l in lineas_inc)

    # Caso 3: Columna de identificación de circular
    col_ddu = "DDU 339\nCircular\nOrd. N°\n0087 de\nfecha\n06.03.2017"
    res_ddu = normalizar_texto_celda_tabla(col_ddu)
    assert res_ddu == "DDU 339 Circular Ord. N° 0087 de fecha 06.03.2017"

