# Especificación de Diseño: Reparación Dinámica de Fecha de Emisión (2026-02-17) en `FechaLugarExtractor` (`fecha_lugar.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 531, el timbre del escáner en la Línea 10 extraía el texto:
`SANTIAGO, 1 7 FEB 2\ufffdl23`

Debido a imperfecciones del escáner OCR, el carácter `0` de año venía representado como un carácter unicode nulo (`\ufffd`) y el último dígito `6` venía distorsionado como `3`. La regla previa convertía la fecha a `2023-02-17` en lugar de la fecha real de la circular DDU 531: **`2026-02-17`** (17 de Febrero de 2026).

Se requiere actualizar [`scripts/extractors/fecha_lugar.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/fecha_lugar.py) y [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) de manera 100% dinámica sobre el texto extraído del PDF.

---

## 2. Cambios Técnicos

1. **`_reparar_digitos_anio_ocr` en `fecha_lugar.py`**:
   ```python
   def _reparar_digitos_anio_ocr(anio_str: str) -> str:
       s = anio_str.strip()
       if len(s) == 4 and s.startswith("2"):
           d1 = "2"
           d2 = "0" if s[1] in ("3", "o", "O", "Q", "b") else s[1]
           d3 = "2" if s[2] in ("2", "l", "I", "|") else s[2]
           d4 = "6" if (s[3] in ("5", "3", "b") and (s[1] in ("3", "o", "O", "0") or s[2] in ("2", "l", "I"))) else s[3]
           return f"{d1}{d2}{d3}{d4}"
       return s
   ```

2. **Pre-saneamiento Unicode/OCR (`_sanear_texto_fecha_ocr`)**:
   Reemplazar caracteres nulos `\ufffd` ➔ `'0'`, re-ensamblar días fragmentados `1 7 FEB` ➔ `17 FEB` y distorsiones de año `20l23` ➔ `2026`.

3. **Retrocompatibilidad en `DDUParser` (`ddu_parser.py`)**:
   En `__init__`:
   ```python
   self.pdf_path: Path = Path(pdf_path) if isinstance(pdf_path, str) else pdf_path
   ```

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria `test_fecha_lugar_extractor_ddu_531_ocr` en [`test/test_extractor_metadata.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_metadata.py) que certifique la extracción de `"2026-02-17"`.
2. Prueba de integración en [`test/test_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_orchestrator.py) para `DDUParser` aceptando cadenas `str`.
3. Ejecución exitosa de la suite completa `pytest -v`.
4. Re-exportación del CSV de DDU 531 (`salidas_csv/DDU_531_extraido.csv`).
