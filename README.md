# Proyecto Biblioteca Normativa Circulares

Este repositorio implementa un sistema para el procesamiento, análisis y enriquecimiento semántico de **Circulares DDU** (División de Desarrollo Urbano del Ministerio de Vivienda y Urbanismo, Chile), transformándolas a formatos abiertos compatibles con la Biblioteca del Congreso Nacional (BCN).

---

## Organización del Repositorio

El proyecto se estructura en los siguientes directorios clave:

* [`bcn - consultas/`](./bcn%20-%20consultas): Contiene los resultados de procesamiento semántico (.ttl, .xml) de las circulares de prueba.
* [`bcn - documentación/`](./bcn%20-%20documentaci%C3%B3n): Contiene la documentación técnica oficial de la BCN, los esquemas de validación estructural (`Esquema Akoma-Ntoso BCN.xsd`), la especificación de cobertura local (`especificacion_cobertura.md`), el contrato de especificación estructural ([`estructura_circular_ddu.csv`](./bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv)) y los CSVs del diccionario de datos y secuencia de plantilla.
* [`circulares/`](./circulares): Colección de circulares DDU originales en formato PDF (por ejemplo, DDU 531, 533, 537 y 546).
* [`salidas_csv/`](./salidas_csv): Colección de datos extraídos de circulares en formato tabular CSV de dominio plano.
* [`salidas_xml/`](./salidas_xml): Archivos XML Akoma Ntoso v2.0 BCN con segmentación atómica de numerales (`<num>`) y validación XSD.
* [`salidas_rdf/`](./salidas_rdf): Grafos semánticos RDF en sintaxis Turtle (`.ttl`) generados desde los CSVs.
* [`scripts/`](./scripts): Módulos funcionales de procesamiento y conversión:
  * [`ddu_types.py`](./scripts/ddu_types.py): Declaraciones de tipado estricto `DatosCircularDDU` y `SeccionDDU`.
  * [`extractors/`](./scripts/extractors): Paquete de ETLs modulares e independientes (`encabezado.py`, `acto_administrativo.py`, `antecedentes.py`, `materia.py`, `descriptores.py`, `fecha_lugar.py`, `destinatarios.py`, `emisor.py`, `cuerpo.py`, `imagen.py`, `tabla.py`, `nota_al_pie.py`, `firma.py`, `distribucion.py`) derivados de la interfaz base `BaseExtractor`. Este conjunto es evolutivo y puede ampliarse o ajustarse según nuevas circulares y nuevos bloques normativos.
  * [`ddu_orchestrator.py`](./scripts/ddu_orchestrator.py): Orquestador central (`DDUOrchestrator`) que coordina los extractores registrados y exporta CSVs.
  * [`ddu_parser.py`](./scripts/ddu_parser.py): Wrapper de retrocompatibilidad apuntando al orquestador.
  * [`ddu_to_xml.py`](./scripts/ddu_to_xml.py): Generador estructurado XML bajo el estándar Akoma Ntoso v2.0 BCN.
  * [`csv_to_akoma_xml.py`](./scripts/csv_to_akoma_xml.py): Transformador independiente especializado que convierte CSVs a XML Akoma Ntoso v2.0 BCN con segmentación atómica de numerales `<num>`.
  * [`csv_to_rdf.py`](./scripts/csv_to_rdf.py): Transformador independiente especializado que convierte CSVs a grafos RDF Turtle (`.ttl`).
  * [`ddu_to_rdf.py`](./scripts/ddu_to_rdf.py): Constructor semántico RDF/Turtle.
  * [`leychile_api.py`](./scripts/leychile_api.py): Integración oficial con la API de Ley Chile de la BCN.
* [`test/`](./test): Suite plana de pruebas automatizadas locales (`test_csv_to_akoma_xml.py`, `test_csv_to_rdf.py`, `test_extractor_base.py`, `test_extractor_metadata.py`, `test_extractor_body.py`, `test_extractor_nota_al_pie.py`, `test_orchestrator.py`, `test_csv_integrity.py`, `test_spec_coverage.py`, `test_xml_generation.py`, `test_rdf_generation.py`, `test_xsd_structural_validation.py`) ejecutables con `pytest`.



---

## Modelo de Datos de Dominio y Extensibilidad Evolutiva

El proyecto adopta una **arquitectura en capas con separación clara de responsabilidades**:

1. **Capa de Dominio Plano e Intuitivo (CSV)**:
   Los datos extraídos se organizan bajo términos de dominio claros y legibles para analistas e ingenieros de datos (`numero_ddu`, `fecha_emision`, `cuerpo`, `firmante`, etc.) en formato CSV. Esto preserva la claridad humana y evita sobrecargar la extracción con nombres técnicos abstractos del estándar XML.
