#!/usr/bin/env python3
"""Script CLI para obtener la estructura jerárquica (árbol) de una norma desde la API Ley Chile de la BCN."""

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
    """Función principal del CLI para obtener la estructura en árbol de una norma."""
    parser = argparse.ArgumentParser(
        description="Obtiene la estructura jerárquica (árbol) de una norma desde la API Ley Chile."
    )
    parser.add_argument(
        "--id",
        required=True,
        help="Identificador numérico de la norma.",
    )

    args: argparse.Namespace = parser.parse_args(argv)
    id_norma: str = str(args.id)

    # Validar que el ID sea numérico
    if not id_norma.isdigit():
        print(f"Error: El --id proporcionado ('{id_norma}') debe ser numérico.", file=sys.stderr)
        return 1

    id_servicio: str = "9"

    try:
        print(f"Instanciando LeyChileAPI para obtener estructura en árbol de la norma {id_norma}...")
        api = LeyChileAPI()

        print(f"Consultando servicio {id_servicio} para norma {id_norma}...")
        contenido: str = api.consultar_servicio(id_servicio, {"idNorma": id_norma})

        # Directorio de salida
        out_dir: Path = ROOT_DIR / "bcn - consultas"
        out_dir.mkdir(parents=True, exist_ok=True)

        filename: str = f"servicio_{id_servicio}_{id_norma}.xml"
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
