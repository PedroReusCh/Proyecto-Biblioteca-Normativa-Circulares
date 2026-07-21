# Especificación de Diseño: Corrección de Extracción de DDU 531

Esta especificación detalla las soluciones técnicas diseñadas para corregir los errores de extracción de metadatos y la mala estructuración del cuerpo detectados en la circular DDU 531.

---

## 1. Problemas Identificados y Soluciones Diseñadas

### 1.1 Acto Administrativo (`numero_ord`) incorrecto
*   **Problema**: Se extrajo `0535` en vez de `088`. El OCR leyó `CIRCULAR ORO. N° 088` (confundiendo `ORD` con `ORO`), lo que provocó que el parser no encontrara el patrón `ORD.` y cayera en un fallback incorrecto.
*   **Diseño**:
    1.  Robustecer la regex del parser central para tolerar variaciones comunes de OCR de `ORD` como `ORO`, `OR0`, `OR`.
    2.  Permitir leer `numero_ord` desde el archivo de fallbacks estáticos si el análisis de texto no produce resultados válidos.
    3.  Actualizar la definición de fallbacks estáticos para declarar `"numero_ord": "088"` para la circular 531.

### 1.2 Antecedentes (`antecedentes`) falsamente poblados
*   **Problema**: La circular DDU 531 no posee antecedentes (`ANT:`). El parser pobló este campo con texto irrelevante debido a un fallback estático mal configurado.
*   **Diseño**: Limpiar el fallback de antecedentes en la configuración estableciéndolo como vacío (`""`), y modificar la lógica de recuperación de fallback del parser para que no use valores estáticos por defecto si se declaran vacíos en la configuración.

### 1.3 Descriptores (`descriptores`) faltantes
*   **Problema**: Faltaron descriptores clave (`PERMISOS, APROBACIONES Y RECEPCIONES; MODIFICACION DE PROYECTOS`).
*   **Diseño**: Proveer los descriptores correspondientes a través del fallback estático del JSON y asegurar su lectura por el parser central.

### 1.4 Fecha de emisión (`fecha`) incorrecta
*   **Problema**: Se extrajo `2023-02-17` en vez de `2026-02-17` debido a un valor estático desactualizado en la configuración.
*   **Diseño**: Corregir la fecha de la DDU 531 en `fallbacks_ddu.json` a `2026-02-17`.

### 1.5 Estructuración incorrecta del Cuerpo (Romanos y Arábigos desalineados)
*   **Problema**: El OCR de la DDU 531 interpretó `I. ANTECEDENTES` como `l. ANTECEDENTES` (l minúscula) y `II. NORMATIVA APLICABLE` como `11. NORMATIVA APLICABLE`. Al no detectarse los números romanos, los numerales arábigos anidados perdieron jerarquía. Traducir genéricamente cualquier `11. <MAYÚSCULAS>` a `II.` puede colisionar con un numeral arábigo legítimo `11.` en circulares extensas.
*   **Diseño**: Implementar una fase de normalización de líneas en el cuerpo del parser restringida estrictamente a títulos de sección conocidos:
    *   `l. ANTECEDENTES` -> `I. ANTECEDENTES`
    *   `11. NORMATIVA APLICABLE` -> `II. NORMATIVA APLICABLE`
    Esto garantiza la correcta jerarquía en la circular 531 sin riesgo de alterar numerales arábigos `11.` reales en otras circulares del proyecto.

### 1.6 Nombre del Firmante (`firmante`) faltante
*   **Problema**: No se extrajo el nombre del firmante debido a ruido en la sección de firmas digitalizadas en el PDF.
*   **Diseño**: Declarar a `VICENTE BURGOS SALAS, JEFE DIVISIÓN DE DESARROLLO URBANO` como firmante fallback en el JSON y robustecer el parser para asignar firmantes automáticos para las circulares emitidas en 2026.

### 1.7 Distribución (`lista_distribucion`) incorrecta
*   **Problema**: La distribución no se extrajo debido a que la palabra clave de corte en el PDF fue leída como `D STRIBUCI?N: 1`.
*   **Diseño**:
    1.  Modificar el corte temprano del cuerpo de las secciones para buscar patrones flexibles de distribución con expresiones regulares insensibles a mayúsculas y acentos (`\b(?:D\s*S|D)?\s*STRIBUC[I\?OÓ]+N\b`).
    2.  Robustecer la regex que extrae la lista de distribución del texto completo del PDF con la misma flexibilidad.

---

## 2. Plan de Validación

1.  **Regeneración**: Correr el exportador a CSV.
2.  **Aserciones de salida**: Verificar que el archivo generado en `bcn - circulares - csv/DDU 531.csv` contenga las correcciones exactas descritas en los puntos anteriores.
3.  **Pruebas de Regresión**: Correr `pytest` para certificar que el parser siga estando 100% verificado y sin regresiones.
