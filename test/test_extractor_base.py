"""Pruebas unitarias para BaseExtractor, ResultadoBloque y ExtractorRegistry."""

from typing import List
from scripts.extractors.base import (
    BaseExtractor,
    ResultadoBloque,
    ExtractorRegistry,
    register_extractor,
)


def test_resultado_bloque_dataclass() -> None:
    """Verifica la creación e inicialización predeterminada de ResultadoBloque."""
    res = ResultadoBloque(
        nombre_bloque="materia",
        exito=True,
        datos={"materia": "Normas de edificación"},
    )
    assert res.nombre_bloque == "materia"
    assert res.exito is True
    assert res.datos == {"materia": "Normas de edificación"}
    assert res.confianza == 1.0
    assert res.observaciones == ""


def test_base_extractor_abstract() -> None:
    """Verifica que BaseExtractor no pueda ser instanciado directamente."""
    exception_raised = False
    try:
        _ = BaseExtractor()  # type: ignore[abstract]
    except TypeError:
        exception_raised = True
    assert exception_raised, "BaseExtractor no debe ser instanciable directamente"


def test_register_and_get_extractors() -> None:
    """Verifica el registro de extractores mediante decorador y su consulta."""
    ExtractorRegistry.clear()
    assert len(ExtractorRegistry.get_all_extractors()) == 0

    @register_extractor
    class DummyExtractor(BaseExtractor):
        @property
        def nombre_bloque(self) -> str:
            return "dummy"

        def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
            return ResultadoBloque(
                nombre_bloque=self.nombre_bloque,
                exito=True,
                datos={"test": "ok"},
                confianza=1.0,
            )

    extractors = ExtractorRegistry.get_all_extractors()
    assert "dummy" in extractors
    cls = extractors["dummy"]
    instancia = cls()
    res = instancia.extract("raw text", ["raw text"])

    assert res.nombre_bloque == "dummy"
    assert res.exito is True
    assert res.datos["test"] == "ok"
    assert res.confianza == 1.0


def test_extractor_registry_clear() -> None:
    """Verifica que el registro se limpie correctamente."""
    ExtractorRegistry.clear()

    @register_extractor
    class TempExtractor(BaseExtractor):
        @property
        def nombre_bloque(self) -> str:
            return "temp"

        def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
            return ResultadoBloque(
                nombre_bloque=self.nombre_bloque,
                exito=True,
                datos={},
            )

    assert len(ExtractorRegistry.get_all_extractors()) == 1
    ExtractorRegistry.clear()
    assert len(ExtractorRegistry.get_all_extractors()) == 0
