# Guía de ola.sh

> Acompaña a `docs/planes/olas.md` (qué features van juntas) y a
> `scripts/ola.sh` (cómo se abren, integran y cierran). En los ejemplos, el
> repo se llama `app`, la rama de integración es `develop` y los IDs
> `APP-NNN` son ficticios. Las líneas que empiezan por `→`, `✓` y `!` son las
> del script.

## El ciclo completo

| Paso | Qué pasa | Quién |
| --- | --- | --- |
| 1. Abrir | Worktree, instalación y una sesión de Claude Code por feature | script |
| 2. Trabajar | La sesión explora, diseña, construye y verifica; tú apruebas GATE#1 | Claude + tú |
| 3. Vigilar | Ver en qué fase va cada feature | script |
| 4. Integrar | Squash a la rama de integración, regresión y commit con el mensaje del reviewer | script + tú |
| 5. Cerrar | Borrar el worktree, la rama temporal y la ventana | script |

**Regla de oro:** el árbol principal (el repo, en `develop`) solo sirve para
integrar. Las features se construyen en sus worktrees (`~/app-wt/app-nnn`).
Integra de una en una, y no empieces la siguiente integración hasta que la
anterior tenga su commit.

## Antes de la primera ola

1. **El script, las guías y `AGENTS.md` tienen que estar commiteados** en la
   rama de integración, para que cada worktree nuevo los tenga.
2. **Configura la cabecera de `scripts/ola.sh`** si tu proyecto lo necesita:
   instalación, lockfiles, generadores y dependencias implícitas
   (`INSTRUCCIONES/OLAS.md` del harness).
3. **Instala tmux** (`sudo apt install tmux`). Sin tmux funciona con
   `--sin-tmux`, pero abres tú cada terminal.
4. **Deja limpio el árbol principal** antes de integrar. Para abrir worktrees
   no hace falta.
5. **Comprueba que responde:** `bash scripts/ola.sh ayuda`.

> **En WSL:** si el repo está en `/mnt/c` o `/mnt/d` funciona, pero git y la
> compilación van más lentos. Los worktrees van en `~/app-wt`, en el disco de
> Linux. Si mueves el repo, ejecuta `git worktree repair`.

## 1. Abrir una ola

Desde el árbol principal, con los IDs de la ola. Antes de tocar nada, el
script comprueba que cada feature sigue en `proposed` y que todas sus
dependencias están integradas, también las implícitas de olas.md §8.

```text
$ bash scripts/ola.sh abrir APP-102 APP-103
→ APP-102: nuevo worktree /home/tu/app-wt/app-102 (rama wt/app-102 desde develop)
→ APP-103: nuevo worktree /home/tu/app-wt/app-103 (rama wt/app-103 desde develop)
✓ APP-102: sesión de Claude Code abierta en la ventana «app-102»
✓ APP-103: sesión de Claude Code abierta en la ventana «app-103»

Entra con: tmux attach -t app-olas   (Ctrl+b w elige ventana · Ctrl+b d sale sin cerrar nada)
```

Cada sesión arranca sola con un prompt que la autoriza a trabajar en
paralelo, le dice que lleve solo esa feature y que la reanude si ya estaba
empezada, y le pide que pare al archivar.

- **Repetir `abrir` no estropea nada:** reutiliza el worktree, instala si
  faltaba y solo abre la ventana si no existe.
- **Más de `MAX_ABIERTAS` abiertas:** te pregunta antes de seguir.
- **Sin tmux** (o con `--sin-tmux`): imprime el comando de cada sesión para
  que lo pegues en una terminal por feature.

## Moverte por tmux

Todas las sesiones viven en la sesión de tmux `app-olas`: una ventana por
feature y otra, `integrar`, en el árbol principal. Si cierras la terminal no
pasa nada: las sesiones siguen vivas.

| Quiero… | Teclas o comando |
| --- | --- |
| Entrar | `tmux attach -t app-olas` |
| Elegir ventana de una lista | `Ctrl+b` y luego `w`, flechas, `Enter` |
| Ventana siguiente o anterior | `Ctrl+b` y luego `n` o `p` |
| Subir para leer lo anterior | `Ctrl+b` y luego `[`; flechas o RePág; `q` para salir |
| Salir dejándolo todo en marcha | `Ctrl+b` y luego `d` |
| Usar el ratón | `echo "set -g mouse on" >> ~/.tmux.conf` y reinicia tmux |

