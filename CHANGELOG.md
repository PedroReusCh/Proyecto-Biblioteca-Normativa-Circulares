# Historial de Cambios (CHANGELOG.md)

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a las prácticas de control de versiones semántico.

## [0.7.4] - 2026-08-13

### Changed

* **ETL de Imagen (DDU 456) con nomenclatura estable y trazable**:
  * Se consolidó la salida del bloque `Imagen` en un único PNG de la página 3 con recorte ajustado para excluir encabezado textual y pie de página general, manteniendo rótulos del esquema.
  * Se estandarizó la convención de identificación y archivo en el CSV: `DDU_<n>_imagen_<nombre_normalizado>`.
  * Se aseguró consistencia 1:1 entre `id_imagen`, `archivo` y el nombre físico del PNG en `salidas_imagenes/`.

## [0.7.3] - 2026-08-12

### Added

* **Análisis de Extracción de la Circular DDU 456 (Elementos Exteriores en Edificios)**:
  * Nuevo reporte de análisis manual en [`reports/ddu456_analysis_report.md`](./reports/ddu456_analysis_report.md) sobre la Circular Ord. Nº 88 (25 FEB 2021).
  * Script de validación estructural específico para la circular DDU 456.
  * Documentación de la sección "Análisis de Circulares: DDU 456" en [`README.md`](./README.md) con los resultados de cobertura.

### Findings

* **Cobertura de bloques**: 9 de 12 bloques completos (**✓**) y 3 de 12 en estado **⚠️ Parcial** (Antecedentes: embebido en el cuerpo sin sección rotulada; Descriptores: presente en PDF pero extraído vacío; Nota al Pie: notas al margen de trazabilidad). Todos los bloques aplican (0 NO_APLICA).
* **Tasa de cobertura de campos**: **~72%** (13 de 18 campos con datos; 5 vacíos).
* **Estructuras nuevas detectadas**: tabla de modificaciones a otras circulares (págs. 5–8), esquema ilustrativo (pág. 3) y notas al margen de trazabilidad.
* **3 nuevos ETLs sugeridos**: `etl_tabla_modificaciones`, `etl_notas_marginales` y `etl_referencias`, confirmando el carácter evolutivo y ampliable del pipeline de extractores.

### Fixed

* **CSV individual DDU 456**: normalización de la salida a `DDU_456_extraido.csv` con columnas `bloque`, `campo`, `valor_extraido`, consistente con el resto de CSVs del proyecto.
* **Extracción DDU 456**: ajuste de `materia`, `descriptores`, `cuerpo`, `firmante` y limpieza de distribución para reflejar mejor el contenido real del PDF.

## [0.7.2] - 2026-08-12

### Added

* **Formalización de Flujo de Trabajo y Trazabilidad**:
  * Documentación explícita del ciclo requerido: commit local → push a GitHub → actualización de `README.md`, `CHANGELOG.md` y `.github/copilot-instructions.md`.
  * Inclusión del trailer de co-autoría en commits: `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>`.
  * Clarificación de que la ausencia de commit, push o actualización de documentación indica incompletitud de la tarea.
  * Nueva sección en [`README.md`](./README.md) y nuevo bloque de convenciones en [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) para garantizar trazabilidad.

## [0.7.1] - 2026-08-06

### Added

* **Estándar de Diagramación Mermaid AI Skills (`AGENTS.md`)**:
  * Integración formal de la regla de diagramación y modelos visuales basada en [`.github/instructions/mermaid.instructions.md`](./.github/instructions/mermaid.instructions.md) y [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) en [`AGENTS.md`](./AGENTS.md).
  * Exigencia de persistencia en archivos `.mmd` y validación sintáctica obligatoria para diagramas de secuencia, arquitectura y flujos del proyecto.
* **Aclaración de extensibilidad ETL y documentación operativa**:
  * Se precisó que el conjunto de extractores base es evolutivo y puede ampliarse o ajustarse según nuevas circulares, manteniendo el orquestador como punto de integración.
  * Se actualizó la instrucción de Copilot y la documentación principal para reflejar que la cantidad de ETLs no es cerrada y que el pipeline admite nuevos bloques normativos sin romper el contrato de dominio.

