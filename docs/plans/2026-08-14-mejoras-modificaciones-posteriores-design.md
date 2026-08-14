# Especificación de Diseño: Extracción Completa y Multi-Página de Modificaciones Posteriores

**Fecha:** 2026-08-14  
**Rama:** `feature/ddu-456`  
**Objetivo:** Extraer de forma íntegra y exhaustiva todas las notas marginales, timbres y aclaraciones de modificaciones posteriores a lo largo de todas las páginas de la circular DDU.

---

## 1. Contexto del Problema

En la versión actual de [`scripts/extractors/modificaciones_posteriores.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/modificaciones_posteriores.py):
1. Sólo se inspeccionaban las 2 primeras páginas del PDF (`reader.pages[:2]`), ignorando notas marginales de modificación presentes en páginas intermedias o tablas (como la página 5 de DDU 456).
2. En la página 1 de DDU 456 se truncaba el fragmento final de la nota `(numeral 7.)`.
3. No se capturaba la segunda nota en página 5:
   `"Mediante Circular Ord. N°214, de fecha 02.05.2024, DDU 498, se aclara que la materia contenida en la Circular DDU 339 se aborda en el punto 6 y no en el 5 como de había indicado previamente."`

---

## 2. Requerimientos de Diseño

1. **Escaneo Exhaustivo Multi-Página**: Analizar la totalidad del documento PDF (o texto extraído) bloque por bloque y página por página.
2. **Captura Íntegra de Notas Marginales**:
   * Patrones ampliados:
     * `Circular\s+Modificada\s+por\b`
     * `Mediante\s+Circular\s+Ord\b`
     * `Modificada\s+por\s+Circular\b`
     * `Dejada\s+sin\s+efecto\s+por\b`
     * `Aclarada\s+por\s+Circular\b`
     * `Complementada\s+por\s+Circular\b`
   * Preservar paréntesis aclaratorios como `(numeral 7.)` y el texto explicativo completo.
3. **Consolidación con `; `**:
   * Unir todas las notas encontradas en orden de aparición delimitadas por `; `.
4. **Preservación de Exclusión en `CuerpoExtractor`**:
   * Garantizar que las notas de modificación posterior sigan excluidas del texto del cuerpo normativo para no contaminar los numerales.

---

## 3. Salida Esperada para DDU 456

En `salidas_csv/DDU_456_extraido.csv` (campo `modificaciones_posteriores`):
```text
Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.); Mediante Circular Ord. N°214, de fecha 02.05.2024, DDU 498, se aclara que la materia contenida en la Circular DDU 339 se aborda en el punto 6 y no en el 5 como de había indicado previamente.
```

---

## 4. Plan de Validación

* Unit tests en `test/test_extractor_modificaciones_posteriores.py` validando la captura de las 2 notas completas en DDU 456.
* Integración en `test/test_orchestrator.py`.
* Suite completa (78+ tests) aprobada al 100%.
