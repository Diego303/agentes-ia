# Olas: varias features a la vez

> Plantilla del harness (perfil `olas`). Las reglas (§1–§5, §7, §9, §10) valen
> para cualquier proyecto; **§6 (las olas) y §8 (dependencias implícitas) se
> rellenan con las del proyecto**, a mano o con el prompt de plan de
> implementación (`INSTRUCCIONES/PROMPT-PLAN-IMPLEMENTACION.md` del harness).
> El catálogo de features fija **qué depende de qué**; este documento fija
> **qué puede ir a la vez** y **cómo hacerlo sin romper el harness**.
> Los IDs `APP-NNN` de los ejemplos son ficticios.

## 1. En una página

- Una **ola** es un grupo de features (como mucho `MAX_ABIERTAS`, 4 por
  defecto) cuyas dependencias ya están integradas en la rama de integración
  (`develop` por defecto) y que no tocan el mismo módulo. Todas las de la ola
  se pueden construir **a la vez**.
- **Cada feature de la ola va en su propio worktree de git** (una carpeta y
  una rama temporal `wt/<id>`) **con su propia sesión de Claude Code**. El
  harness no cambia: cada sesión lleva una feature y tú apruebas cada GATE#1
  como siempre.
- **El árbol principal es solo para integrar.** Cuando una feature queda
  `archived`, la llevas a la rama de integración con un *squash* (un commit
  por feature, con el mensaje de `archive.md`) y pasas `verify.sh`.
- `scripts/ola.sh` hace la mecánica: abrir, estado, integrar y cerrar
  (`docs/planes/guia-olas.md`).

| Etapa | Features | Olas | Mínimo teórico (ruta más larga) |
| --- | --- | --- | --- |
| <versión> | <n> | <n> | <n> |

### Por qué hace falta un worktree por feature

En el mismo árbol, dos features a la vez rompen tres cosas del harness:

1. **El diff del reviewer se mezcla.** Al aprobar GATE#1, el harness guarda el
   HEAD como `base_commit`. Después el reviewer y los especialistas revisan
   `git diff <base_commit>`, y con dos features en el árbol cada uno vería
   también el código del otro.
2. **La regresión falla por código ajeno.** `verify.sh` de una feature
   fallaría por el código a medias de la otra.
3. **`feature.py` puede perder transiciones.** Reescribe `feature_list.json`
   sin bloqueo entre procesos, así que dos transiciones a la vez pueden perder
   una.

Con un worktree por feature, cada sesión ve un repo propio y las tres cosas
funcionan igual que en serie.

## 2. Reglas de las olas

1. **Arranca una feature solo cuando todas sus dependencias estén integradas**
   en la rama de integración, y crea su worktree desde ella. Las dependencias
   son las de «depende de:» en las notas de `feature_list.json` más las
   implícitas de §8.
2. **Una feature por worktree y por sesión**, siempre con su ID explícito.
3. **Nada se construye en el árbol principal mientras haya worktrees
   abiertos.** El árbol principal está en la rama de integración, limpio, y
   solo sirve para integrar.
4. **Como mucho `MAX_ABIERTAS` features a la vez**, y menos si tu máquina va
   justa (§3.2). El límite real eres tú: GATE#1, dependencias e
   integraciones.
5. **Una por módulo.** Dos features que tocan el mismo módulo, registro
   central o formato de datos del usuario no van en la misma ola.
6. **Integra de una en una**, en el orden que marca cada ola (la ruta crítica
   primero). Tras cada integración, `verify.sh` debe quedar en verde antes de
   integrar la siguiente.
7. **Una sola E2E a la vez** si las pruebas usan puertos o recursos fijos. Las
   features de pruebas de versión (x98) van solas y con todo integrado.
8. **Los cuellos de botella van con compañía ligera.** <IDs de las features de
   las que dependen muchas otras>: revisa su GATE#1 con calma y no les pongas
   al lado otra L del mismo dominio.
9. **No se cruzan versiones.** Una ola nunca mezcla versiones del roadmap.
10. **Ritmo continuo.** Las olas son lotes de referencia. Si una feature de la
    ola siguiente ya tiene todas sus dependencias integradas y su módulo está
    libre, puedes arrancarla sin esperar a que acabe la ola entera.

