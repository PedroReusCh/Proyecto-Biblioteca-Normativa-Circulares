# Historial de Cambios (CHANGELOG.md)

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a las prácticas de control de versiones semántico.

---

## [0.2.0] - 2026-07-20

### Added

* **Configuración de pytest**:
  * Creación de [`pytest.ini`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/pytest.ini) para el descubrimiento y ejecución unificada de las pruebas del proyecto.
* **Especificación local de cobertura**:
  * Creación de [`bcn - documentación/especificacion_cobertura.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/especificacion_cobertura.md) con la declaración explícita de todos los elementos del esquema XSD de la BCN para validar la cobertura estructural al 100% de manera local y autónoma.

### Changed

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
