#!/usr/bin/env bash
# ola.sh — varias features a la vez, cada una en su worktree (docs/planes/olas.md).
#
#   bash scripts/ola.sh abrir APP-007 APP-009   worktree + instalación + sesión de Claude Code por feature
#   bash scripts/ola.sh estado                  qué hay abierto, en qué fase y qué falta
#   bash scripts/ola.sh integrar APP-009        squash en la rama de integración, lo mecánico, verify y commit
#   bash scripts/ola.sh integrar --continuar    sigue tras resolver conflictos a mano
#   bash scripts/ola.sh integrar --abortar      deshace una integración a medias
#   bash scripts/ola.sh cerrar APP-009          borra worktree, rama temporal y ventana
#   bash scripts/ola.sh ayuda | version
#
# Opciones:  --dir <carpeta>  worktrees (por defecto ~/<repo>-wt o $OLA_DIR)
#            --sin-tmux       no abre tmux: imprime el comando de cada sesión
#            --forzar         abrir sin dependencias integradas / cerrar sin estar integrada
#            --si             responde «sí» a las confirmaciones (prohibido desde Claude Code)
#
# Nunca aprueba GATE#1 ni hace commit o push sin preguntarte.
set -Eeuo pipefail

VERSION="3"

# ================================================================ configuración del proyecto
# Lo único que se adapta por proyecto (INSTRUCCIONES/OLAS.md del harness).
RAMA="${OLA_RAMA:-develop}"          # rama de integración (el árbol principal vive en ella)
MAX_ABIERTAS="${OLA_MAX:-4}"         # features abiertas a la vez antes de pedir confirmación
TMUX_SESSION="${OLA_TMUX:-}"         # vacío: <repo>-olas
PREFIJO="${OLA_PREFIJO:-}"           # opcional: permite escribir solo el número (007 → <PREFIJO>-007)

# Instalación en cada worktree nuevo. Vacío: no instala nada.
INSTALAR=""                          # p. ej. "pnpm install --frozen-lockfile --prefer-offline || pnpm install --prefer-offline"
INSTALAR_SI_FALTA=""                 # p. ej. "node_modules": solo instala si no existe; vacío: instala en cada «abrir»

# Conflictos que se resuelven con el lado de la rama de integración porque se regeneran después
# (lockfiles, código generado). Patrones de `case`.
AUTO_RAMA=(
  # "pnpm-lock.yaml" "*/pnpm-lock.yaml" "src/bindings.ts"
)

# Pasos tras el squash, en orden: «regex de archivos cambiados :: comando». Cada paso se ejecuta
# si algún archivo que cambió la feature encaja con su regex.
TRAS_INTEGRAR=(
  # '(^|/)(package\.json|pnpm-lock\.yaml)$ :: pnpm install --prefer-offline'
  # '^api/openapi\.yaml$ :: pnpm gen:api'
)

# Dependencias implícitas (olas.md §8): se exigen igual que las de «depende de:» en las notas.
declare -A IMPLICITAS=(
  # [APP-109]="APP-105"   [APP-126]="APP-103 APP-105"
)

# Cómo arranca cada sesión su feature ({ID} se sustituye por el ID).
ARRANQUE='Arráncala con la skill sdd-feature-planning ({ID}); si ya estaba empezada, reanúdala con la skill feature-resume.'
# ================================================================ fin de la configuración

WT_DIR="${OLA_DIR:-}"
ID_RE='^[A-Z][A-Z0-9]*(-[A-Z0-9]+)*-[0-9]+$'   # FEATURE_ID_PATTERN de .claude/tools/harness_lib.py
USE_TMUX=1; FORCE=0; YES=0

