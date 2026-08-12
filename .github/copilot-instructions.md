# Instrucciones para Copilot

## Contexto

Repositorio para procesar circulares DDU desde PDF y convertirlas a CSV, XML Akoma Ntoso BCN y RDF/Turtle. La cadena principal es: extractores modulares en `scripts/extractors/` → `scripts/ddu_orchestrator.py` → `scripts/ddu_parser.py` → `scripts/ddu_to_xml.py` / `scripts/ddu_to_rdf.py`.

## Comandos

- Pruebas completas: `pytest -v`
- Prueba puntual: `pytest -v test/test_orchestrator.py`
- Caso puntual: `pytest -v test/test_orchestrator.py -k "nombre_del_test"`
- Extraer y exportar CSV: `py -3 scripts\ddu_orchestrator.py --pdf "circulares\DDU 531.pdf" --export-csv`
- Generar XML: `py -3 scripts\ddu_to_xml.py`
- Generar RDF: `py -3 scripts\ddu_to_rdf.py`

## Arquitectura

- Los PDFs se leen con extractores independientes registrados dinámicamente.
- `DDUOrchestrator` arma el resultado tabular y coordina exportaciones.
- `DDUParser` conserva compatibilidad y delega en el orquestador.
- La capa de dominio es plana; luego se traduce a Akoma Ntoso XML y RDF/Turtle.

## Convenciones

- La extracción debe ser 100% dinámica; no usar metadatos estáticos ni fallbacks hardcodeados.
- Para URIs normalizadas, usar `normalizar_uri` de `scripts/ddu_parser.py`.
- `pytest.ini` define `pythonpath = . scripts`.
- Mantener tipado estricto compatible con Pylance en `scripts/` y `test/`.
- No versionar `.csv`, `.xlsx`, `.xls` ni `.pdf`.
- Toda solicitud de cambio debe actualizar `README.md`, `CHANGELOG.md` y, si aplica, `\.github\copilot-instructions.md`.
- Toda modificación o creación debe quedar comiteada y respaldada en GitHub.
- Todo comentario al usuario y mensajes de commit van en español.
- Los diagramas Mermaid deben guardarse como `.mmd` y validarse antes de mostrarse.
