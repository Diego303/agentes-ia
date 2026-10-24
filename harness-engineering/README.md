# Harness engineering

Un **harness** es todo lo que rodea al modelo para que trabaje de forma fiable dentro de
un proyecto:

- contratos de agentes y skills;
- una máquina de estados con gates humanos;
- memoria persistente fuera del contexto;
- validación determinista de cada transición;
- medición del coste;
- fronteras de seguridad contra prompt injection.

La IA conserva el juicio; el harness decide dónde lo ejerce y qué evidencia deja.

```text
harness-engineering/
├── harness-base/        harness SDD multiagente para Claude Code (bundle 0.8.0)
│   ├── HARNESS/         lo que se copia a un repositorio
│   └── INSTRUCCIONES/   manuales para humanos
├── harness-base-olas/   el mismo harness con olas: varias features a la vez en worktrees
├── case-studies/        uso en proyectos reales: métricas y lecciones
└── domain-harnesses/    harnesses aplicados a dominios que no son software
    ├── gym/             coach de fuerza e hipertrofia (8 agentes, 47 skills)
    └── software-certs/  apuntes de certificaciones (AI-103, CKAD)
```

## harness-base

[`harness-base/`](harness-base/) es la pieza principal. La sesión principal orquesta y cuatro
subagentes (explorer → designer → **GATE#1** → builder → reviewer) trabajan con contexto limpio.
Herramientas en Python sin dependencias hacen lo determinista:

- `feature.py`: aplica la máquina de estados (`workflow.toml`, 24 guards).
- Congela la especificación aprobada con un hash.
- `run_acceptance.py`: ejecuta la aceptación sin heredar secretos.
- `ledger.py`: registra el coste real de cada subagente.
- `guard.py`: hace cumplir las fronteras de seguridad con listas blancas, y si falla, bloquea.

Tiene 95 tests y lo valida el CI. Instalación y uso: [`harness-base/README.md`](harness-base/README.md).
Análisis pieza a pieza: [`harness-base/INSTRUCCIONES/HARNESS-GUIA-COMPLETA.md`](harness-base/INSTRUCCIONES/HARNESS-GUIA-COMPLETA.md).

## harness-base-olas

[`harness-base-olas/`](harness-base-olas/) es el mismo harness, con el núcleo idéntico (lo
comprueba `make harness-drift`), más el **modo de olas**: varias features a la vez, cada una en
su worktree de git y con su propia sesión, mientras el árbol principal solo integra.

- `scripts/ola.sh` abre, vigila, integra (squash, conflictos mecánicos, `verify.sh`) y cierra.
  Nunca hace commits ni push por su cuenta.
- La skill `olas` y `/ola` permiten llevarlo desde la sesión del árbol principal.
- Incluye un prompt (en `INSTRUCCIONES/`) que convierte un diseño técnico en plan de
  implementación, olas, backlog y harness especializado.

Tiene 100 tests, incluido el script de punta a punta con worktrees reales.

## case-studies

[`case-studies/`](case-studies/) recoge el harness aplicado a dos productos reales: 42 features,
385 ejecuciones de subagentes, en torno a un 60 % de PASS a la primera y el coste medido
por feature. También explica qué correcciones del uso real volvieron al base.

## domain-harnesses

El mismo enfoque (orquestador, agentes especializados, skills como conocimiento
reutilizable y revisión independiente) aplicado fuera del software:

- [`gym/`](domain-harnesses/gym/): diseño, auditoría y reajuste de planes de entrenamiento,
  manuales HTML y análisis longitudinal.
- [`software-certs/azure-ai-103/`](domain-harnesses/software-certs/azure-ai-103/) y
  [`software-certs/kubernetes-ckad/`](domain-harnesses/software-certs/kubernetes-ckad/):
  generación de apuntes atómicos verificados contra la documentación oficial, con ciclo
  autor → revisor independiente, simulacros y flashcards.

Son harnesses ligeros (agentes y comandos, sin motor de estado). Muestran cuándo basta con
contratos de agentes bien escritos y cuándo hace falta la maquinaria del harness base.
