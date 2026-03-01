# ============================================================
# MIHAC v1.0 — Tests del Explicador (core/explainer.py)
# tests/test_explainer.py
# ============================================================
# ~12 tests cubriendo generate(), generate_short() y
# funciones internas.
# ============================================================

import pytest
from core.explainer import Explainer
from core.engine import InferenceEngine
from tests.fixtures import CASO_IDEAL, CASO_RIESGO, CASO_GRIS


def _evaluar(datos: dict) -> tuple[dict, dict]:
    """Evalúa y retorna (datos, resultado) para el explainer."""
    eng = InferenceEngine()
    resultado = eng.evaluate(datos)
    return datos, resultado


# ════════════════════════════════════════════════════════════
# generate() — Reporte completo
# ════════════════════════════════════════════════════════════

class TestGenerate:
    """Tests para Explainer.generate()."""

    def test_generate_aprobado(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        texto = explainer.generate(datos, resultado)
        assert "APROBADO" in texto
        assert "Score crediticio" in texto
        assert "DESGLOSE DEL SCORE" in texto
        assert len(texto) > 200

    def test_generate_rechazado(self, explainer):
        datos, resultado = _evaluar(CASO_RIESGO)
        texto = explainer.generate(datos, resultado)
        assert "RECHAZADO" in texto
        assert "CONCLUSIÓN" in texto

    def test_generate_revision(self, explainer):
        datos, resultado = _evaluar(CASO_GRIS)
        texto = explainer.generate(datos, resultado)
        assert "REVISION_MANUAL" in texto

    def test_secciones_presentes(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        texto = explainer.generate(datos, resultado)
        secciones = [
            "EVALUACIÓN CREDITICIA MIHAC",
            "ANÁLISIS DE SOLVENCIA",
            "DESGLOSE DEL SCORE",
            "FACTORES DETERMINANTES",
            "CONCLUSIÓN",
        ]
        for s in secciones:
            assert s in texto, f"Falta sección '{s}'"

    def test_barras_progreso_presentes(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        texto = explainer.generate(datos, resultado)
        # Barras ASCII
        assert "█" in texto or "░" in texto

    def test_factores_positivos_aprobado(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        texto = explainer.generate(datos, resultado)
        assert "Positivos:" in texto
        assert "▲" in texto

    def test_factores_negativos_rechazado(self, explainer):
        datos, resultado = _evaluar(CASO_RIESGO)
        texto = explainer.generate(datos, resultado)
        assert "Negativos:" in texto
        assert "▼" in texto

    def test_conclusion_aprobado_recomienda_desembolso(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        texto = explainer.generate(datos, resultado)
        assert "desembolso" in texto.lower() or "aprobación" in texto.lower()

    def test_conclusion_rechazado_sugiere_mejora(self, explainer):
        datos, resultado = _evaluar(CASO_RIESGO)
        texto = explainer.generate(datos, resultado)
        assert "sobreendeudamiento" in texto.lower() or "umbral" in texto.lower()


# ════════════════════════════════════════════════════════════
# generate_short() — Resumen de una línea
# ════════════════════════════════════════════════════════════

class TestGenerateShort:
    """Tests para Explainer.generate_short()."""

    def test_short_aprobado(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        linea = explainer.generate_short(datos, resultado)
        assert "APROBADO" in linea
        assert "Score:" in linea
        assert "DTI:" in linea

    def test_short_rechazado(self, explainer):
        datos, resultado = _evaluar(CASO_RIESGO)
        linea = explainer.generate_short(datos, resultado)
        assert "RECHAZADO" in linea

    def test_short_contiene_historial(self, explainer):
        datos, resultado = _evaluar(CASO_IDEAL)
        linea = explainer.generate_short(datos, resultado)
        assert "Historial:" in linea
        assert "Bueno" in linea