if [ -t 1 ]; then R=$'\e[31m'; G=$'\e[32m'; Y=$'\e[33m'; B=$'\e[1m'; N=$'\e[0m'; else R=; G=; Y=; B=; N=; fi
die()  { echo "${R}✗ $*${N}" >&2; exit 1; }
warn() { echo "${Y}! $*${N}" >&2; }
info() { echo "→ $*"; }
ok()   { echo "${G}✓ $*${N}"; }
trap 'echo "${R}✗ Error inesperado en la línea $LINENO (comando: $BASH_COMMAND). No se ha hecho commit ni push.${N}" >&2' ERR

confirm() {   # confirm "pregunta" → 0 si sí
  if [ -n "${CLAUDECODE:-}" ]; then echo "$1 → no (lanzado desde Claude Code: esto lo decide y lo hace el humano)"; return 1; fi
  [ "$YES" = 1 ] && { echo "$1 [s/N] s (--si)"; return 0; }
  [ -t 0 ] || { warn "$1 → sin terminal interactiva: lo tomo como «no» (usa --si si lo quieres)"; return 1; }
  local a; read -r -p "$1 [s/N] " a || return 1
  [[ "${a,,}" == s || "${a,,}" == si || "${a,,}" == sí || "${a,,}" == y ]]
}

usage() { awk 'NR > 1 && /^#/ { sub(/^# ?/, ""); print; next } NR > 1 { exit }' "$0"; }

# ---------------------------------------------------------------- argumentos
ARGS=()
while [ $# -gt 0 ]; do
  case "$1" in
    --dir) [ $# -ge 2 ] || die "--dir necesita una carpeta"; WT_DIR="$2"; shift 2 ;;
    --sin-tmux) USE_TMUX=0; shift ;;
    --forzar) FORCE=1; shift ;;
    --si) YES=1; shift ;;
    -h|--help|ayuda) usage; exit 0 ;;
    version) echo "ola.sh $VERSION"; exit 0 ;;
    *) ARGS+=("$1"); shift ;;
  esac
