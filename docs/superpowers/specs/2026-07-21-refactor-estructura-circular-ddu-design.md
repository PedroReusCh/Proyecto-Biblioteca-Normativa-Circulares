# Especificación de Diseño: Refactorización de Estructura Circular DDU (Maqueta DDU 533)

Esta especificación detalla el diseño y los cambios necesarios para alinear el archivo [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/bcn%20-%20documentación/estructura_circular_ddu.csv) como una maqueta exacta de la circular **DDU 533**, incorporando subtítulos de numerales y marcando adecuadamente los elementos no aplicables a esta circular.

---

## 1. Cambios Propuestos en el CSV

Se aplicarán las siguientes modificaciones y adiciones de registros al archivo CSV de 12 columnas:

### 1.1 Encabezado, Acto Administrativo y Emisión
Se actualizan tanto la expresión regular como el ejemplo con los valores limpios y exactos de la circular DDU 533:
*   **Encabezado**:
    *   `patron_regex`: `533`
    *   `ejemplo`: `533`
*   **Acto Administrativo**:
    *   `patron_regex`: `112`
    *   `ejemplo`: `112`
*   **Emisión**:
    *   `patron_regex`: `JEFE DIVISION DE DESARROLLO URBANO.`
    *   `ejemplo`: `JEFE DIVISION DE DESARROLLO URBANO.`

### 1.2 Campos No Aplicables a DDU 533
Para reflejar que ciertos elementos de la estructura general no se encuentran en la circular maqueta DDU 533, se modifican las filas correspondientes dejando su regex y ejemplo vacíos, y estableciendo su estado y reglas informativas:
*   **Cuerpo (`seccion_romana`)**:
    *   `patron_regex`: *vacío*
    *   `ejemplo`: *vacío*
    *   `estado_parser`: `no_aplica_ddu_533`
    *   `reglas`: `No aplicable a la circular maqueta DDU 533`
*   **Cuerpo (`referencia_cruzada`)**:
    *   `patron_regex`: *vacío*
    *   `ejemplo`: *vacío*
    *   `estado_parser`: `no_aplica_ddu_533`
    *   `reglas`: `No aplicable a la circular maqueta DDU 533`
*   **Cuerpo (`tabla_imagen`)**:
    *   `patron_regex`: *vacío*
    *   `ejemplo`: *vacío*
    *   `estado_parser`: `no_aplica_ddu_533`
    *   `reglas`: `No aplicable a la circular maqueta DDU 533`

### 1.3 Numerales y Nuevos Elementos
*   **Cuerpo (`numeral_arabigo`)**:
    *   `ejemplo`: Se incluye el contenido textual completo del numeral 1: `"1. De conformidad con lo previsto en el artículo 4° de la Ley General de Urbanismo y Construcciones (LGUC), corresponde a esta División interpretar las disposiciones de la dicha Ley y su Ordenanza General mediante circulares que quedarán a disposición de cualquier interesado, y en atención a diversas consultas recibidas relativas a la extensión extraordinaria de vigencia de permisos de construcción establecida por el D.S. Nº33 (V. y U.) de 2024 (en adelante DS 33), se imparten las siguientes instrucciones para uniformar su aplicación."`
*   **Adición de Fila (`subtitulo_numeral`)**:
    *   `bloque`: `Cuerpo`
    *   `campo`: `subtitulo_numeral`
    *   `tipo_dato`: `estructura`
    *   `obligatorio`: `no`
    *   `patron_regex`: `"^([A-ZÁÉÍÓÚÑ\s\d\"()]+[:.])"`
    *   `orden`: `11`
    *   `zona`: `cuerpo`
    *   `campo_parser`: *vacío*
    *   `estado_parser`: `pendiente`
    *   `reglas`: `Subtítulo en mayúsculas dentro del numeral`
    *   `descripcion`: `Subtítulo de sección dentro del numeral arábigo`
    *   `ejemplo`: `MARCO NORMATIVO: DS 33.`

### 1.4 Reajuste de Orden Correlativo
Debido a la inserción de la fila `subtitulo_numeral` con orden `11`, se desplaza el número de orden de las siguientes filas para mantener la secuencia:
*   `referencia_cruzada`: orden `12`
*   `tabla_imagen`: orden `13`
*   `Firma` (firmante): orden `15` (antes 14, se asume que no hay orden 14 o se reestructura correlativamente)
*   `Distribución` (lista_distribucion): orden `16` (antes 15)

---

## 2. Plan de Validación y Pruebas

Para garantizar la integridad y coherencia técnica de esta modificación:
1.  **Validación de Formato CSV**: Ejecutar el script [`test/test_csv_integrity.py`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/test/test_csv_integrity.py) para certificar que el archivo CSV mantiene sus 12 columnas por fila, y que los campos críticos (`bloque`, `campo`, `tipo_dato`, `obligatorio`, `orden`, `zona`) no contienen nulos.
2.  **Validación de Ejecución de Pruebas**: Correr todos los tests del repositorio con pytest para certificar que no existen regresiones.

---

## 3. Auto-Evaluación (Self-Review)

*   **Placeholders**: No se definen placeholders; se especifican todos los campos y valores reales.
*   **Consistencia**: Se respeta la estructura general del archivo CSV original, agregando soporte explícito a los requerimientos del usuario sin romper los campos de validación semántica del test local.
*   **Aislamiento**: El diseño está acotado al archivo CSV de documentación y su impacto directo en el test de integridad, sin requerir cambios invasivos en el código de producción.
