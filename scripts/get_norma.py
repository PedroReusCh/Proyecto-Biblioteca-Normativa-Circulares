#!/usr/bin/env python3
"""Script CLI para obtener normas desde la API Ley Chile de la BCN."""

import argparse
import sys
from pathlib import Path
from typing import Final

# Asegurar que la raíz del proyecto está en sys.path para importaciones
ROOT_DIR: Final[Path] = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.leychile_api import LeyChileAPI


def main(argv: list[str] | None = None) -> int:
    """Función principal del CLI."""
    parser = argparse.ArgumentParser(
        description="Obtiene una norma desde la API Ley Chile y la guarda localmente."
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Identificador numérico de la norma.",
    )
    parser.add_argument(
        "--format",
        choices=["xml", "json"],
        default="xml",
        help="Formato de la norma a descargar (xml o json). Por defecto xml.",
    )

    args: argparse.Namespace = parser.parse_args(argv)
    id_norma: str = str(args.id)
    formato: str = str(args.format)

    # Validar que el ID sea numérico
    if not id_norma.isdigit():
        print(f"Error: El --id proporcionado ('{id_norma}') debe ser numérico.", file=sys.stderr)
        return 1

    id_servicio: str = "7" if formato == "xml" else "7.2"

    try:
        print(f"Instanciando LeyChileAPI para obtener norma {id_norma}...")
        api = LeyChileAPI()

        print(f"Consultando servicio {id_servicio} para norma {id_norma}...")
        contenido: str = api.consultar_servicio(id_servicio, {"idNorma": id_norma})

        # Directorio de salida
        out_dir: Path = ROOT_DIR / "bcn - consultas"
        out_dir.mkdir(parents=True, exist_ok=True)

        filename: str = f"servicio_{id_servicio}_{id_norma}.{formato}"
        filepath: Path = out_dir / filename

        print(f"Guardando respuesta en {filepath}...")
        filepath.write_text(contenido, encoding="utf-8")
        print("Operación completada con éxito.")
        return 0

    except ValueError as e:
        print(f"Error de configuración: {e}", file=sys.stderr)
        return 2
    except PermissionError as e:
        print(f"Error de permisos de API BCN: {e}", file=sys.stderr)
        return 3
    except FileNotFoundError as e:
        print(f"Error: El servicio o la norma no fue encontrada: {e}", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
