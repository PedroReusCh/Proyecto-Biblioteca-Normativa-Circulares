# Especificación de Diseño: Arquitectura de ETLs Modulares y Orquestador DDU

Esta especificación detalla el diseño de software para desacoplar el parser monolítico de circulares DDU en un conjunto de **ETLs/Extractores independientes, escalables y estandarizados** coordinados por un **Orquestador central**, preservando el tipado estricto y la compatibilidad total con la suite de pruebas, XML y RDF.

---

## 1. Organización de Archivos y Componentes

```text
Proyecto Biblioteca Normativa Circulares/
├── scripts/
│   ├── ddu_types.py                  # Definiciones de tipos estrictos (DatosCircularDDU, etc.)
│   ├── ddu_orchestrator.py           # Orquestador principal y exportador de CSVs
│   ├── extractors/                   # Paquete de ETLs modulares independientes
│   │   ├── __init__.py
│   │   ├── base.py                   # BaseExtractor (ABC) y ExtractorRegistry
│   │   ├── encabezado.py             # ETL 1: Número DDU
│   │   ├── acto_administrativo.py    # ETL 2: Número de Acto Ordinario (ej. ORD. N° 112)
│   │   ├── antecedentes.py           # ETL 3: Antecedentes normativos (ANT:)
│   │   ├── materia.py                # ETL 4: Materia (MAT:)
│   │   ├── descriptores.py           # ETL 5: Vocablos / Descriptores de materia
│   │   ├── fecha_lugar.py            # ETL 6: Fecha y ciudad de emisión
│   │   ├── destinatarios.py          # ETL 7: Destinatarios (A:)
│   │   ├── emisor.py                 # ETL 8: Emisor (DE:)
│   │   ├── cuerpo.py                 # ETL 9: Secciones romanas, numerales y listas
│   │   ├── firma.py                  # ETL 10: Firmante de la DDU
│   │   └── distribucion.py           # ETL 11: Lista de distribución formal
│   ├── ddu_parser.py                 # Wrapper de retrocompatibilidad apuntando al Orquestador
│   ├── ddu_to_xml.py                 # Generador Akoma Ntoso XML
│   └── ddu_to_rdf.py                 # Generador RDF Turtle
├── bcn - documentación/
│   ├── estructura_circular_ddu.csv   # Especificación de campos
│   └── especificacion_cobertura.md   # Cobertura XSD BCN
└── test/
    ├── extractors/                   # Pruebas unitarias dedicadas a cada ETL
    │   ├── test_encabezado.py
    │   ├── test_antecedentes.py
    │   └── ...
    └── test_orchestrator.py          # Prueba de integración del orquestador
```

---

## 2. Contrato de Interfaz Base (`BaseExtractor`)

Todos los extractores heredarán de `BaseExtractor` en `scripts/extractors/base.py`:

```python
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

@dataclass
class ResultadoBloque:
    """Resultado estandarizado de la extracción de un bloque."""
    nombre_bloque: str
    exito: bool
    datos: Dict[str, Any]
    confianza: float  # 0.0 a 1.0
    observaciones: str = ""

class BaseExtractor(ABC):
    """Clase base abstracta para todos los ETLs modulares de circulares DDU."""

    @property
    @abstractmethod
    def nombre_bloque(self) -> str:
        """Nombre identificador del bloque (ej. 'antecedentes')."""
        pass

    @abstractmethod
    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Ejecuta la lógica de extracción del bloque sobre el texto plano.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con los datos extraídos y nivel de confianza.
        """
        pass
```

---

## 3. Ejecución Dual (Modulo + CLI Independiente)

Cada extractor podrá ejecutarse solo en consola mediante CLI:

```bash
py -3 -m scripts.extractors.antecedentes --pdf "circulares/DDU 533.pdf" --json
```

Imprimiendo en consola el JSON formateado con el resultado del bloque `ResultadoBloque`.

---

## 4. Orquestador y Formatos de Salida (`DDUOrchestrator`)

`scripts/ddu_orchestrator.py` coordinará la ejecución:

1.  **Entrada**: Recibe la ruta a un PDF o una lista de PDFs.
2.  **Procesamiento**: Instancia los 11 extractores registrados y ejecuta `extract()`.
3.  **Consolidación**: Mapea los resultados al `DatosCircularDDU` tipado estricto.
4.  **Generación de CSVs**:
    *   `export_individual_csv(pdf_path, output_dir)`: Genera un CSV estructurado de la circular específica (ej: `DDU_533_extraido.csv`).
    *   `export_master_csv(pdf_list, output_path)`: Consolida un dataset acumulado de múltiples circulares donde cada fila corresponde a una circular procesada.

---

## 5. Retrocompatibilidad y Suite de Pruebas

*   [`scripts/ddu_parser.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/ddu_parser.py) se actualizará para delegar a `DDUOrchestrator`, asegurando que ningún código o test existente se rompa.
*   Se crearán tests unitarios en `test/extractors/` para certificar el 100% de cobertura y funcionamiento de cada uno de los 11 ETLs de forma independiente.
*   Toda la suite de pruebas (`pytest -v`) continuará pasando al 100%.

---

## 6. Auto-Evaluación de la Especificación (Self-Review)
*   **Placeholders**: Ninguno. Los 11 bloques del documento Word y del CSV de estructura están completamente cubiertos.
*   **Consistencia**: Se mantiene la compatibilidad con `DatosCircularDDU`, `ddu_to_xml.py` y `ddu_to_rdf.py`.
*   **Aislamiento**: Todo el código se organiza dentro del directorio `scripts/extractors/` de manera modular y limpia.
