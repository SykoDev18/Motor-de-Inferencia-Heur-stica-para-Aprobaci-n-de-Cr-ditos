# ============================================================
# MIHAC v1.0 — Modelos de Base de Datos (SQLAlchemy ORM)
# Motor de Inferencia Heurística para Aprobación de Créditos
# ============================================================
# Tres tablas: Solicitud, Evaluacion, LogAuditoria.
# La relación es: Solicitud 1──▶ N Evaluacion 1──▶ N LogAuditoria
# ============================================================

import json
import logging
from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Text,
    DateTime,
    ForeignKey,
    CheckConstraint,
    Index,
    create_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    relationship,
    sessionmaker,
    Mapped,
    mapped_column,
)

logger = logging.getLogger(__name__)


# ────────────────────────────────────────────────────────────
# Base declarativa de SQLAlchemy 2.0
# ────────────────────────────────────────────────────────────
class Base(DeclarativeBase):
    """Clase base para todos los modelos del sistema MIHAC."""
    pass


# ────────────────────────────────────────────────────────────
# MODELO: Solicitud
# ────────────────────────────────────────────────────────────
class Solicitud(Base):
    """Representa una solicitud de crédito ingresada al sistema.

    Contiene todos los datos de entrada del solicitante que serán
    procesados por el motor de inferencia heurística.

    Attributes:
        id: Identificador único autoincremental.
        fecha_solicitud: Fecha y hora de registro de la solicitud.
        nombre_solicitante: Nombre completo del solicitante.
        edad: Edad del solicitante (18–99).
        ingreso_mensual: Ingreso mensual bruto en moneda local (> 0).
        total_deuda_actual: Suma de deudas vigentes (>= 0).
        historial_crediticio: 0=Malo, 1=Neutro, 2=Bueno.
        antiguedad_laboral: Años en el empleo actual (0–40).
        numero_dependientes: Personas dependientes económicamente (0–10).
        tipo_vivienda: 'Propia', 'Alquiler' o 'Familiar'.
        proposito_credito: Destino del crédito solicitado.
        monto_credito: Monto solicitado (500–50000).
        evaluaciones: Relación con las evaluaciones generadas.

    Ejemplo de uso::

        solicitud = Solicitud(
            nombre_solicitante="Juan Pérez",
            edad=35,
            ingreso_mensual=15000.00,
            total_deuda_actual=3000.00,
            historial_crediticio=2,
            antiguedad_laboral=5,
            numero_dependientes=2,
            tipo_vivienda="Propia",
            proposito_credito="Negocio",
            monto_credito=10000.00
        )
        session.add(solicitud)
        session.commit()
    """

    __tablename__ = "solicitudes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    fecha_solicitud: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    nombre_solicitante: Mapped[str] = mapped_column(String(200), nullable=False)

    # ── Variables de entrada del sistema ──
    edad: Mapped[int] = mapped_column(Integer, nullable=False)
    ingreso_mensual: Mapped[float] = mapped_column(Float, nullable=False)
    total_deuda_actual: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    historial_crediticio: Mapped[int] = mapped_column(Integer, nullable=False)
    antiguedad_laboral: Mapped[int] = mapped_column(Integer, nullable=False)
    numero_dependientes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    tipo_vivienda: Mapped[str] = mapped_column(String(50), nullable=False)
    proposito_credito: Mapped[str] = mapped_column(String(100), nullable=False)
    monto_credito: Mapped[float] = mapped_column(Float, nullable=False)

    # ── Relación ──
    evaluaciones = relationship(
        "Evaluacion", back_populates="solicitud", cascade="all, delete-orphan"
    )

    # ── Restricciones a nivel de tabla ──
    __table_args__ = (
        CheckConstraint("edad >= 18 AND edad <= 99", name="chk_edad_rango"),
        CheckConstraint("ingreso_mensual > 0", name="chk_ingreso_positivo"),
        CheckConstraint("total_deuda_actual >= 0", name="chk_deuda_no_negativa"),
        CheckConstraint(
            "historial_crediticio IN (0, 1, 2)", name="chk_historial_valido"
        ),
        CheckConstraint(
            "antiguedad_laboral >= 0 AND antiguedad_laboral <= 40",
            name="chk_antiguedad_rango",
        ),
        CheckConstraint(
            "numero_dependientes >= 0 AND numero_dependientes <= 10",
            name="chk_dependientes_rango",
        ),
        CheckConstraint(
            "monto_credito >= 500 AND monto_credito <= 50000",
            name="chk_monto_rango",
        ),
        Index("idx_solicitud_fecha", "fecha_solicitud"),
    )

    def __repr__(self) -> str:
        return (
            f"<Solicitud(id={self.id}, nombre='{self.nombre_solicitante}', "
            f"monto={self.monto_credito}, fecha='{self.fecha_solicitud}')>"
        )


