# 0001 · Bucle de tool use propio, sin framework de agentes

**Estado**: aceptada

## Contexto

El agente necesita controles en puntos concretos del bucle:
- política por tool antes de ejecutar;
- análisis de cada resultado antes de devolverlo al modelo;
- pausa para aprobación humana y reanudación en otra petición HTTP;
- límites de pasos;
- historial append-only;
- trazas por paso.

## Decisión

Bucle manual sobre `client.messages.create` del SDK oficial de Anthropic
([`agent.py`](../../reference-agent/src/opsagent/agent.py)), con razonamiento adaptativo y
`effort` configurable.

## Alternativas

- **Tool Runner del SDK** (beta). Elimina el bucle, y sus hooks por turno cubren aprobación y
  modificación de resultados. Pero la reanudación entre peticiones HTTP y la contaminación por
  sesión quedan más claras en un bucle explícito, y no depende de una API beta.
- **LangGraph y similares**. Útiles con grafos grandes o persistencia gestionada. Aquí añadirían
  una abstracción sobre unas 150 líneas, justo donde están los controles de seguridad.
- **Claude Agent SDK o Managed Agents**. Adecuados para agentes con sistema de archivos o
  sandbox gestionado. Este agente solo necesita tools propias.

## Consecuencias

- Cada control es visible y testeable con un modelo con guion.
- El equipo mantiene el bucle: los cambios de API (*stop reasons*, thinking, *refusal*) hay
  que incorporarlos a mano. Los tests de contrato del historial lo protegen.
