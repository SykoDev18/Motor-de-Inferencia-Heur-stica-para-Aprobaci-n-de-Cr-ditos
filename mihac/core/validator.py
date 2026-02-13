# ============================================================
# MIHAC v1.0 — Validador de Datos de Entrada
# core/validator.py
# ============================================================
# Verifica que los datos del solicitante sean coherentes antes
# de que el motor de inferencia los procese.  Devuelve errores
# descriptivos en español; nunca lanza excepciones crudas.
# ============================================================

import re
import logging
from typing import Any

logger = logging.getLogger(__name__)

# ── Constantes de validación ────────────────────────────────

CAMPOS_REQUERIDOS: list[str] = [
    "edad", "ingreso_mensual", "total_deuda_actual",
    "historial_crediticio", "antiguedad_laboral",
    "numero_dependientes", "tipo_vivienda",
    "proposito_credito", "monto_credito",
]

CAMPOS_ENTEROS: list[str] = [
    "edad", "historial_crediticio",
    "antiguedad_laboral", "numero_dependientes",
]

CAMPOS_NUMERICOS: list[str] = [
    "ingreso_mensual", "total_deuda_actual", "monto_credito",
]

CAMPOS_TEXTO: list[str] = [
    "tipo_vivienda", "proposito_credito",
]

TIPOS_VIVIENDA_VALIDOS: list[str] = [
    "Propia", "Familiar", "Rentada",
]

PROPOSITOS_VALIDOS: list[str] = [
    "Negocio", "Educacion", "Consumo",
    "Emergencia", "Vacaciones",
]


