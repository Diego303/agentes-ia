# EJEMPLOS-BASE — proyectos de referencia

Esta carpeta contiene **4 proyectos generados con `harness-cli`**,
listos para inspeccionar, copiar o usar como punto de partida.

Cada subcarpeta tiene un `INSTRUCCIONES.md` que explica cómo usar ese
proyecto con **Claude Code**, con **Codex**, con **Cursor** u otros
asistentes IA, y cómo modificarlo (añadir agentes, hooks, dominios).

## Los 4 ejemplos

| Carpeta | Generado con | Para |
|---------|--------------|------|
| [`proyecto-clean/`](proyecto-clean/) | `harness init clean` | Esqueleto vacío (8 agentes orquestación + sample-agent). Útil para entender el contrato sin distracciones. |
| [`proyecto-software/`](proyecto-software/) | `harness init web-app` | SaaS / API / librería. 23 agentes (8 orquestación + 3 software + 5 docs + 6 ideation + 2 cross-cutting). |
| [`proyecto-infra/`](proyecto-infra/) | `harness init infra-only` | IaC con **GATE#3 → Applier** pre-apply. 18 agentes (8 orquestación + 5 infra + 5 docs + security-auditor cross-cutting). |
| [`proyecto-docs/`](proyecto-docs/) | `harness init clean` + `harness add-domain docs` | Documentación / docs site. 13 agentes (8 orquestación + 5 docs + sample). |

## Cómo usar estos ejemplos

### Como referencia de lectura

```bash
cd EJEMPLOS-BASE/proyecto-software
cat AGENTS.md            # contrato de orquestación
cat USAGE.md             # guía operativa específica del perfil
ls .claude/agents/       # agentes disponibles
cat INSTRUCCIONES.md     # cómo usar este proyecto con tu IA
```

### Como punto de partida real

```bash
# Copia el ejemplo más cercano a tu proyecto a otra ubicación
cp -r EJEMPLOS-BASE/proyecto-software ~/my-new-project
cd ~/my-new-project

# Reinicia git history (cada proyecto debe ser independiente)
rm -rf .git 2>/dev/null
./init.sh                # git init + commit inicial
harness doctor           # verifica salud
```

### Para inspirarte y modificar

Edita `feature_list.json` para añadir tus features reales, lee
`INSTRUCCIONES.md` para ver cómo te coordinas con tu asistente IA, y
empieza por la fase Explorer del flujo SDD.

## Diferencias clave entre los ejemplos

| Aspecto | clean | software | infra | docs |
|---------|:-:|:-:|:-:|:-:|
| Agentes de dominio | 0 | 14 (sw + docs + ideation + cross-cutting) | 11 (infra + docs + cross-cutting) | 5 (docs) |
| GATE#3 / Applier | No | No | **Sí** | No |
| Cross-cutting (security/compliance) | No | **Sí** (ambos) | Sí (sólo security) | No |
| Verify stack | markdownlint | ruff, pytest, secret-scanning, markdownlint | tflint, terraform-validate, tfsec, markdownlint | markdownlint |
| Tamaño total | 17 archivos | 32 archivos | 27 archivos | 22 archivos |

## Estructura común a todos

```
proyecto-XXX/
├── AGENTS.md            # contrato de orquestación
├── CLAUDE.md            # guía operativa para Claude
├── USAGE.md             # guía específica del perfil (generada)
├── INSTRUCCIONES.md     # cómo usarlo con tu IA preferida
├── feature_list.json    # cola de features (con seed)
├── harness.toml         # state file
├── init.sh              # bootstrap (git init + commit inicial)
├── progress/            # workspace por feature (vacío)
└── .claude/
    ├── settings.json    # permisos / hooks de Claude Code
    └── agents/          # agentes (8 orquestación + dominio + cross-cutting)
```

## Recordatorios importantes

- **Los proyectos no son `git init`-eados todavía**. Si quieres
  trabajar en uno, ejecuta `./init.sh` para crear el repo.
- **No edites el `feature_list.json` de los ejemplos** si los tratas
  como referencia compartida — copia el proyecto a otra ubicación
  primero.
- **`progress/` está vacío en todos**: cada workspace de feature lo
  irás creando tú al ejecutar el flujo SDD por primera vez.

## Siguientes lecturas

- [`../README.md`](../README.md) — README del repo principal.
- [`../docs/getting-started.md`](../docs/getting-started.md) —
  Tutorial paso a paso.
- [`../docs/concepts.md`](../docs/concepts.md) — Vocabulario.
- [`../docs/best-practices.md`](../docs/best-practices.md) — Operativa.
