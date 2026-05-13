#!/usr/bin/env bash
# init.sh — bootstrap del proyecto generado por harness-cli.
# Ejecútalo UNA vez después de `harness init <perfil>`.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

if [ ! -d .git ]; then
  echo "→ Inicializando repositorio git…"
  git init -q
  git add -A
  git commit -q -m "chore: scaffold from harness-cli"
  echo "✓ git init + primer commit hecho."
else
  echo "→ Ya hay un repositorio git, saltando git init."
fi

cat <<'EOF'

✓ Bootstrap completo.

Próximos pasos:
  1. Lee AGENTS.md (contrato de orquestación), CLAUDE.md (guía operativa) y
     USAGE.md (específico de tu perfil).
  2. Elige una feature en feature_list.json y crea progress/<feature-id>/.
  3. Invoca al Explorer:
     "Lee .claude/agents/explorer.md y ejecuta para la feature <id>".
  4. Detente en cada gate; reanuda sólo con aprobación humana.
EOF
