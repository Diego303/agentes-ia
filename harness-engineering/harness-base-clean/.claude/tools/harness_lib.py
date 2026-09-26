"""Utilidades compartidas por las herramientas del harness (solo biblioteca estandar).

Incluye un cargador/volcador YAML de un subconjunto estricto: mapeos y listas por
bloque, escalares planos o entrecomillados, listas en linea de escalares, `[]`,
`{}` y bloques `|`/`>`. Sin anclas, etiquetas ni documentos multiples. Es
deliberado: el mismo parser en todas las maquinas, sin dependencias externas.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import re
import tempfile
from pathlib import Path
from typing import Any

try:  # Python 3.11+
    import tomllib as _toml
except ModuleNotFoundError:  # pragma: no cover - depende del interprete
    try:
        import tomli as _toml  # type: ignore[no-redef]
    except ModuleNotFoundError:
        _toml = None

ROOT = Path(__file__).resolve().parents[2]
HOME = Path.home()
FEATURE_ID_RE = re.compile(r"^[A-Z][A-Z0-9]*-[0-9]+$")
SPEC_FILES = ("proposal.md", "requirements.md", "design.md", "tasks.md", "acceptance.yaml")


class HarnessError(Exception):
    """Error de configuracion o de datos del harness."""


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------


class Paths:
    def __init__(self, root: Path | None = None) -> None:
        self.root = (root or ROOT).resolve()
        self.bundle = self.root / ".claude"
        self.harness_toml = self.bundle / "harness.toml"
        self.workflow = self.bundle / "contracts" / "workflow.toml"
        self.feature_list = self.bundle / "feature_list.json"
        self.registry = self.bundle / "agents" / "agent-registry.yaml"
        self.settings = self.bundle / "settings.json"
        self.state = self.bundle / "state"
        self.templates = self.bundle / "templates"

    def feature(self, feature_id: str) -> Path:
        return self.state / feature_id


# ---------------------------------------------------------------------------
# Tiempo, hashes y escritura atomica
# ---------------------------------------------------------------------------


def now_iso() -> str:
    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_iso(value: Any) -> _dt.datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = _dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=_dt.timezone.utc)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_text_atomic(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


# ---------------------------------------------------------------------------
# JSON / TOML
# ---------------------------------------------------------------------------


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def dump_json(path: Path, data: Any) -> None:
    write_text_atomic(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def load_toml(path: Path) -> dict:
    if _toml is None:
        raise HarnessError("Se necesita Python 3.11+ (tomllib) o el paquete 'tomli' para leer TOML")
    try:
        return _toml.loads(path.read_text(encoding="utf-8-sig"))
    except _toml.TOMLDecodeError as exc:
        raise HarnessError(f"{path}: TOML invalido: {exc}") from exc


# ---------------------------------------------------------------------------
# YAML (subconjunto)
# ---------------------------------------------------------------------------


class YamlError(HarnessError):
    pass


_KEY_RE = re.compile(r"""^(?P<key>[A-Za-z0-9_][A-Za-z0-9_.\-/]*|"[^"]*"|'[^']*')[ \t]*:(?:[ \t]+|$)""")
_INT_RE = re.compile(r"^[-+]?[0-9]+$")
_FLOAT_RE = re.compile(r"^[-+]?(?:[0-9]+\.[0-9]*|\.[0-9]+)(?:[eE][-+]?[0-9]+)?$")
_BLOCK_SCALAR = {"|", "|-", "|+", ">", ">-", ">+"}


def _read_quoted(text: str, lineno: int) -> tuple[str, str]:
    """Devuelve (valor, resto) para una cadena que empieza por comilla."""
    quote = text[0]
    i = 1
    if quote == '"':
        while i < len(text):
            if text[i] == "\\":
                i += 2
                continue
            if text[i] == '"':
                try:
                    return json.loads(text[: i + 1]), text[i + 1 :]
                except json.JSONDecodeError as exc:
                    raise YamlError(f"linea {lineno}: escape invalido en cadena: {exc}") from exc
            i += 1
    else:
        chunks = []
        while i < len(text):
            if text[i] == "'":
                if text[i + 1 : i + 2] == "'":
                    chunks.append("'")
                    i += 2
                    continue
                return "".join(chunks), text[i + 1 :]
            chunks.append(text[i])
            i += 1
    raise YamlError(f"linea {lineno}: cadena sin cerrar")


def _strip_comment(text: str) -> str:
    match = re.search(r"(^|[ \t])#", text)
    return text[: match.start()].rstrip() if match else text.rstrip()