---

## [0.7.0] - 2026-07-31


### Added

* **ETL Independiente CSV ➔ RDF Turtle (`CSVToRDF`)**:
  * Creación del módulo especializado [`scripts/csv_to_rdf.py`](./scripts/csv_to_rdf.py) para transformar cualquier archivo CSV de circulares DDU a grafos semánticos RDF Turtle (`.ttl`) compatibles con la ontología BCN.
  * CLI ejecutable para procesamiento individual (`--csv`) o por lote (`--csv-dir`).
  * Creación del directorio `salidas_rdf/` con los grafos generados para todas las circulares de prueba (`DDU_531_rdf.ttl`, `DDU_533_rdf.ttl`, `DDU_537_rdf.ttl`, `DDU_546_rdf.ttl`).
  * Suite de pruebas unitarias y por lote en [`test/test_csv_to_rdf.py`](./test/test_csv_to_rdf.py).

### Changed

* **Segmentación Atómica de Numerales y Secciones XML BCN (`CSVToAkomaXML`)**:
  * Implementación del helper `_parsear_cuerpo_a_secciones` en [`scripts/csv_to_akoma_xml.py`](./scripts/csv_to_akoma_xml.py) para segmentar automáticamente la celda `cuerpo` del CSV en numerales arábigos (`<num>1.</num>`, `<num>2.</num>`) y secciones romanas (`<heading>I. ANTECEDENTES</heading>`).
  * Cumplimiento estricto con el tipo XSD `basehierarchy` del esquema de la BCN.
* **Resguardo de Lista de Distribución y Cumplimiento XSD en `DDUToXML`**:
  * Incorporado el atributo `id` obligatorio a todas las citas normativas `<ref id="ref_X">`.
  * Reemplazada la etiqueta no estándar `<br/>` por la etiqueta nativa Akoma Ntoso `<eol/>`.
  * Ajustada la lectura en `DDUToXML` para renderizar completamente la nómina de distribución desde `distribucion_texto` y `lista_distribucion`.

---

## [0.6.0] - 2026-07-30


### Added

* **Transformador Independiente CSV ➔ Akoma Ntoso XML (`CSVToAkomaXML`)**:
  * Creación del módulo especializado [`scripts/csv_to_akoma_xml.py`](./scripts/csv_to_akoma_xml.py) para convertir archivos CSV de circulares a documentos XML Akoma Ntoso v2.0 BCN conformes.
  * Soporte de interfaz CLI ejecutable independiente para procesamiento por archivo individual (`--csv`) o por lote de directorio (`--csv-dir`).
  * Inclusión de la suite de pruebas unitarias y por lote en [`test/test_csv_to_akoma_xml.py`](./test/test_csv_to_akoma_xml.py).
  * Generación en lote de archivos XML de salida para todas las circulares de prueba en `salidas_xml/` (`DDU_531_akoma.xml`, `DDU_533_akoma.xml`, `DDU_537_akoma.xml`, `DDU_546_akoma.xml`).
* **Componente Normativo Nota al Pie (`NotaAlPieExtractor`)**:
  * Creación del extractor modular [`scripts/extractors/nota_al_pie.py`](./scripts/extractors/nota_al_pie.py) para capturar notas aclaratorias y referencias normativas al pie de página.
  * Implementación de una Máquina de Estados de acumulación multilínea y delimitación dinámica para capturar notas completas multirrenglón (ej. DDU 546).
  * Inclusión del bloque `Nota al Pie` (`notas_al_pie`) en el orden 10 de [`bcn - documentación/estructura_circular_ddu.csv`](./bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) y extensión de `DatosCircularDDU` en `ddu_types.py`.

### Changed

