#!/usr/bin/env bash
# init.sh — prepara el proyecto para el harness. Idempotente: puedes repetirlo.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

echo "→ Comprobando Python…"
if ! command -v python3 >/dev/null 2>&1; then
  echo "✗ Falta python3 (se necesita 3.11+, o 3.9+ con el paquete tomli)." >&2
  exit 1
fi
python3 - <<'PY'
import sys
if sys.version_info < (3, 9):
    sys.exit("✗ Python 3.9+ requerido")
try:
    import tomllib  # noqa: F401
except ModuleNotFoundError:
    try:
        import tomli  # noqa: F401
    except ModuleNotFoundError:
        sys.exit("✗ Python < 3.11 sin tomli: instala tomli o usa Python 3.11+")
print(f"✓ Python {sys.version.split()[0]}")
PY

if git -C "$ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "✓ Repositorio git detectado."
else
  echo "→ Inicializando git (sin commit: revisa qué versionas antes del primero)…"
  git -C "$ROOT" init -q
fi

echo "→ Validando el harness…"
python3 .claude/tools/validate_harness.py
echo "→ Tests del harness…"
python3 -m unittest discover -s .claude/tests -q

cat <<'MSG'

✓ Harness listo.

Siguientes pasos:
  1. En Claude Code: "usa project-bootstrap para adaptar el harness a este repositorio"
     (completa AGENTS.md y .claude/bootstrap/verify.sh).
  2. Haz un primer commit: el reviewer compara contra el commit aprobado en GATE#1.
  3. Copia un prompt de FAST-USAGE.md para tu primera feature.
MSG
