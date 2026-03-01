# ============================================================
# MIHAC v1.0 — Tests del Validador (core/validator.py)
# tests/test_validator.py
# ============================================================
# ~30 tests cubriendo los 4 grupos de validación (A–D),
# sanitización y casos límite.
# ============================================================

import pytest
from core.validator import (
    Validator,
    CAMPOS_REQUERIDOS,
    CAMPOS_ENTEROS,
    CAMPOS_NUMERICOS,
    CAMPOS_TEXTO,
    TIPOS_VIVIENDA_VALIDOS,
    PROPOSITOS_VALIDOS,
)
from tests.fixtures import (
    CASO_IDEAL,
    DATOS_INVALIDOS_TIPOS,
    DATOS_CAMPOS_FALTANTES,
    DATOS_RANGOS_EXTREMOS,
    DATOS_SANITIZAR,
)


# ════════════════════════════════════════════════════════════
# GRUPO A — Campos obligatorios
# ════════════════════════════════════════════════════════════

class TestCamposObligatorios:
    """Tests para validación de campos obligatorios (A001)."""

    def test_datos_completos_sin_errores(self, validator, caso_ideal):
        ok, errores = validator.validate(caso_ideal)
        assert ok is True
        assert errores == []

    def test_campo_faltante_unico(self, validator):
        datos = CASO_IDEAL.copy()
        del datos["edad"]
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("edad" in e for e in errores)

    def test_multiples_campos_faltantes(self, validator):
        ok, errores = validator.validate(DATOS_CAMPOS_FALTANTES)
        assert ok is False
        faltantes = [
            "total_deuda_actual", "historial_crediticio",
            "antiguedad_laboral", "numero_dependientes",
            "tipo_vivienda", "proposito_credito", "monto_credito",
        ]
        for campo in faltantes:
            assert any(campo in e for e in errores), (
                f"Debería reportar '{campo}' como faltante"
            )

    def test_diccionario_vacio(self, validator):
        ok, errores = validator.validate({})
        assert ok is False
        assert len(errores) == len(CAMPOS_REQUERIDOS)

    def test_todos_los_campos_requeridos_listados(self):
        assert len(CAMPOS_REQUERIDOS) == 9

    @pytest.mark.parametrize("campo", CAMPOS_REQUERIDOS)
    def test_cada_campo_requerido_individual(self, validator, campo):
        datos = CASO_IDEAL.copy()
        del datos[campo]
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any(campo in e for e in errores)


# ════════════════════════════════════════════════════════════
# GRUPO B — Tipos de dato
# ════════════════════════════════════════════════════════════

class TestTiposDeDato:
    """Tests para validación de tipos de dato (B001–B003)."""

    def test_tipos_correctos_pasan(self, validator, caso_ideal):
        ok, errores = validator.validate(caso_ideal)
        assert ok is True

    def test_edad_string_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = "treinta"
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("edad" in e and "int" in e for e in errores)

    def test_ingreso_string_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = "mucho"
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("ingreso_mensual" in e for e in errores)

    def test_historial_float_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["historial_crediticio"] = 2.5
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("historial_crediticio" in e for e in errores)

    def test_tipo_vivienda_int_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["tipo_vivienda"] = 123
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("tipo_vivienda" in e for e in errores)

    def test_proposito_bool_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["proposito_credito"] = True
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("proposito_credito" in e for e in errores)

    def test_multiples_tipos_invalidos(self, validator):
        ok, errores = validator.validate(DATOS_INVALIDOS_TIPOS)
        assert ok is False
        assert len(errores) >= 3


# ════════════════════════════════════════════════════════════
# GRUPO C — Rangos y valores permitidos
# ════════════════════════════════════════════════════════════