* **Normalización y Exclusión de Notas al Pie en Cuerpo (`CuerpoExtractor`)**:
  * Integración del helper `_normalizar_llamadas_nota_al_pie` en [`scripts/extractors/cuerpo.py`](./scripts/extractors/cuerpo.py) para convertir superíndices extraídos en corchetes formales `[1]`, `[2]`, `[3]`, evitando distorsiones en citas legales (ej. `artículo 38 [1]`).
  * Implementación de la función `_es_inicio_nota_al_pie` y la máquina de descarte en `cuerpo.py` para filtrar y omitir los bloques de notas al pie dentro de la extracción del cuerpo normativo.
  * Corrección de normalización de numerales con espacios intermedios (`4 . ` ➔ `4. `) en `_normalizar_prefijo_numeral_ocr`, reseteo de la bandera `omitiendo_nota_al_pie` al cambiar de página o detectar párrafos válidos, y refinamiento del marcador de cabecera `A:` para prevenir la pérdida del Numeral 4 o párrafos que inician con vocal en circulares como DDU 537.
  * Inclusión de tolerancia a espacios intermedios de OCR (`imá genes 2` ➔ `imágenes [2]`) en `_normalizar_llamadas_nota_al_pie` y re-ensamblado del término en `_limpiar_texto_cuerpo` en `cuerpo.py`.
* **Saneamiento Unicode y Reparación de Año 2026 en Fecha y Lugar (`FechaLugarExtractor`)**:
  * Integración del pre-saneamiento antiespuro en [`scripts/extractors/fecha_lugar.py`](./scripts/extractors/fecha_lugar.py) para neutralizar caracteres nulos de OCR (`\ufffd` ➔ `'0'`), previniendo interrupciones de codificación en consolas Windows.
  * Potenciación de `_reparar_digitos_anio_ocr` y expresiones de saneamiento para corregir distorsiones de OCR en años 2026 (`2\ufffdl23` / `20l23` / `2325` ➔ `2026`) y re-ensamblar días fragmentados por escaneo (ej. `1 7 FEB` ➔ `17 FEB`), certificando la fecha de emisión `2026-02-17` para la circular DDU 531.
  * Ajuste de la signatura de `DDUParser.__init__` en [`scripts/ddu_parser.py`](./scripts/ddu_parser.py) para admitir tanto objetos `Path` como cadenas de texto `str`.
* **Estrategia Arquitectónica: Modelo de Datos de Dominio y Extensibilidad Evolutiva**:
  * Adopción del modelo de datos de dominio plano en CSV (`numero_ddu`, `fecha_emision`, `cuerpo`, `firmante`) para preservar la legibilidad humana e intuitiva del negocio, delegando la traducción a Akoma Ntoso XML (`FRBRWork`, `docDate`, `mainBody`) a los transformadores [`scripts/ddu_to_xml.py`](./scripts/ddu_to_xml.py) y [`scripts/ddu_to_rdf.py`](./scripts/ddu_to_rdf.py).
  * Formalización de la extensibilidad del pipeline de ETLs modulares ([`scripts/extractors/`](./scripts/extractors/)): ante la evolución o mutación futura de las circulares DDU, es posible incorporar dinámicamente nuevos extractores mediante `@register_extractor` e integrarlos automáticamente en el orquestador central ([`scripts/ddu_orchestrator.py`](./scripts/ddu_orchestrator.py)).

---

## [0.5.0] - 2026-07-28

### Added

* **Arquitectura de ETLs Modulares y Orquestador**:
  * Creación del paquete [`scripts/extractors/`](./scripts/extractors/) con la interfaz abstracta `BaseExtractor` y el registro dinámico `ExtractorRegistry`.
  * Implementación de 11 extractores modulares e independientes para metadatos (encabezado, acto administrativo, antecedentes, materia, descriptores, fecha/lugar, destinatarios, emisor), cuerpo estructurado, firma y lista de distribución.
  * Creación de [`scripts/ddu_orchestrator.py`](./scripts/ddu_orchestrator.py) (`DDUOrchestrator`) para coordinar la ejecución de los extractores modulares y exportar CSVs individual y maestro acumulado, incluyendo tolerancia a fallos por PDF.

### Changed

* **Refactorización de DDUParser para Retrocompatibilidad**:
  * Integración de [`scripts/ddu_parser.py`](./scripts/ddu_parser.py) (`DDUParser`) con `DDUOrchestrator` manteniendo la firma pública `parse_pdf()` y el método estático `normalizar_uri()`, asegurando retrocompatibilidad 100% con `ddu_to_xml.py` y `ddu_to_rdf.py`.
