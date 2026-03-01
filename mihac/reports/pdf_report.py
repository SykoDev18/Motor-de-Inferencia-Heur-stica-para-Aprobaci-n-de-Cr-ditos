# ============================================================
# MIHAC v1.0 — Generador de Reportes PDF
# reports/pdf_report.py
# ============================================================
# Genera reportes PDF profesionales:
#   - Versión completa (auditoría/regulador): ~8 páginas
#   - Versión cliente (simplificada): ~2 páginas
#
# Renderer: WeasyPrint (preferido) → xhtml2pdf (fallback).
# En Windows sin GTK3/Pango, usa xhtml2pdf automáticamente.
#
# Dependencias: weasyprint | xhtml2pdf, Jinja2
# ============================================================

import io
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

logger = logging.getLogger(__name__)

# ── Detectar renderer disponible ─────────────────────────────
_USE_WEASYPRINT = False
try:
    from weasyprint import HTML as _WeasyHTML
    # Verify native libs are loadable
    _WeasyHTML(string="<p>test</p>").write_pdf()
    _USE_WEASYPRINT = True
    logger.info("PDF renderer: WeasyPrint")
except Exception:
    logger.info(
        "WeasyPrint no disponible (faltan libs nativas). "
        "Usando xhtml2pdf como renderer."
    )

if not _USE_WEASYPRINT:
    from xhtml2pdf import pisa  # noqa: E402

# ── Rutas ────────────────────────────────────────────────────
_REPORTS_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _REPORTS_DIR.parent
_TEMPLATES_DIR = _REPORTS_DIR / "templates"
_EXPORTS_DIR = _REPORTS_DIR / "exports"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

# ── Mapeos de texto ──────────────────────────────────────────
_HISTORIAL_LABELS = {0: "Malo", 1: "Neutro", 2: "Bueno"}

_DTI_INTERPRETACIONES = {
    "BAJO": (
        "La carga de deuda del solicitante es saludable. "
        "Destina menos del 25% de su ingreso al servicio de "
        "deudas, lo que indica amplio margen para asumir "
        "nuevas obligaciones financieras sin comprometer "
        "su estabilidad económica."
    ),
    "MODERADO": (
        "La carga de deuda es aceptable pero con margen "
        "limitado. El solicitante destina entre el 25% y "
        "40% de su ingreso al pago de deudas. Se recomienda "
        "cautela al asumir nuevas obligaciones."
    ),
    "ALTO": (
        "La carga de deuda es elevada. El solicitante destina "
        "entre el 40% y 60% de su ingreso al servicio de "
        "deudas, lo que compromete su capacidad de pago "
        "ante contingencias financieras."
    ),
    "CRITICO": (
        "El solicitante se encuentra en situación de "
        "sobreendeudamiento crítico. Más del 60% de su "
        "ingreso se destina a deudas existentes. No es "
        "recomendable asumir obligaciones adicionales."
    ),
}

_SUGERENCIAS_POR_REGLA = {
    "R002": (
        "Establecer un historial crediticio positivo "
        "mediante pagos puntuales de compromisos pequeños"
    ),
    "R004": (
        "Consolidar una mayor trayectoria laboral (al menos "
        "1 año continuo) antes de solicitar crédito"
    ),
    "R008": (
        "Considerar un propósito de crédito productivo como "
        "negocio o educación que genere retorno"
    ),
    "R009": (
        "Esperar a cumplir 21 años para un perfil más maduro "
        "ante las instituciones financieras"
    ),
    "R010": (
        "Incrementar el ingreso familiar o reducir el número "
        "de dependientes económicos directos"
    ),
    "R014": (
        "Reducir las deudas vigentes en al menos 30% antes "
        "de adquirir nuevas obligaciones financieras"
    ),
}

_PUNTOS_POSITIVOS_MAP = {
    "R001": "Cuenta con un historial crediticio positivo",
    "R003": "Tiene una trayectoria laboral estable (5+ años)",
    "R005": "Posee vivienda propia, lo que demuestra arraigo",
    "R006": "El propósito del crédito es productivo (negocio)",
    "R007": "Invierte en educación y capital humano",
    "R011": "Su solvencia compensa la falta de historial formal",
    "R012": "Su ingreso es amplio respecto al monto solicitado",
    "R013": "No tiene deudas activas y cuenta con experiencia laboral",
    "R015": "Perfil de máxima estabilidad financiera y personal",
}

