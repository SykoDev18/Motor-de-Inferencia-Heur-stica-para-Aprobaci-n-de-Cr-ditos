# ============================================================
# MIHAC v1.0 — Script de Calibración Completa
# validation/run_calibration.py
# ============================================================
# Ejecuta el pipeline completo:
#   1. Descargar/cargar German Credit Dataset
#   2. Backtesting (1,000 registros)
#   3. Análisis de errores
#   4. Proponer ajustes de pesos
#   5. Simular impacto
#   6. Generar reporte
#   7. Crear backup y aplicar weights v2
# ============================================================

import sys
import json
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from validation.backtesting import Backtester
from validation.calibrator import WeightCalibrator
from data.mapper import GermanCreditMapper


def main():
    print("=" * 60)
    print("MIHAC — Pipeline Completo de Calibración")
    print("=" * 60)

    # ── PASO 1: Backtesting ─────────────────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 1: BACKTESTING                     ║")
    print("╚══════════════════════════════════════════╝")

    bt = Backtester()
    reporte_bt = bt.run(data_path=None)  # UCI download

    # Guardar artefactos de backtesting
    bt_dir = str(_PROJECT_ROOT / "reports" / "backtesting")
    rutas_bt = bt.save_report(bt_dir)

    # ── PASO 2: Calibración ─────────────────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 2: ANÁLISIS DE ERRORES             ║")
    print("╚══════════════════════════════════════════╝")

    cal = WeightCalibrator()
    analisis = cal.analyze_errors(bt.results_df)

    print(f"\nTotal: {analisis['total']}")
    print(f"FP: {analisis['fp']['n']}")
    print(f"FN: {analisis['fn']['n']}")
    print(f"VP: {analisis['vp']['n']}")
    print(f"VN: {analisis['vn']['n']}")

    print("\nVariables críticas:")
    for vc in analisis.get("variables_criticas", []):
        print(
            f"  {vc['variable']:25s} "
            f"Criticidad={vc['criticidad']:.2f}  "
            f"FP diff={vc['diff_fp_pct']:.0f}%  "
            f"FN diff={vc['diff_fn_pct']:.0f}%"
        )

    print("\nAnálisis de umbrales:")
    umbral_info = analisis["umbrales_analisis"]
    print(f"  Umbral óptimo (costo): {umbral_info['umbral_optimo_costo']}")
    for u in sorted(umbral_info["por_umbral"].keys()):
        r = umbral_info["por_umbral"][u]
        print(
            f"  U={u}: Acc={r['accuracy']:.3f} "
            f"Prec={r['precision']:.3f} "
            f"Rec={r['recall']:.3f} "
            f"F1={r['f1_score']:.3f} "
            f"Costo={r['costo_asimetrico']:.3f} "
            f"FP={r['fp']} FN={r['fn']}"
        )

    # ── PASO 3: Propuestas ──────────────────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 3: PROPUESTAS DE AJUSTE            ║")
    print("╚══════════════════════════════════════════╝")

    propuestas = cal.propose_adjustments(analisis)

    print(f"\nPesos actuales: {propuestas['pesos_actuales']}")
    print(f"Pesos nuevos:   {propuestas['pesos_nuevos']}")
    print(f"Umbral:         {propuestas['umbral_actual']} → {propuestas['umbral_propuesto']}")

    if propuestas["cambios_pesos"]:
        print("\nCambios propuestos:")
        for c in propuestas["cambios_pesos"]:
            print(f"  {c['variable']}: {c['peso_anterior']:.2f} → {c['peso_nuevo']:.2f} ({c['razon']})")
    else:
        print("\nNo se proponen cambios de pesos.")

    # ── PASO 4: Simulación ──────────────────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 4: SIMULACIÓN DE IMPACTO           ║")
    print("╚══════════════════════════════════════════╝")

    mapper = GermanCreditMapper()
    df = mapper.load_and_transform(None)
    datos_mihac = mapper.to_mihac_dicts(df)
    y_real = df["etiqueta_binaria"].values

    comparacion = cal.simulate(
        propuestas, datos_mihac, y_real, verbose=True
    )

    # ── PASO 5: Reporte ─────────────────────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 5: REPORTE DE CALIBRACIÓN          ║")
    print("╚══════════════════════════════════════════╝")

    reporte_texto = cal.generate_report(
        analisis, propuestas, comparacion
    )
    print(reporte_texto)

    # Guardar reporte
    ruta_reporte = cal.save_report(
        reporte_texto,
        str(_PROJECT_ROOT / "reports" / "calibration_report.txt"),
    )
    print(f"\n✓ Reporte guardado: {ruta_reporte}")

    # ── PASO 6: Aplicar (backup + v2) ───────────────────
    print("\n╔══════════════════════════════════════════╗")
    print("║  FASE 6: BACKUP v1 + APLICAR PESOS v2    ║")
    print("╚══════════════════════════════════════════╝")

    rutas_pesos = cal.apply_weights(propuestas, backup=True)

    for nombre, ruta in rutas_pesos.items():
        print(f"  {nombre}: {ruta}")

    # Verificar
    weights_path = _PROJECT_ROOT / "knowledge" / "weights.json"
    with open(weights_path, "r", encoding="utf-8") as f:
        w = json.load(f)
    print(f"\n  Versión: {w['_meta'].get('version', 'v1')}")
    print(f"  Pesos finales:")
    for k, v in w["pesos"].items():
        print(f"    {k}: {v['peso']}")

    print(f"\n{'='*60}")
    print("CALIBRACIÓN COMPLETA ✓")
    print(f"{'='*60}")

    return reporte_bt, analisis, propuestas, comparacion


if __name__ == "__main__":
    main()