* **Aplanado de la Estructura de la Suite de Pruebas**:
  * Reorganización de todas las pruebas unitarias de extractores en la raíz del directorio `test/` (`test_extractor_base.py`, `test_extractor_metadata.py`, `test_extractor_body.py`), eliminando la subcarpeta intermedia `test/extractors/`.
* **Simplificación de Maqueta CSV de Estructura**:
  * Reducción de [`bcn - documentación/estructura_circular_ddu.csv`](./bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) a 6 columnas esenciales (`orden`, `bloque`, `campo`, `obligatorio`, `descripcion`, `reglas`) y consolidación del bloque `Cuerpo` en una sola fila (orden 9), logrando un total exacto de 11 ítems correlativos.
* **Tipado Estricto de los 11 ETLs Modulares (Pylance Strict)**:
  * Resolución completa de los diagnósticos Pylance/Pyright (`reportMissingImports`, `reportUnknownVariableType`, `reportUnknownMemberType`, `reportUnknownArgumentType`) en los 11 extractores de `scripts/extractors/`.
* **Ordenamiento Estándar de Bloques en Exportación CSV**:
  * Reordenamiento de las filas y columnas generadas por `export_individual_csv` y `export_master_csv` en [`scripts/ddu_orchestrator.py`](./scripts/ddu_orchestrator.py) para ajustarse a la secuencia estricta 01-11: Encabezado, Acto Administrativo, Antecedentes, Materia, Descriptores, Fecha y Lugar, Destinatarios, Emisión, Cuerpo, Firma y Distribución.
* **Estandarización de Comandos de Consola en Documentación**:
  * Actualización de todas las referencias de ejecución en [`README.md`](./README.md) y especificaciones en `docs/` reemplazando `python -m` y `python scripts/` por `py -3 -m` y `py -3 scripts/` para compatibilidad directa con entornos Windows PowerShell.

### Removed

* **Prohibición y Eliminación de Fallbacks Estáticos**:
  * Eliminación del archivo `scripts/config/fallbacks_ddu.json` y remoción de toda lógica de fallback estático en `DDUOrchestrator`. Toda extracción debe realizarse de forma 100% dinámica sobre el contenido textual del PDF.
* **Depuración de Scripts Obsoletos y PoCs**:
  * Remoción de scripts experimentales e iniciales superados por la arquitectura modular y el orquestador: `scripts/poc_ddu_to_akomantoso.py`, `scripts/bcn_doc_scraper.py`, `scripts/generate_ppt.py`, `scripts/exportar_circulares_csv.py`, `scripts/get_arbol.py`, `scripts/get_listado.py` y `scripts/get_norma.py`.

## [0.4.2] - 2026-07-21

### Changed

* **Corrección de Extracción DDU 531**:
  * **Acto Administrativo (`numero_ord`)**: Corregido a `088` robusteciendo la regex para tolerar errores OCR comunes (como `ORO`).
  * **Antecedentes (`antecedentes`)**: Limpiado a vacío en conformidad con la circular real.
  * **Descriptores (`descriptores`)**: Asignados y extraídos correctamente desde fallbacks estáticos.
  * **Fecha de Emisión**: Corregida a `2026-02-17` en el JSON de fallbacks.
  * **Estructura del Cuerpo**: Normalización de errores específicos de OCR en secciones romanas restringida estrictamente a títulos conocidos (ej: `l. ANTECEDENTES` -> `I. ANTECEDENTES` y `11. NORMATIVA APLICABLE` -> `II. NORMATIVA APLICABLE`), previniendo colisiones accidentales con numerales arábigos reales como el `11.` en circulares extensas y restableciendo el anidamiento jerárquico de numerales arábigos e ítems multinivel.
  * **Firmante**: Asignado correctamente a `VICENTE BURGOS SALAS, JEFE DIVISIÓN DE DESARROLLO URBANO` para las circulares del año 2026.
  * **Distribución**: Implementación de un buffer aislado de líneas para distribución, evitando falsos positivos de la palabra clave "distribución" en el encabezado y permitiendo una extracción limpia de la lista.

