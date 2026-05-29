---
name: warmup-calculator
description: Invoke when defining warm-up sets before the working set. Provides protocol by work-set intensity (60-70% → 2 wu / 75-80% → 3 wu / 85-90% → 4-5 wu / test ≥95% → 6 wu) with exact percentages and rep targets, mobility integration, and "quick warm-up" for accessories. Includes Python script to generate warm-up table from work-set weight.
---

# Warm-up Calculator · cuántos sets y a qué peso antes del trabajo

> **Nota · skill 100% general.** Los porcentajes son universales · solo cambias el 1RM y peso de trabajo. Funciona para cualquier lifter, sexo, edad, modalidad.

## Principio rector

El warm-up debe **RAMP** (subir progresivamente la activación neural y la temperatura tisular) **sin fatigar**. Cada warm-up set debe ser más fácil que el work set · NUNCA debe acercarse a tu RPE prescrito.

**Regla de oro**: si el último warm-up set te cansa, hiciste demasiados o subiste muy alto.

## Tabla maestra · número de warm-up sets por intensidad del work-set

| Intensidad work-set | Reps work-set | Warm-up sets | Esquema sugerido (%/reps) |
|---|---|---|---|
| 60-70% (volumen) | 8-12+ | 2 | 40% × 8 → 55% × 5 |
| 70-80% (intensificación temprana) | 6-8 | 3 | 40% × 8 → 55% × 5 → 70% × 3 |
| 80-87% (intensificación tardía) | 4-6 | 4 | 40% × 8 → 55% × 5 → 70% × 3 → 80% × 2 |
| 87-95% (pico) | 2-4 | 5 | 40% × 8 → 55% × 5 → 70% × 3 → 80% × 2 → 90% × 1 |
| ≥95% (test, single) | 1 | 6 | 40% × 8 → 55% × 5 → 65% × 3 → 75% × 2 → 85% × 1 → 92% × 1 |

## Protocolos detallados

### Work-set 60-70% (sets de volumen 10+ reps)

```
1. Mobility 3-5 min (ver [[mobility-prehab-by-joint]])
2. Barra vacía × 10 (la primera "warm-up" real)
3. 40% × 8 (~30s entre warm-ups)
4. 55% × 5
→ Work set
```

Descanso entre warm-ups: 60-90s.
Descanso del último warm-up al work set: 90s-2min.

### Work-set 75-80% (intensificación · 6-8 reps)

```
1. Mobility 3-5 min
2. Barra vacía × 10
3. 40% × 8
4. 55% × 5
5. 70% × 3
→ Work set (75-80%)
```

### Work-set 85-90% (pico · 4-6 reps)

```
1. Mobility 5 min (cuidado torácica, hombros, caderas)
2. Barra vacía × 10
3. 40% × 8
4. 55% × 5
5. 70% × 3
6. 80% × 2
→ Work set (85-90%)
```

Descanso último warm-up → work set: 2-3 min (recuperación neural).

### Work-set ≥95% (test, opener, single pico)

```
1. Mobility 8-10 min (extendida)
2. Barra vacía × 10
3. 40% × 8
4. 55% × 5
5. 65% × 3
6. 75% × 2
7. 85% × 1
8. 92% × 1
→ Single al 95%+
```

Descansos entre warm-ups: progresivos (90s → 2 min → 3 min).
Último warm-up → intento: **5 min** descanso (recuperación neural completa).

## Mobility pre-warmup (3-10 min específicos por lift)

Antes del primer warm-up con barra, mobility activa específica.

| Sesión | Joints prioritarios | Tiempo |
|---|---|---|
| Pre-bench | Hombro + torácica | 3 min |
| Pre-squat | Cadera + tobillo + torácica | 5 min |
| Pre-deadlift | Cadera + lumbar + torácica | 5 min |
| Pre-hip thrust | Cadera + lumbar | 3 min |
| Pre-press militar | Hombro + torácica | 3 min |
| Pre-test (cualquier lift) | Todos los del lift + activación | 8-10 min |

Ver `[[mobility-prehab-by-joint]]` para detalle de cada joint.

## "Quick warm-up" para accesorios

Los accesorios NO necesitan ramp completo (el lift principal ya activó el sistema).

| Accesorio | Warm-up |
|---|---|
| Remo, jalón, dominada | 1 set × 8 al ~50% del work |
| Press militar (tras bench) | 1 set × 5 al ~60% |
| Curl, tríceps, isolation | NO warm-up · primer set al 70-80% del work |
| Sentadilla búlgara | 1 set × 8 PC |
| Hip thrust BW (tras squat) | 1 set × 10 BW + 1 × 8 al ~50% |

