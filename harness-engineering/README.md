# EJEMPLOS-BASE — proyectos de referencia

Esta carpeta contiene **16 proyectos generados con `harness-cli` 0.4.0**:
los 8 perfiles disponibles × los 2 tipos de flujo (simple, complex). Todos
fueron generados con `--client claude-code` (bundle `.claude/`,
descubrimiento nativo de subagentes en Claude Code).

Si usas otro cliente IA (Codex, Cursor, aider, GPT…), regenera el
proyecto con `--client general` (bundle `.harness/`).

---

## Estructura

```
EJEMPLOS-BASE/
├── simple/         ← 8 proyectos con --type simple (4 agentes canónicos)
│   ├── proyecto-clean/
│   ├── proyecto-web-app/
│   ├── proyecto-infra-only/
│   ├── proyecto-content-studio/
│   ├── proyecto-backend-api/
│   ├── proyecto-data-pipeline/
│   ├── proyecto-fullstack-web/
│   └── proyecto-mobile-app/
└── complex/        ← 8 proyectos con --type complex (9 agentes canónicos)
    ├── proyecto-clean/
    ├── proyecto-web-app/
    ├── proyecto-infra-only/
    ├── proyecto-content-studio/
    ├── proyecto-backend-api/
    ├── proyecto-data-pipeline/
    ├── proyecto-fullstack-web/
    └── proyecto-mobile-app/
```

Comando para cada proyecto: `harness init <perfil> --target . --client claude-code --type <flow>`.

Total: **16 proyectos × HEALTHY** (todos pasan `harness doctor`).

---

## Tabla resumen — agentes por proyecto

### Carpeta `simple/` (4 canónicos: explorer, designer, builder, reviewer)

| Perfil | Agentes totales | Specialists añadidos | default_flow_type |
|---|---:|---|---|
| `clean` | **5** | sample-agent | complex (forzado a simple) |
| `web-app` | **19** | software (2) + docs (5) + ideation (6) + 2 cross-cutting | complex (forzado a simple) |
| `infra-only` | **15** | infra (5) + docs (5) + 1 cross-cutting | complex (forzado a simple) |
| `content-studio` | **21** | content (6) + docs (5) + ideation (6) | complex (forzado a simple) |
| `backend-api` | **18** | software (2) + backend (6) + docs (5) + 1 cross-cutting | complex (forzado a simple) |
| `data-pipeline` | **17** | software (2) + data (5) + docs (5) + 1 cross-cutting | complex (forzado a simple) |
| `fullstack-web` | **22** | software (2) + frontend (5) + content (6) + docs (5) | complex (forzado a simple) |
| `mobile-app` | **15** | software (2) + mobile (4) + docs (5) | **simple (default)** |

### Carpeta `complex/` (9 canónicos)

| Perfil | Agentes totales | Specialists añadidos | default_flow_type |
|---|---:|---|---|
| `clean` | **10** | sample-agent | complex (default) |
| `web-app` | **24** | software (2) + docs (5) + ideation (6) + 2 cross-cutting | complex (default) |
| `infra-only` | **20** | infra (5) + docs (5) + 1 cross-cutting | complex (default) |
| `content-studio` | **26** | content (6) + docs (5) + ideation (6) | complex (default) |
| `backend-api` | **23** | software (2) + backend (6) + docs (5) + 1 cross-cutting | complex (default) |
| `data-pipeline` | **22** | software (2) + data (5) + docs (5) + 1 cross-cutting | complex (default) |
| `fullstack-web` | **27** | software (2) + frontend (5) + content (6) + docs (5) | complex (default) |
| `mobile-app` | **20** | software (2) + mobile (4) + docs (5) | simple (forzado a complex) |

> Cada perfil tiene un `default_flow_type` declarado en
> `src/harness_cli/profiles/<perfil>.yaml`. La carpeta `simple/` o
> `complex/` indica qué `--type` se usó al generar; cuando difiere del
> default del perfil, se anota como "forzado".

---

## Cómo usar estos ejemplos

### Como referencia de lectura

```bash
cd EJEMPLOS-BASE/complex/proyecto-backend-api

# Los 6 archivos raíz
cat HARNESS.md           # contrato del harness (10 fases complex, gates, recovery)
cat AGENTS.md            # reglas locales (template; tú lo editas en proyectos reales)
cat INSTRUCCIONES.md     # manual humano detallado
cat FAST-USAGE.md        # 4 prompts copy-paste
cat CLAUDE.md            # 5 líneas para Claude Code
cat README.md            # README inicial

# El bundle operativo
ls .claude/                              # bundle completo
ls .claude/agents/                       # los 23 agentes (9 canónicos + 6 backend + 2 software + 5 docs + 1 security)
cat .claude/harness.toml                 # state file con flow_type=complex
cat .claude/feature_list.json            # cola de features
cat .claude/agents/agent-registry.yaml   # registry auto-generado con color/memory
```

### Comparar simple vs complex

