# Documento de Diseño: Extracción de Nombre y Cargo en FirmaExtractor

**Fecha:** 2026-08-14  
**Autor:** Antigravity  
**Estado:** Aprobado (Opción 1)

---

## 1. Contexto y Objetivos

En las circulares DDU emitidas por el Ministerio de Vivienda y Urbanismo (MINVU), el bloque de cierre o firma institucional contiene dos elementos fundamentales:
1. **Nombre o identificador del firmante**: Ubicado típicamente en la línea o líneas inmediatamente superiores al cargo (ej. `"JUAN DIEGO IZQUIERDO HEVIA"`, `"VICENTE BURGOS BOLAÑOS"`, o siglas/rúbricas legibles en escaneos OCR como `"JPB"`).
2. **Cargo formal**: Cargo institucional de la autoridad (ej. `"Jefe División de Desarrollo Urbano"`, `"Ministro de Vivienda y Urbanismo"`).

El objetivo es asegurar que `FirmaExtractor` extraiga siempre de forma dinámica y estructurada tanto el `nombre_firmante` (buscando de forma prioritaria en las líneas situadas arriba del cargo) como el `cargo_firmante` y el consolidado `firmante`.

---

## 2. Lógica de Extracción (Opción 1)

1. **Detección del Saludo y Ventana de Firma**:
   - Localizar `"Saluda atentamente..."` o `"Atentamente"`.
   - Limpiar y recolectar las líneas hasta la sección de distribución o banner institucional.

2. **Identificación de Cargo**:
   - Detectar la línea que contiene el cargo (`Jefe División de Desarrollo Urbano`, `Director...`, etc.).
   - Normalizar la tipografía preservando casing.

3. **Extracción Prioritaria del Nombre Arriba del Cargo**:
   - Inspeccionar todas las líneas de `partes_firma` que preceden inmediatamente al cargo.
   - Si se encuentra un nombre de persona completo (ej. `"JUAN DIEGO IZQUIERDO HEVIA"`, `"VICENTE BURGOS"`), extraer y limpiar.
   - Si no hay un nombre completo pero sí una sigla/rúbrica alfabética identificable (ej. `JPB`, `J.P.B.`), extraerla como `nombre_firmante`.
   - Respaldo en cabecera `DE : ...` si no se encontró en la ventana de firma.

4. **Estructura de Retorno**:
   ```json
   {
     "firmante": "JPB, Jefe División de Desarrollo Urbano",
     "nombre_firmante": "JPB",
     "cargo_firmante": "Jefe División de Desarrollo Urbano"
   }
   ```

---

## 3. Criterios de Aceptación y Pruebas

1. `circulares/DDU 456.pdf`: `nombre_firmante == "JPB"`, `cargo_firmante == "Jefe División de Desarrollo Urbano"`, `firmante == "JPB, Jefe División de Desarrollo Urbano"`.
2. `circulares/DDU 546.pdf`: `nombre_firmante == "JUAN DIEGO IZQUIERDO HEVIA"`, `cargo_firmante == "DIVISIÓN DE DESARROLLO URBANO, MINISTERIO DE VIVIENDA Y URBANISMO"`.
3. Casos sintéticos con nombre y cargo en líneas separadas.
4. Cobertura del 100% en la suite de pruebas `pytest -v`.
