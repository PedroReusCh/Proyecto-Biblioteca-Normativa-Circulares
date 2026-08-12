# Instrucciones para Copilot

## Resumen del proyecto

Este repositorio procesa circulares DDU del MINVU desde PDF para generar salidas estructuradas en CSV, XML Akoma Ntoso BCN y RDF/Turtle. La base del sistema es un conjunto de extractores modulares en `scripts/extractors/`, coordinados por `scripts/ddu_orchestrator.py` y reutilizados por `scripts/ddu_parser.py`. Los transformadores de exportación viven en `scripts/ddu_to_xml.py` y `scripts/ddu_to_rdf.py`.

## Comandos útiles

### Pruebas

- Suite completa: `pytest -v`
- Un archivo concreto: `pytest -v test/test_orchestrator.py`
- Un caso concreto: `pytest -v test/test_orchestrator.py -k "nombre_del_test"`

### Ejecución

- Extraer y exportar CSV: `py -3 scripts\ddu_orchestrator.py --pdf "circulares\DDU 531.pdf" --export-csv`
- Generar XML Akoma Ntoso: `py -3 scripts\ddu_to_xml.py`
- Generar RDF Turtle: `py -3 scripts\ddu_to_rdf.py`

### Dependencia externa

- Dependencia externa principal: `pypdf`

## Arquitectura de alto nivel

- Los PDFs se leen y se descomponen con extractores independientes registrados dinámicamente.
- `DDUOrchestrator` coordina la extracción, consolida la salida CSV y alimenta los exportadores posteriores.
- `DDUParser` mantiene compatibilidad con APIs antiguas y delega el trabajo real al orquestador.
- La capa intermedia usa un modelo de datos plano; después se traduce a Akoma Ntoso XML y RDF/Turtle.

## Convenciones clave

- La extracción debe ser 100% dinámica desde el texto del PDF; no agregar metadatos estáticos ni diccionarios de fallback.
- Para normalizar URIs, usar la lógica de `normalizar_uri` definida en `scripts/ddu_parser.py`.
- La configuración de pruebas usa `pytest.ini` con `pythonpath = . scripts`.
- Mantener tipado estricto compatible con Pylance en `scripts/` y `test/`.
- No versionar archivos `.csv`, `.xlsx`, `.xls` ni `.pdf`.
- Toda comunicación y mensajes de commit deben ir en español.
- Los diagramas Mermaid deben guardarse como `.mmd` y validarse antes de mostrarlos.
