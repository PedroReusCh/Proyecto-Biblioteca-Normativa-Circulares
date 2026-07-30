# Especificación de Diseño: Componente "Nota al Pie" (`notas_al_pie`)

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

El proyecto extrae de forma modular 11 bloques de información normativos de las circulares DDU impresas/PDF. Se requiere incorporar un nuevo componente estructurado denominado **Nota al Pie** (`notas_al_pie`) para capturar las referencias normativas, aclaraciones y notas explicativas al pie de página (ej. `1 Artículo 38...`, `2 La orientación técnica...`).

---

## 2. Ubicación en la Estructura del CSV (`estructura_circular_ddu.csv`)

El bloque se inserta como fila de orden **10** (tras el bloque 9 *Cuerpo*), reordenando *Firma* a 11 y *Distribución* a 12.

| orden | bloque | campo | obligatorio | descripcion | reglas |
| :---: | :--- | :--- | :---: | :--- | :--- |
| **9** | Cuerpo | `cuerpo` | si | Contenido estructurado del cuerpo de la circular | Secciones numeradas en romano o arábigos y listas anidadas |
| **10** | Nota al Pie | `notas_al_pie` | no | Notas aclaratorias o referencias normativas al pie de página | Notas explicativas o referencias numeradas al pie de las páginas de la circular |
| **11** | Firma | `firmante` | si | Firma del jefe de división respectivo | Jefe de división del periodo de emisión |
| **12** | Distribución | `lista_distribucion` | si | Lista de personas que reciben copia de la circular | Lista de distribución de la circular |

---

## 3. Arquitectura y Cambios Técnicos

### 3.1 Módulo de Tipos (`scripts/ddu_types.py`)
Se extiende el `TypedDict` `DatosCircularDDU`:
```python
class DatosCircularDDU(TypedDict):
    ...
    notas_al_pie: NotRequired[str]
```

### 3.2 Extractor Modular (`scripts/extractors/nota_al_pie.py`)
- **Clase**: `NotaAlPieExtractor(BaseExtractor)` decorada con `@register_extractor`.
- **Lógica de Extracción**: Escanea las líneas del documento detectando párrafos de pie de página que inician con número superíndice o prefijo numérico aislado (ej. `1 Artículo 38. Lineamientos...`, `2 La orientación técnica...`) ubicados inmediatamente antes del membrete institucional de pie de página.
- **Soporte CLI**: Incluye ejecutable standalone con `--pdf`.

### 3.3 Orquestador (`scripts/ddu_orchestrator.py`)
- Incluye el bloque `nota_al_pie` en la consolidación y exportación de CSV individual y maestro.

### 3.4 Suite de Pruebas y Validación
- Nuevo test unitario `test/extractors/test_nota_al_pie_extractor.py`.
- Actualización de `test/test_csv_integrity.py` para validar 12 filas en `estructura_circular_ddu.csv`.

---

## 4. Criterios de Aceptación
1. `pytest -v` pasa al 100% con las 12 filas registradas en `estructura_circular_ddu.csv`.
2. DDU 537 extrae exitosamente sus 2 notas al pie en el archivo CSV resultante [`salidas_csv/DDU_537_extraido.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_csv/DDU_537_extraido.csv).
