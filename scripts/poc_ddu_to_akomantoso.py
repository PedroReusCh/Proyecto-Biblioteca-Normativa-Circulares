"""Script CLI de Orquestación y Ejecución de la PoC de Conversión de Circulares DDU.

Este script permite procesar circulares DDU en formato PDF, extraer su estructura y metadatos,
y generar sus representaciones en Akoma Ntso XML y RDF Turtle.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional, Set

# Asegurar que el directorio de scripts esté en el path de Python
scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from ddu_parser import DDUParser
from ddu_to_rdf import DDUToRDF
from ddu_to_xml import DDUToXML


def procesar_circular(pdf_path: Path, output_dir: Path) -> bool:
    """Procesa una única circular DDU, generando sus archivos XML y RDF.

    Args:
        pdf_path: Ruta del archivo PDF de la circular DDU.
        output_dir: Directorio donde se guardarán los archivos resultantes.

    Returns:
        True si el procesamiento fue exitoso, False en caso contrario.
    """
    if not pdf_path.exists():
        print(f"Error: El archivo PDF no existe en '{pdf_path}'", file=sys.stderr)
        return False

    try:
        print(f"Procesando circular: {pdf_path.name}")
        
        # 1. Parsear el PDF
        parser = DDUParser(pdf_path)
        datos = parser.parse_pdf()
        
        numero_doc = datos.get("numero")
        if not numero_doc:
            print(f"Error: No se pudo extraer el número de la circular desde '{pdf_path.name}'", file=sys.stderr)
            return False
        
        numero_doc_str = str(numero_doc).strip()
        
        # 2. Generar XML Akoma Ntso
        print(f"  -> Generando XML para DDU {numero_doc_str}...")
        generador_xml = DDUToXML()
        xml_str = generador_xml.generar_xml(datos)
        
        # 3. Generar RDF Turtle
        print(f"  -> Generando RDF Turtle para DDU {numero_doc_str}...")
        generador_rdf = DDUToRDF()
        rdf_str = generador_rdf.generar_rdf(datos)
        
        # 4. Guardar archivos de salida
        output_dir.mkdir(parents=True, exist_ok=True)
        xml_output_path = output_dir / f"servicio_doc_{numero_doc_str}.xml"
        rdf_output_path = output_dir / f"servicio_doc_{numero_doc_str}.ttl"
        
        xml_output_path.write_text(xml_str, encoding="utf-8")
        rdf_output_path.write_text(rdf_str, encoding="utf-8")
        
        print(f"  [Éxito] Archivos guardados:\n    - {xml_output_path}\n    - {rdf_output_path}")
        return True

    except Exception as e:
        print(f"Error procesando {pdf_path.name}: {e}", file=sys.stderr)
        return False


def main() -> None:
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="CLI para orquestar la conversión de circulares DDU a XML Akoma Ntso y RDF Turtle."
    )
    
    grupo = parser.add_mutually_exclusive_group(required=True)
    grupo.add_argument(
        "--all",
        action="store_true",
        help="Procesar todas las circulares PDF presentes en la carpeta 'circulares/'."
    )
    grupo.add_argument(
        "--id",
        type=str,
        help="Identificador numérico de la circular a procesar (ej. 533)."
    )
    
    args = parser.parse_args()
    
    # Definir directorios base del proyecto
    proyecto_raiz = Path(__file__).resolve().parents[1]
    circulares_dir = proyecto_raiz / "circulares"
    output_dir = proyecto_raiz / "bcn - consultas"
    
    if not circulares_dir.exists():
        print(f"Error: La carpeta de circulares no existe en '{circulares_dir}'", file=sys.stderr)
        sys.exit(1)
        
    exitosos: int = 0
    fallidos: int = 0
    
    if args.all:
        # Definir el alcance oficial de la PoC
        ids_oficiales = {"531", "533", "537", "546"}
        # Buscar todas las circulares PDF en la carpeta
        pdf_paths = sorted(list(circulares_dir.glob("DDU *.pdf")) + list(circulares_dir.glob("ddu *.pdf")))
        # Filtrar duplicados y acotar al alcance oficial de la PoC
        pdf_paths_unicas: List[Path] = []
        seen_names: Set[str] = set()
        for p in pdf_paths:
            if p.name.lower() not in seen_names:
                # Extraer el número del nombre del archivo (ej. 'DDU 531.pdf' -> '531')
                partes_nombre = p.stem.split()
                if len(partes_nombre) >= 2:
                    numero_id = partes_nombre[1].strip()
                    if numero_id in ids_oficiales:
                        seen_names.add(p.name.lower())
                        pdf_paths_unicas.append(p)
        
        if not pdf_paths_unicas:
            print("No se encontraron los archivos PDF de las 4 circulares oficiales de la PoC en la carpeta 'circulares/'.", file=sys.stderr)
            sys.exit(1)
            
        print(f"Encontradas {len(pdf_paths_unicas)} circulares oficiales de la PoC para procesar.")
        for pdf_path in pdf_paths_unicas:
            if procesar_circular(pdf_path, output_dir):
                exitosos += 1
            else:
                fallidos += 1
    else:
        # Procesar por ID específico
        id_limpio = str(args.id).strip()
        # Buscar el archivo correspondiente
        posibles_archivos: List[Path] = [
            circulares_dir / f"DDU {id_limpio}.pdf",
            circulares_dir / f"ddu {id_limpio}.pdf",
            circulares_dir / f"DDU_{id_limpio}.pdf",
            circulares_dir / f"ddu_{id_limpio}.pdf",
        ]
        
        pdf_path_seleccionado: Optional[Path] = None
        for path in posibles_archivos:
            if path.exists():
                pdf_path_seleccionado = path
                break
                
        if not pdf_path_seleccionado:
            # Intentar búsqueda flexible por patrón de glob si no existe directo
            patrones: List[str] = [f"*{id_limpio}*.pdf"]
            encontrados: List[Path] = []
            for pat in patrones:
                encontrados.extend(circulares_dir.glob(pat))
            if encontrados:
                pdf_path_seleccionado = encontrados[0]
                
        if not pdf_path_seleccionado:
            print(f"Error: No se encontró ningún archivo PDF para la circular con ID '{id_limpio}' en '{circulares_dir}'.", file=sys.stderr)
            sys.exit(1)
            
        if procesar_circular(pdf_path_seleccionado, output_dir):
            exitosos += 1
        else:
            fallidos += 1
            
    print(f"\nProceso finalizado. Exitosos: {exitosos}, Fallidos: {fallidos}")
    if fallidos > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
