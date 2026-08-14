# Plan de Implementación: Formato Plano Limpio para Tablas e Imágenes en CSV

> **For Antigravity:** REQUIRED WORKFLOW: Use `.agent/workflows/execute-plan.md` to execute this plan in single-flow mode.

**Goal:** Transformar los campos de `Tablas` e `Imágenes` en los CSVs de salida a un formato plano limpio de pares clave-valor separados por `;`, eliminando toda sintaxis JSON (`[`, `]`, `{`, `}`, `"`).

**Architecture:** Implementar la función de formateo `formatear_manifiesto_plano(items: Any) -> str` en `scripts/ddu_orchestrator.py`. Aplicarla en `export_individual_csv` y `export_master_csv` para que los campos `tablas` e `imagenes` se serialicen como texto plano limpio estructurado.

**Tech Stack:** Python 3.13, typing estricto, pytest.

---

### Task 1: Implementar `formatear_manifiesto_plano` y Tests en `test/test_orchestrator.py`

**Files:**
- Modify: `scripts/ddu_orchestrator.py`
- Modify: `test/test_orchestrator.py`

**Step 1: Escribir el test fallido en `test/test_orchestrator.py`**
Validar que `formatear_manifiesto_plano` convierta listas de diccionarios a pares `clave: valor; ...` sin corchetes ni llaves ni comillas.

**Step 2: Ejecutar el test para verificar que falle**
`pytest test/test_orchestrator.py -v`

**Step 3: Implementar la función `formatear_manifiesto_plano` en `scripts/ddu_orchestrator.py`**
```python
def formatear_manifiesto_plano(items: Any) -> str:
    """Convierte una lista de diccionarios de metadatos (tablas/imágenes) a formato plano con ';'.
    
    Elimina sintaxis JSON ([ ], { }, \") y produce pares clave: valor separados por ';'.
    """
    if not items:
        return ""
    if isinstance(items, str):
        # Si ya viene como string limpio
        if not (items.startswith("[") or items.startswith("{")):
            return items
        try:
            items = json.loads(items)
        except Exception:
            return items

    if isinstance(items, dict):
        items = [items]

    if not isinstance(items, list):
        return str(items)

    elementos_str: List[str] = []
    for elem in items:
        if isinstance(elem, dict):
            pares: List[str] = []
            for k, v in elem.items():
                if isinstance(v, list):
                    v_str = ", ".join(str(x) for x in v)
                else:
                    v_str = str(v)
                pares.append(f"{k}: {v_str}")
            elementos_str.append("; ".join(pares))
        else:
            elementos_str.append(str(elem))

    return " || ".join(elementos_str)
```

**Step 4: Ejecutar tests para verificar que pasen**
`pytest test/test_orchestrator.py -v`

**Step 5: Commit**
`git add scripts/ddu_orchestrator.py test/test_orchestrator.py`
`git commit -m "feat: implementar formatear_manifiesto_plano para serialización limpia en CSV"`

---

### Task 2: Integrar `formatear_manifiesto_plano` en Exportadores CSV de `DDUOrchestrator`

**Files:**
- Modify: `scripts/ddu_orchestrator.py:155-215`
- Modify: `test/test_orchestrator.py`

**Step 1: Modificar `export_individual_csv` y `export_master_csv` en `scripts/ddu_orchestrator.py`**
Aplicar `formatear_manifiesto_plano` para los campos `tablas` e `imagenes` antes de escribir cada fila.

**Step 2: Actualizar `test_export_individual_csv_ddu_456` en `test/test_orchestrator.py`**
Verificar que el CSV exportado para DDU 456 contenga:
- `id: DDU_456_tabla_1; nombre: Modificaciones Normativas (DDU 339, DDU 322, DDU 168); paginas: 5, 6, 7, 8; filas: 3; columnas: 3; archivo_anexo: salidas_tablas/DDU_456_tabla_1.csv`
- `id: DDU_456_img_1; nombre: Esquema ilustrativo: Planta azotea y corte esquemático; pagina: 3; tipo: Esquema técnico; formato: png; dimensiones: 2131x1906; ancho: 2131; alto: 1906; xref: 5; descripcion: Esquema ilustrativo: Planta azotea y corte esquemático; archivo_anexo: salidas_imagenes/DDU_456_img_1.png`
- Ausencia total de `[{`, `}]`, `"` dentro de los valores de `tablas` e `imagenes`.

**Step 3: Ejecutar suite de pruebas**
`pytest -v`

**Step 4: Commit**
`git add scripts/ddu_orchestrator.py test/test_orchestrator.py`
`git commit -m "feat: integrar formato plano en exportadores CSV individual y maestro"`

---

### Task 3: Regeneración de Salidas, Validación Completa y Actualización de Documentación

**Files:**
- Modify: `salidas_csv/DDU_456_extraido.csv`
- Modify: `CHANGELOG.md`

**Step 1: Regenerar `salidas_csv/DDU_456_extraido.csv`**
Ejecutar exportación con `DDUOrchestrator`.

**Step 2: Ejecutar la suite completa de pruebas (77/77 tests)**
`pytest -v`

**Step 3: Actualizar `CHANGELOG.md`**
Registrar la eliminación de caracteres JSON y el uso del formato clave-valor delimitado por `;` en los campos `Tablas` e `Imágenes` del CSV.

**Step 4: Commit y Push**
`git add salidas_csv/DDU_456_extraido.csv CHANGELOG.md`
`git commit -m "docs: registrar formato plano sin caracteres JSON en CSVs y regenerar salida DDU 456"`
`git push origin feature/ddu-456`
