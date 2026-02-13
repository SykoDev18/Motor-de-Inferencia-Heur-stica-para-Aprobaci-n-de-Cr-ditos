# ============================================================
# MIHAC v1.0 — Conexión a Base de Datos
# Motor de Inferencia Heurística para Aprobación de Créditos
# ============================================================
# Gestiona la conexión a SQLite mediante SQLAlchemy.
# Migrable a PostgreSQL cambiando SQLALCHEMY_DATABASE_URI en config.py.
# ============================================================

import logging
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from database.models import Base

logger = logging.getLogger(__name__)


def _get_db_uri() -> str:
    """Obtiene la URI de la base de datos desde config.py.

    Returns:
        str: URI de conexión SQLAlchemy.

    Ejemplo::

        uri = _get_db_uri()  # 'sqlite:////.../mihac.db'
    """
    # Importación tardía para evitar dependencias circulares
    import config
    return config.SQLALCHEMY_DATABASE_URI


def get_engine(db_uri: str | None = None):
    """Crea y retorna el engine de SQLAlchemy.

    Args:
        db_uri: URI de conexión. Si es None, se lee de config.py.

    Returns:
        sqlalchemy.engine.Engine: Motor de base de datos configurado.

    Ejemplo::

        engine = get_engine()
        engine = get_engine('sqlite:///test.db')
    """
    uri = db_uri or _get_db_uri()
    try:
        engine = create_engine(uri, echo=False)

        # Activar WAL mode y foreign keys para SQLite
        if uri.startswith("sqlite"):
            @event.listens_for(engine, "connect")
            def _set_sqlite_pragma(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.close()

        logger.info("Engine de base de datos creado: %s", uri)
        return engine
    except Exception as e:
        logger.error("Error al crear engine de BD: %s", e)
        raise


def get_session_factory(engine=None) -> sessionmaker:
    """Crea y retorna una fábrica de sesiones.

    Args:
        engine: Engine de SQLAlchemy. Si es None, se crea uno nuevo.

    Returns:
        sessionmaker: Fábrica configurada para crear sesiones.

    Ejemplo::

        SessionFactory = get_session_factory()
        session = SessionFactory()
    """
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine, expire_on_commit=False)


def init_db(engine=None) -> None:
    """Inicializa la base de datos creando todas las tablas.

    Si las tablas ya existen, no las modifica (CREATE IF NOT EXISTS).

    Args:
        engine: Engine de SQLAlchemy. Si es None, se crea uno nuevo.

    Returns:
        None

    Ejemplo::

        init_db()  # Crea mihac.db con las 3 tablas
    """
    if engine is None:
        engine = get_engine()

    try:
        # Asegurar que el directorio de la BD existe
        import config
        Path(config.DB_PATH).parent.mkdir(parents=True, exist_ok=True)

        Base.metadata.create_all(engine)
        logger.info("Base de datos inicializada correctamente. Tablas creadas.")
    except Exception as e:
        logger.error("Error al inicializar la base de datos: %s", e)
        raise


def get_session(engine=None) -> Session:
    """Crea y retorna una sesión de base de datos lista para usar.

    Args:
        engine: Engine de SQLAlchemy. Si es None, se crea uno nuevo.

    Returns:
        Session: Sesión activa de SQLAlchemy.

    Ejemplo::

        session = get_session()
        session.add(solicitud)
        session.commit()
        session.close()
    """
    factory = get_session_factory(engine)
    return factory()
