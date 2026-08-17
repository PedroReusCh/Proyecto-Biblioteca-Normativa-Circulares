"""Extractor de la lista de distribución de la circular DDU."""

import argparse
from dataclasses import asdict
import importlib
import json
from pathlib import Path
import re
from typing import Any, List

from scripts.extractors.base import BaseExtractor, ResultadoBloque, register_extractor


@register_extractor
class DistribucionExtractor(BaseExtractor):
    """Extractor para la lista de distribución formal de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "distribucion"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la nómina de receptores de la lista de distribución al final de la circular.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la lista_distribucion extraída.
        """
        lista_distribucion: List[str] = []
        en_distribucion = False

        patron_encabezado_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )

def _limpiar_item_distribucion(item: str) -> str:
    """Limpia y repara distorsiones tipográficas de OCR en destinatarios de la lista de distribución."""
    # 1. Normalizar prefijo numérico ruidoso o confundido por OCR (ej: ",2.", "l.", "I.", "1!", "1 !", "2 .") -> "1. ", "2. ", "4. "
    item = re.sub(r"^[\,\!\;\:\_\-\s]+(\d+)", r"\1", item)
    item = re.sub(r"^[lIi\|][\.\!\;\:\,\_\-\s]+\s*", "1. ", item)
    item = re.sub(r"^(\d+)[\!\;\:\,\_\-]+\s*", r"\1. ", item)
    item = re.sub(r"^(\d+)\s*\.\s*", r"\1. ", item)

    # 2. Corregir siglas y palabras divididas erróneamente por OCR
    item = re.sub(r"\bMI\s+NVU\b", "MINVU", item, flags=re.IGNORECASE)
    item = re.sub(r"\bSERE\s+MI\b", "SEREMI", item, flags=re.IGNORECASE)
    item = re.sub(r"\bSER\s+VIU\b", "SERVIU", item, flags=re.IGNORECASE)
    item = re.sub(r"\bI\s+nterna\b", "Interna", item, flags=re.IGNORECASE)

    # 3. Re-ensamblar sufijos en '-ial', '-rial', '-loría' (ej: Territor ial -> Territorial, Contra loría -> Contraloría)
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{2,})\s+(ial|rial|loría)\b", r"\1\2", item, flags=re.IGNORECASE)

    # 4. Re-ensamblar sufijos terminados en '-ción' / '-ciones' (ej: Autorizac iones -> Autorizaciones)
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]+c)\s+(i[óo]n|iones)\b", r"\1\2", item, flags=re.IGNORECASE)

    # 5. Re-ensamblar plurales y terminaciones comunes
    item = re.sub(
        r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,})\s+(res|les|nes|dos|das|tos|tas|ria|rias|rios|tiva|tivas)\b",
        r"\1\2",
        item,
        flags=re.IGNORECASE,
    )

    # 6. Letra aislada al final de palabra
    item = re.sub(r"\b([a-záéíóúñA-ZÁÉÍÓÚÑ]{3,}[a-záéíóúñ])\s+([rlns])\b", r"\1\2", item, flags=re.IGNORECASE)

    correcciones = [
        (r"\bUrban\s+ismo\b", "Urbanismo"),
        (r"\bRegio\s+nales\b", "Regionales"),
        (r"\bRegio\s+nal\b", "Regional"),
        (r"\bSecreta\s+ria\b", "Secretaria"),
        (r"\bSecreta\s+rias\b", "Secretarias"),
        (r"\bSecreta\s+rios\b", "Secretarios"),
        (r"\bSubsecreta\s+ria\b", "Subsecretaria"),
        (r"\bDesarro\s+llo\b", "Desarrollo"),
        (r"\bdesarro\s+lladores\b", "desarrolladores"),
        (r"\binmobiliar\s+ios\b", "inmobiliarios"),
        (r"\bTerr\s+itorial\b", "Territorial"),
        (r"\bTerri\s+torial\b", "Territorial"),
        (r"\bDirecto\s+res\b", "Directores"),
        (r"\bReviso\s+res\b", "Revisores"),
        (r"\bI\s+ndependientes\b", "Independientes"),
        (r"\bBibliot\s+eca\b", "Biblioteca"),
        (r"\bMiniste\s+rio\b", "Ministerio"),
        (r"\bMinisteria\s+les\b", "Ministeriales"),
        (r"\bInstitu\s+to\b", "Instituto"),
        (r"\bInst\s+ituto\b", "Instituto"),
        (r"\bPlanificac\s+i[óo]n\b", "Planificación"),
        (r"\bOrdenamien\s+to\b", "Ordenamiento"),
        (r"\bOrdenam\s+iento\b", "Ordenamiento"),
        (r"\bAmbie\s+nte\b", "Ambiente"),
        (r"\bDivisi[óo]\s+n\b", "División"),
        (r"\bNaciona\s+l\b", "Nacional"),
        (r"\bContra\s+lora\b", "Contralora"),
        (r"\bUrbanis\s+tas\b", "Urbanistas"),
        (r"\bEjecut\s+ivo\b", "Ejecutivo"),
        (r"\bMunicipa\s+lidades\b", "Municipalidades"),
        (r"\bDocumentaci[óo]\s+n\b", "Documentación"),
        (r"\bfa\s+Construcci[óo]n\b", "la Construcción"),
    ]
    for p, r in correcciones:
        item = re.sub(p, r, item, flags=re.IGNORECASE)

    item = re.sub(r"[\s;]+$", "", item)
    item = re.sub(r"\s*;\s*", " ", item)
    item = re.sub(r"\s+\.", ".", item)
    return re.sub(r"\s+", " ", item).strip()


