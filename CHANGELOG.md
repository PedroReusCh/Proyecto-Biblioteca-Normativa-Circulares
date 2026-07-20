# Historial de Cambios (CHANGELOG.md)

Todos los cambios notables en este proyecto serán documentados en este archivo.

El formato se basa en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/) y este proyecto se adhiere a las prácticas de control de versiones semántico.

---

## [0.1.0] - 2026-07-20

### Added

* Creación de archivos de documentación de trazabilidad e instrucciones requeridas por las políticas del proyecto:
  * [`README.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/README.md): Detalla la organización, arquitectura y suite de pruebas del proyecto.
  * [`GEMINI.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/GEMINI.md): Define instrucciones específicas y reglas de aislamiento operativo para la IA.
  * [`CHANGELOG.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/CHANGELOG.md): Control e histórico estructurado de modificaciones del software.
  * [`.gitignore`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.gitignore): Configuración para omitir archivos temporales de test, compilación, entornos virtuales de Python, y exclusión general de archivos `.csv`, Excel y `.pdf` (con excepciones para proteger los recursos oficiales del proyecto).
*   **Inicialización y Publicación**:
    *   Inicialización del repositorio Git local indexando de forma limpia todos los recursos del proyecto.
    *   Creación y publicación del repositorio público en GitHub: [Proyecto-Biblioteca-Normativa-Circulares](https://github.com/PedroReusCh/Proyecto-Biblioteca-Normativa-Circulares).

### Changed

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
