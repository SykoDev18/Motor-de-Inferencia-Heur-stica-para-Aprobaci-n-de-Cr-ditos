# ============================================================
# MIHAC v1.0 — Modelo de Evaluación (SQLAlchemy)
# app/models.py
# ============================================================
# Almacena cada evaluación realizada por el sistema.
# Campos de entrada (9 variables), resultados del motor,
# y metadata de auditoría.
# ============================================================

import json
from datetime import datetime
from typing import Any

from app import db


class Evaluacion(db.Model):
    """Registro persistente de una evaluación crediticia MIHAC.

    Cada fila representa una solicitud evaluada por el motor,
    con los datos del solicitante, el resultado completo, y
    metadata de auditoría.
    """

    __tablename__ = "evaluaciones"

    # ── Clave primaria ──────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )

    # ── Datos del solicitante (9 variables de entrada) ──────
    edad = db.Column(db.Integer, nullable=False)
    ingreso_mensual = db.Column(db.Float, nullable=False)
    total_deuda_actual = db.Column(db.Float, nullable=False)
    historial_crediticio = db.Column(
        db.Integer, nullable=False
    )  # 0=Malo, 1=Neutro, 2=Bueno
    antiguedad_laboral = db.Column(db.Integer, nullable=False)
    numero_dependientes = db.Column(db.Integer, nullable=False)
    tipo_vivienda = db.Column(db.String(20), nullable=False)
    proposito_credito = db.Column(db.String(20), nullable=False)
    monto_credito = db.Column(db.Float, nullable=False)

    # ── Resultados del motor ────────────────────────────────
    score_final = db.Column(db.Integer, nullable=False)
    dti_ratio = db.Column(db.Float, nullable=False)
    dti_clasificacion = db.Column(db.String(20), nullable=False)
    dictamen = db.Column(
        db.String(20), nullable=False
    )  # APROBADO, RECHAZADO, REVISION_MANUAL
    umbral_aplicado = db.Column(db.Integer, nullable=False)
    reglas_activadas = db.Column(
        db.Text, nullable=False, default="[]"
    )  # JSON string
    sub_scores = db.Column(
        db.Text, nullable=False, default="{}"
    )  # JSON string
    reporte_explicacion = db.Column(db.Text, nullable=False)

    # ── Metadata ────────────────────────────────────────────
    analista_usuario = db.Column(
        db.String(50), nullable=True
    )
    notas_adicionales = db.Column(db.Text, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<Evaluacion #{self.id} "
            f"{self.dictamen} score={self.score_final}>"
        )

    # ────────────────────────────────────────────────────────
    # MÉTODOS DE CONVENIENCIA
    # ────────────────────────────────────────────────────────

    def to_dict(self) -> dict[str, Any]:
        """Convierte el modelo a diccionario para JSON API.

        Returns:
            Dict con todos los campos serializados.
        """
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat()
            if self.timestamp
            else None,
            # Entrada
            "edad": self.edad,
            "ingreso_mensual": self.ingreso_mensual,
            "total_deuda_actual": self.total_deuda_actual,
            "historial_crediticio": self.historial_crediticio,
            "antiguedad_laboral": self.antiguedad_laboral,
            "numero_dependientes": self.numero_dependientes,
            "tipo_vivienda": self.tipo_vivienda,
            "proposito_credito": self.proposito_credito,
            "monto_credito": self.monto_credito,
            # Resultado
            "score_final": self.score_final,
            "dti_ratio": self.dti_ratio,
            "dti_clasificacion": self.dti_clasificacion,
            "dictamen": self.dictamen,
            "umbral_aplicado": self.umbral_aplicado,
            "reglas_activadas": self.get_reglas_list(),
            "sub_scores": self.get_sub_scores_dict(),
            "reporte_explicacion": self.reporte_explicacion,
            # Metadata
            "analista_usuario": self.analista_usuario,
            "notas_adicionales": self.notas_adicionales,
        }

    def get_reglas_list(self) -> list[dict]:
        """Deserializa las reglas activadas desde JSON.

        Returns:
            Lista de dicts con las reglas (id, impacto, desc).
        """
        try:
            return json.loads(self.reglas_activadas or "[]")
        except (json.JSONDecodeError, TypeError):
            return []

    def get_sub_scores_dict(self) -> dict[str, Any]:
        """Deserializa los sub-scores desde JSON.

        Returns:
            Dict con los 4 sub-scores.
        """
        try:
            return json.loads(self.sub_scores or "{}")
        except (json.JSONDecodeError, TypeError):
            return {}

    @classmethod
    def from_inference_result(
        cls,
        datos_entrada: dict[str, Any],
        resultado: dict[str, Any],
    ) -> "Evaluacion":
        """Crea una instancia desde los dicts del motor MIHAC.

        Constructor conveniente que toma los datos de entrada
        y el resultado de InferenceEngine.evaluate() para
        crear el registro de evaluación.

        Args:
            datos_entrada: Dict con las 9 variables de entrada
                          (edad, ingreso_mensual, etc.).
            resultado: Dict retornado por engine.evaluate()
                      (score_final, dictamen, reglas, etc.).

        Returns:
            Instancia de Evaluacion lista para db.session.add().
        """
        # Serializar reglas activadas a JSON
        reglas = resultado.get("reglas_activadas", [])
        reglas_json = json.dumps(reglas, ensure_ascii=False)

        # Serializar sub-scores a JSON
        sub_scores = resultado.get("sub_scores", {})
        sub_scores_json = json.dumps(
            sub_scores, ensure_ascii=False
        )

        return cls(
            # Datos de entrada
            edad=datos_entrada.get("edad", 0),
            ingreso_mensual=datos_entrada.get(
                "ingreso_mensual", 0
            ),
            total_deuda_actual=datos_entrada.get(
                "total_deuda_actual", 0
            ),
            historial_crediticio=datos_entrada.get(
                "historial_crediticio", 0
            ),
            antiguedad_laboral=datos_entrada.get(
                "antiguedad_laboral", 0
            ),
            numero_dependientes=datos_entrada.get(
                "numero_dependientes", 0
            ),
            tipo_vivienda=datos_entrada.get(
                "tipo_vivienda", "Rentada"
            ),
            proposito_credito=datos_entrada.get(
                "proposito_credito", "Consumo"
            ),
            monto_credito=datos_entrada.get(
                "monto_credito", 0
            ),
            # Resultados del motor
            score_final=resultado.get("score_final", 0),
            dti_ratio=resultado.get("dti_ratio", 0.0),
            dti_clasificacion=resultado.get(
                "dti_clasificacion", "N/A"
            ),
            dictamen=resultado.get("dictamen", "RECHAZADO"),
            umbral_aplicado=resultado.get(
                "umbral_aplicado", 80
            ),
            reglas_activadas=reglas_json,
            sub_scores=sub_scores_json,
            reporte_explicacion=resultado.get(
                "reporte_explicacion", ""
            ),
        )
