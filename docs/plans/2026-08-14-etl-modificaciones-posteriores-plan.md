# Plan de Implementación: ETL Modular `ModificacionesPosterioresExtractor` y Descontaminación de Numeral 2

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Implementar un nuevo extractor modular `ModificacionesPosterioresExtractor` que capture notas marginales de vigencia como texto libre, y excluir este texto del cuerpo normativo (Numeral 2) en `CuerpoExtractor`.

**Architecture:** 
1. Nuevo extractor `scripts/extractors/modificaciones_posteriores.py` registrado en `ExtractorRegistry`.
2. Filtro `_es_nota_modificacion_posterior` y limpieza en `scripts/extractors/cuerpo.py`.
3. Actualización de `scripts/ddu_types.py`, `scripts/extractors/__init__.py` y `scripts/ddu_orchestrator.py`.
4. Tests unitarios e integración.

**Tech Stack:** Python 3.13, Pytest, Pylance Strict Mode.

---

### Task 1: Crear pruebas unitarias para `ModificacionesPosterioresExtractor` y actualizar `test_extractor_body.py`

**Files:**
- Create: `test/test_extractor_modificaciones_posteriores.py`
- Modify: `test/test_extractor_body.py`

---

### Task 2: Implementar `ModificacionesPosterioresExtractor` y registrarlo en extractores

**Files:**
- Create: `scripts/extractors/modificaciones_posteriores.py`
- Modify: `scripts/extractors/__init__.py`

---

### Task 3: Descontaminar `CuerpoExtractor` de notas de modificación posterior

**Files:**
- Modify: `scripts/extractors/cuerpo.py`

---

### Task 4: Integrar en `ddu_types.py` y `ddu_orchestrator.py`, regenerar salidas y verificar suite completa

**Files:**
- Modify: `scripts/ddu_types.py`
- Modify: `scripts/ddu_orchestrator.py`
- Modify: `test/test_orchestrator.py`
- Modify: `CHANGELOG.md`
- Output: `salidas_csv/DDU_456_extraido.csv`
