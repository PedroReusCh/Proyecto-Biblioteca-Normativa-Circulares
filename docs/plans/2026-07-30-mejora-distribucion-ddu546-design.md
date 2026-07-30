# Especificación de Diseño: Corrección de Extracción de Lista de Distribución en `DistribucionExtractor` (`distribucion.py`)

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 546 (y circulares con distorsión de escaneo u OCR en la sección de cierre), el extractor de lista de distribución en [`scripts/extractors/distribucion.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/distribucion.py) presentaba tres problemas:
1. No reconocía el encabezado `DISTRIBUCIÓN:` cuando venía distorsionado por el OCR como `RIBuc)óN:`.
2. Capturaba prematuramente líneas pertenecientes a la firma (`N DIEGO IZQUIERDO HEVIA`), fórmulas de saludo (`Saluda atentamente`) y ruido de OCR (`tl '.`, `RA/4l...`) incluyéndolas como ítems de la lista de distribución.
3. El segundo ítem traía una coma inicial en la numeración (`,2. Sra. Subsecretaria...`).

Se requiere ajustar `distribucion.py` para reconocer las variantes OCR del encabezado, desinfectar la numeración de los ítems y purgar cualquier ruido previo a la nómina oficial de receptores.

---

## 2. Lógica de Filtrado y Reconocimiento (`distribucion.py`)

1. **Ampliación de `patron_encabezado_distribucion`**:
   ```python
   patron_encabezado_distribucion = (
       r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
   )
   ```

2. **Desinfección de Prefijos en `_limpiar_item_distribucion`**:
   Limpia signos de puntuación iniciales (ej. `,2.` ➔ `2.`, `!1.` ➔ `1.`).

3. **Reinicio de Lista al Detectar Encabezado**:
   Al coincidir con `patron_encabezado_distribucion`, se resetea la lista capturada previamente con `lista_distribucion.clear()` y se fija `idx_auto = 1`.

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `distribucion.py` procese correctamente la nómina de la DDU 546 sin ruido ni elementos del firmante.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 comprobando que la celda `lista_distribucion` comience limpiamente en `1. Sr. Ministro de Vivienda y Urbanismo`.
