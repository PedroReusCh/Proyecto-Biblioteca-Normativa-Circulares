"""Pruebas unitarias para los extractores independientes de cuerpo, firma y distribución (ETLs 9 a 11)."""

import pytest
from typing import List

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
    secciones = resultado.datos["secciones"]
    assert len(secciones) > 0

    # Verificar que los párrafos contengan los numerales principales de la DDU 533
    parrafos_concatenados = " ".join(
        [p for s in secciones for p in s.get("parrafos", [])]
    )
    assert "1. De conformidad con lo previsto" in parrafos_concatenados
    assert "2. MARCO NORMATIVO: DS 33." in parrafos_concatenados
    assert "3. ÁMBITO DE APLICACIÓN DE LA PRÓRROGA" in parrafos_concatenados


def test_firma_extractor() -> None:
    """Prueba la extracción de la firma y firmante (Vicente Burgos Salas)."""
    extractor = FirmaExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533_BODY, SAMPLE_LINES_DDU_533_BODY)
    assert resultado.nombre_bloque == "firma"
    assert resultado.exito is True
    firmante = resultado.datos["firmante"]
    assert "VICENTE BURGOS SALAS" in firmante
    assert "JEFE DIVISIÓN DE DESARROLLO URBANO" in firmante


def test_distribucion_extractor() -> None:
    """Prueba la extracción de la lista de distribución."""
    extractor = DistribucionExtractor()
    resultado = extractor.extract(SAMPLE_TEXT_DDU_533_BODY, SAMPLE_LINES_DDU_533_BODY)
    assert resultado.nombre_bloque == "distribucion"
    assert resultado.exito is True
    distribucion = resultado.datos["lista_distribucion"]
    assert isinstance(distribucion, list)
    assert len(distribucion) == 4
    assert "1. Sr. Ministro de Vivienda y Urbanismo" in distribucion[0]
    assert "4. Biblioteca del Congreso Nacional." in distribucion[3]
