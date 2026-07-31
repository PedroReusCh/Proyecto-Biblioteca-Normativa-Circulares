# Especificación de Diseño: Transformador Independiente CSV ➔ Akoma Ntoso XML (`csv_to_akoma_xml.py`)

**Fecha:** 2026-07-31  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Se requiere un módulo especializado e independiente [`scripts/csv_to_akoma_xml.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/csv_to_akoma_xml.py) que tome los archivos CSV generados para cada circular DDU (`salidas_csv/DDU_*_extraido.csv`) y los transforme directamente a documentos XML válidos según el estándar **Akoma Ntoso v2.0 BCN**, respetando la matriz de homologación acordada.

---

## 2. Matriz de Homologación Aplicada (CSV ➔ XML)

| Campo CSV (`campo`) | Elemento XML Akoma Ntoso | Contenedor / Padre XML |
| :--- | :--- | :--- |
| `numero_ddu` | `FRBRnumber` + `FRBRsubtype` | `<meta>` ➔ `<identification>` ➔ `<FRBRWork>` |
| `numero_ord` | `docNumber` + `docTitle` | `<preface>` |
| `antecedentes` | `citations` / `recitals` | `<preamble>` |
| `materia` | `docPurpose` + `Materia` | `<preface>` + `<MetadataBCN>` |
| `descriptores` | `TerminosLibres` + `TLCConcept` | `<meta>` ➔ `<references>` + `<MetadataBCN>` |
| `fecha_emision` | `FRBRdate` + `docDate` | `<meta>` ➔ `<identification>` + `<preface>` |
| `destinatarios` | `docProponent` | `<preface>` |
| `emisor` | `FRBRauthor` + `docIntroducer` | `<meta>` ➔ `<identification>` + `<preface>` |
| `cuerpo` | `mainBody` ➔ `section` / `paragraph` | `<mainBody>` |
| `notas_al_pie` | `authorialNote` | `<inline>` ➔ `<authorialNote placement="bottom">` |
| `firmante` | `person` + `signature` | `<conclusions>` |
| `lista_distribucion` | `attachments` / `blockList` | `<conclusions>` |

---

## 3. Arquitectura del Módulo (`scripts/csv_to_akoma_xml.py`)

* **Clase `CSVToAkomaXML`**:
  * Método `read_csv(csv_path: Path) -> Dict[str, Any]`: Parsea el CSV delimitado por `;` y reconstruye el diccionario `DatosCircularDDU`.
  * Método `transform(csv_path: Path, output_xml_path: Path) -> Path`: Lee el CSV, delega la generación XML a `DDUToXML` y guarda el archivo XML en `salidas_xml/`.
  * Método `transform_dir(csv_dir: Path, output_dir: Path) -> List[Path]`: Procesa en lote todos los archivos CSV de un directorio.
* **CLI Independiente**:
  * `py -3 scripts/csv_to_akoma_xml.py --csv "salidas_csv/DDU_531_extraido.csv" --output "salidas_xml/DDU_531_akoma.xml"`
  * `py -3 scripts/csv_to_akoma_xml.py --csv-dir "salidas_csv" --output-dir "salidas_xml"`

---

## 4. Criterios de Aceptación y Pruebas

1. Crear `test/test_csv_to_akoma_xml.py` para probar la transformación desde CSV individual y por lote.
2. Validar que cada XML generado sea válido contra el XSD BCN (`bcn - documentación/Esquema Akoma-Ntoso BCN.xsd`).
3. Ejecutar la suite completa `pytest -v`.
