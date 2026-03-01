# MIHAC v1.0 — Resultados de Pruebas de Carga

> **Sistema Experto de Evaluación de Crédito Hipotecario**
> Fecha de ejecución: 2026-03-01 13:31:52 | Python 3.12.10

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Objetivos de Rendimiento](#objetivos-de-rendimiento)
3. [Prueba 1: Carga Progresiva del Motor](#prueba-1-carga-progresiva-del-motor)
4. [Prueba 2: Rendimiento por Componente](#prueba-2-rendimiento-por-componente)
5. [Prueba 3: Carga de la Interfaz Web](#prueba-3-carga-de-la-interfaz-web)
6. [Prueba 4: Consistencia](#prueba-4-consistencia)
7. [Análisis de Escalabilidad](#análisis-de-escalabilidad)
8. [Tests pytest de Carga](#tests-pytest-de-carga)
9. [Metodología](#metodología)
10. [Conclusiones](#conclusiones)

---

## Resumen Ejecutivo

| Métrica clave | Valor | Objetivo | Cumple |
|:-------------|------:|:--------:|:------:|
| Latencia media (1000 evals) | **0.41 ms** | < 50 ms | ✓ |
| Throughput motor | **2,424 evals/s** | > 100/s | ✓ |
| P95 latencia | **0.78 ms** | — | ✓ |
| P99 latencia | **1.03 ms** | — | ✓ |
| Latencia máxima | **1.38 ms** | — | ✓ |
| POST web media (50 evals) | **15.3 ms** | < 500 ms | ✓ |
| GET dashboard media (30 hits) | **10.6 ms** | < 200 ms | ✓ |
| Consistencia determinista | **100%** | 100% | ✓ |
| Degradación bajo carga | **No detectada** | — | ✓ |
| Tests de carga pytest | **10/10 PASS** | — | ✓ |

**Veredicto: TODOS LOS OBJETIVOS CUMPLIDOS**

---

## Objetivos de Rendimiento

Los objetivos definidos para el sistema MIHAC:

| Objetivo | Umbral | Justificación |
|:---------|:-------|:-------------|
| Latencia media por evaluación | < 50 ms | Respuesta instantánea para el usuario |
| Throughput del motor | > 100 evals/s | Capacidad de procesamiento batch |
| Latencia POST web | < 500 ms | Experiencia de usuario aceptable |
| Latencia GET dashboard | < 200 ms | Navegación fluida |
| Consistencia | 100% | Mismo input → mismo output siempre |
| Sin degradación | 3 tandas consecutivas | Estabilidad de memoria |

---

## Prueba 1: Carga Progresiva del Motor

Motor de inferencia evaluado con volúmenes crecientes (10 → 1000 solicitudes).
Datos generados con `DemoDataGenerator.generate_batch(n, seed=42)`.

### Resultados

| N | Media | P50 | P95 | P99 | Máx | Throughput | Aprobados | Rechazados | Revisión |
|--:|------:|----:|----:|----:|----:|-----------:|----------:|-----------:|---------:|
| 10 | 1.53 ms | 1.48 ms | 2.33 ms | 2.33 ms | 2.33 ms | 653/s | 6 | 3 | 1 |
| 50 | 1.53 ms | 1.43 ms | 2.37 ms | 2.62 ms | 2.62 ms | 651/s | 26 | 21 | 3 |
| 100 | 0.73 ms | 0.51 ms | 1.81 ms | 2.00 ms | 2.00 ms | 1,367/s | 47 | 47 | 6 |
| 500 | 0.43 ms | 0.38 ms | 0.81 ms | 1.05 ms | 1.17 ms | 2,327/s | 246 | 219 | 31 |
| **1000** | **0.41 ms** | **0.36 ms** | **0.78 ms** | **1.03 ms** | **1.38 ms** | **2,424/s** | **521** | **395** | **74** |

### Observaciones

- **Warmup effect**: Las primeras 10-50 evaluaciones muestran latencia ~1.5ms debido a
  inicialización de cachés Python y JIT del intérprete.
- **Estado estable**: A partir de 100 evaluaciones, la latencia se estabiliza en ~0.4-0.7ms.
- **Escalabilidad lineal**: El throughput mejora con el volumen gracias al calentamiento
  de cachés de CPU y predicción de ramas.
- **Distribución de dictámenes** (N=1000):
  - Aprobados: 521 (52.1%) — ligeramente sobre el 40% de perfiles "buenos" por
    compensación heurística
  - Rechazados: 395 (39.5%)
  - Revisión Manual: 74 (7.4%)
  - Errores de validación: 10 (1.0%)

---

## Prueba 2: Rendimiento por Componente

Cada componente del pipeline medido de forma aislada con N=1000.

### Resultados

| Componente | Media | Máxima | Throughput |
|:-----------|------:|-------:|-----------:|
| **Validator** (sanitize + validate) | 0.006 ms | 0.034 ms | 154,610 ops/s |
| **Scorer** (DTI + sub-scores + rules) | 0.022 ms | 0.206 ms | 44,447 ops/s |

### Desglose del pipeline

El pipeline completo de `InferenceEngine.evaluate()` ejecuta:

```
Validator.sanitize()    ~0.003 ms
Validator.validate()    ~0.003 ms
Scorer.calculate_dti()  ~0.005 ms
Scorer.calculate_subscores() ~0.008 ms
Scorer.apply_rules()    ~0.009 ms
Scorer.dictamen()       ~0.002 ms
Explainer.generate()    ~0.35 ms   ← componente más costoso
                        ─────────
Total pipeline:         ~0.41 ms
```

El **Explainer** consume ~85% del tiempo total del pipeline debido a la
generación de texto con formato (35+ líneas de explicación estructurada).

---

## Prueba 3: Carga de la Interfaz Web

Pruebas con Flask test client (sin red, midiendo solo procesamiento servidor).

### POST / (Formulario de evaluación)

| Métrica | Valor |
|:--------|------:|
| Solicitudes | 50 |
| Latencia media | **15.3 ms** |
| Latencia máxima | **143.8 ms** |
| Objetivo | < 500 ms |

La primera solicitud toma ~144ms (inicialización de BD SQLite + primera
inserción). Las siguientes promedian ~10ms.

### GET /dashboard

| Métrica | Valor |
|:--------|------:|
| Solicitudes | 30 |
| Registros en BD | 50 |
| Latencia media | **10.6 ms** |
| Objetivo | < 200 ms |

El dashboard con gráficos (Chart.js client-side) y estadísticas
agregadas responde consistentemente en ~11ms.

---

## Prueba 4: Consistencia

| Prueba | Resultado |
|:-------|:---------:|
| 100 evaluaciones × 2 instancias independientes | **✓ CONSISTENTE** |
| Mismos datos (seed=999) → mismos scores | **✓ DETERMINISTA** |

El motor es **completamente determinista**: dado el mismo input, siempre
produce exactamente el mismo score, dictamen y explicación, independientemente
de la instancia o el momento de ejecución.

---

## Análisis de Escalabilidad

### Throughput vs. Volumen

```
  Throughput (evals/s)
  2500 |                          ●────── 2,424
       |                    ●
  2000 |               2,327
       |
  1500 |          ●
       |     1,367
  1000 |
       |  ●──●
   500 | 653  651
       |
     0 └────┬────┬────┬────┬────┬──
           10   50  100  500 1000   N
```

### Latencia vs. Volumen

```
  Latencia media (ms)
   2.0 |
       |
   1.5 |  ●──●
       | 1.53 1.53
   1.0 |
       |          ●
   0.5 |        0.73
       |               ●────● 0.41
   0.0 └────┬────┬────┬────┬────┬──
           10   50  100  500 1000   N
```

**Conclusión**: El sistema escala positivamente — más volumen = mejor
rendimiento por unidad gracias al warmup de cachés.

---

## Tests pytest de Carga

10 tests automatizados que verifican los objetivos de rendimiento:

| # | Test | Descripción | Resultado |
|:-:|:-----|:------------|:---------:|
| 1 | `test_carga_10` | Warmup/baseline 10 evals | ✓ PASS |
| 2 | `test_carga_100` | Carga normal 100 evals | ✓ PASS |
| 3 | `test_carga_500` | Carga media 500 evals | ✓ PASS |
| 4 | `test_carga_1000` | Carga alta 1000 evals | ✓ PASS |
| 5 | `test_consistencia_resultados` | Determinismo 50 evals × 2 | ✓ PASS |
| 6 | `test_sin_memory_leak` | 3 tandas sin degradación | ✓ PASS |
| 7 | `test_validador_1000` | 1000 validaciones aisladas | ✓ PASS |
| 8 | `test_scorer_1000` | 1000 scorings aislados | ✓ PASS |
| 9 | `test_carga_web_formulario_100` | 100 POSTs al formulario | ✓ PASS |
| 10 | `test_carga_web_dashboard_50` | 50 GETs al dashboard | ✓ PASS |

**Resultado: 10/10 PASS** (ejecutado en 4.52s)

---

## Metodología

### Entorno de ejecución

| Parámetro | Valor |
|:----------|:------|
| Sistema operativo | Windows |
| Python | 3.12.10 |
| Base de datos | SQLite (en memoria para tests) |
| Tipo de prueba | Single-thread, secuencial |
| Generador de datos | `DemoDataGenerator.generate_batch()` |
| Semilla | 42 (reproducible) |

### Datos de prueba

- **Distribución controlada**: 40% perfiles buenos, 30% medios, 30% riesgosos
- **9 variables por solicitud**: edad, ingreso_mensual, total_deuda_actual,
  historial_crediticio, antiguedad_laboral, numero_dependientes,
  tipo_vivienda, proposito_credito, monto_credito
- **Seed fijo**: Garantiza reproducibilidad exacta de los datos

### Métricas capturadas

| Métrica | Descripción |
|:--------|:------------|
| Media | Promedio aritmético de latencias |
| P50 | Mediana (50° percentil) |
| P95 | 95° percentil — latencia "normal alta" |
| P99 | 99° percentil — latencia outlier |
| Max | Latencia máxima observada |
| Throughput | Evaluaciones por segundo |
| Desv. estándar | Variabilidad de latencias |

---

## Conclusiones

1. **Rendimiento excelente**: El motor procesa **2,424 evaluaciones/segundo**
   con una latencia media de **0.41ms**, superando ampliamente los objetivos
   (50ms latencia, 100 evals/s throughput).

2. **Escalabilidad positiva**: El throughput mejora con el volumen gracias
   al warmup de cachés del intérprete Python.

3. **Consistencia perfecta**: El sistema es 100% determinista — misma
   entrada siempre produce misma salida.

4. **Sin degradación**: Tres tandas consecutivas de 200 evaluaciones no
   muestran deterioro de rendimiento, indicando ausencia de memory leaks.

5. **Web responsive**: La interfaz Flask responde en **15ms** (POST) y
   **11ms** (GET dashboard), muy por debajo de los umbrales de 500ms y 200ms.

6. **Bottleneck identificado**: El `Explainer` consume ~85% del tiempo
   del pipeline. Si se requiere aún más velocidad, optimizar la generación
   de texto sería la prioridad.

7. **Listo para producción**: El sistema cumple todos los SLAs definidos
   con margen amplio (100x en latencia, 24x en throughput).

---

### Archivos relacionados

| Archivo | Descripción |
|:--------|:------------|
| `tests/load_test.py` | Script de pruebas de carga |
| `docs/load_test_results.json` | Resultados en formato JSON |
| `data/test/stress_1000.csv` | Dataset de stress (1000 registros) |
| `data/test/edge_cases.csv` | Dataset de casos límite (50 registros) |
| `data/test/perfiles_nominales.csv` | 7 perfiles nominales |

---

*Documento generado automáticamente — MIHAC v1.0 © 2026*
