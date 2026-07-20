"""Script para scrapear documentación de la BCN y guardarla secuencialmente.

Este script inicializa la estructura base del scraper y calcula el nombre del
archivo resultante de forma secuencial en la carpeta 'bcn - documentación'.
"""

import argparse
import re
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse
from bs4 import BeautifulSoup, Comment, NavigableString, PageElement, Tag


def extract_slug(url: str) -> str:
    """Extrae el slug final de una URL.

    Si la URL termina en barra, se ignora la barra final. Si no tiene ruta,
    retorna 'index'.
    """
    path = urlparse(url).path
    path_stripped = path.strip("/")
    if not path_stripped:
        return "index"
    parts = path_stripped.split("/")
    return parts[-1]


def clean_slug(slug: str) -> str:
    """Limpia el slug de caracteres inválidos para nombres de archivos."""
    # Decodificar caracteres de URL (ej. %20 -> espacio)
    decoded = unquote(slug)
    # Reemplazar caracteres no permitidos en nombres de archivos (\\ / : * ? " < > |)
    cleaned = re.sub(r'[\\\\/*?:"<>|]', "", decoded)
    # Reemplazar espacios y tabulaciones por guiones bajos
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned


def calculate_sequential_path(url: str, output_dir: Path) -> Path:
    """Calcula la ruta completa del archivo de salida de forma secuencial.

    Crea el directorio de destino si no existe.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    slug = extract_slug(url)
    cleaned_slug = clean_slug(slug)

    # Expresión regular para archivos XX_*.md (donde XX son 2 dígitos)
    pattern = re.compile(r"^\d{2}_.*\.md$")

    count = 0
    if output_dir.exists():
        for item in output_dir.iterdir():
            if item.is_file() and pattern.match(item.name):
                count += 1

    prefix = f"{count + 1:02d}"
    filename = f"{prefix}_{cleaned_slug}.md"
    return output_dir / filename


def download_html(url: str) -> str:
    """Descarga el contenido de una URL usando urllib.request con un User-Agent común.

    Maneja adecuadamente la codificación de caracteres.
    """
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    )
    with urllib.request.urlopen(req) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        content_bytes: bytes = response.read()
        return content_bytes.decode(charset, errors="replace")


def extract_id_norma(url: str) -> str | None:
    """Extrae el identificador numérico de norma desde una URL de Ley Chile."""
    parsed = urlparse(url)
    
    # 1. Buscar en query params
    qs = parse_qs(parsed.query)
    for key in ["idNorma", "normaId"]:
        if key in qs and qs[key]:
            val = qs[key][0]
            if val.isdigit():
                return val

    # 2. Buscar en todo el string de la URL usando regex
    match_query = re.search(r"[?&](?:idNorma|normaId)=(\d+)", url, re.IGNORECASE)
    if match_query:
        return match_query.group(1)

    # 3. Buscar en la ruta
    match_path = re.search(r"/(\d+)(?:/|$)", parsed.path)
    if match_path:
        return match_path.group(1)

    return None


def detect_portal(url: str) -> str:
    """Clasifica la URL en uno de los tres flujos: 'datos', 'leychile' o 'fallback'."""
    parsed = urlparse(url)
    domain = parsed.netloc.lower()
    path = parsed.path.lower()

    if domain == "datos.bcn.cl":
        return "datos"

    # Verificar si el dominio contiene leychile.cl o si es bcn.cl/leychile
    is_leychile_domain = "leychile.cl" in domain or (domain == "bcn.cl" and path.startswith("/leychile"))
    if is_leychile_domain:
        if extract_id_norma(url) is not None:
            return "leychile"

    return "fallback"


def extract_datos_bcn(html_content: str) -> tuple[str, str, str]:
    """Extrae título, descripción y cuerpo principal de una página de Datos BCN."""
    soup = BeautifulSoup(html_content, "html.parser")
    title_el = soup.select_one("#parent-fieldname-title")
    desc_el = soup.select_one("#parent-fieldname-description")
    content_el = soup.select_one("#content-core")

    title = ""
    if title_el and isinstance(title_el, Tag):
        title = title_el.get_text(strip=True)

    desc = ""
    if desc_el and isinstance(desc_el, Tag):
        desc = desc_el.get_text(strip=True)

    content_html = ""
    if content_el and isinstance(content_el, Tag):
        content_html = str(content_el)

    return title, desc, content_html


def extract_ley_chile(url: str) -> tuple[str, str, str]:
    """Extrae título, descripción vacía y contenido XML de una norma de Ley Chile."""
    id_norma = extract_id_norma(url)
    if not id_norma:
        raise ValueError(f"No se pudo extraer el identificador de norma (idNorma) de la URL: {url}")

    xml_url = f"https://www.leychile.cl/Consulta/obtienexml?opt=7&idNorma={id_norma}"
    xml_content = download_html(xml_url)

    soup = BeautifulSoup(xml_content, "html.parser")

    nombre_el = soup.find(re.compile(r"^nombre$", re.IGNORECASE))
    texto_el = soup.find(re.compile(r"^texto$", re.IGNORECASE))

    title = nombre_el.get_text(strip=True) if nombre_el and isinstance(nombre_el, Tag) else f"Norma {id_norma}"
    content_xml = str(texto_el) if texto_el and isinstance(texto_el, Tag) else ""

    return title, "", content_xml


def extract_fallback(html_content: str) -> tuple[str, str, str]:
    """Estrategia fallback para extraer contenido de portales generales de la BCN."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Remover etiquetas innecesarias
    for tag in ["script", "style", "nav", "header", "footer"]:
        for element in soup.find_all(tag):
            if isinstance(element, Tag):
                element.decompose()

    # Remover clases e IDs de navegación o pie de página comunes
    selectors_to_remove = [
        ".navigation", "#navigation", ".header", ".footer", 
        ".menu", "#menu", ".sidebar", "#sidebar", ".aside", "#aside"
    ]
    for selector in selectors_to_remove:
        for element in soup.select(selector):
            if isinstance(element, Tag):
                element.decompose()

    # Intentar obtener título de h1
    h1_el = soup.find("h1")
    title = h1_el.get_text(strip=True) if h1_el and isinstance(h1_el, Tag) else ""

    # Buscar contenedores sugeridos de forma sucesiva
    content_el = None
    for selector in ["article", "#content", ".content", "#main-content"]:
        content_el = soup.select_one(selector)
        if content_el:
            break

    # Si no se encuentra ninguno, buscar el div con mayor volumen de texto
    if not content_el:
        divs = soup.find_all("div")
        max_len = 0
        best_div = None
        for div in divs:
            if isinstance(div, Tag):
                text_content = div.get_text()
                text_len = len(text_content)
                if text_len > max_len:
                    max_len = text_len
                    best_div = div
        content_el = best_div

    content_html = str(content_el) if content_el else ""
    return title, "", content_html


