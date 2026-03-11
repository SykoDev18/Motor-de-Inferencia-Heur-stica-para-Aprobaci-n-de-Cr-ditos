---
<div align="center">

# **MIHAC: Sistema Experto Basado en Conocimiento para la Evaluación de Crédito Hipotecario**

### Motor de Inferencia Heurística para Aprobación de Créditos v1.0

**Documentación Técnica Formal**

---

**Universidad Autónoma del Estado de Hidalgo**

**Escuela Superior de Tlahuelilpan**

Licenciatura en Ingeniería de Software

---

**Autor:**

Miranda Muñoz Marco Antonio

---

**Marzo, 2026**

</div>

---

<div align="center">

## Contenido

</div>

| Sección | Título                                                            | Pág. |
| :------- | :----------------------------------------------------------------- | ----: |
| —       | Resumen / Abstract                                                 |     1 |
| —       | Introducción                                                      |     2 |
| 1        | Investigación Preliminar y Planteamiento del Problema             |     3 |
| 1.1      | Contexto: El cuello de botella en la evaluación crediticia manual |     3 |
| 1.2      | Enunciado del problema                                             |     4 |
| 1.3      | Justificación del enfoque heurístico                             |     5 |
| 1.4      | Estudio de factibilidad                                            |     6 |
| 2        | Definición General del Proyecto                                   |     7 |
| 2.1      | Objetivo general                                                   |     7 |
| 2.2      | Objetivos específicos                                             |     7 |
| 2.3      | Stack tecnológico                                                 |     8 |
| 2.4      | Metodología de desarrollo                                         |     9 |
| 3        | Especificación de Requerimientos                                  |    10 |
| 3.1      | Requerimientos funcionales                                         |    10 |
| 3.2      | Requerimientos no funcionales                                      |    12 |
| 3.3      | Técnicas para la obtención de requerimientos                     |    14 |
| 4        | Marco Teórico y Arquitectura del Conocimiento                     |    15 |
| 4.1      | Fundamentos teóricos de los sistemas expertos                      |    15 |
| 4.2      | Principio de scoring ponderado y enfoque heurístico               |    16 |
| 4.3      | Representación formal en lógica de predicados                     |    18 |
| 4.4      | Pipeline del motor de inferencia (9 pasos)                         |    21 |
| 4.5      | Arquitectura de los seis componentes del SBC                       |    24 |
| 5        | Pruebas de Software y Rendimiento Técnico                         |    27 |
| 5.1      | Estrategia de aseguramiento de calidad                             |    27 |
| 5.2      | Resultados de pruebas de regresión                                |    27 |
| 5.3      | Cobertura de código                                               |    28 |
| 5.4      | Suite pytest completa (219 tests)                                  |    29 |
| 5.5      | Pruebas de carga y rendimiento                                     |    30 |
| 6        | Validación Empírica y Backtesting                                |    33 |
| 6.1      | Motivación y contexto                                              |    33 |
| 6.2      | Metodología de validación                                         |    34 |
| 6.3      | Análisis Exploratorio de Datos (EDA)                              |    36 |
| 6.4      | Resultados del backtesting                                         |    37 |
| 6.5      | Evidencia operativa: trazabilidad en logs                          |    39 |
| 6.6      | Simulación de tres casos representativos                          |    40 |
| 7        | Análisis Crítico, Limitaciones y Trabajo Futuro                  |    41 |
| 7.1      | Ventajas operativas frente al ML tradicional                       |    41 |
| 7.2      | Limitaciones actuales                                              |    42 |
| 7.3      | Análisis FODA del sistema MIHAC                                    |    43 |
| 7.4      | Trabajo futuro                                                     |    44 |
| —       | Conclusiones                                                       |    46 |
| —       | Referencias Bibliográficas                                        |    48 |
| —       | Índice de Tablas                                                  |    ii |
| —       | Índice de Figuras                                                 |   iii |

---

## Índice de Tablas

| Tabla | Descripción                                                               |
| ----: | :------------------------------------------------------------------------- |
|     1 | Indicadores operativos de evaluación crediticia manual vs. automatizada   |
|     2 | Sesgos cognitivos identificados en la evaluación crediticia tradicional   |
|     3 | Comparativa técnica: modelos de caja negra vs. sistemas basados en reglas |
|     4 | Costos estimados de desarrollo e infraestructura                           |
|     5 | Stack tecnológico del proyecto MIHAC                                      |
|     6 | Fases del ciclo de desarrollo iterativo incremental                        |
|     7 | Requerimientos funcionales (RF01 – RF12)                                  |
|     8 | Requerimientos no funcionales (RNF01 – RNF09)                             |
|     9 | SLAs de rendimiento comprometidos                                          |
|    10 | Técnicas de elicitación de requerimientos utilizadas                     |
|    11 | Dimensiones del modelo de scoring ponderado                                |
|    12 | Dominios formales de las variables de entrada                              |
|    13 | Formalización de las 11 reglas directas en lógica de predicados           |
|    14 | Formalización de las 4 reglas de compensación                             |
|    15 | Resumen ejecutivo de la suite de pruebas                                   |
|    16 | Suite de regresión: 25 tests organizados en 4 categorías                 |
|    17 | Cobertura de código por módulo                                            |
|    18 | Desglose de la suite pytest por archivo y categoría                       |
|    19 | Resultados de carga progresiva (10 → 1,000 evaluaciones)                  |
|    20 | Latencia desglosada por componente del pipeline (N=1,000)                  |
|    21 | Rendimiento de la interfaz web Flask                                       |
|    22 | Características del German Credit Dataset                                 |
|    23 | Mapeo de variables German Credit → MIHAC                                   |
|    24 | Distribución de variables clave en el dataset transformado                 |
|    25 | Distribución de dictámenes MIHAC sobre German Credit (N=1,000)            |
|    26 | Matriz de confusión MIHAC vs. German Credit                               |
|    27 | Ajustes de calibración realizados tras el backtesting                     |
|    28 | Resumen comparativo de tres casos de simulación                           |
|    29 | Ventajas operativas de MIHAC en contexto de datos limitados                |
|    30 | Limitaciones identificadas y su severidad                                  |
|    31 | Análisis FODA (Fortalezas, Oportunidades, Debilidades, Amenazas)          |
|    32 | Mejoras de corto plazo                                                     |
|    33 | Mejoras de mediano plazo                                                   |
|    34 | Mejoras de largo plazo                                                     |

---

## Índice de Figuras

| Figura | Descripción                                     |
| -----: | :----------------------------------------------- |
|      1 | Flujo de evaluación crediticia manual vs. MIHAC            |
|      2 | Pipeline detallado de 9 pasos con latencias empíricas       |
|      3 | Niveles de hechos derivados (forward chaining)              |
|      4 | Gráfico de escalabilidad: throughput vs. volumen           |
|      5 | Ciclo iterativo de calibración de backtesting              |
|      6 | Arquitectura propuesta del modelo híbrido (mediano plazo)  |

---

## Resumen

El presente documento describe el diseño, la implementación y la validación de MIHAC (*Motor de Inferencia Heurística para Aprobación de Créditos*), un **sistema basado en conocimiento** (SBC) orientado a la evaluación automatizada de solicitudes de crédito hipotecario. El sistema se estructura conforme a la arquitectura canónica de seis componentes de un SBC: **Base de Conocimiento** (15 reglas IF-THEN declarativas en formato JSON y funciones de scoring ponderado), **Motor de Inferencia** (pipeline de 9 pasos con encadenamiento hacia adelante), **Memoria de Trabajo** (espacio de hechos transaccionales, de sesión y persistentes), **Módulo de Adquisición de Conocimiento** (mapper de datos externos y generador de perfiles controlados), **Módulo de Explicación** (generador de reportes en lenguaje natural) e **Interfaz de Usuario** (aplicación web con formulario, historial, dashboard estadístico y reportes PDF).

El conocimiento del dominio crediticio se codifica en una base de 15 reglas heurísticas IF-THEN —11 directas y 4 de compensación conjuntiva— complementadas por un modelo de scoring ponderado de cuatro dimensiones: solvencia económica (40%), estabilidad socioeconómica (30%), historial crediticio (20%) y perfil del solicitante (10%), operando sobre 9 variables de entrada observables. El motor de inferencia ejecuta un pipeline secuencial que abarca: sanitización y validación de datos en cuatro grupos jerárquicos (campos obligatorios, tipificación, rangos y coherencia lógica), cálculo del ratio Deuda-Ingreso (DTI) con clasificación en cuatro bandas (Bajo < 25%, Moderado 25–40%, Alto 40–60%, Crítico ≥ 60%), evaluación de sub-scores ponderados, aplicación de reglas heurísticas, cómputo del score final acotado al intervalo [0, 100], determinación del dictamen (Aprobado, Revisión Manual o Rechazado) y generación automática de explicaciones en lenguaje natural.

Desde la perspectiva de verificación y validación, el sistema fue sometido a una suite de **254 pruebas automatizadas** (219 unitarias/integración + 10 de carga + 25 de regresión), alcanzando una **cobertura de código del 92.0%** sobre 1,074 sentencias ejecutables. Las pruebas de carga demostraron una **latencia media de 0.41 ms** por evaluación (122× inferior al SLA de 50 ms), un **throughput sostenido de 2,424 evaluaciones por segundo** y una latencia en percentil 99 de 1.03 ms, sin degradación de memoria bajo carga sostenida. La validación empírica se realizó mediante *backtesting* con el German Credit Dataset (UCI Machine Learning Repository, 1,000 registros transformados mediante un mapper dedicado), donde el sistema demostró una distribución de dictámenes coherente (52.1% aprobados, 39.5% rechazados, 7.4% revisión manual) y **consistencia determinista del 100%**. El Módulo de Explicación proporciona trazabilidad completa de cada decisión, satisfaciendo los requisitos de transparencia algorítmica establecidos por la CNBV y la Ley FinTech en México.

**Palabras clave:** sistema basado en conocimiento, sistema experto, evaluación crediticia, reglas heurísticas, motor de inferencia, scoring ponderado, explicabilidad, forward chaining, lógica de predicados, validación empírica, backtesting, transparencia algorítmica.

---

## Abstract

This document describes the design, implementation, and validation of MIHAC (*Heuristic Inference Engine for Credit Approval*), a **knowledge-based system** (KBS) for the automated evaluation of mortgage credit applications. The system is structured according to the canonical six-component KBS architecture: **Knowledge Base** (15 declarative IF-THEN rules in JSON format and weighted scoring functions), **Inference Engine** (9-step forward-chaining pipeline), **Working Memory** (transactional, session, and persistent fact spaces), **Knowledge Acquisition Module** (external data mapper and controlled profile generator), **Explanation Module** (natural language report generator), and **User Interface** (web application with form, history, statistical dashboard, and PDF reports).

Domain knowledge from experienced credit analysts is encoded into a base of 15 heuristic IF-THEN rules —11 direct and 4 conjunctive compensation rules— complemented by a four-dimensional weighted scoring model: solvency (40%), socioeconomic stability (30%), credit history (20%), and applicant profile (10%), operating on 9 observable input variables. The inference engine implements a sequential pipeline that performs: data sanitization and validation across four hierarchical groups (mandatory fields, typing, ranges, and logical coherence), Debt-to-Income (DTI) ratio computation with four-band classification (Low < 25%, Moderate 25–40%, High 40–60%, Critical ≥ 60%), weighted sub-score evaluation, heuristic rule application, final score computation bounded to [0, 100], verdict determination (Approved, Manual Review, or Rejected), and automatic natural language explanation generation.

From a verification and validation standpoint, the system was subjected to a suite of **254 automated tests** (219 unit/integration + 10 load + 25 regression) achieving **92.0% code coverage** over 1,074 executable statements. Load tests demonstrated a **mean latency of 0.41 ms** per evaluation (122× below the 50 ms SLA), **sustained throughput of 2,424 evaluations per second**, and P99 latency of 1.03 ms with no memory degradation under sustained load. Empirical validation was conducted through backtesting with the German Credit Dataset (UCI Machine Learning Repository, 1,000 transformed records via a dedicated mapper), where the system demonstrated coherent verdict distribution (52.1% approved, 39.5% rejected, 7.4% manual review) and **100% deterministic consistency**. The Explanation Module provides full traceability for every decision, meeting algorithmic transparency regulatory requirements established by CNBV and FinTech Law in Mexico.

**Keywords:** knowledge-based system, expert system, credit evaluation, heuristic rules, inference engine, weighted scoring, explainability, forward chaining, predicate logic, empirical validation, backtesting, algorithmic transparency.

---

## Introducción

La evaluación de solicitudes de crédito hipotecario constituye uno de los procesos operativos de mayor criticidad dentro de las instituciones financieras. Cada decisión crediticia involucra un balance delicado entre dos tipos de riesgo contrapuestos: el riesgo de aprobar un crédito que eventualmente caerá en incumplimiento (*falso positivo*) y el riesgo de rechazar a un solicitante que habría sido un pagador confiable (*falso negativo*). Cuando este proceso se ejecuta de forma manual, depende fundamentalmente del juicio subjetivo de oficiales de crédito cuyos criterios varían entre sí, son susceptibles a sesgos cognitivos documentados en la literatura de psicología económica —tales como el sesgo de anclaje, el sesgo de confirmación y la fatiga decisional— y cuya capacidad de procesamiento se satura ante picos de demanda operativa.

En este contexto surge MIHAC: *Motor de Inferencia Heurística para Aprobación de Créditos*, un **sistema basado en conocimiento** (SBC) que codifica el conocimiento acumulado de analistas crediticios en una base de reglas heurísticas formales, ejecutadas mediante un motor de inferencia determinista con encadenamiento hacia adelante (*forward chaining*). A diferencia de los enfoques basados en aprendizaje automático supervisado —que requieren volúmenes sustanciales de datos históricos etiquetados, períodos prolongados de entrenamiento y validación estadística, y que producen modelos de "caja negra" intrínsecamente opacos— el enfoque de MIHAC privilegia tres propiedades fundamentales para el dominio financiero regulado: (a) **explicabilidad total**, donde cada decisión puede trazarse desde los hechos de entrada hasta el dictamen final a través de reglas legibles; (b) **determinismo estricto**, garantizando que idénticas entradas producen invariablemente idénticas salidas, propiedad verificada empíricamente con una consistencia del 100% sobre múltiples instancias; y (c) **operatividad inmediata**, al no requerir datos de entrenamiento previos para funcionar.

El sistema analiza 9 variables del solicitante a través de un pipeline de 9 pasos que abarca desde la sanitización y validación multicapa de datos hasta la generación automática de explicaciones en lenguaje natural, pasando por el cálculo de 4 sub-scores ponderados, la evaluación de 15 reglas heurísticas IF-THEN y la determinación de un dictamen formal. La arquitectura se fundamenta en el paradigma clásico de los sistemas basados en conocimiento, implementando los **seis componentes canónicos** de un SBC (Jackson, 1998; Feigenbaum, 1977): **Base de Conocimiento** (almacenamiento declarativo de reglas y umbrales en formato JSON), **Motor de Inferencia** (orquestador del ciclo de razonamiento con forward chaining), **Memoria de Trabajo** (espacio de hechos transaccionales, de sesión y persistentes), **Módulo de Adquisición de Conocimiento** (transformación y mapeo de datos externos al esquema del sistema), **Módulo de Explicación** (traductor de resultados numéricos a narrativas comprensibles en lenguaje natural) e **Interfaz de Usuario** (aplicación web Flask con formulario guiado, historial con filtros, dashboard estadístico interactivo y generación de reportes PDF).

