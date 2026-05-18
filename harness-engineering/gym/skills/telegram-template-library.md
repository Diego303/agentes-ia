---
name: telegram-template-library
description: Invoke when building or auditing the full library of Telegram (or any chat-based) tracking templates for a multi-month training macro. Defines the template families (pre-session, post-session, weekly close, deload, test, pre-vacation, during-vacation, post-vacation, RECON, daily check-in) with structure, fields, and progression conventions. Skill general — adapta los valores numéricos al perfil.
---

# Telegram Template Library · biblioteca completa de plantillas de tracking

> Este skill define la **estructura** de plantillas. Los valores numéricos (PRs, fechas, %) son del perfil de referencia (ver `[[manual-expansion-rules]]`). Adapta al usuario real antes de aplicar.

## Propósito

Una bitácora consistente es la diferencia entre un macro que se ejecuta y uno que se pierde. La plantilla cumple tres funciones:

1. **Recordar al ejecutor qué medir** (no se olvida campo crítico)
2. **Producir dataset analizable** (mismo formato → análisis longitudinal posible más tarde con `[[longitudinal-analysis-dimensions]]`)
3. **Reducir fricción** (copy-paste, no escritura libre)

## Cabecera mental fija (en todas las plantillas)

Cada plantilla empieza con cabecera de 4-6 líneas que el ejecutor NO debe modificar entre semanas:

```
Día __ - mes - año · Sem N · NOMBRE DE LA SESIÓN
PR lift1: X kg (fecha) · Target macro: Y kg
PR lift2: X kg (fecha) · Target: Y kg
[PR lift3, lift4...]
Sueño noche previa: __ h
Hora inicio: __:__
Sensación pre: __/10
```

**Reglas de la cabecera:**
- PRs y targets HARDCODED (no se actualizan hasta el test final)
- Sueño en horas decimales (6,5 no "6h 30m")
- Sensación 1-10 obligatoria · es el dato más predictivo del rendimiento

## Las 11 familias de plantillas

| # | Familia | Cuándo aplica | Frecuencia |
|---|---|---|---|
| 1 | Test diagnóstico (sem 0) | Inicio de macro | 3 sesiones |
| 2 | Sesión normal · LUN (upper heavy) | Plan corriente | semanal |
| 3 | Sesión normal · MIÉ (lower) | Plan corriente | semanal |
| 4 | Sesión normal · VIE (upper volume) | Plan corriente | semanal |
| 5 | Cierre semanal (domingo) | Cada domingo | semanal |
| 6 | Pre-disrupción (última sesión antes de pausa) | Antes de vacaciones/viaje | puntual |
| 7 | Chequeo diario en disrupción | Cada día sin gym | diario en pausa |
| 8 | Sesión BW (bodyweight) en disrupción | Cada 2-3 días de pausa | puntual |
| 9 | Alerta vuelta (último día disrupción) | Día previo a retomar | puntual |
| 10 | RECON técnico (post-pausa fase 1) | Primera semana post-vacación larga | 2-3 sesiones |
| 11 | RECON ramp (post-pausa fase 2) | Segunda semana post-vacación | 3 sesiones |
| 12 | Taper pre-test (semana antes del test) | sem N-1 del macro | 3 sesiones |
| 13 | Día del test | Día del test | puntual |
| 14 | Post-test (semana 17 deload) | Tras test | 2-3 sesiones |
| 15 | Chequeo matinal diario | TODOS los días | diario |

## Templates de referencia · estructura abstracta

### Template 1 · Test diagnóstico sem 0

```
[Cabecera fija]

CALENTAMIENTO
[movilidad específica al lift]
[barra vacía + ramp progresivo a saltos definidos]

EJ1: [LIFT PRINCIPAL] · TEST 1RM REAL
Escalones de [X] kg buscando serie 4-6 reps RPE 9
__ kg × __ reps · RPE __
__ kg × __ reps · RPE __
__ kg × __ reps · RPE __
1RM calculado = peso × (1 + reps/30) = __ kg

EJ2-N: [ACCESORIOS · mantenimiento RPE 7]
__ kg × N

CIERRE
Cansancio: __/10
Notas: __
```

### Template 2 · Sesión normal LUN (upper heavy con AMRAP)

