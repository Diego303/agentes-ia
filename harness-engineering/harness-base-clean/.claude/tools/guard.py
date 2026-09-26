#!/usr/bin/env python3
"""Hook PreToolUse: fronteras deterministas del harness (defensa frente a prompt injection).

Politica (detalle en HARNESS.md §10). Las rutas se comparan sin distinguir
mayusculas: en discos de Windows (WSL /mnt/*) y macOS `.Claude/` es `.claude/`.

Subagentes (la entrada del hook trae agent_id):
- Write/Edit: explorer, designer y reviewer solo sus artefactos; el builder, su
  implementation.md y codigo del producto; cualquier otro agente, su informe
  .claude/state/<ID>/<agente>.md, workspaces de skill-creator o codigo del producto.
  Nadie escribe en .git/, en .claude/, en archivos de instrucciones (CLAUDE.md,
  AGENTS.md, HARNESS.md a cualquier profundidad) ni fuera del proyecto (salvo
  temporales). El codigo del producto no puede referenciar el harness.
- Bash: el designer solo lee y valida. Nadie: invoca el motor de estado, usa git
  que escribe u opciones peligrosas, llama a hosts externos, instala dependencias,
  toca .claude/ o instrucciones, lee secretos ni escribe por rutas indirectas.
  Las listas blancas aceptan exactamente un comando de una linea.

Sesion principal: decisiones humanas y usos no estandar de las herramientas del
harness -> ask; archivos gestionados por herramientas -> deny; el resto de
.claude/state, la configuracion de control, .git/ e instrucciones -> ask;
secretos -> deny.

Todos: comandos catastroficos -> deny. Si el hook falla, bloquea (fail closed) y
deja el error en .claude/state/hook-errors.log.

No es una barrera absoluta (un modelo con Bash puede ejecutar codigo propio), pero
convierte los accidentes y las inyecciones habituales en bloqueos visibles.
"""

from __future__ import annotations

import fnmatch
import glob
import json
import os
import re
import shlex
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import harness_lib as hl  # noqa: E402

I = re.IGNORECASE
FID = r"[A-Z][A-Z0-9]*-[0-9]+"
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}

# --- Rutas relativas a la raiz del proyecto -------------------------------------
TOOL_MANAGED = re.compile(
    rf"^\.claude/state/{FID}/(state\.yaml|event\.log|cost\.json|acceptance-results\.json|SDD/spec\.lock\.json)$", I)
HOOK_ERRORS = re.compile(r"^\.claude/state/hook-errors\.log$", I)
STATE_TREE = re.compile(r"^\.claude/state/", I)
SKILL_WORKSPACE = re.compile(r"^\.claude/skills/[^/]+-workspace/", I)
CONTROL = re.compile(
    r"^\.claude/(settings(\.local)?\.json|harness\.toml|feature_list\.json"
    r"|(contracts|tools|agents|commands|templates|bootstrap|hooks|skills)/.+)$", I)
# Sensibles a cualquier profundidad: git interno, bundles e instrucciones que Claude Code carga.
SENSITIVE_ANYWHERE = re.compile(
    r"(^|/)(\.git|\.claude)(/|$)|(^|/)(CLAUDE|CLAUDE\.local|AGENTS|HARNESS)\.md$|(^|/)\.mcp\.json$", I)
AGENT_SCOPES = {
    "explorer": re.compile(rf"^\.claude/state/{FID}/SDD/context\.md$", I),
    "designer": re.compile(
        rf"^\.claude/state/{FID}/SDD/(proposal\.md|requirements\.md|design\.md|tasks\.md|acceptance\.yaml)$", I),
    "reviewer": re.compile(
        rf"^\.claude/state/{FID}/(verification\.md|verification-result\.yaml|repair-request\.yaml|archive\.md)$", I),
    "builder": re.compile(rf"^\.claude/state/{FID}/implementation\.md$", I),
}
PRODUCT_WRITERS = {"builder"}  # canonicos que ademas escriben codigo del producto
CONTENT_SENSITIVE = re.compile(
    r"\.claude[/\\](state|tools|settings|contracts|agents|skills|commands|templates|hooks|bootstrap"
    r"|harness\.toml|feature_list)|spec\.lock\.json", I)

