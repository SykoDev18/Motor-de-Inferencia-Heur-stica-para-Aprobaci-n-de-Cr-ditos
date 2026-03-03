# MIHAC v1.0 — Análisis Crítico Comparativo

> **Motor de Inferencia Heurística para Aprobación de Créditos**
> Análisis de ventajas, limitaciones y comparación con enfoques alternativos.

---

## Índice

1. [Enfoque Adoptado: Sistema Basado en Reglas](#1-enfoque-adoptado-sistema-basado-en-reglas)
2. [Ventajas del Enfoque Basado en Reglas](#2-ventajas-del-enfoque-basado-en-reglas)
3. [Limitaciones del Enfoque Basado en Reglas](#3-limitaciones-del-enfoque-basado-en-reglas)
4. [Comparación con Enfoques Alternativos](#4-comparación-con-enfoques-alternativos)
5. [Análisis FODA del Sistema MIHAC](#5-análisis-foda-del-sistema-mihac)
6. [Recomendaciones de Mejora](#6-recomendaciones-de-mejora)
7. [Conclusión](#7-conclusión)

---

## 1. Enfoque Adoptado: Sistema Basado en Reglas

MIHAC implementa un **sistema experto basado en reglas heurísticas** con las siguientes características:

| Característica | Implementación en MIHAC |
|:---------------|:----------------------|
| Representación del conocimiento | 15 reglas IF-THEN en JSON + funciones de scoring |
| Mecanismo de inferencia | Encadenamiento hacia adelante (forward chaining) |
| Resolución de conflictos | Acumulación aditiva, sin exclusión mutua |
| Explicabilidad | Texto en lenguaje natural generado automáticamente |
| Aprendizaje | Ninguno (reglas estáticas definidas por experto) |
| Transparencia | Total — cada decisión es trazable paso a paso |

---

## 2. Ventajas del Enfoque Basado en Reglas

### 2.1 Transparencia y Explicabilidad Total

**Esta es la ventaja más crítica para el dominio financiero.**

El sistema puede explicar exactamente **por qué** se tomó cada decisión:

```
▲ R001: +20 — Premio por historial crediticio bueno
▼ R014: -20 — DTI alto: penalización por sobreendeudamiento
```

En contraste, un modelo de machine learning tipo red neuronal o gradient boosting produce un score sin explicación inherente. Técnicas como SHAP o LIME proporcionan explicaciones aproximadas, pero no certezas.

**Impacto regulatorio**: En México, la CNBV (Comisión Nacional Bancaria y de Valores) y regulaciones como la Ley para Regular las Instituciones de Tecnología Financiera exigen que los solicitantes conozcan las razones de rechazo de un crédito. Un sistema basado en reglas cumple esto nativamente.

### 2.2 Validación por Expertos del Dominio

Las reglas fueron diseñadas con conocimiento del dominio crediticio y pueden ser:

- **Leídas** directamente del archivo `rules.json` por analistas no programadores
- **Validadas** por oficiales de crédito que conocen las políticas de la institución
- **Modificadas** sin cambiar código, solo editando el JSON
- **Auditadas** por reguladores que necesitan entender la lógica de aprobación

### 2.3 Determinismo y Reproducibilidad

| Propiedad | Garantía |
|:----------|:---------|
| Misma entrada → misma salida | **Siempre** (verificado con 100 evaluaciones × 2 instancias) |
| Sin dependencia de datos de entrenamiento | Sí |
| Sin varianza estocástica | Sí |
| Reproducible en cualquier momento | Sí |

Un modelo de ML puede producir diferentes resultados según el conjunto de entrenamiento, la semilla aleatoria o la versión del framework.

### 2.4 Tiempo de Desarrollo Reducido

| Fase | Sistema basado en reglas | Sistema de ML |
|:-----|:------------------------|:-------------|
| Recolección de datos | No requerida (el experto define reglas) | Requiere miles/millones de registros históricos |
| Etiquetado | No requerido | Necesita etiquetas de buenos/malos pagadores |
| Entrenamiento | No aplica | Horas/días de tuning e hiperparámetros |
| Validación | Revisión por experto de dominio | Cross-validation, curvas ROC, matrices de confusión |
| Total estimado | 2-4 semanas | 2-6 meses |

### 2.5 Rendimiento Excepcional

Siendo lógica determinista sin cálculos matriciales:

| Métrica | MIHAC | ML típico (inferencia) |
|:--------|------:|:----------------------|
| Latencia por evaluación | **0.41 ms** | 5-50 ms (dependiendo del modelo) |
| Throughput | **2,424 evals/s** | 50-500 evals/s |
| Memoria | ~10 MB (Python + JSON) | 100 MB - 2 GB (modelo + dependencias) |
| Dependencias | json, math estándar | scikit-learn, PyTorch, TensorFlow, etc. |

### 2.6 Facilidad de Mantenimiento

```json
// Agregar una nueva regla: solo añadir al JSON
{
  "id": "R016",
  "descripcion": "Penalización por monto excesivo respecto al ingreso",
  "condicion_campo": "monto_credito_ratio",
  "condicion_operador": ">",
  "condicion_valor": 5.0,
  "impacto_puntos": -15,
  "tipo": "directa",
  "activa": true
}
```

No requiere re-entrenamiento, re-validación estadística ni re-deployment completo.

### 2.7 Funcionamiento con Datos Limitados

MIHAC funciona desde el **primer día** sin necesitar datos históricos. Esto es crucial para:

- Instituciones financieras nuevas sin historial de préstamos
- Mercados emergentes sin bureaus de crédito establecidos
- Productos nuevos sin datos de desempeño previo

---

## 3. Limitaciones del Enfoque Basado en Reglas

### 3.1 Sin Capacidad de Aprendizaje

| Aspecto | Limitación |
|:--------|:-----------|
| Patrones ocultos | No puede descubrir correlaciones no previstas por el experto |
| Adaptación | No se ajusta automáticamente a cambios en el mercado |
| Evolución | Requiere intervención humana para actualizar reglas |

**Ejemplo**: Si la inflación reduce el poder adquisitivo, los umbrales de ingreso en las reglas de scoring deben ajustarse manualmente.

### 3.2 Precisión Predictiva Limitada

Un modelo de ML entrenado con datos históricos de pagos reales puede alcanzar:

| Métrica | Sistema de reglas (típico) | ML supervisado (típico) |
|:--------|:------------------------:|:-----------------------:|
| AUC-ROC | 0.65 – 0.75 | 0.80 – 0.95 |
| KS statistic | 30 – 45 | 50 – 70 |
| Gini coefficient | 0.30 – 0.50 | 0.60 – 0.90 |

> **Nota**: MIHAC no tiene datos históricos de desempeño para calcular estas métricas.
> Los rangos son estimaciones basadas en literatura del dominio.

### 3.3 Escalabilidad del Conocimiento

A medida que se agregan más reglas:

- **Interacciones imprevistas**: Reglas pueden producir efectos combinados no previstos
- **Mantenimiento costoso**: Con 100+ reglas, la complejidad crece exponencialmente
- **Cobertura incompleta**: Es imposible cubrir todas las combinaciones posibles de las 9 variables

```
Combinaciones posibles (estimadas):
  9 variables × múltiples rangos ≈ 100,000+ combinaciones
  15 reglas cubren solo una fracción de este espacio
```

### 3.4 Sesgo del Experto

Las reglas reflejan el **criterio subjetivo** del diseñador:

| Decisión de diseño | Alternativa posible |
|:-------------------|:-------------------|
| Historial bueno = +20, malo = -25 | ¿Por qué la penalización es mayor que el premio? |
| Umbral DTI crítico = 60% | ¿Por qué no 50% o 70%? |
| Vacaciones = -8 puntos | ¿Es justo penalizar el propósito? |
| Edad < 21 = -12 puntos | ¿Discriminación etaria justificada? |

En ML, estos pesos se aprenden de los datos, reduciendo (pero no eliminando) el sesgo humano.

### 3.5 Sin Manejo de Incertidumbre

MIHAC no modela probabilidades. El dictamen es categórico:

- Score 80 → APROBADO (100% confianza declarada)
- Score 79 → REVISION_MANUAL (pero la diferencia real es mínima)

Un modelo probabilístico diría: "70% de probabilidad de buen pago", permitiendo decisiones más matizadas.

### 3.6 Dependencia de Variables Declaradas

El sistema confía en los datos proporcionados por el solicitante sin validación externa:

| Variable | Riesgo |
|:---------|:-------|
| Ingreso mensual | Puede ser inflado o subdeclarado |
| Total deuda actual | Puede omitir deudas informales |
| Antigüedad laboral | No se verifica con el empleador |

---

## 4. Comparación con Enfoques Alternativos

### 4.1 Matriz Comparativa

| Criterio | Reglas (MIHAC) | Árboles de Decisión | Redes Neuronales | Regresión Logística | Sistemas Bayesianos |
|:---------|:-------------:|:-------------------:|:----------------:|:-------------------:|:-------------------:|
| **Explicabilidad** | ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| **Precisión predictiva** | ★★★☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Datos requeridos** | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ | ★★★☆☆ |
| **Velocidad inferencia** | ★★★★★ | ★★★★★ | ★★★☆☆ | ★★★★★ | ★★★★☆ |
| **Mantenimiento** | ★★★★☆ | ★★★☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ |
| **Cumplimiento regulatorio** | ★★★★★ | ★★★★☆ | ★★☆☆☆ | ★★★★☆ | ★★★☆☆ |
| **Adaptabilidad** | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ | ★★★★☆ |
| **Costo de desarrollo** | ★★★★★ | ★★★☆☆ | ★★☆☆☆ | ★★★☆☆ | ★★☆☆☆ |

### 4.2 vs. Árboles de Decisión (CART, Random Forest)

| Aspecto | Ventaja MIHAC | Ventaja Árboles |
|:--------|:-------------|:---------------|
| Interpretabilidad | Reglas legibles por no-técnicos | Visualización gráfica posible |
| Interacción variables | Manual via reglas de compensación | Automática en cada split |
| Overfitting | No aplica (sin datos de entrenamiento) | Riesgo real, requiere poda |
| Actualización | Editar JSON | Re-entrenar con datos nuevos |

### 4.3 vs. Redes Neuronales

| Aspecto | MIHAC | Redes Neuronales |
|:--------|:------|:----------------|
| Precisión en patrones complejos | Baja | **Alta** |
| Explicabilidad | **Total** | Opaca (caja negra) |
| Datos necesarios | **0 (cero)** | Miles a millones |
| Infraestructura | **CPU estándar** | GPU recomendada |
| Riesgo regulatorio | **Bajo** | Alto (discriminación algorítmica) |

### 4.4 vs. Scorecard Tradicional (Regresión Logística)

| Aspecto | MIHAC | Scorecard |
|:--------|:------|:---------|
| Base matemática | Heurísticas de experto | Estadística (log-odds) |
| Calibración probabilística | No | **Sí** (probabilidad de default) |
| Datos históricos | No requiere | **Requiere** (mínimo ~2,000 casos) |
| Validación estadística | No aplica | **AUC, KS, Gini mensurables** |
| Implementación regulatoria | **Directa** | Estándar de la industria |

### 4.5 vs. Sistemas Bayesianos

| Aspecto | MIHAC | Redes Bayesianas |
|:--------|:------|:----------------|
| Manejo de incertidumbre | Categórico (sí/no) | **Probabilístico** |
| Dependencias entre variables | Parcial (compensaciones) | **Modelado explícito** |
| Complejidad de diseño | **Baja** | Alta (requiere grafo causal) |
| Incorporación de evidencia | Estática | **Dinámica (actualización)** |

---

## 5. Análisis FODA del Sistema MIHAC

### Fortalezas (internas, positivas)

- Transparencia total en las decisiones
- Cumplimiento regulatorio nativo
- Rendimiento de 2,424 evaluaciones/segundo
- Determinismo y reproducibilidad garantizados
- Mantenimiento por no-programadores (editar JSON)
- Suite de 254 tests con 92% de cobertura

### Oportunidades (externas, positivas)

- Integración con bureaus de crédito (Buró de Crédito, Círculo de Crédito) para validar historial
- Evolución a sistema híbrido: reglas + ML como segunda opinión
- Expansión a otros productos (crédito automotriz, personal, tarjetas)
- API REST para integración con sistemas bancarios core

### Debilidades (internas, negativas)

- Sin aprendizaje automático de datos históricos
- Precisión predictiva limitada comparada con ML supervisado
- Reglas diseñadas con sesgo del experto, no datos empíricos
- Sin calibración probabilística (no dice "70% de probabilidad de pago")
- Espacio de decisión cubierto incompleto (15 reglas vs. miles de combinaciones)

### Amenazas (externas, negativas)

- Regulaciones futuras podrían exigir modelos calibrados estadísticamente
- Competidores con modelos de ML podrían ofrecer tasas más competitivas por mejor discriminación
- Cambios macroeconómicos (inflación, crisis) invalidan los umbrales estáticos
- Fraude sofisticado explota la transparencia de las reglas (gaming)

---

## 6. Recomendaciones de Mejora

### Corto plazo (sin cambiar la arquitectura)

| # | Mejora | Esfuerzo | Impacto |
|:-:|:-------|:--------:|:-------:|
| 1 | Agregar más reglas de compensación para reducir falsos negativos | Bajo | Alto |
| 2 | Implementar umbrales graduales (no solo 80/85) | Bajo | Medio |
| 3 | Conectar con Buró de Crédito para validar historial | Medio | Alto |
| 4 | Agregar variable "plazo del crédito" para refinar DTI | Bajo | Medio |
| 5 | Logging de decisiones para análisis posterior | Bajo | Alto |

### Mediano plazo (evolución del sistema)

| # | Mejora | Descripción |
|:-:|:-------|:------------|
| 1 | **Modelo híbrido** | Usar MIHAC como primera línea + regresión logística como validación |
| 2 | **Backtesting** | Comparar decisiones de MIHAC con desempeño real de créditos pasados |
| 3 | **Calibración** | Ajustar pesos de reglas basándose en datos históricos de mora |
| 4 | **A/B testing** | Comparar tasa de aprobación y mora vs. modelo estadístico |
| 5 | **Score probabilístico** | Convertir score 0-100 a probabilidad de pago usando datos históricos |

### Largo plazo (transformación)

| # | Mejora | Descripción |
|:-:|:-------|:------------|
| 1 | **ML supervisado como complemento** | Entrenar modelo con datos de pagos reales generados por MIHAC |
| 2 | **Reglas autogeneradas** | Usar árboles de decisión para descubrir nuevas reglas |
| 3 | **Monitoreo de drift** | Detectar cuando las reglas dejan de ser efectivas |

---

## 7. Conclusión

El enfoque basado en reglas adoptado por MIHAC es **la elección correcta** para el contexto actual del proyecto por las siguientes razones:

1. **Sin datos históricos disponibles**: No existe un dataset de préstamos aprobados/rechazados con resultado de pago. Sin datos, el ML supervisado no es viable.

2. **Requisito de explicabilidad**: El dominio financiero exige que cada decisión sea explicable y auditable. Las reglas cumplen esto nativamente.

3. **Cumplimiento regulatorio**: Las normativas financieras requieren transparencia en los modelos de crédito. Un sistema de reglas es directamente auditable.

4. **Velocidad de implementación**: El sistema se desarrolló en 9 semanas con 254 tests y 92% de cobertura. Un sistema equivalente basado en ML requeriría meses adicionales solo para la recolección y preparación de datos.

5. **Rendimiento excepcional**: 2,424 evaluaciones por segundo con latencia de 0.41ms superan ampliamente cualquier necesidad operativa actual.

Sin embargo, **MIHAC debe evolucionar**. Una vez que se acumule historial de decisiones y resultados de pago (12-24 meses), se recomienda:

- Realizar backtesting de las decisiones del sistema
- Calibrar los pesos de las reglas con datos empíricos
- Evaluar la incorporación de un modelo estadístico complementario
- Mantener el sistema de reglas como capa de explicabilidad y compliance

> **El sistema basado en reglas no es el destino final — es el punto de partida correcto que permite operar de inmediato mientras se construye la base de datos necesaria para métodos más sofisticados.**

---

*Análisis crítico — MIHAC v1.0 © 2026*
