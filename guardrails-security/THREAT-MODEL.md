# Modelo de amenazas del sistema de referencia

Referencia: OWASP Top 10 for Agentic Applications (diciembre de 2025). Activos: credenciales de
los proveedores de modelos y de los servicios, datos operativos, capacidad de declarar
incidentes (avisa a la guardia) y presupuesto.

## Fronteras de confianza

```text
operador (autenticado) ──► ops-agent ──► llm-gateway ──► proveedor de modelos (Internet)
                               │
                               ├──► ops-mcp (datos operativos, runbooks, incidentes)
                               └──► change-advisor (otro equipo, A2A)
Todo lo que vuelve de ops-mcp, change-advisor y el modelo es dato no confiable para el agente.
```

## Riesgos y mitigaciones

| Riesgo (OWASP ASI) | Cómo se materializaría aquí | Mitigación | Dónde | Riesgo residual |
| --- | --- | --- | --- | --- |
| ASI01 Agent Goal Hijack | un mensaje de despliegue ordena crear un SEV1 falso | spotlighting, detector, sesión contaminada que deniega efectos, regla en el system prompt | `guardrails-security`, `agent.py` | inyección no detectada con efectos aprobados por un humano poco atento |
| ASI02 Tool Misuse | el modelo crea incidentes innecesarios o hace bucles | lista blanca, aprobación humana para efectos, límite de llamadas y pasos | `policy.py`, `Settings` | abuso de tools de lectura (coste) dentro de los límites |
| ASI03 Identity & Privilege Abuse | el agente usa más permisos de los que necesita | scopes `ops:read`/`ops:write` en MCP, tokens por consumidor, workloads sin identidad de Azure y una identidad de sincronización con acceso secreto a secreto en Key Vault | `mcp/src/ops_mcp/auth.py`, `integrations/common/scopes.py`, `deploy/terraform` | tokens estáticos sin rotación automática (usa JWT del IdP) |
| ASI04 Agentic Supply Chain | dependencia o imagen comprometida | `uv.lock` con hashes, imágenes con versión fijada, usuario no root, procedencia de skills en el harness | `uv.lock`, `deploy/docker` | sin firma ni verificación de imágenes (cosign) todavía |
| ASI05 Unexpected Code Execution | el agente ejecuta código generado | el agente no tiene tools de ejecución de código ni de shell | diseño | — |
| ASI06 Memory & Context Poisoning | contenido envenenado persiste en la sesión | la contaminación es pegajosa por sesión, TTL de sesiones, sin memoria a largo plazo | `agent.py`, `memory.py` | runbooks envenenados en la fuente de RAG |
| ASI07 Insecure Inter-Agent Communication | respuesta A2A falsificada o con órdenes | bearer token en A2A, NetworkPolicy, respuesta tratada como dato | `a2a`, `networkpolicies.yaml` | sin mTLS entre servicios (añade un service mesh o Cilium mutual auth) |
| ASI08 Cascading Failures | caída del proveedor o del advisor tumba el agente | reintentos y fallback en el gateway, errores de tool devueltos al modelo, límites de pasos | `llm-gateway`, `tools.py` | sin circuit breaker propio hacia MCP |
| ASI09 Human-Agent Trust Exploitation | el agente convence al humano de aprobar algo dañino | la aprobación muestra la tool y los argumentos literales; la acción sensible es acotada | `agent.py` | fatiga de aprobación |
| ASI10 Rogue Agents | el agente actúa fuera de su mandato | sin red propia, una sola acción con efectos, trazas de cada decisión y evals de seguridad en CI | `deploy`, `observability`, `evals` | — |

## Otros controles

- **Secretos**: nunca en código, imágenes ni state de Terraform. En Kubernetes llegan desde
  Key Vault por el CSI driver con Workload Identity.
- **Datos en trazas**: el SDK de Anthropic exporta solo metadatos por defecto y el collector
  borra los atributos de contenido aunque alguien active el modo `content`.
- **Redacción** de secretos y PII en respuestas y en resultados de tools antes de enviarlos al modelo.
