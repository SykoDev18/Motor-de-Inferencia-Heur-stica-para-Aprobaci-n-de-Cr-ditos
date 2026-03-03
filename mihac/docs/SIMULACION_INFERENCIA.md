# MIHAC v1.0 — Simulación Escrita del Proceso de Inferencia

> **Motor de Inferencia Heurística para Aprobación de Créditos**
> Documento de simulación paso a paso con tres casos reales ejecutados por el motor.

---

## Índice

1. [Caso 1: Cliente Ideal → APROBADO](#caso-1-cliente-ideal--aprobado)
2. [Caso 2: Alto Riesgo → RECHAZADO](#caso-2-alto-riesgo--rechazado)
3. [Caso 3: Zona Gris → REVISIÓN MANUAL](#caso-3-zona-gris--revisión-manual)
4. [Tabla Comparativa de los 3 Casos](#tabla-comparativa-de-los-3-casos)

> **Nota**: Todos los datos y resultados fueron generados ejecutando `InferenceEngine.evaluate()` con las entradas exactas mostradas. Los outputs son reales, no simulados manualmente.

---

## Caso 1: Cliente Ideal → APROBADO

### Datos de entrada

| Variable | Valor |
|:---------|:------|
| Edad | 45 años |
| Ingreso mensual | $35,000.00 |
| Total deuda actual | $2,000.00 |
| Historial crediticio | 2 (Bueno) |
| Antigüedad laboral | 15 años |
| Número de dependientes | 1 |
| Tipo de vivienda | Propia |
| Propósito del crédito | Negocio |
| Monto solicitado | $10,000.00 |

### Paso 1 — Sanitización

Los datos se reciben y normalizan. En este caso todos los campos ya están en el tipo correcto, por lo que la sanitización no requiere conversiones.

### Paso 2 — Validación (Grupos A–D)

| Grupo | Verificación | Resultado |
|:------|:-------------|:---------:|
| A — Campos obligatorios | 9/9 presentes | ✓ |
| B — Tipos de dato | Enteros y flotantes correctos | ✓ |
| C — Rangos | Edad 45 ∈ [18,99], Ingreso > 0, Monto ∈ [500,50000], etc. | ✓ |
| D — Coherencia | Antigüedad 15 ≤ edad-15 = 30 | ✓ |

**Resultado**: `(True, [])` — datos válidos, sin errores.

### Paso 3 — Cálculo del DTI

```
DTI = total_deuda_actual / ingreso_mensual
DTI = $2,000 / $35,000 = 0.0571
DTI = 5.71%

Clasificación: BAJO (< 25%)
```

**Interpretación**: Carga de deuda saludable. El solicitante tiene amplio margen para nuevas obligaciones.

### Paso 4 — Cálculo de Sub-Scores

#### Solvencia (máx. 40 pts)
```
base = min(35000 / 30000 × 20, 20) = min(23.33, 20) = 20.0
ajuste_dti = +10  (DTI < 25%)
ajuste_deps = 1 × 1.5 = 1.5
total = 20.0 + 10.0 - 1.5 = 28.5 → 28 pts
```

#### Estabilidad (máx. 30 pts)
```
antigüedad = 15 → pts_antig = 28  (≥ 5 años)
vivienda = "Propia" → pts_viv = 8
total = min(28 + 8, 30) = 30 pts
```

#### Historial (máx. 20 pts)
```
historial = 2 (Bueno) → 20 pts
```

#### Perfil (máx. 10 pts)
```
propósito = "Negocio" → pts = 10
edad = 45 → bonus = 2  (25 ≤ 45 ≤ 55)
total = min(10 + 2, 10) = 10 pts
```

**Score base = 28 + 30 + 20 + 10 = 88 puntos**

### Paso 5 — Evaluación de Reglas Heurísticas

| Regla | Condición | ¿Cumple? | Impacto |
|:------|:----------|:--------:|--------:|
| R001 | historial == 2 | ✓ SÍ | **+20** |
| R002 | historial == 0 | ✗ No | — |
| R003 | antigüedad >= 5 | ✓ SÍ | **+15** |
| R004 | antigüedad < 1 | ✗ No | — |
| R005 | vivienda == "Propia" | ✓ SÍ | **+10** |
| R006 | propósito == "Negocio" | ✓ SÍ | **+8** |
| R007 | propósito == "Educacion" | ✗ No | — |
| R008 | propósito == "Vacaciones" | ✗ No | — |
| R009 | edad < 21 | ✗ No (45) | — |
| R010 | dependientes >= 4 | ✗ No (1) | — |
| R011 | hist==1 AND dti<0.25 AND antig>=3 | ✗ No (hist=2, no 1) | — |
| R012 | ingreso >= monto×0.25 AND hist!=0 | ✓ SÍ (35000 ≥ 2500 AND 2≠0) | **+10** |
| R013 | deuda==0 AND antig>=2 | ✗ No (deuda=2000) | — |
| R014 | dti > 0.40 | ✗ No (0.057) | — |
| R015 | deps==0 AND viv=="Propia" AND antig>=3 | ✗ No (deps=1) | — |

**Reglas activadas: R001, R003, R005, R006, R012**
**Impacto total: +20 +15 +10 +8 +10 = +63 puntos**

### Paso 6 — Score Final y Dictamen

```
score_raw = score_base + impacto_reglas = 88 + 63 = 151
score_final = clamp(151, 0, 100) = 100

umbral = 80  (monto $10,000 ≤ $20,000)

Evaluación:
  DTI = BAJO (no es CRITICO) → no rechazo automático
  score (100) >= umbral (80) → APROBADO
```

**DICTAMEN: APROBADO** (Score 100/100, Umbral 80)

### Paso 7 — Explicación generada por el motor

```
───────────────────────────────────────────────────────
EVALUACIÓN CREDITICIA MIHAC
Fecha: 2026-03-03 12:34:29
───────────────────────────────────────────────────────
DICTAMEN: APROBADO
Score crediticio: 100/100  |  Umbral requerido: 80
───────────────────────────────────────────────────────

ANÁLISIS DE SOLVENCIA
• Ingreso mensual declarado: $35,000.00
• Deuda total vigente:       $2,000.00
• DTI (Relación Deuda/Ingreso): 5.7% — BAJO
  Carga de deuda saludable. El solicitante tiene amplio
  margen para nuevas obligaciones.

DESGLOSE DEL SCORE
  Solvencia    (28/40 pts): ██████████░░░░░
  Estabilidad  (30/30 pts): ███████████████
  Historial    (20/20 pts): ███████████████
  Perfil       (10/10 pts): ███████████████

FACTORES DETERMINANTES
  Positivos:
    ▲ R001: +20 — Premio por historial crediticio bueno
    ▲ R003: +15 — Estabilidad laboral alta (5+ años)
    ▲ R005: +10 — Arraigo por vivienda propia
    ▲ R012: +10 — Margen de ingreso amplio sobre la cuota
    ▲ R006: +8 — Crédito productivo (Negocio)
  Negativos:
    No se identificaron factores negativos.
  Compensaciones heurísticas activadas:
    ⟳ R012: +10 — Margen de ingreso amplio sobre la cuota

CONCLUSIÓN
  El perfil crediticio del solicitante cumple con los
  criterios de aprobación del sistema MIHAC. Los factores
  de premio por historial crediticio bueno y estabilidad
  laboral alta respaldan la capacidad y voluntad de pago.
  Se recomienda proceder con el desembolso por $10,000.00
  bajo las condiciones estándar de la institución.
───────────────────────────────────────────────────────
```

---

## Caso 2: Alto Riesgo → RECHAZADO

### Datos de entrada

| Variable | Valor |
|:---------|:------|
| Edad | 19 años |
| Ingreso mensual | $4,000.00 |
| Total deuda actual | $8,000.00 |
| Historial crediticio | 0 (Malo) |
| Antigüedad laboral | 0 años |
| Número de dependientes | 3 |
| Tipo de vivienda | Rentada |
| Propósito del crédito | Vacaciones |
| Monto solicitado | $15,000.00 |

### Paso 2 — Validación

| Grupo | Resultado |
|:------|:---------:|
| A — Campos | ✓ 9/9 |
| B — Tipos | ✓ |
| C — Rangos | ✓ (edad 19 ∈ [18,99]) |
| D — Coherencia | ✓ (antigüedad 0 ≤ 19-15=4) |

### Paso 3 — DTI

```
DTI = $8,000 / $4,000 = 2.0000
DTI = 200.00%

Clasificación: CRITICO (≥ 60%)
```

**Interpretación**: Sobreendeudamiento crítico. Más del 60% del ingreso se destina al servicio de deudas.

> ⚠ **Alerta**: DTI CRITICO activa el rechazo automático independientemente del score.

### Paso 4 — Sub-Scores

#### Solvencia
```
base = min(4000 / 30000 × 20, 20) = min(2.67, 20) = 2.67
ajuste_dti = -15  (DTI ≥ 60%)
ajuste_deps = 3 × 1.5 = 4.5
total = 2.67 - 15 - 4.5 = -16.83 → clamp → 0 pts
```

#### Estabilidad
```
antigüedad = 0 → pts_antig = 0
vivienda = "Rentada" → pts_viv = 0
total = 0 pts
```

#### Historial
```
historial = 0 (Malo) → 0 pts
```

#### Perfil
```
propósito = "Vacaciones" → pts = 0
edad = 19 → bonus = 0  (19 < 25, fuera del rango óptimo)
total = 0 pts
```

**Score base = 0 + 0 + 0 + 0 = 0 puntos**

### Paso 5 — Reglas

| Regla | ¿Cumple? | Impacto |
|:------|:--------:|--------:|
| R002 | ✓ historial == 0 | **-25** |
| R004 | ✓ antigüedad < 1 | **-10** |
| R008 | ✓ propósito == "Vacaciones" | **-8** |
| R009 | ✓ edad < 21 (19) | **-12** |
| R014 | ✓ dti > 0.40 (2.00) | **-20** |
| R001, R003, R005-R007, R010-R013, R015 | ✗ | — |

**Reglas activadas: R002, R004, R008, R009, R014**
**Impacto total: -25 -10 -8 -12 -20 = -75 puntos**

### Paso 6 — Score Final y Dictamen

```
score_raw = 0 + (-75) = -75
score_final = clamp(-75, 0, 100) = 0

umbral = 80  (monto $15,000 ≤ $20,000)

Evaluación:
  DTI = CRITICO → RECHAZADO AUTOMÁTICO
  (incluso si el score fuera alto, el DTI crítico rechaza)
```

**DICTAMEN: RECHAZADO** (Score 0/100, DTI CRITICO)

### Paso 7 — Explicación generada

```
───────────────────────────────────────────────────────
EVALUACIÓN CREDITICIA MIHAC
───────────────────────────────────────────────────────
DICTAMEN: RECHAZADO
Score crediticio: 0/100  |  Umbral requerido: 80
───────────────────────────────────────────────────────

ANÁLISIS DE SOLVENCIA
• Ingreso mensual declarado: $4,000.00
• Deuda total vigente:       $8,000.00
• DTI (Relación Deuda/Ingreso): 200.0% — CRITICO
  Sobreendeudamiento crítico. Más del 60% del ingreso
  se destina al servicio de deudas.

DESGLOSE DEL SCORE
  Solvencia    ( 0/40 pts): ░░░░░░░░░░░░░░░
  Estabilidad  ( 0/30 pts): ░░░░░░░░░░░░░░░
  Historial    ( 0/20 pts): ░░░░░░░░░░░░░░░
  Perfil       ( 0/10 pts): ░░░░░░░░░░░░░░░

FACTORES DETERMINANTES
  Positivos:
    No se identificaron factores positivos relevantes.
  Negativos:
    ▼ R002: -25 — Penalización por historial crediticio malo
    ▼ R014: -20 — DTI alto: penalización por sobreendeudamiento
    ▼ R009: -12 — Perfil de alto riesgo por juventud
    ▼ R004: -10 — Sin trayectoria laboral (menos de 1 año)
    ▼ R008: -8 — Gasto no productivo (Vacaciones)

CONCLUSIÓN
  Solicitud RECHAZADA por sobreendeudamiento crítico.
  El solicitante destina el 200.0% de su ingreso mensual
  al servicio de deudas existentes, lo que supera el
  límite de riesgo aceptable (60%). Se recomienda revisar
  en 12 meses si la situación de deuda mejora.
───────────────────────────────────────────────────────
```

---

## Caso 3: Zona Gris → REVISIÓN MANUAL

### Datos de entrada

| Variable | Valor |
|:---------|:------|
| Edad | 30 años |
| Ingreso mensual | $15,000.00 |
| Total deuda actual | $3,000.00 |
| Historial crediticio | 1 (Neutro) |
| Antigüedad laboral | 3 años |
| Número de dependientes | 2 |
| Tipo de vivienda | Familiar |
| Propósito del crédito | Consumo |
| Monto solicitado | $12,000.00 |

### Paso 3 — DTI

```
DTI = $3,000 / $15,000 = 0.2000
DTI = 20.00%

Clasificación: BAJO (< 25%)
```

### Paso 4 — Sub-Scores

#### Solvencia
```
base = min(15000 / 30000 × 20, 20) = 10.0
ajuste_dti = +10  (DTI < 25%)
ajuste_deps = 2 × 1.5 = 3.0
total = 10.0 + 10.0 - 3.0 = 17.0 → 17 pts
```

#### Estabilidad
```
antigüedad = 3 → pts_antig = 18  (2 ≤ 3 < 5)
vivienda = "Familiar" → pts_viv = 3
total = min(18 + 3, 30) = 21 pts
```

#### Historial
```
historial = 1 (Neutro) → 10 pts
```

#### Perfil
```
propósito = "Consumo" → pts = 4
edad = 30 → bonus = 2  (25 ≤ 30 ≤ 55)
total = min(4 + 2, 10) = 6 pts
```

**Score base = 17 + 21 + 10 + 6 = 54 puntos**

### Paso 5 — Reglas

| Regla | ¿Cumple? | Razonamiento | Impacto |
|:------|:--------:|:-------------|--------:|
| R001 | ✗ | historial=1, no 2 | — |
| R002 | ✗ | historial=1, no 0 | — |
| R003 | ✗ | antigüedad=3, no ≥5 | — |
| R004 | ✗ | antigüedad=3, no <1 | — |
| R005 | ✗ | vivienda="Familiar", no "Propia" | — |
| R006 | ✗ | propósito="Consumo", no "Negocio" | — |
| R007 | ✗ | propósito="Consumo", no "Educacion" | — |
| R008 | ✗ | propósito="Consumo", no "Vacaciones" | — |
| R009 | ✗ | edad=30, no <21 | — |
| R010 | ✗ | dependientes=2, no ≥4 | — |
| **R011** | **✓** | hist==1 ✓ AND dti=0.20<0.25 ✓ AND antig=3≥3 ✓ | **+15** |
| **R012** | **✓** | ingreso=15000 ≥ 12000×0.25=3000 ✓ AND hist=1≠0 ✓ | **+10** |
| R013 | ✗ | deuda=3000, no ==0 | — |
| R014 | ✗ | dti=0.20, no >0.40 | — |
| R015 | ✗ | dependientes=2, no ==0 | — |

**Reglas activadas: R011, R012 (ambas de compensación)**
**Impacto total: +15 +10 = +25 puntos**

> **Observación clave**: Sin las reglas de compensación, el score sería 54 (RECHAZADO). Las compensaciones R011 y R012 reconocen que aunque el historial es neutro, la buena solvencia y estabilidad compensan parcialmente, elevando el score a 79 → REVISIÓN MANUAL.

### Paso 6 — Score Final y Dictamen

```
score_raw = 54 + 25 = 79
score_final = clamp(79, 0, 100) = 79

umbral = 80  (monto $12,000 ≤ $20,000)

Evaluación:
  DTI = BAJO (no es CRITICO)
  score (79) < umbral (80) → NO aprobado
  score (79) >= umbral - 20 (60) → REVISION_MANUAL
```

**DICTAMEN: REVISION_MANUAL** (Score 79/100, Umbral 80, falta 1 punto)

### Paso 7 — Explicación generada

```
───────────────────────────────────────────────────────
EVALUACIÓN CREDITICIA MIHAC
───────────────────────────────────────────────────────
DICTAMEN: REVISION_MANUAL
Score crediticio: 79/100  |  Umbral requerido: 80
───────────────────────────────────────────────────────

ANÁLISIS DE SOLVENCIA
• Ingreso mensual declarado: $15,000.00
• Deuda total vigente:       $3,000.00
• DTI (Relación Deuda/Ingreso): 20.0% — BAJO
  Carga de deuda saludable. El solicitante tiene amplio
  margen para nuevas obligaciones.

DESGLOSE DEL SCORE
  Solvencia    (17/40 pts): ██████░░░░░░░░░
  Estabilidad  (21/30 pts): ██████████░░░░░
  Historial    (10/20 pts): ███████░░░░░░░░
  Perfil       ( 6/10 pts): █████████░░░░░░

FACTORES DETERMINANTES
  Positivos:
    ▲ R011: +15 — Historial neutro compensado por
                   solvencia y estabilidad
    ▲ R012: +10 — Margen de ingreso amplio sobre la cuota
  Negativos:
    No se identificaron factores negativos.
  Compensaciones heurísticas activadas:
    ⟳ R011: +15 — Historial neutro compensado
    ⟳ R012: +10 — Margen de ingreso amplio

CONCLUSIÓN
  El solicitante se encuentra en zona de análisis. Su
  score de 79 puntos está dentro del rango de revisión
  (60–80), lo que indica un perfil con características
  mixtas que requieren evaluación adicional por parte de
  un analista humano. El factor principal de incertidumbre
  es el historial crediticio neutro, que no permite
  confirmar un patrón de cumplimiento.
───────────────────────────────────────────────────────
```

---

## Tabla Comparativa de los 3 Casos

| Métrica | Caso 1 (Ideal) | Caso 2 (Riesgo) | Caso 3 (Gris) |
|:--------|:--------------:|:----------------:|:--------------:|
| **DTI** | 5.71% (BAJO) | 200.00% (CRITICO) | 20.00% (BAJO) |
| **Solvencia** | 28/40 | 0/40 | 17/40 |
| **Estabilidad** | 30/30 | 0/30 | 21/30 |
| **Historial** | 20/20 | 0/20 | 10/20 |
| **Perfil** | 10/10 | 0/10 | 6/10 |
| **Score base** | 88 | 0 | 54 |
| **Reglas positivas** | +63 (5 reglas) | 0 | +25 (2 reglas) |
| **Reglas negativas** | 0 | -75 (5 reglas) | 0 |
| **Score final** | **100** | **0** | **79** |
| **Umbral** | 80 | 80 | 80 |
| **Dictamen** | **APROBADO** | **RECHAZADO** | **REVISION_MANUAL** |

### Flujo visual de decisión

```
                    ┌─────────────┐
                    │ DTI CRITICO? │
                    └──────┬──────┘
                     Sí    │    No
                     ▼     │    ▼
              ┌──────────┐ │  ┌──────────────────┐
  Caso 2 ──→ │ RECHAZADO│ │  │ score >= umbral?  │
              └──────────┘ │  └────────┬─────────┘
                           │   Sí      │      No
                           │   ▼       │      ▼
                           │┌────────┐ │ ┌─────────────────┐
               Caso 1 ──→ ││APROBADO│ │ │score >= umbral-20│
                           │└────────┘ │ └────────┬────────┘
                           │           │   Sí     │    No
                           │           │   ▼      │    ▼
                           │           │┌────────┐│┌──────────┐
                   Caso 3 ──→         ││REVISIÓN│││ RECHAZADO│
                                      │└────────┘│└──────────┘
```

---

*Simulación ejecutada con datos reales — MIHAC v1.0 © 2026*
