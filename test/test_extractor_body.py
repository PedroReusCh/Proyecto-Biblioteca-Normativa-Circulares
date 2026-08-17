"""Pruebas unitarias para los extractores independientes de cuerpo, firma y distribución (ETLs 9 a 11)."""

import importlib
from pathlib import Path
import re
from typing import Any, List
import pytest

from scripts.ddu_types import SeccionDDU
from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import ExtractorRegistry, ResultadoBloque
from scripts.extractors.cuerpo import CuerpoExtractor
from scripts.extractors.firma import FirmaExtractor
from scripts.extractors.distribucion import DistribucionExtractor


SAMPLE_TEXT_DDU_533_BODY = """A SEGÚN DISTRIBUCIÓN.
DDU 533
CIRCULAR ORD. N° 112
ANT .: 1) Decreto Supremo N°33 (V. y U.) de 2024.
MAT.: Prórroga extraordinaria por dieciocho (18) meses adicionales de permisos de construcción.
PERMISOS, VIGENCIA, RECEPCIONES.
SANTIAGO, 27 FEB 2026
DE JEFE DIVISIÓN DE DESARROLLO URBANO.

1. De conformidad con lo previsto en el artículo 4° de la Ley General de Urbanismo y Construcciones (LGUC), corresponde a esta División interpretar las disposiciones de la dicha Ley y su Ordenanza General mediante circulares.

2. MARCO NORMATIVO: DS 33.
El DS 33, publicado en el Diario Oficial el 30.09.2024, agregó a la Ordenanza General de Urbanismo y Construcciones (OGUC) un artículo transitorio.

3. ÁMBITO DE APLICACIÓN DE LA PRÓRROGA (REQUISITOS COPULATIVOS).
La prórroga extraordinaria de dieciocho (18) meses adicionales resulta aplicable únicamente a aquellos permisos de construcción que cumplan copulativamente las siguientes condiciones:
a) Que se encuentren vigentes a la fecha de entrada en vigencia del DS 33; y,
b) Que, a dicha fecha, no hayan iniciado las obras correspondientes.

Saluda atentamente a Ud.,

VICENTE BURGOS SALAS
JEFE DIVISIÓN DE DESARROLLO URBANO

DISTRIBUCIÓN:
1. Sr. Ministro de Vivienda y Urbanismo
2. Sra. Subsecretaria de Vivienda y Urbanismo
3. Sra. Contralora General de la República
4. Biblioteca del Congreso Nacional.
"""

SAMPLE_LINES_DDU_533_BODY: List[str] = [
    line.strip() for line in SAMPLE_TEXT_DDU_533_BODY.splitlines() if line.strip()
]


def test_registry_contains_body_extractors() -> None:
    """Verifica que los 3 extractores de cuerpo, firma y distribución estén en ExtractorRegistry."""
    registrar_todos_los_extractores()
    all_extractors = ExtractorRegistry.get_all_extractors()
    bloques_esperados = ["cuerpo", "firma", "distribucion"]
    for bloque in bloques_esperados:
        assert bloque in all_extractors, f"Bloque {bloque} no encontrado en ExtractorRegistry"


def test_cuerpo_extractor() -> None:
    """Prueba la extracción del cuerpo estructurado (secciones y párrafos)."""
    extractor = CuerpoExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533_BODY, SAMPLE_LINES_DDU_533_BODY)
    assert resultado.nombre_bloque == "cuerpo"
    assert resultado.exito is True
    assert "secciones" in resultado.datos
    secciones: List[SeccionDDU] = list(resultado.datos["secciones"])
    assert len(secciones) > 0

    # Verificar que los párrafos contengan los numerales principales de la DDU 533
    parrafos_list: List[str] = []
    for sec in secciones:
        parrafos_list.extend(sec["parrafos"])
    parrafos_concatenados = " ".join(parrafos_list)
    assert "1. De conformidad con lo previsto" in parrafos_concatenados
    assert "2. MARCO NORMATIVO: DS 33." in parrafos_concatenados
    assert "3. ÁMBITO DE APLICACIÓN DE LA PRÓRROGA" in parrafos_concatenados