def _split_flow(inner: str, lineno: int) -> list[str]:
    items, current, quote = [], [], None
    for char in inner:
        if quote:
            current.append(char)
            if char == quote:
                quote = None
        elif char in "\"'":
            quote = char
            current.append(char)
        elif char in "[]{}":
            raise YamlError(f"linea {lineno}: colecciones anidadas en linea no soportadas")
        elif char == ",":
            items.append("".join(current).strip())
            current = []
        else:
            current.append(char)
    if quote:
        raise YamlError(f"linea {lineno}: cadena sin cerrar en lista")
    tail = "".join(current).strip()
    if tail:
        items.append(tail)
    elif items:
        raise YamlError(f"linea {lineno}: elemento vacio en lista")
    return items


def _plain(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"", "~", "null"}:
        return None
    if lowered == "true":
        return True
    if lowered == "false":
        return False
    if _INT_RE.match(value):
        return int(value)
    if _FLOAT_RE.match(value):
        return float(value)
    return value


def parse_scalar(text: str, lineno: int = 0) -> Any:
    text = text.strip()
    if text[:1] in "\"'":
        value, rest = _read_quoted(text, lineno)
        if _strip_comment(rest).strip():
            raise YamlError(f"linea {lineno}: texto inesperado tras la cadena: {rest.strip()!r}")
        return value
    text = _strip_comment(text)
    if text.startswith("["):
        if not text.endswith("]"):
            raise YamlError(f"linea {lineno}: lista en linea sin cerrar")
        return [parse_scalar(item, lineno) for item in _split_flow(text[1:-1], lineno)]
    if text.startswith("{"):
        if text.replace(" ", "") != "{}":
            raise YamlError(f"linea {lineno}: solo se admite el mapeo vacio {{}} en linea")
        return {}
    if text.startswith(("&", "*", "!", "|", ">", "%", "@", "`", "- ", "? ")):
        raise YamlError(f"linea {lineno}: sintaxis YAML no soportada: {text!r}")
    if ": " in text or text.endswith(":"):
        raise YamlError(f"linea {lineno}: entrecomilla los valores que contienen ': ' -> {text!r}")
    return _plain(text)


class _Parser:
    def __init__(self, text: str) -> None:
        self.lines = text.replace("\r\n", "\n").split("\n")
        self.i = 0
        if self.lines and self.lines[0].startswith("﻿"):
            self.lines[0] = self.lines[0][1:]

    def peek(self) -> tuple[int, str] | None:
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            stripped = raw.strip()
            if stripped and not stripped.startswith("#") and stripped != "---":
                content = raw.lstrip(" ")
                if content.startswith("\t"):
                    raise YamlError(f"linea {self.i + 1}: tabuladores no permitidos en la indentacion")
                return len(raw) - len(content), content.rstrip()
            self.i += 1
        return None

    def node(self, indent: int) -> Any:
        nxt = self.peek()
        if nxt is None:
            return None
        return self.seq(nxt[0]) if _is_item(nxt[1]) else self.mapping(nxt[0])

    def mapping(self, indent: int) -> dict:
        result: dict = {}
        while True:
            nxt = self.peek()
            if nxt is None or nxt[0] < indent:
                return result
            ind, content = nxt
            lineno = self.i + 1
            if ind > indent:
                raise YamlError(f"linea {lineno}: indentacion inesperada")
            if _is_item(content):
                return result
            match = _KEY_RE.match(content)
            if not match:
                raise YamlError(f"linea {lineno}: se esperaba 'clave: valor', encontrado {content!r}")
            key = match.group("key")
            if key[:1] in "\"'":
                key = key[1:-1]
            if key in result:
                raise YamlError(f"linea {lineno}: clave duplicada {key!r}")
            rest = content[match.end():]
            self.i += 1
            if _strip_comment(rest) in _BLOCK_SCALAR:
                result[key] = self.block_scalar(indent, _strip_comment(rest))
            elif _strip_comment(rest):
                result[key] = self.scalar_with_continuation(rest, indent, lineno)
            else:
                child = self.peek()
                if child is None:
                    result[key] = None
                elif _is_item(child[1]) and child[0] >= indent:
                    result[key] = self.seq(child[0])
                elif child[0] > indent:
                    result[key] = self.mapping(child[0])
                else:
                    result[key] = None

    def seq(self, indent: int) -> list:
        items: list = []
        while True:
            nxt = self.peek()
            if nxt is None or nxt[0] < indent:
                return items
            ind, content = nxt
            lineno = self.i + 1
            if ind > indent:
                raise YamlError(f"linea {lineno}: indentacion inesperada en lista")
            if not _is_item(content):
                return items
            rest = content[1:].lstrip(" ")
            if not rest:
                self.i += 1
                child = self.peek()
                items.append(self.node(child[0]) if child and child[0] > indent else None)
            elif _KEY_RE.match(rest):
                item_indent = indent + len(content) - len(rest)
                self.lines[self.i] = " " * item_indent + rest
                items.append(self.mapping(item_indent))
            else:
                self.i += 1
                items.append(self.scalar_with_continuation(rest, indent, lineno))

    def scalar_with_continuation(self, text: str, indent: int, lineno: int) -> Any:
        """Escalar en linea; admite lineas de continuacion mas indentadas (plegado YAML)."""
        first = text.strip()[:1]
        if first in "\"'":
            joined = text.strip()
            while True:
                try:
                    return parse_scalar(joined, lineno)
                except YamlError as exc:
                    nxt = self.peek()
                    if "sin cerrar" not in str(exc) or nxt is None or nxt[0] <= indent:
                        raise
                    joined = f"{joined} {nxt[1].strip()}"
                    self.i += 1
        if first in "[{":
            return parse_scalar(text, lineno)
        parts = [_strip_comment(text).strip()]
        while True:
            nxt = self.peek()
            if nxt is None or nxt[0] <= indent:
                break
            parts.append(_strip_comment(nxt[1]).strip())
            self.i += 1
        return parse_scalar(" ".join(parts), lineno)

    def block_scalar(self, parent_indent: int, style: str) -> str:
        collected: list[str] = []
        content_indent = None
        while self.i < len(self.lines):
            raw = self.lines[self.i]
            if raw.strip():
                ind = len(raw) - len(raw.lstrip(" "))
                if ind <= parent_indent:
                    break
                if content_indent is None:
                    content_indent = ind
                if ind < content_indent:
                    raise YamlError(f"linea {self.i + 1}: indentacion inconsistente en bloque")
                collected.append(raw[content_indent:])
            else:
                collected.append("")
            self.i += 1
        while collected and collected[-1] == "" and style[-1:] != "+":
            collected.pop()
        if style.startswith(">"):
            text, paragraph = [], []
            for line in collected:
                if line:
                    paragraph.append(line)
                else:
                    text.append(" ".join(paragraph))
                    paragraph = []
            text.append(" ".join(paragraph))
            body = "\n".join(text)
        else:
            body = "\n".join(collected)
        return body if style.endswith("-") else body + "\n"


