# ============================================================
# MIHAC v1.0 — conftest.py (Fixtures compartidas para pytest)
# ============================================================

import sys
import os
import json
import pytest
from pathlib import Path

# Asegurar que el proyecto está en sys.path
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.validator import Validator
from core.scorer import ScoringEngine
from core.explainer import Explainer
from core.engine import InferenceEngine
from app import create_app, db as _db
from app.models import Evaluacion

# Importar fixtures compartidas
from tests.fixtures import (
    CASO_IDEAL,
    CASO_RIESGO,
    CASO_GRIS,
    CASO_JOVEN_VACACIONES,
    CASO_SIN_HISTORIAL_SOLVENTE,
    CASO_DEUDA_CERO,
    CASO_MONTO_ALTO,
    CASO_FRONTERA_REVISION,
    DATOS_INVALIDOS_TIPOS,
    DATOS_CAMPOS_FALTANTES,
    DATOS_RANGOS_EXTREMOS,
    DATOS_SANITIZAR,
)


# ── Core fixtures ───────────────────────────────────────────

@pytest.fixture
def validator():
    """Instancia fresca de Validator."""
    return Validator()


@pytest.fixture
def scorer():
    """Instancia fresca de ScoringEngine con rules.json reales."""
    return ScoringEngine()


@pytest.fixture
def explainer():
    """Instancia fresca de Explainer."""
    return Explainer()


@pytest.fixture
def engine():
    """Instancia fresca de InferenceEngine."""
    return InferenceEngine()


# ── Datos de prueba ─────────────────────────────────────────

@pytest.fixture
def caso_ideal():
    return CASO_IDEAL.copy()


@pytest.fixture
def caso_riesgo():
    return CASO_RIESGO.copy()


@pytest.fixture
def caso_gris():
    return CASO_GRIS.copy()


@pytest.fixture
def caso_joven():
    return CASO_JOVEN_VACACIONES.copy()


@pytest.fixture
def caso_solvente_sin_historial():
    return CASO_SIN_HISTORIAL_SOLVENTE.copy()


@pytest.fixture
def caso_deuda_cero():
    return CASO_DEUDA_CERO.copy()


@pytest.fixture
def caso_monto_alto():
    return CASO_MONTO_ALTO.copy()


@pytest.fixture
def caso_frontera():
    return CASO_FRONTERA_REVISION.copy()


# ── Flask fixtures ──────────────────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Crea la aplicación Flask en modo testing."""
    app = create_app("testing")
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    app.config["TESTING"] = True

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture
def client(app):
    """Cliente de prueba Flask."""
    return app.test_client()


@pytest.fixture
def db_session(app):
    """Sesión de BD limpia para cada test."""
    with app.app_context():
        _db.create_all()
        yield _db.session
        _db.session.rollback()
        # Limpiar todas las evaluaciones
        Evaluacion.query.delete()
        _db.session.commit()


@pytest.fixture
def evaluacion_guardada(db_session):
    """Crea y persiste una evaluación APROBADO en la BD."""
    datos = CASO_IDEAL.copy()
    eng = InferenceEngine()
    resultado = eng.evaluate(datos)

    ev = Evaluacion.from_inference_result(datos, resultado)
    db_session.add(ev)
    db_session.commit()
    return ev