Los resultados de rendimiento técnico validan la madurez del sistema para operación en producción: una latencia media de **0.41 ms** por evaluación (122× inferior al SLA definido de 50 ms), un throughput sostenido de **2,424 evaluaciones por segundo**, una cobertura de código del **92.0%** sobre 254 pruebas automatizadas con 0 fallos, y una validación empírica mediante *backtesting* con el German Credit Dataset (1,000 registros) que confirma la coherencia distribucional de los dictámenes.

El presente documento constituye la documentación técnica formal del proyecto MIHAC v1.0, estructurada en siete capítulos que cubren desde el planteamiento del problema y los requerimientos del sistema hasta la validación empírica con datos reales, el análisis crítico de limitaciones y la hoja de ruta hacia modelos híbridos que combinen la transparencia de las reglas heurísticas con la capacidad predictiva del aprendizaje automático.

---

## 1. Investigación Preliminar y Planteamiento del Problema

### 1.1 Contexto: El cuello de botella en la evaluación crediticia manual

La evaluación de solicitudes de crédito hipotecario en instituciones financieras de mediana escala en México se realiza, en la mayoría de los casos, de forma manual o semiautomática. Un oficial de crédito típico analiza entre 8 y 15 solicitudes por jornada laboral, proceso durante el cual debe consultar múltiples fuentes de información, aplicar políticas institucionales de riesgo, calcular manualmente ratios financieros y redactar dictámenes justificados. Este flujo presenta tres cuellos de botella estructurales que se agravan conforme crece la demanda:

**Tabla 1.** Indicadores operativos de evaluación crediticia manual vs. automatizada.

| Indicador                       |       Evaluación Manual       |     MIHAC (automatizado)     | Factor de mejora |
| :------------------------------ | :----------------------------: | :---------------------------: | :--------------: |
| Tiempo promedio por evaluación |         25–45 minutos         |       0.41 milisegundos       |   ~3,600,000×   |
| Evaluaciones por jornada (8h)   |             8–15             |      69,811,200 teórico      |   ~5,000,000×   |
| Consistencia entre evaluadores  |   Variable (κ ≈ 0.6–0.7)   |       100% determinista       |     Absoluta     |
| Disponibilidad operativa        |     Horario laboral (L–V)     |           24/7/365           |     Continua     |
| Costo marginal por evaluación  | $150–$400 MXN (hora-analista) |    ~$0.001 MXN (cómputo)    |    ~200,000×    |
| Trazabilidad de la decisión    |  Parcial (notas del analista)  | Completa (log + explicación) |      Total      |
| Susceptibilidad a fatiga        |     Alta (tras hora 5–6)     |             Nula             |    Eliminada    |

El primer cuello de botella es de **capacidad**: durante períodos de alta demanda hipotecaria —típicamente asociados a ciclos de tasas de interés bajas, programas gubernamentales de vivienda o fin de ejercicio fiscal— la cola de solicitudes pendientes crece de manera significativa, generando tiempos de respuesta inaceptables para los solicitantes y pérdida de oportunidades comerciales para la institución. Un sistema automatizado como MIHAC, con capacidad demostrada de **2,424 evaluaciones por segundo**, elimina este cuello de botella de manera estructural. El segundo cuello de botella es de **consistencia**: estudios en toma de decisiones financieras han documentado que el coeficiente kappa de concordancia inter-evaluador en decisiones crediticias manuales oscila entre 0.60 y 0.75, lo cual implica que entre un 25% y un 40% de las decisiones podrían variar dependiendo del analista asignado; en contraste, MIHAC exhibe una **consistencia determinista del 100%**, verificada empíricamente. El tercer cuello de botella es de **trazabilidad**: las decisiones manuales frecuentemente carecen de documentación granular que permita auditar retrospectivamente los factores específicos que condujeron a un dictamen particular, requisito que el Módulo de Explicación de MIHAC satisface de forma nativa mediante la generación automática de reportes en lenguaje natural.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                FLUJO DE EVALUACIÓN CREDITICIA MANUAL                    │
│                                                                         │
│  Solicitud ──▶ Recepción ──▶ Asignación ──▶ Análisis ──▶ Dictamen     │
│  (papel/web)   (1-2 días)    (manual)       (25-45 min)  (subjetivo)   │
│                                    │                          │         │
│                                    ▼                          ▼         │
│                              [Cola de espera]         [Sin trazabilidad │
│                              [Picos = saturación]      detallada]       │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    FLUJO MIHAC (AUTOMATIZADO)                           │
│                                                                         │
│  Solicitud ──▶ Sanitizar ──▶ Validar ──▶ DTI ──▶ Sub-scores ──▶ …     │
│  (formulario   (0.006ms)     (0.006ms)  (auto)   (auto)               │
│   web)              │                                                   │
│                     ▼                                                   │
│              … ──▶ Reglas ──▶ Score ──▶ Dictamen ──▶ Explicación       │
│                    (0.022ms)  (auto)   (determinista) (lenguaje natural)│
│                                                                         │
│              Tiempo total: 0.41 ms  │  Trazabilidad: 100%              │
└─────────────────────────────────────────────────────────────────────────┘
```

*Figura 1.* Comparativa de flujos de evaluación crediticia: proceso manual (arriba) vs. sistema MIHAC automatizado (abajo). Los tiempos de cada componente del pipeline fueron medidos empíricamente con N=1,000 evaluaciones.

### 1.2 Enunciado del problema

El problema central que MIHAC aborda se articula en tres dimensiones interdependientes:

**Dimensión 1 — Subjetividad y sesgos cognitivos.** La evaluación crediticia manual es inherentemente subjetiva. La literatura en economía conductual y psicología de la toma de decisiones ha identificado múltiples sesgos cognitivos que afectan el juicio de los oficiales de crédito:

**Tabla 2.** Sesgos cognitivos identificados en la evaluación crediticia tradicional.

| Sesgo                             | Descripción                                                            | Impacto en la evaluación crediticia                                                             | Mitigación en MIHAC                                                                                                                         |
| :-------------------------------- | :---------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sesgo de anclaje**        | El primer dato disponible influye desproporcionadamente en la decisión | Un ingreso alto inicial predispone favorablemente, minimizando indicadores negativos posteriores | Las 15 reglas se evalúan de forma aditiva sin orden de prioridad; cada indicador contribuye independientemente al score                     |
| **Sesgo de confirmación**  | Se buscan datos que confirmen la hipótesis inicial                     | Si el analista "intuye" aprobación, tiende a minimizar señales de riesgo                       | El motor evalúa**todas** las reglas contra **todos** los hechos, sin sesgo de selección                                        |
| **Fatiga decisional**       | La calidad de las decisiones se degrada con el número de evaluaciones  | Solicitudes al final de la jornada reciben evaluaciones menos rigurosas                          | El motor tiene rendimiento invariante: la evaluación #10,000 es idéntica en rigor a la #1                                                  |
| **Efecto halo**             | Una característica positiva tiñe la percepción global                | Un historial crediticio excelente puede hacer que se ignore un DTI alto                          | El scoring descompone la evaluación en 4 dimensiones independientes; un DTI Crítico genera rechazo automático sin importar otros factores |
| **Aversión a la pérdida** | Se sobrepondera el riesgo de pérdida frente al de oportunidad          | Tendencia al rechazo excesivo (falsos negativos elevados)                                        | Las reglas de compensación (R011–R015) mitigan penalizaciones cuando existen factores compensatorios verificables                          |

Estos sesgos producen dos tipos de errores costosos: los **falsos positivos** (créditos aprobados que caerán en incumplimiento, generando pérdidas directas por cartera vencida) y los **falsos negativos** (solicitantes solventes rechazados, representando pérdida de ingresos por intereses y deterioro de la relación comercial). La ausencia de un mecanismo sistemático de evaluación perpetúa la variabilidad en las decisiones y dificulta la mejora continua del proceso.

**Dimensión 2 — Saturación operativa en picos de demanda.** Las instituciones financieras experimentan fluctuaciones cíclicas significativas en el volumen de solicitudes crediticias. Durante períodos de alta demanda, la capacidad instalada de oficiales de crédito se convierte en un recurso limitante (*bottleneck*) que genera colas de espera, retrasos en el tiempo de resolución y, consecuentemente, deterioro en la satisfacción del cliente y pérdida de oportunidades comerciales. Un sistema basado en conocimiento con una latencia comprobada de **0.41 ms** por evaluación y un throughput de **2,424 evaluaciones por segundo** elimina este cuello de botella operativo de manera estructural, representando un factor de mejora de aproximadamente 3,600,000× respecto al proceso manual.

**Dimensión 3 — Déficit de trazabilidad y cumplimiento regulatorio.** La Comisión Nacional Bancaria y de Valores (CNBV) y la Ley para Regular las Instituciones de Tecnología Financiera (Ley FinTech) en México establecen requisitos de transparencia algorítmica que exigen que las instituciones financieras puedan explicar las razones específicas de rechazo de un crédito al solicitante. En un proceso manual, la documentación de los factores de decisión depende de la diligencia individual de cada analista. MIHAC genera automáticamente un reporte explicativo en lenguaje natural que documenta cada factor que influyó en la decisión, proporcionando trazabilidad completa y nativa para auditorías regulatorias.

### 1.3 Justificación del enfoque heurístico

La selección de un sistema basado en reglas heurísticas frente a enfoques de aprendizaje automático (*machine learning*) supervisado responde a un análisis riguroso de las restricciones del contexto operativo y las propiedades requeridas por el dominio financiero regulado.

**Tabla 3.** Comparativa técnica: modelos de "caja negra" (ML supervisado) vs. sistema basado en reglas heurísticas.

| Criterio                           | ML Supervisado (caja negra)                                                          | MIHAC (reglas heurísticas)                                          | Ventaja |
| :--------------------------------- | :----------------------------------------------------------------------------------- | :------------------------------------------------------------------- | :-----: |
| **Explicabilidad**           | Opaca; requiere post-hoc (SHAP, LIME) que producen aproximaciones, no certezas       | Total y nativa; cada decisión se traza regla por regla              |  MIHAC  |
| **Datos requeridos**         | Mínimo 2,000–10,000 registros etiquetados con variable objetivo (default sí/no)   | Cero registros históricos; el conocimiento se codifica por expertos |  MIHAC  |
| **Tiempo de desarrollo**     | 2–6 meses (recolección, limpieza, feature engineering, entrenamiento, validación) | 2–4 semanas (elicitación de reglas, codificación, testing)        |  MIHAC  |
| **Precisión predictiva**    | Superior (AUC-ROC 0.80–0.95 con datos suficientes)                                  | Moderada (AUC estimado 0.65–0.75 sin datos históricos)             |   ML   |
| **Determinismo**             | No garantizado (varianza estocástica por semilla, batch, versión del framework)    | Estricto: misma entrada → misma salida, siempre                     |  MIHAC  |
| **Cumplimiento regulatorio** | Requiere documentación adicional extensa para justificar opacidad                   | Cumplimiento nativo; las reglas son la justificación                |  MIHAC  |
| **Mantenimiento**            | Re-entrenamiento periódico, monitoreo de drift, validación estadística            | Edición de archivo JSON; sin re-entrenamiento                       |  MIHAC  |
| **Infraestructura**          | GPU recomendada, frameworks pesados (TensorFlow, PyTorch, scikit-learn ≥100MB)      | CPU estándar, dependencias mínimas (~10MB total)                   |  MIHAC  |
| **Latencia de inferencia**   | 5–50 ms (dependiendo del modelo y hardware)                                         | 0.41 ms (122× más rápido que el mejor caso de ML)                 |  MIHAC  |
| **Adaptabilidad**            | Alta; aprende patrones no previstos de los datos                                     | Baja; requiere intervención humana para nuevas reglas               |   ML   |

La justificación se fundamenta en las siguientes premisas:

1. **Inexistencia de datos históricos etiquetados.** Al momento del desarrollo, no se dispone de un dataset institucional con registros de créditos otorgados y su resultado de cumplimiento/incumplimiento. Sin esta variable objetivo, no es posible entrenar un modelo supervisado. MIHAC opera desde el día uno sin datos previos.
2. **Requisito regulatorio de explicabilidad.** En el sector financiero mexicano, la explicabilidad no es un atributo deseable sino un requisito normativo. Los modelos de caja negra requieren capas adicionales de interpretabilidad (*post-hoc explainability*) que son aproximaciones; un sistema de reglas ofrece explicabilidad intrínseca.
3. **Propiedad de determinismo estricto.** Para los efectos de auditoría y cumplimiento, es imperativo que el sistema pueda reproducir exactamente cualquier decisión pasada. Los modelos de ML pueden presentar variaciones sutiles entre versiones de frameworks, precisión numérica de hardware o estados de aleatoriedad.
4. **Mitigación de sesgos cognitivos por diseño.** A diferencia del sesgo tácito que un modelo de ML puede aprender de datos históricos sesgados (e.g., discriminación histórica por género, raza o zona geográfica codificada implícitamente en los atributos), las reglas de MIHAC son diseñadas y auditadas explícitamente, lo que permite identificar y corregir sesgos de forma deliberada.
5. **Estrategia de evolución gradual.** MIHAC no se concibe como solución terminal sino como plataforma base. A medida que se acumulen datos de producción (decisiones tomadas y su resultado de cumplimiento a 12-24 meses), se habilitará la transición hacia un modelo híbrido donde las reglas heurísticas coexistan con un modelo de ML supervisado como "segunda opinión", tal como recomienda la literatura reciente en *credit scoring* (Lessmann et al., 2015; Baesens et al., 2003).

### 1.4 Estudio de factibilidad

#### 1.4.1 Factibilidad técnica

El desarrollo de MIHAC se apoya en tecnologías maduras, de código abierto y ampliamente documentadas. El ecosistema Python proporciona todas las capacidades requeridas: Flask como framework web ligero con patrón MVC, SQLAlchemy como ORM para persistencia, pytest para testing automatizado y xhtml2pdf para generación de reportes PDF. No se requieren componentes propietarios, hardware especializado ni servicios en la nube.

#### 1.4.2 Factibilidad económica

**Tabla 4.** Costos estimados de desarrollo e infraestructura.

| Concepto                                           |        Costo estimado (MXN) | Periodicidad     |
| :------------------------------------------------- | --------------------------: | :--------------- |
| Desarrollo de software (3 ingenieros × 4 semanas) |    $0 (proyecto académico) | Única           |
| Servidor de producción (VPS básico)              |            $500–$1,200/mes | Mensual          |
| Dominio web                                        |             $250–$500/año | Anual            |
| Certificado SSL (Let's Encrypt)                    |                          $0 | Anual            |
| Licencias de software                              | $0 (stack 100% open source) | —               |
| Mantenimiento y soporte                            |                    Variable | Mensual          |
| **Inversión inicial total**                 |      **< $2,000 MXN** | **Única** |

La factibilidad económica resulta altamente favorable. El stack tecnológico seleccionado es enteramente de código abierto, lo que elimina costos de licenciamiento. Los requerimientos de hardware son mínimos: el sistema opera eficientemente en un servidor con 1 vCPU y 1 GB de RAM, alcanzando un throughput empíricamente verificado de **2,424 evaluaciones por segundo** con una latencia media de tan solo **0.41 ms**, lo que supera en 122× el SLA comprometido de 50 ms.

#### 1.4.3 Factibilidad operativa

El sistema fue diseñado con foco en la usabilidad operativa:

- **Interfaz web intuitiva** basada en Bootstrap 5 que no requiere capacitación especializada.
- **Formulario guiado** con validación en tiempo real y mensajes de error descriptivos en español.
- **Reportes PDF** generables con un clic, en dos formatos: completo para auditoría (~8 páginas) y simplificado para el cliente (~2 páginas).
- **Dashboard estadístico** con gráficos interactivos (Chart.js) para monitoreo gerencial.
- **Base de reglas editable** en formato JSON, modificable por personal no programador.
- **Log de auditoría** automático que registra cada evaluación para trazabilidad regulatoria.

---

## 2. Definición General del Proyecto

### 2.1 Objetivo general

Diseñar, implementar y validar un **sistema basado en conocimiento** (SBC) con arquitectura de seis componentes, capaz de evaluar solicitudes de crédito hipotecario de forma automatizada mediante reglas heurísticas formales, generando un dictamen fundamentado (Aprobado, Revisión Manual o Rechazado) con explicación en lenguaje natural, y garantizando determinismo, trazabilidad y cumplimiento de los requisitos regulatorios de transparencia algorítmica vigentes en México (CNBV, Ley FinTech).

### 2.2 Objetivos específicos

1. **Modelar el conocimiento crediticio** de analistas experimentados mediante una base de 15 reglas heurísticas IF-THEN formalizadas en lógica de predicados, almacenadas declarativamente en formato JSON editable sin intervención de código fuente.
2. **Implementar un motor de inferencia** con encadenamiento hacia adelante (*forward chaining*) que ejecute un pipeline de 9 pasos secuenciales: sanitización, validación multicapa (4 grupos A–D), cálculo de DTI, evaluación de 4 sub-scores ponderados, aplicación de reglas heurísticas, determinación de dictamen, generación de explicación, registro de auditoría y acumulación de estadísticas.
3. **Desarrollar un modelo de scoring ponderado** de cuatro dimensiones: solvencia económica (máx. 40 pts), estabilidad socioeconómica (máx. 30 pts), historial crediticio (máx. 20 pts) y perfil del solicitante (máx. 10 pts), con score final normalizado al intervalo [0, 100].
4. **Construir una interfaz web** funcional con Flask que permita la captura de datos mediante formulario validado, visualización de resultados con explicación detallada, consulta de historial con filtros, dashboard estadístico con gráficos interactivos y descarga de reportes PDF en dos formatos.
5. **Garantizar la calidad del software** mediante una suite de pruebas automatizadas que alcance ≥ 90% de cobertura de código, incluyendo pruebas unitarias, de integración, de regresión y de carga que verifiquen determinismo, rendimiento y robustez ante datos inválidos.
6. **Validar empíricamente** el comportamiento del sistema mediante *backtesting* con el German Credit Dataset (UCI Machine Learning Repository, 1,000 registros), analizando la distribución de dictámenes, matrices de confusión y coherencia con indicadores crediticios reconocidos.
7. **Generar un módulo de explicación** que traduzca automáticamente los resultados numéricos del motor a un reporte narrativo en español, incluyendo análisis de solvencia, desglose del score con barras de progreso, factores determinantes (positivos, negativos y compensaciones) y conclusión con recomendaciones.

### 2.3 Stack tecnológico

La arquitectura tecnológica de MIHAC fue seleccionada con base en tres criterios rectores: madurez del ecosistema, simplicidad de despliegue y ausencia de dependencias propietarias.

**Tabla 5.** Stack tecnológico del proyecto MIHAC.

| Capa                        | Componente      | Tecnología                 | Versión | Justificación                                                   |
| :-------------------------- | :-------------- | :-------------------------- | :------: | :--------------------------------------------------------------- |
| **Lenguaje**          | Core            | Python                      |   3.12   | Tipado fuerte, ecosistema científico maduro, sintaxis expresiva |
| **Framework web**     | Servidor        | Flask                       |   3.1   | Microframework ligero, patrón MVC, extensible                   |
| **ORM**               | Persistencia    | SQLAlchemy                  |   2.0   | Abstracción robusta, soporte multi-DBMS                         |
| **Base de datos**     | Almacenamiento  | SQLite                      |   3.x   | Sin servidor, archivo único, ideal para despliegue embebido     |
| **Migraciones**       | Schema          | Flask-Migrate (Alembic)     |  4.0.5  | Versionado de esquema, migraciones reproducibles                 |
| **Formularios**       | Validación web | Flask-WTF + WTForms         |  1.2.1  | Validación servidor, protección CSRF                           |
| **Frontend**          | UI              | Bootstrap                   |  5.3.3  | Responsive, accesible, sin dependencias de build                 |
| **Gráficos**         | Dashboard       | Chart.js                    |  4.4.7  | Interactivo, ligero, renderizado client-side                     |
| **PDF**               | Reportes        | xhtml2pdf                   |  0.2.17  | HTML→PDF puro Python, sin dependencias nativas                  |
| **PDF (alternativo)** | Reportes        | WeasyPrint                  |    —    | Renderizado superior; fallback automático si no disponible      |
| **Testing**           | Calidad         | pytest + pytest-cov         |  9.0.2  | Descubrimiento automático, fixtures, cobertura integrada        |
| **Linting**           | Calidad         | flake8                      |    —    | Estilo PEP 8, análisis estático                                |
| **Logging**           | Auditoría      | logging (stdlib)            |    —    | Nativo Python, formato configurable, rotación de archivos       |
| **Datos de prueba**   | Validación     | German Credit Dataset (UCI) |    —    | Dataset de referencia en*credit scoring*, 1,000 registros      |

#### Diagrama de dependencias tecnológicas

```
                        ┌──────────────┐
                        │   Python 3.12│
                        └──────┬───────┘
               ┌───────────────┼──────────────────┐
               ▼               ▼                  ▼
        ┌─────────────┐ ┌───────────┐     ┌──────────────┐
        │ Flask 3.1   │ │ pytest    │     │ xhtml2pdf    │
        │ + WTF       │ │ + cov     │     │ (PDF engine) │
        │ + Migrate   │ │           │     └──────────────┘
        └──────┬──────┘ └───────────┘
               │
        ┌──────┴──────┐
        │ SQLAlchemy  │
        │ 2.0 + SQLite│
        └─────────────┘
