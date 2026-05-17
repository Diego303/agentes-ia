---
name: telegram-tracking
description: Invoke when defining the tracking template for Telegram (or any notes app) for daily session logs. Cabecera mental with 4 PRs, notation conventions (peso × reps × RPE), mancuernas peso/lado, AMRAP notation, daily morning check (FC + sueño + sensación), metrics review every 4 weeks.
---

# Telegram Tracking · cabecera + notación

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

## Por qué importa

La cabecera mental se actualiza con los 4 PRs reales. Eso desplaza la cabecera obsoleta de "PR banca 80×2" de 2024 (mental clutter que limita).

Cada sesión empieza con copy-paste de la plantilla, rellenas los huecos, y queda registro temporal completo para revisar progresión cada 4 semanas.

## Plantilla cabecera · cada sesión

```
Día XX · mes · 2026 · Sem XX · bloque [Acum / Intens / Pico / Deload]
Entrenamiento: [Upper A · LUN / Lower · MIÉ / Upper B · VIE]
PR bench: 85 kg (jun 2025) · Target macro: 92,5 kg
PR sentadilla: 110 kg · Target: 125 kg
PR hip thrust: 120×8 · Target: 130×8
PR prensa: 190×8 · Target: 220×8

Sueño noche previa: X h · Continuidad: __/10
Hora inicio: XX:XX · Sensación pre: __/10
Cafeína: XXX mg a las XX:XX
```

## Quita el "PR banca 80×2" obsoleto

Línea heredada de 2024 que ya no refleja realidad. Desaparece de tu vocabulario. Sustituida por la cabecera de arriba con los 4 PRs actualizados.

## Notación obligatoria por serie

### Lift principal con AMRAP

```
Bench (3+1*)
Set 1: 65 × 5 × RPE 7
Set 2: 65 × 5 × RPE 7
Set 3: 65 × 5 × RPE 8
Set 4 (AMRAP): 65 × 11 × RPE 9
```

### Accesorios sin AMRAP

Formato compacto: `peso × reps × sets RPE`. Ejemplo:

```
Remo Pendlay: 60 × 5-6 × 4 sets RPE 7-8
Overhead tri mc: 17,5 mc/lado × 11-12 × 3 RPE 8
Dominada PC: PC × 7-8 × 3 RPE 8
```

## Notación mancuernas

- **Siempre peso/lado**. Si 25 kg cada mano: `25 mc/lado`
- **Total opcional entre paréntesis**: `25 mc/lado (=50 kg total)`
- **Evita escribir "50t" o "50 t"** → la "t" sugiere toneladas y confunde
- Si las mancuernas no son iguales (raro): `25/23 mc` o anota cuál es la pesada

## Símbolos universales

| Símbolo | Significado |
|---|---|
| `3+1*` | 3 sets fijos + 1 AMRAP |
| `↻` | Superserie (15-20 s entre ejercicios) |
| `25 mc/lado` | 25 kg cada mano |
| `RECAL` | Aplicar Epley al AMRAP de esta sem |
| `RPE X` | Esfuerzo percibido X/10 |
| `WU` | Warm-up set |
| `≥ N` | AMRAP target N reps o más |

## Ejemplo log completo · sesión LUN

```
Día 25 · may · 2026 · Sem 1 bloque Acumulación
Entrenamiento: Upper A · Sueño 6,5 h · Continuidad 8/10 · Hora 20:32 · Sensación pre: 7/10 · Cafeína 240 mg a las 19:00

W: barra 20×10, 30×5, 45×3, 55×2 (8 min)
A1 bench: 65×5×RPE 7 / 65×5×RPE 7 / 65×5×RPE 8 / 65×11 AMRAP×RPE 9 (target ≥9, +2 sobre)
A2 remo Pendlay: 50×6×RPE 7 / 50×6×RPE 7 / 50×6×RPE 8 / 50×6×RPE 8
B overhead tríceps: 12,5 mc×12×RPE 8 ×3
C1+C2 dominada/face pulls: 5 PC×3 / face pulls 25kg×15×3
D lat raises: 7,5 mc/lado×12×RPE 9 ×3
E Bulgarian: PC×10/lado ×2
F dead hangs: 25s / 30s / 30s

Sensación post: 8/10
AMRAP bench salió +2 → sigo plan sem 2 normal
MICRO-WIN: AMRAP destacado bench +2 (zona ideal)
```

## Chequeo diario matinal (60 segundos al despertar)

Plantilla simple:

```
DD/MM · FC: XX bpm · Sueño: X h · Continuidad __/10 · Sensación: __/10
[Notas: dolor, motivación, lo que sea]
```

### FC reposo

- Antes de levantarte (sentado/tumbado), espera 60 s en reposo
- Cuenta pulso 30 s × 2 (con dos dedos en muñeca o cuello)
- Anota
- Calcula media móvil 30 días

### Interpretación FC

| FC vs media 30 días | Interpretación | Acción |
|---|---|---|
| Misma o ±2 bpm | Normal | Sigue plan |
| +3 a +4 un día | Noche mala o ayer fue heavy | Observa al día siguiente |
| **+5 bpm o más durante 3-4 días seguidos** | Sobrecarga real | 1 señal de deload extra |
| +10 bpm aislado | Posible enfermedad o resaca | Día técnico o skip |
| -3 a -5 bpm sostenido | Mejora aeróbica (adaptación Z2) | Sigue plan · recompensa silenciosa |

### Sensación 1-10

- 1 = destrozado · 10 = lleno energía
- 3 días seguidos a ≤ 5 = señal de deload (con o sin FC alterada)
- Día de sesión a ≤ 4 = sesión técnica (50 % vol, RPE 6-7, sin AMRAP)

## Métricas cada 4 semanas (coincide con hitos)

En entrada dedicada de Telegram:

1. **Peso corporal en ayunas** (mismo día semana, mismo momento)
2. **Foto progreso** (mismas condiciones: luz, hora, ropa, distancia) · frontal + perfil + espalda
3. **Medidas con cinta**: brazo (contraído), pecho, cintura (ombligo), muslo (mitad)
4. **Top set del compuesto principal** (mejor AMRAP o single de la semana)
5. **Sueño medio semanal** (media de las 7 noches previas)

## Anotación de micro-celebraciones

Separadas como categoría:

```
MICRO-WIN: [tipo] [descripción breve]
```

Tipos:
- `AMRAP destacado` (+2 o más sobre target)
- `Peso nuevo limpio` (primera vez)
- `Semana completa` (sin saltar ninguna sesión)
- `Sesión 10/10` (mejor lunes / mejor miércoles / mejor viernes)
- `Sueño excepcional` (7+ h consolidadas)
- `Adaptación neural` (técnica que de pronto "encaja")

Acumular 30-40 micro-wins anotados en 17 semanas = archivo de evidencia objetiva que combate cualquier sensación de "esto no avanza".

## Aplicación del tracking

- **Sin tracking**: no puedes aplicar árbol AMRAP (no recuerdas AMRAP previos)
- **Sin FC reposo**: no puedes detectar sobrecarga objetivamente
- **Sin cabecera mental**: la cabecera vieja (PR fantasma) gana

Tracking es ~2-3 minutos por sesión + 60 s diarios. ROI alto.

## Errores típicos

1. **Anotar después** (en casa al día siguiente) → datos imprecisos, faltan series
2. **Solo anotar el top set** → pierdes contexto del resto de la sesión
3. **Olvidar el RPE** → solo el peso × reps no es suficiente para calibrar
4. **No anotar mancuernas peso/lado** → confusión al revisar progresión
5. **No anotar la fecha** → todo se desordena si revisas a las 4 sem
