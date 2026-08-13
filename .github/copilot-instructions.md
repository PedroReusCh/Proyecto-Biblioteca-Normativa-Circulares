# Instrucciones para Copilot

## Contexto

Repositorio para procesar circulares DDU desde PDF y convertirlas a CSV, XML Akoma Ntoso BCN y RDF/Turtle. La cadena principal es: extractores modulares en `scripts/extractors/` → `scripts/ddu_orchestrator.py` → `scripts/ddu_parser.py` → `scripts/ddu_to_xml.py` / `scripts/ddu_to_rdf.py`.

El sistema parte con un conjunto base de ETLs independientes, pero la estructura es evolutiva: a medida que se incorporen nuevas circulares, pueden agregarse, ajustarse o reemplazarse extractores sin romper el orquestador ni el contrato de datos de dominio.

## Comandos

- Pruebas completas: `pytest -v`
- Prueba puntual: `pytest -v test/test_orchestrator.py`
- Caso puntual: `pytest -v test/test_orchestrator.py -k "nombre_del_test"`
- Extraer y exportar CSV: `py -3 scripts\ddu_orchestrator.py --pdf "circulares\DDU 531.pdf" --export-csv`
- Generar XML: `py -3 scripts\ddu_to_xml.py`
- Generar RDF: `py -3 scripts\ddu_to_rdf.py`

## Arquitectura

- Los PDFs se leen con extractores independientes registrados dinámicamente.
- `DDUOrchestrator` arma el resultado tabular, consolida metadatos y coordina exportaciones.
- `DDUParser` conserva compatibilidad y delega en el orquestador.
- La capa de dominio es plana; luego se traduce a Akoma Ntoso XML y RDF/Turtle.
- El conjunto de extractores no es cerrado: el repositorio debe admitir nuevos ETLs modulares cuando cambie la estructura real de las circulares.

## Convenciones

- La extracción debe ser 100% dinámica; no usar metadatos estáticos ni fallbacks hardcodeados.
- Para URIs normalizadas, usar `normalizar_uri` de `scripts/ddu_parser.py`.
- `pytest.ini` define `pythonpath = . scripts`.
- Mantener tipado estricto compatible con Pylance en `scripts/` y `test/`.
- No versionar `.csv`, `.xlsx`, `.xls` ni `.pdf`.
- Toda solicitud de cambio debe actualizar `README.md`, `CHANGELOG.md` y, si aplica, `\.github\copilot-instructions.md`.
- La documentación y los tests deben reflejar que los extractores son ampliables y que la cantidad de ETLs puede variar según nuevas circulares y nuevos bloques normativos.
- Todo comentario al usuario y mensajes de commit van en español.
- Los diagramas Mermaid deben guardarse como `.mmd` y validarse antes de mostrarse.

## Proceso Estándar de Análisis de Nuevas Circulares

Al incorporar una nueva circular DDU al pipeline, seguir este proceso estándar:

1. **Análisis manual del PDF**: revisar la circular e identificar la presencia y estado de los 12 bloques normativos (completo **✓** o parcial **⚠️**), documentando estructuras inusuales (tablas multipágina, esquemas ilustrativos, notas al margen, etc.).
2. **Reporte de extracción**: generar un reporte en `reports/<circular>_analysis_report.md` con hallazgos generales, análisis por bloque (tabla), estructuras nuevas y ETLs sugeridos.
3. **Evaluación de cobertura**: calcular la tasa de cobertura de campos (campos con datos sobre el total esperado) y registrar los bloques parciales o vacíos.
4. **Propuesta de nuevos ETLs**: cuando la estructura real lo exija, proponer extractores adicionales integrables vía `@register_extractor` sin romper el orquestador ni el contrato de dominio.
5. **Salida CSV estándar**: el archivo individual debe llamarse `DDU_<n>_extraido.csv` y mantener siempre las columnas `bloque`, `campo`, `valor_extraido`, igual al resto de circulares exportadas.
6. **Actualización de documentación**: reflejar los resultados en `README.md` (sección de análisis de la circular) y `CHANGELOG.md` (entrada versionada), y ajustar estas instrucciones si cambian las convenciones.

**Referencia**: el análisis de la Circular DDU 456 en `reports/ddu456_analysis_report.md` sirve como plantilla de este proceso (9/12 bloques completos, 3/12 parciales (Antecedentes, Descriptores, Nota al Pie), ~72% de cobertura, 3 ETLs sugeridos, CSV estándar `DDU_456_extraido.csv`).

## Flujo de Trabajo (Trazabilidad y Persistencia)

**Por cada tarea completada:**

1. **Realizar commit en la rama**: Usar mensajes de commit descriptivos en español que resuman los cambios realizados. Incluir el trailer `Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>` al final del mensaje.
2. **Respaldar en GitHub**: Hacer push de los cambios al repositorio remoto para asegurar trazabilidad y sincronización con el repositorio principal.
3. **Actualizar documentación**: Toda modificación debe reflejarse inmediatamente en `README.md` (arquitectura/cambios técnicos), `CHANGELOG.md` (historial versionado) y `\.github\copilot-instructions.md` (instrucciones operativas).

**Nota**: La trazabilidad completa requiere que commit, push y actualización de documentación estén sincronizados en cada ciclo de trabajo.
