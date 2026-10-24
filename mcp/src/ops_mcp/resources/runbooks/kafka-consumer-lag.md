# Lag de consumidores Kafka

## Síntomas

- El lag de un consumer group crece de forma sostenida (más de 10.000 mensajes o más de 5 minutos de retraso).
- Procesamiento retrasado: pedidos que no se confirman, notificaciones tardías.

## Diagnóstico

1. Comprueba cuántas réplicas del consumidor están listas frente a las deseadas: una réplica caída reduce el throughput.
2. Revisa si hay rebalanceos frecuentes del consumer group.
3. Comprueba errores de procesamiento que provoquen reintentos en bucle sobre el mismo mensaje (poison message).
4. Revisa el número de particiones: no se puede escalar por encima del número de particiones.

## Mitigación

- Restaura las réplicas que falten o escala el consumidor hasta el número de particiones.
- Envía los mensajes que fallan siempre a la dead letter queue para desbloquear la partición.
- Si un despliegue reciente cambió el procesamiento por lotes o el backoff, valora el rollback.

## Escalado

Equipo propietario. SEV3 si solo hay retraso; SEV2 si hay pérdida de mensajes o el retraso supera 1 hora en pedidos.
