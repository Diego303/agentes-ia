# Skills del proyecto

Las skills son **procedimientos reutilizables invocables** desde los agentes.
A diferencia de los agentes, las skills no tienen rol propio en el flujo SDD:
son utilidades que un agente puede consultar.

## Cómo añadir una skill custom

1. Crea una carpeta con el nombre de la skill: `skills/<mi-skill>/`.
2. Dentro, crea `SKILL.md` con frontmatter YAML:

```markdown
---
name: mi-skill
description: Lo que hace y cuándo invocarla.
allowed-tools: Read, Grep
---

# mi-skill

(Procedimiento detallado aquí.)
```

3. Cualquier agente del harness puede leer la skill cuando la necesite.

## Skills incluidas

- `example-skill/` — referencia mínima para que copies de plantilla.
