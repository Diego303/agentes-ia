# Tasa de errores 5xx elevada

## Síntomas

- La tasa de respuestas 5xx de un servicio supera el 2 % durante más de 5 minutos.
- Alertas `HighErrorRate` o `SLOBurnRateFast` en el canal de guardia.
- Los servicios que dependen de él empiezan a fallar en cascada (por ejemplo, checkout-web cuando falla payments-api).

## Diagnóstico

1. Comprueba si hubo un despliegue en los 30 minutos anteriores al inicio de los errores. Es la causa más frecuente.
2. Revisa el estado de las réplicas: si están listas, el fallo es de la aplicación o de una dependencia, no de capacidad.
3. Busca en los logs el código concreto (500, 502, 503, 504). Un 503 sostenido suele indicar saturación de un pool de conexiones o de una dependencia.
4. Comprueba las dependencias aguas abajo (base de datos, proveedores externos).

## Mitigación

- Si los errores empezaron con un despliegue reciente, la mitigación preferida es el **rollback** a la versión anterior (ver runbook de rollback). No se depura en producción con el servicio degradado.
- Si no hay despliegue reciente y la causa es una dependencia, activa el circuit breaker o la degradación controlada.
- Declara un incidente: SEV2 si el error supera el 5 % en un servicio tier 0; SEV1 si hay pérdida total de servicio de pago o de login.

## Escalado

Avisa al equipo propietario del servicio. Para servicios tier 0, avisa también al incident commander de guardia.
