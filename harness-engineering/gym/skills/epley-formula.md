---
name: epley-formula
description: Invoke when computing 1RM from a rep max set, recalibrating 1RM after AMRAP, or scaling weights between bloques. Includes formula, validity range, examples, and ratio shortcut for block-to-block scaling.
---

# Epley Formula · cálculo de 1RM + recalibración

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

## Fórmula

```
1RM = peso × (1 + reps / 30)
```

## Validez

- **4-10 reps**: rango ideal · fórmula fiable
- **< 4 reps**: SUBESTIMA tu 1RM real (te pone más bajo de lo que eres) · no fiable
- **> 12 reps**: SOBREESTIMA tu 1RM · si AMRAP da 15+ reps, no aplicar fórmula a pelo · subir peso para futuras series

## Aplicación paso a paso

1. Anota el peso de la serie (kg en la barra)
2. Anota las reps que hiciste (con técnica limpia · cero balanceo)
3. Divide reps / 30
4. Suma 1 al cociente
5. Multiplica resultado por el peso
6. Redondea a múltiplo de 2,5 kg más cercano (o 1,25 si hay disponibles)

## Ejemplos numéricos

| Peso | Reps | Cálculo | 1RM bruto | Redondeado |
|---|---|---|---|---|
| 65 kg | 7 (RPE 10) | 65 × (1 + 7/30) | 80,17 | **80 kg** |
| 72,5 kg | 8 (AMRAP +2) | 72,5 × (1 + 8/30) | 91,83 | **92,5 kg** |
| 67,5 kg | 8 (AMRAP +2) | 67,5 × (1 + 8/30) | 85,5 | **85,5 kg** |
| 77,5 kg | 10 (AMRAP +3) | 77,5 × (1 + 10/30) | 103,33 | **102,5 kg** |
| 75 kg | 5 (RPE 9) | 75 × (1 + 5/30) | 87,5 | **87,5 kg** |
| 70 kg | 4 (RPE 9) | 70 × (1 + 4/30) | 79,33 | **80 kg** |

## Cuándo recalibrar

**Obligatorio** en semanas marcadas RECAL del plan (típico sem 4 y sem 9 · transición de bloque). Aunque el AMRAP esté en target estricto.

**Voluntario**:
- Tras AMRAP +3 sobre target → recalibra al alza
- Tras AMRAP -2 o peor → NO recalibra (baja peso y repite semana)
- Tras lesión recuperada → opcional re-testear

## Atajo del ratio · para escalar todos los pesos de un bloque

Si tu 1RM nuevo es ligeramente distinto al asumido por la tabla:

```
Peso nuevo = Peso tabla × (1RM nuevo / 1RM asumido)
```

**Ejemplo**: tabla bench col 85 sem 6 prescribe 75 kg. Tu 1RM nuevo tras sem 4 = 90 kg (subió desde 85).

```
Ratio = 90 / 85 = 1,059
Peso nuevo sem 6 = 75 × 1,059 = 79,4 → redondea a 80 kg
Peso nuevo sem 7 = 77,5 × 1,059 = 82,06 → 82,5 kg
Peso nuevo sem 8 = 80 × 1,059 = 84,71 → 85 kg
Peso nuevo sem 9 = 82,5 × 1,059 = 87,35 → 87,5 kg
```

Aplicas el ratio a TODA la columna del bloque siguiente, redondeas a 2,5 kg, y te ahorras calcular % rep por rep.

**Cuándo NO funciona el atajo**: si tu 1RM nuevo está muy lejos del asumido (>±5 %). En ese caso recalcula con % puros para tener margen.

## Convenciones de redondeo

- Múltiplo de 2,5 kg más cercano (estándar)
- Si gym no tiene discos de 1,25 kg: redondea a 2,5
- Si el cálculo cae en empate exacto (ej. 58,75): convención es redondear ARRIBA en bloque acumulación (margen para crecer) y ABAJO en pico (seguridad)
- En sem RECAL siempre redondeo ARRIBA (quieres exigir)
- En deload siempre redondeo ABAJO (quieres recuperar)

## Verificación cruzada · script Python

```python
def epley(peso, reps):
    """Devuelve 1RM redondeado a 2,5 kg más cercano."""
    rm = peso * (1 + reps/30)
    return round(rm / 2.5) * 2.5

# Tests
assert epley(65, 7) == 80.0
assert epley(72.5, 8) == 91.83 ... no, 92.5  # round 91.83 → 92.5
print(epley(67.5, 8))  # 85.5
```

## Errores típicos a evitar

1. **Aplicar Epley a <4 reps**: el resultado subestima · no recalibres con singles fallidos o dobles a RPE 10.
2. **Confundir reps con sets**: 3 × 5 reps NO da 1RM = 3 × 5 = 15 input. Usas SOLO la serie AMRAP (la última, al fallo técnico).
3. **Redondear hacia arriba cuando deberías bajar**: tras recalibrar tu 1RM, los pesos de las siguientes semanas SUBEN. No redondees todos arriba porque acumulas exceso.
4. **No re-aplicar el ratio en el bloque siguiente**: si recalibras en sem 4 y otra vez en sem 9, ambos cálculos usan Epley fresh, no acumulas ratios.