done
set -- ${ARGS[@]+"${ARGS[@]}"}
[ $# -ge 1 ] || { usage; exit 1; }
CMD="$1"; shift

if [ -n "${CLAUDECODE:-}" ] && [ "$YES" = 1 ]; then
  die "--si no se permite desde Claude Code: los commits y el push los hace el humano"
fi
for t in git python3; do command -v "$t" >/dev/null || die "falta $t"; done
[ "${BASH_VERSINFO[0]}" -ge 4 ] || die "hace falta bash 4 o superior"

# ---------------------------------------------------------------- repo principal
ORIG_PWD="$PWD"
git rev-parse --is-inside-work-tree >/dev/null 2>&1 || die "ejecútalo dentro del repositorio"
ROOT="$(git worktree list --porcelain | sed -n '1s/^worktree //p')"   # el primero es siempre el principal
[ -n "$ROOT" ] && [ -d "$ROOT" ] || die "no encuentro el árbol principal del repo"
if [ "$(git rev-parse --show-toplevel)" != "$ROOT" ]; then
  warn "Estás dentro de un worktree; trabajo sobre el árbol principal: $ROOT"
fi
cd "$ROOT"
[ -f .claude/tools/feature.py ] || die "no encuentro .claude/tools/feature.py en $ROOT: ¿tiene el harness instalado?"
REPO="$(basename "$ROOT")"
[ -n "$WT_DIR" ] || WT_DIR="$HOME/$REPO-wt"
[ -n "$TMUX_SESSION" ] || TMUX_SESSION="$REPO-olas"
GIT_DIR_ABS="$(cd "$(git rev-parse --git-dir)" && pwd)"
MARK="$GIT_DIR_ABS/ola-integrando"
WT_DIR="$(realpath -m "${WT_DIR/#\~/$HOME}")"
case "$WT_DIR/" in "$ROOT"/*) die "la carpeta de worktrees no puede estar dentro del repo ($WT_DIR)";; esac

# Un solo ola.sh a la vez sobre este repo (el candado va en un disco Linux: flock no funciona en /mnt/c o /mnt/d).
if command -v flock >/dev/null; then
  LOCK="${XDG_RUNTIME_DIR:-/tmp}/ola-$(printf '%s' "$ROOT" | cksum | cut -d' ' -f1).lock"
  if { exec 9>"$LOCK"; } 2>/dev/null; then
    flock -n 9 || die "ya hay otro ola.sh en marcha sobre este repo; espera a que termine"
  fi
fi

# ---------------------------------------------------------------- utilidades
norm_id() {
  local raw="${1^^}"
  if [[ "$raw" =~ ^[0-9]+$ ]] && [ -n "$PREFIJO" ]; then raw="$PREFIJO-$raw"; fi
  [[ "$raw" =~ $ID_RE ]] || die "ID no válido: «$1» (usa el formato del harness, p. ej. APP-007)"
  echo "$raw"
}
slug()    { echo "${1,,}"; }
wt_path() { echo "$WT_DIR/$(slug "$1")"; }
branch()  { echo "wt/$(slug "$1")"; }
is_worktree() { git worktree list --porcelain | grep -qxF "worktree $1"; }
has_branch()  { git show-ref --verify --quiet "refs/heads/$1"; }

# Lee feature_list.json de una revisión (rama) o de un archivo. Imprime el status, «-» si no está, «?» si no se lee.
status_in() {   # status_in <rev|ruta> <ID>
  local src="$1" id="$2" json
  if [ -f "$src" ]; then json="$(cat "$src")"; else json="$(git show "$src:.claude/feature_list.json" 2>/dev/null)" || { echo "?"; return; }; fi
  python3 -c '
import json, sys
data = json.loads(sys.stdin.read())
fid = sys.argv[1]
print(next((f.get("status", "?") for f in data.get("features", []) if f.get("id") == fid), "-"))
' "$id" <<<"$json"
}
deps_of() {     # dependencias de las notas («depende de: A, B» hasta el siguiente «·») + implícitas
  local id="$1"
  { git show "$RAMA:.claude/feature_list.json" | python3 -c '
import json, re, sys
fid = sys.argv[1]
for f in json.loads(sys.stdin.read()).get("features", []):
    if f.get("id") == fid:
        m = re.search(r"depende de:\s*([^·]*)", f.get("notes") or "")
        print(" ".join(re.findall(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[0-9]+", m.group(1) if m else "")))
' "$id"; } 2>/dev/null || true
  echo "${IMPLICITAS[$id]:-}"
}
tm() { tmux "$@" 9>&-; }   # sin heredar el candado: el servidor de tmux vive más que ola.sh
in_tmux_window() { command -v tmux >/dev/null && tm list-windows -t "$TMUX_SESSION" -F '#W' 2>/dev/null | grep -qxF "$1"; }

prompt_for() {
  local id="$1"
  printf '%s' "Esta sesión trabaja en el worktree $(branch "$id") y solo lleva $id (modo olas, docs/planes/olas.md). Autorizo construir esta feature en paralelo en este worktree: una sola feature aquí. ${ARRANQUE//\{ID\}/$id} No crees ramas ni hagas commits. Al archivar, dame el mensaje de «## Commit sugerido» de archive.md y para."
}

open_count() { git worktree list --porcelain | sed -n 's/^worktree //p' | grep -c "^$WT_DIR/" || true; }

# ---------------------------------------------------------------- abrir
cmd_abrir() {
  [ $# -ge 1 ] || die "indica al menos una feature: abrir APP-007 APP-009"
  has_branch "$RAMA" || die "no existe la rama $RAMA"
  local ids=() id raw
  for raw in "$@"; do ids+=("$(norm_id "$raw")"); done
  mkdir -p "$WT_DIR"
  git worktree prune

  # Comprobaciones antes de tocar nada.
  local problems=0 st d dst mst
  for id in "${ids[@]}"; do
    st="$(status_in "$RAMA" "$id")"
    case "$st" in
      proposed) ;;
      -) warn "$id no está en feature_list.json de $RAMA"; problems=1; continue ;;
      *) if ! is_worktree "$(wt_path "$id")"; then warn "$id está «$st» en $RAMA (ya empezada o hecha)"; problems=1; fi; continue ;;
    esac
    mst="$(status_in "$ROOT/.claude/feature_list.json" "$id")"
    if [ "$mst" != proposed ] && [ "$mst" != - ]; then
      warn "$id está «$mst» en el árbol principal (se está haciendo allí)"; problems=1; continue
    fi
    for d in $(deps_of "$id"); do
      dst="$(status_in "$RAMA" "$d")"
      if [ "$dst" != archived ]; then
        warn "$id depende de $d, que en $RAMA está «$dst» (tiene que estar integrada)"
        [ "$FORCE" = 1 ] || problems=1
      fi
    done
  done
  [ "$problems" = 0 ] || die "no abro nada. Corrige lo anterior (o usa --forzar si sabes lo que haces)."
  local total=$(( $(open_count) + ${#ids[@]} ))
  if [ "$total" -gt "$MAX_ABIERTAS" ]; then
    warn "quedarían $total features abiertas a la vez (recomendado ≤ $MAX_ABIERTAS)."
    confirm "¿Abrir de todas formas?" || exit 1
  fi

  local path br
  for id in "${ids[@]}"; do
    path="$(wt_path "$id")"; br="$(branch "$id")"
    if is_worktree "$path"; then
      info "$id: el worktree ya existe ($path); lo reutilizo"
    elif [ -e "$path" ]; then
      die "$path existe pero no es un worktree de este repo. Muévelo o bórralo y repite."
    elif has_branch "$br"; then
      info "$id: la rama $br ya existe (sin carpeta); recreo el worktree sobre ella sin perder su trabajo"
      git worktree add "$path" "$br" >/dev/null
    else
      info "$id: nuevo worktree $path (rama $br desde $RAMA)"
      git worktree add "$path" -b "$br" "$RAMA" >/dev/null
    fi
    if [ -f .claude/settings.local.json ] && [ ! -f "$path/.claude/settings.local.json" ]; then
      cp .claude/settings.local.json "$path/.claude/"
    fi
    if [ -n "$INSTALAR" ] && { [ -z "$INSTALAR_SI_FALTA" ] || [ ! -e "$path/$INSTALAR_SI_FALTA" ]; }; then
      info "$id: $INSTALAR"
      (cd "$path" && bash -c "$INSTALAR") \
        || die "$id: falló la instalación en $path. Arregla la causa y repite «abrir $id»: reutilizo el worktree."
    fi
  done

  local p
  if [ "$USE_TMUX" = 1 ] && command -v tmux >/dev/null && command -v claude >/dev/null; then
    tm has-session -t "$TMUX_SESSION" 2>/dev/null || tm new-session -d -s "$TMUX_SESSION" -n integrar -c "$ROOT"
    local s
    for id in "${ids[@]}"; do
      s="$(slug "$id")"; path="$(wt_path "$id")"
      if in_tmux_window "$s"; then info "$id: ya tiene ventana en tmux"; continue; fi
      p="$(prompt_for "$id")"
      tm new-window -d -t "$TMUX_SESSION:" -n "$s" -c "$path"
      tm send-keys -t "$TMUX_SESSION:$s" -l "claude $(printf '%q' "$p")"
      tm send-keys -t "$TMUX_SESSION:$s" Enter
      ok "$id: sesión de Claude Code abierta en la ventana «$s»"
    done
    echo
    if [ -n "${TMUX:-}" ]; then echo "Ya estás en tmux: ${B}Ctrl+b w${N} para elegir ventana."
    else echo "Entra con: ${B}tmux attach -t $TMUX_SESSION${N}   (Ctrl+b w elige ventana · Ctrl+b d sale sin cerrar nada)"; fi
  else
    [ "$USE_TMUX" = 1 ] && warn "no encuentro tmux o claude: abre tú cada sesión."
    echo; echo "Abre una terminal por feature y pega:"
    for id in "${ids[@]}"; do
      p="$(prompt_for "$id")"
      echo "  ${B}cd $(printf '%q' "$(wt_path "$id")") && claude $(printf '%q' "$p")${N}"
    done
  fi
}

# ---------------------------------------------------------------- estado
cmd_estado() {
  echo "${B}Árbol principal${N}: $ROOT ($(git branch --show-current))"
  if [ -f "$MARK" ]; then warn "integración a medias de $(cat "$MARK"): termina con «integrar --continuar» o «integrar --abortar»"; fi
  local dirty; dirty="$(git status --porcelain | wc -l)"
  [ "$dirty" -eq 0 ] && echo "  limpio" || echo "  $dirty archivos con cambios sin commit"
  echo
  local found=0 path id s phase ahead wdirty win
  while read -r path; do
    case "$path" in "$WT_DIR"/*) ;; *) continue ;; esac
    found=1; s="${path##*/}"; id="${s^^}"
    if [ -d "$path" ]; then
      phase="$(python3 "$path/.claude/tools/feature.py" --root "$path" status "$id" 2>/dev/null | sed -n '2p' | sed 's/^ *//')" || phase=""
      [ -n "$phase" ] || phase="sin arrancar"
      wdirty="$(git -C "$path" status --porcelain 2>/dev/null | wc -l)"
    else phase="(carpeta borrada)"; wdirty=0; fi
    ahead="$(git rev-list --count "$RAMA..$(branch "$id")" 2>/dev/null || echo 0)"
    win="no"; in_tmux_window "$s" && win="sí"
    echo "${B}$id${N}  $phase"
    echo "     $path · commits sin integrar: $ahead · cambios sin commit: $wdirty · ventana tmux: $win"
  done < <(git worktree list --porcelain | sed -n 's/^worktree //p')
  [ "$found" = 1 ] || echo "No hay features abiertas en $WT_DIR."
}

