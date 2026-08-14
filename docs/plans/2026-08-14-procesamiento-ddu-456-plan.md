# Plan de Implementación: Procesamiento Integral de la Circular DDU 456

**Fecha**: 2026-08-14  
**Rama**: `feature/ddu-456`  
**Objetivo**: Procesar la circular `circulares/DDU 456.pdf` (9 páginas, año 2021) generando sus representaciones completas en **CSV de Dominio**, **XML Akoma Ntoso v2.0 BCN** y **Grafo Semántico RDF Turtle**, garantizando el 100% de cobertura en la suite de pruebas automatizadas y tipado estricto.

---

### Tareas y Fases de Implementación

#### Tarea 1: Pruebas Unitarias TDD para DDU 456
- **Archivos involucrados**:
  - `test/test_extractor_metadata.py`
  - `test/test_extractor_body.py`
- **Acciones**:
  - Añadir pruebas para validar la extracción de metadatos de DDU 456 (`numero_ord` = 88, `fecha` = 2021-02-25, 34 destinatarios).
  - Añadir pruebas para la extracción de firma evitando la captura de textos residuales de tablas (`Motivo y/o Consideraciones`).

#### Tarea 2: Refinamiento de Extractores (`scripts/extractors/firma.py`)
- **Archivos involucrados**:
  - `scripts/extractors/firma.py`
- **Acciones**:
  - Ajustar las expresiones regulares y heurísticas de descarte para evitar falsos positivos con encabezados de tablas de modificaciones previas a la firma.

#### Tarea 3: Generación del CSV de Dominio (`salidas_csv/DDU_456_extraido.csv`)
- **Archivos involucrados**:
  - `scripts/ddu_orchestrator.py`
  - `salidas_csv/DDU_456_extraido.csv`
- **Acciones**:
  - Ejecutar `ddu_orchestrator.py` sobre `circulares/DDU 456.pdf`.
  - Validar los 12 bloques normativos en `DDU_456_extraido.csv`.

#### Tarea 4: Generación de XML Akoma Ntoso v2.0 BCN (`salidas_xml/DDU_456_akoma.xml`)
- **Archivos involucrados**:
  - `scripts/csv_to_akoma_xml.py`
  - `salidas_xml/DDU_456_akoma.xml`
- **Acciones**:
  - Convertir el CSV generado a XML Akoma Ntoso.
  - Verificar la segmentación atómica de los 7 numerales (`<num>1.</num>` a `<num>7.</num>`) y las citas a la OGUC/LGUC.

#### Tarea 5: Generación del Grafo Semántico RDF Turtle (`salidas_rdf/DDU_456_rdf.ttl`)
- **Archivos involucrados**:
  - `scripts/csv_to_rdf.py`
  - `salidas_rdf/DDU_456_rdf.ttl`
- **Acciones**:
  - Convertir el CSV a formato Turtle RDF.
  - Verificar la coherencia sintáctica y las relaciones ontológicas.

#### Tarea 6: Verificación y Certificación de Suite de Pruebas
- **Acciones**:
  - Ejecutar `pytest -v` y validar el 100% de éxito de todas las pruebas.
  - Registrar los avances en `docs/plans/task.md` y documentar cambios.
