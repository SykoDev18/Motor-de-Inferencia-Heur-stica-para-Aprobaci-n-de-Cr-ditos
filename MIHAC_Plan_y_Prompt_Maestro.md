# 🏗️ MIHAC — Plan Técnico Completo + Prompt Maestro
> Motor de Inferencia Heurística para Aprobación de Créditos  
> Nivel: Tesis de Ingeniería · Stack: Python + Flask + SQLite

---

## PARTE 1: DECISIONES TÉCNICAS (Con justificación)

---

### 🐍 Lenguaje: Python 3.11+

**¿Por qué Python y no JavaScript o Java?**

| Criterio | Python | JavaScript (Node) | Java |
|---|---|---|---|
| Librerías para datos/ML | ✅ Pandas, Scikit-learn, Matplotlib | ❌ Limitado | ⚠️ Complejo |
| Curva de aprendizaje (intermedio) | ✅ Baja | ⚠️ Media | ❌ Alta |
| Ideal para tesis/validación | ✅ Jupyter + notebooks | ❌ | ❌ |
| Interfaz web rápida | ✅ Flask (minimalista) | ✅ Express | ⚠️ Spring (pesado) |
| Legibilidad del código | ✅ Alta (fácil de mostrar en defensa) | ⚠️ Media | ❌ Verboso |

**Decisión: Python + Flask.** Es el estándar de facto en IA/ML académico y permite demostrar el sistema en vivo durante la defensa con un solo comando.

---

### 🗄️ Base de Datos: SQLite → PostgreSQL

**Estrategia de dos etapas (pensando a futuro desde el inicio):**

```
ETAPA 1 (Tesis):      SQLite     → archivo local, cero configuración
ETAPA 2 (Producción): PostgreSQL → misma interfaz, cambio de 1 línea en config.py
```

**¿Por qué NO usar solo archivos CSV?**
Los CSV no permiten consultas, historial de auditoría, ni escalabilidad.
SQLite es una base de datos completa pero sin servidor: ideal para tesis.

**ORM: SQLAlchemy** — El código que escribas para SQLite funcionará en PostgreSQL, MySQL o cualquier otro motor sin reescribir una línea.

---

### 📊 Datos: Estrategia Dual

#### Dataset 1 — German Credit Data (UCI Machine Learning Repository)
- **1,000 registros** reales con historial validado
- **20 variables** originales (en alemán, requieren mapeo)
- **Uso:** Calibrar y validar las reglas heurísticas, generar métricas reales
- **URL:** https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- **Mapeo de variables clave:**

| Variable German Credit | Variable MIHAC | Transformación |
|---|---|---|
| `duration` | `Plazo_Meses` | Directa |
| `credit_amount` | `Monto_Credito` | Directa |
| `age` | `Edad` | Directa |
| `employment` | `Antiguedad_Laboral` | Categórico → Numérico |
| `credit_history` | `Historial_Crediticio` | Recodificar 0/1/2 |
| `purpose` | `Proposito_Credito` | Mapear categorías |
| `personal_status` | `Numero_Dependientes` | Inferir de estado civil |
| `class` | `Resultado_Real` | 1=Bueno, 2=Malo → etiqueta |

#### Dataset 2 — Datos Sintéticos para Demo en Vivo
- **50–100 registros** generados con `Faker` + lógica controlada
- **Uso:** Demostración en defensa con casos extremos claros
- **Incluye perfiles tipo:** cliente ideal, cliente límite, zona gris, rechazado, no bancarizado
- **Generado automáticamente** por el script `generate_demo_data.py`

---

### 🏛️ Arquitectura del Proyecto (Estructura de Archivos)