def test_firma_extractor() -> None:
    """Prueba la extracción de la firma y firmante (Vicente Burgos Salas)."""
    extractor = FirmaExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533_BODY, SAMPLE_LINES_DDU_533_BODY)
    assert resultado.nombre_bloque == "firma"
    assert resultado.exito is True
    firmante = str(resultado.datos["firmante"])
    assert "VICENTE BURGOS SALAS" in firmante
    assert "JEFE DIVISIÓN DE DESARROLLO URBANO" in firmante


def test_distribucion_extractor() -> None:
    """Prueba la extracción de la lista de distribución."""
    extractor = DistribucionExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533_BODY, SAMPLE_LINES_DDU_533_BODY)
    assert resultado.nombre_bloque == "distribucion"
    assert resultado.exito is True
    distribucion: List[Any] = list(resultado.datos["lista_distribucion"])
    assert isinstance(distribucion, list)
    assert len(distribucion) == 4
    assert "1. Sr. Ministro de Vivienda y Urbanismo" in str(distribucion[0])
    assert "4. Biblioteca del Congreso Nacional." in str(distribucion[3])


# --- Texto de prueba con orden invertido (DE: antes de A:) ---
SAMPLE_TEXT_INVERTIDO_BODY: str = """DDU 120
CIRCULAR ORD. N° 045
ANT.: Ley N° 19.175
MAT.: Interpretación sobre permisos de edificación.
PERMISOS, EDIFICACIÓN.
SANTIAGO, 15 MAR 2005
DE: JEFE DIVISIÓN DE DESARROLLO URBANO
A: SEÑORES INTENDENTES Y GOBERNADORES

1. De conformidad con lo previsto en el artículo 4° de la LGUC, se instruye lo siguiente.

2. MARCO NORMATIVO: Ley 19.175.
Se establece el alcance de la normativa vigente.

Saluda atentamente a Ud.,

PEDRO LÓPEZ MUÑOZ
JEFE DIVISIÓN DE DESARROLLO URBANO

DISTRIBUCIÓN:
1. Sr. Ministro de Vivienda y Urbanismo
"""

SAMPLE_LINES_INVERTIDO_BODY: List[str] = [
    line.strip() for line in SAMPLE_TEXT_INVERTIDO_BODY.splitlines() if line.strip()
]


def test_cuerpo_orden_invertido() -> None:
    """Prueba que el cuerpo se extraiga correctamente cuando DE: aparece antes de A:."""
    extractor = CuerpoExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_INVERTIDO_BODY, SAMPLE_LINES_INVERTIDO_BODY)
    assert resultado.nombre_bloque == "cuerpo"
    assert resultado.exito is True

    secciones: List[SeccionDDU] = list(resultado.datos["secciones"])
    assert len(secciones) > 0

    parrafos_list: List[str] = []
    for sec in secciones:
        parrafos_list.extend(sec["parrafos"])
    parrafos_concatenados = " ".join(parrafos_list)

    # El cuerpo debe contener los numerales, no metadatos del encabezado
    assert "1. De conformidad con lo previsto" in parrafos_concatenados
    assert "2. MARCO NORMATIVO: Ley 19.175." in parrafos_concatenados

    # El cuerpo NO debe contener metadatos del encabezado
    assert "CIRCULAR ORD" not in parrafos_concatenados
    assert "SEÑORES INTENDENTES" not in parrafos_concatenados
    assert "JEFE DIVISIÓN" not in parrafos_concatenados or "Saluda" not in parrafos_concatenados


