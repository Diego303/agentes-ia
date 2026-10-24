---
name: bench-dual-column
description: Invoke when the user has uncertainty about their bench 1RM (e.g., post-bucle estimate vs PR histórico). Provides dual column system (e.g., 1RM 95 vs 100) with multiplier = 1RM_baja / 1RM_alta (e.g., 0,95 = 95/100), rules for column selection, and weight conversion table.
---

# Bench Dual Column · sistema doble columna 1RM

> Los números de los ejemplos son ilustrativos: recalcula con los datos de tu usuario.

## Cuándo usar

Cuando el usuario tiene **incertidumbre real** sobre su 1RM bench actual:
- Bucle reciente de meses con mismo peso/reps sin progresión (1RM real puede haber bajado)
- Lesión recuperada (1RM puede ser menor o igual al previo)
- Pausa larga >2 meses (1RM caído)
- Test diagnóstico (sem 0) da resultado por debajo del PR histórico

Si el usuario no tiene incertidumbre y su 1RM es claro: usa columna única.

## Concepto

Doble columna paralela en la tabla de bench:
- **Columna A (1RM bajo · p. ej., 95 kg)**: refleja el 1RM operativo actual tras bucle/pausa
- **Columna B (1RM alto · p. ej., 100 kg)**: refleja el PR histórico si todavía es alcanzable

El usuario elige columna según el test diagnóstico de sem 0. El target del macro es el mismo (p. ej., 105 kg) independientemente de la columna · solo cambia el % de progreso.

## Multiplicador exacto

```
Ratio col_baja / col_alta = peso_baja / peso_alta
Ejemplo ilustrativo (perfil ficticio): 95 / 100 = 0,95
```

Para cada peso del col alta, el equivalente col baja:
```
Peso col baja = round_a_2.5(Peso col alta × multiplicador)   # × 0,95 en el ejemplo
```

## Tabla de conversión · ejemplo ilustrativo (col 100 → col 95)

| Sem | Lun col 100 | Lun col 95 | Vie col 100 | Vie col 95 |
|---|---|---|---|---|
| 1 | 3×5 @ 77,5 | 3×5 @ 72,5 | 4×8 @ 67,5 | 4×8 @ 65 |
| 2 | 3×5 @ 80 | 3×5 @ 75 | 4×8 @ 70 | 4×8 @ 67,5 |
| 3 | 3×4 @ 82,5 | 3×4 @ 77,5 | 4×6 @ 72,5 | 4×6 @ 70 |
| 4 (RECAL) | 3×4 @ 85 + AMRAP | 3×4 @ 80 + AMRAP | 4×6 @ 77,5 | 4×6 @ 72,5 |
| 5 deload | 3×5 @ 60 | 3×5 @ 57,5 | 3×8 @ 52,5 | 3×8 @ 50 |
| 6 | 3×3 @ 87,5 + AMRAP | 3×3 @ 82,5 + AMRAP | 4×5 @ 77,5 | 4×5 @ 72,5 |
| 7 | 3×3 @ 90 + AMRAP | 3×3 @ 85 + AMRAP | 4×5 @ 80 | 4×5 @ 75 |
| 8 | 3×2 @ 95 + AMRAP | 3×2 @ 90 + AMRAP | 4×4 @ 80 | 4×4 @ 75 |
| 9 (RECAL) | 3×2 @ 97,5 + AMRAP | 3×2 @ 92,5 + AMRAP | 4×4 @ 82,5 | 4×4 @ 77,5 |
| 10 deload | 3×5 @ 65 | 3×5 @ 62,5 | 3×8 @ 60 | 3×8 @ 57,5 |
| 11 | 3×2 @ 97,5 + AMRAP | 3×2 @ 92,5 + AMRAP | 3×3 @ 82,5 | 3×3 @ 77,5 |
| 12 | 2×1 @ 100 + AMRAP @ 95 | 2×1 @ 95 + AMRAP @ 90 | 3×3 @ 85 | 3×3 @ 80 |
| 13 | 2×1 @ 102,5 + AMRAP @ 97,5 | 2×1 @ 97,5 + AMRAP @ 92,5 | 3×2 @ 87,5 | 3×2 @ 82,5 |
| 14 | 1×1 @ 105 apertura | 1×1 @ 100 apertura | 3×3 @ 77,5 técnica | 3×3 @ 72,5 técnica |
| 15 mini-D | 3×5 @ 62,5 | 3×5 @ 60 | 2×8 @ 55 | 2×8 @ 52,5 |
| 16 TEST | 100 → 102,5 → 105 | (mismo target) | — | — |

## Reglas de conversión

1. **Multiplica peso col alta × multiplicador exacto** (0,95 en el ejemplo · si el par no es redondo, usa 4 decimales, no una aproximación de 2)
2. **Redondea a múltiplo de 2,5 más cercano** (no siempre arriba)
3. **Verificar consistencia entre semanas con mismo peso col alta**: si sem 4 y sem 6 col 100 tienen el mismo peso, col 95 también debe ser el mismo
4. **Empate exacto** (ej. 58,75): redondear ARRIBA en acumulación, ABAJO en deload, ARRIBA en RECAL

## Decisión de columna

**Usuario elige al final de sem 0 diagnóstica**:

```
Si test sem 0 (AMRAP del último set a RPE 9) da 1RM Epley:
- ≥ 100 kg → usa col 100
- 95-99 kg → usa col 95
- < 95 kg → recalcula tabla con multiplicador específico (ej. si 1RM = 90 → multiplicador 90/100 = 0,9000)
```

## Convergencia tras recalibración