## 3. Preparación (una vez)

### 3.1 AGENTS.md

`AGENTS.md` ya trae el apartado «Paralelo» de la sección Git y la convención
de dependencias en las notas. Si lo fusionaste con uno anterior, comprueba
que siguen ahí: sin ellos, los agentes creerán que los builds van de uno en
uno.

### 3.2 Máquina

- **Disco.** Cada worktree es una copia del árbol de trabajo con sus
  dependencias y compilados. Pon la carpeta de worktrees en un disco rápido;
  en WSL, en el disco de Linux (`~/<repo>-wt`), nunca en `/mnt/c` o `/mnt/d`.
- **RAM y CPU.** Varias compilaciones y suites de pruebas a la vez pesan. En
  WSL2, sube `memory=` y `processors=` en `%UserProfile%\.wslconfig`. Con
  16 GB de RAM, 2 o 3 builds a la vez como mucho.
- **Ajustes locales.** `ola.sh` copia `.claude/settings.local.json` a cada
  worktree nuevo (git no lo versiona).
- **tmux** para tener una ventana por feature. Sin tmux, `--sin-tmux`
  imprime el comando de cada sesión.

### 3.3 Dependencias de una ola (opcional, recomendado)

Si varias features de una ola necesitan paquetes nuevos, instálalos antes de
abrir los worktrees, de una vez, desde la rama de integración:

```text
Fuera del flujo, cambio concreto: instala las dependencias nuevas que listan
los planes de APP-AAA, APP-BBB y APP-CCC (versiones exactas y licencias),
enséñame los comandos antes y no toques nada más.
```

Haz commit (`build: dependencias de la ola O1.3`) y después abre la ola. Así
evitas casi todos los conflictos de lockfiles.

## 4. Ciclo de una feature en paralelo

| Paso | Orden | Quién |
| --- | --- | --- |
| Abrir | `bash scripts/ola.sh abrir APP-101 APP-102` | script (desde el árbol principal) |
| Trabajar | la sesión de cada ventana: explorer → designer → GATE#1 → builder → reviewer | Claude + tú (GATE#1) |
| Vigilar | `bash scripts/ola.sh estado` | script |
| Integrar | `bash scripts/ola.sh integrar APP-101`: squash, pasos del proyecto, `verify.sh` y commit con el mensaje de `archive.md` | script + tú (commit y push) |
| Cerrar | `bash scripts/ola.sh cerrar APP-101` | script |

- **Si `verify.sh` falla al integrar** (cada feature pasó su verificación por
  separado, pero juntas no), no lo arregles a mano encima: `integrar
  --abortar` y registra un bug en la rama de integración con el log.
- **Las demás features de la ola no necesitan rebase.** Sus conflictos se
  resuelven cuando les toca integrarse.

## 5. Conflictos esperables al integrar

Casi todos son registros donde cada feature añade una línea. Se resuelven
conservando los dos lados. Completa la tabla con los archivos compartidos de
tu proyecto.

| Dónde | Por qué choca | Cómo se resuelve |
| --- | --- | --- |
| `.claude/feature_list.json` | Seguimientos añadidos al final y cambios de `status` | Automático: `ola.sh` une las features por ID. |
| Lockfiles (`pnpm-lock.yaml`, `uv.lock`, `Cargo.lock`…) | Dependencias nuevas en dos features | Nunca a mano: lado de la rama de integración y reinstalar. Ponlos en `AUTO_RAMA` y el comando en `TRAS_INTEGRAR`. |
| Manifiestos (`package.json`, `pyproject.toml`…) | Dependencias nuevas en dos features | Conserva las dos líneas. |
| Código generado (clientes, bindings, tipos) | Se regenera en cada feature | Nunca a mano: `AUTO_RAMA` + su generador en `TRAS_INTEGRAR`. |
| Registros (rutas, comandos, errores, catálogos de textos, ajustes) | Cada feature registra lo suyo | Conserva las dos entradas. |
| Migraciones de base de datos | Dos features añaden «la siguiente» | Primero la de la rama de integración y después la nueva, con el número siguiente. |
| Documentación de formatos | Dos features documentan el mismo formato | Une los dos apartados. |

