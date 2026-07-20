"""Módulo para consultar la API de Ley Chile de la Biblioteca del Congreso Nacional (BCN)."""

import os
import urllib.error
import urllib.parse
import urllib.request


class LeyChileAPI:
    """Clase para interactuar con los servicios web de la API Ley Chile de la BCN."""

    def __init__(self) -> None:
        """Inicializa la clase LeyChileAPI leyendo la API Key de forma segura.

        Raises:
            ValueError: Si la variable de entorno BCN_LEYCHILE_SECRET no está configurada o está vacía.
        """
        secret: str | None = os.environ.get("BCN_LEYCHILE_SECRET")
        if not secret:
            raise ValueError(
                "La variable de entorno 'BCN_LEYCHILE_SECRET' no está configurada o está vacía.\n"
                "Por favor, configúrela en PowerShell de la siguiente forma:\n"
                "  Para la sesión actual:\n"
                "    $env:BCN_LEYCHILE_SECRET = \"tu_api_key_aqui\"\n"
                "  Para que sea permanente:\n"
                "    [System.Environment]::SetEnvironmentVariable('BCN_LEYCHILE_SECRET', 'tu_api_key_aqui', 'User')"
            )
        self._secret: str = secret

    def consultar_servicio(self, id_servicio: str, params: dict[str, str] | None = None) -> str:
        """Consulta un servicio específico de la API Ley Chile.

        Args:
            id_servicio: Identificador del servicio de la API (por ejemplo, 'xml2').
            params: Parámetros opcionales adicionales para la consulta.

        Returns:
            La respuesta del servicio como una cadena de texto.

        Raises:
            PermissionError: Si la API Key no es válida (códigos HTTP 401 o 403).
            FileNotFoundError: Si el servicio no fue encontrado (código HTTP 404).
            RuntimeError: Si ocurre otro error HTTP (5xx, etc.) o error de red.
        """
        query_params: dict[str, str] = {"secret": self._secret}
        if params:
            query_params.update(params)

        query_string: str = urllib.parse.urlencode(query_params)
        url: str = f"https://www.bcn.cl/leychile/api/v1/servicio/{id_servicio}/?{query_string}"

        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Proyecto Biblioteca Normativa (Python urllib)"}
            )
            with urllib.request.urlopen(req) as response:
                charset: str = response.headers.get_content_charset() or "utf-8"
                response_bytes: bytes = response.read()
                return response_bytes.decode(charset, errors="replace")

        except urllib.error.HTTPError as e:
            if e.code in (401, 403):
                raise PermissionError(
                    f"Error de permisos (código {e.code}) al consultar el servicio '{id_servicio}'. "
                    "Verifique que la API Key en 'BCN_LEYCHILE_SECRET' sea correcta."
                ) from e
            elif e.code == 404:
                raise FileNotFoundError(
                    f"Servicio no encontrado (código 404) para id_servicio: '{id_servicio}'."
                ) from e
            else:
                raise RuntimeError(
                    f"Error HTTP {e.code} al consultar el servicio '{id_servicio}': {e.reason}"
                ) from e
        except urllib.error.URLError as e:
            raise RuntimeError(
                f"Error de conexión al consultar el servicio '{id_servicio}': {e.reason}"
            ) from e
