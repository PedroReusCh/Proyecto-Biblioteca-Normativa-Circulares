"""Script de Exportación por Lotes de Circulares DDU a CSV Estructurado.

Este script procesa circulares DDU en formato PDF a través del parser central
y exporta su contenido estructurado a archivos CSV individuales dentro de la
carpeta 'bcn - circulares - csv', alineados con la maqueta maestra documental.
"""

import csv
import os
import re
from pathlib import Path
from typing import Dict, List

from ddu_parser import DDUParser
from ddu_types import DatosCircularDDU, SeccionDDU


class DDUExporter:
    """Clase encargada de mapear y exportar los datos parseados de las circulares a CSV."""

    def __init__(self, ruta_maqueta: Path, ruta_salida: Path) -> None:
        """Inicializa el exportador cargando la maqueta maestra en memoria.

        Args:
            ruta_maqueta: Ruta al archivo CSV maestro de estructura.
            ruta_salida: Ruta al directorio donde se guardarán las salidas CSV.
        """
        self.ruta_maqueta = ruta_maqueta
        self.ruta_salida = ruta_salida
        self.plantilla: Dict[str, Dict[str, str]] = {}
        self._cargar_plantilla_maqueta()

    def _cargar_plantilla_maqueta(self) -> None:
        """Lee el CSV de la maqueta maestra y lo almacena indexado por el identificador de campo."""
        if not self.ruta_maqueta.exists():
            raise FileNotFoundError(f"No se encontró la maqueta maestra en {self.ruta_maqueta}")

        with open(self.ruta_maqueta, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                campo = row.get("campo", "")
                if campo:
                    self.plantilla[campo] = {
                        "bloque": row.get("bloque", ""),
                        "obligatorio": row.get("obligatorio", ""),
                        "orden": row.get("orden", ""),
                        "zona": row.get("zona", ""),
                        "campo_parser": row.get("campo_parser", ""),
                        "estado_parser": row.get("estado_parser", ""),
                        "reglas": row.get("reglas", ""),
                        "descripcion": row.get("descripcion", ""),
                    }

    def _obtener_fila_base(self, campo: str) -> Dict[str, str]:
        """Obtiene una copia de los metadatos de la maqueta para un campo dado.

        Args:
            campo: Identificador del campo.

        Returns:
            Diccionario con las columnas base del CSV.
        """
        if campo in self.plantilla:
            base = self.plantilla[campo].copy()
            base["campo"] = campo
            return base
        return {
            "bloque": "Cuerpo",
            "campo": campo,
            "obligatorio": "no",
            "orden": "",
            "zona": "cuerpo",
            "campo_parser": "",
            "estado_parser": "implementado",
            "reglas": "",
            "descripcion": "",
        }

    def exportar_a_csv(self, datos: DatosCircularDDU, path_salida_csv: Path) -> None:
        """Mapea los datos de la circular a la estructura de 10 columnas y los guarda en un CSV.

        Args:
            datos: Datos estructurados de la circular.
            path_salida_csv: Ruta del archivo CSV de destino.
        """
        filas_salida: List[Dict[str, str]] = []

        # 1. Metadatos de Encabezado (Orden 1 a 8)
        campos_encabezado = [
            ("numero_ddu", datos.get("numero", "")),
            ("numero_ord", datos.get("numero_ord", "")),
            ("antecedentes", datos.get("antecedentes", "")),
            ("materia", datos.get("materia", "")),
            ("descriptores", datos.get("descriptores", "")),
            ("fecha_emision", datos.get("fecha", "")),
            ("destinatarios", datos.get("destinatarios", "")),
            ("emisor", datos.get("emisor", "")),
        ]

        for campo, valor in campos_encabezado:
            fila = self._obtener_fila_base(campo)
            fila["valor_extraido"] = str(valor).strip()
            filas_salida.append(fila)

        # 2. Procesamiento del Cuerpo (Orden 9 a 14)
        secciones: List[SeccionDDU] = datos.get("secciones", [])
        for idx_sec, seccion in enumerate(secciones, 1):
            titulo_sec = str(seccion.get("titulo", "")).strip()
            parrafos = seccion.get("parrafos", [])

            # Agregar Sección Romana (Orden 9) si aplica
            match_romano = re.match(r"^([IVXLCDM]+\.?)\s+(.+)$", titulo_sec, re.IGNORECASE)
            if match_romano or (titulo_sec and titulo_sec != "ENCABEZADO"):
                fila_sec = self._obtener_fila_base("seccion_romana")
                fila_sec["valor_extraido"] = titulo_sec
                filas_salida.append(fila_sec)

            # Iterar sobre párrafos
            for parrafo in parrafos:
                parrafo_str = str(parrafo).strip()
                if not parrafo_str:
                    continue

                # Intentamos extraer número del párrafo (arábigo)
                match_par = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", parrafo_str)
                if match_par:
                    texto_cuerpo = match_par.group(2).strip()
                else:
                    texto_cuerpo = parrafo_str

                # Agregar Numeral Arábigo (Orden 10)
                fila_num = self._obtener_fila_base("numeral_arabigo")
                fila_num["valor_extraido"] = parrafo_str
                filas_salida.append(fila_num)

                # Intentamos extraer subtítulo (Orden 11)
                match_sub = re.match(r"^([A-ZÁÉÍÓÚÑ\s\d\"'()]+[:.])\s+(.+)$", texto_cuerpo)
                if match_sub:
                    fila_sub = self._obtener_fila_base("subtitulo_numeral")
                    fila_sub["valor_extraido"] = match_sub.group(1).strip()
                    filas_salida.append(fila_sub)
                    texto_cuerpo = match_sub.group(2).strip()

                # Intentamos extraer listas multinivel (Orden 12)
                # ej: a) Que se encuentren... b) Que, a dicha fecha...
                patron_lista = re.findall(r"([a-z\d]+\)\s+[^;]+(?:;|\.|$))", texto_cuerpo, re.IGNORECASE)
                for item in patron_lista:
                    fila_list = self._obtener_fila_base("lista_multinivel")
                    fila_list["valor_extraido"] = item.strip()
                    filas_salida.append(fila_list)

        # Referencias Cruzadas (Orden 13)
        fila_ref = self._obtener_fila_base("referencia_cruzada")
        fila_ref["valor_extraido"] = str(datos.get("referencias", "")).strip()
        filas_salida.append(fila_ref)

        # Elementos Visuales (Orden 14)
        fila_vis = self._obtener_fila_base("tabla_imagen")
        fila_vis["valor_extraido"] = str(datos.get("elementos_visuales", "")).strip()
        filas_salida.append(fila_vis)

        # 3. Metadatos de Cierre (Orden 15 a 16)
        campos_cierre = [
            ("firmante", datos.get("firmante", "")),
            ("lista_distribucion", datos.get("lista_distribucion", "")),
        ]

        for campo, valor in campos_cierre:
            fila = self._obtener_fila_base(campo)
            fila["valor_extraido"] = str(valor).strip()
            filas_salida.append(fila)

        # Escribir el CSV con codificación UTF-8 con BOM y punto y coma como delimitador
        columnas = [
            "bloque",
            "campo",
            "obligatorio",
            "orden",
            "zona",
            "campo_parser",
            "estado_parser",
            "reglas",
            "descripcion",
            "valor_extraido",
        ]

        with open(path_salida_csv, mode="w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columnas, delimiter=";")
            writer.writeheader()
            for fila in filas_salida:
                # Filtrar solo las columnas requeridas
                row_data = {col: fila.get(col, "") for col in columnas}
                writer.writerow(row_data)


def main() -> None:
    """Función principal para la ejecución por lotes del exportador."""
    proyecto_raiz = Path(__file__).resolve().parents[1]
    ruta_maqueta = proyecto_raiz / "bcn - documentación" / "estructura_circular_ddu.csv"
    
    # Si la ruta alternativa en minúscula o sin tilde existe, usarla
    if not ruta_maqueta.exists():
        ruta_maqueta = proyecto_raiz / "bcn - documentacion" / "estructura_circular_ddu.csv"

    ruta_salida = proyecto_raiz / "bcn - circulares - csv"
    ruta_salida.mkdir(parents=True, exist_ok=True)

    circulares = ["531", "533", "537", "546"]

    print(f"=== Inicializando Exportación por Lotes a CSV (delimitador ';') ===")
    print(f"Maqueta maestra: {ruta_maqueta.name}")
    print(f"Carpeta de salida: {ruta_salida}\n")

    exporter = DDUExporter(ruta_maqueta, ruta_salida)

    for num in circulares:
        pdf_name = f"DDU {num}.pdf"
        pdf_path = proyecto_raiz / "circulares" / pdf_name
        # Probar en minúscula
        if not pdf_path.exists():
            pdf_path = proyecto_raiz / "circulares" / f"ddu {num}.pdf"

        if not pdf_path.exists():
            print(f"[ERROR] No se encontró el archivo PDF para circular {num} en: {pdf_path}")
            continue

        print(f"Procesando: {pdf_name}...")
        try:
            parser = DDUParser(pdf_path)
            datos = parser.parse_pdf()
            
            csv_name = f"DDU {num}.csv"
            path_salida = ruta_salida / csv_name
            exporter.exportar_a_csv(datos, path_salida)
            print(f"  [OK] Exportado con éxito a: {path_salida.name}")
        except Exception as e:
            print(f"  [ERROR] Falló el procesamiento de la circular {num}: {e}")

    print("\n=== Procesamiento por lotes finalizado ===")


if __name__ == "__main__":
    main()