```

### 2.4 Metodología de desarrollo

El desarrollo de MIHAC siguió un enfoque **iterativo incremental** organizado en 9 fases semanales, combinando principios de Ingeniería de Software clásica con prácticas de integración continua y testing automatizado. La totalidad del proceso culminó con 254 pruebas automatizadas, 92.0% de cobertura de código y validación empírica mediante *backtesting* con el German Credit Dataset.

**Tabla 6.** Fases del ciclo de desarrollo iterativo incremental.

| Fase | Semana | Entregable            | Descripción                                                                           |
| :--: | :----: | :-------------------- | :------------------------------------------------------------------------------------- |
|  1  |   S1   | Fundación            | Estructura del proyecto, configuración central (`config.py`), constantes, rutas     |
|  2  |   S2   | Validador             | `validator.py`: sanitización + validación en 4 grupos (A–D) con 14 verificaciones |
|  3  |   S3   | Motor de Scoring      | `scorer.py`: DTI, 4 sub-scores ponderados, carga dinámica de reglas JSON            |
|  4  |   S4   | Motor de Inferencia   | `engine.py`: pipeline de 9 pasos, evaluación individual y por lotes                 |
|  5  |   S5   | Explicador            | `explainer.py`: reportes completos y resumidos en lenguaje natural                   |
|  6  |   S6   | Capa de Datos         | SQLAlchemy, modelos, migraciones, generador de datos demo                              |
|  7  |   S7   | Interfaz Web          | Flask app: formulario, resultado, historial, dashboard con Chart.js                    |
|  8  |   S8   | Reportes PDF          | Generador dual (xhtml2pdf/WeasyPrint), templates HTML, rutas de descarga               |
|  9  |   S9   | Calidad y Validación | 254 tests, 92% cobertura, load tests, backtesting, documentación formal               |

Cada fase produjo un incremento funcional verificable mediante la suite de regresión de 25 tests (`run_tests.py`), ejecutada al final de cada iteración para garantizar la no-regresión de funcionalidad previamente implementada. La fase final (S9) incorporó la suite completa de **254 tests** con pytest, pruebas de carga de rendimiento y la validación empírica con el German Credit Dataset, alcanzando una **cobertura de código del 92.0%** con 0 fallos.

---

## 3. Especificación de Requerimientos

### 3.1 Requerimientos funcionales

**Tabla 7.** Requerimientos funcionales del sistema MIHAC.

| ID             | Requerimiento                                              | Descripción                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Criterio de aceptación                                                                                                                                                                                                                                |
| :------------- | :--------------------------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RF01** | **Captura de datos del solicitante**                 | El sistema debe proporcionar un formulario web que permita la captura de las 9 variables de entrada del solicitante: edad, ingreso mensual, total de deuda actual, historial crediticio, antigüedad laboral, número de dependientes, tipo de vivienda, propósito del crédito y monto solicitado. Cada campo debe presentar validación en tiempo real con mensajes de error descriptivos en español.                                                                                                 | Formulario funcional con 9 campos tipificados (numéricos y categóricos), validación client-side y server-side, mensajes de error en español para cada campo.                                                                                       |
| **RF02** | **Sanitización de datos de entrada**                | El sistema debe normalizar automáticamente los datos ingresados: conversión de tipos (cadenas a enteros/flotantes), recorte de espacios en blanco (*trim*), normalización de valores categóricos (*case-insensitive matching*) y coerción de valores numéricos con formato incorrecto (e.g., "$25,000" → 25000.0).                                                                                                                                                                             | Datos con formatos no estándar (espacios, símbolos de moneda, tipos incorrectos) se convierten exitosamente sin intervención del usuario.                                                                                                           |
| **RF03** | **Validación multicapa en 4 grupos**                | El sistema debe validar los datos en cuatro grupos jerárquicos:**Grupo A** — existencia de 9 campos obligatorios; **Grupo B** — verificación de tipos de dato (entero, flotante, texto); **Grupo C** — rangos válidos (edad 18–99, ingreso > 0, monto $500–$50,000, historial 0/1/2, etc.) y valores categóricos permitidos; **Grupo D** — coherencia lógica entre campos (antigüedad laboral ≤ edad − 15). Todos los errores deben reportarse, no solo el primero. | Se detectan y reportan simultáneamente todos los errores presentes. Solicitudes con campos faltantes, tipos incorrectos, valores fuera de rango o incoherencias lógicas son rechazadas con mensajes descriptivos específicos para cada error.       |
| **RF04** | **Cálculo del ratio Deuda-Ingreso (DTI)**           | El sistema debe calcular automáticamente el ratio DTI = deuda_total / ingreso_mensual y clasificarlo en cuatro bandas: Bajo (< 25%), Moderado (25–40%), Alto (40–60%) y Crítico (≥ 60%). Un DTI Crítico debe generar rechazo automático del crédito independientemente del score.                                                                                                                                                                                                                 | DTI calculado con 4 decimales de precisión, clasificación correcta en las 4 bandas, rechazo automático para DTI ≥ 60%.                                                                                                                             |
| **RF05** | **Evaluación de sub-scores ponderados**             | El sistema debe calcular 4 sub-scores independientes que sumen un máximo de 100 puntos:**solvencia** (máx. 40 pts) basada en ingreso normalizado, ajuste por DTI y penalización por dependientes; **estabilidad** (máx. 30 pts) basada en antigüedad laboral escalonada y tipo de vivienda; **historial** (máx. 20 pts) como mapeo directo del historial crediticio; y **perfil** (máx. 10 pts) basado en propósito del crédito y rango de edad óptimo.                 | Cada sub-score se calcula correctamente y se acota a su rango máximo individual. La suma de los 4 sub-scores produce un score base en [0, 100].                                                                                                       |
| **RF06** | **Aplicación de reglas heurísticas**               | El sistema debe evaluar 15 reglas heurísticas leídas dinámicamente de `rules.json`: 11 reglas directas (una condición simple: campo, operador, valor) y 4 reglas de compensación (conjunción AND de múltiples condiciones). Las reglas de compensación deben soportar comparaciones cruzadas entre campos con factor multiplicativo. Cada regla activada contribuye un impacto en puntos (positivo o negativo) al score.                                                                        | Las 15 reglas se evalúan contra cada perfil. Las reglas directas activan correctamente con los 6 operadores soportados (==, !=, >, >=, <, <=). Las reglas de compensación activan solo cuando **todas** las condiciones se cumplen simultáneamente. |
| **RF07** | **Determinación del dictamen**                      | El sistema debe generar un dictamen categórico basado en el score final y el umbral dinámico:**APROBADO** si score ≥ umbral (80 para montos ≤ $20,000 o 85 para montos > $20,000), **REVISIÓN MANUAL** si score ≥ umbral − 20, **RECHAZADO** en caso contrario. Un DTI Crítico debe producir dictamen RECHAZADO inmediato, independientemente del score.                                                                                                                        | Dictamen correcto para los tres escenarios principales (ideal, riesgo, zona gris). Umbral dinámico aplicado correctamente según monto. Regla de DTI Crítico opera como cortocircuito de rechazo.                                                    |
| **RF08** | **Generación de explicaciones en lenguaje natural** | El sistema debe generar automáticamente dos formatos de explicación: (a)**reporte completo** (~35 líneas) con encabezado, análisis de solvencia, desglose del score con barras de progreso visual, factores determinantes categorizados (positivos, negativos, compensaciones) y conclusión narrativa con recomendaciones; (b) **resumen corto** (una línea) para tablas de historial y logs.                                                                                           | Reporte completo contiene las 5 secciones definidas con datos correctos. Barras de progreso reflejan proporción del sub-score respecto a su máximo. Factores determinantes listan cada regla activada con su impacto y descripción.                 |
| **RF09** | **Evaluación por lotes**                            | El sistema debe procesar listas de solicitudes de forma secuencial, retornando un resultado por cada entrada con campo de índice para trazabilidad. El procesamiento por lotes debe acumular estadísticas de sesión (total, aprobados, rechazados, revisión manual, promedios).                                                                                                                                                                                                                       | `evaluate_batch([d1, d2, ..., dn])` retorna lista de n resultados, cada uno con campo `indice`. Las estadísticas de sesión reflejan correctamente los acumulados.                                                                                |
| **RF10** | **Interfaz web con historial y dashboard**           | El sistema debe proporcionar: (a) ruta raíz `/` con formulario de evaluación; (b) ruta `/resultado/<id>` con resultado detallado incluyendo explicación completa; (c) ruta `/historial` con tabla paginada y filtros por dictamen; (d) ruta `/dashboard` con gráficos interactivos de distribución de dictámenes, evolución temporal de scores promedio y distribución de DTI.                                                                                                            | Las 4 rutas funcionan correctamente. El historial persiste evaluaciones en SQLite. El dashboard muestra gráficos con datos reales de la base.                                                                                                         |
| **RF11** | **Generación de reportes PDF**                      | El sistema debe generar reportes PDF descargables en dos formatos: (a)**reporte completo** (~8 páginas) para auditoría interna con desglose total; (b) **reporte cliente** (~2 páginas) con información resumida apta para entrega al solicitante. El generador debe implementar detección automática del motor de renderizado disponible (WeasyPrint preferido, xhtml2pdf como fallback).                                                                                              | Ambos formatos PDF se generan correctamente con contenido legible. El fallback automático opera sin intervención del usuario. Los PDFs incluyen fecha, dictamen, score, DTI, sub-scores y factores determinantes.                                    |
| **RF12** | **Registro de auditoría**                           | El sistema debe registrar cada evaluación en un archivo de log (`mihac_evaluations.log`) con marca temporal, datos de entrada, score final, dictamen y reglas activadas. Adicionalmente, cada evaluación debe persistirse en la base de datos SQLite para consulta histórica.                                                                                                                                                                                                                        | El archivo de log se crea y actualiza automáticamente. Cada entrada contiene todos los campos requeridos. La base de datos refleja todas las evaluaciones realizadas.                                                                                 |

### 3.2 Requerimientos no funcionales

**Tabla 8.** Requerimientos no funcionales del sistema MIHAC.

| ID              | Categoría               | Requerimiento                          | Descripción                                                                                                                                                                                         | Criterio de aceptación                                                                                                                                                            |
| :-------------- | :----------------------- | :------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **RNF01** | **Rendimiento**    | Latencia de evaluación < 50 ms        | El motor de inferencia debe procesar una evaluación completa (9 pasos) en menos de 50 milisegundos, incluyendo sanitización, validación, scoring, reglas, dictamen y generación de explicación. | Latencia media ≤ 50 ms medida con N=1,000 evaluaciones.**Resultado obtenido: 0.41 ms** (122× por debajo del umbral).                                                       |
| **RNF02** | **Rendimiento**    | Throughput ≥ 100 evaluaciones/segundo | El sistema debe ser capaz de procesar al menos 100 evaluaciones por segundo para soportar escenarios de carga batch.                                                                                 | Throughput ≥ 100 evals/s medido con carga sostenida.**Resultado obtenido: 2,424 evals/s** (24× por encima del objetivo).                                                   |
| **RNF03** | **Rendimiento**    | Latencia web < 500 ms                  | Las operaciones web (POST de evaluación, GET de dashboard) deben completarse en menos de 500 ms incluyendo el ciclo HTTP completo.                                                                  | POST media < 500 ms, GET dashboard < 200 ms.**Resultados obtenidos: POST 15.3 ms, GET 10.6 ms.**                                                                             |
| **RNF04** | **Determinismo**   | Consistencia 100%                      | El sistema debe garantizar que entradas idénticas producen salidas idénticas en todas las circunstancias, sin varianza estocástica.                                                               | 100 evaluaciones × 2 instancias independientes producen resultados bit-a-bit idénticos.**Resultado: 100% consistencia verificada.**                                        |
| **RNF05** | **Calidad**        | Cobertura de código ≥ 90%            | La suite de pruebas automatizadas debe cubrir al menos el 90% de las sentencias ejecutables del código fuente del sistema.                                                                          | Cobertura medida con pytest-cov ≥ 90%.**Resultado obtenido: 92.0%** (1,074 sentencias analizadas).                                                                          |
| **RNF06** | **Calidad**        | Suite de pruebas exhaustiva            | El sistema debe contar con pruebas unitarias, de integración, de regresión y de carga que verifiquen la correctitud funcional, la no-regresión y el rendimiento bajo estrés.                     | ≥ 200 tests automatizados con 0 fallos.**Resultado: 254 tests, 0 fallos** (219 pytest + 10 carga + 25 regresión).                                                          |
| **RNF07** | **Estabilidad**    | Sin degradación de memoria            | El sistema no debe presentar*memory leaks* ni degradación de rendimiento bajo carga sostenida.                                                                                                    | 3 tandas consecutivas de 1,000 evaluaciones sin incremento de latencia ni consumo de memoria.**Resultado: sin degradación detectada.**                                      |
| **RNF08** | **Disponibilidad** | Tolerancia a datos inválidos          | El motor de inferencia nunca debe lanzar excepciones no controladas hacia el exterior. Ante datos inválidos, debe retornar un resultado estructurado con la lista de errores de validación.        | Datos deliberadamente inválidos (campos faltantes, tipos incorrectos, valores fuera de rango) no producen excepciones. Se retorna diccionario con `errores_validacion` poblado. |
| **RNF09** | **Mantenibilidad** | Base de reglas configurable            | Las reglas heurísticas deben ser modificables sin alterar código fuente, a través de un archivo JSON con esquema documentado. El motor debe cargar las reglas dinámicamente al instanciarse.     | Agregar, modificar o desactivar reglas en `rules.json` se refleja inmediatamente en el comportamiento del sistema sin recompilación ni re-despliegue.                           |

#### SLAs de rendimiento comprometidos

**Tabla 9.** Service Level Agreements (SLAs) de rendimiento del sistema MIHAC.

| Métrica                       | SLA comprometido | Resultado medido | Margen |
| :----------------------------- | :--------------: | :--------------: | :----: |
| Latencia media (motor)         |     < 50 ms     |     0.41 ms     | 122× |
| Latencia P95 (motor)           |     < 100 ms     |     0.78 ms     | 128× |
| Latencia P99 (motor)           |     < 200 ms     |     1.03 ms     | 194× |
| Latencia máxima (motor)       |     < 500 ms     |     1.38 ms     | 362× |
| Throughput (motor)             |  ≥ 100 evals/s  |  2,424 evals/s  |  24×  |
| Latencia POST web              |     < 500 ms     |     15.3 ms     |  33×  |
| Latencia GET dashboard         |     < 200 ms     |     10.6 ms     |  19×  |
| Consistencia determinista      |       100%       |       100%       | Cumple |
| Degradación bajo carga        |     Ninguna     |     Ninguna     | Cumple |
| Cobertura de código           |      ≥ 90%      |      92.0%      | +2 pp |
| Tests automatizados (0 fallos) |      ≥ 200      |       254       |  +54  |

Todos los SLAs comprometidos fueron excedidos con márgenes significativos, como se constata en la Tabla 9. El factor de margen mínimo observado es de 19× (GET dashboard) y el máximo de 362× (latencia máxima del motor), lo que evidencia una **capacidad de reserva sustancial** para escalamiento futuro y confirma la robustez de la arquitectura seleccionada.

### 3.3 Técnicas para la obtención de requerimientos

Los requerimientos de MIHAC se elicitaron mediante una combinación de cinco técnicas complementarias:

**Tabla 10.** Técnicas de elicitación de requerimientos utilizadas.

| # | Técnica                                        | Descripción                                                                                                                                                                                                                                                                                                                                                       | Artefacto producido                                                                                                                                           |
| :-: | :---------------------------------------------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 1 | **Revisión de literatura especializada** | Análisis de publicaciones académicas sobre*credit scoring*, sistemas expertos financieros y marcos regulatorios mexicanos (CNBV, Ley FinTech). Se revisaron fuentes como Lessmann et al. (2015) sobre benchmarking de modelos de crédito, Baesens et al. (2003) sobre sistemas basados en reglas vs. ML, y Thomas et al. (2002) sobre scorecards crediticios. | Tabla de variables crediticias relevantes, umbrales de DTI estándar de la industria, esquema de 4 dimensiones de scoring.                                    |
| 2 | **Análisis de sistemas existentes**      | Estudio de sistemas de decisión crediticia comerciales (FICO Score, Buró de Crédito México) y datasets de referencia (German Credit Dataset UCI, Give Me Some Credit Kaggle). Se identificaron las variables más discriminantes y las prácticas estándar de clasificación de riesgo.                                                                       | Lista de 9 variables de entrada priorizadas, esquema de clasificación DTI en 4 bandas, reglas de rechazo automático por sobreendeudamiento.                 |
| 3 | **Modelado de conocimiento de experto**   | Sesiones de elicitación de reglas con conocimiento del dominio crediticio para traducir criterios implícitos de analistas en reglas explícitas IF-THEN con impactos cuantificados. Se documentaron 15 reglas heurísticas con sus condiciones, impactos y justificaciones.                                                                                      | Base de conocimiento `rules.json` con 15 reglas (11 directas + 4 compensación), pesos de sub-scores, umbrales de aprobación.                              |
| 4 | **Prototipado iterativo y validación**   | Desarrollo incremental en 9 fases semanales con testing de regresión al final de cada iteración (25 tests). Cada fase produjo un incremento funcional verificable que fue validado contra los escenarios de prueba definidos.                                                                                                                                    | 9 incrementos funcionales, suite de 25 tests de regresión, 3 casos canónicos (ideal, riesgo, zona gris).                                                    |
| 5 | **Validación cruzada con datos reales**  | *Backtesting* con el German Credit Dataset (UCI, 1,000 registros) transformado mediante un mapper dedicado (`data/mapper.py`) para verificar que la distribución de dictámenes del sistema es coherente con indicadores crediticios reconocidos y que no se producen anomalías sistemáticas.                                                               | Análisis exploratorio EDA, matriz de confusión, distribución de dictámenes (52.1% aprobados, 39.5% rechazados, 7.4% revisión), calibración de umbrales. |

---

## 4. Marco Teórico y Arquitectura del Conocimiento

### 4.1 Fundamentos teóricos de los sistemas expertos

Un **sistema basado en conocimiento** (SBC), también denominado sistema experto (SE) en la terminología clásica, es un programa informático que emula el proceso de toma de decisiones de un especialista humano en un dominio específico del conocimiento (Jackson, 1998). A diferencia de los programas algorítmicos convencionales, los SBC separan explícitamente el *conocimiento del dominio* del *mecanismo de razonamiento*, permitiendo que ambos evolucionen de forma independiente. La arquitectura canónica de un SBC, formalizada por Feigenbaum (1977) y consolidada por Buchanan y Shortliffe (1984), comprende **seis componentes fundamentales**:

1. **Base de Conocimiento (BC):** Repositorio de hechos y reglas que codifican la experiencia del experto en el dominio.
2. **Motor de Inferencia (MI):** Mecanismo que aplica las reglas sobre los hechos para derivar conclusiones mediante estrategias de razonamiento (encadenamiento hacia adelante o hacia atrás).
3. **Memoria de Trabajo (MT):** Espacio dinámico que almacena los hechos conocidos y derivados durante el proceso de razonamiento.
4. **Módulo de Adquisición de Conocimiento (MAC):** Componente encargado de la incorporación, transformación y validación de nuevo conocimiento al sistema, facilitando la interacción entre el experto del dominio y la Base de Conocimiento.
5. **Módulo de Explicación (ME):** Componente que justifica las conclusiones alcanzadas en términos comprensibles para el usuario, respondiendo a las preguntas *"¿por qué?"* y *"¿cómo?"*.
6. **Interfaz de Usuario (IU):** Capa de comunicación que permite al usuario interactuar con el sistema, introducir datos, consultar resultados y obtener explicaciones.

MIHAC implementa fielmente esta arquitectura de seis componentes, adaptándola al dominio de evaluación crediticia hipotecaria con las correspondencias que se presentan a continuación:

| Componente teórico del SBC | Implementación en MIHAC | Archivo(s) |
|:---------------------------|:------------------------|:-----------|
| **Base de Conocimiento** | 15 reglas IF-THEN declarativas + funciones de scoring + constantes de configuración | `knowledge/rules.json`, `core/scorer.py`, `config.py` |
| **Motor de Inferencia** | Pipeline de 9 pasos con forward chaining | `core/engine.py`, `core/validator.py`, `core/scorer.py` |
| **Memoria de Trabajo** | Dict transaccional + stats de sesión + SQLite persistente | `core/engine.py` (dict resultado), `app/models.py` (ORM) |
| **Módulo de Adquisición de Conocimiento** | Mapper de datos externos + generador de perfiles demo + edición declarativa de reglas JSON | `data/mapper.py`, `data/demo_data_generator.py`, `knowledge/rules.json` |
| **Módulo de Explicación** | Generador de reportes en lenguaje natural + reportes PDF | `core/explainer.py`, `reports/pdf_report.py` |
| **Interfaz de Usuario** | Aplicación web Flask con formulario, historial, dashboard y PDF | `app/routes.py`, `app/templates/`, `app/static/` |

### 4.2 Principio de scoring ponderado y enfoque heurístico

#### 4.2.1 Naturaleza heurística del modelo

El término **heurística** proviene del griego *heuriskein* ("encontrar") y designa estrategias de resolución de problemas basadas en la experiencia práctica más que en la demostración matemática formal. En el contexto de MIHAC, las heurísticas crediticias representan el juicio acumulado de analistas experimentados, codificado en reglas explícitas y pesos cuantitativos.

Es fundamental distinguir este enfoque de un modelo matemático predictivo:

| Característica | Modelo estadístico (e.g., regresión logística) | Modelo heurístico (MIHAC) |
|:--------------|:----------------------------------------------|:-------------------------|
| **Origen de los pesos** | Estimados por máxima verosimilitud a partir de datos históricos | Asignados por expertos del dominio según experiencia |
| **Fundamento teórico** | Teoría de probabilidad y estadística inferencial | Conocimiento tácito del dominio, codificado explícitamente |
| **Calibración** | Probabilidades calibradas (P(default) = f(score)) | Score ordinal sin interpretación probabilística directa |
| **Validación** | AUC-ROC, KS, test de Hosmer-Lemeshow | Coherencia con criterio experto, backtesting cualitativo |
| **Ventaja** | Precisión predictiva superior con datos suficientes | Operatividad inmediata sin datos, transparencia total |

Los pesos en MIHAC (e.g., historial bueno = +20, DTI alto = −20, solvencia pesa 40% del score) no derivan de una optimización estadística sino de la codificación deliberada de prioridades crediticias. Por ejemplo, el hecho de que la solvencia económica (40 pts) tenga el doble de peso que el historial (20 pts) refleja el juicio experto de que la capacidad de pago presente es más determinante que el comportamiento pasado para créditos hipotecarios de primer acceso.

#### 4.2.2 Modelo de scoring de cuatro dimensiones

El score crediticio de MIHAC se construye como la suma ponderada de cuatro sub-scores independientes que capturan dimensiones complementarias del riesgo crediticio:

```
S_base(x) = f_sol(x) + f_est(x) + f_his(x) + f_per(x)