_PUNTOS_NEGATIVOS_MAP = {
    "R002": "Su historial crediticio actual es desfavorable",
    "R004": "No cuenta con suficiente trayectoria laboral",
    "R008": "El propósito del crédito se considera de alto riesgo",
    "R009": "Su edad actual implica un perfil de mayor riesgo",
    "R010": "La carga familiar es elevada respecto al ingreso",
    "R014": "Su nivel de endeudamiento actual es preocupante",
}


class PDFReportGenerator:
    """Generador de reportes PDF profesionales para MIHAC.

    Utiliza Jinja2 para renderizar templates HTML y
    WeasyPrint para convertirlos a PDF.

    Genera dos tipos de reporte:
        - **Completo**: Para auditoría y reguladores (~8 pág.)
        - **Cliente**: Para el solicitante (~2 pág.)

    Ejemplo de uso::

        gen = PDFReportGenerator()
        path = gen.generate_complete_report(datos, "out.pdf")
        print(f"PDF guardado en {path}")
    """

    def __init__(
        self,
        template_dir: str | Path | None = None,
    ) -> None:
        """Inicializa el entorno Jinja2 con los templates.

        Args:
            template_dir: Directorio de templates HTML.
                Si es None, usa reports/templates/.
        """
        tdir = Path(template_dir) if template_dir else _TEMPLATES_DIR
        self._env = Environment(
            loader=FileSystemLoader(str(tdir)),
            autoescape=False,
        )
        # Registrar helpers como funciones globales de Jinja2
        self._env.globals["formato_moneda"] = self._format_currency
        logger.info(
            "PDFReportGenerator inicializado con templates en %s",
            tdir,
        )

    # ────────────────────────────────────────────────────────
    # REPORTE COMPLETO (auditoría / regulador)
    # ────────────────────────────────────────────────────────

    def generate_complete_report(
        self,
        evaluacion: dict[str, Any],
        output_path: str | Path,
    ) -> str:
        """Genera el reporte PDF completo (~8 páginas).

        Contenido:
            1. Portada, 2. Resumen ejecutivo, 3. Datos del
            solicitante, 4. Análisis de solvencia (DTI),
            5. Desglose del score, 6. Reglas activadas,
            7. Explicación completa, 8. Conclusión.

        Args:
            evaluacion: Dict con datos de la evaluación
                (resultado de Evaluacion.to_dict() o
                estructura equivalente).
            output_path: Ruta donde guardar el PDF.

        Returns:
            Ruta absoluta del PDF generado.
        """
        ev = _EvalProxy(evaluacion)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        # ── Preparar contexto ──
        reglas = evaluacion.get("reglas_activadas", [])
        sub_scores = evaluacion.get("sub_scores", {})

        # Dictamen clase CSS
        dictamen = evaluacion.get("dictamen", "")
        dictamen_clase = self._dictamen_clase(dictamen)

        # Texto historial
        hist_val = evaluacion.get("historial_crediticio", -1)
        texto_historial = _HISTORIAL_LABELS.get(hist_val, "Desconocido")

        # Reglas separadas y enriquecidas
        reglas_positivas = sorted(
            [r for r in reglas if r.get("impacto", r.get("impacto_puntos", 0)) > 0],
            key=lambda x: x.get("impacto", x.get("impacto_puntos", 0)),
            reverse=True,
        )
        reglas_negativas = sorted(
            [r for r in reglas if r.get("impacto", r.get("impacto_puntos", 0)) < 0],
            key=lambda x: abs(x.get("impacto", x.get("impacto_puntos", 0))),
            reverse=True,
        )

        # Normalizar campo impacto
        for r in reglas_positivas + reglas_negativas:
            if "impacto" not in r and "impacto_puntos" in r:
                r["impacto"] = r["impacto_puntos"]
            r["condicion_texto"] = self._condicion_texto(r)

        # Módulos de score
        modulos = self._build_modulos(sub_scores)

        # DTI info
        ingreso = evaluacion.get("ingreso_mensual", 1)
        deuda = evaluacion.get("total_deuda_actual", 0)
        monto = evaluacion.get("monto_credito", 0)
        cuota_estimada = round(monto / 12, 2) if monto > 0 else 0

        dti_actual = evaluacion.get("dti_ratio", 0.0)
        dti_proyectado = (deuda + cuota_estimada) / ingreso if ingreso > 0 else 1.0

        dti_clasif = evaluacion.get("dti_clasificacion", "N/A")
        dti_interpretacion = _DTI_INTERPRETACIONES.get(
            dti_clasif, "Clasificación no disponible."
        )

        # Recomendación resumen ejecutivo
        recomendacion = self._generar_recomendacion_resumen(
            evaluacion, reglas_positivas, reglas_negativas
        )

        # Conclusión página 8
        conclusion = self._generar_conclusion(
            evaluacion, reglas_positivas, reglas_negativas
        )

        # Top positivos texto
        top_positivos = ", ".join(
            [r["descripcion"] for r in reglas_positivas[:2]]
        ) if reglas_positivas else "perfil general equilibrado"

        # Sugerencias (para rechazado)
        sugerencias = self._obtener_sugerencias(reglas_negativas)

        # Meses recomendados
        meses_recomendados = self._calcular_meses(evaluacion)

        # Factores manuales (para revisión)
        factores_manuales = self._factores_revision(evaluacion, reglas)

        # ── Renderizar template ──
        template = self._env.get_template("reporte_completo.html")
        html_str = template.render(
            ev=ev,
            timestamp=timestamp,
            dictamen_clase=dictamen_clase,
            texto_historial=texto_historial,
            reglas=reglas,
            reglas_positivas=reglas_positivas,
            reglas_negativas=reglas_negativas,
            modulos=modulos,
            cuota_estimada=cuota_estimada,
            dti_proyectado=dti_proyectado,
            dti_interpretacion=dti_interpretacion,
            recomendacion=recomendacion,
            conclusion=conclusion,
            top_positivos=top_positivos,
            sugerencias=sugerencias,
            meses_recomendados=meses_recomendados,
            factores_manuales=factores_manuales,
        )

        # ── Generar PDF ──
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self._render_pdf(html_str, out)

        logger.info("Reporte completo generado: %s", out)
        return str(out.resolve())

    # ────────────────────────────────────────────────────────
    # REPORTE CLIENTE (simplificado)
    # ────────────────────────────────────────────────────────

    def generate_client_report(
        self,
        evaluacion: dict[str, Any],
        output_path: str | Path,
    ) -> str:
        """Genera el reporte PDF simplificado (~2 páginas).

        Versión para entregar al solicitante. No incluye
        reglas técnicas, sub-scores detallados ni datos
        de auditoría.

        Args:
            evaluacion: Dict con datos de la evaluación.
            output_path: Ruta donde guardar el PDF.

        Returns:
            Ruta absoluta del PDF generado.
        """
        ev = _EvalProxy(evaluacion)
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        dictamen = evaluacion.get("dictamen", "")
        dictamen_clase = self._dictamen_clase(dictamen)

        reglas = evaluacion.get("reglas_activadas", [])

        # Puntos positivos (lenguaje cliente)
        puntos_positivos = []
        for r in reglas:
            impacto = r.get("impacto", r.get("impacto_puntos", 0))
            rid = r.get("id", "")
            if impacto > 0 and rid in _PUNTOS_POSITIVOS_MAP:
                puntos_positivos.append(_PUNTOS_POSITIVOS_MAP[rid])
        if not puntos_positivos:
            puntos_positivos = [
                "Su solicitud fue evaluada con los criterios estándar"
            ]

        # Puntos a mejorar (lenguaje cliente)
        puntos_mejorar = []
        for r in reglas:
            impacto = r.get("impacto", r.get("impacto_puntos", 0))
            rid = r.get("id", "")
            if impacto < 0 and rid in _PUNTOS_NEGATIVOS_MAP:
                puntos_mejorar.append(_PUNTOS_NEGATIVOS_MAP[rid])

        # Acciones de mejora
        acciones_mejora = self._obtener_sugerencias(
            [r for r in reglas if r.get("impacto", r.get("impacto_puntos", 0)) < 0]
        )
        if not acciones_mejora:
            acciones_mejora = [
                "Mantener un buen historial de pagos puntuales",
                "Reducir deudas existentes cuando sea posible",
            ]

        meses_recomendados = self._calcular_meses(evaluacion)

        # ── Renderizar template ──
        template = self._env.get_template("reporte_cliente.html")
        html_str = template.render(
            ev=ev,
            timestamp=timestamp,
            dictamen_clase=dictamen_clase,
            puntos_positivos=puntos_positivos,
            puntos_mejorar=puntos_mejorar,
            acciones_mejora=acciones_mejora,
            meses_recomendados=meses_recomendados,
        )

        # ── Generar PDF ──
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        self._render_pdf(html_str, out)

        logger.info("Reporte cliente generado: %s", out)
        return str(out.resolve())

    # ────────────────────────────────────────────────────────
    # BATCH
    # ────────────────────────────────────────────────────────

    def batch_generate(
        self,
        evaluaciones: list[dict[str, Any]],
        output_dir: str | Path,
        report_type: str = "completo",
    ) -> list[str]:
        """Genera múltiples reportes en lote.

        Args:
            evaluaciones: Lista de dicts de evaluación.
            output_dir: Directorio de salida.
            report_type: 'completo' o 'cliente'.

        Returns:
            Lista de rutas de PDFs generados.
        """
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        rutas: list[str] = []
        total = len(evaluaciones)

        gen_fn = (
            self.generate_complete_report
            if report_type == "completo"
            else self.generate_client_report
        )
        suffix = "completo" if report_type == "completo" else "cliente"

        for i, ev in enumerate(evaluaciones):
            ev_id = ev.get("id", i + 1)
            filename = f"evaluacion_{ev_id}_{suffix}.pdf"
            filepath = out_dir / filename

            if total > 10 and (i + 1) % 10 == 0:
                print(
                    f"  Generando reportes: {i + 1}/{total} "
                    f"({(i + 1) / total * 100:.0f}%)"
                )

            try:
                path = gen_fn(ev, filepath)
                rutas.append(path)
            except Exception as e:
                logger.error(
                    "Error generando PDF %s: %s", filename, e
                )

        logger.info(
            "Batch completado: %d/%d PDFs generados",
            len(rutas), total,
        )
        return rutas

    # ────────────────────────────────────────────────────────
    # HELPERS PRIVADOS
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _format_currency(value: float) -> str:
        """Formatea un número como moneda MXN.

        Args:
            value: Cantidad a formatear.

        Returns:
            String con formato $XX,XXX.XX MXN
        """
        try:
            return f"${value:,.2f} MXN"
        except (TypeError, ValueError):
            return "$0.00 MXN"

    @staticmethod
    def _generate_progress_bar_svg(
        value: int,
        max_value: int,
        width: int = 400,
        height: int = 22,
    ) -> str:
        """Genera SVG de barra de progreso.

        Args:
            value: Valor actual.
            max_value: Valor máximo.
            width: Ancho total en px.
            height: Alto en px.

        Returns:
            String SVG incrustable en HTML.
        """
        if max_value <= 0:
            pct = 0
        else:
            pct = min(value / max_value, 1.0)
        fill_w = int(width * pct)

        # Color según porcentaje
        if pct >= 0.6:
            fill_color = "#10B981"
        elif pct >= 0.3:
            fill_color = "#F59E0B"
        else:
            fill_color = "#EF4444"

        return (
            f'<svg width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            f'<rect x="0" y="0" width="{width}" '
            f'height="{height}" rx="4" fill="#E2E8F0"/>'
            f'<rect x="0" y="0" width="{fill_w}" '
            f'height="{height}" rx="4" fill="{fill_color}"/>'
            f'<text x="{width // 2}" y="{height - 6}" '
            f'text-anchor="middle" font-size="10" '
            f'fill="#0D1B2A" font-weight="bold">'
            f'{value}/{max_value} ({pct:.0%})</text>'
            f'</svg>'
        )

    def _build_modulos(
        self, sub_scores: dict
    ) -> list[dict]:
        """Construye la lista de módulos de score."""
        defs = [
            ("Solvencia", "solvencia", 40),
            ("Estabilidad", "estabilidad", 30),
            ("Historial", "historial_score", 20),
            ("Perfil", "perfil", 10),
        ]
        modulos = []
        for nombre, key, maximo in defs:
            valor = sub_scores.get(key, 0)
            pct = round(valor / maximo * 100, 1) if maximo > 0 else 0
            bar_svg = self._generate_progress_bar_svg(valor, maximo)
            modulos.append({
                "nombre": nombre,
                "key": key,
                "valor": valor,
                "max": maximo,
                "pct": pct,
                "bar_svg": bar_svg,
            })
        return modulos

    @staticmethod
    def _dictamen_clase(dictamen: str) -> str:
        """Retorna clase CSS simplificada."""
        if dictamen == "APROBADO":
            return "aprobado"
        if dictamen == "RECHAZADO":
            return "rechazado"
        return "revision"

    @staticmethod
    def _render_pdf(html_str: str, output_path: Path) -> None:
        """Renderiza HTML a PDF usando el renderer disponible.

        Usa WeasyPrint si las librerías nativas están
        disponibles; de lo contrario usa xhtml2pdf.

        Args:
            html_str: Contenido HTML renderizado.
            output_path: Ruta del archivo PDF de salida.
        """
        if _USE_WEASYPRINT:
            _WeasyHTML(string=html_str).write_pdf(str(output_path))
        else:
            with open(output_path, "wb") as f:
                status = pisa.CreatePDF(
                    src=html_str,
                    dest=f,
                    encoding="utf-8",
                )
                if status.err:
                    raise RuntimeError(
                        f"xhtml2pdf error: {status.err} errores"
                    )

    @staticmethod
    def _condicion_texto(regla: dict) -> str:
        """Genera texto legible de la condición de una regla."""
        if regla.get("tipo") == "compensacion":
            conds = regla.get("condiciones", [])
            partes = []
            for c in conds:
                campo = c.get("campo", "?")
                op = c.get("operador", "?")
                valor = c.get("valor", "?")
                partes.append(f"{campo}{op}{valor}")
            return ", ".join(partes) if partes else ""
        else:
            campo = regla.get("condicion_campo", "")
            op = regla.get("condicion_operador", "")
            valor = regla.get("condicion_valor", "")
            if campo:
                return f"{campo}{op}{valor}"
            return ""

    @staticmethod
    def _generar_recomendacion_resumen(
        evaluacion: dict,
        positivos: list,
        negativos: list,
    ) -> str:
        """Genera texto de recomendación para resumen ejecutivo."""
        dictamen = evaluacion.get("dictamen", "")
        score = evaluacion.get("score_final", 0)
        monto = evaluacion.get("monto_credito", 0)

        if dictamen == "APROBADO":
            tops = ", ".join(
                [r["descripcion"] for r in positivos[:2]]
            ) if positivos else "perfil estable"
            return (
                f"Se recomienda la aprobación del crédito "
                f"por ${monto:,.2f} MXN. El solicitante "
                f"obtuvo un score de {score}/100 respaldado "
                f"por: {tops}."
            )
        if dictamen == "RECHAZADO":
            negs = ", ".join(
                [r["descripcion"] for r in negativos[:2]]
            ) if negativos else "factores múltiples"
            return (
                f"No se recomienda la aprobación. El score "
                f"de {score}/100 está por debajo del umbral "
                f"requerido. Factores críticos: {negs}."
            )
        return (
            f"El perfil presenta elementos mixtos que "
            f"requieren análisis humano. Score: {score}/100, "
            f"en zona de incertidumbre. Se sugiere revisión "
            f"por un analista experimentado."
        )

    @staticmethod
    def _generar_conclusion(
        evaluacion: dict,
        positivos: list,
        negativos: list,
    ) -> str:
        """Genera conclusión para la última página."""
        dictamen = evaluacion.get("dictamen", "")
        score = evaluacion.get("score_final", 0)
        monto = evaluacion.get("monto_credito", 0)
        dti = evaluacion.get("dti_ratio", 0.0)

        if dictamen == "APROBADO":
            tops = " y ".join(
                [r["descripcion"].lower() for r in positivos[:2]]
            ) if positivos else "perfil general"
            return (
                f"Se recomienda la aprobación del crédito "
                f"solicitado por ${monto:,.2f} MXN. El perfil "
                f"del solicitante cumple con los estándares "
                f"mínimos de solvencia y estabilidad del "
                f"sistema MIHAC. Los factores de {tops} "
                f"respaldan su capacidad de pago."
            )
        if dictamen == "RECHAZADO":
            negs = " y ".join(
                [r["descripcion"].lower() for r in negativos[:2]]
            ) if negativos else "múltiples factores de riesgo"
            return (
                f"No se recomienda la aprobación del crédito "
                f"en este momento. El score de {score}/100 "
                f"no alcanza el umbral requerido. Los factores "
                f"críticos identificados son: {negs}. "
                f"El DTI actual es de {dti:.1%}, lo que "
                f"{'agrava' if dti > 0.40 else 'complementa'} "
                f"la evaluación negativa."
            )
        return (
            f"El perfil presenta elementos mixtos que "
            f"requieren análisis humano adicional. El sistema "
            f"no tiene certeza suficiente para una decisión "
            f"automatizada. El score de {score}/100 se "
            f"encuentra en zona de revisión. Se recomienda "
            f"que un analista examine los factores específicos "
            f"del caso antes de emitir un dictamen final."
        )

    @staticmethod
    def _obtener_sugerencias(negativos: list) -> list[str]:
        """Obtiene sugerencias basadas en reglas negativas."""
        sugs: list[str] = []
        for r in negativos:
            rid = r.get("id", "")
            if rid in _SUGERENCIAS_POR_REGLA:
                sugs.append(_SUGERENCIAS_POR_REGLA[rid])
        if not sugs:
            sugs = [
                "Mantener un historial de pagos puntuales",
                "Reducir el nivel de endeudamiento actual",
                "Consolidar estabilidad laboral y de vivienda",
            ]
        return sugs[:4]

    @staticmethod
    def _calcular_meses(evaluacion: dict) -> int:
        """Calcula meses recomendados para re-evaluación."""
        score = evaluacion.get("score_final", 0)
        dti = evaluacion.get("dti_ratio", 0.0)
        if score < 30 or dti > 0.80:
            return 12
        if score < 50 or dti > 0.60:
            return 6
        return 3

    @staticmethod
    def _factores_revision(
        evaluacion: dict, reglas: list
    ) -> list[str]:
        """Identifica factores que deben revisarse manualmente."""
        factores = []
        score = evaluacion.get("score_final", 0)
        dti = evaluacion.get("dti_ratio", 0.0)
        hist = evaluacion.get("historial_crediticio", -1)

        factores.append(
            f"Score en zona gris: {score}/100 "
            f"(entre umbrales de aprobación y rechazo)"
        )

        if hist == 1:
            factores.append(
                "Historial crediticio neutro: sin datos "
                "suficientes para evaluar comportamiento "
                "de pago"
            )
        if 0.25 <= dti <= 0.45:
            factores.append(
                f"DTI moderado ({dti:.1%}): en el límite "
                f"de lo aceptable para nuevas obligaciones"
            )

        # Reglas de compensación activadas
        comps = [
            r for r in reglas
            if r.get("tipo") == "compensacion"
        ]
        if comps:
            factores.append(
                "Se activaron reglas de compensación que "
                "requieren validación documental: " +
                ", ".join(r.get("id", "") for r in comps)
            )

        if not factores:
            factores.append(
                "Perfil con características mixtas sin "
                "factores dominantes claros"
            )
        return factores


class _EvalProxy:
    """Proxy que expone un dict como atributos de objeto.

    Permite que los templates Jinja2 usen {{ ev.campo }}
    tanto con objetos SQLAlchemy como con dicts planos.
    """

    def __init__(self, data: dict) -> None:
        self._data = data

    def __getattr__(self, name: str) -> Any:
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(
                f"Evaluación no tiene campo '{name}'"
            )
