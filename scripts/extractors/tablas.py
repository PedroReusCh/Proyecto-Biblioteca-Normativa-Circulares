"""Extractor modular de Tablas con pdfplumber y análisis tabular (TablasExtractor)."""

import argparse
import csv
from dataclasses import asdict
import json
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Sequence


_PROYECTO_RAIZ = Path(__file__).resolve().parents[2]
if str(_PROYECTO_RAIZ) not in sys.path:
    sys.path.insert(0, str(_PROYECTO_RAIZ))

try:
    from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from scripts.extractors.utils_cleaner import limpiar_palabras_ocr
except ImportError:
    from extractors.base import BaseExtractor, ResultadoBloque, register_extractor
    from extractors.utils_cleaner import limpiar_palabras_ocr


def normalizar_texto_celda_tabla(texto: str) -> str:
    """Normaliza el contenido de una celda tabular uniendo saltos de línea continuos y preservando estructura lógica."""
    if not texto:
        return ""
    texto = limpiar_palabras_ocr(str(texto).strip())
    lineas = [l.strip() for l in texto.splitlines() if l.strip()]
    if not lineas:
        return ""

    patron_nuevo_bloque = re.compile(
        r"^(?:"
        r"[a-zA-ZáéíóúÁÉÍÓÚ]\)\s+|"                 # a), b), c)
        r"[a-zA-ZáéíóúÁÉÍÓÚ]\.\s+|"                 # a., b., c.
        r"\d+[\.\)]\s+|"                            # 1., 2., 1), 2)
        r"(?:i|ii|iii|iv|v|vi|vii|viii|ix|x)\)\s+|" # i), ii), iii)
        r"[-•*]\s+|"                                # viñetas
        r"Mediante\s+Circular| "                    # Notas de modificación
        r"Por\s+la\s+siguiente:| "                  # Cláusulas de sustitución
        r"Reemplázase\b| "
        r"Se\s+deja\s+sin\s+efecto\b"
        r")",
        re.IGNORECASE,
    )


    parrafos: List[str] = []
    parrafo_actual: List[str] = []

    for l in lineas:
        if parrafo_actual and patron_nuevo_bloque.match(l):
            parrafos.append(" ".join(parrafo_actual))
            parrafo_actual = [l]
        else:
            parrafo_actual.append(l)

    if parrafo_actual:
        parrafos.append(" ".join(parrafo_actual))

    resultado = "\n".join(parrafos)
    resultado = re.sub(r" +", " ", resultado)
    return resultado.strip()


def _limpiar_texto_celda(celda: Any) -> str:
    """Limpia y sanea el texto de una celda tabular aplicando corrección OCR y flujo continuo."""
    if celda is None:
        return ""
    return normalizar_texto_celda_tabla(str(celda))



