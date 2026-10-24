---
name: plan-audit-checklist
description: Invoke when running a final audit on a training plan before delivery or before user executes it. Exhaustive checklist covering structure, math, dates, cross-references, consistency, and common error patterns. Use by plan-auditor agent or solo.
---

# Plan Audit Checklist · checklist exhaustivo para auditar planes

> Los números de los ejemplos son ilustrativos: recalcula con los datos de tu usuario. Ejemplo ilustrativo (perfil ficticio): persona intermedia de 75 kg · 1RM banca 100 kg · sentadilla 140 kg · hip thrust 150×8 · prensa 240×8 · target banca 105 kg · macro de 17 semanas · 3 días/sem.

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
# col 95 = round_2.5(col_100 × 95/100)
for sem, (lun_100, vie_100) in tabla_100.items():
    assert tabla_95[sem][0] == red(lun_100 * 95/100)
    assert tabla_95[sem][1] == red(vie_100 * 95/100)
```

Atención a errores típicos:
- Sem 4 vie col 95 = 77,5 × 0,95 = 73,6 → 72,5 (no 75)
- Sem 6 vie col 95 = mismo cálculo → 72,5
- Si sem 4 y sem 6 col 100 son iguales (77,5), col 95 también debe ser igual

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
assert round(epley(75, 10), 2) == 100.0  # → 100
assert round(epley(82.5, 8), 2) == 104.5  # → ≈105
assert round(epley(90, 5), 2) == 105.0
assert round(epley(80, 7), 2) == 98.67
assert round(epley(70, 4), 2) == 79.33
```

### Macros nutricionales (consistencia)

- [ ] Si dice "X g/kg de Y", verificar que X × Y ≈ rango g declarado
- [ ] Ejemplo error: "190-225 g a 2-2,5 g/kg" para 75 kg → matemáticamente imposible (190/75≈2,5 y 225/75=3, no 2-2,5)
- [ ] Fix: o cambia rango g (150-190) o cambia g/kg (2,5-3)

## Capa 3 · fechas (día de la semana, duración, conteos)

### Día de la semana para cada fecha mencionada

```python
from datetime import date
dias = ['LUN', 'MAR', 'MIÉ', 'JUE', 'VIE', 'SÁB', 'DOM']
fechas_clave = [
    ('Inicio macro', date(2026,1,12), 'LUN'),
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

- [ ] Si la tabla §08 dice "sem 8 vie = 4×4 @ 82,5 kg", ninguna sesión RECON o ejemplo dice "4×6 @ 82,5 kg para sem 8"
- [ ] Las prescripciones de los day-cards de RECON respetan las reps de la sem objetivo

## Errores típicos detectados en sesiones previas

### Error 1 · pesos sem 6+ escritos como "%" cuando eran kg

Síntoma: tabla dice "3×3 @ 87,5 %" pero plan original prescribía 87,5 kg
Impacto: si usuario aplica 87,5 % sobre el 1RM conservador (95), saca 83,1 → 82,5 kg (≈6 % menos del plan)
Fix: revertir a kg absolutos

### Error 2 · doble columna mal en una celda

Síntoma: sem 4 vie col 95 = 75 (debería ser 72,5 por el cálculo 77,5 × 0,95 = 73,6 → más cercano 72,5)
Detección: verificar consistencia con sem 6 vie col 95 (mismo cálculo, debe dar mismo resultado)
Fix: cambiar a 72,5

### Error 3 · inconsistencia numeración post-fusión

Síntoma: tras insertar RECON, algunas referencias dicen "sem 23 deload" pero calendar dice "sem 17"
Fix: unificar a "sem 17 reajustada" en todas las referencias

### Error 4 · % test ambiguos para múltiples lifts

Síntoma: "Intento 1 · 95 % target" aplicado a bench (100/105 = 95,2 % ≈ 95% ✓) y sentadilla (140/150 = 93,3 % ≠ 95 %)
Fix: separar por lift Y aplicar la "regla universal" definida en `[[test-day-protocol]]` (apertura = max(PR previo, 95% target) · intermedio = punto medio · target = del macro)

### Error 5 · reps incorrectas en RECON

Síntoma: "Bench pausa 4×6 al peso de sem 8 vie" cuando sem 8 vie original = 4×4
Fix: alinear reps con la sem objetivo (4×4)

### Error 6 · proteína g vs g/kg mismatch

Síntoma: "190-225 g a 2-2,5 g/kg" para 75 kg
Matemática: 190/75 ≈ 2,5 y 225/75 = 3, no 2-2,5
Fix: 150-190 g (a 2-2,5 g/kg para 75 kg = 150-187,5 g) o renombrar a 2,5-3 g/kg

### Error 7 · fechas hito vs fechas calendario

Síntoma: §10 dice "Hito 3 sem 12 = 30 mar-5 abr" pero calendar dice "sem 12 reajustada = 11-17 may"
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
