---
name: calendar-arithmetic
description: Invoke when verifying or computing dates in a training plan. Day-of-week verification, week duration (119 days = 17 weeks), session counting (Lun/Mié/Vie in a date range), macro shift calculations after disruptions, macro2/macro3 date computation.
---

# Calendar Arithmetic · aritmética del calendario

> Los números de los ejemplos son ilustrativos: recalcula con los datos de tu usuario. Calendario de ejemplo: macro que arranca el LUN 12 ene 2026 (sem 0).

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
fecha = date(2026, 1, 12)
print(dias[fecha.weekday()])  # → LUN ✓
```

## Cálculo de duración

```python
from datetime import date, timedelta

inicio = date(2026, 1, 12)  # Sem 0
fin = date(2026, 6, 28)     # Sem 17 fin (reajustado +6 sem)
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

# Ejemplo · vacación de 2 semanas: MIÉ 11 mar - MAR 24 mar
print(sesiones_en_rango(date(2026,3,11), date(2026,3,24)))
# = 6 sesiones perdidas (MIÉ 11, VIE 13, LUN 16, MIÉ 18, VIE 20, LUN 23)
```

## Cálculo de fechas clave macrociclo

### Inicio = LUN 12 ene 2026 (sem 0)

| Sem # | Inicio | Fin |
|---|---|---|
| 0 | LUN 12 ene | DOM 18 ene |
| 1 | LUN 19 ene | DOM 25 ene |
| 2 | LUN 26 ene | DOM 1 feb |
| ... | ... | ... |
| 16 (test) | LUN 4 may (original) o LUN 15 jun (reajustado) | DOM 10 may o DOM 21 jun |
| 17 (deload) | LUN 11 may o LUN 22 jun | DOM 17 may o DOM 28 jun |

### Macro 2 inicia inmediatamente tras sem 17

```python
deload_fin = date(2026, 6, 28)  # Sun (calendario reajustado)
macro2_inicio = deload_fin + timedelta(days=1)  # Mon 29 jun 2026
macro2_fin = macro2_inicio + timedelta(days=118)  # 17 sem = 119 días
# (días: macro2_inicio counts as day 1, día 119 = macro2_inicio + 118 días)
print(macro2_fin)  # 2026-10-25 (Sun)
```

### Macro 3 (con buffer semana entre macros opcional)

Sin buffer: macro 3 inicia día siguiente al fin de macro 2.
Con buffer (convención del plan de ejemplo): macro 3 inicia +1 sem (8 días) tras fin macro 2.

```python
buffer_dias = 7
macro3_inicio = macro2_fin + timedelta(days=1 + buffer_dias)  # Mon 2 nov 2026
macro3_fin = macro3_inicio + timedelta(days=118)  # Sun 28 feb 2027
```

## Caso general · cualquier fecha de inicio

Sustituye `date(2026, 1, 12)` por tu fecha de inicio real:

```python
from datetime import date, timedelta

INICIO_MACRO = date(2026, 1, 12)     # tu lunes de inicio (cambia a tu fecha)
SEMANAS_MACRO = 17                   # tu duración (cambia según tu plan)

fin_macro = INICIO_MACRO + timedelta(days=SEMANAS_MACRO * 7 - 1)
test_fecha = INICIO_MACRO + timedelta(days=(SEMANAS_MACRO - 1) * 7)
deload_post = test_fecha + timedelta(days=7)
macro2_inicio = deload_post + timedelta(days=7)

print(f"Inicio: {INICIO_MACRO}")
print(f"Test: {test_fecha}")
print(f"Fin sem deload post: {deload_post}")
print(f"Macro 2 inicio: {macro2_inicio}")
```

Las fechas concretas del calendario de ejemplo (12 ene 2026 → 28 jun 2026 reajustado) son **ejemplo**, no plantilla. Cualquier humano que diseñe un macro puede sustituir su `INICIO_MACRO` y `SEMANAS_MACRO` para obtener todas las fechas clave.

## Verificación cruzada · checklist de fechas

Para cualquier plan, verifica:

```python
fechas_clave = [
    ('Inicio macro', date(2026, 1, 12), 'LUN'),
    ('Test bench', date(2026, 6, 15), 'LUN'),
    ('Test squat', date(2026, 6, 19), 'VIE'),
    ('Fin sem 17 deload', date(2026, 6, 28), 'DOM'),
    ('Inicio macro 2', date(2026, 6, 29), 'LUN'),
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

vac1 = impacto_vacacion(date(2026,3,11), date(2026,3,24))
# → (14 días, 6 sesiones)

vac2 = impacto_vacacion(date(2026,4,6), date(2026,4,12))
# → (7 días, 3 sesiones)
```

### Disrupción 2 · ventana entre 2 vacaciones

```python
def sesiones_disponibles(start, end):
    """Sesiones de gym disponibles entre 2 fechas."""
    return sesiones_en_rango(start, end)

gap = sesiones_disponibles(date(2026,3,25), date(2026,4,5))
# → 5 sesiones (MIÉ 25 mar, VIE 27 mar, LUN 30 mar, MIÉ 1 abr, VIE 3 abr)
```

### Shift del calendario completo

Si extiendes el macro N semanas:

```python
def shift_dates(original, n_semanas):
    """Desplaza una fecha N semanas adelante."""
    return original + timedelta(days=n_semanas * 7)

test_original = date(2026, 5, 4)
test_reajustado = shift_dates(test_original, 6)  # +6 sem
# → date(2026, 6, 15)  ← Mon 15 jun ✓
```

## Errores típicos en aritmética calendario

1. **17 semanas ≠ 17 días × 7** si cuentas días inclusive vs exclusive
   - Inclusive (día inicio + N-1 días después): 7 días = 1 semana
   - Mejor usar `+ timedelta(days=N*7)` para semana N+1 inicio
2. **Olvidar que 2027 NO es bisiesto** (2024, 2028 sí · 2027 no)
3. **Confundir "sem 17" (numeración programa)** con "sem 17 calendario" (contando todas las semanas calendario incluyendo RECON y vacaciones)
4. **Asumir que macros encadenan sin buffer** · convención del plan de ejemplo = macro 1 → macro 2 sin buffer, macro 2 → macro 3 con 1 sem buffer

## Conversión semana-a-fecha del plan ejemplo

| Sem | Fechas (original) | Fechas (reajustado +6 sem) |
|---|---|---|
| 0 | 12-18 ene 2026 | 12-18 ene 2026 |
| 1 | 19-25 ene | 19-25 ene |
| 4 | 9-15 feb | 9-15 feb (RECAL) |
| 5 | 16-22 feb (deload) | 16-22 feb |
| 8 (intens 8) | 9-15 mar | (con vacación) sem 8a parcial + RECON + sem 8b 20-26 abr |
| 9 (RECAL) | 16-22 mar | 27 abr-3 may |
| 12 (HITO 3) | 6-12 abr | (con vacación 2) 18-24 may |
| 16 (TEST) | 4-10 may | 15-21 jun |
| 17 (deload post) | 11-17 may | 22-28 jun |

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