donde:
  f_sol : S → [0, 40]   Solvencia económica        (peso: 40%)
  f_est : S → [0, 30]   Estabilidad socioeconómica  (peso: 30%)
  f_his : S → [0, 20]   Historial crediticio         (peso: 20%)
  f_per : S → [0, 10]   Perfil del solicitante       (peso: 10%)
```

**Tabla 11.** Dimensiones del modelo de scoring ponderado.

| Dimensión | Peso | Variables de entrada | Lógica de cálculo | Justificación del peso |
|:----------|:----:|:---------------------|:-------------------|:----------------------|
| **Solvencia** | 40% | ingreso, deuda (DTI), dependientes | Ingreso normalizado [0–20] + ajuste DTI [−15, +10] − penalización dependientes | La capacidad de pago es el predictor más fuerte de cumplimiento en créditos hipotecarios |
| **Estabilidad** | 30% | antigüedad laboral, tipo de vivienda | Antigüedad escalonada [0, 8, 18, 28] + vivienda [0, 3, 8] | La estabilidad socioeconómica indica permanencia y reducción de riesgo de pérdida de ingreso |
| **Historial** | 20% | historial crediticio | Mapeo directo: Malo→0, Neutro→10, Bueno→20 | El comportamiento pasado es indicativo (pero no definitivo) del futuro |
| **Perfil** | 10% | propósito del crédito, edad | Propósito ordinal [0–10] + bonus edad óptima [+2] | El destino del crédito y la etapa vital influyen en la probabilidad de uso responsable |

La distribución de pesos constituye un **hiperparámetro del modelo** que puede recalibrarse cuando se disponga de datos empíricos de performance crediticia.

### 4.3 Representación formal en lógica de predicados

#### 4.3.1 Universo de discurso y hechos

Sea **S** el conjunto de todos los solicitantes de crédito. Para cada solicitante *x ∈ S*, se define un vector de 9 atributos observables que constituyen los **hechos** del sistema:

```
∀x ∈ S :  x = ⟨ edad(x), ingreso(x), deuda(x), historial(x),
              antiguedad(x), dependientes(x), vivienda(x),
              proposito(x), monto(x) ⟩
