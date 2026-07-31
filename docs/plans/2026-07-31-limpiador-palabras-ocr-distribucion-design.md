# Especificación de Diseño: Limpiador Universal de Palabras Divididas por OCR en `DistribucionExtractor` (`distribucion.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Al extraer la nómina de distribución en [`scripts/extractors/distribucion.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/distribucion.py) desde los PDFs de las circulares DDU, el proceso de lectura de PDF OCR divide nombres de cargos e instituciones públicas mediante espacios espurios (ej: `Contra loría I nterna MINVU`, `Territor ial`, `Territo rial`, `Autorizac iones`, `Reviso res`, `Secreta rias`).

Se requiere potenciar la función `_limpiar_item_distribucion` en `distribucion.py` mediante expresiones regulares universales para re-ensamblar palabras fragmentadas de forma transparente y general en todas las circulares.

---

## 2. Lógica de Limpieza (`distribucion.py`)

1. **Refactorización de `_limpiar_item_distribucion`**:
   ```python
   def _limpiar_item_distribucion(item: str) -> str:
       # Normalización de prefijos numéricos ruidosos
       item = re.sub(r"^[\,\!\;\:\_\-\s]+(\d+)", r"\1", item)
       item = re.sub(r"^[lIi\|][\.\!\;\:\,\_\-\s]+\s*", r"1. ", item)
       item = re.sub(r"^(\d+)[\!\;\:\,\_\-]+\s*", r"\1. ", item)
       item = re.sub(r"^(\d+)\s*\.\s*", r"\1. ", item)

       # Siglas institucionales
       item = re.sub(r"\bMI\s+NVU\b", "MINVU", item, flags=re.IGNORECASE)
       item = re.sub(r"\bSERE\s+MI\b", "SEREMI", item, flags=re.IGNORECASE)
       item = re.sub(r"\bSER\s+VIU\b", "SERVIU", item, flags=re.IGNORECASE)
       item = re.sub(r"\bI\s+nterna\b", "Interna", item, flags=re.IGNORECASE)

       # Re-ensamblar sufijos en '-ial', '-rial', '-loría'
       item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{2,})\s+(ial|rial|loría)\b", r"\1\2", item, flags=re.IGNORECASE)

       # Re-ensamblar sufijos terminados en '-ción' / '-ciones'
       item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+i([óo]n|iones)\b", r"\1i\2", item, flags=re.IGNORECASE)

       # Re-ensamblar plurales y terminaciones comunes
       item = re.sub(
           r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|ria|rias|rios|tiva|tivas)\b",
           r"\1\2",
           item,
           flags=re.IGNORECASE,
       )

       # Letra aislada al final de palabra
       item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", item, flags=re.IGNORECASE)

       item = re.sub(r"[\s;]+$", "", item)
       item = re.sub(r"\s*;\s*", " ", item)
       item = re.sub(r"\s+\.", ".", item)
       return re.sub(r"\s+", " ", item).strip()
   ```

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria `test_distribucion_extractor_limpieza_palabras_divididas` en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `Contra loría I nterna MINVU`, `Territor ial`, `Territo rial` y `Autorizac iones` queden limpios y sin separaciones.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 verificando la celda `lista_distribucion` en la Fila 13.
