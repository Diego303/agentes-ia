# OLAS.md — Instalar y adaptar las olas

Las olas permiten construir varias features a la vez, cada una en su propio
*worktree* de git y con su propia sesión de Claude Code, mientras el árbol
principal solo integra. Este harness ya las trae montadas; aquí está lo que
tienes que preparar y lo único que cambia de un proyecto a otro.

## Qué hay

| Archivo (en `HARNESS/`) | Para qué |
| --- | --- |
| `scripts/ola.sh` | El script: `abrir`, `estado`, `integrar` (`--continuar`, `--abortar`), `cerrar`. |
| `docs/planes/olas.md` | El plan: reglas (§2), preparación (§3), conflictos (§5), las olas (§6) y las dependencias implícitas (§8). §6 y §8 son del proyecto. |
| `docs/planes/guia-olas.md` | El manual del script, con ejemplos, tmux, conflictos, fallos y chuleta. |
| `.claude/skills/olas/` y `.claude/commands/ola.md` | La skill y `/ola` para la sesión del árbol principal. |
| `AGENTS.md` | El apartado «Paralelo» de Git y la convención `depende de:` en las notas. |
| `HARNESS.md` §15 | Las reglas de las olas dentro del contrato. |

## 1. Preparar la máquina

- `git`, `python3` y **bash 4 o superior** (en macOS, `brew install bash`).
- **tmux** (`sudo apt install tmux`), recomendado. Sin tmux, `--sin-tmux`
  imprime el comando de cada sesión y abres tú las terminales.
- `claude` en el `PATH`, para que el script abra las sesiones.
- **Worktrees en un disco rápido.** En WSL, en el disco de Linux
  (`~/<repo>-wt`, el valor por defecto), nunca en `/mnt/c` o `/mnt/d`. Cada
  worktree lleva sus dependencias y compilados.
- **Memoria.** En WSL2 sube `memory=` y `processors=` en `.wslconfig`. Con
  16 GB, 2 o 3 builds a la vez como mucho.

## 2. Adaptar la cabecera de `scripts/ola.sh`

Todo lo del proyecto está en el bloque «configuración del proyecto», al
principio del script. Lo que no toques funciona con valores genéricos.

| Variable | Qué es | Por defecto |
| --- | --- | --- |
| `RAMA` (`OLA_RAMA`) | Rama de integración, donde vive el árbol principal | `develop` |
| `MAX_ABIERTAS` (`OLA_MAX`) | Features abiertas a la vez antes de pedir confirmación | `4` |
| `TMUX_SESSION` (`OLA_TMUX`) | Sesión de tmux | `<repo>-olas` |
| `PREFIJO` (`OLA_PREFIJO`) | Permite escribir solo el número (`007` → `APP-007`) | vacío |
| `OLA_DIR` o `--dir` | Carpeta de los worktrees | `~/<repo>-wt` |
| `INSTALAR` | Instalación en cada worktree nuevo | vacío (no instala) |
| `INSTALAR_SI_FALTA` | Instala solo si falta esa ruta (p. ej. `node_modules`) | vacío (instala en cada `abrir`) |
| `AUTO_RAMA` | Conflictos que se resuelven con el lado de la rama de integración porque se regeneran después (lockfiles, código generado) | vacío |
| `TRAS_INTEGRAR` | Pasos tras el squash: `'regex de archivos cambiados :: comando'` | vacío |
| `IMPLICITAS` | Dependencias implícitas de `olas.md` §8 | vacío |
| `ARRANQUE` | Cómo arranca cada sesión su feature (`{ID}`) | `sdd-feature-planning` o `feature-resume` |

Ejemplo para un proyecto con pnpm y código generado:

```bash
INSTALAR="pnpm install --frozen-lockfile --prefer-offline || pnpm install --prefer-offline"
INSTALAR_SI_FALTA="node_modules"
AUTO_RAMA=("pnpm-lock.yaml" "*/pnpm-lock.yaml" "src/api/generado.ts")
TRAS_INTEGRAR=(
  '(^|/)(package\.json|pnpm-lock\.yaml)$ :: pnpm install --prefer-offline'
  '^api/openapi\.yaml$ :: pnpm gen:api'
)
declare -A IMPLICITAS=([APP-109]="APP-105")
```

