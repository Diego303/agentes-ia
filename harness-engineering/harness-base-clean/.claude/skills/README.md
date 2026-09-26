# Skills del harness

Procedimientos que Claude Code carga bajo demanda (`/nombre` o activación por
la `description`). No tienen rol propio en el flujo; los agentes precargan las
que necesitan con `skills:` en su frontmatter.

| Skill | Para qué | Quién la usa |
| --- | --- | --- |
| `feature-cost` | Coste por feature, presupuesto y palancas de ahorro | orquestador (obligatoria en inicio, GATE#1 y cierre), humano |
| `sdd-feature-planning` | De intake a GATE#1 | orquestador |
| `feature-kickoff` | Idea ambigua → feature registrada | orquestador, humano |
| `feature-resume` | Reanudar con seguridad | orquestador |
| `harness-doctor` | Validar y diagnosticar el harness | humano, orquestador |
| `project-bootstrap` | Adaptar el harness a un repo real | humano |
| `acceptance-criteria` | Esquema y reglas de `acceptance.yaml` | designer (precargada), humano |
| `test-driven-development` | Rojo-verde-refactor | builder (precargada) |
| `systematic-debugging` | Causa raíz antes de corregir | builder (precargada) |
| `verification-before-completion` | Nada de "hecho" sin evidencia | builder y reviewer (precargada) |
| `secure-code-review` | Checklist de seguridad y prompt injection | reviewer (precargada) |
| `eval-driven-development` | Evaluar sistemas con IA | humano |
| `plugin-eval` | Evaluar skills, agentes y plugins de Claude Code | humano |
| `skill-creator` | Crear y mejorar skills con evals | humano |
| `caveman` | Respuestas comprimidas (menos tokens de salida) | solo humano (`/caveman`) |
| `ponytail` | Solución mínima que funciona (YAGNI) | solo humano (`/ponytail`), en cambios fuera del flujo |

Los comandos `/approve` y `/reject` (en `.claude/commands/`) son decisiones
humanas: `disable-model-invocation: true` impide que el modelo los invoque.

## Procedencia y auditoría

| Skill | Origen | Licencia | Cambios |
| --- | --- | --- | --- |
| `skill-creator` | [anthropics/skills](https://github.com/anthropics/skills) commit `3337550`, idéntica a la de `HARNESS_REFERENCE.md` | Apache-2.0 (`LICENSE.txt`) | ninguno |
| `caveman`, `ponytail`, `eval-driven-development` | `HARNESS_REFERENCE.md` | ponytail: MIT; resto según referencia | caveman y ponytail: `disable-model-invocation: true` (se activaban solas y persistían, chocando con los formatos del orquestador); eval-driven-development: sección final "En este harness" |
| `test-driven-development` | adaptada de [obra/superpowers](https://github.com/obra/superpowers) | MIT | condensada y adaptada al flujo |
| `systematic-debugging`, `verification-before-completion`, `feature-resume`, `harness-doctor`, `project-bootstrap`, `sdd-feature-planning`, `plugin-eval`, `feature-kickoff` | `HARNESS_REFERENCE.md` | — | adaptadas a Claude Code y a las herramientas del harness |
| `feature-cost`, `acceptance-criteria`, `secure-code-review` | propias del harness | — | — |

Auditoría de seguridad (revisada línea a línea al incorporarlas):

- Ninguna skill contiene instrucciones ocultas, exfiltración ni llamadas de red
  propias.
- `skill-creator` incluye scripts que **gastan dinero** (lanzan `claude -p`),
  abren un visor local en `127.0.0.1:3117` (y terminan cualquier proceso que
  ocupe ese puerto) y cargan Google Fonts y SheetJS desde CDN con SRI. Úsala
  sabiendo esto; sus workspaces de evals (`<skill>-workspace/`) están excluidos
  de git y del hook de seguridad.
- Antes de añadir una skill de terceros: léela entera, busca instrucciones que
  intenten cambiar permisos, hooks o el flujo, revisa sus scripts y registra
  aquí su procedencia.

## Crear una skill

Copia `.claude/templates/skill.md` a `.claude/skills/<nombre>/SKILL.md` (el
nombre de la carpeta es el comando y debe coincidir con `name`) y ejecuta
`python3 .claude/tools/validate_harness.py`. Para medirla, usa `skill-creator`.
