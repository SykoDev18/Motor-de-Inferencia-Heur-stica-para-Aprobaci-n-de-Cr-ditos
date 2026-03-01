# ============================================================
# MIHAC v1.0 — Fixtures de Datos para Tests
# tests/fixtures.py
# ============================================================
# Casos de prueba representativos para todos los escenarios
# del motor de inferencia MIHAC.
# ============================================================

# ── CASO IDEAL: Aprobado con score máximo ────────────────────
CASO_IDEAL = {
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

# ── CASO RIESGO: Rechazado por perfil de alto riesgo ────────
CASO_RIESGO = {
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

# ── CASO GRIS: Revisión manual por perfil mixto ─────────────
CASO_GRIS = {
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

# ── CASO JOVEN + VACACIONES: Doble penalización ─────────────
CASO_JOVEN_VACACIONES = {
    "edad": 20,
    "ingreso_mensual": 10000.0,
    "total_deuda_actual": 2000.0,
    "historial_crediticio": 1,
    "antiguedad_laboral": 1,
    "numero_dependientes": 0,
    "tipo_vivienda": "Familiar",
    "proposito_credito": "Vacaciones",
    "monto_credito": 5000.0,
}

# ── CASO SIN HISTORIAL PERO SOLVENTE (compensación R011) ────
CASO_SIN_HISTORIAL_SOLVENTE = {
    "edad": 30,
    "ingreso_mensual": 30000.0,
    "total_deuda_actual": 2000.0,
    "historial_crediticio": 1,
    "antiguedad_laboral": 5,
    "numero_dependientes": 0,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Negocio",
    "monto_credito": 10000.0,
}

# ── CASO DEUDA CERO (compensación R013) ─────────────────────
CASO_DEUDA_CERO = {
    "edad": 40,
    "ingreso_mensual": 20000.0,
    "total_deuda_actual": 0.0,
    "historial_crediticio": 2,
    "antiguedad_laboral": 10,
    "numero_dependientes": 2,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Educacion",
    "monto_credito": 8000.0,
}

# ── CASO MONTO ALTO: umbral 85 ──────────────────────────────
CASO_MONTO_ALTO = {
    "edad": 45,
    "ingreso_mensual": 40000.0,
    "total_deuda_actual": 5000.0,
    "historial_crediticio": 2,
    "antiguedad_laboral": 15,
    "numero_dependientes": 1,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Negocio",
    "monto_credito": 45000.0,
}

# ── CASO FRONTERA REVISIÓN: score justo en el límite ────────
CASO_FRONTERA_REVISION = {
    "edad": 26,
    "ingreso_mensual": 12000.0,
    "total_deuda_actual": 4000.0,
    "historial_crediticio": 1,
    "antiguedad_laboral": 3,
    "numero_dependientes": 2,
    "tipo_vivienda": "Rentada",
    "proposito_credito": "Consumo",
    "monto_credito": 8000.0,
}


# ── DATOS INVÁLIDOS ─────────────────────────────────────────

DATOS_INVALIDOS_TIPOS = {
    "edad": "treinta",
    "ingreso_mensual": "mucho",
    "total_deuda_actual": None,
    "historial_crediticio": 2.5,
    "antiguedad_laboral": [5],
    "numero_dependientes": "dos",
    "tipo_vivienda": 123,
    "proposito_credito": True,
    "monto_credito": "quince mil",
}

DATOS_CAMPOS_FALTANTES = {
    "edad": 30,
    "ingreso_mensual": 15000.0,
    # Faltan los demás campos
}

DATOS_RANGOS_EXTREMOS = {
    "edad": 150,
    "ingreso_mensual": -5000.0,
    "total_deuda_actual": -100.0,
    "historial_crediticio": 9,
    "antiguedad_laboral": 50,
    "numero_dependientes": 20,
    "tipo_vivienda": "Castillo",
    "proposito_credito": "Lujo",
    "monto_credito": 999999.0,
}

# ── DATOS PARA SANITIZACIÓN ─────────────────────────────────

DATOS_SANITIZAR = {
    "edad": "  35 ",
    "ingreso_mensual": "$25,000.00",
    "total_deuda_actual": "4000",
    "historial_crediticio": "2",
    "antiguedad_laboral": "7.0",
    "numero_dependientes": " 1 ",
    "tipo_vivienda": "propia",
    "proposito_credito": "negocio",
    "monto_credito": "$15,000",
}
