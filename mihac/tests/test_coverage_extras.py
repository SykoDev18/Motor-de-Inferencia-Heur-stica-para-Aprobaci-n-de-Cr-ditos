# ============================================================
# MIHAC v1.0 — Tests adicionales para cobertura
# tests/test_coverage_extras.py
# ============================================================
# Tests dirigidos a cubrir ramas faltantes en utils, routes,
# y reports para alcanzar >85% cobertura total.
# ============================================================

import pytest
from app.utils import (
    formato_moneda,
    formato_porcentaje,
    color_dictamen,
    clase_badge_dictamen,
    texto_historial,
    clasificar_dti,
)
from reports.pdf_report import PDFReportGenerator


# ════════════════════════════════════════════════════════════
# app/utils.py — clasificar_dti y helpers
# ════════════════════════════════════════════════════════════

class TestUtils:
    """Tests para funciones de utilidad."""

    def test_formato_moneda(self):
        assert formato_moneda(25000) == "$25,000.00"

    def test_formato_porcentaje(self):
        assert formato_porcentaje(0.25) == "25.0%"

    def test_color_aprobado(self):
        assert color_dictamen("APROBADO") == "#10B981"

    def test_color_rechazado(self):
        assert color_dictamen("RECHAZADO") == "#EF4444"

    def test_color_revision(self):
        assert color_dictamen("REVISION_MANUAL") == "#F59E0B"

    def test_color_desconocido(self):
        assert color_dictamen("OTRO") == "#64748B"

    def test_badge_aprobado(self):
        assert clase_badge_dictamen("APROBADO") == "bg-success"

    def test_badge_rechazado(self):
        assert clase_badge_dictamen("RECHAZADO") == "bg-danger"

    def test_badge_revision(self):
        assert "bg-warning" in clase_badge_dictamen("REVISION_MANUAL")

    def test_badge_desconocido(self):
        assert clase_badge_dictamen("OTRO") == "bg-secondary"

    def test_texto_historial_bueno(self):
        assert texto_historial(2) == "Bueno"

    def test_texto_historial_neutro(self):
        assert texto_historial(1) == "Neutro"

    def test_texto_historial_malo(self):
        assert texto_historial(0) == "Malo"

    def test_texto_historial_desconocido(self):
        assert texto_historial(9) == "Desconocido"

    def test_clasificar_dti_bajo(self):
        r = clasificar_dti(0.15)
        assert r["texto"] == "BAJO"
        assert r["nivel"] == "bajo"
        assert r["color"] == "#10B981"

    def test_clasificar_dti_moderado(self):
        r = clasificar_dti(0.30)
        assert r["texto"] == "MODERADO"
        assert r["nivel"] == "moderado"

    def test_clasificar_dti_alto(self):
        r = clasificar_dti(0.50)
        assert r["texto"] == "ALTO"
        assert r["nivel"] == "alto"

    def test_clasificar_dti_critico(self):
        r = clasificar_dti(0.70)
        assert r["texto"] == "CRÍTICO"
        assert r["nivel"] == "critico"


# ════════════════════════════════════════════════════════════
# reports/pdf_report.py — Helpers internos
# ════════════════════════════════════════════════════════════

