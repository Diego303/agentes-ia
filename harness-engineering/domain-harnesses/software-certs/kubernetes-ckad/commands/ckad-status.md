---
description: Muestra el progreso global del vault CKAD: archivos completados, pendientes, por dominio, porcentaje, archivos críticos pendientes, sugerencia de siguiente paso.
allowed-tools: Read, Bash, Grep, Glob
---

# /ckad-status — Estado del vault CKAD

Eres el **orquestador**. Tu tarea: dar un dashboard claro del progreso.

## Pasos

### 1. Inventario

1. Lee `INDICE-MAESTRO.md`.
2. Cuenta archivos por estado: ✅ completados, 🔄 en revisión, ⬜ pendientes, ⚠️ marcados para humano.
3. Desglosa por dominio (00-Foundational, A, B, C, D, E).
4. Identifica los más críticos (🔥🔥🔥 alta prioridad) pendientes.

### 2. Output al usuario

Formato:

```markdown
# 📊 Estado del vault CKAD

**Verificado:** <fecha actual>
**Kubernetes version target:** v1.35

## Resumen global

- Total: 77 archivos
- ✅ Completados: <N> (<X> %)
- 🔄 En revisión: <N>
- ⬜ Pendientes: <N>
- ⚠️ Para humano: <N>

## Por dominio

| Dominio | Peso | ✅ | ⬜ | Total | % |
|---|---|---|---|---|---|
| 00. Foundational | — | <X> | <Y> | 8 | <Z> % |
| A. Design & Build | 20 % | <X> | <Y> | 21 | <Z> % |
| B. Deployment | 20 % | <X> | <Y> | 10 | <Z> % |
| C. Observability | 15 % | <X> | <Y> | 9 | <Z> % |
| D. Environment/Config/Security | **25 %** ⭐ | <X> | <Y> | 19 | <Z> % |
| E. Services/Networking | 20 % | <X> | <Y> | 10 | <Z> % |

## Archivos críticos pendientes (🔥🔥🔥 alta prioridad)
- [⬜] <slug>
- [⬜] <slug>
- ...

## Siguiente sugerido
`/ckad-write <slug>` — <breve razón>

## Comandos disponibles
- `/ckad-next` — siguiente pendiente según orden pedagógico
- `/ckad-write <slug>` — archivo específico
- `/ckad-review <slug>` — re-revisar archivo existente
- `/ckad-brief <slug>` — expandir brief antes de generar
- `/ckad-batch <dominio>` — generar varios archivos en serie
- `/ckad-help` — menú completo
```

### 3. Reglas

- No modifiques nada.
- Output ≤ 400 palabras.
- Si hay incongruencias (archivo ✅ que no existe en disco o viceversa), repórtalas.
- Verifica filesystem real vs INDICE: `find` cada path declarado.

$ARGUMENTS