```
mihac/
│
├── 📁 core/                             ← El cerebro del sistema
│   ├── engine.py                        ← Motor de inferencia principal
│   ├── scorer.py                        ← Cálculo del Score ponderado + DTI
│   ├── validator.py                     ← Validaciones formato + lógica negocio
│   └── explainer.py                     ← Generador de reportes en lenguaje natural
│
├── 📁 knowledge/                        ← Base de Conocimiento (SIN tocar engine.py)
│   ├── rules.json                       ← Reglas IF-THEN heurísticas
│   ├── weights.json                     ← Pesos de cada variable (ajustables)
│   └── thresholds.json                  ← Umbrales de decisión (60/80)
│
├── 📁 data/
│   ├── german_credit_raw.csv            ← Dataset original UCI
│   ├── german_credit_mapped.csv         ← Dataset traducido/mapeado
│   ├── demo_synthetic.csv               ← Datos ficticios para demo
│   └── mapper.py                        ← Script de transformación German→MIHAC
│
├── 📁 database/
│   ├── models.py                        ← Modelos SQLAlchemy (Solicitud, Evaluacion, Log)
│   ├── db.py                            ← Conexión y sesión (config intercambiable)
│   └── mihac.db                         ← Archivo SQLite (auto-generado)
│
├── 📁 reports/
│   ├── metrics.py                       ← Precisión, Recall, F1, Matriz de Confusión
│   ├── charts.py                        ← Gráficas con Matplotlib/Seaborn
│   └── pdf_report.py                    ← Exportar reporte a PDF (ReportLab)
│
├── 📁 web/                              ← Interfaz Flask
│   ├── app.py                           ← Servidor principal
│   ├── routes.py                        ← Endpoints REST
│   ├── 📁 templates/                    ← HTML con Jinja2
│   │   ├── index.html                   ← Formulario de solicitud
│   │   ├── result.html                  ← Pantalla de dictamen
│   │   └── dashboard.html               ← Panel de métricas
│   └── 📁 static/
│       ├── style.css                    ← Estilos
│       └── charts.js                   ← Gráficas interactivas (Chart.js)
│
├── 📁 tests/
│   ├── test_engine.py                   ← Pruebas unitarias del motor
│   ├── test_validator.py                ← Pruebas de validación
│   └── test_scenarios.py               ← Casos: aprobado, rechazado, zona gris
│
├── 📁 notebooks/
│   └── validacion_german_credit.ipynb  ← Análisis exploratorio + backtesting
│
├── config.py                           ← Configuración global (DB_URL, DEBUG, etc.)
├── requirements.txt                    ← Dependencias del proyecto
├── README.md                           ← Instrucciones de instalación
└── run.py                              ← Punto de entrada: python run.py
```

---

### 📦 Stack de Librerías

```
# requirements.txt
flask==3.0.0           # Interfaz web
sqlalchemy==2.0.0      # ORM para base de datos
pandas==2.1.0          # Manipulación de datos
scikit-learn==1.3.0    # Métricas: matriz de confusión, precisión, recall
matplotlib==3.8.0      # Gráficas estáticas
seaborn==0.13.0        # Gráficas estadísticas bonitas
reportlab==4.0.0       # Exportar reportes a PDF
faker==20.0.0          # Generar datos sintéticos para demo
pytest==7.4.0          # Pruebas unitarias
python-dotenv==1.0.0   # Variables de entorno (para producción futura)
```

---

### 🔮 Decisiones que Protegen el Futuro

Estas decisiones se toman HOY para no reescribir código MAÑANA:

| Decisión de Diseño | Beneficio Futuro |
|---|---|
| Reglas en `rules.json` separado del motor | Agregar/cambiar reglas sin tocar código |
| SQLAlchemy como ORM | Cambiar SQLite→PostgreSQL en 1 línea |
| API REST en Flask (`/api/evaluar`) | Conectar frontend externo o app móvil |
| Pesos en `weights.json` | Ajustar sin recompilar; recalibrar por región |
| Módulo `explainer.py` independiente | Mejorar las explicaciones sin romper el motor |
| Carpeta `tests/` desde el día 1 | Validar que nada se rompe al ampliar |

---

## PARTE 2: HOJA DE RUTA DEL DESARROLLO

---

### 🗓️ Fases de Implementación (Orden Recomendado)

