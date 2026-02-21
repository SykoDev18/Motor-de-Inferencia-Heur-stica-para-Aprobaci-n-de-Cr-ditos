# ============================================================
# MIHAC v1.0 — Formularios WTForms
# app/forms.py
# ============================================================
# Formulario de evaluación crediticia con validaciones
# server-side que reflejan los límites de config.py.
# ============================================================

from flask_wtf import FlaskForm
from wtforms import (
    IntegerField,
    FloatField,
    SelectField,
    SubmitField,
)
from wtforms.validators import (
    DataRequired,
    NumberRange,
    InputRequired,
)

# Límites importados desde la configuración central
import sys
from pathlib import Path

_MIHAC_ROOT = Path(__file__).resolve().parent.parent
if str(_MIHAC_ROOT) not in sys.path:
    sys.path.insert(0, str(_MIHAC_ROOT))

from config import (
    EDAD_MIN,
    EDAD_MAX,
    INGRESO_MIN,
    DEUDA_MIN,
    ANTIGUEDAD_LABORAL_MIN,
    ANTIGUEDAD_LABORAL_MAX,
    DEPENDIENTES_MIN,
    DEPENDIENTES_MAX,
    MONTO_CREDITO_MIN,
    MONTO_CREDITO_MAX,
    HISTORIAL_VALORES,
    TIPOS_VIVIENDA,
    PROPOSITOS_CREDITO,
)


class EvaluacionForm(FlaskForm):
    """Formulario de evaluación crediticia MIHAC.

    9 campos de entrada correspondientes a las variables
    del motor de inferencia, con validaciones server-side.
    """

    # ── 1. Edad ─────────────────────────────────────────────
    edad = IntegerField(
        "Edad (años)",
        validators=[
            InputRequired(message="La edad es obligatoria."),
            NumberRange(
                min=EDAD_MIN,
                max=EDAD_MAX,
                message=f"La edad debe estar entre {EDAD_MIN} y {EDAD_MAX} años.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": f"{EDAD_MIN}–{EDAD_MAX}",
            "min": EDAD_MIN,
            "max": EDAD_MAX,
        },
    )

    # ── 2. Ingreso mensual ──────────────────────────────────
    ingreso_mensual = FloatField(
        "Ingreso mensual ($)",
        validators=[
            InputRequired(message="El ingreso es obligatorio."),
            NumberRange(
                min=INGRESO_MIN,
                message=f"El ingreso debe ser mayor a ${INGRESO_MIN}.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej. 25000",
            "min": INGRESO_MIN,
            "step": "0.01",
        },
    )

    # ── 3. Deuda actual ─────────────────────────────────────
    total_deuda_actual = FloatField(
        "Total deuda actual ($)",
        validators=[
            InputRequired(message="La deuda actual es obligatoria."),
            NumberRange(
                min=DEUDA_MIN,
                message=f"La deuda no puede ser negativa.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": "Ej. 5000",
            "min": DEUDA_MIN,
            "step": "0.01",
        },
    )

    # ── 4. Historial crediticio ─────────────────────────────
    historial_crediticio = SelectField(
        "Historial crediticio",
        choices=[("", "Seleccionar...")] + [
            (str(k), v) for k, v in HISTORIAL_VALORES.items()
        ],
        validators=[
            DataRequired(message="Selecciona un historial."),
        ],
        render_kw={"class": "form-select"},
        coerce=str,
    )

    # ── 5. Antigüedad laboral ───────────────────────────────
    antiguedad_laboral = IntegerField(
        "Antigüedad laboral (años)",
        validators=[
            InputRequired(
                message="La antigüedad laboral es obligatoria."
            ),
            NumberRange(
                min=ANTIGUEDAD_LABORAL_MIN,
                max=ANTIGUEDAD_LABORAL_MAX,
                message=f"Debe estar entre {ANTIGUEDAD_LABORAL_MIN} y {ANTIGUEDAD_LABORAL_MAX} años.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": f"{ANTIGUEDAD_LABORAL_MIN}–{ANTIGUEDAD_LABORAL_MAX}",
            "min": ANTIGUEDAD_LABORAL_MIN,
            "max": ANTIGUEDAD_LABORAL_MAX,
        },
    )

    # ── 6. Número de dependientes ───────────────────────────
    numero_dependientes = IntegerField(
        "Número de dependientes",
        validators=[
            InputRequired(
                message="El número de dependientes es obligatorio."
            ),
            NumberRange(
                min=DEPENDIENTES_MIN,
                max=DEPENDIENTES_MAX,
                message=f"Debe estar entre {DEPENDIENTES_MIN} y {DEPENDIENTES_MAX}.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": f"{DEPENDIENTES_MIN}–{DEPENDIENTES_MAX}",
            "min": DEPENDIENTES_MIN,
            "max": DEPENDIENTES_MAX,
        },
    )

    # ── 7. Tipo de vivienda ─────────────────────────────────
    tipo_vivienda = SelectField(
        "Tipo de vivienda",
        choices=[("", "Seleccionar...")] + [
            (t, t) for t in TIPOS_VIVIENDA
        ],
        validators=[
            DataRequired(message="Selecciona un tipo de vivienda."),
        ],
        render_kw={"class": "form-select"},
    )

    # ── 8. Propósito del crédito ────────────────────────────
    proposito_credito = SelectField(
        "Propósito del crédito",
        choices=[("", "Seleccionar...")] + [
            (p, p) for p in PROPOSITOS_CREDITO
        ],
        validators=[
            DataRequired(
                message="Selecciona el propósito del crédito."
            ),
        ],
        render_kw={"class": "form-select"},
    )

    # ── 9. Monto solicitado ─────────────────────────────────
    monto_credito = FloatField(
        "Monto solicitado ($)",
        validators=[
            InputRequired(
                message="El monto solicitado es obligatorio."
            ),
            NumberRange(
                min=MONTO_CREDITO_MIN,
                max=MONTO_CREDITO_MAX,
                message=f"Debe estar entre ${MONTO_CREDITO_MIN:,.0f} y ${MONTO_CREDITO_MAX:,.0f}.",
            ),
        ],
        render_kw={
            "class": "form-control",
            "placeholder": f"{MONTO_CREDITO_MIN:,.0f}–{MONTO_CREDITO_MAX:,.0f}",
            "min": MONTO_CREDITO_MIN,
            "max": MONTO_CREDITO_MAX,
            "step": "0.01",
        },
    )

    # ── Botón submit ────────────────────────────────────────
    submit = SubmitField(
        "Evaluar Solicitud",
        render_kw={
            "class": "btn btn-primary btn-lg w-100",
        },
    )