# ────────────────────────────────────────────────────────────
# MODELO: Evaluacion
# ────────────────────────────────────────────────────────────
class Evaluacion(Base):
    """Resultado de la evaluación heurística de una solicitud.

    Almacena el score calculado, el dictamen emitido, el reporte
    explicativo en lenguaje natural y las reglas que se activaron
    durante el proceso de inferencia.

    Attributes:
        id: Identificador único autoincremental.
        solicitud_id: Clave foránea a la solicitud evaluada.
        fecha_evaluacion: Fecha y hora de la evaluación.
        score_final: Puntuación final del motor (0–100).
        dictamen: 'APROBADO', 'REVISION_MANUAL' o 'RECHAZADO'.
        dti_calculado: Ratio Deuda/Ingreso calculado.
        reporte_explicacion: Texto en lenguaje natural con la justificación.
        reglas_activadas: Lista JSON con los IDs de las reglas disparadas.
        tiempo_procesamiento_ms: Milisegundos que tomó la evaluación.
        solicitud: Relación inversa con Solicitud.
        logs: Relación con los registros de auditoría.

    Ejemplo de uso::

        evaluacion = Evaluacion(
            solicitud_id=1,
            score_final=85,
            dictamen="APROBADO",
            dti_calculado=0.20,
            reporte_explicacion="El solicitante presenta un perfil sólido...",
            reglas_activadas='["R005", "R006", "R007", "R009"]',
            tiempo_procesamiento_ms=45
        )
        session.add(evaluacion)
        session.commit()
    """

    __tablename__ = "evaluaciones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    solicitud_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("solicitudes.id"), nullable=False
    )
    fecha_evaluacion: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    score_final: Mapped[int] = mapped_column(Integer, nullable=False)
    dictamen: Mapped[str] = mapped_column(String(20), nullable=False)
    dti_calculado: Mapped[float] = mapped_column(Float, nullable=False)
    reporte_explicacion: Mapped[str] = mapped_column(Text, nullable=False)
    reglas_activadas: Mapped[str] = mapped_column(Text, nullable=False, default="[]")
    tiempo_procesamiento_ms: Mapped[int] = mapped_column(Integer, nullable=True)

    # ── Relaciones ──
    solicitud = relationship("Solicitud", back_populates="evaluaciones")
    logs = relationship(
        "LogAuditoria", back_populates="evaluacion", cascade="all, delete-orphan"
    )

    # ── Restricciones ──
    __table_args__ = (
        CheckConstraint(
            "score_final >= 0 AND score_final <= 100", name="chk_score_rango"
        ),
        CheckConstraint(
            "dictamen IN ('APROBADO', 'REVISION_MANUAL', 'RECHAZADO')",
            name="chk_dictamen_valido",
        ),
        CheckConstraint("dti_calculado >= 0", name="chk_dti_no_negativo"),
        Index("idx_evaluacion_fecha", "fecha_evaluacion"),
        Index("idx_evaluacion_dictamen", "dictamen"),
    )

    @property
    def reglas_activadas_lista(self) -> list[str]:
        """Deserializa el campo reglas_activadas de JSON a lista Python.

        Returns:
            Lista de IDs de reglas activadas, e.g. ['R001', 'R005'].

        Ejemplo::

            evaluacion.reglas_activadas_lista  # ['R001', 'R005']
        """
        try:
            return json.loads(self.reglas_activadas)
        except (json.JSONDecodeError, TypeError):
            logger.warning(
                "No se pudo deserializar reglas_activadas para evaluacion id=%s",
                self.id,
            )
            return []

    def __repr__(self) -> str:
        return (
            f"<Evaluacion(id={self.id}, solicitud_id={self.solicitud_id}, "
            f"score={self.score_final}, dictamen='{self.dictamen}')>"
        )


# ────────────────────────────────────────────────────────────
# MODELO: LogAuditoria
# ────────────────────────────────────────────────────────────
class LogAuditoria(Base):
    """Registro de auditoría para cada acción del sistema.

    Permite trazabilidad completa de las operaciones realizadas
    sobre cada evaluación, cumpliendo requisitos de auditoría
    del sector financiero.

    Attributes:
        id: Identificador único autoincremental.
        evaluacion_id: Clave foránea a la evaluación auditada.
        timestamp: Fecha y hora exacta de la acción.
        accion: Tipo de acción realizada (e.g. 'EVALUACION_CREADA').
        usuario: Identificador del usuario o sistema que ejecutó la acción.
        detalle: Descripción textual detallada de la acción.
        evaluacion: Relación inversa con Evaluacion.

    Ejemplo de uso::

        log = LogAuditoria(
            evaluacion_id=1,
            accion="EVALUACION_CREADA",
            usuario="sistema",
            detalle="Score: 85 | Dictamen: APROBADO | Reglas: R005, R007"
        )
        session.add(log)
        session.commit()
    """

    __tablename__ = "log_auditoria"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    evaluacion_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("evaluaciones.id"), nullable=False
    )
    timestamp: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    accion: Mapped[str] = mapped_column(String(100), nullable=False)
    usuario: Mapped[str] = mapped_column(String(100), nullable=False, default="sistema")
    detalle: Mapped[str] = mapped_column(Text, nullable=True)

    # ── Relación ──
    evaluacion = relationship("Evaluacion", back_populates="logs")

    # ── Índices ──
    __table_args__ = (
        Index("idx_log_timestamp", "timestamp"),
        Index("idx_log_accion", "accion"),
    )

    def __repr__(self) -> str:
        return (
            f"<LogAuditoria(id={self.id}, evaluacion_id={self.evaluacion_id}, "
            f"accion='{self.accion}', timestamp='{self.timestamp}')>"
        )
