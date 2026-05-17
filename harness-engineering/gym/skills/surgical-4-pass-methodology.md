---
name: surgical-4-pass-methodology
description: Invoke when producing any deep analytical artifact (longitudinal report, plan audit, code review, document analysis) that requires multiple passes with ultrathink loop. Defines the 4-pass methodology (Reconocimiento → Análisis → Ultrathink → Síntesis) with explicit decision rules, trigger phrases, and stop criteria. Used by surgical-report-builder agent and applicable beyond.
---

# Surgical 4-Pass Methodology · metodología multi-pase con ultrathink loop

## Principio rector

> La calidad surgical de un análisis NO viene de saber más. Viene de **mirar varias veces**.

Un informe profundo NO puede producirse en un solo pase. Esta es la secuencia.

## Pase 1 · Reconocimiento

**Objetivo**: entender QUÉ tienes delante antes de analizarlo.

Carga el dataset/documento/código. Identifica:
- Alcance (periodo cubierto · granularidad · número de entidades)
- Estructura (variables disponibles · tipos · valores faltantes · errores de codificación)
- Forma (¿es plano? ¿hay nested events? ¿hay texto libre además de métricas?)
- Distribución básica de cada variable clave

**Output del Pase 1**: 2 párrafos de "estado de la fuente" EN TU PENSAMIENTO. NO en el entregable. Esto es para ti, no para el cliente.

## Pase 2 · Análisis profundo

**Objetivo**: calcular/auditar/revisar TODO lo que sea aplicable. Generar borrador.

- Para análisis longitudinal: aplica las 25 dimensiones del skill `longitudinal-analysis-dimensions`
- Para audit de plan: aplica el checklist del skill `plan-audit-checklist`
- Para code review: aplica las prácticas estándar de revisión
- Genera todos los outputs derivados (plots, tablas, hallazgos)
- Escribe BORRADOR del entregable

## Pase 3 · ULTRATHINK · auto-auditoría (EL CRÍTICO)

**PARA. NO publiques.** Este es el pase que separa informes superficiales de quirúrgicos.

Pregúntate explícitamente:

### 5 preguntas del ultrathink loop

#### 1. ¿Qué dimensiones NO he calculado?

Lista las que faltan. Justifica por qué cada una "no aplica" — **y si dudas, calcúlala**.

La mayoría de las veces, "no aplica" es pereza intelectual. Si puedes calcularlo en <10 min, calcúlalo.

#### 2. ¿He vuelto a la fuente cruda?

Los datasets/documentos derivados pierden información. Si la fuente tiene texto libre (notas, comentarios, descripciones), reléelo. Busca:

- Menciones de dolor/lesión/molestia/fatiga (para gym)
- Mood, ánimo, contexto vital
- Justificaciones de pausas o cambios
- Anotaciones tipo "hoy no", "olvidé", "saltado"
- Cabeceras o etiquetas obsoletas que el sujeto sigue repitiendo
- Mención de protocolos/ciclos/fases que el sujeto cree estar siguiendo pero no se reflejan en datos
- Inconsistencias entre lo dicho y lo medido

**Regla**: si en Pase 2 no integraste texto crudo, casi seguro tienes 1-2 hallazgos invisibles en métricas derivadas.

#### 3. ¿Hay algún hallazgo que CONTRADIGA mi narrativa?

Si tu resumen dice "consolidación" pero ves regresión en ventanas recientes, la narrativa está mal. Si el primer informe (o el cliente, o el sentido común) dice X y los datos dicen no-X, **escribe no-X**.

Esta es la pregunta más incómoda y la más valiosa. Tu narrativa del Pase 2 es la "hipótesis preferida". Tu trabajo en Pase 3 es probar que está equivocada antes de publicarla.

#### 4. ¿He confundido artefacto con realidad?

- Cambios de unidad de medida
- Cambios de variante (barra → mancuerna · libre → Smith)
- Cambios de instrumento (báscula vieja → nueva)
- Cambios de notación
- Cambios de criterio de inclusión

Toda "regresión brusca" tiene que ser auditada contra el supuesto de continuidad de medición. La mayoría de "caídas dramáticas" son artefactos, no realidad.

#### 5. ¿He distinguido entre "abandonado", "pausado" y "decay natural"?

- Un ejercicio con 0 sesiones en 60 días NO es lo mismo que uno con frecuencia decreciente
- Una métrica que cae después de una pausa NO es lo mismo que una métrica que cae sin causa
- Un PR no batido en 6 meses NO necesariamente es un plateau (puede ser que el sujeto cambió prioridades)

Diferenciar estos tres requiere mirar la **estructura temporal**, no solo el último valor.

### Decisión post-Pase 3

