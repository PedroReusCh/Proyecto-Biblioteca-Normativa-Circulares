# Especificación de Diseño: Exportación de Circulares a CSV Estructurado

Esta especificación detalla el diseño técnico para implementar un exportador por lotes que procesa circulares DDU en formato PDF y genera archivos CSV individuales por cada circular que reflejan la estructura de datos extraída y normalizada según la maqueta de especificación.

---

## 1. Requerimientos de la Prueba de Concepto

*   **Entradas**: Las circulares PDF ubicadas localmente en `circulares/`:
    *   `DDU 531.pdf`
    *   `DDU 533.pdf`
    *   `DDU 537.pdf`
    *   `DDU 546.pdf`
*   **Salidas**: Un archivo CSV por cada circular guardado en la carpeta `/bcn - circulares - csv/` de la raíz del proyecto.
*   **Aislamiento Git**: Excluir la carpeta de salida completa de Git mediante `.gitignore`.
*   **Formato de Salida**: Cada archivo CSV debe reflejar la estructura de la maqueta maestra agregando una 10ª columna al final para el contenido. Utilizará el **punto y coma (`;`) como delimitador de campos** para facilitar su apertura en Excel. Tendrá exactamente 10 columnas:
    1.  `bloque`: El nombre del bloque (ej. Encabezado, Cuerpo, etc.).
    2.  `campo`: El identificador de campo de la maqueta.
    3.  `obligatorio`: Si el campo es requerido o no.
    4.  `orden`: Número correlativo de secuencia.
    5.  `zona`: Ubicación lógica (encabezado, cuerpo, cierre).
    6.  `campo_parser`: Nombre de la variable mapeada en el parser.
    7.  `estado_parser`: Estado de soporte en el parser (ej. implementado).
    8.  `reglas`: Regla de validación o normalización del campo.
    9.  `descripcion`: Detalle informativo de qué representa el campo.
    10. `valor_extraido`: El texto extraído o estructurado real por el parser para esa circular.

---

## 2. Arquitectura de Datos y Flujo de Mapeo

El exportador cargará la plantilla base de [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/bcn%20-%20documentación/estructura_circular_ddu.csv) para usarla como molde y consumirá `DDUParser` de `scripts/ddu_parser.py` para extraer los datos estructurados.

Para cada fila de la plantilla maestra, el script resolverá su valor correspondiente del diccionario `DatosCircularDDU` y escribirá una fila en el CSV de salida copiando todos los metadatos de la maqueta base y poblando la columna `valor_extraido`:

*   **Campos de Registro Único (Encabezado y Cierre)**: Mapeo directo uno a uno de la variable del parser al campo correspondiente.
*   **Campos de Registro Múltiple (Cuerpo)**:
    Dado que las circulares poseen múltiples secciones, numerales y listas anidadas, el script iterará secuencialmente por el cuerpo:
    *   Si detecta una sección con número romano, generará una fila del tipo `seccion_romana` con el título romano en `valor_extraido`.
    *   Para cada párrafo de la sección, generará una fila del tipo `numeral_arabigo` con el contenido del párrafo.
    *   Si el párrafo posee un subtítulo, generará inmediatamente una fila del tipo `subtitulo_numeral` con el subtítulo extraído.
    *   Si posee listas anidadas, generará para cada una de ellas una fila del tipo `lista_multinivel` con el contenido del sub-ítem.
    *   Al final del cuerpo, generará una fila del tipo `referencia_cruzada` con todas las referencias recolectadas y una fila del tipo `tabla_imagen` con los elementos visuales detectados.

---

## 3. Implementación del Script `scripts/exportar_circulares_csv.py`

Se creará un script autónomo que realice los siguientes pasos:
1.  Importar las librerías necesarias (`csv`, `re`, `os`, `pathlib`) y la clase `DDUParser`.
2.  Garantizar la existencia del directorio de salida `/bcn - circulares - csv/`.
3.  Definir la lista de PDFs de entrada.
4.  Para cada PDF, invocar `parse_pdf()` y procesar los metadatos y secciones para escribir el archivo CSV de salida correspondiente con codificación UTF-8 y saltos de línea correctos.
5.  Imprimir en consola el reporte del estado del procesamiento para retroalimentación visual del usuario.

---

## 4. Plan de Validación y Pruebas

1.  **Ejecución**: Correr el script mediante:
    ```powershell
    python scripts/exportar_circulares_csv.py
    ```
2.  **Verificación**:
    *   Comprobar que se crearon los 4 archivos CSV en `/bcn - circulares - csv/`.
    *   Inspeccionar los CSVs y verificar que posean las 4 columnas requeridas.
    *   Asegurar que todas las pruebas existentes de `pytest` continúan pasando sin regresiones.