def test_cuerpo_extractor_llamadas_nota_al_pie() -> None:
    """Verifica la normalización de llamadas a notas al pie al formato [N]."""
    lines = [
        "1. De conformidad con lo dispuesto...",
        "DDU ESPECÍFICA Nº97 /2007 1.",
        "a) Que la pérgola consista en un elemento -es decir que no tenga el carácter de construcción 2- y que además sea exterior.",
        "3. Conforme al artículo 381 del referido DS 86.",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    secciones: List[Any] = list(resultado.datos.get("secciones", []))
    texto_completo = " ".join([p for s in secciones for p in s.get("parrafos", [])])

    assert "Nº97 /2007 [1]" in texto_completo
    assert "carácter de construcción [2]" in texto_completo
    assert "artículo 38 [1]" in texto_completo


def test_cuerpo_extractor_exclusion_notas_al_pie() -> None:
    """Verifica que el extractor de cuerpo excluya las notas explicativas al pie de página."""
    lines = [
        "1. De conformidad a lo dispuesto en el artículo 4°...",
        "7. Por lo tanto, las pérgolas que cumplan...",
        "1 En dicha circular se indica que el citado artículo 5.1.2...",
        "2 En el artículo 1.1.2. de la OGUC se define...",
        "8. Con todo, debe advertirse que la circunstancia...",
        "Saluda atentamente a Ud.,",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    secciones: List[Any] = list(resultado.datos.get("secciones", []))
    texto_completo = " ".join([p for s in secciones for p in s.get("parrafos", [])])

    assert "7. Por lo tanto, las pérgolas que cumplan..." in texto_completo
    assert "8. Con todo, debe advertirse que la circunstancia..." in texto_completo
    assert "1 En dicha circular se indica" not in texto_completo
    assert "2 En el artículo 1.1.2. de la OGUC" not in texto_completo


def test_distribucion_extractor_ddu_546_ocr() -> None:
    """Verifica la extracción limpia de la lista de distribución en DDU 546 con OCR distorsionado y sin banners de pie de página."""
    lines = [
        "Saluda atentamente a Ud.,",
        "N DIEGO ZQUIERDO HEVIA",
        "D VISIÓN DE DESARROLLO URBANO",
        "tl ' .",
        "RA/4l ¡ ~ /O M",
        "RIBuc)óN:",
        "Sr. Ministro de Vivienda y Urbanismo",
        ",2. Sra. Subsecretaria de Vivienda y Urbanismo",
        "3. Sra. Contralora General de la República",
        "=::::= ========= GOBIERNO DE CHILE ====== ==-== = :-=",
    ]

    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    distribucion: List[str] = list(resultado.datos.get("lista_distribucion", []))
    assert len(distribucion) == 3
    assert distribucion[0] == "1. Sr. Ministro de Vivienda y Urbanismo"
    assert distribucion[1] == "2. Sra. Subsecretaria de Vivienda y Urbanismo"
    assert distribucion[2] == "3. Sra. Contralora General de la República"
    assert not any("GOBIERNO DE CHILE" in d for d in distribucion)


def test_firma_extractor_ddu_546_ocr() -> None:
    """Verifica la extracción limpia y normalizada del firmante en DDU 546."""
    lines = [
        "Saluda atentamente a Ud.,",
        "N DIEGO ZQUIERDO HEVIA",
        "D VISIÓN DE DESARROLLO URBANO",
        "IS RIO DE VIVIENDA Y URBANISMO",
        "tl ' .",
        "RA/4l ¡ ~ /O M",
        "RIBuc)óN:",
        "Sr. Ministro de Vivienda y Urbanismo",
    ]

    extractor = FirmaExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    firmante = resultado.datos.get("firmante", "")
    assert firmante == "JUAN DIEGO IZQUIERDO HEVIA, DIVISIÓN DE DESARROLLO URBANO, MINISTERIO DE VIVIENDA Y URBANISMO"
    assert resultado.datos.get("nombre_firmante") == "JUAN DIEGO IZQUIERDO HEVIA"
    assert "DIVISIÓN DE DESARROLLO URBANO" in str(resultado.datos.get("cargo_firmante", ""))
    assert "Sr. Ministro" not in firmante


def test_firma_extractor_nombre_y_cargo_separados() -> None:
    """Verifica que el extractor de firma separe correctamente nombre y cargo en distintas líneas."""
    lines = [
        "Saluda atentamente a Ud.,",
        "VICENTE BURGOS BOLAÑOS",
        "Jefe División de Desarrollo Urbano",
    ]
    extractor = FirmaExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    assert resultado.datos.get("nombre_firmante") == "VICENTE BURGOS BOLAÑOS"
    assert resultado.datos.get("cargo_firmante") == "Jefe División de Desarrollo Urbano"
    assert resultado.datos.get("firmante") == "VICENTE BURGOS BOLAÑOS, Jefe División de Desarrollo Urbano"



def test_distribucion_extractor_limpieza_palabras_divididas() -> None:
    """Verifica la desinfección universal de palabras divididas por OCR en la distribución."""
    lines = [
        "DISTRIBUCIÓN:",
        "7. Contra loría I nterna MINVU.",
        "13. Depto. de Ordenamiento Territor ial y Medio Ambiente (GORE Metropolitano)",
        "16. Sr. Jefe de la Oficina de Autorizac iones Sectoriales e Inversión",
        "26. Consejo Nacional de Desarrollo Territo rial.",
    ]

    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    distribucion: List[str] = list(resultado.datos.get("lista_distribucion", []))
    assert len(distribucion) == 4
    assert distribucion[0] == "7. Contraloría Interna MINVU."
    assert distribucion[1] == "13. Depto. de Ordenamiento Territorial y Medio Ambiente (GORE Metropolitano)"
    assert distribucion[2] == "16. Sr. Jefe de la Oficina de Autorizaciones Sectoriales e Inversión"
    assert distribucion[3] == "26. Consejo Nacional de Desarrollo Territorial."


def test_cuerpo_extractor_ddu_537_exclusion_notas_al_pie() -> None:
    """Verifica la inclusión completa del Numeral 4 y exclusión de notas al pie en DDU 537."""
    lines = [
        "DE: JEFE DIVISIÓN DE DESARROLLO URBANO",
        "3. En atención a las normas antes citadas, es posible afirmar que...",
        "1 Artículo 38. Lineamientos y estándares de los mapas de amenaza y riesgo...",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 2 de 4",
        "4 . Si bien la utilización de estos mapas de amenazas resulta obligatoria para la elaboración de los IPT...",
        "5. Sin embargo, en caso de no existir los mapas de amenazas...",
        "2 La orientación técnica específica para estas materias está contenida en el punto 2.3...",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 3 de 4",
        "a lo establecido en el artículo 29 del Decreto N° 32 de 2015...",
        "8. Por su parte, respecto del artículo 36 de la Ley N° 21.364...",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    cuerpo = str(resultado.datos.get("cuerpo", ""))
    assert "4. Si bien la utilizac" in cuerpo
    assert "1 Art" not in cuerpo
    assert "2 La orientac" not in cuerpo


def test_cuerpo_extractor_llamada_nota_imagenes_ocr() -> None:
    """Verifica que 'imá genes 2' se convierta correctamente a 'imágenes [2]'."""
    lines = [
        "DE: JEFE DIVISIÓN DE DESARROLLO URBANO",
        "4. Es decir, deberán ser sometidos a un procesamiento de las imá genes 2 para la conversión...",
    ]

    extractor = CuerpoExtractor()
    resultado = extractor.extract("\n".join(lines), lines)

    assert resultado.exito is True
    cuerpo = str(resultado.datos.get("cuerpo", ""))
    assert "imágenes [2]" in cuerpo


def test_firma_extractor_ddu_456_tabla_motivo() -> None:
    """Prueba que FirmaExtractor descarte cabeceras de tabla como 'Motivo y/o Consideraciones' y extraiga el cargo real."""
    lines = [
        "7. Para adecuarse a los cambios normativos...",
        "Saluda atentamente a Ud.,",
        "-",
        "~",
        "L",
        "Motivo y/o",
        "Consideraciones",
        "-:.. f' .:s \"-Z, - ~",
        "/ JPB  O~,  1_1-0",
        "Jefe División de Desarrollo Urbano",
        "871/(165-2)",
        "DISTRIBUCIÓN:",
        "1. Sr. Ministro de Vivienda y Urbanismo.",
    ]
    extractor = FirmaExtractor()
    resultado = extractor.extract("\n".join(lines), lines)
    assert resultado.exito is True
    firmante = str(resultado.datos.get("firmante", ""))
    assert "Consideraciones" not in firmante
    assert "Motivo" not in firmante
    assert "JEFE DIVISIÓN DE DESARROLLO URBANO" in firmante.upper()


def test_distribucion_extractor_ddu_456() -> None:
    """Prueba que DistribucionExtractor capture la nómina completa de distribución de DDU 456."""
    lines = [
        "DISTRIBUCIÓN:",
        "1. Sr. Ministro de Vivienda y Urbanismo.",
        "2. Sr. Subsecretario de Vivienda y Urbanismo.",
        "3. Sr. Contralor General de la República.",
        "4. Biblioteca del Congreso Nacional.",
        "Ministerio de Vivienda y Urbanismo - Alameda 924 - Santiago - Chile Página 8 de 9",
        "30. OIRS.",
        "31. Jefe SIAC.",
        "32. Archivo DDU.",
        "33. Oficina de Partes D.D.U.",
        "34. Oficina de Partes MINVU Ley 20.285",
    ]
    extractor = DistribucionExtractor()
    resultado = extractor.extract("\n".join(lines), lines)
    assert resultado.exito is True
    dist_list = list(resultado.datos.get("lista_distribucion", []))
    assert len(dist_list) >= 9
    assert any("Oficina de Partes MINVU Ley 20.285" in d for d in dist_list)


def test_cuerpo_extractor_ddu_456_sin_ruido_imagenes() -> None:
    """Verifica que el cuerpo extraído de DDU 456 no contenga ruido de diagramas ni palabras rotas por OCR."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if pdf_path.exists():
        pypdf_mod: Any = importlib.import_module("pypdf")
        pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
        pdf_pages: Any = pdf_reader.pages
        text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
        raw_text: str = "\n".join(text_list)
        lines: List[str] = [line.strip() for line in raw_text.splitlines()]
    else:
        raw_text = (
            "DDU 456\n"
            "CIRCULAR ORD. N° 0456\n"
            "1. Se han recibido diversas consultas respecto a la aplicación a rtículo 2.6.3. de la OGUC.\n"
            "2. En este sentido, los quinch os deben considerarse como relativo s a elementos exteriores.\n"
            "3. Asimismo, el inciso s segundo establece las condiciones.\n"
            "4. A continuación, se presenta un esquema ilustrativo que sintetiza algunos de los aspectos abordados en la presente Circular:\n"
            "PLANTA AZOTEA\n"
            "CORTE ESQUEMÁTICO\n"
            "Piscina\n"
            "Salida caja de escalera\n"
            "Chimeneas\n"
            "Pérgola\n"
            "Ascensores\n"
            "½\n"
            "5. En el inciso vigésimo tercero se señalan los requerimientos.\n"
            "Saluda atentamente a Ud.,\n"
            "JEFE DIVISIÓN DE DESARROLLO URBANO"
        )
        lines = [line.strip() for line in raw_text.splitlines()]

    extractor = CuerpoExtractor()
    resultado = extractor.extract(raw_text, lines)

    assert resultado.exito is True
    secciones: List[SeccionDDU] = list(resultado.datos.get("secciones", []))
    assert len(secciones) > 0

    parrafos_cuerpo: List[str] = [p for s in secciones for p in s.get("parrafos", [])]
    cuerpo_total = " ".join(parrafos_cuerpo)

    # 1. Numeral 4 debe contener solo la frase narrativa introductoria
    parrafos_num4 = [p for p in parrafos_cuerpo if p.startswith("4. A continuación")]
    assert len(parrafos_num4) == 1
    num4_texto = parrafos_num4[0]
    assert "A continuación, se presenta un esquema ilustrativo que sintetiza algunos de los aspectos abordados en la presente Circular:" in num4_texto

    # 2. Numeral 4 NO debe contener etiquetas o fragmentos sueltos de los diagramas/planos
    ruidos_prohibidos = [
        "PLANTA AZOTEA",
        "CORTE ESQUEMÁTICO",
        "Piscina",
        "Salida caja de escalera",
        "Chimeneas",
        "Pérgola",
        "Ascensores",
        "½",
    ]
    for ruido in ruidos_prohibidos:
        assert ruido not in num4_texto, f"Ruido de diagrama '{ruido}' encontrado en Numeral 4"

    # 3. Verificar saneamiento OCR en el cuerpo
    assert "quinch os" not in cuerpo_total
    assert "quinchos" in cuerpo_total
    assert not re.search(r"\ba\s+rt[íi]culo\b", cuerpo_total, re.IGNORECASE)
    assert not re.search(r"\binciso\s+s\b", cuerpo_total, re.IGNORECASE)
    assert not re.search(r"\brelativo\s+s\b", cuerpo_total, re.IGNORECASE)
    assert "relativos" in cuerpo_total


def test_firma_extractor_ddu_456_cargo_limpio() -> None:
    """Verifica que FirmaExtractor en DDU 456 extraiga mediante OCR el nombre de Enrique Matuschka y su cargo."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if pdf_path.exists():
        pypdf_mod: Any = importlib.import_module("pypdf")
        pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
        pdf_pages: Any = pdf_reader.pages
        text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
        raw_text: str = "\n".join(text_list)
        lines: List[str] = [line.strip() for line in raw_text.splitlines()]
        extractor = FirmaExtractor()
        resultado = extractor.extract(raw_text, lines, pdf_path=pdf_path)

        assert resultado.exito is True
        assert "ENRIQUE MATUSCHKA" in str(resultado.datos.get("nombre_firmante"))
        assert resultado.datos.get("cargo_firmante") == "Jefe División de Desarrollo Urbano"
        assert "ENRIQUE MATUSCHKA" in str(resultado.datos.get("firmante"))
        assert "Jefe División de Desarrollo Urbano" in str(resultado.datos.get("firmante"))
    else:
        raw_text = (
            "Saluda atentamente a Ud.,\n"
            "ENRIQUE MATUSCHKA AYÇAGUER\n"
            "Jefe DIVISIÓN de Desarrollo Urbano"
        )
        lines = [line.strip() for line in raw_text.splitlines()]
        extractor = FirmaExtractor()
        resultado = extractor.extract(raw_text, lines)

        assert resultado.exito is True
        assert resultado.datos.get("nombre_firmante") == "ENRIQUE MATUSCHKA AYÇAGUER"
        assert resultado.datos.get("cargo_firmante") == "Jefe División de Desarrollo Urbano"





def test_cuerpo_extractor_ddu_456_exclusion_tablas_e_imagenes() -> None:
    """Verifica que el cuerpo de DDU 456 contenga exactamente 7 párrafos y excluya tablas e imágenes."""
    pdf_path = Path("circulares/DDU 456.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")


    pypdf_mod: Any = importlib.import_module("pypdf")
    reader = pypdf_mod.PdfReader(pdf_path)
    raw_text = "\n".join([str(p.extract_text() or "") for p in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    extractor = CuerpoExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text, lines)

    assert resultado.exito is True
    secciones: List[SeccionDDU] = list(resultado.datos.get("secciones", []))
    assert len(secciones) == 1
    parrafos: List[str] = secciones[0].get("parrafos", [])

    # Exactamente 7 párrafos (Numerales 1 al 7)
    assert len(parrafos) == 7, f"Se esperaban 7 párrafos normativos, se obtuvieron {len(parrafos)}"

    # Verificar numeral 2 limpio (sin nota marginal de modificación posterior DDU 498 y con texto completo)
    assert parrafos[1].startswith("2.")
    assert "Circular Modificada por" not in parrafos[1]
    assert "DDU 498" not in parrafos[1]
    assert "desde el nivel de la azotea." in parrafos[1]
    assert "ocupada por los elementos" in parrafos[1]


    # Verificar numeral 4 limpio
    assert parrafos[3].startswith("4.")
    assert "A continuación, se presenta un esquema ilustrativo" in parrafos[3]
    assert "PLANTA AZOTEA" not in parrafos[3]
    assert "CORTE ESQUEMÁTICO" not in parrafos[3]

    # Verificar numeral 7 limpio (sin contenido de la tabla de circulares)
    assert parrafos[6].startswith("7.")
    assert "Circular Materia(s) que se modifica(n)" not in parrafos[6]
    assert "DDU 339" not in parrafos[6]
    assert "DDU 322" not in parrafos[6]
    assert "DDU 168" not in parrafos[6]


def test_cuerpo_extractor_ddu_547_exclusion_tablas() -> None:
    """Verifica que el cuerpo de DDU 547 contenga todas sus secciones normativas y excluya las 3 tablas."""
    pdf_path = Path("circulares/DDU 547.pdf")
    if not pdf_path.exists():
        pytest.skip(f"No se encontró el archivo PDF en {pdf_path}")

    pypdf_mod: Any = importlib.import_module("pypdf")
    reader = pypdf_mod.PdfReader(pdf_path)
    raw_text = "\n".join([str(p.extract_text() or "") for p in reader.pages])
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]

    extractor = CuerpoExtractor()
    resultado: ResultadoBloque = extractor.extract(raw_text, lines, pdf_path=pdf_path)

    assert resultado.exito is True
    cuerpo = str(resultado.datos.get("cuerpo", ""))

    # Verificar presencia de secciones y numerales del cuerpo
    assert "1. De conformidad" in cuerpo
    assert "2. MARCO NORMATIVO:" in cuerpo
    assert "3. ¿QUÉ ES LA URBANIZACIÓN?" in cuerpo
    assert "4. HIPÓTESIS Y TIPOS DE GESTIÓN" in cuerpo
    assert "5. OBRAS DE URBANIZACIÓN" in cuerpo
    assert "6. OBRAS DE URBANIZACIÓN" in cuerpo
    assert "7. OBRAS DE URBANIZACIÓN" in cuerpo
    assert "8. PERMISOS DE URBANIZACIÓN" in cuerpo
    assert "9. EXIGENCIA DE ACCEDER" in cuerpo
    assert "10. RECEPCIÓN DEFINITIVA" in cuerpo
    assert "OTRAS MODIFICACIONES" in cuerpo
    assert "12. CIRCULARES QUE SE DEJAN SIN EFECTO O SE MODIFICAN:" in cuerpo
    assert "12.1. Considerando las modificaciones" in cuerpo
    assert "12.2. En atención a los cambios normativos" in cuerpo


    # Verificar exclusión total de encabezados y celdas de las 3 tablas
    assert "TIPO DE GESTIÓN" not in cuerpo
    assert "CASOS QUE COMPRENDE" not in cuerpo
    assert "1. Loteos (Art. 2.2.4." not in cuerpo
    assert "DDU Nº Nº ORD" not in cuerpo
    assert "MATERIA DE LA CIRCULAR" not in cuerpo
    assert "Específica 78-07" not in cuerpo
    assert "Específica 22-07" not in cuerpo
    assert "435 228 20-05-20" not in cuerpo






