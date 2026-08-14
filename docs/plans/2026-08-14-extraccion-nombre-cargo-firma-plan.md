# Plan de Implementación: Extracción de Nombre y Cargo en FirmaExtractor

**Fecha:** 2026-08-14  
**Diseño Asociado:** `docs/plans/2026-08-14-extraccion-nombre-cargo-firma-design.md`

---

## Tareas

- [ ] **Tarea 1**: Actualizar pruebas unitarias en `test/test_extractor_body.py` y `test/test_orchestrator.py`
  - Validar extracción de `nombre_firmante == "JPB"` y `cargo_firmante == "Jefe División de Desarrollo Urbano"` en DDU 456.
  - Validar extracción de `nombre_firmante == "JUAN DIEGO IZQUIERDO HEVIA"` en DDU 546.
- [ ] **Tarea 2**: Implementar en `scripts/extractors/firma.py` la extracción prioritaria del nombre/sigla ubicada arriba del cargo
  - Escanear líneas inmediatamente precedentes al cargo en `partes_firma`.
  - Capturar nombres propios y siglas de rúbricas alfabéticas reconocibles (ej. `JPB`).
- [ ] **Tarea 3**: Regenerar salidas CSV y verificar con la suite de pruebas completa
  - Ejecutar `pytest -v` (77+ tests).
  - Regenerar `salidas_csv/DDU_456_extraido.csv`.
  - Documentar en `CHANGELOG.md` y hacer commit / push.
