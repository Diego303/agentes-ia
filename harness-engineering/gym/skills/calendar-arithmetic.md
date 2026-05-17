---
name: calendar-arithmetic
description: Invoke when verifying or computing dates in a training plan. Day-of-week verification, week duration (119 days = 17 weeks), session counting (Lun/Mié/Vie in a date range), macro shift calculations after disruptions, macro2/macro3 date computation.
---

# Calendar Arithmetic · aritmética del calendario

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

## Reglas básicas

- **1 semana = 7 días exactos** (LUN-DOM)
- **17 semanas = 119 días exactos**
- **365 días/año** (2026, 2027) · 2028 es bisiesto (366)
- **Sesiones típicas plan U/L/U** = LUN + MIÉ + VIE (3/semana)

## Verificación día-de-la-semana en Python

```python
from datetime import date
dias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']

# Cualquier fecha
fecha = date(2026, 10, 19)
print(dias[fecha.weekday()])  # → LUN ✓
```

## Cálculo de duración

```python
from datetime import date, timedelta

inicio = date(2026, 5, 18)  # Sem 0
fin = date(2026, 11, 1)     # Sem 17 fin
dias = (fin - inicio).days + 1
print(dias)  # 168 días = 24 semanas
```

## Conteo de sesiones en un rango (LUN/MIÉ/VIE)

```python
def sesiones_en_rango(start, end):
    """Cuenta sesiones LUN/MIÉ/VIE entre start y end (inclusivo)."""
    count = 0
    d = start
    while d <= end:
        if d.weekday() in (0, 2, 4):  # 0=LUN, 2=MIÉ, 4=VIE
            count += 1
        d += timedelta(days=1)
    return count

# Vac 1 el usuario: 15 jul - 28 jul
print(sesiones_en_rango(date(2026,7,15), date(2026,7,28)))
# = 6 sesiones perdidas (MIÉ 15, VIE 17, LUN 20, MIÉ 22, VIE 24, LUN 27)
```

## Cálculo de fechas clave macrociclo

### Inicio = LUN 18 may 2026 (sem 0)

| Sem # | Inicio | Fin |
|---|---|---|
| 0 | LUN 18 may | DOM 24 may |
| 1 | LUN 25 may | DOM 31 may |
| 2 | LUN 1 jun | DOM 7 jun |
| ... | ... | ... |
| 16 (test) | LUN 7 sep (original) o LUN 19 oct (reajustado) | DOM 25 oct |
| 17 (deload) | LUN 14 sep o LUN 26 oct | DOM 1 nov |

### Macro 2 inicia inmediatamente tras sem 17

```python
deload_fin = date(2026, 11, 1)  # Sun
macro2_inicio = deload_fin + timedelta(days=1)  # Mon 2 nov 2026
macro2_fin = macro2_inicio + timedelta(days=118)  # 17 sem = 119 días
# (días: macro2_inicio counts as day 1, día 119 = macro2_inicio + 118 días)
print(macro2_fin)  # 2027-02-28 (Sun)
```

### Macro 3 (con buffer semana entre macros opcional)

Sin buffer: macro 3 inicia día siguiente al fin de macro 2.
Con buffer (convención v4 original): macro 3 inicia +1 sem (8 días) tras fin macro 2.

```python
buffer_dias = 7
macro3_inicio = macro2_fin + timedelta(days=1 + buffer_dias)  # Mon 8 mar 2027
macro3_fin = macro3_inicio + timedelta(days=118)  # Sun 4 jul 2027
```

## Verificación cruzada · checklist de fechas

Para cualquier plan, verifica:

```python
fechas_clave = [
    ('Inicio macro', date(2026, 5, 18), 'LUN'),
    ('Test bench', date(2026, 10, 19), 'LUN'),
    ('Test squat', date(2026, 10, 23), 'VIE'),
    ('Fin sem 17 deload', date(2026, 11, 1), 'DOM'),
    ('Inicio macro 2', date(2026, 11, 2), 'LUN'),
    ...
]
for nombre, fecha, esperado in fechas_clave:
    real = dias[fecha.weekday()]
    assert real == esperado, f"{nombre}: {fecha} = {real} (esperado {esperado})"
    print(f"✓ {nombre}: {fecha} = {real}")
```