# ---------------------------------------------------------------- integrar
matches_auto() {   # ¿el archivo encaja con algún patrón de AUTO_RAMA?
  local f="$1" pat
  for pat in ${AUTO_RAMA[@]+"${AUTO_RAMA[@]}"}; do
    # shellcheck disable=SC2254
    case "$f" in $pat) return 0 ;; esac
  done
  return 1
}

resolve_auto() {   # resuelve lo mecánico; lo demás queda en conflicto
  local f
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    if [ "$f" = .claude/feature_list.json ]; then
      if python3 - "$f" <<'PY'
import json, subprocess, sys
path = sys.argv[1]
def side(n):
    return json.loads(subprocess.run(["git", "show", f":{n}:{path}"], check=True, capture_output=True, text=True).stdout)
ours, theirs = side(2), side(3)
rank = {"archived": 9, "cancelled": 8}
by_id = {f["id"]: f for f in ours["features"]}
order = [f["id"] for f in ours["features"]]
for f in theirs["features"]:
    if f["id"] not in by_id:
        by_id[f["id"]] = f; order.append(f["id"])
    elif rank.get(f.get("status"), 1) > rank.get(by_id[f["id"]].get("status"), 1):
        by_id[f["id"]] = f
ours["features"] = [by_id[i] for i in order]
with open(path, "w", encoding="utf-8") as fh:
    fh.write(json.dumps(ours, ensure_ascii=False, indent=2) + "\n")
PY
      then git add -- "$f"; info "auto: $f (unión de features por ID)"; else warn "no pude fusionar $f solo"; fi
    elif matches_auto "$f"; then
      git checkout --ours -- "$f" && git add -- "$f" && info "auto: $f (lado de $RAMA; se regenera tras integrar)"
    fi
  done < <(git diff --name-only --diff-filter=U)
}

