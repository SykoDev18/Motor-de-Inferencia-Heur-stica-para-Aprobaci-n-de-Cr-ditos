# MIHAC v1.0 — Representación Formal y Arquitectura del Sistema Experto

## Tabla de Contenidos

1. [Representación Formal en Lógica de Predicados](#1-representación-formal-en-lógica-de-predicados)
   - 1.1 [Universo de Discurso](#11-universo-de-discurso)
   - 1.2 [Predicados Base (Hechos)](#12-predicados-base-hechos)
   - 1.3 [Funciones de Evaluación](#13-funciones-de-evaluación)
   - 1.4 [Reglas Directas en Lógica de Predicados](#14-reglas-directas-en-lógica-de-predicados)
   - 1.5 [Reglas de Compensación (Conjuntivas)](#15-reglas-de-compensación-conjuntivas)
   - 1.6 [Función de Score Final](#16-función-de-score-final)
   - 1.7 [Predicados de Decisión (Dictamen)](#17-predicados-de-decisión-dictamen)
2. [Arquitectura del Sistema Experto](#2-arquitectura-del-sistema-experto)
   - 2.1 [Base de Conocimiento](#21-base-de-conocimiento)
   - 2.2 [Motor de Inferencia](#22-motor-de-inferencia)
   - 2.3 [Memoria de Trabajo](#23-memoria-de-trabajo)
   - 2.4 [Módulo de Explicación](#24-módulo-de-explicación)
3. [Diagrama de Integración](#3-diagrama-de-integración)

---

## 1. Representación Formal en Lógica de Predicados

### 1.1 Universo de Discurso

Sea **S** el conjunto de todos los solicitantes de crédito. Para cada solicitante *x ∈ S*, se define un vector de 9 atributos observables que constituyen los **hechos** del sistema:

```
∀x ∈ S :  x = ⟨ edad(x), ingreso(x), deuda(x), historial(x),
              antiguedad(x), dependientes(x), vivienda(x),
              proposito(x), monto(x) ⟩
```

**Dominios de cada atributo:**

| Atributo | Símbolo | Dominio | Restricción |
|---|---|---|---|
| Edad | `edad(x)` | ℤ | 18 ≤ edad(x) ≤ 99 |
| Ingreso mensual | `ingreso(x)` | ℝ⁺ | ingreso(x) > 0 |
| Deuda total | `deuda(x)` | ℝ≥₀ | deuda(x) ≥ 0 |
| Historial crediticio | `historial(x)` | {0, 1, 2} | 0 = Malo, 1 = Neutro, 2 = Bueno |
| Antigüedad laboral | `antiguedad(x)` | ℤ≥₀ | 0 ≤ antiguedad(x) ≤ 40 |
| Núm. dependientes | `dependientes(x)` | ℤ≥₀ | 0 ≤ dependientes(x) ≤ 10 |
| Tipo de vivienda | `vivienda(x)` | V | V = {Propia, Familiar, Rentada} |
| Propósito del crédito | `proposito(x)` | P | P = {Negocio, Educacion, Consumo, Emergencia, Vacaciones} |
| Monto solicitado | `monto(x)` | ℝ⁺ | 500 ≤ monto(x) ≤ 50,000 |

### 1.2 Predicados Base (Hechos)

Se definen predicados unarios y binarios sobre el universo **S**:

```
HistorialBueno(x)   ≡  historial(x) = 2
HistorialNeutro(x)  ≡  historial(x) = 1
HistorialMalo(x)    ≡  historial(x) = 0

ViviendaPropia(x)   ≡  vivienda(x) = "Propia"
ViviendaFamiliar(x) ≡  vivienda(x) = "Familiar"
ViviendaRentada(x)  ≡  vivienda(x) = "Rentada"

PropositoNegocio(x)    ≡  proposito(x) = "Negocio"
PropositoEducacion(x)  ≡  proposito(x) = "Educacion"
PropositoVacaciones(x) ≡  proposito(x) = "Vacaciones"

Joven(x)            ≡  edad(x) < 21
EdadOptima(x)       ≡  25 ≤ edad(x) ≤ 55
CargaCritica(x)     ≡  dependientes(x) ≥ 4
EstableLab(x)       ≡  antiguedad(x) ≥ 5
SinTrayectoria(x)   ≡  antiguedad(x) < 1
SinDeudas(x)        ≡  deuda(x) = 0
```

### 1.3 Funciones de Evaluación

#### 1.3.1 Función DTI (Debt-To-Income)

```
                    ⎧ 1.0                      si ingreso(x) ≤ 0
DTI(x) = f_dti =   ⎨
                    ⎩ deuda(x) / ingreso(x)    si ingreso(x) > 0
```

**Predicados de clasificación DTI:**

```
DTI_Bajo(x)     ≡  DTI(x) < 0.25
DTI_Moderado(x) ≡  0.25 ≤ DTI(x) < 0.40
DTI_Alto(x)     ≡  0.40 ≤ DTI(x) < 0.60
DTI_Critico(x)  ≡  DTI(x) ≥ 0.60
```

Propiedad de partición exhaustiva y mutuamente excluyente:

```
∀x ∈ S : DTI_Bajo(x) ⊕ DTI_Moderado(x) ⊕ DTI_Alto(x) ⊕ DTI_Critico(x)
```

#### 1.3.2 Funciones de Sub-Score

Se definen 4 funciones de sub-score que mapean atributos del solicitante a puntuaciones parciales:

**a) Solvencia: f_sol : S → [0, 40]**

```
f_sol(x) = clamp(0, 40, base_ing(x) + ajuste_dti(x) − pen_dep(x))

donde:
  base_ing(x)  = min( ingreso(x) / 30000 × 20 , 20 )

                 ⎧ +10   si DTI_Bajo(x)
  ajuste_dti(x) = ⎨  +5   si DTI_Moderado(x)
                 ⎪  −5   si DTI_Alto(x)
                 ⎩ −15   si DTI_Critico(x)

  pen_dep(x) = dependientes(x) × 1.5
```

**b) Estabilidad: f_est : S → [0, 30]**

```
                      ⎧  0   si antiguedad(x) < 1
  pts_antiguedad(x) = ⎨  8   si 1 ≤ antiguedad(x) < 2
                      ⎪ 18   si 2 ≤ antiguedad(x) < 5
                      ⎩ 28   si antiguedad(x) ≥ 5

                      ⎧  8   si ViviendaPropia(x)
  pts_vivienda(x)   = ⎨  3   si ViviendaFamiliar(x)
                      ⎩  0   en otro caso

f_est(x) = min(pts_antiguedad(x) + pts_vivienda(x), 30)
```

**c) Historial: f_his : S → [0, 20]**

```
            ⎧ 20   si HistorialBueno(x)
f_his(x) =  ⎨ 10   si HistorialNeutro(x)
            ⎩  0   si HistorialMalo(x)
```

**d) Perfil: f_per : S → [0, 10]**

```
                     ⎧ 10   si PropositoNegocio(x)
                     ⎪  8   si PropositoEducacion(x)
  pts_proposito(x) = ⎨  6   si proposito(x) = "Emergencia"
                     ⎪  4   si proposito(x) = "Consumo"
                     ⎩  0   si PropositoVacaciones(x)

  bonus_edad(x) = ⎧ 2   si EdadOptima(x)
                  ⎩ 0   en otro caso

f_per(x) = min(pts_proposito(x) + bonus_edad(x), 10)
```

**Score base (suma de sub-scores):**

```
S_base(x) = f_sol(x) + f_est(x) + f_his(x) + f_per(x)

Propiedad: ∀x ∈ S : 0 ≤ S_base(x) ≤ 100
```

---

### 1.4 Reglas Directas en Lógica de Predicados

Las reglas directas del sistema se formalizan como sentencias universalmente cuantificadas con forma **IF-THEN** (modus ponens):

```
∀x ∈ S :  Condición(x)  →  Impacto(x, δ)
```

donde `Impacto(x, δ)` asigna un ajuste de δ puntos al score de x.

| ID | Fórmula en Lógica de Predicados | δ |
|---|---|---|
| R001 | ∀x : HistorialBueno(x) → Impacto(x, +20) | +20 |
| R002 | ∀x : HistorialMalo(x) → Impacto(x, −25) | −25 |
| R003 | ∀x : EstableLab(x) → Impacto(x, +15) | +15 |
| R004 | ∀x : SinTrayectoria(x) → Impacto(x, −10) | −10 |
| R005 | ∀x : ViviendaPropia(x) → Impacto(x, +10) | +10 |
| R006 | ∀x : PropositoNegocio(x) → Impacto(x, +8) | +8 |
| R007 | ∀x : PropositoEducacion(x) → Impacto(x, +6) | +6 |
| R008 | ∀x : PropositoVacaciones(x) → Impacto(x, −8) | −8 |
| R009 | ∀x : Joven(x) → Impacto(x, −12) | −12 |
| R010 | ∀x : CargaCritica(x) → Impacto(x, −10) | −10 |
| R014 | ∀x : DTI(x) > 0.40 → Impacto(x, −20) | −20 |

**Propiedad de independencia:** Las reglas directas no son mutuamente excluyentes; múltiples reglas pueden activarse simultáneamente para un mismo solicitante:

```
∃x ∈ S : HistorialBueno(x) ∧ EstableLab(x) ∧ ViviendaPropia(x)
         → Impacto(x, +20) ∧ Impacto(x, +15) ∧ Impacto(x, +10)
```

### 1.5 Reglas de Compensación (Conjuntivas)

Las reglas de compensación requieren que **todas** las condiciones se satisfagan simultáneamente (conjunción lógica ∧):

```
∀x ∈ S :  (C₁(x) ∧ C₂(x) ∧ ... ∧ Cₙ(x))  →  Impacto(x, δ)
```

| ID | Fórmula en Lógica de Predicados | δ |
|---|---|---|
| R011 | ∀x : HistorialNeutro(x) ∧ DTI_Bajo(x) ∧ antiguedad(x) ≥ 3 → Impacto(x, +15) | +15 |
| R012 | ∀x : ingreso(x) ≥ monto(x) × 0.25 ∧ ¬HistorialMalo(x) → Impacto(x, +10) | +10 |
| R013 | ∀x : SinDeudas(x) ∧ antiguedad(x) ≥ 2 → Impacto(x, +12) | +12 |
| R015 | ∀x : dependientes(x) = 0 ∧ ViviendaPropia(x) ∧ antiguedad(x) ≥ 3 → Impacto(x, +8) | +8 |

**Nota sobre R012:** Se utiliza una **comparación cruzada** entre campos (ingreso vs. monto con factor 0.25), formalizada como:

```
∀x : ingreso(x) ≥ f_ref(monto(x), 0.25) ∧ historial(x) ≠ 0  →  Impacto(x, +10)

donde f_ref(campo, factor) = campo × factor
```

### 1.6 Función de Score Final

Sea **R(x)** el conjunto de reglas activadas para el solicitante x:

```
R(x) = { rᵢ | rᵢ es una regla activa y Condición_rᵢ(x) es verdadera }
```

El impacto acumulado de las reglas activadas:

```
Δ(x) = Σ  δᵢ     ∀rᵢ ∈ R(x)
```

**Score final:**

```
S_final(x) = clamp(0, 100,  S_base(x) + Δ(x))

donde clamp(a, b, v) = max(a, min(b, v))
```

**Función de umbral:**

```
              ⎧ 85   si monto(x) > 20,000
U(x) =       ⎨
              ⎩ 80   en otro caso
```

### 1.7 Predicados de Decisión (Dictamen)

El dictamen final es una función de decisión con **prioridad de rechazo por DTI crítico**:

```
                        ⎧ RECHAZADO         si DTI_Critico(x)
Dictamen(x) =          ⎨ APROBADO          si ¬DTI_Critico(x) ∧ S_final(x) ≥ U(x)
                        ⎪ REVISION_MANUAL   si ¬DTI_Critico(x) ∧ S_final(x) ≥ U(x) − 20
                        ⎩ RECHAZADO         si ¬DTI_Critico(x) ∧ S_final(x) < U(x) − 20
```

**Propiedad de completitud:** Para todo solicitante válido, el sistema produce exactamente un dictamen:

```
∀x ∈ S : ∃! d ∈ {APROBADO, REVISION_MANUAL, RECHAZADO} : Dictamen(x) = d
```

**Propiedad de monotonía del rechazo por DTI:** El dictamen de un solicitante con DTI crítico es RECHAZADO independientemente de su score:

```
∀x ∈ S : DTI_Critico(x) → Dictamen(x) = RECHAZADO
```

---

## 2. Arquitectura del Sistema Experto

MIHAC sigue la arquitectura clásica de un Sistema Experto basado en reglas, compuesta por 4 componentes fundamentales:

```
┌─────────────────────────────────────────────────────────────────┐
│                     INTERFAZ DE USUARIO                        │
│                  (Flask Web / Formulario)                       │
└──────────────────────────┬──────────────────────────────────────┘
                           │ datos crudos del solicitante
                           ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│   BASE DE    │───▶│   MOTOR DE       │───▶│  MEMORIA DE      │
│ CONOCIMIENTO │    │   INFERENCIA     │    │  TRABAJO         │
│              │◀───│                  │◀───│                  │
│ (rules.json, │    │ (engine.py,      │    │ (resultado dict, │
│  config.py)  │    │  scorer.py,      │    │  session stats,  │
│              │    │  validator.py)   │    │  SQLite DB)      │
└──────────────┘    └────────┬─────────┘    └──────────────────┘
                             │ resultado estructurado
                             ▼
                    ┌──────────────────┐
                    │   MÓDULO DE      │
                    │   EXPLICACIÓN    │
                    │                  │
                    │ (explainer.py)   │
                    └──────────────────┘
                             │ texto en lenguaje natural
                             ▼
                    ┌──────────────────┐
                    │  SALIDA: Reporte │
                    │  (pantalla/PDF)  │
                    └──────────────────┘
```

---

### 2.1 Base de Conocimiento

La **Base de Conocimiento** (BC) almacena todo el saber experto del dominio crediticio de forma declarativa y separada del código de inferencia.

#### Componentes

| Componente | Archivo | Contenido |
|---|---|---|
| Reglas heurísticas | `knowledge/rules.json` | 15 reglas IF-THEN (10 directas + 1 DTI + 4 compensación) |
| Constantes globales | `config.py` | Umbrales, rangos válidos, dominios de variables |
| Funciones de scoring | `core/scorer.py` (métodos `_score_*`) | Sub-scores codificados proceduralmente |

#### Estructura de las reglas declarativas

Cada regla en `rules.json` tiene la estructura formal:

```json
{
  "id":                "R_nnn",
  "descripcion":       "Texto legible",
  "tipo":              "directa | compensacion",
  "condicion_campo":   "campo_a_evaluar",          // tipo directa
  "condicion_operador":"== | != | > | >= | < | <=",
  "condicion_valor":   valor_esperado,
  "condiciones":       [ ... ],                     // tipo compensación
  "impacto_puntos":    δ ∈ ℤ,
  "activa":            true | false
}
```

**Propiedad declarativa:** Las reglas son **datos**, no código. El motor las carga dinámicamente desde JSON, lo que permite modificar el comportamiento del sistema sin alterar el código fuente.

#### Representación formal de la BC

```
BC = ⟨ Reglas, Constantes, Funciones ⟩

Reglas     = { r₁, r₂, ..., r₁₅ }  ⊂  knowledge/rules.json
Constantes = { U_base=80, U_alto=85, DTI_critico=0.60, ...}  ⊂  config.py
Funciones  = { f_sol, f_est, f_his, f_per, f_dti }  ⊂  scorer.py
```

---

### 2.2 Motor de Inferencia

El **Motor de Inferencia** (MI) es el orquestador central que aplica el conocimiento de la BC sobre los hechos de la Memoria de Trabajo para derivar nuevas conclusiones.

#### Implementación

- **Archivo principal:** `core/engine.py` → clase `InferenceEngine`
- **Archivos auxiliares:** `core/validator.py` → clase `Validator`, `core/scorer.py` → clase `ScoringEngine`

#### Estrategia de inferencia: Encadenamiento hacia adelante (Forward Chaining)

MIHAC utiliza **encadenamiento hacia adelante** (data-driven): a partir de los hechos de entrada, el motor dispara reglas cuyas condiciones se satisfacen, generando nuevos hechos hasta alcanzar una conclusión.

```
Hechos iniciales  →  Reglas activadas  →  Hechos derivados  →  Dictamen
```

#### Pipeline de 9 pasos

El método `InferenceEngine.evaluate()` ejecuta el ciclo de inferencia en 9 pasos secuenciales:

```
Paso  │ Operación                  │ Componente        │ Entrada → Salida
──────┼────────────────────────────┼───────────────────┼───────────────────────────────
  1   │ Sanitizar datos            │ Validator         │ datos_crudos → datos_limpios
  2   │ Validar datos              │ Validator         │ datos_limpios → (válido, errores)
  3   │ Calcular DTI               │ ScoringEngine     │ (ingreso, deuda) → (dti, clasificación)
  4   │ Calcular sub-scores        │ ScoringEngine     │ (datos, dti) → {sol, est, his, per}
  5   │ Evaluar reglas heurísticas │ ScoringEngine     │ (datos, dti) → [reglas_activadas]
  6   │ Score final y dictamen     │ ScoringEngine     │ (sub, reglas, monto) → (score, dictamen)
  7   │ Generar explicación        │ Explainer         │ (datos, resultado) → texto
  8   │ Registrar en log           │ InferenceEngine   │ resultado → archivo de log
  9   │ Actualizar estadísticas    │ InferenceEngine   │ resultado → stats de sesión
```

#### Resolución de conflictos

Cuando múltiples reglas se activan simultáneamente, MIHAC emplea una estrategia **aditiva sin prioridad explícita**:

```
∀rᵢ, rⱼ ∈ R(x), i ≠ j :  Impacto_total = δᵢ + δⱼ
```

Todas las reglas activadas contribuyen su impacto al score final mediante suma algebraica. No existe mecanismo de prioridad entre reglas ni de inhibición mutua, con una **única excepción**:

```
DTI_Critico(x) → Dictamen = RECHAZADO    (anula cualquier score positivo)
```

#### Evaluación de condiciones

Para reglas **directas**, se evalúa una comparación simple:

```
evaluar_directa(x, r) ≡ campo_r(x)  operador_r  valor_r
```

Para reglas de **compensación**, se evalúa la conjunción de todas las condiciones:

```
evaluar_compensacion(x, r) ≡ ⋀ᵢ₌₁ⁿ (campoᵢ(x) operadorᵢ valorᵢ)
```

Los operadores soportados forman el conjunto: `{==, !=, >, >=, <, <=}`

---

### 2.3 Memoria de Trabajo

La **Memoria de Trabajo** (MT) es el espacio donde se almacenan los hechos conocidos (datos de entrada) y los hechos derivados (resultados intermedios y finales) durante una evaluación.

#### Niveles de persistencia

MIHAC mantiene la Memoria de Trabajo en tres niveles:

| Nivel | Alcance | Estructura | Persistencia |
|---|---|---|---|
| **Transaccional** | Una evaluación | `dict resultado` | Duración de `evaluate()` |
| **Sesión** | Múltiples evaluaciones | `InferenceEngine._stats` | Duración del proceso |
| **Permanente** | Histórico global | Tabla `evaluaciones` (SQLite) | Disco persistente |

#### Nivel 1 — Memoria transaccional (dict `resultado`)

Durante cada invocación de `evaluate()`, se construye progresivamente un diccionario que actúa como la memoria de trabajo inmediata:

```
MT_transaccional(x) = {
    // Hechos derivados en Paso 3
    dti_ratio          : ℝ,            // DTI calculado
    dti_clasificacion  : String,       // BAJO | MODERADO | ALTO | CRITICO

    // Hechos derivados en Paso 4
    sub_scores : {
        solvencia       : ℤ ∈ [0, 40],
        estabilidad     : ℤ ∈ [0, 30],
        historial_score : ℤ ∈ [0, 20],
        perfil          : ℤ ∈ [0, 10]
    },

    // Hechos derivados en Paso 5
    reglas_activadas   : [ {id, impacto, descripcion, tipo} ],
    compensaciones     : [ {id, impacto, descripcion, tipo} ],

    // Hechos derivados en Paso 6
    score_final        : ℤ ∈ [0, 100],
    umbral_aplicado    : {80, 85},
    dictamen           : String,       // APROBADO | REVISION_MANUAL | RECHAZADO

    // Enriquecimiento en Paso 7
    reporte_explicacion : String,      // Texto en lenguaje natural

    // Metadato
    errores_validacion : [ String ]
}
```

**Propiedad de construcción progresiva:** Cada paso del pipeline lee hechos producidos por pasos anteriores y agrega nuevos hechos, sin modificar los existentes:

```
MT₀ = datos_entrada(x)
MT₁ = MT₀ ∪ {datos_limpios}         // Paso 1
MT₂ = MT₁ ∪ {válido, errores}       // Paso 2
MT₃ = MT₂ ∪ {dti, dti_clasif}       // Paso 3
MT₄ = MT₃ ∪ {sub_scores}            // Paso 4
MT₅ = MT₄ ∪ {reglas_activadas}      // Paso 5
MT₆ = MT₅ ∪ {score, umbral, dict}   // Paso 6
MT₇ = MT₆ ∪ {reporte}               // Paso 7
```

#### Nivel 2 — Memoria de sesión (acumuladores estadísticos)

El motor mantiene contadores in-memory que se actualizan en cada evaluación:

```
Stats_sesion = {
    total_evaluaciones : ℤ≥₀,
    aprobados          : ℤ≥₀,
    rechazados         : ℤ≥₀,
    revision_manual    : ℤ≥₀,
    suma_scores        : ℝ≥₀,      // Para calcular promedio
    suma_dti           : ℝ≥₀       // Para calcular promedio
}
```

Métricas derivadas bajo demanda:
```
tasa_aprobacion = aprobados / total × 100
score_promedio  = suma_scores / total
dti_promedio    = suma_dti / total
```

#### Nivel 3 — Memoria permanente (SQLite)

Cada evaluación se persiste en la tabla `evaluaciones` del modelo SQLAlchemy (`app/models.py`), permitiendo consultas históricas, auditoría, y alimentando el dashboard de la interfaz web.

---

### 2.4 Módulo de Explicación

El **Módulo de Explicación** (ME) traduce los resultados numéricos de la inferencia a texto en lenguaje natural comprensible para analistas de crédito y clientes finales.

#### Implementación

- **Archivo:** `core/explainer.py` → clase `Explainer`
- **Métodos principales:**
  - `generate(datos, resultado)` → Reporte completo (multi-línea)
  - `generate_short(datos, resultado)` → Resumen de una línea

#### Capacidad explicativa

El módulo responde a la pregunta fundamental de un sistema experto: **"¿Por qué se llegó a esta conclusión?"**

```
∀x ∈ S : Explicación(x) = f_explicar(datos(x), MT_final(x))
```

#### Estructura del reporte completo

El método `generate()` produce un texto estructurado en 5 secciones:

```
┌─────────────────────────────────────────────┐
│  1. ENCABEZADO                              │
│     • Dictamen, Score, Umbral, Fecha        │
├─────────────────────────────────────────────┤
│  2. ANÁLISIS DE SOLVENCIA                   │
│     • Ingreso, Deuda, DTI, Interpretación   │
├─────────────────────────────────────────────┤
│  3. DESGLOSE DEL SCORE                      │
│     • 4 sub-scores con barras de progreso   │
│     Solvencia    (25/40 pts): ████████░░░   │
│     Estabilidad  (30/30 pts): ██████████    │
│     Historial    (20/20 pts): ██████████    │
│     Perfil       ( 8/10 pts): ████████░░    │
├─────────────────────────────────────────────┤
│  4. FACTORES DETERMINANTES                  │
│     ▲ Positivos:  R001 +20, R003 +15, ...   │
│     ▼ Negativos:  R014 -20, ...             │
│     ⟳ Compensaciones: R011 +15, ...         │
├─────────────────────────────────────────────┤
│  5. CONCLUSIÓN                              │
│     • Resumen narrativo + sugerencias       │
└─────────────────────────────────────────────┘
```

#### Diccionarios interpretativos

El módulo utiliza mapeos declarativos para transformar valores codificados en texto legible:

```
_HISTORIAL_LABELS   : {0 → "Malo", 1 → "Neutro", 2 → "Bueno"}
_DTI_INTERPRETACION : {BAJO → "Carga saludable...", ..., CRITICO → "Sobreendeudamiento..."}
_SUGERENCIAS        : {R002 → "Establecer historial positivo...", R014 → "Reducir deudas..."}
```

#### Trazabilidad

Para cada regla activada, la explicación incluye:
- **Identificador** de la regla (R001 – R015)
- **Impacto numérico** (+/− puntos)
- **Descripción** en lenguaje natural
- **Tipo** (directa o compensación)

Esto permite al usuario trazar el camino completo desde los hechos de entrada hasta la decisión final:

```
Hecho: historial(x) = 2
  → Predicado: HistorialBueno(x) = True
    → Regla R001 activada: Impacto +20
      → Score: S_base + 20 + Σ(otros δ)
        → Dictamen: APROBADO (si score ≥ umbral)
          → Explicación: "▲ R001: +20 — Premio por historial crediticio bueno"
```

---

## 3. Diagrama de Integración

El siguiente diagrama muestra el flujo completo de datos entre los 4 componentes durante una evaluación:

```
                    SOLICITANTE
                         │
                    datos crudos
                         │
    ┌────────────────────▼────────────────────────────────────────┐
    │                 MOTOR DE INFERENCIA                         │
    │                (engine.py → evaluate())                     │
    │                                                             │
    │  ┌──────────┐   ┌───────────┐   ┌──────────────────────┐  │
    │  │ Paso 1-2 │   │  Paso 3-6 │   │      Paso 7          │  │
    │  │Validator │──▶│  Scorer   │──▶│    Explainer          │  │
    │  │          │   │           │   │                       │  │
    │  │sanitizar │   │DTI, sub,  │   │Generar texto          │  │
    │  │validar   │   │reglas,    │   │en lenguaje natural    │  │
    │  │          │   │score,dict │   │                       │  │
    │  └──────────┘   └─────┬─────┘   └───────────┬───────────┘  │
    │        ▲              │                      │              │
    │        │         Lee reglas              Lee mapeos         │
    │        │         y constantes            interpretativos    │
    │        │              │                      │              │
    │  ┌─────┴──────────────▼──────────────────────▼───────────┐ │
    │  │              BASE DE CONOCIMIENTO                      │ │
    │  │  rules.json (15 reglas) │ config.py (constantes)       │ │
    │  │  scorer._score_* (funciones de sub-score)              │ │
    │  └────────────────────────────────────────────────────────┘ │
    │                                                             │
    │               Paso 8-9: Log + Stats                        │
    │                    │                                        │
    └────────────────────┼────────────────────────────────────────┘
                         │
                         ▼
    ┌────────────────────────────────────────────────────────────┐
    │              MEMORIA DE TRABAJO                            │
    │                                                            │
    │  Nivel 1: dict resultado (transaccional)                   │
    │  Nivel 2: _stats sesión (acumuladores in-memory)           │
    │  Nivel 3: SQLite evaluaciones (persistencia permanente)    │
    └────────────────────────────────────────────────────────────┘
                         │
                    resultado completo
                         │
                         ▼
                   INTERFAZ DE USUARIO
              (pantalla web / reporte PDF)
```

---

## Referencias Internas

| Documento | Contenido relacionado |
|---|---|
| `docs/MODELO_CONOCIMIENTO.md` | Variables del sistema, tabla de reglas, fallos comunes |
| `docs/SIMULACION_INFERENCIA.md` | Simulación manual de 3 casos con salida real del motor |
| `docs/ANALISIS_CRITICO.md` | Comparativa reglas vs. ML, análisis FODA |
| `knowledge/rules.json` | Código fuente de las 15 reglas declarativas |
| `config.py` | Constantes, umbrales y rangos de variables |

---

*Documento generado para MIHAC v1.0 — Sistema Experto de Evaluación Crediticia*
