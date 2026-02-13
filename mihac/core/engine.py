# ============================================================
# MIHAC v1.0 — Motor de Inferencia (Orquestador Principal)
# core/engine.py
# ============================================================
# Único punto de entrada al núcleo.  Recibe datos crudos del
# solicitante, orquesta validación → scoring → reglas →
# explicación, y retorna el resultado completo.
# ============================================================

import sys
import logging
from pathlib import Path
from datetime import datetime

# Asegurar que el proyecto raíz esté en sys.path
_CORE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CORE_DIR.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from core.validator import Validator
from core.scorer import ScoringEngine
from core.explainer import Explainer

logger = logging.getLogger(__name__)


class InferenceEngine:
    """Orquestador principal del sistema MIHAC.

    Recibe los datos crudos del solicitante y retorna el
    resultado completo de la evaluación crediticia.
    Es el ÚNICO punto de entrada al núcleo desde el exterior.

    Flujo interno (9 pasos):
        1. Sanitizar datos
        2. Validar datos
        3. Calcular DTI
        4. Calcular sub-scores
        5. Aplicar reglas heurísticas
        6. Calcular score final y dictamen
        7. Generar explicación en lenguaje natural
        8. Registrar en log
        9. Retornar resultado completo

    Ejemplo de uso::

        engine = InferenceEngine()
        resultado = engine.evaluate(datos_solicitante)
        print(resultado["dictamen"])
        print(resultado["score_final"])
    """

    def __init__(self) -> None:
        """Inicializa los componentes del motor."""
        self._validator = Validator()
        self._scorer = ScoringEngine()
        self._explainer = Explainer()

        # Estadísticas de sesión
        self._total_evaluaciones: int = 0
        self._aprobados: int = 0
        self._rechazados: int = 0
        self._revision_manual: int = 0
        self._suma_scores: float = 0.0
        self._suma_dti: float = 0.0

    # ────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL
    # ────────────────────────────────────────────────────────

    def evaluate(self, datos: dict) -> dict:
        """Evalúa una solicitud de crédito completa.

        Ejecuta el flujo de 9 pasos. Nunca lanza excepciones
        hacia afuera: captura errores internos y los incluye
        en errores_validacion.

        Args:
            datos: Diccionario con datos crudos del
                solicitante (ver diccionario de datos).

        Returns:
            Dict con la estructura de salida completa:
            score_final, dictamen, sub_scores,
            reglas_activadas, reporte_explicacion, etc.

        Ejemplo::

            resultado = engine.evaluate({
                "edad": 35,
                "ingreso_mensual": 25000,
                ...
            })
        """
        try:
            # Paso 1 — Sanitizar
            datos_limpios = self._validator.sanitize(datos)

            # Paso 2 — Validar
            valido, errores = self._validator.validate(
                datos_limpios
            )
            if not valido:
                return self._resultado_con_errores(errores)

            # Paso 3 — Calcular DTI
            dti, dti_clasif = self._scorer.calculate_dti(
                datos_limpios["ingreso_mensual"],
                datos_limpios["total_deuda_actual"],
            )

            # Paso 4 — Sub-scores
            sub_scores = self._scorer.calculate_subscores(
                datos_limpios, dti
            )

            # Paso 5 — Reglas heurísticas
            reglas = self._scorer.apply_rules(
                datos_limpios, dti
            )

            # Paso 6 — Score final y dictamen
            score, umbral = (
                self._scorer.calculate_final_score(
                    sub_scores,
                    reglas,
                    datos_limpios["monto_credito"],
                )
            )
            dictamen = self._scorer.get_dictamen(
                score, umbral, dti_clasif
            )

            # Separar compensaciones
            compensaciones = [
                r for r in reglas
                if r["tipo"] == "compensacion"
            ]

            # Construir resultado parcial
            resultado = {
                "score_final": score,
                "dti_ratio": dti,
                "dti_clasificacion": dti_clasif,
                "sub_scores": sub_scores,
                "dictamen": dictamen,
                "umbral_aplicado": umbral,
                "reglas_activadas": reglas,
                "compensaciones": compensaciones,
                "errores_validacion": [],
            }

            # Paso 7 — Explicación en lenguaje natural
            explicacion = self._explainer.generate(
                datos_limpios, resultado
            )
            resultado["reporte_explicacion"] = explicacion

            # Paso 8 — Log
            self._log_evaluation(datos_limpios, resultado)

            # Paso 9 — Actualizar stats y retornar
            self._actualizar_stats(resultado)

            return resultado

        except Exception as e:
            logger.error("Error interno en evaluate: %s", e)
            return self._resultado_con_errores(
                [f"Error interno: {e}"]
            )

    # ────────────────────────────────────────────────────────
    # EVALUACIÓN POR LOTES
    # ────────────────────────────────────────────────────────

    def evaluate_batch(
        self, lista_datos: list[dict]
    ) -> list[dict]:
        """Evalúa una lista de solicitantes.

        Args:
            lista_datos: Lista de dicts con datos de
                cada solicitante.

        Returns:
            Lista de resultados en el mismo orden.
            Cada resultado incluye campo "indice" para
            trazabilidad.

        Ejemplo::

            resultados = engine.evaluate_batch([d1, d2, d3])
            for r in resultados:
                print(r["indice"], r["dictamen"])
        """
        resultados: list[dict] = []
        total = len(lista_datos)

        for i, datos in enumerate(lista_datos):
            logger.info(
                "Evaluando solicitud %d de %d...",
                i + 1, total,
            )
            resultado = self.evaluate(datos)
            resultado["indice"] = i
            resultados.append(resultado)

        return resultados

    # ────────────────────────────────────────────────────────
    # LOG DE EVALUACIÓN
    # ────────────────────────────────────────────────────────

    def _log_evaluation(
        self, datos: dict, resultado: dict
    ) -> None:
        """Escribe la evaluación en mihac_evaluations.log.

        Formato:
        [TIMESTAMP] | DICTAMEN | SCORE | DTI | MONTO | PROP

        Args:
            datos: Datos del solicitante.
            resultado: Resultado de la evaluación.
        """
        try:
            log_path = _PROJECT_ROOT / "mihac_evaluations.log"
            timestamp = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            dictamen = resultado.get("dictamen", "N/A")
            score = resultado.get("score_final", 0)
            dti = resultado.get("dti_ratio", 0.0)
            monto = datos.get("monto_credito", 0)
            proposito = datos.get(
                "proposito_credito", "N/A"
            )

            linea = (
                f"[{timestamp}] | {dictamen} | "
                f"{score} | {dti:.2f} | "
                f"{monto} | {proposito}\n"
            )

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(linea)

        except Exception as e:
            logger.warning(
                "Error al escribir log de evaluación: %s", e
            )

    # ────────────────────────────────────────────────────────
    # ESTADÍSTICAS DE SESIÓN
    # ────────────────────────────────────────────────────────

    @property
    def stats(self) -> dict:
        """Estadísticas acumuladas de la sesión.

        Returns:
            Dict con total_evaluaciones, aprobados,
            rechazados, revision_manual, tasa_aprobacion,
            score_promedio, dti_promedio.

        Ejemplo::

            print(engine.stats["tasa_aprobacion"])
        """
        total = self._total_evaluaciones
        if total == 0:
            return {
                "total_evaluaciones": 0,
                "aprobados": 0,
                "rechazados": 0,
                "revision_manual": 0,
                "tasa_aprobacion": 0.0,
                "score_promedio": 0.0,
                "dti_promedio": 0.0,
            }

        return {
            "total_evaluaciones": total,
            "aprobados": self._aprobados,
            "rechazados": self._rechazados,
            "revision_manual": self._revision_manual,
            "tasa_aprobacion": round(
                self._aprobados / total * 100, 2
            ),
            "score_promedio": round(
                self._suma_scores / total, 2
            ),
            "dti_promedio": round(
                self._suma_dti / total, 4
            ),
        }

    def _actualizar_stats(self, resultado: dict) -> None:
        """Actualiza contadores de la sesión."""
        self._total_evaluaciones += 1
        self._suma_scores += resultado.get(
            "score_final", 0
        )
        self._suma_dti += resultado.get("dti_ratio", 0.0)

        dictamen = resultado.get("dictamen", "")
        if dictamen == "APROBADO":
            self._aprobados += 1
        elif dictamen == "RECHAZADO":
            self._rechazados += 1
        elif dictamen == "REVISION_MANUAL":
            self._revision_manual += 1

    # ────────────────────────────────────────────────────────
    # RESULTADO CON ERRORES
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _resultado_con_errores(
        errores: list[str],
    ) -> dict:
        """Construye un resultado de error sin score.

        Args:
            errores: Lista de mensajes de error.

        Returns:
            Dict con estructura de salida y errores.
        """
        return {
            "score_final": 0,
            "dti_ratio": 0.0,
            "dti_clasificacion": "N/A",
            "sub_scores": {
                "solvencia": 0,
                "estabilidad": 0,
                "historial_score": 0,
                "perfil": 0,
            },
            "dictamen": "RECHAZADO",
            "umbral_aplicado": 80,
            "reglas_activadas": [],
            "compensaciones": [],
            "reporte_explicacion": "",
            "errores_validacion": errores,
        }