def _is_item(content: str) -> bool:
    return content == "-" or content.startswith("- ")


def loads_yaml(text: str) -> Any:
    parser = _Parser(text)
    first = parser.peek()
    if first is None:
        return None
    if first[0] != 0:
        raise YamlError(f"linea {parser.i + 1}: el documento debe empezar sin indentacion")
    value = parser.node(0)
    trailing = parser.peek()
    if trailing is not None:
        raise YamlError(f"linea {parser.i + 1}: contenido inesperado: {trailing[1]!r}")
    return value


def load_yaml(path: Path) -> Any:
    try:
        return loads_yaml(path.read_text(encoding="utf-8-sig"))
    except YamlError as exc:
        raise YamlError(f"{path.as_posix()}: {exc}") from None


_SAFE_PLAIN = re.compile(r"^[A-Za-z0-9_./+(][A-Za-z0-9_./@+()<>=,' -]*$")
_RESERVED = {"true", "false", "null", "~", "yes", "no", "on", "off", ""}


def _dump_scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    text = str(value)
    if (
        _SAFE_PLAIN.match(text)
        and text == text.strip()
        and text.lower() not in _RESERVED
        and not _INT_RE.match(text)
        and not _FLOAT_RE.match(text)
        and ": " not in text
        and " #" not in text
    ):
        return text
    return json.dumps(text, ensure_ascii=False)


def dumps_yaml(data: Any, indent: int = 0) -> str:
    pad = " " * indent
    lines: list[str] = []
    if isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, dict) and value:
                lines.append(f"{pad}{key}:")
                lines.append(dumps_yaml(value, indent + 2))
            elif isinstance(value, list) and value:
                lines.append(f"{pad}{key}:")
                lines.append(dumps_yaml(value, indent + 2))
            elif isinstance(value, dict):
                lines.append(f"{pad}{key}: {{}}")
            elif isinstance(value, list):
                lines.append(f"{pad}{key}: []")
            else:
                lines.append(f"{pad}{key}: {_dump_scalar(value)}")
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) and item:
                body = dumps_yaml(item, indent + 2).split("\n")
                lines.append(f"{pad}- {body[0].lstrip()}")
                lines.extend(body[1:])
            elif isinstance(item, (dict, list)) and not item:
                lines.append(f"{pad}- {'{}' if isinstance(item, dict) else '[]'}")
            elif isinstance(item, list):
                raise YamlError("listas anidadas no soportadas por el volcador")
            else:
                lines.append(f"{pad}- {_dump_scalar(item)}")
    else:
        lines.append(f"{pad}{_dump_scalar(data)}")
    return "\n".join(lines)