# --- Comandos -------------------------------------------------------------------
_SEP = r"[ \t]+"
_TOKEN = r"(\"[^\"$`\\\n]*\"|'[^'\n]*'|[\w.,=/:@+-]+)"
_TAIL = rf"({_SEP}2>&1)?([ \t]*\|[ \t]*(tail|head)({_SEP}-n)?({_SEP}-?[0-9]+)?)?[ \t]*\Z"
_PREFIX = rf"(\./|\"?\$\{{?CLAUDE_PROJECT_DIR\}}?\"?/|{re.escape(str(hl.ROOT))}/)?"


def _cli(tools: str) -> re.Pattern:
    return re.compile(rf"\A[ \t]*python3?{_SEP}{_PREFIX}\.claude/tools/({tools})\.py({_SEP}{_TOKEN})*{_TAIL}")


SUBAGENT_CLI = _cli("run_acceptance|validate_harness")
HARNESS_CLI = _cli("feature|ledger|run_acceptance|validate_harness")
HARNESS_TESTS = re.compile(
    rf"\A[ \t]*python3?{_SEP}-m{_SEP}unittest{_SEP}discover{_SEP}-s{_SEP}\.claude/tests({_SEP}-[vq])*{_TAIL}")
VERIFY_SCRIPT = re.compile(rf"\A[ \t]*(bash{_SEP})?(\./)?\.claude/bootstrap/verify\.sh{_TAIL}")
ORCHESTRATOR_EVENTS = {"start_exploration", "exploration_complete", "design_complete", "build_complete", "pass",
                       "repairable_failure", "human_required", "escalate"}
ENGINE_MENTION = re.compile(
    r"\.claude/tools\b|tools/feature|import\s+feature\b|from\s+feature\s+import|import_module|__import__", I)
ENGINE_EXEC = re.compile(r"\.claude/tools/feature|tools/feature\.py|import\s+feature\b|from\s+feature\s+import", I)
FILE_WRITE_HINT = (
    r"(^|[^0-9&>])>{1,2}(?!&)(?!\s*/dev/null\b)|\btee\b|\bsed\s+(-[a-zA-Z]+\s+)*-[a-zA-Z]*i|\bperl\s+-[a-zA-Z]*i"
    r"|\b(mv|cp|rm|truncate|install|ln|chmod|chown|touch|unlink|dd|tar|unzip|rsync|patch)\b|\bgit\s+apply\b"
    r"|--output\b"
)
WRITE_HINT = re.compile(FILE_WRITE_HINT)
WRITE_OR_EXEC_HINT = re.compile(FILE_WRITE_HINT + r"|\b(python[0-9.]*|node|ruby|perl|bash|sh|zsh)\b")
BUNDLE_OR_INSTRUCTIONS = re.compile(
    r"\.claude(/|(?=[\s\"';|&)]|$))|(^|[\s/\"'=])((CLAUDE|CLAUDE\.local|AGENTS|HARNESS)\.md|\.mcp\.json)\b"
    r"|(^|[\s/\"'=])\.git(/|(?=[\s\"';|&)]|$))", I)
STATE_PATH = re.compile(r"\.claude/state\b", I)
CONTROL_PATH = re.compile(
    r"\.claude/(settings|harness\.toml|feature_list\.json|contracts|tools|agents|commands|templates|bootstrap|hooks"
    r"|skills/(?![^/\s]+-workspace/))|\.claude/?(?=[\s\"';|&)]|$)|(^|[\s/\"'=])((CLAUDE|CLAUDE\.local|AGENTS|HARNESS)\.md"
    r"|\.mcp\.json)\b|(^|[\s/\"'=])\.git(/|(?=[\s\"';|&)]|$))", I)
