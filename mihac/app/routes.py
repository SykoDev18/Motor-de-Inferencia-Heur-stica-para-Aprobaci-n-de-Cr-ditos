# ============================================================
# MIHAC v1.0 — Rutas de la Aplicación Web
# app/routes.py
# ============================================================
# Blueprint principal con las rutas de la interfaz.
# ============================================================

import logging

from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
)

from app import db
from app.forms import EvaluacionForm
from app.models import Evaluacion
from core.engine import InferenceEngine

logger = logging.getLogger(__name__)

main = Blueprint("main", __name__)

# Motor de inferencia (instancia única por proceso)
_engine = InferenceEngine()


# ════════════════════════════════════════════════════════════
# RUTA: PÁGINA PRINCIPAL — FORMULARIO DE EVALUACIÓN
# ════════════════════════════════════════════════════════════

@main.route("/", methods=["GET", "POST"])
def index():
    """Formulario de nueva evaluación crediticia.

    GET:  Renderiza el formulario vacío.
    POST: Valida datos → ejecuta motor → guarda en BD →
          redirige a resultado.
    """
    form = EvaluacionForm()

    if form.validate_on_submit():
        # Construir dict de entrada para el motor
        datos_entrada = {
            "edad": form.edad.data,
            "ingreso_mensual": form.ingreso_mensual.data,
            "total_deuda_actual": form.total_deuda_actual.data,
            "historial_crediticio": int(
                form.historial_crediticio.data
            ),
            "antiguedad_laboral": form.antiguedad_laboral.data,
            "numero_dependientes": form.numero_dependientes.data,
            "tipo_vivienda": form.tipo_vivienda.data,
            "proposito_credito": form.proposito_credito.data,
            "monto_credito": form.monto_credito.data,
        }

        # Ejecutar motor de inferencia
        try:
            resultado = _engine.evaluate(datos_entrada)
        except Exception as e:
            logger.error("Error al evaluar: %s", e)
            flash(
                "Ocurrió un error al procesar la evaluación. "
                "Intenta de nuevo.",
                "danger",
            )
            return render_template("index.html", form=form)

        # Verificar errores de validación del motor
        errores = resultado.get("errores_validacion", [])
        if errores:
            for err in errores:
                flash(f"Error de validación: {err}", "warning")
            return render_template("index.html", form=form)

        # Guardar en base de datos
        try:
            evaluacion = Evaluacion.from_inference_result(
                datos_entrada, resultado
            )
            db.session.add(evaluacion)
            db.session.commit()
            logger.info(
                "Evaluación #%d guardada: %s (score=%d)",
                evaluacion.id,
                evaluacion.dictamen,
                evaluacion.score_final,
            )
        except Exception as e:
            db.session.rollback()
            logger.error("Error al guardar en BD: %s", e)
            flash(
                "Error al guardar la evaluación en la base "
                "de datos.",
                "danger",
            )
            return render_template("index.html", form=form)

        # Redirigir a página de resultado
        flash("Evaluación completada exitosamente.", "success")
        return redirect(
            url_for("main.resultado", eval_id=evaluacion.id)
        )

    return render_template("index.html", form=form)


# ════════════════════════════════════════════════════════════
# RUTA: RESULTADO DE EVALUACIÓN
# ════════════════════════════════════════════════════════════

@main.route("/resultado/<int:eval_id>")
def resultado(eval_id):
    """Muestra el resultado detallado de una evaluación.

    Se implementará completamente en Entregable 3.
    Por ahora redirige al index con flash informativo.
    """
    evaluacion = Evaluacion.query.get_or_404(eval_id)
    # Stub: en Entregable 3 se renderizará resultado.html
    return render_template(
        "resultado_stub.html", evaluacion=evaluacion
    )


# ════════════════════════════════════════════════════════════
# RUTA: HISTORIAL (stub — Entregable 3)
# ════════════════════════════════════════════════════════════

@main.route("/historial")
def historial():
    """Historial de evaluaciones — se implementará en Entregable 3."""
    return render_template("index.html", form=EvaluacionForm())


# ════════════════════════════════════════════════════════════
# RUTA: DASHBOARD (stub — Entregable 4)
# ════════════════════════════════════════════════════════════

@main.route("/dashboard")
def dashboard():
    """Dashboard analítico — se implementará en Entregable 4."""
    return render_template("index.html", form=EvaluacionForm())
