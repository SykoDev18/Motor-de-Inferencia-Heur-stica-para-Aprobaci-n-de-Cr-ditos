# MIHAC — Datos y Fuentes

## Fuentes de Datos

### 1. German Credit Dataset (UCI Machine Learning Repository)

**URL**: https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data  
**Archivo**: `german.data`  
**Registros**: 1,000 solicitudes de crédito  
**Atributos**: 20 predictores + 1 clase (bueno/malo)  
**Autores**: Prof. Dr. Hans Hofmann, Universität Hamburg  
**Año**: 1994  
**Licencia**: CC BY 4.0 (Creative Commons Attribution 4.0)

#### Descarga

Opción A — Manual:
```
1. Ir a https://archive.ics.uci.edu/dataset/144/
2. Descargar german.data
3. Colocar en esta carpeta: mihac/data/german.data
```

Opción B — Programática (ucimlrepo):
```python
from mihac.data.mapper import GermanCreditMapper
mapper = GermanCreditMapper()
df = mapper.load_and_transform(None)  # descarga desde UCI
```

Opción C — Línea de comandos:
```bash
curl -o mihac/data/german.data \
  "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data"
```

#### Formato del Archivo

El archivo `german.data` es un CSV sin encabezados, separado por espacios,
con 21 columnas (20 atributos + clase):

| # | Columna  | Descripción Original        | Mapeo MIHAC             |
|---|----------|----------------------------|-------------------------|
| 1 | attr_1   | Estado cuenta corriente     | → historial_crediticio  |
| 2 | attr_2   | Plazo del crédito (meses)   | → (cálculo de ingreso)  |
| 3 | attr_3   | Historial de crédito        | → historial_crediticio  |
| 4 | attr_4   | Propósito del crédito       | → proposito_credito     |
| 5 | attr_5   | Monto del crédito (DM)      | → monto_credito (MXN)   |
| 6 | attr_6   | Cuenta de ahorros           | → total_deuda_actual    |
| 7 | attr_7   | Empleo desde                | → antiguedad_laboral    |
| 8 | attr_8   | Tasa cuota/ingreso (%)      | → (cálculo de ingreso)  |
| 9 | attr_9   | Sexo/estado civil           | ❌ EXCLUIDO (ética)     |
|10 | attr_10  | Co-deudor/garante           | (no usado)              |
|11 | attr_11  | Residencia desde            | (no usado)              |
|12 | attr_12  | Propiedad                   | → tipo_vivienda (apoyo) |
|13 | attr_13  | Edad                        | → edad                  |
|14 | attr_14  | Otros planes de pago        | → total_deuda_actual    |
|15 | attr_15  | Tipo de vivienda            | → tipo_vivienda         |
|16 | attr_16  | Créditos existentes         | (no usado)              |
|17 | attr_17  | Tipo de empleo              | (no usado)              |
|18 | attr_18  | Dependientes                | → numero_dependientes   |
|19 | attr_19  | Teléfono                    | (no usado)              |
|20 | attr_20  | Trabajador extranjero       | (no usado)              |
|21 | clase    | 1=bueno, 2=malo             | → etiqueta_real         |

#### Nota Ética (A9)

La variable A9 (sexo/estado civil) se **excluye intencionalmente** del mapeo
para evitar discriminación por género en el scoring crediticio. Esto cumple con:
- Principios de IA ética (EU AI Act, AI Fairness 360)
- Normativa mexicana de igualdad (Ley Federal para Prevenir y Eliminar la Discriminación)
- Buenas prácticas de fair lending (Equal Credit Opportunity Act)

#### Nota sobre Ingreso Mensual

El dataset NO contiene ingreso directo. Se estima a partir de:
- A5 (monto del crédito en DM)
- A2 (plazo en meses)
- A8 (tasa de cuota como % del ingreso)

Fórmula: `ingreso_est = (monto_DM / plazo) / (tasa% / 100) × 10.5`

El factor 10.5 aproxima la equivalencia DM → MXN en poder adquisitivo.
Mínimo clampeado a $3,000 MXN (salario mínimo viable).


### 2. Datos Sintéticos (demo)

**Archivo**: `generate_demo_data.py`  
**Registros**: 7 perfiles nominales + generador aleatorio  
**Fuente**: Creados manualmente para cubrir cada ruta lógica del motor

#### 7 Perfiles Nominales

| Perfil               | Dictamen Esperado | Propósito                          |
|---------------------|-------------------|------------------------------------|
| cliente_ideal        | APROBADO          | Score ≈ 100, perfil impecable      |
| alto_riesgo          | RECHAZADO         | Score ≈ 0, todo negativo           |
| zona_gris            | REVISION_MANUAL   | Señales mixtas, score 60-79        |
| heuristica_en_accion | APROBADO          | Reglas R011-R015 compensan         |
| dti_critico          | RECHAZADO         | DTI > 60% → rechazo automático     |
| joven_prometedor     | REVISION_MANUAL   | Joven con potencial                |
| monto_alto_exigente  | REVISION_MANUAL   | Monto > $20K → umbral 85           |


## Archivos en este Directorio

| Archivo                    | Descripción                                        |
|---------------------------|----------------------------------------------------|
| `mapper.py`               | GermanCreditMapper: transforma german.data → MIHAC |
| `generate_demo_data.py`   | DemoDataGenerator: 7 perfiles + batch aleatorio    |
| `german.data`             | (DESCARGABLE) Dataset UCI crudo                    |
| `german_credit_mihac.csv` | (GENERADO) Dataset transformado al formato MIHAC   |
| `demo_batch.csv`          | (GENERADO) Batch demo exportado a CSV              |
| `README.md`               | Este archivo                                       |


## Uso Rápido

```python
# Opción 1: German Credit Dataset
from mihac.data.mapper import GermanCreditMapper
mapper = GermanCreditMapper()
df = mapper.load_and_transform("mihac/data/german.data")
dicts = mapper.to_mihac_dicts(df)

# Opción 2: Datos sintéticos
from mihac.data.generate_demo_data import DemoDataGenerator
gen = DemoDataGenerator()
ideal = gen.get_profile("cliente_ideal")
batch = gen.generate_batch(100)

# Evaluar con el motor
from mihac.core.engine import InferenceEngine
engine = InferenceEngine()
resultado = engine.evaluate(ideal["datos"])
resultados = engine.evaluate_batch(dicts)
```


## Limitaciones

1. **Ingreso estimado**: El ingreso mensual es una proxy, no un dato directo del dataset original.
2. **Deuda estimada**: La deuda se infiere de la cuenta de ahorros y planes de pago, no es un valor real.
3. **Conversión monetaria**: El factor DM → MXN (10.5) es una aproximación histórica.
4. **Sesgo original**: El dataset de 1994 puede contener sesgos históricos en la calificación alemana.
5. **Tamaño**: Solo 1,000 registros — suficiente para demostración pero no para producción.
6. **Desbalance**: 70/30 (buenos/malos) — leve, no requiere tratamiento especial para MIHAC.
