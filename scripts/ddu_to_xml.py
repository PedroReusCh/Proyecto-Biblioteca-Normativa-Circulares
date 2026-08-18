"""Constructor Estructural Akoma Ntso XML para Circulares DDU.

Este módulo implementa la clase DDUToXML encargada de transformar la estructura de datos
extraída de los PDFs de circulares DDU en documentos XML Akoma Ntso v2.0 BCN conformes.
"""

from datetime import date
import re
from typing import Any, Dict, List, Optional

try:
    from scripts.ddu_types import DatosCircularDDU, SeccionDDU
except ImportError:
    from ddu_types import DatosCircularDDU, SeccionDDU




class _XMLBuilder:
    """Clase helper para construir XML con indentación controlada de forma limpia."""

    def __init__(self) -> None:
        self.lines: List[str] = []
        self.level: int = 0

    def add(self, text: str) -> None:
        """Agrega una línea de XML con la indentación actual."""
        indent = "  " * self.level
        self.lines.append(f"{indent}{text}")

    def indent(self) -> None:
        """Incrementa el nivel de indentación."""
        self.level += 1

    def dedent(self) -> None:
        """Decrementa el nivel de indentación."""
        if self.level > 0:
            self.level -= 1

    def get_xml(self) -> str:
        """Retorna el documento XML completo como string."""
        return "\n".join(self.lines)


