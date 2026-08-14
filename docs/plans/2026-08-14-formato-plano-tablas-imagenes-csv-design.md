# Especificación de Diseño: Formato Plano Limpio para Tablas e Imágenes en CSV

**Fecha:** 2026-08-14  
**Rama:** `feature/ddu-456`  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Motivación

En las versiones anteriores del exportador CSV ([`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py)), los metadatos y manifiestos de los bloques `Tablas` e `Imágenes` se serializaban como cadenas JSON sin procesar:

```json
[{"id": "DDU_456_tabla_1", "nombre": "Modificaciones Normativas (DDU 339, DDU 322, DDU 168)", "paginas": [5, 6, 7, 8], "filas": 3, "columnas": 3, "archivo_anexo": "salidas_tablas/DDU_456_tabla_1.csv"}]
```

Esto generaba caracteres JSON redundantes (`[`, `]`, `{`, `}`, `"`) que dificultaban la lectura tabular directa y el consumo en hojas de cálculo.

---

## 2. Requerimientos de Diseño

1. **Eliminación Total de Sintaxis JSON**: Suprimir corchetes `[]`, llaves `{}` y comillas dobles internas `"` de las celdas de Tablas e Imágenes.
2. **Formato Clave-Valor con Delimitador `;`**:
   * Representar cada atributo como `clave: valor`.
   * Si un valor es una lista (ej. páginas `[5, 6, 7, 8]`), formatearlo como `5, 6, 7, 8`.
   * Separar los pares clave-valor dentro de un mismo elemento con `; `.
3. **Múltiples Elementos**: Si una circular contiene múltiples tablas o imágenes, separar cada elemento estructurado mediante ` || `.
4. **Módulo de Serialización Limpia**: Implementar una función utilitaria `formatear_manifiesto_plano(items: Any) -> str` en `scripts/ddu_orchestrator.py` (o `utils_cleaner.py`).

---

## 3. Especificación de Formatos de Salida

### A. Bloque Tablas (`tablas`)
Para la Circular DDU 456:
```text
id: DDU_456_tabla_1; nombre: Modificaciones Normativas (DDU 339, DDU 322, DDU 168); paginas: 5, 6, 7, 8; filas: 3; columnas: 3; archivo_anexo: salidas_tablas/DDU_456_tabla_1.csv
```

### B. Bloque Imágenes (`imagenes`)
Para la Circular DDU 456:
```text
id: DDU_456_img_1; nombre: Esquema ilustrativo: Planta azotea y corte esquemático; pagina: 3; tipo: Esquema técnico; formato: png; dimensiones: 2131x1906; ancho: 2131; alto: 1906; xref: 5; descripcion: Esquema ilustrativo: Planta azotea y corte esquemático; archivo_anexo: salidas_imagenes/DDU_456_img_1.png
```

---

## 4. Componentes y Flujo de Datos

1. [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py):
   * En `export_individual_csv()` y `export_master_csv()`, procesar los campos `tablas` e `imagenes` aplicando `formatear_manifiesto_plano()` antes de escribir las filas del CSV.
2. [`test/test_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_orchestrator.py):
   * Actualizar pruebas unitarias y de integración para validar la ausencia de `[`, `{`, `"`, `}` en los campos `tablas` e `imagenes` del CSV y confirmar el formato con `;`.
3. Regenerar [`salidas_csv/DDU_456_extraido.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_csv/DDU_456_extraido.csv) con el nuevo formato limpio.

---

## 5. Criterios de Éxito y Verificación

* `salidas_csv/DDU_456_extraido.csv` no contiene `[`, `]`, `{`, `}`, `"` en los valores de `tablas` e `imagenes`.
* Los pares clave-valor están separados por `; `.
* La suite completa de 77 pruebas pasa al 100% (`pytest -v`).
* Pylance Strict Mode con 0 diagnósticos de tipo.
