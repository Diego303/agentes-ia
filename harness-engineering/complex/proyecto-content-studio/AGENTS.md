# AGENTS.md — Reglas locales del proyecto

> Este archivo es para **tus reglas específicas** del proyecto. Edítalo libremente.
> Las reglas de **cómo funciona el harness** están en HARNESS.md.

## Lectura obligatoria antes de cualquier acción

1. **Lee primero HARNESS.md** — contrato del harness, flujo SDD, gates, tabla de fases.
2. **Si tienes dudas operativas**, consulta INSTRUCCIONES.md.
3. **Para los prompts más comunes**, mira FAST-USAGE.md.

## Reglas locales del proyecto

> Añade aquí tus convenciones específicas. Estas reglas tienen precedencia
> sobre defaults pero **nunca sobre HARNESS.md** (gates humanos, flujo SDD, etc.).

(Sin reglas locales aún. Edita esta sección.)

### Ejemplos de reglas que podrías añadir:

- **Stack**: Python 3.12, FastAPI, PostgreSQL.
- **Estilo**: ruff config en pyproject.toml.
- **Tests**: cobertura >80%, pytest -q como verificador.
- **Branches**: trunk-based, PR obligatoria.
- **Secretos**: nunca en código, .env.example sin valores reales.
- **Convenciones de naming**: snake_case en Python, camelCase en TypeScript.