```
SEMANA 1-2 │ FUNDACIÓN
           ├─ Configurar entorno virtual Python
           ├─ Crear estructura de carpetas
           ├─ Diseñar models.py (SQLAlchemy)
           └─ Escribir rules.json + weights.json con reglas base

SEMANA 3-4 │ NÚCLEO
           ├─ validator.py → validaciones de formato y lógica
           ├─ scorer.py    → cálculo DTI y scoring ponderado
           ├─ engine.py    → motor de inferencia completo
           └─ explainer.py → reportes en lenguaje natural

SEMANA 5   │ DATOS
           ├─ mapper.py → transformar German Credit Data
           ├─ generate_demo_data.py → datos sintéticos
           └─ Notebook: análisis exploratorio del dataset

SEMANA 6   │ VALIDACIÓN
           ├─ Backtesting con German Credit (1,000 registros)
           ├─ metrics.py → Matriz de Confusión, Precisión, Recall, F1
           └─ Ajustar pesos en weights.json según resultados

SEMANA 7-8 │ INTERFAZ
           ├─ Flask app.py + routes.py
           ├─ HTML: formulario + pantalla de resultado + dashboard
           └─ Gráficas en dashboard (Chart.js)

SEMANA 9   │ REPORTE PDF + PRUEBAS
           ├─ pdf_report.py → exportar evaluación completa
           ├─ test_engine.py / test_validator.py
           └─ Prueba de carga con CSV masivo

SEMANA 10  │ PULIDO FINAL
           ├─ README.md completo
           ├─ Preparar demo para defensa (datos sintéticos)
           └─ Revisión final de documentación técnica
```

---

## PARTE 3: EL PROMPT MAESTRO

---

> **Instrucciones de uso:**
> Copia y pega el bloque de texto de abajo en una conversación NUEVA
> con Claude (u otro asistente de IA). Envíalo solo, sin agregar nada más.
> Espera que complete la "Primera Tarea" antes de pedir cualquier otra cosa.

---

