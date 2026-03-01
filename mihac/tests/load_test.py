# ============================================================
# MIHAC v1.0 — Tests de Carga y Rendimiento
# tests/load_test.py
# ============================================================
# Pruebas de carga progresiva del motor de inferencia y la
# interfaz web. Mide latencia, throughput y estabilidad
# bajo volúmenes crecientes.
#
# Ejecución:
#   python -m pytest tests/load_test.py -v -s
#   python tests/load_test.py              (modo standalone)
# ============================================================

import sys
import time
import csv
import json
import statistics
import logging
from pathlib import Path
from datetime import datetime

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.engine import InferenceEngine
from core.validator import Validator
from core.scorer import ScoringEngine
from data.generate_demo_data import DemoDataGenerator

logger = logging.getLogger(__name__)

# ── Configuración ───────────────────────────────────────────

CARGAS = [10, 50, 100, 500, 1000]
OBJETIVO_LATENCIA_MS = 50       # latencia media < 50ms por eval
OBJETIVO_THROUGHPUT = 100       # evaluaciones/segundo mínimo
RESULTADO_DIR = _PROJECT_ROOT / "docs"


# ════════════════════════════════════════════════════════════
# UTILIDADES
# ════════════════════════════════════════════════════════════

def _generar_datos(n: int, seed: int = 42) -> list[dict]:
    """Genera N solicitudes aleatorias reproducibles."""
    gen = DemoDataGenerator()
    return gen.generate_batch(n, seed=seed)


def _medir_evaluacion(engine: InferenceEngine,
                       datos: list[dict]) -> dict:
    """Evalúa N solicitudes midiendo tiempos individuales.

    Returns:
        Dict con métricas: n, total_ms, media_ms, p50_ms,
        p95_ms, p99_ms, max_ms, min_ms, throughput,
        aprobados, rechazados, revision, errores.
    """
    tiempos: list[float] = []
    aprobados = rechazados = revision = errores = 0

    t_inicio = time.perf_counter()

    for d in datos:
        t0 = time.perf_counter()
        resultado = engine.evaluate(d)
        t1 = time.perf_counter()

        ms = (t1 - t0) * 1000
        tiempos.append(ms)

        dictamen = resultado.get("dictamen", "")
        if resultado.get("errores_validacion"):
            errores += 1
        elif dictamen == "APROBADO":
            aprobados += 1
        elif dictamen == "RECHAZADO":
            rechazados += 1
        elif dictamen == "REVISION_MANUAL":
            revision += 1

    t_total = (time.perf_counter() - t_inicio) * 1000
    n = len(datos)

    tiempos_sorted = sorted(tiempos)
    p50 = tiempos_sorted[int(n * 0.50)] if n > 0 else 0
    p95 = tiempos_sorted[int(min(n * 0.95, n - 1))] if n > 0 else 0
    p99 = tiempos_sorted[int(min(n * 0.99, n - 1))] if n > 0 else 0

    throughput = (n / (t_total / 1000)) if t_total > 0 else 0

    return {
        "n": n,
        "total_ms": round(t_total, 2),
        "media_ms": round(statistics.mean(tiempos), 3) if tiempos else 0,
        "p50_ms": round(p50, 3),
        "p95_ms": round(p95, 3),
        "p99_ms": round(p99, 3),
        "max_ms": round(max(tiempos), 3) if tiempos else 0,
        "min_ms": round(min(tiempos), 3) if tiempos else 0,
        "desv_std_ms": round(statistics.stdev(tiempos), 3) if len(tiempos) > 1 else 0,
        "throughput": round(throughput, 1),
        "aprobados": aprobados,
        "rechazados": rechazados,
        "revision": revision,
        "errores": errores,
    }


def _medir_validacion(n: int, seed: int = 42) -> dict:
    """Mide rendimiento del validador aislado."""
    datos = _generar_datos(n, seed)
    validator = Validator()
    tiempos: list[float] = []

    for d in datos:
        t0 = time.perf_counter()
        validator.sanitize(d)
        validator.validate(d)
        t1 = time.perf_counter()
        tiempos.append((t1 - t0) * 1000)

    return {
        "n": n,
        "media_ms": round(statistics.mean(tiempos), 3) if tiempos else 0,
        "max_ms": round(max(tiempos), 3) if tiempos else 0,
        "throughput": round(n / (sum(tiempos) / 1000), 1) if sum(tiempos) > 0 else 0,
    }