```
[Cabecera fija]

CALENTAMIENTO (8 min)
[movilidad + ramp]

EJ1: [LIFT PRINCIPAL] · 3+1*  (3 fijos + 1 AMRAP)
[peso fijo del plan]
Serie 1: __ kg × __ reps · RPE __
Serie 2: __ kg × __ reps · RPE __
Serie 3: __ kg × __ reps · RPE __
AMRAP: __ kg × __ reps · RPE __
Target AMRAP: ≥ __ reps
Resultado vs target: [en target / +N / -N]

EJ2: [SECUNDARIO] · 3×N RPE 7-8
...

[Resto de accesorios]

CIERRE
Duración total: __ min
Cansancio post: __/10
Notas técnicas: __
Notas dolor/molestia: __
```

### Template 3 · Cierre semanal (domingo)

```
═══════════════════════════════════════
CIERRE SEMANAL · Sem __
═══════════════════════════════════════
Sesiones completadas: __/3
Sesiones saltadas: __ · razón: __

AMRAP del lift principal:
  Lun: __ × __ (target __)
  Mié: __ × __ (target __)
  Vie: __ × __ (target __)

Resultado global: [target / over / under]
Acción próxima semana: [seguir plan / repetir / bajar 5%]

Sueño medio: __ h
Sensación media pre: __/10
Cansancio medio post: __/10

Eventos contextuales: __
Molestias activas: __
Decisión adherencia: __
```

### Template 4 · Pre-disrupción (última sesión antes de pausa)

```
[Cabecera fija + tag "ÚLTIMA PRE-[disrupción]"]

[Sesión normal completa según día]

CIERRE PRE-DISRUPCIÓN
Última sesión antes de [N] días de pausa
Plan en disrupción: [BW · cardio · descanso · híbrido]
Día de vuelta: [fecha]
Plan vuelta: [RECON-1 / directo / consultar antes]
Compromiso: __
```

### Template 5 · Chequeo diario en disrupción

```
═══════════════════════════════════════
CHEQUEO DIA __ DE __ EN [DISRUPCIÓN]
═══════════════════════════════════════
Fecha: __
Sueño: __ h
Pasos ayer: __
Comidas: [bien / regular / mal]
Hidratación: __/10
Movilidad/activación hoy: [SÍ/NO]
Sesión BW programada hoy: [SÍ/NO] → si sí, abrir plantilla BW
Sensación general: __/10
Notas: __
```

### Template 6 · Sesión BW vacaciones

```
[Cabecera adaptada · sin lift principal]

CALENTAMIENTO BW (5 min)
Movilidad articular completa

CIRCUITO BW · 3 rondas
Push-ups: __ reps
Squats: __ reps
Hip thrust BW: __ reps
Plancha: __ seg
Filas invertidas / dominadas: __ reps

CIERRE
Duración: __ min
Sensación: __/10
Sueño noche previa: __ h
```

### Template 7 · Alerta vuelta (último día disrupción)

```
═══════════════════════════════════════
ALERTA · VUELTA AL GYM MAÑANA / EN __ DÍAS
═══════════════════════════════════════
Día de vuelta: __
Sesión de vuelta: [RECON-1a / 1b / 2 / normal]
% del peso normal: __ %
Reps prescritas: __

CHECK PRE-VUELTA:
- Sueño últimas 3 noches: __ __ __ horas
- Molestia/dolor: [ninguna / leve / moderada]
- Estrés vital: __/10
- Pasos diarios mantenidos: [SÍ/NO]

Decisión final: [proceder / aplazar 1 día / RECON extra suave]
```

### Template 8 · RECON técnico (post-pausa fase 1)

```
[Cabecera + tag "RECON-Xa TÉCNICO"]

CALENTAMIENTO EXTENDIDO (10 min)
[más movilidad de lo normal]

EJ1: [LIFT PRINCIPAL] · técnica únicamente al -25% del último peso normal
[peso reducido] kg × 4 × 5 reps · RPE objetivo: 6
Notas técnicas obligatorias por serie: __

EJ2-N: accesorios a -25%
__ kg × N

CIERRE
Sensación técnica: [recuperada / mejorando / rota]
Decisión próxima sesión: [seguir RECON / acelerar a 1b]
```

### Template 9 · RECON ramp (post-pausa fase 2)

