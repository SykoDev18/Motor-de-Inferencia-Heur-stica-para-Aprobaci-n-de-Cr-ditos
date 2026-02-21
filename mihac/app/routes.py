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
    """Muestra el resultado detallado de una evaluación."""
    from app.utils import clasificar_dti

    evaluacion = Evaluacion.query.get_or_404(eval_id)
    reglas = evaluacion.get_reglas_list()
    sub_scores = evaluacion.get_sub_scores_dict()
    dti_info = clasificar_dti(evaluacion.dti_ratio)

    # Preparar info de sub-scores para el template
    maximos = {
        "solvencia": 40,
        "estabilidad": 30,
        "historial_score": 20,
        "perfil": 10,
    }
    labels = {
        "solvencia": "Solvencia",
        "estabilidad": "Estabilidad",
        "historial_score": "Historial",
        "perfil": "Perfil",
    }
    sub_scores_info = {}
    for key, max_val in maximos.items():
        valor = sub_scores.get(key, 0)
        pct = (valor / max_val * 100) if max_val > 0 else 0
        sub_scores_info[key] = {
            "label": labels.get(key, key),
            "valor": valor,
            "max": max_val,
            "pct": round(pct, 1),
            "color": (
                "#10B981" if pct >= 60
                else "#F59E0B" if pct >= 30
                else "#EF4444"
            ),
        }

    return render_template(
        "resultado.html",
        ev=evaluacion,
        reglas=reglas,
        sub_scores_info=sub_scores_info,
        dti_info=dti_info,
    )


# ════════════════════════════════════════════════════════════
# RUTA: HISTORIAL DE EVALUACIONES
# ════════════════════════════════════════════════════════════

PER_PAGE = 15

@main.route("/historial")
def historial():
    """Historial paginado de evaluaciones con filtros."""
    # Parámetros de filtro
    filtro_dictamen = request.args.get("dictamen", "").strip()
    filtro_orden = request.args.get("orden", "reciente").strip()
    pagina = request.args.get("page", 1, type=int)

    # Query base
    query = Evaluacion.query

    # Filtro por dictamen
    if filtro_dictamen in ("APROBADO", "RECHAZADO", "REVISION_MANUAL"):
        query = query.filter(Evaluacion.dictamen == filtro_dictamen)

    # Ordenamiento
    orden_map = {
        "reciente": Evaluacion.timestamp.desc(),
        "antiguo": Evaluacion.timestamp.asc(),
        "score_alto": Evaluacion.score_final.desc(),
        "score_bajo": Evaluacion.score_final.asc(),
    }
    orden = orden_map.get(filtro_orden, Evaluacion.timestamp.desc())
    query = query.order_by(orden)

    # Contar total
    total = query.count()
    paginas = max(1, (total + PER_PAGE - 1) // PER_PAGE)
    pagina = max(1, min(pagina, paginas))

    # Paginar
    evaluaciones = query.offset((pagina - 1) * PER_PAGE).limit(PER_PAGE).all()

    return render_template(
        "historial.html",
        evaluaciones=evaluaciones,
        total=total,
        pagina=pagina,
        paginas=paginas,
        filtro_dictamen=filtro_dictamen,
        filtro_orden=filtro_orden,
    )


# ════════════════════════════════════════════════════════════
# RUTA: DASHBOARD (stub — Entregable 4)
# ════════════════════════════════════════════════════════════

@main.route("/dashboard")
def dashboard():
    """Dashboard analítico — se implementará en Entregable 4."""
    return render_template("index.html", form=EvaluacionForm())
