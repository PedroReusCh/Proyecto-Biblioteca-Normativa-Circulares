"""Extractor de Texto PDF y Normalizador de URIs para Circulares DDU.

Este módulo contiene la clase DDUParser encargada de procesar archivos PDF correspondientes
a circulares DDU (División de Desarrollo Urbano) del Ministerio de Vivienda y Urbanismo,
extrayendo su texto, estructurando su cuerpo y normalizando sus metadatos.

Esta clase actúa como un wrapper de retrocompatibilidad que delega la extracción
al motor orquestado DDUOrchestrator.
"""

import re
import sys
import unicodedata
from pathlib import Path
from typing import List

_PROYECTO_RAIZ = Path(__file__).resolve().parents[1]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

import pypdf

try:
    from ddu_types import DatosCircularDDU
except ImportError:
    from scripts.ddu_types import DatosCircularDDU

try:
    from ddu_orchestrator import DDUOrchestrator
except ImportError:
    from scripts.ddu_orchestrator import DDUOrchestrator


class DDUParser:
    """Clase para extraer y estructurar el contenido y metadatos de circulares DDU en PDF."""

    def __init__(self, pdf_path: Path) -> None:
        """Inicializa el parser con la ruta del archivo PDF.

        Args:
            pdf_path: Ruta del archivo PDF a parsear.
        """
        self.pdf_path: Path = pdf_path
        self.orchestrator: DDUOrchestrator = DDUOrchestrator()

    def extract_raw_text(self) -> str:
        """Extrae todo el texto plano de las páginas del PDF usando pypdf.

        Returns:
            Texto completo del PDF.
        """
        reader = pypdf.PdfReader(self.pdf_path)
        text_parts: List[str] = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)

    def parse_pdf(self) -> DatosCircularDDU:
        """Parsea el PDF para extraer metadatos y cuerpo estructurado utilizando DDUOrchestrator.

        Returns:
            DatosCircularDDU estructurado con metadatos de la circular.
        """
        return self.orchestrator.process_pdf(self.pdf_path)

    @staticmethod
    def normalizar_uri(texto: str) -> str:
        """Normaliza un texto para generar un identificador de URI según pautas de BCN.

        Aplica minúsculas, remoción de diacríticos ASCII, transformación de plural a singular,
        y reemplazo de espacios por guiones medios (-) y comas por guiones bajos (_).

        Args:
            texto: Texto original.

        Returns:
            Identificador normalizado.
        """
        # 1. Convertir a minúsculas
        t = texto.lower()

        # 2. Reemplazar comas por guión bajo limpiando espacios adyacentes
        t = re.sub(r"\s*,\s*", "_", t)

        # 3. Quitar tildes y caracteres especiales usando normalización NFKD
        nfkd = unicodedata.normalize("NFKD", t)
        t = "".join([c for c in nfkd if not unicodedata.combining(c)])

        # 4. Mantener únicamente caracteres alfanuméricos, espacios, guiones y guiones bajos
        t = re.sub(r"[^a-z0-9\s\-_]", "", t)

        # 5. Función auxiliar para pasar palabras a singular
        def singularizar_palabra(w: str) -> str:
            excepciones = {
                "lunes",
                "martes",
                "miercoles",
                "jueves",
                "viernes",
                "crisis",
                "tesis",
                "analisis",
                "gas",
                "pais",
                "interes",
                "mes",
            }
            if w in excepciones:
                return w

            if w.endswith("s"):
                if w.endswith("ces"):
                    return w[:-3] + "z"

                consonantes = "bcdfghjklmnpqrstvwxyz"
                if w.endswith("es") and len(w) > 3:
                    ante_penultima = w[-3]
                    if ante_penultima in consonantes:
                        return w[:-2]  # Ejemplo: circulares -> circular, leyes -> ley

                return w[:-1]  # Ejemplo: casas -> casa

            return w

        # Reemplazar cada token alfanumérico por su versión singular
        def reemplazar_con_singular(m: re.Match[str]) -> str:
            return singularizar_palabra(m.group(1))

        t = re.sub(r"\b([a-z0-9]+)\b", reemplazar_con_singular, t)

        # 6. Reemplazar espacios por guiones
        t = re.sub(r"\s+", "-", t)

        # 7. Limpiar duplicados de guiones o combinaciones extrañas
        t = re.sub(r"-+", "-", t)
        t = re.sub(r"_+", "_", t)
        t = re.sub(r"-_|_-", "_", t)

        # 8. Limpiar caracteres de control al inicio/final
        t = t.strip("-_")

        return t
