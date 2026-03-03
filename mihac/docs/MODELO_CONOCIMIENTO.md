# MIHAC v1.0 — Modelo del Conocimiento

> **Motor de Inferencia Heurística para Aprobación de Créditos**
> Documento técnico del modelo de conocimiento, variables del sistema e identificación de fallas comunes.

---

## Índice

1. [Arquitectura del Conocimiento](#1-arquitectura-del-conocimiento)
2. [Variables del Sistema (Hechos)](#2-variables-del-sistema-hechos)
3. [Base de Reglas Heurísticas](#3-base-de-reglas-heurísticas)
4. [Mecanismo de Inferencia](#4-mecanismo-de-inferencia)
5. [Identificación de Fallas Comunes](#5-identificación-de-fallas-comunes)

---

## 1. Arquitectura del Conocimiento

MIHAC implementa un **sistema experto basado en reglas** con las siguientes capas:

```
┌─────────────────────────────────────────────────────────┐
│                    CAPA DE PRESENTACIÓN                  │
│           Flask Web + Reportes PDF + Dashboard          │
├─────────────────────────────────────────────────────────┤
│                 MOTOR DE INFERENCIA                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐ │
│  │ Validator │→│  Scorer   │→│  Rules    │→│Explainer│ │
│  │(sanitizar │  │(sub-scores│  │(heuríst. │  │(texto  │ │
│  │ validar)  │  │ DTI, base)│  │ IF-THEN) │  │natural)│ │
│  └──────────┘  └──────────┘  └──────────┘  └────────┘ │
├─────────────────────────────────────────────────────────┤
│               BASE DE CONOCIMIENTO                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │ rules.json   │  │  Umbrales    │  │  Pesos de    │  │
│  │ 15 reglas    │  │  DTI/Score   │  │  Sub-scores  │  │
│  │ IF-THEN      │  │  hardcoded   │  │  ponderados  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│                   CAPA DE DATOS                          │
│             SQLite + Log de auditoría                    │
└─────────────────────────────────────────────────────────┘
```

### Representación del conocimiento

El conocimiento del dominio crediticio se codifica en tres formas:

| Forma | Ubicación | Descripción |
|:------|:----------|:------------|
| **Reglas IF-THEN** | `knowledge/rules.json` | 15 reglas heurísticas con impactos en puntos |
| **Funciones de scoring** | `core/scorer.py` | Sub-scores ponderados con lógica embebida |
| **Umbrales de decisión** | `config.py` | Límites para DTI, score y variables de entrada |

---

## 2. Variables del Sistema (Hechos)

### 2.1 Variables de Entrada (9 hechos del solicitante)

Estos son los **hechos reales** que el sistema recibe como entrada para cada evaluación:

| # | Variable | Tipo | Rango válido | Descripción |
|:-:|:---------|:-----|:-------------|:------------|
| 1 | `edad` | Entero | 18 – 99 años | Edad del solicitante |
| 2 | `ingreso_mensual` | Flotante | > $0 | Ingreso mensual bruto declarado |
| 3 | `total_deuda_actual` | Flotante | ≥ $0 | Suma de todas las deudas vigentes |
| 4 | `historial_crediticio` | Entero | 0, 1, 2 | 0=Malo, 1=Neutro, 2=Bueno |
| 5 | `antiguedad_laboral` | Entero | 0 – 40 años | Años en el empleo actual |
| 6 | `numero_dependientes` | Entero | 0 – 10 | Personas dependientes económicamente |
| 7 | `tipo_vivienda` | Texto | Propia, Familiar, Rentada | Tipo de vivienda actual |
| 8 | `proposito_credito` | Texto | Negocio, Educacion, Consumo, Emergencia, Vacaciones | Destino del crédito |
| 9 | `monto_credito` | Flotante | $500 – $50,000 | Monto del crédito solicitado |

### 2.2 Variables Derivadas (calculadas por el motor)

| Variable | Fórmula | Clasificación |
|:---------|:--------|:-------------|
| `dti_ratio` | `total_deuda_actual / ingreso_mensual` | BAJO (<25%), MODERADO (25-40%), ALTO (40-60%), CRITICO (>60%) |
| `solvencia` | Función de ingreso, DTI y dependientes | 0 – 40 puntos |
| `estabilidad` | Función de antigüedad laboral y vivienda | 0 – 30 puntos |
| `historial_score` | Mapeo directo de historial_crediticio | 0, 10 o 20 puntos |
| `perfil` | Función de propósito y rango de edad | 0 – 10 puntos |
| `score_base` | `solvencia + estabilidad + historial_score + perfil` | 0 – 100 puntos |
| `impacto_reglas` | Suma de impactos de reglas activadas | -75 a +69 puntos |
| `score_final` | `clamp(score_base + impacto_reglas, 0, 100)` | 0 – 100 puntos |
| `umbral` | 85 si monto > $20,000; 80 en caso contrario | 80 u 85 |

### 2.3 Variable de Salida (Dictamen)

| Dictamen | Condición | Significado |
|:---------|:----------|:------------|
| **APROBADO** | `score >= umbral` Y DTI ≠ CRITICO | Crédito aprobado |
| **REVISION_MANUAL** | `score >= umbral - 20` Y `score < umbral` Y DTI ≠ CRITICO | Requiere análisis humano |
| **RECHAZADO** | `score < umbral - 20` O DTI = CRITICO | Crédito denegado |

> **Regla especial**: Si el DTI es CRITICO (>60%), el dictamen es **siempre RECHAZADO** independientemente del score.

### 2.4 Cálculo detallado de Sub-Scores

#### Solvencia (máx. 40 pts)

```
base = min(ingreso / 30,000 × 20, 20)          # Ingreso normalizado: 0–20 pts

if DTI < 25%:     ajuste_dti = +10
elif DTI < 40%:   ajuste_dti = +5
elif DTI < 60%:   ajuste_dti = -5
else:              ajuste_dti = -15              # DTI crítico

ajuste_deps = dependientes × 1.5                # Penalización proporcional

solvencia = clamp(base + ajuste_dti - ajuste_deps, 0, 40)
```

#### Estabilidad (máx. 30 pts)

```
if antigüedad < 1 año:   pts_antig = 0
elif antigüedad < 2:     pts_antig = 8
elif antigüedad < 5:     pts_antig = 18
else:                    pts_antig = 28          # 5+ años

if vivienda == "Propia":    pts_viv = 8
elif vivienda == "Familiar": pts_viv = 3
else:                       pts_viv = 0          # Rentada

estabilidad = min(pts_antig + pts_viv, 30)
```

#### Historial (máx. 20 pts)

```
if historial == 2 (Bueno):   historial_score = 20
elif historial == 1 (Neutro): historial_score = 10
else (Malo):                 historial_score = 0
```

#### Perfil (máx. 10 pts)

```
pts_proposito = {Negocio: 10, Educacion: 8, Emergencia: 6, Consumo: 4, Vacaciones: 0}

if 25 ≤ edad ≤ 55: bonus_edad = 2               # Rango óptimo
else:              bonus_edad = 0

perfil = min(pts_proposito + bonus_edad, 10)
```

---

## 3. Base de Reglas Heurísticas

### 3.1 Reglas Directas (10 reglas)

Formato: **SI** `campo operador valor` **ENTONCES** `impacto puntos`

| ID | Descripción | Condición | Impacto | Módulo |
|:---|:------------|:----------|--------:|:-------|
| R001 | Premio por historial bueno | `historial_crediticio == 2` | **+20** | historial |
| R002 | Penalización por historial malo | `historial_crediticio == 0` | **-25** | historial |
| R003 | Estabilidad laboral alta | `antiguedad_laboral >= 5` | **+15** | estabilidad |
| R004 | Sin trayectoria laboral | `antiguedad_laboral < 1` | **-10** | estabilidad |
| R005 | Arraigo por vivienda propia | `tipo_vivienda == "Propia"` | **+10** | estabilidad |
| R006 | Crédito productivo (Negocio) | `proposito_credito == "Negocio"` | **+8** | propósito |
| R007 | Inversión en capital humano | `proposito_credito == "Educacion"` | **+6** | propósito |
| R008 | Gasto no productivo | `proposito_credito == "Vacaciones"` | **-8** | propósito |
| R009 | Riesgo por juventud extrema | `edad < 21` | **-12** | perfil |
| R010 | Carga familiar crítica | `numero_dependientes >= 4` | **-10** | perfil |

### 3.2 Regla de Penalización por DTI (1 regla)

| ID | Descripción | Condición | Impacto | Flag |
|:---|:------------|:----------|--------:|:-----|
| R014 | Sobreendeudamiento | `dti > 0.40` | **-20** | DTI_ALTO_PENALIZADO |

### 3.3 Reglas de Compensación (4 reglas)

Formato: **SI** `condición₁ AND condición₂ [AND condición₃]` **ENTONCES** `impacto`

| ID | Descripción | Condiciones | Impacto |
|:---|:------------|:------------|--------:|
| R011 | Historial neutro compensado | `historial == 1` AND `DTI < 25%` AND `antigüedad >= 3` | **+15** |
| R012 | Margen de ingreso amplio | `ingreso >= monto × 0.25` AND `historial != 0` | **+10** |
| R013 | Sin deudas + trayectoria | `deuda == 0` AND `antigüedad >= 2` | **+12** |
| R015 | Máxima estabilidad | `dependientes == 0` AND `vivienda == "Propia"` AND `antigüedad >= 3` | **+8** |

### 3.4 Rango de impacto total

| Métrica | Valor |
|:--------|------:|
| Máximo impacto positivo posible | +69 pts (si todas las reglas positivas se activan) |
| Máximo impacto negativo posible | -75 pts (si todas las reglas negativas se activan) |
| Reglas de tipo directa | 11 |
| Reglas de tipo compensación | 4 |
| **Total reglas activas** | **15** |

### 3.5 Formato de la regla en JSON

```json
{
  "id": "R001",
  "descripcion": "Premio por historial crediticio bueno",
  "modulo": "historial",
  "condicion_campo": "historial_crediticio",
  "condicion_operador": "==",
  "condicion_valor": 2,
  "impacto_puntos": 20,
  "tipo": "directa",
  "activa": true
}
```

```json
{
  "id": "R011",
  "descripcion": "Historial neutro compensado por solvencia y estabilidad",
  "modulo": "compensacion",
  "condiciones": [
    {"campo": "historial_crediticio", "operador": "==", "valor": 1},
    {"campo": "dti", "operador": "<", "valor": 0.25},
    {"campo": "antiguedad_laboral", "operador": ">=", "valor": 3}
  ],
  "impacto_puntos": 15,
  "tipo": "compensacion",
  "activa": true
}
```

---

## 4. Mecanismo de Inferencia

### 4.1 Pipeline de 9 pasos

```
ENTRADA (9 variables)
    │
    ▼
┌──────────────────────────┐
│ Paso 1: SANITIZAR        │  Normalizar tipos, trim strings, coerción
│ Paso 2: VALIDAR          │  4 grupos (A-D): campos, tipos, rangos, coherencia
└──────────┬───────────────┘
           │ datos_limpios
           ▼
┌──────────────────────────┐
│ Paso 3: CALCULAR DTI     │  DTI = deuda / ingreso → clasificar BAJO/MOD/ALTO/CRIT
└──────────┬───────────────┘
           │ dti, dti_clasificacion
           ▼
┌──────────────────────────┐
│ Paso 4: SUB-SCORES       │  4 dimensiones ponderadas:
│   • Solvencia    (40 pts)│    Ingreso, DTI, dependientes
│   • Estabilidad  (30 pts)│    Antigüedad laboral, vivienda
│   • Historial    (20 pts)│    Score crediticio previo
│   • Perfil       (10 pts)│    Propósito, edad óptima
└──────────┬───────────────┘
           │ sub_scores (suma = score_base, max 100)
           ▼
┌──────────────────────────┐
│ Paso 5: REGLAS           │  Evaluar 15 reglas IF-THEN contra el perfil
│   Directas: campo op val │  Si se cumple → acumular impacto (+/-)
│   Compensación: AND mult.│  Todas las condiciones deben cumplirse
└──────────┬───────────────┘
           │ reglas_activadas, impacto_total
           ▼
┌──────────────────────────┐
│ Paso 6: SCORE + DICTAMEN │  score = clamp(base + impacto, 0, 100)
│   umbral = 85 si >20K    │  dictamen = APROBADO | REVISION | RECHAZADO
│   else umbral = 80       │  DTI CRITICO → RECHAZADO directo
└──────────┬───────────────┘
           │ score_final, dictamen
           ▼
┌──────────────────────────┐
│ Paso 7: EXPLICACIÓN      │  Generar texto en lenguaje natural
│   Análisis de solvencia  │  Barras de progreso por dimensión
│   Factores +/-           │  Conclusión y recomendaciones
│   Conclusión narrativa   │
└──────────┬───────────────┘
           │ reporte_explicacion
           ▼
┌──────────────────────────┐
│ Paso 8: LOG              │  Registrar en mihac_evaluations.log
│ Paso 9: RETORNAR         │  Dict completo con todos los campos
└──────────────────────────┘
           │
           ▼
SALIDA (score, dictamen, explicación, sub-scores, reglas, DTI...)
```

### 4.2 Encadenamiento hacia adelante (Forward Chaining)

MIHAC utiliza **encadenamiento hacia adelante**: parte de los hechos (datos del solicitante) y aplica reglas para derivar nuevos hechos hasta llegar al dictamen.

1. **Hechos iniciales**: 9 variables de entrada
2. **Hechos derivados nivel 1**: DTI, sub-scores
3. **Hechos derivados nivel 2**: Reglas activadas, impactos
4. **Hecho final**: Score + dictamen

No hay backtracking ni encadenamiento hacia atrás.

### 4.3 Resolución de conflictos

Cuando múltiples reglas se activan simultáneamente:

- **No hay conflicto**: Todas las reglas activadas se aplican acumulativamente
- **Clampeo**: El score final se limita al rango [0, 100]
- **Prioridad DTI**: DTI CRITICO anula el score (rechaza siempre)
- **Sin exclusión mutua**: Las reglas son aditivas, no excluyentes

---

## 5. Identificación de Fallas Comunes

### 5.1 Fallas de Datos de Entrada

| Falla | Causa | Detección | Manejo |
|:------|:------|:----------|:-------|
| **Campo faltante** | Formulario incompleto | Grupo A de validación | Error descriptivo: "El campo X es obligatorio" |
| **Tipo incorrecto** | Texto donde se espera número | Grupo B de validación | "El campo X debe ser numérico" |
| **Fuera de rango** | Edad=200, ingreso=-5000 | Grupo C de validación | "X debe estar entre MIN y MAX" |
| **Incoherencia lógica** | Antigüedad > edad - 15 | Grupo D de validación | "La antigüedad no es coherente con la edad" |
| **Valores categóricos inválidos** | vivienda="Casa" | Grupo C de validación | "Valor 'Casa' no válido. Opciones: Propia, Familiar, Rentada" |

### 5.2 Fallas de Borde en el Scoring

| Falla | Ejemplo | Comportamiento |
|:------|:--------|:---------------|
| **Score negativo** | Acumulación de penalizaciones extremas | Se clampea a 0 (nunca score negativo) |
| **Score > 100** | Todas las reglas positivas + sub-scores altos | Se clampea a 100 (nunca excede el máximo) |
| **DTI infinito** | Ingreso = 0 | Validador rechaza ingreso ≤ 0 antes del scoring |
| **DTI = 0** | Sin deudas | Funciona correctamente: DTI=0% → BAJO |
| **Sub-score desbordado** | Valores extremos en una dimensión | Cada sub-score se clampea a su máximo |

### 5.3 Fallas en las Reglas

| Falla | Causa | Protección |
|:------|:------|:-----------|
| **Regla con campo inexistente** | Typo en rules.json | `datos.get(campo)` retorna None → regla no se activa |
| **Operador inválido** | Operador "~=" no implementado | Retorna False, regla ignorada silenciosamente |
| **Regla desactivada** | `"activa": false` | Se omite en la iteración |
| **JSON malformado** | Error de sintaxis en rules.json | `_cargar_reglas()` captura JSONDecodeError, lista vacía |
| **Archivo no encontrado** | rules.json eliminado | Captura FileNotFoundError, opera sin reglas |
| **Error en comparación** | Comparar string con int | `_comparar()` captura TypeError → False |

### 5.4 Fallas Conocidas del Modelo

| Limitación | Descripción | Mitigación |
|:-----------|:------------|:-----------|
| **Sin historial temporal** | No considera tendencia del historial (mejorando/empeorando) | Se evalúa solo el estado actual (0/1/2) |
| **Sin validación de ingresos** | No cruza con fuentes externas | Dependiente de la declaración del solicitante |
| **Reglas estáticas** | Los impactos no se ajustan automáticamente | Actualizar rules.json manualmente según tendencias |
| **Sin correlación entre variables** | Cada sub-score es independiente | Las reglas de compensación mitigan parcialmente |
| **Umbral binario por monto** | Solo 80 o 85, sin gradiente | Simplificación deliberada; se puede extender |

### 5.5 Escenarios de Falla Frecuentes

#### Falso positivo (aprobado que no debería)
```
Edad: 55, Ingreso: $50,000, Deuda: $0, Historial: Bueno
Antigüedad: 20, Dependientes: 0, Vivienda: Propia
Propósito: Negocio, Monto: $50,000

→ Score 100, APROBADO
⚠ El monto es elevado (25% del ingreso mensual),
  pero el score no captura riesgo de concentración.
```

#### Falso negativo (rechazado que podría merecerlo)
```
Edad: 20, Ingreso: $25,000, Deuda: $3,000, Historial: Neutro
Antigüedad: 2, Dependientes: 0, Vivienda: Familiar
Propósito: Educación, Monto: $5,000

→ Score bajo por R009 (-12, juventud) + historial neutro
⚠ Es un joven con buenos ingresos para educación,
  pero el sistema penaliza la juventud.
```

**Mitigación**: La zona de REVISION_MANUAL (score 60-79) captura estos casos ambiguos, delegando al criterio humano.

---

*Documento técnico — MIHAC v1.0 © 2026*