## Cálculo de impacto de disrupciones

### Disrupción 1 · vacación

```python
def impacto_vacacion(inicio, fin):
    """Calcula sesiones perdidas y duración."""
    dias = (fin - inicio).days + 1
    sesiones = sesiones_en_rango(inicio, fin)
    return dias, sesiones

vac1 = impacto_vacacion(date(2026,7,15), date(2026,7,28))
# → (14 días, 6 sesiones)

vac2 = impacto_vacacion(date(2026,8,10), date(2026,8,16))
# → (7 días, 3 sesiones)
```

### Disrupción 2 · ventana entre 2 vacaciones

```python
def sesiones_disponibles(start, end):
    """Sesiones de gym disponibles entre 2 fechas."""
    return sesiones_en_rango(start, end)

gap = sesiones_disponibles(date(2026,7,29), date(2026,8,9))
# → 5 sesiones (MIÉ 29 jul, VIE 31 jul, LUN 3 ago, MIÉ 5 ago, VIE 7 ago)
```

### Shift del calendario completo

Si extiendes el macro N semanas:

```python
def shift_dates(original, n_semanas):
    """Desplaza una fecha N semanas adelante."""
    return original + timedelta(days=n_semanas * 7)

test_original = date(2026, 9, 7)
test_reajustado = shift_dates(test_original, 6)  # +6 sem
# → date(2026, 10, 19)  ← Mon 19 oct ✓
```

## Errores típicos en aritmética calendario

1. **17 semanas ≠ 17 días × 7** si cuentas días inclusive vs exclusive
   - Inclusive (día inicio + N-1 días después): 7 días = 1 semana
   - Mejor usar `+ timedelta(days=N*7)` para semana N+1 inicio
2. **Olvidar que 2027 NO es bisiesto** (2024, 2028 sí · 2027 no)
3. **Confundir "sem 17" (numeración programa)** con "sem 17 calendario" (contando todas las semanas calendario incluyendo RECON y vacaciones)
4. **Asumir que macros encadenan sin buffer** · convención v4 = macro 1 → macro 2 sin buffer, macro 2 → macro 3 con 1 sem buffer

## Conversión semana-a-fecha del plan ejemplo

| Sem | Fechas (original) | Fechas (reajustado +6 sem) |
|---|---|---|
| 0 | 18-24 may 2026 | 18-24 may 2026 |
| 1 | 25-31 may | 25-31 may |
| 4 | 15-21 jun | 15-21 jun (RECAL) |
| 5 | 22-28 jun (deload) | 22-28 jun |
| 8 (intens 8) | 13-19 jul | (con vacación) sem 8a parcial + RECON + sem 8b 24-30 ago |
| 9 (RECAL) | 20-26 jul | 31 ago-6 sep |
| 12 (HITO 3) | 10-16 ago | (con vacación 2) 21-27 sep |
| 16 (TEST) | 7-13 sep | 19-25 oct |
| 17 (deload post) | 14-20 sep | 26 oct-1 nov |

## Validación de un plan completo

Algoritmo:

1. Para cada fecha mencionada en el plan (hero, hardcoded, hitos, test, sem 17, macro 2, macro 3):
   - Verificar día de la semana esperado (LUN/MIÉ/VIE/DOM según corresponda)
2. Para cada duración mencionada (17 sem, 119 días):
   - Verificar matemática
3. Para cada conteo de sesiones (vacaciones, perdidas):
   - Verificar con `sesiones_en_rango`
4. Para coherencia macro:
   - macro 1 deload fin + 1 día = macro 2 inicio (sin buffer)
   - macro 2 deload fin + buffer = macro 3 inicio
