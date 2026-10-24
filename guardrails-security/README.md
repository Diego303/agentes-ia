# guardrails-security

Guardrails deterministas del agente, sin dependencias ni llamadas a modelos. La idea
central es que **la detección no es la defensa**. La defensa es el diseño: mínimo
privilegio, aprobación humana para efectos y bloqueo de efectos cuando el contexto contiene
datos sospechosos. La detección solo decide cuándo un turno queda contaminado.

| Módulo | Qué hace |
| --- | --- |
| [`policy.py`](src/opsagent_guardrails/policy.py) | lista blanca de tools, límite de llamadas, aprobación humana para efectos y **denegación de efectos si la sesión está contaminada** |
| [`injection.py`](src/opsagent_guardrails/injection.py) | detector heurístico (ES/EN): anulación de instrucciones, cambio de rol, exfiltración del prompt, delimitadores falsos, enlaces de exfiltración, caracteres ocultos, coerción de acciones |
| [`spotlight.py`](src/opsagent_guardrails/spotlight.py) | envuelve cada resultado de tool como `<untrusted_data>` y neutraliza cierres falsos del bloque |
| [`redaction.py`](src/opsagent_guardrails/redaction.py) | redacta claves, tokens, JWT, cadenas de conexión, emails, IBAN y tarjetas (con Luhn) en respuestas y resultados de tools |

## La "tríada letal"

Un agente es explotable cuando junta tres cosas: datos privados, contenido no confiable y
capacidad de actuar o comunicar hacia fuera. El agente de referencia rompe la tríada en
varias capas:

1. **Contenido no confiable**: todo resultado de tool entra redactado y marcado como dato.
2. **Capacidad de actuar**: una sola tool con efectos, siempre con aprobación humana, y
   denegada sin opción de aprobar si la sesión leyó algo sospechoso.
3. **Comunicación hacia fuera**: el agente no tiene red. En Kubernetes, solo el gateway sale
   a Internet, y solo al puerto 443.

## Cifras del detector y sus límites

`uv run opsagent-bench` lo mide sobre [`injection.yaml`](../evals-and-benchmarks/datasets/injection.yaml)
(20 ataques y 20 textos operativos benignos con palabras "peligrosas"): **precisión 1,0,
recall 1,0, 0 falsos positivos**. El CI exige al menos 0,95 de precisión y 0,85 de recall.

El corpus es pequeño y de la misma distribución que las reglas. Un atacante adaptativo
encontrará frases que no detecta, y por eso un fallo de detección no debe conceder nada. Lo
que de verdad protege es que, aunque la inyección pase inadvertida, el agente no puede
ejecutar efectos sin un humano. Para más recall, añade un clasificador (un modelo pequeño o
un servicio dedicado) como señal adicional de contaminación, nunca como única barrera.

## Modelo de amenazas

[`THREAT-MODEL.md`](THREAT-MODEL.md) relaciona el OWASP Top 10 for Agentic Applications con
las mitigaciones del sistema y el riesgo residual.
