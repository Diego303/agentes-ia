---
name: disruption-adaptation-framework
description: Invoke when a known disruption (vacation, scheduled surgery, paternity leave, travel work block) interrupts a training macro and the plan needs structural reorganization. Defines the 5-step framework (classify disruption → decide absorb vs shift → reorganize calendar → insert RECON → recompute test date) with decision rules and templates. General — apply to any duration of disruption.
---

# Disruption Adaptation Framework · metodología general para adaptar planes a disrupciones

## Propósito

Una disrupción conocida (vacaciones planificadas, cirugía agendada, paternidad esperada, viaje laboral largo) NO es una crisis si se planifica con antelación. Este skill define el meta-protocolo para reorganizar un macro de N semanas alrededor de una o varias disrupciones.

NO es para disrupciones imprevistas (enfermedad súbita, lesión aguda) · ésas las cubre `[[troubleshooting-catalog]]`.

## Cuándo aplicar

- Disrupción **conocida con antelación ≥4 semanas**
- Disrupción de **duración ≥7 días sin gym**
- Macro **>10 semanas** (en macros cortos, mejor pausar y recomenzar)
- **Más de una disrupción** en el mismo macro (caso compuesto)

## Los 5 pasos

### Paso 1 · Clasificar la disrupción

| Duración | Categoría | Impacto típico |
|---|---|---|
| 3-6 días | Micro-pausa | Cero impacto programático · seguir plan |
| 7-10 días | Pausa corta | RECON ligero al volver · 0 reajuste calendar |
| 11-14 días | Pausa media | RECON completo · posible 1 sem de absorción |
| 15-21 días | Pausa larga | Reajuste calendar · RECON-1 + RECON-2 |
| >21 días | Macro disrupción | Replantear bloques afectados |

Para **disrupciones múltiples** (e.g., 2 vacaciones en mismo macro): aplicar el más severo + considerar acumulación.

### Paso 2 · Decidir absorber vs desplazar

Dos estrategias:

#### Estrategia A · Absorber (recomendada si posible)

- Las semanas afectadas se reorganizan internamente al macro original
- El test final mantiene su fecha
- Se reemplazan sesiones de acumulación normal por sesiones RECON
- Aplica si: disrupción ≤14 días Y queda ≥4 semanas de plan post-disrupción

#### Estrategia B · Desplazar test

- El test se mueve N semanas hacia adelante (N = días disrupción / 7, redondeado arriba)
- Las semanas del plan original se mantienen, solo el calendar se corre
- Aplica si: disrupción >14 días O queda <4 semanas post-disrupción O es disrupción múltiple

#### Estrategia mixta (común en disrupciones múltiples)

- Primera disrupción absorbida
- Segunda disrupción desplaza
- Test recalibrado al nuevo calendar

**Regla de decisión rápida**:
- 1 disrupción ≤10 días → Absorber
- 1 disrupción 11-21 días → Mixta
- 1 disrupción >21 días → Desplazar (+ replantear)
- 2 disrupciones consecutivas → Mixta (primera absorbe, segunda desplaza)
- 3+ disrupciones → Replantear macro completo

### Paso 3 · Reorganizar el calendario

Para cada bloque del macro, decidir su nuevo lugar:

```
Macro original (sem 1-17):
[ACUM1 4sem] [DELOAD 1] [ACUM2 4sem] [DELOAD 2] [PICO 4sem] [TEST] [POST]

Disrupción en sem 8 (14 días):
[ACUM1] [DELOAD 1] [ACUM2 parcial 3sem] [PAUSA 14d] [RECON-1] [ACUM2b] [DELOAD 2] [PICO] [TEST] [POST]
                                                    └────── reemplaza 1 sem ──────┘

→ Test 2 semanas más tarde si no se puede absorber el RECON
```

**Reglas estructurales**:
- NUNCA pegar dos deloads · si una pausa cae en deload programada, considera la pausa como deload de hecho y elimina la programada
- NUNCA empezar bloque PICO con RECON sin completar (mínimo 2 semanas de RECON antes del pico)
- El TEST nunca cae <3 semanas después de una pausa >10 días

### Paso 4 · Insertar protocolos RECON

Según la duración de la pausa, decidir RECON:

| Pausa | RECON requerido |
|---|---|
| 7-10 días | RECON-1 ligero (1-2 sesiones, peso -15%, sin AMRAP) |
| 11-14 días | RECON-1 completo (2 sesiones técnicas -25% + 3 sesiones ramp -15→-10%) |
| 15-21 días | RECON-1 + RECON-2 (1 sem técnica + 1 sem ramp + 1 sem -10%) |
| >21 días | RECON-1 + RECON-2 + 1 sem extra acumulación suave |

Ver detalle en `[[recon-protocols]]`.