2. **Capa de Interoperabilidad Semántica (Akoma Ntoso XML & RDF)**:
   Los módulos [`scripts/ddu_to_xml.py`](./scripts/ddu_to_xml.py) y [`scripts/ddu_to_rdf.py`](./scripts/ddu_to_rdf.py) actúan como traductores que mapean automáticamente los campos de dominio a la taxonomía XML Akoma Ntoso v2.0 BCN (`FRBRWork`, `FRBRnumber`, `docDate`, `mainBody`, `authorialNote`) y a grafos semánticos RDF/Turtle.
3. **Extensibilidad Evolutiva del Pipeline ETL**:
   A medida que las circulares DDU evolucionen o incorporen nuevos bloques normativos en el futuro, es posible registrar nuevos extractores en [`scripts/extractors/`](./scripts/extractors) mediante el decorador `@register_extractor`. El orquestador [`scripts/ddu_orchestrator.py`](./scripts/ddu_orchestrator.py) incorporará los nuevos campos al CSV sin alterar el código existente ni romper la generación Akoma Ntoso. La cantidad de ETLs no se considera cerrada.

---

## Mapeo Estandarizado de la Estructura (CSV -> ETLs)

La suite base de ETLs modulares deriva exactamente del contrato de especificación documentado en [`bcn - documentación/estructura_circular_ddu.csv`](./bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv), simplificado a **6 columnas esenciales** (`orden`, `bloque`, `campo`, `obligatorio`, `descripcion`, `reglas`). Ese contrato describe el núcleo actual, pero el pipeline admite extensión con nuevos ETLs cuando una circular lo exija:

| Bloque CSV | Campo Parser | Módulo ETL (`scripts/extractors/`) | Descripción |
| :--- | :--- | :--- | :--- |
| **Encabezado** | `numero` | `encabezado.py` | Número identificador de la circular DDU |
| **Acto Administrativo** | `numero_ord` | `acto_administrativo.py` | Número de acto ordinario de emisión (ej. ORD. N° 112) |
| **Antecedentes** | `antecedentes` | `antecedentes.py` | Documentos o definiciones de origen (ANT:) |
| **Materia** | `materia` | `materia.py` | Descripción del tema o norma abordada (MAT:) |
| **Descriptores** | `descriptores` | `descriptores.py` | Vocablos y palabras clave de catalogación |
| **Fecha y Lugar** | `fecha_emision` | `fecha_lugar.py` | Fecha en formato ISO YYYY-MM-DD y ciudad |
| **Destinatarios** | `destinatarios` | `destinatarios.py` | Destinatario formal del oficio (A:) |
| **Emisión** | `emisor` | `emisor.py` | Cargo del emisor (DE:) |
| **Cuerpo** | `secciones` | `cuerpo.py` | Estructura de secciones romanas, numerales y listas |
| **Nota al Pie** | `notas_al_pie` | `nota_al_pie.py` | Notas aclaratorias o referencias normativas al pie de página |
| **Firma** | `firmante` | `firma.py` | Firma del Jefe de División |
| **Distribución** | `lista_distribucion` | `distribucion.py` | Nómina de receptores al cierre del documento |

---

## Arquitectura de Procesamiento Modular (ETLs y Orquestador)

```mermaid
graph TD
    subgraph "Entrada"
        PDF[PDF Circular DDU]
    end

    subgraph "Paquete ETL (scripts/extractors/)"
        Base[base.py: BaseExtractor & Registry]
        Base --> Ext1[encabezado.py]
        Base --> Ext2[acto_administrativo.py]
        Base --> Ext3[antecedentes.py]
        Base --> Ext4[materia.py]
        Base --> Ext5[descriptores.py]
        Base --> Ext6[fecha_lugar.py]
        Base --> Ext7[destinatarios.py]
        Base --> Ext8[emisor.py]
        Base --> Ext9[cuerpo.py]
        Base --> Ext10[nota_al_pie.py]
        Base --> Ext11[firma.py]
        Base --> Ext12[distribucion.py]
    end

    subgraph "Orquestación y Salidas (scripts/ddu_orchestrator.py)"
        PDF --> Orch[DDUOrchestrator]
        Ext1 & Ext2 & Ext3 & Ext4 & Ext5 & Ext6 & Ext7 & Ext8 & Ext9 & Ext10 & Ext11 & Ext12 --> Orch
        Orch --> Data[DatosCircularDDU]
        Data --> CSVInd[CSV Individual Circular]
        Data --> CSVMaster[Dataset CSV Acumulado Master]
        Data --> XML[ddu_to_xml.py]
        Data --> RDF[ddu_to_rdf.py]
    end
```

---

## Guía de Ejecución y Visualización de Resultados

### 1. Ejecución de ETLs de Forma Independiente (CLI)

Si deseas probar la extracción de **un bloque específico** sobre cualquier circular (ej. `DDU 531.pdf`):

