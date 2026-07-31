# Especificación de Diseño: Normalización de Llamada a Nota al Pie `imá genes 2` en `CuerpoExtractor` (`cuerpo.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 537, el Numeral 4 del cuerpo normativo contiene el texto fragmentado por OCR:
`"procesamiento de las imá genes 2 para la conversión de la información..."`

Dado que `imá genes` poseía un espacio intermedio de escaneo, la regla previa de conversión a llamada de nota al pie corcheteada (`[2]`) no se activaba, dejando el dígito `2` suelto.

Se requiere actualizar [`scripts/extractors/cuerpo.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/cuerpo.py) para que `_normalizar_llamadas_nota_al_pie` y `_limpiar_texto_cuerpo` reconozcan espacios OCR dentro de `imá genes 2`.

---

## 2. Cambios Técnicos (`cuerpo.py`)

1. **`_normalizar_llamadas_nota_al_pie`**:
   ```python
   line = re.sub(r"im[áa]\s*genes\s*2\b", "imágenes [2]", line, flags=re.IGNORECASE)
   ```

2. **`_limpiar_texto_cuerpo`**:
   ```python
   (r"\bim[áa]\s+genes\b", "imágenes"),
   ```

---

## 3. Criterios de Aceptación y Pruebas

1. Actualización de la prueba unitaria `test_cuerpo_extractor_llamadas_nota_al_pie` en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) para verificar la conversión `imá genes 2` ➔ `imágenes [2]`.
2. Ejecución exitosa de `pytest -v` (38/38 PASSED).
3. Re-exportación del CSV de DDU 537 certificando el cuerpo normativo.
