# Especificación de Diseño: Filtrado de Banners de Pie de Página en `DistribucionExtractor` (`distribucion.py`)

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Propósito

Al extraer la lista de distribución de la DDU 546 (y circulares con isologos o bandas institucionales al pie), el extractor [`scripts/extractors/distribucion.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/distribucion.py) incluía la banda decorativa de cierre `=::::= ========= GOBIERNO DE CHILE ====== ==-== = :-=` como el último ítem numerado de la lista de distribución.

Se requiere ajustar `distribucion.py` para ignorar banners decorativos, isologos y direcciones de pie de página.

---

## 2. Lógica de Filtrado (`distribucion.py`)

Se añade al bloque de omisión dentro de `distribucion.py`:
```python
if (
    re.search(r"P[áa]gina\s+\d+\s+de\s+\d+", line_clean, re.IGNORECASE)
    or re.search(r"Ministerio\s+de\s+Vivienda\s+y\s+Urban\s*ismo", line_clean, re.IGNORECASE)
    or re.search(r"GOBIERNO\s+DE\s+CHILE", line_clean, re.IGNORECASE)
    or re.search(r"Alameda\s+924", line_clean, re.IGNORECASE)
    or re.search(r"Santiago\s*-\s*Chile", line_clean, re.IGNORECASE)
    or re.match(r"^[\=\:\-\~\s]{4,}$", line_clean)
    or re.match(r"^!+$", line_clean)
    or re.match(r"^(?:VICENTE|BURGOS|SALAS|JEFE\s+DIVISI[ÓO]N)\b", line_clean, re.IGNORECASE)
):
    continue
```

---

## 3. Criterios de Aceptación y Pruebas

1. Nueva prueba unitaria en [`test/test_extractor_body.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_body.py) verificando que `distribucion.py` no incluya la línea del banner del Gobierno de Chile.
2. Ejecución exitosa de la suite completa `pytest -v`.
3. Re-exportación del CSV de DDU 546 comprobando que la celda `lista_distribucion` finalice en el receptor 33 (`Oficina de Partes MINVU Ley 20.285`).