## 6. Las olas

Una tabla por versión o etapa del roadmap. Cómo leerla:

- «Integra en este orden»: qué va primero (ruta crítica o quien cambia la
  forma de algo compartido).
- «Vigila»: lo que puede chocar.
- «Decides tú»: las decisiones de GATE#1 y los pasos humanos previos.

### <versión> · <objetivo>

| Ola | Features | Integra en este orden | Vigila | Decides tú |
| --- | --- | --- | --- | --- |
| **O1.1** | APP-101 | — | Cuello de botella: sola. | <decisión de GATE#1> |
| **O1.2** | APP-102 · APP-103 · APP-104 | 104 → 103 → 102 | <archivos compartidos> | — |
| **O1.x** | APP-198 | — | Pruebas de la versión: sola, con todo integrado. | — |
| **O1.y** | APP-199 | — | Release (§7). | <firma, publicación> |

## 7. Entre versiones

- **La x98 va sola**, con toda la versión integrada: comprueba E2E,
  accesibilidad y rendimiento de la versión entera.
- **La x99 (release)** se apoya en la rama de release (`main`): PR de la rama
  de integración a `main`, ensayo y publicación. Mientras dura **puedes
  construir la primera ola de la versión siguiente en worktrees**, pero **no
  integres nada** hasta que la release esté publicada. Si no, la release
  arrastraría código de la versión siguiente.
- **Al publicar,** fusiona `main` en la rama de integración y sigue
  integrando.

## 8. Dependencias implícitas que respetan las olas

Código que una feature usa de otra sin declararlo en sus notas. En serie no
importa, porque el orden global ya las respeta; en paralelo sí. Dalas de alta
también en el mapa `IMPLICITAS` de `scripts/ola.sh` (el script las exige igual
que las declaradas) o, mejor, en las notas de la feature.

| Feature | Necesita antes | Motivo (plan y sección) |
| --- | --- | --- |
| APP-109 | APP-105 | Usa la cola de trabajos que crea APP-105 (plan 02 §3). |

## 9. Cuándo no paralelizar

- **Cuando el GATE#1 de un cuello de botella** te pide pensar: mejor esa
  feature sola, aunque la ola admita más.
- **Cuando `verify.sh` falla al integrar.** Para y arregla en la rama de
  integración antes de integrar la siguiente; si no, los fallos se acumulan y
  ya no sabrás de quién son.
- **Cuando la máquina no da abasto.** Si un comando de aceptación supera su
  `timeout` por la carga de las otras sesiones, el reviewer devuelve
  `BLOCKED_TOOLING`. Baja a 2 sesiones y usa `retry_verification`.
- **Cuando dos features tocan el mismo formato de datos del usuario.** Las
  olas ya lo evitan; si adelantas una, compruébalo.

## 10. Prompts

**Arrancar una feature en su worktree** (lo envía `ola.sh abrir` solo; úsalo
si abres la sesión a mano):

```text
Esta sesión trabaja en el worktree wt/app-nnn y solo lleva APP-NNN (modo olas,
docs/planes/olas.md). Autorizo construir esta feature en paralelo en este
worktree. Arráncala con sdd-feature-planning (o reanúdala con feature-resume).
No crees ramas ni hagas commits. Al archivar, dame el mensaje de «## Commit
sugerido» de archive.md y para.
```

**Integrar con conflictos** (en el árbol principal, cuando `ola.sh integrar`
para con conflictos):

```text
Fuera del flujo, cambio concreto que te pido: integro APP-NNN y el squash ha
dejado conflictos. Resuélvelos sin cambiar comportamiento, según la tabla de
§5 de docs/planes/olas.md: en registros conserva las entradas de los dos
lados; en migraciones, primero la de la rama de integración y después la
nueva con el número siguiente; lockfiles y código generado, nunca a mano. No
ejecutes verify ni hagas commit: avísame cuando no queden marcas.
```

**Llevar las olas desde Claude Code** (sesión del árbol principal, sin
feature): `/ola siguiente`.