class TestRangos:
    """Tests para validación de rangos (C001–C009)."""

    def test_edad_menor_18_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 17
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("Edad fuera de rango" in e for e in errores)

    def test_edad_mayor_99_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 100
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("Edad fuera de rango" in e for e in errores)

    def test_edad_18_pasa(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 18
        datos["antiguedad_laboral"] = 1
        ok, errores = validator.validate(datos)
        assert ok is True

    def test_edad_99_pasa(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 99
        ok, _ = validator.validate(datos)
        assert ok is True

    def test_ingreso_cero_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = 0
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("ingreso" in e.lower() for e in errores)

    def test_ingreso_negativo_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = -1000
        ok, errores = validator.validate(datos)
        assert ok is False

    def test_deuda_negativa_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["total_deuda_actual"] = -100
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("negativa" in e.lower() for e in errores)

    def test_historial_valor_3_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["historial_crediticio"] = 3
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("Historial" in e for e in errores)

    @pytest.mark.parametrize("valor", [0, 1, 2])
    def test_historial_valores_validos(self, validator, valor):
        datos = CASO_IDEAL.copy()
        datos["historial_crediticio"] = valor
        ok, _ = validator.validate(datos)
        assert ok is True

    def test_antiguedad_41_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 99
        datos["antiguedad_laboral"] = 41
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("Antigüedad" in e for e in errores)

    def test_dependientes_11_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["numero_dependientes"] = 11
        ok, errores = validator.validate(datos)
        assert ok is False

    def test_vivienda_invalida_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["tipo_vivienda"] = "Castillo"
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("vivienda" in e.lower() for e in errores)

    @pytest.mark.parametrize("vivienda", TIPOS_VIVIENDA_VALIDOS)
    def test_viviendas_validas(self, validator, vivienda):
        datos = CASO_IDEAL.copy()
        datos["tipo_vivienda"] = vivienda
        ok, _ = validator.validate(datos)
        assert ok is True

    def test_proposito_invalido_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["proposito_credito"] = "Lujo"
        ok, errores = validator.validate(datos)
        assert ok is False

    @pytest.mark.parametrize("proposito", PROPOSITOS_VALIDOS)
    def test_propositos_validos(self, validator, proposito):
        datos = CASO_IDEAL.copy()
        datos["proposito_credito"] = proposito
        ok, _ = validator.validate(datos)
        assert ok is True

    def test_monto_menor_500_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["monto_credito"] = 499
        ok, errores = validator.validate(datos)
        assert ok is False

    def test_monto_mayor_50000_falla(self, validator):
        datos = CASO_IDEAL.copy()
        datos["monto_credito"] = 50001
        ok, errores = validator.validate(datos)
        assert ok is False

    def test_multiples_rangos_invalidos(self, validator):
        ok, errores = validator.validate(DATOS_RANGOS_EXTREMOS)
        assert ok is False
        assert len(errores) >= 5


# ════════════════════════════════════════════════════════════
# GRUPO D — Coherencia lógica
# ════════════════════════════════════════════════════════════

class TestCoherencia:
    """Tests para validación de coherencia (D001–D003)."""

    def test_antiguedad_mayor_edad_menos_15(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 25
        datos["antiguedad_laboral"] = 15  # 15 > 25-15=10
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("Incoherencia" in e for e in errores)

    def test_antiguedad_igual_edad_menos_15_pasa(self, validator):
        datos = CASO_IDEAL.copy()
        datos["edad"] = 25
        datos["antiguedad_laboral"] = 10  # = 25-15
        ok, errores = validator.validate(datos)
        assert ok is True

    def test_deuda_supera_24_meses_ingreso(self, validator):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = 10000
        datos["total_deuda_actual"] = 250000  # > 10000*24
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("24 meses" in e for e in errores)

    def test_monto_supera_18_meses_ingreso(self, validator):
        datos = CASO_IDEAL.copy()
        datos["ingreso_mensual"] = 2000
        datos["monto_credito"] = 40000  # > 2000*18
        ok, errores = validator.validate(datos)
        assert ok is False
        assert any("18 meses" in e for e in errores)


# ════════════════════════════════════════════════════════════
# SANITIZACIÓN
# ════════════════════════════════════════════════════════════

class TestSanitizacion:
    """Tests para el método sanitize()."""

    def test_sanitizar_strings_a_numeros(self, validator):
        limpio = validator.sanitize(DATOS_SANITIZAR)
        assert isinstance(limpio["edad"], int)
        assert limpio["edad"] == 35
        assert isinstance(limpio["ingreso_mensual"], float)
        assert limpio["ingreso_mensual"] == 25000.0

    def test_sanitizar_capitaliza_vivienda(self, validator):
        limpio = validator.sanitize(DATOS_SANITIZAR)
        assert limpio["tipo_vivienda"] == "Propia"

    def test_sanitizar_capitaliza_proposito(self, validator):
        limpio = validator.sanitize(DATOS_SANITIZAR)
        assert limpio["proposito_credito"] == "Negocio"

    def test_sanitizar_y_validar_pasa(self, validator):
        limpio = validator.sanitize(DATOS_SANITIZAR)
        ok, errores = validator.validate(limpio)
        assert ok is True, f"Errores: {errores}"

    def test_sanitizar_no_modifica_original(self, validator):
        original = DATOS_SANITIZAR.copy()
        _ = validator.sanitize(original)
        assert original["edad"] == DATOS_SANITIZAR["edad"]

    def test_sanitizar_entero_float(self, validator):
        datos = {"edad": 35.0}
        limpio = validator.sanitize(datos)
        assert limpio["edad"] == 35
        assert isinstance(limpio["edad"], int)

    def test_sanitizar_monto_con_simbolo(self, validator):
        datos = {"monto_credito": "$15,000.50"}
        limpio = validator.sanitize(datos)
        assert isinstance(limpio["monto_credito"], float)
        assert limpio["monto_credito"] == 15000.50

    def test_sanitizar_valor_no_convertible(self, validator):
        datos = {"edad": "abc"}
        limpio = validator.sanitize(datos)
        # No se puede convertir → se deja como está
        assert limpio["edad"] == "abc"
