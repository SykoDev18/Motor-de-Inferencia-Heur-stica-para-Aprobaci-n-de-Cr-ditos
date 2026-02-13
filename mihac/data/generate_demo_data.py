# ============================================================
# MIHAC v1.0 — Generador de Datos Demo / Sintéticos
# data/generate_demo_data.py
# ============================================================
# Produce perfiles sintéticos pre-diseñados para demostrar
# cada ruta lógica del motor de inferencia, más un generador
# de lotes aleatorios para stress-testing.
#
# 7 perfiles nominales que cubren:
#   1. Cliente ideal → APROBADO
#   2. Alto riesgo   → RECHAZADO
#   3. Zona gris     → REVISION_MANUAL
#   4. Heurística    → compensación en acción
#   5. DTI crítico   → rechazo automático por DTI
#   6. Joven prometedor → bueno pero joven
#   7. Monto alto exigente → umbral 85
# ============================================================

import sys
import csv
import random
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ── Constantes ──────────────────────────────────────────────

TIPOS_VIVIENDA = ["Propia", "Familiar", "Rentada"]
PROPOSITOS = [
    "Negocio", "Educacion", "Consumo",
    "Emergencia", "Vacaciones",
]


# ════════════════════════════════════════════════════════════
# 7 PERFILES NOMINALES
# ════════════════════════════════════════════════════════════

_PROFILES: dict[str, dict[str, Any]] = {
    # ── 1. Cliente ideal ────────────────────────────────
    "cliente_ideal": {
        "nombre": "Cliente Ideal",
        "descripcion": (
            "Perfil impecable: ingreso alto, sin deudas, "
            "historial bueno, propio y estable. "
            "Espera APROBADO con score ~100."
        ),
        "dictamen_esperado": "APROBADO",
        "datos": {
            "edad": 45,
            "ingreso_mensual": 35000.0,
            "total_deuda_actual": 2000.0,
            "historial_crediticio": 2,
            "antiguedad_laboral": 15,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 10000.0,
        },
    },

    # ── 2. Alto riesgo ──────────────────────────────────
    "alto_riesgo": {
        "nombre": "Alto Riesgo",
        "descripcion": (
            "Todo mal: ingreso mínimo, deudas enormes, "
            "historial malo, joven y desempleado. "
            "Espera RECHAZADO con score ~0."
        ),
        "dictamen_esperado": "RECHAZADO",
        "datos": {
            "edad": 19,
            "ingreso_mensual": 4000.0,
            "total_deuda_actual": 8000.0,
            "historial_crediticio": 0,
            "antiguedad_laboral": 0,
            "numero_dependientes": 3,
            "tipo_vivienda": "Rentada",
            "proposito_credito": "Vacaciones",
            "monto_credito": 15000.0,
        },
    },

    # ── 3. Zona gris ────────────────────────────────────
    "zona_gris": {
        "nombre": "Zona Gris (Revisión Manual)",
        "descripcion": (
            "Perfil intermedio con señales mixtas. "
            "Score entre 60–79 → REVISION_MANUAL. "
            "El asesor humano decide."
        ),
        "dictamen_esperado": "REVISION_MANUAL",
        "datos": {
            "edad": 30,
            "ingreso_mensual": 15000.0,
            "total_deuda_actual": 3000.0,
            "historial_crediticio": 1,
            "antiguedad_laboral": 3,
            "numero_dependientes": 2,
            "tipo_vivienda": "Familiar",
            "proposito_credito": "Consumo",
            "monto_credito": 8000.0,
        },
    },

    # ── 4. Heurística en acción ─────────────────────────
    "heuristica_en_accion": {
        "nombre": "Heurística en Acción",
        "descripcion": (
            "Demuestra las reglas de compensación: "
            "antigüedad alta compensa historial neutro, "
            "vivienda propia compensa DTI moderado. "
            "Las reglas R011-R015 entran en acción."
        ),
        "dictamen_esperado": "APROBADO",
        "datos": {
            "edad": 50,
            "ingreso_mensual": 20000.0,
            "total_deuda_actual": 6000.0,
            "historial_crediticio": 1,
            "antiguedad_laboral": 12,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 12000.0,
        },
    },

    # ── 5. DTI crítico ──────────────────────────────────
    "dti_critico": {
        "nombre": "DTI Crítico (Rechazo Automático)",
        "descripcion": (
            "Aunque el cliente tiene buen historial, "
            "su DTI > 60% dispara rechazo automático. "
            "Demuestra la regla DTI CRITICO del motor."
        ),
        "dictamen_esperado": "RECHAZADO",
        "datos": {
            "edad": 40,
            "ingreso_mensual": 10000.0,
            "total_deuda_actual": 7000.0,
            "historial_crediticio": 2,
            "antiguedad_laboral": 10,
            "numero_dependientes": 0,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 5000.0,
        },
    },

    # ── 6. Joven prometedor ─────────────────────────────
    "joven_prometedor": {
        "nombre": "Joven Prometedor",
        "descripcion": (
            "Joven con poco historial pero ingreso "
            "decente y propósito productivo. "
            "Puede caer en REVISION_MANUAL o APROBADO "
            "dependiendo de la heurística."
        ),
        "dictamen_esperado": "REVISION_MANUAL",
        "datos": {
            "edad": 22,
            "ingreso_mensual": 12000.0,
            "total_deuda_actual": 1500.0,
            "historial_crediticio": 1,
            "antiguedad_laboral": 1,
            "numero_dependientes": 0,
            "tipo_vivienda": "Familiar",
            "proposito_credito": "Educacion",
            "monto_credito": 5000.0,
        },
    },

    # ── 7. Monto alto exigente ──────────────────────────
    "monto_alto_exigente": {
        "nombre": "Monto Alto Exigente (Umbral 85)",
        "descripcion": (
            "Monto > $20,000 activa el umbral elevado "
            "de 85 puntos. Buen perfil que con umbral "
            "normal aprobaría, pero con 85 puede quedar "
            "en REVISION_MANUAL."
        ),
        "dictamen_esperado": "REVISION_MANUAL",
        "datos": {
            "edad": 38,
            "ingreso_mensual": 25000.0,
            "total_deuda_actual": 4000.0,
            "historial_crediticio": 2,
            "antiguedad_laboral": 6,
            "numero_dependientes": 1,
            "tipo_vivienda": "Propia",
            "proposito_credito": "Negocio",
            "monto_credito": 25000.0,
        },
    },
}


