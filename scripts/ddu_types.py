"""Definiciones de Tipos Estructurados para el Procesamiento de Circulares DDU.

Este módulo define las estructuras de datos strictly mediante TypedDict para garantizar
el cumplimiento de los estándares de tipado estático (strict) en el proyecto.
"""

from typing import Any, Dict, List, NotRequired, Optional, TypedDict


class SeccionDDU(TypedDict):
    """Representa una sección estructurada dentro del cuerpo de la circular DDU."""

    titulo: str
    parrafos: List[str]


class DatosCircularDDU(TypedDict):
    """Representa la estructura de datos completa extraída de una circular DDU en PDF."""

    numero: str
    fecha: str
    materia: str
    emisor: str
    antecedentes: str
    secciones: List[SeccionDDU]
    referencias: NotRequired[str]
    elementos_visuales: NotRequired[str]
    numero_ord: NotRequired[str]
    descriptores: NotRequired[str]
    cuerpo: NotRequired[str]
    fecha_lugar: NotRequired[str]
    lugar: NotRequired[str]
    destinatarios: NotRequired[str]
    firmante: NotRequired[str]
    nombre_firmante: NotRequired[str]
    cargo_firmante: NotRequired[str]
    lista_distribucion: NotRequired[List[str]]

    distribucion_texto: NotRequired[str]
    notas_al_pie: NotRequired[str]
    tablas: NotRequired[Optional[List[Dict[str, Any]]]]
    imagenes: NotRequired[Optional[List[Dict[str, Any]]]]
    modificaciones_posteriores: NotRequired[str]

