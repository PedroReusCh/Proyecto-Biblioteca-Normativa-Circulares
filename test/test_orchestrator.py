"""Pruebas de integración para DDUOrchestrator y exportadores de CSV."""

import csv
from pathlib import Path
from typing import List


from scripts.ddu_orchestrator import DDUOrchestrator
from scripts.ddu_types import DatosCircularDDU

PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
PDF_DDU_533 = PROYECTO_RAIZ / "circulares" / "DDU 533.pdf"
PDF_DDU_456 = PROYECTO_RAIZ / "circulares" / "DDU 456.pdf"


def test_orchestrator_process_pdf_ddu_533() -> None:
    """Verifica que DDUOrchestrator procese correctamente el PDF de la DDU 533."""
    orchestrator = DDUOrchestrator()
    datos: DatosCircularDDU = orchestrator.process_pdf(PDF_DDU_533)

    assert "533" in datos["numero"]
    assert datos["fecha"] == "2026-02-27"
    assert "extraordinaria" in datos["materia"]
    assert "JEFE" in datos["emisor"] and "DESARROLLO URBANO" in datos["emisor"]
    assert "Decreto Supremo" in datos["antecedentes"] and "OGUC" in datos["antecedentes"]
    assert isinstance(datos["secciones"], list)
    assert len(datos["secciones"]) > 0

    # Campos opcionales de los extractores modulares
    assert "numero_ord" in datos
    assert "CIRCULAR ORD." in datos["numero_ord"]
    assert "destinatarios" in datos
    assert "SEGÚN DISTRIBUCIÓN" in datos["destinatarios"]


def test_export_individual_csv(tmp_path: Path) -> None:
    """Verifica la generación del CSV individual para una circular DDU."""
    orchestrator = DDUOrchestrator()
    output_dir = tmp_path / "csv_output"

    csv_path = orchestrator.export_individual_csv(PDF_DDU_533, output_dir)

    assert csv_path.exists()
    assert csv_path.name == "DDU_533_extraido.csv"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert header == ["bloque", "campo", "valor_extraido"]

        rows = list(reader)
        campos = [row[1] for row in rows]
        assert "numero_ddu" in campos
        assert "materia" in campos
        assert "fecha_emision" in campos
        assert "emisor" in campos


def test_export_individual_csv_ddu_456(tmp_path: Path) -> None:
    """Verifica el CSV individual estándar para la circular DDU 456."""
    orchestrator = DDUOrchestrator()
    output_dir = tmp_path / "csv_output"

    csv_path = orchestrator.export_individual_csv(PDF_DDU_456, output_dir)

    assert csv_path.exists()
    assert csv_path.name == "DDU_456_extraido.csv"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        rows = {row["campo"]: row["valor_extraido"] for row in reader}

    assert rows["materia"]
    assert "NORMAS URBANISTICAS" in rows["descriptores"].upper()
    assert "PLANTA AZOTEA" not in rows["cuerpo"].upper()
    assert "CIRCULAR MATERIA(S) QUE SE MODIFICA(N)" not in rows["cuerpo"].upper()
    assert "CONSIDERACIONES" not in rows["firmante"].upper()
    assert "[" not in rows["lista_distribucion"]
    assert "]" not in rows["lista_distribucion"]
    assert "imagen" in rows
    assert "tabla" in rows


def test_export_master_csv(tmp_path: Path) -> None:
    """Verifica la generación del dataset CSV acumulado master para múltiples circulares DDU."""
    orchestrator = DDUOrchestrator()
    pdf_list: List[Path] = [
        PROYECTO_RAIZ / "circulares" / "DDU 533.pdf",
    ]
    master_path = tmp_path / "master" / "dataset_master_ddu.csv"

    res_path = orchestrator.export_master_csv(pdf_list, master_path)

    assert res_path.exists()
    assert res_path.name == "dataset_master_ddu.csv"

    with open(res_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert header == [
            "numero_ddu",
            "numero_ord",
            "antecedentes",
            "materia",
            "descriptores",
            "fecha_emision",
            "lugar",
            "destinatarios",
            "emisor",
            "cuerpo_resumen",
            "notas_al_pie",
            "firmante",
            "lista_distribucion",
        ]


def test_export_master_csv_error_handling(tmp_path: Path) -> None:
    """Verifica que el exportador maestro continúe si uno de los archivos es inválido o no existe."""
    orchestrator = DDUOrchestrator()
    pdf_list: List[Path] = [
        PROYECTO_RAIZ / "circulares" / "inresistente.pdf",
        PROYECTO_RAIZ / "circulares" / "DDU 533.pdf",
    ]
    master_path = tmp_path / "master" / "dataset_master_error_test.csv"

    res_path = orchestrator.export_master_csv(pdf_list, master_path)
    assert res_path.exists()
