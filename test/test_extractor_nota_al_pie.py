"""Pruebas unitarias para el extractor del metadato Nota al Pie (NotaAlPieExtractor)."""

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


def test_nota_al_pie_extractor_ddu_546_multiline() -> None:
    """Verifica la extracción multilínea de notas al pie en la DDU 546."""
    lines = [
        "7. Por lo tanto, las pérgolas que cumplan...",
        "1 En dicha circular se indica que el citado artículo 5.1.2, que define los casos para los cuales no será necesario",
        "el permiso de edificación, en su N° 2 se refiere a elementos exteriores sobrepuestos complementarios a una",
        "edificación, como pueden ser terrazas, parrones, glorietas, u otros...",
        "2 En el artículo 1.1.2. de la OGUC se define \"Construcción\" como \"obras de edificación o de urbanización\".",
        "--========== GOBIERNO DE CHILE ====== ====~",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 2 de 3",
    ]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.nombre_bloque == "nota_al_pie"
    assert resultado.exito is True
    notas: str = str(resultado.datos.get("notas_al_pie", ""))
    assert "el permiso de edificación, en su N° 2" in notas
    assert "2 En el artículo 1.1.2." in notas


def test_nota_al_pie_extractor_limpieza_palabras_divididas() -> None:
    """Verifica la desinfección de palabras divididas por OCR en notas al pie."""
    lines = [
        "1 En dicha circular se indica pero no a recintos que tengan el carácte r de local habitable, como es el caso para los 'con tain ers'.",
        "3 En el artículo 1.1.2. de la OGUC se define Edificaciones con destinos complementarios al área verde como construcciones complementarias a la recreación, tales como sombreaderos, pérgolas, mirado res, juegos infantiles, servicios higié nicos, paño les para herramien tas... Por su parte, en el literal b) del artícu lo 1.6.3. de la OGUC...",
    ]

    extractor = NotaAlPieExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    notas = str(resultado.datos.get("notas_al_pie", ""))
    assert "carácter de local" in notas
    assert "containers" in notas
    assert "miradores" in notas
    assert "higiénicos" in notas
    assert "pañoles" in notas
    assert "herramientas" in notas
    assert "artículo 1.6.3." in notas
