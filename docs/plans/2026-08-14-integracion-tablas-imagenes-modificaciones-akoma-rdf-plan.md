# Plan de Implementación: Integración de Tablas, Imágenes y Modificaciones Posteriores en Akoma Ntoso XML y RDF

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Extender `scripts/ddu_to_xml.py`, `scripts/csv_to_akoma_xml.py`, `scripts/ddu_to_rdf.py` y `scripts/csv_to_rdf.py` para serializar de forma canónica `<attachments>`, `<img>`, `<lifecycle>`, `<analysis><passiveModifications>` y `minvu-ddu:modificadaPor`.

**Architecture:** Mapeo formal de los 14 bloques del CSV / `DatosCircularDDU` a la estructura del esquema Akoma Ntoso BCN v2.0 y al grafo RDF Turtle.

**Tech Stack:** Python 3.13, xmlschema / lxml / xml.etree, rdflib, pytest, typing estricto.

---

### Task 1: Actualizar Tests Unitarios de XML y RDF con Nuevas Estructuras Canónicas

**Files:**
- Modify: `test/test_xml_generation.py`
- Modify: `test/test_rdf_generation.py`
- Modify: `test/test_csv_to_akoma_xml.py`
- Modify: `test/test_csv_to_rdf.py`

**Step 1: Agregar aserciones para:**
- Presencia de `<attachments>` y `<componentRef>` en XML cuando hay tablas.
- Presencia de `<img>` en XML cuando hay imágenes.
- Presencia de `<lifecycle>` y `<analysis><passiveModifications>` cuando hay modificaciones posteriores.
- Presencia de `minvu-ddu:modificadaPor` en RDF.

**Step 2: Ejecutar tests para verificar fallos iniciales**
`pytest test/test_xml_generation.py test/test_rdf_generation.py test/test_csv_to_akoma_xml.py test/test_csv_to_rdf.py -v`

---

### Task 2: Implementar Soporte en `scripts/ddu_to_xml.py` y `scripts/csv_to_akoma_xml.py`

**Files:**
- Modify: `scripts/ddu_to_xml.py`
- Modify: `scripts/csv_to_akoma_xml.py`

**Step 1: En `scripts/ddu_to_xml.py`:**
- Inyectar `<lifecycle>` y `<analysis>` en `<meta>` según la secuencia del XSD.
- Inyectar `<img>` en párrafos que introducen esquemas/figuras.
- Inyectar `<attachments>` con `<componentRef>` tras `<conclusions>`.
- Parsear adecuadamente diccionarios o manifiestos planos de tablas e imágenes.

**Step 2: En `scripts/csv_to_akoma_xml.py`:**
- En `read_csv()`, cargar campos `tablas`, `imagenes` y `modificaciones_posteriores` y pasarlos a `DatosCircularDDU`.

**Step 3: Ejecutar tests de XML**
`pytest test/test_xml_generation.py test/test_csv_to_akoma_xml.py -v`

---

### Task 3: Implementar Soporte en `scripts/ddu_to_rdf.py` y `scripts/csv_to_rdf.py`

**Files:**
- Modify: `scripts/ddu_to_rdf.py`
- Modify: `scripts/csv_to_rdf.py`

**Step 1: En `scripts/ddu_to_rdf.py`:**
- Extraer circular modificadora desde `modificaciones_posteriores` y generar tripleta `minvu-ddu:modificadaPor <...>`.

**Step 2: En `scripts/csv_to_rdf.py`:**
- En `read_csv()`, cargar `modificaciones_posteriores` hacia `DatosCircularDDU`.

**Step 3: Ejecutar tests de RDF**
`pytest test/test_rdf_generation.py test/test_csv_to_rdf.py -v`

---

### Task 4: Regenerar Salidas de DDU 456, Validar Suite Completa (79+ tests), Actualizar Documentación y Push

**Files:**
- Modify: `salidas_xml/DDU_456_akoma.xml`
- Modify: `salidas_rdf/DDU_456_rdf.ttl`
- Modify: `CHANGELOG.md`

**Step 1: Regenerar salidas completas de DDU 456**
**Step 2: Ejecutar suite completa `pytest -v` y validación XSD**
**Step 3: Actualizar `CHANGELOG.md`**
**Step 4: Commit y Push a origin `feature/ddu-456`**
