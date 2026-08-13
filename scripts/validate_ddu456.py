# scripts/validate_ddu456.py
"""Validacion de extraccion DDU 456 usando extractores actuales.

NOTA: Este script usa el orquestador existente (scripts/ddu_orchestrator.py)
SIN CAMBIOS. Se adapta a su interfaz real:
  - Constructor sin argumentos: DDUOrchestrator()
  - Extraccion de un PDF: process_pdf(Path) -> DatosCircularDDU (un dict)

El codigo de ejemplo del brief (DDUOrchestrator(pdf_path).extract()) NO es
compatible con el orquestador actual; ver task-3-report.md (NEEDS_CONTEXT).
"""
import sys
from pathlib import Path

sys.path.insert(0, ".")

from scripts.ddu_orchestrator import DDUOrchestrator


def validate_ddu456():
    """Ejecuta el orquestador sobre DDU 456, genera CSV y reporta campos vacios."""
    pdf_path = "circulares/DDU 456.pdf"
    output_dir = Path("salidas_csv")
    legacy_csv = output_dir / "ddu456_validation.csv"

    print("\n" + "=" * 60)
    print("VALIDACION DDU 456 - EXTRACCION")
    print("=" * 60)

    try:
        # Instanciar orquestador (interfaz real: sin argumentos)
        orchestrator = DDUOrchestrator()
        print("\n[OK] Orquestador instanciado")

        # Extraer datos del PDF (una circular = un registro/dict DatosCircularDDU)
        registro = orchestrator.process_pdf(Path(pdf_path))
        data = [registro]
        print(f"[OK] PDF cargado: {pdf_path}")
        print(f"[OK] Extraccion completada: {len(data)} registro(s), "
              f"{len(registro)} campos")

        # Guardar CSV con la misma estructura que el resto de circulares:
        # bloque | campo | valor_extraido
        csv_output = orchestrator.export_individual_csv(Path(pdf_path), output_dir)
        if legacy_csv.exists():
            legacy_csv.unlink()
        print(f"[OK] CSV generado: {csv_output}")

        # Analisis de campos vacios
        print("\n" + "-" * 60)
        print("ANALISIS DE CAMPOS VACIOS")
        print("-" * 60)

        empty_count = {}
        for record in data:
            for k, v in record.items():
                if not v or v == "":
                    empty_count[k] = empty_count.get(k, 0) + 1

        if empty_count:
            print("\nCampos con valores vacios:")
            for field, count in sorted(empty_count.items(), key=lambda x: -x[1]):
                pct = (count / len(data)) * 100
                print(f"  - {field}: {count}/{len(data)} ({pct:.1f}%)")
        else:
            print("[OK] Todos los campos tienen valores")

        print("\n" + "=" * 60)
        print("VALIDACION COMPLETADA")
        print("=" * 60)

        return data

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    validate_ddu456()
