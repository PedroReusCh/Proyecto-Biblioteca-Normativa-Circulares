"""Interfaz base y registro centralizado para extractores de circulares DDU."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Type, TypeVar

T = TypeVar("T", bound="BaseExtractor")


@dataclass
class ResultadoBloque:
    """Resultado estandarizado de la extracción de un bloque de circular DDU."""

    nombre_bloque: str
    exito: bool
    datos: Dict[str, Any]
    confianza: float = 1.0
    observaciones: str = ""


class BaseExtractor(ABC):
    """Clase base abstracta para todos los ETLs modulares de circulares DDU."""

    @property
    @abstractmethod
    def nombre_bloque(self) -> str:
        """Nombre identificador del bloque (ej. 'antecedentes')."""
        pass

    @abstractmethod
    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Ejecuta la lógica de extracción del bloque sobre el texto plano.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los datos extraídos y nivel de confianza.
        """
        pass


class ExtractorRegistry:
    """Registro centralizado de clases de extractores decoradas con @register_extractor."""

    _registry: Dict[str, Type[BaseExtractor]] = {}

    @classmethod
    def register(cls, extractor_cls: Type[T]) -> Type[T]:
        """Registra una clase de extractor asociándola a su nombre_bloque.

        Args:
            extractor_cls: Clase que hereda de BaseExtractor.

        Returns:
            La misma clase registrada para permitir uso como decorador.
        """
        instance = extractor_cls()
        cls._registry[instance.nombre_bloque] = extractor_cls
        return extractor_cls

    @classmethod
    def get_all_extractors(cls) -> Dict[str, Type[BaseExtractor]]:
        """Obtiene un diccionario clonado con todas las clases de extractores registrados.

        Returns:
            Diccionario mapeando nombre_bloque a la clase del extractor.
        """
        return dict(cls._registry)

    @classmethod
    def clear(cls) -> None:
        """Limpia todos los extractores registrados."""
        cls._registry.clear()


def register_extractor(cls: Type[T]) -> Type[T]:
    """Decorador para registrar automáticamente una clase de extractor.

    Args:
        cls: Clase que implementa BaseExtractor.

    Returns:
        La clase de extractor decorada.
    """
    return ExtractorRegistry.register(cls)