def extract_content(url: str) -> tuple[str, str, str]:
    """Detecta el portal correspondiente de la URL y extrae su contenido."""
    portal = detect_portal(url)
    if portal == "leychile":
        return extract_ley_chile(url)

    html_content = download_html(url)
    if portal == "datos":
        return extract_datos_bcn(html_content)
    else:
        return extract_fallback(html_content)


def build_arg_parser() -> argparse.ArgumentParser:
    """Construye el parser de argumentos de la línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Scraper de documentación de la BCN con salida secuencial."
    )
    parser.add_argument(
        "--url",
        required=True,
        type=str,
        help="URL del documento de la BCN a scrapear.",
    )
    return parser


def _process_element(element: PageElement, page_url: str, seen_headings: set[str]) -> str:
    """Función auxiliar para procesar un PageElement de BeautifulSoup de forma recursiva.

    Usa page_url para resolver URLs relativas a absolutas y seen_headings para evitar encabezados duplicados.
    """
    if isinstance(element, Comment):
        return ""

    if isinstance(element, NavigableString):
        return str(element)

    if not isinstance(element, Tag):
        return ""

    tag_name = element.name.lower() if element.name else ""

    # 1. Encabezados: h1 a h6 se convierten a sus equivalentes # a ######.
    if tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
        level = int(tag_name[1])
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children).strip()
        if not inner_markdown:
            return ""
        
        # Limpiar puntuación final que viola la regla MD026 (ej. dos puntos o punto final)
        if inner_markdown.endswith(":") or inner_markdown.endswith("."):
            inner_markdown = inner_markdown[:-1].strip()

        # Evitar encabezados duplicados que violan la regla MD024 (se convierten a texto plano introductorio para resolver MD036)
        heading_key = inner_markdown.lower()
        if heading_key in seen_headings:
            return f"\n\n{inner_markdown}:\n\n"
        
        seen_headings.add(heading_key)
        return f"\n\n{'#' * level} {inner_markdown}\n\n"

    # 2. Párrafos e Hilos: <p>, <div>, <br> se convierten a saltos de línea (\n\n o \n).
    elif tag_name in ["p", "div"]:
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children).strip()
        if not inner_markdown:
            return ""
        return f"\n\n{inner_markdown}\n\n"

    elif tag_name == "br":
        return "\n"

    # 3. Formato: <b>/<strong> se convierte a **texto**; <i>/<em> se convierte a *texto*.
    elif tag_name in ["b", "strong"]:
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children)
        stripped = inner_markdown.strip()
        if not stripped:
            return inner_markdown
        return f"**{stripped}**"

    elif tag_name in ["i", "em"]:
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children)
        stripped = inner_markdown.strip()
        if not stripped:
            return inner_markdown
        return f"*{stripped}*"

    # 4. Enlaces: <a> se convierte a [texto](href). Si el enlace es relativo,
    # se debe resolver a absoluto usando el page_url como base.
    elif tag_name == "a":
        href = element.get("href")
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children)
        
        # Limpiar espacios al inicio/final del texto del enlace para resolver MD039
        inner_markdown_clean = inner_markdown.strip()
        
        # En Pyright Strict, element.get() puede retornar un string, una lista de strings o None.
        if isinstance(href, list):
            href_str = "".join(href)
        elif href is not None:
            href_str = str(href)
        else:
            href_str = ""

        if href_str:
            parsed_href = urlparse(href_str)
            # Si no tiene esquema (relativo) y no es ancla
            if not parsed_href.scheme and not href_str.startswith("#"):
                from urllib.parse import urljoin
                href_str = urljoin(page_url, href_str)
            return f"[{inner_markdown_clean}]({href_str})"
        else:
            return inner_markdown_clean

    # 5. Listas: <ul> y <ol> recorren sus elementos <li> para convertirlos en - item o 1. item.
    elif tag_name == "ul":
        items: list[str] = []
        for child in element.children:
            if isinstance(child, Tag) and child.name.lower() == "li":
                li_content = "".join(_process_element(c, page_url, seen_headings) for c in child.children).strip()
                items.append(f"- {li_content}")
        return "\n" + "\n".join(items) + "\n"

    elif tag_name == "ol":
        items: list[str] = []
        index = 1
        for child in element.children:
            if isinstance(child, Tag) and child.name.lower() == "li":
                li_content = "".join(_process_element(c, page_url, seen_headings) for c in child.children).strip()
                items.append(f"{index}. {li_content}")
                index += 1
        return "\n" + "\n".join(items) + "\n"

    # 6. Tablas: <table>, <tr>, <th>, <td>
    elif tag_name == "table":
        markdown_rows: list[str] = []
        rows = element.find_all("tr")
        if not rows:
            return ""
        
        # Determinar cuántas columnas tiene la tabla basándose en la primera fila
        first_row = rows[0]
        header_cells = first_row.find_all(["th", "td"])
        num_cols = len(header_cells)
        if num_cols == 0:
            return ""
            
        # Procesar filas
        for idx, row in enumerate(rows):
            if not isinstance(row, Tag):
                continue
            cells = row.find_all(["th", "td"])
            cell_markdowns: list[str] = []
            for cell in cells:
                if isinstance(cell, Tag):
                    c_md = "".join(_process_element(c, page_url, seen_headings) for c in cell.children).strip()
                    # Convertir bloques de código de triple backtick a código en línea (un backtick)
                    # para evitar saltos de línea innecesarios dentro de la celda de la tabla
                    c_md = re.sub(r"```\s*([\s\S]*?)\s*```", r"`\1`", c_md)
                    # Reemplazar múltiples saltos de línea por un espacio para evitar la necesidad de <br>
                    # y no violar la regla MD033 de HTML en línea
                    c_md_clean = re.sub(r"\n+", " ", c_md)
                    # Remover caracteres | adicionales dentro de la celda para no romper las columnas
                    c_md_clean = c_md_clean.replace("|", "\\|")
                    cell_markdowns.append(c_md_clean)
            
            # Completar con celdas vacías si la fila tiene menos columnas
            while len(cell_markdowns) < num_cols:
                cell_markdowns.append("")
                
            markdown_rows.append(f"| {' | '.join(cell_markdowns)} |")
            
            # Si es la primera fila (encabezado), añadir la línea separadora
            if idx == 0:
                separator = f"| {' | '.join(['---'] * num_cols)} |"
                markdown_rows.append(separator)
                
        return "\n\n" + "\n".join(markdown_rows) + "\n\n"

    # 7. Código: <pre> y <code>
    elif tag_name == "pre":
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children).strip()
        if not inner_markdown:
            return ""
        return f"\n\n```text\n{inner_markdown}\n```\n\n"

    elif tag_name == "code":
        inner_markdown = "".join(_process_element(child, page_url, seen_headings) for child in element.children).strip()
        if not inner_markdown:
            return ""
        return f"`{inner_markdown}`"

    # Fallback: procesamos recursivamente sus hijos
    else:
        return "".join(_process_element(child, page_url, seen_headings) for child in element.children)


def html_to_markdown(element: Tag | str, page_url: str) -> str:
    """Convierte recursivamente un elemento HTML (Tag o string) a Markdown usando page_url como base."""
    seen_headings: set[str] = set()
    if isinstance(element, str):
        # Si es un NavigableString de bs4 (que hereda de str), lo manejamos directamente como texto plano
        if isinstance(element, NavigableString):
            return str(element)
        # Si es un str común (HTML crudo), lo parseamos
        soup = BeautifulSoup(element, "html.parser")
        return "".join(_process_element(child, page_url, seen_headings) for child in soup.children)

    return _process_element(element, page_url, seen_headings)


def normalize_headings(markdown_text: str) -> str:
    """Normaliza los niveles de encabezados para asegurar un incremento gradual (MD001)."""
    lines = markdown_text.split("\n")
    normalized_lines: list[str] = []
    last_level = 1  # El título principal es de nivel 1 (#)
    
    for line in lines:
        # Buscamos encabezados como #, ##, ###, etc.
        match = re.match(r"^(#+)(.*)$", line)
        if match:
            hashes, content = match.groups()
            current_level = len(hashes)
            
            if current_level > 1:
                # Si se salta más de un nivel respecto al último visto, lo ajustamos
                if current_level > last_level + 1:
                    new_level = last_level + 1
                    line = f"{'#' * new_level}{content}"
                    last_level = new_level
                else:
                    last_level = current_level
            normalized_lines.append(line)
        else:
            normalized_lines.append(line)
            
    return "\n".join(normalized_lines)


def main() -> None:
    """Función principal del script."""
    args = build_arg_parser().parse_args()

    # El script está en repo/scripts/bcn_doc_scraper.py, la raíz es repo/
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    output_dir = repo_root / "bcn - documentación"

    # 1. Extraer el contenido
    try:
        title, desc, content_html = extract_content(args.url)
    except Exception as e:
        print(f"Error al extraer contenido de la URL: {args.url}. Detalles: {e}")
        return

    # 2. Convertir HTML a Markdown usando html_to_markdown
    # Se usa args.url (URL de la página) en lugar de base_url
    body_markdown = html_to_markdown(content_html, args.url)

    # Remover encabezado inicial redundante si es idéntico al título (MD024)
    title_escaped = re.escape(title)
    pattern_duplicate_header = re.compile(rf"^#+\s+{title_escaped}\s*$", re.IGNORECASE)
    body_markdown_lines = body_markdown.split("\n")
    if body_markdown_lines:
        for i, line in enumerate(body_markdown_lines):
            if line.strip():
                if pattern_duplicate_header.match(line.strip()):
                    body_markdown_lines[i] = ""
                break
        body_markdown = "\n".join(body_markdown_lines)

    # 3. Ensamblar el documento
    document_parts: list[str] = []
    document_parts.append(f"# {title}")
    
    if desc and desc.strip():
        document_parts.append(f"> {desc.strip()}")
        
    if body_markdown.strip():
        document_parts.append(body_markdown.strip())

    document_markdown = "\n\n".join(document_parts)
    
    # 4. Limpieza de Espacios: Colapsar múltiples saltos de línea consecutivos a un máximo de dos (\n\n)
    document_markdown = re.sub(r"\n{3,}", "\n\n", document_markdown)
    
    # Normalizar niveles de encabezados para resolver MD001
    document_markdown = normalize_headings(document_markdown)
    
    # Reemplazar tabulaciones por espacios para resolver MD010
    document_markdown = document_markdown.replace("\t", "    ")
    
    # Limpiar espacios en blanco al final de cada línea (trailing spaces) para resolver MD009
    document_markdown = "\n".join(line.rstrip() for line in document_markdown.split("\n"))
    
    document_markdown = document_markdown.strip() + "\n"

    # 5. Calcular ruta y guardar en archivo
    final_path = calculate_sequential_path(args.url, output_dir)
    try:
        with open(final_path, "w", encoding="utf-8") as f:
            f.write(document_markdown)
        print(final_path.resolve())
    except Exception as e:
        print(f"Error al guardar el archivo en {final_path}. Detalles: {e}")


if __name__ == "__main__":
    main()
