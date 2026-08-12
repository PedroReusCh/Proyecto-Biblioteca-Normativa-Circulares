# Instrucciones Operativas para la IA

Este archivo contiene las directrices de diseño, reglas específicas y el contexto técnico del **Proyecto Biblioteca Normativa Circulares** destinadas a guiar a la IA (Antigravity CLI) en el mantenimiento y desarrollo del código.

## Contexto y Flujo del Proyecto

El objetivo principal es tomar circulares DDU (División de Desarrollo Urbano del MINVU, Chile) en formato PDF y procesarlas para generar documentos semánticos de forma 100% dinámica sobre el texto extraído:

1. **Extracción y Estructuración Modular**: Paquete de ETLs modulares e independientes [`scripts/extractors/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/) coordinados por el orquestador central [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py) (`DDUOrchestrator`). Los datos extraídos se mantienen en un formato tabular de dominio plano intuitivo (CSV de circulares), manteniendo la extensibilidad para incorporar dinámicamente nuevos bloques o campos normativos a medida que la estructura de las circulares evolucione en el tiempo. El módulo [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) actúa como wrapper de retrocompatibilidad.
2. **Generación Akoma Ntoso XML**: [`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py) transforma la capa de datos de dominio al estándar XML Akoma Ntoso v2.0 BCN compatible con el validador oficial.
3. **Generación RDF (Turtle)**: [`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py) mapea los metadatos a grafos semánticos RDF.

## Flujo de Trabajo (Workflow) con Plugin Superpowers

Para garantizar la correcta ejecución y orden lógico durante el ciclo de vida del desarrollo usando el plugin `superpowers`, el asistente DEBE seguir este flujo de trabajo por fases:

### Fase 1: Inicio y Contexto (Secuencial)

1. **`/using-superpowers`**: Obligatorio al iniciar para establecer las reglas del juego y habilitar las skills.
2. **`/brainstorming`**: Antes de planear, entender la intención, requerimientos y diseño.
3. **`/writing-plans`**: Redactar el plan de acción paso a paso.
4. **`/using-git-worktrees`**: Aislar el entorno en un worktree antes de comenzar a modificar código.

### Fase 2: Ejecución (Iterativa)

1. **`/executing-plans`**: Contenedor principal. Inicia la ejecución del plan. Dentro de la ejecución aplicas:
   * **`/test-driven-development`**: Metodología paso a paso para desarrollar cada característica del plan.
   * **`/subagent-driven-development`**: Ejecutar tareas independientes del plan con subagentes en paralelo cuando no haya dependencias secuenciales.
   * *Condicionales:*
     * **`/dispatching-parallel-agents`**: Despachar 2+ tareas independientes en paralelo cuando no haya estado compartido ni dependencias secuenciales.
   *Reactivo:* Ante errores inesperados o fallos en tests durante la ejecución, interrumpir e invocar **`/systematic-debugging`**.

### Fase 3: Verificación y Calidad

1. **`/verification-before-completion`**: Al finalizar el código, verificar rigurosamente (tests, linting) antes de afirmar que está listo.
2. **`/requesting-code-review`**: Solicitar revisión del código (PR) una vez que todo funciona.
3. **`/receiving-code-review`**: Procesar el feedback recibido de la revisión rigurosamente, no de forma superficial.

### Fase 4: Cierre

1. **`/finishing-a-development-branch`**: Integrar los cambios, decidir cómo hacer merge/PR y limpiar el entorno de desarrollo.

## Reglas Críticas para la IA

### 1. Mantenimiento y Cobertura de la Suite de Pruebas

- **Cobertura Obligatoria del 100%**: Cualquier cambio en la estructura o lógica de los scripts de transformación debe validarse de inmediato y mantener siempre una cobertura del **100%** de los elementos declarados en los esquemas y diccionarios BCN.
- **Autonomía de Pruebas**: Los tests residen en la raíz del directorio `test/` y deben pasar en su totalidad mediante `pytest -v`:
  - [`test/test_extractor_base.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_base.py): Pruebas de la interfaz base `BaseExtractor` y `ExtractorRegistry`.
  - [`test/test_extractor_metadata.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_metadata.py): Pruebas unitarias de los 8 extractores de metadatos.
  - [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py): Pruebas unitarias de los extractores de cuerpo, firma y distribución.
  - [`test/test_extractor_nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_nota_al_pie.py): Pruebas unitarias del extractor del metadato Nota al Pie.
  - [`test/test_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_orchestrator.py): Pruebas de integración del orquestador DDU y exportadores CSV.
  - [`test/test_csv_integrity.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_csv_integrity.py): Valida la coherencia columnar de los archivos CSV locales.
  - [`test/test_spec_coverage.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_spec_coverage.py): Mapea elementos XSD contra el diccionario y contra el archivo de cobertura local.
  - [`test/test_xsd_structural_validation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_xsd_structural_validation.py): Verifica tipos y atributos heredados entre XSD y CSV.
  - [`test/test_xml_generation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_xml_generation.py): Certifica que los XML construidos sean válidos.
  - [`test/test_rdf_generation.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_rdf_generation.py): Valida la sintaxis del formato Turtle (RDF).

