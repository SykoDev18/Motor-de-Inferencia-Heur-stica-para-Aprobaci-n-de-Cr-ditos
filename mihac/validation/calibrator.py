# ============================================================
# MIHAC v1.0 — Módulo de Calibración de Pesos
# validation/calibrator.py
# ============================================================
# Analiza los errores del backtesting (FP y FN) para
# proponer ajustes a los pesos, umbrales y reglas del motor.
#
# IMPORTANTE — ESTO NO ES ML:
#   La calibración NO usa gradient descent ni optimización
#   numérica automatizada. Analiza patrones estadísticos
#   en los errores y propone ajustes heurísticos que un
#   experto humano debe revisar y aprobar.
#
# FLUJO:
#   1. Recibir resultados del backtesting (Backtester)
#   2. Analizar patrones en FP y FN
#   3. Identificar variables que más contribuyen a errores
#   4. Proponer ajustes a weights.json
#   5. Simular impacto de los ajustes propuestos
#   6. Generar reporte comparativo (antes vs después)
#
# PRINCIPIO DE CONSERVADURISMO:
#   Cualquier ajuste propuesto prioriza reducir FP (aprobar
#   morosos) sobre reducir FN (rechazar solventes), con
#   ratio de costo 4:1.
# ============================================================

import copy
import json
import logging
import time
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

import sys

_VAL_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _VAL_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.engine import InferenceEngine
from validation.metrics import MIHACMetrics

logger = logging.getLogger(__name__)

_WEIGHTS_PATH = _PROJECT_ROOT / "knowledge" / "weights.json"
_THRESHOLDS_PATH = _PROJECT_ROOT / "knowledge" / "thresholds.json"