## 2. Dentro de una feature

Cada ventana es una sesión normal de Claude Code en otra carpeta. Con
`[orchestration].mode = "auto"` encadena las fases sola y solo te espera en
GATE#1; en `manual` te pregunta tras cada fase en cada ventana.

> **La primera vez en cada worktree** Claude Code pregunta si confías en la
> carpeta (es una ruta nueva) y la opción marcada es «No, exit». Entra en la
> ventana y elige «Yes, I trust this folder»; hasta entonces la sesión no
> arranca la feature.

1. **Explora y diseña** (Claude, solo).
2. **GATE#1** (tú): para y te presenta la recomendación, las decisiones, los
   riesgos y los comandos de aceptación literales.
   - Para aprobar: `/approve APP-102 apruebo`. Claude Code te pide confirmar
     `feature.py transition APP-102 approved --by human …`: **esa
     confirmación es tu firma**.
   - Para pedir cambios: `/reject APP-102 <qué cambiar>`.
3. **Construye y verifica** (Claude, solo): builder y reviewer. Con
   `FAIL_REPAIRABLE` hay un repair automático; si falla otra vez, te pregunta
   en esa ventana.
4. **Archivada** (tú): te da el mensaje de commit y para. **No hagas commit
   ahí**: ve al paso 4 (integrar).

> **Si cierras una ventana por error:** el estado está en `.claude/state/`
> del worktree y no se pierde nada. Repite `bash scripts/ola.sh abrir
> APP-102`: abre otra ventana y la sesión reanuda la feature. Para recuperar
> la misma conversación: `cd ~/app-wt/app-102 && claude --continue`.

## 3. Ver el estado

```text
$ bash scripts/ola.sh estado
Árbol principal: /home/tu/app (develop)
  limpio

APP-102  fase: implementation (in_progress) desde 2026-10-12T09:41:07Z
     /home/tu/app-wt/app-102 · commits sin integrar: 0 · cambios sin commit: 23 · ventana tmux: sí
APP-103  fase: archived (archived) desde 2026-10-12T10:02:55Z
     /home/tu/app-wt/app-103 · commits sin integrar: 0 · cambios sin commit: 41 · ventana tmux: sí
```

Tener cambios sin commit en una feature en marcha es lo normal: el builder
trabaja sin hacer commits. En el ejemplo, APP-103 ya está archivada y toca
integrarla.

## 4. Integrar

Cuando una feature está archivada. Se hace en el árbol principal, de una en
una y en el orden de la ola. El script para en cuanto algo no está bien:

1. Comprueba que estás en la rama de integración, limpio y sin otra
   integración a medias, y que la feature está `archived`.
2. Si el worktree tiene cambios sin commit, te ofrece commitearlos allí.
3. Hace `git merge --squash`. Resuelve solo lo mecánico: `feature_list.json`
   (unión por ID) y los archivos de `AUTO_RAMA`.
4. Ejecuta los pasos de `TRAS_INTEGRAR` que tocan (reinstalar, regenerar) y
   pasa `verify.sh`.
5. Te enseña el mensaje de `## Commit sugerido` de `archive.md` y te pregunta
   si hace el commit y el push.

```text
$ bash scripts/ola.sh integrar APP-103
El worktree /home/tu/app-wt/app-103 tiene cambios sin commit (lo normal al archivar).
¿Los commiteo allí como «chore(app-103): trabajo de la feature»? [s/N] s
✓ commit en wt/app-103
→ git merge --squash wt/app-103
→ verify.sh (regresión completa; puede tardar)

✓ APP-103 integrada y en verde. Cambios preparados:
 .claude/feature_list.json        |   2 +-
 .claude/state/APP-103/archive.md |  64 +++++
 …
Mensaje de .claude/state/APP-103/archive.md («Commit sugerido»):
   feat(api): APP-103 listado paginado de pedidos
¿Hago el commit con este mensaje? [s/N] s
✓ commit hecho: 4f1c2ab feat(api): APP-103 listado paginado de pedidos
¿Hago push de develop? [s/N] s
Siguiente: bash scripts/ola.sh cerrar APP-103
```