# ════════════════════════════════════════════════════════════
# CLASE DemoDataGenerator
# ════════════════════════════════════════════════════════════

class DemoDataGenerator:
    """Generador de datos sintéticos para MIHAC.

    Provee perfiles pre-diseñados (nominales) y lotes
    aleatorios para pruebas y demostraciones.

    Attributes:
        profiles: Dict de perfiles nominales.

    Ejemplo::

        gen = DemoDataGenerator()
        ideal = gen.get_profile("cliente_ideal")
        batch = gen.generate_batch(100)
    """

    def __init__(self) -> None:
        """Inicializa con los 7 perfiles nominales."""
        self.profiles = _PROFILES

    # ── Acceso a perfiles nominales ─────────────────────

    def get_profile(
        self, nombre: str
    ) -> dict[str, Any]:
        """Retorna un perfil nominal por nombre.

        Args:
            nombre: Clave del perfil (ej. "cliente_ideal").

        Returns:
            Dict con nombre, descripcion, dictamen_esperado
            y datos.

        Raises:
            KeyError: Si el nombre no existe.

        Ejemplo::

            p = gen.get_profile("dti_critico")
            print(p["datos"]["total_deuda_actual"])
        """
        if nombre not in self.profiles:
            disponibles = list(self.profiles.keys())
            raise KeyError(
                f"Perfil '{nombre}' no encontrado. "
                f"Disponibles: {disponibles}"
            )
        return self.profiles[nombre]

    def get_all_profiles(
        self,
    ) -> list[dict[str, Any]]:
        """Retorna todos los perfiles nominales.

        Returns:
            Lista de 7 dicts con los perfiles.

        Ejemplo::

            for p in gen.get_all_profiles():
                print(p["nombre"], p["dictamen_esperado"])
        """
        return list(self.profiles.values())

    def list_profile_names(self) -> list[str]:
        """Lista los nombres (claves) de perfiles.

        Returns:
            ["cliente_ideal", "alto_riesgo", ...]
        """
        return list(self.profiles.keys())

    # ── Generación aleatoria ────────────────────────────

    def generate_batch(
        self,
        n: int = 100,
        seed: int | None = 42,
    ) -> list[dict[str, Any]]:
        """Genera N solicitudes aleatorias.

        Distribución controllada para generar un mix
        realista de buenos, mediocres y malos perfiles.

        Args:
            n: Número de solicitudes a generar.
            seed: Semilla para reproducibilidad.

        Returns:
            Lista de N dicts MIHAC con datos variados.

        Ejemplo::

            batch = gen.generate_batch(500, seed=123)
            print(len(batch))  # 500
        """
        if seed is not None:
            random.seed(seed)

        batch: list[dict[str, Any]] = []
        for _ in range(n):
            batch.append(self._random_solicitud())
        return batch

    def _random_solicitud(self) -> dict[str, Any]:
        """Genera una solicitud aleatoria realista.

        Distribución:
          - 40% perfiles buenos (ingreso alto, deuda baja)
          - 30% perfiles medios
          - 30% perfiles riesgosos

        Returns:
            Dict con 9 variables MIHAC.
        """
        # Determinar categoría
        r = random.random()
        if r < 0.4:
            return self._gen_perfil_bueno()
        elif r < 0.7:
            return self._gen_perfil_medio()
        else:
            return self._gen_perfil_malo()

    def _gen_perfil_bueno(self) -> dict[str, Any]:
        """Perfil con buenas características."""
        ingreso = random.uniform(15000, 50000)
        return {
            "edad": random.randint(30, 60),
            "ingreso_mensual": round(ingreso, 2),
            "total_deuda_actual": round(
                ingreso * random.uniform(0.05, 0.20), 2
            ),
            "historial_crediticio": random.choice([1, 2, 2]),
            "antiguedad_laboral": random.randint(5, 20),
            "numero_dependientes": random.randint(0, 2),
            "tipo_vivienda": random.choice(
                ["Propia", "Propia", "Familiar"]
            ),
            "proposito_credito": random.choice(
                ["Negocio", "Educacion", "Negocio"]
            ),
            "monto_credito": round(
                random.uniform(3000, 15000), 2
            ),
        }

    def _gen_perfil_medio(self) -> dict[str, Any]:
        """Perfil con características mixtas."""
        ingreso = random.uniform(8000, 25000)
        return {
            "edad": random.randint(25, 50),
            "ingreso_mensual": round(ingreso, 2),
            "total_deuda_actual": round(
                ingreso * random.uniform(0.15, 0.40), 2
            ),
            "historial_crediticio": random.choice(
                [0, 1, 1, 1]
            ),
            "antiguedad_laboral": random.randint(1, 8),
            "numero_dependientes": random.randint(0, 3),
            "tipo_vivienda": random.choice(
                TIPOS_VIVIENDA
            ),
            "proposito_credito": random.choice(
                PROPOSITOS
            ),
            "monto_credito": round(
                random.uniform(5000, 20000), 2
            ),
        }

    def _gen_perfil_malo(self) -> dict[str, Any]:
        """Perfil con características riesgosas."""
        ingreso = random.uniform(3000, 12000)
        return {
            "edad": random.randint(18, 30),
            "ingreso_mensual": round(ingreso, 2),
            "total_deuda_actual": round(
                ingreso * random.uniform(0.35, 0.75), 2
            ),
            "historial_crediticio": random.choice(
                [0, 0, 0, 1]
            ),
            "antiguedad_laboral": random.randint(0, 3),
            "numero_dependientes": random.randint(1, 5),
            "tipo_vivienda": random.choice(
                ["Rentada", "Rentada", "Familiar"]
            ),
            "proposito_credito": random.choice(
                ["Vacaciones", "Consumo", "Emergencia"]
            ),
            "monto_credito": round(
                random.uniform(8000, 30000), 2
            ),
        }

    # ── Escenarios especiales ───────────────────────────

    def generate_scenario(
        self,
        scenario: str,
        n: int = 10,
        seed: int | None = 42,
    ) -> list[dict[str, Any]]:
        """Genera N solicitudes para un escenario específico.

        Escenarios disponibles:
          - "todos_aprobados"   : perfil ideal
          - "todos_rechazados"  : perfil de alto riesgo
          - "mixto"             : mezcla equilibrada
          - "dti_extremo"       : DTI > 60%
          - "montos_altos"      : monto > 20,000

        Args:
            scenario: Nombre del escenario.
            n: Número de solicitudes.
            seed: Semilla.

        Returns:
            Lista de dicts con datos del escenario.

        Raises:
            ValueError: Si el escenario no existe.

        Ejemplo::

            extremos = gen.generate_scenario(
                "dti_extremo", 50
            )
        """
        if seed is not None:
            random.seed(seed)

        generators = {
            "todos_aprobados": self._gen_perfil_bueno,
            "todos_rechazados": self._gen_perfil_malo,
            "mixto": self._random_solicitud,
            "dti_extremo": self._gen_dti_extremo,
            "montos_altos": self._gen_monto_alto,
        }

        if scenario not in generators:
            raise ValueError(
                f"Escenario '{scenario}' no encontrado. "
                f"Disponibles: {list(generators.keys())}"
            )

        gen_fn = generators[scenario]
        return [gen_fn() for _ in range(n)]

    def _gen_dti_extremo(self) -> dict[str, Any]:
        """Perfil con DTI > 60%."""
        ingreso = random.uniform(5000, 15000)
        return {
            "edad": random.randint(25, 55),
            "ingreso_mensual": round(ingreso, 2),
            "total_deuda_actual": round(
                ingreso * random.uniform(0.65, 0.90), 2
            ),
            "historial_crediticio": random.choice(
                [0, 1, 2]
            ),
            "antiguedad_laboral": random.randint(1, 10),
            "numero_dependientes": random.randint(0, 3),
            "tipo_vivienda": random.choice(
                TIPOS_VIVIENDA
            ),
            "proposito_credito": random.choice(
                PROPOSITOS
            ),
            "monto_credito": round(
                random.uniform(3000, 15000), 2
            ),
        }

    def _gen_monto_alto(self) -> dict[str, Any]:
        """Perfil con monto > $20,000 (umbral 85)."""
        ingreso = random.uniform(20000, 50000)
        return {
            "edad": random.randint(30, 55),
            "ingreso_mensual": round(ingreso, 2),
            "total_deuda_actual": round(
                ingreso * random.uniform(0.05, 0.30), 2
            ),
            "historial_crediticio": random.choice(
                [1, 2, 2]
            ),
            "antiguedad_laboral": random.randint(3, 15),
            "numero_dependientes": random.randint(0, 2),
            "tipo_vivienda": random.choice(
                ["Propia", "Propia", "Familiar"]
            ),
            "proposito_credito": random.choice(
                ["Negocio", "Educacion"]
            ),
            "monto_credito": round(
                random.uniform(21000, 50000), 2
            ),
        }

    # ── Exportación ─────────────────────────────────────

    def export_to_csv(
        self,
        data: list[dict[str, Any]],
        filepath: str | None = None,
    ) -> str:
        """Exporta datos a CSV.

        Si no se proporciona filepath, guarda en
        data/demo_batch.csv.

        Args:
            data: Lista de dicts MIHAC.
            filepath: Ruta de salida (opcional).

        Returns:
            Ruta absoluta del archivo creado.

        Ejemplo::

            path = gen.export_to_csv(batch, "mi_batch.csv")
        """
        if filepath is None:
            filepath = str(
                _PROJECT_ROOT / "data" / "demo_batch.csv"
            )

        ruta = Path(filepath)
        ruta.parent.mkdir(parents=True, exist_ok=True)

        campos = [
            "edad", "ingreso_mensual", "total_deuda_actual",
            "historial_crediticio", "antiguedad_laboral",
            "numero_dependientes", "tipo_vivienda",
            "proposito_credito", "monto_credito",
        ]

        with open(ruta, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=campos)
            writer.writeheader()
            for row in data:
                writer.writerow(
                    {k: row[k] for k in campos}
                )

        logger.info("Exportados %d registros a %s",
                     len(data), ruta)
        return str(ruta.resolve())


