#!/usr/bin/env python3
"""Hook PreToolUse: fronteras deterministas del harness (defensa frente a prompt injection).

Politica (detalle en HARNESS.md §10). Las rutas se comparan sin distinguir
mayusculas: en discos de Windows (WSL /mnt/*) y macOS `.Claude/` es `.claude/`.

Subagentes (la entrada del hook trae agent_id):
- Write/Edit: explorer, designer y reviewer solo sus artefactos; el builder, su
  implementation.md y codigo del producto; un especialista registrado, su informe
  .claude/state/<ID>/<agente>.md y las rutas de su `product_writes` en
  agent-registry.yaml; un subagente no registrado, su informe o workspaces de
  skill-creator (nunca codigo del producto). Nadie escribe en .git/, en .claude/,
  en archivos de instrucciones (CLAUDE.md, AGENTS.md, HARNESS.md a cualquier
  profundidad) ni fuera del proyecto (salvo temporales). El codigo del producto
  no puede referenciar el harness.
- Bash: solo el builder escribe archivos; el resto es de solo lectura (sin
  redirecciones fuera de los temporales, edicion en el sitio, codigo en linea,
  formateadores que reescriben ni programas de escritura) y el designer, ademas,
  solo lee y valida. Nadie: invoca el motor de estado, usa git que escribe u
  opciones peligrosas, llama a hosts externos, instala dependencias, toca
  .claude/ o instrucciones, lee secretos (tampoco con comodines, sustituciones,
  xargs o busquedas recursivas amplias) ni escribe por rutas indirectas.
  Las listas blancas aceptan exactamente un comando de una linea.

Sesion principal: decisiones humanas y usos no estandar de las herramientas del
harness -> ask; archivos gestionados por herramientas -> deny; el resto de
.claude/state, la configuracion de control, .git/ e instrucciones -> ask;
secretos -> deny (lecturas indirectas de secretos -> ask).

Read/Grep/Glob (todos): archivos de secretos y claves -> deny.

Los comandos se analizan con un lexico que respeta comillas y heredocs: un texto
buscado (`grep "-> None"`, `rg "git"`) no es una redireccion ni una invocacion.

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
FID = hl.FEATURE_ID_PATTERN
EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
READ_TOOLS = {"Read", "Grep", "Glob"}

# --- Rutas relativas a la raiz del proyecto -------------------------------------
TOOL_MANAGED = re.compile(
    rf"^\.claude/state/{FID}/(state\.yaml|event\.log|cost\.json|acceptance-results\.json|SDD/spec\.lock\.json)$", I)
HOOK_ERRORS = re.compile(r"^\.claude/state/hook-errors\.log$", I)
STATE_TREE = re.compile(r"^\.claude/state/", I)
SKILL_WORKSPACE = re.compile(r"^\.claude/skills/[^/]+-workspace/", I)
HANDOFF = re.compile(r"^\.claude/handoff/[^/]+\.md$", I)
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
BASH_WRITERS = {"builder"}  # el resto de subagentes es de solo lectura tambien por Bash
# Secretos y claves: nadie los lee ni los escribe desde Claude Code (.env.example y similares, si).
# El directorio secrets/ solo cuenta en la raiz (un modulo src/secrets/ es codigo normal).
SECRET_FILE = re.compile(
    r"(^|/)(\.env(\.(?!example$|sample$|template$|dist$)[\w.-]+)?|\.envrc|[^/]+\.(pem|key|p12|pfx|jks|keystore)"
    r"|id_(rsa|dsa|ecdsa|ed25519)[^/]*|\.pgpass|\.netrc|\.pypirc|\.npmrc)$|^\.?secrets(/|$)", I)
# Credenciales del usuario, relativas a su home.
HOME_SECRET_DIRS = re.compile(r"^\.(ssh|aws|gnupg|kube|docker|azure|config/gcloud)(/|$)", I)
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
READ_SUBCOMMANDS = {"status", "add", "start", "specialists", "metrics"}  # feature.py sin decision humana
ORCHESTRATOR_EVENTS = {"start_exploration", "exploration_complete", "design_complete", "build_complete", "pass",
                       "repairable_failure", "human_required", "escalate"}
ENGINE_MENTION = re.compile(
    r"\.claude/tools\b|tools/feature|import\s+feature\b|from\s+feature\s+import|import_module|__import__", I)
ENGINE_EXEC = re.compile(r"\.claude/tools/feature|tools/feature\.py|import\s+feature\b|from\s+feature\s+import", I)
# Olas (scripts/ola.sh, perfil olas): las coordina la sesion del arbol principal; commits y push son del humano.
WAVES_SCRIPT = re.compile(r"(^|[\s/;&|(=])ola\.sh\b", I)
WAVES_SELF_CONFIRM = re.compile(r"(^|\s)--si(?=\s|$)|\bCLAUDECODE\b", I)
FILE_WRITE_HINT = (
    r"(^|[^0-9&>])>{1,2}(?!&)(?!\s*/dev/null\b)|\btee\b|\bsed\s+(-[a-zA-Z]+\s+)*-[a-zA-Z]*i|\bperl\s+-[a-zA-Z]*i"
    r"|\b(mv|cp|rm|truncate|install|ln|chmod|chown|touch|unlink|dd|tar|unzip|rsync|patch)\b|\bgit\s+apply\b"
    r"|--output\b|\s-(delete|fprint0?|fprintf|fls)\b|\bsort\b[^|;&\n]*\s-o\b"
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
    r"\b(npm|pnpm|yarn|bun)((\s+(-[A-Za-z]|--dir|--filter|-C))(\s+[^\s-]\S*)?)*\s+"
    r"(install|i|add|ci|update|up|upgrade|remove|rm|uninstall|un|dlx|link|unlink|fetch|import)\b"
    r"|\b(npx|pnpx|bunx|corepack)\b|\bcargo\s+(update|fetch|remove|binstall)\b"
    r"|\brustup\s+(toolchain\s+install|install|update|target\s+add|component\s+add)\b"
    r"|\bpip[0-9.]*\s+install\b|\bpython[0-9.]*\s+-m\s+pip\s+install\b"
    r"|\buv\s+(pip\s+install|add|sync)\b|\bpoetry\s+(add|install)\b|\bcargo\s+(add|install)\b|\bgo\s+(get|install)\b"
    r"|\bgem\s+install\b|\bbundle\s+install\b|\bcomposer\s+(require|install)\b"
    r"|\b(apt|apt-get|yum|dnf|apk|brew|choco|winget)\s+install\b")
READ_ONLY_PROGRAMS = {"ls", "cat", "head", "tail", "wc", "grep", "egrep", "fgrep", "rg", "find", "tree", "file",
                      "stat", "pwd", "echo", "sort", "uniq", "cut", "diff", "which", "git"}
# git en posicion de comando (no dentro de un texto buscado como rg "git").
GIT_CMD_POS = re.compile(r"(^|[;&|(`]\s*|\b(xargs|exec|env|command|nice|nohup|time|timeout\s+\S+|-exec|-execdir)"
                         r"(\s+-\S+)*\s+)[\"']?git[\"']?(\s|$)")
GIT_TAG_LIST = re.compile(r"\bgit\s+tag\s+(--sort=\S+\s+)?(-l|--list|--contains|--points-at|-n[0-9]*)\b")
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
    if GIT_TAG_LIST.search(norm) and not GIT_DANGER.search(norm) and not ENV_ASSIGN.search(norm):
        return None  # git tag --list y similares solo leen
    if GIT_DANGER.search(norm) or ENV_ASSIGN.search(norm):
        return "opcion de git o variable de entorno que escribe archivos o ejecuta codigo"
    subcommands = [match.group(2).lower() for match in GIT_SUB.finditer(norm)]
    if len(subcommands) < len(list(GIT_WORD.finditer(norm))):
        return "invocacion de git no reconocida (opciones globales no permitidas)"
    forbidden = [sub for sub in subcommands if sub not in READ_GIT]
    return f"git {forbidden[0]} no esta permitido a los subagentes (solo lectura)" if forbidden else None


def _read_only(command: str) -> bool:
    """Un unico comando de lectura, opcionalmente con tuberias entre programas de lectura.

    Los literales entre comillas simples son texto (patrones de busqueda): no cuentan como metacaracteres.
    """
    single_unquoted = re.sub(r"'[^']*'", " ", command.replace("2>&1", ""))
    if "\n" in command or "\r" in command or re.search(r"[`$;&<>]|\|\|", single_unquoted):
        return False
    try:
        lexer = shlex.shlex(command.replace("2>&1", ""), posix=True, punctuation_chars="|")
        lexer.whitespace_split = True
        all_tokens = list(lexer)
    except ValueError:
        return False
    segments, current = [], []
    for token in all_tokens:
        if token == "|":
            segments.append(current)
            current = []
        else:
            current.append(token)
    segments.append(current)
    for tokens in segments:
        if not tokens or tokens[0] not in READ_ONLY_PROGRAMS:
            return False
        if tokens[0] == "find" and FIND_ACTIONS & set(tokens):
            return False
        if tokens[0] == "rg" and any(token.startswith("--pre") for token in tokens):
            return False
        if tokens[0] == "git" and _git_problem(" ".join(tokens)):
            return False
    return True


# --- Analisis lexico de comandos ------------------------------------------------
# Respeta comillas y heredocs: `grep "-> None"` no es una redireccion y el cuerpo de un heredoc es texto.
SEPARATORS = {"|", "||", "&&", ";", "&", "\n", "$(", ")", "`", "("}
REDIRECTS = {">", ">>", "&>", "&>>", ">|"}
INTERPRETERS = re.compile(r"^(python[0-9.]*|node|deno|bun|ruby|perl|php|bash|sh|zsh|dash|ksh|fish|pwsh)$")
SHELLS = re.compile(r"^(bash|sh|zsh|dash|ksh|fish)$")
# Opciones del propio interprete que ejecutan codigo pasado como texto (antes del script o de -m).
INLINE_FLAGS = {"python": re.compile(r"-[a-zA-Z]*c"), "node": re.compile(r"-e|-p|--eval|--print|-pe"),
                "deno": re.compile(r"eval"), "bun": re.compile(r"-e|--eval"), "ruby": re.compile(r"-[a-zA-Z]*e"),
                "perl": re.compile(r"-[a-zA-Z]*[eE]"), "php": re.compile(r"-r"),
                "pwsh": re.compile(r"-c|-Command|-EncodedCommand", I)}
INFO_FLAGS = {"--version", "-V", "--help", "-h", "-v"}
WRITE_PROGRAMS = {"tee", "mv", "cp", "rm", "rmdir", "touch", "truncate", "install", "ln", "chmod", "chown", "dd",
                  "tar", "unzip", "zip", "rsync", "patch", "mkdir", "shred", "split", "csplit", "unlink"}
TEMP_PREFIXES = ("/tmp/", "/var/tmp/", "$TMPDIR", "${TMPDIR", "/dev/null")
# Opciones de herramientas de pruebas que escriben informes: solo en temporales para los de solo lectura.
REPORT_OPTIONS = ("--basetemp", "--junitxml", "--junit-xml", "--result-log", "--log-file", "--html", "--report-log",
                  "--json-report-file", "--outputFile", "--coverage-directory")
REWRITE_FLAGS = {"--fix", "--write", "--apply", "--fix-only", "--unsafe-fixes"}
SENSITIVE_NAMES = (".env", ".env.local", ".env.production", ".envrc", "secrets", "secret", ".pgpass", ".netrc",
                   ".pypirc", ".npmrc", ".ssh", ".aws", ".gnupg", "id_rsa", "id_ed25519", "x.key", "x.pem", "x.p12")
SENSITIVE_WORD = re.compile(
    r"^(\./)?\.?secrets(/|$)|(^|[/:=@])\.env(rc)?(\.(?!example\b|sample\b|template\b|dist\b)[\w.-]+)?$"
    r"|(^|[/:=@])(\.pgpass|\.netrc|\.pypirc|\.npmrc|id_(rsa|dsa|ecdsa|ed25519)\w*)$"
    r"|\.(pem|key|p12|pfx)$|(^|[/:=@~])\.(ssh|aws|gnupg|kube)(/|$)|/proc/[\w/]*environ", I)
SENSITIVE_HINT = re.compile(r"\benv\b|\.env|secret|\.ssh|\.aws|\bkey\b|token|passw", I)
READERS = {"cat", "head", "tail", "less", "more", "strings", "xxd", "od", "base64", "cp", "tar", "zip", "nl", "awk",
           "sed", "grep", "rg"}


def lex(command: str) -> list[tuple[str, str, bool]]:
    """Tokens (tipo, texto, entrecomillado) de un comando de shell. tipo: word | op."""
    tokens: list[tuple[str, str, bool]] = []
    buf, quoted, i, n = "", False, 0, len(command)

    def flush() -> None:
        nonlocal buf, quoted
        if buf or quoted:
            tokens.append(("word", buf, quoted))
        buf, quoted = "", False

    while i < n:
        c = command[i]
        if c in "'\"":
            j = i + 1
            while j < n and command[j] != c:
                if c == '"' and command[j] == "\\" and j + 1 < n:
                    buf += command[j + 1]
                    j += 2
                    continue
                buf += command[j]
                j += 1
            quoted, i = True, j + 1
            continue
        if c == "\\" and i + 1 < n:
            buf, i = buf + command[i + 1], i + 2
            continue
        if c in " \t":
            flush()
            i += 1
            continue
        op = next((o for o in ("&>>", "<<<", "$(", "&&", "||", ">>", ">&", ">|", "&>", "<<") if command.startswith(o, i)),
                  None) or (c if c in "|;&\n()`<>" else None)
        if op:
            if op in {">", ">>", ">&", ">|"} and buf.isdigit() and not quoted:
                buf = ""  # descriptor: 2> o 2>>
            flush()
            tokens.append(("op", op, False))
            i += len(op)
            if op == "<<":
                # heredoc: el cuerpo es texto (p. ej. un mensaje), no comandos ni rutas
                match = re.match(r"-?\s*(['\"]?)([\w.-]+)\1", command[i:])
                if match:
                    delimiter = match.group(2)
                    tokens.append(("word", delimiter, True))
                    end_of_line = command.find("\n", i)
                    if end_of_line == -1:
                        i = n
                        continue
                    body = re.search(rf"^[ \t]*{re.escape(delimiter)}[ \t]*$", command[end_of_line + 1:], re.M)
                    tokens.extend(lex(command[i + match.end():end_of_line]))  # resto de la linea: `<<EOF > f`
                    tokens.append(("op", "\n", False))
                    i = n if body is None else end_of_line + 1 + body.end()
            continue
        buf += c
        i += 1
    flush()
    return tokens


def lex_segments(command: str) -> list[dict]:
    """Comandos simples: palabras (texto, entrecomillado) y destinos de redireccion de entrada y salida."""
    segments: list[dict] = []
    current: dict = {"words": [], "redirects": [], "inputs": [], "heredoc": False}
    pending = None
    for kind, text, quoted in lex(command):
        if kind == "op" and text in SEPARATORS:
            segments.append(current)
            current, pending = {"words": [], "redirects": [], "inputs": [], "heredoc": False}, None
            continue
        if kind == "op":
            pending = text
            if text in {"<<", "<<<"}:
                current["heredoc"] = True
            continue
        if pending in REDIRECTS or (pending == ">&" and not text.isdigit() and text != "-"):
            current["redirects"].append(text)
        elif pending == "<":
            current["inputs"].append(text)
        elif pending not in {"<<", "<<<", ">&"}:
            current["words"].append((text, quoted))
        pending = None
    segments.append(current)
    return [s for s in segments if s["words"] or s["redirects"] or s["inputs"]]


def _program(words: list[tuple[str, bool]]) -> tuple[str, list[str]]:
    """(programa, argumentos) saltando asignaciones VAR=valor y envoltorios (env, nohup, timeout...)."""
    texts = [w for w, _ in words]
    with_value = {"env": {"-u", "--unset", "-C", "--chdir", "-S", "--split-string"}, "nice": {"-n", "--adjustment"},
                  "timeout": {"-s", "--signal", "-k", "--kill-after"}, "stdbuf": {"-i", "-o", "-e"},
                  "ionice": {"-c", "-n", "-p"}, "time": {"-f", "-o"}, "command": set(), "nohup": set(), "exec": {"-a"},
                  "setsid": set(), "chrt": set(), "taskset": set()}
    index = 0
    while index < len(texts):
        token = texts[index]
        if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", token):
            index += 1
            continue
        wrapper = token.rsplit("/", 1)[-1]
        if wrapper not in with_value:
            break
        index += 1
        while index < len(texts) and (texts[index].startswith("-") or re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", texts[index])):
            option = texts[index]
            index += 2 if option in with_value[wrapper] else 1
            if option == "--":
                break
        if wrapper == "timeout" and index < len(texts) and re.fullmatch(r"[0-9.]+[smhd]?", texts[index]):
            index += 1  # duracion
    if index >= len(texts):
        return "", []
    return texts[index].rsplit("/", 1)[-1], texts[index + 1:]


def _option_value(args: list[str], *names: str) -> str | None:
    for i, arg in enumerate(args):
        if arg in names and i + 1 < len(args):
            return args[i + 1]
        for name in names:
            if name.startswith("--") and arg.startswith(name + "="):
                return arg.split("=", 1)[1]
            if not name.startswith("--") and arg.startswith(name) and len(arg) > len(name):
                return arg[len(name):]
    return None


def _temp_path(token: str) -> bool:
    return token.startswith(TEMP_PREFIXES)


def _inline_code(program: str, args: list[str], seg: dict) -> bool:
    """Codigo en linea para un interprete: -c/-e antes del script, heredoc o stdin ("-" o sin script)."""
    if not INTERPRETERS.match(program):
        return False
    if seg["heredoc"]:
        return True
    family = "python" if program.startswith("python") else program
    inline = re.compile(r"-[a-zA-Z]*c") if SHELLS.match(program) else INLINE_FLAGS.get(family)
    options = []
    for arg in args:
        if (arg == "-m" and family == "python") or not arg.startswith("-") or arg == "-":
            break
        options.append(arg)
    if inline is not None and any(inline.fullmatch(arg) for arg in options):
        return True
    rest = args[len(options):]
    if rest[:1] == ["-"]:
        return True
    return not rest and not (INFO_FLAGS & set(options))  # sin script ni modulo: ejecuta lo que llegue por stdin


def _nested_programs(program: str, args: list[str]) -> list[str]:
    """Programas que lanzan xargs o find -exec (escrituras escondidas tras otro comando)."""
    if program == "xargs":
        return [a.rsplit("/", 1)[-1] for a in args if not a.startswith("-")][:1]
    if program == "find":
        return [args[i + 1].rsplit("/", 1)[-1] for i, a in enumerate(args[:-1]) if a in FIND_ACTIONS]
    return []


def writes_by_bash(command: str) -> bool:
    """El comando escribe archivos: redireccion fuera de temporales, programas de escritura, edicion en el sitio..."""
    for seg in lex_segments(command):
        if any(not _temp_path(t) for t in seg["redirects"]):
            return True
        program, args = _program(seg["words"])
        for name in [program] + _nested_programs(program, args):
            if name in WRITE_PROGRAMS or INTERPRETERS.match(name) and name != program:
                return True
        if program == "sort" and _option_value(args, "-o", "--output"):
            return True
        if program in {"sed", "perl"} and any(re.fullmatch(r"-[a-zA-Z]*i\S*|--in-place\S*", a) for a in args):
            return True
        if program in {"awk", "gawk", "mawk"} and any(">" in a or "system(" in a for a in args):
            return True
        if _inline_code(program, args, seg):
            return True
        if (program == "git" and args[:1] == ["apply"]) or any(a.startswith("--output") for a in args):
            return True
    return False


def _bare(command: str) -> str:
    """El comando con los literales entrecomillados (y cuerpos de heredoc) sustituidos por un marcador."""
    return " ".join(text if kind == "op" or not quoted else "_" for kind, text, quoted in lex(command))


def _write_hint(command: str) -> bool:
    return bool(WRITE_HINT.search(_bare(command))) or writes_by_bash(command)


def _write_or_exec_hint(command: str) -> bool:
    return bool(WRITE_OR_EXEC_HINT.search(_bare(command))) or writes_by_bash(command)


def readonly_write_problem(command: str) -> str | None:
    """Motivo por el que un subagente de solo lectura no puede ejecutar este comando, o None."""
    for seg in lex_segments(command):
        bad = [t for t in seg["redirects"] if not _temp_path(t)]
        if bad:
            return f"redireccion a {bad[0]}"
        program, args = _program(seg["words"])
        if not program:
            continue
        if program in {"eval", "source", "."}:
            return f"{program} (ejecucion indirecta)"
        if _inline_code(program, args, seg):
            return "codigo en linea (-c/-e/heredoc a un interprete)"
        for nested in _nested_programs(program, args):
            if nested in WRITE_PROGRAMS or INTERPRETERS.match(nested) or nested in {"sed", "perl", "awk"}:
                return f"{program} que lanza {nested}"
        if program in {"sed", "perl"} and any(re.fullmatch(r"-[a-zA-Z]*i\S*|--in-place\S*", a) for a in args):
            return "edicion en el sitio"
        if program in {"awk", "gawk", "mawk"} and any(">" in a or "system(" in a for a in args):
            return "awk que escribe o ejecuta"
        if (program == "git" and args[:1] == ["apply"]) or any(a.startswith("--output") for a in args):
            return "edicion en el sitio"
        for option in REPORT_OPTIONS:
            value = _option_value(args, option)
            if value is not None and not _temp_path(value):
                return f"{option} escribe en {value} (usa /tmp)"
        if REWRITE_FLAGS & set(args) or (program in {"black", "isort"} and "--check" not in args) \
                or (program == "ruff" and "format" in args and "--check" not in args) \
                or (program == "cargo" and args[:1] == ["fmt"] and "--check" not in args) \
                or (program == "gofmt" and "-w" in args):
            return "formateador o --fix/--write (reescribe archivos)"
        positional = [a for a in args if not a.startswith("-")]
        if program in {"cp", "mv", "install", "ln", "rsync"}:
            target = _option_value(args, "-t", "--target-directory")
            targets = [target] if target else positional[-1:]
        elif program == "sort":
            target = _option_value(args, "-o", "--output")
            targets = [target] if target else []
        elif program == "unzip":
            targets = [_option_value(args, "-d") or "."]
        elif program in WRITE_PROGRAMS:
            targets = positional or ["."]
        else:
            targets = []
        if targets and not all(_temp_path(t) for t in targets):
            return f"{program} fuera de los temporales"
    return None


def _sensitive_glob(word: str) -> bool:
    """Un comodin que puede alcanzar un secreto. Como el shell, `*` no casa con archivos ocultos y un
    componente formado solo por comodines (`src/*`) no se considera dirigido a un secreto."""
    if not any(ch in word for ch in "*?["):
        return False
    for component in word.strip("/").split("/"):
        if not any(ch in component for ch in "*?[") or not re.sub(r"[*?\[\]]", "", component):
            continue
        for name in SENSITIVE_NAMES:
            if name.startswith(".") and not component.startswith("."):
                continue
            if fnmatch.fnmatchcase(name.lower(), component.lower()):
                return True
    return False


def private_data_problem(command: str, subagent: bool) -> str | None:
    """Lectura indirecta de secretos por Bash: comodines, sustituciones, xargs y busquedas recursivas amplias."""
    lexed = lex(command)
    visible = " ".join(text for _, text, _ in lexed)
    if any(kind == "op" and text in {"$(", "`"} for kind, text, _ in lexed) and SENSITIVE_HINT.search(visible):
        return "sustitucion de comandos que menciona secretos o el entorno"
    for seg in lex_segments(command):
        program, args = _program(seg["words"])
        words = list(args)
        if program in {"grep", "egrep", "fgrep", "rg", "ag", "ack"}:
            explicit = _option_value(args, "-e", "--regexp")
            quoted_args = seg["words"][len(seg["words"]) - len(args):]
            positional = [a for a, q in quoted_args if q or not a.startswith("-")]
            if explicit is None and positional:
                words.remove(positional[0])  # el patron es texto, no una ruta
            paths = positional[(0 if explicit is not None else 1):]
            recursive = program in {"rg", "ag", "ack"} or any(
                a in {"--recursive", "--dereference-recursive"} or re.fullmatch(r"-[a-zA-Z]*[rR][a-zA-Z]*", a) for a in args)
            hidden = program in {"rg", "ag"} and any(a in {"--hidden", "-u", "-uu", "-uuu", "--no-ignore"} for a in args)
            excluded = any(re.match(r"--exclude(-dir)?=['\"]?\.?env", a) for a in args)
            broad = not paths or any(p.rstrip("/") in {".", "..", "*", "~", "$HOME", ""} for p in paths)
            if subagent and recursive and broad and (program not in {"rg", "ag"} or hidden) and not excluded:
                return "busqueda recursiva amplia que leeria .env o secrets/ (limita las rutas o usa la herramienta Grep)"
        if program == "xargs" and (SENSITIVE_HINT.search(command) or any(a.rsplit("/", 1)[-1] in READERS for a in args)):
            return "xargs que lee o copia una lista de archivos que la guardia no puede ver"
        for word in [program] + words + seg["redirects"] + seg["inputs"]:
            if re.match(r"--(exclude|include|exclude-dir|include-dir|glob)=", word):
                continue  # nombrar secrets/ para excluirlo de una busqueda no es leerlo
            if SENSITIVE_WORD.search(word) or _sensitive_glob(word):
                return f"{word} (secretos o claves)"
    return None


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


def _registry_entry(agent: str) -> dict | None:
    """Entrada del agente en agent-registry.yaml. Un registro ilegible propaga la excepcion: main() bloquea."""
    registry = hl.load_yaml(hl.Paths().registry) or {}
    for entry in registry.get("agents") or []:
        if isinstance(entry, dict) and str(entry.get("name", "")).lower() == agent.lower():
            return entry
    return None


def _product_writes(agent: str) -> list[str]:
    """Patrones fnmatch de `product_writes` de un especialista (ninguno por defecto ni para no registrados)."""
    entry = _registry_entry(agent)
    if not entry or entry.get("role") != "specialist":
        return []
    return [str(item) for item in entry.get("product_writes") or [] if isinstance(item, str) and item.strip()]


def _matches_any(relative: str, patterns: list[str]) -> bool:
    low = relative.lower()
    return any(fnmatch.fnmatchcase(low, pattern.lower()) for pattern in patterns)


def _secret_target(path: str, cwd: str | None) -> bool:
    """La ruta (o el patron) apunta a secretos: del proyecto o del home (~/.ssh, ~/.aws...)."""
    text = path.replace("\\", "/")
    candidates = {text, text[2:] if text.startswith("./") else text}
    if GLOB_CHARS.search(text):
        if _sensitive_glob(text):
            return True
    else:
        relative = _relative(text, cwd)
        if relative is not None:
            candidates.add(relative)
    expanded = os.path.expanduser(text).replace("\\", "/")
    home = str(hl.HOME).replace("\\", "/").rstrip("/") + "/"
    if expanded.lower().startswith(home.lower()):
        candidates.add(expanded[len(home):])
    return any(SECRET_FILE.search(candidate) or HOME_SECRET_DIRS.match(candidate) for candidate in candidates)


def check_read(payload: dict) -> dict | None:
    """Read/Grep/Glob: secretos y claves no se leen (defensa en profundidad sobre los deny de settings.json)."""
    tool_input = payload.get("tool_input") or {}
    keys = ("path", "glob") if payload.get("tool_name") == "Grep" else ("file_path", "path", "pattern")
    for key in keys:
        value = tool_input.get(key)
        if value and _secret_target(str(value), payload.get("cwd")):
            return _decision("deny", f"{value}: los secretos y las claves (.env, *.pem, ~/.ssh...) no se leen desde "
                                     "Claude Code. Usa .env.example o pide el dato al humano.")
    return None


def check_edit(payload: dict) -> dict | None:
    tool_input = payload.get("tool_input") or {}
    target = tool_input.get("file_path") or tool_input.get("notebook_path")
    if not target:
        return None
    cwd = payload.get("cwd")
    relative = _relative(str(target), cwd)
    agent = str(payload.get("agent_type") or "subagente") if payload.get("agent_id") else None
    if _secret_target(str(target), cwd):
        return _decision("deny", f"{target} es un archivo de secretos o claves: lo escribe el humano fuera de Claude "
                                 "Code. Usa un .env.example sin valores reales.")
    if agent is None:
        if relative is None or SKILL_WORKSPACE.match(relative) or HANDOFF.match(relative):
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
    if scope is None and not _matches_any(relative, _product_writes(agent)):
        return _decision("deny", f"El {agent} solo escribe su informe .claude/state/<ID>/{agent}.md: {relative} no "
                                 "esta en su product_writes de agent-registry.yaml. Describe el cambio en tu informe.")
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
    if WAVES_SCRIPT.search(norm):
        return _decision("deny", f"El {agent} no abre, integra ni cierra olas: eso lo coordina la sesion del arbol "
                                 "principal con el humano.")
    git_invoked = GIT_WORD.search(_bare(command)) or GIT_CMD_POS.search(command)
    problem = _git_problem(norm) if git_invoked else None
    if problem:
        return _decision("deny", f"{problem}. El humano gestiona git.")
    if hl.external_network(norm):
        return _decision("deny", "Los subagentes no llaman a hosts externos (solo localhost).")
    if INSTALL.search(norm):
        return _decision("deny", "Instalar o cambiar dependencias es una decision humana: informalo como bloqueo.")
    private = private_data_problem(command, subagent=True)
    if private:
        return _decision("deny", f"Datos privados: {private}. Los subagentes no leen ni copian secretos ni claves.")
    if agent not in BASH_WRITERS:
        problem = readonly_write_problem(command)
        if problem:
            return _decision("deny", f"El {agent} es de solo lectura por Bash ({problem}): escribe solo tus artefactos "
                                     "con Write; los temporales van en /tmp.")
    if BUNDLE_OR_INSTRUCTIONS.search(norm) and _write_or_exec_hint(command):
        return _decision("deny", "Los subagentes no modifican ni ejecutan nada bajo .claude/ ni tocan instrucciones o "
                                 ".git con Bash. Lee con Read, escribe tus artefactos con Write y ejecuta las "
                                 "herramientas del harness como un unico comando.")
    if _write_hint(command) and (INDIRECT.search(command) or
                                 _glob_hits_protected(command, cwd, re.compile(r"(^|/)(\.git|\.claude)(/|$)", I))):
        return _decision("deny", "Escritura con rutas indirectas (variables, sustituciones o comodines hacia rutas "
                                 "protegidas): usa rutas literales.")
    return None


def check_bash_main(command: str, cwd: str | None) -> dict | None:
    norm = _normalized(command)
    if WAVES_SCRIPT.search(norm) and WAVES_SELF_CONFIRM.search(norm):
        return _decision("deny", "ola.sh con --si o tocando CLAUDECODE: los commits, el push y los descartes los "
                                 "confirma el humano. Dale el comando para que lo lance el con ! delante.")
    if STATE_PATH.search(norm) and _write_or_exec_hint(command) and not HARNESS_CLI.match(command):
        return _decision("deny", "El estado de las features lo escriben solo feature.py, ledger.py y run_acceptance.py. "
                                 "Si solo quieres leer, ejecuta la lectura sola (sin python, redirecciones ni otros "
                                 "comandos encadenados) o usa la herramienta Read.")
    if ENGINE_MENTION.search(norm):
        if HARNESS_TESTS.match(command):
            return None
        parsed = _feature_cli(command)
        if parsed:
            subcommand, event, by = parsed
            if subcommand in READ_SUBCOMMANDS:
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
    private = private_data_problem(command, subagent=False)
    if private:
        return _decision("ask", f"Posible lectura de secretos: {private}. Confirma solo si lo has pedido tu y no "
                                "pegues el resultado en ningun sitio.")
    if HARNESS_TESTS.match(command) or VERIFY_SCRIPT.match(command):
        return None
    if _write_hint(command) and (CONTROL_PATH.search(norm) or _glob_hits_protected(
            command, cwd, re.compile(r"(^|/)(\.git|\.claude)(/|$)|(^|/)(CLAUDE|AGENTS|HARNESS)\.md$", I))):
        return _decision("ask", "El comando modifica configuracion del harness, instrucciones o git. Confirma solo si "
                                "lo has pedido tu.")
    return None


def evaluate(payload: dict) -> dict | None:
    tool = payload.get("tool_name")
    if tool in EDIT_TOOLS:
        return check_edit(payload)
    if tool in READ_TOOLS:
        return check_read(payload)
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