Si contestas «no» al commit, los cambios quedan preparados y el script te
deja el mensaje listo: `git commit -F .git/ola-commit-msg`.

## Si hay conflictos

Si la rama de integración cambió los mismos archivos que la feature, el
script resuelve lo mecánico y para con la lista de lo que queda. La rama de
integración no tiene ningún commit nuevo, así que no hay nada roto.

```text
→ git merge --squash wt/app-102
→ hay conflictos; resuelvo los mecánicos
→ auto: .claude/feature_list.json (unión de features por ID)

! quedan conflictos que hay que resolver a mano:
     src/rutas.ts
  …
   2. bash scripts/ola.sh integrar --continuar
  Si prefieres dejarlo:  bash scripts/ola.sh integrar --abortar  (develop queda como estaba)
```

**Resolverlo tú.** Arriba está lo de la rama de integración y abajo lo de la
feature. En un registro casi siempre te quedas con las dos líneas y borras
las marcas:

```text
<<<<<<< HEAD                    export const rutas = [
  "ajustes",           →          "pedidos",
=======                           "ajustes",
  "pedidos",                      ];
>>>>>>> wt/app-102
```

**O pedírselo a Claude Code** en el árbol principal, con el prompt de
«integrar con conflictos» de olas.md §10, o con `/ola continuar` si la está
llevando la sesión del árbol principal.

**Después:** `bash scripts/ola.sh integrar --continuar`. Si queda alguna
marca, se niega («todavía tiene marcas de conflicto»). Si todo está bien,
sigue con los pasos del proyecto, verify y commit.

**Para dejarlo para luego:** `bash scripts/ola.sh integrar --abortar` devuelve
la rama de integración a su último commit y no toca el worktree de la feature.

## 5. Cerrar

Cuando la feature ya tiene su commit en la rama de integración. Cierra la
ventana, borra el worktree y la rama temporal. Si la feature no está
integrada, se niega.

```text
$ bash scripts/ola.sh cerrar APP-103
→ ventana tmux «app-103» cerrada
→ borro el worktree /home/tu/app-wt/app-103 (puede tardar si tiene dependencias o compilados)
→ rama wt/app-103 borrada
✓ APP-103 cerrada.
```

Con el hueco libre, abre la siguiente feature cuyas dependencias ya estén
integradas (olas.md §6).

## Hacerlo desde Claude Code

La sesión de Claude Code del árbol principal puede llevar casi toda la
mecánica con `/ola` (skill `olas`). Abrir, vigilar, integrar (incluidos los
conflictos) y cerrar lo hace ella; tú haces lo que el harness reserva a una
persona.

| Lo hace Claude (sesión del árbol principal) | Lo haces tú |
| --- | --- |
| `abrir`, `estado`, `integrar`, `integrar --continuar`, `cerrar` | GATE#1 de cada feature, en su ventana de tmux |
| Resolver los conflictos que queden | Confirmar dependencias nuevas en cada ventana |
| Avisarte de qué falta y con qué comando | Los dos commits de cada feature, el push y los descartes |

Cuando el script se ejecuta desde Claude Code, nunca hace commits, push ni
descartes: lo detecta (`CLAUDECODE`) y responde «no». En vez de preguntar,
imprime el comando exacto, que tú lanzas en la misma sesión con `!` delante.
`--si` también está prohibido: lo rechazan el script y `guard.py`. Salvo
`estado` y `ayuda`, Claude Code te pedirá permiso cada vez que Claude ejecute
el script.

**Cómo queda una integración desde Claude Code:**

```text
tú:     APP-103 está archivada.
Claude: (ejecuta integrar APP-103) Falta el commit del worktree. Ejecuta:
        ! git -C '/home/tu/app-wt/app-103' add -A && git -C '/home/tu/app-wt/app-103' commit --no-verify -m 'chore(app-103): trabajo de la feature'
tú:     ! git -C … commit …          ← lo lanzas tú
tú:     hecho
Claude: (ejecuta integrar APP-103: squash, pasos del proyecto, verify en verde)
        Listo para el commit:
        ! git commit -F '/home/tu/app/.git/ola-commit-msg' && git push
tú:     ! git commit -F … && git push
Claude: (ejecuta cerrar APP-103) Cerrada. Ya se puede abrir APP-104.
```

## Cuando algo falla