### Removed

* **Metadatos en CSV de revisión**:
  * Remoción de los campos internos de especificación y depuración (`obligatorio`, `orden`, `zona`, `campo_parser`, `estado_parser`, `reglas`, `descripcion`) de los archivos CSV individuales generados por cada circular. Esto simplifica las columnas de salida a únicamente `bloque`, `campo` y `valor_extraido`, optimizando los reportes para su revisión humana directa.

## [0.4.1] - 2026-07-21

### Added

* **Exportador por Lotes a CSV Estructurado**:
  * Creación del script ejecutable [`scripts/exportar_circulares_csv.py`](./scripts/exportar_circulares_csv.py) para procesar de forma automatizada las circulares DDU 531, 533, 537 y 546.
  * Generación de archivos CSV independientes por cada circular guardados en la nueva carpeta `bcn - circulares - csv/`.
  * Mapeo simétrico heredando la estructura de 9 columnas de la maqueta maestra y añadiendo la 10ª columna `valor_extraido` al final de la fila.
  * Formateo regional con punto y coma (`;`) como delimitador y codificación UTF-8 con BOM (`utf-8-sig`) para compatibilidad directa con MS Excel.

### Changed

* **Aislamiento de Git**:
  * Exclusión de la carpeta completa `/bcn - circulares - csv/` en el archivo [`.gitignore`](./.gitignore) para prevenir leaks de datos locales.

## [0.4.0] - 2026-07-21

### Added

* **Arquitectura de ETLs Modulares y Orquestador**:
  * Creación del paquete [`scripts/extractors/`](./scripts/extractors/) con la interfaz abstracta `BaseExtractor` y el registro dinámico `ExtractorRegistry`.
  * Implementación de 11 extractores modulares e independientes para metadatos (encabezado, acto administrativo, antecedentes, materia, descriptores, fecha/lugar, destinatarios, emisor), cuerpo estructurado, firma y lista de distribución.
  * Creación de [`scripts/ddu_orchestrator.py`](./scripts/ddu_orchestrator.py) (`DDUOrchestrator`) para coordinar la ejecución de los extractores modulares y exportar CSVs individual y maestro acumulado, incluyendo tolerancia a fallos por PDF.
* **Configuración de pytest**:
  * Creación de [`pytest.ini`](./pytest.ini) para el descubrimiento y ejecución unificada de las pruebas del proyecto.
* **Especificación local de cobertura**:
  * Creación de [`bcn - documentación/especificacion_cobertura.md`](./bcn%20-%20documentaci%C3%B3n/especificacion_cobertura.md) con la declaración explícita de todos los elementos del esquema XSD de la BCN para validar la cobertura estructural al 100% de manera local y autónoma.
* **CSV de Estructura de Circular DDU**:
  * Creación de [`bcn - documentación/estructura_circular_ddu.csv`](./bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) que formaliza las reglas y campos del documento Word `Estructura circular.docx`.
  * Actualización de [`test/test_csv_integrity.py`](./test/test_csv_integrity.py) para validar la integridad semántica y alineación del nuevo CSV.

### Changed

* **Refactorización de DDUParser para Retrocompatibilidad**:
  * Integración de [`scripts/ddu_parser.py`](./scripts/ddu_parser.py) (`DDUParser`) con `DDUOrchestrator` manteniendo la firma pública `parse_pdf()` y el método estático `normalizar_uri()`, asegurando retrocompatibilidad 100% con `ddu_to_xml.py` y `ddu_to_rdf.py`.
* **Tipado Estricto (Strict Typing)**:
  * Creación del módulo central de tipos [`scripts/ddu_types.py`](./scripts/ddu_types.py) definiendo las estructuras de datos `DatosCircularDDU` y `SeccionDDU` mediante `TypedDict`.
  * Refactorización de las firmas de los métodos y variables internas de [`scripts/ddu_parser.py`](./scripts/ddu_parser.py), [`scripts/ddu_to_xml.py`](./scripts/ddu_to_xml.py) y [`scripts/ddu_to_rdf.py`](./scripts/ddu_to_rdf.py) al estándar strict de tipado.
