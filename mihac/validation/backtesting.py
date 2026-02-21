# ============================================================
# MIHAC v1.0 — Módulo de Backtesting
# validation/backtesting.py
# ============================================================
# Ejecuta el motor MIHAC sobre los 1,000 registros del
# German Credit Dataset, compara dictámenes contra
# etiquetas reales y genera métricas + reportes completos.
#
# PIPELINE DE 7 PASOS:
#   1. Cargar datos transformados (mapper.py)
#   2. Evaluar cada registro con InferenceEngine
#   3. Construir vectores y_real / y_pred / scores
#   4. Calcular métricas con MIHACMetrics
#   5. Generar visualizaciones con MIHACPlots
#   6. Análisis de errores (FP y FN desagregados)
#   7. Generar reporte resumen
#
# CONVENCIÓN DE ETIQUETAS:
#   German Credit: clase 1 = bueno, clase 2 = malo
#   MIHAC y_real:  1 = bueno (clase 1), 0 = malo (clase 2)
#   MIHAC y_pred:  1 = APROBADO, 0 = RECHAZADO o REVISION_MANUAL
# ============================================================

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd

# Asegurar que el proyecto raíz esté en sys.path
_VAL_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _VAL_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.engine import InferenceEngine
from data.mapper import GermanCreditMapper
from validation.metrics import MIHACMetrics, MIHACPlots

logger = logging.getLogger(__name__)