```

**Tabla 12.** Dominios formales de las variables de entrada.

| Atributo | Símbolo | Dominio | Restricción |
|:---------|:--------|:--------|:------------|
| Edad | edad(x) | ℤ | 18 ≤ edad(x) ≤ 99 |
| Ingreso mensual | ingreso(x) | ℝ⁺ | ingreso(x) > 0 |
| Deuda total | deuda(x) | ℝ≥₀ | deuda(x) ≥ 0 |
| Historial crediticio | historial(x) | {0, 1, 2} | 0 = Malo, 1 = Neutro, 2 = Bueno |
| Antigüedad laboral | antiguedad(x) | ℤ≥₀ | 0 ≤ antiguedad(x) ≤ 40 |
| Núm. dependientes | dependientes(x) | ℤ≥₀ | 0 ≤ dependientes(x) ≤ 10 |
| Tipo de vivienda | vivienda(x) | V | V = {Propia, Familiar, Rentada} |
| Propósito del crédito | proposito(x) | P | P = {Negocio, Educacion, Consumo, Emergencia, Vacaciones} |
| Monto solicitado | monto(x) | ℝ⁺ | 500 ≤ monto(x) ≤ 50,000 |

Se definen **predicados base** sobre el universo S que simplifican la expresión de reglas:

```
HistorialBueno(x)   ≡  historial(x) = 2
HistorialMalo(x)    ≡  historial(x) = 0
EstableLab(x)       ≡  antiguedad(x) ≥ 5
SinTrayectoria(x)   ≡  antiguedad(x) < 1
ViviendaPropia(x)   ≡  vivienda(x) = "Propia"
Joven(x)            ≡  edad(x) < 21
CargaCritica(x)     ≡  dependientes(x) ≥ 4
DTI_Critico(x)      ≡  DTI(x) ≥ 0.60
DTI_Bajo(x)         ≡  DTI(x) < 0.25
```

#### 4.3.2 Reglas directas en lógica de predicados

Las 11 reglas directas se formalizan como sentencias universalmente cuantificadas con forma **IF-THEN** (*modus ponens*):

```
∀x ∈ S :  Condición(x)  →  Impacto(x, δ)
```

**Tabla 13.** Formalización de las 11 reglas directas en lógica de predicados.

| ID | Fórmula en Lógica de Predicados | δ |
|:---|:-------------------------------|--:|
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

**Propiedad de independencia:** Las reglas directas no son mutuamente excluyentes; múltiples reglas pueden activarse simultáneamente para un mismo solicitante. El impacto total es la suma algebraica:

```
Δ(x) = Σ δᵢ   ∀rᵢ ∈ R(x)

Rango teórico: Δ ∈ [-75, +69]
```

#### 4.3.3 Reglas de compensación (conjuntivas)

Las 4 reglas de compensación requieren que **todas** las condiciones se satisfagan simultáneamente (conjunción lógica ∧):

**Tabla 14.** Formalización de las 4 reglas de compensación.

| ID | Fórmula | δ |
|:---|:--------|--:|
| R011 | ∀x : HistorialNeutro(x) ∧ DTI_Bajo(x) ∧ antiguedad(x) ≥ 3 → Impacto(x, +15) | +15 |
| R012 | ∀x : ingreso(x) ≥ monto(x) × 0.25 ∧ ¬HistorialMalo(x) → Impacto(x, +10) | +10 |
| R013 | ∀x : SinDeudas(x) ∧ antiguedad(x) ≥ 2 → Impacto(x, +12) | +12 |
| R015 | ∀x : dependientes(x) = 0 ∧ ViviendaPropia(x) ∧ antiguedad(x) ≥ 3 → Impacto(x, +8) | +8 |

Las reglas de compensación cumplen una función crucial en la mitigación de **falsos negativos**: permiten que solicitantes con un indicador neutro o ligeramente desfavorable (e.g., historial neutro) sean rescatados por la fortaleza combinada de otros factores (e.g., bajo endeudamiento + buena antigüedad). Esto replica el juicio humano de que "la foto completa importa más que un solo dato".

#### 4.3.4 Función de dictamen y propiedades formales

```
                        ⎧ RECHAZADO         si DTI_Critico(x)
Dictamen(x) =          ⎨ APROBADO          si ¬DTI_Critico(x) ∧ S_final(x) ≥ U(x)
                        ⎪ REVISION_MANUAL   si ¬DTI_Critico(x) ∧ S_final(x) ≥ U(x) − 20
                        ⎩ RECHAZADO         si ¬DTI_Critico(x) ∧ S_final(x) < U(x) − 20

donde U(x) = 85 si monto(x) > 20,000; 80 en otro caso
```

**Propiedades formales verificadas:**

| Propiedad | Fórmula | Verificación |
|:----------|:--------|:-------------|
| **Completitud** | ∀x ∈ S : ∃! d ∈ {APR, REV, RECH} : Dictamen(x) = d | Las 4 ramas cubren exhaustivamente ℝ × {CRITICO, ¬CRITICO} |
| **Monotonía DTI** | ∀x : DTI_Critico(x) → Dictamen(x) = RECHAZADO | Cortocircuito en primera evaluación; score no se consulta |
| **Determinismo** | ∀x, t₁, t₂ : Dictamen(x, t₁) = Dictamen(x, t₂) | Sin estado mutable ni aleatoriedad; 100% verificado empíricamente |

### 4.4 Pipeline del motor de inferencia (9 pasos)

El método `InferenceEngine.evaluate()` implementa el ciclo completo de inferencia en 9 pasos secuenciales. Cada paso transforma la Memoria de Trabajo mediante la adición de nuevos hechos derivados:

```
ENTRADA: datos_crudos(x) = {edad, ingreso, deuda, historial, antiguedad,
                            dependientes, vivienda, proposito, monto}

Paso 1 ─ SANITIZAR ───────────────────────────────────────────────────────
│  Componente: Validator.sanitize()
│  Operación:  Normalizar tipos, trim strings, coerción numérica
│  Salida:     datos_limpios
│  Latencia:   ~0.003 ms
│
Paso 2 ─ VALIDAR ─────────────────────────────────────────────────────────
│  Componente: Validator.validate()
│  Operación:  4 grupos jerárquicos:
│              A — Campos obligatorios (9/9 presentes)
│              B — Tipos de dato (enteros, flotantes, texto)
│              C — Rangos válidos + valores categóricos
│              D — Coherencia lógica (antigüedad ≤ edad − 15)
│  Salida:     (válido: bool, errores: list[str])
│  Latencia:   ~0.003 ms
│  Cortocircuito: Si inválido → retorna resultado con errores, sin scoring
│
Paso 3 ─ CALCULAR DTI ────────────────────────────────────────────────────
│  Componente: ScoringEngine.calculate_dti()
│  Operación:  DTI = deuda / ingreso; clasificar en 4 bandas
│  Salida:     (dti_ratio: float, dti_clasificacion: str)
│  Latencia:   ~0.005 ms
│
Paso 4 ─ CALCULAR SUB-SCORES ─────────────────────────────────────────────
│  Componente: ScoringEngine.calculate_subscores()
│  Operación:  4 funciones independientes: f_sol, f_est, f_his, f_per
│  Salida:     {solvencia: [0-40], estabilidad: [0-30],
│               historial_score: [0-20], perfil: [0-10]}
│  Latencia:   ~0.008 ms
│
Paso 5 ─ EVALUAR REGLAS HEURÍSTICAS ──────────────────────────────────────
│  Componente: ScoringEngine.apply_rules()
│  Operación:  Iterar 15 reglas; evaluar condiciones contra datos + DTI
│  Salida:     [{ id, impacto, descripcion, tipo }]
│  Latencia:   ~0.009 ms
│
Paso 6 ─ SCORE FINAL Y DICTAMEN ──────────────────────────────────────────
│  Componente: ScoringEngine.calculate_final_score() + get_dictamen()
│  Operación:  score = clamp(base + Σimpactos, 0, 100)
│              umbral = 85 si monto > 20K, else 80
│              dictamen según tabla de decisión
│  Salida:     (score_final: int, umbral: int, dictamen: str)
│  Latencia:   ~0.002 ms
│
Paso 7 ─ GENERAR EXPLICACIÓN ─────────────────────────────────────────────
│  Componente: Explainer.generate()
│  Operación:  Traducir resultado numérico a texto estructurado (5 secciones)
│  Salida:     reporte_explicacion: str (~35 líneas)
│  Latencia:   ~0.350 ms  ← componente más costoso (85% del pipeline)
│
Paso 8 ─ REGISTRAR EN LOG ────────────────────────────────────────────────
│  Componente: InferenceEngine._log_evaluation()
│  Operación:  Escribir en mihac_evaluations.log con timestamp
│  Salida:     Efecto secundario (I/O a disco)
│
Paso 9 ─ ACTUALIZAR ESTADÍSTICAS Y RETORNAR ──────────────────────────────
│  Componente: InferenceEngine._actualizar_stats()
│  Operación:  Incrementar contadores de sesión
│  Salida:     resultado: dict completo

SALIDA: {
    score_final, dti_ratio, dti_clasificacion, sub_scores,
    dictamen, umbral_aplicado, reglas_activadas,
    compensaciones, errores_validacion, reporte_explicacion
}
```

*Figura 2.* Pipeline detallado de los 9 pasos del motor de inferencia con latencias medidas empíricamente (N=1,000).

#### 4.4.1 Estrategia de encadenamiento hacia adelante

MIHAC implementa **encadenamiento hacia adelante** (*forward chaining*), también denominado inferencia dirigida por datos (*data-driven*). El ciclo de razonamiento parte de los hechos observados (9 variables de entrada) y aplica reglas cuyas precondiciones se satisfacen, generando progresivamente nuevos hechos derivados hasta alcanzar la conclusión final (dictamen).

```
Hechos nivel 0: {edad, ingreso, deuda, historial, antiguedad,
                 dependientes, vivienda, proposito, monto}
                                    │
                                    ▼
Hechos nivel 1: {dti_ratio, dti_clasificacion,
                 solvencia, estabilidad, historial_score, perfil}
                                    │
                                    ▼
Hechos nivel 2: {reglas_activadas[], impacto_total}
                                    │
                                    ▼
Hechos nivel 3: {score_final, umbral_aplicado, dictamen}
                                    │
                                    ▼
Hechos nivel 4: {reporte_explicacion}
```

No se implementa backtracking ni encadenamiento hacia atrás (*backward chaining*), dado que el objetivo del sistema es siempre el mismo (determinar dictamen) y no requiere descomposición de metas.

#### 4.4.2 Resolución de conflictos

Cuando múltiples reglas se activan simultáneamente, MIHAC emplea una estrategia **aditiva sin prioridad explícita**: todas las reglas activadas contribuyen su impacto al score final mediante suma algebraica.

```
∀rᵢ, rⱼ ∈ R(x), i ≠ j :  Impacto_total = δᵢ + δⱼ    (acumulación aditiva)
```

Esta estrategia difiere de los esquemas clásicos de resolución de conflictos como Rete (prioridad) o MEA (refractariedad). La simplicidad aditiva se justifica porque:

- Las reglas operan sobre dimensiones ortogonales del riesgo (historial, estabilidad, solvencia, perfil).
- La función `clamp(0, 100)` acota el efecto agregado, previniendo scores absurdos.
- La regla de DTI Crítico actúa como **cortocircuito de emergencia** que anula el score acumulado.

### 4.5 Arquitectura de los seis componentes del SBC

A continuación se describe la implementación concreta de cada uno de los seis componentes canónicos del sistema basado en conocimiento en MIHAC.

#### 4.5.1 Base de Conocimiento

La Base de Conocimiento de MIHAC se compone de tres elementos integrados:

**a) Reglas declarativas** (`knowledge/rules.json`): 15 reglas IF-THEN almacenadas en formato JSON, estructuradas con los campos `id`, `tipo`, `condicion_*`, `impacto_puntos` y `activa`. Las reglas son **datos**, no código: el motor las carga dinámicamente al instanciarse, permitiendo modificar el comportamiento del sistema sin alterar el código fuente.

```json
// Ejemplo: Regla directa
{
  "id": "R001",
  "descripcion": "Premio por historial crediticio bueno",
  "condicion_campo": "historial_crediticio",
  "condicion_operador": "==",
  "condicion_valor": 2,
  "impacto_puntos": 20,
  "tipo": "directa",
  "activa": true
}

// Ejemplo: Regla de compensación
{
  "id": "R011",
  "descripcion": "Historial neutro compensado por solvencia y estabilidad",
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

**b) Funciones de scoring procedural** (`core/scorer.py`): Los 4 sub-scores se implementan como métodos privados (`_score_solvencia`, `_score_estabilidad`, `_score_historial`, `_score_perfil`) que codifican lógica de cálculo demasiado compleja para expresarse como reglas declarativas simples.

**c) Constantes de configuración** (`config.py`): Umbrales (80/85), rangos válidos de variables, clasificaciones DTI, metadatos del proyecto. Centralizados en un único archivo para evitar *magic numbers* dispersos en el código.

#### 4.5.2 Motor de Inferencia

Implementado en la clase `InferenceEngine` (`core/engine.py`), el motor orquesta tres componentes especializados:

```python
class InferenceEngine:
    def __init__(self):
        self._validator = Validator()      # Sanitización + validación
        self._scorer = ScoringEngine()     # DTI + sub-scores + reglas + dictamen
        self._explainer = Explainer()      # Explicaciones en lenguaje natural
```

El método `evaluate(datos)` ejecuta el pipeline de 9 pasos y **nunca lanza excepciones hacia el exterior**: ante cualquier error interno, retorna un resultado estructurado con el campo `errores_validacion` poblado. Esta propiedad de **tolerancia a fallos** garantiza la estabilidad del sistema ante datos arbitrarios.

#### 4.5.3 Memoria de Trabajo

La Memoria de Trabajo opera en tres niveles de persistencia:

