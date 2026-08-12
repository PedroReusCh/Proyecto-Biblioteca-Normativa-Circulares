# DDU 456 - Task 5: Actualización de config YAML con hallazgos

**Circular:** DDU 456 - Circular Ord. Nº 88 (25 FEB 2021) - Elementos Exteriores en Edificios
**Archivo actualizado:** `ddu456_extractor_config.yaml`
**Fecha:** 12 de agosto de 2026
**Rama:** feature/ddu-456-elementos-exteriores-edificios

## Objetivo

Consolidar en el archivo de configuración YAML los hallazgos de los Tasks 2
(análisis manual, 12 bloques) y 3 (validación de extracción, 5 campos vacíos),
asignando status a cada bloque, documentando ajustes y nuevos ETLs, y agregando
una sección de resumen con totales.

## Mapping de bloques y status final

| Bloque | Status | Motivo |
|--------|--------|--------|
| encabezado | OK | Presente en pág. 1, sin ajustes. |
| acto_administrativo | OK | "CIRCULAR ORD. Nº 88 /" en pág. 1. |
| antecedentes | PARCIAL | Sin sección rotulada; referencias embebidas en el cuerpo. Campo vacío (100%). |
| materia | OK | Campo "MAT.:" con descripción extensa. |
| descriptores | PARCIAL | Presentes en el PDF pero extraídos vacíos (100%); requieren parseo por ";" y ",". |
| fecha_lugar | OK | "SANTIAGO, 25 FEB 2021"; normalizar fecha. |
| destinatarios | OK | "A : SEGÚN DISTRIBUCIÓN." |
| emision | OK | "DE : JEFE DIVISIÓN DE DESARROLLO URBANO." |
| cuerpo | OK | Numerales 1-7; maneja estructuras anidadas y deriva tabla/esquema a ETLs. |
| nota_al_pie | PARCIAL | No hay pies clásicos; notas al margen (DDU 498). Campo vacío (100%). |
| firma | OK | Firma y rúbrica "JPB" en pág. 8. |
| distribucion | OK | Lista numerada de 34 destinatarios (págs. 8-9). |

## Correlación con validación de extracción (Task 3)

5 campos se extrajeron vacíos (100%):

| Campo vacío | Bloque/estructura asociada | Cobertura propuesta |
|-------------|----------------------------|---------------------|
| antecedentes | antecedentes | etl_referencias |
| referencias | antecedentes | etl_referencias |
| elementos_visuales | esquema_ilustrativo (estructura nueva) | Diferir a próxima iteración |
| descriptores | descriptores | ajuste de parseo (";" / ",") |
| notas_al_pie | nota_al_pie / notas_al_margen | etl_notas_marginales |

## Estructuras nuevas detectadas

1. **Esquema ilustrativo (pág. 3):** PLANTA AZOTEA y CORTE ESQUEMÁTICO "Sin Escala".
2. **Tabla de modificaciones (págs. 5-8):** tres columnas, se extiende entre páginas.
3. **Notas al margen:** trazabilidad de modificaciones por Circular Ord. Nº 214 / DDU 498.

## Nuevos ETLs documentados

1. **etl_tabla_modificaciones** — reconstruye la tabla de 3 columnas (págs. 5-8)
   respetando saltos de página (pdfplumber). Alimenta `cuerpo`.
2. **etl_notas_marginales** — captura notas al margen y las asocia al numeral del
   cuerpo. Alimenta `nota_al_pie` / `notas_al_pie`.
3. **etl_referencias** — detecta referencias normativas por patrones para poblar
   `antecedentes` / `referencias`.

## Resumen (totales)

- Total bloques: **12**
- OK: **9**
- PARCIAL: **3** (antecedentes, descriptores, nota_al_pie)
- NO_APLICA: **0**
- ERROR: **0**
- Campos vacíos en extracción: **5**
- Estructuras nuevas detectadas: **3**
- Nuevos ETLs requeridos: **3**

## Validación

El archivo `ddu456_extractor_config.yaml` fue validado con `yaml.safe_load()`
(Python 3.13): carga correctamente, 12 bloques, 9 OK / 3 PARCIAL, 3 ETLs nuevos.
