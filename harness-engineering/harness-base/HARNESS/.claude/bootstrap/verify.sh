#!/usr/bin/env bash
# verify.sh — regresión completa del proyecto (lint, tests, build...).
# La usan acceptance.yaml y el reviewer. Sustituye el bloque de abajo por los
# comandos reales del proyecto (los mismos que la CI) y borra la marca
# HARNESS_VERIFY_PLACEHOLDER: mientras exista, el validador lo avisa y ningún
# acceptance puede apoyarse en este script.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

# HARNESS_VERIFY_PLACEHOLDER
echo "verify.sh sin configurar: añade aquí lint y tests del proyecto (skill project-bootstrap)."
exit 0