### Paso 5 · Recomputar fecha del test

Dependiendo de estrategia escogida:

**Si Absorber**: test queda en fecha original. Documentar que el bloque PICO tendrá 1 sem menos de acumulación efectiva (asumir reducción 2-5% en target).

**Si Desplazar**:
```
Nueva_fecha_test = Fecha_test_original + (Días_pausa + Días_RECON_extra)
```

**Si Mixta**: desplazamiento parcial. Calcular caso a caso.

**Validar** la nueva fecha contra:
- Día de la semana (test debe caer en día programado · usar `[[calendar-arithmetic]]`)
- Conflictos vitales (no test en cumpleaños, mudanza, evento social)
- Que el macro siguiente tenga inicio coherente (>=10 días post-test)

## Templates de comunicación al sujeto

### Pre-disrupción (último día antes de pausa)

```
ÚLTIMA SESIÓN PRE-[DISRUPCIÓN] · planning

Días sin gym: __
Plan durante: [BW · cardio · descanso · híbrido]
Día de vuelta: [fecha · día sem]
Vuelta esperada: [RECON-1 ligero / RECON-1 completo / etc.]

Fechas reajustadas del macro:
  Fin bloque actual: [original] → [nueva]
  Test: [original] → [nueva]
  Macro 2 inicio: [original] → [nueva]
```

### Durante disrupción (chequeo diario · ver `[[telegram-template-library]]`)

Templates de chequeo diario y de sesión BW si aplica.

### Vuelta de disrupción (primer día post-pausa)

```
VUELTA AL GYM · día 1 post-[DISRUPCIÓN]

Plan hoy: RECON-Xa [técnico/ramp]
Peso lift principal: __ kg (-__% del último peso normal)
Series: __ × __
RPE objetivo: 6 (NO empujar)

Esperado: sensación rara, pesos cómodos. Es normal.
NO PR. NO AMRAP. NO acelerar.

Próxima sesión: [fecha] · [RECON-Xb / normal]
Test reajustado: [fecha nueva]
```

## Casos especiales

### Caso A · Disrupciones recurrentes (e.g., viaja 1 sem/mes)

NO aplicar RECON cada mes. En su lugar:
- Diseñar macro asumiendo 3 sesiones/sem en lugar de 4 (frecuencia base reducida)
- Convertir 1 sem/mes en sem de "BW + cardio" semi-programada
- Aceptar progresión más lenta (~70% de macro sin disrupciones)

### Caso B · Cirugía / lesión planificada

- Pre-cirugía: 2 semanas de "carga residual" (mantener fuerza sin estrés articular en zona afectada)
- Durante recuperación: protocolo médico (NO programación gym)
- Post-recuperación: replantear macro completo desde cero. NO retomar el anterior.

### Caso C · Mudanza / cambio de gym

- 0-3 días sin gym: sin impacto
- Cambio de gym requiere semana de "calibración" (mismos pesos pero -10% para identificar equivalencias máquinas)
- Documentar diferencias (banco distinto = ajuste arco, etc.)

### Caso D · Paternidad / cambio vital mayor

- NO es disrupción · es cambio de régimen
- Replantear macro asumiendo sueño reducido permanente (-1 sem/macro)
- Volumen recuperable cae ~20% · ajustar series totales
- Frecuencia puede bajar a 2 sesiones/sem temporal

## Anti-patrones

- ❌ Replantear macro completo por una pausa de 1 semana
- ❌ Saltar RECON "porque me siento bien" tras 14 días sin gym
- ❌ Pegar dos deloads consecutivas (programada + de hecho)
- ❌ Test inmediatamente después de RECON sin acumulación
- ❌ Improvisar reajuste al volver del viaje sin haberlo planificado antes
- ❌ Cambiar el target del macro durante la disrupción (mover fechas SÍ, mover targets NO sin nuevo análisis)
- ❌ Esconder al sujeto que el test se retrasa (transparencia es adherencia)

## Sinergia con otros skills

- `[[recon-protocols]]` · protocolos específicos RECON-1 y RECON-2
- `[[vacation-bw-routine]]` · rutina durante la disrupción
- `[[calendar-arithmetic]]` · cálculo de días, semanas, día-de-semana
- `[[troubleshooting-catalog]]` · disrupciones IMPREVISTAS
- `[[telegram-template-library]]` · plantillas pre/durante/post disrupción
- `[[coaching-principles]]` · §10 Adherencia · disrupción bien manejada > macro perfecto roto

## Aplicación por agente

- `plan-reajuster` · agente principal que invoca este skill
- `gym-plan-architect` · invoca este skill SI el usuario reporta disrupciones conocidas durante diseño del macro
- `coach-realtime` · referencia este skill si el usuario pregunta "qué pasa si me voy 2 semanas"