```
=================================================================
PROMPT MAESTRO — PROYECTO MIHAC v1.0
Motor de Inferencia Heurística para Aprobación de Créditos
=================================================================

## ROL Y CONTEXTO

Eres un arquitecto de software senior especializado en sistemas expertos
e inteligencia artificial aplicada al sector financiero. Vas a guiarme
en la construcción completa del sistema MIHAC, un Motor de Inferencia
Heurística para Aprobación de Créditos, como proyecto de titulación
de ingeniería.

---

## DESCRIPCIÓN DEL SISTEMA

MIHAC es un Sistema Experto basado en reglas heurísticas que automatiza
la evaluación de solicitudes de microcréditos. NO es un modelo de
machine learning estadístico: es un motor de inferencia que aplica
reglas IF-THEN con scoring ponderado, emulando el razonamiento de un
analista de crédito senior.

Qué hace:
- Recibe el perfil financiero de un solicitante
- Aplica reglas heurísticas para calcular un Score (0–100)
- Emite un dictamen: APROBADO / RECHAZADO / REVISIÓN MANUAL
- Genera un reporte en lenguaje natural justificando la decisión
- Registra cada evaluación en una base de datos para auditoría

Qué NO hace:
- No se conecta a Burós de Crédito reales (entrada manual)
- No evalúa créditos hipotecarios ni corporativos
- No realiza transferencias ni dispersión de fondos

---

## STACK TECNOLÓGICO (No cambiar)

- Lenguaje: Python 3.11+
- Web: Flask 3.0 (interfaz y API REST)
- Base de datos: SQLite con SQLAlchemy ORM (migrable a PostgreSQL)
- Datos: German Credit Dataset (UCI) + datos sintéticos con Faker
- Métricas: Scikit-learn (Matriz de Confusión, Precisión, Recall, F1)
- Reportes: Matplotlib + Seaborn + ReportLab (PDF)
- Pruebas: Pytest

---

## VARIABLES DEL SISTEMA

Variables de Entrada (Input):
- Edad              | Int   | 18–99       | Peso: 5%  | <21 = riesgo alto
- Ingreso_Mensual   | Float | >0          | Peso: 30% | Capacidad bruta de pago
- Total_Deuda_Actual| Float | >=0         | Peso: 15% | DTI=Deuda/Ingreso; si >0.40 penalizar
- Historial_Credit. | Int   | 0/1/2       | Peso: 20% | Neutro activa compensación
- Antiguedad_Laboral| Int   | 0–40 años   | Peso: 10% | >2 años reduce riesgo
- Numero_Dependientes| Int  | 0–10        | Peso: 5%  | Reduce capacidad de pago real
- Tipo_Vivienda     | Str   | Propia/etc  | Peso: 5%  | Propia = arraigo
- Proposito_Credito | Str   | Negocio/etc | Peso: 10% | Negocio/Educacion suman; Vacaciones resta
- Monto_Credito     | Float | 500–50000   | Control   | Eleva umbral de exigencia, no suma puntos

Variables de Salida (Output):
- Score_Final          | Int  (0–100)
- Dictamen             | Str: "APROBADO" >80 / "REVISION_MANUAL" 60-80 / "RECHAZADO" <60
- Reporte_Explicacion  | Str en lenguaje natural
- Reglas_Activadas     | List[str] con IDs de reglas disparadas
- DTI_Calculado        | Float para mostrar en reporte

---

## ARQUITECTURA DE ARCHIVOS (Respetar esta estructura)

mihac/
├── core/
│   ├── engine.py        Motor de inferencia
│   ├── scorer.py        Scoring + DTI
│   ├── validator.py     Validaciones
│   └── explainer.py     Reportes en lenguaje natural
├── knowledge/
│   ├── rules.json       Reglas IF-THEN (base de conocimiento)
│   ├── weights.json     Pesos por variable
│   └── thresholds.json  Umbrales de decisión
├── data/
│   ├── mapper.py        German Credit → MIHAC
│   └── generate_demo_data.py
├── database/
│   ├── models.py        SQLAlchemy models
│   └── db.py            Conexión DB
├── reports/
│   ├── metrics.py       Métricas de validación
│   └── charts.py        Gráficas
├── web/
│   ├── app.py           Flask
│   ├── routes.py        Endpoints
│   └── templates/       HTML (index, result, dashboard)
├── tests/
│   └── test_engine.py
├── config.py
├── requirements.txt
└── run.py

---

## REGLAS HEURÍSTICAS BASE (Implementar en rules.json)

El sistema debe poder agregar más reglas en rules.json sin tocar engine.py.

Reglas de penalización fuerte:
- R001: Si DTI > 0.40 → penalizar -25 puntos (sobreendeudamiento)
- R002: Si Historial == 0 (Malo) → penalizar -30 puntos
- R003: Si Edad < 21 → penalizar -10 puntos
- R004: Si Antiguedad_Laboral < 1 → penalizar -15 puntos

Reglas de compensación heurística (el corazón del sistema):
- R005: Si Historial == 1 (Neutro) Y DTI < 0.25 → compensar +10 puntos
- R006: Si Tipo_Vivienda == "Propia" Y Antiguedad_Laboral > 3 → compensar +10 pts
- R007: Si Ingreso_Mensual > (Monto_Credito * 0.30) → compensar +15 puntos
- R008: Si dato faltante Y Score_parcial > 75 → flag "revisar" sin rechazar

Reglas por propósito del crédito:
- R009: Si Proposito == "Negocio" O "Educacion" → sumar +10 puntos
- R010: Si Proposito == "Vacaciones" → restar -8 puntos

Validaciones lógicas de negocio:
- V001: Si Antiguedad_Laboral > (Edad - 15) → ERROR: dato incoherente
- V002: Si Total_Deuda_Actual > Ingreso_Mensual * 12 → WARNING: revisar

---

## LÓGICA DEL SCORING PONDERADO

# Pseudocódigo
DTI = Total_Deuda_Actual / Ingreso_Mensual

score_solvencia   = f(Ingreso_Mensual, DTI, Monto_Credito)          # 30%
score_estabilidad = f(Antiguedad_Laboral, Tipo_Vivienda, Dependientes) # 30%
score_historial   = f(Historial_Crediticio)                          # 20%
score_proposito   = f(Proposito_Credito)                             # 10%
score_perfil      = f(Edad)                                          # 10%

score_base = suma ponderada de los 5 módulos

for regla in rules.json:
    if regla.condicion(datos):
        score_base += regla.impacto
        reglas_activadas.append(regla.id)

Score_Final = max(0, min(100, score_base))

---

## MODELO DE BASE DE DATOS

# Tablas que debe tener models.py

Solicitud:
  id, fecha_solicitud, nombre_solicitante,
  edad, ingreso_mensual, total_deuda_actual,
  historial_crediticio, antiguedad_laboral,
  numero_dependientes, tipo_vivienda,
  proposito_credito, monto_credito

Evaluacion:
  id, solicitud_id (FK→Solicitud), fecha_evaluacion,
  score_final, dictamen, dti_calculado,
  reporte_explicacion, reglas_activadas (JSON),
  tiempo_procesamiento_ms

LogAuditoria:
  id, evaluacion_id (FK→Evaluacion), timestamp,
  accion, usuario, detalle

---

## DATOS: ESTRATEGIA DUAL

German Credit Data:
- URL: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data
- El script data/mapper.py transforma las 20 variables alemanas a las 9
  variables MIHAC y guarda el resultado en german_credit_mapped.csv
- Usar los 1,000 registros para backtesting: comparar decisión MIHAC
  vs etiqueta real. Generar Matriz de Confusión.

Datos Sintéticos para Demo (generate_demo_data.py debe generar estos 5):
1. Cliente Ideal: joven profesional, historial bueno, DTI=0.15
2. Cliente Límite: historial neutro, DTI=0.38, vivienda propia
3. Cliente Zona Gris: sin historial, ingresos medios, negocio propio
4. Cliente Rechazado: historial malo, DTI=0.55, propósito vacaciones
5. Perfil No Bancarizado: sin historial, pero alta estabilidad laboral

---

## INTERFAZ WEB (Flask)

Pantallas requeridas:
1. / → index.html: Formulario de solicitud con todos los campos
2. /evaluar → result.html: Dictamen + score visual (barra/gauge) +
   reporte explicación + reglas activadas + botón descargar PDF
3. /dashboard → dashboard.html: Total evaluaciones, % aprobados,
   distribución de scores, gráfica de morosidad proyectada
4. /api/evaluar → JSON: Endpoint REST para integraciones futuras

Diseño visual:
- Bootstrap 5 (CDN, sin instalar)
- Aprobado: verde #28a745 | Rechazado: rojo #dc3545 | Revisión: amarillo #ffc107
- Score como barra de progreso visual con color dinámico

---

## MÓDULO DE MÉTRICAS (reports/metrics.py)

Al correr backtesting con German Credit generar:
- Matriz de Confusión (heatmap Seaborn)
- Precisión: de los que aprobé, cuántos pagaron
- Recall: de los que debí aprobar, cuántos aprobé
- F1-Score: balance entre precisión y recall
- Tasa de Falsos Positivos (aprobé y no pagó = pérdida financiera)
- Tasa de Falsos Negativos (rechacé y sí pagaba = oportunidad perdida)
- Guardar reporte como PNG + PDF

---

## PRINCIPIOS DE CÓDIGO (No negociables)

1. SEPARACIÓN: La Base de Conocimiento (rules.json, weights.json) NUNCA
   debe estar hardcodeada en engine.py. Siempre se lee del archivo JSON.

2. DOCSTRINGS: Cada función debe tener docstring con parámetros, retorno
   y ejemplo de uso.

3. EXCEPCIONES: Usar try/except en todas las operaciones de DB y lectura
   de archivos. El sistema nunca debe crashear silenciosamente.

4. LOGGING: Usar el módulo logging de Python, nunca print().

5. CONFIG: Todas las constantes (DB_URL, umbrales, rutas) en config.py.
   Nunca hardcodeadas en módulos individuales.

6. IDEMPOTENCIA: La misma entrada siempre produce la misma salida.

---

## CÓMO TRABAJAR CONMIGO EN ESTE PROYECTO

Para cada módulo que construyas, sigue este orden:
1. Primero explícame en 3 líneas qué vas a construir y por qué.
2. Después escribe el código completo con docstrings y manejo de errores.
3. Al final muéstrame cómo probarlo con un ejemplo de uso concreto.

Si necesito ampliar una regla heurística o cambiar un peso, recuérdame
siempre que el cambio va en los archivos .json de knowledge/, NO en Python.

Si me preguntas por una decisión de arquitectura, dame siempre 2 opciones
con sus trade-offs.

---

## PRIMERA TAREA

Empieza por la FUNDACIÓN del proyecto:

1. Crea requirements.txt completo
2. Crea config.py con todas las constantes del sistema
3. Crea knowledge/rules.json con las 10 reglas base documentadas
4. Crea knowledge/weights.json con los pesos de cada variable
5. Crea knowledge/thresholds.json con los umbrales de decisión
6. Crea database/models.py con los 3 modelos SQLAlchemy

No construyas el motor de inferencia todavía. Solo la fundación.
Confirma que todo esté correcto antes de avanzar al siguiente módulo.

=================================================================
FIN DEL PROMPT MAESTRO — MIHAC v1.0
=================================================================
```

