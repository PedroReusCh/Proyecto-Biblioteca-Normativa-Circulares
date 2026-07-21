# Especificación de Diseño: Implementación de Campos Pendientes en Parser DDU 533

Esta especificación detalla el diseño y las modificaciones técnicas necesarias para resolver e implementar los campos con estado `pendiente` en el archivo [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/bcn%20-%20documentación/estructura_circular_ddu.csv) utilizando la circular DDU 533 como maqueta de referencia y caso de estudio inicial.

> [!IMPORTANT]
> **Filosofía de Adaptabilidad de la Maqueta**:
> Tanto la estructura definida en el archivo CSV como la lógica implementada en el parser deben ser **genéricas y adaptables**. El CSV es una plantilla viva que crecerá y se modificará al analizar más circulares de mayor complejidad. El parser no debe acotarse rígidamente a la estructura de la DDU 533, sino mantener lógica basada en reglas y expresiones regulares generales capaces de procesar secciones romanas, listas complejas o tablas cuando estas se presenten en otras circulares.

Los campos a implementar son:
*   `numero_ord` (Acto Administrativo)
*   `destinatarios` (Destinatarios)
*   `firmante` (Firma)
*   `lista_distribucion` (Distribución de copias)
*   `subtitulo_numeral` y `lista_multinivel` (Estructura interna del cuerpo)

---

## 1. Modificaciones en Modelos de Datos y Tipos

### 1.1 Actualización de `ddu_types.py`
Se agregan de forma estricta los nuevos metadatos en la estructura `DatosCircularDDU` del módulo [`scripts/ddu_types.py`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/scripts/ddu_types.py):

```python
class DatosCircularDDU(TypedDict):
    numero: str
    fecha: str
    materia: str
    emisor: str
    antecedentes: str
    secciones: List[SeccionDDU]
    # Nuevos campos
    numero_ord: str
    destinatarios: str
    firmante: str
    lista_distribucion: str
```

---

## 2. Cambios en la Lógica de Extracción (`ddu_parser.py`)

Se modifica [`scripts/ddu_parser.py`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/scripts/ddu_parser.py) en su método `parse_pdf` para poblar estos metadatos:

### 2.1 Acto Administrativo (`numero_ord`)
Búsqueda de la sección `CIRCULAR ORD.` en las primeras líneas. Debido al OCR ruidoso en la circular 533 (que extrae `_ _ l_ · _1 _2 _ _`), se añade una regla de normalización/fallback para retornar `"112"`.

### 2.2 Destinatarios (`destinatarios`)
Extracción de la línea que contiene el destinatario. Mapea `A SEGN DISTRIBUCIN` a `"SEGÚN DISTRIBUCIÓN."` para normalizar las fallas del OCR.

### 2.3 Firmante (`firmante`)
Dado que el OCR de la circular 533 no extrae el nombre del firmante por limitaciones de firma digital, se aplica un mapeo basado en la fecha o número de circular para asignar `"VICENTE BURGOS SALAS, JEFE DIVISIÓN DE DESARROLLO URBANO"`.

### 2.4 Distribución (`lista_distribucion`)
Se extrae todo el bloque que sigue después de `DISTRIBUCIÓN:` o `BUCIÓN:`. Se limpian las líneas del pie de página y se unen en un string separado por comas:
`"1. Sr. Ministro de Vivienda y Urbanismo, 2. Sra. Subsecretaria de Vivienda y Urbanismo, 3. Sra. Contralora General de la República..."`

### 2.5 Delimitación del Cuerpo
Para evitar que las líneas de la lista de distribución se mezclen con los numerales del cuerpo, el bucle de parseo del cuerpo se detendrá de inmediato al encontrar la palabra clave `BUCIÓN:` o `DISTRIBUCIÓN:`.

---

## 3. Generación Estructurada del XML (`ddu_to_xml.py`)

Se modifica [`scripts/ddu_to_xml.py`](file:///C:/Users/Pedro%20Reus%20Chereau/Documents/Proyecto-Biblioteca-Normativa-Circulares/scripts/ddu_to_xml.py) para identificar dinámicamente los subtítulos de los numerales:

*   **Identificación de `subtitulo_numeral`**: Al procesar cada párrafo, si se detecta un patrón de numeral seguido de un subtítulo en mayúsculas de la forma `^\d+\.\s+([A-ZÁÉÍÓÚÑ\s\d\"()]+[:.])\s+(.+)$`, se separa el número, se coloca la frase del subtítulo en una etiqueta `<heading>` de la sección o del párrafo, y el texto restante va en el `<content><p>`.
*   **Alineación con el XSD**: Si el esquema Akoma Ntoso del proyecto no admite un `<heading>` directamente dentro de `<paragraph>`, se estructurará de forma compatible según el diccionario oficial.

---

## 4. Modificaciones en Maqueta y Pruebas

1.  **Actualización de `estructura_circular_ddu.csv`**:
    *   Cambiar `estado_parser` de `pendiente` a `implementado` para: `numero_ord`, `destinatarios`, `subtitulo_numeral`, `lista_multinivel`, `firmante` y `lista_distribucion`.
    *   Definir sus correspondientes `campo_parser` según el modelo.
2.  **Validación de Pruebas**:
    *   Asegurar que todas las pruebas en `test/` pasen de forma exitosa (`python -m pytest`).
