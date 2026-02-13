# ============================================================
# MIHAC v1.0 — Generador de Explicaciones en Lenguaje Natural
# core/explainer.py
# ============================================================
# Traduce el resultado numérico del motor a un texto claro
# y profesional en español, apto para pantalla de analista
# y reportes PDF.
# ============================================================

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ── Mapeo de etiquetas ──────────────────────────────────────

_HISTORIAL_LABELS: dict[int, str] = {
    0: "Malo",
    1: "Neutro",
    2: "Bueno",
}

_DTI_INTERPRETACION: dict[str, str] = {
    "BAJO": (
        "Carga de deuda saludable. El solicitante tiene "
        "amplio margen para nuevas obligaciones."
    ),
    "MODERADO": (
        "Carga de deuda aceptable, pero con margen "
        "limitado para nuevas obligaciones."
    ),
    "ALTO": (
        "Carga de deuda elevada. La capacidad de pago "
        "está comprometida."
    ),
    "CRITICO": (
        "Sobreendeudamiento crítico. Más del 60% del "
        "ingreso se destina al servicio de deudas."
    ),
}

_SUGERENCIAS: dict[str, str] = {
    "R002": (
        "Establecer un historial crediticio positivo "
        "mediante pagos puntuales"
    ),
    "R004": (
        "Consolidar una mayor trayectoria laboral antes "
        "de solicitar crédito"
    ),
    "R008": (
        "Considerar un propósito de crédito productivo "
        "como negocio o educación"
    ),
    "R009": (
        "Construir un perfil financiero más maduro con "
        "el paso del tiempo"
    ),
    "R010": (
        "Incrementar el ingreso para compensar la carga "
        "familiar existente"
    ),
    "R014": (
        "Reducir las deudas vigentes antes de adquirir "
        "nuevas obligaciones financieras"
    ),
}


