# Rollback de un despliegue

## Cuándo hacerlo

- Un despliegue reciente coincide con el inicio de errores o de degradación.
- El rollback es la mitigación por defecto durante un incidente: restaura el último estado conocido como bueno y deja la investigación para después.

## Requisitos previos

- La versión anterior debe ser compatible con el esquema actual de base de datos. Si el despliegue incluyó una migración no retrocompatible, no hagas rollback: escala al equipo propietario.
- En servicios tier 0 (payments-api, auth-service) el rollback necesita la conformidad del change advisor y el aviso al incident commander.

## Procedimiento

1. Identifica la versión anterior estable en el historial de despliegues.
2. Solicita la evaluación del cambio al change advisor indicando servicio, acción `rollback` y severidad del incidente.
3. Ejecuta el rollback con el pipeline de despliegue (nunca con kubectl manual en producción).
4. Verifica durante 10 minutos que la tasa de errores y la latencia vuelven a valores normales.

## Después

Registra el rollback en el incidente y abre una tarea para corregir la versión defectuosa.