---

## PARTE 4: GUÍA DE USO

---

### ✅ Cómo usar este prompt correctamente

**Paso 1 — Sesión nueva:**
Abre una conversación nueva con Claude. Copia todo el bloque del Prompt
Maestro (entre las líneas de ===) y envíalo solo, sin agregar nada más.

**Paso 2 — Desarrollo por módulos (en este orden):**
```
1.  validator.py
2.  scorer.py              (incluye cálculo DTI)
3.  engine.py              (usa validator + scorer + rules.json)
4.  explainer.py
5.  data/mapper.py
6.  data/generate_demo_data.py
7.  database/db.py
8.  reports/metrics.py  +  charts.py
9.  web/app.py  +  routes.py
10. web/templates/         (index, result, dashboard)
11. tests/test_engine.py
12. reports/pdf_report.py
```

**Paso 3 — Checkpoint de validación (después de engine.py):**
Pide siempre esto antes de continuar:
> "Corre los 5 perfiles sintéticos de demo y muéstrame el resultado
> de cada uno antes de avanzar al siguiente módulo."

**Paso 4 — Backtesting (antes de la interfaz web):**
> "Carga german_credit_mapped.csv, corre las 1,000 evaluaciones
> y muéstrame la Matriz de Confusión y el F1-Score del sistema."

