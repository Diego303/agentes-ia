---
name: bench-dual-column
description: Invoke when the user has uncertainty about their bench 1RM (e.g., post-bucle estimate vs PR histórico). Provides dual column system (1RM 80 vs 85) with multiplier 0,9412 (= 80/85), rules for column selection, and weight conversion table.
---

# Bench Dual Column · sistema doble columna 1RM

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

## Cuándo usar

Cuando el usuario tiene **incertidumbre real** sobre su 1RM bench actual:
- Bucle reciente de meses con mismo peso/reps sin progresión (1RM real puede haber bajado)
- Lesión recuperada (1RM puede ser menor o igual al previo)
- Pausa larga >2 meses (1RM caído)
- Test diagnóstico (sem 0) da resultado por debajo del PR histórico

Si el usuario no tiene incertidumbre y su 1RM es claro: usa columna única.

## Concepto

Doble columna paralela en la tabla de bench:
- **Columna A (1RM bajo · típico 80 kg)**: refleja el 1RM operativo actual tras bucle/pausa
- **Columna B (1RM alto · típico 85 kg)**: refleja el PR histórico si todavía es alcanzable

el usuario elige columna según el test diagnóstico de sem 0. El target del macro es el mismo (92,5 kg) independientemente de la columna · solo cambia el % de progreso.

## Multiplicador exacto

```
Ratio col_baja / col_alta = peso_baja / peso_alta
Ejemplo el usuario: 80 / 85 = 0,9412
```

Para cada peso del col alta, el equivalente col baja:
```
Peso col baja = round_a_2.5(Peso col alta × 0,9412)
```

## Tabla de conversión el usuario (col 85 → col 80)

| Sem | Lun col 85 | Lun col 80 | Vie col 85 | Vie col 80 |
|---|---|---|---|---|
| 1 | 3×5 @ 65 | 3×5 @ 60 | 4×8 @ 57,5 | 4×8 @ 55 |
| 2 | 3×5 @ 67,5 | 3×5 @ 62,5 | 4×8 @ 60 | 4×8 @ 57,5 |
| 3 | 3×4 @ 70 | 3×4 @ 65 | 4×6 @ 62,5 | 4×6 @ 60 |
| 4 (RECAL) | 3×4 @ 72,5 + AMRAP | 3×4 @ 67,5 + AMRAP | 4×6 @ 65 | 4×6 @ 60 |
| 5 deload | 3×5 @ 50 | 3×5 @ 47,5 | 3×8 @ 45 | 3×8 @ 42,5 |
| 6 | 3×3 @ 75 + AMRAP | 3×3 @ 70 + AMRAP | 4×5 @ 65 | 4×5 @ 60 |
| 7 | 3×3 @ 77,5 + AMRAP | 3×3 @ 72,5 + AMRAP | 4×5 @ 67,5 | 4×5 @ 62,5 |
| 8 | 3×2 @ 80 + AMRAP | 3×2 @ 75 + AMRAP | 4×4 @ 67,5 | 4×4 @ 62,5 |
| 9 (RECAL) | 3×2 @ 82,5 + AMRAP | 3×2 @ 77,5 + AMRAP | 4×4 @ 70 | 4×4 @ 65 |
| 10 deload | 3×5 @ 55 | 3×5 @ 52,5 | 3×8 @ 50 | 3×8 @ 47,5 |
| 11 | 3×2 @ 82,5 + AMRAP | 3×2 @ 77,5 + AMRAP | 3×3 @ 70 | 3×3 @ 65 |
| 12 | 2×1 @ 85 + AMRAP @ 80 | 2×1 @ 80 + AMRAP @ 75 | 3×3 @ 72,5 | 3×3 @ 67,5 |
| 13 | 2×1 @ 87,5 + AMRAP @ 82,5 | 2×1 @ 82,5 + AMRAP @ 77,5 | 3×2 @ 75 | 3×2 @ 70 |
| 14 | 1×1 @ 90 apertura | 1×1 @ 85 apertura | 3×3 @ 65 técnica | 3×3 @ 60 técnica |
| 15 mini-D | 3×5 @ 52,5 | 3×5 @ 50 | 2×8 @ 47,5 | 2×8 @ 45 |
| 16 TEST | 87,5 → 90 → 92,5 | (mismo target) | — | — |