| Resultado del Pase 3 | Acción |
|---|---|
| Revela 3+ hallazgos nuevos significativos | Vuelve al Pase 2 con esos hallazgos integrados |
| Revela 0-2 hallazgos marginales | Pasa al Pase 4 |

**Importante**: el Pase 3 NO se ejecuta una sola vez. Se repite hasta que un loop completo NO genere hallazgos nuevos significativos.

## Pase 4 · Síntesis final

**Objetivo**: reescribir el entregable integrando todo lo descubierto.

- Asegúrate de que la narrativa principal refleje los hallazgos del Pase 3, NO la impresión inicial del Pase 1
- **Si la narrativa cambió radicalmente entre pases, NÓMBRALO en el documento**. El lector merece saber qué pensabas antes y qué piensas ahora. Eso es honestidad metodológica.
- Cada hallazgo numerado con número específico, fecha específica, acción específica
- Cero "considera mejorar X"
- Cada plot y tabla con interpretación adyacente

## Criterio de parada

Te puedes considerar terminado SOLO cuando:
- [ ] Has completado los 4 pases
- [ ] El Pase 3 ha sido ejecutado al menos UNA vez sin generar hallazgos nuevos significativos
- [ ] Cada hallazgo de tu lista final tiene número específico + fecha específica + acción específica
- [ ] El entregable contiene al menos 3 hallazgos que un análisis superficial NO habría detectado
- [ ] Has nombrado al menos 1 artefacto de medición que distorsionaría conclusiones ingenuas

Si alguno NO se cumple: NO entregues. Vuelve al Pase 3.

## Aviso al usuario entre Pase 2 y Pase 3

Para honrar el proceso y reducir ansiedad del usuario:

> "He completado el primer pase de profundidad. Antes de entregar, voy a ejecutar un ultrathink loop para auditar qué dimensiones quedan por explorar."

Esto declara explícitamente que estás iterando. El usuario entiende que el extra tiempo NO es lentitud, es metodología.

## Trigger frase del usuario

Si el usuario pregunta:
> "¿está todo, quirúrgicamente, y todo lo posible que se puede obtener y exprimir?"

(o variantes: "¿lo has exprimido todo?", "¿no falta nada?", "¿de verdad está completo?")

Esta NO es pregunta retórica. Es un **trigger para auto-auditarte**:

1. **Si te quedan dimensiones sin explorar**: nombrarlas y proponer ejecutarlas antes de finalizar
2. **Si el texto crudo no se ha releído**: hacerlo ahora
3. **Si los 4 pases están completos y un nuevo loop no aportaría >2 hallazgos**: decirlo directamente y entregar

Responde HONESTAMENTE. Nunca "sí, todo está perfecto" si no has hecho el último ultrathink loop.

## Aplicación más allá de análisis longitudinal

Aunque este skill nació para informes quirúrgicos, la metodología 4 pases aplica a:

### Auditoría de plan de entrenamiento (`plan-auditor`)

- Pase 1: ¿qué tipo de plan? ¿qué documentos? ¿cuántas semanas?
- Pase 2: aplica `plan-audit-checklist` completo (math, fechas, refs, consistencia)
- Pase 3: ¿qué tabla NO he revisado? ¿hay inconsistencia entre día-card y tabla? ¿hay fechas que no he cruzado contra calendar real?
- Pase 4: lista priorizada de hallazgos con fix

### Code review

- Pase 1: ¿qué hace este código? ¿cuáles son los puntos de entrada?
- Pase 2: revisión línea a línea (correctness, security, performance)
- Pase 3: ¿qué edge cases no he considerado? ¿qué tests faltan? ¿qué pasaría si X falla?
- Pase 4: lista de hallazgos con severidad

### Document review (manuales, prompts, especificaciones)

- Pase 1: ¿qué pretende este documento? ¿quién lo lee?
- Pase 2: revisión sección por sección (claridad, completitud, consistencia)
- Pase 3: ¿qué pregunta del lector NO está contestada? ¿qué término técnico no se definió? ¿qué referencia está rota?
- Pase 4: lista de mejoras + documento revisado

## Anti-patrones

- ❌ **Declarar terminado tras 1 solo pase**. Casi nunca es suficiente.
- ❌ **Pase 3 como "revisión rápida"** en lugar de auditoría sistemática
- ❌ **Mantener narrativa Pase 1 cuando Pase 3 la contradice**
- ❌ **Tratar el texto crudo como secundario** ("solo son notas, no tienen métricas")
- ❌ **Confundir "cambio de instrumento" con "cambio real"**
- ❌ **Hallazgos sin acción** ("hay un problema con X" sin proponer qué hacer)
- ❌ **No avisar al usuario del ultrathink loop** (parece que estás tardando · pierdes confianza)
