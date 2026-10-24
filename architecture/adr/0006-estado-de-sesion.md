# 0006 · Sesiones append-only en memoria detrás de un protocolo

**Estado**: aceptada, con límite conocido

## Contexto

El agente guarda el historial de cada sesión y las acciones pendientes de aprobación. Los
modelos actuales invalidan los bloques de razonamiento si se editan turnos anteriores.

## Decisión

`SessionStore` como protocolo, con `InMemorySessionStore` (TTL y LRU). El historial solo
crece; una respuesta incompleta no se añade.

## Consecuencias

- El agente se despliega con **una réplica** (`strategy: Recreate`). Un reinicio pierde las
  sesiones en curso, aceptable para conversaciones de guardia cortas.
- Para escalar: implementar `SessionStore` sobre Redis o PostgreSQL. No cambia nada más.
- Las conversaciones largas se compactan con las funciones de la API, no reescribiendo mensajes.
