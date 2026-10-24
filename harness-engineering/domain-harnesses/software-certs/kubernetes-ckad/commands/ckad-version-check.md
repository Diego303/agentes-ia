---
description: Detecta drift entre el vault (frontmatter kubernetes_version) y la versión K8s vigente en kubernetes.io. Identifica archivos con apiVersions / features potencialmente afectados por release notes recientes. Reusa ckad-coverage-analyst con prompt específico de version drift. Útil 1-2 veces antes del examen.
allowed-tools: Read, Write, WebFetch, Bash, Glob, Grep, Agent
---

# /ckad-version-check — Detectar drift de versión Kubernetes

Eres el orquestador. El usuario quiere verificar si el vault está alineado con la versión K8s vigente.

## Pasos

### 1. Identificar versión target del vault

1. Lee `INDICE-MAESTRO.md` y `README.md` raíz → extrae `kubernetes_version` (actualmente `v1.35`).
2. Sample-check del frontmatter de 3-5 archivos atómicos para confirmar consistencia.

### 2. Identificar versión vigente

WebFetch a `https://kubernetes.io/releases/` para identificar:
- Versión K8s actual stable.
- Versiones soportadas (typically las últimas 3 minor).
- EOL dates de versiones.

### 3. Si hay drift (vault declara v1.35, vigente es v1.36+)

Dispatch `ckad-coverage-analyst` con prompt modificado:

```
TASK: Version drift analysis (NOT coverage).

Vault declared version: v1.35
Current K8s stable: v1.XX (from kubernetes.io/releases/)

Steps:
1. WebFetch kubernetes.io/blog/ para las release notes de las versiones nuevas (v1.36+, v1.37+ si aplica).
2. Identifica deprecations introducidas tras v1.35.
3. Identifica features que pasaron de beta a stable tras v1.35 (relevante para CKAD).
4. Identifica APIs removed tras v1.35.

Cross-check vs vault:
5. Para cada archivo atómico (Glob `**/*.md` excluyendo apuntes-base/ y _index.md):
   - Lee frontmatter + secciones "🏗️ Cómo se hace" y "🪤 Trampas".
   - Identifica si menciona alguna API/feature potencialmente afectada por el drift.
6. Reporta archivos con potencial drift, severidad ALTA/MEDIA/BAJA.

Output: `00-Aggregations/version-drift-<YYYYMMDD>.md` con:
- Comparación versión declarada vs vigente.
- Tabla de archivos potencialmente stale.
- Acciones recomendadas (qué archivos regenerar / qué cambios manuales aplicar).
```

### 4. Si NO hay drift (vault y vigente coinciden)

Reportar al usuario: "Vault alineado con K8s vigente (v1.35). Próxima check sugerida: tras release v1.36 (~4 meses)."

### 5. Output al usuario

```markdown
# 📡 Version Check Report

**Vault declared**: v1.35
**K8s current stable**: v1.XX
**Drift**: <0 versiones | N versiones>

## Resumen
- Total archivos vault: <N>
- Potencialmente afectados: <N>
- Severidad max: <CRÍTICA|ALTA|MEDIA|BAJA|NINGUNA>

## Top archivos a actualizar (si drift)
1. [[<slug>]] — razón: <e.g., menciona feature X que era beta en v1.35, ahora stable v1.36>
2. ...

## Acciones recomendadas
1. /ckad-write <slug> --regenerate  # regenerar contra docs actuales
2. ...

## Próximo check sugerido
Tras release de K8s v1.XX+1 (~4 meses).
```

## Reglas

- Allowlist WebFetch obligatoria: `kubernetes.io`.
- **No regenera archivos automáticamente** — solo identifica drift y sugiere.
- Si vault es la versión vigente, reporte breve OK.
- Detección de drift es heurística (texto matching); el usuario debe verificar manualmente antes de regenerar.

$ARGUMENTS