class TestPDFHelpers:
    """Tests para métodos helper del PDFReportGenerator."""

    def test_format_currency(self):
        assert PDFReportGenerator._format_currency(25000.0) == "$25,000.00 MXN"

    def test_format_currency_cero(self):
        assert PDFReportGenerator._format_currency(0) == "$0.00 MXN"

    def test_format_currency_none(self):
        assert PDFReportGenerator._format_currency(None) == "$0.00 MXN"

    def test_progress_bar_svg(self):
        svg = PDFReportGenerator._generate_progress_bar_svg(30, 40)
        assert "<svg" in svg
        assert "30/40" in svg
        # 30/40 = 75% → green
        assert "#10B981" in svg

    def test_progress_bar_svg_low(self):
        svg = PDFReportGenerator._generate_progress_bar_svg(5, 40)
        # 5/40 = 12.5% → red
        assert "#EF4444" in svg

    def test_progress_bar_svg_medium(self):
        svg = PDFReportGenerator._generate_progress_bar_svg(15, 40)
        # 15/40 = 37.5% → amber
        assert "#F59E0B" in svg

    def test_progress_bar_svg_zero_max(self):
        svg = PDFReportGenerator._generate_progress_bar_svg(0, 0)
        assert "<svg" in svg

    def test_dictamen_clase_aprobado(self):
        assert PDFReportGenerator._dictamen_clase("APROBADO") == "aprobado"

    def test_dictamen_clase_rechazado(self):
        assert PDFReportGenerator._dictamen_clase("RECHAZADO") == "rechazado"

    def test_dictamen_clase_revision(self):
        assert PDFReportGenerator._dictamen_clase("REVISION_MANUAL") == "revision"

    def test_condicion_texto_directa(self):
        regla = {
            "tipo": "directa",
            "condicion_campo": "edad",
            "condicion_operador": "<",
            "condicion_valor": 21,
        }
        assert "edad<21" == PDFReportGenerator._condicion_texto(regla)

    def test_condicion_texto_compensacion(self):
        regla = {
            "tipo": "compensacion",
            "condiciones": [
                {"campo": "historial_crediticio", "operador": "==", "valor": 1},
                {"campo": "dti", "operador": "<", "valor": 0.25},
            ],
        }
        txt = PDFReportGenerator._condicion_texto(regla)
        assert "historial_crediticio==1" in txt
        assert "dti<0.25" in txt

    def test_condicion_texto_sin_campo(self):
        regla = {"tipo": "directa"}
        assert PDFReportGenerator._condicion_texto(regla) == ""

    def test_calcular_meses_score_bajo(self):
        ev = {"score_final": 20, "dti_ratio": 0.9}
        assert PDFReportGenerator._calcular_meses(ev) == 12

    def test_calcular_meses_score_medio(self):
        ev = {"score_final": 40, "dti_ratio": 0.5}
        assert PDFReportGenerator._calcular_meses(ev) == 6

    def test_calcular_meses_score_alto(self):
        ev = {"score_final": 70, "dti_ratio": 0.2}
        assert PDFReportGenerator._calcular_meses(ev) == 3

    def test_recomendacion_aprobado(self):
        ev = {"dictamen": "APROBADO", "score_final": 95, "monto_credito": 10000}
        positivos = [{"descripcion": "historial bueno"}]
        negativos = []
        txt = PDFReportGenerator._generar_recomendacion_resumen(ev, positivos, negativos)
        assert "aprobación" in txt.lower()

    def test_recomendacion_rechazado(self):
        ev = {"dictamen": "RECHAZADO", "score_final": 30, "monto_credito": 10000}
        positivos = []
        negativos = [{"descripcion": "historial malo"}]
        txt = PDFReportGenerator._generar_recomendacion_resumen(ev, positivos, negativos)
        assert "no se recomienda" in txt.lower()

    def test_recomendacion_revision(self):
        ev = {"dictamen": "REVISION_MANUAL", "score_final": 65, "monto_credito": 10000}
        txt = PDFReportGenerator._generar_recomendacion_resumen(ev, [], [])
        assert "mixto" in txt.lower() or "analista" in txt.lower()

    def test_generar_conclusion_aprobado(self):
        ev = {"dictamen": "APROBADO", "score_final": 95, "monto_credito": 15000, "dti_ratio": 0.16}
        positivos = [{"descripcion": "Trayectoria estable"}]
        txt = PDFReportGenerator._generar_conclusion(ev, positivos, [])
        assert "aprobación" in txt.lower()

    def test_generar_conclusion_rechazado(self):
        ev = {"dictamen": "RECHAZADO", "score_final": 20, "monto_credito": 10000, "dti_ratio": 0.7}
        negativos = [{"descripcion": "historial malo"}]
        txt = PDFReportGenerator._generar_conclusion(ev, [], negativos)
        assert "no se recomienda" in txt.lower()

    def test_generar_conclusion_revision(self):
        ev = {"dictamen": "REVISION_MANUAL", "score_final": 65, "monto_credito": 10000, "dti_ratio": 0.3}
        txt = PDFReportGenerator._generar_conclusion(ev, [], [])
        assert "mixto" in txt.lower()

    def test_obtener_sugerencias_con_reglas(self):
        negativos = [{"id": "R002"}, {"id": "R004"}]
        sugs = PDFReportGenerator._obtener_sugerencias(negativos)
        assert len(sugs) >= 2
        assert any("historial" in s.lower() for s in sugs)

    def test_obtener_sugerencias_sin_reglas(self):
        sugs = PDFReportGenerator._obtener_sugerencias([])
        assert len(sugs) >= 2  # defaults

    def test_factores_revision(self):
        ev = {"score_final": 65, "dti_ratio": 0.30, "historial_crediticio": 1}
        reglas = [{"tipo": "compensacion", "id": "R011"}]
        factores = PDFReportGenerator._factores_revision(ev, reglas)
        assert len(factores) >= 2
        assert any("Score" in f for f in factores)

    def test_build_modulos(self):
        gen = PDFReportGenerator()
        sub = {"solvencia": 30, "estabilidad": 20, "historial_score": 15, "perfil": 8}
        modulos = gen._build_modulos(sub)
        assert len(modulos) == 4
        assert modulos[0]["nombre"] == "Solvencia"
        assert modulos[0]["valor"] == 30
        assert modulos[0]["max"] == 40


# ════════════════════════════════════════════════════════════
# Flask routes — error handling paths
# ════════════════════════════════════════════════════════════

class TestRoutesEdgeCases:
    """Tests adicionales para rutas con edge cases."""

    def test_historial_paginacion_fuera_rango(self, client, evaluacion_guardada):
        resp = client.get("/historial?page=999")
        assert resp.status_code == 200

    def test_historial_filtro_invalido(self, client, evaluacion_guardada):
        resp = client.get("/historial?dictamen=INVALIDO")
        assert resp.status_code == 200

    def test_dashboard_multiples_evaluaciones(self, client, db_session):
        from app.models import Evaluacion
        from core.engine import InferenceEngine
        from tests.fixtures import CASO_IDEAL, CASO_RIESGO, CASO_GRIS

        eng = InferenceEngine()
        for caso in [CASO_IDEAL, CASO_RIESGO, CASO_GRIS]:
            r = eng.evaluate(caso)
            ev = Evaluacion.from_inference_result(caso, r)
            db_session.add(ev)
        db_session.commit()

        resp = client.get("/dashboard")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "3" in html  # total evaluaciones