post_merge() {   # tras un squash sin conflictos pendientes: pasos del proyecto, verify y commit
  local id="$1" changed step regex command
  changed="$(git diff --cached --name-only)"
  [ -n "$changed" ] || { rm -f "$MARK"; die "no hay nada que integrar de $id (¿ya estaba integrada?)"; }
  # Lo que cambió la feature, aunque un conflicto se resolviera con el lado de la rama de integración.
  changed="$changed"$'\n'"$(git diff --name-only "HEAD...$(branch "$id")" 2>/dev/null || true)"

  for step in ${TRAS_INTEGRAR[@]+"${TRAS_INTEGRAR[@]}"}; do
    regex="${step%% :: *}"; command="${step#* :: }"
    if grep -qE "$regex" <<<"$changed"; then
      info "$command"
      bash -c "$command" || die "falló «$command». Arregla y repite «integrar --continuar»."
    fi
  done
  git add -A
  if git diff --cached -U0 | grep -qE '^\+(<<<<<<<|>>>>>>>)( |$)'; then
    git diff --cached -U0 | grep -nE '^(\+\+\+ |\+(<<<<<<<|>>>>>>>)( |$))' | head -20
    die "quedan marcas de conflicto (<<<<<<< / >>>>>>>). Resuélvelas y repite «integrar --continuar»."
  fi

  if [ -f .claude/bootstrap/verify.sh ]; then
    info "verify.sh (regresión completa; puede tardar)"
    if ! bash .claude/bootstrap/verify.sh; then
      echo
      warn "verify.sh falla con $id integrada. No hay commit. Opciones:"
      echo "   a) un conflicto mal resuelto → corrígelo y «bash scripts/ola.sh integrar --continuar»"
      echo "   b) incompatibilidad real entre features → «bash scripts/ola.sh integrar --abortar» y registra un bug en $RAMA con el log"
      exit 1
    fi
  else warn "no hay .claude/bootstrap/verify.sh: me salto la regresión"; fi

  echo; ok "$id integrada y en verde. Cambios preparados:"
  git diff --cached --stat | tail -n 15
  local msg; msg="$(commit_msg "$id")"
  echo
  if [ -n "$msg" ]; then
    echo "Mensaje de .claude/state/$id/archive.md («Commit sugerido»):"; echo "${B}$msg${N}" | sed 's/^/   /'
    if confirm "¿Hago el commit con este mensaje?"; then
      if git commit -q -m "$msg"; then
        rm -f "$MARK"; ok "commit hecho: $(git log -1 --format='%h %s')"
        if confirm "¿Hago push de $RAMA?"; then git push || warn "el push falló (¿$RAMA remoto avanzó? «git pull --rebase» y «git push»)"; fi
        echo "Siguiente: ${B}bash scripts/ola.sh cerrar $id${N}"
        return 0
      fi
      warn "git commit falló (¿hooks de commit?). Los cambios siguen preparados: corrige y haz «git commit» tú."
      exit 1
    fi
  else
    warn "no encuentro un «## Commit sugerido» en Conventional Commits en .claude/state/$id/archive.md"
  fi
  if [ -n "$msg" ]; then
    printf '%s\n' "$msg" > "$GIT_DIR_ABS/ola-commit-msg"
    echo "Haz tú el commit (mensaje ya preparado):  ${B}git commit -F '$GIT_DIR_ABS/ola-commit-msg' && git push${N}"
  else
    echo "Haz tú el commit:  ${B}git commit -m \"<mensaje>\" && git push${N}"
  fi
  echo "y después:  ${B}bash scripts/ola.sh cerrar $id${N}"
  echo "(la marca de integración se limpia sola en la próxima orden)"
}

