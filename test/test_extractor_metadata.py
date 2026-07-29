"""Pruebas unitarias para los 8 extractores independientes de metadatos (ETLs 1 a 8)."""

from typing import List

from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import ExtractorRegistry
from scripts.extractors.encabezado import EncabezadoExtractor
from scripts.extractors.acto_administrativo import ActoAdministrativoExtractor
from scripts.extractors.antecedentes import AntecedentesExtractor
from scripts.extractors.materia import MateriaExtractor
from scripts.extractors.descriptores import DescriptoresExtractor
from scripts.extractors.fecha_lugar import FechaLugarExtractor
from scripts.extractors.destinatarios import DestinatariosExtractor
from scripts.extractors.emisor import EmisorExtractor

SAMPLE_TEXT_DDU_533 = """A SEGÚN DISTRIBUCIÓN.
DDU 533
CIRCULAR ORD. N° 112
ANT .: 1) Decreto Supremo N°33 (V. y
U.) de 2024, que agregó un
artículo transitorio a la OGUC,
en materia de caducidad de
permisos de construcción.
2) Artículo 1.4.17 . de la OGUC.
3) Artículo 120 de la LGUC.
MAT.: Prórroga extraordinaria por
dieciocho (18) meses adicionales
de permisos de construcción
vigentes y sin inicio de obras a la
fecha de entrada en vigencia del
D.S. N°33 (V. y U.) de 2024.
Instruye criterios para su cómputo
y aplicación uniforme .
PERMISOS, VIGENCIA, RECEPCIONES.
SANTIAGO, 27 FEB 2026
DE JEFE DIVISIÓ N DE DESARROLLO URBANO.
1. De conformidad con lo previsto en el artículo 4° de la Ley General de Urbanismo
y Construcciones (LGUC), corresponde a esta División interpretar las
disposiciones de la dicha Ley y su Ordenanza General mediante circulares.
"""

SAMPLE_LINES_DDU_533: List[str] = [line.strip() for line in SAMPLE_TEXT_DDU_533.splitlines() if line.strip()]


def test_registry_contains_metadata_extractors() -> None:
    """Verifica que todos los 8 extractores de metadatos se hayan registrado correctamente."""
    registrar_todos_los_extractores()
    all_extractors = ExtractorRegistry.get_all_extractors()
    bloques_esperados = [
        "encabezado",
        "acto_administrativo",
        "antecedentes",
        "materia",
        "descriptores",
        "fecha_lugar",
        "destinatarios",
        "emisor",
    ]
    for bloque in bloques_esperados:
        assert bloque in all_extractors, f"Bloque {bloque} no encontrado en ExtractorRegistry"


def test_encabezado_extractor() -> None:
    """Prueba la extracción del número DDU."""
    extractor = EncabezadoExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "encabezado"
    assert resultado.exito is True
    assert "533" in resultado.datos["numero"]
    assert "DDU" in resultado.datos["numero"]
    assert resultado.confianza == 1.0


def test_acto_administrativo_extractor() -> None:
    """Prueba la extracción del número ordinario del acto administrativo."""
    extractor = ActoAdministrativoExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "acto_administrativo"
    assert resultado.exito is True
    assert "112" in resultado.datos["numero_ord"]
    assert resultado.confianza == 1.0


def test_antecedentes_extractor() -> None:
    """Prueba la extracción de antecedentes (ANT:)."""
    extractor = AntecedentesExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "antecedentes"
    assert resultado.exito is True
    assert "Decreto Supremo N°33" in resultado.datos["antecedentes"]
    assert "Artículo 120" in resultado.datos["antecedentes"]
    assert resultado.confianza == 1.0


def test_materia_extractor() -> None:
    """Prueba la extracción de materia (MAT:)."""
    extractor = MateriaExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "materia"
    assert resultado.exito is True
    assert "Prórroga extraordinaria" in resultado.datos["materia"]
    assert "aplicación uniforme" in resultado.datos["materia"]
    assert resultado.confianza == 1.0


def test_descriptores_extractor() -> None:
    """Prueba la extracción de descriptores/vocablos de materia."""
    extractor = DescriptoresExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "descriptores"
    assert resultado.exito is True
    assert resultado.datos["descriptores"] == "PERMISOS, VIGENCIA, RECEPCIONES."
    assert resultado.confianza == 1.0


def test_fecha_lugar_extractor() -> None:
    """Prueba la extracción de fecha y lugar de emisión."""
    extractor = FechaLugarExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "fecha_lugar"
    assert resultado.exito is True
    assert resultado.datos["fecha"] == "2026-02-27"
    assert resultado.datos["lugar"] == "Santiago"
    assert resultado.datos["fecha_lugar"] == "Santiago, 2026-02-27"
    assert resultado.confianza == 1.0


def test_destinatarios_extractor() -> None:
    """Prueba la extracción de destinatarios (A:)."""
    extractor = DestinatariosExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "destinatarios"
    assert resultado.exito is True
    assert resultado.datos["destinatarios"] == "SEGÚN DISTRIBUCIÓN."
    assert resultado.confianza == 1.0


def test_emisor_extractor() -> None:
    """Prueba la extracción de emisor (DE:)."""
    extractor = EmisorExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533, SAMPLE_LINES_DDU_533)
    assert resultado.nombre_bloque == "emisor"
    assert resultado.exito is True
    assert resultado.datos["emisor"] == "JEFE DIVISIÓ N DE DESARROLLO URBANO"
    assert resultado.confianza == 1.0


# --- Texto de prueba con orden invertido (DE: antes de A:) ---
SAMPLE_TEXT_INVERTIDO: str = """DDU 120
CIRCULAR ORD. N° 045
ANT.: Ley N° 19.175
MAT.: Interpretación sobre permisos de edificación.
PERMISOS, EDIFICACIÓN.
SANTIAGO, 15 MAR 2005
DE: JEFE DIVISIÓN DE DESARROLLO URBANO
A: SEÑORES INTENDENTES Y GOBERNADORES
1. De conformidad con lo previsto en el artículo 4° de la LGUC...
"""

SAMPLE_LINES_INVERTIDO: List[str] = [
    line.strip() for line in SAMPLE_TEXT_INVERTIDO.splitlines() if line.strip()
]


def test_destinatarios_orden_invertido() -> None:
    """Prueba que la extracción de destinatarios funcione cuando DE: aparece antes de A:."""
    extractor = DestinatariosExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_INVERTIDO, SAMPLE_LINES_INVERTIDO)
    assert resultado.nombre_bloque == "destinatarios"
    assert resultado.exito is True
    assert "INTENDENTES" in resultado.datos["destinatarios"]
    assert resultado.confianza == 1.0


def test_emisor_orden_invertido() -> None:
    """Prueba que la extracción de emisor funcione cuando DE: aparece antes de A:."""
    extractor = EmisorExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_INVERTIDO, SAMPLE_LINES_INVERTIDO)
    assert resultado.nombre_bloque == "emisor"
    assert resultado.exito is True
    assert "DESARROLLO URBANO" in resultado.datos["emisor"]
    assert resultado.confianza == 1.0
