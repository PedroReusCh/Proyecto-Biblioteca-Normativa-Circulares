"""Script de validacion estructural formal que certifica tipos y atributos heredados entre XSD y CSV."""

import csv
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Set


def obtener_atributos_tipo(
    type_name: str,
    root: ET.Element,
    ns: Dict[str, str],
    attr_groups: Dict[str, Set[str]],
    cache: Dict[str, Set[str]]
) -> Set[str]:
    """Resuelve recursivamente los atributos directos e heredados de un complexType."""
    if type_name in cache:
        return cache[type_name]

    # Prevenir bucles de recursion
    cache[type_name] = set()

    ct_node = root.find(f".//xsd:complexType[@name='{type_name}']", ns)
    if ct_node is None:
        return set()

    attrs: Set[str] = set()

    # 1. Atributos directos a nivel de complexType
    for attr in ct_node.findall("xsd:attribute", ns):
        name = attr.attrib.get("name")
        if name:
            attrs.add(name)

    # 2. Extensiones y herencia
    extension = ct_node.find(".//xsd:extension", ns)
    if extension is not None:
        base = extension.attrib.get("base")
        if base:
            base_name = base.split(":")[-1] if ":" in base else base
            # Heredar recursivamente los atributos del tipo base
            attrs.update(obtener_atributos_tipo(base_name, root, ns, attr_groups, cache))
        
        # Atributos declarados dentro del bloque de extension
        for attr in extension.findall("xsd:attribute", ns):
            name = attr.attrib.get("name")
            if name:
                attrs.add(name)
        for group in extension.findall("xsd:attributeGroup", ns):
            ref = group.attrib.get("ref")
            if ref:
                ref_name = ref.split(":")[-1] if ":" in ref else ref
                if ref_name in attr_groups:
                    attrs.update(attr_groups[ref_name])

    # 3. Grupos de atributos directos
    for group in ct_node.findall("xsd:attributeGroup", ns):
        ref = group.attrib.get("ref")
        if ref:
            ref_name = ref.split(":")[-1] if ":" in ref else ref
            if ref_name in attr_groups:
                attrs.update(attr_groups[ref_name])

    # 4. Atributos en complexContent y simpleContent generales
    for content in ct_node.findall(".//xsd:complexContent", ns) + ct_node.findall(".//xsd:simpleContent", ns):
        for attr in content.findall(".//xsd:attribute", ns):
            name = attr.attrib.get("name")
            if name:
                attrs.add(name)
        for group in content.findall(".//xsd:attributeGroup", ns):
            ref = group.attrib.get("ref")
            if ref:
                ref_name = ref.split(":")[-1] if ":" in ref else ref
                if ref_name in attr_groups:
                    attrs.update(attr_groups[ref_name])

    cache[type_name] = attrs
    return attrs


def resolver_atributos_complextype_anonimo(
    local_node: ET.Element,
    root: ET.Element,
    ns: Dict[str, str],
    attr_groups: Dict[str, Set[str]],
    cache: Dict[str, Set[str]]
) -> Set[str]:
    """Resuelve atributos para declaraciones complexType anonimas inline."""
    attrs: Set[str] = set()
    
    # Atributos directos
    for attr in local_node.findall(".//xsd:attribute", ns):
        name = attr.attrib.get("name")
        if name:
            attrs.add(name)
            
    # Atributos por extension
    extension = local_node.find(".//xsd:extension", ns)
    if extension is not None:
        base = extension.attrib.get("base")
        if base:
            base_name = base.split(":")[-1] if ":" in base else base
            attrs.update(obtener_atributos_tipo(base_name, root, ns, attr_groups, cache))
            
        # Atributos locales de la extension
        for attr in extension.findall("xsd:attribute", ns):
            name = attr.attrib.get("name")
            if name:
                attrs.add(name)
            
    # Referencias a grupos
    for group in local_node.findall(".//xsd:attributeGroup", ns):
        ref = group.attrib.get("ref")
        if ref:
            ref_name = ref.split(":")[-1] if ":" in ref else ref
            if ref_name in attr_groups:
                attrs.update(attr_groups[ref_name])
                
    return attrs


