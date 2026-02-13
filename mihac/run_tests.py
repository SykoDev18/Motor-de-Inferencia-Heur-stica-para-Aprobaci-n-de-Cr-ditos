# ============================================================
# MIHAC v1.0 — Runner de Tests de Integración
# run_tests.py
# ============================================================
# Ejecuta todos los tests de los 4 módulos del núcleo en
# secuencia y reporta PASS o FAIL para cada caso.
#
# Uso:  python run_tests.py
# ============================================================

import sys
import logging
from pathlib import Path

# Asegurar ruta del proyecto
_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.validator import Validator
from core.scorer import ScoringEngine
from core.explainer import Explainer
from core.engine import InferenceEngine

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s | %(name)s | %(message)s",
)

# ── Datos de referencia ─────────────────────────────────────

CASO_APROBADO = {
    "edad": 35,
    "ingreso_mensual": 25000.0,
    "total_deuda_actual": 4000.0,
    "historial_crediticio": 2,
    "antiguedad_laboral": 7,
    "numero_dependientes": 1,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Negocio",
    "monto_credito": 15000.0,
}

CASO_RECHAZADO = {
    "edad": 19,
    "ingreso_mensual": 8000.0,
    "total_deuda_actual": 5500.0,
    "historial_crediticio": 0,
    "antiguedad_laboral": 0,
    "numero_dependientes": 3,
    "tipo_vivienda": "Rentada",
    "proposito_credito": "Vacaciones",
    "monto_credito": 12000.0,
}

CASO_REVISION = {
    "edad": 28,
    "ingreso_mensual": 15000.0,
    "total_deuda_actual": 3000.0,
    "historial_crediticio": 1,
    "antiguedad_laboral": 2,
    "numero_dependientes": 1,
    "tipo_vivienda": "Familiar",
    "proposito_credito": "Consumo",
    "monto_credito": 10000.0,
}


# ── Utilidades de test ──────────────────────────────────────

_passed = 0
_failed = 0


def report(nombre: str, ok: bool, detalle: str = ""):
    """Imprime resultado de un test."""
    global _passed, _failed
    if ok:
        _passed += 1
        print(f"  ✓ PASS  {nombre}")
    else:
        _failed += 1
        print(f"  ✗ FAIL  {nombre}")
        if detalle:
            print(f"          → {detalle}")


# ════════════════════════════════════════════════════════════
# SUITE 1: VALIDATOR
# ════════════════════════════════════════════════════════════

def test_validator():
    """Tests del módulo Validator."""
    print("\n" + "─" * 60)
    print("SUITE 1: core/validator.py")
    print("─" * 60)

    v = Validator()

    # T1.1 Datos válidos
    ok, errs = v.validate(CASO_APROBADO)
    report("Datos válidos → (True, [])", ok and errs == [])

    # T1.2 Campo faltante
    incompleto = {k: v for k, v in CASO_APROBADO.items()
                  if k != "edad"}
    ok, errs = v.validate(incompleto)
    report(
        "Campo faltante → error",
        not ok and any("faltante" in e for e in errs),
    )

    # T1.3 Edad fuera de rango
    ok, errs = v.validate({**CASO_APROBADO, "edad": 17})
    report(
        "Edad=17 → fuera de rango",
        not ok and any("Edad fuera" in e for e in errs),
    )

    # T1.4 Incoherencia edad/antigüedad
    ok, errs = v.validate(
        {**CASO_APROBADO, "edad": 22,
         "antiguedad_laboral": 15}
    )
    report(
        "Antigüedad > edad-15 → incoherencia",
        not ok and any("Incoherencia" in e for e in errs),
    )

    # T1.5 Múltiples errores simultáneos
    peor = {
        "edad": 10, "ingreso_mensual": -1.0,
        "total_deuda_actual": -5.0,
        "historial_crediticio": 9,
        "antiguedad_laboral": 50,
        "numero_dependientes": 20,
        "tipo_vivienda": "Cueva",
        "proposito_credito": "Casino",
        "monto_credito": 999999.0,
    }
    ok, errs = v.validate(peor)
    report(
        f"Múltiples errores → {len(errs)} detectados",
        not ok and len(errs) >= 5,
    )

    # T1.6 Sanitización
    sucio = {
        "edad": " 35 ", "ingreso_mensual": "$25,000",
        "total_deuda_actual": "4000",
        "historial_crediticio": 2.0,
        "antiguedad_laboral": "7",
        "numero_dependientes": "1",
        "tipo_vivienda": " propia ",
        "proposito_credito": "negocio",
        "monto_credito": "$15,000",
    }
    limpio = v.sanitize(sucio)
    ok, errs = v.validate(limpio)
    report("Sanitización → datos válidos", ok)


