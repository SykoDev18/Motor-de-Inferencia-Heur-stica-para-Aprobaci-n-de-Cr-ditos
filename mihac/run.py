# ============================================================
# MIHAC v1.0 — Punto de Entrada Principal
# Motor de Inferencia Heurística para Aprobación de Créditos
# ============================================================
# Ejecutar con: python run.py
# ============================================================

import sys
import logging
from pathlib import Path

# Asegurar que el directorio raíz del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import setup_logging, FLASK_HOST, FLASK_PORT, FLASK_DEBUG
from database.db import init_db

logger = logging.getLogger(__name__)


def main() -> None:
    """Punto de entrada principal del sistema MIHAC.

    Inicializa el logging, la base de datos y arranca el servidor Flask.

    Returns:
        None

    Ejemplo::

        python run.py
    """
    # 1. Configurar logging
    setup_logging()
    logger.info("=" * 60)
    logger.info("MIHAC v1.0 — Iniciando sistema...")
    logger.info("=" * 60)

    # 2. Inicializar base de datos
    try:
        init_db()
        logger.info("Base de datos lista.")
    except Exception as e:
        logger.critical("No se pudo inicializar la BD: %s", e)
        sys.exit(1)

    # 3. Arrancar Flask (se implementará en la fase Web)
    logger.info(
        "Servidor listo en http://%s:%s (debug=%s)",
        FLASK_HOST, FLASK_PORT, FLASK_DEBUG
    )
    logger.info("Nota: El servidor Flask se habilitará en la fase Web.")


if __name__ == "__main__":
    main()