def _compactar_tabla_pdf(raw_table: List[List[Any]]) -> Optional[Dict[str, Any]]:
    """Procesa y normaliza una tabla extraída por pdfplumber estructurando encabezados y filas."""
    if not raw_table or len(raw_table) < 2:
        return None

    # 1. Limpieza de texto celda por celda
    cleaned_rows: List[List[str]] = [
        [_limpiar_texto_celda(c) for c in row]
        for row in raw_table
    ]

    # Filtrar filas completamente vacías o con símbolos residuales únicos
    non_empty_rows = [r for r in cleaned_rows if any(bool(c) for c in r)]
    if len(non_empty_rows) < 2:
        return None

    # 2. Detección de encabezados multi-línea
    r0 = non_empty_rows[0]
    r1 = non_empty_rows[1] if len(non_empty_rows) > 1 else []

    is_multi_header = False
    if len(non_empty_rows) >= 3:
        r1_non_empty = [c for c in r1 if c]
        if len(r1_non_empty) <= 2 and not any("ddu" in c.lower() or "art" in c.lower() for c in r1_non_empty):
            is_multi_header = True

    if is_multi_header:
        header_raw: List[str] = []
        max_len = max(len(r0), len(r1))
        r0_pad = r0 + [""] * (max_len - len(r0))
        r1_pad = r1 + [""] * (max_len - len(r1))
        for c0, c1 in zip(r0_pad, r1_pad):
            combined = f"{c0} {c1}".strip()
            header_raw.append(combined)
        data_rows_raw = non_empty_rows[2:]
    else:
        header_raw = r0
        data_rows_raw = non_empty_rows[1:]

    # Encabezados limpios no vacíos
    encabezados = [h.replace("\n", " ").strip() for h in header_raw if h.strip()]
    if not encabezados:
        encabezados = [f"Columna {i + 1}" for i in range(len(header_raw))]

    num_cols = len(encabezados)

    # 3. Alinear filas de datos
    filas_finales: List[List[str]] = []
    for r in data_rows_raw:
        non_empty = [c for c in r if c]
        if not non_empty:
            continue

        aligned_row = [""] * num_cols

        if len(r) == len(header_raw):
            header_indices = [idx for idx, h in enumerate(header_raw) if h.strip()]
            for target_idx, orig_idx in enumerate(header_indices):
                if orig_idx < len(r) and r[orig_idx]:
                    aligned_row[target_idx] = r[orig_idx]

            if sum(1 for c in aligned_row if c) < len(non_empty):
                if not r[0] and len(non_empty) < num_cols:
                    for i, val in enumerate(non_empty):
                        if i + 1 < num_cols:
                            aligned_row[i + 1] = val
                else:
                    for i, val in enumerate(non_empty[:num_cols]):
                        aligned_row[i] = val
        else:
            for i, val in enumerate(non_empty[:num_cols]):
                aligned_row[i] = val

        filas_finales.append(aligned_row)

    if not filas_finales:
        return None

    # 4. Construir representación Markdown
    md_lines: List[str] = []
    headers_clean = [h.replace("\n", " ").strip() for h in encabezados]
    md_lines.append("| " + " | ".join(headers_clean) + " |")
    md_lines.append("| " + " | ".join(["---"] * num_cols) + " |")
    for f in filas_finales:
        row_clean = [c.replace("\n", " ").strip() for c in f]
        md_lines.append("| " + " | ".join(row_clean) + " |")

    return {
        "encabezados": encabezados,
        "filas": filas_finales,
        "markdown": "\n".join(md_lines),
    }


