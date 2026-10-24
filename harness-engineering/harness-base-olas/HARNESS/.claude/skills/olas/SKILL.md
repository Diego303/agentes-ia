---
name: olas
description: "Olas: varias features a la vez, cada una en su worktree con su propia sesión, usando scripts/ola.sh (docs/planes/olas.md y docs/planes/guia-olas.md). Cubre qué features se pueden abrir ahora, abrir la ola, vigilarla, integrar en la rama de integración con squash (conflictos mecánicos automáticos, el resto según olas.md §5, verify) y cerrar. El humano aprueba GATE#1 en cada ventana y hace los commits y el push. Úsala con /ola o cuando el humano hable de olas, worktrees o features en paralelo, solo en la sesión del árbol principal que no lleva ninguna feature."
argument-hint: "[siguiente | abrir ID-A ID-B | estado | integrar ID | continuar | abortar | cerrar ID]"
---

# Olas: features en paralelo

Referencias: `docs/planes/olas.md` (qué va junto: §2 reglas, §5 conflictos,
§6 olas, §8 dependencias implícitas) y `docs/planes/guia-olas.md` (uso del
script y casos de fallo). El script es `scripts/ola.sh`; su cabecera fija la
rama de integración (`RAMA`, por defecto `develop`), el máximo de features
abiertas (`MAX_ABIERTAS`) y las dependencias implícitas (`IMPLICITAS`).

## 1. Tu papel

- Eres la sesión del **árbol principal** (en la rama de integración).
  Coordinas las olas: no llevas ninguna feature. Si esta sesión tiene una
  feature en curso o el árbol tiene trabajo sin commit, dilo y para. Integrar
  con el árbol sucio no es posible.
- Cada feature la lleva **su propia sesión** de Claude Code en su worktree
  (`~/<repo>-wt/<id>`), que abre el script en tmux. Esa sesión es la dueña de
  la feature: nunca tocas sus archivos, su `.claude/state/` ni su GATE#1.
- Todo lo de git y worktrees pasa por `bash scripts/ola.sh …`. El script ya
  comprueba dependencias, estado y limpieza, y para con un mensaje claro.

## 2. Lo que nunca haces

- `--si`. El script lo rechaza desde Claude Code y el guard también: los
  commits, el push y los descartes son del humano.
- `git commit`, `push`, `merge`, `reset`, `worktree` o `branch` a mano.
  Cuando el script imprime un comando de commit, se lo das al humano para que
  lo lance con `!` delante.
- `--forzar`, salvo que el humano lo pida con esas palabras para una feature
  concreta.
- Integrar dos features a la vez, o empezar una integración con otra a medias.
- Editar `.claude/state/`, `feature_list.json` (salvo resolver su conflicto,
  que el script ya hace solo) o los archivos de un worktree.

## 3. Qué se puede abrir ahora (`/ola` o `/ola siguiente`)

1. Ejecuta `bash scripts/ola.sh estado`: qué hay abierto y en qué fase.
2. Lee `git show <rama>:.claude/feature_list.json`. Una feature se puede
   abrir si:
   - está `proposed`;
   - todas sus dependencias están `archived` en la rama de integración: las
     de «depende de:» en sus notas y las implícitas de olas.md §8;
   - no está abierta ya.
3. Toma la primera ola de olas.md §6 que tenga features pendientes y respeta
   sus reglas (§2):
   - como mucho `MAX_ABIERTAS` features abiertas en total, contando las que
     ya lo están;
   - una sola por módulo;
   - los cuellos de botella que marca §2 con compañía ligera;
   - nunca mezclar versiones;
   - las de pruebas de versión (x98) y release (x99) solas y con toda la
     versión integrada.

   Puedes adelantar una feature de la ola siguiente (ritmo continuo, §2) si ya
   cumple todo eso. Si `olas.md` aún no tiene olas, propón la lista solo con
   las dependencias y la regla de un módulo por feature, y dilo.
4. Propón la lista con el motivo de cada una y lo que el humano tendrá que
   decidir en su GATE#1 (columna «Decides tú» de §6). **Espera su
   confirmación** antes de abrir.

## 4. Abrir (`/ola abrir ID-A ID-B`)

