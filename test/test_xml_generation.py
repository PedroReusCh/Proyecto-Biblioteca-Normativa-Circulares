"""Script de prueba para la generación de XML Akoma Ntso de circulares DDU."""

import sys
from pathlib import Path
import xml.etree.ElementTree as ET

# Definir rutas y agregar scripts al path de importaciones
proyecto_raiz = Path(__file__).resolve().parents[1]
scripts_dir = proyecto_raiz / "scripts"
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))
if str(proyecto_raiz) not in sys.path:
    sys.path.insert(0, str(proyecto_raiz))

from scripts.ddu_parser import DDUParser
from scripts.ddu_to_xml import DDUToXML


def test_xml_generation() -> None:
    # Definir rutas
    proyecto_raiz = Path(__file__).resolve().parents[1]
    pdf_path = proyecto_raiz / "circulares" / "DDU 533.pdf"

    assert pdf_path.exists(), f"ERROR: No se encontró el archivo de prueba en {pdf_path}"

    print(f"Parseando PDF: {pdf_path.name}")
    parser = DDUParser(pdf_path)
    datos = parser.parse_pdf()

    print("\nMetadatos extraídos:")
    print(f"  Número: {datos['numero']}")
    print(f"  Fecha: {datos['fecha']}")
    print(f"  Emisor: {datos['emisor']}")
    print(f"  Materia: {datos['materia'][:80]}...")
    print(f"  Cantidad de secciones: {len(datos['secciones'])}")

    print("\nGenerando XML...")
    generador = DDUToXML()
    xml_str = generador.generar_xml(datos)

    # 1. Verificar que no esté vacío
    assert xml_str, "El XML generado está vacío."
    print("XML generado con éxito.")

    # 2. Verificar que sea XML bien formado
    root = ET.fromstring(xml_str)
    print("Verificación de sintaxis XML: BIEN FORMADO (ElementTree parseó con éxito).")

    # 3. Validar estructuralmente elementos clave
    print("\nValidación estructural:")
    print(f"  Elemento raíz: <{root.tag}> (esperado: doc)")
    assert root.tag.endswith("doc"), f"El tag raíz no es doc: {root.tag}"
    assert root.attrib.get("name") == "circular", "El atributo 'name' del tag raíz no es 'circular'"

    # Verificar que exista meta y mainBody
    meta = root.find(".//{http://www.akomantoso.org/2.0}meta")
    preface = root.find(".//{http://www.akomantoso.org/2.0}preface")
    main_body = root.find(".//{http://www.akomantoso.org/2.0}mainBody")

    print(f"  Contiene <meta>: {'SÍ' if meta is not None else 'NO'}")
    print(f"  Contiene <preface>: {'SÍ' if preface is not None else 'NO'}")
    print(f"  Contiene <mainBody>: {'SÍ' if main_body is not None else 'NO'}")

    assert meta is not None, "Falta el bloque <meta>"
    assert preface is not None, "Falta el bloque <preface>"
    assert main_body is not None, "Falta el bloque <mainBody>"

    # 4. Verificar metadatos de preface
    doc_type = preface.find(".//{http://www.akomantoso.org/2.0}docType")
    doc_number = preface.find(".//{http://www.akomantoso.org/2.0}docNumber")
    doc_date = preface.find(".//{http://www.akomantoso.org/2.0}docDate")
    doc_title = preface.find(".//{http://www.akomantoso.org/2.0}docTitle")

    assert doc_type is not None, "Falta el elemento docType"
    assert doc_number is not None, "Falta el elemento docNumber"
    assert doc_date is not None, "Falta el elemento docDate"
    assert doc_title is not None, "Falta el elemento docTitle"

    doc_title_text = doc_title.text or ""

    print(f"  docType: {doc_type.text}")
    print(f"  docNumber: {doc_number.text}")
    print(f"  docDate: {doc_date.text} (date={doc_date.attrib.get('date')})")
    print(f"  docTitle: {doc_title_text[:50]}...")

    # 5. Buscar tags <ref> (citas enlazadas)
    ref_elements = root.findall(".//{http://www.akomantoso.org/2.0}ref")
    print(f"\nSe encontraron {len(ref_elements)} referencias a la OGUC/LGUC (<ref>):")
    for r in ref_elements[:10]:
        print(f"  - Texto: '{r.text}' -> href: '{r.attrib.get('href')}'")

    print("\nXML generado y validado con éxito.")



if __name__ == "__main__":
    test_xml_generation()