def _medir_scoring(n: int, seed: int = 42) -> dict:
    """Mide rendimiento del scorer aislado."""
    datos = _generar_datos(n, seed)
    scorer = ScoringEngine()
    tiempos: list[float] = []

    for d in datos:
        t0 = time.perf_counter()
        ingreso = d.get("ingreso_mensual", 1)
        deuda = d.get("total_deuda_actual", 0)
        dti, _ = scorer.calculate_dti(ingreso, deuda)
        scorer.calculate_subscores(d, dti)
        scorer.apply_rules(d, dti)
        t1 = time.perf_counter()
        tiempos.append((t1 - t0) * 1000)

    return {
        "n": n,
        "media_ms": round(statistics.mean(tiempos), 3) if tiempos else 0,
        "max_ms": round(max(tiempos), 3) if tiempos else 0,
        "throughput": round(n / (sum(tiempos) / 1000), 1) if sum(tiempos) > 0 else 0,
    }


# ════════════════════════════════════════════════════════════
# TESTS PYTEST
# ════════════════════════════════════════════════════════════

class TestCargaMotor:
    """Tests de carga del motor de inferencia."""

    def test_carga_10(self):
        """10 evaluaciones: warmup/baseline."""
        engine = InferenceEngine()
        datos = _generar_datos(10)
        m = _medir_evaluacion(engine, datos)
        assert m["n"] == 10
        assert m["media_ms"] < 200  # relajado para warmup

    def test_carga_100(self):
        """100 evaluaciones: carga normal."""
        engine = InferenceEngine()
        datos = _generar_datos(100)
        m = _medir_evaluacion(engine, datos)
        assert m["n"] == 100
        assert m["media_ms"] < OBJETIVO_LATENCIA_MS
        assert m["throughput"] > OBJETIVO_THROUGHPUT

    def test_carga_500(self):
        """500 evaluaciones: carga media."""
        engine = InferenceEngine()
        datos = _generar_datos(500)
        m = _medir_evaluacion(engine, datos)
        assert m["n"] == 500
        assert m["media_ms"] < OBJETIVO_LATENCIA_MS
        assert m["throughput"] > OBJETIVO_THROUGHPUT

    def test_carga_1000(self):
        """1000 evaluaciones: carga alta."""
        engine = InferenceEngine()
        datos = _generar_datos(1000)
        m = _medir_evaluacion(engine, datos)
        assert m["n"] == 1000
        assert m["media_ms"] < OBJETIVO_LATENCIA_MS
        assert m["throughput"] > OBJETIVO_THROUGHPUT
        # Distribución razonable
        total_validos = m["aprobados"] + m["rechazados"] + m["revision"]
        assert total_validos > 0

    def test_consistencia_resultados(self):
        """Los mismos datos siempre producen los mismos resultados."""
        engine1 = InferenceEngine()
        engine2 = InferenceEngine()
        datos = _generar_datos(50, seed=999)

        r1 = [engine1.evaluate(d)["score_final"] for d in datos]
        r2 = [engine2.evaluate(d)["score_final"] for d in datos]
        assert r1 == r2

    def test_sin_memory_leak(self):
        """Encadenar múltiples cargas sin degradación."""
        engine = InferenceEngine()
        medias = []

        for i in range(3):
            datos = _generar_datos(200, seed=i)
            m = _medir_evaluacion(engine, datos)
            medias.append(m["media_ms"])

        # La última tanda no debería ser > 3x la primera
        assert medias[-1] < medias[0] * 3


class TestCargaComponentes:
    """Tests de carga de componentes individuales."""

    def test_validador_1000(self):
        """1000 validaciones aisladas."""
        m = _medir_validacion(1000)
        assert m["media_ms"] < 5
        assert m["throughput"] > 500

    def test_scorer_1000(self):
        """1000 scorings aislados."""
        m = _medir_scoring(1000)
        assert m["media_ms"] < 10
        assert m["throughput"] > 200