# ════════════════════════════════════════════════════════════
# SUITE 2: SCORER
# ════════════════════════════════════════════════════════════

def test_scorer():
    """Tests del módulo ScoringEngine."""
    print("\n" + "─" * 60)
    print("SUITE 2: core/scorer.py")
    print("─" * 60)

    s = ScoringEngine()

    # T2.1 Carga de reglas
    report(
        f"Reglas cargadas: {len(s._reglas)}",
        len(s._reglas) == 15,
        f"Esperadas 15, obtenidas {len(s._reglas)}",
    )

    # T2.2 DTI cálculos
    dti, c = s.calculate_dti(25000, 4000)
    report(
        f"DTI 4000/25000 = {dti:.2%} ({c})",
        c == "BAJO",
    )

    dti, c = s.calculate_dti(8000, 5500)
    report(
        f"DTI 5500/8000 = {dti:.2%} ({c})",
        c == "CRITICO",
    )

    # T2.3 Caso 1 → APROBADO
    dti1, c1 = s.calculate_dti(25000, 4000)
    sub1 = s.calculate_subscores(CASO_APROBADO, dti1)
    r1 = s.apply_rules(CASO_APROBADO, dti1)
    score1, u1 = s.calculate_final_score(
        sub1, r1, CASO_APROBADO["monto_credito"]
    )
    d1 = s.get_dictamen(score1, u1, c1)
    report(
        f"Caso ideal: score={score1}, dict={d1}",
        d1 == "APROBADO",
    )

    # T2.4 Caso 2 → RECHAZADO
    dti2, c2 = s.calculate_dti(8000, 5500)
    sub2 = s.calculate_subscores(CASO_RECHAZADO, dti2)
    r2 = s.apply_rules(CASO_RECHAZADO, dti2)
    score2, u2 = s.calculate_final_score(
        sub2, r2, CASO_RECHAZADO["monto_credito"]
    )
    d2 = s.get_dictamen(score2, u2, c2)
    report(
        f"Caso riesgo: score={score2}, dict={d2}",
        d2 == "RECHAZADO",
    )

    # T2.5 Caso 3 → REVISION_MANUAL
    dti3, c3 = s.calculate_dti(15000, 3000)
    sub3 = s.calculate_subscores(CASO_REVISION, dti3)
    r3 = s.apply_rules(CASO_REVISION, dti3)
    score3, u3 = s.calculate_final_score(
        sub3, r3, CASO_REVISION["monto_credito"]
    )
    d3 = s.get_dictamen(score3, u3, c3)
    report(
        f"Caso gris: score={score3}, dict={d3}",
        d3 == "REVISION_MANUAL",
    )


# ════════════════════════════════════════════════════════════
# SUITE 3: EXPLAINER
# ════════════════════════════════════════════════════════════