## Script Python · generar tu tabla de warm-up

```python
def warmup_table(work_weight, work_pct, increment_2_5=True):
    """
    Genera tabla de warm-up para un work-set dado.

    Args:
        work_weight: peso del work-set en kg
        work_pct: % del 1RM que representa el work-set (e.g., 80)
        increment_2_5: redondear a 2,5 kg más cercano

    Returns:
        Lista de tuplas (peso_warm_up, reps_warm_up)
    """
    if work_pct < 70:
        pcts = [0.50, 0.65]
    elif work_pct < 80:
        pcts = [0.40, 0.55, 0.70]
    elif work_pct < 87:
        pcts = [0.40, 0.55, 0.70, 0.80]
    elif work_pct < 95:
        pcts = [0.40, 0.55, 0.70, 0.80, 0.90]
    else:
        pcts = [0.40, 0.55, 0.65, 0.75, 0.85, 0.92]

    one_rm = work_weight / (work_pct / 100)
    sets = []
    reps_by_pct = {
        0.40: 8, 0.50: 8, 0.55: 5, 0.65: 3, 0.70: 3,
        0.75: 2, 0.80: 2, 0.85: 1, 0.90: 1, 0.92: 1
    }
    for pct in pcts:
        w = one_rm * pct
        if increment_2_5:
            w = round(w / 2.5) * 2.5
        sets.append((w, reps_by_pct[pct]))
    return sets


# Ejemplo: work-set 80 kg al 85%
print("Work-set 80 kg al 85% del 1RM:")
for w, r in warmup_table(80, 85):
    print(f"  {w} kg × {r}")

# Output:
# 37.5 kg × 8
# 50.0 kg × 5
# 65.0 kg × 3
# 75.0 kg × 2

# Ejemplo: test al 95% del target (target 92,5)
print("\nTest 92,5 kg (intento 1 al 95%):")
test_weight = 92.5 * 0.95
for w, r in warmup_table(test_weight, 95):
    print(f"  {w} kg × {r}")
```

## Variaciones

### Segundo lift del día (post-otro lift pesado)

El sistema ya está activado. Warm-up reducido:
- 1-2 sets menos
- Empezar al 50% directamente (sin barra vacía adicional)
- Foco en activación específica del nuevo patrón

### Lift principal post-cardio Z2

Si hiciste Z2 antes (raro · ver `[[cardio-z2]]`): warm-up normal pero añade 2 min de mobility extra (Z2 enfría músculos lentos).

### Sesión post-pausa (RECON)

Warm-up extendido: añadir 2 sets más al esquema. Ver `[[recon-protocols]]`.

### Sesión con sensación pre <5/10

Warm-up extendido a 12-15 min en lugar de 8. Re-evalúa tras warm-up (ver `[[deload-by-session]]`).

## Errores típicos

- ❌ **Calentar demasiado** (hacer 8 warm-ups para un 75% · te fatigas antes del trabajo)
- ❌ **Calentar muy poco** (saltar directo a 80% sin ramp · técnica falla)
- ❌ **Reps altas en warm-ups** (warm-up de 10 reps al 70% = work set encubierto)
- ❌ **Saltar mobility** y empezar con barra vacía (frío articular en sentadilla pesada)
- ❌ **Mismo warm-up para 60% y 90%** (necesitan ramps distintos)
- ❌ **Warm-up con accesorios pesados** (curl 12,5 mc/lado antes del bench resta neural)
- ❌ **Descanso muy corto último warm-up → work** (necesitas recuperación, no fatiga residual)

## Tiempo total estimado del warm-up

| Intensidad work | Tiempo warm-up |
|---|---|
| 60-70% | 8-10 min (mobility 3 + sets 5-7) |
| 75-80% | 10-12 min |
| 85-90% | 14-17 min |
| ≥95% test | 25-30 min |

## Sinergias

- `[[lift-technique-reference]]` · técnica de la primera rep de cada warm-up
- `[[mobility-prehab-by-joint]]` · mobility pre-warm-up
- `[[pre-session-mental-prep]]` · ritual mental coincide con primeros 3-5 min de warm-up
- `[[test-day-protocol]]` · usa el caso ≥95% específicamente
- `[[bracing-valsalva]]` · activa el bracing desde warm-up al 70%+

## Aplicación

- `manual-html-builder` · §04 "Tu Semana" y §05/06/07 day-cards aplican esta tabla
- `quick-ref-builder` · incluir tabla compacta en §CHEAT
- `gym-plan-architect` · sumar tiempo de warm-up a la duración total de sesión
- `test-day-protocol` · sustituir tabla warm-up actual por referencia a este skill