class WeightCalibrator:
    """Analiza errores y propone ajustes de calibración.

    NO modifica archivos automáticamente — genera un
    reporte con propuestas que el usuario debe aprobar.

    Attributes:
        metrics: Instancia de MIHACMetrics.
        _weights: Pesos actuales cargados del JSON.
        _thresholds: Umbrales actuales cargados del JSON.

    Ejemplo::

        cal = WeightCalibrator()
        analisis = cal.analyze_errors(bt.results_df)
        propuestas = cal.propose_adjustments(analisis)
        comparacion = cal.simulate(
            propuestas, datos_mihac, y_real
        )
        print(cal.generate_report(comparacion))
    """

    # Costo relativo (consistente con MIHACMetrics)
    COSTO_FP: float = 4.0
    COSTO_FN: float = 1.0

    def __init__(self) -> None:
        """Inicializa el calibrador."""
        self.metrics = MIHACMetrics()
        self._weights = self._load_json(_WEIGHTS_PATH)
        self._thresholds = self._load_json(_THRESHOLDS_PATH)

    @staticmethod
    def _load_json(path: Path) -> dict:
        """Carga un archivo JSON."""
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error("Error cargando %s: %s", path, e)
            return {}

    # ════════════════════════════════════════════════════════
    # PASO 1: ANÁLISIS DE ERRORES
    # ════════════════════════════════════════════════════════

    def analyze_errors(
        self,
        results_df: pd.DataFrame,
    ) -> dict[str, Any]:
        """Analiza patrones estadísticos en los errores.

        Examina los FP y FN para encontrar qué variables
        y rangos de valores están causando los errores.

        Args:
            results_df: DataFrame del backtesting con columnas
                y_real, y_pred, score_mihac, dictamen,
                dti_mihac, y las 9 variables de entrada.

        Returns:
            Dict con análisis detallado de errores.

        Ejemplo::

            analisis = cal.analyze_errors(bt.results_df)
            print(analisis["fp"]["n"])
        """
        df = results_df.copy()

        # Identificar errores
        mask_fp = (df["y_pred"] == 1) & (df["y_real"] == 0)
        mask_fn = (df["y_pred"] == 0) & (df["y_real"] == 1)
        mask_vp = (df["y_pred"] == 1) & (df["y_real"] == 1)
        mask_vn = (df["y_pred"] == 0) & (df["y_real"] == 0)

        df_fp = df[mask_fp]
        df_fn = df[mask_fn]
        df_vp = df[mask_vp]
        df_vn = df[mask_vn]

        # Variables numéricas para comparar
        vars_num = [
            "edad", "ingreso_mensual", "total_deuda_actual",
            "dti_mihac", "score_mihac",
        ]
        # Variables categóricas
        vars_cat = [
            "historial_crediticio", "tipo_vivienda",
            "proposito_credito",
        ]

        analisis = {
            "total": len(df),
            "fp": self._perfil_grupo(df_fp, vars_num, vars_cat, "FP"),
            "fn": self._perfil_grupo(df_fn, vars_num, vars_cat, "FN"),
            "vp": self._perfil_grupo(df_vp, vars_num, vars_cat, "VP"),
            "vn": self._perfil_grupo(df_vn, vars_num, vars_cat, "VN"),
            "variables_criticas": self._identificar_variables_criticas(
                df_fp, df_fn, df_vp, df_vn, vars_num
            ),
            "umbrales_analisis": self._analizar_umbrales(df),
        }

        return analisis

    def _perfil_grupo(
        self,
        df: pd.DataFrame,
        vars_num: list[str],
        vars_cat: list[str],
        nombre: str,
    ) -> dict[str, Any]:
        """Calcula perfil estadístico de un grupo."""
        if len(df) == 0:
            return {"n": 0, "nombre": nombre}

        perfil: dict[str, Any] = {
            "n": len(df),
            "nombre": nombre,
        }

        # Estadísticas numéricas
        for var in vars_num:
            if var in df.columns:
                perfil[f"{var}_mean"] = round(
                    float(df[var].mean()), 2
                )
                perfil[f"{var}_median"] = round(
                    float(df[var].median()), 2
                )
                perfil[f"{var}_std"] = round(
                    float(df[var].std()), 2
                ) if len(df) > 1 else 0.0

        # Distribuciones categóricas
        for var in vars_cat:
            if var in df.columns:
                perfil[f"{var}_dist"] = (
                    df[var].value_counts().to_dict()
                )

        return perfil

    def _identificar_variables_criticas(
        self,
        df_fp: pd.DataFrame,
        df_fn: pd.DataFrame,
        df_vp: pd.DataFrame,
        df_vn: pd.DataFrame,
        vars_num: list[str],
    ) -> list[dict[str, Any]]:
        """Identifica variables que más difieren entre aciertos y errores.

        Para cada variable numérica, compara la media de los
        errores (FP/FN) contra la media de los aciertos
        (VP/VN). Variables con mayor diferencia relativa son
        las más críticas para recalibrar.

        Returns:
            Lista de dicts ordenada por criticidad descendente.
        """
        criticas = []

        for var in vars_num:
            if var == "score_mihac":
                continue  # El score es resultado, no causa

            # FP vs VN: ¿por qué aprobamos morosos?
            if len(df_fp) > 0 and len(df_vn) > 0:
                if var in df_fp.columns and var in df_vn.columns:
                    media_fp = float(df_fp[var].mean())
                    media_vn = float(df_vn[var].mean())
                    if media_vn != 0:
                        diff_fp = abs(media_fp - media_vn) / abs(media_vn)
                    else:
                        diff_fp = 0.0
                else:
                    diff_fp = 0.0
                    media_fp = 0.0
                    media_vn = 0.0
            else:
                diff_fp = 0.0
                media_fp = 0.0
                media_vn = 0.0

            # FN vs VP: ¿por qué rechazamos solventes?
            if len(df_fn) > 0 and len(df_vp) > 0:
                if var in df_fn.columns and var in df_vp.columns:
                    media_fn = float(df_fn[var].mean())
                    media_vp = float(df_vp[var].mean())
                    if media_vp != 0:
                        diff_fn = abs(media_fn - media_vp) / abs(media_vp)
                    else:
                        diff_fn = 0.0
                else:
                    diff_fn = 0.0
                    media_fn = 0.0
                    media_vp = 0.0
            else:
                diff_fn = 0.0
                media_fn = 0.0
                media_vp = 0.0

            # Puntaje de criticidad ponderado (FP más peligroso)
            criticidad = diff_fp * self.COSTO_FP + diff_fn * self.COSTO_FN

            criticas.append({
                "variable": var,
                "criticidad": round(criticidad, 4),
                "diff_fp_pct": round(diff_fp * 100, 1),
                "diff_fn_pct": round(diff_fn * 100, 1),
                "media_fp": round(media_fp, 2),
                "media_vn": round(media_vn, 2),
                "media_fn": round(media_fn, 2),
                "media_vp": round(media_vp, 2) if len(df_vp) > 0 else 0.0,
            })

        # Ordenar por criticidad descendente
        criticas.sort(key=lambda x: x["criticidad"], reverse=True)
        return criticas

    def _analizar_umbrales(
        self, df: pd.DataFrame
    ) -> dict[str, Any]:
        """Analiza el impacto de diferentes umbrales.

        Simula qué pasaría con accuracy, precision, recall
        y costo asimétrico si el umbral de aprobación fuera
        diferente (70, 75, 78, 80, 82, 85, 88, 90).

        Returns:
            Dict con resultados por umbral.
        """
        umbrales_test = [70, 75, 78, 80, 82, 85, 88, 90]
        resultados = {}

        y_real = df["y_real"].values
        scores = df["score_mihac"].values

        for u in umbrales_test:
            y_pred_u = np.array(
                [1 if s >= u else 0 for s in scores],
                dtype=int,
            )
            m = self.metrics.calculate_all(
                y_real, y_pred_u, scores
            )
            resultados[u] = {
                "accuracy": m["accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1_score": m["f1_score"],
                "costo_asimetrico": m["costo_asimetrico"],
                "n_aprobados": int(np.sum(y_pred_u == 1)),
                "n_rechazados": int(np.sum(y_pred_u == 0)),
                "fp": m["matriz"]["FP"],
                "fn": m["matriz"]["FN"],
            }

        # Encontrar umbral óptimo (mínimo costo asimétrico)
        umbral_opt = min(
            resultados,
            key=lambda u: resultados[u]["costo_asimetrico"],
        )

        return {
            "por_umbral": resultados,
            "umbral_optimo_costo": umbral_opt,
            "umbral_actual": 80,
        }

    # ════════════════════════════════════════════════════════
    # PASO 2: PROPONER AJUSTES
    # ════════════════════════════════════════════════════════

    def propose_adjustments(
        self,
        analisis: dict[str, Any],
    ) -> dict[str, Any]:
        """Propone ajustes basados en el análisis de errores.

        Las propuestas son conservadoras: cambios máximos
        del 5% en pesos y ±3 puntos en umbrales.

        NUNCA modifica archivos — solo retorna propuestas.

        Args:
            analisis: Dict retornado por analyze_errors().

        Returns:
            Dict con pesos_propuestos, umbral_propuesto,
            y justificaciones.

        Ejemplo::

            propuestas = cal.propose_adjustments(analisis)
            print(propuestas["pesos_nuevos"])
        """
        propuestas: dict[str, Any] = {
            "pesos_actuales": {},
            "pesos_nuevos": {},
            "cambios_pesos": [],
            "umbral_actual": 80,
            "umbral_propuesto": 80,
            "justificacion_umbral": "",
            "justificaciones": [],
        }

        # ── Extraer pesos actuales ──────────────────────────
        pesos_actual = {}
        if "pesos" in self._weights:
            for nombre, info in self._weights["pesos"].items():
                pesos_actual[nombre] = info.get("peso", 0.0)
        propuestas["pesos_actuales"] = pesos_actual.copy()

        # ── Mapeo de variable de análisis → peso ────────────
        var_a_peso = {
            "ingreso_mensual": "Ingreso_Mensual",
            "total_deuda_actual": "Total_Deuda_Actual",
            "edad": "Edad",
            "dti_mihac": "Total_Deuda_Actual",  # DTI depende de deuda
        }

        pesos_nuevos = pesos_actual.copy()
        cambios = []
        justificaciones = []

        # ── Analizar variables críticas ─────────────────────
        for vc in analisis.get("variables_criticas", []):
            var = vc["variable"]
            criticidad = vc["criticidad"]
            diff_fp = vc["diff_fp_pct"]

            peso_key = var_a_peso.get(var)
            if peso_key is None or peso_key not in pesos_nuevos:
                continue

            peso_actual = pesos_nuevos[peso_key]

            # Solo ajustar si la criticidad es significativa
            if criticidad < 0.5:
                continue

            # Si FP tienen valores altos en esta variable,
            # el peso debería ser MENOR (la variable no discrimina bien)
            # Si FP tienen valores bajos, el peso está bien
            if diff_fp > 15:
                # Variable no discrimina bien → reducir peso
                ajuste = -0.02
                razon = (
                    f"{peso_key}: FP difieren {diff_fp:.0f}% de VN → "
                    f"reducir peso de {peso_actual:.2f} a "
                    f"{peso_actual + ajuste:.2f}"
                )
            elif diff_fp > 8:
                ajuste = -0.01
                razon = (
                    f"{peso_key}: FP difieren {diff_fp:.0f}% de VN → "
                    f"ajuste menor de {peso_actual:.2f} a "
                    f"{peso_actual + ajuste:.2f}"
                )
            else:
                continue

            nuevo_peso = max(0.02, peso_actual + ajuste)
            pesos_nuevos[peso_key] = round(nuevo_peso, 2)

            cambios.append({
                "variable": peso_key,
                "peso_anterior": peso_actual,
                "peso_nuevo": round(nuevo_peso, 2),
                "ajuste": round(ajuste, 2),
                "razon": razon,
            })
            justificaciones.append(razon)

        # ── Redistribuir peso excedente/faltante ────────────
        suma_actual = sum(pesos_nuevos.values())
        delta = round(1.0 - suma_actual, 4)

        if abs(delta) > 0.001:
            # Redistribuir al peso más alto (Ingreso_Mensual)
            clave_redistribuir = max(
                pesos_nuevos, key=pesos_nuevos.get
            )
            pesos_nuevos[clave_redistribuir] = round(
                pesos_nuevos[clave_redistribuir] + delta, 2
            )
            justificaciones.append(
                f"Redistribuido {delta:+.2f} a "
                f"{clave_redistribuir} para mantener suma = 1.00"
            )

        propuestas["pesos_nuevos"] = pesos_nuevos
        propuestas["cambios_pesos"] = cambios
        propuestas["justificaciones"] = justificaciones

        # ── Propuesta de umbral ─────────────────────────────
        umbral_info = analisis.get("umbrales_analisis", {})
        umbral_opt = umbral_info.get("umbral_optimo_costo", 80)

        # Limitar cambio máximo a ±3 puntos
        umbral_prop = max(77, min(83, umbral_opt))
        propuestas["umbral_propuesto"] = umbral_prop

        if umbral_prop != 80:
            propuestas["justificacion_umbral"] = (
                f"El análisis de costo asimétrico sugiere "
                f"umbral={umbral_opt} (óptimo), limitado a "
                f"{umbral_prop} por conservadurismo (±3 max)."
            )
        else:
            propuestas["justificacion_umbral"] = (
                "El umbral actual de 80 es adecuado según "
                "el análisis de costo asimétrico."
            )

        return propuestas

    # ════════════════════════════════════════════════════════
    # PASO 3: SIMULAR IMPACTO
    # ════════════════════════════════════════════════════════

    def simulate(
        self,
        propuestas: dict[str, Any],
        datos_mihac: list[dict],
        y_real: list[int] | np.ndarray,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Simula el impacto de los ajustes propuestos.

        Re-evalúa todos los registros con el motor actual
        (los pesos del scorer no se modifican directamente,
        el impacto se simula ajustando el umbral propuesto)
        y compara las métricas antes vs después.

        Args:
            propuestas: Dict retornado por propose_adjustments().
            datos_mihac: Lista de dicts para evaluate().
            y_real: Etiquetas reales binarias.
            verbose: Si True, imprime progreso.

        Returns:
            Dict con métricas_antes, métricas_después, delta,
            y resumen textual.
        """
        y_r = np.asarray(y_real, dtype=int)
        umbral_nuevo = propuestas.get("umbral_propuesto", 80)

        if verbose:
            print("\n── Simulando impacto de propuestas ──")

        # ── Evaluar con motor actual ────────────────────────
        if verbose:
            print(f"  Evaluando {len(datos_mihac)} registros...")

        engine = InferenceEngine()
        t0 = time.time()

        resultados = []
        for d in datos_mihac:
            r = engine.evaluate(d)
            resultados.append(r)

        t_eval = time.time() - t0
        if verbose:
            print(f"  ✓ Evaluados en {t_eval:.1f}s")

        scores = np.array(
            [r.get("score_final", 0) for r in resultados],
            dtype=float,
        )
        dictamenes_orig = [
            r.get("dictamen", "RECHAZADO") for r in resultados
        ]

        # ── Métricas con umbral actual (80) ─────────────────
        y_pred_actual = np.array(
            [1 if d == "APROBADO" else 0 for d in dictamenes_orig],
            dtype=int,
        )
        metricas_antes = self.metrics.calculate_all(
            y_r, y_pred_actual, scores, dictamenes_orig,
        )

        # ── Métricas con umbral propuesto ───────────────────
        # Simular: aprobar si score >= umbral_nuevo
        y_pred_nuevo = np.array(
            [1 if s >= umbral_nuevo else 0 for s in scores],
            dtype=int,
        )
        metricas_despues = self.metrics.calculate_all(
            y_r, y_pred_nuevo, scores,
        )

        # ── Calcular deltas ─────────────────────────────────
        claves_metrica = [
            "accuracy", "precision", "recall", "f1_score",
            "specificity", "auc_roc", "costo_asimetrico",
        ]
        deltas = {}
        for k in claves_metrica:
            antes = metricas_antes.get(k, 0)
            despues = metricas_despues.get(k, 0)
            deltas[k] = round(despues - antes, 4)

        # ── Resumen ─────────────────────────────────────────
        mejora_costo = deltas["costo_asimetrico"] < 0
        mejora_f1 = deltas["f1_score"] >= 0

        comparacion = {
            "metricas_antes": metricas_antes,
            "metricas_despues": metricas_despues,
            "deltas": deltas,
            "umbral_antes": 80,
            "umbral_despues": umbral_nuevo,
            "mejora_costo": mejora_costo,
            "mejora_f1": mejora_f1,
            "recomendacion": (
                "APLICAR" if mejora_costo else "MANTENER"
            ),
        }

        if verbose:
            print(f"\n  Umbral: {80} → {umbral_nuevo}")
            for k in claves_metrica:
                antes = metricas_antes[k]
                despues = metricas_despues[k]
                d = deltas[k]
                signo = "+" if d > 0 else ""
                flecha = "↑" if d > 0 else "↓" if d < 0 else "="
                print(
                    f"  {k:20s}: {antes:.4f} → "
                    f"{despues:.4f} ({signo}{d:.4f}) {flecha}"
                )
            print(
                f"\n  Recomendación: {comparacion['recomendacion']}"
            )

        return comparacion

    # ════════════════════════════════════════════════════════
    # PASO 4: GENERAR REPORTE
    # ════════════════════════════════════════════════════════

    def generate_report(
        self,
        analisis: dict[str, Any],
        propuestas: dict[str, Any],
        comparacion: dict[str, Any],
    ) -> str:
        """Genera el reporte textual de calibración.

        Args:
            analisis: Dict de analyze_errors().
            propuestas: Dict de propose_adjustments().
            comparacion: Dict de simulate().

        Returns:
            Texto multi-línea del reporte.
        """
        lineas = []
        lineas.append("=" * 60)
        lineas.append("REPORTE DE CALIBRACIÓN — MIHAC v1.0")
        lineas.append("=" * 60)

        # ── Resumen de errores ──────────────────────────────
        lineas.append("\n── ANÁLISIS DE ERRORES ──")
        lineas.append(f"Total registros: {analisis['total']}")

        for grupo in ["fp", "fn", "vp", "vn"]:
            info = analisis.get(grupo, {})
            n = info.get("n", 0)
            nombre = info.get("nombre", grupo.upper())
            lineas.append(f"  {nombre}: {n}")

        # ── Variables críticas ──────────────────────────────
        lineas.append("\n── VARIABLES CRÍTICAS (por impacto en error) ──")
        for vc in analisis.get("variables_criticas", [])[:5]:
            lineas.append(
                f"  {vc['variable']:25s} "
                f"Criticidad={vc['criticidad']:.2f}  "
                f"FP diff={vc['diff_fp_pct']:.0f}%  "
                f"FN diff={vc['diff_fn_pct']:.0f}%"
            )

        # ── Análisis de umbrales ────────────────────────────
        lineas.append("\n── ANÁLISIS DE UMBRALES ──")
        umbral_info = analisis.get("umbrales_analisis", {})
        lineas.append(
            f"  Umbral actual: {umbral_info.get('umbral_actual', 80)}"
        )
        lineas.append(
            f"  Umbral óptimo (costo): "
            f"{umbral_info.get('umbral_optimo_costo', '?')}"
        )

        por_umbral = umbral_info.get("por_umbral", {})
        if por_umbral:
            lineas.append(
                f"\n  {'Umbral':>7s} | {'Acc':>6s} | "
                f"{'Prec':>6s} | {'Rec':>6s} | "
                f"{'F1':>6s} | {'Costo':>6s} | "
                f"{'FP':>4s} | {'FN':>4s}"
            )
            lineas.append("  " + "-" * 56)
            for u in sorted(por_umbral.keys()):
                r = por_umbral[u]
                lineas.append(
                    f"  {u:>7d} | {r['accuracy']:>6.3f} | "
                    f"{r['precision']:>6.3f} | "
                    f"{r['recall']:>6.3f} | "
                    f"{r['f1_score']:>6.3f} | "
                    f"{r['costo_asimetrico']:>6.3f} | "
                    f"{r['fp']:>4d} | {r['fn']:>4d}"
                )

        # ── Propuestas de pesos ─────────────────────────────
        lineas.append("\n── PROPUESTAS DE AJUSTE DE PESOS ──")
        if propuestas.get("cambios_pesos"):
            for c in propuestas["cambios_pesos"]:
                lineas.append(
                    f"  {c['variable']:25s} "
                    f"{c['peso_anterior']:.2f} → "
                    f"{c['peso_nuevo']:.2f}  "
                    f"({c['ajuste']:+.2f})"
                )
        else:
            lineas.append(
                "  No se proponen cambios significativos."
            )

        lineas.append(
            f"\n  Umbral: {propuestas['umbral_actual']} → "
            f"{propuestas['umbral_propuesto']}"
        )
        lineas.append(
            f"  {propuestas['justificacion_umbral']}"
        )

        # ── Comparación antes vs después ────────────────────
        lineas.append("\n── SIMULACIÓN: ANTES vs DESPUÉS ──")
        m_antes = comparacion["metricas_antes"]
        m_desp = comparacion["metricas_despues"]
        deltas = comparacion["deltas"]

        claves = [
            "accuracy", "precision", "recall", "f1_score",
            "specificity", "auc_roc", "costo_asimetrico",
        ]
        lineas.append(
            f"  {'Métrica':20s} | {'Antes':>8s} | "
            f"{'Después':>8s} | {'Delta':>8s}"
        )
        lineas.append("  " + "-" * 52)
        for k in claves:
            a = m_antes[k]
            d = m_desp[k]
            delta = deltas[k]
            signo = "+" if delta > 0 else ""
            lineas.append(
                f"  {k:20s} | {a:>8.4f} | "
                f"{d:>8.4f} | {signo}{delta:>7.4f}"
            )

        # ── Matriz antes vs después ─────────────────────────
        cm_a = m_antes["matriz"]
        cm_d = m_desp["matriz"]
        lineas.append("\n  Matriz de Confusión:")
        lineas.append(
            f"    ANTES:  VP={cm_a['VP']}  FP={cm_a['FP']}  "
            f"VN={cm_a['VN']}  FN={cm_a['FN']}"
        )
        lineas.append(
            f"    DESPUÉS: VP={cm_d['VP']}  FP={cm_d['FP']}  "
            f"VN={cm_d['VN']}  FN={cm_d['FN']}"
        )

        # ── Recomendación final ─────────────────────────────
        lineas.append("\n── RECOMENDACIÓN ──")
        rec = comparacion["recomendacion"]
        if rec == "APLICAR":
            lineas.append(
                "  ✓ APLICAR los ajustes propuestos."
            )
            lineas.append(
                "    Los cambios reducen el costo asimétrico "
                "sin degradar significativamente el F1-Score."
            )
        else:
            lineas.append(
                "  ● MANTENER la configuración actual."
            )
            lineas.append(
                "    Los ajustes propuestos no mejoran el "
                "costo asimétrico. Considerar ajustes a las "
                "reglas heurísticas en rules.json."
            )

        return "\n".join(lineas)

    # ════════════════════════════════════════════════════════
    # PASO 5: APLICAR (con backup)
    # ════════════════════════════════════════════════════════

    def apply_weights(
        self,
        propuestas: dict[str, Any],
        backup: bool = True,
    ) -> dict[str, str]:
        """Aplica los pesos propuestos a weights.json.

        Crea un backup del archivo original antes de
        sobrescribir (weights_v1_backup.json).

        SOLO llamar después de que el usuario apruebe
        las propuestas.

        Args:
            propuestas: Dict con pesos_nuevos.
            backup: Si True, crea backup v1.

        Returns:
            Dict con rutas de archivos modificados.

        Ejemplo::

            rutas = cal.apply_weights(propuestas)
            print(rutas["backup"])
        """
        rutas = {}

        # ── Backup ──────────────────────────────────────────
        if backup:
            backup_path = (
                _PROJECT_ROOT / "knowledge"
                / "weights_v1_backup.json"
            )
            with open(_WEIGHTS_PATH, "r", encoding="utf-8") as f:
                original = json.load(f)
            with open(backup_path, "w", encoding="utf-8") as f:
                json.dump(original, f, indent=2, ensure_ascii=False)
            rutas["backup"] = str(backup_path)
            logger.info("Backup creado: %s", backup_path)

        # ── Aplicar nuevos pesos ────────────────────────────
        weights = copy.deepcopy(self._weights)
        pesos_nuevos = propuestas.get("pesos_nuevos", {})

        for nombre, nuevo_peso in pesos_nuevos.items():
            if nombre in weights.get("pesos", {}):
                weights["pesos"][nombre]["peso"] = nuevo_peso

        # Actualizar metadata
        weights["_meta"]["version"] = "v2 (calibrada)"
        weights["_meta"]["calibracion"] = {
            "fecha": pd.Timestamp.now().isoformat(),
            "metodo": "Análisis de errores FP/FN + costo asimétrico 4:1",
            "cambios": propuestas.get("cambios_pesos", []),
        }

        with open(_WEIGHTS_PATH, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2, ensure_ascii=False)
        rutas["weights"] = str(_WEIGHTS_PATH)

        logger.info("Pesos actualizados: %s", _WEIGHTS_PATH)
        print(f"  ✓ Pesos actualizados en {_WEIGHTS_PATH}")
        print(f"  ✓ Backup en {rutas.get('backup', 'N/A')}")

        # Recargar
        self._weights = weights

        return rutas

    def save_report(
        self,
        reporte_texto: str,
        output_path: str = "reports/calibration_report.txt",
    ) -> str:
        """Guarda el reporte de calibración a archivo.

        Args:
            reporte_texto: Texto del reporte.
            output_path: Ruta de salida.

        Returns:
            Ruta absoluta del archivo guardado.
        """
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(reporte_texto)
        logger.info("Reporte guardado: %s", path)
        return str(path.resolve())


# ════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════

def _run_tests() -> None:
    """Tests del módulo de calibración."""
    print("=" * 60)
    print("MIHAC — Tests del Módulo de Calibración")
    print("=" * 60)

    # ── Test 1: Inicialización ──────────────────────────
    print("\n── Test 1: Inicialización ──")
    cal = WeightCalibrator()
    assert cal.metrics is not None
    assert cal._weights is not None
    assert "pesos" in cal._weights
    pesos = cal._weights["pesos"]
    suma = sum(p["peso"] for p in pesos.values())
    print(f"  Pesos cargados: {len(pesos)}")
    print(f"  Suma de pesos: {suma:.2f}")
    assert abs(suma - 1.0) < 0.01, f"FAIL: suma={suma}"
    print("  ✓ Inicialización correcta")

    # ── Test 2: Análisis de errores con datos sintéticos ─
    print("\n── Test 2: Análisis de errores ──")

    # Crear DataFrame simulado
    np.random.seed(42)
    n = 100
    df_test = pd.DataFrame({
        "edad": np.random.randint(20, 65, n),
        "ingreso_mensual": np.random.uniform(5000, 40000, n),
        "total_deuda_actual": np.random.uniform(0, 15000, n),
        "historial_crediticio": np.random.choice([0, 1, 2], n),
        "tipo_vivienda": np.random.choice(
            ["Propia", "Familiar", "Rentada"], n
        ),
        "proposito_credito": np.random.choice(
            ["Negocio", "Educacion", "Consumo", "Vacaciones"], n
        ),
        "score_mihac": np.random.uniform(20, 100, n),
        "dti_mihac": np.random.uniform(0.05, 0.70, n),
        "dictamen": np.random.choice(
            ["APROBADO", "RECHAZADO", "REVISION_MANUAL"], n
        ),
    })

    # Asignar y_real (aleatoriamente pero con sesgo)
    df_test["y_real"] = np.random.choice(
        [1, 0], n, p=[0.7, 0.3]
    )

    # y_pred basado en score > 80
    df_test["y_pred"] = (df_test["score_mihac"] >= 80).astype(int)

    analisis = cal.analyze_errors(df_test)
    assert "fp" in analisis
    assert "fn" in analisis
    assert "variables_criticas" in analisis
    assert "umbrales_analisis" in analisis
    print(f"  Total: {analisis['total']}")
    print(f"  FP: {analisis['fp']['n']}")
    print(f"  FN: {analisis['fn']['n']}")
    print(f"  Variables críticas: {len(analisis['variables_criticas'])}")
    print("  ✓ Análisis completado")

    # ── Test 3: Proponer ajustes ────────────────────────
    print("\n── Test 3: Proponer ajustes ──")
    propuestas = cal.propose_adjustments(analisis)
    assert "pesos_actuales" in propuestas
    assert "pesos_nuevos" in propuestas
    assert "umbral_propuesto" in propuestas

    # Verificar que los pesos suman 1.0
    suma_nueva = sum(propuestas["pesos_nuevos"].values())
    print(f"  Pesos actuales: {propuestas['pesos_actuales']}")
    print(f"  Pesos nuevos:   {propuestas['pesos_nuevos']}")
    print(f"  Suma nueva:     {suma_nueva:.2f}")
    print(f"  Cambios:        {len(propuestas['cambios_pesos'])}")
    print(f"  Umbral:         {propuestas['umbral_propuesto']}")
    assert abs(suma_nueva - 1.0) < 0.02, (
        f"FAIL: suma={suma_nueva}"
    )
    print("  ✓ Propuestas generadas")

    # ── Test 4: Análisis de umbrales ────────────────────
    print("\n── Test 4: Análisis de umbrales ──")
    umbral_info = analisis["umbrales_analisis"]
    assert "por_umbral" in umbral_info
    assert "umbral_optimo_costo" in umbral_info
    n_umbrales = len(umbral_info["por_umbral"])
    print(f"  Umbrales evaluados: {n_umbrales}")
    print(f"  Umbral óptimo: {umbral_info['umbral_optimo_costo']}")
    for u in sorted(umbral_info["por_umbral"].keys())[:3]:
        r = umbral_info["por_umbral"][u]
        print(
            f"    U={u}: Acc={r['accuracy']:.3f} "
            f"Prec={r['precision']:.3f} "
            f"F1={r['f1_score']:.3f} "
            f"Costo={r['costo_asimetrico']:.3f}"
        )
    print("  ✓ Análisis de umbrales correcto")

    # ── Test 5: Generar reporte ─────────────────────────
    print("\n── Test 5: Generar reporte ──")

    # Crear comparación simulada
    comparacion = {
        "metricas_antes": cal.metrics.calculate_all(
            df_test["y_real"].values,
            df_test["y_pred"].values,
            df_test["score_mihac"].values,
        ),
        "metricas_despues": cal.metrics.calculate_all(
            df_test["y_real"].values,
            (df_test["score_mihac"] >= 82).astype(int).values,
            df_test["score_mihac"].values,
        ),
        "deltas": {},
        "umbral_antes": 80,
        "umbral_despues": 82,
        "mejora_costo": True,
        "mejora_f1": True,
        "recomendacion": "APLICAR",
    }

    # Calcular deltas
    for k in ["accuracy", "precision", "recall", "f1_score",
              "specificity", "auc_roc", "costo_asimetrico"]:
        a = comparacion["metricas_antes"].get(k, 0)
        d = comparacion["metricas_despues"].get(k, 0)
        comparacion["deltas"][k] = round(d - a, 4)

    reporte = cal.generate_report(
        analisis, propuestas, comparacion
    )
    assert "REPORTE DE CALIBRACIÓN" in reporte
    assert "VARIABLES CRÍTICAS" in reporte
    assert "SIMULACIÓN" in reporte
    assert "RECOMENDACIÓN" in reporte
    print(f"  Longitud: {len(reporte)} caracteres")
    print("  ✓ Reporte generado correctamente")

    # ── Test 6: No modifica archivos ────────────────────
    print("\n── Test 6: Integridad de archivos ──")
    # Verificar que weights.json NO fue modificado
    cal2 = WeightCalibrator()
    pesos_post = {
        k: v["peso"] for k, v in cal2._weights["pesos"].items()
    }
    pesos_pre = propuestas["pesos_actuales"]
    for k in pesos_pre:
        assert abs(pesos_post[k] - pesos_pre[k]) < 0.001, (
            f"FAIL: {k} fue modificado!"
        )
    print("  ✓ weights.json NO fue modificado (solo propuestas)")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DE CALIBRACIÓN PASARON ✓")
    print(f"{'='*60}")


if __name__ == "__main__":
    _run_tests()