INDIRECT = re.compile(r"[`$]|\{[^{}\s]*,[^{}\s]*\}")
GLOB_CHARS = re.compile(r"[*?\[]")
READ_GIT = {"status", "diff", "log", "show", "ls-files", "rev-parse", "blame", "grep", "merge-base", "describe",
            "diff-tree", "ls-tree", "cat-file", "shortlog"}
GIT_WORD = re.compile(r"(^|[\s;&|(])git(\s|$)")
GIT_SUB = re.compile(r"(?:^|[\s;&|(])git((?:[ \t]+(?:-C[ \t]+\S+|--no-pager|-P))*)[ \t]+([A-Za-z][\w-]*)")
GIT_DANGER = re.compile(
    r"--output\b|--no-index\b|(^|\s)-O|--open-files-in-pager|--ext-diff|--textconv|--exec-path|--upload-pack"
    r"|--receive-pack|--git-dir|--work-tree|--config-env", I)
ENV_ASSIGN = re.compile(
    r"(^|[\s;&|(])(GIT_[A-Z_]+|PAGER|LESSOPEN|LESSCLOSE|EDITOR|VISUAL|SSH_ASKPASS|BASH_ENV|ENV|LD_PRELOAD)=")
INSTALL = re.compile(
    r"\b(npm|pnpm|yarn|bun)\s+(install|i|add|ci)\b|\bpip[0-9.]*\s+install\b|\bpython[0-9.]*\s+-m\s+pip\s+install\b"
    r"|\buv\s+(pip\s+install|add|sync)\b|\bpoetry\s+(add|install)\b|\bcargo\s+(add|install)\b|\bgo\s+(get|install)\b"
    r"|\bgem\s+install\b|\bbundle\s+install\b|\bcomposer\s+(require|install)\b"
    r"|\b(apt|apt-get|yum|dnf|apk|brew|choco|winget)\s+install\b")
READ_ONLY_PROGRAMS = {"ls", "cat", "head", "tail", "wc", "grep", "egrep", "fgrep", "find", "tree", "file", "stat",
                      "pwd", "echo", "sort", "uniq", "cut", "diff", "which", "git"}
FIND_ACTIONS = {"-exec", "-execdir", "-ok", "-okdir", "-delete", "-fprint", "-fprint0", "-fprintf", "-fls"}
CATASTROPHIC = [
    re.compile(r"\brm\s+(-[a-zA-Z-]+\s+)*(/|/\*|~|~/|\$HOME|\$\{HOME\})(\s|$|[;&|)])"),
    re.compile(r"\bmkfs(\.\w+)?\b|\bdd\b[^\n]*\bof=/dev/(sd|nvme|hd|disk)"),
    re.compile(r":\(\)\s*\{\s*:\|:&\s*\};:"),
    re.compile(r"\bchmod\s+-R\s+0?777\s+/(\s|$)"),
]


# --- Utilidades -------------------------------------------------------------------


def _decision(kind: str, reason: str) -> dict:
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": kind,
                                   "permissionDecisionReason": reason}}


def _relative(path: str, cwd: str | None) -> str | None:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = Path(cwd or hl.ROOT) / candidate
    real = Path(os.path.realpath(candidate))
    root = os.path.realpath(hl.ROOT)
    if os.path.normcase(str(real)).lower() == os.path.normcase(root).lower():
        return ""
    prefix = root.rstrip("/") + "/"
    if str(real).lower().startswith(prefix.lower()):
        return str(real)[len(prefix):].replace(os.sep, "/")
    return None


