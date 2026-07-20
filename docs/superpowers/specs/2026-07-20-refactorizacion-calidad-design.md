# Especificación de Diseño: Refactorización y Calidad de Código

Este documento describe el diseño técnico aprobado para implementar la refactorización del **Proyecto Biblioteca Normativa Circulares**, elevando el tipado al estándar estricto (strict), estructurando la suite de pruebas e independizando los fallbacks de configuración.

---

## 1. Arquitectura y Mapeo de Tipos Estrictos (`ddu_types.py`)

Se implementará un sistema de tipado estricto utilizando clases basadas en `TypedDict` para estructurar con rigidez las circulares procesadas:

*   **`SeccionDDU`**: Estructura de diccionario que contiene un título de sección y una lista de párrafos de texto.
*   **`DatosCircularDDU`**: Diccionario completo que consolida metadatos (número, fecha, materia, emisor, antecedentes) y la lista de `SeccionDDU`.

### Modificaciones en los Módulos Lógicos:
*   [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py): La firma de `parse_pdf()` se declara con tipo de retorno `DatosCircularDDU`.
*   [`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py): La firma de `generar_xml()` se cambia a `generar_xml(self, datos: DatosCircularDDU) -> str`.
*   [`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py): La firma de `generar_rdf()` se cambia a `generar_rdf(self, datos: DatosCircularDDU) -> str`.

---

## 2. Desacoplamiento de Fallbacks Estáticos

Los metadatos cableados de circulares DDU históricas se independizan en el archivo de datos JSON [`scripts/config/fallbacks_ddu.json`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/config/fallbacks_ddu.json) (ya creado).

*   El constructor de `DDUParser` carga dinámicamente este JSON al inicializarse utilizando `json.load`.
*   Se eliminan todas las asignaciones directas de diccionarios en el código lógico de parser.

---

## 3. Especificación Local de Cobertura Akoma Ntoso

Se crea un documento de diseño de especificación mínimo en formato Markdown en [`bcn - documentación/especificacion_cobertura.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/especificacion_cobertura.md). 

*   Este spec listará los elementos estructurales obligatorios y atributos de Akoma Ntoso BCN procesados en el proyecto.
*   [`test/test_spec_coverage.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_spec_coverage.py) se actualizará para validar la cobertura directamente contra este archivo markdown local del repositorio, garantizando el 100% de cobertura y autonomía.

---

## 4. Estructuración e Integración con `pytest`

La suite de pruebas locales en [`test/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test) se adaptará para admitir descubrimiento por parte de `pytest` manteniendo la capacidad de ejecutarse de forma independiente con Python estándar:

*   Se renombra la función principal de cada script en `test/` (de `main()` a `test_csv_integrity()`, `test_spec_coverage()`, etc.).
*   Se añade la cláusula `if __name__ == '__main__':` en cada script que invoque de forma directa la función de prueba para conservar la ejecución unitaria manual en terminal.
*   Se utiliza el archivo `pytest.ini` en la raíz del repositorio para configurar la ruta de importación de scripts (`pythonpath = scripts`) y que no fallen las dependencias.

---

## 5. Criterios de Aceptación y Éxito
1.  La suite completa de tests de la biblioteca debe pasar con éxito absoluto al ejecutar `pytest` en la raíz.
2.  Cada test debe seguir ejecutándose de forma aislada con `python test/test_*.py`.
3.  El analizador de tipado estricto no debe arrojar errores de consistencia sobre las firmas modificadas.
4.  No se deben incluir archivos `.csv`, `.xlsx` o `.pdf` al control de versiones de Git.