class Backtester:
    """Ejecuta backtesting completo del motor MIHAC.

    Toma el German Credit Dataset (1,000 registros), pasa
    cada uno por el motor de inferencia, y compara las
    decisiones contra las etiquetas reales para generar
    métricas de validación empírica.

    El pipeline es determinista y reproducible: mismos datos
    → mismos resultados.

    Attributes:
        engine: Instancia del InferenceEngine de MIHAC.
        metrics: Instancia de MIHACMetrics.
        plots: Instancia de MIHACPlots.
        results_df: DataFrame con resultados después de run().

    Ejemplo::

        bt = Backtester()
        reporte = bt.run("data/german.data")
        print(reporte["metricas"]["f1_score"])
        bt.save_report("reports/backtesting/")
    """

    def __init__(self) -> None:
        """Inicializa componentes del backtester."""
        self.engine = InferenceEngine()
        self.metrics = MIHACMetrics()
        self.plots = MIHACPlots()

        # Estado interno (poblado tras run())
        self.results_df: pd.DataFrame | None = None
        self._metricas: dict[str, Any] | None = None
        self._errores_fp: pd.DataFrame | None = None
        self._errores_fn: pd.DataFrame | None = None
        self._reporte: dict[str, Any] | None = None
        self._tiempo_total: float = 0.0

    # ════════════════════════════════════════════════════════
    # PIPELINE PRINCIPAL
    # ════════════════════════════════════════════════════════

    def run(
        self,
        data_path: str | None = None,
        verbose: bool = True,
    ) -> dict[str, Any]:
        """Ejecuta el pipeline completo de 7 pasos.

        Args:
            data_path: Ruta al archivo german.data.
                      Si None, intenta descargar de UCI.
            verbose: Si True, imprime progreso por consola.

        Returns:
            Dict con claves: metricas, errores_fp, errores_fn,
            interpretacion, stats_engine, tiempo_total_seg,
            n_registros, timestamp.

        Ejemplo::

            reporte = bt.run("data/german.data")
            print(reporte["metricas"]["accuracy"])
        """
        t0 = time.time()

        # ── PASO 1: Cargar datos ────────────────────────────
        if verbose:
            print("=" * 60)
            print("MIHAC — Backtesting con German Credit Dataset")
            print("=" * 60)
            print("\n[Paso 1/7] Cargando datos...")

        mapper = GermanCreditMapper()
        df = mapper.load_and_transform(data_path)
        n_total = len(df)

        if verbose:
            buenos = int((df["etiqueta_binaria"] == 1).sum())
            malos = n_total - buenos
            print(f"  ✓ {n_total} registros cargados")
            print(f"  Buenos pagadores: {buenos} ({buenos/n_total*100:.1f}%)")
            print(f"  Malos pagadores:  {malos} ({malos/n_total*100:.1f}%)")

        # ── PASO 2: Evaluar cada registro ───────────────────
        if verbose:
            print(f"\n[Paso 2/7] Evaluando {n_total} registros...")

        dicts_mihac = mapper.to_mihac_dicts(df)
        resultados = []
        t_eval_start = time.time()

        for i, datos in enumerate(dicts_mihac):
            resultado = self.engine.evaluate(datos)
            resultados.append(resultado)

            if verbose and (i + 1) % 200 == 0:
                elapsed = time.time() - t_eval_start
                rate = (i + 1) / elapsed
                print(
                    f"  ... {i+1}/{n_total} evaluados "
                    f"({rate:.0f} reg/seg)"
                )

        t_eval = time.time() - t_eval_start
        if verbose:
            print(
                f"  ✓ {n_total} evaluaciones completadas "
                f"en {t_eval:.1f}s "
                f"({n_total/t_eval:.0f} reg/seg)"
            )

        # ── PASO 3: Construir vectores ──────────────────────
        if verbose:
            print("\n[Paso 3/7] Construyendo vectores y_real / y_pred...")

        y_real = df["etiqueta_binaria"].values  # 1=bueno, 0=malo

        dictamenes = [r.get("dictamen", "RECHAZADO") for r in resultados]
        scores = [r.get("score_final", 0) for r in resultados]

        # REVISION_MANUAL → 0 (rechazo) para métricas binarias
        y_pred = np.array([
            1 if d == "APROBADO" else 0 for d in dictamenes
        ], dtype=int)

        # Construir DataFrame de resultados
        self.results_df = df.copy()
        self.results_df["score_mihac"] = scores
        self.results_df["dictamen"] = dictamenes
        self.results_df["y_pred"] = y_pred
        self.results_df["y_real"] = y_real

        # Agregar DTI calculado y reglas activadas
        self.results_df["dti_mihac"] = [
            r.get("dti_ratio", 0.0) for r in resultados
        ]
        self.results_df["dti_clasificacion"] = [
            r.get("dti_clasificacion", "N/A") for r in resultados
        ]
        self.results_df["n_reglas_activadas"] = [
            len(r.get("reglas_activadas", [])) for r in resultados
        ]
        self.results_df["umbral_aplicado"] = [
            r.get("umbral_aplicado", 80) for r in resultados
        ]

        n_aprobados = int(np.sum(y_pred == 1))
        n_rechazados = int(np.sum(
            np.array(dictamenes) == "RECHAZADO"
        ))
        n_revision = int(np.sum(
            np.array(dictamenes) == "REVISION_MANUAL"
        ))

        if verbose:
            print(f"  ✓ Vectores construidos (n={n_total})")
            print(f"  APROBADOS:        {n_aprobados}")
            print(f"  RECHAZADOS:       {n_rechazados}")
            print(f"  REVISION_MANUAL:  {n_revision} (→ contados como rechazo)")

        # ── PASO 4: Calcular métricas ──────────────────────
        if verbose:
            print("\n[Paso 4/7] Calculando métricas...")

        self._metricas = self.metrics.calculate_all(
            y_real, y_pred, scores, dictamenes
        )

        if verbose:
            m = self._metricas
            print(f"  Accuracy:    {m['accuracy']:.4f}")
            print(f"  Precision:   {m['precision']:.4f}")
            print(f"  Recall:      {m['recall']:.4f}")
            print(f"  F1-Score:    {m['f1_score']:.4f}")
            print(f"  Specificity: {m['specificity']:.4f}")
            print(f"  AUC-ROC:     {m['auc_roc']:.4f}")
            print(f"  Costo Asim.: {m['costo_asimetrico']:.4f}")

        # ── PASO 5: Generar visualizaciones ─────────────────
        if verbose:
            print("\n[Paso 5/7] Generando visualizaciones...")

        # Las visualizaciones se guardan en save_report()
        if verbose:
            print("  ✓ Listas para guardar con save_report()")

        # ── PASO 6: Análisis de errores ─────────────────────
        if verbose:
            print("\n[Paso 6/7] Analizando errores (FP y FN)...")

        self._errores_fp, self._errores_fn = (
            self._analizar_errores(verbose)
        )

        # ── PASO 7: Generar reporte resumen ─────────────────
        self._tiempo_total = time.time() - t0

        if verbose:
            print("\n[Paso 7/7] Generando reporte resumen...")

        self._reporte = self._construir_reporte(
            n_total, t_eval, dictamenes
        )

        if verbose:
            print(f"  ✓ Pipeline completo en {self._tiempo_total:.1f}s")
            print("\n" + self.metrics.interpret(self._metricas))

        return self._reporte

    # ════════════════════════════════════════════════════════
    # ANÁLISIS DE ERRORES
    # ════════════════════════════════════════════════════════

    def _analizar_errores(
        self, verbose: bool = True
    ) -> tuple[pd.DataFrame, pd.DataFrame]:
        """Desagrega los errores FP y FN para diagnóstico.

        Identifica patrones en los errores:
        - FP: ¿Qué perfiles aprueba incorrectamente?
        - FN: ¿Qué perfiles rechaza incorrectamente?

        Calcula promedios de variables clave por tipo de error
        para identificar debilidades del motor.

        Returns:
            (df_fp, df_fn) DataFrames de errores.
        """
        if self.results_df is None:
            return pd.DataFrame(), pd.DataFrame()

        df = self.results_df

        # FP: predijo APROBADO (1) pero era malo (0)
        mask_fp = (df["y_pred"] == 1) & (df["y_real"] == 0)
        df_fp = df[mask_fp].copy()

        # FN: predijo RECHAZADO (0) pero era bueno (1)
        mask_fn = (df["y_pred"] == 0) & (df["y_real"] == 1)
        df_fn = df[mask_fn].copy()

        if verbose:
            print(f"  Falsos Positivos (FP): {len(df_fp)}")
            if len(df_fp) > 0:
                print("    Perfil promedio del FP:")
                print(f"      Edad promedio:       {df_fp['edad'].mean():.1f}")
                print(f"      Ingreso promedio:    ${df_fp['ingreso_mensual'].mean():,.0f}")
                print(f"      DTI promedio:        {df_fp['dti_mihac'].mean():.3f}")
                print(f"      Score promedio:      {df_fp['score_mihac'].mean():.1f}")

                # Distribución por propósito
                print("    Por propósito:")
                for prop, cnt in df_fp["proposito_credito"].value_counts().items():
                    print(f"      {prop}: {cnt}")

            print(f"\n  Falsos Negativos (FN): {len(df_fn)}")
            if len(df_fn) > 0:
                print("    Perfil promedio del FN:")
                print(f"      Edad promedio:       {df_fn['edad'].mean():.1f}")
                print(f"      Ingreso promedio:    ${df_fn['ingreso_mensual'].mean():,.0f}")
                print(f"      DTI promedio:        {df_fn['dti_mihac'].mean():.3f}")
                print(f"      Score promedio:      {df_fn['score_mihac'].mean():.1f}")

                # Distribución por dictamen original
                print("    Por dictamen original:")
                for dict_name, cnt in df_fn["dictamen"].value_counts().items():
                    print(f"      {dict_name}: {cnt}")

        return df_fp, df_fn

    # ════════════════════════════════════════════════════════
    # REPORTE
    # ════════════════════════════════════════════════════════

    def _construir_reporte(
        self,
        n_total: int,
        t_eval: float,
        dictamenes: list[str],
    ) -> dict[str, Any]:
        """Construye el diccionario de reporte final.

        Args:
            n_total: Total de registros evaluados.
            t_eval: Tiempo de evaluación en segundos.
            dictamenes: Lista de dictámenes originales.

        Returns:
            Dict con todo el reporte de backtesting.
        """
        return {
            "timestamp": datetime.now().isoformat(),
            "n_registros": n_total,
            "tiempo_evaluacion_seg": round(t_eval, 2),
            "tiempo_total_seg": round(self._tiempo_total, 2),
            "registros_por_segundo": round(n_total / t_eval, 1) if t_eval > 0 else 0,
            "metricas": self._metricas,
            "distribucion_dictamenes": {
                "APROBADO": sum(1 for d in dictamenes if d == "APROBADO"),
                "RECHAZADO": sum(1 for d in dictamenes if d == "RECHAZADO"),
                "REVISION_MANUAL": sum(1 for d in dictamenes if d == "REVISION_MANUAL"),
            },
            "n_errores_fp": len(self._errores_fp) if self._errores_fp is not None else 0,
            "n_errores_fn": len(self._errores_fn) if self._errores_fn is not None else 0,
            "interpretacion": self.metrics.interpret(self._metricas) if self._metricas else "",
            "stats_engine": self.engine.stats,
            "perfil_errores": self._perfil_errores(),
        }

    def _perfil_errores(self) -> dict[str, Any]:
        """Resume los perfiles de error para el reporte.

        Returns:
            Dict con estadísticas de FP y FN.
        """
        perfil = {"fp": {}, "fn": {}}

        if self._errores_fp is not None and len(self._errores_fp) > 0:
            fp = self._errores_fp
            perfil["fp"] = {
                "n": len(fp),
                "edad_promedio": round(fp["edad"].mean(), 1),
                "ingreso_promedio": round(fp["ingreso_mensual"].mean(), 2),
                "dti_promedio": round(fp["dti_mihac"].mean(), 4),
                "score_promedio": round(fp["score_mihac"].mean(), 1),
                "proposito_mas_comun": fp["proposito_credito"].mode().iloc[0] if len(fp) > 0 else "N/A",
                "vivienda_mas_comun": fp["tipo_vivienda"].mode().iloc[0] if len(fp) > 0 else "N/A",
            }

        if self._errores_fn is not None and len(self._errores_fn) > 0:
            fn = self._errores_fn
            perfil["fn"] = {
                "n": len(fn),
                "edad_promedio": round(fn["edad"].mean(), 1),
                "ingreso_promedio": round(fn["ingreso_mensual"].mean(), 2),
                "dti_promedio": round(fn["dti_mihac"].mean(), 4),
                "score_promedio": round(fn["score_mihac"].mean(), 1),
                "dictamen_rechazado": int((fn["dictamen"] == "RECHAZADO").sum()),
                "dictamen_revision": int((fn["dictamen"] == "REVISION_MANUAL").sum()),
            }

        return perfil

    # ════════════════════════════════════════════════════════
    # GUARDAR REPORTE
    # ════════════════════════════════════════════════════════

    def save_report(
        self,
        output_dir: str = "reports/backtesting",
    ) -> dict[str, str]:
        """Guarda todos los artefactos del backtesting.

        Genera:
        - confusion_matrix.png
        - roc_curve.png
        - score_distribution.png
        - precision_recall.png
        - dashboard.png
        - results.csv (DataFrame completo)
        - report_summary.txt (reporte textual)

        Args:
            output_dir: Directorio de salida (se crea si
                       no existe).

        Returns:
            Dict con rutas de archivos generados.

        Ejemplo::

            rutas = bt.save_report("reports/backtesting/")
            print(rutas["dashboard"])
        """
        if self.results_df is None or self._metricas is None:
            raise RuntimeError(
                "Ejecuta run() antes de save_report()."
            )

        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)

        rutas: dict[str, str] = {}

        y_real = self.results_df["y_real"].values
        scores = self.results_df["score_mihac"].values

        # ── Visualizaciones ─────────────────────────────────
        cm_path = str(out / "confusion_matrix.png")
        self.plots.plot_confusion_matrix(
            self._metricas, save_path=cm_path
        )
        rutas["confusion_matrix"] = cm_path

        roc_path = str(out / "roc_curve.png")
        self.plots.plot_roc_curve(
            y_real, scores, save_path=roc_path,
        )
        rutas["roc_curve"] = roc_path

        dist_path = str(out / "score_distribution.png")
        self.plots.plot_score_distribution(
            scores, y_real, save_path=dist_path,
        )
        rutas["score_distribution"] = dist_path

        pr_path = str(out / "precision_recall.png")
        self.plots.plot_precision_recall_curve(
            y_real, scores, save_path=pr_path,
        )
        rutas["precision_recall"] = pr_path

        dash_path = str(out / "dashboard.png")
        self.plots.plot_metrics_dashboard(
            self._metricas, y_real, scores,
            save_path=dash_path,
        )
        rutas["dashboard"] = dash_path

        # ── CSV de resultados ───────────────────────────────
        csv_path = str(out / "results.csv")
        self.results_df.to_csv(csv_path, index=False)
        rutas["results_csv"] = csv_path

        # ── Reporte textual ─────────────────────────────────
        txt_path = str(out / "report_summary.txt")
        self._guardar_reporte_txt(txt_path)
        rutas["report_summary"] = txt_path

        # ── CSV de errores ──────────────────────────────────
        if self._errores_fp is not None and len(self._errores_fp) > 0:
            fp_path = str(out / "errores_fp.csv")
            self._errores_fp.to_csv(fp_path, index=False)
            rutas["errores_fp"] = fp_path

        if self._errores_fn is not None and len(self._errores_fn) > 0:
            fn_path = str(out / "errores_fn.csv")
            self._errores_fn.to_csv(fn_path, index=False)
            rutas["errores_fn"] = fn_path

        logger.info(
            "Reporte guardado en %s (%d archivos)",
            output_dir, len(rutas),
        )
        print(f"\n✓ Reporte guardado en {output_dir}/")
        for nombre, ruta in rutas.items():
            print(f"  • {nombre}: {ruta}")

        return rutas

    def _guardar_reporte_txt(self, filepath: str) -> None:
        """Genera el reporte textual completo.

        Args:
            filepath: Ruta del archivo .txt.
        """
        if self._reporte is None:
            return

        lineas = []
        lineas.append("=" * 60)
        lineas.append("REPORTE DE BACKTESTING — MIHAC v1.0")
        lineas.append(f"Fecha: {self._reporte['timestamp']}")
        lineas.append("=" * 60)

        lineas.append(f"\nRegistros evaluados: {self._reporte['n_registros']}")
        lineas.append(f"Tiempo de evaluación: {self._reporte['tiempo_evaluacion_seg']}s")
        lineas.append(f"Velocidad: {self._reporte['registros_por_segundo']} reg/seg")

        lineas.append("\n── Distribución de Dictámenes ──")
        dist = self._reporte["distribucion_dictamenes"]
        for k, v in dist.items():
            pct = v / self._reporte["n_registros"] * 100
            lineas.append(f"  {k}: {v} ({pct:.1f}%)")

        lineas.append("\n── Métricas de Desempeño ──")
        m = self._reporte["metricas"]
        for key in ["accuracy", "precision", "recall", "f1_score",
                     "specificity", "auc_roc", "costo_asimetrico"]:
            lineas.append(f"  {key}: {m[key]:.4f}")

        lineas.append("\n── Matriz de Confusión ──")
        cm = m["matriz"]
        lineas.append(f"  VP={cm['VP']}  FP={cm['FP']}")
        lineas.append(f"  FN={cm['FN']}  VN={cm['VN']}")

        lineas.append(f"\n── Errores ──")
        lineas.append(f"  Falsos Positivos: {self._reporte['n_errores_fp']}")
        lineas.append(f"  Falsos Negativos: {self._reporte['n_errores_fn']}")

        perfil = self._reporte.get("perfil_errores", {})
        if perfil.get("fp"):
            fp = perfil["fp"]
            lineas.append("\n  Perfil del FP típico:")
            lineas.append(f"    Edad promedio:    {fp['edad_promedio']}")
            lineas.append(f"    Ingreso promedio: ${fp['ingreso_promedio']:,.0f}")
            lineas.append(f"    DTI promedio:     {fp['dti_promedio']:.4f}")
            lineas.append(f"    Score promedio:   {fp['score_promedio']}")
            lineas.append(f"    Propósito común:  {fp['proposito_mas_comun']}")

        if perfil.get("fn"):
            fn = perfil["fn"]
            lineas.append("\n  Perfil del FN típico:")
            lineas.append(f"    Edad promedio:    {fn['edad_promedio']}")
            lineas.append(f"    Ingreso promedio: ${fn['ingreso_promedio']:,.0f}")
            lineas.append(f"    DTI promedio:     {fn['dti_promedio']:.4f}")
            lineas.append(f"    Score promedio:   {fn['score_promedio']}")
            lineas.append(f"    Rechazados:       {fn['dictamen_rechazado']}")
            lineas.append(f"    Revisión manual:  {fn['dictamen_revision']}")

        lineas.append("\n" + self._reporte.get("interpretacion", ""))

        with open(filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lineas))

    # ════════════════════════════════════════════════════════
    # ACCESORES
    # ════════════════════════════════════════════════════════

    @property
    def metricas(self) -> dict[str, Any] | None:
        """Métricas calculadas (disponible tras run())."""
        return self._metricas

    @property
    def errores_fp(self) -> pd.DataFrame | None:
        """DataFrame de Falsos Positivos."""
        return self._errores_fp

    @property
    def errores_fn(self) -> pd.DataFrame | None:
        """DataFrame de Falsos Negativos."""
        return self._errores_fn

    @property
    def reporte(self) -> dict[str, Any] | None:
        """Reporte completo (disponible tras run())."""
        return self._reporte


