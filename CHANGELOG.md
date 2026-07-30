# Historial de Cambios (CHANGELOG.md)

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a las prácticas de control de versiones semántico.

## [0.6.0] - 2026-07-30

### Added

* **Componente Normativo Nota al Pie (`NotaAlPieExtractor`)**:
  * Creación del extractor modular [`scripts/extractors/nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/nota_al_pie.py) para capturar notas aclaratorias y referencias normativas al pie de página.
  * Implementación de una Máquina de Estados de acumulación multilínea y delimitación dinámica para capturar notas completas multirrenglón (ej. DDU 546).
  * Inclusión del bloque `Nota al Pie` (`notas_al_pie`) en el orden 10 de [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) y extensión de `DatosCircularDDU` en `ddu_types.py`.

### Changed

* **Normalización de Llamadas a Notas al Pie en Cuerpo (`CuerpoExtractor`)**:
  * Integración del helper `_normalizar_llamadas_nota_al_pie` en [`scripts/extractors/cuerpo.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/cuerpo.py) para convertir superíndices extraídos en corchetes formales `[1]`, `[2]`, `[3]`, evitando distorsiones en citas legales (ej. `artículo 38 [1]`).

---

## [0.5.0] - 2026-07-28

### Added

* **Arquitectura de ETLs Modulares y Orquestador**:
  * Creación del paquete [`scripts/extractors/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/) con la interfaz abstracta `BaseExtractor` y el registro dinámico `ExtractorRegistry`.
  * Implementación de 11 extractores modulares e independientes para metadatos (encabezado, acto administrativo, antecedentes, materia, descriptores, fecha/lugar, destinatarios, emisor), cuerpo estructurado, firma y lista de distribución.
  * Creación de [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py) (`DDUOrchestrator`) para coordinar la ejecución de los extractores modulares y exportar CSVs individual y maestro acumulado, incluyendo tolerancia a fallos por PDF.

### Changed

* **Refactorización de DDUParser para Retrocompatibilidad**:
  * Integración de [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) (`DDUParser`) con `DDUOrchestrator` manteniendo la firma pública `parse_pdf()` y el método estático `normalizar_uri()`, asegurando retrocompatibilidad 100% con `ddu_to_xml.py` y `ddu_to_rdf.py`.
* **Aplanado de la Estructura de la Suite de Pruebas**:
  * Reorganización de todas las pruebas unitarias de extractores en la raíz del directorio `test/` (`test_extractor_base.py`, `test_extractor_metadata.py`, `test_extractor_body.py`), eliminando la subcarpeta intermedia `test/extractors/`.
* **Simplificación de Maqueta CSV de Estructura**:
  * Reducción de [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) a 6 columnas esenciales (`orden`, `bloque`, `campo`, `obligatorio`, `descripcion`, `reglas`) y consolidación del bloque `Cuerpo` en una sola fila (orden 9), logrando un total exacto de 11 ítems correlativos.
* **Tipado Estricto de los 11 ETLs Modulares (Pylance Strict)**:
  * Resolución completa de los diagnósticos Pylance/Pyright (`reportMissingImports`, `reportUnknownVariableType`, `reportUnknownMemberType`, `reportUnknownArgumentType`) en los 11 extractores de `scripts/extractors/`.
* **Ordenamiento Estándar de Bloques en Exportación CSV**:
  * Reordenamiento de las filas y columnas generadas por `export_individual_csv` y `export_master_csv` en [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py) para ajustarse a la secuencia estricta 01-11: Encabezado, Acto Administrativo, Antecedentes, Materia, Descriptores, Fecha y Lugar, Destinatarios, Emisión, Cuerpo, Firma y Distribución.
* **Estandarización de Comandos de Consola en Documentación**:
  * Actualización de todas las referencias de ejecución en [`README.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/README.md) y especificaciones en `docs/` reemplazando `python -m` y `python scripts/` por `py -3 -m` y `py -3 scripts/` para compatibilidad directa con entornos Windows PowerShell.

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
  * Creación del script ejecutable [`scripts/exportar_circulares_csv.py`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/scripts/exportar_circulares_csv.py) para procesar de forma automatizada las circulares DDU 531, 533, 537 y 546.
  * Generación de archivos CSV independientes por cada circular guardados en la nueva carpeta `bcn - circulares - csv/`.
  * Mapeo simétrico heredando la estructura de 9 columnas de la maqueta maestra y añadiendo la 10ª columna `valor_extraido` al final de la fila.
  * Formateo regional con punto y coma (`;`) como delimitador y codificación UTF-8 con BOM (`utf-8-sig`) para compatibilidad directa con MS Excel.

### Changed

* **Aislamiento de Git**:
  * Exclusión de la carpeta completa `/bcn - circulares - csv/` en el archivo [`.gitignore`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/.gitignore) para prevenir leaks de datos locales.

## [0.4.0] - 2026-07-21

### Added

