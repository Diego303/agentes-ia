# Pods en CrashLoopBackOff

## Síntomas

- Réplicas listas por debajo de las deseadas y pods en estado `CrashLoopBackOff`.

## Diagnóstico

1. Revisa los logs del contenedor anterior (`--previous`) para ver el error de arranque.
2. Comprueba eventos del pod: `OOMKilled` indica límite de memoria insuficiente; fallos de probes indican arranque lento o dependencia caída.
3. Verifica que los secretos y la configuración que necesita existen.

## Mitigación

- Si empezó con un despliegue, haz rollback.
- Si es `OOMKilled`, ajusta los límites de memoria con un cambio revisado.
- Si una probe es demasiado estricta, ajusta `initialDelaySeconds` o usa una startupProbe.

## Escalado

Equipo propietario del servicio.
