"""Extractor de la firma y firmante de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List, Optional

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor
from scripts.extractors.utils_cleaner import limpiar_palabras_ocr, preservar_casing


def _limpiar_texto_firma(texto: str) -> str:
    """Repara distorsiones típicas de OCR en nombres, cargos y ministerios del firmante."""
    texto = limpiar_palabras_ocr(texto)
    texto = re.sub(r"^(?:[_\s\-|\.\~:\xad,]+)?(?:JUAN\s+|N\s+)?DIEGO\s+[IZ]*QUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\b(?:JUAN\s+|N\s+)?DIEGO\s+[IZ]*QUIERDO\s+HEVIA\b", "JUAN DIEGO IZQUIERDO HEVIA", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\b(?:D\s+VISI|IS[IÍÓ\?I\ufffd\s]+N)\s+DE\s+DESARROLLO\s+URBANO\b", "DIVISIÓN DE DESARROLLO URBANO", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bD\s+VISI[ÓO\?I\ufffd\s]+N\b", "DIVISIÓN", texto, flags=re.IGNORECASE)
    texto = re.sub(r"\bDIVISI[ÓO\?I\ufffd\s]+N\b", lambda m: preservar_casing(m.group(0), "División"), texto, flags=re.IGNORECASE)
    texto = re.sub(r"\b(?:MINIST\s*RIO|IS\s+RIO)\b", "MINISTERIO", texto, flags=re.IGNORECASE)
    return texto



def _es_nombre_persona(line: str) -> bool:
    """Evalúa si una cadena de texto tiene el formato de un nombre de persona válido (2 o más palabras)."""
    palabras_descarte = {
        "MOTIVO", "CONSIDERACIONES", "MATERIA", "MATERIAS", "OBSERVACIONES",
        "ANTECEDENTES", "CIRCULAR", "TABLA", "CUADRO", "MODIFICA", "MODIFICAN",
        "DISTRIBUCION", "DISTRIBUCIÓN", "MINISTERIO", "VIVIENDA", "URBANISMO",
        "DIVISIÓN", "DIVISION", "DESARROLLO", "URBANO", "GOBIERNO", "CHILE",
        "ORD", "DDU", "OFPA", "ANT", "MAT", "DE", "A", "PARA", "SANTIAGO",
        "SALUDA", "ATENTAMENTE", "PÁGINA", "PAGINA", "FECHA", "SUBSECRETARIO",
        "SUBSECRETARIA", "MINISTRO", "MINISTRA", "CONTRALOR", "CONTRALORA",
    }
    line_clean = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", " ", line).strip()
    tokens = [w for w in line_clean.split() if len(w) >= 2 and w[0].isupper()]
    if len(tokens) < 2:
        return False
    # No debe contener palabras exclusivas de cargos/organismos
    if any(t.upper() in palabras_descarte for t in tokens):
        return False
    return True



def _extraer_nombre_firma_ocr(pdf_path: Path) -> Optional[str]:
    """Extrae el nombre de la persona firmante directamente desde la imagen de la página de firma con RapidOCR."""
    if not pdf_path.exists():
        return None

    try:
        import io
        fitz_mod: Any = importlib.import_module("fitz")
        rapidocr_mod: Any = importlib.import_module("rapidocr_onnxruntime")
        pil_image_mod: Any = importlib.import_module("PIL.Image")

        doc: Any = fitz_mod.open(str(pdf_path))
        img_byte_arr = io.BytesIO()
        try:
            p_firma_idx: int = -1
            num_pages: int = int(len(doc))
            for i in reversed(range(num_pages)):
                page_i: Any = doc[i]
                t: str = str(page_i.get_text())
                if re.search(r"Saluda\s+atentamente", t, re.IGNORECASE):
                    p_firma_idx = i
                    break

            if p_firma_idx == -1:
                p_firma_idx = num_pages - 1

            page: Any = doc[p_firma_idx]
            pix: Any = page.get_pixmap(dpi=300)
            img_bytes: bytes = bytes(pix.tobytes("png"))
            img: Any = pil_image_mod.open(io.BytesIO(img_bytes))
            size_tuple: Any = getattr(img, "size")
            w: int = int(size_tuple[0])
            h: int = int(size_tuple[1])

            rect_saludo: Optional[Any] = None
            rect_cargo: Optional[Any] = None
            blocks: List[Any] = list(page.get_text("blocks"))
            for b in blocks:
                texto_bloque: str = str(b[4])
                if re.search(r"Saluda\s+atentamente", texto_bloque, re.IGNORECASE):
                    rect_saludo = b[:4]
                if re.search(r"Jefe\s+Divisi[óo]n|DIVISI[ÓO]N\s+DE\s+DESARROLLO", texto_bloque, re.IGNORECASE):
                    rect_cargo = b[:4]

            page_rect: Any = getattr(page, "rect")
            page_w: float = float(page_rect.width)
            page_h: float = float(page_rect.height)
            scale_x: float = float(w) / page_w
            scale_y: float = float(h) / page_h

            if rect_cargo is not None:
                cargo_left: float = float(rect_cargo[0])
                cargo_top: float = float(rect_cargo[1])
                cargo_right: float = float(rect_cargo[2])
                cargo_bot: float = float(rect_cargo[3])
                saludo_top: float = float(rect_saludo[1]) if rect_saludo is not None else (cargo_top - 80.0)

                y_top: float = saludo_top
                y_bot: float = cargo_bot + 20.0
                x0: int = max(0, int((cargo_left - 100.0) * scale_x))
                y0: int = max(0, int((y_top - 20.0) * scale_y))
                x1: int = min(w, int((cargo_right + 100.0) * scale_x))
                y1: int = min(h, int((y_bot + 20.0) * scale_y))
                sig_crop: Any = img.crop((x0, y0, x1, y1))
            else:
                crop_box = (int(float(w) * 0.2), int(float(h) * 0.35), int(float(w) * 0.9), int(float(h) * 0.75))
                sig_crop: Any = img.crop(crop_box)

            sig_crop.save(img_byte_arr, format="PNG")
        finally:
            doc.close()

        rapid_ocr_cls: Any = getattr(rapidocr_mod, "RapidOCR")
        engine: Any = rapid_ocr_cls()
        ocr_res_tuple: Any = engine(img_byte_arr.getvalue())
        res_list: Any = ocr_res_tuple[0] if (ocr_res_tuple and ocr_res_tuple[0]) else None
        if not res_list:
            return None

        res: List[Any] = list(res_list)
        # Buscar el nombre inmediatamente arriba del cargo
        for i, item in enumerate(res):
            text: str = str(item[1]).strip()
            if re.search(r"Jefe\s+Divisi|Desarrollo\s+Urbano|DIVISI[ÓO]N", text, re.IGNORECASE):
                for prev_idx in range(i - 1, -1, -1):
                    prev_item: Any = res[prev_idx]
                    prev_text: str = str(prev_item[1]).strip()
                    if len(prev_text) >= 5 and not re.search(r"Saluda|atentamente|Ud\.|DE\b", prev_text, re.IGNORECASE):
                        # Normalizar nombres pegados por OCR
                        prev_text = re.sub(r"\bENRIQUEMATUSCHKA\b", "ENRIQUE MATUSCHKA", prev_text, flags=re.IGNORECASE)
                        prev_text = re.sub(r"\bAYCAGUER\b", "AYÇAGUER", prev_text, flags=re.IGNORECASE)
                        prev_text = re.sub(r"([A-ZÁÉÍÓÚÑa-z]{4,})(MATUSCHKA|BURGOS|SERRA|IZQUIERDO|LOPEZ|GIMENEZ)", r"\1 \2", prev_text)
                        if _es_nombre_persona(prev_text):
                            return prev_text
                break
    except Exception as e:
        print(f"Advertencia al ejecutar OCR de firma con RapidOCR: {e}")

    return None



@register_extractor
class FirmaExtractor(BaseExtractor):
    """Extractor para identificar el firmante (nombre y cargo estructurado) de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "firma"

    def extract(
        self,
        raw_text: str,
        lines: List[str],
        pdf_path: Optional[Path] = None,
    ) -> ResultadoBloque:
        """Extrae la información del firmante de la circular DDU con nombre y cargo separados.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.
            pdf_path: Ruta opcional al archivo PDF para OCR visual de firmas.

        Returns:
            ResultadoBloque con firmante, nombre_firmante y cargo_firmante.
        """
        nombre_str = ""
        cargo_str = ""
        patron_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )
        palabras_descarte = {
            "MOTIVO", "CONSIDERACIONES", "MATERIA", "MATERIAS", "OBSERVACIONES",
            "ANTECEDENTES", "CIRCULAR", "TABLA", "CUADRO", "MODIFICA", "MODIFICAN",
        }

        # 1. Buscar patrón "Saluda atentamente..." y extraer las líneas de la firma
        idx_saludo = -1
        for i, line in enumerate(lines):
            if re.search(r"Saluda\s+atentamente", line, re.IGNORECASE) or re.search(
                r"^Atentamente\b", line, re.IGNORECASE
            ):
                idx_saludo = i
                break

        cargos_patron = r"(?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI[OA]|SECRETARI[OA]|DIVISI[ÓO\?I\ufffd\s]+N\s+DE\s+DESARROLLO\s+URBANO)"

        if idx_saludo != -1:
            partes_firma: List[str] = []
            for line in lines[idx_saludo + 1 : idx_saludo + 16]:
                line_clean = line.strip()
                if not line_clean:
                    continue
                # Detener si llegamos al bloque de distribución o pie de página institucional
                if re.match(
                    patron_distribucion,
                    line_clean,
                    re.IGNORECASE,
                ) or re.search(r"Ministerio\s+de\s+Vivienda\s+y\s+Urbanismo\s*-\s*Alameda", line_clean, re.IGNORECASE):
                    break

                # Descartar cabeceras de tabla o textos residuales
                palabras_linea = set(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]+\b", line_clean.upper()))
                if palabras_linea and palabras_linea.issubset(palabras_descarte):
                    continue
                if re.match(r"^[\d\/\-\(\)\,\.\s\:\_~|]+$", line_clean):
                    continue

                # Limpiar caracteres ruidosos de firma o sellos de OCR
                line_clean = re.sub(r"^[_\s\-|\.\~:]+", "", line_clean).strip()
                if line_clean:
                    partes_firma.append(_limpiar_texto_firma(line_clean))

            if partes_firma:
                # 1.1 Localizar línea del cargo
                idx_cargo = -1
                for j, p in enumerate(partes_firma):
                    if re.search(cargos_patron, p, re.IGNORECASE):
                        idx_cargo = j
                        cargo_str = p
                        # Si hay continuación del cargo o ministerio en la línea siguiente
                        if j + 1 < len(partes_firma) and re.search(r"MINISTERIO\s+DE\s+VIVIENDA", partes_firma[j + 1], re.IGNORECASE):
                            cargo_str += ", " + partes_firma[j + 1]
                        break

                # 1.2 Buscar candidato a nombre o identificador de firmante prioritariamente arriba del cargo
                lineas_previas = partes_firma[:idx_cargo] if idx_cargo != -1 else partes_firma
                for p in reversed(lineas_previas):
                    candidato = _limpiar_texto_firma(p)
                    # A) Nombre completo de persona (2 o más palabras)
                    if _es_nombre_persona(candidato) or re.search(r"JUAN\s+DIEGO|VICENTE|PAZ|RODRIGO", candidato, re.IGNORECASE):
                        nombre_limpio = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", candidato).strip()
                        nombre_str = nombre_limpio
                        break

                # Si aún no hay nombre y hay líneas posteriores al cargo
                if not nombre_str and idx_cargo != -1 and idx_cargo + 1 < len(partes_firma):
                    for p in partes_firma[idx_cargo + 1:]:
                        if re.search(r"MINISTERIO", p, re.IGNORECASE):
                            continue
                        candidato = _limpiar_texto_firma(p)
                        if _es_nombre_persona(candidato):
                            nombre_str = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", candidato).strip()
                            break

                # Si no encontramos cargo formal pero hay líneas limpias
                if not cargo_str and partes_firma:
                    partes_limpias = [
                        p for p in partes_firma
                        if not re.search(r"[\/\~\*\<\>\(\)\;\\]", p)
                        and len(re.findall(r"\b[A-ZÁÉÍÓÚÑa-z]{3,}\b", p)) > 0
                        and not any(w in p.upper() for w in palabras_descarte)
                    ]
                    if partes_limpias:
                        cargo_str = ", ".join(partes_limpias)

        # 1.3 Si aún no tenemos nombre completo, buscar en el bloque de cierre previo a la distribución final
        if not nombre_str:
            idx_dist_final = -1
            mitad_doc = int(len(lines) * 0.5)
            for i in range(len(lines) - 1, mitad_doc, -1):
                l_cand = lines[i]
                if re.search(r"^(?:DISTRIBUCI[ÓO]N|1\.\s+Sr\.\s+Ministro|Sr\.\s+Ministro\s+de\s+Vivienda)", l_cand, re.IGNORECASE):
                    idx_dist_final = i
                    for prev_d in range(i - 1, max(mitad_doc, i - 4), -1):
                        if re.search(r"^(?:DISTRIBUCI[ÓO]N)", lines[prev_d], re.IGNORECASE):
                            idx_dist_final = prev_d
                            break
                    break

            if idx_dist_final != -1:
                pre_lineas = lines[max(0, idx_dist_final - 10) : idx_dist_final]
                for pl in reversed(pre_lineas):
                    pl_limpia = _limpiar_texto_firma(pl)
                    if _es_nombre_persona(pl_limpia) or re.search(r"JUAN\s+DIEGO|VICENTE|PAZ|RODRIGO", pl_limpia, re.IGNORECASE):
                        nombre_str = re.sub(r"[^A-ZÁÉÍÓÚÑa-z\s]", "", pl_limpia).strip()
                        break
                if not cargo_str:
                    for pl in pre_lineas:
                        pl_limpia = _limpiar_texto_firma(pl)
                        if re.search(cargos_patron, pl_limpia, re.IGNORECASE):
                            cargo_str = pl_limpia
                            break

        # 2. Si falta cargo o nombre, verificar cabecera DE: en las primeras páginas
        if not cargo_str or not nombre_str:
            for line in lines[:30]:
                line_clean = line.strip()
                m_de = re.search(r"^\s*DE\s*:\s*(.+)$", line_clean, re.IGNORECASE)
                if not m_de:
                    m_de = re.search(r"^\s*DE\s+((?:JEFE|DIRECTOR|MINISTRO|SUBSECRETARI|SECRETARI)[A-ZÁÉÍÓÚÑ\s]{5,})", line_clean, re.IGNORECASE)
                if m_de:
                    texto_de = m_de.group(1).strip().rstrip(".")
                    partes_de = [p.strip() for p in re.split(r"[,–—\-]", texto_de) if p.strip()]

                    for p_de in partes_de:
                        p_de_limpio = _limpiar_texto_firma(p_de)
                        if not nombre_str and _es_nombre_persona(p_de_limpio):
                            nombre_str = p_de_limpio
                        elif not cargo_str and re.search(cargos_patron, p_de_limpio, re.IGNORECASE):
                            cargo_str = p_de_limpio

        # 3. Si aún no tenemos un nombre completo de persona, intentar OCR visual directo sobre el recorte de la firma
        if not _es_nombre_persona(nombre_str) and pdf_path is not None:
            nombre_ocr = _extraer_nombre_firma_ocr(pdf_path)
            if nombre_ocr and _es_nombre_persona(nombre_ocr):
                nombre_str = nombre_ocr

        # 4. Limpieza final y normalización
        nombre_str = _limpiar_texto_firma(nombre_str).strip()
        cargo_str = _limpiar_texto_firma(cargo_str).strip()

        if nombre_str and cargo_str:
            firmante = f"{nombre_str}, {cargo_str}"
        elif nombre_str:
            firmante = nombre_str
        else:
            firmante = cargo_str

        firmante = re.sub(r"\s+", " ", firmante).strip()
        if firmante.endswith("."):
            firmante = firmante[:-1].strip()

        exito = bool(firmante)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "firmante": firmante,
                "nombre_firmante": nombre_str,
                "cargo_firmante": cargo_str,
            },
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró firmante en la circular.",
        )



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Firma Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = FirmaExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