class Explainer:
    """Generador de reportes explicativos para MIHAC.

    Traduce métricas numéricas a texto en lenguaje natural
    para analistas de crédito y reportes de auditoría.

    Ejemplo de uso::

        exp = Explainer()
        texto = exp.generate(datos, resultado)
        resumen = exp.generate_short(datos, resultado)
    """

    # ────────────────────────────────────────────────────────
    # REPORTE COMPLETO
    # ────────────────────────────────────────────────────────

    def generate(
        self, datos: dict, resultado: dict
    ) -> str:
        """Genera el reporte explicativo completo.

        Args:
            datos: Diccionario con datos del solicitante.
            resultado: Dict con score, dictamen, sub_scores,
                reglas_activadas, dti_ratio, etc.

        Returns:
            String multi-línea con la explicación completa.

        Ejemplo::

            texto = explainer.generate(datos, resultado)
            print(texto)
        """
        try:
            linea = "─" * 55
            fecha = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            score = resultado.get("score_final", 0)
            dictamen = resultado.get("dictamen", "N/A")
            umbral = resultado.get("umbral_aplicado", 80)
            dti = resultado.get("dti_ratio", 0.0)
            dti_clasif = resultado.get(
                "dti_clasificacion", "N/A"
            )
            sub = resultado.get("sub_scores", {})
            reglas = resultado.get("reglas_activadas", [])
            ingreso = datos.get("ingreso_mensual", 0)
            deuda = datos.get("total_deuda_actual", 0)
            monto = datos.get("monto_credito", 0)

            secciones = []

            # ── Encabezado ──
            secciones.append(linea)
            secciones.append("EVALUACIÓN CREDITICIA MIHAC")
            secciones.append(f"Fecha: {fecha}")
            secciones.append(linea)
            secciones.append(f"DICTAMEN: {dictamen}")
            secciones.append(
                f"Score crediticio: {score}/100  |  "
                f"Umbral requerido: {umbral}"
            )
            secciones.append(linea)

            # ── Análisis de solvencia ──
            secciones.append("")
            secciones.append("ANÁLISIS DE SOLVENCIA")
            secciones.append(
                f"• Ingreso mensual declarado: "
                f"${ingreso:,.2f}"
            )
            secciones.append(
                f"• Deuda total vigente:       "
                f"${deuda:,.2f}"
            )
            interp = _DTI_INTERPRETACION.get(
                dti_clasif, ""
            )
            secciones.append(
                f"• DTI (Relación Deuda/Ingreso): "
                f"{dti:.1%} — {dti_clasif}"
            )
            secciones.append(f"  {interp}")

            # ── Desglose del score ──
            secciones.append("")
            secciones.append("DESGLOSE DEL SCORE")
            sol = sub.get("solvencia", 0)
            est = sub.get("estabilidad", 0)
            his = sub.get("historial_score", 0)
            per = sub.get("perfil", 0)

            barra_sol = self._build_progress_bar(sol, 40)
            barra_est = self._build_progress_bar(est, 30)
            barra_his = self._build_progress_bar(his, 20)
            barra_per = self._build_progress_bar(per, 10)

            secciones.append(
                f"  Solvencia    ({sol:>2}/40 pts): "
                f"{barra_sol}"
            )
            secciones.append(
                f"  Estabilidad  ({est:>2}/30 pts): "
                f"{barra_est}"
            )
            secciones.append(
                f"  Historial    ({his:>2}/20 pts): "
                f"{barra_his}"
            )
            secciones.append(
                f"  Perfil       ({per:>2}/10 pts): "
                f"{barra_per}"
            )

            # ── Factores determinantes ──
            secciones.append("")
            secciones.append("FACTORES DETERMINANTES")

            positivos = sorted(
                [r for r in reglas if r["impacto"] > 0],
                key=lambda x: x["impacto"],
                reverse=True,
            )
            negativos = sorted(
                [r for r in reglas if r["impacto"] < 0],
                key=lambda x: abs(x["impacto"]),
                reverse=True,
            )
            compensaciones = [
                r for r in reglas
                if r["tipo"] == "compensacion"
            ]

            secciones.append("  Positivos:")
            if positivos:
                for r in positivos:
                    secciones.append(
                        f"    ▲ {r['id']}: +{r['impacto']} — "
                        f"{r['descripcion']}"
                    )
            else:
                secciones.append(
                    "    No se identificaron factores "
                    "positivos relevantes."
                )

            secciones.append("  Negativos:")
            if negativos:
                for r in negativos:
                    secciones.append(
                        f"    ▼ {r['id']}: {r['impacto']} — "
                        f"{r['descripcion']}"
                    )
            else:
                secciones.append(
                    "    No se identificaron factores "
                    "negativos."
                )

            secciones.append(
                "  Compensaciones heurísticas activadas:"
            )
            if compensaciones:
                for r in compensaciones:
                    signo = "+" if r["impacto"] > 0 else ""
                    secciones.append(
                        f"    ⟳ {r['id']}: {signo}"
                        f"{r['impacto']} — {r['descripcion']}"
                    )
            else:
                secciones.append(
                    "    No se activaron compensaciones."
                )

            # ── Conclusión ──
            secciones.append("")
            secciones.append("CONCLUSIÓN")
            conclusion = self._generar_conclusion(
                datos, resultado, positivos, negativos
            )
            secciones.append(f"  {conclusion}")
            secciones.append(linea)

            return "\n".join(secciones)

        except Exception as e:
            logger.error(
                "Error generando explicación: %s", e
            )
            return (
                f"[Error al generar reporte: {e}]"
            )

    # ────────────────────────────────────────────────────────
    # REPORTE CORTO (una línea)
    # ────────────────────────────────────────────────────────

    def generate_short(
        self, datos: dict, resultado: dict
    ) -> str:
        """Genera un resumen de una sola línea.

        Args:
            datos: Diccionario con datos del solicitante.
            resultado: Dict con score, dictamen, dti, etc.

        Returns:
            String de una línea para tablas/logs.

        Ejemplo::

            linea = explainer.generate_short(datos, res)
            # "APROBADO | Score: 84 | DTI: 16.0% (BAJO)
            #  | Historial: Bueno | Propósito: Negocio"
        """
        dictamen = resultado.get("dictamen", "N/A")
        score = resultado.get("score_final", 0)
        dti = resultado.get("dti_ratio", 0.0)
        dti_c = resultado.get("dti_clasificacion", "N/A")

        hist_val = datos.get("historial_crediticio", -1)
        hist_label = _HISTORIAL_LABELS.get(
            hist_val, "Desconocido"
        )
        proposito = datos.get(
            "proposito_credito", "N/A"
        )

        return (
            f"{dictamen} | Score: {score} | "
            f"DTI: {dti:.1%} ({dti_c}) | "
            f"Historial: {hist_label} | "
            f"Propósito: {proposito}"
        )

    # ────────────────────────────────────────────────────────
    # BARRA DE PROGRESO ASCII
    # ────────────────────────────────────────────────────────

    def _build_progress_bar(
        self,
        valor: int,
        maximo: int,
        longitud: int = 15,
    ) -> str:
        """Genera una barra visual ASCII.

        Args:
            valor: Valor actual.
            maximo: Valor máximo posible.
            longitud: Caracteres totales de la barra.

        Returns:
            Barra tipo: ████████████░░░

        Ejemplo::

            barra = self._build_progress_bar(12, 20, 15)
            # "█████████░░░░░░"
        """
        if maximo <= 0:
            return "░" * longitud
        filled = int(longitud * valor / maximo)
        filled = max(0, min(filled, longitud))
        empty = longitud - filled
        return "█" * filled + "░" * empty

    # ────────────────────────────────────────────────────────
    # CONCLUSIÓN CONTEXTUAL
    # ────────────────────────────────────────────────────────

    def _generar_conclusion(
        self,
        datos: dict,
        resultado: dict,
        positivos: list[dict],
        negativos: list[dict],
    ) -> str:
        """Genera el texto de conclusión según dictamen.

        Args:
            datos: Datos del solicitante.
            resultado: Resultado de la evaluación.
            positivos: Reglas con impacto positivo.
            negativos: Reglas con impacto negativo.

        Returns:
            Texto de conclusión profesional.
        """
        dictamen = resultado.get("dictamen", "")
        score = resultado.get("score_final", 0)
        umbral = resultado.get("umbral_aplicado", 80)
        dti = resultado.get("dti_ratio", 0.0)
        dti_c = resultado.get("dti_clasificacion", "")
        monto = datos.get("monto_credito", 0)

        if dictamen == "APROBADO":
            factores = self._top_n_factores(positivos, 2)
            return (
                f"El perfil crediticio del solicitante "
                f"cumple con los criterios de aprobación "
                f"del sistema MIHAC. Los factores de "
                f"{factores} respaldan la capacidad y "
                f"voluntad de pago. Se recomienda proceder "
                f"con el desembolso por ${monto:,.2f} bajo "
                f"las condiciones estándar de la "
                f"institución."
            )

        if dictamen == "RECHAZADO" and dti_c == "CRITICO":
            meses = 12 if dti > 0.80 else 6
            return (
                f"Solicitud RECHAZADA por "
                f"sobreendeudamiento crítico. El "
                f"solicitante destina el {dti:.1%} de su "
                f"ingreso mensual al servicio de deudas "
                f"existentes, lo que supera el límite de "
                f"riesgo aceptable (60%). Agregar nuevas "
                f"obligaciones comprometería seriamente "
                f"su capacidad de pago. Se recomienda "
                f"revisar en {meses} meses si la situación "
                f"de deuda mejora."
            )

        if dictamen == "RECHAZADO":
            factores = self._top_n_factores(negativos, 2)
            sugerencias = self._obtener_sugerencias(
                negativos, 2
            )
            return (
                f"El perfil crediticio no alcanza el "
                f"umbral mínimo requerido ({umbral} "
                f"puntos). Los factores de mayor impacto "
                f"negativo fueron: {factores}. Para "
                f"mejorar el resultado en una futura "
                f"evaluación, se sugiere: {sugerencias}."
            )

        if dictamen == "REVISION_MANUAL":
            factor_principal = self._factor_incertidumbre(
                datos, resultado
            )
            rango_min = umbral - 20
            return (
                f"El solicitante se encuentra en zona de "
                f"análisis. Su score de {score} puntos "
                f"está dentro del rango de revisión "
                f"({rango_min}–{umbral}), lo que indica "
                f"un perfil con características mixtas "
                f"que requieren evaluación adicional por "
                f"parte de un analista humano. "
                f"{factor_principal}"
            )

        return "Dictamen no reconocido."

    def _top_n_factores(
        self, reglas: list[dict], n: int
    ) -> str:
        """Devuelve nombres de los top-N factores."""
        if not reglas:
            return "perfil general"
        top = reglas[:n]
        nombres = [r["descripcion"].lower() for r in top]
        if len(nombres) == 1:
            return nombres[0]
        return " y ".join(
            [", ".join(nombres[:-1]), nombres[-1]]
        ) if len(nombres) > 2 else " y ".join(nombres)

    def _obtener_sugerencias(
        self, negativos: list[dict], n: int
    ) -> str:
        """Genera sugerencias basadas en factores negativos."""
        sugs: list[str] = []
        for r in negativos[:n]:
            rid = r.get("id", "")
            sug = _SUGERENCIAS.get(rid)
            if sug:
                sugs.append(sug)

        if not sugs:
            sugs.append(
                "mejorar el perfil financiero general "
                "antes de una nueva solicitud"
            )
        return "; ".join(sugs)

    def _factor_incertidumbre(
        self, datos: dict, resultado: dict
    ) -> str:
        """Identifica el factor de incertidumbre principal."""
        hist = datos.get("historial_crediticio", -1)
        dti_c = resultado.get("dti_clasificacion", "")

        if hist == 1:
            return (
                "El factor principal de incertidumbre es "
                "el historial crediticio neutro, que no "
                "permite confirmar un patrón de "
                "cumplimiento."
            )
        if dti_c == "MODERADO":
            return (
                "El DTI moderado requiere verificación "
                "adicional de la capacidad de pago real "
                "del solicitante."
            )
        if dti_c == "ALTO":
            return (
                "El nivel de endeudamiento actual es "
                "elevado y requiere evaluación detallada "
                "de la capacidad de pago."
            )

        return (
            "Se recomienda solicitar documentación "
            "adicional para confirmar la capacidad "
            "de pago."
        )


