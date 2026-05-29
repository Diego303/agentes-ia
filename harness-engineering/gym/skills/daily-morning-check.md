---
name: daily-morning-check
description: Invoke when designing or applying the morning recovery check (60 seconds at wake-up). Consolidates FC reposo, hours of sleep, sleep continuity, mental wake-up test, and subjective sensation into ONE protocol with one decision rule. Replaces fragmented mentions in sleep-debt-protocol, telegram-tracking, recovery-optimizer. General · adapta umbrales a tu baseline personal de 30 días.
---

# Daily Morning Check · chequeo recuperación 60s al despertar

> **Nota · skill 100% general aplicable a cualquier humano.** Los umbrales son **relativos a tu baseline** · construye 30 días de datos antes de actuar sobre desviaciones.

## Por qué importa

Un check de 60 segundos al despertar **predice mejor el día que cualquier wearable caro**. Captura:
- Estado del sistema nervioso (FC reposo)
- Calidad real del sueño (horas + continuidad subjetiva)
- Predisposición psicológica (sensación 1-10)
- Recuperación tisular (test mental despertar)

**Sin este check**, decides la sesión por "cómo te sientes al llegar al gym" · que ya está sesgado por cafeína, comida, contexto.

## El protocolo de 60 segundos

Hacer **antes** de levantarte de la cama · idealmente sentado o tumbado al despertar.

### Paso 1 · FC reposo (30 segundos)

1. Sentado o tumbado, sin moverte
2. Espera 60s desde abrir ojos para que el cuerpo se asiente
3. Pulso con dos dedos en muñeca o lateral cuello
4. Cuenta 30 segundos × 2 = bpm
5. **Anota**

### Paso 2 · Horas + continuidad (15 segundos)

- Horas dormidas (en decimal: 6,5 no "6h 30m")
- Continuidad 1-10:
  - 10 = sin despertarme nada
  - 7-8 = 1-2 despertares breves
  - 5-6 = 3+ despertares o uno largo
  - <5 = noche fragmentada

### Paso 3 · Test mental despertar (10 segundos)

Pregúntate honestamente:

> "¿Abro los ojos pensando **ya está** o **todavía me quedaba**?"

- **"Ya está"** → sueño consolidado · cuerpo dice "suficiente"
- **"Todavía me quedaba"** → deuda · el cuerpo quería más

Este es el predictor más sensible y más ignorado.

### Paso 4 · Sensación 1-10 (5 segundos)

Cómo te sientes globalmente · sin pensarlo mucho · el primer número que viene:

- 10 = pleno · energía + ganas
- 7-8 = bien · normal · funcional
- 5-6 = regular · cansado pero operativo
- <5 = mal · cansancio claro
- <3 = muy mal · alerta

## Plantilla Telegram exacta

```
DD/MM · FC: __ bpm · Sueño: __ h · Continuidad __/10 · Despertar: [ya / faltaba] · Sensación: __/10
[Notas: dolor, motivación, contexto vital]
```

Ejemplo:
```
05/06 · FC: 58 bpm · Sueño: 6,5 h · Continuidad 7/10 · Despertar: ya · Sensación: 7/10
[Notas: hijo durmió tirón, comida cenae ligera]
```

## Construir tu baseline (30 días)

**Días 1-7**: solo registra. NO actúes sobre desviaciones.
**Días 8-30**: calcula media móvil de 30 días para cada métrica.
**Día 31+**: la media es tu **baseline personal** · cualquier desviación se interpreta.

```python
def baseline_30d(historico_fc, historico_sueno, historico_sensacion):
    return {
        "fc_baseline": sum(historico_fc[-30:]) / 30,
        "sueno_baseline": sum(historico_sueno[-30:]) / 30,
        "sensacion_baseline": sum(historico_sensacion[-30:]) / 30,
    }
```

Tu baseline NO es "lo normal de la población" · es **lo normal de TI**. Un atleta puede tener FC 50, otro 65. Ambos sanos. La desviación de su propio baseline es la señal.

