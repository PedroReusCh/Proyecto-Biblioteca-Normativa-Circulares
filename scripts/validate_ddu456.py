# scripts/validate_ddu456.py
"""
Validación de extracción DDU 456 usando extractores actuales.
"""
import sys
sys.path.insert(0, '.')

from scripts.ddu_orchestrator import DDUOrchestrator

def validate_ddu456():
    """Ejecuta extractores sobre DDU 456 y reporta hallazgos."""
    pdf_path = "circulares/DDU 456.pdf"

    try:
        orchestrator = DDUOrchestrator(pdf_path)
        data = orchestrator.extract()

        print("\n[VALIDACIÓN DDU 456]")
        print(f"PDF: {pdf_path}")
        print(f"Registros extraídos: {len(data)}")

        # Analizar qué campos quedaron vacíos
        for idx, record in enumerate(data):
            empty_fields = [k for k, v in record.items() if not v or v == ""]
            if empty_fields:
                print(f"  Registro {idx}: campos vacíos: {empty_fields}")

        return data

    except Exception as e:
        print(f"ERROR en validación: {e}")
        raise

if __name__ == "__main__":
    validate_ddu456()
