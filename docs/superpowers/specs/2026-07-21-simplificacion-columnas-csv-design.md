# Especificación de Diseño: Simplificación de Columnas en CSV de Estructura DDU

Esta especificación detalla el diseño y los cambios necesarios para simplificar el archivo [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/bcn%20-%20documentación/estructura_circular_ddu.csv) eliminando las columnas `patron_regex` y `tipo_dato`, que no aportan valor documental directo como maqueta estructural, y actualizando la suite de pruebas.

---

## 1. Cambios Propuestos

### 1.1 Reducción de Columnas en `estructura_circular_ddu.csv`
El archivo CSV pasará de tener 12 columnas a tener exactamente 10 columnas. Se remueven los campos `tipo_dato` (columna 3) y `patron_regex` (columna 5).

La nueva cabecera será:
`bloque,campo,obligatorio,orden,zona,campo_parser,estado_parser,reglas,descripcion,ejemplo`

Todas las filas se reestructurarán en consonancia para mantener la alineación.

### 1.2 Actualización de `test/test_csv_integrity.py`
Se modificarán los parámetros de validación en el script de prueba para adaptarlos al nuevo formato de 10 columnas:
*   La llamada a `validar_csv(csv_estructura, 12)` se cambiará a `validar_csv(csv_estructura, 10)`.
*   Se eliminará `"tipo_dato"` de la lista de verificación de campos obligatorios en el CSV:
    ```python
    # De:
    for col in ["bloque", "campo", "tipo_dato", "obligatorio", "orden", "zona"]:
    # A:
    for col in ["bloque", "campo", "obligatorio", "orden", "zona"]:
    ```

---

## 2. Plan de Validación y Pruebas

1.  **Ejecución de Pruebas de Integridad**: Correr `pytest test/test_csv_integrity.py -v` para certificar que el archivo CSV tiene 10 columnas y el formato está alineado.
2.  **Suite de Pruebas Global**: Correr `pytest` para asegurar que el resto de los tests se mantenga 100% exitoso.

---

## 3. Auto-Evaluación (Self-Review)

*   **Placeholders**: No se definen placeholders; se detalla el diseño de forma exacta.
*   **Consistencia**: Se coordinan los cambios en el CSV con el código de prueba de integridad para asegurar que no se produzcan fallos sintácticos en el testing local.
*   **Aislamiento**: El impacto es puramente local y acotado al archivo CSV documental y su test correspondiente.
