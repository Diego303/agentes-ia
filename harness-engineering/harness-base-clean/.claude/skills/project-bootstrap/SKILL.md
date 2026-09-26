---
name: project-bootstrap
description: Instala o adapta este harness a un repositorio real sin convertirlo en un framework de dominio - detecta stack y comandos de verificación, completa AGENTS.md y configura verify.sh. Úsala al copiar el harness a un proyecto, al inicializarlo, al personalizarlo para un stack o cuando el validador avise de que verify.sh está sin configurar.
---

# Project Bootstrap

## Resultado

El harness operativo en un repositorio real, con el core intacto y las reglas
del proyecto en `AGENTS.md`.

## Procedimiento

1. Copia o conserva `.claude/`, `CLAUDE.md`, `AGENTS.md` y `HARNESS.md`. No
   copies `.claude/state/*` ni entradas de `feature_list.json` del repositorio
   de origen.
2. Detecta stack, gestor de dependencias y comandos de test, lint, typecheck y
   build a partir de archivos existentes (`package.json`, `pyproject.toml`,
   `Makefile`, CI...).
3. Completa `AGENTS.md` con reglas observables: stack, arquitectura,
   convenciones, pruebas, seguridad y comandos de verificación.
4. Sustituye el contenido de `.claude/bootstrap/verify.sh` por la regresión real
   (los mismos comandos que la CI) y elimina la marca `HARNESS_VERIFY_PLACEHOLDER`.
5. Revisa `.claude/harness.toml` (modo, presupuestos, precios) y los permisos
   de `.claude/settings.json` para el stack del proyecto.
6. Ejecuta `bash .claude/bootstrap/init.sh` (valida el harness y pasa sus
   tests) y corrige solo errores del bootstrap.

## Límites

- No inventes comandos ni convenciones que el repositorio no demuestre.
- No instales dependencias ni herramientas sin autorización.
- No añadas agentes o skills de dominio salvo necesidad observada.
