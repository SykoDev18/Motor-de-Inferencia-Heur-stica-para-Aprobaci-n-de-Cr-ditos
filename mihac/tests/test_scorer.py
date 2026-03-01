# ============================================================
# MIHAC v1.0 — Tests del Motor de Scoring (core/scorer.py)
# tests/test_scorer.py
# ============================================================
# ~35 tests cubriendo DTI, sub-scores, reglas, score final
# y dictamen.
# ============================================================

import json
import pytest
from pathlib import Path
from core.scorer import ScoringEngine
from tests.fixtures import (
    CASO_IDEAL,
    CASO_RIESGO,
    CASO_GRIS,
    CASO_JOVEN_VACACIONES,
    CASO_SIN_HISTORIAL_SOLVENTE,
    CASO_DEUDA_CERO,
    CASO_MONTO_ALTO,
)


# ════════════════════════════════════════════════════════════
# DTI (Debt-To-Income)
# ════════════════════════════════════════════════════════════

class TestDTI:
    """Tests para calculate_dti()."""

    def test_dti_bajo(self, scorer):
        dti, clasif = scorer.calculate_dti(25000, 4000)
        assert dti == pytest.approx(0.16, abs=0.01)
        assert clasif == "BAJO"

    def test_dti_moderado(self, scorer):
        dti, clasif = scorer.calculate_dti(20000, 6000)
        assert dti == pytest.approx(0.30, abs=0.01)
        assert clasif == "MODERADO"

    def test_dti_alto(self, scorer):
        dti, clasif = scorer.calculate_dti(10000, 5000)
        assert dti == pytest.approx(0.50, abs=0.01)
        assert clasif == "ALTO"

    def test_dti_critico(self, scorer):
        dti, clasif = scorer.calculate_dti(8000, 5500)
        assert dti == pytest.approx(0.6875, abs=0.01)
        assert clasif == "CRITICO"

    def test_dti_ingreso_cero(self, scorer):
        dti, clasif = scorer.calculate_dti(0, 5000)
        assert dti == 1.0
        assert clasif == "CRITICO"

    def test_dti_ingreso_negativo(self, scorer):
        dti, clasif = scorer.calculate_dti(-1000, 5000)
        assert clasif == "CRITICO"

    def test_dti_sin_deuda(self, scorer):
        dti, clasif = scorer.calculate_dti(25000, 0)
        assert dti == 0.0
        assert clasif == "BAJO"

    def test_dti_frontera_bajo_moderado(self, scorer):
        # 0.25 exacto → MODERADO (no es < 0.25)
        dti, clasif = scorer.calculate_dti(10000, 2500)
        assert dti == 0.25
        assert clasif == "MODERADO"

    def test_dti_frontera_moderado_alto(self, scorer):
        dti, clasif = scorer.calculate_dti(10000, 4000)
        assert dti == 0.40
        assert clasif == "ALTO"

    def test_dti_frontera_alto_critico(self, scorer):
        dti, clasif = scorer.calculate_dti(10000, 6000)
        assert dti == 0.60
        assert clasif == "CRITICO"


# ════════════════════════════════════════════════════════════
# SUB-SCORES
# ════════════════════════════════════════════════════════════

