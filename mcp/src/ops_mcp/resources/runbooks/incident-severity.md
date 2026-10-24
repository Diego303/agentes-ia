# Guía de severidad de incidentes

## Niveles

- **SEV1**: caída total de un servicio tier 0 (pagos, login) o pérdida de datos. Respuesta inmediata, incident commander obligatorio.
- **SEV2**: degradación grave de un servicio tier 0 (errores por encima del 5 % o latencia que incumple el SLO) o caída de un tier 1. Respuesta en 15 minutos.
- **SEV3**: degradación parcial sin impacto grave en clientes, o retrasos recuperables. Respuesta en horario laboral.

## Cómo declarar un incidente

1. Elige la severidad con esta guía; ante la duda, la mayor.
2. Indica servicio afectado, síntoma observable y hora de inicio en el resumen.
3. Un incidente lo declara una persona de guardia: los asistentes automáticos pueden proponerlo, pero necesitan aprobación humana para crearlo.

## Congelación de cambios

Durante un SEV1 o SEV2 activo solo se permiten cambios de mitigación (rollback, escalado, feature flags). Los despliegues de funcionalidad nueva quedan congelados.
