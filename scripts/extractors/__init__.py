"""Paquete de extractores modulares para circulares DDU."""

import importlib
import sys
from typing import List

from scripts.extractors.base import (
    BaseExtractor,
    ResultadoBloque,
    ExtractorRegistry,
    register_extractor,
)

_EXTRACTOR_MODULES: List[str] = [
    "encabezado",
    "acto_administrativo",
    "antecedentes",
    "materia",
    "descriptores",
    "fecha_lugar",
    "destinatarios",
    "emisor",
]


def registrar_todos_los_extractores() -> None:
    """Importa o recarga dinámicamente todos los módulos de extractores para asegurar su registro."""
    for mod_name in _EXTRACTOR_MODULES:
        full_name = f"scripts.extractors.{mod_name}"
        if full_name in sys.modules:
            importlib.reload(sys.modules[full_name])
        else:
            importlib.import_module(full_name)


__all__ = [
    "BaseExtractor",
    "ResultadoBloque",
    "ExtractorRegistry",
    "register_extractor",
    "registrar_todos_los_extractores",
]