class Validator:
    """Validador de datos de entrada para el sistema MIHAC.

    Ejecuta validaciones en 4 grupos (A–D) y retorna todos
    los errores encontrados, no solo el primero.

    Ejemplo de uso::

        v = Validator()
        ok, errores = v.validate(datos)
        if not ok:
            for e in errores:
                print(e)
    """

    # ────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL
    # ────────────────────────────────────────────────────────

    def validate(
        self, datos: dict
    ) -> tuple[bool, list[str]]:
        """Valida el diccionario de datos del solicitante.

        Siempre ejecuta TODAS las validaciones posibles y
        acumula los errores para entregar un reporte completo.

        Args:
            datos: Diccionario con los datos del solicitante.

        Returns:
            (True, []) si todo está correcto.
            (False, [err1, err2, ...]) si hay problemas.
        """
        errores: list[str] = []

        # Grupo A — Campos obligatorios
        self._validar_campos_obligatorios(datos, errores)

        campos_presentes = all(
            c in datos for c in CAMPOS_REQUERIDOS
        )
        if not campos_presentes:
            return (False, errores)

        # Grupo B — Tipos de dato
        self._validar_tipos(datos, errores)

        if not self._tipos_correctos(datos):
            return (len(errores) == 0, errores)

        # Grupo C — Rangos y valores permitidos
        self._validar_rangos(datos, errores)

        # Grupo D — Coherencia lógica de negocio
        self._validar_coherencia(datos, errores)

        return (len(errores) == 0, errores)

    # ────────────────────────────────────────────────────────
    # SANITIZACIÓN
    # ────────────────────────────────────────────────────────

    def sanitize(self, datos: dict) -> dict:
        """Limpia y normaliza el diccionario de entrada.

        - Convierte strings a int/float donde corresponda.
        - Capitaliza tipo_vivienda y proposito_credito.
        - Elimina espacios en blanco y caracteres de moneda.

        Args:
            datos: Diccionario crudo del solicitante.

        Returns:
            Diccionario limpio listo para validación.
        """
        limpio: dict = {}

        for campo, valor in datos.items():
            if isinstance(valor, str):
                valor = valor.strip()

            if campo in CAMPOS_ENTEROS:
                valor = self._a_entero(valor)
            elif campo in CAMPOS_NUMERICOS:
                valor = self._a_flotante(valor)
            elif campo == "tipo_vivienda":
                valor = self._capitalizar(str(valor))
            elif campo == "proposito_credito":
                valor = self._capitalizar(str(valor))

            limpio[campo] = valor

        return limpio

    # ────────────────────────────────────────────────────────
    # GRUPO A — Campos obligatorios
    # ────────────────────────────────────────────────────────

    def _validar_campos_obligatorios(
        self, datos: dict, errores: list[str]
    ) -> None:
        """A001: Verifica que todos los campos requeridos estén."""
        for campo in CAMPOS_REQUERIDOS:
            if campo not in datos:
                errores.append(
                    f"Campo obligatorio faltante: {campo}"
                )

    # ────────────────────────────────────────────────────────
    # GRUPO B — Tipos de dato
    # ────────────────────────────────────────────────────────

    def _validar_tipos(
        self, datos: dict, errores: list[str]
    ) -> None:
        """B001–B003: Verifica tipos de dato correctos."""
        for campo in CAMPOS_ENTEROS:
            val = datos.get(campo)
            if val is not None and not isinstance(val, int):
                errores.append(
                    f"El campo {campo} tiene un tipo de dato "
                    f"inválido. Se esperaba int, se recibió "
                    f"{type(val).__name__}"
                )

        for campo in CAMPOS_NUMERICOS:
            val = datos.get(campo)
            if val is not None and not isinstance(
                val, (int, float)
            ):
                errores.append(
                    f"El campo {campo} tiene un tipo de dato "
                    f"inválido. Se esperaba float, se recibió "
                    f"{type(val).__name__}"
                )

        for campo in CAMPOS_TEXTO:
            val = datos.get(campo)
            if val is not None and not isinstance(val, str):
                errores.append(
                    f"El campo {campo} tiene un tipo de dato "
                    f"inválido. Se esperaba str, se recibió "
                    f"{type(val).__name__}"
                )

    def _tipos_correctos(self, datos: dict) -> bool:
        """Retorna True si todos los tipos son válidos."""
        for campo in CAMPOS_ENTEROS:
            v = datos.get(campo)
            if v is not None and not isinstance(v, int):
                return False
        for campo in CAMPOS_NUMERICOS:
            v = datos.get(campo)
            if v is not None and not isinstance(
                v, (int, float)
            ):
                return False
        for campo in CAMPOS_TEXTO:
            v = datos.get(campo)
            if v is not None and not isinstance(v, str):
                return False
        return True

    # ────────────────────────────────────────────────────────
    # GRUPO C — Rangos y valores permitidos
    # ────────────────────────────────────────────────────────

    def _validar_rangos(
        self, datos: dict, errores: list[str]
    ) -> None:
        """C001–C009: Valida rangos y valores categóricos."""
        # C001 — Edad
        edad = datos.get("edad")
        if isinstance(edad, int) and (edad < 18 or edad > 99):
            errores.append(
                f"Edad fuera de rango. Mínimo 18, máximo 99. "
                f"Recibido: {edad}"
            )

        # C002 — Ingreso
        ingreso = datos.get("ingreso_mensual")
        if isinstance(ingreso, (int, float)) and ingreso <= 0:
            errores.append(
                "El ingreso mensual debe ser mayor a cero."
            )

        # C003 — Deuda
        deuda = datos.get("total_deuda_actual")
        if isinstance(deuda, (int, float)) and deuda < 0:
            errores.append(
                "La deuda total no puede ser negativa."
            )

        # C004 — Historial
        hist = datos.get("historial_crediticio")
        if isinstance(hist, int) and hist not in (0, 1, 2):
            errores.append(
                f"Historial crediticio inválido. Valores "
                f"permitidos: 0 (Malo), 1 (Neutro), 2 (Bueno)"
                f". Recibido: {hist}"
            )

        # C005 — Antigüedad laboral
        antig = datos.get("antiguedad_laboral")
        if isinstance(antig, int) and (
            antig < 0 or antig > 40
        ):
            errores.append(
                "Antigüedad laboral fuera de rango "
                "(0–40 años)."
            )

        # C006 — Dependientes
        deps = datos.get("numero_dependientes")
        if isinstance(deps, int) and (
            deps < 0 or deps > 10
        ):
            errores.append(
                "Número de dependientes fuera de rango "
                "(0–10)."
            )

        # C007 — Tipo de vivienda
        viv = datos.get("tipo_vivienda")
        if isinstance(viv, str) and (
            viv not in TIPOS_VIVIENDA_VALIDOS
        ):
            errores.append(
                f"Tipo de vivienda inválido. Valores "
                f"permitidos: Propia, Familiar, Rentada. "
                f"Recibido: {viv}"
            )

        # C008 — Propósito
        prop = datos.get("proposito_credito")
        if isinstance(prop, str) and (
            prop not in PROPOSITOS_VALIDOS
        ):
            errores.append(
                "Propósito de crédito inválido."
            )

        # C009 — Monto
        monto = datos.get("monto_credito")
        if isinstance(monto, (int, float)) and (
            monto < 500 or monto > 50000
        ):
            errores.append(
                "Monto de crédito fuera de rango "
                "($500 – $50,000)."
            )

    # ────────────────────────────────────────────────────────
    # GRUPO D — Coherencia lógica de negocio
    # ────────────────────────────────────────────────────────

    def _validar_coherencia(
        self, datos: dict, errores: list[str]
    ) -> None:
        """D001–D003: Coherencia cruzada entre campos."""
        edad = datos.get("edad")
        antig = datos.get("antiguedad_laboral")
        ingreso = datos.get("ingreso_mensual")
        deuda = datos.get("total_deuda_actual")
        monto = datos.get("monto_credito")

        # D001 — Antigüedad vs edad
        if (
            isinstance(edad, int)
            and isinstance(antig, int)
        ):
            limite = edad - 15
            if antig > limite:
                errores.append(
                    f"Incoherencia lógica: la antigüedad "
                    f"laboral ({antig} años) no puede superar "
                    f"(edad - 15) = {limite} años."
                )

        # D002 — Deuda vs ingreso anual
        if (
            isinstance(ingreso, (int, float))
            and isinstance(deuda, (int, float))
            and ingreso > 0
        ):
            limite = ingreso * 24
            if deuda > limite:
                errores.append(
                    f"La deuda total ({deuda}) supera el "
                    f"límite razonable de 24 meses de ingreso "
                    f"({limite})."
                )

        # D003 — Monto vs ingreso
        if (
            isinstance(ingreso, (int, float))
            and isinstance(monto, (int, float))
            and ingreso > 0
        ):
            limite = ingreso * 18
            if monto > limite:
                errores.append(
                    f"El monto solicitado ({monto}) supera el "
                    f"límite de 18 meses de ingreso "
                    f"({limite}) para este solicitante."
                )

    # ────────────────────────────────────────────────────────
    # UTILIDADES DE SANITIZACIÓN
    # ────────────────────────────────────────────────────────

    @staticmethod
    def _a_entero(valor: Any) -> Any:
        """Intenta convertir un valor a int."""
        if isinstance(valor, int):
            return valor
        if isinstance(valor, float) and valor == int(valor):
            return int(valor)
        if isinstance(valor, str):
            limpio = re.sub(r'[^\d.\-]', '', valor)
            try:
                return int(float(limpio))
            except (ValueError, TypeError):
                pass
        return valor

    @staticmethod
    def _a_flotante(valor: Any) -> Any:
        """Intenta convertir un valor a float."""
        if isinstance(valor, (int, float)):
            return float(valor)
        if isinstance(valor, str):
            limpio = re.sub(r'[^\d.\-]', '', valor)
            try:
                return float(limpio)
            except (ValueError, TypeError):
                pass
        return valor

    @staticmethod
    def _capitalizar(texto: str) -> str:
        """Capitaliza la primera letra del texto."""
        texto = texto.strip()
        if texto:
            return texto[0].upper() + texto[1:]
        return texto


