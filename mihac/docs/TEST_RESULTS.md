# MIHAC v1.0 — Resultados de Pruebas

> **Sistema Experto de Evaluación de Crédito Hipotecario**
> Fecha de generación: 2026-03-01 | Python 3.12.10 | pytest 9.0.2

---

## Índice

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Suite de Regresión (run_tests.py)](#suite-de-regresión)
3. [Suite pytest Completa](#suite-pytest-completa)
4. [Cobertura de Código](#cobertura-de-código)
5. [Pruebas de Carga](#pruebas-de-carga)
6. [Estructura de Tests](#estructura-de-tests)
7. [Datasets de Prueba](#datasets-de-prueba)
8. [Cómo Reproducir](#cómo-reproducir)

---

## Resumen Ejecutivo

| Métrica                    | Valor       | Estado |
|:---------------------------|:------------|:------:|
| Tests de regresión         | **25/25**   | ✓ PASS |
| Tests pytest               | **219/219** | ✓ PASS |
| Tests de carga             | **10/10**   | ✓ PASS |
| **Total tests**            | **254**     | ✓ PASS |
| Cobertura de código        | **92.0%**   | ✓      |
| Errores de regresión       | 0           | ✓      |

---

## Suite de Regresión

La suite original (`run_tests.py`) verifica los 25 escenarios críticos del motor
organizados en 4 suites:

### Suite 1: Validator (6 tests)

| # | Test | Resultado |
|:-:|:-----|:---------:|
| 1 | Datos válidos → `(True, [])` | ✓ PASS |
| 2 | Campo faltante → error | ✓ PASS |
| 3 | Edad=17 → fuera de rango | ✓ PASS |
| 4 | Antigüedad > edad-15 → incoherencia | ✓ PASS |
| 5 | Múltiples errores → 10 detectados | ✓ PASS |
| 6 | Sanitización → datos válidos | ✓ PASS |

### Suite 2: Scorer (6 tests)

| # | Test | Resultado |
|:-:|:-----|:---------:|
| 1 | Reglas cargadas: 15 | ✓ PASS |
| 2 | DTI 4000/25000 = 16.00% (BAJO) | ✓ PASS |
| 3 | DTI 5500/8000 = 68.75% (CRITICO) | ✓ PASS |
| 4 | Caso ideal: score=100, dict=APROBADO | ✓ PASS |
| 5 | Caso riesgo: score=0, dict=RECHAZADO | ✓ PASS |
| 6 | Caso gris: score=65, dict=REVISION_MANUAL | ✓ PASS |

### Suite 3: Explainer (6 tests)

| # | Test | Resultado |
|:-:|:-----|:---------:|
| 1 | Explicación APROBADO: 35 líneas | ✓ PASS |
| 2 | Resumen corto APROBADO | ✓ PASS |
| 3 | Explicación RECHAZADO: 35 líneas | ✓ PASS |
| 4 | Resumen corto RECHAZADO | ✓ PASS |
| 5 | Explicación REVISION: 31 líneas | ✓ PASS |
| 6 | Resumen corto REVISION | ✓ PASS |

### Suite 4: Engine — Integración (7 tests)

| # | Test | Resultado |
|:-:|:-----|:---------:|
| 1 | evaluate(ideal): score=100, dict=APROBADO | ✓ PASS |
| 2 | evaluate(riesgo): score=0, dict=RECHAZADO | ✓ PASS |
| 3 | evaluate(gris): score=65, dict=REVISION_MANUAL | ✓ PASS |
| 4 | evaluate_batch: 3 resultados | ✓ PASS |
| 5 | stats: 6 evals, tasa=33.33% | ✓ PASS |
| 6 | Datos inválidos → errores sin excepción | ✓ PASS |
| 7 | mihac_evaluations.log existe | ✓ PASS |

**Resultado: 25/25 PASS**

---

## Suite pytest Completa

219 tests organizados en 7 archivos:

### Desglose por archivo

| Archivo | Tests | Estado | Descripción |
|:--------|------:|:------:|:------------|
| `test_validator.py` | 46 | ✓ PASS | Validación A-D, sanitización, edge cases |
| `test_scorer.py` | 40 | ✓ PASS | DTI, sub-scores, reglas, dictamen |
| `test_engine.py` | 20 | ✓ PASS | Pipeline completo, batch, stats |
| `test_explainer.py` | 12 | ✓ PASS | Explicaciones, resúmenes, formato |
| `test_integration.py` | 15 | ✓ PASS | Flujo E2E, persistencia BD |
| `test_web.py` | 16 | ✓ PASS | Rutas Flask, formularios, PDFs |
| `test_coverage_extras.py` | 47 | ✓ PASS | Ramas extremas, edge cases |
| `load_test.py` | 10 | ✓ PASS | Carga y rendimiento |
| **TOTAL** | **229** | **✓ PASS** | — |

### Categorías de prueba

- **Unitarias** (146): Validator, Scorer, Explainer aislados
- **Integración** (35): Engine pipeline, BD, rutas web
- **E2E** (16): Flask client, formularios, descarga PDF
- **Carga** (10): Throughput, latencia, estabilidad
- **Edge cases** (47): Límites, valores extremos, ramas difíciles

---

## Cobertura de Código

**Cobertura global: 92.0%** (1074 sentencias, 86 sin cubrir)

| Módulo | Sentencias | Sin cubrir | Cobertura | Notas |
|:-------|:----------:|:----------:|:---------:|:------|
| `core/validator.py` | 143 | 1 | **99.3%** | Solo `__main__` |
| `core/scorer.py` | 159 | 10 | **93.7%** | Ramas de fallback |
| `core/engine.py` | 87 | 6 | **93.1%** | Guards de import |
| `core/explainer.py` | 146 | 13 | **91.1%** | Templates internos |
| `app/__init__.py` | 41 | 2 | **95.1%** | Config producción |
| `app/config.py` | 19 | 0 | **100.0%** | — |
| `app/forms.py` | 20 | 1 | **95.0%** | — |
| `app/models.py` | 48 | 1 | **97.9%** | — |
| `app/routes.py` | 136 | 20 | **85.3%** | Rutas PDF/error |
| `app/utils.py` | 23 | 0 | **100.0%** | — |
| `reports/pdf_report.py` | 252 | 32 | **87.3%** | WeasyPrint path |

### Líneas no cubiertas más significativas

- `app/routes.py:70-107`: Manejo de errores HTTP (404/500 handlers)
- `app/routes.py:372-408`: Rutas PDF con WeasyPrint (branch alternativo)
- `reports/pdf_report.py:404-439`: Renderizado WeasyPrint (no disponible en Windows sin GTK3)
- `core/explainer.py:476-489`: Templates de explicación raramente activados

---

## Pruebas de Carga

Ver detalle completo en [LOAD_TEST_RESULTS.md](LOAD_TEST_RESULTS.md).

### Resumen rápido

| Métrica | Valor | Objetivo | Estado |
|:--------|------:|:--------:|:------:|
| Latencia media (1000 evals) | 0.41 ms | < 50 ms | ✓ |
| Throughput motor | 2,424 evals/s | > 100/s | ✓ |
| P95 latencia | 0.78 ms | — | ✓ |
| P99 latencia | 1.03 ms | — | ✓ |
| Consistencia | 100% | 100% | ✓ |
| POST web media | 15.3 ms | < 500 ms | ✓ |
| GET dashboard media | 10.6 ms | < 200 ms | ✓ |

---

## Estructura de Tests

```
tests/
├── conftest.py              # Fixtures compartidas (app, db, engine, etc.)
├── fixtures.py              # 12 datasets de prueba predefinidos
├── test_validator.py        # 46 tests — Validación de datos
├── test_scorer.py           # 40 tests — Motor de scoring
├── test_engine.py           # 20 tests — Pipeline de inferencia
├── test_explainer.py        # 12 tests — Generador de explicaciones
├── test_integration.py      # 15 tests — Integración E2E
├── test_web.py              # 16 tests — Interfaz web Flask
├── test_coverage_extras.py  # 47 tests — Ramas y edge cases
└── load_test.py             # 10 tests — Carga y rendimiento
```

### Archivos de configuración

| Archivo | Propósito |
|:--------|:----------|
| `pytest.ini` | Configuración pytest (testpaths, markers) |
| `.coveragerc` | Configuración coverage (sources, exclusions) |
| `run_tests.py` | Suite de regresión original (25 tests) |

---

## Datasets de Prueba

### Datasets predefinidos (`tests/fixtures.py`)

12 casos de prueba con datos y resultados esperados:

| Dataset | Dictamen esperado | Propósito |
|:--------|:------------------|:----------|
| `CASO_IDEAL` | APROBADO | Perfil impecable |
| `CASO_RIESGO` | RECHAZADO | Todo mal |
| `CASO_GRIS` | REVISION_MANUAL | Zona intermedia |
| `CASO_DTI_CRITICO` | RECHAZADO | DTI > 60% |
| `CASO_HEURISTICA` | APROBADO | Compensación activa |
| `CASO_JOVEN` | REVISION_MANUAL | Joven prometedor |
| `CASO_MONTO_ALTO` | APROBADO | Umbral 85 |
| `DATOS_INVALIDOS_*` | — | Campos faltantes, tipos, rangos |

### Datasets CSV generados (`data/test/`)

| Archivo | Registros | Descripción |
|:--------|:---------:|:------------|
| `stress_1000.csv` | 1,000 | Batch aleatorio (40% buenos, 30% medios, 30% riesgosos) |
| `edge_cases.csv` | 50 | Límites y escenarios extremos |
| `perfiles_nominales.csv` | 7 | Los 7 perfiles nominales del sistema |

---

## Cómo Reproducir

### Requisitos previos

```bash
cd mihac
pip install pytest pytest-cov
```

### Ejecutar suite de regresión (25 tests)

```bash
python run_tests.py
```

### Ejecutar suite pytest completa (219 tests + coverage)

```bash
pytest tests/ -v --cov=core --cov=app --cov=reports --cov-report=term-missing --ignore=tests/load_test.py
```

### Ejecutar tests de carga (10 tests)

```bash
# Vía pytest
pytest tests/load_test.py -v

# Modo standalone (reporte detallado)
python tests/load_test.py
```

### Ejecutar TODO (229 tests)

```bash
pytest tests/ -v --cov=core --cov=app --cov=reports --cov-report=term-missing
```

---

*Documento generado automáticamente — MIHAC v1.0 © 2026*
