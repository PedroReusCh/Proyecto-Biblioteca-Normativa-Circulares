# Especificación de Diseño: Normalización de Flujo Continuo en Celdas de Tablas CSV

**Fecha:** 2026-08-14  
**Rama:** `feature/ddu-456`  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Problema

Cuando `pdfplumber` extrae tablas de columnas estrechas en archivos PDF, preserva los saltos de línea visuales duros (`\n`) cada 3 a 5 palabras. Esto provoca que en los archivos CSV (`salidas_tablas/DDU_{num}_tabla_{idx}.csv`), las celdas se lean fragmentadas verticalmente y resulten incómodas de visualizar para usuarios y analistas.

---

## 2. Requerimientos de Diseño

1. **Unificación Continua de Líneas**:
   - Transformar los saltos de línea artificiales de columna estrecha en espacios ` ` continuos.
2. **Preservación Adaptable de Estructura Lógica**:
   - Detectar dinámicamente el inicio de nuevos párrafos o ítems mediante expresiones regulares flexibles:
     - Letras de incisos/ítems: `a)`, `b)`, `c)`, `a.`, `b.`, etc.
     - Numerales: `1.`, `2.`, `1)`, `2)`, etc.
     - Números romanos: `i)`, `ii)`, `iii)`, etc.
     - Viñetas y guiones: `- `, `• `, `* `
     - Frases modificatorias o notas: `Mediante Circular...`, `Por la siguiente:`, `Reemplázase...`, `Se deja sin efecto...`
3. **Saneamiento Tipográfico OCR Universal**:
   - Aplicar `limpiar_palabras_ocr()` a cada celda para eliminar fragmentación OCR (ej. `a rtículo` -> `artículo`).
4. **Formato en CSV Individual de Tablas**:
   - Cada celda queda estructurada en párrafos o ítems fluidos continuos, eliminando la fragmentación vertical palabra por palabra.

---

## 3. Componentes Involucrados

1. [`scripts/extractors/tablas.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/tablas.py):
   - Crear función `normalizar_texto_celda_tabla(texto: str) -> str`.
   - Aplicarla en `_compactar_tabla_pdf()`, `_consolidar_tablas_multipagina()` y `_exportar_tabla_csv()`.
2. [`test/test_extractor_tablas.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_tablas.py):
   - Validar que las celdas no contengan fragmentación línea a línea y que los párrafos se lean continuos.
3. Regenerar [`salidas_tablas/DDU_456_tabla_1.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_tablas/DDU_456_tabla_1.csv).

---

## 4. Criterios de Éxito y Verificación

- `salidas_tablas/DDU_456_tabla_1.csv` presenta texto fluido y continuo en cada celda.
- Suite completa de 78+ pruebas pasando al 100% (`pytest -v`).
- Pylance Strict Mode con 0 errores de tipado.
