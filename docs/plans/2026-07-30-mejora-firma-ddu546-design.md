# Especificación de Diseño: Corrección de Firma y Cargo en `FirmaExtractor` (`firma.py`)

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 546, el extractor de firma en [`scripts/extractors/firma.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/firma.py) presentaba dos problemas:
1. No detenía la lectura al llegar al encabezado de distribución distorsionado por OCR (`RIBuc)óN:`), arrastrando el receptor `Sr. Ministro de Vivienda y Urbanismo`.
2. Presentaba distorsiones de OCR en el nombre y cargo del firmante (`N DIEGO ZQUIERDO HEVIA, D VISIÓN DE DESARROLLO URBANO, IS RIO DE VIVIENDA Y URBANISMO`).

Se requiere ajustar `firma.py` para reconocer el encabezado de distribución distorsionado y reparar los nombres y cargos de firmantes mediante el helper `_limpiar_texto_firma`.

---

## 2. Lógica de Filtrado y Reparación (`firma.py`)

1. **Detención en Encabezado de Distribución OCR**:
   ```python
   patron_encabezado_distribucion = (
       r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
   )
   ```

2. **Normalización OCR en `_limpiar_texto_firma`**:
   ```python
   def _limpiar_texto_firma(texto: str) -> str:
       texto = re.sub(r"\bN\s+DIEGO\s+ZQUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
       texto = re.sub(r"\bD\s+VISI[ÓO]N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
       texto = re.sub(r"\bIS\s+RIO\b", "MINISTERIO", texto, flags=re.IGNORECASE)
       return texto
   ```

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `firma.py` extraiga limpiamente `JUAN DIEGO IZQUIERDO HEVIA, DIVISIÓN DE DESARROLLO URBANO, MINISTERIO DE VIVIENDA Y URBANISMO` sin receptores de distribución.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 comprobando la celda `firmante` en la Fila 12.
