# Plan de Implementación: ETLs Modulares y Orquestador de Circulares DDU

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactorizar la extracción monolítica de circulares DDU construyendo 11 ETLs modulares e independientes basados en una interfaz común `BaseExtractor`, coordinados por un Orquestador central (`DDUOrchestrator`) que exporta el CSV individual y el dataset acumulado sin romper la compatibilidad con el resto del proyecto.

**Architecture:** Se creará un paquete de Python `scripts/extractors/` con una clase base abstracta `BaseExtractor` y un registro decorador `ExtractorRegistry`. `DDUOrchestrator` coordinará los extractores registrados para compilar la estructura `DatosCircularDDU`, exportar CSVs (individual y master) y alimentar a los transformadores existentes.

**Architecture Diagram:**

```mermaid
graph TD
    subgraph "Entrada"
        PDF[PDF Circular DDU]
    end

    subgraph "Paquete ETL (scripts/extractors/)"
        Base[base.py: BaseExtractor ABC & Registry]
        Base --> Ext1[encabezado.py]
        Base --> Ext2[acto_administrativo.py]
        Base --> Ext3[antecedentes.py]
        Base --> Ext4[materia.py]
        Base --> Ext5[descriptores.py]
        Base --> Ext6[fecha_lugar.py]
        Base --> Ext7[destinatarios.py]
        Base --> Ext8[emisor.py]
        Base --> Ext9[cuerpo.py]
        Base --> Ext10[firma.py]
        Base --> Ext11[distribucion.py]
    end

    subgraph "Orquestación (scripts/ddu_orchestrator.py)"
        PDF --> Orch[DDUOrchestrator]
        Ext1 & Ext2 & Ext3 & Ext4 & Ext5 & Ext6 & Ext7 & Ext8 & Ext9 & Ext10 & Ext11 --> Orch
        Orch --> Data[DatosCircularDDU]
    end

    subgraph "Salidas"
        Data --> CSVInd[CSV Individual Circular]
        Data --> CSVMaster[Dataset CSV Acumulado Master]
        Data --> Wrapper[ddu_parser.py (Retrocompatibilidad)]
        Wrapper --> XML[ddu_to_xml.py]
        Wrapper --> RDF[ddu_to_rdf.py]
    end
```

**Tech Stack:** Python 3 (Strict typing, `TypedDict`, `dataclass`, `abc.ABC`), Pytest.

## Global Constraints
- **Tipado Estricto**: Anotaciones explícitas de tipos en todas las funciones, métodos y variables.
- **Idioma**: Mensajes de commit, docstrings y salidas de log exclusivamente en español.
- **Autonomía de Tests**: Cobertura al 100% de la suite de pruebas mediante `pytest -v`.

---

### Task 1: Interfaz Base y Registro de Extractores (`BaseExtractor` & `ExtractorRegistry`)

**Files:**
- Create: `scripts/extractors/__init__.py`
- Create: `scripts/extractors/base.py`
- Test: `test/extractors/test_base_extractor.py`

**Interfaces:**
- Produces: `ResultadoBloque`, `BaseExtractor` (ABC), `@register_extractor`, `ExtractorRegistry`.

- [ ] **Step 1: Escribir la prueba unitaria para `BaseExtractor` y `ExtractorRegistry`**
  Crear `test/extractors/test_base_extractor.py` validando la herencia de `BaseExtractor` y el registro dinámico en `ExtractorRegistry`:
  ```python
  import pytest
  from scripts.extractors.base import BaseExtractor, ResultadoBloque, ExtractorRegistry, register_extractor

  def test_register_and_get_extractors():
      ExtractorRegistry.clear()
      
      @register_extractor
      class DummyExtractor(BaseExtractor):
          @property
          def nombre_bloque(self) -> str:
              return "dummy"
          
          def extract(self, raw_text: str, lines: list[str]) -> ResultadoBloque:
              return ResultadoBloque(
                  nombre_bloque=self.nombre_bloque,
                  exito=True,
                  datos={"test": "ok"},
                  confianza=1.0
              )

      extractors = ExtractorRegistry.get_all_extractors()
      assert "dummy" in extractors
      instancia = extractors["dummy"]()
      res = instancia.extract("raw", ["lines"])
      assert res.exito is True
      assert res.datos["test"] == "ok"
  ```

- [ ] **Step 2: Implementar `scripts/extractors/base.py`**
  Crear `scripts/extractors/base.py` con `ResultadoBloque` dataclass y `BaseExtractor` ABC.

