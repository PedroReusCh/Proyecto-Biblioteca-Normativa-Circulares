# Documento de Diseño: Estructura de Presentación Ejecutiva (PPT)

**Fecha:** 2026-08-06  
**Proyecto:** Biblioteca Normativa Circulares DDU  
**Audiencia:** Ejecutiva / Directiva (Enfoque en Valor Institucional, RAG y Hoja de Ruta de Integración)

---

## 🎯 Objetivo de la Presentación

Comunicar a nivel directivo y estratégico la solución desarrollada para transformar circulares DDU en formatos semánticos (**Akoma Ntoso XML BCN** y **Grafos RDF Turtle**), con el propósito de resolver los problemas de calidad de respuesta del sistema **RAG** en el aplicativo **"Biblioteca Normativa"** enfocado en las Direcciones de Obras Municipales (DOM).

---

## 📐 Estructura de la Presentación (5 Diapositivas Clave)

### Diapositiva 1: Portada
* **Título**: Proyecto Biblioteca Normativa Circulares DDU
* **Subtítulo**: Estructuración Semántica (Akoma Ntoso XML & Grafos RDF) para la Potenciación del Agente AI Legal de las DOM.

---

### Diapositiva 2: El Desafío Institucional y el Agente "Biblioteca Normativa" (DOM)
* **Contexto**: El sistema actual del proyecto "Biblioteca Normativa" opera mediante arquitectura **RAG (Retrieval-Augmented Generation)**, pero la calidad general de las respuestas entregadas a las DOM es mala debido a la falta de estructura de la información ingresada.
* **Comparativo Visual**:
  * **Antes (Documentos No Estructurados con RAG)**: La ingesta tradicional de textos planos o PDFs provoca fragmentación inadecuada, respuestas de baja calidad y falta de precisión jurídica.
  * **Con la Solución (Akoma Ntoso + Grafo RDF)**: Al incorporar circulares en formato Akoma Ntoso y su grafo semántico, el Agente consume una estructura clara, organizada y relaciones normativas definidas.

---

### Diapositiva 3: Arquitectura de Procesamiento y Flujo General End-to-End
* **Objetivo**: Presentar el pipeline de transformación completo a través de un esquema gráfico claro y sencillo.
* **Flujo de Proceso (5 Pasos)**:
  ```
  [1. PDF DDU] ➔ [2. Extractores ETL Modulares] ➔ [3. CSV Dominio] ➔ [4. Akoma XML BCN] ➔ [5. Grafo RDF]
  ```
* **Explicación**: Muestra de forma limpia el recorrido desde el documento PDF original hasta la capa de dominio (CSV), la estandarización jurídica (Akoma Ntoso XML BCN v2.0) y la red de conocimiento (Grafo RDF Turtle).

---

### Diapositiva 4: El Valor de la Estructuración Semántica (Akoma Ntoso + RDF)
* **Objetivo**: Sintetizar los dos pilares estratégicos de valor que la nueva estructura aporta al sistema.
* **Pilares de Valor**:
  * **Pilar 1: Estructura Jurídica Estándar (Akoma Ntoso BCN)**: Permite al Agente citar numerales, párrafos, notas al pie y descriptores exactos.
  * **Pilar 2: Red de Conocimiento Legal (Grafo RDF)**: Permite al Agente navegar las relaciones entre circulares.

---

### Diapositiva 5: Próximos Pasos e Hoja de Ruta de Integración
* **Objetivo**: Definir las fases inmediatas de acoplamiento al aplicativo y evaluación por parte del equipo de negocio.
* **Fases del Roadmap**:
  1. **Fase 1 (Integración Inicial y Evaluación de Rendimiento)**: El equipo técnico acopla la nueva estructura (Akoma Ntoso y Grafo RDF actualmente construidos) al aplicativo "Biblioteca Normativa" como punto de partida. Posteriormente, el equipo interno de negocio genera pruebas de rendimiento para evaluar cómo responde el Agente ante esta nueva ingesta de información asociada a las circulares.
  2. **Fase 2 (Escalamiento y Complejidad)**: Profundizar y escalar la extracción procesando nuevas circulares DDU que posean variaciones estructurales más complejas.

---

## 📋 Registro de Aprobación

* **Estado del Diseño**: Validado y Aprobado por el Usuario.
* **Siguiente Paso**: Invocación de la skill `writing-plans` para elaborar el plan de acción detallado de redacción del contenido de la PPT.