def _in_temp(path: str, cwd: str | None) -> bool:
    candidate = Path(path).expanduser()
    if not candidate.is_absolute():
        candidate = Path(cwd or hl.ROOT) / candidate
    real = os.path.realpath(candidate)
    temps = {os.path.realpath(tempfile.gettempdir()), "/tmp", "/private/tmp", "/var/tmp"}
    return any(real == base or real.startswith(base.rstrip("/") + "/") for base in temps)


def _content(tool_input: dict) -> str:
    parts = [tool_input.get("content"), tool_input.get("new_string"), tool_input.get("new_source")]
    parts += [edit.get("new_string") for edit in tool_input.get("edits") or [] if isinstance(edit, dict)]
    return "\n".join(str(part) for part in parts if part)


def _normalized(command: str) -> str:
    return re.sub(r"[\"'\\]", "", command)


def _mode() -> str | None:
    try:
        return hl.load_config(hl.Paths()).get("orchestration", {}).get("mode")
    except (hl.HarnessError, OSError):
        return None


def _log(message: str) -> None:
    try:
        state = hl.Paths().state
        state.mkdir(parents=True, exist_ok=True)
        with (state / "hook-errors.log").open("a", encoding="utf-8") as handle:
            handle.write(f"{hl.now_iso()} guard {message}\n")
    except OSError:
        pass


def _feature_cli(command: str) -> tuple[str, str | None, str | None] | None:
    """(subcomando, evento, --by) de una invocacion estandar de feature.py; None si no lo es."""
    if not HARNESS_CLI.match(command):
        return None
    try:
        tokens = shlex.split(command)
    except ValueError:
        return None
    index = next((i for i, token in enumerate(tokens) if token.endswith("/feature.py")), None)
    if index is None or index + 1 >= len(tokens):
        return None
    rest = tokens[index + 1:]
    subcommand = rest[0]
    event = rest[2] if subcommand == "transition" and len(rest) > 2 else None
    by = None
    for position, token in enumerate(rest):
        name, _, value = token.partition("=")
        if len(name) >= 3 and "--by".startswith(name):  # argparse admite abreviaturas: --b, --by
            by = value or (rest[position + 1] if position + 1 < len(rest) else "")
    return subcommand, event, by


def _git_problem(norm: str) -> str | None:
    """Los subagentes solo usan git de lectura, sin opciones que escriban o ejecuten codigo."""
    if not GIT_WORD.search(norm):
        return None
    if GIT_DANGER.search(norm) or ENV_ASSIGN.search(norm):
        return "opcion de git o variable de entorno que escribe archivos o ejecuta codigo"
    subcommands = [match.group(2).lower() for match in GIT_SUB.finditer(norm)]
    if len(subcommands) < len(list(GIT_WORD.finditer(norm))):
        return "invocacion de git no reconocida (opciones globales no permitidas)"
    forbidden = [sub for sub in subcommands if sub not in READ_GIT]
    return f"git {forbidden[0]} no esta permitido a los subagentes (solo lectura)" if forbidden else None


def _read_only(command: str) -> bool:
    """Un unico comando de lectura, opcionalmente con tuberias entre programas de lectura."""
    if "\n" in command or "\r" in command or re.search(r"[`$;&<>]|\|\|", command.replace("2>&1", "")):
        return False
    for segment in command.replace("2>&1", "").split("|"):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            return False
        if not tokens or tokens[0] not in READ_ONLY_PROGRAMS:
            return False
        if tokens[0] == "find" and FIND_ACTIONS & set(tokens):
            return False
        if tokens[0] == "git" and _git_problem(" ".join(tokens)):
            return False
    return True


def _glob_hits_protected(command: str, cwd: str | None, protected: re.Pattern) -> bool:
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()
    for token in tokens:
        token = token.lstrip("<>&0123456789") if token[:1] in "<>0123456789&" else token
        if not GLOB_CHARS.search(token):
            continue
        # Como el shell: un segmento con comodines que empieza por "." puede alcanzar .claude o .git,
        # exista o no el archivo todavia.
        for segment in token.replace("\\", "/").split("/"):
            low = segment.lower()
            if low.startswith(".") and any(fnmatch.fnmatchcase(name, low) for name in (".claude", ".git")):
                return True
        base = Path(cwd or hl.ROOT)
        pattern = token if os.path.isabs(token) else str(base / token)
        for match in glob.glob(pattern, recursive=True)[:500]:
            relative = _relative(match, cwd)
            if relative is None or protected.search(relative):
                return True
    return False