- [ ] **Step 3: Ejecutar test unitario**
  Run: `pytest test/extractors/test_base_extractor.py -v`
  Expected: PASS.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/extractors/__init__.py scripts/extractors/base.py test/extractors/test_base_extractor.py
  git commit -m "feat: implementar interfaz base y registro de extractores de ETLs"
  ```

---

### Task 2: Implementar Extractores de Metadatos (ETLs 1 al 8)

**Files:**
- Create: `scripts/extractors/encabezado.py` (Número DDU)
- Create: `scripts/extractors/acto_administrativo.py` (ORD. N°)
- Create: `scripts/extractors/antecedentes.py` (ANT:)
- Create: `scripts/extractors/materia.py` (MAT:)
- Create: `scripts/extractors/descriptores.py` (Vocablos)
- Create: `scripts/extractors/fecha_lugar.py` (Santiago...)
- Create: `scripts/extractors/destinatarios.py` (A:)
- Create: `scripts/extractors/emisor.py` (DE:)
- Test: `test/extractors/test_metadata_extractors.py`

**Interfaces:**
- Consumes: `BaseExtractor`, `ResultadoBloque`
- Produces: Extractores registrados para los 8 bloques de metadatos del encabezado.

- [ ] **Step 1: Escribir la prueba para extractores de metadatos**
  Crear `test/extractors/test_metadata_extractors.py` con muestras de texto plano de la DDU 533 para probar cada extractor individualmente.

- [ ] **Step 2: Implementar los 8 extractores de metadatos**
  Crear los archivos en `scripts/extractors/` decorados con `@register_extractor`. Incluir el bloque `if __name__ == '__main__':` con `argparse` para soporte CLI en cada módulo.

- [ ] **Step 3: Ejecutar pruebas unitarias de metadatos**
  Run: `pytest test/extractors/test_metadata_extractors.py -v`
  Expected: PASS.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/extractors/ test/extractors/test_metadata_extractors.py
  git commit -m "feat: implementar extractores independientes de metadatos (ETLs 1 a 8)"
  ```

---

### Task 3: Implementar Extractores de Cuerpo, Firma y Distribución (ETLs 9, 10, 11)

**Files:**
- Create: `scripts/extractors/cuerpo.py` (Secciones romanas, arábigas y listas)
- Create: `scripts/extractors/firma.py` (Firmante)
- Create: `scripts/extractors/distribucion.py` (Lista de distribución)
- Test: `test/extractors/test_body_extractors.py`

**Interfaces:**
- Consumes: `BaseExtractor`, `ResultadoBloque`
- Produces: Extractores para cuerpo estructurado, firma y distribución.

- [ ] **Step 1: Escribir prueba unitaria para cuerpo, firma y distribución**
  Crear `test/extractors/test_body_extractors.py` probando `CuerpoExtractor`, `FirmaExtractor` y `DistribucionExtractor`.

- [ ] **Step 2: Implementar `cuerpo.py`, `firma.py` y `distribucion.py`**
  Implementar las clases heredando de `BaseExtractor` con lógica robusta de regex y parseo de líneas.

- [ ] **Step 3: Ejecutar pruebas unitarias de cuerpo y cierre**
  Run: `pytest test/extractors/test_body_extractors.py -v`
  Expected: PASS.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/extractors/cuerpo.py scripts/extractors/firma.py scripts/extractors/distribucion.py test/extractors/test_body_extractors.py
  git commit -m "feat: implementar extractores de cuerpo, firma y distribución (ETLs 9 a 11)"
  ```

---

### Task 4: Implementar el Orquestador `DDUOrchestrator` y Exportación de CSVs

**Files:**
- Create: `scripts/ddu_orchestrator.py`
- Test: `test/test_orchestrator.py`

**Interfaces:**
- Consumes: `ExtractorRegistry`, `DatosCircularDDU`
- Produces: `DDUOrchestrator.process_pdf()`, `export_individual_csv()`, `export_master_csv()`.

- [ ] **Step 1: Escribir prueba de integración para el Orquestador**
  Crear `test/test_orchestrator.py` verificando el procesamiento completo del PDF `circulares/DDU 533.pdf` y la generación de los CSVs (individual y master).

- [ ] **Step 2: Implementar `scripts/ddu_orchestrator.py`**
  Implementar la clase `DDUOrchestrator` con métodos para procesar el PDF usando los 11 extractores registrados, compilar `DatosCircularDDU` y exportar a CSV.

- [ ] **Step 3: Ejecutar prueba de integración del Orquestador**
  Run: `pytest test/test_orchestrator.py -v`
  Expected: PASS.

- [ ] **Step 4: Commit**
  ```bash
  git add scripts/ddu_orchestrator.py test/test_orchestrator.py
  git commit -m "feat: implementar orquestador principal DDUOrchestrator y exportadores de CSV"
  ```

---

### Task 5: Refactorizar `ddu_parser.py` para Retrocompatibilidad y Verificación Total

**Files:**
- Modify: `scripts/ddu_parser.py`
- Test: Toda la suite de pruebas (`pytest -v`)

**Interfaces:**
- Consumes: `DDUOrchestrator`
- Produces: `DDUParser.parse_pdf()` apuntando al nuevo motor orquestado.

- [ ] **Step 1: Refactorizar `ddu_parser.py`**
  Actualizar `DDUParser` en `scripts/ddu_parser.py` para delegar la extracción a `DDUOrchestrator`, manteniendo intacta la firma pública y el valor de retorno `DatosCircularDDU`.

- [ ] **Step 2: Ejecutar la suite completa de pruebas**
  Run: `pytest -v`
  Expected: Todos los tests pasen (cobertura XSD, integridad CSV, XML, RDF, extractores unitarios e integración del orquestador).

- [ ] **Step 3: Actualizar CHANGELOG.md**
  Registrar en `CHANGELOG.md` los detalles de la refactorización modular.

- [ ] **Step 4: Commit y Push**
  ```bash
  git add scripts/ddu_parser.py CHANGELOG.md
  git commit -m "refactor: integrar ddu_parser con DDUOrchestrator manteniendo retrocompatibilidad total"
  git push
  ```