Ejemplo para Python con uv:

```bash
INSTALAR="uv sync --frozen"
AUTO_RAMA=("uv.lock")
TRAS_INTEGRAR=('(^|/)(pyproject\.toml|uv\.lock)$ :: uv lock && uv sync')
```

Si el harness especializado tiene su propia skill para arrancar features
(p. ej. `/siguiente`), cámbiala en `ARRANQUE`.

Comprueba siempre: `bash -n scripts/ola.sh && bash scripts/ola.sh ayuda`.

## 3. Rellenar `docs/planes/olas.md`

- **§6, las olas**, por versión: qué features van juntas, en qué orden se
  integran, qué vigilar y qué decides tú. Calcúlalas por niveles del grafo de
  dependencias, con como mucho `MAX_ABIERTAS` por ola y una por módulo.
- **§8, dependencias implícitas**: código que una feature usa de otra sin
  declararlo. Mejor en las notas de la feature (`depende de:`); si no, en
  `IMPLICITAS`.
- **§5, conflictos**: añade los registros y archivos compartidos de tu
  proyecto.
- §2 (reglas) vale casi tal cual; pon los cuellos de botella en la regla 8.

El prompt de [`PROMPT-PLAN-IMPLEMENTACION.md`](PROMPT-PLAN-IMPLEMENTACION.md)
lo hace por ti a partir del diseño técnico, junto con el backlog y el harness
especializado.

## 4. Registrar las dependencias

`ola.sh` lee las dependencias de las notas de `.claude/feature_list.json`, en
la rama de integración:

```text
v1 · orden 3 · tamaño M · plan: docs/planes/02-api.md (sección APP-103) · depende de: APP-101, APP-102
```

Lee desde `depende de:` hasta el siguiente ` · `. `feature-kickoff` ya lo
escribe así al registrar una feature.

## 5. Commit y primera ola

El script y las guías tienen que estar en la rama de integración para que
cada worktree nuevo los tenga:

```bash
git add scripts/ola.sh docs/planes .claude AGENTS.md HARNESS.md CLAUDE.md
git commit -m "chore(olas): harness con olas"
python3 .claude/tools/validate_harness.py
python3 -m unittest discover -s .claude/tests
```

Recomendado: `[orchestration].mode = "auto"` en `.claude/harness.toml`, para
que cada ventana encadene las fases y solo te espere en GATE#1.

Primera prueba: en una sesión de Claude Code en el árbol principal,
`/ola siguiente`. Te dirá qué se puede abrir; ábrelo con `/ola abrir …` o con
`bash scripts/ola.sh abrir APP-101 APP-102` en una terminal. En cada ventana
nueva, Claude Code te preguntará primero si confías en la carpeta del
worktree: acepta para que la sesión arranque.

## Qué necesita el script del harness

Si algo de esto cambia en el harness, el script deja de funcionar
(`test_ola.py` lo detecta):

- `.claude/tools/feature.py --root <worktree> status <ID>` (la fase, en la
  segunda línea) y `.claude/feature_list.json` con `id`, `status` y `notes`.
- IDs con el patrón `FEATURE_ID_PATTERN` de `harness_lib.py`.
- La rama de integración y las ramas temporales `wt/<id>` (no se publican).
- `.claude/bootstrap/verify.sh` como regresión al integrar.
- `.claude/state/<ID>/archive.md` con `## Commit sugerido` en Conventional
  Commits (lo escribe el reviewer).

## Reglas que no cambian

- El árbol principal solo integra. Las features se construyen en sus
  worktrees.
- Integra de una en una, y no empieces otra integración hasta que la anterior
  tenga su commit.
- El GATE#1 lo apruebas tú en cada ventana. Los commits, el push y los
  descartes los haces tú: desde Claude Code el script nunca responde «sí», y
  `--si` lo rechazan el script y `guard.py`.