# ════════════════════════════════════════════════════════════
# DEMO SCRIPT — evalúa los 7 perfiles con el motor
# ════════════════════════════════════════════════════════════

# Colores ANSI para terminal
_COLORES = {
    "APROBADO":        "\033[92m",  # verde
    "REVISION_MANUAL": "\033[93m",  # amarillo
    "RECHAZADO":       "\033[91m",  # rojo
    "RESET":           "\033[0m",
    "BOLD":            "\033[1m",
    "DIM":             "\033[2m",
}


def demo_script() -> None:
    """Ejecuta la demostración completa de MIHAC.

    Importa InferenceEngine, evalúa los 7 perfiles
    nominales y muestra los resultados con colores.
    Ideal para presentaciones y demos de tesis.

    Ejemplo::

        from mihac.data.generate_demo_data import demo_script
        demo_script()
    """
    # Importación local para evitar dependencia circular
    sys.path.insert(0, str(_PROJECT_ROOT.parent))

    try:
        from mihac.core.engine import InferenceEngine
    except ImportError:
        print("ERROR: No se puede importar InferenceEngine.")
        print("Ejecuta desde la raíz del proyecto:")
        print("  python -m mihac.data.generate_demo_data")
        return

    engine = InferenceEngine()
    gen = DemoDataGenerator()

    C = _COLORES
    print(f"\n{C['BOLD']}{'='*70}")
    print("    MIHAC — Motor de Inferencia Heurística "
          "para Aprobación de Créditos")
    print(f"    Demostración con 7 Perfiles Nominales")
    print(f"{'='*70}{C['RESET']}\n")

    resultados = []

    for i, (key, perfil) in enumerate(
        gen.profiles.items(), 1
    ):
        datos = perfil["datos"]
        esperado = perfil["dictamen_esperado"]

        resultado = engine.evaluate(datos)
        dictamen = resultado["dictamen"]
        score = resultado["score_final"]

        # Color según dictamen
        color = C.get(dictamen, C["RESET"])
        match_str = (
            "✓ MATCH" if dictamen == esperado
            else "✗ MISMATCH"
        )

        print(f"{C['BOLD']}── Perfil {i}: "
              f"{perfil['nombre']} ──{C['RESET']}")
        print(f"  {C['DIM']}{perfil['descripcion']}"
              f"{C['RESET']}")
        print(f"  Datos: edad={datos['edad']}, "
              f"ingreso=${datos['ingreso_mensual']:,.0f}, "
              f"deuda=${datos['total_deuda_actual']:,.0f}, "
              f"historial={datos['historial_crediticio']}")
        print(f"         antig={datos['antiguedad_laboral']}a, "
              f"dep={datos['numero_dependientes']}, "
              f"viv={datos['tipo_vivienda']}, "
              f"prop={datos['proposito_credito']}, "
              f"monto=${datos['monto_credito']:,.0f}")
        print(f"  Score: {score}/100  |  "
              f"DTI: {resultado['dti']['valor_porcentaje']}")
        print(f"  Dictamen: {color}{dictamen}{C['RESET']}  "
              f"(esperado: {esperado})  [{match_str}]")

        # Reglas disparadas
        if resultado.get("reglas_disparadas"):
            reglas = [
                r["id"] for r in resultado["reglas_disparadas"]
            ]
            print(f"  Reglas: {', '.join(reglas)}")

        print()

        resultados.append({
            "perfil": key,
            "score": score,
            "dictamen": dictamen,
            "esperado": esperado,
            "match": dictamen == esperado,
        })

    # ── Resumen ─────────────────────────────────────────
    matches = sum(1 for r in resultados if r["match"])
    total = len(resultados)

    print(f"\n{C['BOLD']}{'─'*70}")
    print(f"  RESUMEN: {matches}/{total} perfiles "
          f"coinciden con el dictamen esperado")
    print(f"{'─'*70}{C['RESET']}")

    print(f"\n  {'Perfil':<25} {'Score':>5}  "
          f"{'Dictamen':<18} {'Esperado':<18} "
          f"{'Match'}")
    print(f"  {'─'*25} {'─'*5}  {'─'*18} {'─'*18} "
          f"{'─'*5}")
    for r in resultados:
        color = C.get(r["dictamen"], C["RESET"])
        match_sym = (
            f"{C['BOLD']}✓{C['RESET']}" if r["match"]
            else f"\033[91m✗{C['RESET']}"
        )
        print(
            f"  {r['perfil']:<25} {r['score']:>5}  "
            f"{color}{r['dictamen']:<18}{C['RESET']} "
            f"{r['esperado']:<18} {match_sym}"
        )

    # ── Batch demo ──────────────────────────────────────
    print(f"\n\n{C['BOLD']}── Batch de 100 solicitudes "
          f"aleatorias ──{C['RESET']}")

    batch = gen.generate_batch(100)
    resultados_batch = engine.evaluate_batch(batch)

    stats = {"APROBADO": 0, "REVISION_MANUAL": 0,
             "RECHAZADO": 0}
    for r in resultados_batch:
        stats[r["dictamen"]] += 1

    for dictamen, count in stats.items():
        color = C.get(dictamen, C["RESET"])
        barra = "█" * (count // 2)
        print(f"  {color}{dictamen:<18}{C['RESET']} "
              f"{count:>3}  {barra}")

    print(f"\n  Evaluaciones/seg: "
          f"{engine.stats['evaluaciones_por_segundo']:.0f}")
    print()


# ════════════════════════════════════════════════════════════
# TESTS
# ════════════════════════════════════════════════════════════

def _run_tests() -> None:
    """Tests del generador de datos demo."""
    print("=" * 60)
    print("MIHAC — Tests del Generador de Datos Demo")
    print("=" * 60)

    gen = DemoDataGenerator()

    # Test 1: Perfiles nominales
    print("\n── Test 1: 7 perfiles nominales ──")
    perfiles = gen.get_all_profiles()
    assert len(perfiles) == 7, f"FAIL: {len(perfiles)} != 7"
    print(f"  ✓ {len(perfiles)} perfiles cargados")

    for key in gen.list_profile_names():
        p = gen.get_profile(key)
        datos = p["datos"]
        assert len(datos) == 9, (
            f"FAIL: perfil {key} tiene {len(datos)} campos"
        )
        assert p["dictamen_esperado"] in {
            "APROBADO", "RECHAZADO", "REVISION_MANUAL"
        }, f"FAIL: dictamen inválido en {key}"

    print("  ✓ Todos los perfiles tienen 9 campos y "
          "dictamen válido")

    # Test 2: Perfil inexistente
    print("\n── Test 2: Perfil inexistente ──")
    try:
        gen.get_profile("no_existe")
        print("  ✗ FAIL: no lanzó excepción")
    except KeyError as e:
        print(f"  ✓ PASS: {e}")

    # Test 3: Batch aleatorio
    print("\n── Test 3: Batch de 50 solicitudes ──")
    batch = gen.generate_batch(50, seed=123)
    assert len(batch) == 50, f"FAIL: {len(batch)} != 50"
    campos = {
        "edad", "ingreso_mensual", "total_deuda_actual",
        "historial_crediticio", "antiguedad_laboral",
        "numero_dependientes", "tipo_vivienda",
        "proposito_credito", "monto_credito",
    }
    for i, sol in enumerate(batch):
        assert set(sol.keys()) == campos, (
            f"FAIL: solicitud {i} campos incorrectos"
        )
    print(f"  ✓ {len(batch)} solicitudes con campos "
          f"correctos")

    # Test 4: Escenarios
    print("\n── Test 4: Escenarios especiales ──")
    for scenario in [
        "todos_aprobados", "todos_rechazados",
        "mixto", "dti_extremo", "montos_altos",
    ]:
        datos = gen.generate_scenario(scenario, 10)
        assert len(datos) == 10, (
            f"FAIL: escenario {scenario} → {len(datos)}"
        )
        print(f"  ✓ {scenario}: {len(datos)} registros")

    # Test 4b: escenario inválido
    try:
        gen.generate_scenario("no_existe")
        print("  ✗ FAIL: no lanzó excepción")
    except ValueError as e:
        print(f"  ✓ Escenario inválido: {str(e)[:50]}...")

    # Test 5: Export CSV
    print("\n── Test 5: Exportación CSV ──")
    import tempfile
    with tempfile.NamedTemporaryFile(
        suffix=".csv", delete=False, mode="w"
    ) as f:
        tmp_path = f.name
    ruta = gen.export_to_csv(batch[:10], tmp_path)
    assert Path(ruta).exists(), f"FAIL: {ruta} no existe"
    # Leer y verificar
    import csv as csv_mod
    with open(ruta, "r", encoding="utf-8") as f:
        reader = csv_mod.DictReader(f)
        rows = list(reader)
    assert len(rows) == 10, f"FAIL: {len(rows)} != 10"
    print(f"  ✓ CSV exportado: {ruta}")
    print(f"  ✓ {len(rows)} filas leídas correctamente")
    Path(ruta).unlink()
    print(f"  ✓ Archivo temporal limpiado")

    # Test 6: Reproducibilidad
    print("\n── Test 6: Reproducibilidad (semilla fija) ──")
    b1 = gen.generate_batch(10, seed=42)
    b2 = gen.generate_batch(10, seed=42)
    for i in range(10):
        assert b1[i] == b2[i], (
            f"FAIL: registros diferentes en posición {i}"
        )
    print("  ✓ Misma semilla → mismos datos")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DEL GENERADOR PASARON ✓")
    print(f"{'='*60}")


# ════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if "--demo" in sys.argv:
        demo_script()
    elif "--test" in sys.argv:
        _run_tests()
    else:
        print("Uso:")
        print("  python -m mihac.data.generate_demo_data "
              "--demo    # Demo completa")
        print("  python -m mihac.data.generate_demo_data "
              "--test    # Tests")
        print()
        # Sin argumentos: demo por defecto
        demo_script()
