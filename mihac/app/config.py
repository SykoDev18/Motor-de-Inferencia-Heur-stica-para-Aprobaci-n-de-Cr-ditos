# ============================================================
# MIHAC v1.0 — Configuración por Entorno (Flask)
# app/config.py
# ============================================================
# Tres perfiles: Development, Testing, Production.
# Las variables sensibles se leen de env vars en producción.
# ============================================================

import os
from pathlib import Path

# Directorio raíz de mihac/
_MIHAC_ROOT = Path(__file__).resolve().parent.parent


class Config:
    """Configuración base compartida por todos los entornos."""

    SECRET_KEY = os.environ.get(
        "MIHAC_SECRET_KEY", "dev-secret-key-mihac-2026"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directorio de la base de datos
    DB_DIR = _MIHAC_ROOT / "instance"

    # Motor MIHAC — ruta al núcleo
    MIHAC_ROOT = _MIHAC_ROOT


class DevelopmentConfig(Config):
    """Configuración para desarrollo local."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + str(Config.DB_DIR / "mihac_dev.db")
    )


class TestingConfig(Config):
    """Configuración para pruebas automatizadas."""

    TESTING = True
    WTF_CSRF_ENABLED = False  # Deshabilitar CSRF en tests
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:///" + str(Config.DB_DIR / "mihac_test.db")
    )


class ProductionConfig(Config):
    """Configuración para producción."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + str(Config.DB_DIR / "mihac_prod.db"),
    )


# Mapa de configuraciones accesible por nombre
config_map = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
