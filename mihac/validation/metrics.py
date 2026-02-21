# ============================================================
# MIHAC v1.0 — Módulo de Métricas de Validación
# validation/metrics.py
# ============================================================
# Librería reutilizable para calcular, interpretar y graficar
# todas las métricas de desempeño del motor MIHAC comparado
# contra etiquetas reales.
#
# CONVENCIÓN DE ETIQUETAS:
#   y_real: 1 = buen pagador, 0 = mal pagador
#   y_pred: 1 = APROBADO por MIHAC, 0 = RECHAZADO o REVISION_MANUAL
#
# DECISIÓN DE DISEÑO:
#   REVISION_MANUAL se clasifica como 0 (rechazo) para métricas
#   binarias. Justificación: si el motor no tiene confianza
#   suficiente para aprobar autónomamente, el tratamiento
#   conservador es contarlo como rechazo. Esto penaliza Recall
#   pero protege Precision, alineado con el principio financiero
#   de preferir falsos negativos sobre falsos positivos.
#
# COSTO ASIMÉTRICO:
#   FP (aprobar moroso)  peso = 4 (pérdida directa de capital)
#   FN (rechazar solvente) peso = 1 (costo de oportunidad)
#   Ratio 4:1 estándar en literatura de scoring crediticio.
# ============================================================

import logging
from pathlib import Path
from typing import Any

import numpy as np
import matplotlib
matplotlib.use("Agg")  # backend no-interactivo para servidores
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score as sklearn_f1,
    roc_auc_score,
    roc_curve,
    precision_recall_curve,
    average_precision_score,
)

logger = logging.getLogger(__name__)

# ── Paleta de colores consistente con el EDA ────────────────
VERDE = "#2ECC71"
ROJO = "#E74C3C"
AZUL = "#2E74B5"
AMBAR = "#F39C12"
GRIS = "#95A5A6"

# ── Configuración global de matplotlib ──────────────────────
plt.rcParams.update({
    "figure.figsize": (12, 8),
    "figure.dpi": 100,
    "font.size": 11,
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
})
sns.set_style("whitegrid")


# ════════════════════════════════════════════════════════════
# CLASE: MIHACMetrics
# ════════════════════════════════════════════════════════════