El script nunca hace commit, push ni borra trabajo sin preguntarte. Si algo
falla, para y te dice qué hacer.

| Mensaje | Qué pasa | Qué hacer |
| --- | --- | --- |
| `APP-105 depende de APP-104, que en develop está «proposed»` | Dependencia sin integrar | Integra antes la dependencia. `--forzar` solo si la feature no usa su código. |
| `APP-104 está «in_progress» en el árbol principal` | La feature se está haciendo en la carpeta principal | Termínala allí; no la lleves en dos sitios. |
| `falló la instalación en …` | Red o gestor de paquetes | Arréglalo y repite el mismo `abrir`: reutiliza el worktree. |
| `… existe pero no es un worktree de este repo` | Carpeta suelta con ese nombre | Muévela o bórrala tú. Si borraste la carpeta de un worktree con trabajo, `abrir` lo recrea desde su rama sin perder commits. |
| `el árbol principal tiene cambios sin commit` | La rama de integración no está limpia | Haz commit de esos cambios y repite. |
| `APP-102 está «in_progress» en su worktree` | La feature no está terminada | Mira su ventana: puede estar esperándote. |
| `falta el commit del worktree` | Desde Claude Code o sin terminal | Lanza tú el comando que imprime y repite. |
| `falló «<paso>»` | Un paso de `TRAS_INTEGRAR` | Arréglalo y `integrar --continuar`. |
| `verify.sh falla con APP-102 integrada` | Juntas fallan aunque por separado pasaran | Si fue un conflicto mal resuelto, corrígelo y `--continuar`. Si no, `--abortar`, registra un bug con el log y no integres nada más hasta arreglarlo. |
| `hay una integración a medias de APP-102` | Otra integración sin terminar | `integrar --continuar` o `integrar --abortar`. |
| `no encuentro un «## Commit sugerido»…` | El reviewer no dejó un mensaje en Conventional Commits | Haz el commit tú con `git commit -m "feat(...): APP-NNN …"`. |
| `git commit falló (¿hooks de commit?)` | Un hook (commitlint, lefthook…) rechaza el mensaje | Corrige el mensaje y haz `git commit` tú. |
| `el push falló` | La rama remota avanzó | `git pull --rebase && git push`. |
| `ya hay otro ola.sh en marcha` | Otra orden corriendo (p. ej. un verify) | Espera a que termine. |
| `no cierro. Si de verdad quieres tirarlo…` | La feature no está integrada | Solo si quieres tirar ese trabajo: `cerrar APP-104 --forzar`. |
| `--si no se permite desde Claude Code` | Claude intentó confirmar por ti | Correcto: los commits son tuyos. |
| La feature se bloquea en su ventana | Flujo normal del harness | Decide en esa ventana (`replan`, `retry_build`, `retry_verification`, `cancel`); las demás siguen. |
| Todo va lento, `BLOCKED_TOOLING` por tiempo | Demasiadas compilaciones a la vez | Deja menos features construyendo (las demás pueden esperar en GATE#1) y luego `retry_verification`. |

## Chuleta

| Orden | Qué hace | Cuándo |
| --- | --- | --- |
| `abrir ID-A ID-B` | Worktrees, instalación y sesiones | Al empezar una ola |
| `estado` | Fase y pendientes de cada feature | Cuando quieras |
| `integrar ID` | Squash, resolución automática, pasos, verify, commit con confirmación | Feature archivada |
| `integrar --continuar` | Sigue tras resolver o arreglar | Después de resolver |
| `integrar --abortar` | Deja la rama de integración como estaba | Si prefieres no integrar ahora |
| `cerrar ID` | Borra worktree, rama y ventana | Tras el commit |
| `--sin-tmux` | Imprime los comandos en vez de abrir tmux | Sin tmux |
| `--dir <carpeta>` | Otra carpeta para los worktrees (`~/<repo>-wt` por defecto) | Rara vez |
| `--forzar` | Abrir sin dependencias integradas o cerrar sin integrar | Solo si sabes por qué |
| `--si` | Sí a todo (prohibido desde Claude Code) | Mejor no |

**Lo que haces tú en cada feature:**

1. GATE#1 con `/approve` o `/reject`, y la firma.
2. Confirmar las dependencias nuevas.
3. Decidir si algo se bloquea.
4. Los commits (worktree e integración) y el push.
