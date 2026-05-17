---
name: longitudinal-analysis-dimensions
description: Invoke when analyzing any longitudinal dataset (training log, financial records, health metrics, habit tracker, software telemetry, etc.). Catalog of 25 obligatory analytical dimensions, organized by category, with domain-agnostic structure and explicit adaptations to 5 domains (gym, finance, health, productivity, telemetry).
---

# Longitudinal Analysis · 25 dimensiones obligatorias

## Principio

Para CUALQUIER dataset longitudinal, calcula al menos las 25 dimensiones de este catálogo que apliquen al dataset. Adapta el nombre/aplicación al dominio (gym, finanzas, salud, hábitos, telemetría), pero **la estructura analítica es invariante**.

## Las 25 dimensiones

### 4.1 · Métricas globales del periodo

- Duración total · número de eventos/sesiones · "volumen" agregado
- Eventos por unidad de tiempo (media · mediana · varianza)
- Top N entidades por volumen

### 4.2 · Trayectoria por entidad

Para las top 20-30 entidades por número de eventos:
- Fecha primer evento · fecha último evento · span en meses
- Métrica inicial (media primeros 3 eventos) · métrica actual (media últimos 3)
- Métrica pico (máximo histórico) + fecha del pico
- Regresión lineal global sobre toda la historia
- Pendiente en kg/mes (o unidad correspondiente)

### 4.3 · Ritmo RECIENTE · ventana de 90 días [CRÍTICO]

**Esta dimensión es la que separa informes superficiales de quirúrgicos.**

- Para cada entidad: regresión lineal SOLO sobre los últimos 90 días
- Comparar con la pendiente histórica: ¿acelerando, estabilizando, regresando?
- Clasificar cada entidad en una de cinco categorías:
  - `progressing_fast` (>1 unidad/mes)
  - `progressing` (0.3 a 1)
  - `stalled` (-0.3 a 0.3)
  - `regressing` (<-0.3)
  - `no_data` (sin actividad reciente)

### 4.4 · Detección de plateaus

Para cada entidad activa:
- Días desde el último máximo histórico
- Número de eventos en ese plateau
- **Distinguir entre plateau "real"** (sigue activo sin avanzar) **y plateau "artefacto"** (cambio de variante hace incomparable la métrica)

### 4.5 · Detección de ABANDONO

Para cada entidad con ≥20 eventos históricos:
- Días desde el último evento
- Si >60 días sin actividad: clasificar como abandonado
- ¿Coincide la fecha del último evento con la de otros abandonados?
- Si **5+ entidades fueron abandonadas en la misma semana**, hay un evento programático mayor que merece investigación

### 4.6 · Patrones temporales

- Distribución por día de la semana
- Distribución por mes del año
- Distribución por año (año a año)
- Detección de pausas: gaps mayores a 14 días, con fechas

### 4.7 · Cronobiología (si hay timestamps con hora)

- Distribución por hora del día
- Performance por hora: ¿la métrica clave varía con la hora?
- **Si la diferencia entre horas pico y horas valle es >10 % de la métrica: HALLAZGO IMPORTANTE**

Esta dimensión produjo el famoso "11 kg de diferencia en bench entre 18h y 21h" que llevó al hardcode de hora 20-21h.

### 4.8 · Densidad y dispersión

- Eventos por sesión / por día / por unidad organizativa
- Evolución temporal de la densidad
- Outliers: top 10 sesiones extremas (más densas, más volumen)

### 4.9 · Recuperación post-pausa

Para cada pausa ≥14 días:
- Métrica antes vs primera medición después
- Número de sesiones hasta volver al nivel previo
- ¿Hay efecto rebote (más PRs que media en el mes posterior)?

### 4.10 · Cambios de régimen (Jaccard)

- Identifica el top-N de entidades activas cada mes
- Calcula similitud Jaccard entre meses consecutivos
- Cuando Jaccard < 0.5: cambio significativo. Marca qué se añadió y qué se eliminó

### 4.11 · Frecuencia PR (nuevos máximos)

- PRs nuevos por mes (acumulado y absoluto)
- Top 10 meses con más PRs (incluir contexto: ¿post-pausa? ¿inicio?)
- Gap entre PRs consecutivos por entidad

### 4.12 · Streaks de adherencia

- Rachas consecutivas con actividad mínima (e.g., ≥2 eventos/semana)
- Top 5 rachas más largas
- Racha actual: ¿en curso? ¿terminada?

### 4.13 · Ratios estructurales del dominio

Identifica los ejes principales del dominio y mide su balance:

- **Gym**: push/pull, bilateral/unilateral, máquina/libre, compuesto/aislamiento
- **Finanzas**: ingreso/gasto, fijo/variable, activos/pasivos
- **Hábitos**: rutina/improvisado, intenso/suave, social/solo
- **Salud**: actividad/descanso, calorías/gasto, sueño/vigilia

### 4.14 · Proyecciones a 6 y 12 meses

Para cada entidad activa:
- Extrapolación lineal al ritmo de los últimos 90 días
- Etiqueta cada proyección como "verosímil", "improbable" o "artefacto"
- **Si la proyección a 12 meses es plana o regresiva: alerta de trayectoria insostenible**

### 4.15 · Análisis de "mejores eventos"

- Top 10 eventos por métrica clave
- ¿Hay un evento estadísticamente atípico (>2σ por encima del segundo)?
- ¿Qué tienen en común los top? ¿Vienen tras pausa? ¿Concentran un dominio?

### 4.16 · Distribución de "intensidad"

