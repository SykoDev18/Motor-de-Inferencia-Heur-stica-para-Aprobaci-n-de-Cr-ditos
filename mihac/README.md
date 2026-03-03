# MIHAC v1.0

**Motor de Inferencia Heurística para Aprobación de Créditos**

Sistema experto basado en reglas para evaluación automatizada de solicitudes de crédito hipotecario. Analiza 9 variables del solicitante, aplica 15 reglas heurísticas IF-THEN y genera un dictamen con explicación en lenguaje natural.

---

## Características

- **Motor de inferencia** con pipeline de 9 pasos (validación → scoring → reglas → explicación)
- **15 reglas heurísticas** configurables en JSON (directas + compensación)
- **4 sub-scores ponderados**: Solvencia (40), Estabilidad (30), Historial (20), Perfil (10)
- **3 dictámenes**: APROBADO, REVISIÓN MANUAL, RECHAZADO
- **Interfaz web** con formulario, resultados, historial y dashboard con gráficos
- **Reportes PDF** (completo para auditoría ~8 págs, cliente ~2 págs)
- **Explicaciones en lenguaje natural** con barras de progreso y factores determinantes
- **254 tests** automatizados con **92% de cobertura** de código
- **2,424 evaluaciones/segundo** de throughput

---

## Estructura del Proyecto

```
mihac/
├── core/                        # Motor de inferencia
│   ├── validator.py             # Validador de datos (4 grupos A-D)
│   ├── scorer.py                # Motor de scoring + reglas heurísticas
│   ├── engine.py                # Orquestador principal (9 pasos)
│   └── explainer.py             # Generador de explicaciones
│
├── app/                         # Interfaz web Flask
│   ├── __init__.py              # App factory (create_app)
│   ├── config.py                # Configuraciones (Dev/Test/Prod)
│   ├── routes.py                # Rutas (index, resultado, historial, dashboard, PDF)
│   ├── models.py                # Modelo Evaluacion (SQLAlchemy)
│   ├── forms.py                 # Formulario WTForms
│   ├── utils.py                 # Helpers de formato
│   ├── templates/               # Templates Jinja2 + Bootstrap 5
│   └── static/                  # CSS y JS
│
├── reports/                     # Generación de reportes PDF
│   ├── pdf_report.py            # PDFReportGenerator (dual renderer)
│   └── templates/               # Templates HTML para PDF
│       ├── reporte_completo.html
│       └── reporte_cliente.html
│
├── knowledge/                   # Base de conocimiento
│   └── rules.json               # 15 reglas heurísticas IF-THEN
│
├── data/                        # Datos y generadores
│   ├── generate_demo_data.py    # Generador de datos sintéticos
│   ├── mapper.py                # Mapeo German Credit
│   └── test/                    # Datasets de prueba
│       ├── stress_1000.csv      # 1000 registros para stress test
│       ├── edge_cases.csv       # 50 casos límite
│       └── perfiles_nominales.csv # 7 perfiles nominales
│
├── tests/                       # Suite de pruebas
│   ├── conftest.py              # Fixtures compartidas
│   ├── fixtures.py              # 12 datasets de prueba
│   ├── test_validator.py        # 46 tests
│   ├── test_scorer.py           # 40 tests
│   ├── test_engine.py           # 20 tests
│   ├── test_explainer.py        # 12 tests
│   ├── test_integration.py      # 15 tests
│   ├── test_web.py              # 16 tests
│   ├── test_coverage_extras.py  # 47 tests
│   └── load_test.py             # 10 tests de carga
│
├── docs/                        # Documentación
│   ├── MODELO_CONOCIMIENTO.md   # Reglas, variables, fallas comunes
│   ├── SIMULACION_INFERENCIA.md # Simulación paso a paso (3 casos)
│   ├── ANALISIS_CRITICO.md      # Ventajas y limitaciones
│   ├── TEST_RESULTS.md          # Resultados de 254 tests
│   ├── LOAD_TEST_RESULTS.md     # Análisis de rendimiento
│   └── load_test_results.json   # Métricas en JSON
│
├── config.py                    # Configuración central del sistema
├── run.py                       # Punto de entrada Flask
├── run_tests.py                 # Suite de regresión (25 tests)
├── pytest.ini                   # Configuración pytest
├── .coveragerc                  # Configuración coverage
└── requirements.txt             # Dependencias Python
```

---

## Instalación

### Requisitos

- Python 3.12+
- pip

### Pasos

```bash
# 1. Clonar o descargar el proyecto
cd "Sistema Experto"

# 2. Crear entorno virtual
python -m venv .venv

# 3. Activar entorno virtual
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 4. Instalar dependencias
pip install -r mihac/requirements.txt
```

---

## Uso

### Interfaz Web

```bash
cd mihac
python run.py
```

Acceder a `http://localhost:5000` en el navegador.

| Ruta | Descripción |
|:-----|:------------|
| `/` | Formulario de evaluación |
| `/resultado/<id>` | Resultado detallado de evaluación |
| `/historial` | Historial de evaluaciones con filtros |
| `/dashboard` | Dashboard con gráficos estadísticos |
| `/descargar_pdf/<id>` | Reporte PDF completo (auditoría) |
| `/descargar_pdf_cliente/<id>` | Reporte PDF simplificado (cliente) |

### Motor de Inferencia (Python)