@register_extractor
class DistribucionExtractor(BaseExtractor):
    """Extractor para la lista de distribución formal de la circular DDU."""

    @property
    def nombre_bloque(self) -> str:
        return "distribucion"

    def extract(self, raw_text: str, lines: List[str]) -> ResultadoBloque:
        """Extrae la nómina de receptores de la lista de distribución al final de la circular.

        Args:
            raw_text: Texto completo del PDF.
            lines: Líneas limpias del documento.

        Returns:
            ResultadoBloque con la lista_distribucion extraída.
        """
        lista_distribucion: List[str] = []
        en_distribucion = False

        patron_encabezado_distribucion = (
            r"^(?:DISTRIBUCI[OÓ\?I\s]+N|BUCI[OÓ\?I\s]+N|STRIBUCI[OÓ\?I\s]+N|D\s*STRIBUC[I\?OÓ\s]*N|RIB[a-z\s\)\?]*[ÓO]N)[\s:]*"
        )

        idx_auto = 1
        total_lineas = len(lines)

        for i, line in enumerate(lines):
            line_clean = line.strip()
            if not line_clean:
                continue

            # Encabezado explícito DISTRIBUCIÓN: tiene prioridad absoluta (omitiendo 'A: SEGÚN DISTRIBUCIÓN' en pág 1)
            if re.match(patron_encabezado_distribucion, line_clean, re.IGNORECASE) and not re.match(r"^(?:A|PARA)\b", line_clean, re.IGNORECASE):
                lista_distribucion.clear()
                en_distribucion = True
                idx_auto = 1
                sub = re.sub(patron_encabezado_distribucion, "", line_clean, flags=re.IGNORECASE).strip()
                if sub and not re.match(r"^\d+$", sub):
                    item_clean = _limpiar_item_distribucion(sub)
                    if item_clean:
                        if not re.match(r"^\d+\.", item_clean):
                            item_clean = f"{idx_auto}. {item_clean}"
                            idx_auto += 1
                        lista_distribucion.append(item_clean)
                continue

            if not en_distribucion:
                if re.search(r"Saluda\s+atent", line_clean, re.IGNORECASE):
                    en_distribucion = True
                    continue
                elif re.match(r"^(?:(?:\d+\.|\d+\!|l\.|I\.)\s*)?(?:Sr\.|Sra\.|Sres\.)\s+(?:Ministr|Subsecretari|Contralor|Gobernador|Director|Jefe)", line_clean, re.IGNORECASE):
                    en_distribucion = True
                elif i >= total_lineas - 50 and re.match(r"^(?:Sr\.|Sra\.|1\.|1!)\b", line_clean, re.IGNORECASE):
                    en_distribucion = True



            if en_distribucion:
                # Omitir pie de página de OCR, marcas de corte, firma de emisor y banners institucionales
                if (
                    re.search(r"P[áa]gina\s+\d+", line_clean, re.IGNORECASE)
                    or re.search(r"Ministerio\s+de\s+Vivienda\s+y\s+Urban\s*ismo\s*-\s*Alameda", line_clean, re.IGNORECASE)
                    or re.search(r"GOBIERNO\s+DE\s+CHILE", line_clean, re.IGNORECASE)
                    or re.search(r"Alameda\s+924", line_clean, re.IGNORECASE)
                    or re.search(r"Santiago\s*-\s*Chile", line_clean, re.IGNORECASE)
                    or re.match(r"^[\=\:\-\~\s]{4,}$", line_clean)
                    or re.match(r"^!+$", line_clean)
                    or re.match(r"^(?:JUAN|DIEGO|IZQUIERDO|HEVIA|MATUSCHKA|ENRIQUE|AY[ÇC]AGUER|VICENTE|BURGOS|SALAS|JEFE\s+DIVISI[ÓO]N|DIVISI[ÓO]N\s+DE\s+DESARROLLO|MINISTERIO\s+DE\s+VIVIENDA)\b", line_clean, re.IGNORECASE)
                    or re.match(r"^[\.,\s\~]+\s*k1", line_clean, re.IGNORECASE)
                ):
                    continue

                item_clean = _limpiar_item_distribucion(line_clean)
                if item_clean and len(item_clean) >= 3:
                    tiene_num = re.match(r"^\d+\.", item_clean)
                    if not tiene_num:
                        # Si el item previo no termina en punto o termina en conectores, es continuación de línea
                        if lista_distribucion and (
                            re.search(r"(?:y|e|de|del|al|para|en|la|el|los|las|,)$", lista_distribucion[-1].strip(), re.IGNORECASE)
                            or not lista_distribucion[-1].strip().endswith(".")
                        ):
                            lista_distribucion[-1] = lista_distribucion[-1].rstrip(",") + " " + item_clean
                            continue
                        else:
                            item_clean = f"{idx_auto}. {item_clean}"
                            idx_auto += 1
                    else:
                        m_num = re.match(r"^(\d+)\.", item_clean)
                        if m_num:
                            idx_auto = int(m_num.group(1)) + 1

                    lista_distribucion.append(item_clean)


        exito = len(lista_distribucion) > 0
        distribucion_texto = "; ".join(lista_distribucion)

        return ResultadoBloque(
            nombre_bloque=self.nombre_bloque,
            exito=exito,
            datos={
                "lista_distribucion": lista_distribucion,
                "distribucion_texto": distribucion_texto,
            },
            confianza=1.0 if exito else 0.0,
            observaciones="" if exito else "No se encontró lista de distribución en la circular.",
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ETL Distribucion Extractor Standalone")
    parser.add_argument("--pdf", type=str, required=True, help="Ruta al archivo PDF")
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    pypdf_mod: Any = importlib.import_module("pypdf")
    pdf_reader: Any = pypdf_mod.PdfReader(pdf_path)
    pdf_pages: Any = pdf_reader.pages
    text_list: List[str] = [str(getattr(p, "extract_text", lambda: "")() or "") for p in pdf_pages]
    raw_text: str = "\n".join(text_list)
    lines: List[str] = [line.strip() for line in raw_text.splitlines()]

    extractor = DistribucionExtractor()
    resultado = extractor.extract(raw_text, lines)
    print(json.dumps(asdict(resultado), indent=2, ensure_ascii=False))
