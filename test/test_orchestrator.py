"""Pruebas de integración para DDUOrchestrator y exportadores de CSV."""

import csv
from pathlib import Path
from typing import List

import pytest

from scripts.ddu_orchestrator import DDUOrchestrator
from scripts.ddu_types import DatosCircularDDU

PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
PDF_DDU_533 = PROYECTO_RAIZ / "circulares" / "DDU 533.pdf"


def test_orchestrator_process_pdf_ddu_533() -> None:
    """Verifica que DDUOrchestrator procese correctamente el PDF de la DDU 533."""
    orchestrator = DDUOrchestrator()
    datos: DatosCircularDDU = orchestrator.process_pdf(PDF_DDU_533)

    assert datos["numero"] == "533"
    assert datos["fecha"] == "2026-02-27"
    assert "extraordinaria" in datos["materia"]
    assert "JEFE" in datos["emisor"] and "DESARROLLO URBANO" in datos["emisor"]
    assert "Decreto Supremo" in datos["antecedentes"] and "OGUC" in datos["antecedentes"]
    assert isinstance(datos["secciones"], list)
    assert len(datos["secciones"]) > 0

    # Campos opcionales del decorador de extractores
    assert "numero_ord" in datos
    assert "CIRCULAR ORD." in datos["numero_ord"]
    assert "destinatarios" in datos
    assert "SEGÚN DISTRIBUCIÓN" in datos["destinatarios"]


def test_orchestrator_fallback_texto_corto() -> None:
    """Verifica la carga de fallback estático cuando el texto plano extraído es menor a 50 caracteres."""
    orchestrator = DDUOrchestrator()
    datos = orchestrator.process_text("Texto corto DDU", filename="DDU 530.pdf")

    assert datos["numero"] == "530"
    assert datos["fecha"] == "2023-01-20"
    assert "Modificación de proyecto" in datos["materia"]


def test_export_individual_csv(tmp_path: Path) -> None:
    """Verifica la generación del CSV individual para una circular DDU."""
    orchestrator = DDUOrchestrator()
    output_dir = tmp_path / "csv_output"
    
    csv_path = orchestrator.export_individual_csv(PDF_DDU_533, output_dir)
    
    assert csv_path.exists()
    assert csv_path.name == "DDU_533_extraido.csv"

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == ["bloque", "campo", "valor"]
        
        rows = list(reader)
        campos = [row[1] for row in rows]
        assert "numero" in campos
        assert "materia" in campos
        assert "fecha" in campos
        assert "emisor" in campos


def test_export_master_csv(tmp_path: Path) -> None:
    """Verifica la generación del dataset CSV acumulado master para múltiples circulares DDU."""
    orchestrator = DDUOrchestrator()
    pdf_list: List[Path] = [
        PROYECTO_RAIZ / "circulares" / "DDU 533.pdf",
        PROYECTO_RAIZ / "circulares" / "DDU 531.pdf",
    ]
    master_path = tmp_path / "master" / "dataset_master_ddu.csv"

    res_path = orchestrator.export_master_csv(pdf_list, master_path)

    assert res_path.exists()
    assert res_path.name == "dataset_master_ddu.csv"

    with open(res_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        assert header == [
            "numero",
            "fecha",
            "lugar",
            "materia",
            "emisor",
            "antecedentes",
            "numero_ord",
            "descriptores",
            "destinatarios",
            "firmante",
            "lista_distribucion",
            "cant_secciones",
        ]

        rows = list(reader)
        assert len(rows) == 2
        numeros = [row[0] for row in rows]
        assert "533" in numeros
        assert "531" in numeros


def test_export_master_csv_error_handling(tmp_path: Path) -> None:
    """Verifica que export_master_csv capture errores en archivos PDF defectuosos o inexistentes y continúe."""
    orchestrator = DDUOrchestrator()
    pdf_list: List[Path] = [
        PROYECTO_RAIZ / "circulares" / "DDU 533.pdf",
        tmp_path / "pdf_inexistente.pdf",
    ]
    master_path = tmp_path / "master" / "dataset_master_error_test.csv"

    res_path = orchestrator.export_master_csv(pdf_list, master_path)

    assert res_path.exists()
    with open(res_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        rows = list(reader)
        # Solo el PDF válido debe haberse procesado y agregado a las filas
        assert len(rows) == 1
        assert rows[0][0] == "533"