---

### ⚠️ Errores comunes que debes evitar

| Error | Por qué ocurre | Cómo evitarlo |
|---|---|---|
| Pedir todo a la vez | El código sale incompleto o con bugs | Pedir módulo por módulo |
| Cambiar pesos en engine.py | Mezcla conocimiento con lógica | Siempre editar weights.json |
| Saltarse las pruebas | Bugs ocultos hasta la defensa | Pedir test después de cada módulo |
| Hardcodear rutas de archivo | No funciona en otra computadora | Usar config.py siempre |
| No versionar con Git | Perder trabajo por accidente | git commit después de cada módulo |

---

### 🎯 Lo que tendrás al terminar

- ✅ Motor de inferencia con 10+ reglas heurísticas expansibles
- ✅ Base de datos SQLite lista para migrar a PostgreSQL
- ✅ Interfaz web Flask con formulario, resultado y dashboard
- ✅ Backtesting validado con 1,000 registros reales
- ✅ Métricas de tesis: Precisión, Recall, F1, Matriz de Confusión
- ✅ Reporte PDF descargable por evaluación
- ✅ 5 perfiles demo listos para mostrar en la defensa
- ✅ API REST /api/evaluar para futuras integraciones
- ✅ Código limpio con docstrings, tests y README

---

*Documento generado como parte de la planificación técnica del proyecto MIHAC*
*Versión 1.0 — Listo para iniciar desarrollo*