commit_msg() {
  local f=".claude/state/$1/archive.md"
  [ -f "$f" ] || return 0
  python3 - "$f" <<'PY'
import re, sys
text = open(sys.argv[1], encoding="utf-8").read()
m = re.search(r"^##\s*Commit sugerido\s*$(.*?)(?=^##\s|\Z)", text, re.S | re.M)
if not m:
    sys.exit(0)
lines = [l.rstrip() for l in m.group(1).strip().splitlines() if not l.strip().startswith("```")]
lines = [l.strip("`") for l in lines]
while lines and not lines[0].strip():
    lines.pop(0)
if lines and re.match(r"^(feat|fix|docs|refactor|perf|test|build|ci|chore|revert|style)(\([^)]+\))?!?: \S", lines[0]):
    print("\n".join(lines).strip())
PY
}

cmd_integrar() {
  case "${1:-}" in
    --continuar)
      [ -f "$MARK" ] || die "no hay ninguna integración a medias"
      local id; id="$(cat "$MARK")"
      local left=() f
      while IFS= read -r f; do [ -n "$f" ] && left+=("$f"); done < <(git diff --name-only --diff-filter=U)
      for f in ${left[@]+"${left[@]}"}; do
        if grep -qE '^(<<<<<<<|>>>>>>>)( |$)' "$f" 2>/dev/null; then die "$f todavía tiene marcas de conflicto"; fi
        git add -- "$f"
      done
      [ -z "$(git diff --name-only --diff-filter=U)" ] || die "quedan archivos en conflicto: $(git diff --name-only --diff-filter=U | tr '\n' ' ')"
      post_merge "$id"; return ;;
    --abortar)
      [ -f "$MARK" ] || [ -n "$(git diff --cached --name-only)" ] || die "no hay ninguna integración a medias"
      echo "Se descartan TODOS los cambios del árbol principal (estaba limpio antes de integrar)."
      confirm "¿Deshago la integración de $(cat "$MARK" 2>/dev/null || echo '?')?" || exit 1
      git reset -q --hard HEAD && rm -f "$MARK" && ok "integración deshecha; $RAMA queda como estaba. El worktree no se toca."
      return ;;
  esac
  [ $# -eq 1 ] || die "integra una feature cada vez: integrar APP-009"
  local id br path wst
  id="$(norm_id "$1")"; br="$(branch "$id")"; path="$(wt_path "$id")"

  if [ -f "$MARK" ]; then
    if [ -z "$(git diff --cached --name-only)" ] && [ -z "$(git status --porcelain)" ]; then rm -f "$MARK"
    else die "hay una integración a medias de $(cat "$MARK"): «integrar --continuar» o «integrar --abortar»"; fi
  fi
  [ "$(git branch --show-current)" = "$RAMA" ] || die "el árbol principal tiene que estar en $RAMA (git switch $RAMA)"
  if [ -n "$(git status --porcelain)" ]; then
    git status --short | head
    die "el árbol principal tiene cambios sin commit. Haz commit de lo anterior antes de integrar."
  fi
  has_branch "$br" || die "no existe la rama $br (¿la abriste con «abrir $id»?)"
  [ "$(status_in "$RAMA" "$id")" = archived ] && die "$id ya está archived en $RAMA: ya está integrada. Usa «cerrar $id»."

  # El worktree: todo commiteado y la feature archivada en ese commit.
  if [ -d "$path" ] && [ -n "$(git -C "$path" status --porcelain)" ]; then
    wst="$(status_in "$path/.claude/feature_list.json" "$id")"
    [ "$wst" = archived ] || die "$id está «$wst» en su worktree: termina la feature antes de integrar"
    echo "El worktree $path tiene cambios sin commit (lo normal al archivar)."
    confirm "¿Los commiteo allí como «chore($(slug "$id")): trabajo de la feature»?" \
      || die "falta el commit del worktree. Hazlo tú y repite «integrar $id»:
     git -C '$path' add -A && git -C '$path' commit --no-verify -m 'chore($(slug "$id")): trabajo de la feature'"
    git -C "$path" add -A
    git -C "$path" commit -q -m "chore($(slug "$id")): trabajo de la feature" --no-verify \
      || die "no pude hacer el commit en el worktree"
    ok "commit en $br"
  fi
  wst="$(status_in "$br" "$id")"
  [ "$wst" = archived ] || die "$id está «$wst» en la rama $br: solo se integra una feature archived"
  git show "$br:.claude/state/$id/archive.md" >/dev/null 2>&1 || die "falta .claude/state/$id/archive.md en $br"

  echo "$id" > "$MARK"
  info "git merge --squash $br"
  if git merge --squash --no-commit "$br" >/dev/null 2>&1; then
    post_merge "$id"; return
  fi
  if [ -z "$(git diff --name-only --diff-filter=U)" ]; then
    rm -f "$MARK"; git reset -q --hard HEAD
    die "git merge --squash falló sin conflictos (revisa «git merge --squash $br» a mano)"
  fi
  info "hay conflictos; resuelvo los mecánicos"
  resolve_auto
  local left; left="$(git diff --name-only --diff-filter=U)"
  if [ -z "$left" ]; then post_merge "$id"; return; fi
  echo
  warn "quedan conflictos que hay que resolver a mano:"
  echo "$left" | sed 's/^/     /'
  cat <<EOF

  Qué hacer (docs/planes/olas.md §5):
   1. Abre cada archivo, busca <<<<<<< y, en los registros, deja las entradas de los
      dos lados. O pídeselo a Claude Code en el árbol principal con el prompt de
      «integrar con conflictos» de olas.md §10.
   2. ${B}bash scripts/ola.sh integrar --continuar${N}
  Si prefieres dejarlo:  ${B}bash scripts/ola.sh integrar --abortar${N}  ($RAMA queda como estaba)
EOF
  exit 2
}