def test_explainer():
    """Tests del módulo Explainer."""
    print("\n" + "─" * 60)
    print("SUITE 3: core/explainer.py")
    print("─" * 60)

    s = ScoringEngine()
    e = Explainer()

    casos = [
        ("APROBADO", CASO_APROBADO, "recomienda proceder"),
        ("RECHAZADO", CASO_RECHAZADO, None),
        ("REVISION", CASO_REVISION, "zona de análisis"),
    ]

    for nombre, datos, verificar in casos:
        dti, c = s.calculate_dti(
            datos["ingreso_mensual"],
            datos["total_deuda_actual"],
        )
        sub = s.calculate_subscores(datos, dti)
        reglas = s.apply_rules(datos, dti)
        score, umbral = s.calculate_final_score(
            sub, reglas, datos["monto_credito"]
        )
        dictamen = s.get_dictamen(score, umbral, c)

        resultado = {
            "score_final": score,
            "dti_ratio": dti,
            "dti_clasificacion": c,
            "sub_scores": sub,
            "dictamen": dictamen,
            "umbral_aplicado": umbral,
            "reglas_activadas": reglas,
            "compensaciones": [
                r for r in reglas
                if r["tipo"] == "compensacion"
            ],
        }

        texto = e.generate(datos, resultado)
        corto = e.generate_short(datos, resultado)
        lineas = texto.split("\n")

        ok_lineas = len(lineas) >= 20
        ok_texto = True
        if verificar:
            ok_texto = verificar in texto

        report(
            f"Explicación {nombre}: "
            f"{len(lineas)} líneas, texto={'OK' if ok_texto else 'FAIL'}",
            ok_lineas and ok_texto,
        )

        report(
            f"Resumen corto {nombre}: {corto[:50]}...",
            len(corto) > 10,
        )


# ════════════════════════════════════════════════════════════
# SUITE 4: ENGINE (Integración completa)
# ════════════════════════════════════════════════════════════

def test_engine():
    """Tests de integración del InferenceEngine."""
    print("\n" + "─" * 60)
    print("SUITE 4: core/engine.py (Integración)")
    print("─" * 60)

    engine = InferenceEngine()

    # T4.1-3 Evaluaciones individuales
    for nombre, datos, esperado in [
        ("ideal", CASO_APROBADO, "APROBADO"),
        ("riesgo", CASO_RECHAZADO, "RECHAZADO"),
        ("gris", CASO_REVISION, "REVISION_MANUAL"),
    ]:
        r = engine.evaluate(datos)
        report(
            f"evaluate({nombre}): "
            f"score={r['score_final']}, "
            f"dict={r['dictamen']}",
            r["dictamen"] == esperado
            and r["errores_validacion"] == [],
        )

    # T4.4 Batch
    lote = engine.evaluate_batch(
        [CASO_APROBADO, CASO_RECHAZADO, CASO_REVISION]
    )
    report(
        f"evaluate_batch: {len(lote)} resultados",
        len(lote) == 3
        and all("indice" in r for r in lote),
    )

    # T4.5 Stats
    st = engine.stats
    report(
        f"stats: {st['total_evaluaciones']} evals, "
        f"tasa={st['tasa_aprobacion']}%",
        st["total_evaluaciones"] == 6,
    )

    # T4.6 Manejo de errores
    r_err = engine.evaluate({"edad": 10})
    report(
        "Datos inválidos → errores sin excepción",
        r_err["errores_validacion"] != []
        and r_err["dictamen"] == "RECHAZADO",
    )

    # T4.7 Log creado
    log_path = _PROJECT_ROOT / "mihac_evaluations.log"
    report(
        "mihac_evaluations.log existe",
        log_path.exists(),
    )


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("  MIHAC v1.0 — SUITE COMPLETA DE TESTS")
    print("=" * 60)

    test_validator()
    test_scorer()
    test_explainer()
    test_engine()

    print("\n" + "=" * 60)
    total = _passed + _failed
    print(
        f"  RESULTADO FINAL: {_passed}/{total} tests "
        f"pasaron"
    )
    if _failed > 0:
        print(f"  ⚠ {_failed} test(s) fallaron")
    else:
        print("  ✓ TODOS LOS TESTS PASARON")
    print("=" * 60)

    sys.exit(1 if _failed > 0 else 0)
