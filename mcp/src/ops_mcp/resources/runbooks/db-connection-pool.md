# Agotamiento del pool de conexiones a base de datos

## Síntomas

- Errores 503 o `TimeoutError: could not acquire connection` en los logs.
- Latencia que crece de golpe con carga moderada.
- Métrica `db_pool_in_use` igual a `db_pool_max` de forma sostenida.

## Diagnóstico

1. Compara el tamaño del pool con la concurrencia real: réplicas × peticiones simultáneas por réplica.
2. Revisa si un despliegue reciente cambió el tamaño del pool o el cliente de base de datos.
3. Busca conexiones que no se devuelven (fugas) o transacciones largas.
4. Comprueba que la base de datos no está al límite de `max_connections`.

## Mitigación

- Si un despliegue reciente redujo el pool, haz rollback.
- Aumentar el pool exige revisar el límite de conexiones de la base de datos: un pool grande en muchas réplicas puede tumbarla.
- Reduce la concurrencia temporalmente o activa limitación de tráfico.

## Escalado

Equipo propietario del servicio y equipo de plataforma de datos.
