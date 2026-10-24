---
description: Muestra el progreso global del vault AI-103: archivos completados, pendientes, por dominio, porcentaje, archivos críticos pendientes, sugerencia de siguiente paso.
allowed-tools: Read, Bash, Grep, Glob
---

# /ai103-status — Estado del vault AI-103

Eres el **orquestador**. Tu tarea: dar un dashboard claro del progreso.

## Pasos

### 1. Inventario

1. Lee `INDICE-MAESTRO.md`.
2. Cuenta archivos por estado: ✅ completados, 🟡 en revisión, ⬜ pendientes.
3. Desglosa por dominio (0-foundational, A, B, C, D, E).
4. Identifica los más críticos (🔥 alta prioridad) pendientes.

### 2. Output al usuario

Formato:

```markdown
# 📊 Estado del vault AI-103

**Verificado:** <fecha actual>

## Resumen global

- Total: 168 archivos
- ✅ Completados: <N> (<X> %)
- 🟡 En revisión: <N>
- ⬜ Pendientes: <N>

## Por dominio

| Dominio | Peso | ✅ | ⬜ | Total | % |
|---|---|---|---|---|---|
| 0. Foundational | — | <X> | <Y> | 8 | <Z> % |
| A. Plan & Manage | 25-30 % | <X> | <Y> | 32 | <Z> % |
| B. GenAI + Agents | 30-35 % | <X> | <Y> | 45 | <Z> % |
| C. Computer Vision | 10-15 % | <X> | <Y> | 28 | <Z> % |
| D. Text Analysis | 10-15 % | <X> | <Y> | 30 | <Z> % |
| E. Information Extraction | 10-15 % | <X> | <Y> | 25 | <Z> % |

## Archivos críticos pendientes (🔥 alta prioridad)
- [⬜] <slug>
- [⬜] <slug>
- ...

## Siguiente sugerido
`/ai103-write <slug>` — <breve razón>

## Comandos disponibles
- `/ai103-next` — siguiente pendiente según orden pedagógico
- `/ai103-write <slug>` — archivo específico
- `/ai103-review <slug>` — re-revisar archivo existente
- `/ai103-brief <slug>` — expandir brief antes de generar
- `/ai103-batch <dominio>` — generar varios archivos en serie
```

### 3. Reglas

- No modifiques nada.
- Output ≤ 400 palabras.
- Si hay incongruencias (archivo ✅ que no existe en disco o viceversa), repórtalas.

$ARGUMENTS