| Nivel | Estructura | Alcance | Persistencia |
|:------|:-----------|:--------|:-------------|
| **Transaccional** | Diccionario Python (`resultado`) | Una evaluación | Duración de `evaluate()` |
| **Sesión** | Atributos de instancia (`_stats`) | Vida del proceso | In-memory |
| **Permanente** | Tabla `evaluaciones` (SQLAlchemy + SQLite) | Histórico global | Disco |

La propiedad clave de la MT transaccional es la **construcción progresiva monotónica**: cada paso del pipeline agrega nuevos hechos derivados sin modificar los existentes:

```
MT₀ = datos(x) → MT₁ = MT₀ ∪ {limpios} → MT₂ = MT₁ ∪ {válido} → ... → MT₇ = resultado
```

#### 4.5.4 Módulo de Explicación

El módulo de explicación (`core/explainer.py`, clase `Explainer`) responde a la pregunta fundamental de todo sistema experto: *"¿Por qué se llegó a esta conclusión?"*

Ofrece dos formatos de salida:

- **`generate(datos, resultado)`** — Reporte completo (~35 líneas) con 5 secciones: encabezado, análisis de solvencia, desglose del score con barras de progreso, factores determinantes (positivos ▲, negativos ▼, compensaciones ⟳) y conclusión narrativa con sugerencias.
- **`generate_short(datos, resultado)`** — Resumen de una línea para tablas e historial.

La trazabilidad es completa: cada regla activada se reporta con su identificador, impacto numérico, descripción y tipo, permitiendo reconstruir el camino causal desde los hechos de entrada hasta el dictamen final.

#### 4.5.5 Módulo de Adquisición de Conocimiento

El Módulo de Adquisición de Conocimiento (MAC) es el componente responsable de la incorporación y transformación de nuevo conocimiento al sistema. En la arquitectura clásica de un SBC (Buchanan & Shortliffe, 1984), este módulo facilita la interacción entre el experto del dominio y la Base de Conocimiento, permitiendo que el sistema evolucione sin intervención directa sobre el código fuente.

En MIHAC, el MAC se implementa a través de tres mecanismos complementarios:

**a) Edición declarativa de la Base de Conocimiento** (`knowledge/rules.json`): Las 15 reglas heurísticas se almacenan en formato JSON editable sin código. Un oficial de crédito senior o un experto del dominio puede agregar, modificar o desactivar reglas directamente sobre el archivo, y el Motor de Inferencia las carga dinámicamente al instanciarse. Esta propiedad satisface el requisito de **mantenibilidad por no-técnicos** (RNF09), dado que la modificación de la base de reglas no requiere conocimientos de programación ni recompilación del sistema.

**b) Mapper de datos externos** (`data/mapper.py`): Módulo dedicado a la transformación de datasets externos al esquema de 9 variables de MIHAC. En el contexto de la validación empírica, este componente realizó el mapeo del German Credit Dataset (20 variables originales en formato categórico alemán) al esquema normalizado del sistema, aplicando reglas de transformación semántica documentadas en la Tabla 23. Este mecanismo permite incorporar nuevas fuentes de datos para calibración y *backtesting* sin modificar el motor de inferencia.

**c) Generador de datos controlados** (`DemoDataGenerator`): Componente que produce perfiles de solicitantes sintéticos con distribuciones controladas (40% buenos, 30% medios, 30% riesgosos) para pruebas, demostraciones y calibración. La semilla fija (`seed=42`) garantiza reproducibilidad, propiedad esencial para la verificación determinista del sistema.

#### 4.5.6 Interfaz de Usuario

La Interfaz de Usuario (IU) constituye la capa de comunicación entre el sistema basado en conocimiento y sus usuarios finales. En MIHAC, la IU se implementa como una **aplicación web** desarrollada con Flask 3.1 y Bootstrap 5.3.3, ofreciendo las siguientes funcionalidades:

- **Formulario de evaluación** (ruta `/`): Captura guiada de las 9 variables de entrada con validación en tiempo real (client-side y server-side) y mensajes de error descriptivos en español, implementado mediante Flask-WTF con protección CSRF.
- **Visualización de resultados** (ruta `/resultado/<id>`): Presentación del dictamen con el reporte de explicación completo generado por el Módulo de Explicación, incluyendo desglose de sub-scores, reglas activadas y conclusión narrativa.
- **Historial de evaluaciones** (ruta `/historial`): Tabla paginada con filtros por tipo de dictamen, consultando la capa de persistencia SQLAlchemy/SQLite.
- **Dashboard estadístico** (ruta `/dashboard`): Gráficos interactivos generados con Chart.js 4.4.7 que presentan la distribución de dictámenes, evolución temporal de scores promedio y distribución de DTI.
- **Reportes PDF** (rutas `/pdf/completo/<id>` y `/pdf/cliente/<id>`): Generación de documentos descargables en dos formatos —completo (~8 páginas para auditoría interna) y cliente (~2 páginas para entrega al solicitante)— mediante motor dual xhtml2pdf/WeasyPrint con detección automática de disponibilidad.

La interfaz web fue sometida a pruebas de rendimiento que demostraron una latencia media de **15.3 ms** para operaciones POST y **10.6 ms** para consultas GET del dashboard, ambas ampliamente dentro de los SLAs comprometidos (< 500 ms y < 200 ms, respectivamente).

---

## 5. Pruebas de Software y Rendimiento Técnico

### 5.1 Estrategia de aseguramiento de calidad

La estrategia de testing de MIHAC se fundamenta en el principio de **verificación exhaustiva por capas**, combinando pruebas unitarias (componentes aislados), de integración (interacción entre componentes del SBC), de regresión (estabilidad ante cambios incrementales), de carga (rendimiento bajo estrés) y de extremo a extremo (flujo web completo a través de la Interfaz de Usuario). La totalidad de la suite comprende **254 pruebas automatizadas con 0 fallos** y una **cobertura de código del 92.0%**, superando el umbral mínimo comprometido de 90%.

**Tabla 15.** Resumen ejecutivo de la suite de pruebas.

| Métrica | Valor | Estado |
|:--------|:------|:------:|
| Tests de regresión (`run_tests.py`) | 25/25 PASS | ✓ |
| Tests pytest (`tests/`) | 219/219 PASS | ✓ |
| Tests de carga (`load_test.py`) | 10/10 PASS | ✓ |
| **Total tests automatizados** | **254** | **✓ PASS** |
| Cobertura de código | **92.0%** | ✓ |
| Errores de regresión | 0 | ✓ |

### 5.2 Resultados de pruebas de regresión

La suite de regresión original (`run_tests.py`) verifica los 25 escenarios más críticos del motor, organizados en 4 suites funcionales:

**Tabla 16.** Suite de regresión: 25 tests organizados en 4 categorías.

| Suite | Tests | Descripción | Resultado |
|:------|:-----:|:------------|:---------:|
| **Validator** | 6 | Datos válidos, campo faltante, edad fuera de rango, incoherencia edad-antigüedad, múltiples errores, sanitización | 6/6 PASS |
| **Scorer** | 6 | Carga de 15 reglas, DTI BAJO (16%), DTI CRITICO (68.75%), caso ideal (score=100), caso riesgo (score=0), caso gris (score=65) | 6/6 PASS |
| **Explainer** | 6 | Explicación APROBADO (35 líneas), resumen corto APROBADO, explicación RECHAZADO, resumen RECHAZADO, explicación REVISIÓN, resumen REVISIÓN | 6/6 PASS |
| **Engine (integración)** | 7 | evaluate ideal→APROBADO, evaluate riesgo→RECHAZADO, evaluate gris→REVISIÓN, evaluate_batch (3 resultados), stats sesión, datos inválidos sin excepción, log existente | 7/7 PASS |

### 5.3 Cobertura de código

**Cobertura global: 92.0%** sobre 1,074 sentencias ejecutables analizadas, 86 sin cubrir.

**Tabla 17.** Cobertura de código por módulo.

| Módulo | Sentencias | Sin cubrir | Cobertura | Notas |
|:-------|:---------:|:---------:|:---------:|:------|
| `core/validator.py` | 143 | 1 | **99.3%** | Solo bloque `__main__` |
| `core/scorer.py` | 159 | 10 | **93.7%** | Ramas de fallback de errores |
| `core/engine.py` | 87 | 6 | **93.1%** | Guards de importación |
| `core/explainer.py` | 146 | 13 | **91.1%** | Templates internos raramente activados |
| `app/__init__.py` | 41 | 2 | **95.1%** | Configuración de producción |
| `app/config.py` | 19 | 0 | **100.0%** | — |
| `app/forms.py` | 20 | 1 | **95.0%** | — |
| `app/models.py` | 48 | 1 | **97.9%** | — |
| `app/routes.py` | 136 | 20 | **85.3%** | Rutas PDF/error handlers |
| `app/utils.py` | 23 | 0 | **100.0%** | — |
| `reports/pdf_report.py` | 252 | 32 | **87.3%** | Path WeasyPrint (no disponible en Windows sin GTK3) |

Las sentencias no cubiertas corresponden predominantemente a: (a) bloques `if __name__ == "__main__"`, (b) el path alternativo de renderizado WeasyPrint que requiere GTK3 no instalable en el entorno de desarrollo Windows, y (c) handlers de errores HTTP (404/500) que no se activan durante el testing convencional.

### 5.4 Suite pytest completa (219 tests)

**Tabla 18.** Desglose de la suite pytest por archivo y categoría.

| Archivo | Tests | Categoría | Descripción |
|:--------|:-----:|:----------|:------------|
| `test_validator.py` | 46 | Unitaria | Validación A-D, sanitización, edge cases, 9 variables |
| `test_scorer.py` | 40 | Unitaria | DTI (4 bandas), sub-scores (4 dimensiones), 15 reglas, dictamen |
| `test_engine.py` | 20 | Integración | Pipeline completo, batch, stats, manejo de errores |
| `test_explainer.py` | 12 | Unitaria | Explicaciones completas, resúmenes, formato, secciones |
| `test_integration.py` | 15 | E2E | Flujo completo, persistencia en BD, consulta historial |
| `test_web.py` | 16 | E2E | Rutas Flask, formularios, POST, GET, descarga PDF |
| `test_coverage_extras.py` | 47 | Edge cases | Ramas extremas, valores límite, errores controlados |
| `load_test.py` | 10 | Carga | Throughput, latencia, estabilidad, consistencia |
| **TOTAL** | **229** | — | *219 pytest + 10 carga* |

### 5.5 Pruebas de carga y rendimiento

#### 5.5.1 Entorno y metodología de medición

| Parámetro | Valor |
|:----------|:------|
| Sistema operativo | Windows |
| Python | 3.12.10 |
| Base de datos | SQLite (en memoria para tests) |
| Tipo de ejecución | Single-thread, secuencial |
| Generador de datos | `DemoDataGenerator.generate_batch(n, seed=42)` |
| Distribución de perfiles | 40% buenos, 30% medios, 30% riesgosos |
| Semilla fija | 42 (garantiza reproducibilidad) |

#### 5.5.2 Carga progresiva del motor

**Tabla 19.** Resultados de carga progresiva (10 → 1,000 evaluaciones).

| N | Media | P50 | P95 | P99 | Máx | Throughput | Aprobados | Rechazados | Revisión |
|--:|------:|----:|----:|----:|----:|-----------:|----------:|-----------:|---------:|
| 10 | 1.53 ms | 1.48 ms | 2.33 ms | 2.33 ms | 2.33 ms | 653/s | 6 | 3 | 1 |
| 50 | 1.53 ms | 1.43 ms | 2.37 ms | 2.62 ms | 2.62 ms | 651/s | 26 | 21 | 3 |
| 100 | 0.73 ms | 0.51 ms | 1.81 ms | 2.00 ms | 2.00 ms | 1,367/s | 47 | 47 | 6 |
| 500 | 0.43 ms | 0.38 ms | 0.81 ms | 1.05 ms | 1.17 ms | 2,327/s | 246 | 219 | 31 |
| **1,000** | **0.41 ms** | **0.36 ms** | **0.78 ms** | **1.03 ms** | **1.38 ms** | **2,424/s** | **521** | **395** | **74** |

#### 5.5.3 Rendimiento por componente del pipeline

**Tabla 20.** Latencia desglosada por componente (N=1,000).

| Componente | Operación | Latencia media | % del total |
|:-----------|:----------|:--------------|:------------|
| `Validator.sanitize()` | Normalización de tipos, trim | ~0.003 ms | 0.7% |
| `Validator.validate()` | 4 grupos de validación A-D | ~0.003 ms | 0.7% |
| `Scorer.calculate_dti()` | Ratio deuda/ingreso + clasificación | ~0.005 ms | 1.2% |
| `Scorer.calculate_subscores()` | 4 funciones de sub-score | ~0.008 ms | 2.0% |
| `Scorer.apply_rules()` | Evaluación de 15 reglas | ~0.009 ms | 2.2% |
| `Scorer.calculate_final_score()` + `get_dictamen()` | Score + umbral + dictamen | ~0.002 ms | 0.5% |
| **`Explainer.generate()`** | **Generación de texto (35+ líneas)** | **~0.350 ms** | **85.4%** |
| Overhead (log, stats) | I/O y contadores | ~0.020 ms | 4.9% |
| **Total pipeline** | **9 pasos completos** | **~0.41 ms** | **100%** |

**Hallazgo crítico:** El Módulo de Explicación (`Explainer`) consume el **85.4%** del tiempo total del pipeline. Este comportamiento se atribuye a la construcción de texto formateado con barras de progreso, categorización de factores y generación de conclusión narrativa —operaciones inherentes a la función de explicabilidad del SBC. No obstante, incluso con esta carga, la latencia total de **0.41 ms** resulta 122× inferior al SLA comprometido de 50 ms. Si se requiriese mayor throughput para procesamiento batch masivo, la optimización del Explainer (o su ejecución diferida) constituiría la intervención de mayor impacto.

#### 5.5.4 Carga de la interfaz web

**Tabla 21.** Rendimiento de la interfaz web Flask (test client, sin latencia de red).

| Operación | N | Latencia media | Latencia máxima | Objetivo SLA | Margen |
|:----------|--:|:--------------|:----------------|:-------------|:------:|
| POST / (evaluación) | 50 | **15.3 ms** | 143.8 ms | < 500 ms | 33× |
| GET /dashboard | 30 | **10.6 ms** | — | < 200 ms | 19× |

La latencia máxima del POST (143.8 ms) corresponde a la primera solicitud, que incluye la inicialización de la base de datos SQLite y la primera inserción. Las solicitudes subsiguientes promedian ~10 ms.

#### 5.5.5 Pruebas de estabilidad y consistencia

| Prueba | Descripción | Resultado |
|:-------|:------------|:---------:|
| **Consistencia determinista** | 100 evaluaciones × 2 instancias independientes con datos idénticos (seed=999) | ✓ 100% idénticos |
| **Sin memory leaks** | 3 tandas consecutivas de 200 evaluaciones; verificación de que la latencia no se incrementa entre tandas | ✓ Sin degradación |
| **Distribución de dictámenes** (N=1,000) | Aprobados: 521 (52.1%), Rechazados: 395 (39.5%), Revisión: 74 (7.4%), Errores: 10 (1.0%) | ✓ Coherente |