def _consolidar_tablas_multipagina(tablas_crudas: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Consolida tablas consecutivas con encabezados idénticos en una sola tabla lógica.

    Cuando pdfplumber detecta tablas en páginas diferentes que comparten los mismos
    encabezados (mismo número y nombres de columnas), se fusionan concatenando sus
    filas. Las filas cuya primera columna está vacía se tratan como continuaciones
    de la fila precedente, concatenando su texto.

    Returns:
        Lista de tablas consolidadas con campo 'paginas' (lista de int).
    """
    if not tablas_crudas:
        return []

    consolidadas: List[Dict[str, Any]] = []
    actual: Optional[Dict[str, Any]] = None

    for t in tablas_crudas:
        enc: List[str] = t["encabezados"]
        filas: List[List[str]] = t["filas"]
        pag: int = int(t["pagina"])

        if actual is not None and actual["encabezados"] == enc:
            # Mismos encabezados: fusionar filas
            for fila in filas:
                if fila[0].strip() == "" and actual["filas"]:
                    # Fila de continuación: concatenar con la última fila existente
                    ultima = actual["filas"][-1]
                    for i in range(len(fila)):
                        if i < len(ultima):
                            sep = "\n" if fila[i].strip() else ""
                            combinado = (ultima[i] + sep + fila[i]).strip()
                            ultima[i] = normalizar_texto_celda_tabla(combinado)
                else:
                    actual["filas"].append([normalizar_texto_celda_tabla(c) for c in fila])
            actual["paginas"].append(pag)
        else:
            # Nueva tabla lógica (encabezados distintos o primera tabla)
            if actual is not None:
                consolidadas.append(actual)
            actual = {
                "encabezados": [normalizar_texto_celda_tabla(h).replace("\n", " ") for h in enc],
                "filas": [[normalizar_texto_celda_tabla(c) for c in fila] for fila in filas],
                "paginas": [pag],
            }

    if actual is not None:
        consolidadas.append(actual)

    return consolidadas


def _determinar_nombre_tabla(encabezados: List[str], filas: List[List[str]], paginas: List[int]) -> str:
    """Genera un nombre descriptivo para una tabla a partir de sus encabezados y contenido."""
    todo_texto = " ".join(encabezados + [c for fila in filas for c in fila])
    circulares_mencionadas: List[str] = []
    for ddu_id in ["DDU 339", "DDU 322", "DDU 168"]:
        if ddu_id in todo_texto:
            circulares_mencionadas.append(ddu_id)
    if circulares_mencionadas:
        return f"Modificaciones Normativas ({', '.join(circulares_mencionadas)})"
    if any("modifica" in h.lower() or "circular" in h.lower() for h in encabezados):
        rango = f"Pág. {paginas[0]}-{paginas[-1]}" if len(paginas) > 1 else f"Pág. {paginas[0]}"
        return f"Tabla de Modificaciones Normativas ({rango})"
    if encabezados:
        rango = f"Pág. {paginas[0]}-{paginas[-1]}" if len(paginas) > 1 else f"Pág. {paginas[0]}"
        return f"Tabla: {', '.join(encabezados[:2])} ({rango})"
    return f"Tabla técnica (Pág. {paginas[0]})"


def _exportar_tabla_csv(encabezados: List[str], filas: List[List[str]], destino_csv: Path) -> None:
    """Exporta una tabla individual como archivo CSV estructurado."""
    destino_csv.parent.mkdir(parents=True, exist_ok=True)
    with open(destino_csv, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")
        writer.writerow([normalizar_texto_celda_tabla(h).replace("\n", " ") for h in encabezados])
        filas_limpias = [
            [normalizar_texto_celda_tabla(c) for c in fila]
            for fila in filas
        ]
        writer.writerows(filas_limpias)



def _extraer_tablas_lineas(lines: Sequence[str] | List[str]) -> List[Dict[str, Any]]:
    """Extrae tablas en formato Markdown presentes en una lista de líneas de texto."""

    tablas: List[Dict[str, Any]] = []
    idx = 0
    n = len(lines)

    while idx < n:
        line = lines[idx].strip()
        if line.startswith("|") and line.endswith("|") and line.count("|") >= 3:
            # Posible inicio de tabla Markdown
            table_lines: List[str] = [line]
            idx += 1
            while idx < n and lines[idx].strip().startswith("|") and lines[idx].strip().endswith("|"):
                table_lines.append(lines[idx].strip())
                idx += 1

            if len(table_lines) >= 3:
                raw_headers = [c.strip() for c in table_lines[0].split("|")[1:-1]]
                encabezados = [_limpiar_texto_celda(h) for h in raw_headers]
                filas: List[List[str]] = []

                # Saltar la línea delimitadora (fila 1 con ---)
                for tl in table_lines[2:]:
                    cells = [c.strip() for c in tl.split("|")[1:-1]]
                    cleaned_cells = [_limpiar_texto_celda(c) for c in cells]
                    filas.append(cleaned_cells)

                if encabezados and filas:
                    tablas.append({
                        "pagina": 1,
                        "encabezados": encabezados,
                        "filas": filas,
                        "markdown": "\n".join(table_lines),
                    })
        else:
            idx += 1

    return tablas


@register_extractor
class TablasExtractor(BaseExtractor):
    """Extractor modular para tablas normativas y comparativas en circulares DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "tablas"

    def extract(
        self,
        raw_text: str,
        lines: Sequence[str] | List[str],
        pdf_path: Optional[Path] = None,
        output_dir: Optional[Path] = None,
    ) -> ResultadoBloque:

        """Extrae tablas estructuradas usando pdfplumber o análisis de líneas de texto y genera manifiesto.

        Args:
            raw_text: Texto completo de la circular.
            lines: Lista de líneas limpias.
            pdf_path: Ruta opcional al archivo PDF para extracción nativa con pdfplumber.
            output_dir: Directorio opcional de salida para guardar los CSVs de tablas.

        Returns:
            ResultadoBloque con la lista de manifiesto ligero de tablas extraídas.
        """
        tablas_crudas: List[Dict[str, Any]] = []

        if pdf_path is not None and pdf_path.exists():
            try:
                import importlib
                pdfplumber_mod: Any = importlib.import_module("pdfplumber")

                with pdfplumber_mod.open(pdf_path) as pdf:
                    for p_idx, page in enumerate(pdf.pages):
                        num_pag = p_idx + 1
                        raw_tables = page.extract_tables()
                        if not raw_tables:
                            continue
                        for raw_t in raw_tables:
                            res = _compactar_tabla_pdf(raw_t)
                            if res is not None:
                                tablas_crudas.append({
                                    "pagina": num_pag,
                                    "encabezados": res["encabezados"],
                                    "filas": res["filas"],
                                    "markdown": res["markdown"],
                                })
            except Exception as e:
                return ResultadoBloque(
                    nombre_bloque=self.nombre_bloque,
                    exito=False,
                    datos={"tablas": []},
                    confianza=0.0,
                    observaciones=f"Error al procesar PDF con pdfplumber: {e}",
                )

        if not tablas_crudas:
            tablas_crudas = _extraer_tablas_lineas(lines)

        if not tablas_crudas:
            return ResultadoBloque(
                nombre_bloque=self.nombre_bloque,
                exito=False,
                datos={"tablas": []},
                confianza=0.0,
                observaciones="No se detectaron tablas en el documento.",
            )

        # Consolidar tablas multi-página con encabezados idénticos
        tablas_consolidadas = _consolidar_tablas_multipagina(tablas_crudas)

        # Determinar identificador base DDU (ej. DDU_456)
        num_str = "desconocido"
        if pdf_path is not None:
            m_pdf = re.search(r"\b(\d+)\b", pdf_path.stem)
            if m_pdf:
                num_str = m_pdf.group(1)
        if num_str == "desconocido" and raw_text:
            m_txt = re.search(r"DDU\s*(\d+)", raw_text, re.IGNORECASE)
            if m_txt:
                num_str = m_txt.group(1)

        dir_tablas = output_dir if output_dir is not None else (_PROYECTO_RAIZ / "salidas_tablas")
        dir_tablas.mkdir(parents=True, exist_ok=True)

        manifest_tablas: List[Dict[str, Any]] = []
        for idx, t in enumerate(tablas_consolidadas, start=1):
            tabla_id = f"DDU_{num_str}_tabla_{idx}"
            encabezados: List[str] = t["encabezados"]
            filas: List[List[str]] = t["filas"]
            paginas: List[int] = t["paginas"]
            nombre = _determinar_nombre_tabla(encabezados, filas, paginas)
            csv_filename = f"{tabla_id}.csv"
            csv_path = dir_tablas / csv_filename

            _exportar_tabla_csv(encabezados, filas, csv_path)

            rel_path = f"salidas_tablas/{csv_filename}"
            manifest_tablas.append({
                "id": tabla_id,
                "nombre": nombre,
                "paginas": paginas,
                "filas": len(filas),
                "columnas": len(encabezados),
                "archivo_anexo": rel_path,
            })

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=True,
            datos={"tablas": manifest_tablas},
            confianza=1.0,
            observaciones=f"Se extrajeron {len(manifest_tablas)} tabla(s) consolidada(s) y se exportaron a {dir_tablas.name}/.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Tablas Extractor Standalone con pdfplumber")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    parser.add_argument("--output-dir", type=str, default="salidas_tablas", help="Directorio de salida para tablas")
    args = parser.parse_args()

    target_pdf = Path(args.pdf)
    extractor = TablasExtractor()
    resultado_bloque = extractor.extract(
        raw_text="",
        lines=[],
        pdf_path=target_pdf,
        output_dir=Path(args.output_dir),
    )
    print(json.dumps(asdict(resultado_bloque), indent=2, ensure_ascii=False))