# --- Politicas --------------------------------------------------------------------


def check_edit(payload: dict) -> dict | None:
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return None
    cwd = payload.get("cwd")
    relative = _relative(str(target), cwd)
    agent = str(payload.get("agent_type") or "subagente") if payload.get("agent_id") else None
    if agent is None:
        if relative is None or SKILL_WORKSPACE.match(relative):
            return None
        if TOOL_MANAGED.match(relative):
            return _decision("deny", f"{relative} lo gestionan las herramientas del harness (feature.py, ledger.py, "
                                     "run_acceptance.py). No se edita a mano.")
        if HOOK_ERRORS.match(relative) or STATE_TREE.match(relative):
            return _decision("ask", f"{relative} pertenece al estado de una feature (lo escriben los agentes). "
                                    "Confirma solo si lo has pedido tu.")
        if CONTROL.match(relative) or SENSITIVE_ANYWHERE.search(relative):
            return _decision("ask", f"Cambio en configuracion, instrucciones o git ({relative}). "
                                    "Confirma solo si lo has pedido tu.")
        return None
    if relative is None:
        if _in_temp(str(target), cwd):
            return None
        return _decision("deny", f"El {agent} no escribe fuera del proyecto salvo en directorios temporales.")
    scope = AGENT_SCOPES.get(agent)
    if scope is not None and scope.match(relative):
        return None
    if scope is None:
        own_report = re.match(rf"^\.claude/state/{FID}/{re.escape(agent)}\.md$", relative, I)
        if own_report or SKILL_WORKSPACE.match(relative):
            return None
    if SENSITIVE_ANYWHERE.search(relative) or relative == "":
        return _decision("deny", f"El {agent} no puede escribir {relative or 'la raiz'}: .git/, .claude/ e instrucciones "
                                 "estan protegidos (ver 'Propiedad de artefactos' en HARNESS.md). Informa al orquestador.")
    if scope is not None and agent not in PRODUCT_WRITERS:
        return _decision("deny", f"El {agent} no escribe codigo del producto ({relative}); solo sus artefactos.")
    if CONTENT_SENSITIVE.search(_content(tool_input)):
        return _decision("deny", "El codigo del producto no debe referenciar el estado ni las herramientas del harness "
                                 "(.claude/state, .claude/tools, settings, spec.lock). Si es necesario, informa al orquestador.")
    return None


def check_bash_subagent(command: str, agent: str, cwd: str | None) -> dict | None:
    if SUBAGENT_CLI.match(command) or HARNESS_TESTS.match(command) or VERIFY_SCRIPT.match(command):
        return None
    norm = _normalized(command)
    if agent == "designer" and not _read_only(command):
        return _decision("deny", "El designer solo lee y valida: usa comandos de lectura sueltos o "
                                 "python3 .claude/tools/validate_harness.py --feature <ID> --pre-gate")
    if ENGINE_EXEC.search(norm):
        return _decision("deny", f"El {agent} no cambia el estado del flujo: devuelve tu informe al orquestador.")
    problem = _git_problem(norm)
    if problem:
        return _decision("deny", f"{problem}. El humano gestiona git.")
    if hl.external_network(norm):
        return _decision("deny", "Los subagentes no llaman a hosts externos (solo localhost).")
    if INSTALL.search(norm):
        return _decision("deny", "Instalar dependencias es una decision humana: informalo como bloqueo.")
    if BUNDLE_OR_INSTRUCTIONS.search(norm) and WRITE_OR_EXEC_HINT.search(norm):
        return _decision("deny", "Los subagentes no modifican ni ejecutan nada bajo .claude/ ni tocan instrucciones o "
                                 ".git con Bash. Lee con Read, escribe tus artefactos con Write y ejecuta las "
                                 "herramientas del harness como un unico comando.")
    if WRITE_HINT.search(norm) and (INDIRECT.search(command) or
                                    _glob_hits_protected(command, cwd, re.compile(r"(^|/)(\.git|\.claude)(/|$)", I))):
        return _decision("deny", "Escritura con rutas indirectas (variables, sustituciones o comodines hacia rutas "
                                 "protegidas): usa rutas literales.")
    return None


