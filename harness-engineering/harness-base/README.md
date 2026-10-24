# harness-base

Harness SDD multiagente para Claude Code (bundle `0.8.0`). La sesión principal
orquesta y cuatro subagentes con contexto limpio hacen el trabajo: explorer,
designer, builder y reviewer. Entre designer y builder hay un único gate humano
(GATE#1). Herramientas deterministas en Python (solo stdlib) aplican la máquina
de estados, congelan la especificación aprobada, ejecutan la aceptación, miden
el coste de cada subagente y hacen cumplir las fronteras de seguridad.

```text
harness-base/
├── HARNESS/          lo que se copia al repositorio destino (bundle mínimo)
│   ├── CLAUDE.md     entrada del orquestador (importa HARNESS.md y AGENTS.md)
│   ├── HARNESS.md    contrato: flujo, decisiones humanas, seguridad, invariantes
│   ├── AGENTS.md     reglas del proyecto destino (plantilla)
│   ├── .gitignore
│   └── .claude/      agentes, skills, comandos, contrato, herramientas, tests
└── INSTRUCCIONES/    manuales para humanos (no se copian)
    ├── INSTRUCCIONES.md         manual paso a paso
    ├── FAST-USAGE.md            prompts listos para copiar
    ├── README-PROYECTO.md       plantilla de README para el proyecto destino
    ├── HARNESS-GUIA-COMPLETA.md harness engineering y análisis pieza a pieza
    └── HARNESS_REFERENCE.md     histórico: bundle 0.4.0 para Codex del que parte
```

## Instalar

Requisitos: Claude Code reciente, Python 3.11+ (o 3.9+ con `tomli`), `bash` y `git`.

```bash
cp -r harness-base/HARNESS/. /ruta/a/tu-repo/   # incluye .claude/ y .gitignore
cd /ruta/a/tu-repo
bash .claude/bootstrap/init.sh                  # valida el harness y pasa sus tests
```

Si el repositorio ya tiene `CLAUDE.md`, `AGENTS.md` o `.gitignore`, fusiónalos
en lugar de pisarlos. Después, en Claude Code: *"usa project-bootstrap para
adaptar el harness a este repositorio"* (completa `AGENTS.md` y `verify.sh`).

## Validar

```bash
python3 .claude/tools/validate_harness.py          # bundle y features
python3 -m unittest discover -s .claude/tests      # tests del harness
python3 .claude/tools/feature.py metrics           # métricas agregadas de las features
```

## Más

- Manual: [`INSTRUCCIONES/INSTRUCCIONES.md`](INSTRUCCIONES/INSTRUCCIONES.md)
- Prompts: [`INSTRUCCIONES/FAST-USAGE.md`](INSTRUCCIONES/FAST-USAGE.md)
- Contrato: [`HARNESS/HARNESS.md`](HARNESS/HARNESS.md)
- Cambios: [`HARNESS/.claude/CHANGELOG.md`](HARNESS/.claude/CHANGELOG.md)
- Cómo extenderlo: [`HARNESS/.claude/docs/extending.md`](HARNESS/.claude/docs/extending.md)