class TestSubScores:
    """Tests para calculate_subscores()."""

    def test_subscores_caso_ideal(self, scorer):
        dti = 4000 / 25000
        sub = scorer.calculate_subscores(CASO_IDEAL, dti)
        assert "solvencia" in sub
        assert "estabilidad" in sub
        assert "historial_score" in sub
        assert "perfil" in sub
        assert sub["solvencia"] <= 40
        assert sub["estabilidad"] <= 30
        assert sub["historial_score"] <= 20
        assert sub["perfil"] <= 10

    def test_solvencia_max_con_ingreso_alto(self, scorer):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = 50000
        datos["numero_dependientes"] = 0
        sub = scorer.calculate_subscores(datos, 0.05)
        assert sub["solvencia"] >= 25  # base alta + ajuste bajo

    def test_solvencia_baja_dti_critico(self, scorer):
        sub = scorer.calculate_subscores(CASO_RIESGO, 0.6875)
        assert sub["solvencia"] <= 10

    def test_estabilidad_alta_propia_veterano(self, scorer):
        datos = {"antiguedad_laboral": 10, "tipo_vivienda": "Propia"}
        sub = scorer.calculate_subscores(datos, 0.1)
        assert sub["estabilidad"] == 30  # 28 + 8 → capped at 30

    def test_estabilidad_baja_novato_rentada(self, scorer):
        datos = {"antiguedad_laboral": 0, "tipo_vivienda": "Rentada"}
        sub = scorer.calculate_subscores(datos, 0.3)
        assert sub["estabilidad"] == 0

    def test_estabilidad_familiar(self, scorer):
        datos = {"antiguedad_laboral": 3, "tipo_vivienda": "Familiar"}
        sub = scorer.calculate_subscores(datos, 0.2)
        assert sub["estabilidad"] == 21  # 18 + 3

    def test_historial_bueno(self, scorer):
        sub = scorer.calculate_subscores({"historial_crediticio": 2}, 0.1)
        assert sub["historial_score"] == 20

    def test_historial_neutro(self, scorer):
        sub = scorer.calculate_subscores({"historial_crediticio": 1}, 0.1)
        assert sub["historial_score"] == 10

    def test_historial_malo(self, scorer):
        sub = scorer.calculate_subscores({"historial_crediticio": 0}, 0.1)
        assert sub["historial_score"] == 0

    def test_perfil_negocio_edad_optima(self, scorer):
        datos = {"proposito_credito": "Negocio", "edad": 35}
        sub = scorer.calculate_subscores(datos, 0.1)
        assert sub["perfil"] == 10  # 10 + 2 → capped at 10

    def test_perfil_vacaciones_joven(self, scorer):
        datos = {"proposito_credito": "Vacaciones", "edad": 20}
        sub = scorer.calculate_subscores(datos, 0.3)
        assert sub["perfil"] == 0

    def test_perfil_educacion(self, scorer):
        datos = {"proposito_credito": "Educacion", "edad": 30}
        sub = scorer.calculate_subscores(datos, 0.2)
        assert sub["perfil"] == 10  # 8 + 2 = 10

    def test_subscores_todos_no_negativos(self, scorer):
        sub = scorer.calculate_subscores(CASO_RIESGO, 0.9)
        for key, val in sub.items():
            assert val >= 0, f"Sub-score {key} no puede ser negativo"


# ════════════════════════════════════════════════════════════
# REGLAS HEURÍSTICAS
# ════════════════════════════════════════════════════════════

class TestReglas:
    """Tests para apply_rules()."""

    def test_15_reglas_cargadas(self, scorer):
        assert len(scorer._reglas) == 15

    def test_reglas_caso_ideal_tiene_positivas(self, scorer):
        dti = 4000 / 25000
        reglas = scorer.apply_rules(CASO_IDEAL, dti)
        ids = [r["id"] for r in reglas]
        assert "R001" in ids  # historial bueno
        assert "R003" in ids  # estabilidad 5+
        assert "R005" in ids  # vivienda propia
        assert "R006" in ids  # negocio

    def test_reglas_caso_riesgo_tiene_negativas(self, scorer):
        dti = 5500 / 8000
        reglas = scorer.apply_rules(CASO_RIESGO, dti)
        ids = [r["id"] for r in reglas]
        assert "R002" in ids   # historial malo
        assert "R004" in ids   # sin trayectoria
        assert "R008" in ids   # vacaciones
        assert "R009" in ids   # menor de 21
        assert "R014" in ids   # DTI > 40%

    def test_regla_r009_joven_menor_21(self, scorer):
        reglas = scorer.apply_rules(CASO_JOVEN_VACACIONES, 0.2)
        ids = [r["id"] for r in reglas]
        assert "R009" in ids

    def test_regla_r010_carga_familiar(self, scorer):
        datos = CASO_IDEAL.copy()
        datos["numero_dependientes"] = 5
        reglas = scorer.apply_rules(datos, 0.16)
        ids = [r["id"] for r in reglas]
        assert "R010" in ids

    def test_compensacion_r011(self, scorer):
        # historial=1, dti<0.25, antiguedad>=3
        datos = CASO_SIN_HISTORIAL_SOLVENTE.copy()
        dti = 2000 / 30000  # ≈ 0.067
        reglas = scorer.apply_rules(datos, dti)
        ids = [r["id"] for r in reglas]
        assert "R011" in ids

    def test_compensacion_r013_deuda_cero(self, scorer):
        datos = CASO_DEUDA_CERO.copy()
        reglas = scorer.apply_rules(datos, 0.0)
        ids = [r["id"] for r in reglas]
        assert "R013" in ids

    def test_compensacion_r015_maxima_estabilidad(self, scorer):
        datos = {
            "numero_dependientes": 0,
            "tipo_vivienda": "Propia",
            "antiguedad_laboral": 5,
            "historial_crediticio": 2,
            "ingreso_mensual": 30000,
            "monto_credito": 10000,
        }
        reglas = scorer.apply_rules(datos, 0.1)
        ids = [r["id"] for r in reglas]
        assert "R015" in ids

    def test_regla_impacto_tiene_campos(self, scorer):
        reglas = scorer.apply_rules(CASO_IDEAL, 0.16)
        for r in reglas:
            assert "id" in r
            assert "impacto" in r
            assert "descripcion" in r
            assert "tipo" in r

    def test_regla_r014_flag_dti_alto(self, scorer):
        datos = CASO_IDEAL.copy()
        reglas = scorer.apply_rules(datos, 0.50)
        r14 = [r for r in reglas if r["id"] == "R014"]
        assert len(r14) == 1
        assert r14[0].get("flag") == "DTI_ALTO_PENALIZADO"


