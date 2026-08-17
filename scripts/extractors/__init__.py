"""Paquete de extractores modulares para circulares DDU."""

import importlib
from pathlib import Path
import sys
from typing import List

_PROYECTO_RAIZ = Path(__file__).resolve().parents[2]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

from typing import TYPE_CHECKING, Any, List

if TYPE_CHECKING:
    from scripts.extractors.base import (
        BaseExtractor,
        ResultadoBloque,
        ExtractorRegistry,
        register_extractor,
    )
    from scripts.extractors.tablas import TablasExtractor
    from scripts.extractors.imagenes import ImagenesExtractor
    from scripts.extractors.modificaciones_posteriores import ModificacionesPosterioresExtractor
else:
    try:
        from scripts.extractors.base import (
            BaseExtractor,
            ResultadoBloque,
            ExtractorRegistry,
            register_extractor,
        )
    except ImportError:
        from extractors.base import (
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
    "cuerpo",
    "firma",
    "distribucion",
    "nota_al_pie",
    "tablas",
    "imagenes",
    "modificaciones_posteriores",
]


def registrar_todos_los_extractores() -> None:
    """Importa o recarga dinámicamente todos los módulos de extractores para asegurar su registro."""
    for mod_name in _EXTRACTOR_MODULES:
        full_name = f"scripts.extractors.{mod_name}"
        try:
            if full_name in sys.modules:
                importlib.reload(sys.modules[full_name])
            else:
                importlib.import_module(full_name)
        except ModuleNotFoundError:
            alt_name = f"extractors.{mod_name}"
            if alt_name in sys.modules:
                importlib.reload(sys.modules[alt_name])
            else:
                importlib.import_module(alt_name)


def __getattr__(name: str) -> Any:
    """Resuelve exportaciones de extractores bajo demanda para evitar RuntimeWarning al usar python -m."""
    if name == "TablasExtractor":
        from scripts.extractors.tablas import TablasExtractor
        return TablasExtractor
    elif name == "ImagenesExtractor":
        from scripts.extractors.imagenes import ImagenesExtractor
        return ImagenesExtractor
    elif name == "ModificacionesPosterioresExtractor":
        from scripts.extractors.modificaciones_posteriores import ModificacionesPosterioresExtractor
        return ModificacionesPosterioresExtractor
    raise AttributeError(f"El módulo 'scripts.extractors' no tiene el atributo '{name}'")


__all__ = [
    "BaseExtractor",
    "ResultadoBloque",
    "ExtractorRegistry",
    "register_extractor",
    "TablasExtractor",
    "ImagenesExtractor",
    "ModificacionesPosterioresExtractor",
    "registrar_todos_los_extractores",
]



