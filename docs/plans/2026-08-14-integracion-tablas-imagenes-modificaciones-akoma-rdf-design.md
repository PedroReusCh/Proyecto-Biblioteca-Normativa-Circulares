# Especificación de Diseño: Integración de Tablas, Imágenes y Modificaciones Posteriores en Akoma Ntoso XML y RDF

**Fecha:** 2026-08-14  
**Rama:** `feature/ddu-456`  
**Estándar:** Akoma Ntoso v2.0 BCN (`bcn - documentación/Esquema Akoma-Ntoso BCN.xsd`)  
**Estado:** Aprobado por el usuario  

---

## 1. Objetivo y Alcance

Incorporar de forma 100% estándar, canónica y validada los 3 nuevos bloques normativos (`Tablas`, `Imágenes`, `Modificaciones Posteriores`) en el generador XML Akoma Ntoso ([`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py) / [`scripts/csv_to_akoma_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/csv_to_akoma_xml.py)) y en el grafo RDF Turtle ([`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py) / [`scripts/csv_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/csv_to_rdf.py)), cumpliendo estrictamente con el orden de secuencia y tipos del XSD oficial de la BCN.

---

## 2. Conformidad Estructural XSD de Akoma Ntoso BCN

### 2.1 Orden Jerárquico de Elementos en `<doc>`
El elemento raíz `<doc>` (de tipo `openStructure`) exige la secuencia ordenada:
1. `<meta>` (requerido)
2. `<preface>` (opcional)
3. `<mainBody>` (requerido)
4. `<conclusions>` (opcional)
5. `<attachments>` (opcional, posicionado al final del documento)

### 2.2 Orden Jerárquico de Elementos en `<meta>`
El elemento `<meta>` exige la secuencia ordenada estricta:
1. `<identification>`
2. `<classification>`
3. `<lifecycle>` *(Nuevo: eventos temporales y de vigencia)*
4. `<analysis>` *(Nuevo: análisis de modificaciones pasivas/activas)*
5. `<references>` *(TLCs y referencias a personas, roles, organizaciones)*

---

## 3. Especificación de los Nuevos Elementos

### 3.1 Tablas (`Tablas` -> `<attachments>`)
Cuando existan tablas extraídas (en `datos.get("tablas")` o `tablas_manifiesto`), se serializa un contenedor `<attachments>` tras `<conclusions>` con elementos `<componentRef>`:
```xml
<attachments>
  <componentRef id="tabla_1" src="salidas_tablas/DDU_456_tabla_1.csv" showAs="Modificaciones Normativas (DDU 339, DDU 322, DDU 168)"/>
</attachments>
```

### 3.2 Imágenes (`Imágenes` -> `<img>` en Numeral de Introducción)
Cuando existan imágenes extraídas (en `datos.get("imagenes")` o `imagenes_manifiesto`), se inyecta el elemento `<img>` dentro del `<paragraph>` cuyo texto introduzca la figura (ej. Numeral 4: *"A continuación, se presenta un esquema ilustrativo..."*):
```xml
<paragraph id="par_1_4">
  <num>4.</num>
  <content>
    <p>A continuación, se presenta un esquema ilustrativo que sintetiza algunos de los aspectos abordados en la presente Circular:</p>
    <p><img id="img_1" src="salidas_imagenes/DDU_456_img_1.png" alt="Esquema ilustrativo: Planta azotea y corte esquemático" width="2131" height="1906"/></p>
  </content>
</paragraph>
```

### 3.3 Modificaciones Posteriores (`Modificaciones Posteriores` -> `<lifecycle>` y `<analysis>`)
Cuando existan notas de modificación posterior (ej. `"Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.)"`):
- En `<lifecycle>`:
  ```xml
  <lifecycle source="#minvu-ddu">
    <eventRef id="evento_mod_1" date="2024-05-02" source="#ddu-498" type="amendment"/>
  </lifecycle>
  ```
- En `<analysis>`:
  ```xml
  <analysis source="#redactor">
    <passiveModifications>
      <textualMod id="mod_1" type="substitution">
        <source href="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/2024-05-02/DDU 498"/>
        <destination href="#par_1_6"/>
      </textualMod>
    </passiveModifications>
  </analysis>
  ```
- En `<references>`:
  ```xml
  <TLCReference id="ddu-498" href="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/2024-05-02/DDU 498" showAs="Circular DDU 498"/>
  ```
- En el Grafo RDF (`scripts/ddu_to_rdf.py`):
  ```turtle
  minvu-ddu:modificadaPor <http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/2024-05-02/DDU 498> ;
  ```

---

## 4. Criterios de Éxito y Verificación

1. El XML generado en `salidas_xml/DDU_456_akoma.xml` valida contra `bcn - documentación/Esquema Akoma-Ntoso BCN.xsd` (mediante `xmlschema` o `lxml`).
2. El Grafo RDF en `salidas_rdf/DDU_456_rdf.ttl` incluye `minvu-ddu:modificadaPor`.
3. Todos los tests existentes y nuevos pasan al 100% (`pytest -v`).
4. Tipado estricto (Pylance Strict Mode) con 0 errores.