# ════════════════════════════════════════════════════════════
# SCORE FINAL Y DICTAMEN
# ════════════════════════════════════════════════════════════

class TestScoreFinal:
    """Tests para calculate_final_score() y get_dictamen()."""

    def test_score_caso_ideal_es_100(self, scorer):
        dti = 4000 / 25000
        sub = scorer.calculate_subscores(CASO_IDEAL, dti)
        reglas = scorer.apply_rules(CASO_IDEAL, dti)
        score, umbral = scorer.calculate_final_score(
            sub, reglas, 15000
        )
        assert score == 100
        assert umbral == 80

    def test_score_caso_riesgo_es_0(self, scorer):
        dti = 5500 / 8000
        sub = scorer.calculate_subscores(CASO_RIESGO, dti)
        reglas = scorer.apply_rules(CASO_RIESGO, dti)
        score, umbral = scorer.calculate_final_score(
            sub, reglas, 12000
        )
        assert score == 0
        assert umbral == 80

    def test_umbral_85_monto_alto(self, scorer):
        dti = 5000 / 40000
        sub = scorer.calculate_subscores(CASO_MONTO_ALTO, dti)
        reglas = scorer.apply_rules(CASO_MONTO_ALTO, dti)
        _, umbral = scorer.calculate_final_score(
            sub, reglas, 45000
        )
        assert umbral == 85

    def test_umbral_80_monto_normal(self, scorer):
        _, umbral = scorer.calculate_final_score(
            {"solvencia": 30, "estabilidad": 20,
             "historial_score": 15, "perfil": 5},
            [], 20000
        )
        assert umbral == 80

    def test_score_clamp_no_mayor_100(self, scorer):
        sub = {
            "solvencia": 40, "estabilidad": 30,
            "historial_score": 20, "perfil": 10,
        }
        reglas = [{"impacto": 50}]  # +50 sobre 100
        score, _ = scorer.calculate_final_score(sub, reglas, 10000)
        assert score == 100

    def test_score_clamp_no_menor_0(self, scorer):
        sub = {
            "solvencia": 5, "estabilidad": 5,
            "historial_score": 0, "perfil": 0,
        }
        reglas = [{"impacto": -50}]
        score, _ = scorer.calculate_final_score(sub, reglas, 10000)
        assert score == 0

    def test_dictamen_aprobado(self, scorer):
        d = scorer.get_dictamen(90, 80, "BAJO")
        assert d == "APROBADO"

    def test_dictamen_rechazado_por_score(self, scorer):
        d = scorer.get_dictamen(50, 80, "BAJO")
        assert d == "RECHAZADO"

    def test_dictamen_revision_manual(self, scorer):
        d = scorer.get_dictamen(65, 80, "BAJO")
        assert d == "REVISION_MANUAL"

    def test_dictamen_critico_siempre_rechazado(self, scorer):
        d = scorer.get_dictamen(100, 80, "CRITICO")
        assert d == "RECHAZADO"

    def test_dictamen_frontera_aprobado(self, scorer):
        d = scorer.get_dictamen(80, 80, "BAJO")
        assert d == "APROBADO"

    def test_dictamen_frontera_revision(self, scorer):
        d = scorer.get_dictamen(60, 80, "BAJO")
        assert d == "REVISION_MANUAL"

    def test_dictamen_frontera_rechazado(self, scorer):
        d = scorer.get_dictamen(59, 80, "BAJO")
        assert d == "RECHAZADO"


# ════════════════════════════════════════════════════════════
# CARGA DE REGLAS
# ════════════════════════════════════════════════════════════

class TestCargaReglas:
    """Tests para carga/error de reglas."""

    def test_reglas_cargadas_default(self, scorer):
        assert len(scorer._reglas) == 15

    def test_reglas_archivo_inexistente(self):
        s = ScoringEngine(rules_path="/inexistente/rules.json")
        assert s._reglas == []

    def test_comparar_operador_desconocido(self):
        assert ScoringEngine._comparar(5, "~=", 5) is False

    def test_comparar_tipo_incompatible(self):
        assert ScoringEngine._comparar("abc", ">", 5) is False
