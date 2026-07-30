"""Pruebas unitarias para los extractores independientes de cuerpo, firma y distribución (ETLs 9 a 11)."""

from typing import Any, List

from scripts.ddu_types import SeccionDDU
from scripts.extractors import registrar_todos_los_extractores
from scripts.extractors.base import ExtractorRegistry
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
