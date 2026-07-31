# Especificación de Diseño: Segmentación de Numerales XML (`csv_to_akoma_xml.py`) y Módulo ETL Independiente CSV ➔ RDF (`csv_to_rdf.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Se requiere:
1. **Segmentación Estructural BCN en `csv_to_akoma_xml.py`**: Parsear dinámicamente el campo `cuerpo` del CSV en unidades atómicas de `<section>` y `<paragraph>`, aislando numerales (`<num>1.</num>`) y encabezados (`<heading>I. ANTECEDENTES</heading>`) en cumplimiento estricto con el esquema XSD de la BCN (`basehierarchy`).
2. **Módulo ETL Independiente `scripts/csv_to_rdf.py`**: Crear un script especializado que lea archivos CSV de circulares DDU (`salidas_csv/DDU_*_extraido.csv`) y construya grafos semánticos RDF en sintaxis Turtle (`.ttl`) dentro del directorio `salidas_rdf/`.

---

## 2. Componente 1: Segmentación de Numerales y Secciones en `csv_to_akoma_xml.py`

* **Mecanismo de Segmentación**:
  En `CSVToAkomaXML.read_csv()`, si la celda `cuerpo` contiene texto corrido:
  - Detectar títulos de sección romanas/mayúsculas (ej: `I. ANTECEDENTES`, `II. NORMATIVA APLICABLE`, `III. INSTRUCCIÓN COMPLEMENTARIA...`).
  - Dividir el cuerpo por saltos de línea y por la presencia de numerales al inicio de renglón (ej: `1. `, `2. `, `3. `, `a) `, `b) `).
  - Reconstruir `secciones: List[SeccionDDU]` con títulos de sección y párrafos individuales.
* **Estructura XML Generada en `mainBody`**:
  ```xml
  <section id="sec_1">
    <heading>I. ANTECEDENTES</heading>
    <paragraph id="par_1_1">
      <num>1.</num>
      <content>
        <p>De conformidad con lo dispuesto...</p>
      </content>
    </paragraph>
  </section>
  ```

---

## 3. Componente 2: Módulo ETL Independiente CSV ➔ RDF (`scripts/csv_to_rdf.py`)

* **Clase `CSVToRDF`**:
  * Método `read_csv(csv_path: Path) -> DatosCircularDDU`: Reconstruye el diccionario de datos desde el CSV.
  * Método `transform(csv_path: Path, output_rdf_path: Path) -> Path`: Delega la construcción del grafo RDF a `DDUToRDF` y escribe el archivo `.ttl`.
  * Método `transform_dir(csv_dir: Path, output_dir: Path) -> List[Path]`: Procesa en lote todos los CSVs de un directorio.
* **Interfaz CLI**:
  * `py -3 scripts/csv_to_rdf.py --csv "salidas_csv/DDU_531_extraido.csv" --output "salidas_rdf/DDU_531_rdf.ttl"`
  * `py -3 scripts/csv_to_rdf.py --csv-dir "salidas_csv" --output-dir "salidas_rdf"`

---

## 4. Criterios de Aceptación y Pruebas

1. `test/test_csv_to_akoma_xml.py`: Verificar que el XML generado contenga elementos `<num>` y `<heading>` separados.
2. `test/test_csv_to_rdf.py`: Verificar la creación de grafos `.ttl` válidos desde CSV con prefijos BCN y tripletas de relaciones normativas (`bcn-norms`, `minvu-ddu`).
3. Generación en lote de archivos XML (`salidas_xml/`) y grafos RDF (`salidas_rdf/`).
4. Cobertura del 100% de la suite con `pytest -v`.
