"""Pruebas unitarias para el transformador independiente CSV a RDF Turtle."""

from pathlib import Path

from scripts.csv_to_rdf import CSVToRDF


def test_csv_to_rdf_transformation(tmp_path: Path) -> None:
    """Verifica la transformación de un archivo CSV a un grafo semántico RDF/Turtle."""
    csv_input = Path("salidas_csv/DDU_531_extraido.csv")
    assert csv_input.exists(), "El CSV de prueba DDU_531_extraido.csv debe existir"

    out_ttl = tmp_path / "DDU_531_rdf.ttl"
    converter = CSVToRDF()
    result_path = converter.transform(csv_input, out_ttl)

    assert result_path.exists()
    content = result_path.read_text(encoding="utf-8")
    assert "@prefix bcn-norms:" in content
    assert "@prefix minvu-ddu:" in content
    assert 'bcn-norms:hasNumber "DDU 531"' in content or 'bcn-norms:hasNumber "531"' in content


def test_csv_to_rdf_batch_dir(tmp_path: Path) -> None:
    """Verifica la transformación por lote a grafos RDF de un directorio de CSVs."""
    csv_dir = Path("salidas_csv")
    assert csv_dir.exists()

    converter = CSVToRDF()
    generated = converter.transform_dir(csv_dir, tmp_path)

    assert len(generated) >= 4
    for ttl_file in generated:
        assert ttl_file.exists()
        text = ttl_file.read_text(encoding="utf-8")
        assert "@prefix bcn-norms:" in text
