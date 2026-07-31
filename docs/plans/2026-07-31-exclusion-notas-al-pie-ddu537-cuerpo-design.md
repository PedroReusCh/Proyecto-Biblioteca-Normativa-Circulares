# Especificación de Diseño: Exclusión de Notas al Pie y Preservación de Numerales en `CuerpoExtractor` (`cuerpo.py`) para DDU 537

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 537, las notas al pie de página (ej. `1 Artículo 38...` y `2 La orientación técnica...`) provocaban la pérdida del Numeral 4 debido a que el encabezado del párrafo venía con un espacio antes del punto (`4 . Si bien...`), impidiendo el reinicio del estado `omitiendo_nota_al_pie`.

Se requiere actualizar [`scripts/extractors/cuerpo.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/cuerpo.py) para normalizar prefijos `\d+\s+\.` a `\d+.` y reiniciar la máquina de estados de descarte al cambiar de página o encontrar numerales del cuerpo.

---

## 2. Lógica de Filtrado y Normalización (`cuerpo.py`)

1. **Normalización de Numerales OCR (`_normalizar_prefijo_numeral_ocr`)**:
   ```python
   def _normalizar_prefijo_numeral_ocr(line: str) -> str:
       # Normalizar espacio entre dígito y punto (ej. "4 . ", "7 . ") -> "4. "
       line = re.sub(r"^(\d+)\s+\.\s*", r"\1. ", line)
       # ...
       return line
   ```

2. **Control de Estado `omitiendo_nota_al_pie`**:
   - Al detectar `_es_pie_de_pagina`, resetear `omitiendo_nota_al_pie = False`.
   - Al encontrar cualquier numeral `\d+\.` o número romano, resetear `omitiendo_nota_al_pie = False`.

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria `test_cuerpo_extractor_ddu_537_exclusion_notas_al_pie` en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que el Numeral 4 se incluya en el cuerpo y que las notas 1 y 2 no se arrastren.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Exportación del CSV de DDU 537 comprobando el cuerpo normativo completo.