def dump_yaml(path: Path, data: Any, header: str = "") -> None:
    text = dumps_yaml(data)
    if loads_yaml(text) != data:  # nunca escribir estado que luego no se pueda leer
        raise YamlError(f"{path.as_posix()}: el volcado YAML no es reversible")
    write_text_atomic(path, header + text + "\n")


def portable_path(path: str | None) -> str | None:
    """Sustituye el home por ~ para no versionar rutas personales."""
    if not path:
        return path
    home = str(HOME)
    return "~" + path[len(home):] if path.startswith(home + os.sep) else path


# ---------------------------------------------------------------------------
# Patrones de seguridad compartidos (validador y guard)
# ---------------------------------------------------------------------------

# Referencias a secretos: nunca hacen falta en la aceptacion ni en Bash (.env.example si).
SECRET_REF = re.compile(
    r"(^|[\s/'\"=@<:(])(\.env(\.(?!example\b|sample\b|template\b|dist\b)[\w-]+)?|id_(rsa|dsa|ecdsa|ed25519)\w*"
    r"|[\w.-]+\.(pem|p12|pfx|key)|\.netrc|\.pgpass|\.pypirc|\.npmrc)(?=$|[\s'\";|&)<>])"
    r"|(~|\$HOME|\$\{HOME\})/\.(ssh|aws|gnupg|kube|docker)\b|/etc/(shadow|sudoers)\b",
    re.IGNORECASE,
)
NETWORK_CLIENT = re.compile(r"\b(curl|wget|nc|ncat|netcat|socat|telnet|ssh|scp|sftp|ftp|rsync)\b|/dev/(tcp|udp)/")
URL_RE = re.compile(r"https?://[^\s'\"]+")
LOCAL_URL_RE = re.compile(r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])([:/]|$)")
INLINE_CODE = re.compile(
    r"\b(python[0-9.]*|node|deno|bun|perl|ruby|php|pwsh|powershell)\b[^|;&\n]*?\s(-c|-e|-r|--eval|-Command|-EncodedCommand)(\s|$)"
    r"|\b(ba|z|k|da|fi)?sh\b[^|;&\n]*?\s-[a-zA-Z]*c(\s|$)|\beval\b|\bbase64\s+(-d|--decode)\b|\bxxd\s+-r\b"
)


def external_network(command: str) -> bool:
    """True si el comando usa un cliente de red contra algo distinto de localhost."""
    clients = {match.group(1) or "dev" for match in NETWORK_CLIENT.finditer(command)}
    if not clients:
        return False
    urls = URL_RE.findall(command)
    local_http = clients <= {"curl", "wget"} and urls and all(LOCAL_URL_RE.match(url) for url in urls)
    return not local_http


# ---------------------------------------------------------------------------
# Frontmatter de agentes y skills
# ---------------------------------------------------------------------------


def frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8-sig")
    if not text.startswith("---"):
        return None
    parts = re.split(r"^---[ \t]*$", text, maxsplit=2, flags=re.MULTILINE)
    if len(parts) < 3:
        return None
    data = loads_yaml(parts[1])
    return data if isinstance(data, dict) else None


# ---------------------------------------------------------------------------
# Estado del harness
# ---------------------------------------------------------------------------


def load_config(paths: Paths) -> dict:
    return load_toml(paths.harness_toml)


def load_workflow(paths: Paths) -> dict:
    return load_toml(paths.workflow)


def transitions_from(workflow: dict, phase: str) -> list[dict]:
    found = []
    for transition in workflow.get("transitions", []):
        sources = transition.get("from")
        sources = sources if isinstance(sources, list) else [sources]
        if phase in sources:
            found.append(transition)
    return found


def find_transition(workflow: dict, phase: str, event: str) -> dict | None:
    for transition in transitions_from(workflow, phase):
        if transition.get("event") == event:
            return transition
    return None


def load_features(paths: Paths) -> list[dict]:
    data = load_json(paths.feature_list)
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        raise HarnessError(f"{paths.feature_list}: falta la lista 'features'")
    return features


def find_feature(paths: Paths, feature_id: str) -> dict | None:
    return next((item for item in load_features(paths) if item.get("id") == feature_id), None)


def read_events(paths: Paths, feature_id: str) -> list[dict]:
    log = paths.feature(feature_id) / "event.log"
    events: list[dict] = []
    if not log.is_file():
        return events
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def append_event(paths: Paths, feature_id: str, event: dict) -> None:
    log = paths.feature(feature_id) / "event.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    record = {"ts": now_iso(), "feature_id": feature_id, **event}
    with log.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
