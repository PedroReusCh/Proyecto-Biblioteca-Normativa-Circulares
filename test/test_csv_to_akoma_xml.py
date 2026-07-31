"""Pruebas unitarias para el transformador independiente CSV a Akoma Ntoso XML."""

from pathlib import Path
import pytest
from scripts.csv_to_akoma_xml import CSVToAkomaXML


def test_csv_to_akoma_xml_transformation(tmp_path: Path) -> None:
    """Verifica la transformación de un archivo CSV a XML Akoma Ntoso BCN."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    assert csv_input.exists(), "El CSV de prueba DDU_531_extraido.csv debe existir"

    out_xml = tmp_path / "DDU_531_akoma.xml"
    converter = CSVToAkomaXML()
    result_path = converter.transform(csv_input, out_xml)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "<akomaNtoso" in content
    assert '<doc name="circular">' in content
    assert 'FRBRnumber value="531"' in content
    assert "2026-02-17" in content
