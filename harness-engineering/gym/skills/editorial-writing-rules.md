---
name: editorial-writing-rules
description: Invoke when writing any editorial technical document (longitudinal report, audit, manual, deep analysis) that requires editorial quality without sacrificing rigor. The 5 rules of editorial writing — honesty without cruelty, mandatory specificity, editorial tone, every finding ends in action, the three hard truths. 100% general (no domain).
---

# Editorial Writing Rules · 5 reglas de escritura editorial

## Propósito

Un documento técnico puede ser preciso y aburrido (paper académico mediocre), preciso y panfletario (charla TED genérica), o preciso y editorial (revista técnica buena). El objetivo de este skill es producir el tercer tipo.

Estas reglas se aplican a:
- Informes longitudinales quirúrgicos (gym, finanzas, salud, telemetría)
- Auditorías de plan / código / documento
- Manuales operativos largos
- Análisis profundos de cualquier dataset

NO se aplican a: README breves, mensajes en chat, comentarios de código, especificaciones API.

## Las 5 reglas

### Regla 1 · Honestidad sin crueldad

**Enunciado**: si los datos contradicen una narrativa previa, cámbiala. Si un hallazgo es crítico, nómbralo. PERO equilibrio: por cada crítica, un reconocimiento de lo que funciona.

**Por qué**: el lector debe terminar con imagen completa, no demolido. Un informe que solo es crítica genera rechazo defensivo. Uno que solo celebra es inservible. La calidad surgical viene del equilibrio.

**Aplicación**:
- ❌ "Tu adherencia es vergonzosa, solo entrenas 3 veces por semana" 
- ❌ "Tu plan es perfecto, sigues progresando excelentemente"
- ✅ "Llevas 11 meses con 3 sesiones/sem · adherencia 87%, top decil. Pero el dato más relevante es otro: tus 12 últimas sesiones tienen RPE +2 sobre prescrito · estás progresando, pero a coste de fatiga acumulada que ya está pasando factura"

**Test**: si el documento se puede resumir solo en frases negativas O solo en positivas, está mal calibrado. Debe haber crítica Y reconocimiento Y matiz.

### Regla 2 · Especificidad obligatoria

**Enunciado**: cada afirmación lleva número, fecha, o porcentaje específicos. Cero adjetivos sin métrica.

**Por qué**: "estás estancado" es opinión. "Llevas 331 días sin superar 85 kg, tu PR del 17 jun 2025" es hecho. Solo lo segundo permite actuar.

**Aplicación**:

| Vago (NO) | Específico (SÍ) |
|---|---|
| Está estancado | Lleva 331 días sin superar 85 kg, PR del 17 jun 2025 |
| Hace muchas series | 26 series por sesión en 2025, top 4% del histórico |
| Mejoró bastante | +12 kg en bench y +18 kg en sentadilla en 14 meses |
| Sleep deficitario | Mediana 6,1 h/noche últimos 90 días vs target 7+ |
| Buena adherencia | 87% de sesiones planificadas ejecutadas (303 de 348) |

**Test**: si cualquier frase del informe se puede reescribir sin perder sentido cambiando un número por otro, el número estaba mal usado (era decoración, no evidencia).

### Regla 3 · Tono editorial · cadencia y restricción

**Enunciado**: prosa con cadencia (frases largas y cortas alternando). Tecnicismos cuando aporten · metáforas cuando aclaren. Italics para énfasis, NO para todo. `monospace` solo para números/comandos/IDs. Negrita estratégica (1-2 fragmentos por párrafo máximo).

**Por qué**: el lector recorre el documento con ritmo. Frases todas largas → mareo. Todas cortas → telegrama. La cadencia mantiene la atención.

**Aplicación**:

> ❌ "El sujeto ha realizado un total de 303 sesiones en el periodo analizado, alcanzando un volumen agregado de 6213 series válidas, lo que representa una distribución promedio de 20,5 series por sesión, con una desviación estándar significativa que se analiza a continuación en detalle."

> ✅ "303 sesiones. 6.213 series. Promedio: 20,5 por sesión. La varianza, sin embargo, cuenta otra historia."

**Test**: leer en voz alta. Si te quedas sin respiración, frases muy largas. Si suena a SMS, muy cortas. Si todas tienen la misma cadencia, monótono.

### Regla 4 · Cada hallazgo termina en acción

**Enunciado**: cada hallazgo numerado del informe termina con `Acción · [verbo específico] [objeto específico] [parámetro específico]`. Cero "considera mejorar X".

**Por qué**: hallazgo sin acción es entretenimiento. El lector cierra el informe pensando "interesante" y nada cambia. Con acción, el lector puede ejecutar mañana.

**Aplicación**:

