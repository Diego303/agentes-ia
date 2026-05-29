---
name: deload-by-session
description: Invoke when deciding mid-week if a single session should be converted to a "deload session" (rather than a full deload week). Different from sleep-debt protocol — applies when you arrive at the gym and sensation/warm-up signal poor recovery. Defines criteria, single-session protocol (volume -40%, intensity -15%, RPE 6, no AMRAP), and rule "max 2 single-session deloads per macro before triggering full deload week".
---

# Deload by Session · sesión-única deload

> **Nota · skill 100% general aplicable a cualquier lifter.**

## Concepto · entre sesión normal y semana deload completa

Hay un escalón intermedio que el harness no documentaba:

| Trigger | Respuesta |
|---|---|
| 1 noche mala aislada | Sesión normal con -1 serie + caffeine ajustada |
| Sensación pre <5/10 sin causa clara | **DELOAD DE SESIÓN** ← este skill |
| 2-3 noches malas en 7 días | Sesión técnica esa semana (ver `[[sleep-debt-protocol]]`) |
| 4+ noches malas | Pausa total semana (ver `[[sleep-debt-protocol]]`) |

El deload de sesión es la opción para "hoy NO estoy" pero "no llevo días así". Sustituye 1 sesión sin romper el bloque del macro.

## Diferencia con sleep-debt-protocol

| Aspecto | sleep-debt-protocol | deload-by-session |
|---|---|---|
| Trigger | Noches malas acumuladas | Sensación + warm-up + FC del día |
| Cuándo se decide | Antes de salir de casa (datos de sueño) | **Al llegar al gym** (post-warm-up) |
| Duración | Toda la semana | Solo HOY |
| Próxima sesión | Sigue el plan ajustado | Vuelve normal si lo del día ya pasó |

## Cuándo aplicar (criterios objetivos)

Cumplir **≥2 de estos**:

1. **Sensación pre <5/10** sin causa clara (no fiesta, no enfermedad)
2. **FC reposo +5 bpm vs tu baseline** ese día (ver `[[daily-morning-check]]`)
3. **Warm-up al 50% del 1RM se siente pesado** (debería sentirse muy fácil)
4. **Dolor articular leve persistente** (no agudo · si agudo: aplica `[[exercise-substitution-matrix]]`)
5. **Mental: cero ganas tras 5 min calentamiento** (no es solo "pereza", es "no responde el cuerpo")

## Cómo decidir DURANTE el warm-up (no antes)

**Regla**: no canceles antes de hacer el warm-up. La sensación pre subjetiva miente más que el cuerpo.

Protocolo de decisión:

1. **Min 0-5**: warm-up estándar normal
2. **Min 5-10**: warm-up al 50-60% del 1RM (work set)
3. **Pausa de auto-evaluación**: ¿cumplo ≥2 criterios?
4. **SÍ → deload de sesión** (aplicar protocolo)
5. **NO → sesión normal** (sigue tu plan)

> Decisión post-warm-up evita los falsos positivos de "no me apetece pero me pondré bien al moverme".

## Protocolo de deload de sesión

### Estructura

```
W (8 min) Warm-up extendido (igual al estándar)
A Lift principal: 3 sets × 5 reps al -15% del prescrito · RPE 6 · SIN AMRAP
B-C Secundarios: -10% peso · RPE 7 · series normales
OMITE: D, E, F (accesorios)
M (10 min) Mobility cierre extendido
```

Tiempo total: ~35-40 min (vs 65-75 normal).

### Comparación numérica

Si la sesión normal era:
- A bench: 4 sets × 5 reps al 80% del 1RM (work + AMRAP)
- B remo: 4 sets × 6 al 70%
- C-F: ~12 sets más de accesorios

Deload de sesión:
- A bench: 3 × 5 al **65%** (= 80% - 15%) · sin AMRAP
- B remo: 3 × 6 al **65%** (= 75% × 0.90)
- C remo o press: 2 × 8 al 65%
- OMITE D-F

### Documentar

En la plantilla Telegram:
```
[fecha] · Sem N · DELOAD DE SESIÓN [razón]
A bench: peso × reps × RPE
B remo: peso × reps × RPE
C ___
Sensación post: X/10
```

La razón es importante: "FC +6", "sensación pre 4", "warm-up pesado", "rodilla tirante".

## Regla del máximo 2 por macro

**2 deloads de sesión por macro (17 sem) = aceptable**.
**3+ deloads de sesión = señal de algo más grande**:
- O necesitas deload de semana completo
- O sleep/comida/estrés vital están comprometiendo recuperación crónicamente
- O el volumen del plan está cerca de tu MRV (ver `[[volume-landmarks-mev-mav-mrv]]`)

### Acción si llegas a 3

Tras el 3er deload de sesión:
1. Revisar sueño últimas 2 sem (`[[daily-morning-check]]`)
2. Revisar nutrición · estás en superávit real?
3. Revisar contexto vital · estrés laboral, familiar nuevo
4. Si 1 causa identificable + temporal → continúa plan + ajusta lo identificado
5. Si 2+ causas O sin causa clara → próxima sem completa = **deload completo** (no esperes a la programada)

## Errores típicos

- ❌ **Usar deload de sesión por pereza** ("no me apetece" sin warm-up)
- ❌ Saltarse el warm-up para no tener que decidir
- ❌ Volver normal próxima sesión sin reflexión (si fue real, ajusta sueño/comida)
- ❌ Convertir deload de sesión en "casi sesión normal" subiendo pesos
- ❌ Sin documentar la razón (pierdes patrón temporal)
- ❌ Acumular 5+ por macro sin replantar plan

## Sinergias

- `[[sleep-debt-protocol]]` · si llevas 3+ noches malas, NO es deload de sesión · es sleep-debt directo
- `[[deload-week-design]]` · si llevas 3+ deloads de sesión, próxima sem = deload completo
- `[[troubleshooting-catalog]]` · §C4 Energía <4/10 trigger común
- `[[daily-morning-check]]` · alimenta los criterios objetivos
- `[[mental-game-plateau]]` · si causa es mental no física
- `[[volume-landmarks-mev-mav-mrv]]` · 3+ deloads = señal volumen excesivo

## Aplicación

- `coach-realtime` · invocar cuando usuario reporta "no me apetece" / "me siento raro"
- `manual-html-builder` · §09 Autorregulación incluir esta categoría
- `troubleshooting-catalog` · §C4 enlazar a este skill
- `sleep-debt-protocol` · línea 18 (1 sesión técnica) sustituir por referencia a este skill