class TestCargaWeb:
    """Tests de carga de la interfaz web (Flask test client)."""

    def _get_app(self):
        from app import create_app, db
        app = create_app("testing")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
        with app.app_context():
            db.create_all()
        return app

    def test_carga_web_formulario_100(self):
        """100 POSTs al formulario."""
        app = self._get_app()
        datos = _generar_datos(100)
        tiempos: list[float] = []

        with app.test_client() as client:
            for d in datos:
                form_data = {
                    "edad": d["edad"],
                    "ingreso_mensual": d["ingreso_mensual"],
                    "total_deuda_actual": d["total_deuda_actual"],
                    "historial_crediticio": str(d["historial_crediticio"]),
                    "antiguedad_laboral": d["antiguedad_laboral"],
                    "numero_dependientes": d["numero_dependientes"],
                    "tipo_vivienda": d["tipo_vivienda"],
                    "proposito_credito": d["proposito_credito"],
                    "monto_credito": d["monto_credito"],
                }
                t0 = time.perf_counter()
                resp = client.post("/", data=form_data, follow_redirects=True)
                t1 = time.perf_counter()
                tiempos.append((t1 - t0) * 1000)
                assert resp.status_code == 200

        media = statistics.mean(tiempos)
        assert media < 500, f"Latencia media web: {media:.1f}ms (objetivo <500ms)"

    def test_carga_web_dashboard_50(self):
        """50 GETs al dashboard con datos."""
        app = self._get_app()

        # Poblar BD
        with app.test_client() as client:
            for d in _generar_datos(20):
                client.post("/", data={
                    "edad": d["edad"],
                    "ingreso_mensual": d["ingreso_mensual"],
                    "total_deuda_actual": d["total_deuda_actual"],
                    "historial_crediticio": str(d["historial_crediticio"]),
                    "antiguedad_laboral": d["antiguedad_laboral"],
                    "numero_dependientes": d["numero_dependientes"],
                    "tipo_vivienda": d["tipo_vivienda"],
                    "proposito_credito": d["proposito_credito"],
                    "monto_credito": d["monto_credito"],
                }, follow_redirects=True)

        tiempos: list[float] = []
        with app.test_client() as client:
            for _ in range(50):
                t0 = time.perf_counter()
                resp = client.get("/dashboard")
                t1 = time.perf_counter()
                tiempos.append((t1 - t0) * 1000)
                assert resp.status_code == 200

        media = statistics.mean(tiempos)
        assert media < 200, f"Latencia dashboard: {media:.1f}ms (objetivo <200ms)"


# ════════════════════════════════════════════════════════════
# MODO STANDALONE — Reporte completo
# ════════════════════════════════════════════════════════════

