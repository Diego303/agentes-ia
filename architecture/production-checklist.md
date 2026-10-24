# Checklist de producción para un agente de IA

Lo que debe ser cierto antes de exponer un agente a usuarios reales. Entre paréntesis, dónde
lo resuelve este repositorio; ✗ marca lo que queda por hacer en el sistema de referencia.

## Comportamiento y calidad

- [ ] Evals de punta a punta con casos reales, graders de trayectoria y umbral en CI (`evals-and-benchmarks`).
- [ ] Juez LLM calibrado contra etiquetas humanas, con kappa ≥ 0,6 (`--calibrate`).
- [ ] Fiabilidad medida con repeticiones (`--repeat`), no solo con la media.
- [ ] Gestión explícita de `refusal`, `max_tokens` y límites de pasos (`agent.py`).
- [ ] Prompt y tools versionados junto al código; cada cambio de modelo pasa por las evals.

## Seguridad

- [ ] Modelo de amenazas con OWASP Agentic Top 10 (`THREAT-MODEL.md`).
- [ ] Mínimo privilegio en tools: scopes por servidor MCP y efectos con aprobación humana.
- [ ] Datos de tools tratados como no confiables: spotlighting, detección y bloqueo de efectos.
- [ ] Sin secretos en código, imágenes ni state; secretos desde Key Vault con una identidad que solo lee los de la app (Workload Identity).
- [ ] Red *default-deny*; solo el gateway sale a Internet.
- [ ] ✗ mTLS entre servicios (service mesh o Cilium mutual auth).
- [ ] ✗ Firma y verificación de imágenes (cosign y política de admisión).

## Operación

- [ ] Una traza por petición que cruza el agente, el gateway, MCP y A2A (OTel GenAI).
- [ ] Coste por conversación y por modelo visible y con alerta (`opsagent.llm.cost`).
- [ ] Reintentos y fallback de modelo en el gateway; timeouts en cada llamada.
- [ ] Probes, PDB y HPA en los servicios sin estado.
- [ ] ✗ Estado de sesión externo para tener más de una réplica del agente (ADR 0006).
- [ ] ✗ Presupuesto por consumidor con *virtual keys* del gateway (ADR 0002).
- [ ] ✗ Alertas sobre `opsagent.stop_reason` (`budget`, `refusal`) y `opsagent.guardrail.events`.

## Gobierno

- [ ] Sin prompts ni respuestas en la telemetría por defecto; el collector los borra.
- [ ] Redacción de PII y secretos en respuestas y resultados de tools.
- [ ] Registro de decisiones humanas (aprobaciones) asociado a la traza.
- [ ] ✗ Retención de conversaciones definida y documentada según la normativa aplicable.