```powershell
py -3 -m scripts.extractors.materia --pdf "circulares/DDU 531.pdf"
```

* **Salida / Visualización**: Imprime en consola un JSON estructurado (`ResultadoBloque`) con el resultado del bloque y su nivel de confianza.

### 2. Ejecución Orquestada Completa (Generación de CSV)

Para procesar todos los ETLs y exportar la ficha CSV de la circular:

```powershell
py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 531.pdf" --export-csv
```

* **Salida / Visualización**: Genera un archivo CSV codificado en UTF-8 con BOM y delimitado por punto y coma (`;`) listo para MS Excel en la carpeta `salidas_csv/` (ej. [`salidas_csv/DDU_531_extraido.csv`](./salidas_csv/DDU_531_extraido.csv)).
* El CSV individual conserva bloques atómicos por extractor, incluyendo los nuevos bloques independientes `Imagen` y `Tabla` cuando la circular los contiene.
* Cuando existe bloque `Imagen`, el ETL exporta el PNG asociado en `salidas_imagenes/` y usa convención de enlace estable en CSV: `DDU_<n>_imagen_<nombre_normalizado>` (mismo valor para `id_imagen` y base de `archivo`).

---

## Dependencias e Instalación

Este proyecto utiliza módulos estándar de Python 3 y requiere la siguiente dependencia externa:

* **pypdf**: Librería de extracción de texto y parseo de PDF.

Para verificar o instalar dependencias, ejecute:

```powershell
pip install pypdf
```

---

## Ejecución de la Suite de Pruebas

Para garantizar que el sistema y sus modelos semánticos de datos cumplen al 100% con los contratos estructurales definidos por el XSD, los CSV de la BCN y la suite de extractores, ejecute en la raíz del repositorio:

```powershell
pytest -v
```

Actualmente, **42 de 42 pruebas pasan exitosamente** (100% de cobertura de la suite en estructura plana).

---

## Análisis de Circulares: DDU 456 (Elementos Exteriores en Edificios)

Como parte de la ampliación evolutiva del pipeline, se realizó el análisis de extracción de la **Circular DDU 456** (Orden Ord. Nº 88, 25 FEB 2021, sobre terrazas y elementos exteriores ubicados en la parte superior de los edificios y pisos mecánicos). El detalle completo se documenta en [`reports/ddu456_analysis_report.md`](./reports/ddu456_analysis_report.md).

### Resultados

* **Cobertura de bloques**: 9 de 12 bloques completamente funcionales (**✓**); 3 de 12 bloques en estado **⚠️ Parcial** (Antecedentes: embebido en el cuerpo sin sección rotulada; Descriptores: presente en PDF pero extraído vacío; Nota al Pie: notas al margen de trazabilidad). Todos los bloques aplican (0 NO_APLICA).
* **Tasa de cobertura de campos**: **~72%** (13 de 18 campos con datos; 5 vacíos).
* **Estructuras nuevas detectadas**: tabla de modificaciones a otras circulares (págs. 5–8), esquema ilustrativo (pág. 3) y notas al margen de trazabilidad.
* **CSV estándar**: `salidas_csv/DDU_456_extraido.csv` con columnas `bloque`, `campo`, `valor_extraido`, igual al resto de circulares exportadas por el orquestador.

### Nuevos ETLs sugeridos

A partir de estos hallazgos se proponen **3 nuevos ETLs** para el paquete [`scripts/extractors/`](./scripts/extractors):

1. `etl_tabla_modificaciones`: reconstrucción de la tabla de tres columnas que abarca varias páginas.
2. `etl_notas_marginales`: captura de notas al margen de trazabilidad y su asociación al numeral del cuerpo.
3. `etl_referencias`: detección por patrones de referencias normativas para poblar el bloque Antecedentes.

Estos ETLs confirman el carácter evolutivo del pipeline: se integran mediante el decorador `@register_extractor` sin alterar el contrato de dominio ni la generación Akoma Ntoso.

---

## Flujo de Trabajo y Trazabilidad

Este proyecto exige **trazabilidad completa** de todas las modificaciones realizadas:

1. **Commit Local**: Toda tarea completada debe registrarse con un mensaje de commit descriptivo en español.
2. **Push a GitHub**: Los cambios se respaldan en el repositorio remoto para sincronización y auditoría.
3. **Actualización de Documentación**: Cada modificación se refleja inmediatamente en:
   - **`README.md`**: cambios arquitectónicos, estructurales y técnicos.
   - **`CHANGELOG.md`**: historial versionado según [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/).
   - **`.github/copilot-instructions.md`**: reglas operativas y convenciones.

El commit incluirá el trailer de co-autoría:
```
Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>
```

**La ausencia de commit, push o actualización de documentación indica que la tarea está incompleta.**