def run_load_tests() -> dict:
    """Ejecuta la suite completa de carga y retorna resultados."""
    logging.basicConfig(
        level=logging.WARNING,
        format="%(asctime)s | %(name)s | %(message)s",
    )

    print("=" * 65)
    print("  MIHAC v1.0 — PRUEBAS DE CARGA Y RENDIMIENTO")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 65)

    resultados = {
        "fecha": datetime.now().isoformat(),
        "motor": [],
        "componentes": {},
        "web": {},
    }

    # ── 1. Carga progresiva del motor ────────────────────
    print("\n" + "─" * 65)
    print("  PRUEBA 1: Carga progresiva del Motor de Inferencia")
    print("─" * 65)
    print(f"  {'N':>6} │ {'Media':>8} │ {'P50':>8} │ {'P95':>8} │ "
          f"{'P99':>8} │ {'Max':>8} │ {'Thr/s':>7} │ {'A/Re/Rv':>10}")
    print(f"  {'─'*6}─┼─{'─'*8}─┼─{'─'*8}─┼─{'─'*8}─┼─"
          f"{'─'*8}─┼─{'─'*8}─┼─{'─'*7}─┼─{'─'*10}─")

    engine = InferenceEngine()

    for n in CARGAS:
        datos = _generar_datos(n, seed=42)
        m = _medir_evaluacion(engine, datos)
        resultados["motor"].append(m)

        arv = f"{m['aprobados']}/{m['rechazados']}/{m['revision']}"
        print(f"  {m['n']:>6} │ {m['media_ms']:>7.2f}ms │ {m['p50_ms']:>7.2f}ms │ "
              f"{m['p95_ms']:>7.2f}ms │ {m['p99_ms']:>7.2f}ms │ {m['max_ms']:>7.2f}ms │ "
              f"{m['throughput']:>7.0f} │ {arv:>10}")

    # ── 2. Componentes aislados ──────────────────────────
    print("\n" + "─" * 65)
    print("  PRUEBA 2: Rendimiento por Componente (N=1000)")
    print("─" * 65)

    val_m = _medir_validacion(1000)
    scr_m = _medir_scoring(1000)

    resultados["componentes"]["validador"] = val_m
    resultados["componentes"]["scorer"] = scr_m

    print(f"  Validador : media={val_m['media_ms']:.3f}ms | "
          f"max={val_m['max_ms']:.3f}ms | {val_m['throughput']:.0f} ops/s")
    print(f"  Scorer    : media={scr_m['media_ms']:.3f}ms | "
          f"max={scr_m['max_ms']:.3f}ms | {scr_m['throughput']:.0f} ops/s")

    # ── 3. Carga Web ─────────────────────────────────────
    print("\n" + "─" * 65)
    print("  PRUEBA 3: Carga de la Interfaz Web")
    print("─" * 65)

    try:
        from app import create_app, db
        app = create_app("testing")
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

        with app.app_context():
            db.create_all()

            with app.test_client() as client:
                # POST 50 evaluaciones
                datos_web = _generar_datos(50, seed=77)
                tiempos_post: list[float] = []

                for d in datos_web:
                    form_data = {
                        "edad": d["edad"],
                        "ingreso_mensual": d["ingreso_mensual"],
                        "total_deuda_actual": d["total_deuda_actual"],
                        "historial_crediticio": str(d["historial_crediticio"]),
                        "antiguedad_laboral": d["antiguedad_laboral"],
                        "numero_dependientes": d["numero_dependientes"],
                        "tipo_vivienda": d["tipo_vivienda"],
                        "proposito_credito": d["proposito_credito"],
                        "monto_credito": d["monto_credito"],
                    }
                    t0 = time.perf_counter()
                    resp = client.post("/", data=form_data, follow_redirects=True)
                    t1 = time.perf_counter()
                    tiempos_post.append((t1 - t0) * 1000)

                media_post = statistics.mean(tiempos_post)
                max_post = max(tiempos_post)

                # GET dashboard 30 veces
                tiempos_dash: list[float] = []
                for _ in range(30):
                    t0 = time.perf_counter()
                    client.get("/dashboard")
                    t1 = time.perf_counter()
                    tiempos_dash.append((t1 - t0) * 1000)

                media_dash = statistics.mean(tiempos_dash)

                resultados["web"] = {
                    "post_n": 50,
                    "post_media_ms": round(media_post, 2),
                    "post_max_ms": round(max_post, 2),
                    "dashboard_n": 30,
                    "dashboard_media_ms": round(media_dash, 2),
                }

                print(f"  POST /  (50 evals)  : media={media_post:.1f}ms | max={max_post:.1f}ms")
                print(f"  GET /dashboard (30x): media={media_dash:.1f}ms")
    except Exception as e:
        print(f"  ⚠ Error en pruebas web: {e}")

    # ── 4. Test de consistencia ──────────────────────────
    print("\n" + "─" * 65)
    print("  PRUEBA 4: Consistencia (misma entrada → misma salida)")
    print("─" * 65)

    eng1 = InferenceEngine()
    eng2 = InferenceEngine()
    datos_check = _generar_datos(100, seed=999)
    scores1 = [eng1.evaluate(d)["score_final"] for d in datos_check]
    scores2 = [eng2.evaluate(d)["score_final"] for d in datos_check]
    consistente = scores1 == scores2
    print(f"  100 evaluaciones x 2 instancias: {'✓ CONSISTENTE' if consistente else '✗ INCONSISTENTE'}")
    resultados["consistencia"] = consistente

    # ── Resumen ──────────────────────────────────────────
    ultimo = resultados["motor"][-1] if resultados["motor"] else {}
    print("\n" + "=" * 65)
    print("  RESUMEN DE RENDIMIENTO")
    print("=" * 65)
    print(f"  Motor (1000 evals):")
    print(f"    Latencia media : {ultimo.get('media_ms', 0):.2f} ms "
          f"({'✓' if ultimo.get('media_ms', 999) < OBJETIVO_LATENCIA_MS else '✗'} "
          f"objetivo <{OBJETIVO_LATENCIA_MS}ms)")
    print(f"    Throughput     : {ultimo.get('throughput', 0):.0f} evals/s "
          f"({'✓' if ultimo.get('throughput', 0) > OBJETIVO_THROUGHPUT else '✗'} "
          f"objetivo >{OBJETIVO_THROUGHPUT}/s)")
    print(f"    P95 latencia   : {ultimo.get('p95_ms', 0):.2f} ms")
    print(f"    P99 latencia   : {ultimo.get('p99_ms', 0):.2f} ms")
    print(f"  Consistencia     : {'✓ PASS' if consistente else '✗ FAIL'}")
    print("=" * 65)

    # ── Guardar resultados JSON ──────────────────────────
    RESULTADO_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTADO_DIR / "load_test_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)
    print(f"\n  Resultados guardados en: {json_path}")

    return resultados


if __name__ == "__main__":
    run_load_tests()
