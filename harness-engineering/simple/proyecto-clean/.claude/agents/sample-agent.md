---
name: sample-agent
description: Plantilla de agente custom con el contrato de 5 secciones. Usar cuando
  se quiere clonar este SKILL.md como punto de partida para un agente nuevo, ajustando
  name, description, tools y model.
tools: Read, Grep
model: sonnet
color: cyan
memory: project
---

# sample-agent

> **Reemplaza este archivo con tu propio agente.** Sigue el contrato de 5
> secciones que usan los agentes de orquestación en `.claude/agents/`.

## Rol
[Una frase describiendo la responsabilidad **única** de este agente. Si
necesitas dos frases, probablemente son dos agentes.]

## Inputs esperados
- [Qué archivo o artefacto del paso anterior necesita.]
- [Qué partes del repo necesita leer.]
- [Qué información humana asume disponible.]

## Procedimiento
1. [Primer paso concreto.]
2. [Segundo paso.]
3. [Continúa numerando hasta el último paso. Cada paso debe ser observable
   por un humano que mira tu output.]


### Event logging (obligatorio)

Antes de empezar tu trabajo real, appendea una línea a `<bundle>/state/<feature-id>/event.log`:

```jsonl
{"timestamp": "<ISO-8601-UTC>", "feature_id": "<id>", "agent": "sample-agent", "event": "started"}
```

Al terminar exitosamente:

```jsonl
{"timestamp": "<ISO-8601-UTC>", "feature_id": "<id>", "agent": "sample-agent", "event": "completed", "artifact": "<path-relativo>", "duration_ms": <N>}
```

Si fallas:

```jsonl
{"timestamp": "<ISO-8601-UTC>", "feature_id": "<id>", "agent": "sample-agent", "event": "failed", "error": "<mensaje>"}
```

Tu `agent` ID debe ser exactamente `sample-agent` (matching el `name:` de este archivo).
Esto es crítico para que `harness events` verifique multi-agencia.

## Output
- [Ruta exacta del archivo que escribe, con sus secciones esperadas.]
- [Otros side-effects bien acotados.]

**Siguiente paso**: [Quién lee tu artefacto. Sé explícito: nombre del
agente o el gate humano. Ej.: "**Proposer** lee tu `mi-output.md` para
formular la propuesta".]

**Cuándo parar y pedir ayuda**:
- [Inputs faltantes: ¿qué artefacto previo es bloqueante? Documenta el
  fallback si lo hay; si no, para.]
- [Ambigüedad irreductible: ¿qué tipo de pregunta no debes resolver tú?]
- [Dependencia externa caída: ¿qué pasa si el comando/herramienta falla?]

## Anti-patterns
- ❌ [Algo que este agente NO debe hacer aunque sea tentador.]
- ❌ [Otra cosa.]
- ❌ [Mezclarse con la responsabilidad de otro agente — dilo explícito.]
