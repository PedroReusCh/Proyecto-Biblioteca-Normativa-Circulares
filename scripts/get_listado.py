#!/usr/bin/env python3
"""Script CLI para obtener el listado masivo de IDs de normas desde la API Ley Chile de la BCN (Servicio 39)."""

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
    """Función principal del CLI para obtener el listado masivo de IDs de normas."""
    parser = argparse.ArgumentParser(
        description="Obtiene el listado masivo de IDs de normas desde la API Ley Chile (Servicio 39)."
    )

    # No se requieren argumentos adicionales posicionales u obligatorios,
    # pero argparse procesará automáticamente --help / -h
    _args: argparse.Namespace = parser.parse_args(argv)

    id_servicio: Final[str] = "39"

    try:
        print("Instanciando LeyChileAPI...")
        api = LeyChileAPI()

        print(f"Consultando servicio de listado masivo (Servicio {id_servicio})...")
        contenido: str = api.consultar_servicio(id_servicio)

        # Directorio de salida
        out_dir: Path = ROOT_DIR / "bcn - consultas"
        out_dir.mkdir(parents=True, exist_ok=True)

        filename: str = f"servicio_{id_servicio}_listado.xml"
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
        print(f"Error: El servicio no fue encontrado: {e}", file=sys.stderr)
        return 4
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}", file=sys.stderr)
        return 5


if __name__ == "__main__":
    sys.exit(main())