## Reglas de conversión

1. **Multiplica peso col alta × 0,9412** (exacto) o × 0,94 (aproximación)
2. **Redondea a múltiplo de 2,5 más cercano** (no siempre arriba)
3. **Verificar consistencia entre semanas con mismo peso col alta**: si sem 4 y sem 6 col 85 tienen el mismo peso, col 80 también debe ser el mismo
4. **Empate exacto** (ej. 58,75): redondear ARRIBA en acumulación, ABAJO en deload, ARRIBA en RECAL

## Decisión de columna

**Usuario elige al final de sem 0 diagnóstica**:

```
Si test sem 0 (AMRAP del último set a RPE 9) da 1RM Epley:
- ≥ 85 kg → usa col 85
- 80-84 kg → usa col 80
- < 80 kg → recalcula tabla con multiplicador específico (ej. si 1RM = 75 → multiplicador 75/85 = 0,8824)
```

## Convergencia tras recalibración

Tras RECAL en sem 4 y sem 9, ambas columnas convergen:
- Col 85: si AMRAP sale en target, 1RM nuevo ≈ 89 (+4)
- Col 80: si AMRAP sale en target, 1RM nuevo ≈ 85 (+5)

Por sem 6, ambos usuarios trabajan con 1RM nuevo similar (~85-89), aunque hayan partido de columnas distintas. La columna inicial solo afecta sem 1-4.

## Por qué doble columna y no un único peso

- Si el usuario fuerza la columna alta y su 1RM real es bajo: los AMRAPs sem 4-5 caen en -2 o peor, el plan se rompe
- Si el usuario va por la baja pero su 1RM real es alto: AMRAPs salen +3-5 sobre target, recalibra y vuelve a la realidad

La doble columna evita esa "ruleta inicial". El usuario elige según el test diagnóstico y el AMRAP de sem 1 confirma.

## Notación en el manual

En la tabla del manual editorial:

```html
<thead>
  <tr><th>Sem</th><th>Fase</th><th>Lun · 1RM 80</th><th>Lun · 1RM 85</th><th>Vie · 1RM 80</th><th>Vie · 1RM 85</th><th>AMRAP</th></tr>
</thead>
```

7 columnas: Sem · Fase · Lun col 80 · Lun col 85 · Vie col 80 · Vie col 85 · AMRAP target.

## Verificación automática

```python
def verificar_doble_columna(pesos_85_dict, pesos_80_dict):
    """Verifica que cada peso col 80 = round_2.5(col_85 × 80/85)."""
    for sem, (lun_85, vie_85) in pesos_85_dict.items():
        esperado_lun = round(lun_85 * 80/85 / 2.5) * 2.5
        esperado_vie = round(vie_85 * 80/85 / 2.5) * 2.5
        actual_lun, actual_vie = pesos_80_dict[sem]
        assert actual_lun == esperado_lun, f"Sem {sem} Lun: {actual_lun} vs esperado {esperado_lun}"
        assert actual_vie == esperado_vie, f"Sem {sem} Vie: {actual_vie} vs esperado {esperado_vie}"
```

## Error típico de fusión

Cuando se fusionan tabla original (col 85 only) + tabla expandida (col 80 añadida), es FÁCIL que alguna celda col 80 quede mal:
- Sem 4 vie es ejemplo clásico (65 × 0,94 = 61,1 → debería ser 60 pero se escribe 62,5 por error)
- Auditar TODA la columna después de fusionar

## Alternativa · si el usuario insiste en columna única

Si rechaza la doble columna y solo quiere una:
- Calcula con su 1RM real (no el histórico)
- Acepta que los AMRAPs sem 1 pueden salir +3-5 si el 1RM era subestimado
- Aplica el árbol AMRAP normalmente (recalibra al alza)
