# AGENTS.md — Reglas locales del proyecto

> Reglas de **este** proyecto. Las leen el orquestador (vía `CLAUDE.md`) y todos
> los subagentes del harness antes de trabajar.
> Precedencia: invariantes de seguridad y de flujo de `HARNESS.md` > este
> archivo > preferencias del modelo.
> Escribe solo reglas observables y verificables: cada regla vaga se paga en
> tokens en cada agente y no cambia nada. Completa este archivo con la skill
> `project-bootstrap`.

## Stack

(sin definir: lenguaje, versión, frameworks y gestor de dependencias)

## Arquitectura

(módulos principales, sus fronteras y dependencias permitidas entre ellos)

## Convenciones de código

(estilo, naming, manejo de errores, logging; enlaza la configuración del linter)

## Pruebas y comandos de verificación

Estos comandos alimentan `acceptance.yaml` y `.claude/bootstrap/verify.sh`:

- Tests: `<comando>`
- Lint / formato: `<comando>`
- Typecheck / build: `<comando>`

## Seguridad y datos

- Los secretos viven en variables de entorno o en un gestor de secretos; nunca
  en el código, en los tests ni en los artefactos del harness.
- Los datos de ejemplo y de prueba son ficticios.

## Decisiones fijadas

(decisiones que no se vuelven a discutir, p. ej. "Base de datos: PostgreSQL".
En modo yolo el orquestador las aplica sin preguntar y rechaza lo que las contradiga.)

## Git

- Los agentes no hacen commits, cambios de rama ni push: lo hace el humano
  (el reviewer propone el mensaje de commit en `archive.md`).
