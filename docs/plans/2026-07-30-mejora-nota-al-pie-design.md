# Especificación de Diseño: Captura Multilínea y Delimitación Dinámica en `NotaAlPieExtractor`

**Fecha:** 2026-07-30  
**Proyecto:** Biblioteca Normativa Circulares DDU (MINVU)  
**Estado:** Aprobado por el usuario  

---

## 1. Contexto y Problema

En circulares DDU como la **DDU 546**, las notas al pie de página abarcan múltiples líneas continuas de texto explicativo (ej. la Nota 1 y 3 en la página 2 de la DDU 546 contienen varios renglones). El extractor simple actual capturaba únicamente la primera línea de cada nota al pie.

Se requiere implementar una **Máquina de Estados Multilínea** en [`scripts/extractors/nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/scripts/extractors/nota_al_pie.py) que acumule el texto completo de cada nota y delimite dinámicamente el fin de cada nota al pie.

---

## 2. Lógica de Delimitación Dinámica (Máquina de Estados)

### 2.1 Inicios de Nota al Pie
Una nota al pie inicia cuando una línea cumple el patrón de prefijo numérico (1-20) seguido de texto que contiene palabras clave normativas (`Artículo`, `Circular`, `Orientación`, `Guía`, `Decreto`, `Ley`, `Construcción`, `Edificación`, `OGUC`, `LGUC`, etc.), descartando falsos positivos de párrafos del cuerpo (`1. `, `2. `) y pies de página institucionales (`Página X de Y`).

### 2.2 Acumulación Multilínea
Cualquier línea subsecuente que no constituya un nuevo inicio de nota ni un pie institucional se añade al contenido de la nota en curso.

### 2.3 Criterios de Delimitación de Fin
La acumulación de la nota actual se detiene de forma automática ante:
1. **Nuevo inicio de nota** (`2 ...`, `3 ...`): Guarda la nota previa y abre una nueva.
2. **Pie Institucional / Membrete** (`--========= GOBIERNO DE CHILE`, `Ministerio de Vivienda y Urbanismo... Página X de Y`): Cierra la nota actual y resetea la máquina de estados.
3. **Cierre de Documento** (`Saluda atentamente`, `DISTRIBUCIÓN:`): Cierra la nota actual y finaliza el escaneo.

---

## 3. Formato de Salida

Cada nota al pie se consolida en una frase única continua (unificando saltos de línea), y las distintas notas al pie se concatenan usando el separador ` | `.

---

## 4. Criterios de Aceptación y Pruebas
1. Actualización de [`test/test_extractor_nota_al_pie.py`](file:///C:/Users/preusc/Documents/Proyecto%20Biblioteca%20Normativa%20Ciculares/test/test_extractor_nota_al_pie.py) incluyendo casos multilínea para la DDU 546.
2. Ejecución exitosa de la suite completa de pruebas: `pytest -v` (30/30 PASSED).
3. Exportación correcta del CSV de DDU 546 con el texto completo multilínea de sus 3 notas al pie en la celda `notas_al_pie`.