# ---------------------------------------------------------------- cerrar
cmd_cerrar() {
  [ $# -eq 1 ] || die "cerrar <ID>"
  local id s path br
  id="$(norm_id "$1")"; s="$(slug "$id")"; path="$(wt_path "$id")"; br="$(branch "$id")"
  if [ -f "$MARK" ] && [ "$(cat "$MARK")" = "$id" ] && [ -n "$(git diff --cached --name-only)" ]; then
    die "$id está a medio integrar: termina con «integrar --continuar» (o --abortar) antes de cerrar"
  fi
  if [ "$(status_in "$RAMA" "$id")" != archived ]; then
    warn "$id no está archived en $RAMA: su trabajo NO está integrado y se perdería."
    [ "$FORCE" = 1 ] || die "no cierro. Si de verdad quieres tirarlo: «cerrar $id --forzar»"
    confirm "¿Borrar el worktree y la rama $br con su trabajo sin integrar?" || exit 1
  fi
  if command -v tmux >/dev/null && in_tmux_window "$s"; then
    tm kill-window -t "$TMUX_SESSION:$s" && info "ventana tmux «$s» cerrada"
  fi
  if is_worktree "$path"; then
    info "borro el worktree $path (puede tardar si tiene dependencias o compilados)"
    git worktree remove --force "$path" || { warn "git no pudo quitarlo; lo borro a mano"; rm -rf "$path"; git worktree prune; }
  else
    if [ -e "$path" ]; then warn "$path existe pero no es worktree: no lo toco"; fi
    git worktree prune
  fi
  if has_branch "$br"; then git branch -D "$br" >/dev/null && info "rama $br borrada"; fi
  if [ -f "$MARK" ] && [ "$(cat "$MARK")" = "$id" ]; then rm -f "$MARK"; fi
  ok "$id cerrada."
  case "$ORIG_PWD" in "$path"*) warn "tu terminal estaba dentro de $path: haz «cd $ROOT»";; esac
}

case "$CMD" in
  abrir)    cmd_abrir "$@" ;;
  estado)   cmd_estado ;;
  integrar) cmd_integrar "$@" ;;
  cerrar)   cmd_cerrar "$@" ;;
  *) die "orden desconocida: $CMD (abrir · estado · integrar · cerrar · ayuda)" ;;
esac