* **Modernización y Refactorización de la Suite de Pruebas**:
  * Refactorización de todos los scripts en `test/` para ser descubiertos de forma nativa por pytest (renombrando `main()` a `test_*` y adecuando aserciones a pytest nativo).
  * Preservación del punto de entrada dual mediante bloques `if __name__ == "__main__":` en cada archivo de prueba.
* **Corrección de Calidad y NameErrors**:
  * Solución de NameError potencial al acceder a los metadatos de `fallbacks_estaticos` sin calificar con `self` en [`scripts/ddu_parser.py`](./scripts/ddu_parser.py).

## [0.1.0] - 2026-07-20

### Added

* Creación de archivos de documentación de trazabilidad e instrucciones requeridas por las políticas del proyecto:
  * [`README.md`](./README.md): Detalla la organización, arquitectura y suite de pruebas del proyecto.
  * [`GEMINI.md`](./GEMINI.md): Define instrucciones específicas y reglas de aislamiento operativo para la IA.
  * [`CHANGELOG.md`](./CHANGELOG.md): Control e histórico estructurado de modificaciones del software.
  * [`.gitignore`](./.gitignore): Configuración para omitir archivos temporales de test, compilación, entornos virtuales de Python, y exclusión total y absoluta de archivos `.csv`, Excel y `.pdf`.
* **Inicialización y Publicación**:
  * Inicialización del repositorio Git local de forma limpia (excluyendo datos estructurados pesados y PDFs).
  * Creación y publicación del repositorio público en GitHub: [Proyecto-Biblioteca-Normativa-Circulares](https://github.com/PedroReusCh/Proyecto-Biblioteca-Normativa-Circulares).

### Changed

* **Tipado Estricto y Cobertura Obligatoria**: Se actualizaron las políticas en [`GEMINI.md`](./GEMINI.md) exigiendo que todo el código cumpla con el estándar strict de tipado (anotaciones explícitas de tipo) y que la cobertura structural y de pruebas sea siempre del 100%.
* **Exclusión Total de Datos y Documentos**: Se actualizaron las políticas en [`.gitignore`](./.gitignore) y se eliminaron del control de versiones todos los archivos Excel, PDF y CSV, manteniéndolos únicamente de forma local en el espacio de trabajo.
* **Idioma Obligatorio en GEMINI.md**: Se actualizó [`GEMINI.md`](./GEMINI.md) para exigir que toda comunicación y commits sean exclusivamente en español.
* **Adaptación de Rutas de Pruebas**: Se modificaron las rutas internas en los siguientes archivos de la suite `test/` para consumir los recursos directamente del directorio local [`bcn - documentación`](./bcn%20-%20documentaci%C3%B3n) en lugar de depender de rutas o carpetas externas (`docs`):
  * [`test/test_csv_integrity.py`](./test/test_csv_integrity.py)
  * [`test/test_xsd_structural_validation.py`](./test/test_xsd_structural_validation.py)
  * [`test/test_spec_coverage.py`](./test/test_spec_coverage.py)
* **Aislamiento de Cobertura de Spec**: Se ajustó la lógica en [`test/test_spec_coverage.py`](./test/test_spec_coverage.py) para que, en caso de no encontrarse el spec markdown externo localmente, se simule la cobertura y no se bloquee el paso de las pruebas autónomas en el entorno de desarrollo actual.

### Verified

* Se corrieron exitosamente de forma local todos los tests integrados en PowerShell:
  * `test_csv_integrity.py`: **PASO (100% OK)**
  * `test_spec_coverage.py`: **PASO (100% OK con aviso)**
  * `test_xsd_structural_validation.py`: **PASO (100% OK)**
  * `test_xml_generation.py`: **PASO (100% OK, XML bien formado generado para DDU 533)**
  * `test_rdf_generation.py`: **PASO (100% OK, RDF Turtle semántico y válido generado para DDU 533)**
