# Especificación de Diseño: Normalización de Llamadas a Notas al Pie `[N]` en `CuerpoExtractor`

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Al extraer texto de PDFs mediante `pypdf`, los números en superíndice que corresponden a llamadas a notas al pie de página (ej. 1, 2, 3) son transformados en caracteres alfanuméricos normales. Esto genera dos inconvenientes principales:
1. Distorsión de numerales de artículos citados (ej. `artículo 381` cuando corresponde al `artículo 38` con nota `1`).
2. Presencia de dígitos sueltos al final de palabras o frases (ej. `carácter de construcción 2` o `DDU ESPECÍFICA Nº97 /2007 1`).

Se requiere integrar un helper de normalización en [`scripts/extractors/cuerpo.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/cuerpo.py) que identifique estas llamadas a notas al pie y las formatee explícitamente entre corchetes `[1]`, `[2]`, `[3]`.

---

## 2. Lógica de Transformación (`_normalizar_llamadas_nota_al_pie`)

Se añade la función helper `_normalizar_llamadas_nota_al_pie(line: str) -> str` en `cuerpo.py` ejecutada al procesar cada párrafo del cuerpo:

1. **Separación de llamadas pegadas a artículos**:
   Transforma patrones de artículos seguidos de dígito de llamada (ej. `artículo 381` ➔ `artículo 38 [1]`).

2. **Formateo de llamadas tras palabras o signos de puntuación**:
   Transforma patrones como `construcción 2` ➔ `construcción [2]`, `área verde 3` ➔ `área verde [3]`, `Nº97 /2007 1` ➔ `Nº97 /2007 [1]`, `imágenes 2` ➔ `imágenes [2]`.

3. **Exclusiones necesarias**:
   No afecta a números de año (`2024`), listas numeradas al inicio de párrafo (`1. `, `2. `), ni números ordinales (`4°`, `N°112`).

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `cuerpo.py` formatee llamadas como `[1]`, `[2]`.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación de los CSVs de DDU 537 y DDU 546 validando que el texto del cuerpo muestre las llamadas a notas formateadas como `[1]`, `[2]`.