## Tabla de interpretación combinada

| FC vs baseline | Continuidad | Sensación | Despertar | Acción |
|---|---|---|---|---|
| Normal (±2 bpm) | ≥7/10 | ≥7/10 | "ya está" | Sigue plan · día normal |
| +3-4 bpm aislado | ≥6/10 | ≥5/10 | cualquiera | Observa mañana · sigue plan |
| +5 bpm × 3-4 días | cualquiera | cualquiera | cualquiera | **1 señal de deload extra** (ver `[[sleep-debt-protocol]]`) |
| Normal | <5/10 | <4/10 | "faltaba" | **Sesión técnica** o deload de sesión (ver `[[deload-by-session]]`) |
| +10 bpm aislado | cualquiera | <5/10 | cualquiera | Posible enfermedad incipiente · evalúa al mediodía |
| -3 a -5 bpm sostenido | ≥7/10 | ≥7/10 | "ya está" | Adaptación aeróbica silenciosa (recompensa Z2) |
| Normal | normal | <4/10 sin causa | "faltaba" | Posible bajón mental · ver `[[mental-game-plateau]]` |

## Cuándo invalida una sesión vs cuándo se ajusta

| Condición | Decisión |
|---|---|
| Cumple criterios para sigue plan | Sesión normal |
| FC +5 bpm × 3-4 días | Sesión normal · pero ya cuenta como 1 señal deload |
| Sensación <5 sin otra causa | Warm-up extendido · re-evalúa post (ver `[[deload-by-session]]`) |
| FC +10 bpm + fatiga severa | Skip día gym · descanso o caminata suave |
| 4+ noches malas (semana) | Plan pausa toda la sem (ver `[[sleep-debt-protocol]]` regla 4+) |

## Errores típicos

- ❌ **Medir parado** → FC ya activada, no reposo verdadero
- ❌ **Medir tras cafeína** → cafeína sube FC 5-10 bpm artificialmente
- ❌ **Wearable sin calibrar** → si tu reloj dice 65 y tu pulso manual 58, NO ajustes plan por el wearable
- ❌ **Anotar después** (a media mañana) → los números cambian
- ❌ **Actuar sobre desviaciones antes de baseline 30d** → ruido > señal
- ❌ **Solo medir FC** y olvidar sensación/continuidad
- ❌ **Sensación influenciada por la noche previa social** sin contextualizar

## Variaciones por contexto

### Fin de semana
- Aún registrar (los datos son MÁS valiosos si incluyen días de descanso)
- Si dormiste +90 min de lo habitual: nota "weekend sleep-in" para contextualizar

### Post-evento social (cena, alcohol)
- Anota el contexto en notas
- NO ajustes el baseline incluyendo estos días si son outliers · pueden distorsionar la media móvil

### Viaje / jet lag
- Mantén el check
- Acepta que FC y sensación estarán fuera de baseline 3-5 días
- NO actúes sobre desviaciones durante adaptación

### Periodo menstrual (perfiles femeninos)
- FC tiende a subir 2-5 bpm en fase lútea (días 14-28)
- Crea un baseline POR FASE del ciclo si es relevante
- O simplemente anota el día del ciclo en notas

## Sinergias

- `[[sleep-debt-protocol]]` · este check ALIMENTA la decisión sleep-debt (3-4 días FC alta = 1 señal)
- `[[telegram-tracking]]` · plantilla diaria estándar
- `[[deload-by-session]]` · si sensación <5 + warm-up confirma, deload de sesión
- `[[mental-game-plateau]]` · si bajón sensación sin causa física
- `[[longitudinal-analysis-dimensions]]` · FC tracking es §4.7 cronobiología

## Aplicación

- `recovery-optimizer` · capa 5 ahora delega a este skill
- `telegram-tracking` · plantilla diaria viene de aquí
- `coach-realtime` · pregunta primero "¿cuál fue tu morning check?" antes de cualquier decisión
- `surgical-report-builder` · los datos del morning check son insumo del análisis longitudinal
