"""Script de prueba para validar la integridad y alineación de columnas de los CSV de la BCN."""

import csv
import sys
from pathlib import Path


def validar_csv(file_path: Path, expected_cols: int) -> bool:
    """Verifica que cada fila de un archivo CSV tenga exactamente el número esperado de columnas.

    Args:
        file_path: Ruta al archivo CSV.
        expected_cols: Número esperado de columnas en la cabecera.

    Returns:
        True si el archivo es válido, False en caso contrario.
    """
    if not file_path.exists():
        print(f"ERROR: El archivo no existe en: {file_path}")
        return False

    print(f"Validando estructura de: {file_path.name}")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            
            if len(header) != expected_cols:
                print(f"  [FALLO] La cabecera tiene {len(header)} columnas, se esperaban {expected_cols}.")
                print(f"  Cabecera encontrada: {header}")
                return False
                
            print(f"  [OK] Cabecera correcta con {expected_cols} columnas.")
            
            for line_idx, row in enumerate(reader, start=2):
                if len(row) != expected_cols:
                    print(f"  [FALLO] Línea {line_idx} tiene {len(row)} columnas, se esperaban {expected_cols}.")
                    print(f"  Contenido de la fila: {row}")
                    return False
                    
            print(f"  [OK] Todas las filas están perfectamente alineadas.")
            return True
            
    except Exception as e:
        print(f"  [ERROR] Ocurrió un error leyendo el archivo: {e}")
        return False


def test_csv_integrity() -> None:
    proyecto_raiz = Path(__file__).resolve().parents[1]
    
    # Buscar en 'bcn - documentación' de forma compatible
    doc_dir = proyecto_raiz / "bcn - documentación"
    if not doc_dir.exists():
        doc_dir = proyecto_raiz / "bcn - documentacion"
        
    csv_diccionario = doc_dir / "diccionario_dato_akoma_ntoso.csv"
    csv_secuencia = doc_dir / "secuencia_planilla_akoma_ntoso.csv"
    
    # 1. Validar Diccionario de Datos (6 columnas esperadas)
    success_dicc = validar_csv(csv_diccionario, 6)
    
    # 2. Validar Secuencia de Plantilla (6 columnas esperadas)
    success_sec = validar_csv(csv_secuencia, 6)
    
    print("\nResumen de Validacion:")
    print(f"  Diccionario de Datos: {'PASO' if success_dicc else 'FALLO'}")
    print(f"  Secuencia de Plantilla: {'PASO' if success_sec else 'FALLO'}")
    
    assert success_dicc, "Diccionario de Datos CSV no es válido."
    assert success_sec, "Secuencia de Plantilla CSV no es válida."


if __name__ == "__main__":
    test_csv_integrity()
