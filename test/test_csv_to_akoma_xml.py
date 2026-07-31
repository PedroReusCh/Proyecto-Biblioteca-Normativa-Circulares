"""Pruebas unitarias para el transformador independiente CSV a Akoma Ntoso XML."""

from pathlib import Path

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
    assert '<doc name="circular"' in content
    assert 'Esquema%20Akoma-Ntoso%20BCN.xsd' in content
    assert 'FRBRdate date="2026-02-17"' in content or "2026-02-17" in content


def test_csv_to_akoma_xml_batch_dir(tmp_path: Path) -> None:
    """Verifica la transformación por lote de un directorio de CSVs."""
    csv_dir = Path("salidas_csv")
    assert csv_dir.exists()

    converter = CSVToAkomaXML()
    generated = converter.transform_dir(csv_dir, tmp_path)

    assert len(generated) >= 4
    for xml_file in generated:
        assert xml_file.exists()
        text = xml_file.read_text(encoding="utf-8")
        assert '<doc name="circular"' in text


def test_csv_to_akoma_xml_numeral_segmentation(tmp_path: Path) -> None:
    """Verifica que la transformación desde CSV extraiga numerales <num> e identificadores <paragraph>."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    out_xml = tmp_path / "DDU_531_num_test.xml"

    converter = CSVToAkomaXML()
    result_path = converter.transform(csv_input, out_xml)

    content = result_path.read_text(encoding="utf-8")
    assert "<num>1.</num>" in content or "<num>1</num>" in content
    assert '<paragraph id="' in content


