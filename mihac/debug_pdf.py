"""Debug: Quick test of PDF generator standalone."""
import sys, traceback
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from reports.pdf_report import PDFReportGenerator

gen = PDFReportGenerator()
datos = {
    "id": 1,
    "timestamp": "2026-03-01T10:00:00",
    "edad": 35,
    "ingreso_mensual": 25000.0,
    "total_deuda_actual": 3000.0,
    "historial_crediticio": 2,
    "antiguedad_laboral": 8,
    "numero_dependientes": 1,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Negocio",
    "monto_credito": 15000.0,
    "score_final": 100,
    "dti_ratio": 0.12,
    "dti_clasificacion": "BAJO",
    "dictamen": "APROBADO",
    "umbral_aplicado": 80,
    "reglas_activadas": [
        {"id": "R001", "impacto": 20, "impacto_puntos": 20,
         "descripcion": "Premio por historial crediticio bueno",
         "tipo": "directa", "condicion_campo": "historial_crediticio",
         "condicion_operador": "==", "condicion_valor": 2},
        {"id": "R003", "impacto": 15, "impacto_puntos": 15,
         "descripcion": "Estabilidad laboral alta",
         "tipo": "directa", "condicion_campo": "antiguedad_laboral",
         "condicion_operador": ">=", "condicion_valor": 5},
    ],
    "sub_scores": {"solvencia": 35, "estabilidad": 25, "historial_score": 20, "perfil": 8},
    "reporte_explicacion": "APROBADO con score 100/100.",
}
try:
    path = gen.generate_complete_report(datos, "reports/exports/debug_test.pdf")
    print(f"OK: {path}")
except Exception as e:
    traceback.print_exc()