| Vago (NO) | Accionable (SÍ) |
|---|---|
| Considera mejorar la dieta | Añadir 30g proteína whey post-entreno LUN/MIÉ/VIE durante 8 semanas |
| Trabajar más el core | Añadir 3×30s plancha al final del día de espalda, semanas 1-12 |
| Cuidar la postura | 5 min wall slides + band pull-aparts antes de cada sesión upper |
| Optimizar el sueño | Dejar móvil fuera del dormitorio + Magnesio 400mg 30 min pre-cama |
| Reducir gastos | Cancelar suscripciones 1, 2, 3 (€42/mes) antes del 30 jun |

**Test**: cada acción debe responder a tres preguntas — ¿qué hago? · ¿cuándo? · ¿durante cuánto?

### Regla 5 · Las tres verdades duras

**Enunciado**: el resumen ejecutivo siempre incluye tres hallazgos que **reformulan la comprensión** que el sujeto tenía. NO son los tres "más grandes" — son los tres que más cambian la narrativa.

**Por qué**: si el resumen confirma lo que el lector ya sabía, el informe ha fallado en su función esencial. El valor del análisis profundo es revelar lo invisible.

**Aplicación**:

> ❌ Verdades blandas (cosas que el lector ya sabe):
> 1. Llevas progresando bien
> 2. Tu adherencia es alta
> 3. Tu nutrición es decente

> ✅ Verdades duras (cosas que el lector NO sabía o subestimaba):
> 1. Tu bench rinde 11 kg menos a las 18h que a las 21h — y casi todas tus sesiones de bench las haces a 18h
> 2. Llevas 253 días sin tocar hip thrust — tu PR de junio 2025 ya no es válido como referencia
> 3. Tu adherencia es 87% global, pero solo 62% en sesiones de viernes — has perdido 18 sesiones de volumen que el plan asumía

**Test**: si las 3 verdades se las hubieras podido decir al sujeto en una conversación de café SIN haber hecho el análisis, no son verdades duras. Son tópicos.

## Reglas adicionales (corolarios)

### 5b · Cero "lo que sigue se analiza a continuación"

Auto-referencias procedimentales son ruido. Si la siguiente sección es lo que sigue, el lector lo verá. No necesita anuncio.

### 5c · Si la sección §1 dice X y §15 dice no-X, una de las dos está mal

El documento debe tener narrativa coherente. Contradicciones entre secciones revelan que el Pase 3 ultrathink no se ejecutó (ver `[[surgical-4-pass-methodology]]`).

### 5d · Vocabulario emocional preciso, no decorativo

"Preocupante", "alarmante", "interesante" sin métrica → eliminar. Con métrica → conservar solo si añaden información que el número solo no comunica.

### 5e · Plot caption ≠ "evolución de X"

Cada figcaption debe contar una historia o señalar el dato relevante. "Evolución del bench 2023-2026" es etiqueta. "Bench progresa lineal 2023-2024, plateau abrupto jun 2024 coincidiendo con cambio de gym, recuperación parcial desde feb 2026" es figcaption editorial.

## Anti-patrones

- ❌ Adjetivos sin números ("notable", "significativo", "considerable")
- ❌ Verbos pasivos cuando hay agente claro ("fue observado que..." → "el dato muestra...")
- ❌ Conclusiones que repiten introducción
- ❌ Recomendaciones genéricas ("optimiza", "mejora", "trabaja en")
- ❌ Frases compuestas con 3+ subordinadas
- ❌ Pseudo-personalización ("como persona disciplinada que eres...")
- ❌ Negrita en >2 fragmentos por párrafo
- ❌ Italics en frases enteras (es decoración, no énfasis)
- ❌ Disclaimers académicos ("este análisis tiene limitaciones inherentes a la naturaleza del dataset...")
- ❌ Verdades blandas en §01 resumen ejecutivo

## Checklist pre-entrega

Antes de declarar un informe/manual/auditoría terminado:

- [ ] Cada hallazgo numerado tiene número, fecha o %, y acción específica
- [ ] El resumen ejecutivo contiene 3 verdades duras (no obvias)
- [ ] Hay equilibrio entre crítica y reconocimiento (no monolítico)
- [ ] Frases varían en longitud · cadencia editorial
- [ ] Negrita usada con restricción (1-2 por párrafo)
- [ ] Italics solo para énfasis verdadero
- [ ] Cero adjetivos sin métrica
- [ ] Cero "considera mejorar X" en recomendaciones
- [ ] Plot captions son editoriales, no etiquetas
- [ ] No hay contradicciones entre secciones

## Sinergia con otros skills

- `[[surgical-4-pass-methodology]]` · el Pase 4 (Síntesis) aplica estas 5 reglas en la reescritura final
- `[[surgical-report-structure]]` · define qué secciones llevan qué tipo de hallazgo
- `[[manual-expansion-rules]]` · cubre reglas similares para manuales operativos (no informes)
- `[[longitudinal-analysis-dimensions]]` · provee los hallazgos que se reescribirán con estas reglas

## Aplicación por agente

- `surgical-report-builder` · invoca obligatorio en Pase 4
- `plan-auditor` · invoca al redactar la lista de hallazgos
- `manual-html-builder` · invoca para texto narrativo (no para tablas/cards)
