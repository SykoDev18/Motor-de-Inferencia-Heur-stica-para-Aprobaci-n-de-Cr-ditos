# ============================================================
# MIHAC v1.0 — Motor de Scoring Heurístico
# core/scorer.py
# ============================================================
# Calcula el Score Final aplicando sub-scores ponderados y
# reglas heurísticas leídas dinámicamente de rules.json.
# ============================================================

import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CORE_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CORE_DIR.parent
_RULES_PATH = _PROJECT_ROOT / "knowledge" / "rules.json"


class ScoringEngine:
    """Motor de scoring heurístico del sistema MIHAC.

    Lee las reglas desde knowledge/rules.json al instanciarse
    y las aplica para calcular el score crediticio del
    solicitante.

    Attributes:
        _reglas: Lista de reglas cargadas del JSON.

    Ejemplo de uso::

        scorer = ScoringEngine()
        dti, clasif = scorer.calculate_dti(25000, 4000)
        sub = scorer.calculate_subscores(datos, dti)
        reglas = scorer.apply_rules(datos, dti)
        score, umbral = scorer.calculate_final_score(
            sub, reglas, 15000
        )
        dictamen = scorer.get_dictamen(score, umbral, clasif)
    """

    def __init__(self, rules_path: str | Path | None = None):
        """Inicializa el motor cargando las reglas.

        Args:
            rules_path: Ruta al archivo rules.json.
                Si es None, usa la ruta por defecto.
        """
        ruta = Path(rules_path) if rules_path else _RULES_PATH
        self._reglas: list[dict] = []
        self._cargar_reglas(ruta)

    def _cargar_reglas(self, ruta: Path) -> None:
        """Lee y parsea el archivo de reglas JSON.

        Args:
            ruta: Ruta absoluta al archivo rules.json.
        """
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._reglas = data.get("reglas", [])
            logger.info(
                "Cargadas %d reglas desde %s",
                len(self._reglas), ruta
            )
        except FileNotFoundError:
            logger.error("Archivo de reglas no encontrado: %s", ruta)
            self._reglas = []
        except json.JSONDecodeError as e:
            logger.error("Error al parsear rules.json: %s", e)
            self._reglas = []

    # ────────────────────────────────────────────────────────
    # DTI (Debt-To-Income)
    # ────────────────────────────────────────────────────────

    def calculate_dti(
        self, ingreso: float, deuda: float
    ) -> tuple[float, str]:
        """Calcula la relación Deuda/Ingreso y la clasifica.

        Args:
            ingreso: Ingreso mensual del solicitante (> 0).
            deuda: Total de deudas vigentes (>= 0).

        Returns:
            Tupla (dti_ratio, clasificacion).
            clasificacion: "BAJO"|"MODERADO"|"ALTO"|"CRITICO"

        Ejemplo::

            dti, clasif = scorer.calculate_dti(25000, 4000)
            # (0.16, "BAJO")
        """
        if ingreso <= 0:
            return (1.0, "CRITICO")

        dti = round(deuda / ingreso, 4)

        if dti < 0.25:
            clasificacion = "BAJO"
        elif dti < 0.40:
            clasificacion = "MODERADO"
        elif dti < 0.60:
            clasificacion = "ALTO"
        else:
            clasificacion = "CRITICO"

        return (dti, clasificacion)

    # ────────────────────────────────────────────────────────
    # SUB-SCORES
    # ────────────────────────────────────────────────────────

    def calculate_subscores(
        self, datos: dict, dti: float
    ) -> dict:
        """Calcula los 4 sub-scores independientes.

        Args:
            datos: Diccionario validado del solicitante.
            dti: Ratio Deuda/Ingreso ya calculado.

        Returns:
            Dict con claves: solvencia (max 40),
            estabilidad (max 30), historial_score (max 20),
            perfil (max 10).

        Ejemplo::

            sub = scorer.calculate_subscores(datos, 0.16)
            # {"solvencia": 25, "estabilidad": 30, ...}
        """
        return {
            "solvencia": self._score_solvencia(datos, dti),
            "estabilidad": self._score_estabilidad(datos),
            "historial_score": self._score_historial(datos),
            "perfil": self._score_perfil(datos),
        }

    def _score_solvencia(
        self, datos: dict, dti: float
    ) -> int:
        """Solvencia económica (max 40 pts).

        - Ingreso normalizado 0–20
        - Ajuste por DTI
        - Penalización por dependientes
        """
        ingreso = datos.get("ingreso_mensual", 0)
        deps = datos.get("numero_dependientes", 0)

        # Base: ingreso en escala 0–20
        base = min(ingreso / 30000.0 * 20.0, 20.0)

        # Ajuste por DTI
        if dti < 0.25:
            ajuste_dti = 10.0
        elif dti < 0.40:
            ajuste_dti = 5.0
        elif dti < 0.60:
            ajuste_dti = -5.0
        else:
            ajuste_dti = -15.0

        # Penalización por dependientes
        ajuste_deps = deps * 1.5

        total = base + ajuste_dti - ajuste_deps
        return int(max(0, min(40, total)))

    def _score_estabilidad(self, datos: dict) -> int:
        """Estabilidad socioeconómica (max 30 pts).

        - Antigüedad laboral escalonada
        - Tipo de vivienda
        """
        antig = datos.get("antiguedad_laboral", 0)
        vivienda = datos.get("tipo_vivienda", "")

        # Antigüedad
        if antig < 1:
            pts_antig = 0
        elif antig < 2:
            pts_antig = 8
        elif antig < 5:
            pts_antig = 18
        else:
            pts_antig = 28

        # Vivienda
        if vivienda == "Propia":
            pts_viv = 8
        elif vivienda == "Familiar":
            pts_viv = 3
        else:
            pts_viv = 0

        return int(min(pts_antig + pts_viv, 30))

    def _score_historial(self, datos: dict) -> int:
        """Historial crediticio (max 20 pts)."""
        hist = datos.get("historial_crediticio", 0)
        if hist == 2:
            return 20
        elif hist == 1:
            return 10
        else:
            return 0

    def _score_perfil(self, datos: dict) -> int:
        """Perfil del solicitante (max 10 pts).

        - Propósito del crédito
        - Bonus por rango de edad óptimo
        """
        prop = datos.get("proposito_credito", "")
        edad = datos.get("edad", 0)

        proposito_pts = {
            "Negocio": 10,
            "Educacion": 8,
            "Emergencia": 6,
            "Consumo": 4,
            "Vacaciones": 0,
        }
        pts = proposito_pts.get(prop, 2)

        # Bonus por edad óptima (25–55)
        if 25 <= edad <= 55:
            pts += 2

        return int(min(pts, 10))

    # ────────────────────────────────────────────────────────
    # REGLAS HEURÍSTICAS
    # ────────────────────────────────────────────────────────

    def apply_rules(
        self, datos: dict, dti: float
    ) -> list[dict]:
        """Evalúa todas las reglas activas contra el perfil.

        Crea un diccionario extendido que incluye 'dti' como
        campo virtual para las reglas que lo necesiten.

        Args:
            datos: Diccionario validado del solicitante.
            dti: Ratio DTI calculado.

        Returns:
            Lista de reglas activadas, cada una con:
            id, impacto, descripcion, tipo.

        Ejemplo::

            reglas = scorer.apply_rules(datos, 0.16)
            for r in reglas:
                print(r["id"], r["impacto"])
        """
        # Datos extendidos con campo virtual 'dti'
        datos_ext = {**datos, "dti": dti}
        activadas: list[dict] = []

        for regla in self._reglas:
            if not regla.get("activa", False):
                continue

            tipo = regla.get("tipo", "directa")
            cumple = False

            try:
                if tipo == "directa":
                    cumple = self._evaluar_directa(
                        datos_ext, regla
                    )
                elif tipo == "compensacion":
                    cumple = self._evaluar_compensacion(
                        datos_ext, regla
                    )
            except Exception as e:
                logger.warning(
                    "Error evaluando regla %s: %s",
                    regla.get("id", "?"), e
                )
                continue

            if cumple:
                entrada = {
                    "id": regla["id"],
                    "impacto": regla["impacto_puntos"],
                    "descripcion": regla["descripcion"],
                    "tipo": tipo,
                }
                if "flag" in regla:
                    entrada["flag"] = regla["flag"]
                activadas.append(entrada)

        return activadas

    def _evaluar_directa(
        self, datos: dict, regla: dict
    ) -> bool:
        """Evalúa una regla directa (condición simple)."""
        campo = regla.get("condicion_campo", "")
        operador = regla.get("condicion_operador", "==")
        valor_esperado = regla.get("condicion_valor")

        valor_actual = datos.get(campo)
        if valor_actual is None:
            return False

        return self._comparar(
            valor_actual, operador, valor_esperado
        )

    def _evaluar_compensacion(
        self, datos: dict, regla: dict
    ) -> bool:
        """Evalúa una regla de compensación (AND múltiple).

        Todas las condiciones deben cumplirse.
        """
        condiciones = regla.get("condiciones", [])
        if not condiciones:
            return False

        for cond in condiciones:
            campo = cond.get("campo", "")
            operador = cond.get("operador", "==")
            valor_actual = datos.get(campo)

            if valor_actual is None:
                return False

            # Comparación cruzada entre campos
            if "campo_referencia" in cond:
                ref = datos.get(cond["campo_referencia"])
                factor = cond.get("factor", 1.0)
                if ref is None:
                    return False
                valor_esperado = ref * factor
            else:
                valor_esperado = cond.get("valor")

            if not self._comparar(
                valor_actual, operador, valor_esperado
            ):
                return False

        return True

    @staticmethod
    def _comparar(
        actual: Any, operador: str, esperado: Any
    ) -> bool:
        """Compara dos valores según el operador dado."""
        ops = {
            "==": lambda a, b: a == b,
            "!=": lambda a, b: a != b,
            ">":  lambda a, b: a > b,
            ">=": lambda a, b: a >= b,
            "<":  lambda a, b: a < b,
            "<=": lambda a, b: a <= b,
        }
        fn = ops.get(operador)
        if fn is None:
            return False
        try:
            return fn(actual, esperado)
        except TypeError:
            return False

    # ────────────────────────────────────────────────────────
    # SCORE FINAL Y DICTAMEN
    # ────────────────────────────────────────────────────────

    def calculate_final_score(
        self,
        sub_scores: dict,
        reglas_activadas: list[dict],
        monto_credito: float,
    ) -> tuple[int, int]:
        """Calcula el score final combinando sub-scores y reglas.

        1. Suma los 4 sub-scores (max 100).
        2. Aplica impactos de reglas activadas.
        3. Clampea entre 0 y 100.
        4. Determina el umbral según monto solicitado.

        Args:
            sub_scores: Dict con los 4 sub-scores.
            reglas_activadas: Reglas que se activaron.
            monto_credito: Monto solicitado.

        Returns:
            (score_final, umbral_aplicado)

        Ejemplo::

            score, umbral = scorer.calculate_final_score(
                sub, reglas, 15000
            )
            # (85, 80)
        """
        # 1. Suma de sub-scores
        base = sum(sub_scores.values())

        # 2. Impacto de reglas
        impacto_total = sum(
            r["impacto"] for r in reglas_activadas
        )
        raw_score = base + impacto_total

        # 3. Clampeo
        score_final = int(max(0, min(100, raw_score)))

        # 4. Umbral por monto
        umbral = 85 if monto_credito > 20000 else 80

        return (score_final, umbral)

    def get_dictamen(
        self,
        score: int,
        umbral: int,
        dti_clasificacion: str,
    ) -> str:
        """Determina el dictamen final de la evaluación.

        Regla especial: DTI CRITICO → RECHAZADO inmediato,
        sin importar el score.

        Args:
            score: Score final (0–100).
            umbral: Umbral de aprobación (80 o 85).
            dti_clasificacion: Clasificación del DTI.

        Returns:
            "APROBADO" | "REVISION_MANUAL" | "RECHAZADO"

        Ejemplo::

            dictamen = scorer.get_dictamen(85, 80, "BAJO")
            # "APROBADO"
        """
        # DTI crítico → rechazo directo
        if dti_clasificacion == "CRITICO":
            return "RECHAZADO"

        if score >= umbral:
            return "APROBADO"
        elif score >= umbral - 20:
            return "REVISION_MANUAL"
        else:
            return "RECHAZADO"