### 2. Extracción 100% Dinámica (Prohibición de Fallbacks Estáticos)

- Toda extracción de metadatos y cuerpo debe ser realizada **dinámicamente desde el contenido textual del PDF**. Está prohibido inyectar metadatos estáticos hardcodeados mediante archivos JSON o diccionarios estáticos.

### 3. Normalización y URIs

- Al generar identificadores normalizados para URIs, se debe seguir estrictamente la función `normalizar_uri` implementada en [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py).

### 4. Exclusión de Datos Estructurados y PDFs

- **Prohibición de Control de Versiones**: Ningún archivo con extensión `.xlsx`, `.xls`, `.pdf` o `.csv` debe formar parte del repositorio Git.

### 5. Idioma Obligatorio (Interacciones y Commits)

- **Idioma Único**: Toda la comunicación, explicaciones, preguntas y respuestas con el usuario deben generarse exclusivamente en **español**.
- **Mensajes de Commit**: Todos los mensajes de confirmación (commits) generados para Git por la IA deben redactarse exclusivamente en **español**.

### 6. Calidad de Código y Tipado Estricto (Pylance Strict Mode)

- **Cumplimiento Obligatorio en Scripts y Tests**: Todo el código de producción ([`scripts/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/)) y todos los archivos de la suite de pruebas ([`test/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/)) deben cumplir estrictamente con el estándar **Pylance Strict Mode** configurado en [`.vscode/settings.json`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.vscode/settings.json) (`python.analysis.typeCheckingMode: strict`).
- **Cero Advertencias o Errores de Tipado**: Ningún archivo Python del proyecto debe generar diagnósticos de Pylance/Pyright (`reportMissingImports`, `reportUnknownVariableType`, `reportUnknownMemberType`, `reportUnknownArgumentType`, `reportRedeclaration`, etc.).
- **Preferencia de Código Limpio**: Se debe dar preferencia a importaciones estructuradas, tipados explícitos mediante `typing` y librerías nativas por sobre el uso de comentarios de supresión estática (`# pyright: ignore`).

### 7. Trazabilidad y Evidencia

- Antes de cerrar cualquier tarea técnica, reporta el comando exacto ejecutado en la consola y la salida del test como evidencia empírica de funcionamiento.
- Cualquier modificación debe quedar debidamente descrita en [`CHANGELOG.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/CHANGELOG.md).

### 8. Generación y Validación de Diagramas de Arquitectura (Mermaid AI Skills)

- **Cumplimiento de Estándar `.github`**: Para cualquier creación, edición o visualización de diagramas de arquitectura, secuencias ETL o flujos de procesos del proyecto, se deben seguir estrictamente las directrices definidas en [`.github/instructions/mermaid.instructions.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.github/instructions/mermaid.instructions.md) y [`.github/copilot-instructions.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.github/copilot-instructions.md).
- **Archivos `.mmd` y Validación de Sintaxis**: Todos los diagramas deben escribirse o persistirse en archivos con extensión `.mmd` en el proyecto y validar la sintaxis (flechas, corchetes balanceados, palabras clave de inicio) antes de presentarlos al usuario.
