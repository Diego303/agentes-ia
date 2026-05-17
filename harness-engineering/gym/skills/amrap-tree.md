---
name: amrap-tree
description: Invoke when interpreting AMRAP results to decide next-week action (recalibrate, repeat, progress, deload extra). Decision tree with numerical examples.
---

# Árbol AMRAP · qué hacer según resultado del AMRAP

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

El AMRAP final del lift principal es tu termómetro semanal. Te dice si el peso prescrito fue adecuado, alto o bajo. La acción depende del resultado vs el target.

## Tabla de decisión

| Resultado vs target | Interpretación | Acción |
|---|---|---|
| **+3 o más sobre target** | Tu 1RM real era mayor del estimado | Recalibra 1RM al alza con Epley · sube los % +5 % o salta a la siguiente semana del plan |
| **+1 a +2 sobre target** | Zona ideal · cargas calibradas | Sigue plan tal cual · próxima semana avanza normalmente |
| **En target exacto** | Estímulo correcto | Sigue plan tal cual |
| **-1 del target** | Día algo peor o cargas algo justas · aún manejable | Repite la semana sin avanzar |
| **-2 o peor** | Cargas demasiado altas para tu estado real | Baja 5 % los pesos y repite · si falla otra vez: deload extra 1 sem |

## Excepción crítica · sem 4 y sem 9 SIEMPRE recalibras

Aunque el AMRAP esté solo en target (no +1, +2 o +3 sobre):
- Sem 4 y sem 9 marcan transición de bloque
- Aplica Epley al peso × reps del AMRAP de esa semana
- Todas las cargas del bloque siguiente se calculan sobre el 1RM nuevo
- Si AMRAP exactamente target: 1RM nuevo ≈ al actual (poco cambio)
- Si AMRAP +1 o +2: recalibras al alza (cambio notable)

## Ejemplos numéricos completos

### Caso 1 · Sem 1 bench, target ≥9, haces 12

```
Resultado: +3
Acción: recalibras al alza
Cálculo: 1RM nuevo = 65 × (1 + 12/30) = 91 kg
Tu 1RM real era 91 kg, no 85
Acción operativa: saltas a sem 2 directamente o subes +5 % todos los pesos
```

### Caso 2 · Sem 4 bench, target ≥6, haces 7

```
Resultado: +1 (zona ideal)
Acción: recalibras (porque es sem 4, transición de bloque)
Cálculo: 1RM = 72,5 × (1 + 7/30) = 89,4 kg
Bloque 2 (sem 6+) se calcula sobre 89,4 kg
Sem 6 (que originalmente era 75 kg al 88,2 % de 85) → ahora 88,2 % de 89,4 = 78,9 → redondea a 80 kg
```

### Caso 3 · Sem 6 bench, target ≥6, haces 5

```
Resultado: -1
Acción: repite la semana sin avanzar
Sem 7 = mismo peso y target que sem 6 (no avanza progresión hasta confirmar)
```

### Caso 4 · Sem 8 bench, target ≥4, haces 2

```
Resultado: -2
Acción: bajas 5 % los pesos y repites la semana
Sem 9 (la siguiente) repite el bloque de sem 8 con -5 % de carga
Si vuelve a fallar: deload extra 1 sem antes de bloque pico
```

### Caso 5 · Sem 13 bench (pico), target ≥3, fallas a 2

```
Resultado: -1 en zona pico
Acción: NO repites · aceptas y sigues a sem 14 (apertura)
Razón: el pico es zona de testeo neural, no de acumulación
Si llegas al test y no sale: aplica regla test fallido (PR previo se mantiene)
```

## Combinación con escala RPE

El AMRAP solo cuenta reps válidas. Si la última rep "muere":
- Termina pero apenas → cuenta como RPE 9-10 · contabilizas esa rep
- Aborta a mitad → NO cuenta · contabilizas la anterior · RPE 10+

## Bandera roja del árbol

Si **2 AMRAPs seguidos** dan -2 o peor (incluso aplicando -5 % entre medias):
- Algo externo va mal (sueño · estrés · comida · enfermedad incipiente)
- Deload extra 1 sem
- Diagnóstico: revisar `sleep-debt-protocol`, motivación, comida
- Si tras deload sigue: considerar revisar el 1RM de partida (puede haber sido sobreestimado en sem 0)

## Lógica matemática del árbol

Por qué -1 = repetir y +3 = recalibrar al alza:

- **AMRAP en target**: tu 1RM real ≈ asumido
- **AMRAP +1-2**: ligeramente subestimado, dentro de margen
- **AMRAP +3+**: claramente subestimado, hay que recalibrar para evitar subentrenamiento en próximas semanas
- **AMRAP -1**: ligeramente sobreestimado o día puntual peor, repetir es seguro
- **AMRAP -2+**: claramente sobreestimado o estado real ha bajado, hay que ajustar a la baja

El plan está diseñado para que los AMRAP típicamente caigan en zona +1 a +2 (zona ideal). Si caen sistemáticamente fuera, hay un problema de calibración inicial o de recuperación.

## Aplicación · agente coach-realtime

Cuando el usuario pregunta "mi AMRAP fue X, ¿qué hago?":
1. Identifica el target de la semana
2. Calcula diferencia (X - target)
3. Aplica la fila correspondiente del árbol
4. Si es sem 4 o sem 9: añade nota "recalibra siempre por transición de bloque"
5. Si es -2 o peor: añade nota "revisar sueño/comida/estrés esta semana"
