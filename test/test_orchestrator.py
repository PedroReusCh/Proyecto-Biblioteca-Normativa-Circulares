import csv
from pathlib import Path
from typing import Any, Dict, List
import pytest

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


def test_orchestrator_process_pdf_ddu_456() -> None:
    """Verifica el procesamiento completo de DDU 456 con los 14 bloques normativos, tablas e imágenes."""
    if not PDF_DDU_456.exists():
        pytest.skip(f"No se encontró {PDF_DDU_456}")

    orchestrator = DDUOrchestrator()
    datos: DatosCircularDDU = orchestrator.process_pdf(PDF_DDU_456)

    # 1. Metadatos principales saneados
    assert "456" in datos["numero"]
    assert datos["fecha"] == "2021-02-25"
    assert "artículo 2.6.3" in datos["materia"]
    assert "JEFE" in datos["emisor"] and "DESARROLLO URBANO" in datos["emisor"]
    assert datos.get("numero_ord") == "CIRCULAR ORD. N° 88"
    assert "NORMAS URBANISTICAS" in str(datos.get("descriptores", ""))
    assert "SEGÚN DISTRIBUCIÓN" in str(datos.get("destinatarios", ""))
    assert str(datos.get("lugar", "")) == "Santiago"

    # 2. Cuerpo descontaminado y estructurado
    cuerpo = str(datos.get("cuerpo", ""))
    assert "1. Conforme a las facultades" in cuerpo
    assert "PLANTA AZOTEA" not in cuerpo
    assert "Piscina Chimeneas Terraza" not in cuerpo

    # 3. Tablas estructuradas con manifiesto ligero (pdfplumber)
    tablas: List[Dict[str, Any]] = datos.get("tablas") or []
    assert isinstance(tablas, list)
    assert len(tablas) == 4
    ids_tablas = [t["id"] for t in tablas]
    assert ids_tablas == ["DDU_456_tabla_1", "DDU_456_tabla_2", "DDU_456_tabla_3", "DDU_456_tabla_4"]
    paginas_tablas = [t["pagina"] for t in tablas]
    assert paginas_tablas == [5, 6, 7, 8]
    assert all("archivo_anexo" in t for t in tablas)
    assert any("339" in t["nombre"] or "322" in t["nombre"] for t in tablas)

    # 4. Imágenes técnicas con manifiesto ligero (PyMuPDF fitz)
    imagenes: List[Dict[str, Any]] = datos.get("imagenes") or []
    assert isinstance(imagenes, list)
    assert len(imagenes) >= 1
    img_p3 = next((img for img in imagenes if img.get("pagina") == 3), None)
    assert img_p3 is not None
    assert img_p3["id"] == "DDU_456_img_1"
    assert img_p3["ancho"] == 700
    assert img_p3["alto"] == 760
    assert img_p3["formato"] == "png"
    assert img_p3["xref"] == 5
    assert img_p3["tipo"] == "Esquema técnico"
    assert img_p3["archivo_anexo"] == "salidas_imagenes/DDU_456_img_1.png"
    assert any(k in str(img_p3.get("nombre", "")).lower() for k in ["esquema", "planta azotea", "corte"])

    # 5. Firma y distribución
    assert "DIVISIÓN" in str(datos.get("firmante", ""))
    dist_lista = datos.get("lista_distribucion") or []
    assert len(dist_lista) >= 30


def test_export_individual_csv_ddu_456(tmp_path: Path) -> None:
    """Verifica que el CSV individual de DDU 456 contenga los 14 bloques normativos estructurados."""
    if not PDF_DDU_456.exists():
        pytest.skip(f"No se encontró {PDF_DDU_456}")

    orchestrator = DDUOrchestrator()
    output_dir = tmp_path / "csv_output_456"
    csv_path = orchestrator.export_individual_csv(PDF_DDU_456, output_dir)

    assert csv_path.exists()
    assert csv_path.name == "DDU_456_extraido.csv"

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)
        assert header == ["bloque", "campo", "valor_extraido"]

        rows = list(reader)
        assert len(rows) == 14, f"Se esperaban 14 bloques, se encontraron {len(rows)}"

        bloques = [row[0] for row in rows]
        bloques_esperados = [
            "Encabezado",
            "Acto Administrativo",
            "Antecedentes",
            "Materia",
            "Descriptores",
            "Fecha y Lugar",
            "Destinatarios",
            "Emisión",
            "Cuerpo",
            "Tablas",
            "Imágenes",
            "Nota al Pie",
            "Firma",
            "Distribución",
        ]
        assert bloques == bloques_esperados

        # Verificar contenido de Tablas e Imágenes no vacío en DDU 456 (manifiesto con IDs)
        tablas_row = next(r for r in rows if r[0] == "Tablas")
        assert tablas_row[2] != ""
        assert "DDU_456_tabla_1" in tablas_row[2]
        assert "salidas_tablas/DDU_456_tabla_1.csv" in tablas_row[2]

        imagenes_row = next(r for r in rows if r[0] == "Imágenes")
        assert imagenes_row[2] != ""
        assert "DDU_456_img_1" in imagenes_row[2]
        assert "salidas_imagenes/DDU_456_img_1.png" in imagenes_row[2]
