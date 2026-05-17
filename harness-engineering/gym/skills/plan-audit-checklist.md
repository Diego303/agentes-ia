---
name: plan-audit-checklist
description: Invoke when running a final audit on a training plan before delivery or before user executes it. Exhaustive checklist covering structure, math, dates, cross-references, consistency, and common error patterns. Use by plan-auditor agent or solo.
---

# Plan Audit Checklist · checklist exhaustivo para auditar planes

> **Nota · ejemplos basados en perfil de referencia.** Los números concretos (PRs, pesos, targets, fechas) que aparecen en este skill son del perfil intermedio natural masculino que se usó como caso de estudio: **~80 kg corporal · PR bench 85 kg · PR sentadilla 110 kg · PR HT 120×8 · PR prensa 190×8 · target bench 92,5 kg · 17 semanas · 3 días/sem · 6 h sueño consolidadas**. **Adapta los valores a tu usuario antes de aplicar.**

## Capa 1 · estructura técnica (HTML)

### Validación HTML

- [ ] DOCTYPE html presente
- [ ] `<html lang="es">` con atributo idioma
- [ ] `<head>` y `<body>` cerrados
- [ ] Cierre `</html>` al final del documento

### Etiquetas balanceadas (cuenta tag open vs tag close)

```python
import re
with open('plan.html') as f: c = f.read()
for t in ['div', 'section', 'table', 'tr', 'td', 'th', 'dl', 'dt', 'dd', 'ul', 'ol', 'li', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'span', 'code', 'strong', 'em', 'a']:
    o = len(re.findall(f'<{t}[\\s>]', c))
    cl = len(re.findall(f'</{t}>', c))
    assert o == cl, f'{t}: {o} abiertos / {cl} cerrados'
```

### Validación de assets

- [ ] Google Fonts link válido (Fraunces · Newsreader · JetBrains Mono)
- [ ] Sin recursos externos rotos
- [ ] CSS en `<style>` o linked
- [ ] Print stylesheet (`@media print`) incluido

## Capa 2 · matemática (pesos, % , Epley)

### Bench dual columna (si aplica)

Verifica para cada semana:
```python
def red(x): return round(x/2.5)*2.5
# col 80 = round_2.5(col_85 × 80/85)
for sem, (lun_85, vie_85) in tabla_85.items():
    assert tabla_80[sem][0] == red(lun_85 * 80/85)
    assert tabla_80[sem][1] == red(vie_85 * 80/85)
```

Atención a errores típicos:
- Sem 4 vie col 80 = 65 × 0,94 = 61,1 → 60 (no 62,5)
- Sem 6 vie col 80 = mismo cálculo → 60
- Si sem 4 y sem 6 col 85 son iguales (65), col 80 también debe ser igual

### Squat Plan B (si aplica)

```python
# Plan B = Plan A × 1,2
for sem in range(1, 16):
    assert plan_b[sem] == plan_a[sem] * 1.2
```

### Epley en ejemplos numéricos

```python
def epley(peso, reps): return peso * (1 + reps/30)
# Verifica todos los ejemplos numéricos del manual
assert round(epley(65, 7), 2) == 80.17  # → 80
assert round(epley(72.5, 8), 2) == 91.83  # → 92,5
assert round(epley(67.5, 8), 2) == 85.5
assert round(epley(75, 5), 2) == 87.5
assert round(epley(70, 4), 2) == 79.33
```

### Macros nutricionales (consistencia)

- [ ] Si dice "X g/kg de Y", verificar que X × Y ≈ rango g declarado
- [ ] Ejemplo error: "200-240 g a 2-2,5 g/kg" para 80 kg → matemáticamente imposible (200/80=2,5 y 240/80=3, no 2-2,5)
- [ ] Fix: o cambia rango g (160-200) o cambia g/kg (2,5-3)

## Capa 3 · fechas (día de la semana, duración, conteos)

### Día de la semana para cada fecha mencionada

```python
from datetime import date
dias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
fechas_clave = [
    ('Inicio macro', date(2026,5,18), 'LUN'),
    ('Test bench', date(2026,X,Y), 'LUN'),
    ('Test sentadilla', date(2026,X,Y), 'VIE'),
    ('Sem 17 fin', date(2026,X,Y), 'DOM'),
    ('Macro 2 inicio', date(2026,X,Y), 'LUN'),
    ('Macro 2 fin', date(2027,X,Y), 'DOM'),
    ('Macro 3 inicio', date(2027,X,Y), 'LUN'),
    ('Macro 3 fin', date(2027,X,Y), 'DOM'),
]
for n, f, e in fechas_clave:
    assert dias[f.weekday()] == e, f'{n}: {f} = {dias[f.weekday()]} (esperado {e})'
```

### Duración 17 semanas = 119 días

```python
inicio = date(2026, X, Y)
fin = date(2026, X, Y)
assert (fin - inicio).days + 1 == 119  # 17 sem
```

### Conteos de sesiones (vacaciones, perdidas, disponibles)

```python
def sesiones(start, end):
    count = 0
    d = start
    while d <= end:
        if d.weekday() in (0, 2, 4): count += 1
        d += timedelta(days=1)
    return count

# Verificar conteos del manual
assert sesiones(vac_inicio, vac_fin) == sesiones_perdidas_declaradas
```

## Capa 4 · consistencia interna