# ════════════════════════════════════════════════════════════
# TESTS DE INTEGRACIÓN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(name)-15s | %(message)s",
    )

    print("=" * 60)
    print("MIHAC — Tests de Integración del Motor")
    print("=" * 60)

    engine = InferenceEngine()

    # ── Datos de referencia ──
    caso_1 = {
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

    caso_2 = {
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

    caso_3 = {
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

    # ── Test 1: Evaluación individual ──
    print("\n── Test 1: Evaluaciones individuales ──")
    for i, (caso, esperado) in enumerate([
        (caso_1, "APROBADO"),
        (caso_2, "RECHAZADO"),
        (caso_3, "REVISION_MANUAL"),
    ], 1):
        res = engine.evaluate(caso)
        print(
            f"  Caso {i}: Score={res['score_final']} | "
            f"DTI={res['dti_ratio']:.2%} "
            f"({res['dti_clasificacion']}) | "
            f"Dictamen={res['dictamen']}"
        )
        assert res["dictamen"] == esperado, (
            f"FAIL Caso {i}: esperado {esperado}, "
            f"obtenido {res['dictamen']}"
        )
        assert res["errores_validacion"] == [], (
            f"FAIL Caso {i}: errores inesperados: "
            f"{res['errores_validacion']}"
        )
        print(f"  ✓ PASS")

    # ── Test 2: Evaluación por lotes ──
    print("\n── Test 2: Evaluación por lotes ──")
    lote = [caso_1, caso_2, caso_3]
    resultados = engine.evaluate_batch(lote)
    assert len(resultados) == 3, "FAIL: lote incompleto"
    for r in resultados:
        assert "indice" in r, "FAIL: falta campo indice"
        print(
            f"  Índice {r['indice']}: "
            f"{r['dictamen']} (Score: {r['score_final']})"
        )
    print("  ✓ PASS (3 evaluaciones en lote)")

    # ── Test 3: Estadísticas ──
    print("\n── Test 3: Estadísticas de sesión ──")
    st = engine.stats
    print(f"  Total evaluaciones: {st['total_evaluaciones']}")
    print(f"  Aprobados: {st['aprobados']}")
    print(f"  Rechazados: {st['rechazados']}")
    print(f"  Revisión manual: {st['revision_manual']}")
    print(f"  Tasa aprobación: {st['tasa_aprobacion']}%")
    print(f"  Score promedio: {st['score_promedio']}")
    print(f"  DTI promedio: {st['dti_promedio']}")
    assert st["total_evaluaciones"] == 6, (
        "FAIL: esperadas 6 evaluaciones"
    )
    print("  ✓ PASS")

    # ── Test 4: Log creado ──
    print("\n── Test 4: Archivo de log ──")
    log_path = _PROJECT_ROOT / "mihac_evaluations.log"
    assert log_path.exists(), "FAIL: log no creado"
    with open(log_path, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    print(f"  Entradas en log: {len(lineas)}")
    assert len(lineas) >= 6, "FAIL: faltan entradas en log"
    print(f"  Última: {lineas[-1].strip()}")
    print("  ✓ PASS")

    # ── Test 5: Manejo de errores ──
    print("\n── Test 5: Datos con errores ──")
    caso_malo = {"edad": 10}  # Campos faltantes
    res_malo = engine.evaluate(caso_malo)
    assert res_malo["errores_validacion"] != [], (
        "FAIL: debería tener errores"
    )
    assert res_malo["dictamen"] == "RECHAZADO"
    print(
        f"  Errores capturados: "
        f"{len(res_malo['errores_validacion'])}"
    )
    for e in res_malo["errores_validacion"]:
        print(f"    → {e}")
    print("  ✓ PASS (sin excepción, errores capturados)")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DE INTEGRACIÓN PASARON ✓")
    print(f"{'='*60}")
