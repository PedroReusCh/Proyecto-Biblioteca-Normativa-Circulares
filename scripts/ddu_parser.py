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
            if not secciones:
                secciones = fb.get("secciones", [])

        # 7. Extraer firmante y lista de distribución
        if not firmante:
            if numero in ["531", "533", "537", "546"]:
                firmante = "VICENTE BURGOS SALAS, JEFE DIVISIÓN DE DESARROLLO URBANO"
            if numero in self.fallbacks_estaticos and "firmante" in self.fallbacks_estaticos[numero]:
                firmante = self.fallbacks_estaticos[numero]["firmante"]

        lista_distribucion_str = ""
        if lineas_distribucion:
            texto_dist_raw = "\n".join(lineas_distribucion)
            match_dist = re.search(r"(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N)\s*:?\s*(.*)", texto_dist_raw, re.IGNORECASE | re.DOTALL)
            dist_text = match_dist.group(1) if match_dist else texto_dist_raw
            lines_dist = [d.strip() for d in dist_text.splitlines() if d.strip()]
            dist_items: List[str] = []
            for d in lines_dist:
                # Quitar pie de página ruidoso y marcas de agua de BCN/MINVU
                d_clean = re.sub(r"\s*!+\.?\s*Ministerio de Vivienda.*$", "", d)
                d_clean = re.sub(r"\s*P[áa]gina\s+\d+\s+de\s+\d+\s*$", "", d_clean, flags=re.IGNORECASE)
                d_clean = d_clean.strip()
                if not d_clean:
                    continue
                # Normalizar "l. " inicial a "1. "
                d_clean = re.sub(r"^l\.\s+", "1. ", d_clean)
                dist_items.append(d_clean)
            lista_distribucion_str = ", ".join(dist_items)

        # 8. Extraer descriptores, referencias y elementos visuales de forma genérica
        if not descriptores:
            match_desc = re.search(r"(?:DESCRIPTORES|PALABRAS\s+CLAVE|VOCABLOS)\s*:?\s*([^\n]+)", raw_text_norm, re.IGNORECASE)
            if match_desc:
                descriptores = match_desc.group(1).strip()

        referencias_list: List[str] = []
        patron_ref = re.compile(r"(?:circular\s+(?:ddu\s+)?n?[°oº]?\s*(\d+)\b|\bddu\s+n?[°oº]?\s*(\d+)\b)", re.IGNORECASE)
        for match in patron_ref.finditer(raw_text_norm):
            num_ref = match.group(1) or match.group(2)
            if num_ref and num_ref != numero and num_ref not in referencias_list:
                referencias_list.append(f"DDU {num_ref}")
        referencias = ", ".join(referencias_list)

        elementos_visuales_list: List[str] = []
        if re.search(r"\b(tabla|cuadro|gr[áa]fico|imagen|esquema)\b", raw_text_norm, re.IGNORECASE):
            elementos_visuales_list.append("Menciones de tablas/gráficos/imágenes en el texto")
        if re.search(r"[\-\+\|]{5,}", raw_text_norm):
            elementos_visuales_list.append("Estructura tabular detectada por caracteres de control")
        elementos_visuales = ", ".join(elementos_visuales_list)

        return {
            "numero": numero,
            "fecha": fecha,
            "materia": materia,
            "emisor": emisor,
            "antecedentes": antecedentes,
            "secciones": secciones,
            "numero_ord": numero_ord,
            "destinatarios": destinatarios,
            "firmante": firmante,
            "lista_distribucion": lista_distribucion_str,
            "descriptores": descriptores,
            "referencias": referencias,
            "elementos_visuales": elementos_visuales,
        }
=======
        return self.orchestrator.process_pdf(self.pdf_path)
>>>>>>> 23d2ec4 (refactor: integrar ddu_parser con DDUOrchestrator manteniendo retrocompatibilidad total)

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