# ════════════════════════════════════════════════════════════
# TESTS DE VALIDACIÓN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 60)
    print("MIHAC — Tests del Validador")
    print("=" * 60)

    v = Validator()

    # ── Caso 1: Datos perfectamente válidos ──
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
    ok, errs = v.validate(caso_1)
    print(f"\nCaso 1 (válido): OK={ok}, Errores={errs}")
    assert ok is True and errs == [], "FAIL Caso 1"
    print("  ✓ PASS")

    # ── Caso 2: Edad = 17 (menor de edad) ──
    caso_2 = {**caso_1, "edad": 17}
    ok, errs = v.validate(caso_2)
    print(f"\nCaso 2 (edad=17): OK={ok}")
    for e in errs:
        print(f"  → {e}")
    assert ok is False, "FAIL Caso 2"
    assert any("Edad fuera de rango" in e for e in errs)
    print("  ✓ PASS")

    # ── Caso 3: Antigüedad imposible ──
    caso_3 = {**caso_1, "edad": 22, "antiguedad_laboral": 15}
    ok, errs = v.validate(caso_3)
    print(f"\nCaso 3 (antig=15, edad=22): OK={ok}")
    for e in errs:
        print(f"  → {e}")
    assert ok is False, "FAIL Caso 3"
    assert any("Incoherencia lógica" in e for e in errs)
    print("  ✓ PASS")

    # ── Caso 4: Varios errores simultáneos ──
    caso_4 = {
        "edad": 17,
        "ingreso_mensual": -500.0,
        "total_deuda_actual": -100.0,
        "historial_crediticio": 5,
        "antiguedad_laboral": 50,
        "numero_dependientes": 15,
        "tipo_vivienda": "Cueva",
        "proposito_credito": "Casino",
        "monto_credito": 100000.0,
    }
    ok, errs = v.validate(caso_4)
    print(f"\nCaso 4 (múltiples errores): OK={ok}")
    print(f"  Total errores encontrados: {len(errs)}")
    for i, e in enumerate(errs, 1):
        print(f"  {i}. {e}")
    assert ok is False, "FAIL Caso 4"
    assert len(errs) >= 5, "FAIL Caso 4: pocos errores"
    print("  ✓ PASS")

    # ── Caso 5: Sanitización ──
    caso_sucio = {
        "edad": "  35  ",
        "ingreso_mensual": "$25,000.00",
        "total_deuda_actual": "4000",
        "historial_crediticio": 2.0,
        "antiguedad_laboral": "7",
        "numero_dependientes": "1",
        "tipo_vivienda": "  propia  ",
        "proposito_credito": "negocio",
        "monto_credito": "$15,000",
    }
    limpio = v.sanitize(caso_sucio)
    ok, errs = v.validate(limpio)
    print(f"\nCaso 5 (sanitización): OK={ok}")
    print(f"  Datos limpios: {limpio}")
    assert ok is True, f"FAIL Caso 5: {errs}"
    print("  ✓ PASS")

    print("\n" + "=" * 60)
    print("TODOS LOS TESTS DEL VALIDADOR PASARON ✓")
    print("=" * 60)
