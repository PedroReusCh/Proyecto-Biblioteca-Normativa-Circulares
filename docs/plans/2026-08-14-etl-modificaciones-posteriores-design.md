# Documento de Diseño: ETL Modular `ModificacionesPosterioresExtractor` (Texto Libre)

## 1. Contexto y Objetivos

En circulares DDU históricas (como **DDU 456**), el MINVU estampa notas marginales de vigencia o timbres de modificación posterior cuando una circular posterior altera su contenido normativo:
> *"Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.)"*

### Objetivos:
1. **Descontaminar `CuerpoExtractor`**: Evitar que este texto se filtre dentro del Numeral 2 (o cualquier párrafo del cuerpo).
2. **Nuevo ETL Modular `ModificacionesPosterioresExtractor`**: Extraer estas notas como **texto libre** flexible y dinámico (sin asumir esquemas rígidos), capturando notas de modificación posterior, derogaciones o aclaraciones stamped a posteriori.

## 2. Arquitectura de la Solución

### 2.1. Nuevo Extractor: `ModificacionesPosterioresExtractor` (`scripts/extractors/modificaciones_posteriores.py`)
* **Nombre de bloque**: `modificaciones_posteriores`.
* **Estructura de datos (`ResultadoBloque`)**:
  ```python
  {
      "texto": "Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.)",
      "notas": [
          "Circular Modificada por Circular Ord. N°214, de fecha 02 de mayo de 2024, DDU 498 (numeral 7.)"
      ]
  }
  ```
* **Extracción**:
  * Busca patrones de notas marginales en el texto / primeras páginas:
    * `Circular\s+Modificada\s+por\b.+`
    * `Modificada\s+por\s+Circular\b.+`
    * `Dejada\s+sin\s+efecto\s+por\b.+`
    * `Aclarada\s+por\s+Circular\b.+`
  * Si no existen notas marginales de modificación: retorna `exito=False`, `datos={"texto": "", "notas": []}`.

### 2.2. Filtro en `CuerpoExtractor` (`scripts/extractors/cuerpo.py`)
* Se agrega `_es_nota_modificacion_posterior(line: str) -> bool` para descartar líneas que comiencen o contengan patrones como `Circular Modificada por...` o `Modificada por Circular...`.
* Se remueve cualquier remanente dentro de los párrafos del cuerpo.

### 2.3. Integración en el Orquestador y Modelos
* `scripts/ddu_types.py`: Se agrega `modificaciones_posteriores: Optional[str]` en `DatosCircularDDU`.
* `scripts/ddu_orchestrator.py`: Se incluye el bloque `Modificaciones Posteriores` en la exportación CSV.

## 3. Plan de Verificación

1. **`test/test_extractor_modificaciones_posteriores.py`**:
   * Prueba de registro en `ExtractorRegistry`.
   * Extracción en `circulares/DDU 456.pdf` verificando la captura como texto libre.
   * Prueba con documentos sin notas de modificación (retorna vacío y `exito=False`).
2. **`test/test_extractor_body.py`**:
   * Verificar que el Numeral 2 de DDU 456 no contenga `Circular Modificada por Circular Ord. N°214...`.
3. **`pytest -v`**: Suite completa pasando al 100%.
