# Latencia p95 elevada

## Síntomas

- La latencia p95 supera el SLO (300 ms para APIs internas, 800 ms para APIs de cara al cliente) durante más de 10 minutos.
- Timeouts en los clientes y aumento de reintentos.

## Diagnóstico

1. Distingue entre latencia propia y de dependencias usando las trazas distribuidas: busca el span más lento de la traza.
2. Revisa saturación: CPU throttling, memoria cercana al límite, pools de conexiones al máximo, colas de hilos.
3. Revisa consultas lentas en la base de datos y bloqueos.
4. Un pool de conexiones pequeño provoca esperas largas antes de obtener conexión: latencia alta seguida de errores 503.

## Mitigación

- Escala horizontalmente si la causa es carga y hay margen en el clúster.
- Ajusta el tamaño del pool o los timeouts solo con un cambio revisado; si la causa es un despliegue, haz rollback.
- Activa caché o degradación de funcionalidades no críticas.

## Escalado

Si la latencia afecta a pagos o login durante más de 15 minutos, declara un incidente SEV2.