class DDUToXML:
    """Clase encargada de construir la estructura XML Akoma Ntso v2.0 BCN a partir de circulares DDU."""

    def __init__(self) -> None:
        """Inicializa la clase DDUToXML."""
        pass

    def _xml_escape(self, texto: str) -> str:
        """Escapa caracteres especiales requeridos por el estándar XML.

        Args:
            texto: Texto plano.

        Returns:
            Texto escapado.
        """
        return (
            texto.replace("&", "&amp;")
                 .replace("<", "&lt;")
                 .replace(">", "&gt;")
                 .replace('"', "&quot;")
                 .replace("'", "&apos;")
         )

    def _formatear_fecha_legible(self, fecha_iso: str) -> str:
        """Formatea una fecha ISO (YYYY-MM-DD) a formato legible en español.

        Args:
            fecha_iso: Fecha en formato ISO.

        Returns:
            Fecha en texto legible (ej: 17 de febrero de 2023).
        """
        if not fecha_iso:
            return ""
        partes = fecha_iso.split("-")
        if len(partes) != 3:
            return fecha_iso
        yyyy, mm, dd = partes
        meses = {
            "01": "enero",
            "02": "febrero",
            "03": "marzo",
            "04": "abril",
            "05": "mayo",
            "06": "junio",
            "07": "julio",
            "08": "agosto",
            "09": "septiembre",
            "10": "octubre",
            "11": "noviembre",
            "12": "diciembre",
        }
        mes_str = meses.get(mm, "de")
        try:
            dia_int = int(dd)
            return f"{dia_int} de {mes_str} de {yyyy}"
        except ValueError:
            return f"{dd} de {mes_str} de {yyyy}"

    def _aplicar_referencias_citas(self, texto: str, prefix_id: str = "ref") -> str:
        """Identifica menciones de normas (OGUC, LGUC) en el texto y las envuelve en etiquetas <ref>.

        Args:
            texto: Texto en el cual buscar citas normativas.
            prefix_id: Prefijo único para generar atributos id válidos e irrepetibles.

        Returns:
            Texto con las citas transformadas a elementos <ref>.
        """
        patron_citas = re.compile(
            r'(?P<art_oguc>\bart(?:[ií]culo|[ií]c)?\.?\s+(?P<num_oguc>\d+\.\d+\.\d+(?:\.\d+)*)\.?(?:\s+de\s+la\s+OGUC|\s+de\s+la\s+Ordenanza\s+General\s+de\s+Urbanismo\s+y\s+Construcciones)?\b)|'
            r'(?P<art_lguc>\bart(?:[ií]culo|[ií]c)?\.?\s+(?P<num_lguc>\d+(?:\s+(?:bis|ter|quater))?)\.?(?:\s+de\s+la\s+LGUC|\s+de\s+la\s+Ley\s+General\s+de\s+Urbanismo\s+y\s+Construcciones|\s+del\s+D\.F\.L\.\s*(?:N[°oº])?\s*458(?:\s+de\s+1975)?|\s+del\s+DFL\s*458)\b)|'
            r'(?P<oguc_completa>\bOrdenanza\s+General\s+de\s+Urbanismo\s+y\s+Construcciones\b|\bOGUC\b)|'
            r'(?P<lguc_completa>\bLey\s+General\s+de\s+Urbanismo\s+y\s+Construcciones\b|\bL\.G\.U\.C\.\b|\bLGUC\b|\bD\.F\.L\.\s*(?:N[°oº])?\s*458(?:\s+de\s+1975)?\b|\bDFL\s*(?:N[°oº])?\s*458\b)',
            re.IGNORECASE
        )

        ref_idx = 0

        def reemplazar_cita(m: re.Match[str]) -> str:
            nonlocal ref_idx
            ref_idx += 1
            ref_id = f"{prefix_id}_{ref_idx}"
            gd = m.groupdict()
            if gd.get("art_oguc"):
                num_oguc = gd["num_oguc"]
                if num_oguc:
                    num_oguc_clean = num_oguc.strip(".").strip()
                    num_normalizado = num_oguc_clean.lower().replace(" ", "-")
                    uri = f"http://datos.bcn.cl/recurso/cl/dto/ministerio-de-vivienda-y-urbanismo/1992-05-19/47/seccion/articulo-{num_normalizado}"
                    return f'<ref id="{ref_id}" href="{uri}">{m.group(0)}</ref>'
            elif gd.get("art_lguc"):
                num_lguc = gd["num_lguc"]
                if num_lguc:
                    num_lguc_clean = num_lguc.strip(".").strip()
                    num_normalizado = num_lguc_clean.lower().replace(" ", "-")
                    uri = f"http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-vivienda-y-urbanismo/1976-04-13/458/seccion/articulo-{num_normalizado}"
                    return f'<ref id="{ref_id}" href="{uri}">{m.group(0)}</ref>'
            elif gd.get("oguc_completa"):
                uri = "http://datos.bcn.cl/recurso/cl/dto/ministerio-de-vivienda-y-urbanismo/1992-05-19/47"
                return f'<ref id="{ref_id}" href="{uri}">{m.group(0)}</ref>'
            elif gd.get("lguc_completa"):
                uri = "http://datos.bcn.cl/recurso/cl/dfl/ministerio-de-vivienda-y-urbanismo/1976-04-13/458"
                return f'<ref id="{ref_id}" href="{uri}">{m.group(0)}</ref>'
            return m.group(0)

        return patron_citas.sub(reemplazar_cita, texto)

    def _parsear_manifiesto_o_lista(self, valor: Any) -> List[Dict[str, Any]]:
        """Convierte una lista de diccionarios o una cadena de manifiesto plano en lista de dicts."""
        if not valor:
            return []
        if isinstance(valor, list):
            return [item for item in valor if isinstance(item, dict)]

        texto_manifiesto = str(valor).strip()
        if not texto_manifiesto:
            return []

        elementos: List[Dict[str, Any]] = []
        bloques = texto_manifiesto.split(" || ")
        for bloque in bloques:
            d: Dict[str, Any] = {}
            partes = bloque.split("; ")
            for p in partes:
                if ":" in p:
                    k, v = p.split(":", 1)
                    d[k.strip()] = v.strip()
            if d:
                elementos.append(d)
        return elementos

    def _obtener_info_modificacion_posterior(self, mod_texto: str) -> Optional[Dict[str, str]]:
        """Extrae la información estructurada clave de la nota de modificación posterior."""
        if not mod_texto or not mod_texto.strip():
            return None
        texto = mod_texto.strip()

        # Extraer DDU modificadora (ej: DDU 498)
        m_ddu = re.search(r"\bDDU\s*(\d+)\b", texto, re.IGNORECASE)
        ddu_num = m_ddu.group(1) if m_ddu else ""
        if not ddu_num:
            return None

        # Extraer fecha (ej: 02 de mayo de 2024 o 02.05.2024)
        m_fecha = re.search(r"(\d{1,2})\s+de\s+([a-zA-ZáéíóúÁÉÍÓÚ]+)\s+de\s+(\d{4})", texto, re.IGNORECASE)
        meses = {
            "enero": "01", "febrero": "02", "marzo": "03", "abril": "04", "mayo": "05", "junio": "06",
            "julio": "07", "agosto": "08", "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
        }
        if m_fecha:
            dia = m_fecha.group(1).zfill(2)
            mes_str = m_fecha.group(2).lower()
            mes = meses.get(mes_str, "01")
            ano = m_fecha.group(3)
            fecha_iso = f"{ano}-{mes}-{dia}"
        else:
            m_fecha_num = re.search(r"(\d{2})[\.\/](\d{2})[\.\/](\d{4})", texto)
            if m_fecha_num:
                fecha_iso = f"{m_fecha_num.group(3)}-{m_fecha_num.group(2)}-{m_fecha_num.group(1)}"
            else:
                fecha_iso = "0000-00-00"

        # Extraer numeral afectado si existe (ej. numeral 7)
        m_num = re.search(r"numeral\s*(\d+)", texto, re.IGNORECASE)
        numeral_dest = f"#par_1_{m_num.group(1)}" if m_num else "#par_1_1"

        return {
            "ddu_num": ddu_num,
            "ddu_id": f"ddu-{ddu_num}",
            "fecha": fecha_iso,
            "uri": f"http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha_iso}/DDU {ddu_num}",
            "numeral_dest": numeral_dest,
            "texto": texto,
        }

    def generar_xml(self, datos: DatosCircularDDU) -> str:
        """Genera un documento XML Akoma Ntso v2.0 BCN a partir de los datos estructurados.

        Args:
            datos: Datos estructurados de la circular.

        Returns:
            String con el documento XML Akoma Ntso formateado de forma limpia.
        """
        numero: str = str(datos.get("numero", "")).strip()
        fecha: str = str(datos.get("fecha", "")).strip()
        materia: str = str(datos.get("materia", "")).strip()
        secciones: List[SeccionDDU] = datos.get("secciones", [])

        fecha_generacion: str = date.today().isoformat()
        fecha_legible: str = self._formatear_fecha_legible(fecha)
        materia_escapada: str = self._xml_escape(materia)

        builder = _XMLBuilder()
        builder.add('<?xml version="1.0" encoding="utf-8"?>')
        builder.add('<doc name="circular"')
        builder.indent()
        builder.add('xmlns="http://www.akomantoso.org/2.0"')
        builder.add('xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"')
        builder.add('xsi:schemaLocation="http://www.akomantoso.org/2.0 ../bcn%20-%20documentaci%C3%B3n/Esquema%20Akoma-Ntoso%20BCN.xsd">')

        builder.dedent()

        # Bloque <meta>
        builder.add('<meta>')
        builder.indent()

        # 1. identification
        builder.add('<identification source="#redactor">')
        builder.indent()

        # FRBRWork
        builder.add('<FRBRWork>')
        builder.indent()
        builder.add(f'<FRBRthis value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}/main"/>')
        builder.add(f'<FRBRuri value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}"/>')
        builder.add(f'<FRBRdate date="{fecha}" name="fecha-publicacion"/>')
        builder.add('<FRBRauthor href="#minvu-ddu" as="#autor"/>')
        builder.add('<FRBRcountry value="cl"/>')
        builder.dedent()
        builder.add('</FRBRWork>')

        # FRBRExpression
        builder.add('<FRBRExpression>')
        builder.indent()
        builder.add(f'<FRBRthis value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}/espanol/main"/>')
        builder.add(f'<FRBRuri value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}/espanol"/>')
        builder.add(f'<FRBRdate date="{fecha}" name="fecha-publicacion"/>')
        builder.add('<FRBRauthor href="#minvu-ddu" as="#autor"/>')
        builder.add('<FRBRlanguage language="es"/>')
        builder.dedent()
        builder.add('</FRBRExpression>')

        # FRBRManifestation
        builder.add('<FRBRManifestation>')
        builder.indent()
        builder.add(f'<FRBRthis value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}/espanol/datos.xml"/>')
        builder.add(f'<FRBRuri value="http://datos.bcn.cl/recurso/cl/circular/minvu-ddu/{fecha}/{numero}/espanol/datos.xml"/>')
        builder.add(f'<FRBRdate date="{fecha_generacion}" name="fecha-generacion"/>')
        builder.add('<FRBRauthor href="#redactor" as="#editor"/>')
        builder.add('<FRBRformat value="xml"/>')
        builder.dedent()
        builder.add('</FRBRManifestation>')

        builder.dedent()
        builder.add('</identification>')

        # 2. classification (Descriptores)
        descriptores: str = str(datos.get("descriptores", "")).strip()
        if descriptores:
            builder.add('<classification source="#minvu-ddu">')
            builder.indent()
            builder.add(f'<keyword value="{self._xml_escape(descriptores)}" showAs="Descriptores" dictionary="http://datos.bcn.cl/recurso/cl/descriptores"/>')
            builder.dedent()
            builder.add('</classification>')

        # 3. lifecycle (Modificaciones Posteriores / Hitos de vigencia)
        mod_info = self._obtener_info_modificacion_posterior(str(datos.get("modificaciones_posteriores", "")))
        if mod_info:
            builder.add('<lifecycle source="#minvu-ddu">')
            builder.indent()
            builder.add(f'<eventRef id="evento_mod_1" date="{mod_info["fecha"]}" source="#{mod_info["ddu_id"]}" type="amendment"/>')
            builder.dedent()
            builder.add('</lifecycle>')

        # 4. analysis (Modificaciones Pasivas / Normas modificadoras)
        if mod_info:
            builder.add('<analysis source="#redactor">')
            builder.indent()
            builder.add('<passiveModifications>')
            builder.indent()
            builder.add('<textualMod id="mod_1" type="substitution">')
            builder.indent()
            builder.add(f'<source href="{mod_info["uri"]}"/>')
            builder.add(f'<destination href="{mod_info["numeral_dest"]}"/>')
            builder.dedent()
            builder.add('</textualMod>')
            builder.dedent()
            builder.add('</passiveModifications>')
            builder.dedent()
            builder.add('</analysis>')

        # 5. references
        builder.add('<references source="#redactor">')
        builder.indent()
        builder.add('<TLCOrganization id="redactor" href="http://datos.bcn.cl/recurso/cl/organismo/biblioteca-del-congreso-nacional" showAs="Biblioteca del Congreso Nacional"/>')
        builder.add('<TLCOrganization id="minvu" href="http://datos.bcn.cl/recurso/cl/organismo/ministerio-de-vivienda-y-urbanismo" showAs="Ministerio de Vivienda y Urbanismo"/>')
        builder.add('<TLCOrganization id="minvu-ddu" href="http://datos.bcn.cl/recurso/cl/organismo/ministerio-de-vivienda-y-urbanismo/division-de-desarrollo-urbano" showAs="División de Desarrollo Urbanismo"/>')
        builder.add('<TLCPerson id="jefe-division-desarrollo-urbano" href="http://datos.bcn.cl/recurso/cl/persona/jefe-division-desarrollo-urbano" showAs="Jefe División de Desarrollo Urbano"/>')
        builder.add('<TLCRole id="autor" href="http://datos.bcn.cl/recurso/cl/rol/autor" showAs="Autor"/>')
        builder.add('<TLCRole id="editor" href="http://datos.bcn.cl/recurso/cl/rol/editor" showAs="Editor"/>')
        if mod_info:
            builder.add(f'<TLCReference id="{mod_info["ddu_id"]}" name="circular-modificadora" href="{mod_info["uri"]}" showAs="Circular DDU {mod_info["ddu_num"]}"/>')
        builder.dedent()
        builder.add('</references>')

        builder.dedent()
        builder.add('</meta>')

        numero_clean = re.sub(r"^DDU\s*", "", numero, flags=re.IGNORECASE).strip()

        # Bloque <preface>
        builder.add('<preface>')
        builder.indent()
        builder.add('<p><docType>CIRCULAR</docType></p>')
        builder.add(f'<p><docNumber>DDU {numero_clean}</docNumber></p>')
        builder.add(f'<p><docDate date="{fecha}">{fecha_legible}</docDate></p>')
        builder.add(f'<p><docTitle>{materia_escapada}</docTitle></p>')

        if descriptores:
            builder.add(f'<p>Descriptores: {self._xml_escape(descriptores)}</p>')
        builder.dedent()
        builder.add('</preface>')

        # Extraer lista de imágenes si existen
        imagenes_list = self._parsear_manifiesto_o_lista(datos.get("imagenes") or datos.get("imagenes_manifiesto"))
        imagenes_pendientes: List[Dict[str, Any]] = list(imagenes_list)

        # Bloque <mainBody>
        builder.add('<mainBody>')
        builder.indent()

        for idx_sec, seccion in enumerate(secciones, 1):
            titulo_sec: str = str(seccion.get("titulo", "")).strip()
            parrafos: List[str] = seccion.get("parrafos", [])

            # Intentamos separar número romano del título
            match_romano = re.match(r"^([IVXLCDM]+\.?)\s+(.+)$", titulo_sec, re.IGNORECASE)
            if match_romano:
                num_sec = match_romano.group(1)
                heading_sec = match_romano.group(2)
            else:
                num_sec = ""
                heading_sec = titulo_sec

            heading_sec_escapado: str = self._xml_escape(heading_sec)
            sec_id = f"sec_{idx_sec}"

            builder.add(f'<section id="{sec_id}">')
            builder.indent()

            if num_sec:
                builder.add(f'<num>{self._xml_escape(num_sec)}</num>')
            if heading_sec_escapado:
                builder.add(f'<heading>{heading_sec_escapado}</heading>')

            for idx_par, parrafo_texto in enumerate(parrafos, 1):
                parrafo_texto_str = str(parrafo_texto).strip()
                if not parrafo_texto_str:
                    continue

                # Intentamos extraer número del párrafo (arábigo)
                match_par = re.match(r"^(\d+(?:\.\d+)*\.?)\s+(.+)$", parrafo_texto_str)
                if match_par:
                    num_par = match_par.group(1)
                    texto_par = match_par.group(2)
                else:
                    num_par = ""
                    texto_par = parrafo_texto_str

                # Intentamos extraer subtítulo en mayúsculas dentro del numeral
                heading_par = ""
                match_sub = re.match(r"^([A-ZÁÉÍÓÚÑ\s\d\"'()\─\-–—:]+\.)\s+(.+)$", texto_par)
                if not match_sub:
                    match_sub = re.match(r"^([A-ZÁÉÍÓÚÑ\s\d\"'()\─\-–—:]+:)\s+(.+)$", texto_par)
                if match_sub:
                    heading_par = match_sub.group(1).strip()
                    texto_par = match_sub.group(2).strip()

                par_id = f"par_{idx_sec}_{idx_par}"
                texto_escapado: str = self._xml_escape(texto_par)
                texto_procesado: str = self._aplicar_referencias_citas(texto_escapado, prefix_id=f"ref_{par_id}")

                # Identificar y formatear listas multinivel del cuerpo con saltos de línea <eol/>
                texto_procesado = re.sub(r"\s+([a-z\d]+\)\s+)", r"<eol/>\1", texto_procesado)

                builder.add(f'<paragraph id="{par_id}">')
                builder.indent()

                if num_par:
                    builder.add(f'<num>{self._xml_escape(num_par)}</num>')

                if heading_par:
                    builder.add(f'<heading>{self._xml_escape(heading_par)}</heading>')

                builder.add('<content>')
                builder.indent()
                builder.add(f'<p>{texto_procesado}</p>')

                # Inyectar elemento <img> si el párrafo introduce un esquema o plano técnico (máximo una vez por imagen)
                if imagenes_pendientes:
                    texto_lower = texto_par.lower()
                    imgs_a_inyectar: List[Dict[str, Any]] = []
                    for img in list(imagenes_pendientes):
                        es_ddu_456 = "ddu 456" in numero.lower()
                        es_ddu_547 = "ddu 547" in numero.lower()
                        if (
                            "esquema ilustrativo" in texto_lower
                            or "siguiente esquema" in texto_lower
                            or "siguiente figura" in texto_lower
                            or (es_ddu_456 and num_par in ["4.", "4"])
                            or (es_ddu_547 and ("urbanizaciones voluntarias desvinculadas" in texto_lower or num_par in ["7.", "7"]))
                        ):
                            imgs_a_inyectar.append(img)
                            imagenes_pendientes.remove(img)

                    for img in imgs_a_inyectar:
                        img_id = self._xml_escape(str(img.get("id", f"img_{idx_sec}_{idx_par}")))
                        img_src = self._xml_escape(str(img.get("archivo_anexo", "salidas_imagenes/DDU_456_img_1.png")))
                        img_alt = self._xml_escape(str(img.get("descripcion", img.get("nombre", "Esquema ilustrativo"))))
                        img_w = str(img.get("ancho", "1761"))
                        img_h = str(img.get("alto", "543"))
                        builder.add(f'<p><img id="{img_id}" src="{img_src}" alt="{img_alt}" width="{img_w}" height="{img_h}"/></p>')


                builder.dedent()
                builder.add('</content>')

                builder.dedent()
                builder.add('</paragraph>')


            builder.dedent()
            builder.add('</section>')

        builder.dedent()
        builder.add('</mainBody>')

        # Bloque <conclusions> (para firma, notas al pie y lista de distribución)
        firmante: str = str(datos.get("firmante", "")).strip()
        notas_al_pie: str = str(datos.get("notas_al_pie", "")).strip()
        distribucion_raw = datos.get("distribucion_texto") or datos.get("lista_distribucion") or ""
        if isinstance(distribucion_raw, list):
            lista_distribucion: str = "; ".join([str(item) for item in distribucion_raw if str(item).strip()]).strip()
        else:
            lista_distribucion: str = str(distribucion_raw).strip()

        if firmante or lista_distribucion or notas_al_pie:
            builder.add('<conclusions>')
            builder.indent()
            if firmante:
                builder.add(f'<p><span refersTo="#jefe-division-desarrollo-urbano">{self._xml_escape(firmante)}</span></p>')
            if notas_al_pie:
                builder.add(f'<p><authorialNote id="fn_1" placement="bottom"><p>Notas al Pie: {self._xml_escape(notas_al_pie)}</p></authorialNote></p>')
            if lista_distribucion:
                builder.add(f'<p>Distribución: {self._xml_escape(lista_distribucion)}</p>')
            builder.dedent()
            builder.add('</conclusions>')

        # Bloque <attachments> (para tablas normativas anexas)
        tablas_list = self._parsear_manifiesto_o_lista(datos.get("tablas") or datos.get("tablas_manifiesto"))
        if tablas_list:
            builder.add('<attachments>')
            builder.indent()
            for t in tablas_list:
                t_id = self._xml_escape(str(t.get("id", "tabla_1")))
                t_src = self._xml_escape(str(t.get("archivo_anexo", f"salidas_tablas/{t_id}.csv")))
                t_nombre = self._xml_escape(str(t.get("nombre", "Tabla de Modificaciones Normativas")))
                builder.add(f'<componentRef id="{t_id}" src="{t_src}" showAs="{t_nombre}"/>')
            builder.dedent()
            builder.add('</attachments>')

        builder.add('</doc>')

        return builder.get_xml()

