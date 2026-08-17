# Instrucciones Operativas para la IA (GEMINI.md)

Este archivo contiene las directrices de diseño, reglas específicas y el contexto técnico del **Proyecto Biblioteca Normativa Circulares** destinadas a guiar a la IA (Antigravity CLI) en el mantenimiento y desarrollo del código.

## Reglas Críticas para la IA

### 1. Mantenimiento y Cobertura de la Suite de Pruebas

- **Cobertura Obligatoria del 100%**: Cualquier cambio en la estructura o lógica de los scripts de transformación debe validarse de inmediato y mantener siempre una cobertura del **100%** de los elementos declarados en los esquemas y diccionarios BCN.

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

- **Cumplimiento de Estándar `.github`**: Para cualquier creación, edición o visualización de diagramas de arquitectura, secuencias ETL o flujos de procesos del proyecto, se deben seguir estrictamente las directrices definidas en [`.github/instructions/mermaid.instructions.md`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/.github/instructions/mermaid.instructions.md).
- **Archivos `.mmd` y Validación de Sintaxis**: Todos los diagramas deben escribirse o persistirse en archivos con extensión `.mmd` en el proyecto y validar la sintaxis (flechas, corchetes balanceados, palabras clave de inicio) antes de presentarlos al usuario.
