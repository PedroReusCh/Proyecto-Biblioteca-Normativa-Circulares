# Especificación de Diseño: Limpiador Universal de Palabras Divididas por OCR en `NotaAlPieExtractor` (`nota_al_pie.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Al extraer el metadato de notas al pie en [`scripts/extractors/nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/nota_al_pie.py) desde PDFs de circulares DDU, la lectura de texto mediante PDF OCR divide palabras en español y anglicismos mediante espacios intermedios espurios (ej: `carácte r`, `'con tain ers'`, `mirado res`, `higié nicos`, `paño les`, `herramien tas`, `artícu lo`, `edificac ión`).

Se requiere integrar un helper universal `_limpiar_palabras_divididas_ocr(texto: str) -> str` en `nota_al_pie.py` para re-ensamblar automáticamente las palabras fragmentadas de forma transversal en todas las circulares.

---

## 2. Lógica de Limpieza (`nota_al_pie.py`)

1. **Función `_limpiar_palabras_divididas_ocr`**:
   ```python
   def _limpiar_palabras_divididas_ocr(texto: str) -> str:
       # Re-ensamblar anglicismos y términos compuestos divididos
       texto = re.sub(r"\bcon\s+tain\s+ers\b", "containers", texto, flags=re.IGNORECASE)
       texto = re.sub(r"\bcon\s+tainers\b", "containers", texto, flags=re.IGNORECASE)
       texto = re.sub(r"\bcontain\s+ers\b", "containers", texto, flags=re.IGNORECASE)

       # Re-ensamblar sufijos terminados en 'ción' / 'ciones' (ej: edificac ión -> edificación)
       texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+i([óo]n|iones)\b", r"\1i\2", texto)

       # Re-ensamblar sufijos terminados en 'lo' / 'los' (ej: artícu lo -> artículo)
       texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+tícu)\s+(lo|los)\b", r"\1\2", texto)

       # Re-ensamblar plurales y terminaciones comunes en 'res', 'les', 'nes', 'dos', 'das', 'tos', 'tas', 'nicos', 'mente'
       texto = re.sub(
           r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|mente|nicos|nica|nicas)\b",
           r"\1\2",
           texto,
       )

       # Re-ensamblar letra aislada al final de palabra (ej: carácte r -> carácter)
       texto = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", texto)

       return re.sub(r"\s+", " ", texto).strip()
   ```

2. **Puntos de Invocación**:
   - En `_guardar_nota_actual()` al acumular cada renglón.
   - En `extract()` antes de unir la lista de notas con `" | "`.

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria `test_nota_al_pie_extractor_limpieza_palabras_divididas` en [`test/test_extractor_nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_nota_al_pie.py) verificando que `carácte r`, `'con tain ers'`, `mirado res`, `higié nicos`, `paño les`, `herramien tas`, `artícu lo 1.6.3.` sean corregidos limpiamente.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 verificando la celda `notas_al_pie` en la Fila 11.
