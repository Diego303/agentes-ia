# 0002 · Gateway LiteLLM delante del proveedor; la app usa el SDK nativo

**Estado**: aceptada

## Contexto

Varias aplicaciones y agentes consumirán modelos. Repartir claves de proveedor, reintentos,
fallbacks y límites de gasto en cada una es inseguro y difícil de auditar.

## Decisión

Todas las llamadas pasan por LiteLLM. La aplicación usa el SDK de Anthropic contra el
endpoint `/v1/messages` del gateway con una clave del gateway. Los nombres de modelo son los
IDs oficiales.

## Alternativas

- **Llamada directa al proveedor**. Más simple, pero sin un único punto para claves,
  presupuesto y política.
- **Endpoint compatible con OpenAI del gateway**. Pierde los tipos, los errores tipados, los
  spans y las funciones propias de Claude (thinking, `output_config`).
- **Gateway gestionado de la nube**. Válido; LiteLLM se eligió por ser portable y desplegable
  en el mismo clúster.

## Consecuencias

- Verificado: `thinking` y `output_config` pasan intactos, y el fallback Opus → Sonnet
  funciona ante 529.
- El presupuesto sin base de datos es por réplica. Para presupuestos por consumidor, LiteLLM
  con PostgreSQL y *virtual keys*.
- Un componente más en el camino crítico: dos réplicas, PDB y probes.
