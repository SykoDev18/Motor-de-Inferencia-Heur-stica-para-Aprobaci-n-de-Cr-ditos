# ============================================================
# MIHAC v1.0 — Tests de la Interfaz Web (app/routes.py)
# tests/test_web.py
# ============================================================
# ~12 tests cubriendo rutas, formulario, historial, dashboard
# y descarga de PDFs.
# ============================================================

import pytest
from app.models import Evaluacion
from core.engine import InferenceEngine
from tests.fixtures import CASO_IDEAL, CASO_RIESGO, CASO_GRIS


# ════════════════════════════════════════════════════════════
# Rutas básicas
# ════════════════════════════════════════════════════════════

class TestRutasBasicas:
    """Tests para GET en rutas principales."""

    def test_index_get(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
        assert "Evaluar" in resp.data.decode("utf-8")

    def test_historial_vacio(self, client):
        resp = client.get("/historial")
        assert resp.status_code == 200

    def test_dashboard_vacio(self, client):
        resp = client.get("/dashboard")
        assert resp.status_code == 200

    def test_resultado_inexistente(self, client):
        resp = client.get("/resultado/99999")
        assert resp.status_code == 404


# ════════════════════════════════════════════════════════════
# Formulario — POST
# ════════════════════════════════════════════════════════════

class TestFormulario:
    """Tests para envío del formulario de evaluación."""

    def test_post_caso_ideal_redirect(self, client, db_session):
        resp = client.post("/", data={
            "edad": 35,
            "ingreso_mensual": 25000.0,
            "total_deuda_actual": 4000.0,
            "historial_crediticio": "2",
            "antiguedad_laboral": 7,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 15000.0,
        }, follow_redirects=False)
        assert resp.status_code == 302
        assert "/resultado/" in resp.headers["Location"]

    def test_post_caso_ideal_resultado(self, client, db_session):
        resp = client.post("/", data={
            "edad": 35,
            "ingreso_mensual": 25000.0,
            "total_deuda_actual": 4000.0,
            "historial_crediticio": "2",
            "antiguedad_laboral": 7,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 15000.0,
        }, follow_redirects=True)
        html = resp.data.decode("utf-8")
        assert resp.status_code == 200
        assert "APROBADO" in html

    def test_post_datos_invalidos_no_redirect(self, client):
        resp = client.post("/", data={
            "edad": "",
            "ingreso_mensual": "",
        }, follow_redirects=False)
        # Formulario inválido → re-render del form (200)
        assert resp.status_code == 200

    def test_resultado_con_evaluacion(self, client, evaluacion_guardada):
        ev_id = evaluacion_guardada.id
        resp = client.get(f"/resultado/{ev_id}")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "PDF Completo" in html or "pdf" in html.lower()


# ════════════════════════════════════════════════════════════
# Historial y Dashboard con datos
# ════════════════════════════════════════════════════════════

class TestConDatos:
    """Tests para historial y dashboard con evaluaciones."""

    def test_historial_con_evaluaciones(self, client, evaluacion_guardada):
        resp = client.get("/historial")
        assert resp.status_code == 200
        html = resp.data.decode("utf-8")
        assert "APROBADO" in html

    def test_historial_filtro_dictamen(self, client, evaluacion_guardada):
        resp = client.get("/historial?dictamen=APROBADO")
        assert resp.status_code == 200

    def test_historial_orden(self, client, evaluacion_guardada):
        resp = client.get("/historial?orden=score_alto")
        assert resp.status_code == 200

    def test_dashboard_con_evaluaciones(self, client, evaluacion_guardada):
        resp = client.get("/dashboard")
        html = resp.data.decode("utf-8")
        assert resp.status_code == 200
        # Debería tener KPIs visibles
        assert "1" in html  # al menos 1 evaluación total


# ════════════════════════════════════════════════════════════
# Descarga de PDFs
# ════════════════════════════════════════════════════════════

class TestPDF:
    """Tests para descarga de reportes PDF."""

    def test_pdf_completo_descarga(self, client, evaluacion_guardada):
        ev_id = evaluacion_guardada.id
        resp = client.get(f"/resultado/{ev_id}/pdf")
        assert resp.status_code == 200
        assert resp.content_type == "application/pdf"
        assert len(resp.data) > 1000

    def test_pdf_cliente_descarga(self, client, evaluacion_guardada):
        ev_id = evaluacion_guardada.id
        resp = client.get(f"/resultado/{ev_id}/pdf-cliente")
        assert resp.status_code == 200
        assert resp.content_type == "application/pdf"
        assert len(resp.data) > 500

    def test_pdf_evaluacion_inexistente(self, client):
        resp = client.get("/resultado/99999/pdf")
        assert resp.status_code == 404

    def test_pdf_header_valido(self, client, evaluacion_guardada):
        ev_id = evaluacion_guardada.id
        resp = client.get(f"/resultado/{ev_id}/pdf")
        # PDF must start with %PDF-
        assert resp.data[:5] == b"%PDF-"
