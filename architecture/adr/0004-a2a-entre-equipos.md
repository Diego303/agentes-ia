# 0004 · A2A solo para delegar entre agentes de equipos distintos

**Estado**: aceptada

## Contexto

La política de cambios pertenece a otro equipo, que la despliega y versiona por su cuenta.

## Decisión

Ese equipo expone un agente A2A (protocolo 1.0) con Agent Card, skill `evaluate_change` y
artefacto estructurado. El agente de operaciones lo consume como una tool más. Dentro de un
mismo equipo, una tool MCP o una función bastan.

## Alternativas

- **Copiar la política en el agente**. Se desincroniza y rompe la propiedad del equipo.
- **API REST**. Funciona, pero A2A aporta descubrimiento, ciclo de vida de tareas
  (incluidos `input-required` y `rejected`) y un contrato común entre frameworks.

## Consecuencias

- El change advisor es determinista. A2A no obliga a usar un LLM, y el cliente no cambia si
  mañana lo hay.
- La respuesta de otro agente es un dato no confiable para quien la recibe.
