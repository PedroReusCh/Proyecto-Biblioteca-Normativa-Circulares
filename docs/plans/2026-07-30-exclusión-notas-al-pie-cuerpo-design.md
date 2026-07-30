# Especificación de Diseño: Exclusión de Notas al Pie en `CuerpoExtractor` (`cuerpo.py`)

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

En la circular DDU 546 (y circulares similares con notas explicativas al pie), la extracción del cuerpo normativo en [`scripts/extractors/cuerpo.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/cuerpo.py) incluía dentro de los párrafos del bloque `cuerpo` las líneas pertenecientes a las notas al pie de página (ej. `1 En dicha circular se indica...`, `2 En el artículo 1.1.2...`, `3 En el artículo 1.1.2...`).

Dado que la arquitectura del proyecto define un componente específico y dedicado llamado `Nota al Pie` (`nota_al_pie.py`), el bloque `Cuerpo` debe contener únicamente los numerales y articulados del cuerpo de la circular, excluyendo cualquier renglón correspondiente a las notas explicativas de pie de página.

---

## 2. Lógica de Filtrado y Descarte (`_es_inicio_nota_al_pie`)

Se añade el helper `_es_inicio_nota_al_pie(line: str) -> bool` en `cuerpo.py`:

```python
def _es_inicio_nota_al_pie(line: str) -> bool:
    """Detecta si una línea corresponde al inicio de una nota al pie explicativa."""
    match = re.match(r"^(\d{1,2})\s+([A-ZÁÉÍÓÚÑ][a-záéíóúñA-ZÁÉÍÓÚÑ\s\.,\(\)\"\'-].+)$", line.strip())
    if match:
        num = match.group(1)
        texto = match.group(2).strip()
        if int(num) <= 20 and not line.strip().startswith(f"{num}. "):
            if not re.match(r"^\d+\s+(?:de\s+la|de\s+los|del|en\s+la|con\s+la|que|por|para)\b", line.strip(), re.IGNORECASE):
                if re.search(r"(?:Art[íi]culo|Circular|Orientaci[óo]n|Gu[íi]a|Decreto|Ley|Construcci[óo]n|Edificaci[óo]n|OGUC|LGUC)\b", texto, re.IGNORECASE):
                    return True
    return False
```

En la rutina `extract()` de `CuerpoExtractor`:
1. Si `_es_inicio_nota_al_pie(line_clean)` es `True`, se activa el estado `omitiendo_nota_al_pie = True` y se omite la línea (`continue`).
2. Mientas `omitiendo_nota_al_pie` sea `True`, si la línea no es un nuevo numeral del cuerpo (ej. `8. Con todo...`), ni un encabezado de sección, se omite (`continue`).
3. El estado `omitiendo_nota_al_pie` se desactiva al detectar el inicio de un numeral legítimo del cuerpo (`^\d+\.\s+`).

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `cuerpo.py` no incluya líneas de notas al pie en los párrafos extraídos.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 comprobando que la fila 9 (`Cuerpo`) termine de forma limpia en el punto 8 sin arrastrar las notas 1, 2 y 3.
