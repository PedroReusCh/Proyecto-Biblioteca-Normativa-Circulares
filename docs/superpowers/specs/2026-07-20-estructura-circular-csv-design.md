# Especificación de Diseño: Estructura Circular DDU a CSV

Esta especificación detalla el diseño, la estructura y las reglas de negocio para modelar el documento Word `Estructura circular.docx` en un archivo estructurado CSV de referencia local, su validación y la futura integración con el parser.

---

## 1. Archivo CSV de Referencia: `estructura_circular_ddu.csv`
El archivo se creará en el directorio [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv). 

### Columnas y Contrato del CSV
1. **bloque**: Agrupación física del documento (`Encabezado`, `Cuerpo`, `Firma`, `Distribución`, etc.).
2. **campo**: Identificador técnico del elemento (ej. `numero_ddu`, `materia`, `referencia_cruzada`).
3. **tipo_dato**: Naturaleza del dato (`metadato`, `estructura`, `contenido`, `referencia`).
4. **obligatorio**: Si debe aparecer siempre en cada circular (`si` / `no`).
5. **patron_regex**: Expresión regular sugerida para su identificación en texto plano.
6. **orden**: Secuencia típica de aparición (1 a 15).
7. **zona**: Sección lógica del documento (`encabezado`, `cuerpo`, `cierre`).
8. **campo_parser**: Nombre de la variable mapeada en `DatosCircularDDU` si existe.
9. **estado_parser**: Estado de desarrollo del soporte en el parser (`implementado`, `pendiente`, `no_relevante`, `parcial`).
10. **reglas**: Lógica y restricciones descritas en el documento Word.
11. **descripcion**: Explicación funcional del elemento.
12. **ejemplo**: Fragmento de ejemplo extraído directamente del documento Word.

---

## 2. Plan de Pruebas e Integración
Una vez creado el archivo CSV:
*   Se actualizará el test de integridad [`test/test_csv_integrity.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_csv_integrity.py) para validar la coherencia columnar del nuevo CSV.
*   En la fase de implementación posterior, se diseñará un test estructural que cargue este CSV y valide que las circulares procesadas por el parser contengan al menos los bloques marcados como `implementado` y `obligatorio: si`.

---

## 3. Auto-Evaluación (Self-Review)
*   **Placeholders**: Ninguno. Todos los 15 elementos identificados del Word y del parser han sido mapeados.
*   **Consistencia**: El orden coincide con el flujo secuencial del parser. Las regex propuestas son compatibles con Python.
*   **Aislamiento**: El CSV reside completamente dentro de [`bcn - documentación/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n), sin generar dependencias con librerías externas o rutas absolutas de desarrollo ajenas.