# ════════════════════════════════════════════════════════════
# TESTS DEL SCORING ENGINE
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("MIHAC — Tests del Scoring Engine")
    print("=" * 60)

    scorer = ScoringEngine()
    print(f"Reglas cargadas: {len(scorer._reglas)}")

    # ── Caso 1: Cliente ideal (debe dar APROBADO) ──
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

    dti1, clasif1 = scorer.calculate_dti(
        caso_1["ingreso_mensual"],
        caso_1["total_deuda_actual"]
    )
    sub1 = scorer.calculate_subscores(caso_1, dti1)
    reglas1 = scorer.apply_rules(caso_1, dti1)
    score1, umbral1 = scorer.calculate_final_score(
        sub1, reglas1, caso_1["monto_credito"]
    )
    dict1 = scorer.get_dictamen(score1, umbral1, clasif1)

    print(f"\n{'─'*50}")
    print(f"CASO 1 — Cliente ideal")
    print(f"  DTI: {dti1:.2%} ({clasif1})")
    print(f"  Sub-scores: {sub1}")
    print(f"  Reglas activadas: {len(reglas1)}")
    for r in reglas1:
        signo = "+" if r["impacto"] > 0 else ""
        print(f"    {r['id']}: {signo}{r['impacto']} "
              f"({r['descripcion']})")
    print(f"  Score: {score1} | Umbral: {umbral1}")
    print(f"  DICTAMEN: {dict1}")
    assert dict1 == "APROBADO", f"FAIL: esperado APROBADO, obtenido {dict1}"
    print("  ✓ PASS")

    # ── Caso 2: Cliente de alto riesgo (RECHAZADO) ──
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

    dti2, clasif2 = scorer.calculate_dti(
        caso_2["ingreso_mensual"],
        caso_2["total_deuda_actual"]
    )
    sub2 = scorer.calculate_subscores(caso_2, dti2)
    reglas2 = scorer.apply_rules(caso_2, dti2)
    score2, umbral2 = scorer.calculate_final_score(
        sub2, reglas2, caso_2["monto_credito"]
    )
    dict2 = scorer.get_dictamen(score2, umbral2, clasif2)

    print(f"\n{'─'*50}")
    print(f"CASO 2 — Cliente de alto riesgo")
    print(f"  DTI: {dti2:.2%} ({clasif2})")
    print(f"  Sub-scores: {sub2}")
    print(f"  Reglas activadas: {len(reglas2)}")
    for r in reglas2:
        signo = "+" if r["impacto"] > 0 else ""
        print(f"    {r['id']}: {signo}{r['impacto']} "
              f"({r['descripcion']})")
    print(f"  Score: {score2} | Umbral: {umbral2}")
    print(f"  DICTAMEN: {dict2}")
    assert dict2 == "RECHAZADO", f"FAIL: esperado RECHAZADO, obtenido {dict2}"
    print("  ✓ PASS")

    # ── Caso 3: Cliente zona gris (REVISION_MANUAL) ──
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

    dti3, clasif3 = scorer.calculate_dti(
        caso_3["ingreso_mensual"],
        caso_3["total_deuda_actual"]
    )
    sub3 = scorer.calculate_subscores(caso_3, dti3)
    reglas3 = scorer.apply_rules(caso_3, dti3)
    score3, umbral3 = scorer.calculate_final_score(
        sub3, reglas3, caso_3["monto_credito"]
    )
    dict3 = scorer.get_dictamen(score3, umbral3, clasif3)

    print(f"\n{'─'*50}")
    print(f"CASO 3 — Zona gris")
    print(f"  DTI: {dti3:.2%} ({clasif3})")
    print(f"  Sub-scores: {sub3}")
    print(f"  Reglas activadas: {len(reglas3)}")
    for r in reglas3:
        signo = "+" if r["impacto"] > 0 else ""
        print(f"    {r['id']}: {signo}{r['impacto']} "
              f"({r['descripcion']})")
    print(f"  Score: {score3} | Umbral: {umbral3}")
    print(f"  DICTAMEN: {dict3}")
    assert dict3 == "REVISION_MANUAL", (
        f"FAIL: esperado REVISION_MANUAL, obtenido {dict3}"
    )
    print("  ✓ PASS")

    print(f"\n{'='*60}")
    print("TODOS LOS TESTS DEL SCORER PASARON ✓")
    print(f"{'='*60}")