Bandas razonables según dominio (e.g., rangos de reps en gym; bandas de gasto en finanzas) por año, año a año.
- ¿Hay bandas casi vacías? ¿Bandas crecientes/decrecientes?

### 4.17 · Fatiga intra-sesión (si aplica)

Diferencial entre el primer ítem de una sesión y el último.
- ¿Cae el rendimiento? ¿Cuánto?

### 4.18 · Auditoría de notación

- ¿Hay cambios de unidad documentados o inferibles?
- ¿Hay sub-poblaciones donde el "mismo nombre" significa cosas distintas?
- ¿Hay cabeceras o tags obsoletos que el sujeto sigue copiando sesión a sesión?

### 4.19 · Detección de patrones programáticos

- Esquemas predominantes (en gym: straight/ascending/pyramid · en finanzas: pagos recurrentes, picos estacionales)
- ¿Hay "bucles" — el mismo patrón repetido N veces seguidas sin variación?

### 4.20 · Lectura del TEXTO CRUDO

Si el dataset incluye texto libre (notas, descripciones, comentarios):
- Buscar menciones de: lesión, dolor, molestia, fatiga, cambio, decisión, "hoy no", motivos de pausa, protocolos mencionados pero no parseados
- **Identificar al menos 1 hallazgo que NO esté en las métricas derivadas**

Esta es la dimensión que más se olvida y la que más insight produce.

### 4.21 · Comparación con el "yo del pasado"

- Métricas del primer trimestre vs último trimestre
- ¿Qué ha mejorado? ¿Qué ha empeorado? ¿Qué se ha mantenido?

### 4.22 · Aceleración (segunda derivada)

- ¿La pendiente está acelerando, desacelerando, o constante?
- Útil para detectar inflexiones ANTES de que el plateau sea evidente

### 4.23 · Co-ocurrencias

- ¿Qué entidades aparecen juntas? Top pares de co-ocurrencia
- Indicador de "rutina" o "régimen" subyacente

### 4.24 · Primer evento de la sesión (o equivalente)

- ¿Qué entidad abre las sesiones?
- ¿Es siempre la misma? ¿Ha cambiado?

### 4.25 · Estado actual real · últimos 30 días

- Snapshot exhaustivo del periodo reciente
- Inventario completo de entidades activas con métricas
- Lectura inmediata del régimen actual

## Adaptaciones por dominio

El framework anterior es agnóstico de dominio. Adaptaciones específicas:

### Bitácora deportiva (gym, running, ciclismo)

- "Entidad" = ejercicio o sesión
- "Métrica" = peso, reps, tonelaje, ritmo, frecuencia cardíaca
- Ratios típicos: push/pull · bilateral/unilateral · compuesto/aislamiento
- Texto crudo: nombre del ejercicio + comentarios libres
- Cronobiología CRÍTICA (puede haber diferencias 10-15 % por hora)

### Finanzas personales

- "Entidad" = categoría de gasto o fuente de ingreso
- "Métrica" = importe, frecuencia, %
- Ratios típicos: fijo/variable · esencial/discrecional · ingreso/gasto
- Texto crudo: descripción de la transacción
- Cronobiología: día del mes (cobro vs gasto)
- Detección de patrones: pagos recurrentes · picos estacionales

### Métricas de salud (peso, sueño, glucosa)

- "Entidad" = métrica corporal
- "Métrica" = valor + contexto (comida previa, actividad)
- Ratios típicos: sueño profundo/total · actividad/descanso · calorías/gasto
- Texto crudo: diario de alimentos, mood, eventos
- Cronobiología: hora de medición vs valor

### Productividad / hábitos

- "Entidad" = tarea, proyecto, hábito
- "Métrica" = tiempo dedicado, frecuencia, completitud
- Ratios típicos: focus/reactivo · creativo/operativo · solo/colaborativo
- Texto crudo: descripción de tareas, notas de retrospectiva
- Cronobiología: hora del día vs productividad

### Telemetría software / uso

- "Entidad" = feature, endpoint, página
- "Métrica" = uso, latencia, errores
- Ratios típicos: lectura/escritura · autenticado/anónimo · móvil/desktop
- Texto crudo: logs, errores, comentarios de usuarios
- Cronobiología: hora pico vs hora valle

## Cómo aplicar este catálogo

1. **No todas las dimensiones aplican a todos los datasets**. Si una no aplica, justifica brevemente por qué (NO la saltes sin justificar).

2. **Marca cada dimensión como** `aplicada`, `no aplica · razón`, `aplazada · razón`.

3. **Dimensión CRÍTICA**: §4.3 (ritmo reciente 90d). Si esta no se hace, el informe es superficial.

4. **Dimensión MÁS IGNORADA**: §4.20 (texto crudo). Casi siempre produce el hallazgo más valioso del informe.

5. **Tras Pase 2**: verifica que has cubierto ≥18 de las 25 dimensiones. Si menos, hay algo mal.

6. **En Pase 3 (ultrathink)**: revisa la lista de "no aplica" y ataca al menos 2 más si es posible.

## Anti-patrones

- ❌ Calcular solo §4.1 (globales) y declarar informe terminado
- ❌ Saltarse §4.3 (ritmo reciente) "porque es lo mismo que la tendencia global" — NO lo es
- ❌ Ignorar §4.20 (texto crudo) "porque no hay métricas en notas" — ahí está el insight
- ❌ Tratar §4.4 plateaus y §4.5 abandonos como la misma cosa
- ❌ Producir 25 secciones (una por dimensión) sin sintetizar. Agrupa por temática.