### Cabecera mental coherente

- [ ] PRs mencionados en §00 = PRs mencionados en §10 hitos = PRs mencionados en §16 cheat = PRs mencionados en cabecera Telegram §13
- [ ] Si el PR cambia (ej. tras test), se actualiza en TODAS las secciones

### Targets macro coherentes

- [ ] Target bench en §00 = target en §11 test = target en §16 resumen ejecutivo
- [ ] Target sentadilla similar
- [ ] Si el target cambia (raro), actualizar en todas partes

### Fechas test coherentes

- [ ] Test bench fecha mencionada en §00 hardcoded = §11 protocolo = §16 calendario
- [ ] Test sentadilla mismo
- [ ] Sem 17 deload post-test fecha coherente

### Numeración de semanas tras inserción de RECON

Si se han insertado semanas adicionales (RECON, parciales, buffer):
- [ ] La numeración elegida (programa vs calendario) es coherente
- [ ] No hay mezcla "sem 17 (post-test)" en una sección + "sem 23 (post-test)" en otra
- [ ] El calendario §16 y las referencias narrativas usan la misma numeración

### Cross-references válidas

- [ ] Cada "ver §X" apunta a sección que existe
- [ ] Cada link "#anchor" tiene su `id="anchor"` correspondiente
- [ ] Topnav incluye todas las secciones principales

### Tablas vs narrativa

- [ ] Si la tabla §08 dice "sem 8 vie = 4×4 @ 67,5 kg", ninguna sesión RECON o ejemplo dice "4×6 @ 67,5 kg para sem 8"
- [ ] Las prescripciones de los day-cards de RECON respetan las reps de la sem objetivo

## Errores típicos detectados en sesiones previas

### Error 1 · pesos sem 6+ escritos como "%" cuando eran kg

Síntoma: tabla dice "3×3 @ 75 %" pero plan original prescribía 75 kg
Impacto: si usuario aplica 75 % de 1RM nuevo (90), saca 67,5 kg (12 % menos del plan)
Fix: revertir a kg absolutos

### Error 2 · doble columna mal en una celda

Síntoma: sem 4 vie col 80 = 62,5 (debería ser 60 por el cálculo 65 × 0,94 = 61,1 → más cercano 60)
Detección: verificar consistencia con sem 6 vie col 80 (mismo cálculo, debe dar mismo resultado)
Fix: cambiar a 60

### Error 3 · inconsistencia numeración post-fusión

Síntoma: tras insertar RECON, algunas referencias dicen "sem 23 deload" pero calendar dice "sem 17"
Fix: unificar a "sem 17 reajustada" en todas las referencias

### Error 4 · % test ambiguos para múltiples lifts

Síntoma: "Intento 1 · 95 % target" aplicado a bench (87,5/92,5 = 94,6 % ≈ 95% ✓) y sentadilla (110/125 = 88 % ≠ 95 %)
Fix: separar por lift o renombrar como "apertura/intermedio/target"

### Error 5 · reps incorrectas en RECON

Síntoma: "Bench pausa 4×6 al peso de sem 8 vie" cuando sem 8 vie original = 4×4
Fix: alinear reps con la sem objetivo (4×4)

### Error 6 · proteína g vs g/kg mismatch

Síntoma: "200-240 g a 2-2,5 g/kg" para 80 kg
Matemática: 200/80 = 2,5 y 240/80 = 3, no 2-2,5
Fix: 160-200 g (a 2-2,5 g/kg para 80 kg) o renombrar a 2,5-3 g/kg

### Error 7 · fechas hito vs fechas calendario

Síntoma: §10 dice "Hito 3 sem 12 = 10-16 ago" pero calendar dice "sem 12 reajustada = 21-27 sep"
Fix: actualizar fechas de hitos para reflejar reajuste

## Output del audit

```
AUDITORÍA · [nombre del plan] · [fecha]

═══════════════════════════════════════════════════
HALLAZGOS CRÍTICOS (afectan ejecución directa)
═══════════════════════════════════════════════════
[N] Hallazgo · §X línea Y
  - Descripción del error
  - Impacto: [pérdida de progreso / riesgo lesión / etc.]
  - Fix propuesto: [cambio específico]

═══════════════════════════════════════════════════
HALLAZGOS MEDIOS (no rompen plan pero confunden)
═══════════════════════════════════════════════════
...

═══════════════════════════════════════════════════
HALLAZGOS MENORES (cosméticos)
═══════════════════════════════════════════════════
...

═══════════════════════════════════════════════════
RESUMEN
═══════════════════════════════════════════════════
Total hallazgos: X
- Críticos: N
- Medios: N
- Menores: N

Estado: [APTO PARA EJECUTAR / REQUIERE CORRECCIONES ANTES DE EJECUTAR]
```

## Niveles de severidad

| Severidad | Definición |
|---|---|
| **Crítico** | Afecta la ejecución directa · pesos mal · fechas mal · prescripción contradictoria |
| **Medio** | Confunde al usuario pero no rompe el plan · numeración inconsistente · cross-reference roto |
| **Menor** | Cosmético · typo · etiqueta inconsistente |

Un plan con crítico ≥ 1 NO se entrega · requiere corrección.
Un plan con medio ≥ 3 conviene revisar antes de entrega.
Un plan con solo menores se puede entregar con nota.