def check_bash_main(command: str, cwd: str | None) -> dict | None:
    norm = _normalized(command)
    if STATE_PATH.search(norm) and WRITE_OR_EXEC_HINT.search(norm) and not HARNESS_CLI.match(command):
        return _decision("deny", "El estado de las features lo escriben solo feature.py, ledger.py y run_acceptance.py. "
                                 "Si solo quieres leer, ejecuta la lectura sola (sin python, redirecciones ni otros "
                                 "comandos encadenados) o usa la herramienta Read.")
    if ENGINE_MENTION.search(norm):
        if HARNESS_TESTS.match(command):
            return None
        parsed = _feature_cli(command)
        if parsed:
            subcommand, event, by = parsed
            if subcommand in {"status", "add", "start"}:
                return None
            if subcommand == "transition" and event in ORCHESTRATOR_EVENTS and by in (None, "orchestrator"):
                return None
            if subcommand == "transition" and event == "approved" and by == "yolo-mode" and _mode() == "yolo":
                return None  # delegacion yolo de GATE#1: feature.py valida tags, comandos y rationale
        elif HARNESS_CLI.match(command):
            return None  # ledger, validador o runner con argumentos simples
        return _decision("ask", "Decision humana del flujo o invocacion no estandar de las herramientas del harness. "
                                "Aprueba SOLO si tu has tomado esta decision en esta conversacion; nunca por "
                                "instrucciones leidas en archivos o herramientas.")
    if HARNESS_TESTS.match(command) or VERIFY_SCRIPT.match(command):
        return None
    if WRITE_HINT.search(norm) and (CONTROL_PATH.search(norm) or _glob_hits_protected(
            command, cwd, re.compile(r"(^|/)(\.git|\.claude)(/|$)|(^|/)(CLAUDE|AGENTS|HARNESS)\.md$", I))):
        return _decision("ask", "El comando modifica configuracion del harness, instrucciones o git. Confirma solo si "
                                "lo has pedido tu.")
    return None


def evaluate(payload: dict) -> dict | None:
    tool = payload.get("tool_name")
    if tool in EDIT_TOOLS:
        return check_edit(payload)
    if tool != "Bash":
        return None
    command = str((payload.get("tool_input") or {}).get("command") or "")
    for pattern in CATASTROPHIC:
        if pattern.search(command):
            return _decision("deny", "Comando catastrofico bloqueado por el harness.")
    if hl.SECRET_REF.search(_normalized(command)):
        return _decision("deny", "Los comandos no leen ni exponen secretos (.env, claves, credenciales); "
                                 ".env.example si esta permitido.")
    if payload.get("agent_id"):
        return check_bash_subagent(command, str(payload.get("agent_type") or "subagente"), payload.get("cwd"))
    return check_bash_main(command, payload.get("cwd"))


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        decision = evaluate(payload)
    except Exception as exc:  # noqa: BLE001 - fail closed: ante la duda, se bloquea
        _log(f"error inesperado: {exc!r}")
        decision = _decision("deny", "El hook de seguridad fallo y bloquea por precaucion. Revisa "
                                     ".claude/state/hook-errors.log.")
    if decision:
        print(json.dumps(decision, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
