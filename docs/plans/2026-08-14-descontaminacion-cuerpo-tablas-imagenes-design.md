# Documento de Diseño: Descontaminación de Tablas e Imágenes en CuerpoExtractor

## 1. Contexto y Objetivos

En la extracción de la circular **DDU 456**, el módulo `CuerpoExtractor` (`scripts/extractors/cuerpo.py`) presentaba contaminación por:
1. **Filtración de Tablas Normativas (Páginas 5 a 8)**: La tabla comparativa de modificaciones a las circulares DDU 339, DDU 322 y DDU 168 se volcaba como texto no estructurado en el cuerpo, generando párrafos espurios 8, 9 y 10.
2. **Filtración de Etiquetas de Diagramas en Numeral 4**: El Numeral 4 debe contener únicamente la frase normativa introductoria al esquema técnico, mientras que el gráfico y sus rótulos residen en `salidas_imagenes/`.

## 2. Arquitectura de la Solución (Opción 1)

### 2.1. Detección y Omisión de Bloques Tabulares en `CuerpoExtractor`
* **Marcador de inicio de tabla**: Detección de encabezados tabulares como `Circular\s+Materia\(s\)\s+que\s+se\s+modifica\(n\)`, líneas de tablas Markdown (`| ... |`) o patrones de columnas de tablas normativas.
* **Comportamiento de omisión**: Al detectar el inicio de un bloque tabular, `CuerpoExtractor` activa un estado `omitiendo_tabla = True` y descarta todas las líneas tabulares hasta llegar a la sección de cierre (`Saluda atentamente`, `DISTRIBUCIÓN`).
* **Saneamiento del párrafo previo (Numeral 7)**: Si el párrafo previo capturó parte de la primera línea de encabezados de la tabla (ej. `Circular Materia(s)... DDU 339...`), se trunca y sanea para que finalice limpiamente en la frase introductoria normativa terminando en dos puntos (`:`).

### 2.2. Aislamiento del Numeral 4 (Esquema Ilustrativo)
* El Numeral 4 queda compuesto exclusivamente por:
  > *"4. A continuación, se presenta un esquema ilustrativo que sintetiza algunos de los aspectos abordados en la presente Circular:"*
* Se descartan todas las líneas de rótulos o cotas que pertenezcan al plano visual.

### 2.3. Estructura Final del Cuerpo en DDU 456
El cuerpo de la DDU 456 contendrá **exactamente 7 párrafos / numerales**:
1. **Numeral 1**: Facultades legales y objeto de la circular (LGUC / OGUC).
2. **Numeral 2**: Transcripción de los incisos vigésimo, vigésimo primero, vigésimo segundo y vigésimo tercero del art. 2.6.3.
3. **Numeral 3**: Criterios de inferencia normativa (letras a, b, c, d, e).
4. **Numeral 4**: Frase introductoria al esquema ilustrativo.
5. **Numeral 5**: Criterios de aplicación para pisos mecánicos.
6. **Numeral 6**: Criterios de distanciamiento y cálculo de sombras proyectadas (Circular DDU 168).
7. **Numeral 7**: Modificación a circulares anteriores (introducción formal a la tabla anexa).

## 3. Plan de Verificación y Testing

1. **Prueba unitaria en `test/test_extractor_body.py`**:
   * Verificar que `CuerpoExtractor` extraiga exactamente 7 párrafos normativos en DDU 456.
   * Verificar que no existan encabezados de tabla (`Circular Materia(s)...`) ni párrafos residuales 8, 9, 10 en el cuerpo.
   * Verificar que el Numeral 7 termine limpiamente en su introducción.
2. **Pruebas de integración en `test/test_orchestrator.py`**:
   * Validar consistencia de los 14 bloques normativos con el cuerpo limpio.
3. **Suite completa (`pytest -v`)**:
   * Certificar que las 72 pruebas pasen al 100%.