Tras RECAL en sem 4 y sem 9, ambas columnas convergen:
- Col 100: si AMRAP sale en target, 1RM nuevo ≈ 105 (+5)
- Col 95: si AMRAP sale en target, 1RM nuevo ≈ 100 (+5)

Por sem 6, ambos usuarios trabajan con 1RM nuevo similar (~100-105), aunque hayan partido de columnas distintas. La columna inicial solo afecta sem 1-4.

## Por qué doble columna y no un único peso

- Si el usuario fuerza la columna alta y su 1RM real es bajo: los AMRAPs sem 4-5 caen en -2 o peor, el plan se rompe
- Si el usuario va por la baja pero su 1RM real es alto: AMRAPs salen +3-5 sobre target, recalibra y vuelve a la realidad

La doble columna evita esa "ruleta inicial". El usuario elige según el test diagnóstico y el AMRAP de sem 1 confirma.

## Caso general · cualquier par de 1RMs (no solo 95/100)

La doble columna funciona para cualquier par (1RM_referencia_alta, 1RM_referencia_baja). La fórmula del multiplicador:

```
multiplicador = 1RM_baja / 1RM_alta
peso_columna_baja[sem] = round_a_2.5( peso_columna_alta[sem] × multiplicador )
```

### Pares estándar comunes

| Par (alta, baja) | Multiplicador | Cuándo aplica |
|---|---|---|
| 100, 95 | 0,9500 | -5% (incertidumbre menor) |
| 100, 90 | 0,9000 | -10% (incertidumbre moderada) |
| 100, 85 | 0,8500 | -15% (post-bucle largo) |
| 80, 75 | 0,9375 | lifter intermedio-ligero · -6% |
| 140, 130 | 0,9286 | lifter avanzado |
| 50, 45 | 0,9000 | lifter ligero / mujer intermedia · -10% |

### Ejemplo · lifter de 60 kg corporal con 1RM bench 50 kg ± 5

```
1RM alta asumida: 50 kg
1RM baja asumida: 45 kg
multiplicador = 45 / 50 = 0,9000

Sem 1 col 50: 3×5 @ 37,5 + AMRAP    (37,5 = round_2.5(50 × 0,76))
Sem 1 col 45: 3×5 @ 35 + AMRAP      (35 = round_2.5(45 × 0,76))
                                     (peso = peso_col_50 × 0,90)
```

### Script Python · generar tu tabla

```python
def col_baja(peso_alta, ratio):
    return round(peso_alta * ratio / 2.5) * 2.5

# Configura tus dos 1RMs y la tabla %1RM del bloque
RM_alta = 100     # cambia a tu 1RM alta asumida
RM_baja = 95      # cambia a tu 1RM baja asumida
ratio = RM_baja / RM_alta

tabla_porcentajes = {
    1: (77.5, 67.5),   # sem: (%lun, %vie) · reproduce la tabla de ejemplo
    2: (80, 70),
    3: (82.5, 72.5),
    4: (85, 77.5),
    # ... etc según tu plan
}

print(f"Multiplicador: {ratio:.4f}")
for sem, (pct_lun, pct_vie) in tabla_porcentajes.items():
    lun_alta = round(RM_alta * pct_lun / 100 / 2.5) * 2.5
    vie_alta = round(RM_alta * pct_vie / 100 / 2.5) * 2.5
    lun_baja = col_baja(lun_alta, ratio)
    vie_baja = col_baja(vie_alta, ratio)
    print(f"Sem {sem}: LUN {lun_alta}/{lun_baja} kg · VIE {vie_alta}/{vie_baja} kg")
```

Esto reemplaza la decisión manual de columna por una **regla operativa universal** aplicable a cualquier perfil.

## Notación en el manual

En la tabla del manual editorial:

```html
<thead>
  <tr><th>Sem</th><th>Fase</th><th>Lun · 1RM 95</th><th>Lun · 1RM 100</th><th>Vie · 1RM 95</th><th>Vie · 1RM 100</th><th>AMRAP</th></tr>
</thead>
```

7 columnas: Sem · Fase · Lun col 95 · Lun col 100 · Vie col 95 · Vie col 100 · AMRAP target.

## Verificación automática

```python
def verificar_doble_columna(pesos_100_dict, pesos_95_dict):
    """Verifica que cada peso col 95 = round_2.5(col_100 × 95/100)."""
    for sem, (lun_100, vie_100) in pesos_100_dict.items():
        esperado_lun = round(lun_100 * 95/100 / 2.5) * 2.5
        esperado_vie = round(vie_100 * 95/100 / 2.5) * 2.5
        actual_lun, actual_vie = pesos_95_dict[sem]
        assert actual_lun == esperado_lun, f"Sem {sem} Lun: {actual_lun} vs esperado {esperado_lun}"
        assert actual_vie == esperado_vie, f"Sem {sem} Vie: {actual_vie} vs esperado {esperado_vie}"
```

## Error típico de fusión

Cuando se fusionan tabla original (col 100 only) + tabla expandida (col 95 añadida), es FÁCIL que alguna celda col 95 quede mal:
- Sem 1 vie es ejemplo clásico (67,5 × 0,95 = 64,1 → debería ser 65 pero se escribe 62,5 por redondear hacia abajo)
- Auditar TODA la columna después de fusionar

## Alternativa · si el usuario insiste en columna única

Si rechaza la doble columna y solo quiere una:
- Calcula con su 1RM real (no el histórico)
- Acepta que los AMRAPs sem 1 pueden salir +3-5 si el 1RM era subestimado
- Aplica el árbol AMRAP normalmente (recalibra al alza)
