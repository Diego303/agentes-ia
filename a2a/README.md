# a2a — change advisor

Agente [A2A](https://a2a-protocol.org) (protocolo 1.0, `a2a-sdk` 1.2) que representa al equipo de
gestión de cambios. El agente de operaciones le pregunta si una acción en producción está
permitida antes de recomendarla. Es el caso de uso que justifica A2A: **agentes de equipos
distintos, desplegados y versionados por separado, que colaboran mediante un contrato**
(Agent Card, tareas y artefactos) sin compartir código ni prompts.

## Contrato

- **Agent Card** pública en `/.well-known/agent-card.json`: nombre, skill `evaluate_change`,
  modos de entrada y salida, y esquema de seguridad `bearer`.
- **Petición**: un mensaje con un *data part* JSON
  `{"service", "action", "environment", "incident_severity", "reason"}`.
- **Respuesta**: una tarea `completed` con un artefacto `verdict`
  (`decision`: `approved` | `needs_approval` | `rejected`, más `reasons`, `conditions` y
  `required_approvers`). Una petición mal formada termina en `rejected` con el formato esperado.

## Política ([`policy.py`](src/change_advisor/policy.py))

| Caso | Decisión |
| --- | --- |
| Fuera de producción | approved |
| Despliegue o cambio de configuración durante un SEV1/SEV2 | rejected (congelación) |
| Mitigación (rollback, restart, scale) en tier 0 durante un SEV1/SEV2 | approved, con aviso al incident commander |
| Cualquier otro cambio en tier 0 | needs_approval (change manager + equipo propietario) |
| Cambio que no es mitigación en fin de semana (viernes 16:00 – lunes 08:00 UTC) | needs_approval |
| Resto | approved, con pipeline estándar y vigilancia |

**Es determinista a propósito.** Una decisión de control de cambios tiene que ser
reproducible y auditable. A2A no exige que el agente remoto sea un LLM, y el executor puede
envolver cualquier implementación (LangGraph, otro proveedor, un motor de reglas) sin que el
cliente cambie.

## Uso

```bash
A2A_TOKENS='["secreto"]' A2A_PUBLIC_URL=http://127.0.0.1:9000/ uv run change-advisor
```

```python
from change_advisor import ChangeAdvisorClient

client = ChangeAdvisorClient("http://change-advisor:9000/", token)
verdict = await client.evaluate(
    {"service": "payments-api", "action": "rollback", "incident_severity": "SEV2"}
)
```

El cliente descubre el agente por su Agent Card y usa el transporte que esta anuncia
(JSON-RPC). La instrumentación de `httpx` y ASGI propaga la traza del agente que llama.

## Seguridad

- El JSON-RPC exige bearer token (comparación en tiempo constante). La Agent Card y
  `/healthz` son públicas.
- La respuesta del advisor es un dato para el agente que llama: entra a su contexto
  envuelta como `<untrusted_data>` (ASI07, comunicación insegura entre agentes).
