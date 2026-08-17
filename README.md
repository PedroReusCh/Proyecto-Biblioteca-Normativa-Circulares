# Proyecto Biblioteca Normativa Circulares

Este repositorio implementa un sistema para el procesamiento, análisis y enriquecimiento semántico de **Circulares DDU** (División de Desarrollo Urbano del Ministerio de Vivienda y Urbanismo, Chile), transformándolas a formatos abiertos compatibles con la Biblioteca del Congreso Nacional (BCN).

## Organización del Repositorio

El proyecto se estructura en los siguientes directorios clave:

* [`bcn - consultas/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20consultas): Contiene los resultados de procesamiento semántico (.ttl, .xml) de las circulares de prueba.
* [`bcn - documentación/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n): Contiene la documentación técnica oficial de la BCN, los esquemas de validación estructural (`Esquema Akoma-Ntoso BCN.xsd`), la especificación de cobertura local (`especificacion_cobertura.md`), el contrato de especificación estructural ([`estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv)) y los CSVs del diccionario de datos y secuencia de plantilla.
* [`circulares/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/circulares): Colección de circulares DDU originales en formato PDF (por ejemplo, DDU 456, 531, 533, 537 y 546).
* [`salidas_csv/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_csv): Colección de datos extraídos de circulares en formato tabular CSV de dominio plano.
* [`salidas_tablas/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_tablas): Tablas normativas extraídas y consolidadas en archivos CSV estructurados (`utf-8-sig`, delimitador `;`).
* [`salidas_imagenes/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_imagenes): Esquemas, figuras y planos técnicos exportados en formato PNG sin pérdida a alta resolución (300 DPI).
* [`salidas_xml/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_xml): Archivos XML Akoma Ntoso v2.0 BCN con segmentación atómica de numerales (`<num>`), etiquetas `<img>`, anexos `<attachments>` y validación XSD.
* [`salidas_rdf/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_rdf): Grafos semánticos RDF en sintaxis Turtle (`.ttl`) generados desde los CSVs con predicados `minvu-ddu:modificadaPor`.
* [`salidas_ppt/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_ppt): Presentaciones ejecutivas del proyecto en formato PowerPoint nativo (`.pptx`).
* [`scripts/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts): Módulos funcionales de procesamiento y conversión:
  * [`ddu_types.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_types.py): Declaraciones de tipado estricto `DatosCircularDDU` y `SeccionDDU`.
  * [`extractors/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors): Paquete de ETLs modulares e independientes (`encabezado.py`, `acto_administrativo.py`, `antecedentes.py`, `materia.py`, `descriptores.py`, `fecha_lugar.py`, `destinatarios.py`, `emisor.py`, `cuerpo.py`, `nota_al_pie.py`, `firma.py`, `distribucion.py`, `tablas.py`, `imagenes.py`, `modificaciones_posteriores.py`) derivados de la interfaz base `BaseExtractor`.
  * [`ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py): Orquestador central (`DDUOrchestrator`) que coordina los extractores registrados y exporta CSVs.
  * [`ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py): Wrapper de retrocompatibilidad apuntando al orquestador.
  * [`ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py): Generador estructurado XML bajo el estándar Akoma Ntoso v2.0 BCN.
  * [`csv_to_akoma_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/csv_to_akoma_xml.py): Transformador independiente especializado que convierte CSVs a XML Akoma Ntoso v2.0 BCN con segmentación atómica de numerales `<num>`.
  * [`csv_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/csv_to_rdf.py): Transformador independiente especializado que convierte CSVs a grafos RDF Turtle (`.ttl`).
  * [`ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py): Constructor semántico RDF/Turtle.
  * [`generar_ppt.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/generar_ppt.py): Generador de presentaciones ejecutivas en PowerPoint nativo (`.pptx`).
  * [`leychile_api.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/leychile_api.py): Integración oficial con la API de Ley Chile de la BCN.
* [`test/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test): Suite plana de pruebas automatizadas locales (`test_csv_to_akoma_xml.py`, `test_csv_to_rdf.py`, `test_extractor_base.py`, `test_extractor_metadata.py`, `test_extractor_body.py`, `test_extractor_nota_al_pie.py`, `test_extractor_tablas.py`, `test_extractor_imagenes.py`, `test_extractor_modificaciones_posteriores.py`, `test_orchestrator.py`, `test_csv_integrity.py`, `test_spec_coverage.py`, `test_xml_generation.py`, `test_rdf_generation.py`, `test_xsd_structural_validation.py`, `test_utils_cleaner.py`) ejecutables con `pytest`.

## Modelo de Datos de Dominio y Extensibilidad Evolutiva

El proyecto adopta una **arquitectura en capas con separación clara de responsabilidades**:

1. **Capa de Dominio Plano e Intuitivo (CSV)**:
   Los datos extraídos se organizan bajo términos de dominio claros y legibles para analistas e ingenieros de datos (`numero_ddu`, `fecha_emision`, `cuerpo`, `firmante`, `tablas`, `imagenes`, `modificaciones_posteriores`, etc.) en formato CSV. Los campos complejos se formatean como manifiestos clave-valor delimitados por `; ` (sin sintaxis JSON invasiva).
2. **Capa de Interoperabilidad Semántica (Akoma Ntoso XML & RDF)**:
   Los módulos [`scripts/ddu_to_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_xml.py) y [`scripts/ddu_to_rdf.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_to_rdf.py) actúan como traductores que mapean automáticamente los campos de dominio a la taxonomía XML Akoma Ntoso v2.0 BCN (`FRBRWork`, `lifecycle`, `analysis`, `mainBody`, `img`, `conclusions`, `attachments`) y a grafos semánticos RDF/Turtle (`minvu-ddu:interpretaA`, `minvu-ddu:complementaA`, `minvu-ddu:modificadaPor`).
3. **Extensibilidad Evolutiva del Pipeline ETL**:
   A medida que las circulares DDU evolucionen o incorporen nuevos bloques normativos en el futuro, es posible registrar nuevos extractores en [`scripts/extractors/`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors) mediante el decorador `@register_extractor`. El orquestador [`scripts/ddu_orchestrator.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_orchestrator.py) incorporará las nuevas columnas al CSV sin alterar el código existente ni romper la generación Akoma Ntoso.

## Mapeo Estandarizado de la Estructura (CSV -> ETLs)

La suite de los ETLs modulares deriva exactamente del contrato de especificación documentado en [`bcn - documentación/estructura_circular_ddu.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/bcn%20-%20documentaci%C3%B3n/estructura_circular_ddu.csv), simplificado a **6 columnas esenciales** (`orden`, `bloque`, `campo`, `obligatorio`, `descripcion`, `reglas`):

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
| **Firma** | `firmante` | `firma.py` | Nombre y cargo del Jefe de División (con soporte OCR visual) |
| **Distribución** | `lista_distribucion` | `distribucion.py` | Nómina de receptores al cierre del documento |
| **Tablas** | `tablas` | `tablas.py` | Extracción, consolidación multi-página y exportación de tablas a CSV |
| **Imágenes** | `imagenes` | `imagenes.py` | Detección y exportación de diagramas y esquemas técnicos a PNG 300 DPI |
| **Modificaciones Posteriores** | `modificaciones_posteriores` | `modificaciones_posteriores.py` | Captura de notas marginales de vigencia y reformas posteriores |

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
        Base --> Ext13[tablas.py]
        Base --> Ext14[imagenes.py]
        Base --> Ext15[modificaciones_posteriores.py]
    end

    subgraph "Orquestación y Salidas (scripts/ddu_orchestrator.py)"
        PDF --> Orch[DDUOrchestrator]
        Ext1 & Ext2 & Ext3 & Ext4 & Ext5 & Ext6 & Ext7 & Ext8 & Ext9 & Ext10 & Ext11 & Ext12 & Ext13 & Ext14 & Ext15 --> Orch
        Orch --> Data[DatosCircularDDU]
        Data --> CSVInd[CSV Individual Circular]
        Data --> CSVMaster[Dataset CSV Acumulado Master]
        Data --> XML[ddu_to_xml.py]
        Data --> RDF[ddu_to_rdf.py]
        Ext13 -.-> CSVTablas[salidas_tablas/ .csv]
        Ext14 -.-> PNGImg[salidas_imagenes/ .png]
    end
```

## Guía de Ejecución y Visualización de Resultados

### 1. Ejecución de ETLs de Forma Independiente (CLI)

Si deseas probar la extracción de **un bloque específico** de forma aislada sobre cualquier circular PDF:

```powershell
# Extracción de Materia y Metadatos
py -3 -m scripts.extractors.materia --pdf "circulares/DDU 531.pdf"

# Extracción y exportación de Tablas Normativas (salidas_tablas/)
py -3 -m scripts.extractors.tablas --pdf "circulares/DDU 456.pdf"

# Extracción y exportación de Imágenes y Esquemas PNG a 300 DPI (salidas_imagenes/)
py -3 -m scripts.extractors.imagenes --pdf "circulares/DDU 456.pdf"

# Extracción de Modificaciones Posteriores
py -3 -m scripts.extractors.modificaciones_posteriores --pdf "circulares/DDU 456.pdf"
```

* **Salida / Visualización**: Cada extractor genera sus archivos anexos correspondientes (`salidas_tablas/*.csv`, `salidas_imagenes/*.png`) e imprime en consola un JSON estructurado (`ResultadoBloque`) con el resultado del bloque y su nivel de confianza.

### 2. Ejecución Orquestada Completa (Generación de CSV)

Para procesar todos los ETLs y exportar la ficha CSV de la circular:

```powershell
py -3 scripts/ddu_orchestrator.py --pdf "circulares/DDU 531.pdf" --export-csv
```

* **Salida / Visualización**: Genera un archivo CSV codificado en UTF-8 con BOM y delimitado por punto y coma (`;`) en la carpeta `salidas_csv/` (ej. [`salidas_csv/DDU_531_extraido.csv`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/salidas_csv/DDU_531_extraido.csv)).


## Dependencias e Instalación

Este proyecto utiliza módulos estándar de Python 3 y requiere las siguientes librerías externas:

* **pypdf**: Extracción de capas de texto y metadatos de documentos PDF.
* **pdfplumber**: Extracción geométrica de tablas estructuradas.
* **PyMuPDF (`fitz`)**: Extracción de imágenes y renderizado de áreas vectoriales en alta resolución (300 DPI).
* **rapidocr_onnxruntime**: OCR visual de alta precisión para firmas y facsímiles manuscritos.
* **lxml**: Compilación y validación estricta contra esquemas XSD (`Esquema Akoma-Ntoso BCN.xsd`).

Para verificar o instalar todas las dependencias requeridas:

```powershell
pip install pypdf pdfplumber pymupdf rapidocr_onnxruntime lxml
```

## Ejecución de la Suite de Pruebas

Para garantizar que el sistema y sus modelos semánticos de datos cumplen al 100% con los contratos estructurales definidos por el XSD, los CSV de la BCN y la suite de extractores, ejecute en la raíz del repositorio:

```powershell
pytest -v
```

Actualmente, **81 de 81 pruebas pasan exitosamente** (100% de cobertura de la suite en estructura modular y plana).