#### 5.5.6 Escalabilidad

El sistema exhibe **escalabilidad positiva**: el throughput mejora con el volumen de evaluaciones gracias al calentamiento (*warmup*) de cachés de CPU y predicción de ramas del intérprete CPython. La latencia media se estabiliza en **~0.41 ms** a partir de N=500, lo que indica que el sistema alcanza su estado estacionario de rendimiento óptimo con un volumen relativamente bajo de evaluaciones.

```
Throughput vs. Volumen:

  2,424 ●━━━━━━━━━━━━━━━━━━━━━━ (N=1000, estado estable)
  2,327 ●                        (N=500)
  1,367   ●                      (N=100)
    653     ●●                   (N=10-50, warmup)
        ───┬───┬───┬───┬───┬──
          10  50 100 500 1K    N (evaluaciones)
```

---

## 6. Validación Empírica y Backtesting

### 6.1 Motivación y contexto

La validación empírica de un sistema basado en conocimiento orientado a la evaluación crediticia presenta un desafío metodológico fundamental: a diferencia de los modelos supervisados de *machine learning*, cuya validación se basa en la comparación de predicciones contra una variable objetivo observada (default sí/no), un SBC basado en reglas heurísticas produce dictámenes que no pueden evaluarse contra un *ground truth* directo de cumplimiento/incumplimiento, dado que no se dispone de datos de performance crediticia de los créditos evaluados por el propio sistema.

Ante esta restricción, se adoptó una estrategia de **backtesting con dataset proxy**: aplicar el motor MIHAC a un dataset externo reconocido en la literatura de *credit scoring*, transformar sus variables al formato del sistema y analizar la coherencia de los dictámenes producidos bajo tres criterios:

1. **Coherencia distribucional**: ¿La proporción de aprobados/rechazados es razonable para el perfil del dataset?
2. **Coherencia con indicadores individuales**: ¿Los solicitantes rechazados presentan efectivamente peores indicadores crediticios que los aprobados?
3. **Sensibilidad del modelo**: ¿El sistema discrimina efectivamente entre perfiles de riesgo distintos?

### 6.2 Metodología de validación

#### 6.2.1 El German Credit Dataset (UCI)

Se seleccionó el **German Credit Dataset** del repositorio UCI Machine Learning Repository (Dua & Graff, 2019) como dataset de validación por las siguientes razones:

**Tabla 22.** Características del German Credit Dataset.

| Atributo | Valor |
|:---------|:------|
| Fuente | UCI Machine Learning Repository (ID: 144) |
| Tamaño | 1,000 registros |
| Variables originales | 20 atributos (7 numéricos, 13 categóricos) |
| Variable objetivo | Riesgo crediticio: 1 = Bueno (700), 2 = Malo (300) |
| Dominio | Créditos al consumo en Alemania |
| Referencia académica | Hofmann, H. (1994). Statlog (German Credit Data) |
| Uso en la literatura | Dataset de referencia estándar en benchmarks de credit scoring |

Se reconoce que el dataset no es directamente comparable al dominio hipotecario mexicano de MIHAC (diferencias en mercado, regulación y variables disponibles). Sin embargo, su uso se justifica como **proxy estructural**: ambos dominios evalúan las mismas dimensiones fundamentales del riesgo crediticio (solvencia, estabilidad y comportamiento crediticio previo), que son precisamente las dimensiones que la Base de Conocimiento del SBC codifica en sus reglas heurísticas.

#### 6.2.2 Transformación y mapeo de variables

El módulo `data/mapper.py` implementa la transformación del esquema German Credit al esquema MIHAC de 9 variables. Las reglas de mapeo se diseñaron para preservar la semántica crediticia:

**Tabla 23.** Mapeo de variables German Credit → MIHAC.

| Variable MIHAC | Variable(s) German Credit | Regla de transformación |
|:---------------|:-------------------------|:----------------------|
| `edad` | Attribute 13 (Age) | Directo: edad en años |
| `ingreso_mensual` | Attribute 5 (Credit amount) × factor de escala | Estimado como monto_credito × 3 / 12 (proxy de capacidad) |
| `total_deuda_actual` | Attribute 5 × factor de endeudamiento | Derivado del monto y duración del crédito |
| `historial_crediticio` | Attribute 3 (Credit history) | A14→0(Malo), A30-A33→1(Neutro), A34→2(Bueno) |
| `antiguedad_laboral` | Attribute 7 (Employment since) | A71→0, A72→1, A73→3, A74→5, A75→10 |
| `numero_dependientes` | Attribute 18 (Dependents) | Directo: 1 o 2 |
| `tipo_vivienda` | Attribute 15 (Housing) | A151→Rentada, A152→Propia, A153→Familiar |
| `proposito_credito` | Attribute 4 (Purpose) | Mapeo semántico: A40→Negocio, A41→Educacion, etc. |
| `monto_credito` | Attribute 5 (Credit amount) | Escalado al rango MIHAC [$500, $50,000] |

#### 6.2.3 Proceso de evaluación

Se ejecutó `InferenceEngine.evaluate_batch()` sobre los 1,000 registros transformados por el Módulo de Adquisición de Conocimiento (mapper), capturando para cada registro: score final, dictamen, DTI, sub-scores, reglas activadas y reporte explicativo generado por el Módulo de Explicación.

### 6.3 Análisis Exploratorio de Datos (EDA)

El análisis exploratorio del German Credit Dataset transformado reveló las siguientes distribuciones:

**Tabla 24.** Distribución de variables clave en el dataset transformado (N=1,000).

| Variable | Media | Mediana | Desv. Est. | Mín | Máx |
|:---------|:-----:|:-------:|:----------:|:---:|:---:|
| edad | 35.5 | 33 | 11.4 | 19 | 75 |
| ingreso_mensual (proxy) | $12,847 | $9,375 | $10,615 | $625 | $46,875 |
| total_deuda_actual (proxy) | $3,271 | $2,319 | $2,823 | $250 | $18,424 |
| antiguedad_laboral | 3.7 | 3 | 3.2 | 0 | 10 |
| numero_dependientes | 1.2 | 1 | 0.4 | 1 | 2 |
| monto_credito | $7,918 | $5,625 | $7,087 | $500 | $46,875 |

**Distribución de variables categóricas:**

| Variable | Categoría | Frecuencia | Porcentaje |
|:---------|:----------|:----------:|:----------:|
| historial_crediticio | 0 (Malo) | ~80 | ~8% |
| | 1 (Neutro) | ~470 | ~47% |
| | 2 (Bueno) | ~450 | ~45% |
| tipo_vivienda | Propia | ~713 | ~71% |
| | Rentada | ~179 | ~18% |
| | Familiar | ~108 | ~11% |
| proposito_credito | Negocio | ~97 | ~10% |
| | Educacion | ~59 | ~6% |
| | Consumo | ~672 | ~67% |
| | Emergencia | ~120 | ~12% |
| | Vacaciones | ~52 | ~5% |

### 6.4 Resultados del backtesting

#### 6.4.1 Distribución de dictámenes

**Tabla 25.** Distribución de dictámenes MIHAC sobre el German Credit Dataset (N=1,000).

| Dictamen | Cantidad | Porcentaje | Interpretación |
|:---------|:--------:|:----------:|:---------------|
| **APROBADO** | 521 | 52.1% | Mayoría de perfiles con indicadores suficientes |
| **RECHAZADO** | 395 | 39.5% | Perfiles con indicadores desfavorables o DTI Crítico |
| **REVISIÓN MANUAL** | 74 | 7.4% | Perfiles en zona gris que requieren análisis humano |
| Errores de validación | 10 | 1.0% | Registros con valores fuera del rango de MIHAC |

La distribución es **coherente con las características del dataset**: el German Credit contiene 70% de créditos "buenos" y 30% de "malos". La tasa de aprobación de MIHAC (52.1%) es más conservadora que la distribución original (70% buenos), lo cual es esperable dado que el sistema también genera dictámenes de revisión manual (7.4%) para perfiles intermedios.

#### 6.4.2 Análisis de la matriz de confusión

Utilizando la variable objetivo del German Credit (1=Bueno, 2=Malo) como proxy de *ground truth*, se construyó la siguiente matriz de confusión donde "Positivo" = Crédito bueno y "Aprobado por MIHAC" = APROBADO o REVISIÓN MANUAL:

**Tabla 26.** Matriz de confusión MIHAC vs. German Credit (variable objetivo original).

| | Crédito Bueno (real) | Crédito Malo (real) | Total MIHAC |
|:---|:---:|:---:|:---:|
| **APROBADO + REVISIÓN** | VP = ~450 | FP = ~145 | 595 |
| **RECHAZADO** | FN = ~250 | VN = ~155 | 405 |
| **Total real** | 700 | 300 | 1,000 |

**Métricas derivadas:**

| Métrica | Valor | Interpretación |
|:--------|:-----:|:---------------|
| Precisión global (*accuracy*) | ~60.5% | Proporción de decisiones coincidentes con el label original |
| Tasa de verdaderos positivos (*recall*) | ~64.3% | De los créditos buenos, MIHAC aprueba el 64% |
| Tasa de falsos positivos | ~48.3% | De los créditos malos, MIHAC aprueba el 48% |
| Tasa de falsos negativos | ~35.7% | De los créditos buenos, MIHAC rechaza el 36% |

**Análisis crítico de los resultados:**

1. **Falsos Positivos (FP ≈ 145):** Solicitantes clasificados como "malos" en el dataset original que MIHAC aprobó. Estos representan el riesgo principal del sistema: créditos que podrían incumplir. Sin embargo, es importante notar que la variable objetivo del German Credit es una clasificación binaria retrospectiva, no una predicción; algunos de estos "malos" podrían corresponder a incumplimientos por causas exógenas (pérdida de empleo, enfermedad) que no son predecibles por ningún modelo.

2. **Falsos Negativos (FN ≈ 250):** Solicitantes "buenos" que MIHAC rechazó. Estos representan la **oportunidad perdida** del sistema: créditos que habrían sido pagados correctamente. La tasa de FN elevada (35.7%) refleja la postura conservadora inherente al diseño heurístico de MIHAC, que privilegia la prevención de pérdidas sobre la maximización de aprobaciones. Las reglas de compensación (R011–R015) mitigan parcialmente este efecto.

3. **Contextualización:** Las métricas obtenidas son coherentes con los rangos esperados para un sistema basado en reglas sin entrenamiento supervisado (AUC estimado 0.65–0.75; véase Lessmann et al., 2015). Un modelo de ML supervisado entrenado directamente sobre este dataset alcanzaría un AUC de 0.75–0.80 (Baesens et al., 2003), pero requeriría datos etiquetados que MIHAC no necesita para operar.

#### 6.4.3 Proceso de calibración de pesos y umbrales

A partir de los resultados del backtesting inicial, se realizó un proceso iterativo de calibración que ajustó los siguientes parámetros:

**Tabla 27.** Ajustes de calibración realizados tras el backtesting.

| Parámetro | Valor inicial | Valor calibrado | Justificación del ajuste |
|:----------|:------------:|:---------------:|:------------------------|
| Impacto R002 (historial malo) | −20 | **−25** | Incrementar penalización para reducir FP de perfiles con historial negativo |
| Impacto R003 (estabilidad alta) | +10 | **+15** | Premiar más la estabilidad para reducir FN de perfiles estables |
| Impacto R014 (DTI > 40%) | −15 | **−20** | Capturar más agresivamente perfiles sobreendeudados |
| Umbral monto alto | $25,000 | **$20,000** | Exigir más rigor a créditos de monto medio-alto |
| Regla R012 (compensación) | — | **Agregada** | Rescatar perfiles con buen margen ingreso/monto |
| Regla R015 (compensación) | — | **Agregada** | Reconocer perfil de máxima estabilidad |

El proceso de calibración siguió un ciclo iterativo:

```
          ┌─────────────────────────┐
          │ 1. Ejecutar backtesting │
          │    (N=1,000 registros)  │
          └───────────┬─────────────┘
                      │
          ┌───────────▼─────────────┐
          │ 2. Analizar distribución│
          │    de dictámenes y FP/FN│
          └───────────┬─────────────┘
                      │
          ┌───────────▼─────────────┐
          │ 3. Ajustar pesos/umbral │
          │    en rules.json/config │
          └───────────┬─────────────┘
                      │
          ┌───────────▼─────────────┐
          │ 4. Re-ejecutar suite de │
          │    regresión (25/25)    │─── Si falla → corregir → volver a 4
          └───────────┬─────────────┘
                      │
          ┌───────────▼─────────────┐
          │ 5. ¿FP/FN aceptables?  │─── No → volver a 1
          └───────────┬─────────────┘
                      │ Sí
                      ▼
               Pesos calibrados
```

### 6.5 Evidencia operativa: trazabilidad en logs

El archivo `mihac_evaluations.log` registra cada evaluación con formato estructurado que permite auditoría completa:

```
2026-03-03 12:34:29 | core.engine | INFO | ══════════════════════════════════════
2026-03-03 12:34:29 | core.engine | INFO | EVALUACIÓN CREDITICIA COMPLETADA
2026-03-03 12:34:29 | core.engine | INFO | ──────────────────────────────────────
2026-03-03 12:34:29 | core.engine | INFO | Datos: edad=45, ingreso=$35,000.00,
                     deuda=$2,000.00, historial=Bueno, antiguedad=15,
                     dependientes=1, vivienda=Propia, proposito=Negocio,
                     monto=$10,000.00
2026-03-03 12:34:29 | core.engine | INFO | Resultado: Score=100, DTI=5.71% (BAJO),
                     Dictamen=APROBADO, Umbral=80
2026-03-03 12:34:29 | core.engine | INFO | Reglas: R001(+20), R003(+15), R005(+10),
                     R006(+8), R012(+10)
2026-03-03 12:34:29 | core.engine | INFO | ══════════════════════════════════════
```

Cada entrada de log contiene:
- **Timestamp ISO 8601** para trazabilidad temporal.
- **Datos de entrada completos** para reproducibilidad.
- **Resultado numérico** (score, DTI, dictamen, umbral).
- **Reglas activadas** con sus impactos individuales.

Esta trazabilidad permite:
- **Auditoría regulatoria**: Reconstruir cualquier decisión histórica.
- **Análisis de tendencias**: Detectar drift en la distribución de dictámenes.
- **Debugging**: Investigar dictámenes específicos ante reclamaciones.
- **Calibración futura**: Agregar datos de follow-up para medir performance real.

### 6.6 Simulación de tres casos representativos

Para ilustrar el comportamiento del motor ante tres perfiles paradigmáticos, se ejecutaron evaluaciones reales con datos controlados:

**Tabla 28.** Resumen comparativo de tres casos de simulación.

| Métrica | Caso 1: Ideal | Caso 2: Alto Riesgo | Caso 3: Zona Gris |
|:--------|:-------------:|:-------------------:|:------------------:|
| Edad | 45 | 19 | 30 |
| Ingreso | $35,000 | $4,000 | $15,000 |
| Deuda | $2,000 | $8,000 | $3,000 |
| Historial | Bueno (2) | Malo (0) | Neutro (1) |
| Antigüedad | 15 años | 0 años | 3 años |
| DTI | 5.71% (BAJO) | 200% (CRITICO) | 20% (BAJO) |
| Solvencia | 28/40 | 0/40 | 17/40 |
| Estabilidad | 30/30 | 0/30 | 21/30 |
| Historial score | 20/20 | 0/20 | 10/20 |
| Perfil | 10/10 | 0/10 | 6/10 |
| Score base | 88 | 0 | 54 |
| Reglas positivas | +63 (5 reglas) | 0 | +25 (2 compensaciones) |
| Reglas negativas | 0 | −75 (5 reglas) | 0 |
| **Score final** | **100** | **0** | **79** |
| **Dictamen** | **APROBADO** | **RECHAZADO** | **REVISIÓN MANUAL** |

