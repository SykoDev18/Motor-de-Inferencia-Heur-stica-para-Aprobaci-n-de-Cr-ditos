# ============================================================
# MIHAC v1.0 — Tests del Motor de Inferencia (core/engine.py)
# tests/test_engine.py
# ============================================================
# ~20 tests cubriendo evaluate(), evaluate_batch(), stats y
# manejo de errores.
# ============================================================

import pytest
from core.engine import InferenceEngine
from tests.fixtures import (
    CASO_IDEAL,
    CASO_RIESGO,
    CASO_GRIS,
    CASO_MONTO_ALTO,
    CASO_DEUDA_CERO,
    DATOS_INVALIDOS_TIPOS,
    DATOS_CAMPOS_FALTANTES,
    DATOS_RANGOS_EXTREMOS,
)


# ════════════════════════════════════════════════════════════
# evaluate() — Flujo completo
# ════════════════════════════════════════════════════════════

class TestEvaluate:
    """Tests para el método evaluate()."""

    def test_caso_ideal_aprobado(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        assert r["dictamen"] == "APROBADO"
        assert r["score_final"] == 100
        assert r["errores_validacion"] == []

    def test_caso_riesgo_rechazado(self, engine):
        r = engine.evaluate(CASO_RIESGO)
        assert r["dictamen"] == "RECHAZADO"
        assert r["score_final"] == 0

    def test_caso_gris_revision(self, engine):
        r = engine.evaluate(CASO_GRIS)
        assert r["dictamen"] == "REVISION_MANUAL"
        assert 60 <= r["score_final"] <= 80

    def test_resultado_tiene_campos_completos(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        campos = [
            "score_final", "dti_ratio", "dti_clasificacion",
            "sub_scores", "dictamen", "umbral_aplicado",
            "reglas_activadas", "compensaciones",
            "reporte_explicacion", "errores_validacion",
        ]
        for c in campos:
            assert c in r, f"Falta campo '{c}' en resultado"

    def test_sub_scores_tiene_4_modulos(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        sub = r["sub_scores"]
        assert set(sub.keys()) == {
            "solvencia", "estabilidad",
            "historial_score", "perfil",
        }

    def test_dti_clasificacion_valida(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        assert r["dti_clasificacion"] in (
            "BAJO", "MODERADO", "ALTO", "CRITICO"
        )

    def test_reporte_explicacion_no_vacio(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        assert len(r["reporte_explicacion"]) > 50

    def test_reglas_activadas_son_lista(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        assert isinstance(r["reglas_activadas"], list)

    def test_compensaciones_subconjunto_de_reglas(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        comps = r["compensaciones"]
        for c in comps:
            assert c["tipo"] == "compensacion"

    def test_monto_alto_umbral_85(self, engine):
        r = engine.evaluate(CASO_MONTO_ALTO)
        assert r["umbral_aplicado"] == 85

    def test_monto_normal_umbral_80(self, engine):
        r = engine.evaluate(CASO_IDEAL)
        assert r["umbral_aplicado"] == 80

    def test_deuda_cero_dti_bajo(self, engine):
        r = engine.evaluate(CASO_DEUDA_CERO)
        assert r["dti_ratio"] == 0.0
        assert r["dti_clasificacion"] == "BAJO"


# ════════════════════════════════════════════════════════════
# Manejo de errores
# ════════════════════════════════════════════════════════════

class TestErrores:
    """Tests para manejo de datos inválidos."""

    def test_datos_faltantes_retorna_errores(self, engine):
        r = engine.evaluate(DATOS_CAMPOS_FALTANTES)
        assert len(r["errores_validacion"]) > 0
        assert r["dictamen"] == "RECHAZADO"
        assert r["score_final"] == 0

    def test_datos_tipos_invalidos_retorna_errores(self, engine):
        r = engine.evaluate(DATOS_INVALIDOS_TIPOS)
        assert len(r["errores_validacion"]) > 0

    def test_diccionario_vacio(self, engine):
        r = engine.evaluate({})
        assert len(r["errores_validacion"]) > 0
        assert r["dictamen"] == "RECHAZADO"

    def test_datos_rangos_extremos(self, engine):
        r = engine.evaluate(DATOS_RANGOS_EXTREMOS)
        assert len(r["errores_validacion"]) > 0


# ════════════════════════════════════════════════════════════
# evaluate_batch() y stats
# ════════════════════════════════════════════════════════════

class TestBatchYStats:
    """Tests para evaluate_batch() y estadísticas."""

    def test_batch_tres_casos(self, engine):
        resultados = engine.evaluate_batch(
            [CASO_IDEAL, CASO_RIESGO, CASO_GRIS]
        )
        assert len(resultados) == 3
        assert all("indice" in r for r in resultados)
        assert resultados[0]["indice"] == 0
        assert resultados[1]["indice"] == 1
        assert resultados[2]["indice"] == 2

    def test_batch_dictamen_correcto(self, engine):
        resultados = engine.evaluate_batch(
            [CASO_IDEAL, CASO_RIESGO]
        )
        assert resultados[0]["dictamen"] == "APROBADO"
        assert resultados[1]["dictamen"] == "RECHAZADO"

    def test_batch_lista_vacia(self, engine):
        resultados = engine.evaluate_batch([])
        assert resultados == []

    def test_stats_acumuladas(self):
        eng = InferenceEngine()
        assert eng.stats["total_evaluaciones"] == 0

        eng.evaluate(CASO_IDEAL)
        eng.evaluate(CASO_RIESGO)
        eng.evaluate(CASO_GRIS)

        stats = eng.stats
        assert stats["total_evaluaciones"] == 3
        assert stats["aprobados"] == 1
        assert stats["rechazados"] == 1
        assert stats["revision_manual"] == 1
        assert stats["tasa_aprobacion"] == pytest.approx(33.33, abs=0.1)
        assert stats["score_promedio"] > 0
        assert stats["dti_promedio"] > 0
