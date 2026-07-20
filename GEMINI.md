# Instrucciones Operativas para la IA (GEMINI.md)

Este archivo contiene las directrices de diseño, reglas específicas y el contexto técnico del **Proyecto Biblioteca Normativa Circulares** destinadas a guiar a la IA (Antigravity CLI) en el mantenimiento y desarrollo del código.

## Contexto y Flujo del Proyecto

El objetivo principal es tomar circulares DDU (División de Desarrollo Urbano del MINVU, Chile) en formato PDF y procesarlas para generar documentos semánticos:

1. **Extracción y Estructuración**: [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) extrae el texto de los PDFs usando `pypdf`, estructurándolo en secciones y párrafos.
2. **Generación Akoma Ntoso XML**: [`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py) transforma los datos estructurados al estándar XML Akoma Ntoso v2.0 BCN compatible con el validador oficial.
3. **Generación RDF (Turtle)**: [`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py) mapea los metadatos a grafos semánticos RDF.

---

## Reglas Críticas para la IA

### 1. Mantenimiento de la Suite de Pruebas

* Cualquier cambio en la estructura o lógica de los scripts de transformación debe validarse de inmediato mediante la ejecución de la suite de pruebas local.
* Los tests deben permanecer completamente autónomos y pasar en su totalidad:
  * [`test/test_csv_integrity.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_csv_integrity.py): Valida la coherencia columnar de los archivos CSV locales.
  * [`test/test_spec_coverage.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_spec_coverage.py): Mapea elementos XSD contra el diccionario. Si la especificación externa no está presente, simula cobertura para no bloquear el flujo autónomo.
  * [`test/test_xsd_structural_validation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_xsd_structural_validation.py): Verifica tipos y atributos heredados entre XSD y CSV.
  * [`test/test_xml_generation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_xml_generation.py): Certifica que los XML construidos sean válidos y conformes estructuralmente.
  * [`test/test_rdf_generation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_rdf_generation.py): Valida la correctitud sintáctica del formato Turtle (RDF) y sus relaciones lógicas.

### 2. Normalización y URIs

* Al generar identificadores normalizados para URIs, se debe seguir estrictamente la función `normalizar_uri` implementada en [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py), la cual contempla remoción de diacríticos y singularización de sustantivos.

### 4. Idioma Obligatorio (Interacciones y Commits)
*   **Idioma Único**: Toda la comunicación, explicaciones, preguntas y respuestas con el usuario deben generarse exclusivamente en **español**.
*   **Mensajes de Commit**: Todos los mensajes de confirmación (commits) generados para Git por la IA deben redactarse exclusivamente en **español** (por ejemplo, `doc: actualizar documentación` en lugar de `docs: update documentation`).

### 5. Trazabilidad y Evidencia
*   Antes de cerrar cualquier tarea técnica, reporta el comando exacto ejecutado en la consola y la salida del test como evidencia empírica de funcionamiento.
*   Cualquier modificación debe quedar debidamente descrita en el archivo [`CHANGELOG.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/CHANGELOG.md).