1. `bash scripts/ola.sh abrir ID-A ID-B`. Si se niega, explica el motivo con
   las palabras del script; no lo esquives.
2. Dile al humano:
   - que entre en otra terminal con `tmux attach -t <repo>-olas` (`Ctrl+b w`
     para elegir ventana);
   - que cada sesión llegará sola a su GATE#1 y le esperará allí;
   - que no apruebe a la vez más builds de los que su máquina aguanta
     (olas.md §3.2).

## 5. Estado (`/ola estado`)

Ejecuta `bash scripts/ola.sh estado` y resume en una línea por feature: fase
y qué falta. Señala las que estén `archived`: toca integrarlas.

## 6. Integrar (`/ola integrar ID`)

Integra cuando el humano te diga que una feature está archivada (o lo veas en
`estado`). El orden lo marca la ola en olas.md §6.

Ejecuta `bash scripts/ola.sh integrar ID` con el `timeout` máximo de la
herramienta Bash, porque incluye `verify.sh`. Según cómo termine:

| Salida del script | Qué haces |
| --- | --- |
| «falta el commit del worktree» (código 1) | Da al humano el comando `git -C … commit …` que imprime, con `!` delante, y espera a que te diga «hecho». Después repite `integrar ID`. |
| «quedan conflictos que hay que resolver a mano» (código 2) | Resuélvelos (§7) y ejecuta `bash scripts/ola.sh integrar --continuar`. |
| «verify.sh falla» (código 1) | Lee el error. Si viene de un conflicto mal resuelto, corrígelo y ejecuta `integrar --continuar`. Si es una incompatibilidad real entre features, explícasela al humano y propón `integrar --abortar` y registrar un bug; decide él. |
| «integrada y en verde… Haz tú el commit» (código 0) | Da al humano el comando exacto, `git commit -F '<…>/ola-commit-msg' && git push`, con `!` delante, y espera. |
| Otro error | Explícalo con las palabras del script y propón el siguiente paso de guia-olas.md («Cuando algo falla»). |

Tras el commit del humano, comprueba con `git log -1 --format=%s` que el
mensaje es el de la feature. Después ejecuta `bash scripts/ola.sh cerrar ID`
y vuelve al §3: con un hueco libre, propón qué abrir.

## 7. Resolver conflictos

Es un cambio concreto que el humano te ha pedido al lanzar `/ola integrar`.
Edita solo los archivos que el script lista como conflicto, en el árbol
principal, siguiendo olas.md §5:

- **Registros** (rutas, comandos, códigos de error, catálogos de textos,
  claves de configuración, documentación de formatos, fixtures): conserva las
  entradas de los dos lados, sin duplicar.
- **Migraciones**: primero la de la rama de integración, después la nueva con
  el número siguiente. Revisa los tests que comprueben la versión del esquema.
- **Nunca a mano**: lockfiles y código generado. Los que estén en `AUTO_RAMA`
  los resuelve el script y los regenera con `TRAS_INTEGRAR`; si no están, toma
  el lado de la rama de integración y deja que el paso de regeneración los
  complete.
- **Si un conflicto exige elegir comportamiento** (dos features cambian la
  misma lógica de forma incompatible), no elijas tú. Para, explícaselo al
  humano y propón `--abortar` y registrar un bug.

Antes de `--continuar`, comprueba que no queda ninguna marca `<<<<<<<` ni
`>>>>>>>` en esos archivos.

## 8. Abortar y cerrar

- `/ola abortar` → `bash scripts/ola.sh integrar --abortar`. Es destructivo
  para la integración en curso: pide confirmación explícita al humano antes.
  Desde Claude Code el script dirá «no», así que dale el comando para que lo
  lance él con `!`.
- `/ola cerrar ID` → `bash scripts/ola.sh cerrar ID`. Solo se cierra lo
  integrado. Si el script se niega, no uses `--forzar` salvo petición
  explícita del humano.

## 9. Cómo informar

Breve. Una línea por feature, con la fase y lo que falta. Los comandos que le
tocan al humano, siempre en un bloque y con `!` delante. Nada de repetir la
salida completa del script: resúmela.