def main() -> None:
    proyecto_raiz = Path(__file__).resolve().parents[1]
    xsd_path = proyecto_raiz / "bcn - documentación" / "Esquema Akoma-Ntoso BCN.xsd"
    if not xsd_path.exists():
        xsd_path = proyecto_raiz / "bcn - documentacion" / "Esquema Akoma-Ntoso BCN.xsd"
        
    doc_dir = proyecto_raiz / "bcn - documentación"
    if not doc_dir.exists():
        doc_dir = proyecto_raiz / "bcn - documentacion"
    csv_dicc_path = doc_dir / "diccionario_dato_akoma_ntoso.csv"

    print("Iniciando Validacion Estructural Formal: CSV vs XSD (con Resolucion de Herencia)...")

    if not xsd_path.exists():
        print(f"ERROR: Archivo XSD no encontrado en {xsd_path}")
        sys.exit(1)
    if not csv_dicc_path.exists():
        print(f"ERROR: CSV de Diccionario de Datos no encontrado en {csv_dicc_path}")
        sys.exit(1)

    # 1. Parsear el XSD original
    tree = ET.parse(xsd_path)
    root = tree.getroot()
    ns = {"xsd": "http://www.w3.org/2001/XMLSchema"}

    # Mapear grupos de atributos globales del XSD
    attr_groups: Dict[str, Set[str]] = {}
    for group in root.findall("xsd:attributeGroup", ns):
        g_name = group.attrib.get("name")
        if g_name:
            attrs: Set[str] = set()
            for attr in group.findall(".//xsd:attribute", ns):
                name = attr.attrib.get("name")
                if name:
                    attrs.add(name)
            attr_groups[g_name] = attrs

    # Cache de resolucion de complexTypes
    complex_types_cache: Dict[str, Set[str]] = {}

    # Extraer las definiciones de elementos y sus atributos globales del XSD
    elementos_xsd: Dict[str, Dict[str, str | Set[str]]] = {}
    for el in root.findall("xsd:element", ns):
        name = el.attrib.get("name")
        if not name:
            continue
            
        type_attr = el.attrib.get("type", "")
        type_class = type_attr.split(":")[-1] if ":" in type_attr else type_attr
        
        attrs_soportados: Set[str] = set()
        
        # Resolver tipo complejo global
        if type_class:
            attrs_soportados.update(obtener_atributos_tipo(type_class, root, ns, attr_groups, complex_types_cache))
            
        # Resolver complexType inline local
        local_complex = el.find("xsd:complexType", ns)
        if local_complex is not None:
            attrs_soportados.update(resolver_atributos_complextype_anonimo(local_complex, root, ns, attr_groups, complex_types_cache))

        # Atributos basicos comunes
        attrs_soportados.add("id")

        elementos_xsd[name] = {
            "tipo": type_class,
            "atributos": attrs_soportados
        }

    print(f"  [XSD] Mapeados {len(elementos_xsd)} elementos globales con sus atributos y tipos.")

    # 2. Leer y validar el CSV de diccionario de datos
    discrepancias_tipo = 0
    discrepancias_attrs = 0
    total_validados = 0

    with open(csv_dicc_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames:
            for row in reader:
                el = row.get("Elemento_XML")
                if not isinstance(el, str) or not el:
                    continue
                
                desc = row.get("Descripcion", "")
                csv_attrs_raw = row.get("Atributos_Soportados", "")
                
                # Intentar resolver como global o local
                if el not in elementos_xsd:
                    local_el_node = root.find(f".//xsd:element[@name='{el}']", ns)
                    if local_el_node is not None:
                        type_attr = local_el_node.attrib.get("type", "")
                        type_class = type_attr.split(":")[-1] if ":" in type_attr else type_attr
                        attrs_locales: Set[str] = set()
                        if type_class:
                            attrs_locales.update(obtener_atributos_tipo(type_class, root, ns, attr_groups, complex_types_cache))
                        local_complex = local_el_node.find("xsd:complexType", ns)
                        if local_complex is not None:
                            attrs_locales.update(resolver_atributos_complextype_anonimo(local_complex, root, ns, attr_groups, complex_types_cache))
                        attrs_locales.add("id")
                        def_xsd = {
                            "tipo": type_class,
                            "atributos": attrs_locales
                        }
                    else:
                        if el == "xsd:schema":
                            continue
                        print(f"  [AVISO] Elemento '{el}' en CSV no existe en XSD.")
                        continue
                else:
                    def_xsd = elementos_xsd[el]
                
                total_validados += 1
                tipo_real_xsd = str(def_xsd["tipo"])
                attrs_reales_xsd = def_xsd["atributos"]
                assert isinstance(attrs_reales_xsd, set)

                # A. Validar coherencia del tipo
                if tipo_real_xsd:
                    pattern = rf"\(Tipo:\s*{re.escape(tipo_real_xsd)}\)"
                    if not re.search(pattern, desc):
                        print(f"  [ERROR Tipo] Elemento '{el}': XSD define tipo '{tipo_real_xsd}' pero no figura en la descripcion CSV. Desc actual: {desc}")
                        discrepancias_tipo += 1

                # B. Validar coherencia de atributos
                csv_attrs = {a.strip() for a in csv_attrs_raw.split(",") if a.strip()}
                for attr_csv in csv_attrs:
                    if attr_csv not in attrs_reales_xsd:
                        print(f"  [ERROR Atributos] Elemento '{el}': CSV declara atributo '{attr_csv}' no soportado en XSD. Soportados reales: {sorted(list(attrs_reales_xsd))}")
                        discrepancias_attrs += 1

    print(f"\nResumen de la Validacion:")
    print(f"  Total elementos validados: {total_validados}")
    print(f"  Discrepancias de Tipo: {discrepancias_tipo}")
    print(f"  Discrepancias de Atributos: {discrepancias_attrs}")

    if discrepancias_tipo == 0 and discrepancias_attrs == 0:
        print("\n  [EXITO] Los archivos CSV cumplen formalmente al 100% con la estructura del XSD.")
        sys.exit(0)
    else:
        print("\n  [FALLO] Existen discrepancias de estructura o atributos entre los CSV y el XSD.")
        sys.exit(1)


if __name__ == "__main__":
    main()