# ════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════

def _run_tests() -> None:
    """Tests del módulo de backtesting.

    Verifica la funcionalidad con un subconjunto de datos
    sintéticos (no requiere german.data para pasar).
    """
    import tempfile

    print("=" * 60)
    print("MIHAC — Tests del Módulo de Backtesting")
    print("=" * 60)

    # ── Test 1: Inicialización ──────────────────────────
    print("\n── Test 1: Inicialización ──")
    bt = Backtester()
    assert bt.engine is not None
    assert bt.metrics is not None
    assert bt.plots is not None
    assert bt.results_df is None
    print("  ✓ Backtester inicializado correctamente")

    # ── Test 2: Pipeline con datos sintéticos ───────────
    print("\n── Test 2: Pipeline con datos sintéticos ──")

    # Crear 10 registros sintéticos directamente
    datos_sinteticos = [
        {  # Buen pagador → APROBADO esperado
            "edad": 40, "ingreso_mensual": 30000,
            "total_deuda_actual": 3000,
            "historial_crediticio": 2,
            "antiguedad_laboral": 10,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 10000,
        },
        {  # Buen pagador → APROBADO esperado
            "edad": 35, "ingreso_mensual": 25000,
            "total_deuda_actual": 2000,
            "historial_crediticio": 2,
            "antiguedad_laboral": 8,
            "numero_dependientes": 0,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Educacion",
            "monto_credito": 8000,
        },
        {  # Mal pagador → RECHAZADO esperado
            "edad": 22, "ingreso_mensual": 8000,
            "total_deuda_actual": 6000,
            "historial_crediticio": 0,
            "antiguedad_laboral": 1,
            "numero_dependientes": 3,
            "tipo_vivienda": "Rentada",
            "proposito_credito": "Vacaciones",
            "monto_credito": 15000,
        },
        {  # Mal pagador → RECHAZADO esperado
            "edad": 20, "ingreso_mensual": 6000,
            "total_deuda_actual": 5000,
            "historial_crediticio": 0,
            "antiguedad_laboral": 0,
            "numero_dependientes": 2,
            "tipo_vivienda": "Rentada",
            "proposito_credito": "Consumo",
            "monto_credito": 20000,
        },
        {  # Buen pagador → debería aprobar
            "edad": 45, "ingreso_mensual": 35000,
            "total_deuda_actual": 4000,
            "historial_crediticio": 2,
            "antiguedad_laboral": 15,
            "numero_dependientes": 2,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 12000,
        },
    ]

    etiquetas_reales = [1, 1, 0, 0, 1]  # 1=bueno, 0=malo

    # Evaluar y construir vectores manualmente
    engine = InferenceEngine()
    resultados = []
    for d in datos_sinteticos:
        r = engine.evaluate(d)
        resultados.append(r)

    dictamenes = [r["dictamen"] for r in resultados]
    scores = [r["score_final"] for r in resultados]
    y_pred = [1 if d == "APROBADO" else 0 for d in dictamenes]

    print(f"  Dictámenes: {dictamenes}")
    print(f"  Scores:     {scores}")
    print(f"  y_pred:     {y_pred}")
    print(f"  y_real:     {etiquetas_reales}")

    # Calcular métricas
    metricas = bt.metrics.calculate_all(
        etiquetas_reales, y_pred, scores
    )
    print(f"  Accuracy:  {metricas['accuracy']}")
    print(f"  Precision: {metricas['precision']}")
    print(f"  Recall:    {metricas['recall']}")
    print("  ✓ Pipeline de evaluación funcional")

    # ── Test 3: Análisis de errores ─────────────────────
    print("\n── Test 3: Análisis de errores ──")

    # Simular resultados en el DataFrame
    import pandas as pd
    bt.results_df = pd.DataFrame({
        "edad": [40, 35, 22, 20, 45],
        "ingreso_mensual": [30000, 25000, 8000, 6000, 35000],
        "total_deuda_actual": [3000, 2000, 6000, 5000, 4000],
        "proposito_credito": ["Negocio", "Educacion", "Vacaciones", "Consumo", "Negocio"],
        "tipo_vivienda": ["Propia", "Propia", "Rentada", "Rentada", "Propia"],
        "score_mihac": scores,
        "dictamen": dictamenes,
        "y_pred": y_pred,
        "y_real": etiquetas_reales,
        "dti_mihac": [r["dti_ratio"] for r in resultados],
        "dti_clasificacion": [r["dti_clasificacion"] for r in resultados],
        "n_reglas_activadas": [len(r["reglas_activadas"]) for r in resultados],
        "umbral_aplicado": [r["umbral_aplicado"] for r in resultados],
    })

    df_fp, df_fn = bt._analizar_errores(verbose=True)
    assert isinstance(df_fp, pd.DataFrame)
    assert isinstance(df_fn, pd.DataFrame)
    print(f"  ✓ FP={len(df_fp)}, FN={len(df_fn)}")

    # ── Test 4: Guardar reporte ─────────────────────────
    print("\n── Test 4: Guardar reporte (dir temporal) ──")

    bt._metricas = metricas
    bt._errores_fp = df_fp
    bt._errores_fn = df_fn
    bt._tiempo_total = 1.23
    bt._reporte = bt._construir_reporte(
        5, 0.5, dictamenes
    )

    with tempfile.TemporaryDirectory() as tmpdir:
        rutas = bt.save_report(tmpdir)

        assert "dashboard" in rutas
        assert "results_csv" in rutas
        assert "report_summary" in rutas

        # Verificar que archivos existen
        for nombre, ruta in rutas.items():
            assert Path(ruta).exists(), f"FAIL: {ruta} no existe"
            size = Path(ruta).stat().st_size
            print(f"  ✓ {nombre}: {size:,} bytes")

    # ── Test 5: Accesores ───────────────────────────────
    print("\n── Test 5: Accesores ──")
    assert bt.metricas is not None
    assert bt.reporte is not None
    assert bt.reporte["n_registros"] == 5
    assert "metricas" in bt.reporte
    assert "perfil_errores" in bt.reporte
    print("  ✓ Accesores funcionan correctamente")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DE BACKTESTING PASARON ✓")
    print(f"{'='*60}")


if __name__ == "__main__":
    _run_tests()