class MIHACMetrics:
    """Calcula e interpreta métricas de validación del motor MIHAC.

    Todas las métricas principales (VP/FP/VN/FN, Precision,
    Recall, F1) se calculan manualmente primero y luego se
    verifican contra sklearn.metrics para garantizar corrección.

    Convención:
        y_real = 1 → buen pagador (debería aprobarse)
        y_real = 0 → mal pagador  (debería rechazarse)
        y_pred = 1 → APROBADO por MIHAC
        y_pred = 0 → RECHAZADO o REVISION_MANUAL

    Ejemplo::

        metrics = MIHACMetrics()
        m = metrics.calculate_all(y_real, y_pred, scores)
        print(metrics.interpret(m))
    """

    # Costo relativo FP vs FN (configurable)
    COSTO_FP: float = 4.0
    COSTO_FN: float = 1.0

    # ────────────────────────────────────────────────────────
    # MATRIZ DE CONFUSIÓN
    # ────────────────────────────────────────────────────────

    def confusion_matrix_data(
        self,
        y_real: list[int] | np.ndarray,
        y_pred: list[int] | np.ndarray,
    ) -> dict[str, Any]:
        """Calcula los 4 componentes de la matriz de confusión.

        Cálculo manual sin usar sklearn, para demostrar
        comprensión de la lógica subyacente.

        VP = predijo APROBADO (1) y era buen pagador (1)
        FP = predijo APROBADO (1) y era mal pagador (0)  ← PELIGROSO
        VN = predijo RECHAZADO (0) y era mal pagador (0)
        FN = predijo RECHAZADO (0) y era buen pagador (1)

        Args:
            y_real: Etiquetas reales (1=bueno, 0=malo).
            y_pred: Predicciones binarias del motor.

        Returns:
            Dict con VP, FP, VN, FN, total y descripciones.

        Ejemplo::

            cm = metrics.confusion_matrix_data(
                [1,1,0,0], [1,0,0,1]
            )
            print(cm["VP"], cm["FP"])  # 1, 1
        """
        y_r = np.asarray(y_real, dtype=int)
        y_p = np.asarray(y_pred, dtype=int)

        vp = int(np.sum((y_p == 1) & (y_r == 1)))
        fp = int(np.sum((y_p == 1) & (y_r == 0)))
        vn = int(np.sum((y_p == 0) & (y_r == 0)))
        fn = int(np.sum((y_p == 0) & (y_r == 1)))

        return {
            "VP": vp,
            "FP": fp,
            "VN": vn,
            "FN": fn,
            "total": vp + fp + vn + fn,
            "descripcion_FP": (
                "Créditos aprobados que resultaron en morosidad"
            ),
            "descripcion_FN": (
                "Clientes solventes rechazados incorrectamente"
            ),
        }

    # ────────────────────────────────────────────────────────
    # CÁLCULO COMPLETO DE MÉTRICAS
    # ────────────────────────────────────────────────────────

    def calculate_all(
        self,
        y_real: list[int] | np.ndarray,
        y_pred: list[int] | np.ndarray,
        scores: list[float] | np.ndarray,
        dictamenes: list[str] | None = None,
    ) -> dict[str, Any]:
        """Calcula TODAS las métricas de validación.

        Precision, Recall, F1 se calculan manualmente y luego
        se verifican con sklearn (AssertionError si delta > 0.001).

        Args:
            y_real: Etiquetas reales (1=bueno, 0=malo).
            y_pred: Predicciones binarias (1=aprobado, 0=rechazado).
            scores: Scores numéricos 0–100 del motor.
            dictamenes: Lista opcional de dictámenes originales
                       ("APROBADO", "RECHAZADO", "REVISION_MANUAL").

        Returns:
            Dict con todas las métricas, incluyendo la matriz.

        Raises:
            AssertionError: Si cálculo manual difiere de sklearn
                           en más de 0.001.

        Ejemplo::

            m = metrics.calculate_all(
                [1,1,0], [1,0,0], [85, 55, 30]
            )
            print(m["f1_score"])
        """
        y_r = np.asarray(y_real, dtype=int)
        y_p = np.asarray(y_pred, dtype=int)
        sc = np.asarray(scores, dtype=float)

        # Matriz de confusión manual
        cm = self.confusion_matrix_data(y_r, y_p)
        vp, fp, vn, fn = cm["VP"], cm["FP"], cm["VN"], cm["FN"]
        total = cm["total"]

        # ── Métricas manuales ───────────────────────────────
        accuracy = (vp + vn) / total if total > 0 else 0.0

        precision = vp / (vp + fp) if (vp + fp) > 0 else 0.0
        recall = vp / (vp + fn) if (vp + fn) > 0 else 0.0
        f1 = (
            2 * (precision * recall) / (precision + recall)
            if (precision + recall) > 0 else 0.0
        )

        specificity = vn / (vn + fp) if (vn + fp) > 0 else 0.0

        tasa_morosidad = fp / (vp + fp) if (vp + fp) > 0 else 0.0
        tasa_rechazo_injusto = fn / (vn + fn) if (vn + fn) > 0 else 0.0

        costo_asimetrico = (
            (fp * self.COSTO_FP + fn * self.COSTO_FN) / total
            if total > 0 else 0.0
        )

        # ── Verificación con sklearn ────────────────────────
        if total > 0 and len(np.unique(y_r)) > 1:
            sk_precision = precision_score(y_r, y_p, zero_division=0)
            sk_recall = recall_score(y_r, y_p, zero_division=0)
            sk_f1 = sklearn_f1(y_r, y_p, zero_division=0)

            assert abs(precision - sk_precision) <= 0.001, (
                f"Precision manual ({precision:.4f}) != "
                f"sklearn ({sk_precision:.4f})"
            )
            assert abs(recall - sk_recall) <= 0.001, (
                f"Recall manual ({recall:.4f}) != "
                f"sklearn ({sk_recall:.4f})"
            )
            assert abs(f1 - sk_f1) <= 0.001, (
                f"F1 manual ({f1:.4f}) != sklearn ({sk_f1:.4f})"
            )
            logger.debug(
                "Verificación sklearn OK: P=%.4f R=%.4f F1=%.4f",
                precision, recall, f1,
            )

        # ── AUC-ROC (requiere scores y varianza) ───────────
        auc_roc = 0.0
        if len(np.unique(y_r)) > 1 and len(sc) == len(y_r):
            try:
                # Normalizar scores a 0-1 para AUC
                scores_norm = sc / 100.0
                auc_roc = roc_auc_score(y_r, scores_norm)
            except ValueError as e:
                logger.warning("No se pudo calcular AUC-ROC: %s", e)

        # ── Conteos por dictamen ────────────────────────────
        n_aprobados = int(np.sum(y_p == 1))
        n_rechazados = int(np.sum(y_p == 0))
        n_revision = 0
        if dictamenes is not None:
            n_revision = sum(
                1 for d in dictamenes if d == "REVISION_MANUAL"
            )
            n_rechazados = sum(
                1 for d in dictamenes if d == "RECHAZADO"
            )

        return {
            "accuracy": round(accuracy, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "specificity": round(specificity, 4),
            "tasa_morosidad_predicha": round(tasa_morosidad, 4),
            "tasa_rechazo_injusto": round(tasa_rechazo_injusto, 4),
            "costo_asimetrico": round(costo_asimetrico, 4),
            "matriz": cm,
            "auc_roc": round(auc_roc, 4),
            "n_aprobados": n_aprobados,
            "n_rechazados": n_rechazados,
            "n_revision": n_revision,
        }

    # ────────────────────────────────────────────────────────
    # INTERPRETACIÓN
    # ────────────────────────────────────────────────────────

    def interpret(self, metricas: dict[str, Any]) -> str:
        """Genera texto interpretativo en español.

        Analiza las métricas y produce una interpretación
        comprensible para no-técnicos, con recomendaciones
        condicionales según los resultados.

        Args:
            metricas: Dict retornado por calculate_all().

        Returns:
            Texto multi-línea con interpretación.

        Ejemplo::

            texto = metrics.interpret(m)
            print(texto)
        """
        p = metricas["precision"]
        r = metricas["recall"]
        f1 = metricas["f1_score"]
        acc = metricas["accuracy"]
        spec = metricas["specificity"]
        costo = metricas["costo_asimetrico"]
        auc = metricas["auc_roc"]
        cm = metricas["matriz"]

        lineas = []
        lineas.append("=" * 60)
        lineas.append("INTERPRETACIÓN DE RESULTADOS — MOTOR MIHAC")
        lineas.append("=" * 60)

        # Precision
        p_pct = int(p * 100)
        morosidad_pct = 100 - p_pct
        lineas.append(
            f"\nPrecision ({p:.2f}): De cada 100 créditos que "
            f"el motor aprobó, {p_pct} resultaron en buen pago "
            f"y {morosidad_pct} en morosidad."
        )

        # Recall
        r_pct = int(r * 100)
        lineas.append(
            f"\nRecall ({r:.2f}): El motor identificó "
            f"correctamente al {r_pct}% de los buenos pagadores "
            f"del dataset."
        )

        # Specificity
        s_pct = int(spec * 100)
        lineas.append(
            f"\nSpecificity ({spec:.2f}): El motor detectó "
            f"correctamente al {s_pct}% de los malos pagadores."
        )

        # F1
        lineas.append(
            f"\nF1-Score ({f1:.2f}): Balance armónico entre "
            f"Precision y Recall."
        )

        # Costo asimétrico
        lineas.append(
            f"\nCosto Asimétrico ({costo:.2f}): Ponderado 4:1 "
            f"(FP vs FN). "
            f"FP={cm['FP']} (pérdida directa), "
            f"FN={cm['FN']} (oportunidad perdida)."
        )

        # AUC
        lineas.append(
            f"\nAUC-ROC ({auc:.2f}): Capacidad discriminatoria "
            f"general del motor."
        )

        # ── Recomendaciones condicionales ───────────────────
        lineas.append("\n" + "─" * 60)
        lineas.append("RECOMENDACIONES")
        lineas.append("─" * 60)

        if costo > 0.30:
            lineas.append(
                "⚠ Costo asimétrico ALTO (>0.30): Se recomienda "
                "aumentar el umbral de aprobación para reducir FP."
            )
        elif costo > 0.20:
            lineas.append(
                "△ Costo asimétrico MODERADO (0.20-0.30): "
                "Considerar ajustes finos a las reglas de "
                "compensación."
            )
        else:
            lineas.append(
                "✓ Costo asimétrico BAJO (<0.20): El balance "
                "FP/FN es adecuado para el contexto financiero."
            )

        if r < 0.65:
            lineas.append(
                "⚠ Recall BAJO (<0.65): Las reglas de "
                "penalización podrían ser demasiado agresivas. "
                "Revisar R004, R008, R009."
            )

        if p < 0.72:
            lineas.append(
                "⚠ Precision BAJA (<0.72): Demasiados morosos "
                "aprobados. Considerar subir umbral de 80 a 82."
            )

        if auc < 0.65:
            lineas.append(
                "⚠ AUC-ROC BAJO (<0.65): La capacidad "
                "discriminatoria del motor es limitada. Revisar "
                "la estructura de sub-scores."
            )

        # ── Objetivos para tesis ────────────────────────────
        lineas.append("\n" + "─" * 60)
        lineas.append("OBJETIVOS PARA TESIS")
        lineas.append("─" * 60)

        objetivos = {
            "Accuracy > 0.70": acc > 0.70,
            "Precision > 0.75": p > 0.75,
            "Recall > 0.65": r > 0.65,
            "F1-Score > 0.70": f1 > 0.70,
            "AUC-ROC > 0.70": auc > 0.70,
            "Costo Asim. < 0.25": costo < 0.25,
        }
        cumplidos = sum(objetivos.values())

        for nombre, cumple in objetivos.items():
            marca = "✓" if cumple else "✗"
            lineas.append(f"  {marca} {nombre}")

        lineas.append(
            f"\n  Resultado: {cumplidos}/6 objetivos cumplidos."
        )

        return "\n".join(lineas)


# ════════════════════════════════════════════════════════════
# CLASE: MIHACPlots
# ════════════════════════════════════════════════════════════

class MIHACPlots:
    """Visualizaciones de métricas del motor MIHAC.

    Genera gráficas de alta calidad listas para la tesis,
    con paleta consistente con el EDA del German Credit.

    Ejemplo::

        plots = MIHACPlots()
        plots.plot_confusion_matrix(metricas, "cm.png")
    """

    # ────────────────────────────────────────────────────────
    # MATRIZ DE CONFUSIÓN
    # ────────────────────────────────────────────────────────

    def plot_confusion_matrix(
        self,
        metricas: dict[str, Any],
        save_path: str | None = None,
        ax: plt.Axes | None = None,
    ) -> plt.Figure | None:
        """Matriz 2x2 como heatmap con anotaciones detalladas.

        Colores: VP/VN en verde (aciertos), FP en rojo
        (error peligroso), FN en ámbar (error menor).

        Args:
            metricas: Dict con clave 'matriz' de calculate_all().
            save_path: Ruta para guardar PNG. None = no guardar.
            ax: Axes existente (para dashboard). None = nueva fig.

        Returns:
            Figure si ax es None, else None.

        Ejemplo::

            plots.plot_confusion_matrix(m, "cm.png")
        """
        cm = metricas["matriz"]
        vp, fp, vn, fn = cm["VP"], cm["FP"], cm["VN"], cm["FN"]
        total = cm["total"]

        # Matriz como array 2x2
        # Filas: Predicción (Aprobó / Rechazó)
        # Columnas: Real (Buen pagador / Moroso)
        mat = np.array([[vp, fp], [fn, vn]])

        # Colores personalizados
        colores = np.array([
            [VERDE, ROJO],
            [AMBAR, VERDE],
        ])

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.get_figure()

        # Pintar celdas manualmente
        for i in range(2):
            for j in range(2):
                val = mat[i, j]
                pct = val / total * 100 if total > 0 else 0

                # Fondo
                ax.add_patch(plt.Rectangle(
                    (j, i), 1, 1,
                    facecolor=colores[i, j],
                    alpha=0.3, edgecolor="white", linewidth=2,
                ))

                # Etiquetas
                labels = [
                    ["VP", "FP"],
                    ["FN", "VN"],
                ]
                descripciones = [
                    ["Buen pago\naprobado", "Moroso\naprobado"],
                    ["Solvente\nrechazado", "Moroso\ndetectado"],
                ]

                ax.text(
                    j + 0.5, i + 0.35,
                    f"{labels[i][j]}\n{val}\n({pct:.1f}%)",
                    ha="center", va="center",
                    fontsize=14, fontweight="bold",
                )
                ax.text(
                    j + 0.5, i + 0.75,
                    descripciones[i][j],
                    ha="center", va="center",
                    fontsize=9, color="gray",
                )

        ax.set_xlim(0, 2)
        ax.set_ylim(0, 2)
        ax.invert_yaxis()

        ax.set_xticks([0.5, 1.5])
        ax.set_xticklabels(
            ["REAL: Buen pagador", "REAL: Moroso"],
            fontsize=11,
        )
        ax.set_yticks([0.5, 1.5])
        ax.set_yticklabels(
            ["PRED: Aprobó", "PRED: Rechazó"],
            fontsize=11,
        )

        ax.set_title(
            "Matriz de Confusión — Motor MIHAC vs. "
            "German Credit Dataset\n"
            f"n = {total:,} registros | "
            "REVISION_MANUAL clasificada como rechazo",
            fontsize=12, pad=15,
        )

        ax.tick_params(length=0)
        ax.grid(False)

        if save_path and created_fig:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info("Matriz guardada: %s", save_path)
        if created_fig:
            plt.close(fig)
            return fig
        return None

    # ────────────────────────────────────────────────────────
    # CURVA ROC
    # ────────────────────────────────────────────────────────

    def plot_roc_curve(
        self,
        y_real: list[int] | np.ndarray,
        scores: list[float] | np.ndarray,
        save_path: str | None = None,
        ax: plt.Axes | None = None,
    ) -> plt.Figure | None:
        """Curva ROC con punto óptimo (Youden's J).

        Args:
            y_real: Etiquetas reales (1=bueno, 0=malo).
            scores: Scores numéricos 0-100 del motor.
            save_path: Ruta para guardar PNG.
            ax: Axes existente (para dashboard).

        Returns:
            Figure si ax es None.
        """
        y_r = np.asarray(y_real, dtype=int)
        sc = np.asarray(scores, dtype=float) / 100.0

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.get_figure()

        if len(np.unique(y_r)) < 2:
            ax.text(
                0.5, 0.5, "No hay varianza en y_real",
                ha="center", va="center", fontsize=14,
            )
            if save_path and created_fig:
                fig.savefig(save_path, dpi=300, bbox_inches="tight")
            if created_fig:
                plt.close(fig)
            return fig if created_fig else None

        fpr, tpr, thresholds = roc_curve(y_r, sc)
        auc = roc_auc_score(y_r, sc)

        # Punto óptimo: maximizar Youden's J
        j_scores = tpr - fpr
        idx_optimo = np.argmax(j_scores)
        fpr_opt = fpr[idx_optimo]
        tpr_opt = tpr[idx_optimo]
        umbral_opt = thresholds[idx_optimo] * 100

        # Diagonal (clasificador aleatorio)
        ax.plot(
            [0, 1], [0, 1], "k--", alpha=0.3,
            label="Aleatorio (AUC = 0.50)",
        )

        # Curva ROC
        ax.plot(
            fpr, tpr, color=AZUL, linewidth=2.5,
            label=f"MIHAC (AUC = {auc:.3f})",
        )

        # Punto óptimo
        ax.scatter(
            [fpr_opt], [tpr_opt], s=120,
            color=ROJO, zorder=5,
            label=f"Umbral óptimo: {umbral_opt:.0f}",
        )
        ax.annotate(
            f"Umbral = {umbral_opt:.0f}\n"
            f"TPR = {tpr_opt:.2f}\n"
            f"FPR = {fpr_opt:.2f}",
            xy=(fpr_opt, tpr_opt),
            xytext=(fpr_opt + 0.15, tpr_opt - 0.15),
            fontsize=9,
            arrowprops=dict(arrowstyle="->", color="gray"),
            bbox=dict(boxstyle="round", fc="white", alpha=0.8),
        )

        # Anotación AUC
        ax.text(
            0.6, 0.15,
            f"AUC = {auc:.3f}",
            fontsize=14, fontweight="bold",
            bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8),
        )

        ax.set_xlabel("Tasa de Falsos Positivos (1 - Especificidad)")
        ax.set_ylabel(
            "Tasa de Verdaderos Positivos (Sensibilidad / Recall)"
        )
        ax.set_title("Curva ROC — Motor MIHAC")
        ax.legend(loc="lower right", fontsize=10)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)

        if save_path and created_fig:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info("ROC guardada: %s", save_path)
        if created_fig:
            plt.close(fig)
            return fig
        return None

    # ────────────────────────────────────────────────────────
    # DISTRIBUCIÓN DE SCORES
    # ────────────────────────────────────────────────────────

    def plot_score_distribution(
        self,
        scores: list[float] | np.ndarray,
        y_real: list[int] | np.ndarray,
        save_path: str | None = None,
        ax: plt.Axes | None = None,
    ) -> plt.Figure | None:
        """Histograma/KDE de scores separado por clase.

        Incluye zonas sombreadas para los umbrales MIHAC
        y conteo de registros en la zona de ambigüedad.

        Args:
            scores: Scores numéricos 0-100 del motor.
            y_real: Etiquetas reales (1=bueno, 0=malo).
            save_path: Ruta para guardar PNG.
            ax: Axes existente (para dashboard).

        Returns:
            Figure si ax es None.
        """
        sc = np.asarray(scores, dtype=float)
        y_r = np.asarray(y_real, dtype=int)

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(12, 6))
        else:
            fig = ax.get_figure()

        # KDE por clase
        buenos = sc[y_r == 1]
        malos = sc[y_r == 0]

        if len(buenos) > 1:
            sns.kdeplot(
                buenos, ax=ax, color=VERDE,
                label=f"Buenos pagadores (n={len(buenos)})",
                fill=True, alpha=0.3, linewidth=2,
            )
        if len(malos) > 1:
            sns.kdeplot(
                malos, ax=ax, color=ROJO,
                label=f"Malos pagadores (n={len(malos)})",
                fill=True, alpha=0.3, linewidth=2,
            )

        # Zona REVISION_MANUAL sombreada
        ax.axvspan(
            60, 80, alpha=0.1, color=AMBAR,
            label="Zona REVISIÓN MANUAL",
        )

        # Líneas de umbrales
        ax.axvline(
            60, color=AMBAR, linestyle="--", linewidth=1.5,
            label="Inicio revisión (60)",
        )
        ax.axvline(
            80, color=ROJO, linestyle="--", linewidth=1.5,
            label="Umbral aprobación (80)",
        )
        ax.axvline(
            85, color=ROJO, linestyle=":", linewidth=1.5,
            alpha=0.7, label="Umbral monto alto (85)",
        )

        # Conteo en zona ambigua
        en_zona = int(np.sum((sc >= 60) & (sc < 80)))
        ax.text(
            70, ax.get_ylim()[1] * 0.85,
            f"Zona de ambigüedad:\n{en_zona} registros",
            ha="center", fontsize=10,
            bbox=dict(boxstyle="round", fc="lightyellow", alpha=0.8),
        )

        ax.set_xlabel("Score MIHAC (0–100)")
        ax.set_ylabel("Densidad")
        ax.set_title(
            "Distribución de Scores MIHAC por Clase Real"
        )
        ax.legend(loc="upper left", fontsize=9)
        ax.set_xlim(-5, 105)

        if save_path and created_fig:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info("Distribución guardada: %s", save_path)
        if created_fig:
            plt.close(fig)
            return fig
        return None

    # ────────────────────────────────────────────────────────
    # CURVA PRECISION-RECALL
    # ────────────────────────────────────────────────────────

    def plot_precision_recall_curve(
        self,
        y_real: list[int] | np.ndarray,
        scores: list[float] | np.ndarray,
        save_path: str | None = None,
        ax: plt.Axes | None = None,
    ) -> plt.Figure | None:
        """Curva Precision-Recall con punto de operación actual.

        Args:
            y_real: Etiquetas reales (1=bueno, 0=malo).
            scores: Scores numéricos 0-100 del motor.
            save_path: Ruta para guardar PNG.
            ax: Axes existente (para dashboard).

        Returns:
            Figure si ax es None.
        """
        y_r = np.asarray(y_real, dtype=int)
        sc = np.asarray(scores, dtype=float) / 100.0

        created_fig = ax is None
        if created_fig:
            fig, ax = plt.subplots(figsize=(8, 6))
        else:
            fig = ax.get_figure()

        if len(np.unique(y_r)) < 2:
            ax.text(
                0.5, 0.5, "No hay varianza en y_real",
                ha="center", va="center", fontsize=14,
            )
            if save_path and created_fig:
                fig.savefig(save_path, dpi=300, bbox_inches="tight")
            if created_fig:
                plt.close(fig)
            return fig if created_fig else None

        prec_curve, rec_curve, _ = precision_recall_curve(y_r, sc)
        ap = average_precision_score(y_r, sc)

        # Línea base (tasa de positivos)
        baseline = np.mean(y_r)
        ax.axhline(
            baseline, color=GRIS, linestyle="--", alpha=0.5,
            label=f"Baseline (tasa buenos = {baseline:.2f})",
        )

        # Curva PR
        ax.plot(
            rec_curve, prec_curve, color=AZUL, linewidth=2.5,
            label=f"MIHAC (AP = {ap:.3f})",
        )

        # Punto de operación actual (umbral 80 → score 0.8)
        y_pred_80 = (sc >= 0.80).astype(int)
        if np.sum(y_pred_80) > 0:
            p_actual = precision_score(y_r, y_pred_80, zero_division=0)
            r_actual = recall_score(y_r, y_pred_80, zero_division=0)
            ax.scatter(
                [r_actual], [p_actual], s=120,
                color=ROJO, zorder=5,
                label=f"Operación actual (umbral 80)",
            )

        ax.set_xlabel("Recall")
        ax.set_ylabel("Precision")
        ax.set_title("Curva Precision-Recall — Motor MIHAC")
        ax.legend(loc="lower left", fontsize=10)
        ax.set_xlim(-0.02, 1.02)
        ax.set_ylim(-0.02, 1.02)

        if save_path and created_fig:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info("PR curve guardada: %s", save_path)
        if created_fig:
            plt.close(fig)
            return fig
        return None

    # ────────────────────────────────────────────────────────
    # DASHBOARD COMPLETO (2x2)
    # ────────────────────────────────────────────────────────

    def plot_metrics_dashboard(
        self,
        metricas: dict[str, Any],
        y_real: list[int] | np.ndarray,
        scores: list[float] | np.ndarray,
        save_path: str | None = None,
    ) -> plt.Figure:
        """Dashboard de 4 paneles para la tesis.

        Panel 1 (sup-izq): Matriz de confusión
        Panel 2 (sup-der): Barras de métricas
        Panel 3 (inf-izq): Distribución de scores
        Panel 4 (inf-der): Dona de composición de errores

        Args:
            metricas: Dict retornado por calculate_all().
            y_real: Etiquetas reales.
            scores: Scores numéricos 0-100.
            save_path: Ruta para guardar PNG (300 DPI).

        Returns:
            Figure de matplotlib.

        Ejemplo::

            fig = plots.plot_metrics_dashboard(
                m, y_real, scores,
                "dashboard.png"
            )
        """
        fig, axes = plt.subplots(2, 2, figsize=(18, 14))

        # ── Panel 1: Matriz de confusión ────────────────────
        self.plot_confusion_matrix(metricas, ax=axes[0, 0])

        # ── Panel 2: Barras de métricas ─────────────────────
        ax2 = axes[0, 1]
        metricas_nombres = [
            "Accuracy", "Precision", "Recall",
            "F1-Score", "Specificity",
        ]
        metricas_valores = [
            metricas["accuracy"],
            metricas["precision"],
            metricas["recall"],
            metricas["f1_score"],
            metricas["specificity"],
        ]
        colores_barras = []
        for v in metricas_valores:
            if v >= 0.75:
                colores_barras.append(VERDE)
            elif v >= 0.60:
                colores_barras.append(AMBAR)
            else:
                colores_barras.append(ROJO)

        bars = ax2.barh(
            metricas_nombres, metricas_valores,
            color=colores_barras, edgecolor="white",
            height=0.6,
        )
        ax2.axvline(
            0.75, color=GRIS, linestyle="--", alpha=0.7,
            label="Umbral aceptable (0.75)",
        )
        for bar, val in zip(bars, metricas_valores):
            ax2.text(
                val + 0.02, bar.get_y() + bar.get_height() / 2,
                f"{val:.3f}", va="center", fontweight="bold",
            )
        ax2.set_xlim(0, 1.15)
        ax2.set_title("Métricas de Desempeño")
        ax2.legend(loc="lower right", fontsize=9)

        # ── Panel 3: Distribución de scores ─────────────────
        self.plot_score_distribution(
            scores, y_real, ax=axes[1, 0]
        )

        # ── Panel 4: Dona de composición ────────────────────
        ax4 = axes[1, 1]
        cm = metricas["matriz"]
        labels_dona = [
            f"VP: {cm['VP']}",
            f"VN: {cm['VN']}",
            f"FP: {cm['FP']}",
            f"FN: {cm['FN']}",
        ]
        sizes = [cm["VP"], cm["VN"], cm["FP"], cm["FN"]]
        colors_dona = [VERDE, VERDE, ROJO, AMBAR]
        explode = (0, 0, 0.08, 0.04)

        wedges, texts, autotexts = ax4.pie(
            sizes, labels=labels_dona,
            colors=colors_dona, explode=explode,
            autopct="%1.1f%%", startangle=90,
            pctdistance=0.78, textprops={"fontsize": 10},
        )
        # Hacer dona (círculo blanco central)
        centro = plt.Circle(
            (0, 0), 0.55, fc="white", edgecolor="white"
        )
        ax4.add_patch(centro)
        ax4.text(
            0, 0,
            f"Total\n{cm['total']:,}",
            ha="center", va="center",
            fontsize=14, fontweight="bold",
        )
        ax4.set_title("Composición de Predicciones")

        fig.suptitle(
            "Reporte de Validación MIHAC — Semana 6",
            fontsize=18, fontweight="bold", y=0.98,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.95])

        if save_path:
            fig.savefig(save_path, dpi=300, bbox_inches="tight")
            logger.info("Dashboard guardado: %s", save_path)

        plt.close(fig)
        return fig