```python
from core.engine import InferenceEngine

engine = InferenceEngine()

resultado = engine.evaluate({
    "edad": 35,
    "ingreso_mensual": 25000.0,
    "total_deuda_actual": 4000.0,
    "historial_crediticio": 2,
    "antiguedad_laboral": 7,
    "numero_dependientes": 1,
    "tipo_vivienda": "Propia",
    "proposito_credito": "Negocio",
    "monto_credito": 15000.0,
})

print(resultado["dictamen"])          # APROBADO
print(resultado["score_final"])       # 100
print(resultado["dti_ratio"])         # 0.16
print(resultado["reporte_explicacion"])  # Texto completo
```

### Evaluación por Lotes

```python
resultados = engine.evaluate_batch([datos1, datos2, datos3])
for r in resultados:
    print(f"{r['indice']}: {r['dictamen']} (score={r['score_final']})")
```

---

## Variables de Entrada

| Variable | Tipo | Rango | Descripción |
|:---------|:-----|:------|:------------|
| `edad` | int | 18–99 | Edad del solicitante |
| `ingreso_mensual` | float | > 0 | Ingreso mensual bruto ($) |
| `total_deuda_actual` | float | ≥ 0 | Deuda total vigente ($) |
| `historial_crediticio` | int | 0, 1, 2 | Malo / Neutro / Bueno |
| `antiguedad_laboral` | int | 0–40 | Años en empleo actual |
| `numero_dependientes` | int | 0–10 | Dependientes económicos |
| `tipo_vivienda` | str | Propia, Familiar, Rentada | Tipo de vivienda |
| `proposito_credito` | str | Negocio, Educacion, Consumo, Emergencia, Vacaciones | Destino |
| `monto_credito` | float | 500–50,000 | Monto solicitado ($) |

---

## Reglas Heurísticas

15 reglas definidas en `knowledge/rules.json`:

| ID | Tipo | Impacto | Descripción |
|:---|:-----|--------:|:------------|
| R001 | Directa | +20 | Historial bueno |
| R002 | Directa | -25 | Historial malo |
| R003 | Directa | +15 | Antigüedad ≥ 5 años |
| R004 | Directa | -10 | Sin trayectoria laboral |
| R005 | Directa | +10 | Vivienda propia |
| R006 | Directa | +8 | Crédito para negocio |
| R007 | Directa | +6 | Crédito para educación |
| R008 | Directa | -8 | Crédito para vacaciones |
| R009 | Directa | -12 | Edad < 21 |
| R010 | Directa | -10 | 4+ dependientes |
| R011 | Compensación | +15 | Historial neutro + solvencia + estabilidad |
| R012 | Compensación | +10 | Margen de ingreso amplio |
| R013 | Compensación | +12 | Sin deudas + trayectoria |
| R014 | Directa | -20 | DTI > 40% |
| R015 | Compensación | +8 | Máxima estabilidad |

---

## Tests

### Suite de regresión (25 tests)

```bash
python run_tests.py
# Resultado: 25/25 PASS
```

### Suite pytest completa (219 tests + cobertura)

```bash
pytest tests/ -v --cov=core --cov=app --cov=reports --cov-report=term-missing --ignore=tests/load_test.py
# Resultado: 219 passed, 92.0% coverage
```

### Tests de carga (10 tests)

```bash
# Vía pytest
pytest tests/load_test.py -v
# Resultado: 10/10 PASS

# Modo standalone (reporte detallado)
python tests/load_test.py
```

### Todos los tests (229 tests)

```bash
pytest tests/ -v
```

### Métricas de rendimiento

| Métrica | Valor |
|:--------|------:|
| Latencia media (1000 evals) | 0.41 ms |
| Throughput | 2,424 evals/s |
| P95 latencia | 0.78 ms |
| Consistencia | 100% determinista |
| POST web media | 15.3 ms |

---

## Documentación

| Documento | Contenido |
|:----------|:----------|
| [MODELO_CONOCIMIENTO.md](docs/MODELO_CONOCIMIENTO.md) | Reglas, variables, cálculos y fallas comunes |
| [SIMULACION_INFERENCIA.md](docs/SIMULACION_INFERENCIA.md) | 3 simulaciones paso a paso con datos reales |
| [ANALISIS_CRITICO.md](docs/ANALISIS_CRITICO.md) | Ventajas, limitaciones y comparación con ML |
| [TEST_RESULTS.md](docs/TEST_RESULTS.md) | Resultados de 254 tests y 92% cobertura |
| [LOAD_TEST_RESULTS.md](docs/LOAD_TEST_RESULTS.md) | Análisis detallado de rendimiento |

---

## Stack Tecnológico

| Componente | Tecnología |
|:-----------|:-----------|
| Lenguaje | Python 3.12 |
| Framework web | Flask 3.1 |
| Base de datos | SQLAlchemy 2.0 + SQLite |
| Formularios | Flask-WTF + WTForms |
| Frontend | Bootstrap 5.3.3 + Chart.js 4.4.7 |
| PDF | xhtml2pdf (WeasyPrint como alternativa) |
| Testing | pytest 9.0 + pytest-cov |
| Cobertura | 92.0% (1074 sentencias) |

---

## Arquitectura del Motor

```
Datos crudos → Sanitizar → Validar → DTI → Sub-scores → Reglas → Score → Dictamen → Explicación
                  │           │         │        │          │        │         │            │
              Normalizar   Grupos    Ratio   4 dimensiones  15     Clamp   APROBADO/     Texto
              tipos        A-D     Deuda/    ponderadas   reglas  [0-100] REVISION/    lenguaje
                                  Ingreso                 IF-THEN         RECHAZADO    natural
```

---

*MIHAC v1.0 — Sistema Experto de Evaluación Crediticia © 2026*