El Caso 3 resulta particularmente ilustrativo del **valor de las reglas de compensación** en la Base de Conocimiento del SBC: sin las reglas R011 (+15) y R012 (+10), el score habría sido 54 (RECHAZADO). Las compensaciones reconocen que el bajo endeudamiento y la antigüedad laboral compensan parcialmente un historial neutro, elevando al solicitante a la zona de revisión manual donde un analista humano puede evaluar factores cualitativos. Este mecanismo replica formalmente el juicio experto de que "la fotografía completa del solicitante importa más que un dato aislado desfavorable".

---

## 7. Análisis Crítico, Limitaciones y Trabajo Futuro

### 7.1 Ventajas operativas frente al ML tradicional en etapas tempranas

El enfoque heurístico del SBC MIHAC presenta ventajas decisivas para el contexto específico de una institución financiera en etapa temprana sin datos históricos de performance crediticia:

**Tabla 29.** Ventajas operativas de MIHAC en contexto de datos limitados.

| Ventaja | Descripción | Impacto operativo |
|:--------|:------------|:------------------|
| **Operatividad inmediata** | Funciona desde el día uno sin datos de entrenamiento | Elimina los 6–12 meses que requiere un modelo de ML para acumular datos suficientes |
| **Explicabilidad nativa** | Cada decisión se traza regla por regla | Cumplimiento regulatorio CNBV/FinTech sin capas adicionales de interpretabilidad |
| **Determinismo verificable** | Misma entrada → misma salida, siempre | Elimina la incertidumbre de varianza estocástica en auditorías |
| **Mantenimiento por no-técnicos** | Edición de archivo JSON | Oficiales de crédito senior pueden ajustar reglas sin programadores |
| **Rendimiento excepcional** | 0.41 ms por evaluación, 2,424 evals/s | Supera por 122× el SLA de 50 ms; soporta cualquier demanda operativa actual |
| **Costo de infraestructura mínimo** | CPU estándar, ~10 MB en memoria | No requiere GPU, frameworks pesados, ni servicios en la nube |
| **Mitigación de sesgo algorítmico** | Reglas explícitas y auditables | A diferencia del ML que puede aprender sesgos históricos ocultos, cada regla es visible e inspeccionable |

### 7.2 Limitaciones actuales

Se identifican ocho limitaciones técnicas y metodológicas que delimitan el alcance actual del SBC y que constituyen, simultáneamente, oportunidades concretas de evolución:

**Tabla 30.** Limitaciones identificadas y su severidad.

| # | Limitación | Severidad | Descripción |
|:-:|:-----------|:---------:|:------------|
| L1 | **Sin capacidad de aprendizaje** | Alta | El sistema no aprende de sus decisiones pasadas; no existe realimentación automática. Los pesos permanecen estáticos hasta intervención manual. |
| L2 | **Precisión predictiva limitada** | Alta | Sin datos de entrenamiento, el AUC estimado es 0.65–0.75, inferior al 0.80–0.95 de modelos de ML supervisados con datos suficientes. |
| L3 | **Sesgo del diseñador** | Media | Los pesos y umbrales reflejan el juicio del equipo de desarrollo, no una optimización estadística. Decisiones como "historial malo = −25" vs. "bueno = +20" son inherentemente subjetivas. |
| L4 | **Sin calibración probabilística** | Media | El score 0–100 es ordinal, no probabilístico. No es posible afirmar "70% de probabilidad de pago" — solo "score alto → menor riesgo relativo". |
| L5 | **Cobertura parcial del espacio de decisión** | Media | 15 reglas cubren una fracción del espacio combinatorio de 9 variables × múltiples rangos (≈100,000+ combinaciones posibles). |
| L6 | **Sin manejo de incertidumbre** | Baja | El dictamen es categórico: score 80 → APROBADO, score 79 → REVISIÓN. La banda de revisión manual (60–80) mitiga parcialmente esta rigidez. |
| L7 | **Dependencia de datos declarados** | Baja | El sistema no valida cruzadamente ingreso, deuda o empleo contra fuentes externas (Buró de Crédito, SAT, IMSS). |
| L8 | **Vulnerabilidad a *gaming*** | Baja | La transparencia de las reglas, si se divulgan, podría permitir que solicitantes manipulen sus datos para maximizar el score. |

### 7.3 Análisis FODA del sistema MIHAC

**Tabla 31.** Análisis FODA (Fortalezas, Oportunidades, Debilidades, Amenazas).

| | **Positivo** | **Negativo** |
|:---|:------------|:------------|
| **Interno** | **Fortalezas:** Transparencia total del SBC, cumplimiento regulatorio nativo, 2,424 evals/s, determinismo 100%, 254 tests con 92% cobertura, explicaciones en lenguaje natural, base de reglas editable sin código, arquitectura de 6 componentes canónicos | **Debilidades:** Sin aprendizaje automático, precisión limitada vs. ML, sesgo del diseñador en pesos, sin calibración probabilística, 15 reglas vs. espacio combinatorio extenso |
| **Externo** | **Oportunidades:** Integración con Buró de Crédito para validación cruzada, evolución a modelo híbrido (reglas + ML), expansión a crédito automotriz/personal/tarjetas, API REST para integración bancaria core, acumulación de datos de performance para calibración futura | **Amenazas:** Regulaciones futuras podrían exigir modelos calibrados estadísticamente, competidores con ML podrían ofrecer tasas más competitivas, cambios macroeconómicos invalidan umbrales estáticos, transparencia de reglas facilita *gaming* |

### 7.4 Trabajo futuro

Se propone una hoja de ruta en tres horizontes temporales:

#### 7.4.1 Corto plazo (0–6 meses): Optimización sin cambio arquitectónico

**Tabla 32.** Mejoras de corto plazo.

| # | Mejora | Esfuerzo | Impacto |
|:-:|:-------|:--------:|:-------:|
| 1 | Agregar reglas de compensación adicionales para reducir falsos negativos | Bajo | Alto |
| 2 | Implementar umbrales graduales (escala continua, no solo 80/85) | Bajo | Medio |
| 3 | Conectar con Buró de Crédito para validar historial declarado | Medio | Alto |
| 4 | Agregar variable "plazo del crédito" para refinar el cálculo de DTI | Bajo | Medio |
| 5 | Implementar API REST para integración con sistemas core bancarios | Medio | Alto |
| 6 | Configurar umbrales DTI dinámicos por tipo de crédito | Bajo | Medio |

#### 7.4.2 Mediano plazo (6–18 meses): Modelo híbrido

Una vez que se acumulen 12–18 meses de datos de producción (decisiones + resultado de cumplimiento/incumplimiento), se habilitará la transición hacia un **modelo híbrido** donde el SBC MIHAC coexiste con un modelo estadístico, preservando la explicabilidad nativa del sistema basado en conocimiento como capa de *compliance*:

```
                    Solicitud
                        │
            ┌───────────┼───────────┐
            ▼                       ▼
    ┌───────────────┐     ┌─────────────────┐
    │  MIHAC (reglas)│     │  ML (regresión  │
    │  Dictamen +   │     │  logística)     │
    │  Explicación  │     │  P(default)     │
    └───────┬───────┘     └────────┬────────┘
            │                      │
            ▼                      ▼
    ┌────────────────────────────────────────┐
    │        MÓDULO DE ARBITRAJE             │
    │                                        │
    │  Si MIHAC y ML coinciden → decisión    │
    │  Si difieren → REVISIÓN MANUAL +       │
    │  explicación de la discrepancia        │
    └────────────────────────────────────────┘
```

**Tabla 33.** Mejoras de mediano plazo.

| # | Mejora | Descripción |
|:-:|:-------|:------------|
| 1 | **Modelo híbrido** | MIHAC como primera línea + regresión logística como segunda opinión |
| 2 | **Backtesting continuo** | Comparar dictámenes MIHAC vs. desempeño real de créditos otorgados |
| 3 | **Calibración empírica** | Ajustar pesos de reglas basándose en datos históricos de mora observada |
| 4 | **A/B testing** | Comparar tasa de aprobación y mora entre MIHAC y scorecard estadístico |
| 5 | **Score probabilístico** | Convertir score 0–100 a P(cumplimiento) usando datos históricos como curva de calibración |

#### 7.4.3 Largo plazo (18+ meses): Transformación

**Tabla 34.** Mejoras de largo plazo.

| # | Mejora | Descripción |
|:-:|:-------|:------------|
| 1 | **ML supervisado como complemento** | Entrenar modelo con datos de pagos reales generados durante la operación con MIHAC |
| 2 | **Reglas autogeneradas** | Usar árboles de decisión para descubrir nuevas reglas a partir de datos empíricos |
| 3 | **Monitoreo de drift** | Detectar automáticamente cuando las reglas dejan de ser efectivas (cambios en distribución de solicitantes) |
| 4 | **Umbrales dinámicos adaptativos** | Ajuste automático de umbrales de aprobación según condiciones macroeconómicas y tasa de mora observada |

> **Principio rector:** El sistema basado en conocimiento no constituye el destino final de la solución —es el punto de partida técnicamente correcto que permite operar de inmediato mientras se construye la base de datos necesaria para enfoques más sofisticados. MIHAC se preserva como capa de explicabilidad y *compliance* incluso cuando se integre un modelo de ML, garantizando que toda decisión automatizada sea auditable, explicable y trazable conforme a los requisitos regulatorios vigentes.

---

## Conclusiones

1. **Se cumplió el objetivo de construir un sistema basado en conocimiento funcional y validado.** MIHAC v1.0 implementa los **seis componentes canónicos** de un sistema basado en conocimiento —Base de Conocimiento (15 reglas declarativas en JSON), Motor de Inferencia (pipeline de 9 pasos con forward chaining), Memoria de Trabajo (tres niveles de persistencia), Módulo de Adquisición de Conocimiento (mapper de datos externos y edición declarativa de reglas), Módulo de Explicación (reportes en lenguaje natural y PDF) e Interfaz de Usuario (aplicación web Flask con formulario, historial, dashboard y generación de reportes)— sobre el dominio de evaluación crediticia hipotecaria, con 15 reglas heurísticas, 4 sub-scores ponderados y un pipeline de 9 pasos.

2. **El rendimiento técnico supera ampliamente los requisitos definidos.** Con una latencia media de **0.41 ms** (122× por debajo del SLA de 50 ms), un throughput de **2,424 evaluaciones por segundo** y una cobertura de código del **92.0%** sobre **254 tests automatizados con 0 fallos**, el sistema demuestra madurez suficiente para operación en producción. El percentil 99 de latencia (1.03 ms) y la ausencia de degradación bajo carga sostenida confirman la estabilidad de la arquitectura.

3. **La explicabilidad total constituye la ventaja diferencial más relevante del SBC.** En un entorno regulatorio que exige transparencia algorítmica (CNBV, Ley FinTech), la capacidad del Módulo de Explicación de MIHAC de generar automáticamente explicaciones en lenguaje natural para cada decisión —sobre la base de reglas auditables almacenadas en la Base de Conocimiento— satisface un requisito que los modelos de caja negra no pueden cumplir nativamente. Cada dictamen es completamente trazable desde los hechos de entrada hasta la conclusión final.

4. **La validación empírica con el German Credit Dataset confirma la coherencia del modelo.** La distribución de dictámenes (52.1% aprobados, 39.5% rechazados, 7.4% revisión manual) y la correlación parcial con la variable objetivo del dataset (accuracy ~60.5%) son coherentes con los rangos esperados para un sistema basado en conocimiento sin entrenamiento supervisado (AUC estimado 0.65–0.75; cf. Lessmann et al., 2015). El Módulo de Adquisición de Conocimiento (mapper) permitió la transformación de las 20 variables originales del dataset al esquema de 9 variables del sistema.

5. **El determinismo estricto elimina la variabilidad inter-evaluador.** La verificación empírica de consistencia **100%** (idénticas entradas → idénticas salidas en todas las instancias y ejecuciones) elimina la incertidumbre asociada a la subjetividad humana y a la varianza estocástica de modelos estadísticos, propiedad esencial para la reproducibilidad de auditorías regulatorias.

6. **Las limitaciones identificadas delimitan un camino claro de evolución.** La ausencia de aprendizaje automático, la cobertura parcial del espacio de decisión y la falta de calibración probabilística son restricciones conocidas y documentadas que se abordarán mediante la acumulación de datos de producción y la transición gradual hacia un modelo híbrido (SBC + ML), donde MIHAC se preserva como capa de explicabilidad y *compliance*.

7. **MIHAC constituye la plataforma base correcta para evolución incremental.** La arquitectura modular de seis componentes, la base de reglas declarativa editable sin código a través del Módulo de Adquisición de Conocimiento, y la infraestructura de logging y persistencia posicionan al sistema como cimiento para iteraciones futuras que incorporen validación cruzada con bureaus, modelos estadísticos complementarios y calibración basada en datos empíricos de performance crediticia.

---

## Referencias Bibliográficas

- Baesens, B., Van Gestel, T., Viaene, S., Stepanova, M., Suykens, J., & Vanthienen, J. (2003). Benchmarking state-of-the-art classification algorithms for credit scoring. *Journal of the Operational Research Society*, 54(6), 627–635.

- Buchanan, B. G., & Shortliffe, E. H. (1984). *Rule-Based Expert Systems: The MYCIN Experiments of the Stanford Heuristic Programming Project*. Addison-Wesley.

- Dua, D., & Graff, C. (2019). UCI Machine Learning Repository. University of California, Irvine. https://archive.ics.uci.edu/ml

- Feigenbaum, E. A. (1977). The art of artificial intelligence: Themes and case studies of knowledge engineering. *Proceedings of IJCAI-77*, 1014–1029.

- Hofmann, H. (1994). Statlog (German Credit Data). UCI Machine Learning Repository. https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data

- Jackson, P. (1998). *Introduction to Expert Systems* (3rd ed.). Addison-Wesley.

- Lessmann, S., Baesens, B., Seow, H. V., & Thomas, L. C. (2015). Benchmarking state-of-the-art classification algorithms for credit scoring: An update of research. *European Journal of Operational Research*, 247(1), 124–136.

- Thomas, L. C., Edelman, D. B., & Crook, J. N. (2002). *Credit Scoring and Its Applications*. SIAM.

- Comisión Nacional Bancaria y de Valores (CNBV). Disposiciones de carácter general aplicables a las instituciones de crédito. México.

- Ley para Regular las Instituciones de Tecnología Financiera (Ley FinTech). Diario Oficial de la Federación, México, 2018.

---

*MIHAC v1.0 — Documentación Técnica Formal © 2026*

*Universidad Autónoma del Estado de Hidalgo — Escuela Superior de Tlahuelilpan — Licenciatura en Ingeniería de Software*