# ════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════

def _run_tests() -> None:
    """Tests del módulo de métricas."""
    import tempfile

    print("=" * 60)
    print("MIHAC — Tests del Módulo de Métricas")
    print("=" * 60)

    metrics = MIHACMetrics()
    plots = MIHACPlots()

    # ── Test 1: Matriz de confusión con caso conocido ───
    print("\n── Test 1: Matriz de confusión (caso conocido) ──")
    y_real = [1, 1, 1, 0, 0, 0]
    y_pred = [1, 1, 0, 0, 0, 1]
    # VP=2 (pred=1,real=1), FP=1 (pred=1,real=0),
    # VN=2 (pred=0,real=0), FN=1 (pred=0,real=1)

    cm = metrics.confusion_matrix_data(y_real, y_pred)
    assert cm["VP"] == 2, f"FAIL VP: {cm['VP']} != 2"
    assert cm["FP"] == 1, f"FAIL FP: {cm['FP']} != 1"
    assert cm["VN"] == 2, f"FAIL VN: {cm['VN']} != 2"
    assert cm["FN"] == 1, f"FAIL FN: {cm['FN']} != 1"
    assert cm["total"] == 6, f"FAIL total: {cm['total']} != 6"
    print(f"  ✓ VP={cm['VP']}, FP={cm['FP']}, "
          f"VN={cm['VN']}, FN={cm['FN']}, total={cm['total']}")

    # ── Test 2: Métricas manuales ───────────────────────
    print("\n── Test 2: Precision/Recall/F1 manual ──")
    # Precision = VP/(VP+FP) = 2/3
    # Recall    = VP/(VP+FN) = 2/3
    # F1        = 2*(2/3 * 2/3)/(2/3 + 2/3) = 2/3

    scores_test = [90, 85, 40, 20, 15, 75]
    m = metrics.calculate_all(y_real, y_pred, scores_test)

    expected_p = 2 / 3
    expected_r = 2 / 3
    expected_f1 = 2 / 3

    assert abs(m["precision"] - round(expected_p, 4)) < 0.001, (
        f"FAIL Precision: {m['precision']} != {expected_p:.4f}"
    )
    assert abs(m["recall"] - round(expected_r, 4)) < 0.001, (
        f"FAIL Recall: {m['recall']} != {expected_r:.4f}"
    )
    assert abs(m["f1_score"] - round(expected_f1, 4)) < 0.001, (
        f"FAIL F1: {m['f1_score']} != {expected_f1:.4f}"
    )
    print(f"  ✓ Precision={m['precision']:.4f} "
          f"(esperado {expected_p:.4f})")
    print(f"  ✓ Recall={m['recall']:.4f} "
          f"(esperado {expected_r:.4f})")
    print(f"  ✓ F1={m['f1_score']:.4f} "
          f"(esperado {expected_f1:.4f})")

    # ── Test 3: Verificación sklearn ────────────────────
    print("\n── Test 3: Manual == sklearn (delta < 0.001) ──")
    sk_p = precision_score(y_real, y_pred, zero_division=0)
    sk_r = recall_score(y_real, y_pred, zero_division=0)
    sk_f1 = sklearn_f1(y_real, y_pred, zero_division=0)

    delta_p = abs(m["precision"] - sk_p)
    delta_r = abs(m["recall"] - sk_r)
    delta_f1 = abs(m["f1_score"] - sk_f1)

    print(f"  Precision: manual={m['precision']:.4f}, "
          f"sklearn={sk_p:.4f}, delta={delta_p:.6f}")
    print(f"  Recall:    manual={m['recall']:.4f}, "
          f"sklearn={sk_r:.4f}, delta={delta_r:.6f}")
    print(f"  F1:        manual={m['f1_score']:.4f}, "
          f"sklearn={sk_f1:.4f}, delta={delta_f1:.6f}")
    assert delta_p < 0.001, "FAIL Precision delta"
    assert delta_r < 0.001, "FAIL Recall delta"
    assert delta_f1 < 0.001, "FAIL F1 delta"
    print("  ✓ Todas las deltas < 0.001")

    # ── Test 4: Costo asimétrico ────────────────────────
    print("\n── Test 4: Costo asimétrico ──")
    # costo = (FP*4 + FN*1) / total = (1*4 + 1*1) / 6 = 5/6
    expected_costo = (1 * 4 + 1 * 1) / 6
    assert abs(m["costo_asimetrico"] - round(expected_costo, 4)) < 0.001, (
        f"FAIL Costo: {m['costo_asimetrico']} "
        f"!= {expected_costo:.4f}"
    )
    print(f"  ✓ Costo asimétrico={m['costo_asimetrico']:.4f} "
          f"(esperado {expected_costo:.4f})")

    # ── Test 5: Interpretación ──────────────────────────
    print("\n── Test 5: Interpretación ──")
    texto = metrics.interpret(m)
    assert "Precision" in texto
    assert "Recall" in texto
    assert "RECOMENDACIONES" in texto
    print("  ✓ Interpretación generada correctamente")
    print(f"  (longitud: {len(texto)} caracteres)")

    # ── Test 6: Dashboard con datos sintéticos ──────────
    print("\n── Test 6: Dashboard (guardado a PNG) ──")
    with tempfile.NamedTemporaryFile(
        suffix=".png", delete=False
    ) as f:
        tmp_path = f.name

    fig = plots.plot_metrics_dashboard(
        m, y_real, scores_test, save_path=tmp_path
    )
    assert Path(tmp_path).exists(), f"FAIL: {tmp_path} no existe"
    size_kb = Path(tmp_path).stat().st_size / 1024
    print(f"  ✓ Dashboard guardado: {tmp_path}")
    print(f"  ✓ Tamaño: {size_kb:.0f} KB")
    Path(tmp_path).unlink()

    # ── Test 7: Caso extremo — todo aprobado ────────────
    print("\n── Test 7: Caso extremo (todo aprobado) ──")
    y_all_1 = [1, 1, 1, 0, 0]
    y_pred_all_1 = [1, 1, 1, 1, 1]
    s_all = [90, 85, 80, 75, 70]
    m2 = metrics.calculate_all(y_all_1, y_pred_all_1, s_all)
    assert m2["precision"] == 0.6, (
        f"FAIL: precision={m2['precision']}"
    )
    assert m2["recall"] == 1.0, (
        f"FAIL: recall={m2['recall']}"
    )
    assert m2["specificity"] == 0.0, (
        f"FAIL: specificity={m2['specificity']}"
    )
    print(f"  ✓ Todo aprobado: P={m2['precision']}, "
          f"R={m2['recall']}, Spec={m2['specificity']}")

    # ── Test 8: Caso extremo — todo rechazado ───────────
    print("\n── Test 8: Caso extremo (todo rechazado) ──")
    y_pred_all_0 = [0, 0, 0, 0, 0]
    m3 = metrics.calculate_all(y_all_1, y_pred_all_0, s_all)
    assert m3["precision"] == 0.0, (
        f"FAIL: precision={m3['precision']}"
    )
    assert m3["recall"] == 0.0, (
        f"FAIL: recall={m3['recall']}"
    )
    assert m3["specificity"] == 1.0, (
        f"FAIL: specificity={m3['specificity']}"
    )
    print(f"  ✓ Todo rechazado: P={m3['precision']}, "
          f"R={m3['recall']}, Spec={m3['specificity']}")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DE MÉTRICAS PASARON ✓")
    print(f"{'='*60}")


if __name__ == "__main__":
    _run_tests()
