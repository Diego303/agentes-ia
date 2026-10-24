---
name: feature-resume
description: Reanuda de forma segura una feature interrumpida del harness reconciliando estado, eventos, lock, gate, intentos, coste y artefactos antes de lanzar ningún agente. Úsala cuando el humano diga reanudar, continuar, retomar o recuperar una feature, al abrir una sesión con features in_progress o blocked, o cuando estado y artefactos puedan estar desalineados.
argument-hint: "[FEATURE-ID]"
---

# Feature resume

## Procedimiento

1. `python3 .claude/tools/feature.py status <ID>`: fase, intentos, GATE#1,
   lock, eventos válidos, coste y siguiente acción.
2. `python3 .claude/tools/validate_harness.py --feature <ID>`: cualquier error
   es una inconsistencia que se resuelve antes de avanzar.
3. Lee los últimos eventos de `.claude/state/<ID>/event.log`: la última
   transición y el último `subagent_stop` de cada agente.
4. **Lock**: si está activo y es reciente, otra sesión puede estar trabajando
   en la feature; pregunta al humano antes de seguir. Si parece obsoleto, pide
   confirmación para continuar.
5. **GATE#1 pendiente**: nunca se infiere una aprobación; espera `/approve` o
   `/reject`.
6. **Fase de trabajo interrumpida** (exploration, design, implementation,
   verification): si no hay `subagent_stop` del agente de la fase posterior a
   `phase_entered_at`, relánzalo con la misma cabecera (mismo `ATTEMPT`). Si sí
   lo hay y su artefacto existe, ejecuta la transición que corresponda; el
   motor comprobará las guards.
7. **blocked**: presenta `blocked_reason` y las salidas humanas posibles
   (`replan`, `retry_exploration`, `retry_build`, `retry_verification`, `cancel`).

## Salida

Fase real, estado de GATE#1 y del lock, último runtime válido, intentos, coste
y la siguiente acción segura, o la inconsistencia concreta que necesita al humano.

## Límites

- No edites `state.yaml` ni `event.log` a mano (el hook de seguridad lo impide):
  el estado cambia solo con transiciones.
- Nunca concedas un segundo repair automático; eso es `retry_build`, una
  decisión humana.