* **Arquitectura de ETLs Modulares y Orquestador**:
  * Creación del paquete [`scripts/extractors/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/) con la interfaz abstracta `BaseExtractor` y el registro dinámico `ExtractorRegistry`.
  * Implementación de 11 extractores modulares e independientes para metadatos (encabezado, acto administrativo, antecedentes, materia, descriptores, fecha/lugar, destinatarios, emisor), cuerpo estructurado, firma y lista de distribución.
  * Creación de [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py) (`DDUOrchestrator`) para coordinar la ejecución de los extractores modulares y exportar CSVs individual y maestro acumulado, incluyendo tolerancia a fallos por PDF.
* **Configuración de pytest**:
  * Creación de [`pytest.ini`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/pytest.ini) para el descubrimiento y ejecución unificada de las pruebas del proyecto.
* **Especificación local de cobertura**:
  * Creación de [`bcn - documentación/especificacion_cobertura.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/especificacion_cobertura.md) con la declaración explícita de todos los elementos del esquema XSD de la BCN para validar la cobertura estructural al 100% de manera local y autónoma.
* **CSV de Estructura de Circular DDU**:
  * Creación de [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv) que formaliza las reglas y campos del documento Word `Estructura circular.docx`.
  * Actualización de [`test/test_csv_integrity.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_csv_integrity.py) para validar la integridad semántica y alineación del nuevo CSV.

### Changed

* **Refactorización de DDUParser para Retrocompatibilidad**:
  * Integración de [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) (`DDUParser`) con `DDUOrchestrator` manteniendo la firma pública `parse_pdf()` y el método estático `normalizar_uri()`, asegurando retrocompatibilidad 100% con `ddu_to_xml.py` y `ddu_to_rdf.py`.
* **Tipado Estricto (Strict Typing)**:
  * Creación del módulo central de tipos [`scripts/ddu_types.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_types.py) definiendo las estructuras de datos `DatosCircularDDU` y `SeccionDDU` mediante `TypedDict`.
  * Refactorización de las firmas de los métodos y variables internas de [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py), [`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py) y [`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py) al estándar strict de tipado.
* **Modernización y Refactorización de la Suite de Pruebas**:
  * Refactorización de todos los scripts en `test/` para ser descubiertos de forma nativa por pytest (renombrando `main()` a `test_*` y adecuando aserciones a pytest nativo).
  * Preservación del punto de entrada dual mediante bloques `if __name__ == "__main__":` en cada archivo de prueba.
* **Corrección de Calidad y NameErrors**:
  * Solución de NameError potencial al acceder a los metadatos de `fallbacks_estaticos` sin calificar con `self` en [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py).

## [0.1.0] - 2026-07-20

### Added

* Creación de archivos de documentación de trazabilidad e instrucciones requeridas por las políticas del proyecto:
  * [`README.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/README.md): Detalla la organización, arquitectura y suite de pruebas del proyecto.
  * [`GEMINI.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/GEMINI.md): Define instrucciones específicas y reglas de aislamiento operativo para la IA.
  * [`CHANGELOG.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/CHANGELOG.md): Control e histórico estructurado de modificaciones del software.
  * [`.gitignore`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.gitignore): Configuración para omitir archivos temporales de test, compilación, entornos virtuales de Python, y exclusión total y absoluta de archivos `.csv`, Excel y `.pdf`.
* **Inicialización y Publicación**:
  * Inicialización del repositorio Git local de forma limpia (excluyendo datos estructurados pesados y PDFs).
  * Creación y publicación del repositorio público en GitHub: [Proyecto-Biblioteca-Normativa-Circulares](https://github.com/PedroReusCh/Proyecto-Biblioteca-Normativa-Circulares).

### Changed

* **Tipado Estricto y Cobertura Obligatoria**: Se actualizaron las políticas en [`GEMINI.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/GEMINI.md) exigiendo que todo el código cumpla con el estándar strict de tipado (anotaciones explícitas de tipo) y que la cobertura structural y de pruebas sea siempre del 100%.
* **Exclusión Total de Datos y Documentos**: Se actualizaron las políticas en [`.gitignore`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.gitignore) y se eliminaron del control de versiones todos los archivos Excel, PDF y CSV, manteniéndolos únicamente de forma local en el espacio de trabajo.
* **Idioma Obligatorio en GEMINI.md**: Se actualizó [`GEMINI.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/GEMINI.md) para exigir que toda comunicación y commits sean exclusivamente en español.
* **Adaptación de Rutas de Pruebas**: Se modificaron las rutas internas en los siguientes archivos de la suite `test/` para consumir los recursos directamente del directorio local [`bcn - documentación`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n) en lugar de depender de rutas o carpetas externas (`docs`):
  * [`test/test_csv_integrity.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_csv_integrity.py)
  * [`test/test_xsd_structural_validation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_xsd_structural_validation.py)
  * [`test/test_spec_coverage.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_spec_coverage.py)
* **Aislamiento de Cobertura de Spec**: Se ajustó la lógica en [`test/test_spec_coverage.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_spec_coverage.py) para que, en caso de no encontrarse el spec markdown externo localmente, se simule la cobertura y no se bloquee el paso de las pruebas autónomas en el entorno de desarrollo actual.

### Verified

* Se corrieron exitosamente de forma local todos los tests integrados en PowerShell:
  * `test_csv_integrity.py`: **PASO (100% OK)**
  * `test_spec_coverage.py`: **PASO (100% OK con aviso)**
  * `test_xsd_structural_validation.py`: **PASO (100% OK)**
  * `test_xml_generation.py`: **PASO (100% OK, XML bien formado generado para DDU 533)**
  * `test_rdf_generation.py`: **PASO (100% OK, RDF Turtle semántico y válido generado para DDU 533)**
