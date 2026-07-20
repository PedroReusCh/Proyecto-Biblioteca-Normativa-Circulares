"""Script de prueba para la generación de RDF/Turtle de circulares DDU."""

import os
import sys
import py_compile
from pathlib import Path
from typing import Any, Dict

# Agregar scripts al path de importaciones
proyecto_raiz = Path(__file__).resolve().parents[1]
scripts_dir = proyecto_raiz / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from ddu_parser import DDUParser
from ddu_to_rdf import DDUToRDF


def main() -> None:
    # Definir rutas
    proyecto_raiz = Path(__file__).resolve().parents[1]
    pdf_path = proyecto_raiz / "circulares" / "DDU 533.pdf"

    if not pdf_path.exists():
        print(f"ERROR: No se encontró el archivo de prueba en {pdf_path}")
        return

    print("=== PASO 1: Validando compilación con py_compile ===")
    try:
        py_compile.compile(str(proyecto_raiz / "scripts" / "ddu_to_rdf.py"), doraise=True)
        print("Compilación EXITOSA para scripts/ddu_to_rdf.py")
    except Exception as e:
        print(f"ERROR de compilación: {e}")
        return

    print("\n=== PASO 2: Parseando PDF ===")
    print(f"Parseando PDF: {pdf_path.name}")
    parser = DDUParser(pdf_path)
    datos = parser.parse_pdf()

    print("\nMetadatos extraídos:")
    print(f"  Número: {datos.get('numero')}")
    print(f"  Fecha: {datos.get('fecha')}")
    print(f"  Emisor: {datos.get('emisor')}")
    print(f"  Materia: {datos.get('materia')[:80]}...")
    print(f"  Cantidad de secciones: {len(datos.get('secciones', []))}")

    print("\n=== PASO 3: Generando RDF (Turtle) ===")
    generador = DDUToRDF()
    rdf_str = generador.generar_rdf(datos)

    # 1. Verificar que no esté vacío
    assert rdf_str, "El RDF generado está vacío."
    print("RDF generado con éxito.")

    # Imprimir un extracto del RDF
    print("\nExtracto del RDF generado (Turtle):")
    print("-" * 60)
    print(rdf_str)
    print("-" * 60)

    # Guardar en tmp para inspección visual y auditoría
    tmp_dir = proyecto_raiz / "tmp"
    tmp_dir.mkdir(exist_ok=True)
    out_rdf_path = tmp_dir / "DDU_533_test.ttl"
    out_rdf_path.write_text(rdf_str, encoding="utf-8")
    print(f"\nArchivo RDF guardado en: {out_rdf_path}")

    # Validar que los prefijos y elementos estén presentes
    print("\n=== PASO 4: Validando contenido del RDF ===")
    prefijos = [
        "rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
        "rdfs: <http://www.w3.org/2000/01/rdf-schema#>",
        "owl: <http://www.w3.org/2002/07/owl#>",
        "dc: <http://purl.org/dc/elements/1.1/>",
        "bcn-norms: <http://datos.bcn.cl/ontologies/bcn-norms#>",
        "minvu-ddu: <http://datos.bcn.cl/ontologies/minvu-ddu#>",
        "bcn-resources: <http://datos.bcn.cl/ontologies/bcn-resources#>",
        "xsd: <http://www.w3.org/2001/XMLSchema#>"
    ]
    
    for p in prefijos:
        assert p in rdf_str, f"Falta el prefijo: {p}"
    print("  [OK] Todos los prefijos requeridos están presentes.")

    assert "minvu-ddu:CircularDDU rdfs:subClassOf bcn-norms:Norm ." in rdf_str, "Falta la declaración de jerarquía de clases."
    print("  [OK] Declaración de subclase de Norm correcta.")

    assert f"<http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{datos['fecha']}/{datos['numero']}>" in rdf_str, "Falta el recurso principal de la circular."
    print("  [OK] Identificador de circular correcto.")

    assert 'bcn-norms:hasNumber "533" ;' in rdf_str, "Falta o está incorrecto el número de circular."
    print("  [OK] Propiedad bcn-norms:hasNumber correcta.")

    assert f'bcn-norms:publishDate "{datos["fecha"]}"^^xsd:date ;' in rdf_str, "Falta o está incorrecta la fecha de publicación."
    print("  [OK] Propiedad bcn-norms:publishDate correcta.")

    assert "bcn-norms:createdBy <http://datos.bcn.cl/recurso/cl/organismo/ministerio-de-vivienda-y-urbanismo/division-de-desarrollo-urbano>" in rdf_str, "Falta o está incorrecta la relación de emisor."
    print("  [OK] Relación de emisor bcn-norms:createdBy correcta.")

    assert "minvu-ddu:interpretaA" in rdf_str, "Falta la relación de interpretación."
    print("  [OK] Relación minvu-ddu:interpretaA detectada.")

    assert "minvu-ddu:complementaA" in rdf_str, "Falta la relación de complementariedad con otras circulares."
    print("  [OK] Relación minvu-ddu:complementaA detectada.")

    assert "bcn-resources:tieneDocumentoAkomaNtoso" in rdf_str, "Falta el enlace al documento Akoma Ntoso XML."
    print("  [OK] Propiedad bcn-resources:tieneDocumentoAkomaNtoso correcta.")

    print("\n¡TODAS LAS VALIDACIONES DE CONTENIDO PASARON CON ÉXITO!")


if __name__ == "__main__":
    main()