# ════════════════════════════════════════════════════════════
# TESTS DEL EXPLAINER
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import sys
    from pathlib import Path

    _dir = Path(__file__).resolve().parent.parent
    if str(_dir) not in sys.path:
        sys.path.insert(0, str(_dir))

    from core.scorer import ScoringEngine

    print("=" * 60)
    print("MIHAC — Tests del Explainer")
    print("=" * 60)

    scorer = ScoringEngine()
    explainer = Explainer()

    casos = [
        {
            "nombre": "Cliente ideal (APROBADO)",
            "datos": {
                "edad": 35,
                "ingreso_mensual": 25000.0,
                "total_deuda_actual": 4000.0,
                "historial_crediticio": 2,
                "antiguedad_laboral": 7,
                "numero_dependientes": 1,
                "tipo_vivienda": "Propia",
                "proposito_credito": "Negocio",
                "monto_credito": 15000.0,
            },
        },
        {
            "nombre": "Alto riesgo (RECHAZADO)",
            "datos": {
                "edad": 19,
                "ingreso_mensual": 8000.0,
                "total_deuda_actual": 5500.0,
                "historial_crediticio": 0,
                "antiguedad_laboral": 0,
                "numero_dependientes": 3,
                "tipo_vivienda": "Rentada",
                "proposito_credito": "Vacaciones",
                "monto_credito": 12000.0,
            },
        },
        {
            "nombre": "Zona gris (REVISION_MANUAL)",
            "datos": {
                "edad": 28,
                "ingreso_mensual": 15000.0,
                "total_deuda_actual": 3000.0,
                "historial_crediticio": 1,
                "antiguedad_laboral": 2,
                "numero_dependientes": 1,
                "tipo_vivienda": "Familiar",
                "proposito_credito": "Consumo",
                "monto_credito": 10000.0,
            },
        },
    ]

    verificaciones = {
        "APROBADO": "recomienda proceder",
        "RECHAZADO": None,  # check negative factor
        "REVISION_MANUAL": "zona de análisis",
    }

    for caso in casos:
        datos = caso["datos"]
        nombre = caso["nombre"]

        dti, clasif = scorer.calculate_dti(
            datos["ingreso_mensual"],
            datos["total_deuda_actual"],
        )
        sub = scorer.calculate_subscores(datos, dti)
        reglas = scorer.apply_rules(datos, dti)
        score, umbral = scorer.calculate_final_score(
            sub, reglas, datos["monto_credito"]
        )
        dictamen = scorer.get_dictamen(
            score, umbral, clasif
        )

        resultado = {
            "score_final": score,
            "dti_ratio": dti,
            "dti_clasificacion": clasif,
            "sub_scores": sub,
            "dictamen": dictamen,
            "umbral_aplicado": umbral,
            "reglas_activadas": reglas,
            "compensaciones": [
                r for r in reglas
                if r["tipo"] == "compensacion"
            ],
            "errores_validacion": [],
        }

        texto = explainer.generate(datos, resultado)
        corto = explainer.generate_short(datos, resultado)

        print(f"\n{'═'*60}")
        print(f"CASO: {nombre}")
        print(f"{'═'*60}")
        print(texto)
        print(f"\nResumen: {corto}")

        # Verificaciones
        lineas = texto.split("\n")
        assert len(lineas) >= 20, (
            f"FAIL: texto muy corto ({len(lineas)} líneas)"
        )

        if dictamen == "APROBADO":
            assert "recomienda proceder" in texto, (
                "FAIL: APROBADO sin 'recomienda proceder'"
            )
        elif dictamen == "REVISION_MANUAL":
            assert "zona de análisis" in texto, (
                "FAIL: REVISION sin 'zona de análisis'"
            )
        elif dictamen == "RECHAZADO":
            negativos = [
                r for r in reglas if r["impacto"] < 0
            ]
            if negativos:
                assert "impacto negativo" in texto or \
                    "sobreendeudamiento" in texto, (
                    "FAIL: RECHAZADO sin mención negativa"
                )

        print(f"  ✓ Verificación PASS ({dictamen})")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DEL EXPLAINER PASARON ✓")
    print(f"{'='*60}")
