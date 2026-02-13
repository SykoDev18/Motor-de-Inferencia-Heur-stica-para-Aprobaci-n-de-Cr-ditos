# ============================================================
# MIHAC v1.0 — Configuración Central del Sistema
# Motor de Inferencia Heurística para Aprobación de Créditos
# ============================================================
# Todas las constantes del sistema se definen aquí.
# Ningún módulo debe hardcodear valores; siempre importar desde config.
# ============================================================

import os
import logging
from pathlib import Path

# ────────────────────────────────────────────────────────────
# 1. RUTAS BASE DEL PROYECTO
# ────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = BASE_DIR / "database"
REPORTS_DIR = BASE_DIR / "reports"
TEMPLATES_DIR = BASE_DIR / "web" / "templates"
STATIC_DIR = BASE_DIR / "web" / "static"

# ────────────────────────────────────────────────────────────
# 2. ARCHIVOS DE LA BASE DE CONOCIMIENTO
# ────────────────────────────────────────────────────────────
RULES_FILE = KNOWLEDGE_DIR / "rules.json"
WEIGHTS_FILE = KNOWLEDGE_DIR / "weights.json"
THRESHOLDS_FILE = KNOWLEDGE_DIR / "thresholds.json"

# ────────────────────────────────────────────────────────────
# 3. BASE DE DATOS
# ────────────────────────────────────────────────────────────
DB_FILENAME = "mihac.db"
DB_PATH = DATABASE_DIR / DB_FILENAME
SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False  # True para debug SQL

# ────────────────────────────────────────────────────────────
# 4. UMBRALES DE DECISIÓN (valores por defecto; thresholds.json
#    puede sobreescribirlos en tiempo de ejecución)
# ────────────────────────────────────────────────────────────
UMBRAL_APROBADO = 80          # Score >= 80 → APROBADO
UMBRAL_REVISION = 60          # Score >= 60 y < 80 → REVISIÓN MANUAL
# Score < 60 → RECHAZADO (implícito)

SCORE_MINIMO = 0
SCORE_MAXIMO = 100
SCORE_BASE_INICIAL = 50       # Punto de partida neutral del scoring

# ────────────────────────────────────────────────────────────
# 5. LÍMITES DE VARIABLES DE ENTRADA
# ────────────────────────────────────────────────────────────
EDAD_MIN = 18
EDAD_MAX = 99

INGRESO_MIN = 0.01            # Ingreso debe ser > 0

DEUDA_MIN = 0.0

ANTIGUEDAD_LABORAL_MIN = 0
ANTIGUEDAD_LABORAL_MAX = 40

DEPENDIENTES_MIN = 0
DEPENDIENTES_MAX = 10

MONTO_CREDITO_MIN = 500.0
MONTO_CREDITO_MAX = 50_000.0

# ────────────────────────────────────────────────────────────
# 6. VALORES VÁLIDOS PARA VARIABLES CATEGÓRICAS
# ────────────────────────────────────────────────────────────
HISTORIAL_VALORES = {
    0: "Malo",
    1: "Neutro",
    2: "Bueno",
}

TIPOS_VIVIENDA = ["Propia", "Familiar", "Rentada"]

PROPOSITOS_CREDITO = [
    "Negocio",
    "Educacion",
    "Consumo",
    "Emergencia",
    "Vacaciones",
]

# ────────────────────────────────────────────────────────────
# 7. DTI (Debt-To-Income)
# ────────────────────────────────────────────────────────────
DTI_CRITICO = 0.40            # Por encima de esto → penalización fuerte
DTI_BAJO = 0.25               # Por debajo → elegible a compensación

# ────────────────────────────────────────────────────────────
# 8. FLASK
# ────────────────────────────────────────────────────────────
FLASK_SECRET_KEY = os.environ.get("MIHAC_SECRET_KEY", "mihac-dev-secret-key-cambiar-en-prod")
FLASK_DEBUG = os.environ.get("MIHAC_DEBUG", "True").lower() in ("true", "1", "yes")
FLASK_HOST = os.environ.get("MIHAC_HOST", "127.0.0.1")
FLASK_PORT = int(os.environ.get("MIHAC_PORT", 5000))

# ────────────────────────────────────────────────────────────
# 9. REPORTES
# ────────────────────────────────────────────────────────────
REPORTS_OUTPUT_DIR = REPORTS_DIR / "output"
CHART_DPI = 150
CHART_FORMAT = "png"

# ────────────────────────────────────────────────────────────
# 10. DATOS
# ────────────────────────────────────────────────────────────
GERMAN_CREDIT_UCI_ID = 144
GERMAN_CREDIT_MAPPED_FILE = DATA_DIR / "german_credit_mapped.csv"
DEMO_DATA_FILE = DATA_DIR / "demo_data.csv"

# ────────────────────────────────────────────────────────────
# 11. LOGGING
# ────────────────────────────────────────────────────────────
LOG_LEVEL = os.environ.get("MIHAC_LOG_LEVEL", "INFO").upper()
LOG_FORMAT = "%(asctime)s | %(name)-20s | %(levelname)-8s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging() -> None:
    """Configura el logging global del sistema MIHAC.

    Establece el nivel, formato y handler de consola para todos
    los módulos del proyecto.

    Returns:
        None

    Ejemplo de uso::

        from config import setup_logging
        setup_logging()
    """
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL, logging.INFO),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
    )
    # Silenciar loggers ruidosos de terceros
    logging.getLogger("werkzeug").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

# ────────────────────────────────────────────────────────────
# 12. METADATOS DEL PROYECTO
# ────────────────────────────────────────────────────────────
PROJECT_NAME = "MIHAC"
PROJECT_VERSION = "1.0.0"
PROJECT_DESCRIPTION = (
    "Motor de Inferencia Heurística para Aprobación de Créditos"
)
PROJECT_AUTHOR = "Proyecto de Titulación"
