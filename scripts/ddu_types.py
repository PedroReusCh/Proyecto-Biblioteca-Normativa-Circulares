"""Definiciones de Tipos Estructurados para el Procesamiento de Circulares DDU.

Este módulo define las estructuras de datos estrictas mediante TypedDict para garantizar
el cumplimiento de los estándares de tipado estático (strict) en el proyecto.
"""

from typing import List, TypedDict


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
    numero_ord: str
    destinatarios: str
    firmante: str
    lista_distribucion: List[str]
