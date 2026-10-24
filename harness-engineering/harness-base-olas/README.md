# harness-base-olas

El [harness base](../harness-base/) (bundle `0.8.0`) con el **modo de olas**:
varias features a la vez, cada una en su propio worktree de git y con su
propia sesión de Claude Code, mientras el árbol principal solo integra. El
núcleo (motor de estado, contratos, agentes, validador, guard y ledger) es
idéntico al de la base; lo que añade es la capa de olas y un prompt para
arrancar proyectos grandes.

```text
harness-base-olas/
├── HARNESS/                      lo que se copia a la raíz del repositorio
│   ├── CLAUDE.md  HARNESS.md (§15 olas)  AGENTS.md («Paralelo», «depende de:»)
│   ├── scripts/ola.sh            abrir · estado · integrar · cerrar
│   ├── docs/planes/olas.md       plantilla: reglas, conflictos, olas, dependencias implícitas
│   ├── docs/planes/guia-olas.md  manual del script
│   └── .claude/                  el bundle base + skill olas, /ola y test_ola.py
└── INSTRUCCIONES/                para humanos (no se copian)
    ├── INSTRUCCIONES.md          manual paso a paso
    ├── FAST-USAGE.md             prompts listos para copiar
    ├── OLAS.md                   instalar las olas y adaptar ola.sh a un proyecto
    ├── PROMPT-PLAN-IMPLEMENTACION.md  diseño técnico → plan, olas y harness especializado
    └── README-PROYECTO.md        plantilla de README para el proyecto destino
```

La guía completa y la referencia histórica del harness son las de la base:
[`../harness-base/INSTRUCCIONES/`](../harness-base/INSTRUCCIONES/).

## Cuándo usar este y no la base

- **Base**: una feature cada vez. Es lo más simple y suficiente para la
  mayoría de repos.
- **Olas**: backlog grande con dependencias conocidas (decenas de features),
  donde varias pueden construirse en paralelo. Cuesta más atención humana
  (varios GATE#1 abiertos) y más máquina.

## Instalar

Requisitos: los de la base (Claude Code reciente, Python 3.11+ o 3.9+ con
`tomli`, `git`) más bash 4+ y, recomendado, `tmux`.

```bash
cp -r harness-base-olas/HARNESS/. /ruta/a/tu-repo/   # .claude/, scripts/, docs/planes/, CLAUDE.md...
cd /ruta/a/tu-repo
bash .claude/bootstrap/init.sh
bash scripts/ola.sh ayuda
```

Después, en Claude Code: *"usa project-bootstrap para adaptar el harness a
este repositorio"*, y adapta la cabecera de `scripts/ola.sh` según
[`INSTRUCCIONES/OLAS.md`](INSTRUCCIONES/OLAS.md).

## Arrancar un proyecto desde su diseño técnico

[`INSTRUCCIONES/PROMPT-PLAN-IMPLEMENTACION.md`](INSTRUCCIONES/PROMPT-PLAN-IMPLEMENTACION.md):
pegas el prompt en Claude, adjuntas el diseño técnico y este `HARNESS/` en
zip, y rellenas los parámetros. Devuelve un zip con el plan de implementación
(`docs/`), el harness especializado con el backlog registrado (`harness/`),
las guías de uso (`guia/`) y un `backlog.yaml` con su generador y su
comprobador (`herramientas/`).

## Validar

```bash
python3 .claude/tools/validate_harness.py
python3 -m unittest discover -s .claude/tests     # incluye test_ola.py (ola.sh de punta a punta)
```

Desde la raíz de este repositorio, `make harness-test` pasa los tests de los
dos harnesses y `make harness-drift` comprueba que el núcleo sigue idéntico al
de la base. Los cambios del núcleo se hacen en `harness-base` y se copian aquí.