```bash
# Mismo perfil, distinto flow_type
diff -rq EJEMPLOS-BASE/simple/proyecto-backend-api EJEMPLOS-BASE/complex/proyecto-backend-api

# Ver el HARNESS.md de cada uno (la sección 5 cambia entre los dos flows)
diff EJEMPLOS-BASE/simple/proyecto-backend-api/HARNESS.md \
     EJEMPLOS-BASE/complex/proyecto-backend-api/HARNESS.md

# Comparar el conjunto de agentes
diff <(ls EJEMPLOS-BASE/simple/proyecto-backend-api/.claude/agents/*.md | xargs -n1 basename | sort) \
     <(ls EJEMPLOS-BASE/complex/proyecto-backend-api/.claude/agents/*.md | xargs -n1 basename | sort)
# Verás: simple tiene builder, reviewer (4 canónicos)
#        complex tiene proposer, spec-writer, task-planner, code-reviewer, verifier, archiver (9 canónicos)
```

### Como punto de partida

```bash
# Copiar uno como base
cp -r EJEMPLOS-BASE/simple/proyecto-mobile-app ~/proyectos/mi-app

# Editar AGENTS.md con tus reglas reales (CRÍTICO si vas a usar yolo)
$EDITOR ~/proyectos/mi-app/AGENTS.md

# Verificar
cd ~/proyectos/mi-app
harness doctor                # → HEALTHY
harness mode yolo             # ⚠ warning sobre AGENTS.md
```

---

## Cuál perfil + flow elegir

### Si nunca has usado harness

→ `complex/proyecto-clean/` — esqueleto mínimo con todos los 9 agentes
canónicos del flow complex. Ideal para entender el contrato.

### Si vas a hacer una API REST/GraphQL/gRPC

→ `complex/proyecto-backend-api/` — incluye specialists de DB, auth,
versionado API, migrations, cache, observabilidad. Cross-cutting
security-auditor.

### Si vas a hacer un pipeline de datos

→ `complex/proyecto-data-pipeline/` — incluye pipeline-architect (opus),
quality, schema-evolution, transformation, lineage.

### Si vas a hacer una app web fullstack

→ `complex/proyecto-fullstack-web/` — frontend specialists (a11y,
state, bundle, e2e) + content specialists (copywriter, seo) +
software specialists (test-engineer, api-designer).

### Si vas a hacer una app móvil

→ `simple/proyecto-mobile-app/` — flow simple por default (iteración
rápida típica de mobile). Mobile specialists (platform-strategist,
offline-sync, perf-auditor, release-manager).

### Si vas a hacer un prototipo rápido

→ `simple/proyecto-clean/` o `simple/proyecto-mobile-app/`.

### Si vas a hacer IaC con Terraform

→ `complex/proyecto-infra-only/` — flow complex con `gate3_pre_apply`
+ Applier post-aprobación. NO recomendable simple para infra.

### Si vas a hacer marketing / blog

→ `complex/proyecto-content-studio/` — content specialists (strategist,
copywriter, copy-editor, seo, fact-checker, distribution-planner) +
ideation (brainstormer, critic, etc.) + docs.

---

## Regenerar estos ejemplos

```bash
# Limpiar
rm -rf EJEMPLOS-BASE/simple EJEMPLOS-BASE/complex
mkdir -p EJEMPLOS-BASE/simple EJEMPLOS-BASE/complex

# Regenerar los 16
PROFILES="clean web-app infra-only content-studio backend-api data-pipeline fullstack-web mobile-app"
for p in $PROFILES; do
    .venv/bin/harness init $p --target EJEMPLOS-BASE/simple/proyecto-$p \
                              --client claude-code --type simple
    .venv/bin/harness init $p --target EJEMPLOS-BASE/complex/proyecto-$p \
                              --client claude-code --type complex
done

# Verificar
for ft in simple complex; do
    for p in $PROFILES; do
        .venv/bin/harness doctor --target EJEMPLOS-BASE/$ft/proyecto-$p | grep HEALTHY
    done
done
```

---

## Caveats

- Los proyectos están **vacíos** (sin features iniciadas, sin
  artefactos en `state/`). Al generarlos no se ejecuta ningún flujo,
  sólo se renderiza el esqueleto.
- `feature_list.json` contiene los seeds del perfil (1 feature de
  ejemplo cada uno).
- `AGENTS.md` es el template inicial. **En proyectos reales, edítalo**
  con tus reglas locales antes de empezar la primera feature
  (especialmente crítico si vas a usar `harness mode yolo`).
- `init.sh` viene como bash script ejecutable. Se ejecuta una vez
  para bootstrap del entorno.

---

## Ver también

- [`docs/getting-started.md`](../docs/getting-started.md) — tutorial
  paso a paso de tu primera feature.
- [`docs/flow-types.md`](../docs/flow-types.md) — simple vs complex
  en detalle.
- [`docs/modes.md`](../docs/modes.md) — los 3 modos (manual / auto /
  yolo).
- [`docs/domains.md`](../docs/domains.md) — mapa de los 56 agentes en
  9 dominios.
- [`FAST-USAGE.md`](../FAST-USAGE.md) — cheatsheet de los 14 comandos
  + 6 combinaciones mode×flow_type.
