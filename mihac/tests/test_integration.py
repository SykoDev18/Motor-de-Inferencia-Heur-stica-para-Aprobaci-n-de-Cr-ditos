# ============================================================
# MIHAC v1.0 — Tests de Integración End-to-End
# tests/test_integration.py
# ============================================================
# ~15 tests que verifican el flujo completo:
# datos → validación → scoring → dictamen → BD → PDF
# ============================================================

import json
import os
import pytest
from pathlib import Path

from core.engine import InferenceEngine
from core.validator import Validator
from core.scorer import ScoringEngine
from app.models import Evaluacion
from tests.fixtures import (
    CASO_IDEAL,
    CASO_RIESGO,
    CASO_GRIS,
    CASO_JOVEN_VACACIONES,
    CASO_SIN_HISTORIAL_SOLVENTE,
    CASO_DEUDA_CERO,
    CASO_MONTO_ALTO,
    CASO_FRONTERA_REVISION,
    DATOS_SANITIZAR,
)


# ════════════════════════════════════════════════════════════
# Flujo completo: datos → motor → resultado coherente
# ════════════════════════════════════════════════════════════

class TestFlujoCompleto:
    """Verifica coherencia entre validación, scoring y dictamen."""

    def test_ideal_score_100_aprobado(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_IDEAL)
        assert r["score_final"] == 100
        assert r["dictamen"] == "APROBADO"
        assert r["dti_clasificacion"] == "BAJO"

    def test_riesgo_score_0_rechazado(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_RIESGO)
        assert r["score_final"] == 0
        assert r["dictamen"] == "RECHAZADO"
        assert r["dti_clasificacion"] == "CRITICO"

    def test_gris_score_revision(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_GRIS)
        assert r["dictamen"] == "REVISION_MANUAL"
        assert 60 <= r["score_final"] <= 80

    def test_sanitizar_y_evaluar(self):
        v = Validator()
        limpio = v.sanitize(DATOS_SANITIZAR)
        ok, errores = v.validate(limpio)
        assert ok is True, f"Errores: {errores}"

        eng = InferenceEngine()
        r = eng.evaluate(limpio)
        assert r["dictamen"] == "APROBADO"

    def test_compensacion_r011_mejora_score(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_SIN_HISTORIAL_SOLVENTE)
        # R011 (+15) debería activarse
        ids = [reg["id"] for reg in r["reglas_activadas"]]
        assert "R011" in ids
        assert r["dictamen"] in ("APROBADO", "REVISION_MANUAL")

    def test_deuda_cero_r013_activada(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_DEUDA_CERO)
        ids = [reg["id"] for reg in r["reglas_activadas"]]
        assert "R013" in ids

    def test_monto_alto_umbral_85(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_MONTO_ALTO)
        assert r["umbral_aplicado"] == 85

    def test_joven_vacaciones_doble_penalizacion(self):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_JOVEN_VACACIONES)
        ids = [reg["id"] for reg in r["reglas_activadas"]]
        assert "R008" in ids  # vacaciones
        assert "R009" in ids  # joven < 21


# ════════════════════════════════════════════════════════════
# Persistencia: motor → modelo → BD
# ════════════════════════════════════════════════════════════

class TestPersistencia:
    """Verifica que las evaluaciones se guardan y recuperan."""

    def test_guardar_evaluacion(self, db_session):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_IDEAL)
        ev = Evaluacion.from_inference_result(CASO_IDEAL, r)
        db_session.add(ev)
        db_session.commit()

        assert ev.id is not None
        assert ev.dictamen == "APROBADO"
        assert ev.score_final == 100

    def test_to_dict_completo(self, db_session):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_RIESGO)
        ev = Evaluacion.from_inference_result(CASO_RIESGO, r)
        db_session.add(ev)
        db_session.commit()

        d = ev.to_dict()
        assert d["dictamen"] == "RECHAZADO"
        assert d["score_final"] == 0
        assert isinstance(d["reglas_activadas"], list)
        assert isinstance(d["sub_scores"], dict)

    def test_get_reglas_list(self, db_session):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_IDEAL)
        ev = Evaluacion.from_inference_result(CASO_IDEAL, r)
        db_session.add(ev)
        db_session.commit()

        reglas = ev.get_reglas_list()
        assert isinstance(reglas, list)
        assert len(reglas) > 0
        assert "id" in reglas[0]

    def test_get_sub_scores_dict(self, db_session):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_IDEAL)
        ev = Evaluacion.from_inference_result(CASO_IDEAL, r)
        db_session.add(ev)
        db_session.commit()

        sub = ev.get_sub_scores_dict()
        assert "solvencia" in sub
        assert "estabilidad" in sub

    def test_from_inference_result_campos(self, db_session):
        eng = InferenceEngine()
        r = eng.evaluate(CASO_GRIS)
        ev = Evaluacion.from_inference_result(CASO_GRIS, r)
        db_session.add(ev)
        db_session.commit()

        assert ev.edad == 28
        assert ev.ingreso_mensual == 15000.0
        assert ev.tipo_vivienda == "Familiar"
        assert ev.proposito_credito == "Consumo"
        assert ev.dti_ratio > 0

    def test_multiples_evaluaciones(self, db_session):
        eng = InferenceEngine()
        for caso in [CASO_IDEAL, CASO_RIESGO, CASO_GRIS]:
            r = eng.evaluate(caso)
            ev = Evaluacion.from_inference_result(caso, r)
            db_session.add(ev)
        db_session.commit()

        total = Evaluacion.query.count()
        assert total >= 3

    def test_reglas_json_invalido_retorna_lista_vacia(self, db_session):
        ev = Evaluacion(
            edad=30, ingreso_mensual=20000, total_deuda_actual=5000,
            historial_crediticio=1, antiguedad_laboral=3,
            numero_dependientes=1, tipo_vivienda="Propia",
            proposito_credito="Consumo", monto_credito=10000,
            score_final=70, dti_ratio=0.25, dti_clasificacion="MODERADO",
            dictamen="REVISION_MANUAL", umbral_aplicado=80,
            reglas_activadas="INVALIDO", sub_scores="INVALIDO",
            reporte_explicacion="test",
        )
        assert ev.get_reglas_list() == []
        assert ev.get_sub_scores_dict() == {}