```
[Cabecera + tag "RECON-Xb RAMP"]

CALENTAMIENTO (8 min)

EJ1: [LIFT PRINCIPAL] · ramp -15% → -10%
[peso reducido] kg × N reps · RPE __
Resultado vs sensación: __

[Resto progresivo]

CIERRE
¿Listo para sem normal próxima? [SÍ/NO/parcial]
Decisión: [retomar plan / +1 RECON / consultar]
```

### Template 10 · Taper pre-test

```
[Cabecera + tag "TAPER SEM __ pre-test"]

Sesión LIGERA · -20-30% del peso normal
EJ1: 2-3 sets máximo · RPE 6
EJ2-3: 1-2 sets accesorio · RPE 6-7

CIERRE
Sensación: __/10
Energía para test: __/10
Plan día test: [confirmado / ajustar]
```

### Template 11 · Día del test

```
[Cabecera + tag "TEST DAY · [LIFT]"]

DESAYUNO/COMIDA: __ (qué + hora)
CAFEÍNA: __ mg a las __

LLEGADA GYM: __:__

CALENTAMIENTO (15 min)
[movilidad + ramp con saltos definidos]

INTENTOS DEL TEST
Intento 1 (87,5% target): __ kg × 1 · [SÍ/NO]
Intento 2 (92,5% target): __ kg × 1 · [SÍ/NO]
Intento 3 (target): __ kg × 1 · [SÍ/NO]

PR DÍA: __ kg
PR PREVIO: __ kg
DELTA: +/- __ kg

NOTAS
Técnica intento fallido (si aplica): __
Sensación: __
Decisión próximo macro: __
```

### Template 12 · Chequeo matinal diario (universal)

```
═══════════════════════════════════════
MATINAL · [FECHA]
═══════════════════════════════════════
FC reposo: __ bpm
Sueño: __ h (continuo/interrumpido)
Despertar: [fácil / costoso]
Sensación general: __/10
Hidratación primera hora: __ ml
Plan día: [gym / descanso / actividad]
Si gym: lift principal = __
Notas: __
```

## Reglas de la biblioteca

1. **Estructura > contenido**. El skill define la estructura. Los pesos, fechas, ejercicios concretos vienen del plan del usuario.

2. **Copy-paste antes que escritura libre**. Una plantilla en blanco genera ansiedad y datos inconsistentes. Templates fijos generan adherencia.

3. **Cabecera fija nunca cambia entre semanas** (excepto al alcanzar nuevo PR · y solo si el plan lo permite).

4. **Campos obligatorios vs opcionales**:
   - **Obligatorios**: sueño, sensación pre, hora, peso×reps×RPE de cada serie del lift principal
   - **Opcionales**: notas técnicas, dolor/molestia (rellenar solo si hay)

5. **Plantilla universal diaria** (matinal) debería completarse incluso días sin gym · es el dato más útil retrospectivamente

## Anti-patrones

- ❌ Plantillas con 30 campos · el ejecutor abandona el tracking
- ❌ Cambios de plantilla entre semanas (rompe análisis longitudinal)
- ❌ Campos "subjetivos" sin escala (`mood: __` sin /10)
- ❌ Omitir hora del día (crítico para cronobiología · ver `[[longitudinal-analysis-dimensions]]` §4.7)
- ❌ Tracking solo de PRs (perdés tendencias y volumen)
- ❌ Cabecera mental con PRs obsoletos · el sujeto los arrastra meses y se desconectan de su 1RM real

## Sinergia con otros skills

- `[[telegram-tracking]]` · convenciones de notación (peso×reps, mancuernas/lado, etc.)
- `[[longitudinal-analysis-dimensions]]` · análisis del dataset resultante
- `[[recon-protocols]]` · protocolos RECON específicos
- `[[vacation-bw-routine]]` · rutina BW para Template 6
- `[[test-day-protocol]]` · protocolo completo del Template 11
- `[[pre-session-mental-prep]]` · qué hacer en los 5 min previos a abrir la plantilla

## Aplicación

Cuando `manual-html-builder` construya §13 Cabecera Telegram, invocar este skill para generar las plantillas relevantes a la estructura del plan. Cuando `surgical-report-builder` analice una bitácora, conocer estas plantillas le ayuda a parsear el texto crudo (§4.20 del catálogo de dimensiones).
